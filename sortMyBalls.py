from dynamixel import dynamixel
from waiter import waiter
import time
from datetime import datetime
import serial
from collections import Counter
from revolver import revolver

t = time.time()
r = 45 # increment by
flipRevolver = True

last_ball = 'n'


# BALL INFORMATION 
BALL_NONE = 'n'
BALL_BLACK = 'b'
BALL_WHITE = 'w'
ball_print = {
    BALL_NONE : "None",
    BALL_BLACK : "Black",
    BALL_WHITE : "White"
}

class sorter(object):
     
    def __init__(self, revolver : revolver, arm : dynamixel, serialBoi : serial, samples = 3):
        self.revolver = revolver
        self.revolver.set_current_limit(800)
        
        self.sample_size = samples
        
        self.cereal = serialBoi
        
        self.last_ball = 'n'
        
        self.arm = arm
        self.arm.set_mode("Position")
        self.arm.set_enable(True)
           
    def get_ball_color(self, samples=1):
        balls_read = ""
        for i in range(samples):
            balls_read = balls_read + self.read_sensor()
        ball = Counter(balls_read)
        ball = max(ball, key=ball.get)
        return ball
           
    def read_sensor(self):
        while(True):
            ball_color = self.__sendMessage('-')
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

    def set_arm(self, angle):
        offset = 12
        neutral = 181
        goal = neutral + angle * offset
        self.arm.set_position(goal)
        diff = 10
        time.sleep(.01)
            
    def update(self):
        if not self.revolver.if_there(margin=15):
            return False
        
        ball = self.get_ball_color(self.sample_size)
        
        if ball == BALL_NONE:
            pass
            
        if ball == BALL_BLACK:
            print("Black")
            self.set_arm(-1)
            
        if ball == BALL_WHITE:
            print("White")
            self.set_arm(1)
        
        self.revolver.next_slot(overshoot=5)
        
        return True

if __name__ == '__main__':
    arm = dynamixel(ID = 3, op = 3)
    revolver_motor = dynamixel(ID = 2, op = 4)
    revolver = revolver(revolver_motor,8,flip=True)
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    s = sorter(revolver, arm, ser,samples=1)
 
    # s.next_ball()
    iterator = 0
    start = time.monotonic()
    delta = 0
    while True:
        if (s.update()):
            iterator += 1
            delta = round(time.monotonic() - start,3)
            print(iterator, " time is ", delta)
            if iterator == 100:
                break
    print("balls per second = ", round(iterator / delta, 2))
