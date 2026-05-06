"""
Canteen - Reservoir modeling and simulation package.

A Python package for modeling reservoir/dam operations and water release simulations.
Given inflow timeseries, it simulates reservoir storage volumes and outflows.
Supports both integer and floating-point arithmetic with type safety.

Basic Usage
-----------
    # Create components using module factory functions
    from canteen import reservoir, operations, outlet, pool
    
    # Create operations
    ops = operations.factory()  # Default passive operations
    
    # Create outlets
    spillway = outlet.factory(name="Spillway", location=95.0)
    gate = outlet.factory(name="Gate", location=80.0)
    
    # Create pools
    conservation = pool.factory(
        name="Conservation", 
        location=85.0,
        range_=(0.0, 85.0)
    )
    
    # Create reservoir with components
    res = reservoir.factory(
        name="My Reservoir", 
        storage=75.0, 
        capacity=150.0,
        operations=ops,
        outlets=outlet.Outlets((spillway, gate))
    )
    
    # Operate the reservoir
    spill = res.operate(inflow=50.0)

Builder Pattern
---------------
    # Reservoirs support fluent builder pattern for incremental construction
    from canteen import BaseReservoir, operations, outlet, pool, Outlets, Pools
    
    # Create base reservoir
    res = BaseReservoir(name="Dam", storage=50.0, capacity=100.0)
    
    # Add components using builder methods (chainable)
    res.add_operations(operations.factory()) \\
       .add_outlets(Outlets((
           outlet.factory(name="Spillway", location=95.0),
           outlet.factory(name="Gate", location=80.0)
       ))) \\
       .add_pools(Pools((
           pool.factory(name="Flood", location=95.0),
           pool.factory(name="Conservation", location=85.0)
       )))
    
    # Or add components step by step
    res2 = BaseReservoir(name="Another Dam", storage=25.0, capacity=50.0)
    res2.add_operations(operations.factory())
    res2.add_outlets(Outlets((outlet.factory(name="Outlet", location=45.0),)))
    
    # Operate after building
    spill = res.operate(inflow=30.0)
"""

from canteen import operations, outlet, reservoir, pool, mapping as mapping_module, metadata
from canteen.operations import (
    Operations,
    PassiveOperations,
)
from canteen.outlet import (
    BasicOutlet,
    Outlet,
    Outlets,
    ReleaseRange,
)
from canteen.reservoir import (
    BaseReservoir,
    Reservoir,
)
from canteen.pool import (
    Pool,
    Pools,
)
from canteen.mapping import (
    Mapping,
    Mappings,
    build_interpolation_fx,
    build_1D_interpolation_fxs,
)
from canteen.metadata import (
    MetaData,
    MetaDataPlusRange,
    XYMetaData
)
from canteen.units import (
    Quantity
)

__version__ = "0.1.0"
__all__ = [
    # Modules
    "operations",
    "outlet",
    "reservoir",
    "pool",
    "mapping_module",
    "metadata",

    # Protocols
    "Operations", 
    "Outlet",
    "Reservoir",
    "Pool",
    "Mapping",

    # Implementations
    "BasicOutlet",
    "BaseReservoir",
    "PassiveOperations",

    # Container classes
    "Outlets",
    "Pools",
    "Mappings",

    # Data types
    "ReleaseRange",
    "MetaData",
    "MetaDataPlusRange",
    "XYMetaData",
    "Quantity",

    # Utility functions
    "build_interpolation_fx",
    "build_1D_interpolation_fxs",
]
