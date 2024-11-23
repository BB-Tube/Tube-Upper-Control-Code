import time
from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
from dynamixel_unstall import Dynamixel_Unstall, Default_Dynamixel_Unstall
from util import *
import atexit

class Default():
    ### ID typical is 20]
    POSITION_TOLERANCE = math.radians(15) # radians

class Revolver(Dynamixel_Unstall):
    def __init__(self, 
            id, port, baudrate, 
            name = "Revolver",
            slots : float = 8, 
            offset : float = 0,
            position_tolerance = Default.POSITION_TOLERANCE,
            flip : bool = False,
            backoff = math.tau/10,
            current : float = Default_Dynamixel_Unstall.JAMMED_CURRENT, 
            velocity : float = Default_Dynamixel_Unstall.SPEED,
            current_tolerance = Default_Dynamixel_Unstall.CURRENT_TOLERANCE,
            velocity_tolerance = Default_Dynamixel_Unstall.VELOCITY_TOLERANCE,
            check_Stall_time = Default_Dynamixel_Unstall.CHECK_STALL_TIME,
            back_off_time = Default_Dynamixel_Unstall.BACK_OFF_TIME,
            cooldown_time = Default_Dynamixel_Unstall.COOLDOWN_TIME): 
        super().__init__(
            id = id, port=port, baudrate=baudrate, 
            name=name,
            backoff = backoff,
            current = current,
            velocity = velocity,
            current_tolerance = current_tolerance,
            velocity_tolerance = velocity_tolerance,
            check_Stall_time = check_Stall_time,
            back_off_time = back_off_time,
            cooldown_time = cooldown_time)
        self.set_profile_acceleration(0)
        self.flip = flip
        self.offset = offset # not absolute
        self.r = math.tau / slots # amount turn per slot
        
        self.slot = self.get_slot()
        self.goal_position = None
        Revolver.set_goal_position(self, self.__set_slot())
        self.last_position = 0
        
        self.POSITION_TOLERANCE = position_tolerance
        self.revolver_state = State.READY
      
    def next_slot(self, overshoot = 0):
        self.revolver_state = State.BUSY
        return self.move_slot(forwards = True, overshoot = overshoot)
    
    def back_slot(self, overshoot = 0):
        self.revolver_state = State.BUSY
        return self.move_slot(forwards = False, overshoot = overshoot)
    
    def move_slot(self,
            overshoot = 0, 
            forwards = True):
        self.slot = self.get_slot()
        
        ## manage overshoot
        over = abs(overshoot)
        if self.flip:
            over *= -1
            
        ## manage case of back vs forwards
        if forwards:
            self.__increment()        
            Revolver.set_goal_position(self, self.__set_slot() + over)
        else:
            self.__decrement()
            Revolver.set_goal_position(self, self.__set_slot() - over)
            
    def set_goal_position(self, position):
        self.goal_position = position
        super().set_goal_position(position)
     
    def __increment(self):
        if self.flip:
            self.slot += -1
        else:
            self.slot += 1
    
    def __decrement(self):
        if not self.flip:
            self.slot += -1
        else:
            self.slot += 1
     
    def get_slot(self):
        """
            Returns slot index nearest from current motor position
        """        
        def __round_to_multiple(number, multiple):
            return multiple * round(number / multiple)
        
        current_position = self.get_position() - self.offset
        slot = __round_to_multiple(current_position, self.r) / self.r
        return slot
    
    def __set_slot(self):
        """
            returns motor goal position for the motor from self.slot
        """
        return self.slot * self.r + self.offset

    def update(self):
        ### Check if motor is jammed
        super().update()
        
        not_stalled = super().get_state() == State.READY
        close_enough = self.check_proximity()
        stopped = self.check_speed()

        if not_stalled and close_enough and stopped:
            self.revolver_state = State.READY
        else:
            self.revolver_state = State.BUSY
    
    def get_state(self):
        return self.revolver_state
        
    def check_proximity(self):
        return self.get_proximity() < self.POSITION_TOLERANCE

    def check_speed(self):
        velocity = self.get_velocity()
        speed = abs(velocity)
        return speed < math.radians(30)

    def get_proximity(self):
        return abs(self.get_position() - self.goal_position)
        
if __name__ == '__main__':
    baud = 57600
    port = "/dev/ttyUSB0"
    # d = Dynamixel(14, port, baud)
    # print(d.get_model())
    r = Revolver(14, port, baud, 8, flip=True,
        current = 500, velocity= 0, offset=math.radians(15))
    
    iterator = 0
    start = time.monotonic()
    delta = 0
    while True:
        r.update()
        
        if r.get_state() == State.READY:
            r.next_slot()
            iterator += 1
            delta = round(time.monotonic() - start,3)
            print(iterator, " time is ", delta)
            if iterator == 100:
                break

    time.sleep(10)

    # print("balls per second = ", round(iterator / delta, 2))