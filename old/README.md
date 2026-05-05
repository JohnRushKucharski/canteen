# Legacy Canteen Implementation

This directory contains the legacy/reference implementation of the Canteen package.

## Contents

- `canteen/` - Previous implementation with full functionality
  - `reservoir.py` - Reservoir protocols and implementations
  - `outlet.py` - Outlet interfaces and utilities  
  - `operations.py` - Operations interface and Passive class
  - `asset.py` - Asset modeling
  - `condition.py` - Asset condition modeling
  - `plugin.py` - Plugin system
- `plugins/` - Plugin implementations
- `tests/` - 33 working legacy tests (as mentioned in copilot-instructions.md)

## Usage

According to the Copilot instructions, legacy tests can be run with:
```bash
uv run pytest old/tests/  # Legacy tests (33 tests, all pass)
```

## Note

This directory structure was recreated as a placeholder for future migration steps.
The current active implementation is in `src/canteen/` with modern PEP 695 syntax
and comprehensive validation utilities.

Legacy code would be restored here when needed for migration reference.
