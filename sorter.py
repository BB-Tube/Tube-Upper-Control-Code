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
from color_sensor import ColorSensor
from camera_color_sensor import CameraColorSensor

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
        self.revolver.set_profile_acceleration(1000)
        self.revolver.set_profile_velocity(math.tau*2)
        self.arm = arm
        self.microcontroller = serialBoi
        self.colorsensor = CameraColorSensor()
        
        self.sample_size = samples
        self.state = SorterState.READING
        self.on()
        
        self.store = True
      
    def on(self):
        self.on_off = True
        self.revolver.on()
        self.microcontroller.sorter_light_on()
        self.arm.on()
      
    def off(self):
        self.on_off = False
        self.revolver.off()
        self.microcontroller.sorter_light_off()
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
        # time.sleep(1)
        if self.state == SorterState.READING:
            color_reading = self.get_ball_color_camera()
            self.arm.set_ball(color_reading)
            self.arm.update()
            self.state = SorterState.PREPPING_ARM
        if self.state == SorterState.PREPPING_ARM:
            if self.arm.get_state() == State.READY:
                self.revolver.next_slot()
                self.state = SorterState.MOVING_REVOLVER
        if self.state == SorterState.MOVING_REVOLVER:
            if self.revolver.get_state() == State.READY:
                self.state = SorterState.READING
            
        
    def get_ball_color_sensor(self, sample_count = 0):
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

    def get_ball_color_camera(self):
        ball_color = self.colorsensor.get_ball_color()
        return ball_color

if __name__ == '__main__':
    baud = 1000000
    port = "/dev/ttyACM0"
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