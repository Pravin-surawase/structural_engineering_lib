# Python Module Dependency Graph

This graph shows direct imports between `structural_lib` modules.

![Python module dependency graph](dependencies.png)

## Notes
- Derived from an AST import scan of `Python/structural_lib`.
- `__init__.py` and `__main__.py` are excluded to keep the graph readable.
- `structural_lib.insights.*` modules are tinted to stand out.

## Regenerate
```bash
.venv/bin/python docs/architecture/tools/generate_dependency_graph.py
```

Requires `networkx` and `matplotlib` in the active virtualenv.
