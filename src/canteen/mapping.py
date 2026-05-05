'''
Highly flexible functional relationship (mapping) module.

Mappings define functional relationships between inputs and outputs.
- They are flexible to facilitate extending the functionality of canteen objects.
- Some specific use cases are scoped, i.e., 
        rule curves for variable pools, 
        rating curves for reservoir volume-elevation relationships.
- This can make them inherently confusing and less type safe. 
- MetaData is used to record information about mappings.

The Mappings class is a container for Mapping instances. 
It ensures unique mapping names and provides convenient access.
'''
from collections import UserDict, OrderedDict
from typing import Protocol, Sequence, Callable, Any

from canteen.metadata import MetaData, XYMetaData
from canteen.validation import is_increasing, is_strictly_increasing, is_equal_lengths, is_on_range

class Mapping(Protocol):
    """Protocol for mapping components."""
    info: MetaData

    def f(self, *args: Any, **kwargs: Any) -> Any:
        """
        Apply the mapping function.
        
        Parameters
        ----------
        *args : Any
            Positional arguments for the mapping function.
        **kwargs : Any
            Keyword arguments for the mapping function.
        Returns
        -------
        Any
            The result of the mapping function.
        """

    def inverse_f(self, *args: Any, **kwargs: Any) -> Any:
        """
        Apply the inverse mapping function.
        
        Parameters
        ----------
        *args : Any
            Positional arguments for the inverse mapping function.
        **kwargs : Any
            Keyword arguments for the inverse mapping function.
        Returns
        -------
        Any
            The result of the inverse mapping function.
        """

class Mappings(UserDict[str, Mapping]):
    '''
    Holds list of mappings in a dictionary. Ensures retrieval by name is unique.
    '''
    def __init__(self, mappings: None|Sequence[Mapping]=None) -> None:
        if mappings is None:
            super().__init__({})
            return
        data = OrderedDict[str, Mapping]()
        for m in mappings:
            if m.info.name in data:
                raise ValueError(f"Duplicate mapping name found: {m.info.name}")
            data[m.info.name] = m
        super().__init__(data)

    @property
    def names(self) -> tuple[str, ...]:
        '''
        Get all mapping names as a tuple.
        '''
        return tuple(self.data.keys())
    @property
    def mappings(self) -> tuple[Mapping, ...]:
        '''
        Get all mappings as a tuple.
        '''
        return tuple(self.data.values())

    def add(self, key: None|str, mapping: Mapping) -> None:
        '''
        Add a new mapping to the collection.
        '''
        key = key if key else mapping.info.name
        if key in self.data:
            raise ValueError(f"Duplicate mapping name found: {key}")
        self.data[key] = mapping

    def __setitem__(self, key: str, value: Mapping) -> None:
        if key in self.data:
            raise ValueError(f"Duplicate mapping name found: {key}")
        super().__setitem__(key, value)
    def __delitem__(self, key: str) -> None:
        raise NotImplementedError("Mappings cannot be deleted from collection.")

class ConstantMapping:
    '''
    A mapping that always returns a constant value.
    '''
    def __init__(self, name: str, value: int|float) -> None:
        self.info: MetaData = MetaData(name=name,
                                       description="""
                                       Used to represent constant value as a function.
                                       Mapping.f returns a constant value for any input,
                                       Mapping.inverse_f is not defined and returns None."""
                                       )
        self._constant: int|float = value

    def f(self, *args: Any, **kwargs: Any) -> int|float:                #pylint: disable=unused-argument
        '''Constant value.'''
        return self._constant

    def inverse_f(self, *args: Any, **kwargs: Any) -> None|int|float:   #pylint: disable=unused-argument
        '''Constant value.'''
        return None

class XYMapping:
    '''
    Used to define f(x)=y relationship, and if possible inverse (i.e., f(y)=x) relationships.
    
    Implements Mapping protocol.
    '''
    def __init__(self, f: Callable[[float], float],
                 inverse_f: None|Callable[[float], float],
                 info: XYMetaData) -> None:
        self._f: Callable[[float], float] = f
        self._inverse_f: None|Callable[[float], float] = inverse_f
        if info.description == "":
            info.description = """
            Maps an sequence of x values (the domain) to a sequence of y values (the range) using Mapping.f.
            If Mapping.f is invertible and Mapping.inverse_f is provided, it maps y values back to x values.
            """
        self.info: MetaData = info

    def f(self, x: int|float, *args: Any, **kwargs: Any)->float:                #pylint: disable=unused-argument
        '''
        Apply the mapping function.
        '''
        return self._f(x)
    def inverse_f(self, y: int|float, *args: Any, **kwargs: Any)->None|float:   #pylint: disable=unused-argument
        '''
        Apply the inverse mapping function.
        '''
        if self._inverse_f is None:
            return None
        return self._inverse_f(y)

def factory(xs: None|Sequence[int|float] = (0, 1),
            ys: int|float|Sequence[int|float] = (0, 1),
            name: str = "1D Mapping", xname: str = "x", yname: str = "y") -> Mapping:
    '''
    Factory function to create a 1D Mapping from xs and ys data.
    '''
    if isinstance(ys, (int, float)):
        if xs is None:
            return constantmapping_factory(ys, name)
        ys = [ys] * len(xs)
    if xs is None:
        raise ValueError("xs cannot be None when ys is a sequence.")
    f, inverse_f = build_1D_interpolation_fxs(xs, ys, bounded=True)
    info = XYMetaData(name=name,
                      xname=xname, yname=yname,
                      domain=(min(xs), max(xs)), range_=(min(ys), max(ys)))
    return XYMapping(f, inverse_f, info)

def constantmapping_factory(value: int|float, name: str = "constant_mapping") -> Mapping:
    '''
    Factory function to create a ConstantMapping.
    '''
    return ConstantMapping(name, value)

def ratingcurve_factory(xs: Sequence[int|float], ys: Sequence[int|float],
                        name: str = "rating_curve", xname: str = "volume", yname: str = "elevation"
                        ) -> Mapping:
    '''
    Factory function to create a RatingCurve from xs and ys data.
    
    Implements Mapping protocol.
    '''
    if not is_strictly_increasing(xs) or not is_increasing(ys):
        raise ValueError("xs and ys must be increasing sequences of values.")
    return factory(xs, ys, name, xname, yname)

def rulecurve_factory(days_of_year: Sequence[int|float], locations: Sequence[int|float],
                      name: str = "rule_curve", xname: str = "day_of_year", yname: str = "location"
                      ) -> Mapping:
    '''
    Factory function to create a rule curve relationship 
    between the day of year and volume associated with a pool location.
    
    Implements Mapping protocol.
    '''
    min_day, max_day = min(days_of_year), max(days_of_year)
    if (not is_strictly_increasing(days_of_year) or min_day < 1 or max_day > 365):
        raise ValueError(f"{xname} must be monotonically increasing on range [1, 365].")
    return factory(xs=days_of_year, ys=locations, name=name, xname=xname, yname=yname)


def build_interpolation_fx(xs: Sequence[int|float], ys: Sequence[int|float],
                           bounded: bool = True) -> Callable[[int|float], int|float]:
    '''
     Builds a closure for 1D linear interpolation between xs and ys.
    '''
    if not is_equal_lengths(xs, ys) or len(xs) < 2:
        raise ValueError("xs and ys must be of equal length and contain at least two points.")
    y_min, y_max = min(ys), max(ys)
    x_min, x_max = min(xs), max(xs)
    def f(x: int|float) -> int|float:
        '''
        Linear interpolation function.
        '''
        if not is_on_range(x, x_min, x_max):
            if bounded:
                raise ValueError(f"x={x} is not in interpolation domain: [{x_min}, {x_max}].")
            return y_min if x < x_min else y_max
        for i in range(1, len(xs)):
            if xs[i-1] <= x <= xs[i]:
                # Linear interpolation formula
                slope = (ys[i] - ys[i-1]) / (xs[i] - xs[i-1])
                return ys[i-1] + slope * (x - xs[i-1])
        raise ValueError(f"x={x} is out of bounds for interpolation.") # should be unreachable
    return f

def build_1D_interpolation_fxs(xs: Sequence[int|float],                         # pylint: disable=invalid-name
                               ys: Sequence[int|float], bounded: bool = True
                               ) -> tuple[Callable[[int|float], int|float],
                                          None|Callable[[int|float], int|float]]:
    '''
    Builds a linear interpolation function and if possible its inverse from 1D x, y data.
    '''
    # Cannot be a function if xs are not unique
    if len(xs) != len(set(xs)):
        raise ValueError("Function cannot be built: xs contain duplicate values.")
    f = build_interpolation_fx(xs, ys, bounded)
    if len(ys) != len(set(ys)):
        return f, None
    return f, build_interpolation_fx(ys, xs, bounded) # pylint: disable=arguments-out-of-order
