# Canteen

A Python library for modeling reservoir/dam operations and water release simulations. Given inflow timeseries, it simulates reservoir storage volumes and outflows.

## Language

**Reservoir**:
A physical dam/reservoir represented by its name, current storage, and capacity. Owns mutable simulation state (`storage`) and a fixed structural configuration (outlets, pools, operations, mappings). Structure is frozen after construction; only storage changes during simulation.
_Avoid_: Dam, tank, basin

**Storage**:
The current volume of water held in a reservoir at a given timestep. The only mutable state on a Reservoir during simulation.
_Avoid_: Volume (too generic), level, fill

**Capacity**:
The maximum storage volume a reservoir can hold. Fixed at construction.
_Avoid_: Max volume, max storage

**Inflow**:
The volume of water entering a reservoir in a single timestep. The primary input to `operate()`.
_Avoid_: Input, flow-in

**Outflow**:
The volume of water leaving a reservoir in a single timestep through outlets or spill. Returned by `operate()` as a tuple — one value per outlet plus one for spill.
_Avoid_: Release, discharge (use only when specific to an outlet's physics)

**Spill**:
Outflow that occurs when storage + inflow exceeds capacity. Always the last element of the outflow tuple returned by `operate()`.
_Avoid_: Overflow, excess release

**Outlet**:
A physical structure through which water is released from a reservoir. Has a location (elevation/depth), a design release range, and optional mappings for domain-specific behavior (e.g. discharge coefficient curve). Only releases when fill state exceeds its location.
_Avoid_: Gate, valve, structure (too generic)

**ReleaseRange**:
The minimum and maximum possible release volume through an outlet for a given fill state. Returned by `Outlet.operations()`. Not a global constraint — it is recomputed each timestep from the outlet's location and design limits.
_Avoid_: Release bounds, flow range

**Pool**:
A named storage zone within a reservoir, defined by a top-of-storage location. Determines which operational rules apply at a given storage level (e.g. flood pool, conservation pool, inactive pool).
_Avoid_: Zone, tier, layer

**Rule Curve**:
A time-varying pool location expressed as a day-of-year → volume/elevation relationship. Stored as a `Mapping` on a `VariablePool`.
_Avoid_: Operating curve, seasonal target

**Rating Curve**:
A volume → elevation (or elevation → volume) relationship stored as a `Mapping` on a `Reservoir`. Used when operational rules are expressed in elevation rather than volume.
_Avoid_: Stage-storage curve

**Operations**:
A strategy object (Strategy pattern) that computes outflows from a reservoir given its current state and an inflow. Pure computation — takes reservoir state in, returns a tuple of outflows. `BaseReservoir` is the context; `Operations` is the strategy interface. `BaseReservoir.operate()` owns the mutation of `self.storage` after calling the strategy.
_Avoid_: Policy (reserve for `StandardOperatingPolicy` specifically), rules

**Physical Infrastructure**:
The fixed structural properties of a reservoir: capacity, outlets, pools, and mappings. Cannot change without real-world construction. Frozen permanently after construction in code via the builder pattern.
_Avoid_: Physical state, hardware

**Management Policy**:
The `Operations` strategy attached to a reservoir. Can change between simulation runs without any physical change to the reservoir. The sanctioned swap point in the Strategy pattern. Frozen per simulation run.

**Passive Operations**:
The default `Operations` strategy. Makes maximum releases through all outlets in order from highest to lowest location, then spills any remaining volume above capacity. No demand target.
_Avoid_: Uncontrolled, gravity operations

**Standard Operating Policy (SOP)**:
A planned `Operations` strategy that meets a demand target, releases through pools in priority order, and spills only when necessary. Not yet implemented.

**Mapping**:
A named functional relationship (`f(x) → y`) with an optional inverse. The extension point for attaching domain-specific behavior to components. Stored in a `Mappings` bag keyed by name (e.g. `"rating_curve"`, `"evaporation"`, `"location"`).
_Avoid_: Function, curve (use specific names like RatingCurve, RuleCurve)

**Mappings**:
An ordered, name-keyed container of `Mapping` instances attached to a component. Provides the extension point for domain-specific functional relationships (rating curves, evaporation equations, etc.). Keys are well-known strings documented per component.
_Avoid_: Map, dictionary, config

## Relationships

- A **Reservoir** has exactly one **Operations** strategy, zero or more **Outlets**, zero or more **Pools**, and zero or more **Mappings**
- **Outlets** are sorted highest-to-lowest location; **Pools** are sorted highest-to-lowest location
- `operate(inflow)` calls the **Operations** strategy → returns **Outflow** tuple → `BaseReservoir` updates **Storage**
- A **Pool** location may be fixed (**StaticPool**) or time-varying via a **Rule Curve** (**VariablePool**)
- A **ReleaseRange** is computed per-timestep by an **Outlet** from fill state; it is not stored

**Null Object**:
An empty-but-valid instance of a container component (`Outlets`, `Pools`, `Mappings`) that holds zero elements. Used in place of `None` for optional reservoir components so that strategies can iterate and query components without defensive `None` checks. Default value for `outlets`, `pools`, and `mappings` on all reservoir instances.
_Avoid_: Empty, default, placeholder

## Flagged ambiguities

- `verbose` on `PassiveOperations` changed the return type at runtime (`int|float` vs `tuple`). Resolved: removed. `operate()` always returns `tuple[int|float, ...]`.
- `factory` was exported unqualified from `__init__.py`. Resolved: removed. Callers use `reservoir.factory()`, `outlet.factory()`, etc.
- `Operations.mappings` field existed but had no documented purpose. Resolved: removed from `Operations`. Operations strategies use typed named fields for configuration (e.g. `demand: Mapping`) and a `modifiers: Sequence[Mapping]` for behavioral extension. Component-level domain data lives in the component's `Mappings` bag.

## Open questions

- **Modifiers on Operations**: The proposed pattern is `modifiers: Sequence[Mapping]` on strategy classes, where each modifier takes reservoir context and returns an adjustment. Direction is agreed but the interface is not yet locked in — treat as proposed, not decided. Review when porting the plugin architecture.
