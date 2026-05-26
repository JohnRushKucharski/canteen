# Extensible Plugin Architecture for Canteen

## Problem Statement

Canteen models reservoir operations through **Operations** strategies, **Outlets**, and **Pools**. Currently, only built-in implementations are available, limiting extensibility for researchers, teams, and end users who want to:

- Develop custom operations strategies (e.g., demand-based policies, hydrologic forecasting)
- Create custom outlet models (e.g., turbine discharge curves)
- Model alternative pool definitions (e.g., rule curves for specific water years)

These users have different needs:
- **Researchers**: Drop a `.py` file in a local directory, no packaging required
- **Teams**: Build and distribute proper packages via pip or entry points
- **Notebook users**: Register implementations inline during interactive sessions

A single registration mechanism cannot serve all three patterns. Canteen needs an extensible plugin system that:

1. Supports multiple authorship patterns (packaged, file-based, inline)
2. Maintains security (no arbitrary code execution from untrusted sources)
3. Provides clear discovery and documentation
4. Integrates cleanly with the existing factory pattern

## Solution

Implement a **three-tier plugin architecture** with per-component registries:

### Three Tiers (in priority order)

1. **Entry Points** (`importlib.metadata` groups: `canteen.operations`, `canteen.outlets`, `canteen.pools`)
   - Discovers installed, packaged plugins automatically on import
   - For teams building and distributing proper packages
   - Public contract: group naming conventions are published API

2. **File Discovery** (scans `./plugins/{component_type}/` for `.py` files)
   - Scans and imports plugin modules, discovers `__canteen_{component}__` dicts
   - For researchers who drop files locally without packaging
   - Preserves compatibility with legacy `old/plugins/` approach
   - Lazy discovery on first `factory()` call (not on import)

3. **Explicit Registration** (`canteen.{component}.register(name, cls)`)
   - Available at any time for in-process use (notebooks, tests, ad-hoc use)
   - Users explicitly pass objects; maximum control
   - No security concerns

### Registry and Lookup

- Each component type (operations, outlets, pools) maintains its own per-module registry
- All three tiers write to the same registry dict
- Lookup via `factory()` is indifferent to registration source
- Name collision policy: built-ins > entry points > file discovery > explicit registration (with override power)
- Collisions generate log warnings, not errors

### Security & Stability

- **File discovery path**: Fixed to `./plugins/{component_type}/` relative to current working directory
- **No arbitrary paths**: Never user-configurable
- **Protocol validation**: After import, plugins must implement the relevant protocol (Operations, Outlet, Pool)
- **Error isolation**: Failed plugin loads log warnings and continue; other plugins still load
- **Kill switch**: Environment variable `CANTEEN_DISABLE_FILE_PLUGINS=1` disables file discovery entirely
- **Clear docs**: Document that `plugins/` is a trusted execution directory (like `site-packages`)

### User Experience

- **Plugin directory messaging**: 
  - If `./plugins/{component}/` exists but no valid plugins found → warn user "Did you mean to add custom plugins here?"
  - If directory does not exist → silent (no noise)
- **Explicit reload**: Provide `reload_plugins()` function per module for interactive development
- **Error handling**: Log and continue on individual plugin failures; never fail the entire discovery
- **Introspection API**: `list_plugins()` per module returns registered plugin names and optional docstrings
- **Docstring convention**: Require all plugins to have docstrings for discoverability

## User Stories

1. As a **researcher**, I want to write custom **Operations** in a local `.py` file and drop it in `./plugins/operations/`, so that I can test new release strategies without modifying the library.

2. As a **team**, I want to package a custom **Outlet** model as a pip-installable package with an entry point in the `canteen.outlets` group, so that team members can install and use it like any other dependency.

3. As a **notebook user**, I want to register a custom **Pool** class inline via `canteen.pool.register("MyPool", MyPoolClass)`, so that I can experiment with alternative pool definitions interactively.

4. As a **user**, I want to discover available plugins by calling `canteen.operations.list_plugins()`, so that I can see what strategies are installed and pick one for my simulation.

5. As a **plugin author**, I want to write a docstring for my plugin class, so that users who call `list_plugins()` can see what my plugin does.

6. As a **developer**, I want to reload plugins during an interactive session via `canteen.operations.reload_plugins()`, so that I can iterate on plugin code without restarting Python.

7. As a **user**, I want to see a helpful message if I create `./plugins/operations/` but forget to add any plugins, so that I know the plugin system is looking in the right place.

8. As a **user**, I want a failed plugin to generate a warning, not crash my entire simulation, so that one broken plugin doesn't prevent me from using the rest of the system.

9. As a **user**, I want to use custom plugins from multiple sources (entry points, local files, and inline registration) at the same time, so that I can combine packaged, team, and experimental plugins in a single simulation.

10. As a **user**, I want clear documentation on how to write and register plugins, so that I can build custom components without guessing.

11. As a **security-conscious user**, I want an environment variable to disable file plugin discovery, so that I can lock down production environments and prevent arbitrary code execution.

12. As a **library maintainer**, I want built-in plugins to always take priority, so that production code is never accidentally shadowed by user plugins.

## Implementation Decisions

### Module Structure

- **Per-component registries**: Each component module (`operations.py`, `outlet.py`, `pool.py`) maintains its own `NAMED_{COMPONENT}` dict registry
- **No central registry**: Avoids coupling and matches current factory pattern
- **Module-level globals**: Track plugin discovery state per module (`_file_{component}_plugins_loaded` flag)

### Plugin Discovery Interface

- **File discovery function**: `_discover_file_{component}_plugins()` — scans `Path.cwd() / "plugins" / {component_type}` for `.py` files
- **Module loading**: Use `importlib.util.spec_from_file_location()` to import plugins without modifying `sys.modules`
- **Plugin dict extraction**: Look for `__canteen_{component}__` dict at module level after import
- **Registry update**: Add discovered plugins to `NAMED_{COMPONENT}` if name not already present

### Factory Signature

Extend `factory()` functions to accept optional named plugin parameter:
- `operations.factory(named_operation=None)` — if provided, look up in registry; otherwise use defaults or create Basic implementations
- `outlet.factory(named_outlet=None, ...)`
- `pool.factory(named_pool=None, ...)`

### Plugin Registration (Tier 3)

Provide `register()` function per module:
- `operations.register(name, cls)` — add class to `NAMED_OPERATIONS` (allow override)
- `outlet.register(name, cls)`
- `pool.register(name, cls)`

### Plugin Reload (Tier 2)

Provide `reload_plugins()` function per module:
- `operations.reload_plugins()` — clear `NAMED_OPERATIONS` (keep built-ins), re-scan file directory
- `outlet.reload_plugins()`
- `pool.reload_plugins()`

### Plugin Discovery (Tiers 1 & 2)

- **Entry points**: Discover on module import via `importlib.metadata.entry_points()` (future enhancement, MVP defers this)
- **File discovery**: Lazy on first `factory()` call; subsequent calls use cached registry
- **Error handling**: Catch all exceptions during file plugin load, log with module name and error, continue to next file
- **User messaging**: After discovery, if directory exists but no plugins registered, print advisory message

### Plugin Introspection (API)

Provide `list_plugins()` function per module:
- `operations.list_plugins()` — return dict of `{name: (class, docstring)}` for all registered plugins
- `outlet.list_plugins()`
- `pool.list_plugins()`

### Name Collision Handling

- **Priority**: Built-ins > entry points > file discovery > explicit registration
- **Logging**: When a `register()` call attempts to override an existing name, log a warning
- **Override allowed**: Explicit registration (tier 3) is allowed to override all; used for testing and advanced scenarios

### Security & Environment Variables

- **Disable file plugins**: Check `os.getenv("CANTEEN_DISABLE_FILE_PLUGINS")` at discovery time; skip file discovery if set
- **Fixed path**: Hard-code plugin path to `Path.cwd() / "plugins" / {component}` — never read from user input or config
- **Module validation**: After import, verify plugin implements or is compatible with the protocol (optional in MVP, required for future versions)

### MVP Scope

- **No entry points**: Tier 1 deferred to future enhancement
- **No versioning**: No `__canteen_version__` metadata; plugins must keep up with breaking changes
- **File discovery only**: Tiers 2 and 3 fully implemented
- **Basic introspection**: `list_plugins()` returns simple list of names; docstring extraction optional

## Testing Decisions

### What Makes a Good Test

- **Test external behavior, not implementation**: Test that plugins are discovered, registered, and callable; don't test internal registry data structures
- **Avoid mock filesystems**: Use real temporary directories for file discovery tests
- **Isolation**: Each test should start with a clean registry state (use `setUp` to reset or provide a isolated registry instance)
- **Realistic scenarios**: Test discovery with multiple plugins, name collisions, import errors, missing files

### Modules to Test

1. **Plugin discovery** (`_discover_file_{component}_plugins`):
   - Happy path: `.py` file with valid `__canteen_{component}__` dict gets registered
   - Missing dict: `.py` file without `__canteen_{component}__` is skipped silently
   - Import error: Syntax error or failed import generates warning and continues
   - No plugins: Directory exists but no `.py` files generates advisory message
   - Directory missing: No directory → silent, no warning

2. **Registry and lookup** (`factory()` with named parameter):
   - Built-in plugin returned by default
   - Named plugin returned from registry
   - Unknown name raises `KeyError` with clear message
   - Name collision: Later registrations don't override earlier ones (tier priority)

3. **Explicit registration** (`register()`):
   - New plugin added to registry
   - Duplicate name generates warning but still updates registry (explicit tier overrides)
   - `factory(named=...)` returns newly registered plugin

4. **Plugin reload** (`reload_plugins()`):
   - Reload clears file-discovered plugins but keeps built-ins
   - New files discovered after reload
   - Removed files are no longer available after reload

5. **Introspection** (`list_plugins()`):
   - Returns all registered plugin names
   - Includes built-ins, file-discovered, and explicitly registered
   - Docstrings extracted and included if present

### Prior Art

- Look at existing tests in `tests/` for similar patterns (e.g., how `Outlets` and `Pools` containers are tested)
- Use temporary directories via `tempfile.TemporaryDirectory()` for file-based tests
- Mock `sys.modules` if needed to simulate import failures

## Out of Scope

### MVP Out of Scope

1. **Entry points (Tier 1)**: Deferred to future enhancement. Requires `pyproject.toml` configuration and packaging documentation.

2. **Plugin versioning**: No `__canteen_version__` metadata or compatibility checking. Plugins must keep up with breaking changes.

3. **Plugin dependency management**: No way to declare that a plugin requires a specific version of canteen or other packages.

4. **Plugin sandboxing or security validation**: File plugins have full Python privileges; no code inspection or sandboxing.

5. **CLI plugin discovery**: `canteen` CLI (if implemented) does not auto-discover or list plugins. Only library API exposes plugin registry.

6. **Documentation generation**: No automatic doc generation from plugin docstrings. Users manage plugin docs separately.

## Further Notes

### Documentation

A separate issue will cover creating `docs/plugins.md` with:
- Plugin authoring guide (how to write and register a plugin for each tier)
- Examples for each component type (operations, outlets, pools)
- Troubleshooting (common errors, how to debug plugin imports)
- Glossary of plugin concepts

### Future Enhancements

1. **Tier 1 (Entry Points)**: Discover and register packaged plugins via `importlib.metadata.entry_points()` on module import
2. **Plugin versioning**: Add `__canteen_version__` metadata and check compatibility at load time
3. **CLI support**: `canteen list-plugins` command to show available plugins
4. **Module introspection**: Deeper inspection of plugin signatures, requirements, and metadata
5. **Registry export**: Serialize registry to JSON for deployment and environment setup

### Relationship to Existing Code

- Builds on existing `factory()` pattern in `operations.py`, `outlet.py`, `pool.py`
- Complements ADR-0001 (Three-tier plugin architecture concept)
- Respects ADR-0002 (Operations as Strategy pattern context) — plugins are alternative strategies
- Respects ADR-0003 (Null Object pattern) — empty component containers remain unchanged

### Community & Ecosystem

This architecture enables:
- Independent developers to publish canteen plugins as standalone packages
- Teams to maintain internal plugin libraries without forking canteen
- Researchers to rapidly prototype custom behaviors in notebooks
- Production deployments to lock down to specific, tested plugins via environment variables

It intentionally maintains backward compatibility with the legacy `old/plugins/` file-discovery approach while adding the flexibility of entry points and explicit registration.
