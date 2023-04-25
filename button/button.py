# This class handles the big button push on the Marble Run
# The user gets to press down the button, and while pressed,
# the motors turn on the marble run so marbles are raised to
# the top of the run and dispense onto the track.
#
# We are watching the button as an async process so that other
# tasks, like the motor steps being generated, can operate at the
# same time with cooperative multi-tasking.

import asyncio
import board
import keypad

class Button:
    def __init__(self, onPressCb, onReleaseCb):

        print("Initting Button library...")
        self._pinButtonPin = board.IO21

        # User should pass in a callback function so we can call it
        # upon button press and release
        self._onPressCb = onPressCb
        self._onReleaseCb = onReleaseCb

    async def asyncTaskCatchButtonPinPress(self):
        """Print a message when pin goes low and when it goes high."""
        with keypad.Keys((self._pinButtonPin,), interval=0.2, value_when_pressed=False, pull=True) as keys:
            print("Starting button listen infinite loop")
            while True:
                event = keys.events.get()
                if event:
                    if event.pressed:
                        # print("pin went low.")
                        if self._onPressCb != None:
                            # print("Calling onPress cb.")
                            self._onPressCb()
                    elif event.released:
                        # print("pin went high")
                        if self._onReleaseCb != None:
                            # print("Calling onRelease cb.")
                            self._onReleaseCb()
                await asyncio.sleep(0.2)

# def testOnPressCb():
#     print("Got onPress")

# def testOnReleaseCb():
#     print("Got onRelease")

# async def test():
#     b = Button(testOnPressCb, testOnReleaseCb)
#     interrupt_task = asyncio.create_task(b.catch_pin_transitions())
#     await asyncio.gather(interrupt_task)

# asyncio.run(test())