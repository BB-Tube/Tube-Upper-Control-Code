from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time
from datetime import datetime
import serial
from collections import Counter
import math

class Default():
    MTR_OFFSET = 2.1 / 12 * math.tau
    NAME = "Susan"
    ASK_KEY = 's'
    PASS_KEY = '1'
    COL_PER_ROTATION = 12
    COL_TOTAL = 96

class Susan(Dynamixel):
     
    def __init__(self, 
                 id, port, baudrate, 
                 serialBoi : serial,
                 motor_offset = Default.MTR_OFFSET,
                 name = Default.NAME,
                 ask_key = Default.ASK_KEY,
                 pass_key = Default.PASS_KEY,
                 col_per_rotation = Default.COL_PER_ROTATION,
                 col_total = Default.COL_TOTAL):
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        self.cereal = serialBoi
        self.ask_key = ask_key
        self.pass_key = pass_key
        self.col_per_rotation = col_per_rotation
        self.col_total = col_total
        self.motor_offset = motor_offset
        self._setup_motor()
                
    def _setup_motor(self):
        self.off()
        self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self.on()
        self.set_goal_current(400)
        
    def indicate(self):
        self.off()
        self.set_mode(Mode.VELOCITY)
        self.on()
        self.set_goal_velocity(math.tau)
        while(self._read_sensor() == self.pass_key):
            time.sleep(.01)
        self.set_goal_velocity(0)
        while(self.get_velocity() > math.tau/16):
            time.sleep(.001)
        self.off()
        self.set_mode(Mode.POSITION)
        self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self._set_goal_position(0)
        self.on()
    
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
           
    def _read_sensor(self):
        while(True):
            ball_color = self.__sendMessage(self.ask_key)
            if ball_color is None:
                pass
            else:
                return ball_color
        
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

if __name__ == '__main__':
    baud = 57600
    port = "/dev/ttyUSB0"
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    susan = Susan(id = 13, port=port, baudrate=baud, serialBoi = ser)
    susan.on()
    susan.indicate()
    susan.on()
    while(True):
        # print("Column at : ", susan.get_column())
        number = float(input("Please enter a number: "))
        print("Number : " , number)
        # susan.set_column(number, error_checker = False)
        susan.go_to_column_nearest(number)
        while True:
            x = susan.get_dist_to_goal()
            # print("dist_to_goal, ", x)
            if abs(x) < .2:
                break
        print("Susan at : ", susan.at_column_absolute())
        



