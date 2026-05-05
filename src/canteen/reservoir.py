"""
Reservoir modeling components for the Canteen package.

This module provides the core reservoir interfaces and implementations
with basic functionality and state management.

Reservoirs can be created created and maintained with integer or floating-point arithmetic.

A builder pattern is used to support for adding reservoir components like outlets and pools,
composition is used instead of inheritance for extensible component management.
"""

from dataclasses import dataclass
from typing import Any, Protocol, Self

from canteen.mapping import Mappings
from canteen.pool import Pools
from canteen.outlet import Outlets
from canteen.operations import Operations, PassiveOperations

class Reservoir(Protocol):
    '''
    Protocol defining the reservoir interface.
    '''
    name: str
    storage: int|float
    capacity: int|float

    mappings: None|Mappings = None
    pools: None|Pools = None
    outlets: None|Outlets = None

    def operate(self, *args: Any, **kwargs: Any) -> Any:
        '''Calls operations to perform reservoir operations.'''
        #Return failure if no operations are defined.

@dataclass
class BaseReservoir:
    """
    Basic reservoir implementing the Reservoir interface.
    
    Supports builder pattern for adding components.
    """
    name: str
    storage: int|float
    capacity: int|float
    operations: None|Operations = None

    mappings: None|Mappings = None
    pools: None|Pools = None
    outlets: None|Outlets = None

    def __post_init__(self) -> None:
        if not 0 <= self.storage <= self.capacity:
            raise ValueError(f"""Storage must be between 0 and {self.capacity}.
                             Got storage={self.storage}.""")
        if self.pools and not self.is_pools_less_than_capacity(self.pools):
            raise ValueError(
                    f"""Invalid pool location. Reservoir capacity: {self.capacity} must be
                    greater than top of storage for upper pool.
                    {self.pools[0].info.name} has top of storage:{self.pools[0].info.range_[1]}.""")
        if self.outlets and not self.is_outlets_less_than_capacity(self.outlets):
            raise ValueError(
                    f"""Invalid outlet location. Reservoir capacity: {self.capacity} must be
                    greater than outlet location.
                    Got outlets:{[f'{o.name}: {o.location}' for o in self.outlets]}.""")

    def is_pools_less_than_capacity(self, pools: Pools) -> bool:
        """Check if pool top of storage is less than reservoir capacity."""
        return pools[0].info.range_[1] <= self.capacity

    def is_outlets_less_than_capacity(self, outlets: Outlets) -> bool:
        """Check if outlet location is less than reservoir capacity."""
        return all(outlet.location <= self.capacity for outlet in outlets)

    def add_maps(self, mappings: Mappings) -> Self:
        """Add mappings to the reservoir, modifying its state."""
        if self.mappings:
            raise ValueError("Mappings already defined for reservoir.")
        self.mappings = mappings
        return self

    def add_pools(self, pools: Pools) -> Self:
        """Add pools to the reservoir, modifying its state."""
        if self.pools:
            raise ValueError("Pools already defined for reservoir.")
        if not self.is_pools_less_than_capacity(pools):
            raise ValueError(
                f"""Invalid pool location. Reservoir capacity: {self.capacity} must be
                greater than top of storage for upper pool.
                {pools[0].info.name} has top of storage:{pools[0].info.range_[1]}.""")
        self.pools = pools
        return self

    def add_outlets(self, outlets: Outlets) -> Self:
        """Add outlets to the reservoir, modifying its state."""
        if self.outlets:
            raise ValueError("Outlets already defined for reservoir.")
        if not self.is_outlets_less_than_capacity(outlets):
            raise ValueError(
                f"""Invalid outlet location. Reservoir capacity: {self.capacity} must be
                greater than outlet location.
                Got outlets:{[f'{o.name}: {o.location}' for o in outlets]}.""")
        self.outlets = outlets
        return self

    def add_operations(self, operations: Operations) -> Self:
        """Add operations to the reservoir, modifying its state."""
        if self.operations:
            raise ValueError("Operations already defined for reservoir.")
        self.operations = operations
        return self

    def operate(self, *args: Any, **kwargs: Any) -> Any:
        """Perform reservoir operations."""
        if not self.operations:
            raise ValueError('No operations defined for reservoir.')
        return self.operations.operate(self,*args, **kwargs)

    def __repr__(self) -> str:
        """String representation of the reservoir."""
        outlet_names = [o.name for o in self.outlets] if self.outlets else []
        base_repr = (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"storage={self.storage}, "
            f"capacity={self.capacity}, "
            f"operations={self.operations}"
        )
        if outlet_names:
            return base_repr + f", outlets={outlet_names})"
        return base_repr + ")"

def factory(name: str = "reservoir", storage: int|float = 0, capacity: int|float = 1,
            operations: None|Operations = PassiveOperations(),
            outlets: None|Outlets = None, pools: None|Pools = None, mappings: None|Mappings = None
            )-> Reservoir:
    """Factory function to create a reservoir with specified parameters."""
    return BaseReservoir(
        name=name,
        storage=storage,
        capacity=capacity,
        operations=operations,
        outlets=outlets,
        pools=pools,
        mappings=mappings
    )
