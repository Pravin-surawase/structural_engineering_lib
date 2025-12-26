# Copilot Instructions — structural_engineering_lib

## What this project is
IS 456 RC beam design library with **Python + VBA parity**.

## Non-negotiables
- Deterministic calculations (no hidden defaults).
- Units must be explicit and consistent.
- Keep Python/VBA behavior aligned.
- Prefer minimal, surgical changes.

## Always load this context first
- docs/AI_CONTEXT_PACK.md
- docs/PROJECT_OVERVIEW.md
- docs/API_REFERENCE.md
- docs/KNOWN_PITFALLS.md
- docs/TASKS.md

## Coding rules
- Don’t mix UI/I-O code into core calculation modules.
- Add/extend tests with every behavior change (Python at minimum).
- If you move files, keep redirect stubs to avoid breaking links.- Format Python code with `black` before committing.
## Definition of done
- Tests pass (at least Python).
- Docs updated where contracts/examples changed.
- No unrelated refactors.
- Code formatted with `black` (run `python -m black .` in Python/ directory).

---

## Layer architecture (always respect)

| Layer | Python | VBA | Rules |
|-------|--------|-----|-------|
| **Core** | `flexure.py`, `shear.py`, `detailing.py`, `serviceability.py`, `compliance.py`, `tables.py`, `ductile.py`, `materials.py`, `constants.py`, `types.py`, `utilities.py` | `M01-M07, M15-M17` | Pure functions, no I/O, explicit units |
| **Application** | `api.py`, `job_runner.py`, `bbs.py`, `rebar_optimizer.py` | `M08_API` | Orchestrates core, no formatting |
| **UI/I-O** | `excel_integration.py`, `dxf_export.py`, `job_cli.py` | `M09_UDFs`, macros | Reads/writes external data |

## Units convention
- **Inputs:** mm, N/mm², kN, kN·m
- **Internal:** mm, N, N·mm (convert at layer boundaries)
- **Outputs:** mm, N/mm², kN, kN·m

## Mac VBA safety (critical for VBA changes)
- Wrap dimension multiplications in `CDbl()`: `CDbl(b) * CDbl(d)`
- Never pass inline boolean expressions to `ByVal` args — use local variable first
- No `Debug.Print` interleaved with floating-point math
- Prefer `Long` over `Integer`

## Testing requirements
- Each calculation function needs unit tests
- Include edge cases: min/max values, boundary conditions
- Tolerance: ±0.1% for areas, ±1mm for dimensions
- Document source for expected values (SP:16, textbook, hand calc)

## Role context (see agents/*.md for full details)
When working on specific task types, apply these focuses:
- **Implementation:** Layer-aware, clause refs in comments, Mac-safe
- **Testing:** Benchmark sources, edge cases, tolerance specs
- **Integration:** Schema validation, unit mapping, error surfacing
- **Docs:** API examples, units documented, changelog entries
