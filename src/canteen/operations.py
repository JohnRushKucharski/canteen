"""
Operations strategies for reservoir management.

This module provides the operations interface and implementations for
different reservoir operation strategies, such as passive spillway operations.
Supports both floating-point and integer arithmetic with type safety.
"""
from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING
from dataclasses import dataclass

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
    def output_labels(self, reservoir: Reservoir) -> tuple[str, ...]:
        """
        Get labels for operation outputs.

        Parameters
        ----------
        reservoir : Reservoir
            The reservoir to get labels for.
        """

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
