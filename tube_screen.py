from enum import Enum
from susan import Susan
from dispo import Dispo
from emptier import Emptier

class State(Enum):
    WAITING = 0
    MOVING = 1
    EMPTYING = 2
    FILLING = 3
    
class Defaults():
    EMPTY_TIME = 3 # seconds
    
class Tube_Screen():
    def __init__(self, 
            susan : Susan,
            dispo : Dispo,
            emptier : Emptier):
        self.susan = susan
        self.dispo = dispo