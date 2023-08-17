# This class handles the kill switch on the Marble Run
# The user gets to toggle the kill switch and if it's off, the main code
# runs, but if it's on then the main.py code just exits so you can debug
#
# We are literally just doing one test here on boot. So this is very
# straightforward code.

import board
import digitalio

class KillSwitch:

    def __init__(self):

        print("Initting Kill Switch library...")
        self._pinKillSwitchPin = board.IO1

        self._pinKillSwitch = digitalio.DigitalInOut(self._pinKillSwitchPin)
        self._pinKillSwitch.switch_to_input(pull=digitalio.Pull.UP)

    def isKillSwitchOn(self):

        val = not self._pinKillSwitch.value
        print("KillSwitch:", val)
        return val      


# def test():
#     ks = KillSwitch()

#     if ks.isKillSwitchOn():
#         print("Kill switch is on, so exiting code.")
#     else:
#         print("Kill switch is not on, so proceeding with running massive main code...")

# test()