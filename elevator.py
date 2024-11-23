from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter
import time 
import math
from dynamixel_cont_unstall import Dynamixel_Cont_Unstall

class Default():
    ### ID typical is 20
    OPEN = 0
    CLOSED = math.pi
    JAMMED_CURRENT = 1200 # ma

class Elevator():
    def __init__(self, 
            id = None, 
            port = None, 
            baudrate = None, 
            anticlockwise = False,
            backoff = math.tau,
            current = 1000,
            velocity = math.tau * 3,
            back_off_time = 2,
            cooldown_time = .5,
            velocity_tolerance = .05,
            name = "elevator",
            follower_id = 0):
        self.elevator = Dynamixel_Cont_Unstall(
            id = id, 
            port=port, 
            baudrate=baudrate, 
            anticlockwise=anticlockwise,
            backoff=backoff,
            current=current,
            velocity=velocity,
            back_off_time=back_off_time,
            cooldown_time=cooldown_time,
            velocity_tolerance=velocity_tolerance)
        self.elevator_secondary = Dynamixel(
            id = follower_id,
            port = port,
            baudrate = baudrate
        )

    def update(self):
        self.elevator.update()
        self.elevator_secondary.set_goal_current(self.elevator.get_current())
        
    def on(self):
        self.elevator.on()
        self.elevator_secondary.on()

    def off(self):
        self.elevator.off()
        self.elevator_secondary.off()

    def get_model(self):
        return [self.elevator.get_model(), self.elevator_secondary.get_model()]

if __name__ == '__main__':
    ID_ELEVATOR = 20
    ID_ELEVATOR_SECONDARY = 19
    PORT_DYNAMIXELS = "/dev/ttyACM0"
    BAUD_DYNAMIXELS = 1000000

    elevator = Elevator(
        id = ID_ELEVATOR, 
        port = PORT_DYNAMIXELS, 
        baudrate = BAUD_DYNAMIXELS, 
        anticlockwise = False,
        backoff = math.tau,
        current = 1000,
        velocity = math.tau * 3,
        back_off_time = 2,
        cooldown_time = .5,
        velocity_tolerance = .05,
        follower_id = ID_ELEVATOR_SECONDARY)
    
    elevator.off()

    while(True):
        elevator.update()
        



