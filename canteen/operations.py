'''
Operations Interface
'''
from typing import Protocol, Any
#from canteen.reservoir import Reservoir # causes circular import
from canteen.plugin import load_module, load_modules, Tags, PLUGINS

class Operations(Protocol):
    '''Provides interface for operation functions that can be dynamically installed as plugins.'''
    def operate(self, *args, **kwargs) -> Any:
        '''Calls operations to perform reservoir operations.'''
    def output_labels(self) -> tuple[str,...]:
        '''Returns labels for operation outputs.'''

def load_operations_module(module_name: str) -> None:
    '''Discover and load single operations module by name.'''
    load_module(module_name, Tags.OPERATIONS)

def load_operations_modules() -> None:
    '''Discover and load all operations modules.'''
    load_modules(Tags.OPERATIONS)

class Passive:
    '''
    Passive operations implements Operations interface.
    '''
    def operate(self, reservoir: 'Reservoir', inflow: float) -> float: #type: ignore #noqa: F821
        '''
        Simplest possible operations, i.e.:

            release = reservoir.storage + inflow - reservoir.capacity 
                        if (reservoir.storage + inflow) > reservoir.capacity
                    0 otherwise

        Updates reservoir storage in place, and returns the spilled release 
        
        Implements the Operations interface.
        '''
        release = max(0, reservoir.storage + inflow - reservoir.capacity)
        reservoir.storage += inflow - release
        return release

    def output_labels(self) -> tuple[str,...]:
        '''Returns labels for operation outputs.'''
        return ('Spill',)

    def __repr__(self) -> str:
        '''String representation of the Passive operations.'''
        return 'Passive: Reservoir spills if capacity is exceeded.'

def load_basic_ops(basic_module: str = 'passive_outlets',
                   basic_ops: str = 'PassiveOutlets') -> Operations:
    '''Load basic operations module.'''
    load_operations_module(basic_module)
    return PLUGINS[Tags.OPERATIONS][basic_ops]()
