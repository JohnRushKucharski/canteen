"""
Operations strategies for reservoir management.

This module provides the operations interface and implementations for
different reservoir operation strategies, such as passive spillway operations.
Supports both floating-point and integer arithmetic with type safety.
"""
from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING
from dataclasses import dataclass

from canteen.validation import (
    validate_is_at_least,
    validate_is_ascending_range,
    validate_is_not_negative,
    validate_operation_output_shape,
    validate_is_on_range,
)

if TYPE_CHECKING:
    from canteen.reservoir import Reservoir


# TODO: Pool operations, maybe use mappings to demonstrate how these can be used to stack functions.

class Operations(Protocol):
    """
    Protocol for reservoir operation strategies.
    """

    def operate(self, reservoir: Reservoir, inflow: int|float,
                *args: Any, **kwargs: Any) -> tuple[int|float, ...]:
        """
        Execute reservoir operations.

        Parameters
        ----------
        reservoir : Reservoir
            The reservoir to operate.
        inflow : int|float
            Volume of water entering the reservoir this timestep.
        *args : Any
            Additional positional arguments.
        **kwargs : Any
            Additional keyword arguments.

        Returns
        -------
        tuple[int|float, ...]
            One release volume per outlet (highest-to-lowest location) plus spill
            as the final element. Returns (spill,) when no outlets are defined.
        """
        return (0.0,)

    def output_labels(self, reservoir: Reservoir) -> tuple[str, ...]:
        """
        Get labels for operation outputs.

        Parameters
        ----------
        reservoir : Reservoir
            The reservoir to get labels for.
        """
        return ('Spill',)

@dataclass
class PassiveOperations:
    """
    Passive operations strategy for reservoirs.

    Makes maximum releases through outlets from highest to lowest location,
    then spills any remaining volume above capacity. Always returns a tuple:
    one value per outlet plus spill as the final element.
    """

    def operate(self, reservoir: Reservoir, inflow: int|float,
                *args: Any, **kwargs: Any) -> tuple[int|float, ...]:
        """
        Apply passive operations to reservoir for a single timestep.

        Parameters
        ----------
        reservoir : Reservoir
            The reservoir to operate. Storage is NOT mutated here.
        inflow : int|float
            Volume of water entering the reservoir this timestep.

        Returns
        -------
        tuple[int|float, ...]
            One release per outlet (highest-to-lowest location) plus spill.
            Returns (spill,) when no outlets are defined.
        """
        active_storage = reservoir.storage + inflow
        outflows: list[int|float] = []
        for outlet in reservoir.outlets:
            outflows.append(inc_outflow := outlet.operations(active_storage).max)
            active_storage -= inc_outflow
        outflows.append(max(0.0, active_storage - reservoir.capacity))
        return tuple(outflows)

    def output_labels(self, reservoir: Reservoir) -> tuple[str, ...]:
        """
        Get output labels matching the tuple returned by operate().
        """
        outlet_labels = [outlet.name for outlet in reservoir.outlets]
        return tuple(outlet_labels + ['Spill'])

    def __repr__(self) -> str:
        """String representation."""
        return "PassiveOperations()"


#TODO: Generalize the use of Decorators.

@dataclass
class HedgingOperationsDecorator:
    """Operations decorator that reduces outlet releases in a hedging range."""

    base_operations: Operations
    hedging_min_storage: int | float
    hedging_max_storage: int | float
    reduction_factor: int | float

    def __post_init__(self) -> None:
        """Validate hedging parameter domains at construction time."""
        validate_is_not_negative(self.hedging_min_storage, "hedging_min_storage")
        validate_is_ascending_range(self.hedging_min_storage, self.hedging_max_storage, "hedging storage range") # pylint: disable=line-too-long
        validate_is_on_range(self.reduction_factor, 0.0, 1.0, "reduction_factor")

    def operate(self, reservoir: Reservoir, inflow: int | float, *args: Any, **kwargs: Any
                ) -> tuple[int | float, ...]:
        """Delegate to base operations and optionally reduce non-spill releases."""
        validate_is_at_least(reservoir.capacity, self.hedging_max_storage,
                             "reservoir.capacity", "hedging_max_storage")

        base_outflows = tuple(self.base_operations.operate(reservoir, inflow, *args, **kwargs))
        validate_operation_output_shape(base_outflows, len(reservoir.outlets),
                                        self.base_operations.__class__.__name__)

        active_storage = reservoir.storage + inflow
        if not self.hedging_min_storage <= active_storage <= self.hedging_max_storage:
            return base_outflows

        non_spill = base_outflows[:-1]

        reduced_non_spill: list[int | float] = []
        for base_release, outlet in zip(non_spill, reservoir.outlets, strict=True):
            outlet_range = outlet.operations(active_storage)
            reduced_release = base_release * self.reduction_factor
            bounded_release = max(
                outlet_range.min,
                min(reduced_release, outlet_range.max),
            )
            reduced_non_spill.append(bounded_release)
            active_storage -= bounded_release

        post_release_active_storage = active_storage
        spill = max(0.0, post_release_active_storage - reservoir.capacity)
        return tuple(reduced_non_spill) + (spill,)

    def output_labels(self, reservoir: Reservoir) -> tuple[str, ...]:
        """Delegate output labels to wrapped operations strategy."""
        return self.base_operations.output_labels(reservoir)

    def __repr__(self) -> str:
        """String representation."""
        return (
            "HedgingOperationsDecorator("
            f"base_operations={self.base_operations}, "
            f"hedging_min_storage={self.hedging_min_storage}, "
            f"hedging_max_storage={self.hedging_max_storage}, "
            f"reduction_factor={self.reduction_factor}"
            ")"
        )

NAMED_OPERATIONS = {
    "PASSIVE": PassiveOperations,
}

def factory(named_operation: None|str = None) -> Operations:
    """
    Factory function to create operations instances by name.
    
    Parameters
    ----------
    named_operation : str
        Name of the operations strategy (e.g., 'Passive')
    
    Returns
    -------
    Operations
        The created operations instance.
    Raises
    ------
    KeyError
        If the specified operations name is not recognized.
    
    Examples
    --------
    >>> ops = factory("Passive")
    """
    named_operation = "Passive" if named_operation is None else named_operation
    if (_name := named_operation.upper()) in NAMED_OPERATIONS:
        return NAMED_OPERATIONS[_name]()
    raise KeyError(f"Unknown operations strategy name: {named_operation}")
