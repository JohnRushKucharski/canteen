"""Tests for the validation module."""

import pytest

from canteen.validation import (
    is_at_least,
    validate_is_at_least,
    is_greater_than,
    validate_is_greater_than,
    is_positive,
    is_not_negative,
    is_ascending_range,
    validate_is_ascending_range,
    is_on_range,
    is_equal_lengths,
    is_strictly_increasing,
    is_strictly_decreasing,
    is_strictly_monotonic,
    is_valid_day_of_year,
)


class TestIsAtLeast:
    """Test is_at_least function."""

    def test_valid_values(self):
        """Test that valid values return True."""
        assert is_at_least(5, 0) is True
        assert is_at_least(0, 0) is True
        assert is_at_least(10.5, 10.0) is True

    def test_invalid_values(self):
        """Test that invalid values return False."""
        assert is_at_least(-1, 0) is False
        assert is_at_least(5, 10) is False


class TestValidateIsAtLeast:
    """Test validate_is_at_least function."""

    def test_valid_no_exception(self):
        """Test that valid values do not raise exception."""
        validate_is_at_least(5, 0)
        validate_is_at_least(10, 10)

    def test_invalid_raises_error(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="must be greater than"):
            validate_is_at_least(-1, 0)


class TestIsGreaterThan:
    """Test is_greater_than function."""

    def test_valid_values(self):
        """Test that strictly greater values return True."""
        assert is_greater_than(5, 0) is True
        assert is_greater_than(10.1, 10.0) is True

    def test_invalid_values(self):
        """Test that equal or lesser values return False."""
        assert is_greater_than(0, 0) is False
        assert is_greater_than(5, 10) is False


class TestValidateIsGreaterThan:
    """Test validate_is_greater_than function."""

    def test_valid_no_exception(self):
        """Test that strictly greater values do not raise exception."""
        validate_is_greater_than(5, 0)
        validate_is_greater_than(10.1, 10.0)

    def test_invalid_raises_error(self):
        """Test that equal or lesser values raise ValueError."""
        with pytest.raises(ValueError, match="must be greater than"):
            validate_is_greater_than(0, 0)


class TestIsPositive:
    """Test is_positive function."""

    def test_valid_values(self):
        """Test that positive values return True."""
        assert is_positive(1) is True
        assert is_positive(0.001) is True

    def test_invalid_values(self):
        """Test that zero and negative values return False."""
        assert is_positive(0) is False
        assert is_positive(-1) is False


class TestIsNotNegative:
    """Test is_not_negative function."""

    def test_valid_values(self):
        """Test that non-negative values return True."""
        assert is_not_negative(0) is True
        assert is_not_negative(10) is True

    def test_invalid_values(self):
        """Test that negative values return False."""
        assert is_not_negative(-1) is False
        assert is_not_negative(-0.001) is False


class TestIsAscendingRange:
    """Test is_ascending_range function."""

    def test_valid_ranges(self):
        """Test that valid ranges return True."""
        assert is_ascending_range(0, 10) is True
        assert is_ascending_range(5, 5) is True

    def test_invalid_ranges(self):
        """Test that descending ranges return False."""
        assert is_ascending_range(10, 5) is False


class TestValidateIsAscendingRange:
    """Test validate_is_ascending_range function."""

    def test_valid_no_exception(self):
        """Test that valid ranges do not raise exception."""
        validate_is_ascending_range(0, 10)
        validate_is_ascending_range(5, 5)

    def test_invalid_raises_error(self):
        """Test that invalid ranges raise ValueError."""
        with pytest.raises(ValueError, match="minimum cannot be greater than maximum"):
            validate_is_ascending_range(10, 5)


class TestIsOnRange:
    """Test is_on_range function."""

    def test_valid_values(self):
        """Test that values within range return True."""
        assert is_on_range(5, 0, 10) is True
        assert is_on_range(0, 0, 10) is True
        assert is_on_range(10, 0, 10) is True

    def test_invalid_values(self):
        """Test that values outside range return False."""
        assert is_on_range(-1, 0, 10) is False
        assert is_on_range(11, 0, 10) is False


class TestIsEqualLengths:
    """Test is_equal_lengths function."""

    def test_equal_length_sequences(self):
        """Test that equal length sequences return True."""
        assert is_equal_lengths([1, 2, 3], [4, 5, 6]) is True
        assert is_equal_lengths([1], [2], [3]) is True
        assert is_equal_lengths() is True

    def test_unequal_length_sequences(self):
        """Test that unequal length sequences return False."""
        assert is_equal_lengths([1, 2], [3, 4, 5]) is False
        assert is_equal_lengths([1], [2, 3]) is False


class TestIsStrictlyIncreasing:
    """Test is_strictly_increasing function."""

    def test_strictly_increasing_sequences(self):
        """Test that strictly increasing sequences return True."""
        assert is_strictly_increasing([1, 2, 3, 4]) is True
        assert is_strictly_increasing([]) is True

    def test_non_increasing_sequences(self):
        """Test that non-increasing sequences return False."""
        assert is_strictly_increasing([1, 2, 2, 4]) is False
        assert is_strictly_increasing([4, 3, 2, 1]) is False


class TestIsStrictlyDecreasing:
    """Test is_strictly_decreasing function."""

    def test_strictly_decreasing_sequences(self):
        """Test that strictly decreasing sequences return True."""
        assert is_strictly_decreasing([4, 3, 2, 1]) is True
        assert is_strictly_decreasing([]) is True

    def test_non_decreasing_sequences(self):
        """Test that non-decreasing sequences return False."""
        assert is_strictly_decreasing([4, 3, 3, 1]) is False
        assert is_strictly_decreasing([1, 2, 3, 4]) is False


class TestIsMonotonic:
    """Test is_monotonic function."""

    def test_monotonic_sequences(self):
        """Test that monotonic sequences return True."""
        assert is_strictly_monotonic([1, 2, 2, 3]) is True
        assert is_strictly_monotonic([4, 3, 3, 1]) is True
        assert is_strictly_monotonic([1, 1, 1]) is True

    def test_non_monotonic_sequences(self):
        """Test that non-monotonic sequences return False."""
        assert is_strictly_monotonic([1, 3, 2]) is False
        assert is_strictly_monotonic([1, 2, 1]) is False


class TestIsValidDayOfYear:
    """Test is_valid_day_of_year function."""

    def test_valid_days(self):
        """Test that valid days do not raise exception."""
        is_valid_day_of_year(1)
        is_valid_day_of_year(182.5)
        is_valid_day_of_year(365)

    def test_invalid_days(self):
        """Test that invalid days raise ValueError."""
        with pytest.raises(ValueError):
            is_valid_day_of_year(0)
        with pytest.raises(ValueError):
            is_valid_day_of_year(366)
