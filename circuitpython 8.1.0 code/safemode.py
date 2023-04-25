# This file is the file initially loaded by the ESP-32 S2 CircuitPython
# after booting into safemode. We're going to just log that we went into safemode
# and then do a full reboot back to normal mode. So, we're basically overriding this
# safety measure as we're in production and we know we have good code. So, I don't
# want to get the Marble Run into a state where it's not responding. I have seen
# reboots to safe mode after 24 hours and I'm not sure why, so just handle this by rebooting
# every night at midnight.

from killswitch.killswitch import KillSwitch
from reboot.r import RebootReason

def main():
    
    # Log the reboot reason
    r = RebootReason()

    ks = KillSwitch()

    if ks.isKillSwitchOn():
        print("Kill switch is on, so exiting code.")

        r.logToFile("From safemode.py. Kill switch on.")

        # Create our display hardware object so we spit out our IP address to display
        import display.display
        d = display.display.Display()

        # Dump log file
        r.dumpLogFile()

    else:
        print("Kill switch is not on, so proceeding with rebooting to normal mode...")

        r.logToFile("From safemode.py. Kill switch off.")

        # Create our display hardware object so we spit out our IP address to display
        import display.display
        d = display.display.Display()

        # Dump log file
        r.dumpLogFile()

        r.rebootToNormalMode()

main()