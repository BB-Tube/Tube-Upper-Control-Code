from .util import *
from abc import ABC, abstractmethod
from .abstract_component import ComponentInterface
from .units import *

class Mode(Enum):
    CURRENT = 0
    VELOCITY = 1
    POSITION = 3
    EXTENDED_POSITION = 4
    EXTENDED_POSITION_CURRENT = 5
    PWM = 16

### Motor Exceptions 
### Only works with motors that are intelligent
### hard required implementations are abstractmethods

class Motor(ComponentInterface, ABC): 
    def __init__(self, id, port, protocol, units = Units(), name = None):
        self.id = id
        self.mv = []
        self.port = port
        self.protocol = protocol
        super().__init__(name = name, units = units)
        
        self.velocity_limit = None
        self.current_limit = None
        
    def _log_bounds(self):
        self.velocity_limit = self.get_velocity_limit()
        self.current_limit = self.get_current_limit()
    
    @abstractmethod
    def set_enable(self, state):
        """
        Abstract method to enable or disable the actuator based on the provided state.
        Subclasses must implement this method to define specific enabling/disabling logic.
        
        Parameters:
        - state (bool): True to enable, False to disable.
        """
        
        ### any class that does not use set_enable must instantiate it and super to this
        pass

    @abstractmethod
    def get_enable(self, names = False):
        pass
        
    @abstractmethod
    def get_model(self):
        pass
            
    @abstractmethod       
    def set_mode(self, mode : Mode) :
        pass

    @abstractmethod
    def get_mode(self) -> Mode:
        pass
    
    @abstractmethod
    def get_max_voltage_limit(self):
        pass
    
    @abstractmethod
    def get_min_voltage_limit(self):
        pass
    
    @abstractmethod
    def get_current_limit(self):
        pass
    
    @abstractmethod
    def get_velocity_limit(self):
        pass
    
    def get_input_voltage(self):
        return None    

    def get_goal_velocity(self):
        return None    
    
    def set_goal_velocity(self, value):
        return None    
    
    def get_goal_effort(self):
        return None    

    def set_goal_effort(self, value):
        return None    
    
    def set_goal_current(self):
        return None    
    
    def get_goal_current(self):
        return None    
    
    def set_goal_velocity(self, value):
        return None    
    
    def get_goal_velocity(self):
        return None    
    
    def get_goal_position(self):
        return None
    
    def set_goal_position(self, value):
        return None
    
    def get_current(self):
        return None
        
    def get_velocity(self):
        return None
        
    def get_position(self):
        return None
    
    def get_input_voltage(self):
        return None
        
    def get_temperature(self):
        return None
    
class ValueOutOfRangeError(Exception):
    def __init__(self, value, min_val, max_val, range_name : Enum):
        self.value = value
        self.min_val = round(min_val, 4)
        self.max_val = round(max_val, 4)
        self.range_name = range_name
        super().__init__(f"Value {value} is out of range for {range_name.name}. Range: [{self.min_val}, {self.max_val}]")

if __name__  == '__main__':
    pass    