"""
Pool protocols and implementations for reservoir components.

This module provides the Pool interface and concrete implementations for
modeling storage pools within reservoirs with generic numeric types.
Supports both static and dynamic pool location definitions.
"""
from typing import Protocol, Any
from dataclasses import dataclass

from canteen.metadata import MetaDataPlusRange
from canteen.mapping import Mappings, constantmapping_factory, rulecurve_factory
from canteen.validation import validate_is_not_negative, validate_is_ascending_range

class Pool(Protocol):
    """Protocol for pool components."""
    info: MetaDataPlusRange
    mappings: None|Mappings

    def location(self, *args: Any, **kwargs: Any) -> int|float:
        """
        Get the current top of poolstorage location for this pool.
        
        Returns
        -------
        int | float
            The current top of poolstorage location (int or float)
        """

@dataclass
class Pools:
    """Container for multiple Pool instances with iteration support."""
    pools: tuple[Pool, ...]

    def __post_init__(self) -> None:
        sorted_pools = sorted(self.pools, key=lambda p: p.location(), reverse=True)
        # Pools sorted top to bottom (descending location)
        self.pools = tuple(sorted_pools)
        # Initialize iteration index
        self._index = 0

    def __iter__(self):
        """Return iterator starting from top (highest location) pool."""
        self._index = 0
        return self

    def __next__(self) -> Pool:
        """Return next pool going from top to bottom."""
        if self._index < len(self.pools):
            pool = self.pools[self._index]
            self._index += 1
            return pool
        raise StopIteration

    def __len__(self) -> int:
        """Return number of pools."""
        return len(self.pools)

    def __getitem__(self, index: int) -> Pool:
        """Allow indexing: pools[0] returns top pool."""
        return self.pools[index]

    def active_pool(self, volume: int|float, *args, **kwargs) -> Pool:
        """
        Determine the active pool for a given reservoir volume.
        
        Parameters
        ----------
        volume : int|float
            Current reservoir volume.
        
        Returns
        -------
        Pool
            The active Pool instance for the given volume.
        
        Raises
        ------
        ValueError
            If volume is negative or exceeds all pool locations.
        """
        if volume < 0:
            validate_is_not_negative(volume, "volume")
        # Find first pool with volume
        for i, pool in enumerate(self.pools):
            top = pool.location(*args, **kwargs)
            # TOP POOL, invalid volume.
            if i == 0 and top < volume:
                # volume above top pool location, which is invalid.
                raise ValueError(
                    f"""Volume cannot exceed the top of the top pool.
                    Got: {volume} with top of top pool: {(pool.info.name, top)}""")
            # BOTTOM POOL, must be here.
            if i == len(self.pools) - 1:
                # volume must be here.
                return pool
            bottom = self.pools[i + 1].location(*args, **kwargs)
            # POOL OVERLAP, invalid result.
            if bottom > top:
                raise ValueError(
                    f"""Pools not properly ordered.
                    {pool.info.name} with top of storage: {top} listed above,
                    {self.pools[i + 1].info.name} with top of storage: {bottom}""")
            if bottom < volume <= top:
                return pool
        # Should never reach here due to earlier checks
        raise ValueError(f"No pool found for volume: {volume}")

class StaticPool:
    """
    Static pool implementation with fixed location.
    
    Parameters
    ----------
    info : PoolMetaData, optional
        Pool metadata, by default None
    location : int | float, optional
        Top of pool storage location, 1 by default.
    """
    def __init__(self, info: MetaDataPlusRange, mappings: Mappings)-> None:
        if "location" not in mappings:
            raise ValueError("""StaticPool requires a 'location' mapping in mappings.
                             Use the factory function or provide a location mapping in mappings.""")
        loc = mappings["location"].f()
        validate_is_not_negative(loc, "Pool location")
        if info.range_[0] != info.range_[1] or info.range_[0] != loc:
            raise ValueError(f"""StaticPool range must be a single value matching location mapping.
                             Got range {info.range_} and location {loc}.""")
        self.info: MetaDataPlusRange = info
        self.mappings: None|Mappings = mappings

    def __repr__(self) -> str:
        """String representation."""
        return f"StaticPool(name={self.info.name}, location={self.location()})"

    def location(self, *args: Any, **kwargs: Any) -> int|float: #pylint: disable=unused-argument
        """
        Get the fixed location value.
        
        Returns
        -------
        int | float
            The fixed location value.
        """
        assert self.mappings is not None
        return self.mappings["location"].f()

class VariablePool:
    """
    Variable pool implementation with dynamic location.
    
    Uses a callable function to determine the location dynamically.
    
    Parameters
    ----------
    name : str, optional
        Pool name, by default ""
    location_function : Callable[..., int | float]
        Function that returns the top pool storage location.
    
    Examples
    --------
    A common use case for VariablePool is to define a rule curve 
    for the conservation pool based on the day of the water year.
    >>> def rule_curve(day_of_water_year: int) -> float:
    """
    def __init__(self, info: MetaDataPlusRange, mappings: Mappings)-> None:
        if "location" not in mappings:
            raise ValueError("VariablePool requires a 'location' mapping in mappings.")
        if info.range_[0] > info.range_[1] or info.range_[0] < 0:
            validate_is_not_negative(info.range_[0], "Pool location range minimum")
            validate_is_ascending_range(info.range_[0], info.range_[1], "Pool location range")
        self.info: MetaDataPlusRange = info
        self.mappings: None|Mappings = mappings

    def location(self, *args: Any, **kwargs: Any) -> int|float: #pylint: disable=unused-argument
        """
        Get the dynamic location value by calling the location function.
        
        Returns
        -------
        int | float
            The location value returned by the location function.
        """
        assert self.mappings is not None
        return self.mappings["location"].f(*args, **kwargs)

    def __repr__(self) -> str:
        """String representation."""
        #assert self.mappings is not None
        return f"VariablePool(name={self.info.name}, locations={self.info.range_})"
        # info = self.mappings["location"].info
        # if isinstance(info, XYMetaData):
        #     return f"VariablePool(name='{self.name}', location_range={info.range_})"
        # return f"VariablePool(name='{self.name}', location_map={self.mappings['location']})"


def factory(
    location: None|int|float = 1.0,
    name: str = "", description: str = "",
    mappings: None|Mappings = None) -> Pool:
    """
    Factory function to create Static or Variable Pool instances.
    
    Examples
    --------
    Static pool at location 10.0:
    >>> pool = factory(name="Static Pool", location=10.0)
    Variable pool with default rule curve:
    >>> pool = factory(name="Variable Pool", location=None)
    Variable pool with a custom rating curve:
    >>> from canteen.mapping import ratingcurve_factory
    >>> custom_map = Mappings([
        ratingcurve_factory([1, 30, 60, 180, 210, 365], [10.0, 10.0, 5.0, 5.0, 10.0, 10.0])
        ])
    >>> pool = factory(name="Seasonal Conservation Pool", location=None, mappings=custom_map)
    """
    mappings = mappings if mappings else Mappings()
    if isinstance(location, int|float):
        if "location" in mappings:
            raise ValueError("location: location mapping already exists in mappings.")
        mappings["location"] = constantmapping_factory(location, "location")
        info = MetaDataPlusRange(name=name if name else "static pool",
                                 description=description if description else f"A pool with fixed top of storage @{location}.", #pylint: disable=line-too-long
                                 range_ = (location, location))
        return StaticPool(info, mappings)
    # location argument is none.
    if "location" in mappings:
        if not hasattr(mappings["location"].info, "range_"):
            raise ValueError("location mapping must have range_ attribute in info.")
        location_range = mappings["location"].info.range_
        info = MetaDataPlusRange(name=name if name else "variable pool",
                                 description=description if description else f"pool with top of storage on range {location_range}.", #pylint: disable=line-too-long
                                 range_ = location_range)
        return VariablePool(info, mappings)
    mappings["location"] = rulecurve_factory([1, 365], [1.0, 1.0])
    info = MetaDataPlusRange(name=name if name else "variable pool",
                             description=description if description else f"pool with top of storage on range {(1, 1)}.", #pylint: disable=line-too-long
                             range_ = (1, 1))
    return VariablePool(info, mappings)
