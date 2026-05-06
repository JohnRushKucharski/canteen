# PRD: Multi-Timestep Reservoir Simulation

## Problem Statement

Users need to evaluate reservoir operations over extended periods (days, months, years) given historical or forecasted inflow timeseries. Currently, the codebase only supports single-timestep operations (`reservoir.operate(inflow)`), requiring users to manually write simulation loops, track state, and aggregate results. This creates friction for the primary use case: analyzing how a reservoir behaves under different operational strategies and inflow scenarios.

## Solution

Add a simulation orchestration layer that:
1. Accepts a reservoir and inflow timeseries
2. Runs the reservoir through multiple timesteps automatically
3. Returns structured results (storage, inflows, outflows) in a format ready for analysis (numpy structured array, convertible to pandas/polars)

The simulation layer is separate from reservoir physics—it orchestrates single-timestep operations without modifying the core domain model.

## User Stories

1. As a water resources engineer, I want to simulate a reservoir over a 365-day period with daily inflows, so that I can evaluate annual water balance
2. As a researcher, I want simulation results as a pandas DataFrame, so that I can plot storage and outflows over time
3. As a developer, I want to reuse a reservoir for multiple simulation scenarios without manually resetting state, so that scenario comparison is simple
4. As a modeler, I want the simulation to validate that storage never goes negative or exceeds capacity, so that I catch operational strategy bugs early
5. As a user, I want to simulate with negative inflows (representing evaporation/seepage), so that I can model realistic water losses
6. As an analyst, I want to pass empty inflows and get an empty result, so that edge cases don't break my automation
7. As a developer, I want per-outlet outflow tracking by name, so that I can analyze which gates released how much water
8. As a scientist, I want optional timestamp labels on results, so that I can align simulation output with calendar dates
9. As a modeler, I want to extend simulations with custom metrics (elevation, pool states), so that I can track domain-specific values (future enhancement)
10. As a developer, I want to construct reservoirs via a builder pattern, so that invalid states (missing operations, None checks) are unrepresentable
11. As a Python developer, I want factory functions to use the builder internally, so that simple cases remain convenient
12. As a strategy pattern user, I want to decorate Operations strategies with additional behavior (hedging rules), so that I can extend operations without modifying existing strategies
13. As a tester, I want `reservoir.operate()` to mutate storage automatically, so that simulation loops don't need to manually update state
14. As a user, I want outlets, pools, and mappings to default to empty containers (never None), so that strategies don't need defensive None checks
15. As a performance-conscious user, I want simulations to use pre-allocated numpy arrays, so that 10,000-timestep simulations run efficiently
16. As a data analyst, I want converter functions (to_pandas, to_polars), so that I can use my preferred DataFrame library
17. As a domain modeler, I want all new terms (Simulation, Timestep, Metric, ReservoirBuilder) documented in CONTEXT.md, so that terminology is consistent
18. As a maintainer, I want comprehensive unit tests for simulation, builder, and storage mutation, so that core functionality is reliable
19. As a quality-focused developer, I want a final integration/performance/coverage test suite, so that I can measure baseline performance and coverage before optimization
20. As a user, I want clear error messages when reservoir has no operations, storage goes negative, or storage exceeds capacity, so that I can debug configuration issues quickly

## Implementation Decisions

### Module Structure
- **simulation.py (new)**: Contains `simulate()` function, `to_pandas()` and `to_polars()` converters
- **metrics.py (new, future)**: Contains `Metric` protocol and built-in metric implementations (not MVP)
- **reservoir.py (modified)**: Add `ReservoirBuilder` class, update `BaseReservoir.operate()`, update factory
- **operations.py (modified)**: Add example Decorator implementation (e.g., `HedgingOperationsDecorator`)

### ReservoirBuilder Pattern
- New `ReservoirBuilder` class accumulates components via `add_operations()`, `add_outlets()`, `add_pools()`, `add_mappings()`
- `build()` validates completeness (operations required) and constructs immutable `BaseReservoir`
- `BaseReservoir` loses `add_*` methods—they belong to the builder
- Optional components (outlets, pools, mappings) default to empty Null Objects (never None)
- Factory functions (`reservoir.factory()`) use builder internally: construct builder, call add methods, return `build()` result
- This ensures invalid states are unrepresentable and eliminates None checks throughout codebase

### Storage Mutation in operate()
- `BaseReservoir.operate(inflow)` now mutates `self.storage` after calling the Operations strategy
- Flow: call `operations.operate(self, inflow)` → get outflows tuple → update `self.storage = storage + inflow - sum(outflows)` → return outflows
- Operations strategies remain pure functions (no storage mutation)—mutation responsibility is in BaseReservoir
- This simplifies simulation loop: just call `operate(inflow)` repeatedly without manual storage tracking

### Decorator Pattern for Operations
- Add concrete example showing how to wrap an Operations strategy with behavioral modifications
- Example: `HedgingOperationsDecorator` wraps SOP and reduces releases when storage is in a critical range
- Demonstrates: Decorator accepts base Operations in constructor, implements Operations interface, delegates to base with modifications
- Shows extension point for salinity checks, adaptive policies, etc. without modifying core strategies

### Simulation Interface
- `simulate(reservoir: Reservoir, inflows: Sequence[float] | np.ndarray, timestamps: Sequence[Any] | None = None) -> np.ndarray`
- Copies reservoir internally (via `copy.copy()`) so original is unchanged
- Pre-allocates numpy structured array with columns: `['timestep', 'inflow', 'storage', <outlet_names...>, 'spill']`
- Outlet column names dynamically extracted from `reservoir.outlets` (e.g., "Spillway", "Gate")
- Loops over inflows, calls `reservoir_copy.operate(inflow)`, records results in array
- If timestamps provided, use them as timestep labels; otherwise integer indices (0, 1, 2, ...)
- Returns numpy structured array (named columns, efficient access via `result['storage']`)

### Result Schema
- **MVP columns**: timestep (int or timestamp), inflow (float), storage (float), one column per outlet (float), spill (float)
- **End-of-timestep storage**: Only record storage after operation (start storage is previous timestep's end or initial value)
- **Extensible schema (future)**: Metrics can add columns (elevation, pool state, total outflow)—not in MVP

### Error Handling
- Validate `reservoir.operations is not None` at start of simulate(), raise ValueError with message
- Allow negative inflows (evaporation is valid)
- After each timestep, assert `0 <= storage <= capacity`, raise detailed error with timestep info if violated
- Empty inflows edge case: return empty numpy array with correct dtype (valid scenario)

### Converters
- `to_pandas(result: np.ndarray) -> pd.DataFrame`: Convert structured array to pandas DataFrame
- `to_polars(result: np.ndarray) -> pl.DataFrame`: Convert to polars DataFrame (optional dependency)
- Simple functions, not methods—no wrapper class for MVP
- Import pandas/polars inside converter functions (fail gracefully if not installed)

### Dependencies
- Add numpy as core dependency (already used in scientific Python ecosystem)
- pandas and polars remain optional (only needed for converters)

### Null Object Pattern Enforcement
- All container components (Outlets, Pools, Mappings) implement Null Object pattern
- `BaseReservoir` defaults: `outlets=Outlets([])`, `pools=Pools([])`, `mappings=Mappings([])`
- Never use `None` for optional components—always use empty containers
- Strategies can iterate/query without `if is None` checks

## Testing Decisions

### What Makes a Good Test
- Test external behavior only (public API), not implementation details
- Use TDD: write test first, implement until green, refactor
- Each test should be independent and deterministic
- Test names should describe the scenario and expected outcome

### Modules to Test (TDD)
1. **simulation.py**: Full coverage
   - Basic simulation with no outlets (just spill)
   - Simulation with multiple outlets
   - Empty inflows edge case
   - Negative inflows (valid)
   - Negative storage error case
   - Storage exceeds capacity error case
   - Reservoir with no operations error case
   - Optional timestamps parameter
   - to_pandas converter
   - to_polars converter (conditional on polars installed)

2. **ReservoirBuilder**: Full coverage
   - Incremental construction (add operations, outlets, pools, mappings)
   - build() validates operations is required
   - build() creates BaseReservoir with Null Objects for optional components
   - Factory function uses builder internally
   - Cannot build without operations

3. **BaseReservoir.operate()**: Update existing tests
   - Verify storage mutation after operation
   - Verify outflows returned correctly
   - Test with PassiveOperations
   - Test with multiple outlets
   - Test storage calculation: storage + inflow - sum(outflows)

4. **HedgingOperationsDecorator**: Basic pattern demonstration
   - Decorator wraps base Operations
   - Modifies behavior based on condition (e.g., storage in hedging range)
   - Delegates to base operations

5. **Integration/Performance/Coverage (final issue)**
   - Measure current test coverage percentage (baseline)
   - Measure performance of 10,000-timestep simulation (baseline)
   - Set coverage targets based on baseline (e.g., maintain or increase by 5%)
   - Set performance targets based on baseline (e.g., < 1 second for 10k timesteps)
   - Integration test: end-to-end simulation with realistic reservoir configuration
   - Stress test: large inflow arrays (100k+ timesteps)

### Prior Art
- Existing tests in `tests/test_operations.py` show pattern for Operations testing
- Existing tests in `tests/test_reservoir.py` show pattern for Reservoir testing
- Existing tests use pytest, follow same conventions

## Out of Scope

### Not in this PRD
- **Units handling**: Assume float inputs only (no Quantity objects). Units validation deferred to future work
- **Pandas/polars as required dependencies**: They remain optional; converters fail gracefully if not installed
- **Metrics implementation**: Metric protocol and built-in metrics are designed but not implemented (blocked until simulation MVP is stable)
- **Multi-reservoir simulation**: Single reservoir only; system-level simulation deferred
- **Adaptive time-stepping**: Fixed timestep intervals only (ODE formulation is future work per TODO.md)
- **Optimization integration**: Single objective optimization framework is separate feature (TODO.md Focus 4A)
- **Plugin system updates**: Existing plugin architecture in `old/` is reference only; porting deferred

### Will Be Separate Issues (Post-MVP)
- Metric system implementation (blocked by this PRD)
- Performance optimization of simulation loop (e.g., numba JIT)
- Parallel scenario execution
- Streaming/incremental simulation for large datasets
- Time-series alignment helpers for pandas Series inflows

## Further Notes

### Architectural Alignment
This PRD aligns with existing ADRs:
- **ADR-0001**: Three-tier plugin architecture—simulation is orchestration tier
- **ADR-0002**: Reservoir as Strategy pattern context—ReservoirBuilder ensures strategy is always present
- **ADR-0003**: Null Object for optional components—builder enforces this pattern

### Breaking Changes
- `BaseReservoir.add_*()` methods removed (move to ReservoirBuilder)—existing code using incremental construction must update to builder pattern
- `BaseReservoir.operate()` now mutates storage—existing code expecting immutable operate must update (minimal impact, this was already documented intent)
- Optional components no longer accept None—must use empty containers (Outlets([]), etc.)

### Migration Path
Existing code using factory functions continues to work (factory uses builder internally). Code using `BaseReservoir` constructor directly or `add_*` methods needs updates:

**Before**:
```python
res = BaseReservoir(name="Dam", storage=50, capacity=100)
res.add_operations(PassiveOperations())
```

**After**:
```python
builder = ReservoirBuilder(name="Dam", storage=50, capacity=100)
builder.add_operations(PassiveOperations())
res = builder.build()
```

Or use factory:
```python
res = reservoir.factory(name="Dam", storage=50, capacity=100, operations=PassiveOperations())
```

### Example Usage (Acceptance Criteria)

**Basic simulation**:
```python
from canteen import reservoir, operations
from canteen.simulation import simulate, to_pandas

# Create reservoir
res = reservoir.factory(
    name="Example Dam",
    storage=50.0,
    capacity=100.0,
    operations=operations.factory()  # PassiveOperations
)

# Run simulation
inflows = [10.0, 20.0, 15.0, -5.0, 30.0]
result = simulate(res, inflows)

# Access results
print(result['storage'])  # [60.0, 80.0, 95.0, 90.0, 100.0]
print(result['spill'])     # [0.0, 0.0, 0.0, 0.0, 20.0]

# Convert to DataFrame
df = to_pandas(result)
df.plot(x='timestep', y='storage')
```

**With outlets**:
```python
from canteen import reservoir, operations, outlet
from canteen.outlet import Outlets, ReleaseRange
from canteen.simulation import simulate

gate = outlet.factory(name="Gate", location=80.0, design_range=ReleaseRange(0, 15))
res = reservoir.factory(
    name="Dam with Gates",
    storage=50.0,
    capacity=100.0,
    operations=operations.factory(),
    outlets=Outlets([gate])
)

result = simulate(res, inflows=[20.0, 30.0])
# result columns: ['timestep', 'inflow', 'storage', 'Gate', 'spill']
print(result['Gate'])  # Releases through gate outlet
```

**With decorator**:
```python
from canteen.operations import PassiveOperations, HedgingOperationsDecorator

base_ops = PassiveOperations()
hedging_ops = HedgingOperationsDecorator(
    base=base_ops,
    hedging_range=(40, 60),
    reduction_factor=0.8
)

res = reservoir.factory(name="Hedged", storage=50, capacity=100, operations=hedging_ops)
result = simulate(res, inflows)
# When storage in [40, 60], releases reduced by 20%
```
