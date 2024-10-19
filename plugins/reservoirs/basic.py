'''
Basic plugin for reservoirs.
'''
from typing import Callable

from canteen.reservoir import Reservoir
from canteen.outlet import Outlet, format_outlets

def passive_management(reservoir: Reservoir) -> Callable[[float], tuple[float,...]]:  # pylint: disable=line-too-long
    '''
    Updates storage in place and returns reservoir releases under passive operations,
    i.e., each reservoir outlet releases what it can, based on its location and the storage.
    
    Args:
        reservoir (Reservoir): The reservoir to operate.
        
    Returns:
        Callable[[float], tuple[float,...]]: 
            A function that returns storage and releases from a reservoir given inflow and storage.
    
    Note:
        Modifies the reservoir storage in place.
    '''
    def operate(inflow: float) -> tuple[float,...]:
        '''Modifies storage in place and returns releases from the reservoir.

        Args:
            inflow_volume (float): Inflow of water to manage at beginning of timestep.

        Returns:
            tuple[float,...]: Outflow, and spill volumes in sorted order of the outlets.
        '''
        output: list[float] = []
        volume = reservoir.storage + inflow
        for outlet in reservoir.outlets:
            # Each outlet releases what it can,
            # based on its location and the storage.
            release = outlet.release_range(volume).max
            output.append(release)
            volume -= release
        # Spill can be modeled as an outlet,
        # with a location at the reservoir capacity.
        # Then, hitting this line would be an error.
        spill = max(0.0, volume - reservoir.capacity)
        reservoir.storage = min(volume, reservoir.capacity)
        output.append(spill)
        return tuple(output)
    return operate

class BasicReservoir(Reservoir):
    '''Basic reservoir.'''
    def __init__(self, **kwargs):
        '''
        Keyword Args:
            name (str): Default is ''.
            storage (float): Initial reservoir storage. Default is 0.
            capacity (float): The capacity of the reservoir. Default is 1.
            operations (Callable[[float], tuple[float,...]]): The operations function.
                Default is passive_management.
            outputs (tuple[str,...]): Reservoir operations output.
        '''
        self.name = kwargs.get('name', '')
        self.storage = kwargs.get('storage', 0)
        self.capacity = kwargs.get('capacity', 1)
        self.outlets = kwargs.get(
            'outlets', format_outlets([Outlet(location=self.capacity)]))
        self.__operation_fx = kwargs.get(
            'operations', passive_management(self))
        self.__outputs = kwargs.get(
            'outputs', tuple([o.name for o in self.outlets] + ['spill']))

    def operate(self, *args, **kwargs):
        '''Operate the reservoir.'''
        return self.__operation_fx(*args, **kwargs)

    def outputs(self):
        '''Return the reservoir outputs.'''
        return self.__outputs

def initialize() -> tuple[str, type]:
    '''Initialize the plugin'''
    return ('Basic', BasicReservoir), ('passive', passive_management)
