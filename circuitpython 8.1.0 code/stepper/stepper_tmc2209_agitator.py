# The Liberty Christian Stepper Motor Library for CircuitPython
import digitalio
import board
import time
import asyncio
import pwmio

class StepperAgitator:
    def __init__(self, *args):

        print("Initting Agitator Stepper library...")
        self._pinEnablePin = board.IO13
        self._pinDirPin = board.IO14
        self._pinStepPin = board.IO15
        self._pinDiagPin = board.IO16

        self._minPulseWidth = 0.00055 #0.001 #0.00055

        # open pins
        self._pinEnable = digitalio.DigitalInOut(self._pinEnablePin)
        self._pinEnable.direction = digitalio.Direction.OUTPUT
        self._pinDir = digitalio.DigitalInOut(self._pinDirPin)
        self._pinDir.direction = digitalio.Direction.OUTPUT
        self._pinStep = digitalio.DigitalInOut(self._pinStepPin)
        self._pinStep.direction = digitalio.Direction.OUTPUT
        self._pinDiag = digitalio.DigitalInOut(self._pinDiagPin)
        self._pinDiag.direction = digitalio.Direction.INPUT

        # ensure disabled since GND=on and default state of pin is GND, thus drive would be on
        self.disable()

        # ensure fwd
        self.fwd()

        # For our async spin method, let's create a boolean that we can watch
        # so if it becomes True, we can exit the async process
        self._isAsyncSpinning = False

        # print vals of pins on init
        self.dump()

        # Set the force stop to false so we keep our rockAsyncTask running from the get go
        # Set to true to force exit the infinite loop
        self._isAsyncForceStop = False

    def dump(self):
        # print vals of pins on init
        print("---DUMP----")
        print("Enable:", self._pinEnable.value)
        print("Dir:", self._pinDir.value)
        print("Step:", self._pinStep.value)
        print("Diag:", self._pinDiag.value)
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

    def getDir(self):
        return self._pinDir.value
    
    def dir(self, d):
        if self._pinDir.value != d:
            print("Setting dir to:", d)
            self._pinDir.value = d

    def fwd(self):
        if self._pinDir.value != True:
            print("Going fwd")
            self._pinDir.value = True

    def rev(self):
        if self._pinDir.value != False:
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
        print("Deinitted")

    def rockAsyncStop(self):
        self._isAsyncSpinning = False

    def rockAsyncStart(self):
        self._isAsyncSpinning = True

    def rockAsyncForceStop(self):
        self._isAsyncForceStop = True

    async def rockAsyncTask(self):
        """This method starts an infinite loop task to rock the stepper motor. Rocking the motor
        means we start pointing down on the flapper, then move forward 45 degrees fwd, then move
        back (rev) to start. Then move reverse 45 degrees. Then move back to start. This should 
        happen in sync with each pick up of a marble by the scoopers.
        It does not actually rock the motor when first called, rather just starts the watch loop.
        To start rocking the motor, call rockAsyncStart(). To stop rocking the motor, call
        rockAsyncStop()."""

        print("Starting infinite async rocker task...")

        self._isAsyncForceStop = False

        # This stepper motor is 1.8deg per step
        # That means 360/1.8 = 200 steps per revolution
        # 45 degrees = 45/1.8 = 25 steps
        # We are at 8 microsteps, so multiply all by 8
        # 45 degrees = 45/1.8 = 25 steps * 8 = 200

        # We need some variables for speed/accel
        # ramp = []
        # Start accel from base position to pos 45 deg
        ramp = [
            {'pause':True, 'dur':0.1},
            {'pw':0.01, 'steps':45, 'dir':True},  # Fwd
            {'pw':0.008, 'steps':45, 'dir':True},
            {'pw':0.006, 'steps':45, 'dir':True},
            # max speed
            {'pw':0.004, 'steps':45*3, 'dir':True},
            {'pw':0.004, 'steps':45*3, 'dir':True},
            # Slow down to end of 1st 45 degree swing
            {'pw':0.006, 'steps':45, 'dir':True},
            {'pw':0.008, 'steps':45, 'dir':True},
            {'pw':0.01, 'steps':45, 'dir':True},
            # Pause at top of 45 deg
            {'pause':True, 'dur':0.1},
            # Start accel back towards base
            {'pw':0.01, 'steps':45, 'dir':False}, # Rev
            {'pw':0.008, 'steps':45, 'dir':False},
            {'pw':0.006, 'steps':45, 'dir':False},
            # max speed
            {'pw':0.004, 'steps':45*3, 'dir':False},
            {'pw':0.004, 'steps':45*3, 'dir':False},
            # Slow down to end of 1st 45 degree swing back to base
            {'pw':0.006, 'steps':45, 'dir':False},
            {'pw':0.008, 'steps':45, 'dir':False},
            {'pw':0.01, 'steps':45, 'dir':False},
            # Pause at base
            {'pause':True, 'dur':0.1},
            # Start accel from base position to neg 45 deg
            {'pw':0.01, 'steps':45, 'dir':False}, # Fwd
            {'pw':0.008, 'steps':45, 'dir':False},
            {'pw':0.006, 'steps':45, 'dir':False},
            # max speed
            {'pw':0.004, 'steps':45*3, 'dir':False},
            {'pw':0.004, 'steps':45*3, 'dir':False},
            # Slow down to end of 1st 45 degree swing
            {'pw':0.006, 'steps':45, 'dir':False},
            {'pw':0.008, 'steps':45, 'dir':False},
            {'pw':0.01, 'steps':45, 'dir':False},
            # Pause at top of neg 45 deg
            {'pause':True, 'dur':0.1},
            # Start accel back towards base
            {'pw':0.01, 'steps':45, 'dir':True}, # Rev
            {'pw':0.008, 'steps':45, 'dir':True},
            {'pw':0.006, 'steps':45, 'dir':True},
            # max speed
            {'pw':0.004, 'steps':45*3, 'dir':True},
            {'pw':0.004, 'steps':45*3, 'dir':True},
            # Slow down to end of 2nd 45 degree swing back to base
            {'pw':0.006, 'steps':45, 'dir':True},
            {'pw':0.008, 'steps':45, 'dir':True},
            {'pw':0.01, 'steps':45, 'dir':True},
            # Pause at base
            {'pause':True, 'dur':0.2}
        ]
        # # Continue loop...
        
        # Loop index variable
        liv = 0

        while True and self._isAsyncForceStop == False:

            # print("in while loop of rockAsyncTask. isAsyncSpinning:", self._isAsyncSpinning, "liv:", liv, "ramp[liv]:", ramp[liv])

            # each time through loop we should check if they want to start or stop steps
            if self._isAsyncSpinning:

                # Let's see if we're in a pause mode or a step mode
                if 'pause' in ramp[liv]:

                    # They want a pause
                    print("Pausing for dur:", ramp[liv]['dur'])
                    await asyncio.sleep(ramp[liv]['dur'])

                else:

                    # They want a step move. We are given steps so do a range
                    print("Doing range of steps:", ramp[liv]['steps'], "pw:", ramp[liv]['pw'], "dir:", ramp[liv]['dir'])
                    
                    # Set the direction
                    self.dir(ramp[liv]['dir'])
                    # if ramp[liv].dir and :
                    #     self.fwd()
                    # else:
                    #     self.rev()

                    for x in range(ramp[liv]['steps']):

                        # print("doing a step")
                        # They want spin, so do a step
                        self._pinStep.value = True
                        # Let another task run for our pulsewidth
                        await asyncio.sleep(self._minPulseWidth)
                        # await asyncio.sleep(ramp[liv]['pw'] * 0.1)
                        
                        self._pinStep.value = False
                        # Let another task run for our pulsewidth
                        await asyncio.sleep(ramp[liv]['pw'] * 0.1)

                        # during debug wait a long time
                        # await asyncio.sleep(2)

                # Increment loop index variable
                liv += 1

                # See if we went past end of array
                if liv >= len(ramp):
                    print("Going back to start of ramp array. liv:", liv)
                    liv = 0

            else:
                # print("not doing a step")

                # They don't want spin so skip and yield to other events
                # wait a decent amount of time to not overload the system
                await asyncio.sleep(0.1)

        # They want to fully exit this infinite loop
        print("Exiting the rockAsyncTask infinite loop")
            

    async def rockAsyncExitTimer(self, duration):
        print("Starting rock timer")
        self.rockAsyncStart()
        await asyncio.sleep(duration) # don't forget the await
        self.rockAsyncStop()  # This just stops the steps from executing, not the infinite loop
        self.rockAsyncForceStop() # This forces the infinite loop to exit
        print("Ended rock timer")


            
# Test Code

async def testAsyncRock():
    print("Testing agitator async spin")
    s = StepperAgitator()
    s.enable()
    # start spinning
    rock_task = asyncio.create_task(s.rockAsyncTask())
    # spin for 5 seconds
    exit_task = asyncio.create_task(s.rockAsyncExitTimer(60*10))

    await asyncio.gather(rock_task, exit_task)

    print("Disabling stepper and deinnitting.")
    s.disable()
    s.deinit()

# test()
asyncio.run(testAsyncRock())

