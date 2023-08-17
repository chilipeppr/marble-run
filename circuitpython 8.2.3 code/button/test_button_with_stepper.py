# This file acts like a main entry point to test the button
# pressing by creating the Button object and creating a
# ButtonMimic object

import asyncio
from button.button import Button 
from button.button_mimic import ButtonMimic 
from stepper.stepper_tmc2209 import Stepper

class Dashboard:
    def __init__(self):

        print("Initting Dashboard")
        # self._pinButtonPin = board.IO21

        # Create an async button with callbacks for press/release
        self._button = Button(self.onPressCb, self.onReleaseCb)
        self.interrupt_task = asyncio.create_task(self._button.asyncTaskCatchButtonPinPress())

        # Create stepper object so we can call spin on button press/release
        self._stepper = Stepper()
        self.spin_task = asyncio.create_task(self._stepper.spinAsyncTask())

    def onPressCb(self):
        print("Got onPress. Spinning motor.")
        self._stepper.enable()
        # start spinning
        self._stepper.spinAsyncStart()

    def onReleaseCb(self):
        print("Got onRelease. Stopping motor.")
        # stop spinning
        self._stepper.spinAsyncStop()
        self._stepper.disable()

async def test():
    
    d = Dashboard()
    await asyncio.gather(d.interrupt_task, d.spin_task)  # Don't forget the await!
    
    print("done with test")

asyncio.run(test())
