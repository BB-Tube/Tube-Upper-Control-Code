from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time
from datetime import datetime
from collections import Counter
import math
import atexit
from serial_microcontroller import SerialMicrocontroller
from typing import List, Tuple

# Define your keyframes as (input_position, corrected_position) tuples
keyframes: List[Tuple[int, float]] = [
    (0, 0),        
    (8, 8.4),
    (16, 16),
    (24, 23.9),
    (32, 31.9),
    (40, 39.8),
    (48, 48),
    (56, 56),
    (64, 64),
    (72, 72),
    (80, 80),
    (88, 88),
    (96, 95.95)
    # The 96 case is implicitly handled as a wrap-around to 0
]

def interpolate_wrapping_forward(input_pos: float, keyframes: List[Tuple[int, float]]) -> float:
    num_keyframes = len(keyframes)
    step_size = 8  # The increment step size between keyframes
    
    # Normalize the input position to the wrapping range (0-95)
    input_pos = input_pos % 96

    # Find the keyframes before and after the input position
    for i in range(num_keyframes):
        start_keyframe = keyframes[i]
        end_keyframe = keyframes[(i + 1) % num_keyframes]  # Wrap around using modulo
        
        # Adjust end_keyframe to handle wrap-around between 88 and 0
        if end_keyframe[0] == 0 and input_pos >= start_keyframe[0]:
            end_input = 96
        else:
            end_input = end_keyframe[0]
        
        if start_keyframe[0] <= input_pos < end_input:
            # Linear interpolation
            start_input, start_corrected = start_keyframe
            end_corrected = end_keyframe[1]
            
            # Calculate the interpolation factor
            t = (input_pos - start_input) / (end_input - start_input)
            
            # Interpolate the corrected position
            corrected_pos = start_corrected + t * (end_corrected - start_corrected)
            return corrected_pos

    # This point should not be reached due to the wrapping nature of the keyframes
    raise ValueError("Interpolation failed; check keyframe setup.")

def interpolate_wrapping_backward(input_pos: float, keyframes: List[Tuple[int, float]]) -> float:
    num_keyframes = len(keyframes)
    step_size = 8  # The increment step size between keyframes
    
    # Normalize the input position to the wrapping range (0-95)
    input_pos = input_pos % 96

    # Find the keyframes before and after the input position, but in reverse direction
    for i in range(num_keyframes):
        end_keyframe = keyframes[i]
        start_keyframe = keyframes[(i - 1) % num_keyframes]  # Wrap around using modulo

        # Adjust start_keyframe to handle wrap-around between 0 and 88
        if start_keyframe[0] == 88 and input_pos < end_keyframe[0]:
            start_input = -8
        else:
            start_input = start_keyframe[0]

        if start_input <= input_pos < end_keyframe[0] or (end_keyframe[0] == 0 and input_pos >= start_keyframe[0]):
            # Linear interpolation in reverse
            start_corrected = start_keyframe[1]
            end_input, end_corrected = end_keyframe

            # Calculate the interpolation factor in reverse direction
            t = (input_pos - start_input) / (end_input - start_input)
            
            # Interpolate the corrected position
            corrected_pos = start_corrected + t * (end_corrected - start_corrected)
            return corrected_pos

    # This point should not be reached due to the wrapping nature of the keyframes
    raise ValueError("Interpolation failed; check keyframe setup.")

class Default():
    MTR_OFFSET = 2 / 12 * math.tau
    NAME = "Susan"
    COL_PER_ROTATION = 12
    COL_TOTAL = 96
    CURRENT = 750 # mA

class Susan(Dynamixel):
    @classmethod
    def get_default(cls):
        baud = 1000000
        port = "/dev/ttyACM0"
        ser = SerialMicrocontroller()
        susan = Susan(id = 13, port=port, baudrate=baud, serialBoi = ser)
        return susan
     
    def __init__(self, 
                 id, port, baudrate, 
                 serialBoi : SerialMicrocontroller,
                 motor_offset = Default.MTR_OFFSET,
                 name = Default.NAME,
                 col_per_rotation = Default.COL_PER_ROTATION,
                 col_total = Default.COL_TOTAL):
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        # self.off()
        # super().reboot()
        self.cereal = serialBoi
        self.col_per_rotation = col_per_rotation
        self.col_total = col_total
        self.motor_offset = motor_offset
        self._setup_motor()
        atexit.register(self.off)
                
    def _setup_motor(self):
        self.off()
        # self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self.set_mode(Mode.EXTENDED_POSITION)
        self.on()
        self.set_goal_current(Default.CURRENT)
        
    def indicate(self):
        self.off()
        self.set_mode(Mode.VELOCITY)
        self.on()
        self.set_goal_velocity(math.tau)
        while not self.cereal.get_susan_hall():
            time.sleep(.01)
        self.set_goal_velocity(0)
        while(self.get_velocity() > math.tau/16):
            time.sleep(.001)
        self.off()
        self.set_mode(Mode.POSITION)
        self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self.set_goal_current(1000)
        self._set_goal_position(0)
        self.set_profile_velocity(math.tau)
        self.set_profile_acceleration(math.tau*100)
        self.set_position_D_gain(200)
        self.set_position_I_gain(300)
        self.set_position_P_gain(500)

        self.on()
        print("susan indicated")
    
    def _set_goal_position(self, angle):
        self.set_goal_position(angle * (self.col_total / self.col_per_rotation) + self.motor_offset)
    
    def _get_position(self):
        return (self.get_position() - self.motor_offset) / (self.col_total / self.col_per_rotation)
    
    def go_to_column_nearest(self, column):
        if (column < 0 or column >= self.col_total):
            raise ValueError("Column number must be between 0 and {}".format(self.col_total - 1))
        goal = column + round(self.at_column() - self.at_column_absolute())
        # print("goal :       ", goal)
        # print("current :    ", self.get_column())
        
        delta = column - self.at_column_absolute()
        # print("delta :  ", delta)
        if delta > 48:
            goal = goal - 96
            # print("down one")
        elif delta < -48:
            goal = goal + 96
            # print("up one")
        # print("going to :   ", goal)
        self.go_to_column(goal, error_checker = False)
        print()

    def go_to_column(self, column, error_checker = True):
        if error_checker and (column < 0 or column >= self.col_total):
            raise ValueError("Column number must be between 0 and {}".format(self.col_total - 1))
        self._set_goal_position(math.tau * column / (self.col_total))
        
    def at_column(self):
        current_pos = self._get_position()
        current_column = (current_pos / math.tau) * self.col_total
        return current_column
          
    def at_column_absolute(self):
        return self.at_column() % self.col_total
    
    def __sendMessage(self, stringg):
        timeout = 0.01  # Timeout value in seconds
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            self.cereal.write(stringg.encode())
            echo_message = self.cereal.readline().decode(errors='ignore').strip()
            if echo_message:
                return echo_message
        return None

    def get_dist_to_goal(self):
        return abs(self.get_goal_position() - self.get_position())/math.tau * self.col_per_rotation

    def is_there(self, tolerance = .2):
        return self.get_dist_to_goal() < tolerance
        
if __name__ == '__main__':
    susan = Susan.get_default()
    print(susan.get_model())
    susan.on()
    susan.indicate()
    while(True):
        # print("Column at : ", susan.get_column())
        number = float(input("Please enter a number: "))
        print("Number : " , number)
        # susan.set_column(number, error_checker = False)
        susan.go_to_column_nearest(number)
        while True:
            x = susan.get_dist_to_goal()
            time.sleep(.25)
            print(susan.get_current())
            # print("dist_to_goal, ", x)
            if abs(x) < .05:
                break
        print("Susan at : ", susan.at_column_absolute())