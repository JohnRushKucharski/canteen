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

    def test_freshly_constructed_reservoir_has_null_object_containers(self):
        """Freshly constructed reservoir has empty containers, never None (ADR-0003)."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)

        assert reservoir.mappings is not None
        assert isinstance(reservoir.mappings, Mappings)
        assert len(reservoir.mappings) == 0

        assert reservoir.pools is not None
        assert isinstance(reservoir.pools, Pools)
        assert len(reservoir.pools) == 0

        assert reservoir.outlets is not None
        assert isinstance(reservoir.outlets, Outlets)
        assert len(reservoir.outlets) == 0

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


class TestNullObjectDefaults:
    """Test that optional components default to empty containers, never None (ADR-0003)."""

    def test_reservoir_without_args_defaults_to_empty_containers(self):
        """BaseReservoir with no outlets/pools/mappings args defaults to empty containers."""
        reservoir = BaseReservoir(name="Minimal", storage=0, capacity=100)

        # Should be empty containers, not None
        assert reservoir.outlets is not None
        assert isinstance(reservoir.outlets, Outlets)
        assert len(reservoir.outlets) == 0

        assert reservoir.pools is not None
        assert isinstance(reservoir.pools, Pools)
        assert len(reservoir.pools) == 0

        assert reservoir.mappings is not None
        assert isinstance(reservoir.mappings, Mappings)
        assert len(reservoir.mappings) == 0

    def test_empty_outlets_are_iterable(self):
        """Empty Outlets container is iterable and produces zero iterations."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)

        count = 0
        for _ in reservoir.outlets:
            count += 1

        assert count == 0

    def test_empty_pools_are_iterable(self):
        """Empty Pools container is iterable and produces zero iterations."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)

        count = 0
        for _ in reservoir.pools:
            count += 1

        assert count == 0

    def test_passive_operations_work_with_empty_outlets(self):
        """PassiveOperations should work without defensive None checks on empty outlets."""
        reservoir = BaseReservoir(
            name="Test",
            storage=50,
            capacity=100,
            operations=PassiveOperations()
        )

        # Should return only spill, no None checks needed
        outflows = reservoir.operate(inflow=60)

        # storage (50) + inflow (60) = 110 > capacity (100), so spill = 10
        assert outflows == (10.0,)
        assert reservoir.storage == 100


class TestReservoirBuilder:
    """Test ReservoirBuilder pattern for construction (issue #19)."""

    def test_builder_fluent_api_accumulates_operations(self):
        """Builder accumulates operations via fluent interface."""
        from canteen.reservoir import ReservoirBuilder

        builder = ReservoirBuilder(name="Test", storage=50, capacity=100)
        result = builder.add_operations(PassiveOperations())

        assert result is builder  # Returns self for chaining

    def test_builder_fluent_api_accumulates_outlets(self):
        """Builder accumulates outlets via fluent interface."""
        from canteen.reservoir import ReservoirBuilder

        outlet = outlet_factory(name="spillway", location=80.0)
        outlets = Outlets([outlet])

        builder = ReservoirBuilder(name="Test", storage=50, capacity=100)
        result = builder.add_outlets(outlets)

        assert result is builder  # Returns self for chaining

    def test_builder_fluent_api_accumulates_pools(self):
        """Builder accumulates pools via fluent interface."""
        from canteen.reservoir import ReservoirBuilder

        pool = pool_factory(name="conservation", location=75.0)
        pools = Pools((pool,))

        builder = ReservoirBuilder(name="Test", storage=50, capacity=100)
        result = builder.add_pools(pools)

        assert result is builder  # Returns self for chaining

    def test_builder_fluent_api_accumulates_mappings(self):
        """Builder accumulates mappings via fluent interface."""
        from canteen.reservoir import ReservoirBuilder

        mapping = ratingcurve_factory(xs=[0, 100], ys=[0, 10])
        mappings = Mappings([mapping])

        builder = ReservoirBuilder(name="Test", storage=50, capacity=100)
        result = builder.add_mappings(mappings)

        assert result is builder  # Returns self for chaining

    def test_build_without_operations_raises_error(self):
        """Builder.build() raises ValueError when operations not set."""
        from canteen.reservoir import ReservoirBuilder

        builder = ReservoirBuilder(name="Test", storage=50, capacity=100)

        with pytest.raises(ValueError, match="Operations must be set"):
            builder.build()

    def test_build_with_operations_creates_reservoir(self):
        """Builder.build() creates BaseReservoir when operations set."""
        from canteen.reservoir import ReservoirBuilder

        builder = ReservoirBuilder(name="Test", storage=50, capacity=100)
        builder.add_operations(PassiveOperations())

        reservoir = builder.build()

        assert isinstance(reservoir, BaseReservoir)
        assert reservoir.name == "Test"
        assert reservoir.storage == 50
        assert reservoir.capacity == 100
        assert reservoir.operations is not None

    def test_build_creates_reservoir_with_all_components(self):
        """Builder.build() creates reservoir with all accumulated components."""
        from canteen.reservoir import ReservoirBuilder

        outlet = outlet_factory(name="spillway", location=80.0)
        outlets = Outlets([outlet])
        pool = pool_factory(name="conservation", location=75.0)
        pools = Pools((pool,))
        mapping = ratingcurve_factory(xs=[0, 100], ys=[0, 10])
        mappings = Mappings([mapping])

        builder = (ReservoirBuilder(name="Test", storage=50, capacity=100)
                   .add_operations(PassiveOperations())
                   .add_outlets(outlets)
                   .add_pools(pools)
                   .add_mappings(mappings))

        reservoir = builder.build()

        assert reservoir.outlets == outlets
        assert reservoir.pools == pools
        assert reservoir.mappings == mappings

    def test_factory_uses_builder_internally(self):
        """Factory function creates reservoir via builder pattern."""
        # Factory should set PassiveOperations by default if none provided
        reservoir = factory(name="Test", storage=50, capacity=100)

        assert isinstance(reservoir, BaseReservoir)
        assert reservoir.name == "Test"
        assert reservoir.storage == 50
        assert reservoir.capacity == 100
        assert reservoir.operations is not None
        assert isinstance(reservoir.operations, PassiveOperations)

    def test_factory_with_components_uses_builder(self):
        """Factory with components passes them through builder."""
        outlet = outlet_factory(name="spillway", location=80.0)
        outlets = Outlets([outlet])
        pool = pool_factory(name="conservation", location=75.0)
        pools = Pools((pool,))

        reservoir = factory(
            name="Test",
            storage=50,
            capacity=100,
            outlets=outlets,
            pools=pools
        )

        assert reservoir.outlets == outlets
        assert reservoir.pools == pools

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


class TestReservoirFreeze:
    """Test that structural fields are frozen after construction (ADR-0002)."""

    def test_direct_assignment_to_outlets_raises_after_construction(self):
        """Direct assignment to a structural field raises AttributeError."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        with pytest.raises(AttributeError):
            reservoir.outlets = Outlets()  # type: ignore[misc]

    def test_direct_assignment_to_pools_raises_after_construction(self):
        """Direct assignment to pools raises AttributeError."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        with pytest.raises(AttributeError):
            reservoir.pools = Pools()  # type: ignore[misc]

    def test_direct_assignment_to_mappings_raises_after_construction(self):
        """Direct assignment to mappings raises AttributeError."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        with pytest.raises(AttributeError):
            reservoir.mappings = Mappings()  # type: ignore[misc]

    def test_direct_assignment_to_capacity_raises_after_construction(self):
        """Direct assignment to capacity raises AttributeError."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        with pytest.raises(AttributeError):
            reservoir.capacity = 200  # type: ignore[misc]

    def test_storage_assignment_is_allowed(self):
        """Storage remains mutable after construction."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        reservoir.storage = 42
        assert reservoir.storage == 42

    def test_add_outlets_still_works_after_freeze(self):
        """add_outlets() is the sanctioned path and must work despite the freeze."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        outlet = outlet_factory(name="spillway", location=80.0)
        reservoir.add_outlets(Outlets([outlet]))
        assert len(reservoir.outlets) == 1

    def test_add_pools_still_works_after_freeze(self):
        """add_pools() is the sanctioned path and must work despite the freeze."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        pool = pool_factory(name="conservation", location=60.0)
        reservoir.add_pools(Pools((pool,)))
        assert len(reservoir.pools) == 1

    def test_add_maps_still_works_after_freeze(self):
        """add_maps() is the sanctioned path and must work despite the freeze."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        reservoir.add_maps(Mappings())
        assert isinstance(reservoir.mappings, Mappings)

    def test_add_operations_still_works_after_freeze(self):
        """add_operations() is the sanctioned path and must work despite the freeze."""
        reservoir = BaseReservoir(name="Test", storage=0, capacity=100)
        reservoir.add_operations(PassiveOperations())
        assert isinstance(reservoir.operations, PassiveOperations)


class TestReservoirStorageMutation:
    """Test that operate() advances storage correctly each timestep."""

    def test_operate_advances_storage_no_outlets(self):
        """operate() with no spill increments storage by inflow."""
        reservoir = BaseReservoir(
            name="Test", storage=50, capacity=100,
            operations=PassiveOperations()
        )
        reservoir.operate(inflow=20)
        assert reservoir.storage == 70

    def test_operate_advances_storage_with_spill(self):
        """operate() caps storage at capacity when inflow causes spill."""
        reservoir = BaseReservoir(
            name="Test", storage=90, capacity=100,
            operations=PassiveOperations()
        )
        reservoir.operate(inflow=20)
        assert reservoir.storage == 100

    def test_operate_returns_spill_tuple_no_outlets(self):
        """operate() returns a (spill,) tuple when no outlets are configured."""
        reservoir = BaseReservoir(
            name="Test", storage=90, capacity=100,
            operations=PassiveOperations()
        )
        result = reservoir.operate(inflow=20)
        # PassiveOperations always returns a tuple; (spill,) when no outlets
        assert result == (10.0,)

    def test_successive_operates_advance_storage(self):
        """Multiple successive operate() calls correctly advance storage."""
        reservoir = BaseReservoir(
            name="Test", storage=0, capacity=100,
            operations=PassiveOperations()
        )
        reservoir.operate(inflow=30)
        assert reservoir.storage == 30
        reservoir.operate(inflow=30)
        assert reservoir.storage == 60
        reservoir.operate(inflow=30)
        assert reservoir.storage == 90


class TestReservoirFactoryIndependence:
    """Test that factory() produces independent instances."""

    def test_factory_called_twice_returns_independent_operations(self):
        """factory() called twice returns reservoirs with independent operations instances."""
        r1 = factory()
        r2 = factory()
        assert r1.operations is not r2.operations
