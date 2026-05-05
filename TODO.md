# Canteen Development Roadmap - TODO List

## Current Status
**COMPLETED**
- [x] Pool protocol and basic implementations (StaticPool, VariablePool)
- [x] Factory function with simplified API (single location parameter)
- [x] Type safety with StaticPool `__post_init__` fix
- [x] Simplified `create_rule_curve` with breakpoint-based data structure
- [x] Fractional day support for sub-daily calculations
- [x] Comprehensive unit tests for all components (206 tests passing)
- [x] Integration tests for rule curves + VariablePool
- [x] Full linting and type checking compliance (mypy strict mode)
- [x] Comprehensive validation system with type compatibility checking

---

## Development Focus Areas

### **FOCUS 1: Pool-Based Operations & Standard Operating Policy (SOP)**
*Priority: HIGH - Core functionality for reservoir operations*

- [ ] **1A**: Add pools collection to `ReservoirComponents` 
  - [ ] Implement `pools: tuple[Pool, ...]` field (sorted by location, largest to smallest)
  - [ ] Add pool validation and type compatibility checking
  - [ ] Pool sorting implementation (decide: tuple vs custom iterable - see Questions)

- [ ] **1B**: Create `StandardOperatingPolicy` class
  - [ ] Implement `Operations` interface with `operate(reservoir, inflow, demand)` method
  - [ ] Pool-based release logic: meet demand, spill only when necessary
  - [ ] Support multiple pool scenarios (flood/conservation/inactive)
  - [ ] Integration with existing outlet constraints
  - [ ] Numeric type support (int/float) like `PassiveOperations`

- [ ] **1C**: SOP Test Scenarios (5 comprehensive test cases)
  - [ ] Test 1: One StaticPool, no outlets - spill only if (storage + inflow - capacity) > demand
  - [ ] Test 2: One StaticPool, one outlet - outlet location constrains releases
  - [ ] Test 3: Multiple StaticPools, no outlets - flood/conservation/inactive pool logic
  - [ ] Test 4: Multiple StaticPools with outlets - outlet constraints on pool releases
  - [ ] Test 5: Replace conservation pool with VariablePool - test sorting validation

**Architectural Questions (Need Input):**
- Pool Storage: Tuple vs Custom Iterable? (frequency of modification, iteration behavior)
- Operations Component Selection: Builder pattern vs Configuration vs Method parameters?
- Component selection at creation time or execution time?

---

### **FOCUS 2: Operations Architecture Enhancement**
*Priority: MEDIUM - Improve flexibility and component selection*

- [ ] **2A**: Operations Component Selection System
  - [ ] Design pattern for Operations to use/ignore specific ReservoirComponents
  - [ ] Implementation options: Builder pattern, Configuration object, Method parameters, or Specialized classes
  - [ ] Support mixed operations (PassiveOperations + SOP for different pools)

- [ ] **2B**: Advanced Operations Features
  - [ ] Runtime component filtering capabilities
  - [ ] Type safety for component compatibility
  - [ ] Error handling for invalid component configurations

---

### **FOCUS 3: Plugin Architecture Migration**
*Priority: MEDIUM - Modernize extensibility system*

- [ ] **3A**: Modern Plugin System Design
  - [ ] Protocol-based plugin interfaces for type safety
  - [ ] Entry points or decorator-based registration (vs file discovery)
  - [ ] Plugin metadata and validation system
  - [ ] Configurable plugin directories and namespace management

- [ ] **3B**: Plugin Categories & Examples
  - [ ] Support operations, outlets, reservoirs, pools
  - [ ] Create demonstration plugins:
    - Updated pool-based operations plugin using new SOP architecture
    - Custom outlet plugin with advanced release logic
    - Specialized reservoir plugin with extended functionality
  - [ ] Plugin documentation and development guide

**Legacy System Issues to Address:**
- Hard-coded paths, global state, no type safety
- Manual imports, poor error handling, no metadata
- Module conflicts between plugin directories

---

### **FOCUS 4: Simulation Optimization & Dynamic Time-Stepping**
*Priority: MEDIUM-HIGH - Advanced simulation capabilities*

- [ ] **4A**: Single Objective Optimization Framework
  - [ ] **Objective Functions**: Interface for simulation goals (maximize storage, minimize spill, etc.)
  - [ ] **Constraints System**: Define operational limits (no spill releases, minimum flows, etc.)
  - [ ] **Decision Variables**: Parameterize operational components (pool locations, release rules)
  - [ ] **Optimization Integration**: Interface with scipy.optimize or similar solvers
  - [ ] **Multi-Period Operations**: Handle optimization across multiple time periods

- [ ] **4B**: Dynamic Time-Stepping & ODE Formulation
  - [ ] **ODE-Based Operations**: Formulate reservoir operations as differential equations
  - [ ] **Adaptive Time-Stepping**: Variable time steps based on system dynamics
  - [ ] **SciPy Integration**: Interface with scipy.integrate solvers (solve_ivp, etc.)
  - [ ] **Continuous vs Discrete**: Hybrid formulations for different operation types
  - [ ] **Performance Analysis**: Compare ODE vs discrete time-step approaches

- [ ] **4C**: Optimization-Simulation Integration
  - [ ] **Simulation Engine**: Multi-period simulation with configurable operations
  - [ ] **Sensitivity Analysis**: Parameter sensitivity for optimization guidance
  - [ ] **Optimization Algorithms**: Support different solver types (gradient-based, metaheuristic)
  - [ ] **Result Analysis**: Post-optimization analysis and visualization tools

**Analysis Required:**
- Mathematical formulation of reservoir operations as ODEs
- Optimization variable parameterization strategies
- Solver selection criteria and performance trade-offs
- Integration patterns between optimization and simulation

---

### **FOCUS 5: Asset Modeling & Condition Tracking**
*Priority: MEDIUM - Infrastructure asset management and failure modeling*

- [ ] **5A**: Asset Condition Framework
  - [ ] **Condition Tracking**: Extend existing `Asset` class from legacy code to support reservoir components
  - [ ] **Condition Models**: Implement depreciation-based, inspection-based, and event-exposure condition tracking
  - [ ] **Performance Impact**: Define how condition affects component properties (capacity reduction, flow limits, etc.)
  - [ ] **Failure Modeling**: Probabilistic failure models based on condition and exposure events
  - [ ] **Cascade Effects**: Model failure propagation between connected components

- [ ] **5B**: Asset Integration Architecture  
  - [ ] **Component-Asset Relationship**: Design bidirectional relationship between reservoirs/components and assets
  - [ ] **Condition Aggregation**: Aggregate component conditions to reservoir-level condition metrics
  - [ ] **Maintenance Scheduling**: Resource allocation for inspection and maintenance activities
  - [ ] **Event Impact Tracking**: Track how operational events (floods, extreme releases) affect asset condition
  - [ ] **Performance Degradation**: Dynamic property modification based on current asset condition

- [ ] **5C**: Asset Failure & Cascade System
  - [ ] **Failure Probability**: Dynamic failure probability based on condition, exposure, and operational stress
  - [ ] **Failure Trigger Events**: Define events that can trigger failures (inflow > threshold, etc.)
  - [ ] **Component Dependencies**: Model how outlet failure affects other outlets or reservoir operations
  - [ ] **Cascade Propagation**: Implement failure cascade logic within ReservoirComponents
  - [ ] **Recovery Modeling**: Asset repair/replacement mechanics and timeline

**Core Requirements Analysis:**
- **Condition Factors**: (a) Inspection/maintenance resources and schedules, (b) Depreciation schedules, (c) Event exposure history
- **Performance Effects**: (a) Property changes (capacity reduction, flow limits), (b) Failure probability increases
- **Cascade Effects**: Failure of one component increases failure probability of connected components

**Architecture Questions (Need Deep Analysis):**
1. **Required Elements**: What variables, attributes, classes needed for comprehensive asset modeling?
2. **Asset Organization**: How should condition tracking be structured within an asset framework?
3. **Condition Tracking**: Best methods for tracking multi-factor condition changes over time?
4. **Component-Asset Relationship**: Should `Reservoir`/`ReservoirComponents` be asset components, or should assets be reservoir components?
5. **Failure Modeling**: Discrete event-based vs continuous probability-based failure models?
6. **Cascade Implementation**: How to efficiently model and propagate failure cascades through component networks?
7. **Maintenance Integration**: How to integrate maintenance/inspection schedules with operational simulations?
8. **Legacy Migration**: How to extend existing `Asset`, `Lifetime`, `Values` classes for reservoir-specific needs?

**Legacy Asset System Analysis:**
- **Existing Classes**: `Asset`, `Lifetime`, `Values` with depreciation functions
- **Depreciation Models**: Linear and cascading depreciation with shape parameters
- **Time Units**: Support for time-based and production-based useful life
- **Value Tracking**: Current, initial, salvage values with accumulated depreciation
- **Extension Needs**: Multi-factor condition models, failure probability, component relationships

**Design Considerations:**
- **Flexibility**: Support different condition models for different component types
- **Performance**: Efficient condition updates during simulation
- **Extensibility**: Plugin-based condition models and failure mechanisms
- **Integration**: Seamless integration with existing reservoir/component architecture
- **Validation**: Type safety and constraint validation for asset relationships

---

### **FOCUS 6: Technical Improvements**
*Priority: LOW - Polish and optimization*

- [ ] **6A**: `create_rule_curve` Refinements
  - [ ] Fix validation logic bugs and boundary conditions
  - [ ] Add better error messages and warnings

- [ ] **6B**: Performance & Features
  - [ ] Rule curve interpolation caching
  - [ ] Support for leap years (366 days)
  - [ ] Alternative interpolation methods (cubic spline)

- [ ] **6C**: Documentation & Integration
  - [ ] Update module docstrings with examples
  - [ ] Add usage examples to README
  - [ ] Better integration patterns exploration

---

## Recommended Development Sequence

1. **Start with FOCUS 1** (Pool-Based SOP) - Core functionality needed
2. **Answer architectural questions** for pool storage and operations selection
3. **Complete SOP implementation and testing** before moving to next focus
4. **Move to FOCUS 2** (Operations Architecture) - Build on SOP learnings
5. **Choose between FOCUS 3, FOCUS 4, or FOCUS 5** based on priorities:
   - **FOCUS 3** (Plugin Architecture) - For extensibility and modularity
   - **FOCUS 4** (Optimization) - For advanced simulation capabilities  
   - **FOCUS 5** (Asset Modeling) - For infrastructure management and failure modeling
6. **Finish with FOCUS 6** (Polish) - Final improvements

## Technical Reference

### Pool-Based SOP Architecture Details
**Core Components:**
- `ReservoirComponents.pools: tuple[Pool, ...]` - sorted largest to smallest location
- `StandardOperatingPolicy` class with `operate(reservoir, inflow, demand)` method
- Pool validation functions similar to outlet validation
- Integration with existing `Operations` protocol

**Pool Operation Logic:**
1. **Flood Pool** (top): Release max(storage + inflow - conservation_location, demand)
2. **Conservation Pool** (middle): Release demand if sufficient water, otherwise available water
3. **Inactive Pool** (bottom): No releases allowed
4. **Outlet Integration**: Outlet location constraints override pool logic when applicable

### Legacy Plugin Architecture Analysis
**Current System Strengths:**
- Clear separation: Operations, outlets, reservoirs as distinct plugin types
- Simple discovery: File-based plugin discovery with glob patterns
- Initialize pattern: Consistent `initialize()` function returns plugin registry
- Flexible loading: Load single plugin, module, or all plugins by type

**Current System Issues:**
- Hard-coded paths, global state, no type safety
- Manual imports, poor error handling, no metadata
- Module conflicts between `/canteen/plugins` and `/plugins`

### Architecture Options for Discussion

**Pool Storage: Tuple vs Custom Iterable**
- Tuple: Simple, immutable, consistent with outlets ✅ | Limited extensibility ❌
- Custom Iterable: Better encapsulation, extensible ✅ | More complex ❌

**Operations Component Selection Patterns**
- Builder: `ops.with_pools().without_outlets()`
- Configuration: `OperationsConfig(use_pools=True)`
- Method Parameters: `operate(reservoir, use_components=['pools'])`
- Specialized Classes: `PoolOnlyOperations` vs `FullOperations`

---
*Last updated: September 11, 2025*
*Total tests: 206 (all passing)*

---

### 🏭 **FOCUS 5: Asset Modeling & Condition Tracking**
*Priority: MEDIUM - Infrastructure asset management and failure modeling*

- [ ] **5A**: Asset Condition Framework
  - [ ] **Condition Tracking**: Extend existing `Asset` class from legacy code to support reservoir components
  - [ ] **Condition Models**: Implement depreciation-based, inspection-based, and event-exposure condition tracking
  - [ ] **Performance Impact**: Define how condition affects component properties (capacity reduction, flow limits, etc.)
  - [ ] **Failure Modeling**: Probabilistic failure models based on condition and exposure events
  - [ ] **Cascade Effects**: Model failure propagation between connected components

- [ ] **5B**: Asset Integration Architecture  
  - [ ] **Component-Asset Relationship**: Design bidirectional relationship between reservoirs/components and assets
  - [ ] **Condition Aggregation**: Aggregate component conditions to reservoir-level condition metrics
  - [ ] **Maintenance Scheduling**: Resource allocation for inspection and maintenance activities
  - [ ] **Event Impact Tracking**: Track how operational events (floods, extreme releases) affect asset condition
  - [ ] **Performance Degradation**: Dynamic property modification based on current asset condition

- [ ] **5C**: Asset Failure & Cascade System
  - [ ] **Failure Probability**: Dynamic failure probability based on condition, exposure, and operational stress
  - [ ] **Failure Trigger Events**: Define events that can trigger failures (inflow > threshold, etc.)
  - [ ] **Component Dependencies**: Model how outlet failure affects other outlets or reservoir operations
  - [ ] **Cascade Propagation**: Implement failure cascade logic within ReservoirComponents
  - [ ] **Recovery Modeling**: Asset repair/replacement mechanics and timeline

**Core Requirements Analysis:**
- **Condition Factors**: (a) Inspection/maintenance resources and schedules, (b) Depreciation schedules, (c) Event exposure history
- **Performance Effects**: (a) Property changes (capacity reduction, flow limits), (b) Failure probability increases
- **Cascade Effects**: Failure of one component increases failure probability of connected components

**Architecture Questions (Need Deep Analysis):**
1. **Required Elements**: What variables, attributes, classes needed for comprehensive asset modeling?
2. **Asset Organization**: How should condition tracking be structured within an asset framework?
3. **Condition Tracking**: Best methods for tracking multi-factor condition changes over time?
4. **Component-Asset Relationship**: Should `Reservoir`/`ReservoirComponents` be asset components, or should assets be reservoir components?
5. **Failure Modeling**: Discrete event-based vs continuous probability-based failure models?
6. **Cascade Implementation**: How to efficiently model and propagate failure cascades through component networks?
7. **Maintenance Integration**: How to integrate maintenance/inspection schedules with operational simulations?
8. **Legacy Migration**: How to extend existing `Asset`, `Lifetime`, `Values` classes for reservoir-specific needs?

**Legacy Asset System Analysis:**
- **Existing Classes**: `Asset`, `Lifetime`, `Values` with depreciation functions
- **Depreciation Models**: Linear and cascading depreciation with shape parameters
- **Time Units**: Support for time-based and production-based useful life
- **Value Tracking**: Current, initial, salvage values with accumulated depreciation
- **Extension Needs**: Multi-factor condition models, failure probability, component relationships

**Design Considerations:**
- **Flexibility**: Support different condition models for different component types
- **Performance**: Efficient condition updates during simulation
- **Extensibility**: Plugin-based condition models and failure mechanisms
- **Integration**: Seamless integration with existing reservoir/component architecture
- **Validation**: Type safety and constraint validation for asset relationships

---

### 🏗️ **FOCUS 6: Technical Improvements**ations (StaticPool, VariablePool)
- [x] Factory function with simplified API (single location parameter)
- [x] Type safety with StaticPool `__post_init__` fix
- [x] Simplified `create_rule_curve` with breakpoint-based data structure
- [x] Fractional day support for sub-daily calculations
- [x] Comprehensive unit tests for all components (62 tests passing)
- [x] Integration tests for rule curves + VariablePool

---

## Development Focus Areas

### 🎯 **FOCUS 1: Pool-Based Operations & Standard Operating Policy (SOP)**
*Priority: HIGH - Core functionality for reservoir operations*

- [ ] **1A**: Add pools collection to `ReservoirComponents` 
  - [ ] Implement `pools: tuple[Pool, ...]` field (sorted by location, largest to smallest)
  - [ ] Add pool validation and type compatibility checking
  - [ ] Pool sorting implementation (decide: tuple vs custom iterable - see Questions)

- [ ] **1B**: Create `StandardOperatingPolicy` class
  - [ ] Implement `Operations` interface with `operate(reservoir, inflow, demand)` method
  - [ ] Pool-based release logic: meet demand, spill only when necessary
  - [ ] Support multiple pool scenarios (flood/conservation/inactive)
  - [ ] Integration with existing outlet constraints
  - [ ] Numeric type support (int/float) like `PassiveOperations`

- [ ] **1C**: SOP Test Scenarios (5 comprehensive test cases)
  - [ ] Test 1: One StaticPool, no outlets - spill only if (storage + inflow - capacity) > demand
  - [ ] Test 2: One StaticPool, one outlet - outlet location constrains releases
  - [ ] Test 3: Multiple StaticPools, no outlets - flood/conservation/inactive pool logic
  - [ ] Test 4: Multiple StaticPools with outlets - outlet constraints on pool releases
  - [ ] Test 5: Replace conservation pool with VariablePool - test sorting validation

**Architectural Questions (Need Input):**
- Pool Storage: Tuple vs Custom Iterable? (frequency of modification, iteration behavior)
- Operations Component Selection: Builder pattern vs Configuration vs Method parameters?
- Component selection at creation time or execution time?

---

### 🔧 **FOCUS 2: Operations Architecture Enhancement**
*Priority: MEDIUM - Improve flexibility and component selection*

- [ ] **2A**: Operations Component Selection System
  - [ ] Design pattern for Operations to use/ignore specific ReservoirComponents
  - [ ] Implementation options: Builder pattern, Configuration object, Method parameters, or Specialized classes
  - [ ] Support mixed operations (PassiveOperations + SOP for different pools)

- [ ] **2B**: Advanced Operations Features
  - [ ] Runtime component filtering capabilities
  - [ ] Type safety for component compatibility
  - [ ] Error handling for invalid component configurations

---

### 🔌 **FOCUS 3: Plugin Architecture Migration**
*Priority: MEDIUM - Modernize extensibility system*

- [ ] **3A**: Modern Plugin System Design
  - [ ] Protocol-based plugin interfaces for type safety
  - [ ] Entry points or decorator-based registration (vs file discovery)
  - [ ] Plugin metadata and validation system
  - [ ] Configurable plugin directories and namespace management

- [ ] **3B**: Plugin Categories & Examples
  - [ ] Support operations, outlets, reservoirs, pools
  - [ ] Create demonstration plugins:
    - Updated pool-based operations plugin using new SOP architecture
    - Custom outlet plugin with advanced release logic
    - Specialized reservoir plugin with extended functionality
  - [ ] Plugin documentation and development guide

**Legacy System Issues to Address:**
- Hard-coded paths, global state, no type safety
- Manual imports, poor error handling, no metadata
- Module conflicts between plugin directories

---

### � **FOCUS 4: Simulation Optimization & Dynamic Time-Stepping**
*Priority: MEDIUM-HIGH - Advanced simulation capabilities*

- [ ] **4A**: Single Objective Optimization Framework
  - [ ] **Objective Functions**: Interface for simulation goals (maximize storage, minimize spill, etc.)
  - [ ] **Constraints System**: Define operational limits (no spill releases, minimum flows, etc.)
  - [ ] **Decision Variables**: Parameterize operational components (pool locations, release rules)
  - [ ] **Optimization Integration**: Interface with scipy.optimize or similar solvers
  - [ ] **Multi-Period Operations**: Handle optimization across multiple time periods

- [ ] **4B**: Dynamic Time-Stepping & ODE Formulation
  - [ ] **ODE-Based Operations**: Formulate reservoir operations as differential equations
  - [ ] **Adaptive Time-Stepping**: Variable time steps based on system dynamics
  - [ ] **SciPy Integration**: Interface with scipy.integrate solvers (solve_ivp, etc.)
  - [ ] **Continuous vs Discrete**: Hybrid formulations for different operation types
  - [ ] **Performance Analysis**: Compare ODE vs discrete time-step approaches

- [ ] **4C**: Optimization-Simulation Integration
  - [ ] **Simulation Engine**: Multi-period simulation with configurable operations
  - [ ] **Sensitivity Analysis**: Parameter sensitivity for optimization guidance
  - [ ] **Optimization Algorithms**: Support different solver types (gradient-based, metaheuristic)
  - [ ] **Result Analysis**: Post-optimization analysis and visualization tools

**Analysis Required:**
- Mathematical formulation of reservoir operations as ODEs
- Optimization variable parameterization strategies
- Solver selection criteria and performance trade-offs
- Integration patterns between optimization and simulation

---

### �🏗️ **FOCUS 5: Technical Improvements**
*Priority: LOW - Polish and optimization*

- [ ] **5A**: `create_rule_curve` Refinements
  - [ ] Fix validation logic bugs and boundary conditions
  - [ ] Add better error messages and warnings

- [ ] **5B**: Performance & Features
  - [ ] Rule curve interpolation caching
  - [ ] Support for leap years (366 days)
  - [ ] Alternative interpolation methods (cubic spline)

- [ ] **5C**: Documentation & Integration
  - [ ] Update module docstrings with examples
  - [ ] Add usage examples to README
  - [ ] Better integration patterns exploration

---

## Recommended Development Sequence

1. **Start with FOCUS 1** (Pool-Based SOP) - Core functionality needed
2. **Answer architectural questions** for pool storage and operations selection
3. **Complete SOP implementation and testing** before moving to next focus
4. **Move to FOCUS 2** (Operations Architecture) - Build on SOP learnings
5. **Choose between FOCUS 3, FOCUS 4, or FOCUS 5** based on priorities:
   - **FOCUS 3** (Plugin Architecture) - For extensibility and modularity
   - **FOCUS 4** (Optimization) - For advanced simulation capabilities  
   - **FOCUS 5** (Asset Modeling) - For infrastructure management and failure modeling
6. **Finish with FOCUS 6** (Polish) - Final improvements

## Technical Reference

### Pool-Based SOP Architecture Details
**Core Components:**
- `ReservoirComponents.pools: tuple[Pool, ...]` - sorted largest to smallest location
- `StandardOperatingPolicy` class with `operate(reservoir, inflow, demand)` method
- Pool validation functions similar to outlet validation
- Integration with existing `Operations` protocol

**Pool Operation Logic:**
1. **Flood Pool** (top): Release max(storage + inflow - conservation_location, demand)
2. **Conservation Pool** (middle): Release demand if sufficient water, otherwise available water
3. **Inactive Pool** (bottom): No releases allowed
4. **Outlet Integration**: Outlet location constraints override pool logic when applicable

### Legacy Plugin Architecture Analysis
**Current System Strengths:**
- Clear separation: Operations, outlets, reservoirs as distinct plugin types
- Simple discovery: File-based plugin discovery with glob patterns
- Initialize pattern: Consistent `initialize()` function returns plugin registry
- Flexible loading: Load single plugin, module, or all plugins by type

**Current System Issues:**
- Hard-coded paths, global state, no type safety
- Manual imports, poor error handling, no metadata
- Module conflicts between `/canteen/plugins` and `/plugins`

### Architecture Options for Discussion

**Pool Storage: Tuple vs Custom Iterable**
- Tuple: Simple, immutable, consistent with outlets ✅ | Limited extensibility ❌
- Custom Iterable: Better encapsulation, extensible ✅ | More complex ❌

**Operations Component Selection Patterns**
- Builder: `ops.with_pools().without_outlets()`
- Configuration: `OperationsConfig(use_pools=True)`
- Method Parameters: `operate(reservoir, use_components=['pools'])`
- Specialized Classes: `PoolOnlyOperations` vs `FullOperations`

---
*Last updated: September 10, 2025*
*Total tests: 62 (all passing)*
