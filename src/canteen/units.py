'''
Optional units dependency re-export module for canteen.

This module provides a central location for importing from the optional units package.
All modules should import units-related items from here, not directly from units.

Available when units is installed:
- Quantity: Main quantity class
- NamedUnit: Enumeration of named units
- Unit: Unit class
- unit_factory: Factory function for creating units
- And all other units package top-level exports

Usage:
------
>>> from canteen.units import Quantity, NamedUnit, unit_factory
>>> if Quantity is not None:
...     # Use units functionality
...     q = Quantity(10, unit_factory(NamedUnit.METER))
'''
from typing import TYPE_CHECKING

# Optional dependency on units package
# Re-export the units API for convenience
if TYPE_CHECKING:
    # At type-check time, import what we need for type hints
    try:
        from units import Quantity  # type: ignore[import-not-found]
        from units import Unit  # type: ignore[import-not-found]
        from units import unit_factory  # type: ignore[import-not-found]
        from units.named_unit import NamedUnit, Category  # type: ignore[import-not-found]
    except ImportError:
        # Provide minimal type stubs when units is not installed
        class Quantity:  # type: ignore
            """Type stub for units.Quantity when package is not installed."""
        class NamedUnit:  # type: ignore
            """Type stub for units.NamedUnit when package is not installed."""
        class Category:  # type: ignore
            """Type stub for units.Category when package is not installed."""
        class Unit:  # type: ignore
            """Type stub for units.Unit when package is not installed."""
        unit_factory = None  # type: ignore

else:
    # At runtime, try to import from units package
    try:
        # Import commonly used items explicitly
        from units import Quantity
        from units import Unit
        from units import unit_factory
        from units.named_unit import NamedUnit, Category

        # Make all other units top-level exports available
        # This allows: from canteen.units import <anything>
        try:
            from units import *  # noqa: F401, F403 # pylint: disable=wildcard-import, unused-wildcard-import
        except ImportError:
            pass

    except ImportError:
        # Units package not installed - set everything to None
        Quantity = None  # type: ignore
        NamedUnit = None  # type: ignore
        Category = None  # type: ignore
        Unit = None  # type: ignore
        unit_factory = None  # type: ignore

# Explicit exports for clarity
__all__ = ['Quantity', 'NamedUnit', 'Category', 'Unit', 'unit_factory']
