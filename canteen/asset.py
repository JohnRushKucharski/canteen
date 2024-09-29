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
        # self.ft = self.build_ft()
        # self.inverse_ft = self.build_inverse_ft()
        # self.scheduler = self.build_scheduler()

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

# class Asset:
#     '''Depreciable asset.'''
#     def __init__(self,
#                  init_value: float = 100.0,
#                  salvage_value: float = 0.0,
#                  replacement_value: float = 100.0,
#                  depreciation_params: DepreciationParameters = DepreciationParameters()):
#         if not salvage_value <= init_value <= replacement_value:
#             raise ValueError(
#                 f'''Invalid asset values.
#                 salvage_value <= init_value <= replacement_value required.
#                 salvage: {salvage_value}, initial: {init_value}, and
#                 replacement: {replacement_value} values found.
#                 '''
#             )
#         self.__value = init_value
#         self.__salvage_value = salvage_value
#         self.__replacement_value = replacement_value
#         self.__parameters = depreciation_params
#         self.__depreciation_fx = self.build_depreciation_function()

#     # def __post_init__(self):
#     #     self.__depreciation_fx = self.build_depreciation_function()

#     @property
#     def value(self):
#         '''Current value of asset.'''
#         return max(self.salvage_value,
#                    min(self.replacement_value, self.__value))
#     @value.setter
#     def value(self, value: float):
#         '''Sets current value of asset.'''
#         self.__value = value

#     @property
#     def salvage_value(self):
#         '''Minimum (salvage) asset value.'''
#         return self.__salvage_value

#     @property
#     def replacement_value(self):
#         '''Maximum (replacement) asset value.'''
#         return self.__replacement_value

#     @property
#     def parameters(self):
#         '''Depreciation parameters.'''
#         return self.__parameters

#     @property
#     def portion_remaining(self):
#         '''Portion of asset value remaining.'''
#         value_range = self.replacement_value - self.salvage_value
#         return (self.value - self.salvage_value) / value_range

#     @property
#     def remaining_life(self):
#         '''Remaining life of asset in time periods.'''
#         inverse_ft = self.parameters.build_inverse_ft()
#         return self.parameters.n - inverse_ft(self.portion_remaining)

#     def build_depreciation_function(self) -> Callable[[Self, float], float]:
#         '''Builds depreciation function.'''
#         acceleration = self.parameters.acceleration
#         required = self.parameters.maintenance_requirement
#         if acceleration < 1.0:
#             raise ValueError(
#                 f'''Invalid acceleration value: {acceleration}.
#                 Acceleration must be >= 1.0.'''
#             )
#         def scheduler(maintenance: float) -> float:
#             '''
#             Computes time periods of depreciation, for a given amount of maintenance.
#             '''
#             if required < maintenance:
#                 raise ValueError(
#                     f'''Invalid maintenance value: {maintenance}.
#                     maintenance: {maintenance} > maintenance requirement {required}.
#                     '''
#                 )
#             # if no deferred maintenance, returns 1 time period of depreciation.
#             deferred = (required - maintenance) / required
#             return 1 + deferred * acceleration

#         ft = self.parameters.build_ft()
#         inverse_ft = self.parameters.build_inverse_ft()

#         def fx(asset: 'Asset', maintenance: float) -> float:
#             '''
#             Depreciates asset based on maintenance performed.
#             '''
#             value_range = asset.replacement_value - asset.salvage_value

#             def t_in_schedule(maintenance: float) -> float:
#                 '''Time periods of depreciation based on maintenance level.'''
#                 return inverse_ft(self.portion_remaining) + scheduler(maintenance)

#             def constrain_value(value: float) -> float:
#                 '''Constrains value to value_range.'''
#                 return max(self.salvage_value, min(self.replacement_value, value))

#             maintenance = min(maintenance, required)
#             recap = max(0.0, maintenance - required)

#             #val = self.salvage_value + value_range * ft(t_in_schedule(maintenance)) + recap
#             return constrain_value(self.salvage_value + value_range * ft(t_in_schedule(maintenance)) + recap) # pylint: disable=line-too-long
#         return fx

#     def depreciate(self, maintenance: float) -> float:
#         '''Depreciates asset value based on maintenance level.'''
#         self.__value = self.__depreciation_fx(self, maintenance)
#         return self.value


# # def build_ft(periods_in_schedule: int, shape_parameter: float):
# #     '''Builds function that computes portion depreciated value remaining as function of time.'''
# #     if shape_parameter < 0:
# #         raise ValueError('shape_parameter must be greater than 0.0.')
# #     def ft(t: float) -> float:  # pylint: disable=invalid-name
# #         '''
# #         Portion depreciable asset value remaining as function of time.

# #         Args:
# #             t (float): time period in depreciation schedule.

# #         Returns:
# #             float: portion of depreciable asset value remaining.
# #         '''
# #         if periods_in_schedule <= t:
# #             # prevents a negative result.
# #             return 0.0
# #         return (1 - t / periods_in_schedule) ** shape_parameter
# #     return ft

# # def build_inverse_ft(periods_in_schedule: float, shape_parameter: float):
# #     '''
# #     Builds function that computes time period of depreciation for a given maintenance level.
# #     '''
# #     def inverse_ft(y: float) -> float:
# #         '''
# #         Time period in schedule corresponding to given portion of depreciable asset value.

# #         Args:
# #             y (float): portion of depreciable asset value remaining.

# #         Returns:
# #             float: time period in depreciation schedule.
# #         '''
# #         if not 0.0 <= y <= 1.0:
# #             # prevents a complex result, or non-sense y values.
# #             raise ValueError(f'y: {y} must be between 0.0 and 1.0.')
# #         return periods_in_schedule * (1 - y) ** (1 / shape_parameter)
# #     return inverse_ft

# # def build_scheduler(maintenance_requirement: float,
# #                     acceleration: float) -> Callable[[float], float]:
# #     '''
# #     Builds function that computes time period of depreciation for a given maintenance level.
# #     '''
# #     if acceleration < 1:
# #         raise ValueError('acceleration must be greater than or equal to 1.0.')
# #     def scheduler(maintenance: float) -> float:
# #         '''
# #         Computes time period of depreciation for a given maintenance level.

# #         Args:
# #             maintenance (float): maintenance level.

# #         Raises:
# #             ValueError: if maintenance exceeds maintenance requirement.
# #             There is no benefit to overfunded maintenance, for this use repairs.

# #         Returns:
# #             float: time periods of depreciation.
# #         '''
# #         if maintenance_requirement < maintenance:
# #             raise ValueError('Maintenance exceeds maintenance requirement.')
# #         # if no deferred maintenance, returns 1 time period of depreciation.
# #         return 1 + (maintenance_requirement - maintenance) / maintenance_requirement * acceleration # pylint: disable=line-too-long
# #     return scheduler

# # # Estimate = NamedTuple('Estimates', [('min', float), ('actual', float), ('max', float)])

# # def build_depreciation_function(shape_parameter: float = 1.0,
# #                                 periods_in_schedule: int = 100,
# #                                 maintenance_requirement: float = 1.0,
# #                                 acceleration: float = 1.0
# #                                 ) -> Callable[['Asset', float], float]:
# #     '''Defines the general shape of the depreciation function.

# #     Args:
# #         periods_in_schedule (int): number of periods in depreciation schedule.
# #         shape_parameter (float): parameter controling shape of depreciation schedule.
# #             1.0 by default.

# #             Notes:
# #             0.0 is constant (no depreciation),
# #             1.0 is linear,
# #             > 1.0 is concave,
# #             < 1.0 is convex
# #         acceleration (float): parameter controlling acceleration of depreciation schedule.
# #             1.0 by default. Value must be greater than or equal to 1.0.

# #             Notes:
# #             1.0 is linear acceleration.

# #             Explaination:
# #             Defered maintenance can speed up deterioration (i.e., depreciation).

# #     Returns:
# #         Callable[[Asset, float, float], Estimate]:
# #         Depreciation function takes asset, maintenance arguments returns depreciated value.
# #     '''
# #     ft = build_ft(periods_in_schedule, shape_parameter)
# #     inverse_ft = build_inverse_ft(periods_in_schedule, shape_parameter)
# #     scheduler = build_scheduler(maintenance_requirement, acceleration)

# #     def depreciation_function(asset: 'Asset', maintenance: float) -> float:
# #         '''
# #         Depreciates asset value based on depreciation schedule and maintenance level.
# #         '''
# #         # setup.
# #         value_range = asset.value_range.replacement - asset.value_range.salvage
# #         def constrain_value(value: float) -> float:
# #             '''Constrains value to value_range.'''
# #             return max(asset.value_range.salvage, min(asset.value_range.replacement, value))
# #         def time(maintenance: float) -> float:
# #             '''Time periods of depreciation based on maintenance level.'''
# #             # test (value - salvage) / depreciable_value vs. value / depreciable_value
# #             return inverse_ft(asset.value/value_range) + scheduler(maintenance)

# #             # t_estimates = []
# #             # for i in range(3):
# #             #     # should the first part be (value - salvage) / depreciable_value?
# #             #     t = inverse_ft(asset.value[i]/depreciable_value) + schedulers[i](asset, maintenance)
# #             #     t_estimates.append(t)
# #             # return tuple(t_estimates)

# #         # simple calculations.
# #         maintenance = min(maintenance, maintenance_requirement)
# #         recap = max(0.0, maintenance - maintenance_requirement)
# #         return constrain_value(value_range * ft(time(maintenance))) + recap
# #         # # estimates for number of time periods of depreciation.
# #         # t_estimates = time_periods_of_depreciation(maint)
# #         # return tuple([constrain_value(depreciable_value * ft(t) + recap) for t in t_estimates])
# #     return depreciation_function

# # ValueRange = NamedTuple('ValueRange', [('salvage', float), ('replacement', float)])

# # class Asset:
# #     '''Depreciable asset.'''
# #     def __init__(self, init_value: float, salvage_value: float, replacement_value: float,
# #                  maintenance_requirement: float, inverse_ft: Callable[[float], float],
# #                  depreciation_fx: Callable[[Self, float], float]) -> None:
# #         '''
# #         Initializes an asset.
# #         '''
# #         self.value = init_value
# #         self.value_range = ValueRange(salvage_value, replacement_value)
# #         self.__inverse_ft = inverse_ft
# #         self.__depreciation_fx = depreciation_fx
# #         self.__maintenance_requirement = maintenance_requirement

# #     # def __init__(self,
# #     #              init_value: float = 100.0,
# #     #              salvage_value: float = 0.0,
# #     #              replacement_value: float = 100.0,
# #     #              maintenance_requirement: float = 1.0,
# #     #              depreciation_shape_parameter: float = 1.0,
# #     #              periods_in_depreciation_schedule: int = 100,
# #     #              depreciation_acceleration: float = 1.0) -> None:
# #     #     '''
# #     #     Initializes an asset.

# #     #     Args:
# #     #         init_value (float):
# #     #             initial value of asset.
# #     #         salvage_value (float):
# #     #             minimum (salvage) asset value.
# #     #         replacement_value (float):
# #     #             maximum (replacement) asset value.
# #     #         maintenance_requirement (float):
# #     #             maintenance requirement per time period.
# #     #         depreciation_shape_parameter (float):
# #     #             parameter controling shape of depreciation schedule.
# #     #             1.0 by default.

# #     #             Notes:
# #     #             0.0 is constant (no depreciation),
# #     #             1.0 is linear,
# #     #             > 1.0 is concave,
# #     #             < 1.0 is convex

# #     #         periods_in_depreciation_schedule (int):
# #     #             number of periods in depreciation schedule.
# #     #         depreciation_acceleration (float):
# #     #             parameter controlling acceleration of depreciation schedule,
# #     #             when required maintenance is not performed.
# #     #             1.0 by default. Value must be greater than or equal to 1.0.

# #     #             Notes:
# #     #             1.0 is linear acceleration.
# #     #             > 1.0 if faster than linear acceleration.

# #     #             Explaination:
# #     #             Defered maintenance can speed up deterioration (i.e., depreciation).

# #     #     '''
# #     #     self.value = init_value
# #     #     self.value_range = ValueRange(salvage_value, replacement_value)

# #     #     self.__k = depreciation_shape_parameter
# #     #     self.__n = periods_in_depreciation_schedule
# #     #     self.__acceleration = depreciation_acceleration
# #     #     self.__maintenance_requirement = maintenance_requirement

# #     #     # self.__ft = build_ft(
# #     #     #     self.__n, self.__k)
# #     #     self.__inverse_ft = build_inverse_ft(
# #     #         self.__n, self.__k)
# #     #     # self.__scheduler = build_scheduler(
# #     #     #     self.__maintenance_requirement, self.__acceleration)
# #     #     self.__depreciation_fx = build_depreciation_function(
# #     #         self.__k, self.__n,
# #     #         self.__maintenance_requirement, self.__acceleration)

# #     #     self.__total_maintenance = 0.0

# #     @property
# #     def portion_remaining(self):
# #         '''Portion of asset value remaining.'''
# #         value_range = self.value_range.replacement - self.value_range.salvage
# #         return (self.value - self.value_range.salvage) / value_range

# #     @property
# #     def remaining_life(self):
# #         '''Remaining life of asset in time periods.'''
# #         return self.__inverse_ft(self.portion_remaining)

# #     def depreciate(self, maintenance: float) -> None:
# #         '''Depreciates asset value based on maintenance level.'''
# #         recap = max(0.0, maintenance - self.__maintenance_requirement)
# #         self.value = self.__depreciation_fx(self, maintenance - recap) + recap

# # class UncertainAsset:
# #     '''
# #     Depreciable asset with uncertainty.
# #     Holds a list of assets representing different possible states of the asset.
# #     '''
# #     def __init__(self, assets: list[Asset]) -> None:
# #         '''
# #         Initializes an uncertain asset.

# #         Args:
# #             assets (list[Asset]): list of assets
# #                 representing different possible states of the asset.
# #         '''
# #         self.assets = assets

# # @datclass

# # def factory(
# #         init_value: float = 100.0,
# #         salvage_value: float = 0.0,
# #         replacement_value: float = 100.0,
# #         maintenance_requirement: float = 1.0,
# #         depreciation_periods: float = 100,
# #         depreciation_shape_parameter: float = 1.0,
# #         decpreciation_acceleration: float = 1.0) -> Asset:
# #     '''
# #     Factory function for creating an asset.

# #     Args:
# #         init_value (float):
# #             initial value of asset.
# #         salvage_value (float):
# #             minimum (salvage) asset value.
# #         replacement_value (float):
# #             maximum (replacement) asset value.
# #         maintenance_requirement (float):
# #             maintenance requirement per time period.
# #         depreciation_shape_parameter (float):
# #             parameter controling shape of depreciation schedule.
# #             1.0 by default.

# #             Notes:
# #             0.0 is constant (no depreciation),
# #             1.0 is linear,
# #             > 1.0 is concave,
# #             < 1.0 is convex

# #         depreciation_periods (float):
# #             number of periods in depreciation schedule, 100 by default.
# #         depreciation_acceleration (float):
# #             parameter controlling acceleration of depreciation schedule,
# #             when required maintenance is not performed.
# #             1.0 by default. Value must be greater than or equal to 1.0.

# #             Notes:
# #             1.0 is linear acceleration.
# #             > 1.0 if faster than linear acceleration.

# #             Explaination:
# #             Defered maintenance can speed up deterioration (i.e., depreciation).
# #     Returns:
# #         Asset: asset object.
# #     '''
# #     inverse_ft = build_inverse_ft(
# #         periods_in_schedule=depreciation_periods,
# #         shape_parameter=depreciation_shape_parameter)
# #     depreciation_fx = build_depreciation_function(
# #         shape_parameter=depreciation_shape_parameter,
# #         periods_in_schedule=depreciation_periods,
# #         maintenance_requirement=maintenance_requirement,
# #         acceleration=decpreciation_acceleration)
# #     return Asset(init_value=init_value,
# #                  salvage_value=salvage_value, replacement_value=replacement_value,
# #                  maintenance_requirement=maintenance_requirement,
# #                  inverse_ft=inverse_ft, depreciation_fx=depreciation_fx)


# # def factory_uncertain_acceleration(
# #         asset: Asset,
# #         acceleration: list[float]) -> UncertainAsset:
# #     '''
# #     Builds an uncertain asset with different acceleration values.
# #     '''
# #     assets = []
# #     for i, val in enumerate(acceleration):
# #         # this could be very slow.
# #         asset_copy = copy.deepcopy(asset)

# #         asset.depreciation_acceleration = val
# #         acceleration[i] = asset

# #     # def best_case(self) -> float:
# #     #     '''Best case asset value.'''
# #     #     depreciation_fx = build_depreciation_function(
# #     #         self.__k, self.__n,
# #     #         self.__maintenance_requirement, acceleration=1.0)
# #     #     maintenance = self.__total_maintenance % self.__maintenance_requirement
# #     #     return depreciation_fx(self, maintenance)

# # # @dataclass
# # # class Asset:
# # #     '''Depreciable asset utility class.'''
# # #     salvage_value: float = 0.0
# # #     '''Minimum (salvage) asset value.'''
# # #     replacement_value: float = 100.0
# # #     '''Maximum (replacement) asset value.'''
# # #     maintenance_requirement: float = 1.0
# # #     '''Maintenance requirement per time period.'''
# # #     periods_in_depreciation_schedule: int = 100
# # #     '''Number of periods in depreciation schedule.'''
# # #     depreciation_shape_parameter: float = 1.0
# # #     '''Parameter controling shape of depreciation schedule.'''
# # #     depreciation_acceleration: float = 1.0
# # #     '''
# # #     Parameter controlling acceleration of depreciation schedule,
# # #     when required maintenance is not performed.
# # #     '''

# # #     def __post_init__(self):
# # #         self.__depreciation_fx = build_depreciation_function(
# # #             self.depreciation_shape_parameter,
# # #             self.periods_in_depreciation_schedule,
# # #             self.depreciation_acceleration
# # #         )

# # #     def depreciate

# # # ValueRange = NamedTuple('ValueRange', [('salvage', float), ('replacement', float)])

# # # class Asset:
# # #     '''Depreciable asset.'''
# # #     maintenance_requirement: float = 1.0
# # #     '''Maintenance requirement per time period.'''
# # #     value_range: ValueRange = ValueRange(0.0, 100.0)
# # #     '''Asset minimum (salvage) and maximum (replacement) values.'''

# # #     def __init__(self, init_value: float = 100.0,
# # #                  salvage_value: float = 0.0, replacement_value: float = 100.0,
# # #                  depreciation_fx: Callable[[Self, float], Estimate] = build_depreciation_function(),
# # #                  maintenance_requirement: float = 1.0) -> None:
# # #         '''
# # #         Initializes an asset.

# # #         Args:
# # #             init_value (float): initial value of asset.
# # #             salvage_value (float): minimum (salvage) asset value.
# # #             replacement_value (float): maximum (replacement) asset value.
# # #             depreciation_fx (Callable[[Self, float], Estimate]): function to compute depreciation.
# # #             maintenance_requirement (float): maintenance requirement per time period.
# # #         '''
# # #         self.value = init_value
# # #         self.salvage_value = salvage_value
# # #         self.replacement_value = replacement_value
# # #         self.__depreciation_function = depreciation_fx
# # #         self.maintenance_requirement = maintenance_requirement

# # #     def depreciate(self, maintenance: float) -> Estimate:
# # #         '''Depreciates asset value based on maintenance level.'''
# # #         return self.__depreciation_function(self, maintenance)
