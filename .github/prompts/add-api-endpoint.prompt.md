---
description: "Add a new FastAPI endpoint — check routes, implement, test"
---

# Add FastAPI Endpoint

Follow this workflow when adding a new API endpoint to `fastapi_app/`.

## Pre-Check

1. **Check existing routes** — avoid duplicating:
   ```bash
   grep -r "@router" fastapi_app/routers/ | head -30
   ```

2. **Check if the core function exists** in structural_lib:
   ```bash
   .venv/bin/python scripts/discover_api_signatures.py {{function_name}}
   ```

3. **Check existing Pydantic models:**
   ```bash
   ls fastapi_app/models/
   ```

## Implementation

1. Add the route to the appropriate router in `fastapi_app/routers/`
2. Import the core function from `structural_lib` — NEVER reimplement math
3. Create request/response Pydantic models in `fastapi_app/models/` if needed
4. Use explicit units in model field names: `b_mm`, `fck`, `Mu_kNm`

## Validation

1. Test with Docker:
   ```bash
   docker compose up --build
   ```
2. Check auto-generated docs at `http://localhost:8000/docs`
3. Run API tests:
   ```bash
   .venv/bin/pytest Python/tests/ -v -k "test_api"
   ```

## Commit

```bash
./scripts/should_use_pr.sh --explain    # FastAPI changes require PR
./scripts/create_task_pr.sh TASK-XXX "feat(fastapi): add endpoint description"
```
