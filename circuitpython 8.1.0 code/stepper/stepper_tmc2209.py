# The Liberty Christian Stepper Motor Library for CircuitPython
import digitalio
import board
import time
import asyncio

class Stepper:
    def __init__(self, *args):

        print("Initting Stepper library...")
        self._pinEnablePin = board.IO5
        self._pinDirPin = board.IO6
        self._pinStepPin = board.IO7
        self._pinDiagPin = board.IO8
        self._pinMs1Pin = board.IO9
        self._pinMs2Pin = board.IO15

        self._minPulseWidth = 0.001 #0.00055

        # open pins
        self._pinEnable = digitalio.DigitalInOut(self._pinEnablePin)
        self._pinEnable.direction = digitalio.Direction.OUTPUT
        self._pinDir = digitalio.DigitalInOut(self._pinDirPin)
        self._pinDir.direction = digitalio.Direction.OUTPUT
        self._pinStep = digitalio.DigitalInOut(self._pinStepPin)
        self._pinStep.direction = digitalio.Direction.OUTPUT
        self._pinDiag = digitalio.DigitalInOut(self._pinDiagPin)
        self._pinDiag.direction = digitalio.Direction.INPUT

        # set ms1/ms2 pins to gnd to do 8 microsteps
        self._pinMs1 = digitalio.DigitalInOut(self._pinMs1Pin)
        self._pinMs1.direction = digitalio.Direction.OUTPUT
        self._pinMs1.value = False #GND
        # self._pinMs1.pull = digitalio.Pull.DOWN
        self._pinMs2 = digitalio.DigitalInOut(self._pinMs2Pin)
        self._pinMs2.direction = digitalio.Direction.OUTPUT
        self._pinMs2.value = False #GND
        # self._pinMs2.pull = digitalio.Pull.DOWN

        # ensure disabled since GND=on and default state of pin is GND, thus drive would be on
        self.disable()

        # ensure fwd
        self.fwd()

        # For our async spin method, let's create a boolean that we can watch
        # so if it becomes True, we can exit the async process
        self._isAsyncSpinning = False

        # print vals of pins on init
        self.dump()

    def dump(self):
        # print vals of pins on init
        print("---DUMP----")
        print("Enable:", self._pinEnable.value)
        print("Dir:", self._pinDir.value)
        print("Step:", self._pinStep.value)
        print("Diag:", self._pinDiag.value)
        print("MS1:", self._pinMs1.value)
        print("MS2:", self._pinMs2.value)
        print("-------")

    def step(self):
        
        # print("Stepping...")
        self._pinStep.value = True
        time.sleep(self._minPulseWidth)
        self._pinStep.value = False
        time.sleep(self._minPulseWidth)

    def steps(self, cnt):
        print("Stepping", cnt, "steps...")
        for i in range(cnt):
            self.step()
        print("Done stepping", cnt, "steps")

    # Do steps, but enable/disable as part of it
    def stepsEnDis(self, cnt):
        self.enable()
        print("Enabling. Stepping", cnt, "steps...")
        for i in range(cnt):
            self.step()
        self.disable()
        print("Disabled. Done stepping", cnt, "steps")

    def enable(self):
        # Enable Motor Outputs (GND=on, VIO=off)
        # enable driver
        self._pinEnable.value = False 
        # self._pinEnable.pull = digitalio.Pull.DOWN
        print("Enabled")

    def disable(self):
        # Enable Motor Outputs (GND=on, VIO=off)
        # enable driver
        self._pinEnable.value = True 
        # self._pinEnable.pull = digitalio.Pull.UP
        print("Disabled")

    def fwd(self):
        print("Going fwd")
        self._pinDir.value = True

    def rev(self):
        print("Going rev")
        self._pinDir.value = False

    def setMinPulseWidth(self, seconds):
        print("Set min pulse width:", seconds)
        self._minPulseWidth = seconds

    def deinit(self):
        self._pinEnable.deinit()
        self._pinDir.deinit()
        self._pinStep.deinit()
        self._pinDiag.deinit()
        self._pinMs1.deinit()
        self._pinMs2.deinit()
        print("Deinitted")

    def spinAsyncStop(self):
        self._isAsyncSpinning = False

    def spinAsyncStart(self):
        self._isAsyncSpinning = True

    async def spinAsync(self):
        """NOT USING CURRENTLY. This method will spin the stepper motor as fast as it can, but in an async way."""
        # set this bool to True, because if we're getting called then user wants a spin
        # the user has to call Stepper.spinAsyncStop() to exit out of this
        self._isAsyncSpinning = True

        print("Starting async spin...")
        while self._isAsyncSpinning == True:
            self._pinStep.value = True
            # Let another task run.
            await asyncio.sleep(self._minPulseWidth)
            
            self._pinStep.value = False
            # Let another task run.
            await asyncio.sleep(self._minPulseWidth)
        
        print("Exiting out of async spin")

    async def spinAsyncTask(self):
        """This method starts an infinite loop task to spin the stepper motor.
        It does not actually spin the motor when first called, rather just starts the watch loop.
        To start the motor call spinAsyncStart(). To stop the motor call
        spinAsyncStop()."""

        print("Starting infinite async spin task...")
         
        while True:

            # print("in while loop of spinAsyncTask. isAsyncSpinning:", self._isAsyncSpinning)

            # each time through loop we should check if they want to start or stop steps
            if self._isAsyncSpinning:

                # print("doing a step")
                # They want spin, so do a step
                self._pinStep.value = True
                # Let another task run.
                await asyncio.sleep(self._minPulseWidth)
                
                self._pinStep.value = False
                # Let another task run.
                await asyncio.sleep(self._minPulseWidth)

                # during debug wait a long time
                # await asyncio.sleep(2)
            else:
                # print("not doing a step")

                # They don't want spin so skip and yield to other events
                await asyncio.sleep(0)

                # during debug wait a long time
                # await asyncio.sleep(2)

    async def spinAsyncExitTimer(self, duration):
        print("Starting timer")
        await asyncio.sleep(duration) # don't forget the await
        self.spinAsyncStop()
        print("Ended timer")
            
# Test Code
# def test():
#     import stepper
#     s = stepper.Stepper()

#     s.enable()

#     s.dump()

#     print("Step one")
#     s.step()
#     time.sleep(0.1)
#     print("Step two")
#     s.step()

#     # step multiple
#     s.steps(200)

#     s.disable()

#     # time.sleep(0.1)
#     s.dump()
#     s.deinit()

async def testAsyncSpin():
    print("Testing async spin")
    s = Stepper()
    s.enable()
    s.rev()
    # start spinning
    spin_task = asyncio.create_task(s.spinAsync())
    # spin for 2 seconds
    exit_task = asyncio.create_task(s.spinAsyncExitTimer(5))

    await asyncio.gather(spin_task, exit_task)

    s.disable()
    s.deinit()

# # test()
asyncio.run(testAsyncSpin())

