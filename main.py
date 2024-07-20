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

### Variables
BAUD_MICROCONTROLLER = 9600
PORT_MICROCONTROLLER = "/dev/ttyACM0"
BAUD_DYNAMIXELS = 1000000
PORT_DYNAMIXELS = "/dev/ttyUSB0"
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
sorter_revolver = Revolver(14, 
    PORT_DYNAMIXELS,BAUD_DYNAMIXELS, 8, flip=True, 
    current = 500, velocity= 0, offset=math.radians(15))
# Arm
sorter_arm = Arm(
    id = ID_SORTER_ARM, port = PORT_DYNAMIXELS, baudrate = BAUD_DYNAMIXELS,
    current = 400, tolerance=math.radians(5))
# Sorter
sorter = Sorter(sorter_revolver, sorter_arm, sm)
## Emptier
emptier = Emptier(
    id = ID_EMPTIER,
    port = PORT_DYNAMIXELS,
    baudrate = BAUD_DYNAMIXELS)
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
## Susan
susan = Susan(
    id = ID_SUSAN,
    port = PORT_DYNAMIXELS,
    baudrate= BAUD_DYNAMIXELS,  
    serialBoi = sm,
    motor_offset= math.tau * 6/12)
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
# Revolver Black
revolver_black = Revolver(
    ID_DISPO_BLACK, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
    slots = 6, flip=False, current = 300, velocity= math.tau,
    position_tolerance=math.radians(6), 
    offset=math.radians(42))
# Revolver White
revolver_white = Revolver(
    ID_DISPO_WHITE, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
    slots = 6, flip=True, current = 300, velocity= math.tau, 
    position_tolerance=math.radians(6), 
    offset=math.radians(45))
# Dispenser
dispo = Dispenser(
    white_revolver=revolver_white,
    black_revolver=revolver_black,
    dispo_driver=dispo_driver,
    microcontroller=sm)


#### Example

## Test Sorter Revolver
if False: 
    iterator = 0
    start = time.monotonic()
    delta = 0
    while True:
        sorter_revolver.update()
        if sorter_revolver.get_state() == State.READY:
            sorter_revolver.next_slot()
            iterator += 1
            delta = round(time.monotonic() - start,3)
            print(iterator, " time is ", delta)
            if iterator == 100:
                break
## Arm
while False:
    print('b')
    a.set_ball(Ball.BLACK)
    while not a.get_state() == State.READY:
        a.update()
    
    print('w')  
    a.set_ball(Ball.WHITE)
    while not a.get_state() == State.READY:
        a.update()  

    print('n')
    a.set_ball(Ball.NONE)
    while not a.get_state() == State.READY:
        a.update()
## Emptier
while(False):
    emptier.open()
    time.sleep(3)
    emptier.close()
    time.sleep(3)
# Elevator          
while(False):
    elevator.update()
## Sorter
while False:
    sorter.update()
### Elevate & Sorter
if False:
    emptier.open()
        
    while True:
        sorter.update()
        elevator.update()
        # time.sleep()
### Empty Columns
if False:
    # susan.indicate()
    susan.off()
    emptier.open()
    w = Waiter()
    time_to_empty = 15
    for i in range(96):
        w.wait(time_to_empty)
        while(not w.if_past()):
            elevator.update()
            sorter.update()
        # susan.go_to_column(i)
        

### Elevate & Sorter & Dispense 
if False: 
    increment = 0
    up_to = 32
    susan.off()
    
    emptier.open()
    time.sleep(1.5)
    # emptier.close()
    
    white_black_alternator = False
    added_ball_state = None
    while True:
        sorter.update()
        elevator.update()
        # time.sleep(.5)
        dispo.update()
        if dispo.get_state() == State.READY:
            # dispo.print_states()
            added_ball_state = False
            if white_black_alternator:
                added_ball = dispo.add_white()
                print("Add White : ", added_ball)
            else:
                added_ball = dispo.add_black()
                print("Add Black : ", added_ball)
            if added_ball:
                increment += 1
                if increment >= up_to:
                    emptier.open()
                    # time.sleep(1)
                    # emptier.close()
                    increment = 0
                white_black_alternator = not white_black_alternator
                white_black_alternator = False
                
### Elevate & Sorter & Dispense 
if True: 
    increment = 0
    up_to = 32
    susan.go_to_column_nearest(90)
    susan.off()
    
    emptier.open()
    time.sleep(1.5)
    emptier.close()
    
    white_black_alternator = True
    added_ball_state = None
    while True:
        sorter.update()
        elevator.update()
        # time.sleep(.5)
        dispo.update()
        if dispo.get_state() == State.READY:
            # dispo.print_states()
            added_ball_state = False
            if white_black_alternator:
                added_ball = dispo.add_white()
                print("Add White : ", added_ball)
            else:
                added_ball = dispo.add_black()
                print("Add Black : ", added_ball)
            if added_ball:
                increment += 1
                if increment >= up_to:
                    # susan.go_to_column(round(susan.at_column()) + 1)
                    emptier.open()
                    time.sleep(1)
                    emptier.close()
                    increment = 0
                white_black_alternator = False
