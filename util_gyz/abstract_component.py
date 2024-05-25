from abc import ABC, abstractmethod
from .units import *

class ComponentInterface(ABC):
    def __init__(self, name, units : Units = Units()):
        self.name = name
        self.units = units
        
    def set_units(self, units : Units = Units()):
        self.units = units    

    def set_enable(self):
        print("set_enable() not implemented for ", self.name)

    def on(self):
        """
        Convenience method to enable the actuator.
        Calls set_enable with True.
        """
        self.set_enable(True)

    def off(self):
        """
        Convenience method to disable the actuator.
        Calls set_enable with False.
        """
        self.set_enable(False)