# Copilot Instructions for Canteen Repository

## Repository Overview
Canteen is a Python package for modeling reservoir/dam operations and water release simulations. Given inflow timeseries, it simulates reservoir storage volumes and outflows. The package is designed to be flexible (library or CLI), extensible (plugin system), and supports both simple (passive spillway) and complex (multi-outlet, asset condition-based) reservoir representations.

**Repository Size**: Small (~50 files), primarily Python codebase
**Languages**: Python 3.13+ (requires-python = ">=3.13")
**Build System**: UV package manager with Hatchling backend
**Target Runtime**: Python 3.13+ with type checking support

## Critical Build Instructions

### Environment Setup (ALWAYS REQUIRED)
1. **ALWAYS use UV**: This project uses UV package manager exclusively. Never use pip directly.
2. **Python Version**: Requires Python 3.13+. Project has `.python-version` file set to "3.12" but pyproject.toml requires ">=3.13"
3. **Initial Setup**: Run `uv sync` first to create virtual environment and install dependencies

### Build Commands (VALIDATED)
**Bootstrap/Install Dependencies**:
```bash
uv sync
```
- Creates virtual environment automatically
- Installs package in editable mode
- No additional setup required

**Build Package**:
```bash
uv build
```
- Creates dist/canteen-0.1.0.tar.gz and .whl files
- Always succeeds if source code is valid
- Clean build: `rm -rf dist/ && uv build`

**Run Tests**:
```bash
uv run pytest tests/
uv run pytest old/tests/  # Legacy tests (33 tests, all pass)
```
- New tests in `tests/` directory (currently minimal)
- Legacy tests in `old/tests/` are fully functional
- Test execution time: <0.1 seconds

**Lint/Type Check**:
```bash
uv run ruff check src/     # Linting (passes cleanly)
uv run pylint src/ tests/  # Pylint (passes cleanly, .pylintrc configures suppressions)
uv run mypy src/           # Type checking (passes cleanly)
```

**Run Package**:
```bash
uv run python -c "import canteen; print(canteen.hello())"
```
- Expected output: "Hello from canteen!"

### Adding Dependencies
- Development dependencies: `uv add --dev package_name`
- Runtime dependencies: `uv add package_name`
- Currently includes: pytest, mypy, ruff as dev dependencies

## Project Architecture

### Directory Structure
```
/
├── src/canteen/           # NEW codebase (minimal, being rebuilt)
│   ├── __init__.py        # Single hello() function
│   └── py.typed           # Type checking marker
├── old/                   # LEGACY codebase (reference implementation)
│   ├── canteen/           # Previous version with full functionality
│   │   ├── reservoir.py   # Reservoir protocols and implementations
│   │   ├── outlet.py      # Outlet interfaces and utilities
│   │   ├── operations.py  # Operations interface and Passive class
│   │   ├── asset.py       # Asset modeling
│   │   ├── condition.py   # Asset condition modeling
│   │   └── plugin.py      # Plugin system
│   ├── plugins/           # Plugin implementations
│   └── tests/             # 33 working legacy tests
├── tests/                 # NEW test directory (minimal)
├── pyproject.toml         # UV/Hatchling configuration
└── uv.lock               # Dependency lock file
```

### Key Architectural Elements
- **Plugin System**: Legacy code shows extensible plugin architecture for reservoirs, outlets, operations
- **Protocol-Based Design**: Uses Python protocols for interfaces (Reservoir, Outlet, Operations)
- **Modular Components**: Separates concerns (reservoirs, outlets, operations, assets, conditions)
- **Type Safety**: Full type hints with py.typed marker file

### Legacy Code Reference (DO NOT MODIFY `old/` directory)
The `old/` directory contains the previous implementation with:
- Complete reservoir modeling system
- Plugin architecture for operations, outlets, reservoirs
- Asset and condition modeling
- 33 comprehensive tests that demonstrate expected functionality

## Validation & CI
**No GitHub Actions**: No automated CI/CD pipelines configured
**No Pre-commit Hooks**: Manual validation required
**Validation Steps**:
1. `uv run ruff check src/` - Must pass cleanly
2. `uv run mypy src/` - Must pass with no type errors  
3. `uv run pytest tests/` - All tests must pass
4. `uv build` - Must build successfully

## Development Guidelines
- **Always run uv sync first** when working in repository
- **Use UV for all Python operations**: `uv run python`, `uv run pytest`, etc.
- **Type hints required**: All new code must include complete type annotations
- **Test coverage**: Add tests to `tests/` directory, not `old/tests/`
- **Code style**: Follow existing patterns, ruff configuration handles formatting
- **No direct modification** of `old/` directory - it's reference only

## Trust These Instructions
These instructions have been validated through direct testing. Only perform additional exploration if:
1. Commands fail with specific error messages
2. New functionality requires understanding legacy implementation patterns
3. Information in these instructions proves incomplete or incorrect

The legacy codebase in `old/` provides complete examples of the intended architecture and can be referenced for implementation patterns, but active development should occur in `src/canteen/`.



