"""
Units-aware validation utilities for the Canteen package.

This module contains all validators that depend on the optional `units` package.
It must not be imported by core modules directly — domain objects with optional
Quantity fields embed their own unit guards inline (see ReleaseRange.check_units).

All isinstance(..., Quantity) checks are guarded with `Quantity is not None and ...`
so that this module can be imported even when the optional units extra is not installed.
"""
from typing import Any

from canteen.units import Quantity, Category


def is_all_quantities(*values: Any) -> bool:
    """
    Return True if every value is a Quantity instance.

    Returns False (rather than raising) when the units package is not installed.
    """
    if Quantity is None:
        return False
    return all(isinstance(v, Quantity) for v in values)


def is_all_numeric(*values: Any) -> bool:
    """Return True if all values are int or float."""
    return all(isinstance(v, (int, float)) for v in values)


def is_all_volume_quantities(*values: Any) -> bool:
    """
    Return True if every value is a Quantity with volume units.

    Returns False (rather than raising) when the units package is not installed.
    """
    if Quantity is None or Category is None:
        return False
    return all(
        isinstance(v, Quantity) and v.unit.category == Category.VOLUME
        for v in values
    )


def is_same_unit_and_value_base(*values: Any) -> bool:
    """
    Return True if all values are Quantities sharing the same units and value base.

    Returns False (rather than raising) when the units package is not installed,
    or when the first value is not a Quantity.
    """
    if Quantity is None:
        return False
    if not isinstance(values[0], Quantity):
        return False
    for i in range(1, len(values)):
        if (not isinstance(values[i], Quantity) or
                not values[i].is_same_unit_and_value_base(values[0])):
            return False
    return True
