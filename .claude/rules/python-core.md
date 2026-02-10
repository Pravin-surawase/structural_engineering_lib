---
description: Rules for editing the Python structural_lib core
globs: Python/structural_lib/**
---

# Python Core Library Rules

## 3-Layer Architecture — STRICT

Core modules (`codes/is456/`) CANNOT import from App (`api.py`) or UI layers.
Core is pure math — no I/O, no formatting, no HTTP, no file operations.

## Units are ALWAYS explicit

All parameters and return values use explicit units: mm, N/mm2, kN, kNm.
No hidden conversions. No assumptions about input units.

## API Surface

Before wrapping or calling any function from `api.py`:
```bash
.venv/bin/python scripts/discover_api_signatures.py <function_name>
```
NEVER guess parameter names. It's `b_mm` not `width`, `fck` not `concrete_grade`.

The public API has 43 functions. Key entry points:
- `design_beam_is456()` — Main beam design
- `detail_beam_is456()` — Detailing
- `beam_to_3d_geometry()` — 3D geometry (in geometry_3d.py)
- `GenericCSVAdapter` — CSV parsing (in adapters.py, 40+ column mappings)

## Testing

```bash
cd Python && .venv/bin/pytest tests/ -v
```
CI requires 85% branch coverage. Add tests for any behavior changes.

## Production code requires PR

Never direct-commit changes to `Python/structural_lib/`. Use:
```bash
./scripts/create_task_pr.sh TASK-XXX "description"
```
