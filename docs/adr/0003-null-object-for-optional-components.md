# Null Object pattern for optional reservoir components

Optional reservoir components (`outlets`, `pools`, `mappings`) were typed as `None | Outlets`, `None | Pools`, `None | Mappings`. This forced every `Operations` strategy to defensively check `if reservoir.outlets` before iterating, with branching that compounds as strategies grow more complex.

We adopt the Null Object pattern: optional components default to empty-but-valid container instances (zero-element `Outlets`, `Pools`, `Mappings`) rather than `None`. Strategies iterate and query components unconditionally — an empty container produces an empty loop with no branching required.

As a complement, strategies that require specific components (e.g. `StandardOperatingPolicy` requires at least one pool) validate that requirement at attachment time via `add_operations()`, not silently at `operate()` time. This surfaces misconfiguration at construction rather than mid-simulation.

## Consequences

- `Reservoir` protocol fields `outlets`, `pools`, `mappings` are always-present, never `None`
- `BaseReservoir` builder defaults construct empty containers rather than leaving fields as `None`
- `Operations.operate()` implementations require no `None` guards for reservoir components
- Strategies with component requirements declare and validate them at attachment time

## Considered options

- **`None` sentinels (prior approach)**: simple to construct but forces defensive branching into every strategy, which compounds with modifier chains and SOP complexity
- **Union types with type narrowing**: keeps `None` but uses `assert` or `isinstance` guards — still branches, just moves them to type-checker hints
