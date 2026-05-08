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
        """Test that per-outlet releases are recorded with exact expected values."""
        from canteen import outlet
        from canteen.outlet import ReleaseRange

        # Reservoir: storage=50, capacity=100
        # Gate at location=30.0, max release=15.0
        test_outlet = outlet.factory(
            name="Gate",
            location=30.0,
            design_range=ReleaseRange(min=0.0, max=15.0)
        )
        res = reservoir.factory(
            name="Test",
            storage=50.0,
            capacity=100.0,
            outlets=[test_outlet]
        )
        inflows = [20.0, 30.0]

        result = simulate(res, inflows)

        # Timestep 0: active=50+20=70, over_gate=40, Gate releases min(40,15)=15
        #   storage = 50+20-15-0 = 55, spill = max(0, 55-100) = 0
        assert result['Gate'][0] == 15.0
        assert result['storage'][0] == 55.0
        assert result['spill'][0] == 0.0

        # Timestep 1: active=55+30=85, over_gate=55, Gate releases min(55,15)=15
        #   storage = 55+30-15-0 = 70, spill = max(0, 70-100) = 0
        assert result['Gate'][1] == 15.0
        assert result['storage'][1] == 70.0
        assert result['spill'][1] == 0.0

    def test_simulate_with_zero_outlets_only_has_spill(self):
        """Test that simulation with zero outlets works (regression test)."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, 20.0]

        result = simulate(res, inflows)

        # Should have standard columns only (no outlet columns)
        assert result.dtype.names == ('timestep', 'inflow', 'storage', 'spill')
        assert 'spill' in result.dtype.names

    def test_simulate_raises_on_outlet_name_collision_with_reserved_column(self):
        """Test that a ValueError is raised when an outlet name collides with reserved columns."""
        import pytest
        from canteen import outlet

        for reserved in ('timestep', 'inflow', 'storage', 'spill'):
            bad_outlet = outlet.factory(name=reserved, location=10.0)
            res = reservoir.factory(
                name="Test",
                storage=50.0,
                capacity=100.0,
                outlets=[bad_outlet]
            )
            with pytest.raises(ValueError, match="conflict with reserved simulation columns"):
                simulate(res, [10.0])


class TestSimulateValidation:
    """Test validation and error handling in simulation."""

    def test_simulate_raises_when_reservoir_has_no_operations(self):
        """Test that simulate raises ValueError when reservoir.operations is None."""
        import pytest
        from canteen.reservoir import BaseReservoir

        # Create reservoir without operations
        res = BaseReservoir(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, 20.0]

        with pytest.raises(ValueError, match="operations"):
            simulate(res, inflows)

    def test_simulate_raises_when_storage_goes_negative(self):
        """Test that simulate raises error when storage becomes negative."""
        import pytest

        # Create reservoir with starting storage that will go negative
        res = reservoir.factory(name="Test", storage=10.0, capacity=100.0)
        # Large negative inflow will cause storage to go negative
        inflows = [5.0, -20.0]  # After t=1: storage = 15 + (-20) = -5

        with pytest.raises(ValueError, match="storage|negative"):
            simulate(res, inflows)

    def test_simulate_raises_when_storage_exceeds_capacity(self):
        """Test that simulate raises error when storage exceeds capacity after operation."""
        import pytest
        from canteen.operations import Operations
        from canteen.reservoir import Reservoir, BaseReservoir

        # Create custom operations that fails to spill properly (buggy strategy)
        # pylint: disable=redefined-outer-name
        class BuggyOperations(Operations):
            """Operations that doesn't release or spill anything."""

            def operate(
                self,
                reservoir: Reservoir,
                inflow: float,
                *args,
                **kwargs,
            ) -> tuple[float, ...]:
                """Return zero outflows (buggy - doesn't spill)."""
                _ = (reservoir, inflow, args, kwargs)
                return (0.0,)  # No spill, will cause capacity overflow
        # pylint: enable=redefined-outer-name

        # Create reservoir with buggy operations directly
        res = BaseReservoir(
            name="Test",
            storage=95.0,
            capacity=100.0,
            operations=BuggyOperations()
        )
        inflows = [10.0]  # storage = 95 + 10 - 0 = 105 > capacity

        with pytest.raises(ValueError, match="capacity|exceeds"):
            simulate(res, inflows)

    def test_simulate_accepts_optional_timestamps_parameter(self):
        """Test that simulate accepts optional timestamps parameter."""
        res = reservoir.factory(name="Test", storage=50.0, capacity=100.0)
        inflows = [10.0, 20.0, 15.0]
        timestamps = ['2024-01-01', '2024-01-02', '2024-01-03']

        # Should not raise - timestamps parameter exists
        result = simulate(res, inflows, timestamps=timestamps)

        # Result should be returned successfully
        assert result is not None
        assert len(result) == 3


class TestSimulationDataFrameConverters:
    """Test structured-array to DataFrame converter helpers."""

    @staticmethod
    def _get_value(frame_payload, row_index, column_name):
        """Read values from fake row- or column-oriented frame payloads."""
        if 'rows' in frame_payload:
            return frame_payload['rows'][row_index][column_name]
        return frame_payload['columns'][column_name][row_index]

    def test_to_pandas_converts_structured_array_to_dataframe(self):
        """Test that to_pandas converts simulation result to pandas DataFrame."""
        from canteen.simulation import to_pandas
        import sys
        import types

        result = np.array(
            [(0, 10.0, 50.0, 0.0), (1, 20.0, 70.0, 0.0)],
            dtype=[
                ('timestep', np.int32),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('spill', np.float64),
            ],
        )

        def _dataframe(rows):
            """Return rows payload for assertion-friendly fake dataframe behavior."""
            return {'rows': rows}

        monkey_module = types.ModuleType("pandas")
        monkey_module.DataFrame = _dataframe
        old_pandas = sys.modules.get("pandas")
        sys.modules["pandas"] = monkey_module
        try:
            converted = to_pandas(result)
        finally:
            if old_pandas is None:
                del sys.modules["pandas"]
            else:
                sys.modules["pandas"] = old_pandas

        assert isinstance(converted, dict)
        assert len(converted['rows']) == 2
        assert converted['rows'][0]['timestep'] == 0
        assert converted['rows'][1]['storage'] == 70.0

    def test_to_polars_converts_structured_array_to_dataframe(self):
        """Test that to_polars converts simulation result to polars DataFrame."""
        from canteen.simulation import to_polars
        import sys
        import types

        result = np.array(
            [(0, 10.0, 50.0, 0.0), (1, 20.0, 70.0, 5.0)],
            dtype=[
                ('timestep', np.int32),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('spill', np.float64),
            ],
        )

        def _dataframe(columns):
            """Return columns payload for assertion-friendly fake dataframe behavior."""
            return {'columns': columns}

        monkey_module = types.ModuleType("polars")
        monkey_module.DataFrame = _dataframe
        old_polars = sys.modules.get("polars")
        sys.modules["polars"] = monkey_module
        try:
            converted = to_polars(result)
        finally:
            if old_polars is None:
                del sys.modules["polars"]
            else:
                sys.modules["polars"] = old_polars

        assert isinstance(converted, dict)
        assert len(converted['columns']['timestep']) == 2
        assert self._get_value(converted, 0, 'inflow') == 10.0
        assert self._get_value(converted, 1, 'spill') == 5.0

    def test_to_pandas_passes_structured_array_directly_to_dataframe(self):
        """Test that to_pandas passes the structured array directly to DataFrame()."""
        from canteen.simulation import to_pandas
        import sys
        import types

        result = np.array(
            [(0, 10.0, 50.0, 0.0)],
            dtype=[
                ('timestep', np.int32),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('spill', np.float64),
            ],
        )

        def _dataframe(data):
            """Capture the argument passed to DataFrame() for assertion."""
            return {'data': data}

        monkey_module = types.ModuleType("pandas")
        monkey_module.DataFrame = _dataframe
        old_pandas = sys.modules.get("pandas")
        sys.modules["pandas"] = monkey_module
        try:
            converted = to_pandas(result)
        finally:
            if old_pandas is None:
                del sys.modules["pandas"]
            else:
                sys.modules["pandas"] = old_pandas

        # Fake receives the raw structured array — not a row-dict list
        assert isinstance(converted['data'], np.ndarray)
        assert converted['data'].dtype.names == ('timestep', 'inflow', 'storage', 'spill')

    def test_converters_handle_results_with_outlet_columns_and_timestamps(self):
        """Test converter compatibility with richer simulation schemas."""
        from canteen.simulation import to_pandas, to_polars
        import sys
        import types

        result = np.array(
            [
                (0, np.datetime64('2026-01-01'), 10.0, 50.0, 2.0, 0.0),
                (1, np.datetime64('2026-01-02'), 20.0, 68.0, 3.0, 1.0),
            ],
            dtype=[
                ('timestep', np.int32),
                ('timestamp', 'datetime64[D]'),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('MainGate', np.float64),
                ('spill', np.float64),
            ],
        )

        def _pandas_dataframe(rows):
            """Return rows payload for assertion-friendly fake dataframe behavior."""
            return {'rows': rows}

        def _polars_dataframe(columns):
            """Return columns payload for assertion-friendly fake dataframe behavior."""
            return {'columns': columns}

        old_pandas = sys.modules.get("pandas")
        old_polars = sys.modules.get("polars")
        fake_pd = types.ModuleType("pandas")
        fake_pd.DataFrame = _pandas_dataframe
        fake_pl = types.ModuleType("polars")
        fake_pl.DataFrame = _polars_dataframe

        sys.modules["pandas"] = fake_pd
        sys.modules["polars"] = fake_pl
        try:
            pandas_df = to_pandas(result)
            polars_df = to_polars(result)
        finally:
            if old_pandas is None:
                del sys.modules["pandas"]
            else:
                sys.modules["pandas"] = old_pandas
            if old_polars is None:
                del sys.modules["polars"]
            else:
                sys.modules["polars"] = old_polars

        assert self._get_value(pandas_df, 0, 'timestamp') == np.datetime64('2026-01-01')
        assert self._get_value(pandas_df, 1, 'MainGate') == 3.0
        assert self._get_value(polars_df, 0, 'MainGate') == 2.0
        assert self._get_value(polars_df, 1, 'spill') == 1.0

    def test_converters_preserve_schema_for_empty_results(self):
        """Test empty structured arrays preserve dtype schema columns in converters."""
        from canteen.simulation import to_pandas, to_polars
        import sys
        import types

        result = np.array(
            [],
            dtype=[
                ('timestep', np.int32),
                ('timestamp', 'datetime64[D]'),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('MainGate', np.float64),
                ('spill', np.float64),
            ],
        )

        def _pandas_dataframe(data):
            """Return data payload for assertion-friendly fake dataframe behavior."""
            return {'data': data}

        def _polars_dataframe(columns):
            """Return columns payload for assertion-friendly fake dataframe behavior."""
            return {'columns': columns}

        old_pandas = sys.modules.get("pandas")
        old_polars = sys.modules.get("polars")
        fake_pd = types.ModuleType("pandas")
        fake_pd.DataFrame = _pandas_dataframe
        fake_pl = types.ModuleType("polars")
        fake_pl.DataFrame = _polars_dataframe

        sys.modules["pandas"] = fake_pd
        sys.modules["polars"] = fake_pl
        try:
            pandas_df = to_pandas(result)
            polars_df = to_polars(result)
        finally:
            if old_pandas is None:
                del sys.modules["pandas"]
            else:
                sys.modules["pandas"] = old_pandas
            if old_polars is None:
                del sys.modules["polars"]
            else:
                sys.modules["polars"] = old_polars

        expected_columns = [
            'timestep',
            'timestamp',
            'inflow',
            'storage',
            'MainGate',
            'spill',
        ]
        assert list(pandas_df['data'].dtype.names) == expected_columns
        assert list(polars_df['columns'].keys()) == expected_columns

    def test_to_pandas_raises_helpful_error_when_pandas_missing(self, monkeypatch):
        """Test that to_pandas raises ImportError with helpful guidance."""
        import pytest
        import sys
        from importlib import import_module as real_import_module

        from canteen.simulation import to_pandas

        result = np.array(
            [(0, 10.0, 50.0, 0.0)],
            dtype=[
                ('timestep', np.int32),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('spill', np.float64),
            ],
        )

        def _fake_import(name, package=None):
            if name == "pandas":
                raise ImportError("No module named pandas")
            return real_import_module(name, package)

        monkeypatch.setattr("canteen.simulation.importlib.import_module", _fake_import)
        monkeypatch.delitem(sys.modules, "pandas", raising=False)

        with pytest.raises(ImportError, match="pandas"):
            to_pandas(result)

    def test_to_polars_raises_helpful_error_when_polars_missing(self, monkeypatch):
        """Test that to_polars raises ImportError with helpful guidance."""
        import pytest
        import sys
        from importlib import import_module as real_import_module

        from canteen.simulation import to_polars

        result = np.array(
            [(0, 10.0, 50.0, 0.0)],
            dtype=[
                ('timestep', np.int32),
                ('inflow', np.float64),
                ('storage', np.float64),
                ('spill', np.float64),
            ],
        )

        def _fake_import(name, package=None):
            if name == "polars":
                raise ImportError("No module named polars")
            return real_import_module(name, package)

        monkeypatch.setattr("canteen.simulation.importlib.import_module", _fake_import)
        monkeypatch.delitem(sys.modules, "polars", raising=False)

        with pytest.raises(ImportError, match="polars"):
            to_polars(result)
