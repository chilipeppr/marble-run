# This class handles the kill switch on the Marble Run
# The user gets to toggle the switch and if it's on, the main code
# runs, but if it's off then the main.py code just exits so you can debug
#
# We are only watching the switch on boot up for 5 seconds as an async 
# process so that other
# tasks can operate at the
# same time with cooperative multi-tasking.

import asyncio
import board
import keypad

class KillSwitch:

    def __init__(self, onKillSwitchDoneWatchingFor5SecondsCb):
        """You should pass in a callback that's called once we are done watching
        for the kill switch. This means you'll get a callback roughly 5 seconds later."""

        print("Initting Kill Switch library...")
        self._pinKillSwitchPin = board.IO1

        # User should pass in a callback function so we can call it
        # upon button press and release
        self.onKillSwitchDoneWatchingFor5SecondsCb = onKillSwitchDoneWatchingFor5SecondsCb

    def onKillSwitchBeingOn(self):

        import sys
        print("Exiting due to kill switch")
        sys.exit()

    async def asyncTaskWatchKillSwitch(self):

        with keypad.Keys((self._pinKillSwitchPin,), interval=0.2, value_when_pressed=False, pull=True) as keys:
            print("Starting kill switch listen 5 second loop")
            while True:
                event = keys.events.get()
                if event:
                    if event.pressed:
                        # print("pin went low.")
                        if self.onKillSwitchDoneWatchingFor5SecondsCb != None:
                            print("Calling onKillSwitchDoneWatchingFor5SecondsCb cb.")
                            self.onKillSwitchDoneWatchingFor5SecondsCb()
                await asyncio.sleep(0.2)

def testOnKillSwitchCb():
    print("Got kill switch callback")

async def test():
    ks = KillSwitch(testOnKillSwitchCb)
    killswitch_task = asyncio.create_task(ks.asyncTaskWatchKillSwitch())
    await asyncio.gather(killswitch_task)

asyncio.run(test())