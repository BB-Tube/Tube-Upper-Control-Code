import time
from util_gyz.dynamixel import Dynamixel
from util_gyz.abstract_motor import * 
from util_gyz.util import waiter

class Default():
    ### ID typical is 20]
    JAMMED_CURRENT = 800 # ma
    TOLERANCE = math.radians(3)
    BACK_OFF_AMOUNT = math.tau / 6

class revolver(Dynamixel):
    def __init__(self, 
                 id, port, baudrate, 
                 name = "Revolver",
                 slots : float = 8, 
                 current_Limit : float = Default.JAMMED_CURRENT, 
                 offset : float = 0, 
                 flip : bool = False): 
        super().__init__(id = id, port=port, baudrate=baudrate, name=name)
        self._setup_motor()
        self.flip = flip
        self.offset = offset # not absolute
        self.current_limit = current_Limit
        self.r = math.tau / slots # amount turn per slot
        self.slot = self.__get_slot()
        self.set_goal_position(self.__goal())
        
        self.check_stall_timer = waiter()
        self.check_stall_timer.wait(.1)
        self.got_stalled = False
        self.last_position = 0
        self.backed_off = waiter()
        self.backed_off.wait(.1)
        
    def _setup_motor(self):
        self.off()
        self.set_mode(Mode.EXTENDED_POSITION_CURRENT)
        self.set_goal_current(self.current_limit)
        self.on()
      
    def next_slot(self, overshoot = 0):
        self.slot = self.__get_slot()
        over = abs(overshoot)
        if self.flip:
            over *= -1
        self.__increment()
        self.set_goal_position(self.__goal() + over)

    def if_there(self, margin = Default.TOLERANCE):
        if not self.backed_off.if_past(): # waiting for back off
            return False
        if self.got_stalled: # trigger restart
            self.got_stalled = False
            self.next_slot()
        if self.__if_stalled(): # if stalled
            self.got_stalled = True
            print("Stalled")
            self.__back_off(Default.BACK_OFF_AMOUNT)
            self.backed_off.wait(.5)
            return False
        at = self.get_position()
        return abs(self.__goal() - at) < abs(margin)
    
    def __back_off(self, back_off):
        back_off_radians = back_off
        if self.flip: back_off_radians *= -1
        goto = self.get_position() - back_off_radians
        self.set_goal_position(goto)
    
    def __if_stalled(self, position_margin = 5, current_margin = 20):
        current_peaked = False
        position_unchanged = False
        if self.check_stall_timer.if_past():
            self.check_stall_timer.wait(.3)
            current_milliamp = self.get_current()
            if (abs(current_milliamp) > (self.current_limit - current_margin)):
                current_peaked = True
                print("Current draw :   ", current_milliamp, " mA")
            current_position = self.get_position()
            if (abs(self.last_position - current_position) < position_margin):
                position_unchanged = True
            self.last_position = current_position
        return current_peaked and position_unchanged
     
    def __increment(self):
        if self.flip:
            self.slot += -1
        else:
            self.slot += 1
          
    def __get_slot(self):
        current_position = self.get_position() - self.offset
        slot = self.__round_to_multiple(current_position, self.r) / self.r
        return slot
            
    def __goal(self):
        return self.slot * self.r + self.offset
            
    def __round_to_multiple(self, number, multiple):
        return multiple * round(number / multiple)
                  
if __name__ == '__main__':
    baud = 57600
    port = "/dev/ttyUSB0"
    r = revolver(14, port, baud, 8, flip=True)
    r.set_goal_current(800)
    
    iterator = 0
    start = time.monotonic()
    delta = 0
    while True:
        if r.if_there(10):
            r.next_slot(math.radians(10))
            iterator += 1
            delta = round(time.monotonic() - start,3)
            print(iterator, " time is ", delta)
            if iterator == 100:
                break

    print("balls per second = ", round(iterator / delta, 2))