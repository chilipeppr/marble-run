import board
import countio
import asyncio
import pwmio
import storage

class MarbleCounter:

    def __init__(self, callbackOnMarbleCount=None) -> None:
        
        # store the callback method that the user gave us that we call
        # when we get a marble increment count
        self.cbOnMarbleCount = callbackOnMarbleCount

        self.pinListenNum = board.IO4

        # Count rising edges only.
        self.pinCtrObj = countio.Counter(self.pinListenNum, edge=countio.Edge.RISE)

        # Keep track of step counts
        self.leftoverStepCtr = 0

        # Keep track of total marbles vended
        self.marbleCtr = 0

        self.fileNameMarbleCtr = "marblectr.txt"

        # Now, re-read in the marble count from disk
        # Make sure to create this file with a 0 and no newline
        self.loadMarbleCountFromDisk()

        # How long to wait between marble count write to disk
        self.intervalSecsWriteMarbleCtrToDisk = 60 * 60 # 1 hour

        # Remount so CircuitPython can write to the drive
        storage.remount("/", readonly=False)

    def loadMarbleCountFromDisk(self):

        # We will occasionally write the marble count to disk, so when we load
        # we should try to get a marble count from disk so we can have a better ongoing
        # count of marbles launched, since we know the device will reboot often
        f = open(self.fileNameMarbleCtr, "r")
        line = f.readline()
        self.marbleCtr = int(line)
        f.close()

        print("Loaded previous marble count from disk:", self.marbleCtr)

        self.cbOnMarbleCount(self.marbleCtr)

    def writeMarbleCountToDisk(self):

        # We will get called occasionally from the flush task to write the latest
        # marble count to disk
        f = open(self.fileNameMarbleCtr, "w")
        f.write(str(self.marbleCtr))
        f.flush()
        f.close()

    async def asyncTaskWriteMarbleCountToDiskEveryHour(self):

        # We write every hour so that we don't kill the flash drive. 
        # 24 hrs per day * 365 = 8,760 writes per year.
        # So start an infinite loop and write to disk on each hour interval
        
        while True:

            self.writeMarbleCountToDisk()

            # await asyncio.sleep(60*60) # do every hour
            await asyncio.sleep(self.intervalSecsWriteMarbleCtrToDisk) # do every hour
            print("Just wrote marble count to disk. marbleCtr:", self.marbleCtr)

    async def asyncTaskCountSteps(self): 
        """We create an infinite loop task to watch the pin counter. When we loop,
        we take the newStepsCtr we just got on the pin + the leftoverCtr from the previous 
        time through the loop (if any), 
        then divide those steps by what it takes for one marble to be vended (200 steps) 
        to get the new marbles launched, 
        keep track of the leftover step count for next time thru the loop, 
        then reset the pin counter back to zero.
        
        The math to figure out how many steps it takes to launch one marble is:
        It is 8 microsteps per full step. It takes 200 full steps to do a full rotation of
        the stepper motor. The pulley is 320mm. It takes 80mm to get one marble launched.
        Thus it takes 1/4 of a turn of the pulley for one
        marble. Thus it takes 50 full steps. So 50*8 = 400 microsteps to get one marble.
        So, each 400 microsteps from our countio pin counter, is one marble launched.
        """

        while True: 

            # Get our latest pin ctr
            newStepsCtr = self.pinCtrObj.count

            if newStepsCtr > 0:

                # Immediately reset it so we lose as little step count as possible
                self.pinCtrObj.reset()

                # If we had any leftovers from last time thru loop, add them here
                # We will reset the new leftoverStepCtr at the end
                totalStepsCtr = newStepsCtr + self.leftoverStepCtr

                # keep track of last marble count so we know if we got an increase, cuz
                # if we did then call their callback method
                lastMarbleCtr = self.marbleCtr

                # Get integer value of marbles by modding.
                newIncrementalMarbleCtr = totalStepsCtr // 400  # 50 full steps for one marble * 8 microsteps

                # Figure out our remainder
                newLeftoverStepsCtr = totalStepsCtr - (newIncrementalMarbleCtr * 400)

                print("newStepsCtr:", newStepsCtr, "newIncrementalMarbleCtr:", newIncrementalMarbleCtr, "newLeftoverStepsCtr:", newLeftoverStepsCtr, "Prev marbleCtr:", self.marbleCtr, "Prev leftoverStepsCtr:", self.leftoverStepCtr)

                # Add our new marbles counted to overall marble counter
                self.marbleCtr += newIncrementalMarbleCtr

                # Reset our leftover steps ctr for next time thru this loop
                self.leftoverStepCtr = newLeftoverStepsCtr

                # Now, see if we should call their callback
                # print("Testing is self.marbleCtr > lastMarbleCtr. self.marbleCtr:", self.marbleCtr, "lastMarbleCtr:", lastMarbleCtr)
                if self.marbleCtr > lastMarbleCtr:
                    # yes, we had an increment
                    # print("Calling cbOnMarbleCount as we had marble increase. self.marbleCtr:", self.marbleCtr, "lastMarbleCtr:", lastMarbleCtr)
                    if self.cbOnMarbleCount != None:
                        self.cbOnMarbleCount(self.marbleCtr)
                        # print("Called")

                # a pause of 0.4 is roughly coinciding with the max frequency we run the stepper at
                # so we should go thru this loop about once each time we think there's a marble
                # when the accel/decel is going then we won't get a marble increment each time but that's
                # totally fine cuz this loop would just not generate a callback to update the display
                await asyncio.sleep(0.4) # do every second
            
            else:

                # wait longer if there's no button pressed
                # this means we could lag on first press of button, but this will help slow down how much
                # watching and calculating we're doing if we don't think there are marbles launching
                await asyncio.sleep(2)

    def reset(self):
        self.pinCtrObj.reset()
        print("Reset pin counter")

# Tests

# freqGen = None
# def turnOnTestFrequency():

#     # setup pinStep as PWM output
#     freqGen = pwmio.PWMOut(
#         board.IO7, 
#         frequency=500, # Not allowed to set to 0, so use duty_cycle as our method of turning off stepper
#         duty_cycle=2 ** 15,  # Cycles the pin with 50% duty cycle (half of 2 ** 16) 
#         variable_frequency=True
#         )
#     print("Turned on frequency:", freqGen.frequency, "duty:", freqGen.duty_cycle)

# def onMarbleCount(ctr):
#     print("Got onMarbleCount. ctr:", ctr)

# async def testAsyncCountSteps():

#     # Create our display hardware object
#     mc = MarbleCounter(onMarbleCount)

#     turnOnTestFrequency()

#     count_task = asyncio.create_task(mc.asyncTaskCountSteps())
#     write_marblectr_todisk_task = asyncio.create_task(mc.asyncTaskWriteMarbleCountToDiskEveryHour())

#     await asyncio.gather(count_task, write_marblectr_todisk_task)

#     print("Done counting steps")

# asyncio.run(testAsyncCountSteps())
