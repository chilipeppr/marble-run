# This version of main joins the display with the step pin marble counter

from display.display import Display
from display.display_bmp import DisplayBmp
from counter.counter import MarbleCounter
import board 
import pwmio 
import asyncio

class Dashboard:
    def __init__(self):

        print("Initting Dashboard")

        # Create our display hardware object
        self.d = Display()

        # Create bitmap UI display helper object. Pass in display to init().
        self.dbmp = DisplayBmp(self.d.display)

        # Create our countio marble counting object. 
        # This counts steps on pin IO4, divides the steps to marble count, 
        # then calls our callback when appropriate.
        # Pass in our callback to the init method that's called on each marble count update.
        self.mc = MarbleCounter(self.onMarbleCount)
        # self.mc.marbleCtr = 1073741700

        # Generate steps on IO7 as if user is pressing button to move steppers
        # Remember IO4 is physically wired to listen to IO7 to make this test frequency work
        self.freqGen = self.turnOnTestFrequency()

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

    def turnOnTestFrequency(self):

        # setup pinStep as PWM output
        freqGen = pwmio.PWMOut(
            board.IO7, 
            frequency=500, # Not allowed to set to 0, so use duty_cycle as our method of turning off stepper
            duty_cycle=2 ** 15,  # Cycles the pin with 50% duty cycle (half of 2 ** 16) 
            variable_frequency=True
            )
        print("Turned on frequency:", freqGen.frequency, "duty:", freqGen.duty_cycle)

        return freqGen

    def onMarbleCount(self, ctr):
        print("Got onMarbleCount. ctr:", ctr)

        # for testing, let's show the info screen at increments
        remainder = ctr % 30
        if remainder >= 10 and remainder <= 15:
            self.dbmp.showAccel()

        elif remainder >= 16 and remainder <= 20:
            self.dbmp.showMax()

        elif remainder >= 21 and remainder <= 25:
            self.dbmp.showDecel()

        elif remainder == 26:
            # this would be like our stepper object saying it's done showing info screens
            self.dbmp.showSplashScreensAgain()
            
        self.dbmp.updateCounter(ctr)

async def main():
    
    d = Dashboard()

    await asyncio.gather(d.marble_count_task, d.display_task, d.write_marblectr_todisk_task)  # Don't forget the await!

    d.deinit()
    
    print("done with main")

asyncio.run(main())
