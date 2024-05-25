from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time 
import math

class Default():
    ### ID typical is 12
    OPEN = 0
    CLOSED = math.pi
    MAX_CURRENT = 400 # ma

class Emptier(Dynamixel):
    def __init__(self, 
                 id, port, baudrate,
                 name = "Emptier",
                 OPEN = Default.OPEN,
                 CLOSED = Default.CLOSED):
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        self.OPEN_POSITION = OPEN
        self.CLOSED_POSITION = CLOSED
        self._setup_motor()
        
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
    baud = 57600
    port = "/dev/ttyUSB0"
    susan = Emptier(id = 12, port=port, baudrate=baud)
    while(True):
        susan.open()
        time.sleep(1)
        susan.close()
        time.sleep(1)
        



