import board
import pwmio

pinStep = pwmio.PWMOut(board.IO7, frequency=6000, duty_cycle=0, variable_frequency=True)
# pinStep.frequency = 0
# pinStep.duty_cycle = 32768

for i in range(10, 6000, 10):
    pinStep.frequency = i
    pinStep.duty_cycle = 32768
    print("i:", i, "Freq:", pinStep.frequency, "Duty:", pinStep.duty_cycle)

print("done")
