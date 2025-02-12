'''
Reservoir objects.
'''
from dataclasses import dataclass, field
from typing import Protocol, Callable, Self, Any

#from canteen.operations import Operations
from canteen.outlet import Outlet, format_outlets, sort_by_location
from canteen.plugins import Tags, PLUGINS, load_module, load_modules, load_plugin

type Operations = Callable[['Reservoir', Any], Any]
'''
Provides interface for operation functions that can be dynamically installed as plugins.
'''

def load_operations_module(module_name: str) -> None:
    '''Discover and load single operations module by name.'''
    load_module(module_name, Tags.OPERATIONS)

def load_operations_modules() -> None:
    '''Discover and load all operations modules.'''
    load_modules(Tags.OPERATIONS)

@dataclass
class Reservoir(Protocol):
    '''Provides interface for reservoir objects that can be dynamically installed as plugins.'''	
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

def load_basic_ops(basic_module: str = 'passive',
                   basic_ops: str = 'passive') -> Operations:
    '''Load basic operations module.'''
    load_operations_module(basic_module)
    return PLUGINS[Tags.OPERATIONS][basic_ops]

@dataclass
class BasicReservoir:
    '''Basic Reservoir implementing Reservoir Interface.'''
    name: str = ''
    storage: float = 0.0
    capacity: float = 1.0
    operations: None|Operations = None

    def __post_init__(self) -> None:
        if not self.operations:
            self.operation = load_basic_ops()

    def add_outlets(
        self, outlets: tuple[Outlet],
        sorter: None|Callable[[list[Outlet]], list[Outlet]] = sort_by_location) -> Reservoir:
        '''
        Makes a deep copy of the existing reservoir, returning one the outlets attribute.
        '''
        outlets = sorter(format_outlets(outlets)) if sorter else format_outlets(outlets)
        return ReservoirWithOutlets(self.name, self.storage, self.capacity, self.operations,
                                    outlets)

    def operate(self, *args, **kwargs) -> Any:
        '''Perform reservoir operations.'''
        return self.operations(self, *args, **kwargs)

@dataclass
class ReservoirWithOutlets(BasicReservoir):
    '''Reservoir with outlets.'''
    outlets: list[Outlet] = field(default_factory=list)

def load_reservoir_module(module_name: str) -> None:
    '''Discover and load single reservoir module by name.'''
    load_module(module_name, Tags.RESERVOIRS)

def load_reservoir_modules() -> None:
    '''Discover and load all reservoir modules.'''
    load_modules(Tags.RESERVOIRS)

def factory(name: str, **kwargs) -> Reservoir:
    '''Create an reservoir object.'''
    return load_plugin(name, Tags.RESERVOIRS)(**kwargs)
