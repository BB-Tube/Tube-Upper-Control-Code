from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time 
import math

class Default():
    ### ID typical is 20
    OPEN = 0
    CLOSED = math.pi
    JAMMED_CURRENT = 1200 # ma

class Elevator(Dynamixel):
    def __init__(self, 
                 id, port, baudrate,
                 name = "Emptier",
                 OPEN = Default.OPEN,
                 CLOSED = Default.CLOSED):
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        self.speed = -math.tau * 1
        self._setup_motor()
        self.unjamming = False
        self.jam_position = None
        
    def _setup_motor(self):
        self.off()
        self.set_mode(Mode.VELOCITY)
        self.on()
    
    def go(self):
        self.on()
        self.set_goal_velocity(self.speed)
    
    def stop(self):
        self.set_goal_velocity(0)
        
    def reverse(self):
        self.set_goal_velocity(-self.speed)

    def update(self):
        if not self.unjamming and self.is_jammed():
            self.reverse()
            self.jam_position = self.get_position()
            
        if unjamming and self.get_position() < self.jam_position:
            self.unjamming = False
            if self.jam_position - self.get_position() > math.pi:
                self.go()
    
    def is_jammed(self): 
        return self.get_current() > Default.JAMMED_CURRENT

if __name__ == '__main__':
    baud = 57600
    port = "/dev/ttyUSB0"
    vator = Elevator(id = 20, port=port, baudrate=baud)
    vator.set_shutdown(0)
    while True:
        time.sleep(.5)
        vator.go()
        print("velocity : ", vator.get_velocity())
        print("current :  ", vator.get_current())
    vator.off()
        



