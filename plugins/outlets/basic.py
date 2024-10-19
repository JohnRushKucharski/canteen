'''Basic outlet, plugin implementation.'''	
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

def initialize() -> tuple[str, BasicOutlet]:
    '''Initialize the plugin.'''
    return 'BasicOutlet', BasicOutlet
