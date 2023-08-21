from dynamixel import dynamixel
import time
from waiter import waiter

ball_dict = {
        'b' : 193,
        'n' : 181,
        'w' : 169
    }

class arm(object):
    def __init__(self, 
                motor : dynamixel):
        self.motor = motor
        self.motor.set_mode("Current-based_Position")
        self.motor.set_enable(True)
        
        self.check_stall_timer = waiter()
        self.check_stall_timer.wait(.1)
        self.got_stalled = False
        self.last_input = 'n'
        self.last_last_input = 'n'
        self.backed_off = waiter()
        self.backed_off.wait(.1)

    def ball_input(self, ball):
        if not ball == self.last_input:
            goal = self.__goal(ball)
            self.move_to(goal)
        self.last_last_input = self.last_input
        self.last_input = ball
        
    def move_to(self, degrees):
        self.motor.set_position_current(degrees, self.current_limit)

    def if_there(self, margin = 3):
        if self.last_last_input == self.last_input:
            # print("     did nothing")
            return True
        if not self.backed_off.if_past(): # waiting for back off
            return False
        if self.got_stalled: # trigger restart
            self.got_stalled = False
            self.ball_input(self.last_input)
            return False
        if self.__if_stalled(): # if stalled
            self.got_stalled = True
            print("     Stalled!!!!!!!!!!!!!!!!!!")
            self.__back_off()
            self.backed_off.wait(.5)
            return False
        at = self.motor.get_extended_position()
        return abs(self.__goal(self.last_input) - at) < abs(margin)
    
    def __back_off(self):
        self.motor.set_position_current(self.__goal('n'), self.current_limit)
        
    
    def set_current_limit(self, milliamps):
        self.current_limit = milliamps
    
    def __if_stalled(self, current_margin = 20):
        if self.check_stall_timer.if_past():
            self.check_stall_timer.wait(.3)
            current_milliamp = self.motor.get_current()
            if (abs(current_milliamp) > (self.current_limit - current_margin)):
                return True
        return False
            
    def __goal(self, ball):
        return ball_dict[ball]
                  
if __name__ == '__main__':
    motor = dynamixel(ID = 2, op = 4)
    r = arm(motor)
    r.set_current_limit(800)
    
    iterator = 0
    start = time.monotonic()
    delta = 0
    while True:
        if r.if_there(10):
            r.next_slot(10)
            iterator += 1
            delta = round(time.monotonic() - start,3)
            print(iterator, " time is ", delta)
            if iterator == 100:
                break

    print("balls per second = ", round(iterator / delta, 2))