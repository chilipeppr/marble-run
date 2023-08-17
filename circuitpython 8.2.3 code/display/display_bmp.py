"""
This object will iterate over all of the splash screens we have available.
It will also display the info screens when the button is pressed like:
    - Accel Screen
    - Max Speed Screen
    - Decel Screen
Including updating the screen with a counter if we are passed that data.
If we are passed the counter and something other than Accel/Max/Decel are
showing then we won't put the counter on the screen.

All sending to the display should happen thru this object. If you want to add
other features to show on the display, then add methods here and perhaps add
more groups/tile_grids to the layout.
"""

from display.display import Display
import displayio
import asyncio
from adafruit_display_text import label
import terminalio

class DisplayBmp:
    def __init__(self, display, *args):

        print("Initting DisplayBMP library...")

        # Keep track of the display they passed into us on init()
        self.display = display

        # This will setup our UI layout on our display for our main bitmap background
        # and our text label for the marble counter
        self.setupDisplay()

        # This bool keeps track of whether an info screen is showing like accel/max/decel
        # or if just a splash screen is showing. If this bool is set to true, the async
        # task that iterates the splash screens yields for us and won't overwrite our info screens
        self.isInfoScreenShowing = False

        # Keep track of marbleCtr so we can show it in lieu of being sent an update
        # from an external object
        self.marbleCtr = 0

    def setupDisplay(self):
        # Setup the file as the bitmap data source
        bitmap = displayio.OnDiskBitmap("/images/title.bmp")

        # Create a TileGrid to hold the bitmap
        self.tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)

        # Create a Group to hold the TileGrid
        self.group = displayio.Group()

        # Add the TileGrid to the Group
        self.group.append(self.tile_grid)

        # Set text, font, and color
        text = "9,999,999"
        font = terminalio.FONT
        color = 0xffffff

        # Create the text label
        self.text_area = label.Label(font, text=text, color=color)
        
        # Set the location
        self.text_area.x = 5
        self.text_area.y = 56

        # Add the Label to the Group
        self.group.append(self.text_area)

        # Add the Group to the Display
        self.display.show(self.group)

        self.wipeCounter()

    def loadBmp(self, file):

        # Setup the file as the bitmap data source
        bitmap = displayio.OnDiskBitmap(file)
        self.tile_grid.bitmap = bitmap

    """Call this method with a marble counter value and it will be
    updated on the display, if an info screen is showing. You can call
    this all you want from a countio pin counter and we will take care
    of whether to show it on the screen or not."""
    def updateCounter(self, ctr):
        
        # store for later
        self.marbleCtr = ctr 

        if self.isInfoScreenShowing:
            self.text_area.text = f'{ctr:,}' #str(ctr)
        else:
            # Hide ctr by setting label to empty
            self.text_area.text = ""

    def wipeCounter(self):
        self.text_area.text = ""

    def showTitle(self):
        print("Showing Title")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/title.bmp")

    def showPushBtn(self):
        print("Showing Push Button to Launch Marbles")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/pushbtn.bmp")

    def showLogo(self):
        print("Showing Logo")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/logo.bmp")

    def showDonation(self):
        print("Showing Donation Screen")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/donation.bmp")

    def showInspire(self):
        print("Showing Inspiration Reason")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/inspire.bmp")

    def showBday(self):
        print("Showing Born On Date")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/bday.bmp")

    def showLaunched(self):
        print("Showing Marbles Launched Counter")

        # Play some tricks here. Act as if we're a splash screen
        # but use the marble counter label as well, so show splash,
        # then manually update the marble counter
        self.isInfoScreenShowing = False
        self.updateCounter(self.marbleCtr)
        self.loadBmp("/images/launched.bmp")
        self.text_area.text = f'{self.marbleCtr:,}' #str(ctr)

    def showEsp32(self):
        print("Showing ESP32")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/esp32.bmp")

    def showTmc2209(self):
        print("Showing TMC2209")
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.loadBmp("/images/tmc2209.bmp")

    # If accel/max/decel are called, we should stop iterating the splash screens
    def showAccel(self):
        self.isInfoScreenShowing = True
        self.loadBmp("/images/accel.bmp")

    def showMax(self):
        self.isInfoScreenShowing = True
        self.loadBmp("/images/max.bmp")

    def showDecel(self):
        self.isInfoScreenShowing = True
        self.loadBmp("/images/decel.bmp")

    def showSplashScreensAgain(self):
        self.isInfoScreenShowing = False
        self.wipeCounter()
        self.showPushBtn()

    async def asyncTaskShowSplashScreens(self):

        # The order and duration of splash screens
        splashScreens = [
            {"func":self.showLaunched, "dur":8},
            {"func":self.showTitle, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showLogo, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showLaunched, "dur":8},
            {"func":self.showDonation, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showBday, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showLaunched, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showEsp32, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showTmc2209, "dur":4},
            {"func":self.showPushBtn, "dur":12},
            {"func":self.showInspire, "dur":6}
            ]

        lcv = 0
        while True:

            if self.isInfoScreenShowing:
                # An info screen is showing, so yield to that instead
                await asyncio.sleep(1)

            else:
                # show the image by calling the show func in the array
                # we should have a func for each screen
                splashScreens[lcv]["func"]()
                print("Just ran image func:", splashScreens[lcv])

                await asyncio.sleep(splashScreens[lcv]["dur"]) # don't forget the await

                # Increment image func to run
                lcv += 1

                if lcv >= len(splashScreens):
                    lcv = 0

        # we really should never get here
        print("Exiting asyncTaskShowMultiScreens. Should never get here.")

    async def asyncTaskRunCounter(self):

        myCtr = 0
        while True:

            myCtr += 1
            self.updateCounter(myCtr)
            print("myCtr:", myCtr)

            # for testing, let's show the info screen at increments
            remainder = myCtr % 50
            if remainder >= 10 and remainder <= 15:
                self.showAccel()

            elif remainder >= 16 and remainder <= 20:
                self.showMax()

            elif remainder >= 21 and remainder <= 25:
                self.showDecel()

            elif remainder == 26:
                # this would be like our stepper object saying it's done showing info screens
                self.showSplashScreensAgain()

            await asyncio.sleep(0.4) # don't forget the await

    def deinit(self):
        print("Deinnitting DisplayBMP")

# def test():

#     # Create our display hardware object
#     d = Display()
#     # Create bitmap display helper object. Pass in display to init().
#     dbmp = DisplayBmp(d.display)

#     dbmp.load("/images/pushbtn_4bit.bmp")
#     print("should be showing a bitmap now")

# async def testAsyncShowMultiScreens():

#     # Create our display hardware object
#     d = Display()
#     # Create bitmap display helper object. Pass in display to init().
#     dbmp = DisplayBmp(d.display)

#     display_task = asyncio.create_task(dbmp.asyncTaskShowSplashScreens())

#     ctr_task = asyncio.create_task(dbmp.asyncTaskRunCounter())

#     await asyncio.gather(display_task, ctr_task)

#     print("Done showing all the screens")
#     dbmp.deinit()
#     d.deinit()


# # test()
# asyncio.run(testAsyncShowMultiScreens())
