---
description: "New feature workflow — search, design, implement, test, commit"
---

# New Feature Workflow

## 1. Search Before Coding

Check what already exists — agents frequently duplicate code:
```bash
ls react_app/src/hooks/                                         # React hooks
ls react_app/src/components/                                    # React components
grep -r "@router" fastapi_app/routers/ | head -30               # API routes
grep "^def " Python/structural_lib/services/api.py | head -20   # Python API
./scripts/python_runtime.sh scripts/find_automation.py "{{feature_topic}}" # Existing scripts
```

## 2. Identify the Right Layer

| What you're adding | Where it goes |
|---------------------|---------------|
| IS 456 calculation | `Python/structural_lib/codes/is456/` |
| API orchestration | `Python/structural_lib/services/` |
| REST endpoint | `fastapi_app/routers/` |
| React UI component | `react_app/src/components/` |
| React data hook | `react_app/src/hooks/` |

## 3. Implement

- Core math: pure functions, explicit units, no I/O
- Services: import from core, orchestrate, no formatting
- UI: call services via API, never duplicate core math
- React: data flows through FastAPI (never parse/calculate locally)

## 4. Test

```bash
.venv/bin/pytest Python/tests/ -v         # Python tests
cd react_app && npm run build                   # React build check
```

## 5. Commit

Production changes require a Codex-managed task branch and PR.

```bash
# Codex reviews the final diff, commits intended paths, pushes, and updates the PR.
```
