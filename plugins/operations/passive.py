'''
Basic plugin for reservoir operations.

It serves 2 purposes:
    1. Provides implementation of the Operations interface.
        Note: this interface is defined by the Operations protocol in canteen.reervoir

Reservoir plugs must either:
    1. Define one or more implementations of the Reservoir interface.
    
        i.e. BasicReservoir below
        
    2. Define one or more implementations of the Operations interface.
        
        i.e. PassiveManagement below.
        
    3. Both 1, and 2 above.
    
Reservoir plugins must also contain an initialize() method, that returns 2 dictionaries:
    1. The reservoir implementations, with string name keys for each implementation.
    
        i.e. {'Basic': BasicReservoir}
        
    2. The operations implementations, with string name keys for each implementation.
    
        i.e. {'passive': PassiveManagement }  

The two dictionaries returned by the initialize method are packaged into a tuple,
    i.e. 
        def initialize() -> tuple[dict[str, Reservoir], dict[str, Callable[..., Any]]]:
            ...
            return {'Basic': Reservoir}, {'passive': PassiveManagement}

These principals are demonstrated below.
'''
from canteen.reservoir import Reservoir

class Passive:
    '''
    Simpliest possible operations, i.e.:
    
        release = reservoir.storage + inflow - reservoir.capacity 
                    if (reservoir.storage + inflow) > reservoir.capacity
                  0 otherwise
    '''
    def operate(self, reservoir: Reservoir, inflow: float) -> float:
        '''
        Updates reservoir storage in place, and returns the spilled release 
            if storage + inflow exceeds capacity,
            0.0 (no water is released) otherwise.
        '''
        release = max(0, reservoir.storage + inflow - reservoir.capacity)
        reservoir.storage += inflow - release
        return release

    def outputs(self, reservoir: Reservoir) -> tuple[str]: #pylint: disable=unused-argument
        '''Names output from operations function.'''
        return ('spill',)

class PassiveOutlets:
    '''
    Similiar to passive operations above but for reservoir with outlets,
    reservoir storage is modified in place and maximum release is made from
    each of the available outlets, based on their location in the reservoir.
    '''
    def operations(self, reservoir: Reservoir, inflow: float,
                   *args, **kwargs) -> tuple[float,...]:
        '''
        Makes releases from reservoir first by maximizing release from
        list of outlets based on location in reservoir, and spilling any
        remaining volume above the reservoir capacity. Reservoir storage
        is updated in place and releases are returns as a tuple in top to
        bottom order w.r.t their location in the reservoir.
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

    def outputs(self, reservoir: Reservoir) -> tuple[str,...]:
        '''
        List of outputs, s.t.
            ('spill', <Outlet.name>, ..., <Outlet.name>)
        
        where outlet names are in order from top to bottom of reservoir,
        according to their location.
        '''
        return (['spill'] + [o.name for o in reservoir.outlets])
