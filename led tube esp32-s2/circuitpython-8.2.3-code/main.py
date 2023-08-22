import touchio
import board
import asyncio
import microcontroller
import neopixel
import supervisor

class Main:
    def __init__(self):

        print("Initting main code")

        # This is threshold for the touch sensors whereby if the raw_value
        # goes above the configured value on boot up, it triggers a touch
        # The default is 100
        self.threshold = 60

        # Base brightness of blue color that shows across whole strip while idel
        self.baseBlue = 5
        
        # We will create the task later in the process
        self.touch_watcher_task = None # asyncio.create_task(self.asyncTouchWatcherTask())

        # Setup LEDs
        pixel_pin = board.IO21
        self.num_pixels = 28

        self.pixels = neopixel.NeoPixel(pixel_pin, self.num_pixels, brightness=1.0, auto_write=False, pixel_order=neopixel.GRB)

        self.RED = (255, 0, 0)
        self.YELLOW = (255, 150, 0)
        self.GREEN = (0, 255, 0)
        self.CYAN = (0, 255, 255)
        self.BLUE = (0, 0, 255)
        self.PURPLE = (180, 0, 255)
        self.BLACK = (0, 0, 0)

        

        # Run a color cycle startup sequence
        # self.color_cycle_task = asyncio.create_task(self.asyncRainbowCycleTask())

        # Create an async timer that reboots the ESP32-S2 every 8 hours
        # self.reboot_timer_task = asyncio.create_task(self.rebootTimer(20))  # 1 minute for testing
        self.reboot_timer_task = asyncio.create_task(self.rebootTimer(60*60*8)) # 8 hours
        
    def runStartupColors(self):

        pass

    def wheel(self, pos):
        
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        
        # print("pos:", pos)

        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b) #if self.ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


    async def asyncRainbowCycleTask(self):
        
        print("Starting rainbow cycle")
        
        # Do an async version of color cycling
        
        # Run 10 times
        for numLoops in range(1):
            
            print("Loop", numLoops)

            for j in range(0, 255, 10):
                # print("In rainbow cycle. j:", j)
                self.pixels.brightness = 1.0
                for i in range(self.num_pixels):
                    pixel_index = (i * 256 // self.num_pixels) + j
                    self.pixels[i] = self.wheel(pixel_index & 255)
                self.pixels.show()
                
                # sleep 0.01 second per loop 
                await asyncio.sleep(0.00000)

        print("Done running rainbow cycle")

    def dumpAllThresholdVals(self):
        
        for i in range(14):
            print("Touch", i+1, ", Raw:", self.touch[i].raw_value, "Thresh:", self.touch[i].threshold)

    def setupTouchButtons(self):
        
        print("Setting up touch buttons...")

        # Setup touch buttons
        self.touch = []
        for i in range(14):
            # self.touch.append(1) 
            pinStr = "board.IO" + str(i+1)
            # print("Creating touch pin:", pinStr)
            self.touch.append(
                touchio.TouchIn(eval(pinStr))
            )

            # Set threshold lower than the default 100 for each one
            # So remove the 100 that Adafruit added, then add our own
            self.touch[i].threshold = self.touch[i].threshold - 100 + self.threshold
       
    async def runThresholdTest(self):

        # We are going to run a test where we keep track of the max, min, avg, numSamples of each
        # of the 14 touch sensors
        
        d = []

        for i in range(14):

            # create data entry
            d.append({
                "min": None,
                "max": None,
                "runTot": None,
                "numSamples": 0
            })
            print("d[" + str(i) + "]", d[i])

            for testCtr in range(10):
                # run 10 tests
                raw = self.touch[i].raw_value
                
                # see if first time thru
                if d[i]["min"] == None:
                    # it is first time thru, so just set raw to all min, max, and avg
                    d[i]["min"] = d[i]["max"] = d[i]["runTot"] = raw

                else:

                    if raw < d[i]["min"]:
                        d[i]["min"] = raw

                    if raw > d[i]["max"]:
                        d[i]["max"] = raw

                    # set avg
                    d[i]["runTot"] += raw

                d[i]["numSamples"] += 1

                await asyncio.sleep(0.1)

        # Now dump test
        print("Indx", "Min", "Max", "RunTot", "Avg", "NumSamp")
        for i in range(14):
            print(i, d[i]["min"], d[i]["max"], d[i]["runTot"], 0,  d[i]["numSamples"])

    def showGreenLeds(self):

        self.pixels.fill(self.GREEN)
        self.pixels.show()

    def showRedLeds(self):

        self.pixels.fill(self.RED)
        self.pixels.show()

    def showPurpleLeds(self):

        self.pixels.fill(self.PURPLE)
        self.pixels.show()

    def show2YellowLeds(self):

        self.pixels[0] = self.YELLOW
        self.pixels[27] = self.YELLOW
        self.pixels.show()

    async def asyncTouchWatcherTask(self):
        print("Starting infinite async touch watcher loop")

        self.pixels.fill((0,0,self.baseBlue))
        self.pixels.show()

        # The amount of color in each of the rgb to decrement each time thru loop if touch is not present
        # This means if there was a prior touch you'll get a slow fade from the original full brightness on
        # those particular pixels
        decrementPerStep = 3

        # Define our dirty var so it's not instantiated each time thru loop
        # this is for extra loop speed
        isDirty = False 

        while True:

            # print("In touch watcher async loop, checking on touch state...")

            # Fade to black incrementally each time thru loop
            # self.pixels.brightness = self.pixels.brightness - 0.0000001

            isDirty = False

            for i in range(14):

                if self.touch[i].value:

                    isDirty = True

                    # print("touch1")
                    # self.pixels.brightness = 1.0
                    self.pixels[i*2] = (0,0,255)
                    self.pixels[(i*2) + 1] = (0,0,255)
                    # self.pixels.fill(self.BLUE)
                    # self.pixels.show()
                
                else:

                    # see if we need a change
                    curBlue = self.pixels[i*2][2]
                    if curBlue > self.baseBlue:

                        isDirty = True

                        # just change blue since that's all we're doing
                        newBlue = curBlue - decrementPerStep
                        if newBlue < self.baseBlue:
                            newBlue = self.baseBlue
                        self.pixels[i*2] = (0, 0, newBlue)
                        self.pixels[(i*2) + 1] = (0, 0, newBlue)

            if isDirty:
                self.pixels.show()    
            else:
                # do nothing if nothing is dirty, that way we loop faster
                # so we can pick up touches faster
                pass

            # sleep 1 second 
            await asyncio.sleep(0.000001) 
            # await asyncio.sleep(0.001) 

    async def rebootTimer(self, duration):
        print("Starting reboot timer. Duration (secs):", duration)
        
        await asyncio.sleep(duration) # don't forget the await
        
        print("Rebooting manually")
        
        # Show some yellow led's to indicate reboot timer in case something goes weird
        self.show2YellowLeds()

        # Rebooting
        microcontroller.reset()

        print("Ended reboot timer")

    async def asyncDelayTask(self, delay):
        
        print("Starting delay task for delay:", delay)
        
        # sleep 0.01 second per loop 
        await asyncio.sleep(delay)

        print("Done running delay task")

async def main():

    

    # if we made it here we did not get rebooted
    m = Main()

    # f = await asyncio.wait_for(
    #     m.color_cycle_task
    # )

    # Run this first to show boot up
    asyncio.run(m.asyncRainbowCycleTask())

    # We seem to be getting weirdness on the touch threshold
    # So, let's do a delay at boot to let things settle down, then
    # continue on with turning on touch buttons
    m.showRedLeds()
    asyncio.run(m.asyncDelayTask(1))

    # Show green that we're go
    m.showGreenLeds()
    
    # Setup touch buttons
    # We do this after the rainbow cycle so things settle down on the ESP32 so our threshold read
    # that occurs during setup is the most accurate to the standing capacitance levels
    m.setupTouchButtons()

    # Dump all the threshold vals for debug
    m.dumpAllThresholdVals()
    # asyncio.run(m.runThresholdTest())

    # Now create the touch task
    m.touch_watcher_task = asyncio.create_task(m.asyncTouchWatcherTask())

    # if this is our first power_on then do a reboot from software
    # for some reason we are getting hung up on first power on when just using
    # 24v to 5v DC DC converter, so this is a workaround to reboot from software
    # which seems to fix the problem
    if microcontroller.cpu.reset_reason == microcontroller.ResetReason.POWER_ON:

        print("Rebooting cuz first time power up, so hopefully reboot clears things up")
        m.showPurpleLeds()
        # Rebooting
        microcontroller.reset()
        
    # Then run the infinite loops
    await asyncio.gather(
        # m.color_cycle_task
        m.touch_watcher_task,
        m.reboot_timer_task
    )  # Don't forget the await!
    
    print("done with main")

asyncio.run(main())
