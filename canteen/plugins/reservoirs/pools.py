'''
Basic plugin for reservoirs.

It serves 2 purposes:
    1. Provides implementation of the Reservoir interface.
    2. Is an example for the development of other reservoir plugins.

Reservoir plugs must define one or more implementations of the Reservoir interface.
    
        i.e. ReservoirWithPools below
    
Reservoir plugins must also contain an initialize() method, 
that returns a dictionary with string name keys for each implementation.
    
        i.e. {'Pools': ReservoirWithPools} 

The dictionary returned by the initialize method,
    i.e. 
        def initialize() -> dict[str, Reservoir]:
            ...
            return {'Pools': ReservoirWithPools}

These principals are demonstrated below.
'''
from dataclasses import dataclass, field

from canteen.reservoir import Reservoir, BasicReservoir

@dataclass
class Pools:
    ''''
    Implementation of pool concept. 
    
    Default values for demonstratio purposes only.
    '''
    names: list[str] = field(default_factory=lambda:
        ['dead', 'conservation', 'flood', 'surcharge', 'spill'])
    top_locations: list[float] = field(default_factory=lambda:
        [0.2, 0.5, 0.75, 0.9, 1.1]) # purely for demonstration purposes.

    def __post_init__(self):
        if len(self.names) != len(self.top_locations):
            raise ValueError(
                f'''Error: each named pool must be given a location,
                {len(self.names)} pools named, {len(self.top_locations)} locations given.'''
            )
        self.__i = -1
        self.count = len(self.names)

    def __iter__(self):
        return self
    def __next__(self):
        self.__i += 1
        if self.__i < self.count:
            return self.names[self.__i], self.top_locations[self.__i]
        self.__i = -1
        raise StopIteration

@dataclass(kw_only=True)
class ReservoirWithPools(BasicReservoir):
    '''
    Extends the basic reservoir object by adding pools.
    '''
    pools: Pools

    def __post_init__(self):
        for i, (_, v) in enumerate(self.pools):
            if self.capacity < v and i < self.pools.count - 1:
                raise ValueError(
                    f'''Bottom of {self.pools.names[i+1]} pool,
                    at {v} not in reservoir with capacity of {self.capacity}.''')

    def active_pool(self, volume: float) -> tuple[str, float]:
        '''
        Returns: tuple[str, float]
            str: the name of the active pool for a given the reservoir volume.
            float: the volume in the active pool.
        
        Note: If the volume is above all named pools, then:
            str: '' is returned for the first tuple item.
            float: volume above top of last pool is returned for second tuple item.
        '''
        for i, (k, v) in enumerate(self.pools):
            if volume <= v:
                #bottom pool
                if i == 0:
                    return k, volume
                return k, volume - self.pools.top_locations[i-1]
        return ''

def initialize() -> dict[str, Reservoir]:
    '''
    Required plugin method to initialize the plugin.
    
    Returns: dict[str, Reservoir]
        Keys for each dictionary are string names for the implementation values.
    '''
    return {'Pools': ReservoirWithPools}
