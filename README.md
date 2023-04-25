# marble-run
The code for running on an ESP32-S2 to control the Liberty Christian School Evolving Marble Run

This is the prototype breadboard for driving the Marble Run. It has the following main modules:
- ESP32-S2 (Lolin S2 Mini)
- Stepper Motor TMC2209 Driver for Elevator
- Stepper Motor TMC2209 Driver for Agitator
- 2.42" OLED Display
- 24V to 5V DC to DC Converter
- 24V to 3.3V DC to DC Converter
- 24V Fan MOSFET Driver
- 24V Fan

<![alt](/readme/breadboard.jpg)>

PCB designed in Fusion 360 Electronics and produced at JLCPCB.
<![alt](/readme/pcb.png)>

This is a full view of the 8 foot tall Marble Run elevator that carries marbles from the bottom reservoir to the top of the run.
<![alt](/readme/tallshot.jpg)>
<![alt](/readme/tallshot.png)>

This is the bottom reservoir. It has an agitator to ensure marbles are continuallyl flowing into the exit pipe, thus
ensuring the elevator is constantly picking up a new marble.
<![alt](/readme/reservoir.jpg)>
<![alt](/readme/reservoir.png)>

This is the motor at top which rotates the GT2 timing belt. It is a NEMA 23 stepper motor.
<![alt](/readme/motor.jpg)>
<![alt](/readme/motor.png)>