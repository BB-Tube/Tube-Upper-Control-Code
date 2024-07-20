from util_gyz.dynamixel import Dynamixel
from util_gyz.util import waiter
import time
from datetime import datetime

from collections import Counter
from enum import Enum, auto

from revolver import Revolver
from arm import Arm
from serial_microcontroller import SerialMicrocontroller
from util import *
import math

class SorterState(Enum):
    READING = auto()
    PREPPING_ARM = auto()
    MOVING_REVOLVER = auto()

class Sorter(object):
    def __init__(self, 
            revolver : Revolver, 
            arm : Arm, 
            serialBoi : SerialMicrocontroller, 
            samples = 3):
        
        self.revolver = revolver
        self.arm = arm
        self.microcontroller = serialBoi
        
        self.sample_size = samples
        self.state = SorterState.READING
        self.on_off = True # On to start
      
    def on(self):
        self.on_off = True
        self.revolver.on()
        self.arm.on()
      
    def off(self):
        self.on_off = False
        self.revolver.off()
        self.arm.off()
      
    def update(self):
        if not self.on_off:
            return None
        
        self.revolver.update()
        self.arm.update()        
        
        revolver_not_ready = not self.revolver.get_state() == State.READY
        arm_not_ready = not self.arm.get_state() == State.READY
        
        if revolver_not_ready or arm_not_ready:
            return None
        
        # print()
        # print("updating")
        if self.state == SorterState.READING:
            print("READING")
            color_reading = self.get_ball_color()
            print("Color Reading: ", color_reading)
            self.arm.set_ball(color_reading)
            self.state = SorterState.PREPPING_ARM
        if self.state == SorterState.PREPPING_ARM:
            print("PREPPING_ARM")
            if self.arm.get_state() == State.READY:
                self.revolver.next_slot()
                self.state = SorterState.MOVING_REVOLVER
        if self.state == SorterState.MOVING_REVOLVER:
            print("MOVING_REVOLVER")
            if self.revolver.get_state() == State.READY:
                self.state = SorterState.READING
            
        
    def get_ball_color(self, sample_count = 0):
        balls_read = ""
        count = sample_count
        if sample_count == 0:
            count = self.sample_size
        for i in range(count):
            reading = self.microcontroller.get_color_sensor().value
            # print(reading)
            balls_read = balls_read + reading
        ball = Counter(balls_read)
        ball = max(ball, key=ball.get)
        return ball_reverse_index(ball)

if __name__ == '__main__':
    baud = 1000000
    port = "/dev/ttyUSB0"
    r = Revolver(14, port = port, baudrate = baud, 
        slots = 8, flip=True,
        current = 500, velocity= 0, offset=math.radians(15))
    r.set_profile_acceleration(0)
    a = Arm(15, port = port, baudrate = baud,
        current = 400, tolerance=math.radians(5))
    sm = SerialMicrocontroller()
    s = Sorter(r, a, sm)
    
    while True:
        # print(s.get_ball_color())
        s.update()