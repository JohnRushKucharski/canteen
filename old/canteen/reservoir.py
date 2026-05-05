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

@dataclass(kw_only=True)
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
        sorter: None|Callable[[list[Outlet]|tuple[Outlet,...]], tuple[Outlet,...]] = sort_by_location #pylint: disable=line-too-long
        ) -> 'ReservoirWithOutlets':
        '''
        Adds outlets to the reservoir, sorts them if sorter is provided.
        '''
        if sorter:
            outlets_formatted = sorter(format_outlets(outlets))
        else:
            outlets_formatted = format_outlets(outlets)
        return ReservoirWithOutlets(
            name=self.name, storage=self.storage,
            capacity=self.capacity, operations=self.operations,
            outlets=outlets_formatted
        )

    def operate(self, *args, **kwargs) -> Any:
        '''Perform reservoir operations.'''
        if not self.operations:
            raise ValueError('No operations defined for reservoir.')
        return self.operations.operate(self, *args, **kwargs)

@dataclass(kw_only=True)
class ReservoirWithOutlets(BasicReservoir):
    '''Reservoir with outlets.'''
    outlets: tuple[Outlet, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.outlets:
            self.outlets = format_outlets(list(self.outlets))

    def __repr__(self) -> str:
        '''String representation of the BasicReservoir.'''
        return f'''Reservoir(
            name={self.name}, storage={self.storage}, capacity={self.capacity},
            operations={self.operations}, outlets={(o.name for o in self.outlets)})'''

def load_reservoir_module(module_name: str) -> None:
    '''Discover and load single reservoir module by name.'''
    load_module(module_name, Tags.RESERVOIRS)

def load_reservoir_modules() -> None:
    '''Discover and load all reservoir modules.'''
    load_modules(Tags.RESERVOIRS)

def factory(name: str, **kwargs) -> Reservoir:
    '''Create an reservoir object.'''
    return load_plugin(name, Tags.RESERVOIRS)(**kwargs)
