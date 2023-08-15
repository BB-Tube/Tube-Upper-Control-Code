from dynamixel import dynamixel
from waiter import waiter
import time
from datetime import datetime
import serial
import collections
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
t = time.time()
r = 45 # increment by
flipRevolver = True

last_ball = 'n'

class sorter(object):
    
    
    def __init__(self, revolver : dynamixel, arm : dynamixel, revolver_count = 8):
        self.revolver = revolver
        self.revolver.set_mode(4)
        self.revolver.set_enable(True)
        # self.revolver.set_profile_velocity(6/8)
        
        self.last_ball = 'n'
        
        self.arm = arm
        self.arm.set_mode(3)
        self.arm.set_enable(True)
        
        self.revolver_increment = self.zero_revolver()
        revolver.set_extended_position(self.revolver_increment * r)

        
    def zero_revolver(self):
        currPos = revolver.get_extended_position()
        print("currPos              ", currPos)
        print("r                    ",r)
        ri = self.__round_to_multiple(currPos, r) / r
        print("revolver increment:  ", ri)
        goto = ri * r
        print("goto                 ", goto)
        return ri
            
        
    def next_ball(self):
        if flipRevolver:
            self.revolver_increment += -1
        else:
            self.revolver_increment += 1
        goal = self.revolver_increment * r
        self.revolver.set_extended_position(goal)
        diff = 10
        while not abs(diff) < 8:
            self.revolver.set_extended_position(goal)
            diff = goal - self.revolver.get_extended_position()
        
    def __round_to_multiple(self, number, multiple):
        return multiple * round(number / multiple)
    
    def get_ball_color(self):
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
            ser.write(stringg.encode())
            echo_message = ser.readline().decode(errors='ignore').strip()
            if echo_message:
                return echo_message
        return None
    
    def update(self):
        # print("sample")
        sample = 3
        balls_read = ""
        # print(balls_read)
        for i in range(sample):
            balls_read = balls_read + self.get_ball_color()
        ball_color = collections.Counter(balls_read).most_common(1)[0][0]

        # print("balls_read:  ", balls_read)
        # print("ball_color:  ", ball_color)
        
        # print(ball_color)
        if  ball_color == 'n':
            # print("none")            
            self.next_ball()
            
        if ball_color == 'b':
            print("black")
            if not self.last_ball == ball_color:
                self.set_arm(-1)
            self.last_ball = ball_color
            # print("next ball")
            self.next_ball()
            
        if ball_color == 'w':
            print("white")
            if not self.last_ball == ball_color:
                self.set_arm(1)
            self.last_ball = ball_color
            # print("next ball")
            self.next_ball()

    def set_arm(self, angle):
        offset = 12
        neutral = 181
        goal = neutral + angle * offset
        self.arm.set_position(goal)
        diff = 10
        time.sleep(.01)
        while False and not abs(diff) < 10:
            # print(self.arm.get_position())
            # print(diff)
            # time.sleep(.01)
            diff = goal - self.arm.get_position()

if __name__ == '__main__':
    arm = dynamixel(ID = 3, op = 3)
    revolver = dynamixel(ID = 2, op = 4)
    s = sorter(revolver, arm)
 
    # s.next_ball()
    iterator = 0
    while True:
        # iterator += 1
        # print(iterator, " balls ", s.get_ball_color())
        # s.next_ball()
        # time.sleep(.01)
        s.update()
        time.sleep(.001)
        print(time.time())
        # s.set_arm(-1)
        # time.sleep(1)
        # s.set_arm(1)
        # time.sleep(1)

