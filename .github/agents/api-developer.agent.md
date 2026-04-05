---
description: "FastAPI routers, REST endpoints, WebSocket, Pydantic models, OpenAPI"
tools: ['search', 'editFiles', 'runInTerminal', 'listFiles', 'readFile']
model: Claude Opus 4.6 (copilot)
permission_level: WorkspaceWrite
registry_ref: agents/agent_registry.json
handoffs:
  - label: Frontend Integration
    agent: frontend
    prompt: "Create a React hook for the API endpoint implemented above."
    send: false
  - label: Backend Function Needed
    agent: backend
    prompt: "The API endpoint above needs a new or modified function in structural_lib."
    send: false
  - label: Review Changes
    agent: reviewer
    prompt: "Review the API changes made above."
    send: false
  - label: Back to Planning
    agent: orchestrator
    prompt: "API work is complete. Plan the next steps."
    send: false
---

# API Developer Agent

> **Config precedence:** Agent-specific (.agent.md) > file-type (.instructions.md) > global (copilot-instructions.md). See [config-precedence.md](../../docs/architecture/config-precedence.md).

You are a FastAPI specialist for **structural_engineering_lib**.

> Architecture, git rules, and session workflow are in global instructions — not repeated here.
> For fast context: `bash scripts/agent_brief.sh --agent api-developer`

## Terminal Commands

```bash
# Check existing routes before adding
grep -r "@router" fastapi_app/routers/ | head -30

# Run API tests
.venv/bin/pytest fastapi_app/tests/ -v
.venv/bin/pytest fastapi_app/tests/ -v -k "test_design"  # Specific router

# Get exact API function signatures (NEVER guess param names)
.venv/bin/python scripts/discover_api_signatures.py <function_name>

# Docker testing (start Colima FIRST on Mac)
colima start --cpu 4 --memory 4
docker compose up --build                              # Production at :8000/docs
docker compose -f docker-compose.dev.yml up            # Dev with hot reload

# Quick validation
./run.sh check --quick                                 # Or: bash run.sh check --quick
```

> See terminal-rules.instructions.md for fallback chain when commands fail.

## Check Existing Routes First

```bash
grep -r "@router" fastapi_app/routers/ | head -30
```

59 endpoints across 13 routers already exist. Do NOT duplicate.

## Existing Routers

| Router | Key Endpoints |
|--------|---------------|
| **design** | `POST /api/v1/design/beam`, `/beam/check`, `/beam/torsion`, `/beam/enhanced-shear`, `/beam/ductility-check`, `/beam/slenderness-check`, `/beam/deflection-check`, `/beam/crack-width-check`, `/beam/compliance`, `GET /limits` |
| **column** | `POST /effective-length`, `/classify`, `/eccentricity`, `/axial`, `/uniaxial`, `/interaction-curve`, `/biaxial-check`, `/additional-moment`, `/long-column`, `/helical-check`, `/design/column` (unified), `/detailing` |
| **detailing** | `POST /api/v1/detailing/beam`, `GET /bar-areas`, `/development-length/{d}`, `POST /anchorage-check` |
| **analysis** | `POST /api/v1/analysis/loads/simple`, `/beam/smart`, `GET /limiting-values` |
| **imports** | `POST /csv`, `/csv/text`, `/dual-csv`, `/batch-design`, `GET /formats`, `/sample` |
| **geometry** | `POST /beam/3d`, `/beam/full`, `/reference-geometry`, `/building`, `/cross-section` |
| **insights** | `POST /dashboard`, `/code-checks`, `/suggestions`, `/project-boq` |
| **optimization** | `POST /beam/cost`, `GET /cost-rates` |
| **rebar** | `POST /validate`, `/apply` |
| **export** | `POST /bbs`, `/dxf`, `/report`, `/building-summary` |
| **health** | `GET /health`, `/ready`, `/info` |
| **streaming** | `GET /batch-design`, `/job/{job_id}` |
| **websocket** | `WS /ws/design/{session_id}` |

## After Work: Hand off to @reviewer with files changed, endpoints added/modified, Pydantic models, curl example.

## Skills: Use `/api-discovery` for param lookup, `/development-rules` for FastAPI rules (FA-1 through FA-7).

## Development Rules Quick Reference

Before writing any FastAPI code, review these critical rules from `/development-rules`:

| Rule | Description |
|------|-------------|
| FA-1 | NEVER use `str(e)` in error responses — generic messages only |
| FA-2 | All endpoints must have rate limiting |
| FA-3 | WebSocket inputs validated via Pydantic |
| FA-4 | CORS from config/env, never hardcoded |
| FA-6 | Routers import from `structural_lib` — never reimplement math |
| FA-7 | No internal paths or stack traces in responses |

## Rules

1. **Routers import from `structural_lib`** — never duplicate math logic
2. **Pydantic models** in `fastapi_app/models/` — validate inputs
3. **Check existing before adding** — avoid route duplication
4. **Test with Docker:** `docker compose up --build` (start Colima first)
5. **API docs auto-generated** at `http://localhost:8000/docs`

## Architecture

```
fastapi_app/
├── main.py          # App factory, middleware, CORS
├── config.py        # Settings
├── auth.py          # Auth (if needed)
├── models/          # Pydantic request/response models
├── routers/         # 13 router files
├── examples/        # Example requests
└── tests/           # API tests (86+ tests)
```

## MANDATORY: Quality Pipeline for New Endpoints

When adding a FastAPI endpoint for a new IS 456 function, you are executing Step 7 of the `/function-quality-pipeline`. Requirements:

### Pre-requisites (MUST be done before you start)
- [ ] IS 456 math function exists in `codes/is456/` (Step 3 complete)
- [ ] Tests pass for the math function (Step 4 complete)
- [ ] Math reviewed by @structural-engineer (Step 5 complete)
- [ ] Function wired into `services/api.py` by @backend (Step 6 complete)

### Endpoint Quality Checklist
- [ ] Pydantic request model with explicit unit fields (`b_mm: float`, `fck: float`)
- [ ] Pydantic response model matching the frozen dataclass result
- [ ] Unit plausibility guards (reject if b_mm > 10000 — likely meters not mm)
- [ ] Input validation via Pydantic (min/max constraints)
- [ ] Router imports from `structural_lib` — NEVER reimplements math
- [ ] API test in `fastapi_app/tests/` with success + error cases
- [ ] Endpoint documented in OpenAPI (auto-generated from Pydantic models)

### Unit Plausibility Guards (prevent #1 user mistake)

Add input range validation to catch unit confusion:

```python
from pydantic import Field

class ColumnDesignRequest(BaseModel):
    b_mm: float = Field(..., ge=100, le=3000, description="Column width in mm")
    D_mm: float = Field(..., ge=100, le=3000, description="Column depth in mm")
    height_mm: float = Field(..., ge=500, le=50000, description="Column height in mm")
    fck: float = Field(..., ge=15, le=80, description="Concrete strength in N/mm²")
    fy: float = Field(..., ge=250, le=600, description="Steel yield strength in N/mm²")
    Pu_kN: float = Field(..., ge=0, description="Axial load in kN")
```

**Why:** Engineers mistakenly pass meters instead of mm (300mm → 0.3). Pydantic constraints catch this at the API boundary.

### Endpoint Patterns for New Elements

Follow the existing beam endpoint pattern:

```python
# fastapi_app/routers/column.py
from fastapi import APIRouter
from structural_lib.services.api import design_column_is456

router = APIRouter(prefix="/api/v1/design", tags=["column"])

@router.post("/column")
async def design_column(request: ColumnDesignRequest) -> ColumnDesignResponse:
    result = design_column_is456(**request.model_dump())
    return ColumnDesignResponse.from_result(result)
```

### Error Response Standards

All endpoints must return structured errors matching the library's error hierarchy:

```python
# Error responses include:
# - error_code: "E_COLUMN_001"
# - message: "Column section too slender for IS 456 Cl 25.3.1"
# - recovery: "INCREASE_SECTION" (when available)
# - clause_ref: "25.3.1"
```

### Handoff After Endpoint Creation

After creating the endpoint:
1. → @reviewer for API review
2. → @doc-master for documentation
3. → @ops for safe commit
```

See [fastapi.instructions.md](../instructions/fastapi.instructions.md) for full rules.
