"""This class controls the fan PWM output. The idea is to connect an external
MOSFET driver to the PWM output of the ESP32."""

import pwmio
import board 
import time

class Fan:

    def __init__(self) -> None:
        
        print("Initting Fan library.")

        self.pinFanNum = board.IO3

        self.turnOnFanFrequency()

    def turnOnFanFrequency(self):

        # setup pinStep as PWM output
        self.freqGen = pwmio.PWMOut(
            self.pinFanNum, 
            frequency=10, # Not allowed to set to 0, can't set to 0, so adjust duty to turn on/off
            duty_cycle=2 ** 15,  # Cycles the pin with 50% duty cycle (half of 2 ** 16) 
            variable_frequency=True
            )
        print("Turned on fan frequency generator. Freq:", self.freqGen.frequency, "Duty:", self.freqGen.duty_cycle)

    def turnOn(self):

        self.freqGen.duty_cycle = (2 ** 16) - 1
        print("Turned on fan. Freq:", self.freqGen.frequency, "Duty:", self.freqGen.duty_cycle)

    def turnOff(self):

        self.freqGen.duty_cycle = 0
        print("Turned off fan. Freq:", self.freqGen.frequency, "Duty:", self.freqGen.duty_cycle)

# def test():

#     f = Fan()

#     while True:

#         f.turnOn()
#         time.sleep(3)
#         f.turnOff()
#         time.sleep(3)

# test()