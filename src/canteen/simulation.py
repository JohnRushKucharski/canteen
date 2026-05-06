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
        storage (float), spill (float). Returns empty array with correct
        dtype when inflows is empty.
    """
    # Define result dtype
    dtype = np.dtype([
        ('timestep', np.int32),
        ('inflow', np.float64),
        ('storage', np.float64),
        ('spill', np.float64)
    ])

    # Handle empty inflows edge case
    if len(inflows) == 0:
        return np.array([], dtype=dtype)

    # Copy reservoir to preserve original
    res_copy = copy.deepcopy(reservoir)

    # Pre-allocate result array
    result = np.zeros(len(inflows), dtype=dtype)

    # Simulate each timestep
    for timestep, inflow in enumerate(inflows):
        # Call operate to get outflows
        outflows = res_copy.operate(inflow)

        # Record results
        result[timestep]['timestep'] = timestep
        result[timestep]['inflow'] = inflow
        result[timestep]['storage'] = res_copy.storage
        # Spill is always the last element of outflows tuple
        result[timestep]['spill'] = outflows[-1]

    return result
