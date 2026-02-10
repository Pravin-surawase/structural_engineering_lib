---
applyTo: "**/structural_lib/**"
---

# Python Core Library Rules

## Architecture

- 3-layer architecture: Core (`codes/is456/`) cannot import from App or UI layers
- Units always explicit: mm, N/mm2, kN, kNm — no hidden conversions

## Folder Structure

```
Python/structural_lib/
├── __init__.py          # Package root
├── codes/               # Code implementations (IS 456 etc.)
│   └── is456/           # IS 456:2000 — pure math, NO I/O
├── core/                # Shared types, base classes, materials
├── insights/            # Design insights & analysis helpers
├── reports/             # Report generation
├── visualization/       # Visualization utilities
├── api.py               # Public API (43 functions) — orchestration layer
├── adapters.py          # CSV/Excel adapters
├── beam_pipeline.py     # Multi-step beam design pipeline
└── types.py             # Shared type definitions
```

## Key files to check BEFORE coding

- `api.py` — 43 public functions, the main entry point
- `codes/is456/` — all IS 456 math lives here
- `core/` — base types, sections, materials
- Before wrapping API functions: `.venv/bin/python scripts/discover_api_signatures.py <func>`
- Never guess parameter names (`b_mm` not `width`, `fck` not `concrete_grade`)

## Migration Scripts

- **Move a module:** `.venv/bin/python scripts/migrate_python_module.py <src> <dst> --dry-run`
- **Validate imports:** `.venv/bin/python scripts/validate_imports.py --scope structural_lib`

## Testing & Quality

- Tests: `cd Python && .venv/bin/pytest tests/ -v` (85% branch coverage required)
- Production code always requires PR: `./scripts/create_task_pr.sh TASK-XXX "desc"`
