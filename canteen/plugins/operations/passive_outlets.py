'''
Basic plugin for reservoir operations.

It provides implementation of the Operations interface.
    Note: this interface is defined by the Operations type interface in canteen.reservoir.
        
Plugins must contain an initialize() method, that returns a dictionary
containing the Operations implementation(s), with string name keys for each implementation.
        i.e. {'passive': PassiveManagement }  

These principals are demonstrated below.
'''
from canteen.reservoir import Reservoir
from canteen.operations import Operations

class PassiveOutlets:
    '''
    Passive operations with outlets, releases maximum volume from each outlet
    in the reservoir, and spills any remaining volume above the reservoir capacity.
    
    Implements the Operations interface.
    '''
    def operate(self, reservoir: Reservoir, inflow: float) -> tuple[float,...]:
        '''
        Similiar to passive operations above but for reservoir with outlets,
        reservoir storage is modified in place and maximum release is made from
        each of the available outlets, based on their location in the reservoir.
        
        Makes releases from reservoir first by maximizing release from
        list of outlets based on location in reservoir, and spilling any
        remaining volume above the reservoir capacity. Reservoir storage
        is updated in place and releases are returns as a tuple in top to
        bottom order w.r.t their location in the reservoir.
        
        Implements the Operations interface.
        '''
        output = []
        volume = reservoir.storage + inflow
        for outlet in reservoir.outlets:
            release = outlet.operations(fill_state=volume).max
            output.append(release)
            volume -= release
        spill = max(0, volume - reservoir.capacity)
        output.append(spill)
        reservoir.storage = volume
        return tuple(output)
    def output_labels(self, reservoir: 'Reservoir') -> tuple[str,...]:
        '''Returns labels for operation outputs.'''
        return tuple([outlet.name for outlet in reservoir.outlets] + ['Spill'])

def initialize() -> dict[str, Operations]:
    '''
    Returns dictionary of operations implementations.
    '''
    return {'PassiveOutlets': PassiveOutlets}
