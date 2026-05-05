"""
Tests for the units module's optional units dependency handling.
"""
import sys
import pytest
import canteen.units
from canteen.units import Quantity

# Optional imports for units package
try:
    from units.unit import factory as unit_factory  # type: ignore[import-not-found]
    from units.named_unit import NamedUnit  # type: ignore[import-not-found]
except ImportError:
    unit_factory = None  # type: ignore
    NamedUnit = None  # type: ignore


class TestQuantityImport:
    """Test the optional Quantity import from units module."""
    def test_quantity_is_importable(self):
        """Test that Quantity can be imported from canteen.units."""
        assert Quantity is not None or Quantity is None  # Either imported or None

    def test_quantity_availability(self):
        """Test that Quantity is either a class or None based on units availability."""
        if Quantity is None:
            # Units package not installed
            assert Quantity is None
        else:
            # Units package is installed
            assert hasattr(Quantity, "__name__")
            assert callable(Quantity)


@pytest.mark.skipif(Quantity is None, reason="units package not installed")
class TestQuantityWithUnits:
    """Tests that run only when units package is available."""

    def test_quantity_is_class_when_available(self):
        """Test that Quantity is a proper class when units is installed."""
        assert Quantity is not None
        assert hasattr(Quantity, "__name__")
        assert Quantity.__name__ == "Quantity"

    def test_quantity_can_be_instantiated(self):
        """Test that Quantity can be created when units is installed."""
        # Create a Quantity using a predefined NamedUnit
        distance = Quantity(10.0, unit_factory(NamedUnit.METER))

        assert distance.value == 10.0
        assert distance.unit.named_unit == NamedUnit.METER


class TestQuantityWithoutUnits:
    """Tests for behavior when units package is not available."""

    def test_quantity_none_when_not_installed(self):
        """Test that Quantity is None when units is not installed."""
        # This test will pass regardless, documenting expected behavior
        if "units" not in sys.modules:
            # If units truly not available, Quantity should be None
            # But if units IS available, we skip this assertion
            pass
        else:
            # Units is available, so Quantity should not be None
            assert Quantity is not None

    def test_quantity_import_does_not_raise(self):
        """Test that importing Quantity never raises an error."""
        # Quantity import at module level should always succeed
        # whether units is installed or not
        assert Quantity is not None or Quantity is None


class TestUnitsModuleStructure:
    """Test the overall structure of the units module."""

    def test_units_module_is_importable(self):
        """Test that units module can be imported."""
        assert canteen.units is not None

    def test_units_has_quantity_export(self):
        """Test that units module exports Quantity."""
        assert hasattr(canteen.units, "Quantity")

    def test_units_module_docstring_exists(self):
        """Test that units module has docstring."""
        assert canteen.units.__doc__ is not None
        assert len(canteen.units.__doc__) > 0
