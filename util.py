from enum import Enum, auto

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
    NONE = 'n'
    WHITE = 'w'
    BLACK = 'b'
    
reverse_lookup = {v.value: v for v in Ball}
def ball_reverse_index(value):
    looked_up = reverse_lookup.get(value, None)
    # print(type(looked_up))
    # print(looked_up)
    return looked_up