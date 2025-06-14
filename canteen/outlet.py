'''
Reservoir outlets.
'''
import copy
from collections import Counter
from typing import NamedTuple, Protocol

from canteen.plugin import Tags, load_module, load_modules, load_plugin

ReleaseRange = NamedTuple('ReleaseRange', [('min', float), ('max', float)])

class Outlet(Protocol):
    '''Template for a reservoir outlet.'''
    name: str
    location: float
    design_range: ReleaseRange

    def operations(self, *args, **kwargs) -> ReleaseRange:
        '''
        Return the min and max possible release for an outlet.

        Args:
            state (Any): Reservoir, outlet or other state variables.
        
        Returns:
            ReleaseRange (tuple[min: float, max: float]):
            A tuple of the minimum and maximum possible releases.
        '''

def load_outlet_module(module_name: str) -> None:
    '''Discover and load single reservoir module by name.'''
    load_module(module_name, Tags.OUTLETS)

def load_outlet_modules() -> None:
    '''Discover and load all reservoir modules.'''
    load_modules(Tags.OUTLETS)

def factory(name: str, **kwargs) -> Outlet:
    '''Create an reservoir object.'''
    return load_plugin(name, Tags.OUTLETS)(**kwargs)

def sort_by_location(outlets: list[Outlet]|tuple[Outlet,...]) -> tuple[Outlet,...]:
    '''Sort outlets by location, name.'''
    class Reverse:
        '''Reverse comparison for sorting by location.'''
        def __init__(self, value):
            self.value = value
        def __lt__(self, other):
            return self.value > other.value
    return tuple(sorted(outlets, key=lambda o: (Reverse(o.location), o.name)))

def format_outlets(outlets: list[Outlet]) -> tuple[Outlet,...]:
    '''
    Makes deep copy of outlets, modifies the names to be unique, s.t.:
        outlet.name is set to = 'outlet' if it is empty, then
        new_name =  <outlet.name>@<outlet.location>, if unique
                    <outlet.name><duplicate_number>@<outlet.location> otherwise    
    Returns a tuple of outlets.
    '''
    def preprocess(outlets: list[Outlet]) -> list[Outlet]:
        '''
        Makes deep copy of input outlets, sets empty names to 'outlet',
        '''
        outlets = copy.deepcopy(outlets)
        for outlet in outlets:
            if not outlet.name:
                outlet.name = 'outlet'
            else:
                split_name = outlet.name.split('@')
                if len(split_name) > 2:
                    raise ValueError(f'Invalid name: {outlet.name}')
                if len(split_name) == 2 and split_name[1] != str(outlet.location):
                    raise ValueError(f'Invalid name: {outlet.name}')
        return outlets

    def find_duplicates(name: str, count: int, outlets: list[Outlet]) -> list[Outlet]:
        '''
        Finds list <count> of outlets with specified <name>.
        '''
        duplicates = []
        for outlet in outlets:
            if outlet.name == name:
                duplicates.append(outlet)
        if len(duplicates) != count:
            raise ValueError(f'Found {len(duplicates)} {name} names, expected {count}.')
        return duplicates

    def rename_duplicates(duplicates: list[Outlet], is_first_pass: bool) -> list[Outlet]:
        '''
        Renames the outlets in <duplicates> list, s.t.:
            new_name =  <outlet.name>@<outlet.location>, if unique
                        <outlet.name><duplicate_number>@<outlet.location> otherwise
        '''
        for i, outlet in enumerate(duplicates):
            if is_first_pass:
                if isinstance(outlet.location, int):
                    location = str(outlet.location)
                elif isinstance(outlet.location, float):
                    location = f'{round(outlet.location, 1)}'
                else:
                    raise ValueError(f'Invalid location type: {type(outlet.location)}')
                outlet.name = f'{outlet.name}@{location}'
            else:
                pre_name = outlet.name[:outlet.name.index('@')]
                location = outlet.name[outlet.name.index('@'):]
                outlet.name = f'{pre_name}{i+1}{location}'
        return duplicates

    outlets = preprocess(outlets)
    name_counter = Counter([o.name for o in outlets])
    # fist pass add location to name.
    for k, n in name_counter.items():
        if n > 1: # k is duplicated.
            duplicates = rename_duplicates(find_duplicates(k, n, outlets), True)
            name_recounter = Counter([o.name for o in duplicates])

            # second pass add index to name.
            for k, n in name_recounter.items():
                if n > 1:
                    rename_duplicates(find_duplicates(k, n, duplicates), False)

    # check for unique names.
    if len({o.name for o in outlets}) != len(outlets):
        raise ValueError(f'Failed to create unique names: {[o.name for o in outlets]}.')
    return tuple(outlets)
