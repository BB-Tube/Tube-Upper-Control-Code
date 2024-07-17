from dynamixel_unstall import Dynamixel_Unstall, Default_Dynamixel_Unstall
from util import *
import math
import time
import atexit

class Default:
    BALL_DICT = {
        Ball.BLACK : math.radians(190),
        Ball.NONE : math.radians(180),
        Ball.WHITE : math.radians(170)
    }
    POSITION_TOLERANCE = math.tau / 100 # radians

class Arm(Dynamixel_Unstall):
    def __init__(self,
                 id, port, baudrate,
            name = "Arm",
            tolerance = Default.POSITION_TOLERANCE,
            ball_dict = Default.BALL_DICT,
            backoff = Default_Dynamixel_Unstall.BACK_OFF_AMOUNT,
            current : float = Default_Dynamixel_Unstall.JAMMED_CURRENT,
            velocity : float = Default_Dynamixel_Unstall.SPEED,
            current_tolerance = Default_Dynamixel_Unstall.CURRENT_TOLERANCE,
            velocity_tolerance = math.tau/100,
            check_Stall_time = Default_Dynamixel_Unstall.CHECK_STALL_TIME,
            back_off_time = Default_Dynamixel_Unstall.BACK_OFF_TIME,
            cooldown_time = Default_Dynamixel_Unstall.COOLDOWN_TIME):
        super().__init__(
            id = id, port=port, baudrate=baudrate, name=name,
            backoff = backoff,
            current = current,
            velocity = velocity,
            current_tolerance = current_tolerance,
            velocity_tolerance = velocity_tolerance,
            check_Stall_time = check_Stall_time,
            back_off_time = back_off_time,
            cooldown_time = cooldown_time)
        self.set_profile_acceleration(0)
        self.TOLERANCE = tolerance
        self.BALL_DICT = ball_dict
        
        self.goal_position = 0
        
        self.state = State.READY
        self.ball = None
        self.set_ball(Ball.NONE)
        
    def update(self):
        ### Check if motor is jammed
        super().update()
        
        not_stalled = super().get_state() == State.READY
        close_enough = self.get_proximity() < self.TOLERANCE
        
        # print("Arm Proximity :      ", self.get_proximity())
        # print("Arm Position :       ", self.get_position())
        # print("Arm Goal Position :  ", self.get_goal_position())
        # print("Arm Stalled :        ", super().get_state())
        
        if not_stalled and close_enough:
            self.state = State.READY
        else:
            self.state = State.BUSY  
    
    def get_state(self):
        # print(self.state)
        # print(self.get_current())
        return self.state
    
    def set_ball(self, ball):
        if not ball == self.ball:
            self.ball = ball
            self.set_goal_position(self.BALL_DICT[self.ball])
            self.state = State.BUSY
            
    def get_proximity(self):
        return abs(self.get_position() - self.goal_position)
    
    def set_goal_position(self, position):
        self.goal_position = position
        super().set_goal_position(position)
        
if __name__ == "__main__":
    baud = 57600
    port = "/dev/ttyUSB0"
    a = Arm(15, port = port, baudrate = baud,
            current = 400,
            tolerance=math.radians(5))
    
    while True:
        print('b')
        a.set_ball(Ball.BLACK)
        while not a.get_state() == State.READY:
            a.update()
        
        print('w')  
        a.set_ball(Ball.WHITE)
        while not a.get_state() == State.READY:
            a.update()  

        print('n')
        a.set_ball(Ball.NONE)
        while not a.get_state() == State.READY:
            a.update()