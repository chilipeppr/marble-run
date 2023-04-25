# This file mimics a button press by a user
# Use this file by attaching a wire from pin 18 to pin 21
# We generate a signal on pin 18, which then propagates
# to pin 21. Pin 21 is the pin listening for button presses
# by the actual button, so once you have a button attached
# to the ESP32, this file will no longer work unless you keep
# pin 18 attached to the button wire.

import asyncio
import board
import digitalio

class ButtonMimic:
    def __init__(self):

        print("Initting Button Mimic library...")
        self._pinMimicButtonPin = board.IO18

        self._pinMimicButton = digitalio.DigitalInOut(self._pinMimicButtonPin)
        self._pinMimicButton.switch_to_output(value=False)

    async def mimicPress(self, interval, count):  # Don't forget the async!
            for _ in range(count):
                self._pinMimicButton.value = True
                print("Mimic button press", _)
                await asyncio.sleep(interval)  # Don't forget the await!
                self._pinMimicButton.value = False
                print("Mimic button release", _)
                await asyncio.sleep(interval)  # Don't forget the await!


# async def test():  # Don't forget the async!
#     bm = ButtonMimic()
#     mimic_task = asyncio.create_task(bm.mimicPress(1.25, 10))
#     await asyncio.gather(mimic_task)  # Don't forget the await!
#     print("done")

# asyncio.run(test())