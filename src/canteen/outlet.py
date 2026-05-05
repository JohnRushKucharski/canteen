"""
Reservoir outlet components for the Canteen package.

This module provides outlet interfaces and implementations for modeling
reservoir outlet structures with generic numeric types for release ranges.
"""

import copy
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Sequence, Protocol, Callable

from canteen.mapping import Mappings
from canteen.units import Quantity, Category
from canteen.validation import validate_is_not_negative, validate_is_ascending_range

@dataclass(slots=True)
class ReleaseRange:
    """
    min and max release volumes (per timestep).
    """
    min: float|Quantity = 0.0
    max: float|Quantity = math.inf

    def __post_init__(self) -> None:
        validate_is_not_negative(self.min, "ReleaseRange minimum")
        validate_is_ascending_range(self.min, self.max, "ReleaseRange")
        self.check_units()

    def check_units(self) -> None:
        '''Validate that min and max are of the same type (both numeric or both Quantity).'''
        # units package not installed, nothing to check.
        if Quantity is None:
            return
        # both are not quantities, no need to check units.
        if not isinstance(self.min, Quantity) and not isinstance(self.max, Quantity):
            return
        # one is a quantity and the other is not, invalid.
        if not isinstance(self.min, Quantity) or not isinstance(self.max, Quantity):
            raise ValueError(
                f"min: {self.min} and max: {self.max} must be same type (Quantities or numeric)")
        # both are quantities,
        # check if both are volume quantities
        if self.min.unit.category != Category.VOLUME or self.max.unit.category != Category.VOLUME:
            raise ValueError(
                f"min: {self.min.unit.category} and max: {self.max.unit.category} must be volumes.")
        # check if both are same units and value bases.
        if not self.min.is_same_unit_and_value_base(self.max):
            raise ValueError(
                f"min: {self.min} and max: {self.max} must have the same units and value bases")

class Outlet(Protocol):
    """
    Protocol defining the outlet interface with generic release ranges.
    """
    name: str
    location: float|Quantity
    design_range: ReleaseRange
    mappings: None|Mappings = None

    def operations(self, fill_state: float|Quantity) -> ReleaseRange:
        """
        Return the min and max possible release for an outlet.
        
        Parameters
        ----------
        fill_state : float|Quantity
            Reservoir fill state (volume, stage, etc.)
            
        Returns
        -------
        ReleaseRange
            Tuple of (min, max) possible releases in the outlet's numeric type
        """

@dataclass
class BasicOutlet:
    """
    Basic outlet implementation with generic numeric types for release ranges.
    
    Provides a simple outlet model where releases are limited by:
    1. Physical constraints (location and available head)
    2. Design limitations (min/max design range)
    
    The outlet only allows flow when the reservoir fill state exceeds
    the outlet location (elevation/depth).
    """
    name: str = ""
    location: float|Quantity = 0.0
    design_range: ReleaseRange = field(default_factory=lambda: ReleaseRange(0, math.inf))
    mappings: None|Mappings = None

    def __post_init__(self) -> None:
        """Validate outlet parameters after initialization."""
        validate_is_not_negative(self.location, "Outlet location")


    def operations(self, fill_state: float|Quantity) -> ReleaseRange:
        """
        Return the min and max possible release based on reservoir fill state.
        
        The outlet can only release water when the fill state exceeds the
        outlet location. Release is limited by both physical constraints
        (available head) and design constraints (design range).
        
        Parameters
        ----------
        fill_state : float
            Reservoir fill state (volume, stage, elevation, etc.)
            
        Returns
        -------
        ReleaseRange
            Tuple of (min, max) possible releases in the outlet's numeric type
            
        Notes
        -----
        For integer outlets, results are rounded down (floor) to prevent
        fractional flows and ensure conservative release estimates.
        """
        # Calculate available head over the outlet
        over_gate = fill_state - self.location

        if over_gate <= 0:
            # No flow possible if reservoir level is at or below outlet
            return ReleaseRange(0, 0)
        physical_max = over_gate

        # Apply design constraints
        min_release = min(self.design_range.min, physical_max)
        max_release = min(physical_max, self.design_range.max)

        return ReleaseRange(min_release, max_release)

    def __repr__(self) -> str:
        """String representation of the outlet."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"location={self.location}, "
            f"design_range={self.design_range}, "
        )

def factory(
    name: str = "",
    location: float|Quantity = 0.0,
    design_range: ReleaseRange | None = None,
    mappings: None|Mappings = None) -> BasicOutlet:
    """
    Create an outlet with specified parameters.
    
    Parameters
    ----------
    name : str, optional
        Outlet name, by default ""
    location : float|Quantity, optional
        Physical outlet location (elevation, depth, etc.), by default 0.0
    design_range : ReleaseRange | None, optional
        Design min/max release range, by default None (uses 0 to infinity)
        
    Returns
    -------
    BasicOutlet
        Outlet instance for the specified numeric type
        
    Examples
    --------
    >>> outlet = factory()  # Creates outlet
    >>> outlet = factory(int_only=True)  # Creates integer outlet
    >>> outlet = factory(name="Spillway", location=100.0, int_only=True)
    """
    if design_range is None:
        design_range = ReleaseRange(0, math.inf)

    return BasicOutlet(
        name=name,
        location=location,
        design_range=design_range,
        mappings=mappings,
    )

class Outlets:
    """Container for multiple Outlet instances with iteration support."""

    def __init__(self, outlets: list[Outlet]|tuple[Outlet,...],
                 sorter: None|Callable[[list[Outlet]|tuple[Outlet,...]], tuple[Outlet,...]]=None
                 )->None:
        self._index = 0  # Initialize iteration index
        outlets = format_outlets(outlets)
        sorter = sorter if sorter is not None else default_sorter
        self.outlets = sorter(outlets)

    def __iter__(self):
        """Return iterator starting from lowest location outlet."""
        self._index = 0
        return self

    def __next__(self) -> Outlet:
        """Return next outlet going from lowest to highest location."""
        if self._index < len(self.outlets):
            outlet = self.outlets[self._index]
            self._index += 1
            return outlet
        raise StopIteration

    def __len__(self) -> int:
        """Return number of outlets."""
        return len(self.outlets)

    def __getitem__(self, index: int) -> Outlet:
        """Allow indexing: outlets[0] returns lowest location outlet."""
        return self.outlets[index]

def default_sorter(outlets: Sequence[Outlet]) -> tuple[Outlet, ...]:
    """
    Default sorter function for outlets: sorts by location descending,
    then by name ascending.
    
    Parameters
    ----------
    outlets : Sequence[Outlet]
        Collection of outlets to sort
        
    Returns
    -------
    tuple[Outlet, ...]
        Sorted tuple of outlets
    """
    sorted_outlets = sorted(outlets, key=lambda o: (-o.location, o.name))
    return tuple(sorted_outlets)

def format_outlets(outlets: list[Outlet]|tuple[Outlet, ...]) -> tuple[Outlet, ...]:
    """
    Format outlet names to ensure uniqueness and consistency.
    
    Makes deep copy of outlets, modifies names to be unique using the pattern:
    - outlet.name is set to 'outlet' if empty
    - new_name = <outlet.name>@<outlet.location> if unique
    - new_name = <outlet.name><duplicate_number>@<outlet.location> otherwise
    
    Parameters
    ----------
    outlets : list[Outlet] | tuple[Outlet, ...]
        Collection of outlets to format
        
    Returns
    -------
    tuple[Outlet, ...]
        Tuple of outlets with formatted unique names
        
    Raises
    ------
    ValueError
        If outlet names are invalid or unique names cannot be created
    """
    def preprocess(outlets: list[Outlet]) -> list[Outlet]:
        # Deep copy avoids modifying original outlets.
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
        # Find list of outlets with specified name.
        duplicates = []
        for outlet in outlets:
            if outlet.name == name:
                duplicates.append(outlet)
        if len(duplicates) != count:
            raise ValueError(f'Found {len(duplicates)} {name} names, expected {count}.')
        return duplicates

    def rename_duplicates(duplicates: list[Outlet], is_first_pass: bool) -> list[Outlet]:
        # Rename outlets to ensure uniqueness.
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

    outlets = preprocess(list(outlets))
    # Counter is dict: keys are matching elements, values are count of dups,
    # i.e., keys = outlet.name and value = count of outlets with the same name.
    name_counter = Counter([o.name for o in outlets])

    # First pass: add location to name
    for k, n in name_counter.items():
        if n > 1:  # k is duplicated
            duplicates = rename_duplicates(find_duplicates(k, n, outlets), True)
            name_recounter = Counter([o.name for o in duplicates])

            # Second pass: add index to name
            for k, n in name_recounter.items():
                if n > 1:
                    rename_duplicates(find_duplicates(k, n, duplicates), False)

    # Check for unique names
    if len({o.name for o in outlets}) != len(outlets):
        raise ValueError(f'Failed to create unique names: {[o.name for o in outlets]}.')
    return tuple(outlets)
