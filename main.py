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
from elevator import Elevator

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
ID_ELEVATOR_SECONDARY = 19
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
elevator = Elevator(
    id = ID_ELEVATOR, 
    port = PORT_DYNAMIXELS, 
    baudrate = BAUD_DYNAMIXELS, 
    anticlockwise = False,
    backoff = math.tau,
    current = 1000,
    velocity = math.tau * 3,
    back_off_time = 2,
    cooldown_time = .5,
    velocity_tolerance = .05,
    follower_id = ID_ELEVATOR_SECONDARY)
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
    current = 500,
    velocity = math.tau * 6,
    back_off_time = 2,
    cooldown_time = .5,
    velocity_tolerance = .05)
print("dispo_driver : ", dispo_driver.get_model())
# Revolver Black
revolver_black = Revolver(
    ID_DISPO_BLACK, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
    slots = 6, flip=False, current = 300, velocity= math.tau * 1,
    position_tolerance=math.radians(6), 
    offset=math.radians(42))
print("revolver_black : ", revolver_black.get_model())
# Revolver White
revolver_white = Revolver(
    ID_DISPO_WHITE, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
    slots = 6, flip=True, current = 300, velocity= math.tau * 1, 
    position_tolerance=math.radians(6), 
    offset=math.radians(45))
print("revolver_white : ", revolver_white.get_model())
# Dispenser
dispo = Dispenser(
    white_revolver=revolver_white,
    black_revolver=revolver_black,
    dispo_driver=dispo_driver,
    microcontroller=sm)
elevator.on()
w = Waiter()

def wait_sort_elevate(wait_time):
    w.wait(wait_time)
    while not w.if_past():
        sorter.update()
        elevator.update()

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

### Kill Susan & Open & Elevate & Dispense
if False:
    emptier.open()
    susan.off()
    while(True):
        elevator.update()
        sorter.update()

## Emptier
while(False):
    emptier.open()
    print("OPEN")
    time.sleep(3)
    emptier.close()
    print("CLOSE")
    time.sleep(3)
    emptier.filling()
    print("FILLING")
    time.sleep(3)

# Elevator          
if(False):
    elevator.on()
    while(True):
        tic = time.time()
        for i in range(100):
            elevator.update()
        toc = time.time()
        print((toc-tic)/100)

## Sorter
while False:
    sorter.update()

### Elevate & Sorter
if False:
    susan.off()
    emptier.open()
    while True:
        # print(elevator.get_current())
        sorter.update()
        elevator.update()

### Empty Columns
if False:
    # susan.indicate()
    susan.off()
    emptier.open()
    while True:
        elevator.update()
        # sorter.update()
        # susan.go_to_column(i)
        
### Elevate & Sorter & Empty 
if False: 
    emptier.close()
    # print(susan.get_shutdown())
    susan.on()
    print("here")
    susan.indicate()
    susan.go_to_column_nearest(0)
    while susan.get_dist_to_goal() > .5:
        time.sleep(.001)
    time.sleep(3)
    emptier.open()
    w = Waiter()
    w.wait(10)
    
    # susan.off()
    while True:
        sorter.update()
        elevator.update()
        if w.if_past():
            if round(susan.at_column()) == 95:
                break
            print(susan.at_column())
            susan.go_to_column_nearest((round(susan.at_column()+1%96)))
            w.wait(10)

### Elevate & Sorter & Dispense 
if True: 
    increment = 0
    up_to = 32
    emptier.open()
    time.sleep(3)
    emptier.close()
    susan.indicate()
    susan.go_to_column_nearest(0)
    
    time.sleep(2)
    emptier.open()
    time.sleep(2)
    emptier.filling()
    
    white_black_alternator = False
    added_ball_state = None
    added_ball = False

    while True:
        sorter.update()
        elevator.update()
        dispo.update()
        if dispo.get_state() == State.READY:
            # dispo.print_states()
            added_ball_state = False
            if white_black_alternator:
                added_ball = dispo.add_white()
                # print("Add White : ", added_ball)
            else:
                added_ball = dispo.add_black()
                # print("Add Black : ", added_ball)
            if added_ball:
                increment += 1
                white_black_alternator = not white_black_alternator
                # white_black_alternator = True
            if increment >= up_to:
                wait_sort_elevate(1.5)
                emptier.close()
                wait_sort_elevate(1.5)
                if round(susan.at_column()) == 95:
                    exit()
                susan.go_to_column(round(susan.at_column()) + 1)
                white_black_alternator = not white_black_alternator
                wait_sort_elevate(1.5)
                print(susan.at_column_absolute())
                emptier.open()
                wait_sort_elevate(2)
                emptier.filling()
                increment = 0
                             
### Elevate & Sorter & Dispense & Kill Susan
if False: 
    increment = 0
    up_to = 32
    # susan.go_to_column_nearest(90)
    susan.off()
    
    emptier.open()
    time.sleep(1.5)
    emptier.close()
    
    white_black_alternator = True
    added_ball_state = None
    while True:
        dispo.print_states()
        sorter.update()
        elevator.update()
        # time.sleep(.5)
        dispo.update()
        if dispo.get_state() == State.READY:
            # dispo.print_states()
            added_ball_state = False
            if white_black_alternator:
                added_ball = dispo.add_white()
                # print("Add White : ", added_ball)
            else:
                added_ball = dispo.add_black()
                # print("Add Black : ", added_ball)
            if added_ball:
                increment += 1
                if increment >= up_to:
                    # susan.go_to_column(round(susan.at_column()) + 1)
                    emptier.open()
                    time.sleep(1)
                    emptier.close()
                    increment = 0
                white_black_alternator = not white_black_alternator

### Print Susan
if True:
    emptier.filling()
    susan.off()
    while(True):
        time.sleep(.1)
        print(susan.at_column_absolute())