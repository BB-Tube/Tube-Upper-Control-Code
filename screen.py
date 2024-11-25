from emptier import Emptier
from arm import Arm
import time
from util import *
import math
import numpy as np

from dynamixel_cont_unstall import Dynamixel_Cont_Unstall
from serial_microcontroller import SerialMicrocontroller
from dispenser import Dispenser
from revolver import Revolver
from sorter import Sorter
from susan import Susan
from elevator import Elevator
from screen_state_rw import ScreenStateRW
from screen_state_handler import ScreenStateHandler

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

class ScreenState(Enum):
    HOME = auto()
    QUEING = auto()
    MOVING = auto()
    BUSY_COLUMN = auto()

class ColumnState(Enum):
    QUEING = auto()
    EMPTYING = auto()
    FILLING = auto()

class Screen(object):
    def __init__(self, screen_state_handler : ScreenStateHandler):
        self.state_handler = screen_state_handler

        self.column_count = screen_state_handler.column_count
        self.row_count = screen_state_handler.row_count

        self.fill_que = []
        self.goal = []
        self.current = []

        self.column_manipulating = None

        self.column_que = []
        self.ball_que = []

        self.screen_state = State.READY
        self.column_state = State.READY

        self.empty_waiter = Waiter()

        self.boot()

    def on(self):
        elevator.on()
        susan.on()
        dispo.on()
        emptier.on()
        sorter.on()

    def boot(self):
        self.on()
        emptier.close()
        time.sleep(1)
        susan.indicate()

    def update(self):
        time.sleep(.1)
        print()
        self.screen_update()
        self.column_update()
        sorter.update()
        elevator.update()
        dispo.update()

    def screen_update(self):
        if self.screen_state == State.READY:
            # print("screen state - ready")
            self.column_que = self.state_handler.get_list_different_columns()
            print(self.column_que)
            if len(self.column_que) > 0:
                self.screen_state = State.BUSY
                self.column_manipulating  = self._nearest_column_in_que()
                # print("column_picked ", self.column_manipulating)
                susan.go_to_column_nearest(self.column_manipulating )
                self.ball_que = self.state_handler.goal.read_column(self.column_manipulating)
                # print("ball_que ",  self.ball_que)
                self.column_state = ColumnState.QUEING
        if self.screen_state == State.BUSY:
            # print("screen state - busy")
            if self.column_state == State.READY:
                balls_added = self.state_handler.goal.read_column(self.column_manipulating)
                self.state_handler.now.write_column(self.column_manipulating, balls_added)
                self.screen_state = State.READY

    def _nearest_column_in_que(self):
        target = susan.at_column_absolute()
        max_range = self.column_count
        numbers = self.column_que

        # Adjust target and numbers to wrap within the range 0 to max_range - 1
        target %= max_range
        wrapped_numbers = [num % max_range for num in numbers]
        
        # Find the number with the smallest wrapped distance
        closest = min(
            wrapped_numbers,
            key=lambda x: min(abs(x - target), max_range - abs(x - target))
        )
    
        # Return the original number corresponding to the closest wrapped number
        return numbers[wrapped_numbers.index(closest)]

    def column_update(self):
        if self.column_state == ColumnState.QUEING:
            # print("column_update - queing")
            if susan.is_there():
                self.column_state = ColumnState.EMPTYING
                self.empty_waiter.wait(3)
                emptier.open()
        if self.column_state == ColumnState.EMPTYING:
            # print("column_update - emptying")
            if self.empty_waiter.if_past():
                self.column_state = ColumnState.FILLING
                emptier.filling()
        if self.column_state == ColumnState.FILLING:
            # print("column_update - filling")
            if len(self.ball_que) == 0:
                # print("ball que done")
                emptier.close()
                self.column_state = State.READY
            else:
                ball_added = self.feed_ball(self.ball_que[0])
                print(ball_added)
                if (ball_added):
                    # print("ball inserted")
                    self.ball_que = np.delete(self.ball_que, 0)

    def feed_ball(self, ball : Ball):
        if ball == Ball.NONE:
            return True
        if ball == Ball.WHITE:
            # print("Trying White")
            return dispo.add_white()
        if ball == Ball.BLACK:
            # print("Trying Black")
            return dispo.add_black()
        return False

if __name__ == "__main__":
    now = ScreenStateRW('screen_state_now.json')
    goal = ScreenStateRW('screen_state_goal.json')
    memory_handler = ScreenStateHandler(now, goal)  
    s = Screen(memory_handler)
    while(True):
        s.update()