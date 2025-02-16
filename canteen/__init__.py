'''
Initializes plugins
'''
from enum import Enum
from pathlib import Path
from importlib import import_module
#from canteen.plugins import Tags, load_modules

class Tags(Enum):
    '''Supported Plugin Types.'''
    OPERATIONS = 'operations'
    OUTLETS = 'outlets'
    RESERVOIRS = 'reservoirs'

BASEPATH = Path(Path(__file__).parent.parent/'plugins')

PATHS = {
    Tags.OPERATIONS: list(
        Path(BASEPATH/f'{Tags.OPERATIONS.value}').glob('*.py')),
    Tags.OUTLETS: list(
        Path(BASEPATH/f'{Tags.OUTLETS.value}').glob('*.py')),
    Tags.RESERVOIRS: list(
        Path(BASEPATH/f'{Tags.RESERVOIRS.value}').glob('*.py'))
}

PLUGINS = {
    Tags.OPERATIONS: {},
    Tags.OUTLETS: {},
    Tags.RESERVOIRS: {},
}


def load_module(name: str, tag: Tags) -> None:
    '''
    Discover and load single plugin by name. 
    '''
    for file in PATHS[tag]:
        if file.stem == name:
            load_plugins(name, tag)
            return
    raise ValueError(
        f'''Plugin module with name: {name} not found
        in {PATHS[tag]}.''')

def load_modules(tag: Tags) -> None:
    '''
    Discover and load all plugins in path.
    '''
    for file in PATHS[tag]:
        load_plugins(file.stem, tag)

def load_plugins(module_name: str, tag: Tags) -> None:
    '''
    Load all plugins in named module.    
    '''
    module_locations = {
        Tags.OPERATIONS: 'plugins.operations.',
        Tags.OUTLETS: 'plugins.outlets.',
        Tags.RESERVOIRS: 'plugins.reservoirs.'
    }
    module = import_module(f'{module_locations[tag]}{module_name}', '.')
    found_plugins = module.initialize()
    for k, v in found_plugins.items():
        if k in PLUGINS[tag] and not isinstance(v, type(PLUGINS[tag][k])):
            raise ValueError(
                f'''Error: Plugin name: {k} is duplicated.
                The same name is given to {PLUGINS[tag][k]} plugin. {v}
                cannot be added without overwriting {PLUGINS[tag][k]}.''')
        PLUGINS[tag][k] = v

def load_plugin(plugin_name: str, tag: Tags) -> type:
    '''Searches for a specific plugin by name.'''
    module_locations = {
        Tags.OPERATIONS: 'plugins.operations.',
        Tags.OUTLETS: 'plugins.outlets',
        Tags.RESERVOIRS: 'plugins.reservoirs'
    }
    if plugin_name in PLUGINS[tag]:
        return PLUGINS[tag][plugin_name]
    for file in PATHS[tag]:
        module = import_module(f'{module_locations[tag]}{file.stem}', '.')
        plugins = module.initialize()
        for k, v in plugins.items():
            if k == plugin_name:
                return v
    raise ValueError(
        f'''Plugin with name: {plugin_name} not found
        in discovered modules: {PATHS[tag]}.''')

def initialize():
    '''Initialize plugins.'''
    for tag in Tags:
        load_modules(tag)

initialize()
print(PLUGINS)
