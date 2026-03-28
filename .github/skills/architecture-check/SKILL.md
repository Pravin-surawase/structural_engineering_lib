---
name: architecture-check
description: "Validate 4-layer architecture boundaries, import direction, code duplication, and structural integrity. Use during code review or after cross-layer changes. Wraps check_architecture_boundaries.py, validate_imports.py, and duplication scans."
argument-hint: "Optional: 'boundaries' | 'imports' | 'duplication' | 'all' (default: all)"
---

# Architecture Check Skill

Validate the 4-layer architecture, import direction, and code duplication rules.

## When to Use

- During code review (reviewer agent)
- After any change that touches multiple layers
- After adding new imports across modules
- Before merging PRs that modify `structural_lib/`, `fastapi_app/`, or `react_app/`

## Architecture Layers (Strict)

```
Layer 1: Core types    → Python/structural_lib/core/         # Base classes, types (NO IS 456 math)
Layer 2: IS 456 Code   → Python/structural_lib/codes/is456/  # Pure math, NO I/O, explicit units
Layer 3: Services      → Python/structural_lib/services/      # Orchestration: api.py, adapters.py
Layer 4: UI/IO         → react_app/, fastapi_app/             # External interfaces
```

**Import rule:** Core ← IS 456 ← Services ← UI. Never import upward.

## Full Architecture Validation

```bash
.venv/bin/python scripts/check_architecture_boundaries.py
```

Checks:
- No upward imports (Core importing from Services, Services from UI)
- IS 456 layer has no I/O operations
- FastAPI routers only import from Services layer

## Import Validation

```bash
.venv/bin/python scripts/validate_imports.py --scope structural_lib
```

Checks:
- No circular imports
- No broken import paths
- Import direction follows layer hierarchy

## Circular Import Check

```bash
.venv/bin/python scripts/check_circular_imports.py
```

## Duplication Scan

### React hooks (most common duplication):
```bash
ls react_app/src/hooks/
# Compare with the 21 existing hooks listed in frontend.agent.md
```

### FastAPI routes:
```bash
grep -r "@router" fastapi_app/routers/ | sort
# Check for duplicate HTTP method + path combinations
```

### Python API functions:
```bash
grep "^def " Python/structural_lib/services/api.py | head -30
# Verify no function duplicates the logic of an existing one
```

## Quick Check (< 30 seconds)

```bash
./run.sh check --quick
```

Runs 8 fast checks including architecture boundaries.

## Full Check (28 checks)

```bash
./run.sh check
```

## Common Violations

| Violation | Example | Fix |
|-----------|---------|-----|
| Upward import | `codes/is456/flexure.py` imports from `services/` | Move shared code to `core/` |
| Math in UI | React component calculates reinforcement | Move to API endpoint + structural_lib |
| Math in router | FastAPI router computes shear capacity | Call `structural_lib` function instead |
| I/O in IS 456 | `codes/is456/` reads a file or network | Move I/O to Services layer |
| Duplicate hook | New `useCSVImport` when `useCSVFileImport` exists | Use existing hook |

## Interpreting Results

- **PASS (0 violations):** Architecture is clean
- **WARNING (1-2 minor):** Fix before merge
- **FAIL (3+ or critical):** Block the PR, fix immediately
