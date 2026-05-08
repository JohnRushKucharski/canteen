"""
Simulation module for running reservoir operations over multiple timesteps.

This module provides the orchestration layer that runs a reservoir through
multiple timesteps given a sequence of inflows. Copies the reservoir internally,
calls operate(inflow) for each timestep, and records storage and outflow states.
"""

from typing import Sequence, Any
import copy
import numpy as np
from numpy.typing import NDArray

from canteen.reservoir import Reservoir

_RESERVED_COLUMNS: frozenset[str] = frozenset({'timestep', 'inflow', 'storage', 'spill'})


def simulate(
    reservoir: Reservoir,
    inflows: Sequence[float] | NDArray[np.floating[Any]],
    timestamps: Sequence[Any] | None = None
) -> NDArray[np.void]:
    """
    Simulate reservoir operations over multiple timesteps.

    Copies the reservoir internally to preserve the original state, then runs
    operate() for each inflow and records results.

    Parameters
    ----------
    reservoir : Reservoir
        The reservoir to simulate. Original instance is not modified.
    inflows : Sequence[float] | NDArray[np.floating[Any]]
        Volume of water entering the reservoir at each timestep. Can be negative
        (evaporation is valid).
    timestamps : Sequence[Any] | None
        Optional timestamps for labeling results. Not required for execution.

    Returns
    -------
    NDArray[np.void]
        Structured array with columns: timestep (int), inflow (float),
        storage (float), one column per outlet (named by outlet), spill (float).
        Returns empty array with correct dtype when inflows is empty.
    """
    # Extract outlet names from reservoir for dynamic columns
    outlet_names = [outlet.name for outlet in reservoir.outlets]

    # Guard: outlet names must not collide with reserved column names
    conflicts = _RESERVED_COLUMNS.intersection(outlet_names)
    if conflicts:
        raise ValueError(
            f"Outlet name(s) conflict with reserved simulation columns: "
            f"{sorted(conflicts)}. Reserved names are: {sorted(_RESERVED_COLUMNS)}."
        )

    # Build dtype dynamically: timestep, inflow, storage, [outlets...], spill
    dtype_fields = [
        ('timestep', np.int32),
        ('inflow', np.float64),
        ('storage', np.float64),
    ]
    # Add one column per outlet
    for outlet_name in outlet_names:
        dtype_fields.append((outlet_name, np.float64))
    # Add spill as the last column
    dtype_fields.append(('spill', np.float64))

    dtype = np.dtype(dtype_fields)

    # Handle empty inflows edge case
    if len(inflows) == 0:
        return np.array([], dtype=dtype)

    # Validate reservoir has operations defined
    if reservoir.operations is None:
        raise ValueError(
            "Reservoir must have operations defined. "
            "Use reservoir.factory() with operations or builder pattern."
        )

    # Copy reservoir to preserve original
    res_copy = copy.deepcopy(reservoir)

    # Pre-allocate result array
    result = np.zeros(len(inflows), dtype=dtype)

    # Simulate each timestep
    for timestep, inflow in enumerate(inflows):
        # Call operate to get outflows
        outflows = res_copy.operate(inflow)

        # Validate storage bounds after operation
        if res_copy.storage < 0:
            raise ValueError(
                f"Storage became negative at timestep {timestep}: "
                f"storage={res_copy.storage:.2f}. "
                f"Check inflows and operations configuration."
            )
        if res_copy.storage > res_copy.capacity:
            raise ValueError(
                f"Storage exceeded capacity at timestep {timestep}: "
                f"storage={res_copy.storage:.2f}, capacity={res_copy.capacity:.2f}. "
                f"Check operations spill behavior."
            )

        # Record results
        result[timestep]['timestep'] = timestep
        result[timestep]['inflow'] = inflow
        result[timestep]['storage'] = res_copy.storage

        # Record per-outlet releases (all elements except the last, which is spill)
        for i, outlet_name in enumerate(outlet_names):
            result[timestep][outlet_name] = outflows[i]

        # Spill is always the last element of outflows tuple
        result[timestep]['spill'] = outflows[-1]

    return result
