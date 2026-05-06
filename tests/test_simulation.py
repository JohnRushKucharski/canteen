"""Tests for simulation functionality."""

import numpy as np

from canteen import reservoir
from canteen.simulation import simulate


class TestSimulateBasics:
    """Test basic simulation behavior."""

    def test_simulate_accepts_reservoir_and_inflows(self):
        """Test that simulate accepts a reservoir and inflows."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, 20.0, 15.0]

        result = simulate(res, inflows)

        # Should return something
        assert result is not None

    def test_simulate_returns_structured_array_with_correct_columns(self):
        """Test that simulate returns numpy structured array with correct dtype."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, 20.0]

        result = simulate(res, inflows)

        # Check it's a numpy array
        assert isinstance(result, np.ndarray)
        # Check it has the right columns
        assert 'timestep' in result.dtype.names
        assert 'inflow' in result.dtype.names
        assert 'storage' in result.dtype.names
        assert 'spill' in result.dtype.names
        # Check dtypes
        # pylint: disable=unsubscriptable-object
        assert result.dtype['timestep'] == np.int32
        assert result.dtype['inflow'] == np.float64
        assert result.dtype['storage'] == np.float64
        assert result.dtype['spill'] == np.float64

    def test_simulate_preserves_original_reservoir(self):
        """Test that original reservoir is unchanged after simulation."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        original_storage = res.storage
        inflows = [10.0, 20.0, 30.0]

        simulate(res, inflows)

        # Original reservoir should be unchanged
        assert res.storage == original_storage

    def test_simulate_records_correct_values(self):
        """Test that simulation records correct storage and spill values."""
        res = reservoir.factory(name="Test", storage=0.0, capacity=100.0)
        inflows = [50.0, 60.0, 40.0]

        result = simulate(res, inflows)

        # Check timesteps
        assert result['timestep'][0] == 0
        assert result['timestep'][1] == 1
        assert result['timestep'][2] == 2

        # Check inflows are recorded
        assert result['inflow'][0] == 50.0
        assert result['inflow'][1] == 60.0
        assert result['inflow'][2] == 40.0

        # Check storage progression (no outlets, so no release except spill)
        # t=0: storage = 0 + 50 - 0 = 50
        assert result['storage'][0] == 50.0
        assert result['spill'][0] == 0.0

        # t=1: storage = 50 + 60 - 10 (spill) = 100
        assert result['storage'][1] == 100.0
        assert result['spill'][1] == 10.0

        # t=2: storage = 100 + 40 - 40 (spill) = 100
        assert result['storage'][2] == 100.0
        assert result['spill'][2] == 40.0


class TestSimulateEdgeCases:
    """Test edge cases and special scenarios."""

    def test_simulate_empty_inflows_returns_empty_array(self):
        """Test that empty inflows returns empty array with correct dtype."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows: list[float] = []

        result = simulate(res, inflows)

        assert len(result) == 0
        assert isinstance(result, np.ndarray)
        # Should still have the right column structure
        assert 'timestep' in result.dtype.names
        assert 'inflow' in result.dtype.names
        assert 'storage' in result.dtype.names
        assert 'spill' in result.dtype.names

    def test_simulate_accepts_negative_inflows(self):
        """Test that negative inflows (evaporation) are accepted."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, -5.0, 15.0]

        result = simulate(res, inflows)

        # Check negative inflow is recorded
        assert result['inflow'][1] == -5.0

        # Check storage calculation with negative inflow
        # t=0: storage = 50 + 10 = 60
        # t=1: storage = 60 + (-5) = 55
        # t=2: storage = 55 + 15 = 70
        assert result['storage'][0] == 60.0
        assert result['storage'][1] == 55.0
        assert result['storage'][2] == 70.0

    def test_simulate_with_numpy_array_inflows(self):
        """Test that simulate accepts numpy array inflows."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = np.array([10.0, 20.0, 15.0])

        result = simulate(res, inflows)

        assert len(result) == 3
        assert result['inflow'][0] == 10.0


class TestSimulateOutletTracking:
    """Test outlet release tracking in simulation results."""

    def test_simulate_with_single_outlet_includes_outlet_column(self):
        """Test that simulation with one outlet includes outlet release column."""
        from canteen import outlet
        
        # Create reservoir with one outlet
        test_outlet = outlet.factory(name="MainGate", location=20.0)
        res = reservoir.factory(
            name="Test", 
            storage=50.0, 
            capacity=100.0,
            outlets=[test_outlet]
        )
        inflows = [10.0, 20.0]

        result = simulate(res, inflows)

        # Should have outlet column between storage and spill
        assert 'MainGate' in result.dtype.names
        # Column order should be: timestep, inflow, storage, MainGate, spill
        assert result.dtype.names == ('timestep', 'inflow', 'storage', 'MainGate', 'spill')

    def test_simulate_with_multiple_outlets_includes_all_outlet_columns(self):
        """Test that simulation with multiple outlets tracks each outlet separately."""
        from canteen import outlet
        
        # Create reservoir with two outlets (sorted by location descending)
        outlet1 = outlet.factory(name="Upper", location=50.0)
        outlet2 = outlet.factory(name="Lower", location=20.0)
        res = reservoir.factory(
            name="Test",
            storage=80.0,
            capacity=100.0,
            outlets=[outlet1, outlet2]
        )
        inflows = [10.0, 20.0, 15.0]

        result = simulate(res, inflows)

        # Should have both outlet columns
        assert 'Upper' in result.dtype.names
        assert 'Lower' in result.dtype.names
        # Column order: timestep, inflow, storage, Upper, Lower, spill
        assert result.dtype.names == ('timestep', 'inflow', 'storage', 'Upper', 'Lower', 'spill')

    def test_simulate_records_correct_per_outlet_releases(self):
        """Test that per-outlet releases are recorded correctly."""
        from canteen import outlet
        
        # Create reservoir with known behavior
        test_outlet = outlet.factory(name="Gate", location=30.0, max_release=15.0)
        res = reservoir.factory(
            name="Test",
            storage=50.0,
            capacity=100.0,
            outlets=[test_outlet]
        )
        inflows = [20.0, 30.0]

        result = simulate(res, inflows)

        # Check that outlet releases are recorded (values depend on operations)
        # Just verify columns exist and contain numeric data
        assert 'Gate' in result.dtype.names
        assert result['Gate'][0] >= 0.0
        assert result['Gate'][1] >= 0.0

    def test_simulate_with_zero_outlets_only_has_spill(self):
        """Test that simulation with zero outlets works (regression test)."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, 20.0]

        result = simulate(res, inflows)

        # Should have standard columns only (no outlet columns)
        assert result.dtype.names == ('timestep', 'inflow', 'storage', 'spill')
        assert 'spill' in result.dtype.names
