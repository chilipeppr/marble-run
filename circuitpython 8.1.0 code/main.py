# This file is the file initially loaded by the ESP-32 S2 CircuitPython
# We watch for a kill switch, i.e. a button on GPIO1, and if it's on we
# don't proceed with running the main program.

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
        # import display.display
        # d = display.display.Display()

        # Dump log file
        r.dumpLogFile()

        import main_kitchensink
        # import main_test_why_circuitpython_hardfaults

main()