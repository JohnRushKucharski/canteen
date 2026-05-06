"""Tests for the reservoir module."""
import pytest
from canteen.reservoir import BaseReservoir, factory
from canteen.pool import Pools, factory as pool_factory
from canteen.outlet import Outlets, factory as outlet_factory
from canteen.operations import PassiveOperations
from canteen.mapping import Mappings, ratingcurve_factory


class TestBaseReservoirInitialization:
    """Test BaseReservoir initialization and validation."""

    def test_valid_reservoir_creation(self):
        """Test that a reservoir is created with valid parameters."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)

        assert reservoir.name == "Test"
        assert reservoir.storage == 50
        assert reservoir.capacity == 100
        assert reservoir.operations is None
        assert reservoir.mappings is None
        assert reservoir.pools is None
        assert reservoir.outlets is None

    def test_storage_exceeds_capacity_raises_error(self):
        """Test that storage greater than capacity raises ValueError."""
        with pytest.raises(ValueError, match="capacity.*must be greater than storage"):
            BaseReservoir(name="Invalid", storage=150, capacity=100)

    def test_negative_storage_raises_error(self):
        """Test that negative storage raises ValueError."""
        with pytest.raises(ValueError, match="storage.*cannot be negative"):
            BaseReservoir(name="Invalid", storage=-10, capacity=100)

    def test_storage_at_capacity_boundary(self):
        """Test that storage exactly at capacity is valid."""
        reservoir = BaseReservoir(name="Full", storage=100, capacity=100)
        assert reservoir.storage == 100

    def test_zero_storage_is_valid(self):
        """Test that zero storage is valid."""
        reservoir = BaseReservoir(name="Empty", storage=0, capacity=100)
        assert reservoir.storage == 0


class TestReservoirWithPools:
    """Test reservoir interaction with pools."""

    def test_pool_top_exceeds_capacity_raises_error(self):
        """Test that pool with top of storage above capacity raises ValueError."""
        pool1 = pool_factory(name="conservation", location=50.0)
        pool2 = pool_factory(name="flood", location=150.0)  # Exceeds capacity
        pools = Pools((pool1, pool2))

        with pytest.raises(ValueError, match="Invalid pool location"):
            BaseReservoir(name="Test", storage=25, capacity=100, pools=pools)

    def test_pool_at_capacity_boundary_is_valid(self):
        """Test that pool with top of storage exactly at capacity is valid."""
        pool1 = pool_factory(name="conservation", location=50.0)
        pool2 = pool_factory(name="flood", location=100.0)  # Exactly at capacity
        pools = Pools((pool1, pool2))

        reservoir = BaseReservoir(name="Test", storage=25, capacity=100, pools=pools)
        assert reservoir.pools is not None
        assert len(reservoir.pools) == 2

    def test_add_pools_to_existing_reservoir(self):
        """Test adding pools to reservoir after creation."""
        reservoir = BaseReservoir(name="Test", storage=25, capacity=100)
        pool = pool_factory(name="conservation", location=50.0)
        pools = Pools((pool,))

        result = reservoir.add_pools(pools)
        assert result.pools == pools
        assert result is reservoir  # Returns self for chaining

    def test_add_pools_twice_raises_error(self):
        """Test that adding pools twice raises ValueError."""
        reservoir = BaseReservoir(name="Test", storage=25, capacity=100)
        pool = pool_factory(name="conservation", location=50.0)
        pools = Pools((pool,))

        reservoir.add_pools(pools)
        with pytest.raises(ValueError, match="Pools already defined"):
            reservoir.add_pools(pools)

    def test_add_pools_exceeding_capacity_raises_error(self):
        """Test that adding pools exceeding capacity raises ValueError."""
        reservoir = BaseReservoir(name="Test", storage=25, capacity=100)
        pool = pool_factory(name="flood", location=150.0)
        pools = Pools((pool,))

        with pytest.raises(ValueError, match="Invalid pool location"):
            reservoir.add_pools(pools)


class TestReservoirWithOutlets:
    """Test reservoir interaction with outlets."""

    def test_outlet_above_capacity_raises_error(self):
        """Test that outlet location above capacity raises ValueError."""
        outlet = outlet_factory(name="spillway", location=150.0)
        outlets = Outlets([outlet])

        with pytest.raises(ValueError, match="Invalid outlet location"):
            BaseReservoir(name="Test", storage=25, capacity=100, outlets=outlets)

    def test_outlet_at_capacity_boundary_is_valid(self):
        """Test that outlet at capacity is valid."""
        outlet = outlet_factory(name="spillway", location=100.0)
        outlets = Outlets([outlet])

        reservoir = BaseReservoir(name="Test", storage=25, capacity=100, outlets=outlets)
        assert reservoir.outlets is not None
        assert len(reservoir.outlets) == 1

    def test_add_outlets_to_existing_reservoir(self):
        """Test adding outlets to reservoir after creation."""
        reservoir = BaseReservoir(name="Test", storage=25, capacity=100)
        outlet = outlet_factory(name="spillway", location=80.0)
        outlets = Outlets([outlet])

        result = reservoir.add_outlets(outlets)
        assert result.outlets == outlets
        assert result is reservoir  # Returns self for chaining

    def test_add_outlets_twice_raises_error(self):
        """Test that adding outlets twice raises ValueError."""
        reservoir = BaseReservoir(name="Test", storage=25, capacity=100)
        outlet = outlet_factory(name="spillway", location=80.0)
        outlets = Outlets([outlet])

        reservoir.add_outlets(outlets)
        with pytest.raises(ValueError, match="Outlets already defined"):
            reservoir.add_outlets(outlets)

    def test_multiple_outlets_one_exceeds_capacity_raises_error(self):
        """Test that if any outlet exceeds capacity, error is raised."""
        outlet1 = outlet_factory(name="low_level", location=50.0)
        outlet2 = outlet_factory(name="spillway", location=120.0)  # Exceeds capacity
        outlets = Outlets([outlet1, outlet2])

        with pytest.raises(ValueError, match="Invalid outlet location"):
            BaseReservoir(name="Test", storage=25, capacity=100, outlets=outlets)


class TestReservoirOperations:
    """Test reservoir operations functionality."""

    def test_operate_without_operations_raises_error(self):
        """Test that calling operate without operations raises ValueError."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)

        with pytest.raises(ValueError, match="No operations defined"):
            reservoir.operate(inflow=10)

    def test_add_operations_to_reservoir(self):
        """Test adding operations to reservoir."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)
        ops = PassiveOperations()

        result = reservoir.add_operations(ops)
        assert result.operations == ops
        assert result is reservoir  # Returns self for chaining

    def test_add_operations_twice_raises_error(self):
        """Test that adding operations twice raises ValueError."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)
        ops = PassiveOperations()

        reservoir.add_operations(ops)
        with pytest.raises(ValueError, match="Operations already defined"):
            reservoir.add_operations(ops)

    def test_operate_with_operations_executes_successfully(self):
        """Test that operate executes when operations are defined."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )

        result = reservoir.operate(inflow=10)
        # With passive operations and no outlets, should return (spill,) tuple
        # storage (50) + inflow (10) = 60, which is below capacity (100), so spill = 0
        assert result == (0.0,)


class TestReservoirMapsAndBuilder:
    """Test reservoir maps and builder pattern."""

    def test_add_maps_to_reservoir(self):
        """Test adding maps to reservoir."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)
        mappings = Mappings()

        result = reservoir.add_maps(mappings)
        assert result.mappings == mappings
        assert result is reservoir

    def test_add_maps_twice_raises_error(self):
        """Test that adding maps twice raises ValueError."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)
        map_ = ratingcurve_factory(name="test", xs=[0, 100], ys=[0, 1])
        mappings = Mappings([map_])

        reservoir.add_maps(mappings)
        with pytest.raises(ValueError, match="Mappings already defined"):
            reservoir.add_maps(mappings)

    def test_builder_pattern_chaining(self):
        """Test that builder methods can be chained."""
        reservoir = BaseReservoir(name="Test", storage=50, capacity=100)
        pool = pool_factory(name="conservation", location=60.0)
        outlet = outlet_factory(name="spillway", location=80.0)

        result = (reservoir
                  .add_pools(Pools((pool,)))
                  .add_outlets(Outlets([outlet]))
                  .add_operations(PassiveOperations())
                  .add_maps(Mappings()))

        assert result.pools is not None
        assert result.outlets is not None
        assert result.operations is not None
        assert result.mappings is not None


class TestReservoirFactory:
    """Test reservoir factory function."""

    def test_factory_creates_reservoir_with_defaults(self):
        """Test factory creates reservoir with default values."""
        reservoir = factory()

        assert reservoir.name == "reservoir"
        assert reservoir.storage == 0
        assert reservoir.capacity == 1
        assert isinstance(reservoir.operations, PassiveOperations)

    def test_factory_creates_reservoir_with_custom_values(self):
        """Test factory creates reservoir with custom values."""
        reservoir = factory(name="Custom", storage=75, capacity=150)

        assert reservoir.name == "Custom"
        assert reservoir.storage == 75
        assert reservoir.capacity == 150

    def test_factory_creates_reservoir_with_all_components(self):
        """Test factory creates reservoir with pools, outlets, and operations."""
        pool = pool_factory(name="conservation", location=80.0)
        outlet = outlet_factory(name="spillway", location=120.0)
        ops = PassiveOperations()

        reservoir = factory(
            name="Full", storage=50, capacity=150,
            pools=Pools((pool,)),
            outlets=Outlets([outlet]),
            operations=ops
        )

        assert reservoir.pools is not None
        assert reservoir.outlets is not None
        assert reservoir.operations == ops


class TestReservoirRepresentation:
    """Test reservoir string representation."""

    def test_repr_without_outlets(self):
        """Test __repr__ for reservoir without outlets."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )

        repr_str = repr(reservoir)
        assert "BaseReservoir" in repr_str
        assert "name='Test'" in repr_str
        assert "storage=50" in repr_str
        assert "capacity=100" in repr_str

    def test_repr_with_outlets(self):
        """Test __repr__ for reservoir with outlets."""
        outlet1 = outlet_factory(name="low_level", location=50.0)
        outlet2 = outlet_factory(name="spillway", location=80.0)
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            outlets=Outlets([outlet1, outlet2])
        )

        repr_str = repr(reservoir)
        assert "outlets=" in repr_str
        assert "low_level" in repr_str
        assert "spillway" in repr_str
