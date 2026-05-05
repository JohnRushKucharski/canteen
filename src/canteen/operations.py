"""
Operations strategies for reservoir management.

This module provides the operations interface and implementations for
different reservoir operation strategies, such as passive spillway operations.
Supports both floating-point and integer arithmetic with type safety.
"""
from __future__ import annotations

from typing import Any, Protocol, TYPE_CHECKING
from dataclasses import dataclass

from canteen.mapping import Mappings
#from canteen.reservoir import Reservoir

if TYPE_CHECKING:
    from canteen.reservoir import Reservoir


# TODO: Pool operations, maybe use mappings to demonstrate how these can be used to stack functions.

class Operations(Protocol):
    """
    Protocol for reservoir operation strategies.
    """
    verbose: bool
    mappings: None|Mappings

    def operate(self, *args: Any, **kwargs: Any) -> int|float|tuple[int|float,...]:
        """
        Execute reservoir operations.
        
        Parameters
        ----------
        *args : Any
            Additional positional arguments
        **kwargs : Any
            Additional keyword arguments
            
        Returns
        -------
        int|float|tuple[int|float,...]
            Single release volume if no outlets are defined, or
            Tuple of release volumes, one for each reservoir outlet and a spilled release. 
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
    Makes maximum releases through outlets, if they are defined and spills excess above capacity.
    """
    verbose: bool = True
    mappings: None|Mappings = None

    def operate(self, reservoir: Reservoir, inflow: int|float, #pylint: disable=unused-argument
                *args: Any, **kwargs: Any) -> int|float|tuple[int|float, ...]:
        """
        Apply passive operations to reservoir for single time step.
        """
        def operate_outlets(active_storage: int|float) -> tuple[int|float, ...]:
            """
            Helper function for reservoirs with outlets.
            """
            # Only called if has_outlets is True
            assert reservoir.outlets is not None
            outflows: list[int|float] = []
            # first operate outlets.
            for outlet in reservoir.outlets:
                outflows.append(inc_outflow := outlet.operations(active_storage).max)
                active_storage-=inc_outflow
            # then spill any remaining volume above capacity.
            outflows.append(max(0.0, active_storage - reservoir.capacity))
            return tuple(outflows)

        active_storage = reservoir.storage + inflow
        spilled_outflow: int|float = max(0.0, active_storage - reservoir.capacity)
        # if outlets operate outlets, then spill. if no outlets, only spill excess.
        return operate_outlets(active_storage) if reservoir.outlets and self.verbose else spilled_outflow #pylint: disable=line-too-long

    def output_labels(self, reservoir: Reservoir) -> tuple[str, ...]:
        """
        Get labels for operation outputs.
        """
        if reservoir.outlets and self.verbose:
            outlet_labels = [outlet.name for outlet in reservoir.outlets]
            return tuple(outlet_labels + ['Spill'])
        else:
            return ("Spill",)

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
