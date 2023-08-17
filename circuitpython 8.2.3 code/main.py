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

        # Create our display hardware object so we spit out our IP address to display
        import display.display
        d = display.display.Display()

        print("Kill switch is on, so exiting code.")

        # Make sure steppers are off
        from stepper.stepper_tmc2209_pwm import Stepper as StepperElevator
        from stepper.stepper_tmc2209_pa_pwmagitator import StepperAgitator

        se = StepperElevator()
        se.disable()

        sa = StepperAgitator()
        sa.disable()

        # Ok, now that we're safe with steppers off, continue...
        r.logToFileWithWifi("From main.py. Kill switch on.")

        # Dump log file
        r.dumpLogFile()

        # Temporarily dish over to AdafruitIO test
        # import adafruitio.test_adafruit

        # Temporarily test wifi watcher
        from wifi.watcher import WifiWatcher
        import asyncio
        async def testAsyncTask():

            # Create our display hardware object
            ww = WifiWatcher()

            ww_task = asyncio.create_task(ww.asyncWifiWatcherTask())

            await asyncio.gather(ww_task)

            print("Done watching wifi")

        asyncio.run(testAsyncTask())

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