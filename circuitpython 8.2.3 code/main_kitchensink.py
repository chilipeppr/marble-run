# This file is the main entry point to the Marble Run
# It brings together the:
#   - Stepper Driver for the Elevator
#   - Stepper Driver for the Agitator
#   - Display
#   - Counter
#   - Button Listener
#   - Reboot Timer
#   - Fan

# import sys
# print("exiting immediately")
# sys.exit()

import asyncio
from button.button import Button 
# from button_mimic import ButtonMimic 
from stepper.stepper_tmc2209_pwm import Stepper
from stepper.stepper_tmc2209_pa_pwmagitator import StepperAgitator
import microcontroller
from display.display import Display
from display.display_bmp import DisplayBmp
from counter.counter import MarbleCounter
import board 
from fan.fan import Fan

""" 
PINS 

Elevator Stepper Motor
    In stepper/stepper_tmc2209_pwm.py

    self._pinEnablePin = board.IO5
    self._pinDirPin = board.IO6
    self._pinStepPin = board.IO7
    self._pinDiagPin = board.IO8
    # self._pinMs1Pin = board.IO9
    # self._pinMs2Pin = board.IO15

Agitator Stepper Motor
    In stepper/stepper_tmc2209_pa_pwmagitator.py

    self._pinEnablePin = board.IO13
    self._pinDirPin = board.IO14
    self._pinStepPin = board.IO15
    self._pinDiagPin = board.IO16
    # self._pinMs1Pin = board.IO9
    # self._pinMs2Pin = board.IO15

Display
    In display/display.py

    # On Teyleten  | GPIO for Lolin S2 Mini
    # SCK (SCLK)     IO12
    # SDA (MOSI)     IO11
    # RES (Reset)    IO9  
    # DC             IO38
    # CS (SS)        IO10

Loopback Step Counter
    In counter/counter.py

    # This pin should be loop connected to the step pin for the elevator
    # so connect it physically on the board to self._pinStepPin = board.IO7
    self.pinListenNum = board.IO4

Fan Control
    In fan/fan.py

    self.pinFanPwm = board.IO3

Button Listener
    In button/button.py

    self._pinButtonPin = board.IO21

Kill Switch Button
    In killswitch/killswitch.py
    
    self._pinKillSwitchPin = board.IO1
"""


class Dashboard:
    def __init__(self):

        print("Initting Dashboard")
        # self._pinButtonPin = board.IO21

        # BUTTON SETUP

        # Create an async button with callbacks for press/release
        self._button = Button(self.onPressCb, self.onReleaseCb)
        self.button_interrupt_task = asyncio.create_task(self._button.asyncTaskCatchButtonPinPress())

        # STEPPER MOTORS 

        # Create Elevator stepper object so we can call spin on button press/release
        self._stepper = Stepper(onAccelCb=self.onAccelCb, 
                                onMaxSpeedCb=self.onMaxCb, 
                                onDecelCb=self.onDecelCb,
                                onStoppedCb=self.onStoppedCb)
        # self._stepper.freqMax = 300
        # self._stepper.freqStep = 30
        # self._stepper.enable()

        # Create stepperAgitator object so we can call agitate on button press/release
        self._stepperAgitator = StepperAgitator()
        self._stepperAgitator.freqMax = 300
        self._stepperAgitator.freqStep = 40
        # self._stepperAgitator.enable()

        # Create spin task that spins the main motor to carry the marbles to the top
        # We need this as a task so that it can control the accel/decel on its own
        # We can just call start/stop on this task to have the motor accel/decel for us
        self.elevator_task = asyncio.create_task(self._stepper.spinAsyncTaskPwm())

        # Create a rocking agitator task that helps the marbles drop down
        # into the onramp pipe to the elevator
        # We can just call start/stop to have the rocking commence/end
        self.agitator_task = asyncio.create_task(self._stepperAgitator.spinAsyncTaskPwm())

        # DISPLAY AND MARBLE COUNTER

        # Create our display hardware object
        self.d = Display()

        # Create bitmap UI display helper object. Pass in display to init().
        self.dbmp = DisplayBmp(self.d.display)

        # Create our countio marble counting object. 
        # This counts steps on pin IO4, divides the steps to marble count, 
        # then calls our callback when appropriate.
        # Remember IO4 is physically wired to listen to IO7 to make this technique work
        # Pass in our callback to the init method that's called on each marble count update.
        self.mc = MarbleCounter(self.onMarbleCount)
        # self.mc.marbleCtr = 1073741700

        # Generate steps on IO7 as if user is pressing button to move steppers
        # Remember IO4 is physically wired to listen to IO7 to make this test frequency work
        # self.freqGen = self.turnOnTestFrequency()

        # Create the async task for our marble counter
        # This starts an infinite loop that counts the steps from the loopback pin 
        # and calls the callback when the count increases
        self.marble_count_task = asyncio.create_task(self.mc.asyncTaskCountSteps())

        # Create the async task that persists our marble count to disk so we can
        # keep track of it across reboots/crashes. It writes each hour.
        self.write_marblectr_todisk_task = asyncio.create_task(self.mc.asyncTaskWriteMarbleCountToDiskEveryHour())
        # self.mc.intervalSecsWriteMarbleCtrToDisk = 10 # temporarily override speed in seconds at which to write. defaults to 60*60 = 1 hr

        # Create the async task that shows the splash screens on the display
        self.display_task = asyncio.create_task(self.dbmp.asyncTaskShowSplashScreens())

        # FAN

        self.fan = Fan()
        self.fan.freqGen.frequency = 300
        self.fan.turnOff()

        # Create an async timer that reboots the ESP32-S2 every 8 hours
        # self.reboot_timer_task = asyncio.create_task(self.rebootTimer(60))  # 1 minute for testing
        self.reboot_timer_task = asyncio.create_task(self.rebootTimer(60*60*8)) # 8 hours
        # Manually log that we're rebooting
        from reboot.r import RebootReason
        self.rr = RebootReason()

        # Watch the wifi network
        from wifi.watcher import WifiWatcher
        ww = WifiWatcher()
        self.ww_task = asyncio.create_task(ww.asyncWifiWatcherTask())
        

    def deinit(self):
        self._stepper.disable()
        self._stepperAgitator.disable()

    def onPressCb(self):
        print("Got onPress. Spinning motor.")

        # Enable the power to the steppers
        # self._stepper.enable()
        self._stepperAgitator.enable()

        # start spinning
        self._stepper.spinAsyncStart()
        self._stepperAgitator.spinAsyncStart()

        # Turn on the fan to cool the stepper drivers
        self.fan.turnOn()

    def onReleaseCb(self):
        print("Got onRelease. Stopping motor.")
        # stop spinning
        self._stepper.spinAsyncStop()
        self._stepperAgitator.spinAsyncStop()
        # self._stepper.disable()

    def onMarbleCount(self, ctr):
        print("Got onMarbleCount. ctr:", ctr)

        # # for testing, let's show the info screen at increments
        # remainder = ctr % 30
        # if remainder >= 10 and remainder <= 15:
        #     self.dbmp.showAccel()

        # elif remainder >= 16 and remainder <= 20:
        #     self.dbmp.showMax()

        # elif remainder >= 21 and remainder <= 25:
        #     self.dbmp.showDecel()

        # elif remainder == 26:
        #     # this would be like our stepper object saying it's done showing info screens
        #     self.dbmp.showSplashScreensAgain()
            
        self.dbmp.updateCounter(ctr)

    def onAccelCb(self):
        # This is our callback we get from the elevator motor when it starts accelerating
        self.dbmp.showAccel()

    def onMaxCb(self):
        # This is our callback we get from the elevator motor when it is at max speed
        self.dbmp.showMax()

    def onDecelCb(self):
        # This is our callback we get from the elevator motor when it starts decelerating
        self.dbmp.showDecel()

    def onStoppedCb(self):
        # This is our callback we get from the elevator motor when it stops moving
        self.dbmp.showSplashScreensAgain()

        # Disable the hold power to the steppers
        # self._stepper.disable() # marbles will drop a bit
        self._stepperAgitator.disable()

        # Turn off fan
        self.fan.turnOff()

    async def rebootTimer(self, duration):
        print("Starting reboot timer. Duration (secs):", duration)
        
        await asyncio.sleep(duration) # don't forget the await
        
        self.rr.logToFileWithWifi("Manually rebooting due to reboot timer task")

        # Rebooting
        microcontroller.reset()

        print("Ended reboot timer")

async def main():
    
    d = Dashboard()

    # reboot_task = asyncio.create_task(d.rebootTimer(10))

    await asyncio.gather(
        d.marble_count_task, 
        d.display_task,
        d.write_marblectr_todisk_task, 
        d.button_interrupt_task, 
        d.elevator_task, 
        d.agitator_task,
        d.reboot_timer_task,
        d.ww_task
        )  # Don't forget the await!

    d.deinit()
    
    print("done with main")

asyncio.run(main())
