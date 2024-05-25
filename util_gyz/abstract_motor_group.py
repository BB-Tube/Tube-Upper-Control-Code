from abc import ABC
from .abstract_component_group import ComponentGroup
from .abstract_motor import Motor, Mode
from .units import *

### Need to make base functionality of regular motor
class MotorGroup(ComponentGroup, ABC):
    """
    Represents a group of motors or motor groups, allowing for nested structures.
    Implements the motorInterface to ensure that motor groups can be controlled
    just like individual motors.
    """
    def __init__(self, name, motors=None, units = Units()):
        """
        Initializes a MotorGroup with a list of motors or other motorGroups.
        
        Parameters:
        - motors (list of motorInterface): A list of objects implementing the
          motorInterface. Defaults to an empty list if not provided.
        """
        self._motors : list[Motor]= motors if motors is not None else []
        super().__init__(name=name, units=units, components=motors)

    def add_motor(self, mot: Motor):
        """
        Adds a new motor or motorGroup to the existing list of motors.
        
        This method allows for dynamic expansion of the motor group by adding
        individual motors or other motor groups, enabling the flexible
        motosition of motor hierarchies or networks. This is particularly
        useful for creating motlex control systems where motors need to be
        grouped or managed in a modular fashion.

        Parameters:
        - mot (motorInterface): The motor or motorGroup to be added to the
          group. Must implement the motorInterface to ensure motatibility with
          the group's operations.
        """
        self._motors.append(mot)
        self.add_component(mot)
        
    def set_enable(self, state):
        """
        Sets the enable state for all contained actuators or Actuator groups
        by iterating over them and calling their set_enable method with the given state.
        """
        for comp in self._motors:
            comp.set_enable(state)

    def get_enable(self, names = False):
        return self._get_all(Motor.get_enable, names = names)

    @property
    def motors(self):
        """
        Provides access to the list of contained motors or motor groups.
        """
        return self._motors.copy()
        
    @motors.setter
    def motors(self, value):
        """
        Allows replacing the list of motors or motor groups with a new one.
        """
        self._motors = value
        
    def set_mode(self, mode : Mode):
        for motor in self._motors: 
            motor.set_mode(mode)
            
    def get_mode(self, names = False) -> Mode:
        return self._get_all(Motor.get_mode, names = names)
    
    def get_model(self, names = False) -> Mode:
        return self._get_all(Motor.get_model, names = names)
    
    def get_min_voltage_limit(self, names = False):
        return self._get_all(Motor.get_min_voltage_limit, names = names)
    
    def get_max_voltage_limit(self, names):
        return self._get_all(Motor.get_max_voltage_limit, names = names)
    
    def get_current_limit(self, names = False):
        return self._get_all(Motor.get_current_limit, names = names)
    
    def get_velocity_limit(self, names = False):
        return self._get_all(Motor.get_current_limit, names = names)
     
    def _get_all(self, function, names=False):
        results = []
        for motor in self._motors:
            result = function(motor, names)
            results.append(result)
        
        return results if not names else (self.name, results)