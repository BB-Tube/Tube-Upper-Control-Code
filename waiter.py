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

if __name__ == "__main__":
    w = waiter()
    do = True
    
    while True:
        if do or w.if_past():
            do = False
            print(time.time())
            w.wait(4)
            