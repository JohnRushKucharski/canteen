"""Tests for the updated factory and builder pattern API."""

import pytest

from canteen import (
    operations, reservoir, outlet, pool,
    BaseReservoir, Outlets, Pools, factory
)
from canteen.operations import PassiveOperations


class TestFactoryPatternAPI:
    """Test the factory pattern API for creating reservoirs."""

    def test_basic_reservoir_factory(self):
        """Test creating a basic reservoir with factory."""
        res = reservoir.factory(name="Test Dam", storage=50.0, capacity=100.0)

        assert res.name == "Test Dam"
        assert res.storage == 50.0
        assert res.capacity == 100.0
        assert isinstance(res.operations, PassiveOperations)  # Default operations

    def test_reservoir_factory_with_operations(self):
        """Test creating reservoir with operations via factory."""
        ops = operations.factory()
        res = reservoir.factory(
            name="Dam with Ops",
            storage=25.0,
            capacity=100.0,
            operations=ops
        )

        assert res.operations is ops
        assert isinstance(res.operations, PassiveOperations)

    def test_reservoir_factory_with_outlets(self):
        """Test creating reservoir with outlets via factory."""
        outlets_tuple = Outlets((
            outlet.factory(name="Spillway", location=95.0),
            outlet.factory(name="Gate", location=80.0)
        ))
        res = reservoir.factory(
            name="Dam with Outlets",
            storage=50.0,
            capacity=100.0,
            outlets=outlets_tuple
        )

        assert res.outlets is outlets_tuple
        assert len(res.outlets) == 2
        assert res.outlets[0].name == "Spillway"
        assert res.outlets[1].name == "Gate"

    def test_reservoir_factory_complete(self):
        """Test creating fully configured reservoir via factory."""
        ops = operations.factory()
        outlets_tuple = Outlets((outlet.factory(name="Main", location=90.0),))
        pools_tuple = Pools((
            pool.factory(name="Flood", location=95.0),
            pool.factory(name="Conservation", location=85.0)
        ))

        res = reservoir.factory(
            name="Complete Dam",
            storage=50.0,
            capacity=100.0,
            operations=ops,
            outlets=outlets_tuple,
            pools=pools_tuple
        )

        assert res.name == "Complete Dam"
        assert res.operations is ops
        assert res.outlets is outlets_tuple
        assert res.pools is pools_tuple

class TestBuilderPatternAPI:
    """Test the builder pattern API for incremental construction."""

    def test_builder_incremental_construction(self):
        """Test step-by-step builder pattern."""
        # Create base reservoir
        res = BaseReservoir(name="Builder Dam", storage=50.0, capacity=100.0)
        assert res.operations is None
        assert res.outlets is None

        # Add operations
        res.add_operations(operations.factory())
        assert res.operations is not None

        # Add outlets
        res.add_outlets(Outlets((outlet.factory(name="Gate", location=80.0),)))
        assert res.outlets is not None
        assert len(res.outlets) == 1

    def test_builder_chained_construction(self):
        """Test fluent chained builder pattern."""
        res = (BaseReservoir(name="Chained Dam", storage=50.0, capacity=100.0)
            .add_operations(operations.factory())
            .add_outlets(Outlets((outlet.factory(name="Spillway", location=95.0),)))
            .add_pools(Pools((pool.factory(name="Storage", location=90.0),))))

        assert res.name == "Chained Dam"
        assert res.operations is not None
        assert res.outlets is not None
        assert res.pools is not None

    def test_builder_prevents_duplicate_operations(self):
        """Test that builder prevents adding operations twice."""
        res = BaseReservoir(name="Test", storage=50.0, capacity=100.0)
        res.add_operations(operations.factory())

        with pytest.raises(ValueError, match="Operations already defined"):
            res.add_operations(operations.factory())

    def test_builder_prevents_duplicate_outlets(self):
        """Test that builder prevents adding outlets twice."""
        res = BaseReservoir(name="Test", storage=50.0, capacity=100.0)
        res.add_outlets(Outlets((outlet.factory(name="Gate", location=80.0),)))

        with pytest.raises(ValueError, match="Outlets already defined"):
            res.add_outlets(Outlets((outlet.factory(name="Other", location=70.0),)))

class TestModuleFactories:
    """Test individual module factory functions."""

    def test_operations_factory(self):
        """Test operations.factory() creates PassiveOperations."""
        ops = operations.factory()
        assert isinstance(ops, PassiveOperations)

    def test_top_level_factory(self):
        """Test top-level factory() creates operations."""
        ops = factory()
        assert isinstance(ops, PassiveOperations)

class TestDocstringExamples:
    """Test all examples from module docstrings."""

    def test_basic_usage_example(self):
        """Test the Basic Usage example from __init__.py docstring."""
        # Create components using module factory functions

        # Create operations
        ops = operations.factory()  # Default passive operations

        # Create outlets
        spillway = outlet.factory(name="Spillway", location=95.0)
        gate = outlet.factory(name="Gate", location=80.0)

        # Create reservoir with components
        res = reservoir.factory(
            name="My Reservoir",
            storage=75.0,
            capacity=150.0,
            operations=ops,
            outlets=outlet.Outlets((spillway, gate))
        )

        # Verify creation
        assert res.name == "My Reservoir"
        assert res.storage == 75.0
        assert res.capacity == 150.0
        assert res.operations is ops
        assert len(res.outlets) == 2

        # Operate the reservoir
        spill = res.operate(inflow=50.0)
        assert spill is not None

    def test_builder_pattern_chained_example(self):
        """Test chained builder pattern from __init__.py docstring."""
        # Create base reservoir
        res = BaseReservoir(name="Dam", storage=50.0, capacity=100.0)

        # Add components using builder methods (chainable)
        res.add_operations(operations.factory()) \
           .add_outlets(Outlets((
               outlet.factory(name="Spillway", location=95.0),
               outlet.factory(name="Gate", location=80.0)
           ))) \
           .add_pools(Pools((
               pool.factory(name="Flood", location=95.0),
               pool.factory(name="Conservation", location=85.0)
           )))

        assert res.name == "Dam"
        assert res.operations is not None
        assert len(res.outlets) == 2
        assert len(res.pools.pools) == 2

        # Operate after building
        spill = res.operate(inflow=30.0)
        assert spill is not None

    def test_builder_pattern_stepwise_example(self):
        """Test step-by-step builder pattern from __init__.py docstring."""
        # Or add components step by step
        res2 = BaseReservoir(name="Another Dam", storage=25.0, capacity=50.0)
        res2.add_operations(operations.factory())
        res2.add_outlets(Outlets((outlet.factory(name="Outlet", location=45.0),)))

        assert res2.name == "Another Dam"
        assert res2.operations is not None
        assert len(res2.outlets) == 1
        assert res2.outlets[0].name == "Outlet"

    def test_pool_factory_static_example(self):
        """Test static pool example from pool.factory docstring."""
        # Static pool at location 10.0
        p = pool.factory(name="Static Pool", location=10.0)
        assert p.info.name == "Static Pool"
        assert p.location() == 10.0

    def test_pool_factory_variable_example(self):
        """Test variable pool example from pool.factory docstring."""
        # Variable pool with default rule curve
        p = pool.factory(name="Variable Pool", location=None)
        assert p.info.name == "Variable Pool"
        # Should have a location function (requires day argument)
        loc = p.location(1)  # day 1 of water year
        assert loc is not None
        assert isinstance(loc, (int, float))

    def test_outlet_factory_basic_example(self):
        """Test basic outlet factory examples from outlet.factory docstring."""
        # Creates outlet
        out1 = outlet.factory()
        assert out1 is not None

        # Creates named outlet at location
        out2 = outlet.factory(name="Spillway", location=100.0)
        assert out2.name == "Spillway"
        assert out2.location == 100.0

    def test_operations_factory_named_example(self):
        """Test named operations factory example from operations.factory docstring."""
        # ops = factory("Passive")
        ops = operations.factory("Passive")
        assert isinstance(ops, PassiveOperations)
