# Reservoir as Strategy pattern context — operations on the same object as physical infrastructure

A reservoir has two conceptually distinct categories of state: physical infrastructure (capacity, outlets, pools, mappings) that cannot change without real-world construction, and management policy (the Operations strategy) that can change between simulation runs without any physical change.

An early design considered separating these into two objects. We chose not to. Splitting them would require every caller to compose a physical reservoir with a policy object before running a simulation, with no decoupling benefit — because `Operations` is already the decoupled piece. The Strategy pattern provides that decoupling: `BaseReservoir` is the context, `Operations` is the strategy interface, and concrete strategies (`PassiveOperations`, `StandardOperatingPolicy`, etc.) are swappable without touching the reservoir.

The lifecycle contract is:
- **Physical fields** (`outlets`, `pools`, `capacity`, `mappings`): frozen permanently after construction via the builder pattern
- **`operations`**: frozen per simulation run, but the sanctioned swap point between runs — a reservoir can change how it is managed without new construction

`operations` appears in the `Reservoir` protocol because a context object without its strategy field in the interface is an incomplete contract.

## Considered options

- **Separate `PhysicalReservoir` and `ManagedReservoir` objects**: cleaner conceptual boundary but forces two-object composition on every caller, and the decoupling is already provided by the Strategy interface
- **Operations as a parameter to `operate()` rather than a field**: makes the strategy stateless but loses the ability to configure and attach a strategy at construction time, which the builder pattern depends on
