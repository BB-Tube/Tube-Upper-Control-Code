
from util_gyz.util import waiter
from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import *
import math
from dynamixel_unstall import *

class Dynamixel_Cont_Unstall(Dynamixel_Unstall):
    def __init__(self, 
                 id, port, baudrate, 
                 name = "Unstalled_Motor",
                 anticlockwise = True,
                 backoff = Default.BACK_OFF_AMOUNT,
                 current : float = Default.JAMMED_CURRENT, 
                 velocity : float = Default.SPEED,
                 current_tolerance = Default.CURRENT_TOLERANCE,
                 velocity_tolerance = Default.VELOCITY_TOLERANCE,
                 check_Stall_time = Default.CHECK_STALL_TIME,
                 back_off_time = Default.BACK_OFF_TIME,
                 cooldown_time = Default.COOLDOWN_TIME): 
        super().__init__(
            id = id, 
            port=port, 
            baudrate=baudrate, 
            name=name,
            backoff = backoff,
            current = current,
            velocity = velocity,
            current_tolerance = current_tolerance,
            velocity_tolerance = velocity_tolerance,
            check_Stall_time = check_Stall_time,
            back_off_time = back_off_time,
            cooldown_time = cooldown_time)
        self.anticlockwise = anticlockwise
        self.set_goal_current(current)
        self.set_goal_velocity(velocity)
    
    def set_goal_velocity(self, velocity):
        self.set_profile_velocity(velocity)
        
    def bump_position(self, rotations = 5):
        current_position = self.get_position()
        delta = rotations * math.tau
        if not self.anticlockwise:
            delta *= -1
        
        self.set_goal_position(current_position + delta)
    
    def update(self):
        super().update()
        self.bump_position()
        
if __name__ == "__main__":
    DISPO_DRIVER = "Driver Elevator"
    ELEVATOR_ID = 20
    PORT = "/dev/ttyUSB0"
    
    motor = Dynamixel_Cont_Unstall(
        id = ELEVATOR_ID, 
        port = PORT, 
        baudrate = 57600, 
        anticlockwise = False,
        backoff = math.tau,
        current = 800,
        velocity = math.tau * 3,
        back_off_time = 2,
        cooldown_time = .5,
        velocity_tolerance = .05)
    
    while(True):
        motor.update()