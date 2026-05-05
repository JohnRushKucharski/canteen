"""Tests for the map module."""

import pytest

from canteen.mapping import (
    Mappings, ConstantMapping, XYMapping, factory,
    ratingcurve_factory, rulecurve_factory,
    XYMetaData, build_interpolation_fx
)


class TestConstantMap:
    """Test ConstantMapping class - simplest Mapping implementation."""

    def test_constantmap_returns_constant_value(self):
        """Test that ConstantMapping always returns the same value."""
        cmap = ConstantMapping("test", 42.0)

        assert cmap.f() == 42.0
        assert cmap.f(100) == 42.0  # Arguments ignored
        assert cmap.f(x=5, y=10) == 42.0  # Kwargs ignored

    def test_constantmap_inverse_returns_none(self):
        """Test that inverse_f returns None (not defined for constants)."""
        cmap = ConstantMapping("test", 15.5)

        assert cmap.inverse_f() is None     # Inverse is not defined, should return None
        assert cmap.inverse_f(y=5) is None  # Arguments ignored, should return None


class TestXYMap:
    """Test XYMapping class - core interpolation implementation."""

    def test_xymap_returns_none_when_inverse_not_provided(self):
        """Test that XYMapping returns None when inverse_f is not defined."""
        #pylint: disable=unnecessary-lambda-assignment
        f = lambda x: x * 2  # noqa: E731
        xymap = XYMapping(f, None, XYMetaData())

        assert xymap.f(10) == 20
        assert xymap.inverse_f(20) is None  # Inverse not provided, should return None


class TestMaps:
    """Test Mappings container - critical for duplicate handling."""

    def test_duplicate_map_names_raises_error_on_init(self):
        """Test that duplicate map names raise ValueError during initialization."""
        map1 = ConstantMapping("duplicate", 10.0)
        map2 = ConstantMapping("duplicate", 20.0)

        with pytest.raises(ValueError, match="Duplicate mapping name found: duplicate"):
            Mappings([map1, map2])

    def test_add_duplicate_map_name_raises_error(self):
        """Test that adding duplicate map name raises ValueError."""
        mappings = Mappings([ConstantMapping("first", 10.0)])

        with pytest.raises(ValueError, match="Duplicate mapping name found"):
            mappings.add("first", ConstantMapping("first", 20.0))

    def test_delete_map_raises_not_implemented(self):
        """Test that deleting maps raises NotImplementedError."""
        mappings = Mappings([ConstantMapping("test", 10.0)])

        with pytest.raises(NotImplementedError, match="cannot be deleted"):
            del mappings["test"]

    def test_maps_properties_return_correct_data(self):
        """Test that names and maps properties return correct tuples."""
        map1 = ConstantMapping("first", 10.0)
        map2 = ConstantMapping("second", 20.0)
        mappings = Mappings([map1, map2])

        assert mappings.names == ("first", "second")
        assert len(mappings.mappings) == 2
        assert mappings.mappings[0] == map1
        assert mappings.mappings[1] == map2


class TestFactory:
    """Test factory function - complex logic with multiple code paths."""

    def test_factory_with_single_float_ys_creates_constant_map(self):
        """Test that single float ys with xs=None creates ConstantMapping."""
        result = factory(xs=None, ys=42.0, name="constant")

        assert result.f() == 42.0
        assert result.info.name == "constant"

    def test_factory_with_single_float_ys_and_xs_creates_horizontal_line(self):
        """Test that single float ys with xs creates horizontal interpolation."""
        result = factory(xs=[0, 10, 20], ys=5.0, name="flat")

        assert result.f(0) == 5.0
        assert result.f(10) == 5.0
        assert result.f(20) == 5.0

    def test_factory_raises_error_when_xs_none_with_sequence_ys(self):
        """Test that xs=None with sequence ys raises ValueError."""
        with pytest.raises(ValueError, match="xs cannot be None when ys is a sequence"):
            factory(xs=None, ys=[1, 2, 3])

    def test_factory_creates_interpolating_xymap(self):
        """Test that factory creates XYMapping with working interpolation."""
        result = factory(xs=[0, 10, 20], ys=[0, 100, 200], name="linear")

        # Test exact points
        assert result.f(0) == 0
        assert result.f(10) == 100
        assert result.f(20) == 200
        # Test interpolation
        assert result.f(5) == 50  # Halfway between 0 and 10


class TestRatingCurveFactory:
    """Test ratingcurve_factory - validation is critical."""

    def test_non_strictly_increasing_xs_raises_error(self):
        """Test that non-strictly increasing xs raises ValueError."""
        xs = [0, 10, 10, 20]  # Duplicate value
        ys = [0, 100, 150, 200]

        with pytest.raises(ValueError, match="must be increasing"):
            ratingcurve_factory(xs, ys)

    def test_decreasing_ys_raises_error(self):
        """Test that decreasing ys raises ValueError."""
        xs = [0, 10, 20, 30]
        ys = [0, 100, 50, 200]  # Decreases at index 2

        with pytest.raises(ValueError, match="must be increasing"):
            ratingcurve_factory(xs, ys)

class TestRuleCurveFactory:
    """Test rulecurve_factory - day of year validation is error-prone."""

    def test_day_less_than_1_raises_error(self):
        """Test that day of year < 1 raises ValueError."""
        with pytest.raises(ValueError, match="must be monotonically increasing on range"):
            rulecurve_factory([0, 100, 200], [10.0, 15.0, 20.0])

    def test_day_greater_than_365_raises_error(self):
        """Test that day of year > 365 raises ValueError."""
        with pytest.raises(ValueError, match="must be monotonically increasing on range"):
            rulecurve_factory([1, 100, 366], [10.0, 15.0, 20.0])

    def test_non_strictly_increasing_days_raises_error(self):
        """Test that non-strictly increasing days raises ValueError."""
        with pytest.raises(ValueError, match="must be monotonically increasing"):
            rulecurve_factory([1, 100, 100, 200], [10.0, 15.0, 20.0, 25.0])


class TestBuildInterpolationFx:
    """Test build_interpolation_fx function - most complex logic."""

    def test_simple_linear_interpolation(self):
        """Test basic linear interpolation between two points."""
        f = build_interpolation_fx([0, 10], [0, 100])
        assert f(0) == 0
        assert f(5) == 50
        assert f(10) == 100

    def test_multi_segment_interpolation(self):
        """Test interpolation with multiple segments."""
        f = build_interpolation_fx([0, 10, 20], [0, 50, 60])
        # First segment: (0,0) to (10,50)
        assert f(5) == 25
        # Second segment: (10,50) to (20,60)
        assert f(15) == 55

    def test_bounded_mode_raises_outside_domain(self):
        """Test that bounded mode raises error for out-of-bounds x values."""
        f = build_interpolation_fx([0, 10], [0, 100], bounded=True)
        with pytest.raises(ValueError, match="not in interpolation domain"):
            f(-1)
        with pytest.raises(ValueError, match="not in interpolation domain"):
            f(11)

    def test_unbounded_mode_returns_boundary_values(self):
        """Test that unbounded mode returns min/max y for out-of-bounds x."""
        f = build_interpolation_fx([0, 10], [5, 100], bounded=False)
        assert f(-10) == 5  # Returns y_min
        assert f(20) == 100  # Returns y_max

    def test_requires_at_least_two_points(self):
        """Test that function raises error with less than 2 points."""
        with pytest.raises(ValueError, match="at least two points"):
            build_interpolation_fx([0], [0])

    def test_requires_equal_length_sequences(self):
        """Test that function raises error when xs and ys have different lengths."""
        with pytest.raises(ValueError, match="equal length"):
            build_interpolation_fx([0, 10], [0, 10, 20])
