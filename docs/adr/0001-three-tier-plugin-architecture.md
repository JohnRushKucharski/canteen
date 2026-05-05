# Three-tier plugin architecture for extensible components

Canteen needs to support three distinct plugin authorship patterns: researchers who drop a `.py` file in a local directory, teams who build and distribute proper packages, and notebook users who register implementations inline. A single registration mechanism cannot serve all three.

We adopt a three-tier plugin registry that loads in priority order:

1. **Entry points** (`importlib.metadata`, group names `canteen.operations`, `canteen.outlets`, `canteen.pools`, etc.) — discovers installed, packaged plugins automatically on import. The group naming convention is a public contract once plugins are published against it.
2. **File discovery** — scans a configured directory (default: `./plugins/`) for `.py` files, imports them, and registers anything implementing the relevant protocol. Preserves compatibility with the legacy `old/plugins/` approach.
3. **Explicit registration** — `canteen.register(name, cls)` available at any time for in-process use (e.g. notebooks, tests).

All three paths write to the same registry dict. Lookup via `factory("NAME")` is indifferent to registration source.

## Considered options

- Entry points only: excludes script-level users who won't package their code
- File discovery only: no standard packaging support, fragile path handling (the old system's weakness)
- Decorator/explicit registration only: requires explicit import of plugin modules, awkward for installed packages
