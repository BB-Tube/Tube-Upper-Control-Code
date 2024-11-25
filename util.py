from enum import Enum, auto
import time

class State(Enum):
    READY = auto()
    BUSY = auto()

class ScreenState(Enum):
    MOVING = auto()
    EMPTYING = auto()
    FILLING = auto()

class StalledState(Enum):
    STALLED = auto()
    BACKING_OFF = auto()
    COOLDOWN = auto()
    
class Ball(Enum):
    NONE = ' '
    WHITE = 'w'
    BLACK = 'b'

BALL_COLOR = { ### BGR 
    Ball.WHITE: [189, 190, 189],
    Ball.BLACK: [56, 57, 62]
}
    
reverse_lookup = {v.value: v for v in Ball}
def ball_reverse_index(value):
    looked_up = reverse_lookup.get(value, None)
    # print(type(looked_up))
    # print(looked_up)
    return looked_up

class Waiter:
    def __init__(self):
        self.now = time.time()
        self.till = self.now
        
    def record_now(self):
        self.now = time.time()
        
    def wait(self, seconds):
        self.till = time.time() + seconds
        
    def if_past(self) -> bool:
        return (time.time() > self.till)
    
if __name__ == "__main__":
    print(ball_reverse_index('w'))