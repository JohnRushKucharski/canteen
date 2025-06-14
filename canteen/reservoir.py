'''
Reservoir objects.
'''
from dataclasses import dataclass, field
from typing import Protocol, Callable, Self, Any

from canteen.operations import Operations, Passive
from canteen.outlet import Outlet, format_outlets, sort_by_location
from canteen.plugin import Tags, load_module, load_modules, load_plugin

# type Operations = Callable[['Reservoir', Any], Any]
# '''
# Provides interface for operation functions that can be dynamically installed as plugins.
# '''

# def load_operations_module(module_name: str) -> None:
#     '''Discover and load single operations module by name.'''
#     load_module(module_name, Tags.OPERATIONS)

# def load_operations_modules() -> None:
#     '''Discover and load all operations modules.'''
#     load_modules(Tags.OPERATIONS)

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

@dataclass
class BasicReservoir:
    '''Basic Reservoir implementing Reservoir Interface.'''
    name: str = ''
    storage: float = 0.0
    capacity: float = 1.0
    operations: None|Operations = None

    def __post_init__(self) -> None:
        if not self.operations:
            self.operations = Passive()

    def add_outlets(
        self, outlets: list[Outlet],
        sorter: None|
        Callable[[list[Outlet]|tuple[Outlet,...]], tuple[Outlet,...]] = sort_by_location
        ) -> Reservoir:
        '''
        Makes a deep copy of the existing reservoir, returning one the outlets attribute.
        '''
        if sorter:
            outlets_formatted = sorter(format_outlets(outlets))
        else:
            outlets_formatted = format_outlets(outlets)
        return ReservoirWithOutlets(self.name, self.storage, self.capacity, self.operations,
                                    outlets_formatted) # type: ignore #noqa: F821

    def operate(self, *args, **kwargs) -> Any:
        '''Perform reservoir operations.'''
        if not self.operations:
            raise ValueError('No operations defined for reservoir.')
        return self.operations.operate(self, *args, **kwargs)

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
