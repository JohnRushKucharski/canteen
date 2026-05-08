# Canteen

A Python library for modeling reservoir/dam operations and water release simulations with type-safe generic numeric support.

## Features

- **Type-Safe Generic Operations**: Support for both integer and floating-point arithmetic with type safety
- **Mass Balance Preservation**: Integer operations use logical rounding to maintain mass balance  
- **Simplified Factory API**: Easy-to-use factory methods for creating reservoirs, operations, and outlets
- **Protocol-Based Design**: Flexible architecture using Python protocols
- **Physical Outlet Modeling**: Realistic outlet behavior with location-based constraints and design limits
- **Conservative Integer Outlets**: Integer outlets use floor operation to prevent fractional flows
- **Comprehensive Testing**: Full test suite with 90+ tests ensuring reliability

## Installation

This project uses [UV](https://github.com/astral-sh/uv) for dependency management.

```bash
# Clone the repository
git clone <repository-url>
cd canteen

# Install dependencies and create virtual environment
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

Install optional DataFrame dependencies only if you need converter helpers:

```bash
# pandas only
uv sync --extra pandas

# polars only
uv sync --extra polars
```

## Quick Start

### Building Reservoirs with Components

Canteen supports an extensible builder pattern for adding components to reservoirs. This pattern is designed to be composable and extensible for future component types.

#### Adding Outlets

Use the `add_outlets()` method to add outlet components to reservoirs:

```python
import canteen

# Create a basic reservoir
dam = canteen.create_reservoir(name="Highland Dam", storage=750, capacity=1000)

# Create outlet components
spillway = canteen.create_outlet(name="Spillway", location=95.0, 
                                design_range=canteen.ReleaseRange(0, 50))
gate = canteen.create_outlet(name="Gate", location=40.0,
                            design_range=canteen.ReleaseRange(5, 15))

# Add outlets using builder pattern (returns BasicReservoir with outlets)
dam_with_outlets = dam.add_outlets([spillway, gate])

# Calculate total outlet capacity at different fill levels
min_capacity, max_capacity = dam_with_outlets.get_total_outlet_capacity(60.0)
print(f"Total capacity: {min_capacity} - {max_capacity}")
```

#### Outlet Sorting

By default, outlets are sorted by location in descending order (highest first). You can provide a custom sorting function:

```python
# Custom sorting by name
def sort_by_name(outlets):
    return tuple(sorted(outlets, key=lambda o: o.name))

dam_with_sorted_outlets = dam.add_outlets(outlets, sorter=sort_by_name)

# Or disable sorting entirely
dam_unsorted = dam.add_outlets(outlets, sorter=lambda x: x)
```

#### Builder Pattern Chaining

The builder pattern supports chaining - each `add_outlets()` call returns a new reservoir instance:

```python
# Start with basic reservoir
dam = canteen.create_reservoir()

# Add outlets in stages
dam_with_primary = dam.add_outlets([spillway, main_gate])
dam_with_all = dam_with_primary.add_outlets([emergency_outlet, bottom_drain])

# Original reservoir remains unchanged
assert isinstance(dam, canteen.BasicReservoir)
assert isinstance(dam_with_all, canteen.BasicReservoir)
```

#### Extensible Component Architecture

The builder pattern is designed to support future component types:

```python
# Current (implemented)
reservoir_with_outlets = reservoir.add_outlets(outlets)

# Future extensions (planned)
# reservoir_with_pools = reservoir.add_pools(pools)
# reservoir_with_spillways = reservoir.add_spillways(spillways)
# reservoir_with_custom = reservoir.add_components(custom_components)
```

### Advanced Dam System

```python
from canteen import reservoir, outlet
from canteen.outlet import ReleaseRange

# Create a complete dam system
dam = reservoir.factory(
    name="Main Dam",
    storage=85,
    capacity=100,
    int_only=True
)

# Create outlets at different elevations
spillway = outlet.factory(
    name="Emergency Spillway",
    location=100.0,  # At capacity level
    int_only=True
)

low_outlet = outlet.factory(
    name="Low Level Outlet",
    location=30.0,  # Deep outlet
    design_range=ReleaseRange(0, 20),  # Max 20 units
    int_only=True
)

# Check outlet capabilities at current level
current_level = float(dam.storage)  # 85.0

spillway_range = spillway.operations(current_level)
print(f"Spillway: {spillway_range}")  # ReleaseRange(0, 0) - no head

low_outlet_range = low_outlet.operations(current_level)
print(f"Low outlet: {low_outlet_range}")  # ReleaseRange(0, 20) - good head

# Simulate flood event
spill = dam.operate(inflow=25)
print(f"Reservoir spill: {spill}")  # 10 units spilled
print(f"New storage: {dam.storage}")  # 100 (at capacity)
```

## Type Safety and Mass Balance

Canteen provides strict type safety for numeric operations across all components:

### Integer Operations
- Uses logical rounding to preserve mass balance
- All operations return integer values
- Outlets use floor operation to prevent fractional flows

```python
# Integer outlet prevents fractional releases
int_outlet = outlet.factory(location=50.0, int_only=True)

# Test with fractional head
release = int_outlet.operations(52.7)  # 2.7 units of head
print(release)  # ReleaseRange(0, 2) - floored to prevent fractional flow
```

### Float Operations  
- Standard floating-point precision
- Suitable for continuous modeling

```python
# Float outlet allows precise releases
float_outlet = outlet.factory(location=50.0, int_only=False)

release = float_outlet.operations(52.7)  # 2.7 units of head
print(release)  # ReleaseRange(0.0, 2.7) - precise floating-point
```

### Physical Constraints

Outlets respect physical laws and design limitations:

```python
# Outlet only releases when reservoir level exceeds outlet location
outlet = outlet.factory(location=75.0, design_range=ReleaseRange(0, 100))

# Below outlet - no flow possible
release = outlet.operations(70.0)  # ReleaseRange(0, 0)

# Above outlet - limited by available head and design
release = outlet.operations(80.0)  # ReleaseRange(0, 5) - limited by head
release = outlet.operations(200.0)  # ReleaseRange(0, 100) - limited by design
```

## API Reference

### Factory Methods

#### `reservoir.factory()`
```python
def factory(
    name: str = "",
    storage: int | float = 0,
    capacity: int | float = 1,
    operations: PassiveOperations | None = None,
    *,
    int_only: bool = False
) -> BasicReservoir
```

#### `operations.factory()`
```python
def factory(*, int_only: bool = False) -> PassiveOperations
```

#### `outlet.factory()`
```python
def factory(
    name: str = "",
    location: float = 0.0,
    design_range: ReleaseRange | None = None,
    *,
    int_only: bool = False
) -> BasicOutlet
```

### Core Classes

- **`BasicReservoir`**: Main reservoir implementation with storage, capacity, and operations
- **`BasicOutlet`**: Outlet implementation with location-based release calculations
- **`PassiveOperations`**: Spillway-based operations strategy
- **`ReleaseRange`**: Named tuple for min/max release values
- **`Reservoir`**: Protocol defining reservoir interface
- **`Operations`**: Protocol defining operations interface  
- **`Outlet`**: Protocol defining outlet interface

## Outlet Behavior

### Physical Constraints
- Outlets only release water when reservoir level exceeds outlet location
- Release is limited by available head (level - location)
- Design range provides additional constraints on min/max release

### Conservative Integer Behavior
Integer outlets use floor operation to ensure:
- No fractional flows are allowed
- Conservative release estimates
- Mass balance preservation in discrete models

```python
int_outlet = outlet.factory(location=50.0, int_only=True)

# Fractional heads are floored
test_cases = [
    (50.1, 0),  # 0.1 head -> 0 release
    (50.9, 0),  # 0.9 head -> 0 release  
    (51.0, 1),  # 1.0 head -> 1 release
    (52.7, 2),  # 2.7 head -> 2 release (floored)
]

for level, expected_max in test_cases:
    release = int_outlet.operations(level)
    assert release.max == expected_max
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/canteen

# Run specific test file
uv run pytest tests/test_outlet.py -v
```

### Code Quality

```bash
# Linting
uv run ruff check src/

# Type checking  
uv run mypy src/

# Formatting
uv run ruff format src/
```

### Building

```bash
# Build the package
uv build
```

## Architecture

The Canteen library is built around protocols and generic types:

```
┌─────────────────┐    ┌──────────────────┐
│   Reservoir     │◄───│  BasicReservoir  │
│   Protocol      │    │      Class       │
└─────────────────┘    └──────────────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         └──────────────│   Operations     │
                        │   Protocol       │
                        └──────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │ PassiveOperations│
                        │      Class       │  
                        └──────────────────┘

┌─────────────────┐    ┌──────────────────┐
│     Outlet      │◄───│   BasicOutlet    │
│   Protocol      │    │      Class       │
└─────────────────┘    └──────────────────┘
         │                       │
         │                       ▼
         │              ┌──────────────────┐
         └──────────────│  ReleaseRange    │
                        │   NamedTuple     │
                        └──────────────────┘
```

## License

[License information here]

## Contributing

[Contributing guidelines here]
