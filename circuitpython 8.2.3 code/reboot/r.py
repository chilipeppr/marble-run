"""This file will look at what the boot reason was for and then log it in a file."""

import supervisor
import microcontroller
from adafruit_datetime import datetime as adatetime
import storage

class RebootReason:

    def __init__(self) -> None:

        print("Running Reboot Reason")

        self.fileNameLog = "rebootreason.txt"

    def checkReason(self):

        print("Supervisor.runtime.run_reason:", supervisor.runtime.run_reason)
        # print("Supervisor.runtime.autoreload:", supervisor.runtime.autoreload)
        print("Supervisor.runtime.usb_connected:", supervisor.runtime.usb_connected)
        print("Microcontroller.Processor.reset_reason:", microcontroller.Processor.reset_reason)
        print("Microcontroller.cpu.reset_reason:",microcontroller.cpu.reset_reason)
        print("supervisor.runtime.safe_mode_reason:", supervisor.runtime.safe_mode_reason)
        
    def logToFile(self, prefix):

        # Remount so CircuitPython can write to the drive
        storage.remount("/", readonly=False)

        f = open(self.fileNameLog, "a")
        f.write(
            # "{} {}, supervisor.runtime.run_reason:{}, microcontroller.cpu.reset_reason:{}, supervisor.runtime.safe_mode_reason:{}\n".format(
            "{} {}, {}, {}, {}\n".format(
            prefix,
            adatetime.now(), 
            supervisor.runtime.run_reason, 
            microcontroller.cpu.reset_reason,
            supervisor.runtime.safe_mode_reason
        ))
        
        f.flush()
        f.close()

    def logToFileWithWifi(self, prefix):

        # Reset the datetime on the ESP32 from NTP since we have a network connection
        import rtc
        import socketpool
        import wifi
        import adafruit_ntp
        pool = socketpool.SocketPool(wifi.radio)
        ntp = adafruit_ntp.NTP(pool, tz_offset=-6 )

        # NOTE: This changes the system time so make sure you aren't assuming that time
        # doesn't jump.
        rtc.RTC().datetime = ntp.datetime

        # Do normal logging with correct timestamp
        self.logToFile(prefix)

    def dumpLogFile(self):

        # only dump the last 5 lines of the log file
        f = open(self.fileNameLog, "r")
        
        # get number of lines in file
        ctr = 0
        for line in f:
            ctr += 1
        f.close()
        print("Lines in log file:", ctr)

        # if ctr < 5 lines, then
        f = open(self.fileNameLog, "r")
        for line in f:
            ctr -= 1
            if ctr < 5:
                print(line)

        f.close()

    def d(self):

        self.dumpLogFile()

    def rebootToUf2Mode(self):

        microcontroller.on_next_reset(microcontroller.RunMode.UF2)
        microcontroller.reset()

    def rebootToSafeMode(self):

        microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
        microcontroller.reset()

    def rebootToNormalMode(self):

        microcontroller.on_next_reset(microcontroller.RunMode.NORMAL)
        microcontroller.reset()

    def rebootToBootLoaderMode(self):

        microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
        microcontroller.reset()


# reboot.r.RebootReason().checkReason()
# reboot.r.RebootReason().rebootToSafeMode()
# import reboot.r; reboot.r.RebootReason().dumpLogFile()
# import reboot.r; reboot.r.RebootReason().rebootToSafeMode()
# import reboot.r; reboot.r.RebootReason().rebootToNormalMode()

# rr = RebootReason()
# rr.checkReason()
# print("Dumping log file")
# rr.dumpLogFile()
# rr.logToFile()
# rr.logToFileWithWifi()
# print("Dumping log file after logging")
# rr.dumpLogFile()
