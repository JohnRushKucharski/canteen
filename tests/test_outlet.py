"""Tests for the outlet module."""

import pytest
from canteen.units import Quantity

# Skip tests that require Quantity if units is not installed
requires_units = pytest.mark.skipif(Quantity is None, reason="units package not installed")

try:
    from units.unit import factory as unit_factory  # type: ignore[import-not-found]
    from units.named_unit import NamedUnit  # type: ignore[import-not-found]
except ImportError:
    unit_factory = None  # type: ignore
    NamedUnit = None  # type: ignore

from canteen.outlet import (  # noqa: E402 # pylint: disable=wrong-import-position, ungrouped-imports
    BasicOutlet,
    Outlets,
    ReleaseRange,
    format_outlets,
    default_sorter,
    factory
)

class TestBasicOutletValidation:
    """Test BasicOutlet initialization and validation rules."""

    def test_negative_location_raises_error(self):
        """Test that negative location raises ValueError."""
        with pytest.raises(ValueError, match="Outlet location"):
            BasicOutlet(location=-10.0)

    def test_negative_design_min_raises_error(self):
        """Test that negative design minimum raises ValueError."""
        with pytest.raises(ValueError, match="ReleaseRange minimum"):
            BasicOutlet(design_range=ReleaseRange(-5, 100))

    def test_invalid_design_range_raises_error(self):
        """Test that max < min raises ValueError."""
        with pytest.raises(ValueError, match="ReleaseRange"):
            BasicOutlet(design_range=ReleaseRange(100, 50))


class TestBasicOutletOperations:
    """Test BasicOutlet operations method - most critical logic."""

    def test_operations_no_flow_when_below_location(self):
        """Test that outlet returns zero flow when fill state is below location."""
        outlet = BasicOutlet(location=50.0, design_range=ReleaseRange(0, 100))
        result = outlet.operations(fill_state=30.0)
        assert result == ReleaseRange(0, 0)

    def test_operations_no_flow_when_at_location(self):
        """Test that outlet returns zero flow when fill state equals location."""
        outlet = BasicOutlet(location=50.0, design_range=ReleaseRange(0, 100))
        result = outlet.operations(fill_state=50.0)
        assert result == ReleaseRange(0, 0)

    def test_operations_limited_by_available_head(self):
        """Test that max release is limited by available head when head < design max."""
        outlet = BasicOutlet(location=50.0, design_range=ReleaseRange(0, 100))
        # Fill state = 60, so available head = 10
        result = outlet.operations(fill_state=60.0)
        assert result == ReleaseRange(0, 10.0)  # Limited by head, not design max

    def test_operations_limited_by_design_max(self):
        """Test that max release is limited by design max when head > design max."""
        outlet = BasicOutlet(location=50.0, design_range=ReleaseRange(0, 20))
        # Fill state = 100, so available head = 50
        result = outlet.operations(fill_state=100.0)
        assert result == ReleaseRange(0, 20)  # Limited by design max

    def test_operations_min_limited_by_available_head(self):
        """Test that min release is limited by available head when head < design min."""
        outlet = BasicOutlet(location=50.0, design_range=ReleaseRange(30, 100))
        # Fill state = 55, so available head = 5
        result = outlet.operations(fill_state=55.0)
        assert result == ReleaseRange(5.0, 5.0)  # Both limited by head


class TestFormatOutlets:
    """Test format_outlets function - most error-prone logic."""

    def test_format_outlets_empty_names_get_default(self):
        """Test that outlets with empty names get 'outlet' as default name."""
        outlets = [
            BasicOutlet(location=10.0),
            BasicOutlet(location=20.0)
        ]
        formatted = format_outlets(outlets)
        assert formatted[0].name == "outlet@10.0"
        assert formatted[1].name == "outlet@20.0"

    def test_format_outlets_with_duplicates_at_same_location(self):
        """Test that duplicate names at same location get numbered."""
        outlets = [
            BasicOutlet(name="gate", location=10.0),
            BasicOutlet(name="gate", location=10.0),
            BasicOutlet(name="gate", location=10.0)
        ]
        formatted = format_outlets(outlets)
        assert "gate1@10.0" in [o.name for o in formatted]
        assert "gate2@10.0" in [o.name for o in formatted]
        assert "gate3@10.0" in [o.name for o in formatted]

    def test_format_outlets_invalid_name_with_multiple_at_symbols(self):
        """Test that names with multiple '@' symbols raise ValueError."""
        outlets = [BasicOutlet(name="gate@1@2", location=10.0)]
        with pytest.raises(ValueError, match="Invalid name"):
            format_outlets(outlets)

    def test_format_outlets_invalid_name_with_mismatched_location(self):
        """Test that pre-formatted names with wrong location raise ValueError."""
        outlets = [BasicOutlet(name="gate@99.0", location=10.0)]
        with pytest.raises(ValueError, match="Invalid name"):
            format_outlets(outlets)

    def test_format_outlets_does_not_modify_originals(self):
        """Test that format_outlets makes deep copy and doesn't modify originals."""
        original = BasicOutlet(name="", location=10.0)
        outlets = [original]
        formatted = format_outlets(outlets)
        # Original should still have empty name
        assert original.name == ""
        # Formatted should have new name (no @location suffix when name is unique)
        assert formatted[0].name == "outlet"


class TestDefaultSorter:
    """Test default_sorter function."""

    def test_sort_outlets_descending_by_location(self):
        """Test that outlets are sorted by location in descending order."""
        outlets = [
            BasicOutlet(name="low", location=10.0),
            BasicOutlet(name="high", location=50.0),
            BasicOutlet(name="mid", location=30.0)
        ]
        sorted_outlets = default_sorter(outlets)
        assert sorted_outlets[0].location == 50.0
        assert sorted_outlets[1].location == 30.0
        assert sorted_outlets[2].location == 10.0

    def test_sort_outlets_by_name_when_same_location(self):
        """Test that outlets with same location are sorted alphabetically by name."""
        outlets = [
            BasicOutlet(name="zebra", location=10.0),
            BasicOutlet(name="alpha", location=10.0),
            BasicOutlet(name="beta", location=10.0)
        ]
        sorted_outlets = default_sorter(outlets)
        assert sorted_outlets[0].name == "alpha"
        assert sorted_outlets[1].name == "beta"
        assert sorted_outlets[2].name == "zebra"


class TestOutletsContainer:
    """Test Outlets container iteration and Null Object construction."""

    def test_iterating_outlets_twice_yields_same_sequence(self):
        """Iterating Outlets a second time must produce the same sequence."""
        o1 = BasicOutlet(name="low", location=10.0)
        o2 = BasicOutlet(name="high", location=50.0)
        outlets = Outlets([o1, o2])

        first_pass = list(outlets)
        second_pass = list(outlets)

        assert first_pass == second_pass

    def test_nested_loop_over_outlets_produces_cartesian_product(self):
        """A nested loop over the same Outlets must not silently reset the outer loop."""
        o1 = BasicOutlet(name="a", location=10.0)
        o2 = BasicOutlet(name="b", location=20.0)
        outlets = Outlets([o1, o2])

        pairs = [(outer.name, inner.name) for outer in outlets for inner in outlets]

        assert len(pairs) == 4
        assert ("a", "a") in pairs
        assert ("a", "b") in pairs
        assert ("b", "a") in pairs
        assert ("b", "b") in pairs

    def test_outlets_empty_construction_is_valid(self):
        """Outlets() with no arguments must construct and iterate as an empty sequence."""
        outlets = Outlets()

        assert len(outlets) == 0
        assert not list(outlets)



class TestBasicOutletWithQuantities:
    """Test BasicOutlet with Quantity types for locations and fill states."""

    def test_quantity_location_validation(self):
        """Test that negative Quantity location raises ValueError."""
        negative_volume = Quantity(-10, unit_factory(NamedUnit.CUBIC_METER))
        with pytest.raises(ValueError, match="Outlet location cannot be negative"):
            BasicOutlet(location=negative_volume)

    def test_operations_with_quantity_no_flow_below_location(self):
        """Test that outlet returns zero flow when Quantity fill state is below location."""
        location = Quantity(50, unit_factory(NamedUnit.CUBIC_METER))
        outlet = BasicOutlet(
            location=location,
            design_range=ReleaseRange(0, 100)
        )

        fill_state = Quantity(30, unit_factory(NamedUnit.CUBIC_METER))
        result = outlet.operations(fill_state=fill_state)
        assert result == ReleaseRange(0, 0)

    def test_operations_with_quantity_limited_by_head(self):
        """Test that Quantity outlet returns flow limited by available head."""
        location = Quantity(50, unit_factory(NamedUnit.CUBIC_METER))
        outlet = BasicOutlet(
            location=location,
            design_range=ReleaseRange(0, 100)
        )

        # Fill state = 60m³, available head = 10m³
        fill_state = Quantity(60, unit_factory(NamedUnit.CUBIC_METER))
        result = outlet.operations(fill_state=fill_state)

        # With numeric design_range (0, 100) and Quantity over_gate of 10m³
        # min(0, 10m³) -> 0 (int)
        # min(10m³, 100) -> 10m³ (Quantity)
        assert result.min == 0
        assert isinstance(result.max, Quantity)
        assert result.max.value == 10
        assert result.max.unit.named_unit == NamedUnit.CUBIC_METER

    def test_operations_with_quantity_design_range(self):
        """Test outlet with Quantity design range."""
        location = Quantity(50, unit_factory(NamedUnit.CUBIC_METER))
        min_release = Quantity(5, unit_factory(NamedUnit.CUBIC_METER))
        max_release = Quantity(20, unit_factory(NamedUnit.CUBIC_METER))

        outlet = BasicOutlet(
            location=location,
            design_range=ReleaseRange(min_release, max_release)
        )

        # Large head available (100m³ - 50m³ = 50m³)
        fill_state = Quantity(100, unit_factory(NamedUnit.CUBIC_METER))
        result = outlet.operations(fill_state=fill_state)

        # Should be limited by design range, not physical head
        assert result.min == min_release
        assert result.max == max_release

    def test_sort_outlets_with_quantities(self):
        """Test that outlets with Quantity locations sort correctly."""
        outlets = [
            BasicOutlet(name="low", location=Quantity(10, unit_factory(NamedUnit.CUBIC_METER))),
            BasicOutlet(name="high", location=Quantity(50, unit_factory(NamedUnit.CUBIC_METER))),
            BasicOutlet(name="mid", location=Quantity(30, unit_factory(NamedUnit.CUBIC_METER)))
        ]

        sorted_outlets = default_sorter(outlets)
        assert sorted_outlets[0].location.value == 50
        assert sorted_outlets[1].location.value == 30
        assert sorted_outlets[2].location.value == 10

    def test_operations_mixed_float_location_quantity_fill_state(self):
        """Test operations with float location and Quantity fill state."""
        # Float location, Quantity fill state
        outlet = BasicOutlet(
            name="mixed_outlet",
            location=50.0,  # float
            design_range=ReleaseRange(0, 100)
        )

        fill_state = Quantity(75, unit_factory(NamedUnit.CUBIC_METER))
        result = outlet.operations(fill_state=fill_state)

        # over_gate = Quantity(75, m³) - 50.0 = Quantity(25, m³)
        # Should return Quantity results based on available head
        assert isinstance(result.max, Quantity)
        assert result.max.value == 25

    def test_factory_creates_outlet_with_quantity_parameters(self):
        """Test that factory function properly handles Quantity parameters."""
        location = Quantity(100, unit_factory(NamedUnit.CUBIC_METER))
        min_release = Quantity(10, unit_factory(NamedUnit.CUBIC_METER))
        max_release = Quantity(50, unit_factory(NamedUnit.CUBIC_METER))

        outlet = factory(
            name="quantity_outlet",
            location=location,
            design_range=ReleaseRange(min_release, max_release)
        )

        assert outlet.name == "quantity_outlet"
        assert outlet.location == location
        assert outlet.design_range.min == min_release
        assert outlet.design_range.max == max_release

        # Verify it works in operations
        fill_state = Quantity(150, unit_factory(NamedUnit.CUBIC_METER))
        result = outlet.operations(fill_state)
        assert result.max == max_release  # Limited by design range

    def test_quantity_design_range_validation(self):
        """Test that validation works with Quantity design ranges."""
        location = Quantity(50, unit_factory(NamedUnit.CUBIC_METER))

        # Test negative design range minimum
        negative_min = Quantity(-5, unit_factory(NamedUnit.CUBIC_METER))
        with pytest.raises(ValueError, match="Design range minimum cannot be negative"):
            BasicOutlet(
                location=location,
                design_range=ReleaseRange(negative_min, 100)
            )

        # Test max < min with Quantities
        min_release = Quantity(50, unit_factory(NamedUnit.CUBIC_METER))
        max_release = Quantity(20, unit_factory(NamedUnit.CUBIC_METER))
        with pytest.raises(ValueError, match="Design range maximum cannot be less than minimum"):
            BasicOutlet(
                location=location,
                design_range=ReleaseRange(min_release, max_release)
            )
