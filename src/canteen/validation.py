"""
Validation utilities for the Canteen package.

This module provides common validation functions used across the package
to reduce code duplication and improve consistency.
"""
from typing import Sequence, Protocol, Any

#region validate value domains.
def is_at_least(value: int|float, min_val: int|float = 0) -> bool:
    """
    Validates that value is larger than a specified minimum.
    
    Parameters
    ----------
    value : int | float | Quantity
        Value to validate
    min_val : int | float, optional
        Minimum allowed value, by default 0
    name : str, optional
        Name of the value for error messages, by default "value"
    min_name : str, optional
        Name of the minimum value for error messages, by default "min"
        
    Raises
    ------
    ValueError
        If value is less than the minimum value.
    """
    return value >= min_val
def validate_is_at_least(value: int|float, min_val: int|float = 0,
                         name: str = "value", min_name: str = "min") -> None:
    """
    Raise ValueError if numeric value is not greater than or equal to a specified minimum.
    
    Parameters
    ----------
    value : int | float
        Value to validate
    min_val : int | float, optional
        Minimum threshold value, by default 0
    min_name : str, optional
        Name of the minimum value for error messages, by default "min"
    name : str, optional
        Name of the value for error messages, by default "value"
        
    Raises
    ------
    ValueError
        If value is not greater than minimum
    """
    if not is_at_least(value, min_val):
        raise ValueError(f"{name}: {value} must be greater than {min_name}:{min_val}.")

def is_greater_than(value: int|float, min_val: int|float = 0) -> bool:
    """
    Validate that a numeric value is greater than or equal to a specified minimum.
    
    Parameters
    ----------
    value : int | float
        Value to validate
    min_val : int | float, optional
        Minimum threshold value, by default 0
    min_name : str, optional
        Name of the minimum value for error messages, by default "min"
    name : str, optional
        Name of the value for error messages, by default "value"
        
    Raises
    ------
    ValueError
        If value is not greater than minimum
    """
    return value > min_val
def validate_is_greater_than(value: int|float, min_val: int|float = 0,
                             name: str = "value", min_name: str = "min") -> None:
    """
    Raise ValueError if numeric value is not greater than a specified minimum.

    Parameters
    ----------
    value : int | float
        Value to validate
    min_val : int | float, optional
        Minimum threshold value, by default 0
    min_name : str, optional
        Name of the minimum value for error messages, by default "min"
    name : str, optional
        Name of the value for error messages, by default "value"

    Raises
    ------
    ValueError
        If value is not greater than minimum
    """
    if not is_greater_than(value, min_val):
        raise ValueError(f"{name}: {value} must be greater than {min_name}:{min_val}.")

def is_positive(value: int|float) -> bool:
    """
    Validate that a value is positive.
    
    Parameters
    ----------
    value : int | float
        Value to validate
    name : str, optional
        Name of the value for error messages, by default "value"
        
    Raises
    ------
    ValueError
        If value is not positive
    """
    return value > 0
def validate_is_positive(value: int|float,
                         name: str = "value") -> None:
    """
    Raise ValueError if a value is not positive.

    Parameters
    ----------
    value : int | float
        Value to validate
    name : str, optional
        Name of the value for error messages, by default "value"
    Raises
    ------
    ValueError
        If value is not positive
    """
    if not is_positive(value):
        raise ValueError(f"{name}: {value} must be positive.")

def is_not_negative(value: int|float) -> bool:
    """
    Validate that a value is non-negative.
    
    Parameters
    ----------
    value : int | float
        Value to validate
    name : str, optional
        Name of the value for error messages, by default "value"
        
    Raises
    ------
    ValueError
        If value is negative
    """
    return is_at_least(value, 0)
def validate_is_not_negative(value: int|float,
                             name: str = "value") -> None:
    """
    Raise ValueError if a value is negative.
    Parameters
    ----------
    value : int | float
        Value to validate
    name : str, optional
        Name of the value for error messages, by default "value"
    Raises
    ------
    ValueError
        If value is negative
    """
    if not is_not_negative(value):
        raise ValueError(f"{name}: {value} cannot be negative.")

def is_ascending_range(min_val: int|float, max_val: int|float) -> bool:
    """
    Validate that min <= max for a range.
    
    Parameters
    ----------
    min_val : int | float
        Minimum value
    max_val : int | float  
        Maximum value
    name : str, optional
        Name of the range for error messages, by default "range"
        
    Raises
    ------
    ValueError
        If min > max
    """
    return is_at_least(max_val, min_val)
def validate_is_ascending_range(min_val: int|float, max_val: int|float,
                                name: str = "range") -> None:
    """
    Raise ValueError if min > max for a range.
    Parameters
    ----------
    min_val : int | float
        Minimum value
    max_val : int | float
        Maximum value
    name : str, optional
        Name of the range for error messages, by default "range"
    Raises
    ------
    ValueError
        If min > max
    """
    if not is_ascending_range(min_val, max_val):
        raise ValueError(f"{name}: [{min_val}, {max_val}] minimum cannot be greater than maximum.")

def is_on_range(value: int|float, min_val: int|float, max_val: int|float) -> bool:
    """
    Validate that a numeric value is within a specified range [min_val, max_val].
    
    Parameters
    ----------
    value : int | float
        Value to validate
    min_val : int | float
        Minimum allowed value
    max_val : int | float
        Maximum allowed value
    name : str, optional
        Name of the value for error messages, by default "value"
        
    Raises
    ------
    ValueError
        If value is outside the specified range
    """
    return is_at_least(value, min_val) and is_at_least(max_val, value)
def validate_is_on_range(value: int|float, min_val: int|float, max_val: int|float,
                            name: str = "value") -> None:
    """
    Raise ValueError if a numeric value is outside a specified range [min_val, max_val
    Parameters
    ----------
    value : int | float
        Value to validate
    min_val : int | float
        Minimum allowed value
    max_val : int | float
        Maximum allowed value
    name : str, optional
        Name of the value for error messages, by default "value"
    Raises
    ------
    ValueError
        If value is outside the specified range
    """
    if not is_on_range(value, min_val, max_val):
        raise ValueError(f"{name}: {value} must be in range [{min_val}, {max_val}].")
#endregion

def is_equal_lengths(*sequences: Sequence[Any]) -> bool:
    """
    Validate that all provided sequences have equal lengths.
    
    Parameters
    ----------
    *sequences : Sequence[Any]
        Sequences to validate
        
    Returns
    -------
    bool
        True if all sequences have equal lengths, False otherwise.
    """
    if not sequences:
        return True
    first_length = len(sequences[0])
    return all(len(seq) == first_length for seq in sequences)


def validate_operation_output_shape(outputs: Sequence[Any], outlet_count: int, operation_name: str
                                    ) -> None:
    """Validate operations output shape as one value per outlet plus spill."""
    expected_outputs = outlet_count + 1
    if len(outputs) != expected_outputs:
        raise ValueError(
            "Operation output shape invalid. "
            f"Expected {expected_outputs} values (one per outlet plus spill), "
            f"got {len(outputs)} from {operation_name}."
        )

def is_increasing(sequence: Sequence[int|float]) -> bool:
    """
    Check if a sequence of numbers is non-decreasing.
    
    Parameters
    ----------
    sequence : list[float]
        List of numeric values to check.
        
    Returns
    -------
    bool
        True if the sequence is non-decreasing, False otherwise.
        
    Examples
    --------
    >>> is_increasing([1, 2, 2, 3])
    True
    >>> is_increasing([1, 3, 2])
    False
    """
    return all(later >= earlier for earlier, later in zip(sequence, sequence[1:]))

def is_strictly_increasing(sequence: Sequence[int|float]) -> bool:
    """
    Check if a sequence of numbers is strictly increasing.
    
    Parameters
    ----------
    sequence : list[float]
        List of numeric values to check.
        
    Returns
    -------
    bool
        True if the sequence is strictly increasing, False otherwise.
        
    Examples
    --------
    >>> is_strictly_increasing([1, 2, 3, 4])
    True
    >>> is_strictly_increasing([1, 2, 2, 4])
    False
    >>> is_strictly_increasing([4, 3, 2, 1])
    False
    """
    return all(later > earlier for earlier, later in zip(sequence, sequence[1:]))

def is_strictly_decreasing(sequence: Sequence[int|float]) -> bool:
    """
    Check if a sequence of numbers is strictly decreasing.
    
    Parameters
    ----------
    sequence : list[float]
        List of numeric values to check.
        
    Returns
    -------
    bool
        True if the sequence is strictly decreasing, False otherwise.
        
    Examples
    --------
    >>> is_strictly_decreasing([4, 3, 2, 1])
    True
    >>> is_strictly_decreasing([4, 3, 3, 1])
    False
    >>> is_strictly_decreasing([1, 2, 3, 4])
    False
    """
    return all(later < earlier for earlier, later in zip(sequence, sequence[1:]))

def is_strictly_monotonic(sequence: Sequence[int|float]) -> bool:
    """
    Check if a sequence of numbers is monotonic (either entirely non-increasing or non-decreasing).
    
    Parameters
    ----------
    sequence : list[float]
        List of numeric values to check.
        
    Returns
    -------
    bool
        True if the sequence is monotonic, False otherwise.
        
    Examples
    --------
    >>> is_strictly_monotonic([1, 2, 2, 3])
    True
    >>> is_strictly_monotonic([4, 3, 3, 1])
    True
    >>> is_strictly_monotonic([1, 3, 2])
    False
    """
    is_non_decreasing = all(later >= earlier for earlier, later in zip(sequence, sequence[1:]))
    is_non_increasing = all(later <= earlier for earlier, later in zip(sequence, sequence[1:]))
    return is_non_decreasing or is_non_increasing

#region operations specific validation
# def is_valid_rule_curve_ordinates(ordinates: Sequence[tuple[int | float, int | float]]) -> None:
#     """
#     Validate rule curve ordinates.
#     Parameters
#     ----------
#     ordinates : Sequence[tuple[int | float, int | float]]
#         Sequence of (day, location) tuples
#     Raises
#     ------
#     ValueError
#         If ordinates are invalid
#     """
#     if not ordinates:
#         raise ValueError("Ordinates cannot be empty")

#     if len(ordinates) < 2:
#         raise ValueError("Must have at least 2 ordinates")

#     # Sort by day for validation
#     sorted_points = sorted(ordinates, key=lambda x: x[0])

#     if sorted_points[0][0] != 1:
#         raise ValueError("First ordinate must be day 1")

#     if sorted_points[-1][0] != 365:
#         raise ValueError("Last ordinate must be day 365")
#     # Check for duplicates
#     days = [bp[0] for bp in ordinates]
#     if len(days) != len(set(days)):
#         raise ValueError("Duplicate days found in ordinates")

#     # Validate day range and numeric types
#     for day, location in ordinates:
#         if not isinstance(day, (int, float)):
#             raise ValueError(f"Day must be numeric, got {type(day).__name__}")
#         if not isinstance(location, (int, float)):
#             raise ValueError("Location must be numeric")
#         if not 1 <= day <= 365:
#             raise ValueError(f"Day must be in range [1, 365], got {day}")

def is_valid_day_of_year(day: float, name: str = "day_of_year") -> None:
    """
    Validate day of water year is in valid range.
    
    Parameters
    ----------
    day : float
        Day to validate (allows fractional days)
    name : str, optional
        Name for error messages, by default "day_of_year"
        
    Raises
    ------
    ValueError
        If day is out of range [1, 365]
    """
    if not is_on_range(day, 1, 365):
        raise ValueError(f"{name}: {day} must be in range [1, 365].")
#endregion

#region Integer-only type compatibility validation
class IntOnly(Protocol):
    """Protocol for int_only objects."""
    int_only: bool

def int_only_compatible_values(obj: IntOnly, values: Sequence[int | float])  -> None:
    """
    Validate that int_only object values are compatible.
    """
    if obj.int_only:
        for x in values:
            if not isinstance(x, int):
                raise TypeError(f"Non-integer value:{x} not a valid int_only object element.")

def int_only_compatible_objects(obj: IntOnly, other: IntOnly)  -> None:
    """
    Validate that two int_only objects are compatible.
    """
    if not obj.int_only == other.int_only:
        raise TypeError("Incompatible int_only objects.")
    # If both are int_only or not int_only, then they are compatible
#endregion
