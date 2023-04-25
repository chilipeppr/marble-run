# This file is the file initially loaded by the ESP-32 S2 CircuitPython
# We need to watch for a kill switch and if we don't get it after 5 seconds
# we run our main code.

from killswitch.killswitch import KillSwitch
from reboot.r import RebootReason

def main():
    
    # Log the reboot reason
    r = RebootReason()

    ks = KillSwitch()

    if ks.isKillSwitchOn():
        print("Kill switch is on, so exiting code.")

        r.logToFileWithWifi("From main.py. Kill switch on.")

        # Create our display hardware object so we spit out our IP address to display
        import display.display
        d = display.display.Display()

        # Dump log file
        r.dumpLogFile()

    else:
        print("Kill switch is off, so proceeding with running massive main code...")

        r.logToFileWithWifi("From main.py. Kill switch off.")

        # Create our display hardware object so we spit out our IP address to display
        import display.display
        d = display.display.Display()

        # Dump log file
        r.dumpLogFile()

        import main_kitchensink

main()