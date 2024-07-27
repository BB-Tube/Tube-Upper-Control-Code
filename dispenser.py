from revolver import Revolver
from dynamixel_unstall import Dynamixel_Unstall
from dynamixel_cont_unstall import Dynamixel_Cont_Unstall
from serial_microcontroller import SerialMicrocontroller

import math
import time
from util import *
from enum import Enum, auto

import atexit

class DispenserVar():
    pass
    INLET_WHITE = math.radians(120)
    INLET_BLACK = math.radians(240)
    OUTLET = 0

class DispenserState(Enum):
    # Mechansim State
    ASKING = auto()
    ADDING = auto()
    INSERTING = auto()
    
    # Inserter State
    LOADED = auto()
    UNLOADED = auto()

class Dispenser(object):
    def __init__(self,
        white_revolver : Revolver,
        black_revolver : Revolver,
        dispo_driver : Dynamixel_Cont_Unstall,
        microcontroller : SerialMicrocontroller):
        
        ### Setup revolvers
        # White
        self.white_revolver = white_revolver
        self.white_state = DispenserState.UNLOADED
        # Black
        self.black_revolver = black_revolver
        self.black_state = DispenserState.UNLOADED
        
        ### Setup Driver
        self.dispo_driver = dispo_driver
        self.dispo_state = State.BUSY
        self.dispo_last_positon = self.dispo_driver.get_position()
        self.dispo_waiting = 0
        
        self.microcontroller = microcontroller
        
        ### Mechanism
        self.state = State.READY
        
        atexit.register(self.off)
        
    def dispo_ready_after_move(self, movement):
        # print("Dispo Position : ", self.dispo_driver.get_position())
        self.dispo_waiting = self.dispo_driver.get_position() - movement
        # print("dispo_waiting : ", movement)
    
    def dispo_move_enough(self):
        is_move_enough = self.dispo_waiting > self.dispo_driver.get_position()
        # print("Dispo Position : ", self.dispo_driver.get_position())
        # print("dispo_move_enough : ", is_move_enough)
        return is_move_enough
        
    def on(self):
        self.white_revolver.on()
        self.black_revolver.on()
        self.dispo_driver.on()
    
    def off(self):
        self.white_revolver.off()
        self.black_revolver.off()
        self.dispo_driver.off()
        
    def print_states(self):
        is_dispo_ready = self.dispo_driver.get_state() == State.READY 
        is_dispo_moved = self.dispo_move_enough()
        is_white_ready = self.white_state == State.READY
        is_black_ready = self.black_state == State.READY
        
        print()
        print("Dispo State :    ", is_dispo_ready)
        print("Dispo Moved :    ", is_dispo_moved)
        print("White State :    ", is_white_ready)
        print("Black State :    ", is_black_ready)
        print("Dispo_State : ", self.state)
        
    def update(self):
        self.dispo_driver.update()
        self.update_white()
        self.update_black()
        
        is_dispo_ready = self.dispo_driver.get_state() == State.READY 
        is_dispo_moved = self.dispo_move_enough()
        
        if is_dispo_ready: # and is_white_ready and is_black_ready:
            self.state = State.READY
        else: 
            self.state = State.BUSY
    
    def get_state(self):
        return self.state
    
    def log_dispenser_pos(self):
        self.dispo_last_positon = self.dispo_driver.get_position()
        
    def proximity_dispenser(self):
        proximity = abs(self.dispo_driver.get_position() - self.dispo_last_positon)
    
    def update_white(self):
        self.white_revolver.update()
        white_beam = self.microcontroller.get_white_dispo_sensor()
        white_revolver_state = self.white_revolver.get_state() == State.READY
        if white_revolver_state and white_beam:
            self.white_state = State.READY
        if white_revolver_state and not white_beam:
            self.white_state = DispenserState.UNLOADED
            self.white_revolver.next_slot()
        if not white_revolver_state:
            self.white_state = State.BUSY
        return None
    
    def add_white(self):
        if self.white_state == State.READY:
            self.white_revolver.next_slot()
            self.dispo_ready_after_move(DispenserVar.INLET_WHITE)
            self.white_state = DispenserState.UNLOADED
            return True
        if not self.white_state == State.READY:
            return False
        return None
    
    def update_black(self):
        self.black_revolver.update()
        black_beam = self.microcontroller.get_black_dispo_sensor()
        black_revolver_state = self.black_revolver.get_state() == State.READY
        if black_revolver_state and black_beam:
            self.black_state = State.READY
        if black_revolver_state and not black_beam:
            self.black_state = DispenserState.UNLOADED
            self.black_revolver.next_slot()
        if not black_revolver_state:
            self.black_state = State.BUSY
        return None
    
    def add_black(self):
        if self.black_state == State.READY:
            self.black_revolver.next_slot()
            self.dispo_ready_after_move(DispenserVar.INLET_BLACK)
            self.black_state = DispenserState.UNLOADED
            return True
        if not self.black_state == State.READY:
            return False
        return None
    
if __name__ == "__main__":
    BAUD_MICROCONTROLLER = 9600
    PORT_MICROCONTROLLER = "/dev/ttyACM0"
    BAUD_DYNAMIXELS = 1000000
    PORT_DYNAMIXELS = "/dev/ttyUSB0"
    ID_DISPO_INSERTER = 16
    ID_DISPO_WHITE = 17
    ID_DISPO_BLACK = 18
    
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
    revolver_black = Revolver(
        ID_DISPO_BLACK, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
        slots = 6, flip=False, current = 300, velocity= 0,
        position_tolerance=math.radians(6), 
        offset=math.radians(42))
    revolver_white = Revolver(
        ID_DISPO_WHITE, PORT_DYNAMIXELS, BAUD_DYNAMIXELS, 
        slots = 6, flip=True, current = 300, velocity= 0, 
        position_tolerance=math.radians(6), 
        offset=math.radians(45))
    dispo = Dispenser(
        white_revolver=revolver_white,
        black_revolver=revolver_black,
        dispo_driver=dispo_driver,
        microcontroller=SerialMicrocontroller(
            port = PORT_MICROCONTROLLER,
            baudrate = BAUD_MICROCONTROLLER))
        
    white_black_alternator = True
    added_ball_state = None
    while False:
        dispo.update()
        if dispo.get_state() == State.READY:
            dispo.print_states()
            added_ball_state = False
            if white_black_alternator:
                added_ball = print("Add White : ", dispo.add_white())
            else:
                added_ball = print("Add Black : ", dispo.add_black())
            if added_ball:
                white_black_alternator = not white_black_alternator
    dispo_driver.off()