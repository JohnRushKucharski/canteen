'''
Depreciable assets.

Supported asset lifetime methods:
- Useful life
- Units of production

Supported depreciation models:
- Linear
- Cascading
'''
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable

class LifeTimeUnits(Enum):
    '''Supported useful life units.'''
    TIME = 'time'
    '''Time periods.'''
    PRODUCTION = 'production'
    '''Units of production.'''

@dataclass
class Lifetime:
    '''Depreciation model for assets.'''
    shape_parameter: float = 1.0
    '''Parameter controlling shape of deprecation function.'''
    useful_life: float = 100.0
    '''Total initial useful life in lifetime units.'''
    functional_age: float = 0.0
    '''Current useful life in lifetime units.'''
    lifetime_units: LifeTimeUnits = LifeTimeUnits.TIME
    '''Units of useful life.'''
    ft: Callable[[float], float] = field(init=False, repr=False)
    '''Portion of depreciable asset value remaining as function of time.'''
    inverse_ft: Callable[[float], float] = field(init=False, repr=False)
    '''Time period in schedule corresponding to given portion of depreciable asset value.'''

    def __post_init__(self):
        self.ft = build_ft(n=self.useful_life, k=self.shape_parameter)
        self.inverse_ft = build_inverse_ft(n=self.useful_life, k=self.shape_parameter)

    def age_to_value(self, asset: 'Asset', t: None|float = None) -> float:
        '''
        Computes depreciable asset value at time t.
        
        Args:
            asset (Asset): The asset to compute value for.
            t (float): Time period in lifetime units.

        Returns:
            float: Depreciated asset value.
        '''
        if t is None:
            t = asset.lifetime.functional_age
        if t < 0:
            raise ValueError(f'Time parameter, t; {t} must be positive.')
        if self.useful_life <= t:
            print(f'Warning: time parameter, {t} exceeds useful life, {self.useful_life}.')
            return asset.values.salvage
        return asset.values.salvage + self.ft(t) * asset.values.depreciable_value

def build_ft(n: float = 100.0, k: float = 1.0) -> Callable[[float], float]:
    '''
    Builds a function that computes depreciable asset value at time t.
    
    Args:
        n (float): Useful life of asset in units of time or production.
        k (float): Shape parameter for the depreciation function.
    
    Returns:
        Callable: Function that computes portion of asset value remaining at time t.
    '''
    if n < 0:
        raise ValueError(f'Useful life parameter, n: {n} must be greater than zero.')
    if k < 0:
        raise ValueError(f'Shape parameter, k: {k} must be greater than zero.')
    def ft(t: float) -> float:
        '''
        Computes depreciable asset value at time t.
        
        Args:
            t (float): Time period in lifetime units.
        
        Returns:
            float: Portion asset value remaining.
        '''
        if t < 0:
            print(f'Warning: invalid (negative) time parameter, {t} set to 0.')
            return 1.0
        if t > n:
            print(f'Warning: invalid (t > n) time parameter, {t} set to {n}.')
            return 0.0
        return (1 - t / n) ** k
    return ft

def build_inverse_ft(n: float = 100.0, k: float = 1.0) -> Callable[[float], float]:
    '''
    Builds a function that computes time in depreciation schedule
    as function of remaining portion of assets depreciable value.
    
    Args:
        n (float): Useful life of asset in units of time or production.
        k (float): Shape parameter for the depreciation function.
    
    Returns:
        Callable: Function that converts portion remaining of depreciable value
        to time on depreciation schedule.
    '''
    if n < 0:
        raise ValueError(f'Useful life parameter, n: {n} must be greater than zero.')
    if k < 0:
        raise ValueError(f'Shape parameter, k: {k} must be greater than zero.')
    def inverse_ft(y: float) -> float:
        '''
        Computes time period in depreciation schedule as function of 
        remaining portion of depreciable value.
        
        Args:
            y (float): Remaining portion of depreciable asset value.
        Returns:
            float: Time period in lifetime units.
        '''
        if not 0 <= y <= 1:
            raise ValueError('Portion value remaining parameter, y: {y} must be on range: [0, 1].')
        return n * (1 - y) ** (1 / k)
    return inverse_ft

@dataclass
class Values:
    '''Holds value range for an asset.'''
    salvage: float = 0.0
    '''Minimum value of the asset.'''
    initial: float = 100.0
    '''Original new value of the asset at time of creation.'''
    current: float = 100.0
    '''Current value of the asset.'''

    def __post_init__(self):
        if self.salvage < 0 or self.initial < 0:
            raise ValueError('Values must be non-negative.')
        if self.initial < self.salvage:
            raise ValueError(
                'Invalid value range: Initial value cannot be less than salvage value.'
            )
        if not self.salvage <= self.current <= self.initial:
            raise ValueError(
                f'''Invalid current value: {self.current}.
                salvage <= current_value <= initial required.
                salvage: {self.salvage}, current_value: {self.current},
                and initial: {self.initial} values found.
                '''
            )

    @property
    def depreciable_value(self) -> float:
        '''Computes the value range of the asset.'''
        return self.initial - self.salvage

@dataclass
class Asset:
    '''Depreciable asset.'''
    values: Values = field(default_factory=Values)
    '''Current, initial and salvage values for asset.'''
    lifetime: Lifetime = field(default_factory=Lifetime)
    '''Current age, useful life of the asset in lifetime units.'''

    @property
    def age(self) -> float:
        '''Returns functional age of asset.'''
        return self.lifetime.functional_age
    @age.setter
    def age(self, t: float) -> None:
        '''Sets functional age of the asset, modifies value to match.'''
        if t < 0:
            raise ValueError(f'Functional age must be non-negative, got: {t}.')
        if t < self.lifetime.functional_age:
            print(f'''Invalid (t > useful_life) functional age:
                  {t} set to useful life: {self.lifetime.useful_life}.''')
            t = self.lifetime.useful_life
        self.lifetime.functional_age = t
        self.values.current = self.lifetime.age_to_value(self, t)

    @property
    def value(self) -> float:
        '''Returns current value of the asset.'''
        return self.values.current
    @value.setter
    def value(self, v: float) -> None:
        '''Sets current value of the asset, modifies age to match.'''
        if v < self.values.salvage or v > self.values.initial:
            raise ValueError(f'''Invalid value: {v}.
                             Must be in range: [{self.values.salvage}, {self.values.initial}].''')
        self.values.current = v
        portion_remaining = (v - self.values.salvage) / self.values.depreciable_value
        self.lifetime.functional_age = self.lifetime.inverse_ft(portion_remaining)

    @property
    def accumulated_depreciation(self) -> float:
        '''Computes accumulated depreciation of the asset.'''
        return self.values.initial - self.values.current

    @property
    def remaining_life(self) -> float:
        '''Computes remaining life of the asset in lifetime units.'''
        return self.lifetime.useful_life - self.lifetime.functional_age

    @property
    def portion_remaining(self) -> float:
        '''Computes portion of asset value remaining.'''
        return (self.values.current - self.values.salvage) / self.values.depreciable_value

    def increment_time(self, t: float = 1.0) -> None:
        '''Advances the functional age of the asset by t periods.'''
        self.lifetime.functional_age += t
        if self.lifetime.functional_age < 0:
            print(f'Warning: computed time: {self.lifetime.functional_age} set to 0.')
            self.lifetime.functional_age = 0
        if self.lifetime.useful_life < self.lifetime.functional_age:
            self.values.current = self.values.salvage       #type: ignore[misc]
        self.values.current = self.lifetime.age_to_value(   #type: ignore[misc]
            self, self.lifetime.functional_age)             #type: ignore[misc]
