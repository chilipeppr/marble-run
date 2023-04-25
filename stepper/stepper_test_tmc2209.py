from stepper_tmc2209 import Stepper
s = Stepper()
s.enable()
s.dump()
s.setMinPulseWidth(0.00054)
s.steps(200*8)
s.dump()
