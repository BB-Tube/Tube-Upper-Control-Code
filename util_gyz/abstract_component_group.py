from abc import ABC
from .abstract_component import ComponentInterface
from .units import *

class ComponentGroup(ComponentInterface, ABC):
    """
    Represents a group of components or Component groups, allowing for nested structures.
    Implements the ComponentInterface to ensure that Component groups can be controlled
    just like individual components.
    """
    def __init__(self, name, components=None, units = Units()):
        """
        Initializes a ComponentGroup with a list of components or other ComponentGroups.
        
        Parameters:
        - components (list of ComponentInterface): A list of objects implementing the
          ComponentInterface. Defaults to an empty list if not provided.
        """
        super().__init__(name=name, units=units)
        self._components = components if components is not None else []

    def set_units(self, units = Units()):
        """
        Sets the units for all contained components or Component groups
        by iterating over them and calling their set_units method with the given units.
        """
        for component in self._components:
            component.set_units(units)

    def add_component(self, comp: ComponentInterface):
        """
        Adds a new component or ComponentGroup to the existing list of components.
        
        This method allows for dynamic expansion of the component group by adding
        individual components or other component groups, enabling the flexible
        composition of component hierarchies or networks. This is particularly
        useful for creating complex control systems where components need to be
        grouped or managed in a modular fashion.

        Parameters:
        - comp (ComponentInterface): The component or ComponentGroup to be added to the
          group. Must implement the ComponentInterface to ensure compatibility with
          the group's operations.
        """
        self._components.append(comp)

    @property
    def components(self):
        """
        Provides access to the list of contained components or Component groups.
        """
        return self._components.copy()
        
    @components.setter
    def components(self, value):
        """
        Allows replacing the list of components or Component groups with a new one.
        """
        self._components = value

        """
        Allows replacing the list of actuators or Actuator groups with a new one.
        """
        self._actuators = value