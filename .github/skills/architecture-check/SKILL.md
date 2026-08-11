---
name: architecture-check
description: "Validate the live four-layer Python architecture and import resolution after cross-layer changes. Report only confirmed violations that change the scoped main process."
argument-hint: "Optional: 'boundaries' | 'imports' | 'duplication' | 'all' (default: all)"
---

# Architecture Check

Validate the four-layer architecture and imports from the workspace root.

## When to Use

- After a change adds or moves imports between architecture layers
- During review of a cross-layer Python or FastAPI change
- When diagnosing a confirmed layer-boundary failure

## Architecture Layers (Strict)

```
Layer 1: Core types    → Python/structural_lib/core/         # Base classes, types (NO IS 456 math)
Layer 2: IS 456 Code   → Python/structural_lib/codes/is456/  # Pure math, NO I/O, explicit units
Layer 3: Services      → Python/structural_lib/services/      # Orchestration: api.py, adapters.py
Layer 4: UI/IO         → react_app/, fastapi_app/             # External interfaces
```

**Import rule:** Core ← IS 456 ← Services ← UI. Never import upward.

## Boundary Validation

```bash
./scripts/python_runtime.sh scripts/check_architecture_boundaries.py
```

Checks:
- Core does not import IS 456, Services, or UI
- IS 456 does not import Services or UI and does not perform ordinary file I/O
- Services does not import UI
- FastAPI does not bypass Services/public APIs to import Core or IS 456 internals

## Import Validation

```bash
./scripts/python_runtime.sh scripts/validate_imports.py --scope structural_lib
```

This is a separate resolution check. It catches broken module paths; the boundary checker owns layer direction.

Run the circular-import checker only if the change creates an import cycle or the normal import validation reports one:

```bash
./scripts/python_runtime.sh scripts/check_circular_imports.py
```

Do not run generic duplication scans as part of this skill. Before adding a new hook, route, or public function, use targeted `rg` in that component to locate an existing implementation.

## Gate Relationship

```bash
./run.sh check --quick
```

The quick gate validates import/hygiene essentials but is not evidence that the full architecture boundary checker ran. Run the boundary command above for architecture work.

`./run.sh check` includes the architecture checker and runs once at implementation closeout.

## Common Violations

| Violation | Example | Fix |
|-----------|---------|-----|
| Upward import | `codes/is456/beam/flexure.py` imports `services/` | Move the dependency to `core/` or orchestrate it from Services |
| Math in UI | React component calculates reinforcement | Move to API endpoint + structural_lib |
| Math in router | FastAPI router computes shear capacity | Call `structural_lib` function instead |
| I/O in IS 456 | `codes/is456/` reads a file or network | Move I/O to Services layer |
| Duplicate hook | New `useCSVImport` when `useCSVFileImport` exists | Use existing hook |

## Review Decision

A nonzero checker result blocks a cross-layer change only when the reported import is introduced or exercised by the scoped main process. Fix the root dependency direction. Do not turn unrelated pre-existing findings, comments, coverage gaps, or generic cleanup into current-scope work.
