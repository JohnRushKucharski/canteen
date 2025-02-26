'''
Basic outlet plugin.

It serves 2 purposes:
    1. Provides implementation of the Outlet interface.
    2. Is an example for the development of other outlet plugins.

Outlet plugins must define one or more implementations of the Outlet interface.
        i.e. BasicOutlet below
    
All plugins must also contain an initialize() method. The Outlet plugin returns a dictionary
containing one or more Outlet implementations, with string name keys for each implementation.
        i.e. {'Basic': BasicOutlet}

These principals are demonstrated below.
'''
import math
from typing import NamedTuple
from dataclasses import dataclass

ReleaseRange = NamedTuple('ReleaseRange', [('min', float), ('max', float)])

@dataclass
class BasicOutlet:
    '''Outlet implementation.'''
    name: str  = ''
    location: float = 0.0
    design_range: ReleaseRange = ReleaseRange(0, math.inf)

    def operations(self, fill_state: float) -> ReleaseRange:
        '''
        Return the min and max possible release based on
        reservoir fill state (volume, stage, etc.) and outlet constraints.
        '''
        over_gate = fill_state - self.location
        if over_gate <= 0:
            return ReleaseRange(0, 0)
        # reservoir filled over outlet location.
        return ReleaseRange(
            min=min(self.design_range.min, over_gate),
            max=min(over_gate, self.design_range.max))

def initialize() -> dict[str, BasicOutlet]:
    '''Initialize the plugin.'''
    return {'Basic': BasicOutlet}
