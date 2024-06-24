from util_gyz.util import waiter
from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import *
import math

class Default:
    JAMMED_CURRENT = 400 # ma
    BACK_OFF_AMOUNT = math.tau / 6
    SPEED = math.tau * 3,
    
    CHECK_STALL_TIME = .01
    BACK_OFF_TIME = .5
    COOLDOWN_TIME = .15
    
    CURRENT_TOLERANCE = 50 # ma
    VELOCITY_TOLERANCE = math.pi/10
    
class State:
    READY = 0
    STALLED = 1
    BACKING_OFF = 2
    COOLDOWN = 3
    
class Dynamixel_Unstall(Dynamixel):
    def __init__(self, 
                 id, port, baudrate, 
                 name = "Unstalled_Motor",
                 backoff = Default.BACK_OFF_AMOUNT,
                 current : float = Default.JAMMED_CURRENT, 
                 velocity : float = Default.SPEED,
                 current_tolerance = Default.CURRENT_TOLERANCE,
                 velocity_tolerance = Default.VELOCITY_TOLERANCE,
                 check_Stall_time = Default.CHECK_STALL_TIME,
                 back_off_time = Default.BACK_OFF_TIME,
                 cooldown_time = Default.COOLDOWN_TIME): 
        ### Motor Setup
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        
        self.BACKOFF = backoff

        self.CURRENT_LIMIT = current
        self.VELOCITY_PROFILE = velocity
        self.CURRENT_TOLERANCE = current_tolerance
        self.VELOCITY_TOLERANCE = velocity_tolerance
        
        self.CHECK_STALL_TIME = check_Stall_time
        self.BACK_OFF_TIME = back_off_time
        self.COOLDOWN_TIME = cooldown_time

        self.state = State.READY

        self._setup_motor()
        
        self.check_stall_timer = waiter()
        self.backed_off_timer = waiter()
        self.cooldown_timer = waiter()
        
        self.last_goal_position = self.get_goal_position()
            
    def _setup_motor(self):
        self.off()
        self.set_mode(Mode.POSITION)
        self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self.set_goal_current(self.CURRENT_LIMIT)
        self.set_profile_velocity(self.VELOCITY_PROFILE)
        self.set_profile_acceleration(1000)
        self.on()
        self.set_goal_position(self.get_position())
        
    def set_goal_position(self, position, ready_override = False, log = True):
        if log:
            self.last_goal_position = position
        if ready_override or self.is_ready():
            super().set_goal_position(position)
     
    def is_ready(self):
        ready = None
        if self.state is State.READY:
            ready = True
        else:
            ready = False
        return ready
        
    def update(self):
        if self.state == State.READY:
            stalled = False
            if self.check_stall_timer.if_past():
                stalled = self.is_stalled()
                self.check_stall_timer.wait(self.CHECK_STALL_TIME)
            if stalled:
                self.state = State.STALLED
                
        if self.state == State.STALLED:
            self.unstall()
            self.state = State.BACKING_OFF
            self.backed_off_timer.wait(self.BACK_OFF_TIME)
            
        if self.state == State.BACKING_OFF:
            if self.backed_off_timer.if_past():
                self.resume()
                self.state = State.COOLDOWN 
                self.cooldown_timer.wait(self.COOLDOWN_TIME)       
                
        if self.state == State.COOLDOWN:
            if self.cooldown_timer.if_past():
                if self.is_stalled():
                    self.state = State.STALLED
                else:
                    self.state = State.READY
                
            
    def is_stalled(self):
        # if current limit is reached
        current_limited = self.CURRENT_LIMIT - self.CURRENT_TOLERANCE < abs(self.get_current()) 
        # if velocity is near zero
        velocity_near_zero = (abs(self.get_velocity()) < self.VELOCITY_TOLERANCE)
        
        return current_limited and velocity_near_zero
    
    def unstall(self):
        sign_delta = math.copysign(1, self.get_current())
        backoff = -1 * sign_delta * self.BACKOFF
        self.set_goal_position(
            self.get_position() + backoff, 
            ready_override = True,
            log = False)
        
    def resume(self):
        self.set_goal_position(self.last_goal_position, ready_override = True)
    
if __name__ == "__main__":
    DISPO_DRIVER = "Driver Dispo"
    DISPO_ID = 16
    PORT = "/dev/ttyUSB0"
    motor = Dynamixel_Unstall(
        id=DISPO_ID, port=PORT, name=DISPO_DRIVER, 
        baudrate=57600, velocity=math.tau * 6)
    print(motor.get_model())
    
    w = waiter()
    motor.set_goal_position(-2000)
    while(True):
        motor.update()
        # print(motor.is_ready())
        if w.if_past():
            w.wait(.5)
            pos = motor.get_position()
            vel = motor.get_velocity()
            cur = motor.get_current()
            print()
            print("Position : ", pos)
            print("Velocity : ", vel)
            print("Current :  ", cur)