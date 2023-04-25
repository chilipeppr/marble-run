"""This class will create a watchdog. It will setup an async task that feeds
the watchdog. If the feed stops happening, the ESP32 will reboot. We will log
each reboot so we can see if the ESP32 is rebooting and at what interval since
I have seen it lock up after about 24 hours."""

from microcontroller import watchdog as w
from watchdog import WatchDogMode, WatchDogTimeout
import asyncio

class MarbleRunWatchdog:

    def __init__(self) -> None:
        
        print("Initting Watchdog...")

        w.timeout = 10 # Set a timeout of 10 seconds
        w.mode = WatchDogMode.RESET
        
        # w.mode = WatchDogMode.RAISE

    def logOnBoot(self):
        """This method creates a log entry that we just rebooted. This
        way we can review the log file to see how often we are rebooting.
        We will keep a timestamp so we can calculate."""
    
    async def asyncWatchdogTimer(self):
        print("Starting infinite async watchdog loop")
    
        # watchdog.mode = WatchDogMode.RAISE

        isLooping = True
        ctr = 0

        while isLooping:
            print("Going thru watchdog loop")

            w.feed()
            await asyncio.sleep(5) # don't forget the await

            ctr += 1
            if ctr > 5:
                isLooping = False
                print("Exiting watcdog timer due to count")

# Test Code

async def testAsyncWatchdog():

    print("Testing watchdog")

    w = MarbleRunWatchdog()
    
    watchdog_task = asyncio.create_task(w.asyncWatchdogTimer())

    await asyncio.gather(watchdog_task)

try:
    asyncio.run(testAsyncWatchdog())
except WatchDogTimeout as e:
    print("Watchdog expired. e:", e)
except Exception as e:
    print("Other watchdog loop exception. e:", e)
    w.deinit()   