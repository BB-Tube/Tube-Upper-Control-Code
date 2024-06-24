from enum import Enum, auto
import math
from datetime import datetime 
import time

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
    
