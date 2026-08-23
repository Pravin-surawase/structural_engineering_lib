---
description: "Essential-only code review — main-process outcome, architecture, and units"
---

# Code Review Checklist

Use this checklist when reviewing changes to this repository.

## Essential-Only Gate

Before applying the checklist, define the main process changed by the work. For every potential finding, answer: **Would fixing this change the outcome of the main process?** If not, ignore it. Do not report comment-only concerns, edge cases, test-coverage or falsification gaps, generic hardening, adjacent improvements, or security/concurrency observations that are merely hardening. Do not add or request tests during review. File a follow-up bead/task only when a non-essential concern truly needs preservation. Within the scoped main process, trace confirmed defects to their root cause and verify the corrected outcome completely.

## Architecture Boundaries

- [ ] Core (`codes/is456/`) does NOT import from Services or UI
- [ ] Services does NOT import from UI layer
- [ ] React components do NOT calculate math locally (must go through FastAPI)
- [ ] FastAPI routers import from `structural_lib` (no reimplemented math)

## Units & Safety

- [ ] All parameters use explicit units: `b_mm`, `fck` (N/mm²), `Mu_kNm`
- [ ] No hidden unit conversions (`* 1000`, `* 1e6` patterns)
- [ ] Division operations guard against zero: `a / b if b != 0 else 0`

## IS 456 Compliance

- [ ] Formulas match IS 456:2000 clause references
- [ ] Python and VBA implementations produce identical results
- [ ] Edge cases handled (min reinforcement, max spacing, etc.)

## Code Quality

- [ ] No duplicate hooks/components (check `react_app/src/hooks/`, `react_app/src/components/`)
- [ ] No duplicate API routes (check `grep -r "@router" fastapi_app/routers/`)
- [ ] Tests added/updated for behavior changes
- [ ] Test coverage maintained (85% branch coverage target for Python)
- [ ] `./scripts/python_runtime.sh -m pytest Python/tests/ -v` passes

## Documentation

- [ ] Public API changes reflected in docs
- [ ] File moves used `safe_file_move.py` (preserves 870+ links)
