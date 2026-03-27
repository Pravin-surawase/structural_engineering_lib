---
name: api-discovery
description: "Discover exact API function signatures, parameter names, and types from structural_lib. Use BEFORE wrapping or calling any API function. Prevents the #1 agent mistake: guessing parameter names (b_mm not width, fck not concrete_grade)."
argument-hint: "Function name to look up, e.g. 'design_beam_is456' or '--all' to list everything"
---

# API Discovery Skill

Discover exact function signatures from `structural_lib/services/api.py` before using them. The #1 cause of agent bugs is guessing parameter names (`b_mm` not `width`, `fck` not `concrete_grade`).

## When to Use

- Before calling ANY function from `api.py`
- Before wrapping an API function in FastAPI or React
- When creating new endpoints or forms
- When unsure about parameter names or types
- NEVER guess parameter names — always verify

## Look Up a Specific Function

```bash
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
```

Output includes:
- Full function signature with all parameters
- Parameter types and defaults
- Return type
- Docstring summary

## List All Public API Functions

```bash
.venv/bin/python scripts/discover_api_signatures.py --all
```

Shows all 23 public functions + 6 private helpers.

## Filter by Keyword

```bash
.venv/bin/python scripts/discover_api_signatures.py --filter beam
.venv/bin/python scripts/discover_api_signatures.py --filter rebar
.venv/bin/python scripts/discover_api_signatures.py --filter detailing
```

## JSON Output (for programmatic use)

```bash
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456 --json
.venv/bin/python scripts/discover_api_signatures.py --all --json
```

## Key API Entry Points

| Function | Purpose | Module |
|----------|---------|--------|
| `design_beam_is456()` | Main beam design | `services/api.py` |
| `detail_beam_is456()` | Detailing (rebar, stirrups) | `services/api.py` |
| `beam_to_3d_geometry()` | 3D geometry generation | `visualization/geometry_3d.py` |
| `GenericCSVAdapter` | CSV/Excel parsing (40+ cols) | `services/adapters.py` |

## Common Parameter Name Traps

| WRONG (guessed) | RIGHT (actual) | Function |
|-----------------|----------------|----------|
| `width` | `b_mm` | `design_beam_is456` |
| `height` / `depth` | `d_mm` | `design_beam_is456` |
| `concrete_grade` | `fck` | `design_beam_is456` |
| `steel_grade` | `fy` | `design_beam_is456` |
| `moment` | `Mu_kNm` | `design_beam_is456` |
| `shear` | `Vu_kN` | `design_beam_is456` |

## Important Warnings

- **Stub file:** `Python/structural_lib/api.py` is a backward-compat stub. Real code is in `services/api.py`.
- **Units are ALWAYS explicit:** mm, N/mm², kN, kNm — never bare numbers.
- **Adapters moved:** `adapters.py` → `services/adapters.py`
- **Geometry moved:** `geometry_3d.py` → `visualization/geometry_3d.py`

## Quick Grep (alternative)

If the script isn't available:
```bash
grep "^def " Python/structural_lib/services/api.py | head -30
```
