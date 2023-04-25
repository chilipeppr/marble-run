# This file acts like a main entry point to test the button
# pressing by creating the Button object and creating a
# ButtonMimic object

# import sys
# print("exiting immediately")
# sys.exit()

import asyncio
from button.button import Button 
# from button_mimic import ButtonMimic 
from stepper.stepper_tmc2209_pwm import Stepper
from stepper.stepper_tmc2209_pa_pwmagitator import StepperAgitator
import microcontroller

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

    self.pinListenNum = board.IO4

Fan Control
    In fan/fany.py

    self.pinFanPwm = board.IO3

Button Listener
    In button/button.py

    self._pinButtonPin = board.IO21
"""


class Dashboard:
    def __init__(self):

        print("Initting Dashboard")
        # self._pinButtonPin = board.IO21

        # Create an async button with callbacks for press/release
        self._button = Button(self.onPressCb, self.onReleaseCb)
        self.interrupt_task = asyncio.create_task(self._button.asyncTaskCatchButtonPinPress())

        # Create stepper object so we can call spin on button press/release
        self._stepper = Stepper()
        self._stepper.enable()

        # Create stepperAgitator object so we can call rock on button press/release
        self._stepperAgitator = StepperAgitator()
        self._stepperAgitator.enable()

        # Create spin task that spins the main motor to carry the marbles to the top
        # We can just call start/stop on this task to have the motor accel/decel for us
        self.spin_task = asyncio.create_task(self._stepper.spinAsyncTaskPwm())

        # Create a rocking agitator task that helps the marbles drop down
        # into the onramp pipe to the elevator
        # We can just call start/stop to have the rocking commence/end
        self.rock_task = asyncio.create_task(self._stepperAgitator.spinAsyncTaskPwm())

        # Create an async timer that reboots the ESP32-S2 every 4 hours
        # self.reboot_timer_task = asyncio.create_task(self.rebootTimer(60*60*4))

    def deinit(self):
        self._stepper.disable()

    def onPressCb(self):
        print("Got onPress. Spinning motor.")
        # self._stepper.enable()
        # start spinning
        self._stepper.spinAsyncStart()
        self._stepperAgitator.spinAsyncStart()

    def onReleaseCb(self):
        print("Got onRelease. Stopping motor.")
        # stop spinning
        self._stepper.spinAsyncStop()
        self._stepperAgitator.spinAsyncStop()
        # self._stepper.disable()

    async def rebootTimer(self, duration):
        print("Starting reboot timer")
        
        await asyncio.sleep(duration) # don't forget the await
        
        # Rebooting
        microcontroller.reset()

        print("Ended timer")

async def main():
    
    d = Dashboard()

    # await asyncio.gather(d.interrupt_task, d.spin_task, d.reboot_timer_task)  # Don't forget the await!
    await asyncio.gather(d.interrupt_task, d.spin_task, d.rock_task)  # Don't forget the await!

    d.deinit()
    
    print("done with main")

asyncio.run(main())
