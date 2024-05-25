from enum import Enum, auto
import math
from datetime import datetime 
import time

# Enumeration for different communication protocols, probably for interfacing with devices.
class Protocol(Enum):
    VIRTUAL = auto()
    RS_485 = auto()
    I2C = auto()
    CAN = auto()
    SPI = auto()
    SERIAL = auto()
    DYNAMIXEL = auto()

class waiter:
    def __init__(self):
        self.now = time.time()
        self.till = self.now
        
    def record_now(self):
        self.now = time.time()
        
    def wait(self, seconds):
        self.till = time.time() + seconds
        
    def if_past(self) -> bool:
        return (time.time() > self.till)