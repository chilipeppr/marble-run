# The Liberty Christian Stepper Motor Library for CircuitPython
import digitalio
import board
import time


class Stepper:
    def __init__(self, *args):

        print("Initting Stepper library...")
        self._pinEnablePin = board.IO5
        self._pinDirPin = board.IO6
        self._pinStepPin = board.IO7
        self._pinDiagPin = board.IO8
        self._pinMs1Pin = board.IO9     # For drv8825 M0
        self._pinMs2Pin = board.IO10    # For drv8825 M1
        self._pinMs3Pin = board.IO11    # For drv8825 M2
        self._pinSleepPin = board.IO18    # For drv8825 Sleep is active low. Pull high to enable.
        self._pinResetPin = board.IO21    # For drv8825 Reset is active low. Pull high to enable.

        self._minPulseWidth = 0.001

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
        self._pinMs1.value = True #GND
        # self._pinMs1.pull = digitalio.Pull.DOWN
        self._pinMs2 = digitalio.DigitalInOut(self._pinMs2Pin)
        self._pinMs2.direction = digitalio.Direction.OUTPUT
        self._pinMs2.value = True #GND
        # self._pinMs2.pull = digitalio.Pull.DOWN

        # For Drv8825 we do a 3rd pin
        # Low / Low / Low = Full Step
        self._pinMs3 = digitalio.DigitalInOut(self._pinMs3Pin)
        self._pinMs3.direction = digitalio.Direction.OUTPUT
        self._pinMs3.value = False #GND

        # For Drv8825 we had Sleep and Reset pins as well
        # They both are active low, so we must pull them high to enable the chip
        self._pinSleep = digitalio.DigitalInOut(self._pinSleepPin)
        self._pinSleep.direction = digitalio.Direction.OUTPUT
        self._pinSleep.value = True # Pulled high
        self._pinReset = digitalio.DigitalInOut(self._pinResetPin)
        self._pinReset.direction = digitalio.Direction.OUTPUT
        self._pinReset.value = True # Pulled high

        # ensure disabled since GND=on and default state of pin is GND, thus drive would be on
        self.disable()

        # ensure fwd
        self.fwd()

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
        print("MS3:", self._pinMs3.value)
        print("Sleep:", self._pinSleep.value)
        print("Reset:", self._pinReset.value)
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
        self._pinMs3.deinit()
        self._pinSleep.deinit()
        self._pinReset.deinit()
        print("Deinitted")

# Test Code
def test():
    import stepper
    s = stepper.Stepper()

    s.enable()

    s.dump()

    print("Step one")
    s.step()
    time.sleep(0.1)
    print("Step two")
    s.step()

    # step multiple
    s.steps(200)

    s.disable()

    # time.sleep(0.1)
    s.dump()
    s.deinit()

test()

