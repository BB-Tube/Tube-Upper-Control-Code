from dynamixel import dynamixel
import time
from waiter import waiter

class revolver(object):
    def __init__(self, 
                 motor : dynamixel, 
                 slots : float, 
                 current_Limit : float = 500, 
                 offset : float = 0, 
                 flip : bool = False):
        self.motor = motor
        self.motor.set_mode("Current-based_Position")
        self.motor.set_enable(True)
        self.flip = flip
        self.offset = offset # not absolute
        self.current_limit = current_Limit
        self.r = 360 / slots
        self.slot = self.__get_slot()
        self.__goal()
        
        self.check_stall_timer = waiter()
        self.check_stall_timer.wait(.1)
        self.got_stalled = False
        self.last_position = 0
        self.backed_off = waiter()
        self.backed_off.wait(.1)
      
    def next_slot(self, overshoot = 0):
        self.slot = self.__get_slot()
        over = abs(overshoot)
        if self.flip:
            over *= -1
        self.__increment()
        self.motor.set_position_current(self.__goal() + over, self.current_limit)

    def if_there(self, margin = 3):
        if not self.backed_off.if_past(): # waiting for back off
            return False
        if self.got_stalled: # trigger restart
            self.got_stalled = False
            self.next_slot()
        if self.__if_stalled(): # if stalled
            self.got_stalled = True
            print("Stalled")
            self.__back_off(60)
            self.backed_off.wait(.5)
            return False
        at = self.motor.get_extended_position()
        return abs(self.__goal() - at) < abs(margin)
    
    def __back_off(self, back_off_degrees):
        degrees = back_off_degrees
        if self.flip: degrees *= -1
        current_position = self.motor.get_extended_position()
        goto = current_position - degrees
        self.motor.set_position_current(goto, self.current_limit)
    
    def set_current_limit(self, milliamps):
        self.current_limit = milliamps
    
    def __if_stalled(self, position_margin = 5, current_margin = 20):
        if self.check_stall_timer.if_past():
            self.check_stall_timer.wait(.3)
            current_position = self.motor.get_extended_position()
            current_milliamp = self.motor.get_current()
            if (abs(current_milliamp) > (self.current_limit - current_margin)) and (abs(self.last_position - current_position) < position_margin):
                return True    
            else:
                self.last_position = current_position
        return False
     
    def __increment(self):
        if self.flip:
            self.slot += -1
        else:
            self.slot += 1
          
    def __get_slot(self):
        current_position = self.motor.get_extended_position() - self.offset
        # print("Current Position     ", current_position)
        # print("Amount to shift:     ", self.r)
        slot = self.__round_to_multiple(current_position, self.r) / self.r
        # print("Current Slot         ", slot)
        return slot
            
    def __goal(self):
        return self.slot * self.r + self.offset
            
    def __round_to_multiple(self, number, multiple):
        return multiple * round(number / multiple)
                  
if __name__ == '__main__':
    motor = dynamixel(ID = 2, op = 4)
    r = revolver(motor, 8, flip=True)
    r.set_current_limit(800)
    while True:
        if r.if_there(20):
            r.next_slot(20)
        