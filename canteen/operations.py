'''
Provide interface for operation functions that can be dynamically installed as plugins.
'''
from typing import Protocol, Any

class Operations(Protocol):
    '''
    Interface for reservoir operations.
    '''
    def operations(self, reservoir: 'Reservoir', *args, **kwargs) -> Any: #pylance: disable=reportUndefinedVariable
        '''Reservoir operations function.'''
    def outputs(self) -> tuple[str,...]:
        '''Describes output of operations function.'''
