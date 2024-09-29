'''
Reservoir objects.
'''
import math
from enum import Enum
from typing import NamedTuple, Protocol, Callable

ReleaseRange = NamedTuple('ReleaseRange', [('min', float), ('max', float)])

class Outlet(Protocol):
    '''Template for a reservoir outlet.'''
    name: str
    location: float
    design_range = ReleaseRange

    def operations(self, fill_state: float) -> ReleaseRange:
        '''
        Return the min and max possible release for a given reservoir state and outlet condition.

        Args:
            state: the current reservoir fill state as a storage volume, stage, or other measure.
        
        Returns:
            ReleaseRange (tuple[min: float, max: float]):
            A tuple of the minimum and maximum possible releases.
        '''

def basic_operations(outlet: Outlet, fill_state: float) -> ReleaseRange:
    '''
    Return the min and max possible release based on
    reservoir fill state (volume, stage, etc.) and outlet constraints.
    '''
    over_gate = fill_state - outlet.location
    if over_gate <= 0:
        return ReleaseRange(0, 0)
    # resvoir filled over outlet location.
    return ReleaseRange(
        min=min(outlet.design_range.min, over_gate),
        max=min(over_gate, outlet.design_range.max))

type OutletOperations = Callable[[Outlet, float], ReleaseRange]

class BasicOutlet(Outlet):
    '''Basic outlet implementation.'''
    def __init__(self, name: str = '', location: float = 0.0,
                 design_range: ReleaseRange = ReleaseRange(0, math.inf),
                 operation: OutletOperations = basic_operations) -> None:
        self.name = name
        self.location = location
        self.design_range = design_range
        self.__outlet_operation = operation

    def operations(self, fill_state: float) -> ReleaseRange:
        return self.__outlet_operation(self, fill_state)

class OutletFailureState(Enum):
    '''Failure states for outlet.'''
    NORMAL = 0
    FAILED_OPEN = 1
    FAILED_CLOSED = 2
