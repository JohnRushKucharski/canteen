'''
Reservoir objects.
'''
import importlib
from pathlib import Path
from typing import Protocol, Any

class Reservoir(Protocol):
    '''Reservoir object.'''	
    name: str
    storage: float
    capacity: float

    def operate(self, *args, **kwargs) -> Any:
        '''Operate the reservoir.'''

    def outputs(self) -> tuple[str,...]:
        '''Return the reservoir operate outputs.'''

RESERVOIRS = {}
OPERATIONS = {}
PLUGIN_PATHS = list(Path(Path(__file__).parent.parent/'plugins'/'reservoir').glob('*.py'))

def load_reservoir_plugins() -> None:
    '''Load reservoir plugins.'''
    for file in PLUGIN_PATHS:
        module = importlib.import_module(f'plugins.reservoirs.{file.stem}', ".")
        reservoirs, operations = module.initialize()
        for k, v in reservoirs:
            RESERVOIRS[k] = v
        for k, v in operations:
            OPERATIONS[k] = v

def reservoir_factory(name: str, **kwargs) -> Reservoir:
    '''Create an reservoir object.'''
    if name not in RESERVOIRS:
        raise ValueError(f'Reservoir plugin {name} not found.')
    return RESERVOIRS[name](**kwargs)
