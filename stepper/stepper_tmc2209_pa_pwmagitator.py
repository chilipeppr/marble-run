# The Liberty Christian Stepper Motor Library for CircuitPython
import digitalio
import board
import time
import asyncio
import pwmio

class StepperAgitator:
    def __init__(self, *args):

        print("Initting PWM Agitator Stepper library...")
        self._pinEnablePin = board.IO13
        self._pinDirPin = board.IO14
        self._pinStepPin = board.IO15
        self._pinDiagPin = board.IO16
        # self._pinMs1Pin = board.IO9
        # self._pinMs2Pin = board.IO15

        self._minPulseWidth = 0.001 #0.00055

        # open pins
        self._pinEnable = digitalio.DigitalInOut(self._pinEnablePin)
        self._pinEnable.direction = digitalio.Direction.OUTPUT
        self._pinDir = digitalio.DigitalInOut(self._pinDirPin)
        self._pinDir.direction = digitalio.Direction.OUTPUT
        self._pinDir.value = False
        self._pinDiag = digitalio.DigitalInOut(self._pinDiagPin)
        self._pinDiag.direction = digitalio.Direction.INPUT

        # setup pinStep as PWM output
        self.freqMin = 10   # we can't go below this (pwm hardware won't support it)
        self.freqMax = 200 #1000 # we can't go above as motor would turn too fast
        self.freqStep = 3 * 100 # since doing 0.1 sleep, if 0.01 sleep use 3  # when accel/decel on stepper this is the amount of ramp
        self._pinStep = pwmio.PWMOut(
            self._pinStepPin, 
            frequency=self.freqMax, # Not allowed to set to 0, so use duty_cycle as our method of turning off stepper
            duty_cycle=0, #2 ** 15,  # Cycles the pin with 50% duty cycle (half of 2 ** 16) 
            variable_frequency=True
            )
        # track our own frequency since the actual frequency of the pin ends up at a different number
        # than what we originally set it to, so our math gets screwed up unless we track on our own
        self.freq = self.freqMin

        # NOW just setting these pins to GND via wires, instead of using up ports
        # # set ms1/ms2 pins to gnd to do 8 microsteps
        # self._pinMs1 = digitalio.DigitalInOut(self._pinMs1Pin)
        # self._pinMs1.direction = digitalio.Direction.OUTPUT
        # self._pinMs1.value = False #GND
        # # self._pinMs1.pull = digitalio.Pull.DOWN
        # self._pinMs2 = digitalio.DigitalInOut(self._pinMs2Pin)
        # self._pinMs2.direction = digitalio.Direction.OUTPUT
        # self._pinMs2.value = False #GND
        # # self._pinMs2.pull = digitalio.Pull.DOWN

        # ensure disabled since GND=on and default state of pin is GND, thus drive would be on
        self.disable()

        # ensure fwd
        # self.fwd()
        # self.rev()

        # For our async spin method, let's create a boolean that we can watch
        # so if it becomes True, we can exit the async process
        self._isAsyncSpinning = False

        # print vals of pins on init
        self.dump()

        # setup a time.monotonic() so our diag check doesn't error out
        self._lastTimeDiagShown = time.time()

    def dump(self):
        # print vals of pins on init
        print("---AGITATOR DUMP----")
        print("Enable:", self._pinEnable.value)
        print("Dir:", self._pinDir.value)
        print("Step: Freq:", self._pinStep.frequency, "Duty:", self._pinStep.duty_cycle)
        print("Diag:", self._pinDiag.value)
        # print("MS1:", self._pinMs1.value)
        # print("MS2:", self._pinMs2.value)
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
        print("Agitator Enabled")

    def disable(self):
        # Enable Motor Outputs (GND=on, VIO=off)
        # enable driver
        self._pinEnable.value = True 
        # self._pinEnable.pull = digitalio.Pull.UP
        print("Agitator Disabled")

    def fwd(self):
        print("Agitator Going fwd")
        # self._pinDir.value = True
        self._pinDir.pull = digitalio.Pull.UP


    def rev(self):
        print("Agitator Going rev")
        # self._pinDir.value = False
        self._pinDir.pull = digitalio.Pull.DOWN


    def setMinPulseWidth(self, seconds):
        print("Set min pulse width:", seconds)
        self._minPulseWidth = seconds

    def deinit(self):
        self._pinEnable.deinit()
        self._pinDir.deinit()
        self._pinStep.deinit()
        self._pinDiag.deinit()
        # self._pinMs1.deinit()
        # self._pinMs2.deinit()
        print("Agitator Deinitted")

    def spinAsyncStop(self):
        self._isAsyncSpinning = False

    def spinAsyncStart(self):
        self._isAsyncSpinning = True

    async def spinAsyncTaskPwm(self):
        """This method starts an infinite loop task to spin the stepper motor.
        It does not actually spin the motor when first called, rather just starts the watch loop.
        To start the motor call spinAsyncStart(). To stop the motor call
        spinAsyncStop().
        
        This method is unique in that it's using PWM to generate the steps rather than a tight
        loop. It can also increase the frequency as it moves along and decrease the frequency
        as it stops."""

        print("Agitator Starting infinite async spin PWM task...")
        
        # define preFreq out here so it doesn't get recreated each time thru while loop
        prevFreq = -1

        while True:

            # print("in while loop of spinAsyncTask. isAsyncSpinning:", self._isAsyncSpinning)

            # Track previous frequency so we can make some comparisons in this loop
            # For example, we have these scenarios...
            
            # Prev          New     Desc
            # ------------- ------- ----------
            # INCREASING
            # 10 (minFreq)  20      1st turn on. Need to turn on duty cycle to 50%. Then set freq.
            # 20            30      Just increase freq
            # 5990          6000    Just increase freq
            # 6000 (maxFreq) 6000   Max check would have set to max so we don't overshoot. Leave at this.
            # DECREASING
            # 6000 (maxFreq) 5990   Just decrease freq
            # 20            10      Just decrease freq. Hit minFreq, but allow.
            # 10 (minFreq)  10      Went below minFreq. Min check would have set min so we don't overshoot.
            #                       Turn duty cycle to 0 to turn off motor.

            prevFreq = self.freq
                
            # each time through loop we should check if they want to start or stop steps
            if self._isAsyncSpinning:

                # They want increased speed
                # print("Increasing freq")

                if self.freq == self.freqMin and self._pinStep.duty_cycle == 0:
                    # 1st turn on. Need to turn on duty cycle to 50%. Then set freq.
                    self._pinStep.duty_cycle = 32768
                    self._pinStep.frequency = self.freq
                    print("Agitator 1st turn on. Setting duty to 50%. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency, "duty:", self._pinStep.duty_cycle)

                elif self.freq == self.freqMax:
                    # They are at max speed. So leave alone.
                    # print("At max freq. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency)
                    pass 

                elif self.freq > self.freqMax:
                    # They are at max speed. So leave alone.
                    # This is not really an error as the pwm subsystem doesn't always
                    # set at exactly the value you ask for.
                    # print("Agitator ERROR: self.freq is > than freqMax. Huh? This should never happen. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency)
                    pass 
                
                else:
                    # Just increase freq
                    self.freq = self.freq + self.freqStep
                    self._pinStep.frequency = self.freq
                    # print("Increase freq. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency)

            else:
                # print("Decreasing freq")
                
                if self.freq == self.freqMin:
                    # We need to stop motor by setting duty to 0
                    if self._pinStep.duty_cycle > 0:
                        self._pinStep.duty_cycle = 0
                        print("Agitator Just turned off motor. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency, "duty:", self._pinStep.duty_cycle)
                    else:
                        # do nothing as motor is off and we should just ignore
                        # print("Motor is idle. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency)
                        pass
                else:
                    # Decrease freq
                    self.freq = self.freq - self.freqStep
                    self._pinStep.frequency = self.freq
                    # print("Decrease freq. prevFreq:", prevFreq, "newFreq:", self.freq, "actual:", self._pinStep.frequency)

            # check to see if diag pin went high and print error
            self.checkDiag()

            # Yield to other events
            # await asyncio.sleep(0)
            # during debug/run wait a long time so as not to call ourself back too often
            await asyncio.sleep(0.1)

    async def spinAsyncExitTimer(self, duration):
        print("Starting timer")
        self.spinAsyncStart()
        await asyncio.sleep(duration) # don't forget the await
        self.spinAsyncStop()
        print("Ended timer")

    def checkDiag(self):
        """This method checks the value of the Diag pin to see if it is high. If it is, we print an error."""

        if self._pinDiag.value == True and time.time() - self._lastTimeDiagShown > 1:
            print("Agitator Diag Pin ERROR!!!")
            self._lastTimeDiagShown = time.time()
            
# Test Code

# async def testAsyncSpin():
#     print("Testing async spin")
#     s = StepperAgitator()
#     s.enable()
#     # start spinning
#     spin_task = asyncio.create_task(s.spinAsyncTaskPwm())
#     # spin for 5 seconds
#     exit_task = asyncio.create_task(s.spinAsyncExitTimer(10))

#     await asyncio.gather(spin_task, exit_task)

#     s.disable()
#     s.deinit()

# # test()
# asyncio.run(testAsyncSpin())

