from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time 
import math
import atexit

class Default():
    BAUD = 57600
    PORT = "/dev/ttyUSB0"
    ID = 12
    
    ### ID typical is 12
    OPEN = math.tau * (.95)
    CLOSED = math.tau * (1/2 - .1)
    MAX_CURRENT = 200 # ma

class Emptier(Dynamixel):
    def __init__(self, 
                 id = Default.ID, 
                 port = Default.PORT, 
                 baudrate = Default.BAUD,
                 name = "Emptier",
                 OPEN = Default.OPEN,
                 CLOSED = Default.CLOSED):
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        self.OPEN_POSITION = OPEN
        self.CLOSED_POSITION = CLOSED
        self._setup_motor()
        atexit.register(self.off)
        
    def _setup_motor(self):
        self.off()
        self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self.on()
        self.set_goal_current(Default.MAX_CURRENT)
    
    def open(self):
        self.set_goal_position(self.OPEN_POSITION)
    
    def close(self):
        self.set_goal_position(self.CLOSED_POSITION)

if __name__ == '__main__':
    emptier = Emptier()
    while(True):
        emptier.open()
        time.sleep(1)
        emptier.close()
        time.sleep(1)
        



