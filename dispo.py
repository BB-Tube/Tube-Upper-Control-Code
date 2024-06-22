from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time 
import math
from revolver import revolver
from elevator import Elevator

class Default():
    BAUD = 57600
    PORT = "/dev/ttyUSB0"
    
    DISPO_DRIVER = "Driver Dispo"
    DISPO_ID = 16
    DISPO_SPEED = -math.tau * 3
    
    WHITE_NAME = "White Dispo"
    WHITE_ID = 17
    WHITE_FLIP = True
    WHITE_OFFSET = 0
    
    BLACK_NAME = "Black Dispo"
    BLACK_ID = 18
    BLACK_FLIP = False  
    BLACK_OFFSET = 0
      
    ASK_WHITE =         'e'
    ASK_BLACK =         'n'
    ANSWER_LOADED =     '0'
    ANSWER_UNLOADED =   '1'
    
    JAMMED_CURRENT = 800 # ma
    
class Dispo(object):
    def __init__(
            self,
            id_dispo = Default.DISPO_ID, 
            id_white = Default.WHITE_ID,
            id_black = Default.BLACK_ID, 
            port = Default.PORT, baudrate = Default.BAUD,
            name_dispo = Default.DISPO_DRIVER,
            name_white = Default.WHITE_NAME, 
            name_black = Default.BLACK_NAME):
        self.dispo = Dynamixel(id = id_dispo, port=port, baudrate=baudrate, name=name_dispo)
        self.white_revolver = revolver(id_white, port, baudrate, name_white, 
            6, flip = Default.WHITE_FLIP, offset = Default.WHITE_OFFSET)
        self.black_revolver = revolver(id_black, port, baudrate, name_black,
            6, flip = Default.BLACK_FLIP, offset = Default.BLACK_OFFSET)   
        self._setup_motor()
        
    def on(self):
        for motor in (self.dispo, self.white_revolver, self.black_revolver):
            motor.on()
            
    def off(self):
        for motor in (self.dispo, self.white_revolver, self.black_revolver):
            motor.off()
        
    def dispo_drive(self):
        self.dispo.set_goal_velocity(Default.DISPO_SPEED)
        
    def _setup_motor(self):
        self.off()
        self.dispo.set_mode(Mode.VELOCITY)
        self.on()

if __name__ == "__main__":
    dispenser = Dispo()
    dispenser.dispo_drive()
    dispenser.on()
    
    while(True):
        ma = dispenser.dispo.get_current()
        print("Current: ", ma)
        time.sleep(1)
    
    baud = 57600
    port = "/dev/ttyUSB0"
    vator = Elevator(id = 20, port=port, baudrate=baud)
    # vator.go()
    
    # dispenser.white_revolver.off()
    # dispenser.white_revolver.set_mode(Mode.VELOCITY)
    # dispenser.white_revolver.on()
    # dispenser.white_revolver.set_goal_velocity(math.pi * -1)
    
    # dispenser.off()
    # vator.off()
    
    while False:
        # time.sleep(1)
        # print("White : ", dispenser.white_revolver.get_position())
        # print("Black : ", dispenser.black_revolver.get_position())
        # print("Dispo : ", dispenser.dispo.get_velocity())
        
        letter = input("Please enter 'b' or 'w' for black or white: ")
        if letter == 'b':
            dispenser.black_revolver.next_slot()
        if letter == 'w':
            dispenser.white_revolver.next_slot()
