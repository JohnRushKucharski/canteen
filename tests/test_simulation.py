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
