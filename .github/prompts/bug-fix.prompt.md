---
description: "Bug fix workflow — reproduce, diagnose, fix, test, commit"
---

# Bug Fix Workflow

## 1. Reproduce

- Find the failing test or create a minimal reproduction
- Check if there's an existing test:
  ```bash
  grep -r "{{bug_keyword}}" Python/tests/ --include="*.py" -l
  ```

## 2. Diagnose

- Check the relevant code layer:
  - IS 456 math? → `Python/structural_lib/codes/is456/`
  - API orchestration? → `Python/structural_lib/services/api.py`
  - React UI? → `react_app/src/`
  - FastAPI route? → `fastapi_app/routers/`
- Use exact parameter names:
  ```bash
  .venv/bin/python scripts/discover_api_signatures.py {{function_name}}
  ```

## 3. Fix

- Make the minimal change needed
- Respect architecture boundaries (Core ← IS 456 ← Services ← UI)
- Keep units explicit (mm, N/mm², kN, kNm)

## 4. Test

```bash
.venv/bin/pytest Python/tests/ -v -k "{{test_name}}"
.venv/bin/pytest Python/tests/ -v        # Full suite
```

## 5. Commit

```bash
./scripts/should_use_pr.sh --explain
./scripts/ai_commit.sh "fix(scope): description of fix"
```
