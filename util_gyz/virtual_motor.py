from .abstract_motor import Motor, Mode
from .util import *
from .units import *
import math

class VirtualMotor(Motor):
    def __init__(self, id = 0, port = "Portless", protocol = Protocol.VIRTUAL, units = Units(), name = "DEFAULT_VIRTUAL_MOTOR"):
        super().__init__(id = id, port = port, protocol = protocol, units = units, name = name)
        self.enable = False
        self.mode = Mode.POSITION
        self.model = "!!!!! VIRTUAL !!!!"
        self.min_voltage_limit = 5 # v
        self.max_voltage_limit = 32 # v
        self.current_limit = 1000 # ma
        self.velocity_limit = 6 * math.tau # rad per sec 
        
        self.goal_position = 0
        self.goal_current = 0
        self.goal_velocity = 0

        self._internal_rotational_velocity = Unit_Rotational_Speed.RAD_PER_SEC
        self._internal_current = Unit_Current.AMP
        self._internal_rotational = Unit_Rotation.RADIAN
        self._internal_voltage = Unit_Voltage.VOLT

        self.velocity = 0
        self.current = 0
        self.position = 0

    def set_enable(self, state):
        if state is False and self.enable is True:
            self.position = self.goal_position
            self.current = 0
            self.velocity = 0
        
        if state is True and self.enable is False:
            self.goal_position = self.position
            self.goal_current = 0
            self.goal_velocity = 0
            
        self.enable = state
        
    def get_enable(self, name = False):
        if name:
            return [self.name, self.enable]
        else:
            return self.enable
        
    def get_model(self):
        return self.model
        
    def set_mode(self, mode : Mode):
        if not self.enable:
            self.mode = mode
        
    def get_mode(self):
        return self.mode
    
    def get_max_voltage_limit(self):
        return self.units.convert(self.max_voltage_limit, self._internal_voltage)
    
    def get_min_voltage_limit(self):
        return self.units.convert(self.min_voltage_limit, self._internal_voltage)
    
    def get_current_limit(self):
        return self.units.convert(self.current_limit, self._internal_current)
    
    def get_velocity_limit(self):
        return self.units.convert(self.velocity_limit, self._internal_rotational_velocity)

    def set_goal_velocity(self, value):
        self.goal_velocity = convert_units(value, self.units.REVOLUTION_SPEED, self._internal_rotational_velocity)
        if self.mode is Mode.VELOCITY and self.enable and abs(self.goal_velocity) < self.velocity_limit:
            self.velocity = self.goal_velocity
        
    def get_goal_velocity(self):
        return self.units.convert(self.goal_velocity, self._internal_rotational_velocity)
        
    def set_goal_current(self, value):
        self.goal_current = convert_units(value, self.units.CURRENT, self._internal_current)
        if self.mode is Mode.CURRENT and self.enable and abs(self.goal_current) < self.current_limit:
            self.current = self.goal_current
        
    def get_goal_current(self):
        return self.units.convert(self.goal_current, self._internal_current)
        
    def set_goal_position(self, value):
        self.goal_position = convert_units(value, self.units.REVOLUTION, self._internal_rotational)
        if self.mode is Mode.POSITION and self.enable:
            self.current = self.goal_position
        
    def get_goal_position(self):
        return self.units.convert(self.goal_position, self._internal_rotational)
        
    def get_position(self):
        return self.units.convert(self.position, self._internal_rotational)
    
    def get_velocity(self):
        return self.units.convert(self.velocity, self._internal_rotational_velocity)
    
    def get_current(self):
        return self.units.convert(self.current, self._internal_rotational)
    
if __name__ == "__main__":
    vm = VirtualMotor(name = "VIRTUAL_MOTOR_1")
    vm.set_goal_velocity(math.tau)
    print("Commanded ", vm.get_goal_velocity(), "   Doing", vm.get_velocity())
    vm.set_mode(Mode.VELOCITY)
    print("Mode      ", vm.get_mode().name)
    print("Enable    ", vm.get_enable())
    vm.on()
    vm.set_goal_velocity(10)
    print("Commanded ", vm.get_goal_velocity(), "   Doing", vm.get_velocity())
    
    