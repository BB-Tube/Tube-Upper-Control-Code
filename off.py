from emptier import Emptier
from arm import Arm
import time
from util import *
import math

from dynamixel_cont_unstall import Dynamixel_Cont_Unstall
from serial_microcontroller import SerialMicrocontroller
from dispenser import Dispenser
from revolver import Revolver
from sorter import Sorter
from susan import Susan

### column 3 is the one to dump

### Variables
BAUD_MICROCONTROLLER = 9600
PORT_MICROCONTROLLER = "/dev/ttyACM1"
BAUD_DYNAMIXELS = 1000000
PORT_DYNAMIXELS = "/dev/ttyACM0"
ID_EMPTIER = 12
ID_SUSAN = 13
ID_SORTER_REVOLVER = 14
ID_SORTER_ARM = 15
ID_DISPO_INSERTER = 16
ID_DISPO_WHITE = 17
ID_DISPO_BLACK = 18
ID_ELEVATOR = 20

### Objects

## Sorter 
# MicroController
sm = SerialMicrocontroller(
    port = PORT_MICROCONTROLLER,
    baudrate = BAUD_MICROCONTROLLER)
# Revolver
sorter_revolver = Revolver(ID_SORTER_REVOLVER, 
    PORT_DYNAMIXELS,BAUD_DYNAMIXELS, 8, flip=True, 
    current = 500, velocity= 0, offset=math.radians(5))
print("sorter_revolver : ", sorter_revolver.get_model())
# Arm
sorter_arm = Arm(
    id = ID_SORTER_ARM, port = PORT_DYNAMIXELS, baudrate = BAUD_DYNAMIXELS,
    current = 400, tolerance=math.radians(5))
print("sorter_arm : ", sorter_arm.get_model())
# Sorter
sorter = Sorter(sorter_revolver, sorter_arm, sm)
## Emptier
emptier = Emptier(
    id = ID_EMPTIER,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
print("emptier : ", emptier.get_model())
## Elevator
elevator = Dynamixel_Cont_Unstall(
    id = ID_ELEVATOR, 
    port = PORT_DYNAMIXELS, 
    baudrate = BAUD_DYNAMIXELS, 
    anticlockwise = False,
    backoff = math.tau,
    current = 1000,
    velocity = math.tau * 3,
    back_off_time = 2,
    cooldown_time = .5,
    velocity_tolerance = .05)
print("elevator : ", elevator.get_model())
## Susan
susan = Susan(
    id = ID_SUSAN,
    port = PORT_DYNAMIXELS,
    baudrate= BAUD_DYNAMIXELS,  
    serialBoi = sm,
    motor_offset= math.tau * .25/12)
# Dispenser
# Driver
dispo_driver = Dynamixel_Cont_Unstall(
    id = ID_DISPO_INSERTER, 
    port = PORT_DYNAMIXELS, 
    baudrate = BAUD_DYNAMIXELS, 
    anticlockwise = False,
    backoff = math.tau,
    current = 400,
    velocity = math.tau * 3,
    back_off_time = 2,
    cooldown_time = .5,
    velocity_tolerance = .05)
print("dispo_driver : ", dispo_driver.get_model())
# Revolver Black
revolver_black = Revolver(
    ID_DISPO_BLACK, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
    slots = 6, flip=False, current = 300, velocity= math.tau,
    position_tolerance=math.radians(6), 
    offset=math.radians(42))
print("revolver_black : ", revolver_black.get_model())
# Revolver White
revolver_white = Revolver(
    ID_DISPO_WHITE, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
    slots = 6, flip=True, current = 300, velocity= math.tau, 
    position_tolerance=math.radians(6), 
    offset=math.radians(45))
print("revolver_white : ", revolver_white.get_model())
# Dispenser
dispo = Dispenser(
    white_revolver=revolver_white,
    black_revolver=revolver_black,
    dispo_driver=dispo_driver,
    microcontroller=sm)

sorter.off()
susan.off()
emptier.off()
elevator.off()
dispo.off()