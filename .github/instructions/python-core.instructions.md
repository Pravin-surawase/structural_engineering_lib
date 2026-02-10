---
applyTo: "**/structural_lib/**"
---

# Python Core Library Rules

- 3-layer architecture: Core (`codes/is456/`) cannot import from App or UI layers
- Units always explicit: mm, N/mm2, kN, kNm — no hidden conversions
- Before wrapping API functions: `.venv/bin/python scripts/discover_api_signatures.py <func>`
- Never guess parameter names (`b_mm` not `width`, `fck` not `concrete_grade`)
- Tests: `cd Python && .venv/bin/pytest tests/ -v` (85% branch coverage required)
- Production code always requires PR: `./scripts/create_task_pr.sh TASK-XXX "desc"`
