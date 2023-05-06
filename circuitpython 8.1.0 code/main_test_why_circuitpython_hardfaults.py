# This file will just run a simple asyncio infinite loop to see if that causes
# a hard fault after 24 hours.

import asyncio
import time
from adafruit_datetime import datetime as adatetime

class Dashboard:
    def __init__(self):

        print("Initting Dashboard")

        # Create several infinite loop tasks that loop each 0.01 to 0.5 seconds
        self.loop_task1 = asyncio.create_task(self.asyncTaskLoop("task1", 100, 0.1))
        self.loop_task2 = asyncio.create_task(self.asyncTaskLoop("task2", 50, 0.2))
        self.loop_task3 = asyncio.create_task(self.asyncTaskLoop("task3", 100, 0.1))
        self.loop_task4 = asyncio.create_task(self.asyncTaskLoop("task4", 20, 0.5))
        self.loop_task5 = asyncio.create_task(self.asyncTaskLoop("task5", 17, 0.6))
        self.loop_task6 = asyncio.create_task(self.asyncTaskLoop("task6", 100, 0.1))
        self.loop_task7 = asyncio.create_task(self.asyncTaskLoop("task7", 50, 0.2))
        self.loop_task8 = asyncio.create_task(self.asyncTaskLoop("task8", 100, 0.1))
        self.loop_task9 = asyncio.create_task(self.asyncTaskLoop("task9", 20, 0.5))
        self.loop_task10 = asyncio.create_task(self.asyncTaskLoop("task10", 17, 0.6))

    async def asyncTaskLoop(self, taskName, howOftenTellUsYouLooped, loopDelay):
        print("{}: Starting infinite loop".format(taskName))
        
        ctr = 0
        startTime = time.monotonic()

        while True:
            await asyncio.sleep(loopDelay) # don't forget the await

            ctr += 1
            if ctr > howOftenTellUsYouLooped:
                
                print("{} {}: Looped {} times waiting {}s on each loop. Should have taken {}s, but took {}s".format(
                    adatetime.now(), taskName, howOftenTellUsYouLooped, loopDelay, 
                    loopDelay*howOftenTellUsYouLooped, 
                    time.monotonic() - startTime))
                ctr = 0
                startTime = time.monotonic()
        

async def main():
    
    d = Dashboard()

    await asyncio.gather(
        d.loop_task1, d.loop_task2, d.loop_task3, d.loop_task4, d.loop_task5,
        d.loop_task6, d.loop_task7, d.loop_task8, d.loop_task9, d.loop_task10
    )  # Don't forget the await!

asyncio.run(main())
