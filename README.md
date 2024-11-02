# Canteen

The canteen Python package is used to model reservoirs and reservoir operations in water resource systems.

### Installation

The canteen package Python dependencies are managed using Poetry. Installing poetry makes installing canteen and its dependencies straightforward. If you haven't already first install Python. To install Poetry follow the instructions here: https://python-poetry.org/docs/#installing-with-the-official-installer. Clone or fork the respository located on Github: https://github.com/JohnRushKucharski/canteen. Using your favorite command-line shell run:

```
poetry install
```

### Design

canteen is designed to be as flexible a possible. It facilitates both simple and detailed representations of reservoirs and operational policies. For example, individual outlet (i.e., gate) level controls bound to reservoir pool-based operations (not unlike HEC-ResSim [https://www.hec.usace.army.mil/software/hec-ressim/]) can be modeled; or reservoirs can be modeled more simply (i.e., without outlets and pools). This flexibility is achieved in part though a plugin-based architecture. Major package elements, i.e., Operations, Outlets, and Reservoirs can be extended as though the use of customized plugins.

The following basic interfaces are at the core of the canteen package:

### Reservoir

Implementations of the reservoir interface, track the storage of water though the 'storage' state variable.

```python
class Reservoir(Protocol):
    '''Interface for reservoir object.'''	
    name: str
    storage: float
    capacity: float
    operations: Operations

    def add_outlets(self, outlets: list[Outlet],
                    sorter: None|Callable[[list[Outlet]], list[Outlet]]) -> Self:
        '''
        Makes a deep copy of the Reservoir adds outlets attribute
        and returns new Reservoir object.
        '''

    def operate(self, *args, **kwargs) -> Any:
        '''Calls operations to perform reservoir operations.'''
```

Optional elements like outlets can attached as dynamic attributes [using for example, the Reservoir.add_outlets() method].

The Outlet interface is shown below...

```python
class Outlet(Protocol):
    '''Template for a reservoir outlet.'''
    name: str
    location: float
    design_range = ReleaseRange

    def operations(self, *args, **kwargs) -> ReleaseRange:
        '''
        Return the min and max possible release for an outlet.

        Args:
            state (Any): Reservoir, outlet or other state variables.
        
        Returns:
            ReleaseRange (tuple[min: float, max: float]):
            A tuple of the minimum and maximum possible releases.
        '''
```

Plugins implementing the Reservoir interface can extend the basic functionality of the interface. Python modules (i.e. *.py files) containing Reservoir plugins placed in the plugins.reservoirs namespace can by dynamically loaded by canteen programs. 

For example, the plugins.reservoirs.pools module contains the following ReservoirWithPools plugin, which implements the Reservoir interface:

```python
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
                return k, volume - self.pools[i-1].v
        return ''
```

This extends the BasicReservoir implementation, displayed below...

```python
@dataclass
class BasicReservoir:
    '''Basic Reservoir implementing Reservoir Interface.'''
    name: str = ''
    storage: float = 0.0
    capacity: float = 1.0
    operations: Operations = load_basic_ops()

    def add_outlets(
        self, outlets: tuple[Outlet],
        sorter: None|Callable[[list[Outlet]], list[Outlet]] = sort_by_location) -> Reservoir:
        '''
        Makes a deep copy of the existing reservoir, returning one the outlets attribute.
        '''
        reservoir = copy.deepcopy(Reservoir)
        reservoir.outlets = sorter(format_outlets(outlets)) if sorter else format_outlets(outlets)
        return reservoir
    
    def operate(self, *args, **kwargs) -> Any:
        '''Perform reservoir operations.'''
        return self.operations(self, *args, **kwargs)
```

This adds the pools atttribute, which are also defined in the pools module ...

```python
class Pools:
    ''''
    Implementation of pool concept. 
    
    Default values for demonstratio purposes only.
    '''
    names: list[str] = field(default_factory=lambda:
        ['dead', 'conservation', 'flood', 'surcharge', 'spill'])
    top_locations: list[float] = field(default_factory=lambda:
        # values for demonstration purposes.
        [0.2, 0.5, 0.75, 0.9, 1.1]) 

    def __post_init__(self):
        if len(self.names) != len(self.top_locations):
            raise ValueError(
                f'''Error: each named pool must be given a location,
                {len(self.names)} pools named, {len(self.top_locations)} locations given.'''
            )
        self.__i = -1
        self.count = len(self.names)

    # implements the iterator interface.
    def __iter__(self):
        return self

    def __next__(self):
        self.__i += 1
        if self.__i < self.count:
            return self.names[self.__i], self.top_locations[self.__i]
        self.__i = -1
        raise StopIteration
```

### Operations

Reservoir operations are attached as a seperate plugins. The Operations interface is a simple python function, the signature is defined in the canteen.reservoir module.

```python
type Operations = Callable[['Reservoir', Any], Any]
```

At this point, it becomes clear that flexibility and dynamism is given precedent over type safety, etc. (i.e. liberal use the of Any type safe escape hatch).

The PoolBasedOperations plugin located in the plugins.operations.pools module crudely demonstrates how the Operations interface might be fullfilled for a ReservoirWithPools instantiation of the Reservoir interface (from above).

```python
def pool_based_operations(reservoir: ReservoirWithPools,
                          inflow: float, demand: float) -> tuple[float,...]:
    '''
    Only meant as an example for plugin development.
    
    Provides a simple example for pool based rules.

    Uses ReservoirWithPools plugin in plugins/reservoirs/pools.py module

    In deadpool not releases are made.
    In conservation pool, standard operating proceedures for given demand.
    In flood pool, empty pool given constrained maximum release.
    In surcharge space unlimited release to top of flood pool.
    In spill same as surcharge space.
    '''
    # needed for surcharge and flood ops.
    max_flood_release = 0.1
    # needed for surcharge and spill ops
    flood_pool_volume = reservoir.pools.top_locations[2] - reservoir.pools.top_locations[1]

    volume = reservoir.storage + inflow
    releases = [0 for _ in reservoir.pools]
    pool_name, pool_vol = reservoir.active_pool(volume)
    match pool_name:
        case 'dead':
            return tuple(releases)
        case 'conservation':
            releases[1] = min(demand, pool_vol)
        case 'flood':
            releases[2] = min(pool_vol, max_flood_release)
        case 'surcharge':
            releases[2] = min(flood_pool_volume, max_flood_release)
            releases[3] = pool_vol
        case 'spill':
            releases[2] = min(flood_pool_volume, max_flood_release)
            releases[3] = reservoir.pools.top_locations[3] - reservoir.pools.top_locations[2]
            releases[4] = pool_vol
        case _:
            raise ValueError('Unexpected pool name: {pool_name}')
    return releases
```
For new plugin modules to be registered the module must: 

1. Location: be placed in the appropriate plugins folder, namely the: "canteen\plugins\operations", "canteen\plugins\outlets", or "canteen\plugins\reservoirs" directories. Examples are provided in each of these directories.

2. Intialize Function: each plugin (i.e. implementation of the relevant interface) must contain an initialize() function. For example, the initialize() function from the plugins\outlets\basic.py module is show below. The initailize function must return a dictionary of key-value pairs. The key, are plugin names (strings). The values are the plugin implementations. For example the basic.py module initialize function shown below registers the BasicOutlet plugin.

```python
def initialize() -> dict[str, BasicOutlet]:
    '''Initialize the plugin.'''
    return {'BasicOutlet': BasicOutlet}
```

### Example Usage

