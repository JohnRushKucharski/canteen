"""Tests for the pool module."""
import pytest
from canteen.pool import StaticPool, VariablePool, Pools, factory
from canteen.mapping import Mappings, constantmapping_factory, rulecurve_factory
from canteen.metadata import MetaDataPlusRange


class TestStaticPool:
    """Test StaticPool - critical validation and map handling."""

    def test_staticpool_raises_error_without_location_map(self):
        """Test that StaticPool raises ValueError when 'location' mapping is missing."""
        mappings = Mappings([constantmapping_factory(10.0, name="other")])
        info = MetaDataPlusRange(name="test", range_=(10.0, 10.0))

        with pytest.raises(ValueError, match="requires a 'location' mapping"):
            StaticPool(info=info, mappings=mappings)

    def test_staticpool_raises_error_with_negative_location(self):
        """Test that StaticPool raises ValueError when location is negative."""
        mappings = Mappings([constantmapping_factory(-5.0, name="location")])
        info = MetaDataPlusRange(name="test", range_=(-5.0, -5.0))

        with pytest.raises(ValueError, match="cannot be negative"):
            StaticPool(info=info, mappings=mappings)

    def test_staticpool_location_returns_constant_value(self):
        """Test that StaticPool.location() returns the constant location value."""
        mappings = Mappings([constantmapping_factory(42.5, name="location")])
        info = MetaDataPlusRange(name="test", range_=(42.5, 42.5))
        pool = StaticPool(info=info, mappings=mappings)

        assert pool.location() == 42.5
        assert pool.location(100) == 42.5  # Args ignored


class TestVariablePool:
    """Test VariablePool - complex validation and dynamic location."""

    def test_variablepool_raises_error_without_location_map(self):
        """Test that VariablePool raises ValueError when 'location' mapping is missing."""
        mappings = Mappings([rulecurve_factory([1, 365], [10.0, 20.0], name="other")])
        info = MetaDataPlusRange(name="test", range_=(10.0, 20.0))

        with pytest.raises(ValueError, match="requires a 'location' mapping"):
            VariablePool(info=info, mappings=mappings)

    def test_variablepool_raises_error_with_negative_range(self):
        """Test that VariablePool raises ValueError when location range contains negative values."""
        # Create rule curve with negative location
        mappings = Mappings([rulecurve_factory([1, 100, 365], [-10.0, 5.0, 10.0], name="location")])
        info = MetaDataPlusRange(name="test", range_=(-10.0, 10.0))

        with pytest.raises(ValueError, match="cannot be negative"):
            VariablePool(info=info, mappings=mappings)

    def test_variablepool_location_with_args(self):
        """Test that VariablePool.location() passes args to underlying map."""
        mappings = Mappings([rulecurve_factory([1, 100, 200, 365],
                                       [10.0, 20.0, 15.0, 10.0], name="location")])
        info = MetaDataPlusRange(name="test", range_=(10.0, 20.0))
        pool = VariablePool(info=info, mappings=mappings)

        # Test interpolation at different days
        assert pool.location(1) == 10.0
        assert pool.location(100) == 20.0
        # Day 50 is approximately halfway (note: interpolation may not be exactly linear)
        assert 14.8 < pool.location(50) < 15.2


class TestPools:
    """Test Pools container - critical for sorting and active pool logic."""

    def test_pools_sorts_by_descending_location(self):
        """Test that Pools automatically sorts pools from highest to lowest location."""
        pool1 = factory(name="low", location=10.0)
        pool2 = factory(name="high", location=100.0)
        pool3 = factory(name="mid", location=50.0)

        pools = Pools((pool1, pool2, pool3))

        assert pools.pools[0].info.name == "high"  # 100.0
        assert pools.pools[1].info.name == "mid"   # 50.0
        assert pools.pools[2].info.name == "low"   # 10.0

    def test_active_pool_raises_error_for_negative_volume(self):
        """Test that active_pool raises ValueError for negative volume."""
        pool = factory(name="test", location=10.0)
        pools = Pools((pool,))

        with pytest.raises(ValueError, match="cannot be negative"):
            pools.active_pool(-5.0)

    def test_active_pool_raises_error_for_volume_exceeding_top(self):
        """Test that active_pool raises ValueError when volume exceeds top pool."""
        pool1 = factory(name="bottom", location=10.0)
        pool2 = factory(name="top", location=50.0)
        pools = Pools((pool1, pool2))

        with pytest.raises(ValueError, match="cannot exceed"):
            pools.active_pool(60.0)

    def test_active_pool_returns_correct_pool_for_volume_in_dead_pool(self):
        """Test that active_pool correctly identifies volume in dead pool."""
        dead = factory(name="dead", location=10.0)
        conservation = factory(name="conservation", location=50.0)
        flood = factory(name="flood", location=100.0)
        pools = Pools((dead, conservation, flood))

        result = pools.active_pool(5.0)
        assert result.info.name == "dead"

    def test_active_pool_returns_correct_pool_for_volume_in_conservation_pool(self):
        """Test that active_pool correctly identifies volume in conservation pool."""
        dead = factory(name="dead", location=10.0)
        conservation = factory(name="conservation", location=50.0)
        flood = factory(name="flood", location=100.0)
        pools = Pools((dead, conservation, flood))

        result = pools.active_pool(25.0)
        assert result.info.name == "conservation"

    def test_active_pool_returns_correct_pool_for_volume_in_flood_pool(self):
        """Test that active_pool correctly identifies volume in flood pool."""
        dead = factory(name="dead", location=10.0)
        conservation = factory(name="conservation", location=50.0)
        flood = factory(name="flood", location=100.0)
        pools = Pools((dead, conservation, flood))

        result = pools.active_pool(75.0)
        assert result.info.name == "flood"

    def test_active_pool_returns_correct_pool_for_volume_at_boundary(self):
        """Test that active_pool handles volume at exact pool boundary."""
        dead = factory(name="dead", location=10.0)
        conservation = factory(name="conservation", location=50.0)
        flood = factory(name="flood", location=100.0)
        pools = Pools((dead, conservation, flood))

        result = pools.active_pool(50.0)
        assert result.info.name == "conservation"


class TestFactory:
    """Tests for pool factory function."""

    def test_factory_with_none_location_and_no_maps_creates_variablepool(self):
        """Test that factory with location=None creates VariablePool with default rule curve."""
        pool = factory(name="test", location=None)

        assert isinstance(pool, VariablePool)
        # Default rule curve should have location at day 1
        assert pool.location(1) == 1.0

    def test_factory_raises_error_when_location_map_already_exists(self):
        """Test that factory raises ValueError when location mapping already exists in maps."""
        mappings = Mappings([constantmapping_factory(10.0, name="location")])

        with pytest.raises(ValueError, match="location mapping already exists"):
            factory(name="test", location=5.0, mappings=mappings)

    def test_factory_with_numeric_location_creates_staticpool(self):
        """Test that factory with numeric location creates StaticPool."""
        pool = factory(name="test", location=25.0)

        assert isinstance(pool, StaticPool)
        assert pool.location() == 25.0
        assert pool.info.name == "test"

    def test_factory_with_none_location_and_custom_maps_creates_variablepool(self):
        """Test that factory with location=None and custom maps creates VariablePool."""
        custom_map = rulecurve_factory([1, 100, 365], [5.0, 15.0, 5.0], name="location")
        mappings = Mappings([custom_map])
        pool = factory(name="seasonal", location=None, mappings=mappings)

        assert isinstance(pool, VariablePool)
        assert pool.location(1) == 5.0
        assert pool.location(100) == 15.0


class TestPoolsContainerMethods:
    """Test Pools container iteration and indexing methods."""

    def test_pools_iteration_yields_pools_in_descending_order(self):
        """Test that iterating over Pools yields pools from highest to lowest location."""
        pool1 = factory(name="low", location=10.0)
        pool2 = factory(name="high", location=100.0)
        pool3 = factory(name="mid", location=50.0)
        pools = Pools((pool1, pool2, pool3))
        names = [pool.info.name for pool in pools]
        assert names == ["high", "mid", "low"]

    def test_pools_len_returns_correct_count(self):
        """Test that len(pools) returns the correct number of pools."""
        pool1 = factory(name="pool1", location=10.0)
        pool2 = factory(name="pool2", location=20.0)
        pools = Pools((pool1, pool2))

        assert len(pools) == 2

    def test_pools_getitem_returns_pool_at_index(self):
        """Test that pools[index] returns the correct pool."""
        pool1 = factory(name="bottom", location=10.0)
        pool2 = factory(name="top", location=50.0)
        pools = Pools((pool1, pool2))

        assert pools[0].info.name == "top"  # Highest location
        assert pools[1].info.name == "bottom"  # Lowest location


class TestPoolRepresentations:
    """Test string representations of pool objects."""

    def test_staticpool_repr_shows_name_and_location(self):
        """Test that StaticPool.__repr__ includes name and location."""
        pool = factory(name="dead_pool", location=15.5)

        repr_str = repr(pool)
        assert "StaticPool" in repr_str
        assert "dead_pool" in repr_str
        assert "15.5" in repr_str

    def test_variablepool_repr_shows_name_and_range(self):
        """Test that VariablePool.__repr__ includes name and location range."""
        mappings = Mappings([rulecurve_factory([1, 365], [10.0, 50.0], name="location")])
        pool = factory(name="conservation", location=None, mappings=mappings)

        repr_str = repr(pool)
        assert "VariablePool" in repr_str
        assert "conservation" in repr_str
        assert "10.0" in repr_str or "50.0" in repr_str  # Range values should appear
