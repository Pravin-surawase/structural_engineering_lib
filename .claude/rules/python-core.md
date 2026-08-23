---
description: Rules for editing the Python structural_lib core
globs: Python/structural_lib/**
---

# Python Core Library Rules

## Architecture (4-Layer — STRICT)

- Core types (`core/`) → base classes, constants — no IS 456 math
- IS 456 Code (`codes/is456/`) → pure math, NO I/O, explicit units (mm, N/mm², kN, kNm)
- Services (`services/`) → orchestration: api.py, adapters.py, beam_pipeline.py
- UI/IO → react_app/, fastapi_app/

**Import rule:** Core CANNOT import from Services or UI. Services CANNOT import from UI.
**Units rule:** Always explicit — no hidden conversions.

## Folder Structure

```
Python/structural_lib/
├── __init__.py          # Package root
├── codes/               # Code implementations (IS 456 etc.)
│   └── is456/           # IS 456:2000 — pure math, NO I/O
├── core/                # Shared types, base classes, materials
├── services/            # Orchestration: api.py, adapters.py, beam_pipeline.py
├── insights/            # Design insights & analysis helpers
├── reports/             # Report generation
├── visualization/       # Visualization utilities (geometry_3d.py)
├── api.py               # Backward-compat STUB → real code in services/api.py
├── adapters.py          # CSV/Excel adapters
├── beam_pipeline.py     # Multi-step beam design pipeline
└── types.py             # Shared type definitions
```

## API Surface

Before wrapping or calling any function from `api.py`:
```bash
./scripts/python_runtime.sh scripts/discover_api_signatures.py <function_name>
```
NEVER guess parameter names. It's `b_mm` not `width`, `fck` not `concrete_grade`.

The services API currently has 68 public functions and 15 internal helpers. Key entry points:
- `design_beam_is456()` — Main beam design
- `detail_beam_is456()` — Detailing
- `beam_to_3d_geometry()` — 3D geometry (in `visualization/geometry_3d.py`)
- `GenericCSVAdapter` — CSV parsing (in `services/adapters.py`, 40+ column mappings)

**Stub warning:** `Python/structural_lib/api.py` is a backward-compat stub. Real code → `services/api.py`.

## Key files to check BEFORE coding

- `services/api.py` — 68 public functions and 15 internal helpers, the real entry point
- `codes/is456/` — all IS 456 math lives here
- `core/` — base types, sections, materials
- Before wrapping API functions: `./scripts/python_runtime.sh scripts/discover_api_signatures.py <func>`
- Never guess parameter names (`b_mm` not `width`, `fck` not `concrete_grade`)

## Migration Scripts

- **Move a module:** `./scripts/python_runtime.sh scripts/migrate_python_module.py <src> <dst> --dry-run`
- **Validate imports:** `./scripts/python_runtime.sh scripts/validate_imports.py --scope structural_lib`

## Testing & Quality

- Tests: `./scripts/python_runtime.sh -m pytest Python/tests/ -v` (85% branch coverage required)
- Production code requires a Codex-managed branch and PR through the connected GitHub integration.

## Cross-Platform File I/O

Always use `encoding="utf-8"` with `Path.read_text()` and `Path.write_text()`. Windows defaults to cp1252, causing `UnicodeDecodeError` in CI.

```python
# WRONG — fails on Windows CI
content = filepath.read_text()
filepath.write_text(content)

# RIGHT — works everywhere
content = filepath.read_text(encoding="utf-8")
filepath.write_text(content, encoding="utf-8")
```
