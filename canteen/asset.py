'''
Depreciable asset module.
'''
from typing import Callable, Self
from dataclasses import dataclass, field

@dataclass(frozen=True)
class DepreciationParameters:
    '''Holds depreciation parameters.'''
    k: float = 1.0
    '''
    Parameter controling shape of depreciation schedule.
    
    1.0 by default.
    = 1.0 is linear (w.r.t time),
    < 1.0 is convex (slower than linear),
    > 1.0 is concave (faster than linear),
    '''
    n: int = 100
    '''Number of periods in depreciation schedule.'''
    maintenance_requirement: float = 1.0
    '''Maintenance requirement per time period.'''
    acceleration: float = 1.0
    '''
    Parameter controlling acceleration of depreciation schedule,
    when required maintenance is not performed.

    1.0 by default.

    = 1.0 is no acceleraton (normal depreciation),
    > 1.0 if faster than linear acceleration.
    < 1.0 is invalid.

    Defered maintenance can speed up deterioration (i.e., depreciation).
    '''
    ft: Callable[[float], float] = field(init=False)
    '''Portion of depreciable asset value remaining as function of time.'''
    inverse_ft: Callable[[float], float] = field(init=False)
    '''Time period in schedule corresponding to given portion of depreciable asset value.'''
    scheduler: Callable[[float], float] = field(init=False)
    '''Time periods of depreciation based on maintenance level.'''

    def __post_init__(self):
        if self.k < 0:
            raise ValueError(
                f'Invalid shape_parameter, k: {self.k}. k must be > 0.'
            )
        if self.n < 1:
            raise ValueError(
                f'Invalid number of periods in depreciation schedule, n: {self.n}. n must be > 0.'
            )
        if self.acceleration < 1.0:
            raise ValueError(
                f'Invalid acceleration value: {self.acceleration}. Acceleration must be >= 1.0.'
            )
        object.__setattr__(self, 'ft', self.build_ft())
        object.__setattr__(self, 'inverse_ft', self.build_inverse_ft())
        object.__setattr__(self, 'scheduler', self.build_scheduler())

    def build_ft(self) -> Callable[[float], float]:
        '''Builds function that computes portion depreciated value remaining as function of time.'''
        if self.k < 0:
            raise ValueError(
                f'Invalid shape_parameter, k: {self.k}. k must be > 0.'''
            )
        if self.n < 1:
            raise ValueError(
                f'Invalid number of periods in depreciation schedule, n: {self.n}. n must be > 0.'
            )
        def ft(t: float) -> float:  # pylint: disable=invalid-name
            '''
            Portion depreciable asset value remaining as function of time.

            Args:
                t (float): time period in depreciation schedule.

            Returns:
                float: portion of depreciable asset value remaining.
            '''
            if self.n <= t:
                # prevents a negative result.
                return 0.0
            return (1 - t / self.n) ** self.k
        return ft

    def build_inverse_ft(self) -> Callable[[float], float]:
        '''
        Builds function that computes time period of depreciation for a given maintenance level.
        '''
        if self.k < 0:
            raise ValueError(
                f'Invalid shape_parameter, k: {self.k}. k must be > 0.'''
            )
        if self.n < 1:
            raise ValueError(
                f'Invalid number of periods in depreciation schedule, n: {self.n}. n must be > 0.'
            )
        def inverse_ft(y: float) -> float:
            '''
            Time period in schedule corresponding to given portion of depreciable asset value.
        
            Args:
                y (float): portion of depreciable asset value remaining.
        
            Returns:
                float: time period in depreciation schedule.
            '''
            if not 0.0 <= y <= 1.0:
                # prevents a complex result, or non-sense y values.
                raise ValueError(f'y: {y} must be between 0.0 and 1.0.')
            return self.n * (1 - y) ** (1 / self.k)
        return inverse_ft

    def build_scheduler(self) -> Callable[[float], float]:
        '''
        Builds function that computes time period of depreciation for a given maintenance level.
        '''
        if self.k < 0:
            raise ValueError(
                f'Invalid shape_parameter, k: {self.k}. k must be > 0.'''
            )
        if self.n < 1:
            raise ValueError(
                f'Invalid number of periods in depreciation schedule, n: {self.n}. n must be > 0.'
            )
        if self.acceleration < 1:
            raise ValueError('acceleration must be greater than or equal to 1.0.')

        def scheduler(maintenance: float) -> float:
            '''
            Computes time periods of depreciation, for a given amount of maintenance.

            Args:
                maintenance (float): maintenance performed in time period.

            Raises:
                ValueError: if maintenance exceeds maintenance requirement.

            Returns:
                float: time periods of depreciation.
            '''
            if self.maintenance_requirement < maintenance:
                raise ValueError(
                    f'''Invalid maintenance value: {maintenance}.
                    maintenance: {maintenance} > maintenance requirement {self.maintenance_requirement}. # pylint: disable=line-too-long
                    '''
                )
            # if no deferred maintenance, returns 1 time period of depreciation.
            deferred = (self.maintenance_requirement - maintenance) / self.maintenance_requirement
            return 1 + deferred * self.acceleration
        return scheduler


@dataclass(frozen=True)
class Asset:
    '''
    Depreciable asset.
    
    The depreciation function makes this class a sort of monad.
    '''
    value: float = 100.0
    salvage_value: float = 0.0
    replacement_value: float = 100.0
    parameters: DepreciationParameters = DepreciationParameters()
    depreciation_fn: Callable[[float], Self] = field(init=False)
    log: list[float] = field(default_factory=list)

    def __post_init__(self):
        if not self.salvage_value <= self.value <= self.replacement_value:
            raise ValueError(
                f'''Invalid asset values.
                salvage_value <= value <= replacement_value required.
                salvage: {self.salvage_value}, value: {self.value}, and
                replacement: {self.replacement_value} values found.
                '''
            )
        object.__setattr__(self, 'depreciation_fn', self.bind_depreciation_fn())

    @property
    def portion_remaining(self) -> float:
        '''Portion of asset value remaining.'''
        value_range = self.replacement_value - self.salvage_value
        return (self.value - self.salvage_value) / value_range

    @property
    def remaining_life(self) -> float:
        '''Remaining life of asset in time periods.'''
        return self.parameters.n - self.parameters.inverse_ft(self.portion_remaining)

    def bind_depreciation_fn(self) -> Callable[[float], Self]:
        '''Builds depreciation function.'''
        self.log.append(self.value) # this is done at binding time.

        value_range = self.replacement_value - self.salvage_value

        def depreciation_fn(maintenance: float) -> Self:
            '''
            Depreciates asset based on maintenance performed.
            '''
            maint = min(maintenance, self.parameters.maintenance_requirement)
            recap = max(0.0, maint - self.parameters.maintenance_requirement)

            t = min(self.parameters.n,
                    self.parameters.inverse_ft(self.portion_remaining) + self.parameters.scheduler(maint)) # pylint: disable=line-too-long

            val = max(self.salvage_value,
                      min(self.salvage_value + (value_range * self.parameters.ft(t)) + recap,
                          self.replacement_value))

            return Asset(value=val,
                         salvage_value=self.salvage_value, replacement_value=self.replacement_value,
                         parameters=self.parameters, log=self.log)
        return depreciation_fn

    def depreciate(self, maintenance: float) -> Self:
        '''Depreciates asset value based on maintenance level.'''
        return self.depreciation_fn(maintenance)
