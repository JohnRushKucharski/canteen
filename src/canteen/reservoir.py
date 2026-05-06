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
from canteen.validation import validate_is_not_negative, validate_is_at_least

class Reservoir(Protocol):
    '''
    Protocol defining the reservoir interface.
    '''
    name: str
    storage: int|float
    capacity: int|float

    operations: None|Operations
    mappings: Mappings
    pools: Pools
    outlets: Outlets

    def operate(
            self, inflow: int|float, *args: Any, **kwargs: Any
    ) -> tuple[int|float, ...]:
        '''Calls operations to perform reservoir operations.'''

@dataclass
class BaseReservoir:
    """
    Basic reservoir implementing the Reservoir interface.
    
    Supports builder pattern for adding components.

    Physical infrastructure fields (outlets, pools, capacity, mappings) are frozen
    after construction (ADR-0002). Only storage remains mutable. Optional container
    fields (outlets, pools, mappings) default to empty Null Objects — never None
    (ADR-0003).
    """
    name: str
    storage: int|float
    capacity: int|float
    operations: None|Operations = None

    mappings: Mappings = None  # type: ignore  # Will be set in __post_init__
    pools: Pools = None  # type: ignore  # Will be set in __post_init__
    outlets: Outlets = None  # type: ignore  # Will be set in __post_init__

    def __post_init__(self) -> None:
        validate_is_not_negative(self.storage, "storage")
        validate_is_at_least(self.capacity, self.storage, "capacity", "storage")
        if self.outlets is None:
            object.__setattr__(self, 'outlets', Outlets())
        if self.pools is None:
            object.__setattr__(self, 'pools', Pools())
        if self.mappings is None:
            object.__setattr__(self, 'mappings', Mappings())
        if len(self.outlets) > 0 and not self.is_outlets_less_than_capacity(self.outlets):
            raise ValueError(
                    f"""Invalid outlet location. Reservoir capacity: {self.capacity} must be
                    greater than outlet location.
                    Got outlets:{[f'{o.name}: {o.location}' for o in self.outlets]}.""")
        if len(self.pools) > 0 and not self.is_pools_less_than_capacity(self.pools):
            raise ValueError(
                    f"""Invalid pool location. Reservoir capacity: {self.capacity} must be
                    greater than top of storage for upper pool.
                    {self.pools[0].info.name} has top of storage:{self.pools[0].info.range_[1]}.""")
        # Freeze structural fields — storage remains mutable (ADR-0002).
        object.__setattr__(self, '_initialised', True)

    def __setattr__(self, name: str, value: Any) -> None:
        """Freeze structural fields after construction; storage stays mutable."""
        if hasattr(self, '_initialised') and name != 'storage':
            raise AttributeError(
                f"Cannot set '{name}' after construction. "
                "Physical infrastructure is frozen after construction (ADR-0002). "
                "Use ReservoirBuilder or factory() to construct reservoirs with components."
            )
        object.__setattr__(self, name, value)

    def is_pools_less_than_capacity(self, pools: Pools) -> bool:
        """Check if pool top of storage is less than reservoir capacity."""
        return pools[0].info.range_[1] <= self.capacity

    def is_outlets_less_than_capacity(self, outlets: Outlets) -> bool:
        """Check if outlet location is less than reservoir capacity."""
        return all(outlet.location <= self.capacity for outlet in outlets)

    def add_maps(self, mappings: Mappings) -> Self:
        """Add mappings to the reservoir, modifying its state."""
        if len(self.mappings) > 0:
            raise ValueError("Mappings already defined for reservoir.")
        object.__setattr__(self, 'mappings', mappings)
        return self

    def add_pools(self, pools: Pools) -> Self:
        """Add pools to the reservoir, modifying its state."""
        if len(self.pools) > 0:
            raise ValueError("Pools already defined for reservoir.")
        if not self.is_pools_less_than_capacity(pools):
            raise ValueError(
                f"""Invalid pool location. Reservoir capacity: {self.capacity} must be
                greater than top of storage for upper pool.
                {pools[0].info.name} has top of storage:{pools[0].info.range_[1]}.""")
        object.__setattr__(self, 'pools', pools)
        return self

    def add_outlets(self, outlets: Outlets) -> Self:
        """Add outlets to the reservoir, modifying its state."""
        if len(self.outlets) > 0:
            raise ValueError("Outlets already defined for reservoir.")
        if not self.is_outlets_less_than_capacity(outlets):
            raise ValueError(
                f"""Invalid outlet location. Reservoir capacity: {self.capacity} must be
                greater than outlet location.
                Got outlets:{[f'{o.name}: {o.location}' for o in outlets]}.""")
        object.__setattr__(self, 'outlets', outlets)
        return self

    def add_operations(self, operations: Operations) -> Self:
        """Add operations to the reservoir, modifying its state."""
        if self.operations:
            raise ValueError("Operations already defined for reservoir.")
        object.__setattr__(self, 'operations', operations)
        return self

    def operate(
            self, inflow: int|float, *args: Any, **kwargs: Any
    ) -> tuple[int|float, ...]:
        """Perform reservoir operations and advance storage."""
        if not self.operations:
            raise ValueError('No operations defined for reservoir.')
        result = self.operations.operate(self, inflow, *args, **kwargs)
        self.storage = self.storage + inflow - sum(result)
        return result

    def __repr__(self) -> str:
        """String representation of the reservoir."""
        outlet_names = [o.name for o in self.outlets] if len(self.outlets) > 0 else []
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
            operations: None|Operations = None,
            outlets: None|Outlets = None, pools: None|Pools = None, mappings: None|Mappings = None
            )-> Reservoir:
    """
    Factory function to create a reservoir with specified parameters.
    
    Uses ReservoirBuilder internally to ensure consistent validation
    and construction. Provides a convenient interface for simple cases
    while maintaining the builder pattern's guarantees.
    """
    builder = ReservoirBuilder(name=name, storage=storage, capacity=capacity)
    
    # Add operations (required, defaults to PassiveOperations)
    builder.add_operations(operations if operations is not None else PassiveOperations())
    
    # Add optional components if provided
    if outlets is not None:
        builder.add_outlets(outlets)
    if pools is not None:
        builder.add_pools(pools)
    if mappings is not None:
        builder.add_mappings(mappings)
    
    return builder.build()


class ReservoirBuilder:
    """
    Builder for constructing immutable BaseReservoir instances.
    
    Accumulates components via fluent API and validates completeness
    before construction. Ensures invalid reservoir states (missing operations,
    None checks) are unrepresentable.
    """

    def __init__(self, name: str, storage: int|float, capacity: int|float) -> None:
        """
        Initialize builder with required reservoir parameters.
        
        Parameters
        ----------
        name : str
            Reservoir name.
        storage : int|float
            Initial storage volume.
        capacity : int|float
            Maximum storage capacity.
        """
        self._name = name
        self._storage = storage
        self._capacity = capacity
        self._operations: None|Operations = None
        self._outlets: None|Outlets = None
        self._pools: None|Pools = None
        self._mappings: None|Mappings = None

    def add_operations(self, operations: Operations) -> Self:
        """
        Add operations strategy to the builder.
        
        Parameters
        ----------
        operations : Operations
            The operations strategy to attach.
        
        Returns
        -------
        Self
            This builder instance for method chaining.
        """
        self._operations = operations
        return self

    def add_outlets(self, outlets: Outlets) -> Self:
        """
        Add outlets to the builder.
        
        Parameters
        ----------
        outlets : Outlets
            The outlets collection to attach.
        
        Returns
        -------
        Self
            This builder instance for method chaining.
        """
        self._outlets = outlets
        return self

    def add_pools(self, pools: Pools) -> Self:
        """
        Add pools to the builder.
        
        Parameters
        ----------
        pools : Pools
            The pools collection to attach.
        
        Returns
        -------
        Self
            This builder instance for method chaining.
        """
        self._pools = pools
        return self

    def add_mappings(self, mappings: Mappings) -> Self:
        """
        Add mappings to the builder.
        
        Parameters
        ----------
        mappings : Mappings
            The mappings collection to attach.
        
        Returns
        -------
        Self
            This builder instance for method chaining.
        """
        self._mappings = mappings
        return self

    def build(self) -> BaseReservoir:
        """
        Construct and return an immutable BaseReservoir.
        
        Returns
        -------
        BaseReservoir
            A fully validated reservoir instance.
        
        Raises
        ------
        ValueError
            If operations is not set.
        """
        if self._operations is None:
            raise ValueError("Operations must be set before building reservoir.")
        
        return BaseReservoir(
            name=self._name,
            storage=self._storage,
            capacity=self._capacity,
            operations=self._operations,
            outlets=self._outlets if self._outlets is not None else Outlets(),
            pools=self._pools if self._pools is not None else Pools(),
            mappings=self._mappings if self._mappings is not None else Mappings()
        )
