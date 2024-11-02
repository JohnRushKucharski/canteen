'''
Basic plugin for reservoir operations.

It provides implementation of the Operations interface.
    Note: this interface is defined by the Operations type interface in canteen.reservoir.
        
Plugins must contain an initialize() method, that returns a dictionary
containing the Operations implementation(s), with string name keys for each implementation.
        i.e. {'passive': PassiveManagement }  

These principals are demonstrated below.
'''
from canteen.reservoir import Reservoir, Operations

def passive(reservoir: Reservoir, inflow: float) -> float:
    '''
    Simpliest possible operations, i.e.:

        release = reservoir.storage + inflow - reservoir.capacity 
                    if (reservoir.storage + inflow) > reservoir.capacity
                  0 otherwise

    Updates reservoir storage in place, and returns the spilled release 
    
    Implements the Operations interface.
    '''
    release = max(0, reservoir.storage + inflow - reservoir.capacity)
    reservoir.storage += inflow - release
    return release

def passive_outlets(reservoir: Reservoir, inflow: float,
                   *args, **kwargs) -> tuple[float,...]:
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
        release = outlet.operations(args, kwargs).max
        output.append(release)
        volume -= release
    spill = max(0, volume - reservoir.capacity)
    reservoir.storage = volume
    return tuple([spill] + [output])

def initialize() -> dict[str, Operations]:
    '''
    Returns dictionary of operations implementations.
    '''
    return {'passive': passive, 'passive_outlets': passive_outlets}
