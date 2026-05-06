"""Tests for the operations module."""
import pytest
from canteen.operations import PassiveOperations, factory, NAMED_OPERATIONS
from canteen.reservoir import BaseReservoir
from canteen.outlet import Outlets, factory as outlet_factory, ReleaseRange

class TestPassiveOperationsBasic:
    """Test basic PassiveOperations functionality without outlets."""

    def test_passive_operations_no_overflow(self):
        """Test passive operations when storage + inflow is below capacity."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=20)

        # storage (50) + inflow (20) = 70, below capacity (100), so spill = 0
        assert result == (0.0,)

    def test_passive_operations_exact_capacity(self):
        """Test passive operations when storage + inflow equals capacity."""
        reservoir = BaseReservoir(
            name="Test", storage=80, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=20)

        # storage (80) + inflow (20) = 100, exactly at capacity, no spill
        assert result == (0.0,)

    def test_passive_operations_overflow(self):
        """Test passive operations when storage + inflow exceeds capacity."""
        reservoir = BaseReservoir(
            name="Test", storage=90, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=30)

        # storage (90) + inflow (30) = 120, exceeds capacity by 20
        assert result == (20.0,)

    def test_passive_operations_zero_inflow(self):
        """Test passive operations with zero inflow."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=0)

        assert result == (0.0,)

    def test_passive_operations_negative_inflow(self):
        """Test passive operations with negative inflow (evaporation/seepage)."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=-10)

        # storage (50) + inflow (-10) = 40, below capacity, no spill
        assert result == (0.0,)

class TestPassiveOperationsWithOutlets:
    """Test PassiveOperations with outlet integration."""

    def test_single_outlet_below_capacity(self):
        """Test single outlet when active storage is below capacity after release."""
        outlet = outlet_factory(name="spillway", location=50.0,
                               design_range=ReleaseRange(0, 20))
        reservoir = BaseReservoir(
            name="Test", storage=60, capacity=100,
            outlets=Outlets([outlet]),
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=10)

        # active_storage = 60 + 10 = 70
        # outlet releases max(20) -> active_storage = 50
        # remaining 50 < capacity (100), so spill = 0
        assert result == (20, 0.0)
        assert len(result) == 2  # (outlet_release, spill)

    def test_single_outlet_exceeds_capacity_after_release(self):
        """Test single outlet when active storage exceeds capacity after outlet release."""
        outlet = outlet_factory(name="spillway", location=50.0,
                               design_range=ReleaseRange(0, 10))
        reservoir = BaseReservoir(
            name="Test", storage=80, capacity=100,
            outlets=Outlets([outlet]),
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=35)

        # active_storage = 80 + 35 = 115
        # outlet releases max(10) -> active_storage = 105
        # remaining 105 > capacity (100), so spill = 5
        assert result == (10, 5.0)

    def test_multiple_outlets_sequential_release(self):
        """Test that multiple outlets release sequentially, updating active storage."""
        outlet1 = outlet_factory(name="outlet1", location=30.0,
                                design_range=ReleaseRange(0, 15))
        outlet2 = outlet_factory(name="outlet2", location=60.0,
                                design_range=ReleaseRange(0, 10))
        reservoir = BaseReservoir(
            name="Test", storage=70, capacity=100,
            outlets=Outlets([outlet1, outlet2]),
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=20)

        # active_storage = 70 + 20 = 90
        # First outlet (sorted by location) releases, then second, etc.
        # Result should be tuple of (outlet1_release, outlet2_release, spill)
        assert len(result) == 3
        assert isinstance(result, tuple)
        assert result == (10, 15, 0.0)  # outlet1 releases 15, outlet2 releases 10, no spill

    def test_outlet_above_active_storage_no_release(self):
        """Test that outlet at higher location than active storage releases nothing."""
        outlet = outlet_factory(name="spillway", location=80.0,
                               design_range=ReleaseRange(0, 50))
        reservoir = BaseReservoir(
            name="Test", storage=30, capacity=100,
            outlets=Outlets([outlet]),
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=10)

        # active_storage = 30 + 10 = 40
        # outlet location (80) > active_storage (40), so no release from outlet
        # The outlet.operations() should return ReleaseRange(0, 0)
        assert result == (0, 0.0)  # No outlet release, no spill


class TestPassiveOperationsAlwaysTuple:
    """Test that PassiveOperations always returns a tuple regardless of outlet configuration."""

    def test_no_outlets_returns_single_element_tuple(self):
        """Test that operate() with no outlets returns a one-element spill tuple."""
        reservoir = BaseReservoir(
            name="Test", storage=90, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=30)

        # storage (90) + inflow (30) = 120, exceeds capacity by 20
        assert isinstance(result, tuple)
        assert len(result) == 1
        assert result == (20.0,)

    def test_with_outlets_always_returns_tuple(self):
        """Test that operate() with outlets always returns a tuple."""
        outlet = outlet_factory(name="spillway", location=50.0,
                               design_range=ReleaseRange(0, 20))
        reservoir = BaseReservoir(
            name="Test", storage=90, capacity=100,
            outlets=Outlets([outlet]),
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=30)

        assert isinstance(result, tuple)
        assert len(result) == 2  # (outlet_release, spill)
        assert result == (20, 0.0)

class TestPassiveOperationsOutputLabels:
    """Test output_labels method of PassiveOperations."""

    def test_output_labels_no_outlets(self):
        """Test output labels for reservoir without outlets."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )

        labels = reservoir.operations.output_labels(reservoir)

        assert labels == ("Spill",)

    def test_output_labels_with_outlets(self):
        """Test output labels for reservoir with outlets."""
        outlet1 = outlet_factory(name="low_level", location=30.0)
        outlet2 = outlet_factory(name="spillway", location=80.0)
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            outlets=Outlets([outlet1, outlet2]),
            operations=PassiveOperations()
        )

        labels = reservoir.operations.output_labels(reservoir)

        # Should include outlet names followed by Spill
        assert len(labels) == 3
        assert labels[-1] == "Spill"
        assert "low_level" in labels
        assert "spillway" in labels



class TestOperationsFactory:
    """Test the operations factory function."""

    def test_factory_default_creates_passive_operations(self):
        """Test that factory with no args creates PassiveOperations."""
        ops = factory()

        assert isinstance(ops, PassiveOperations)

    def test_factory_with_passive_string_creates_passive_operations(self):
        """Test that factory('Passive') creates PassiveOperations."""
        ops = factory("Passive")

        assert isinstance(ops, PassiveOperations)

    def test_factory_case_insensitive(self):
        """Test that factory is case-insensitive."""
        ops_lower = factory("passive")
        ops_upper = factory("PASSIVE")
        ops_mixed = factory("PaSsIvE")

        assert isinstance(ops_lower, PassiveOperations)
        assert isinstance(ops_upper, PassiveOperations)
        assert isinstance(ops_mixed, PassiveOperations)

    def test_factory_unknown_operation_raises_key_error(self):
        """Test that factory raises KeyError for unknown operation type."""
        with pytest.raises(KeyError, match="Unknown operations strategy"):
            factory("UnknownOperationType")


class TestPassiveOperationsRepresentation:
    """Test PassiveOperations string representation."""

    def test_repr_shows_class_name(self):
        """Test that __repr__ shows PassiveOperations class name."""
        ops = PassiveOperations()

        repr_str = repr(ops)

        assert "PassiveOperations" in repr_str


class TestNamedOperationsRegistry:
    """Test the NAMED_OPERATIONS registry."""

    def test_named_operations_contains_passive(self):
        """Test that NAMED_OPERATIONS registry contains PASSIVE."""
        assert "PASSIVE" in NAMED_OPERATIONS
        assert NAMED_OPERATIONS["PASSIVE"] == PassiveOperations
