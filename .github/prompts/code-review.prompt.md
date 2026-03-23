---
description: "Code review checklist — architecture, units, tests, security"
---

# Code Review Checklist

Use this checklist when reviewing changes to this repository.

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
- [ ] `cd Python && .venv/bin/pytest tests/ -v` passes

## Streamlit (if applicable)

- [ ] No `st.sidebar` inside `@st.fragment` functions
- [ ] Safe patterns used: `.get()` instead of direct key access
- [ ] Scanner passes: `.venv/bin/python scripts/check_streamlit.py --all-pages`

## Documentation

- [ ] Public API changes reflected in docs
- [ ] File moves used `safe_file_move.py` (preserves 870+ links)
