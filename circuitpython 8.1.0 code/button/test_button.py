# This file acts like a main entry point to test the button
# pressing by creating the Button object and creating a
# ButtonMimic object

import asyncio
from button.button import Button 
from button.button_mimic import ButtonMimic 

def testOnPressCb():
    print("Got onPress")

def testOnReleaseCb():
    print("Got onRelease")

async def test():
    b = Button(testOnPressCb, testOnReleaseCb)
    interrupt_task = asyncio.create_task(b.asyncTaskCatchButtonPinPress())

    # bm = ButtonMimic()
    # mimic_task = asyncio.create_task(bm.mimicPress(1.25, 10))

    # await asyncio.gather(mimic_task, interrupt_task)  # Don't forget the await!
    await asyncio.gather(interrupt_task)  # Don't forget the await!

    print("done with test")

asyncio.run(test())