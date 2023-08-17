import stepper
import time 
s = stepper.Stepper()
s.enable()
s.dump()
s.setMinPulseWidth(0.001)
s.stepsEnDis(200*8)
s.dump()
