# Module 8: Backend — Servers, APIs, and Business Logic

## The Big Idea

The **backend** is the invisible part of the system — it receives requests, processes data, runs calculations, and sends results back. It's where the real work happens. The frontend is the face; the backend is the brain.

---

## Part 1: What Does a Backend Do?

```
User                    Frontend              Backend                 Library
 │                         │                     │                       │
 │  Clicks "Design"        │                     │                       │
 │ ───────────────────────→│                     │                       │
 │                         │  POST /design/beam  │                       │
 │                         │ ───────────────────→│                       │
 │                         │                     │  Validate input       │
 │                         │                     │  ┌─────────────┐     │
 │                         │                     │  │ Pydantic    │     │
 │                         │                     │  └──────┬──────┘     │
 │                         │                     │         │            │
 │                         │                     │  Call library        │
 │                         │                     │ ──────────────────→  │
 │                         │                     │                     │ Calculate
 │                         │                     │  ←──────────────────│ (IS 456)
 │                         │                     │  Return JSON        │
 │                         │ ←───────────────────│                     │
 │  ←─────────────────────│  Show results        │                     │
 │  Sees "Ast: 1206 mm²"  │                     │                     │
```

### Backend responsibilities:
1. **Receive requests** — Listen on a port (e.g., 8000)
2. **Validate input** — Check data types, ranges, required fields
3. **Run business logic** — Call the library, orchestrate workflows
4. **Return responses** — JSON data with proper status codes
5. **Handle errors** — Return useful error messages, not crashes
6. **Security** — Authentication, rate limiting, input sanitization

---

## Part 2: FastAPI — The Framework

**FastAPI** is a Python web framework that makes building APIs fast and safe.

### Minimal FastAPI app:
```python
from fastapi import FastAPI

app = FastAPI(title="Structural Design API")

@app.get("/health")
def health_check():
    """Check if the server is running."""
    return {"status": "ok"}

@app.post("/api/v1/design/beam")
def design_beam(input: BeamInput):
    """Design a beam per IS 456:2000."""
    result = structural_lib.design_beam_is456(**input.model_dump())
    return result
```

### Running the server:
```bash
# Development (auto-reload on file changes)
uvicorn fastapi_app.main:app --reload --port 8000

# Or with the project launcher
./run.sh dev
```

### What you get:
```
http://localhost:8000          → API root
http://localhost:8000/docs     → Interactive Swagger UI
http://localhost:8000/redoc    → Alternative docs (ReDoc)
http://localhost:8000/health   → Health check
```

---

## Part 3: Routes — Mapping URLs to Functions

A **route** maps a URL path + HTTP method to a Python function.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/design", tags=["design"])

@router.post("/beam")           # POST /api/v1/design/beam
def design_beam(input: BeamInput):
    ...

@router.post("/column")        # POST /api/v1/design/column
def design_column(input: ColumnInput):
    ...

@router.post("/column/axial")  # POST /api/v1/design/column/axial
def column_axial(input: AxialInput):
    ...
```

### This project's router organization:
```
fastapi_app/routers/
├── design.py          ← /api/v1/design/beam
├── column.py          ← /api/v1/design/column/* (14 endpoints)
├── detailing.py       ← /api/v1/detailing/beam
├── geometry.py        ← /api/v1/geometry/beam/full
├── imports.py         ← /api/v1/import/csv
├── export.py          ← /api/v1/export/bbs|dxf|report
├── insights.py        ← /api/v1/insights/dashboard
├── optimization.py    ← /api/v1/optimization/*
├── rebar.py           ← /api/v1/rebar/*
├── analysis.py        ← /api/v1/analysis/*
├── streaming.py       ← SSE batch endpoints
├── websocket.py       ← WebSocket live design
└── health.py          ← /health
```

13 routers, 60+ endpoints.

---

## Part 4: Request → Processing → Response

### Step-by-step:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from structural_lib import design_beam_is456

router = APIRouter()

# Step 1: Define the input schema
class BeamInput(BaseModel):
    b_mm: float = Field(gt=0, description="Width in mm")
    d_mm: float = Field(gt=0, description="Effective depth in mm")
    fck: float = Field(ge=15, le=80)
    fy: float = Field(default=500, ge=250, le=600)
    Mu_kNm: float = Field(gt=0)

# Step 2: Define the route
@router.post("/api/v1/design/beam")
def design_beam(input: BeamInput):
    # Step 3: FastAPI + Pydantic auto-validate the input
    # If we get here, input is guaranteed valid

    try:
        # Step 4: Call the library (business logic)
        result = design_beam_is456(
            b_mm=input.b_mm,
            d_mm=input.d_mm,
            fck=input.fck,
            fy=input.fy,
            Mu_kNm=input.Mu_kNm,
        )

        # Step 5: Return the result (auto-converted to JSON)
        return result

    except ValueError as e:
        # Step 6: Handle domain errors
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        # Step 7: Handle unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Part 5: Middleware — Code That Runs on Every Request

**Middleware** sits between the incoming request and your route handler.

```
Request → Middleware 1 → Middleware 2 → Route Handler
                                          │
Response ← Middleware 1 ← Middleware 2 ← ─┘
```

### Common middleware:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: Allow frontend (port 5173) to call backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### What middleware does:
| Middleware | Purpose |
|-----------|---------|
| CORS | Allow cross-origin requests (frontend→backend) |
| Authentication | Check JWT tokens |
| Logging | Log every request and response |
| Rate limiting | Prevent too many requests |
| Error handling | Catch unhandled exceptions |

---

## Part 6: Pydantic Models — Input/Output Contracts

Pydantic models define exactly what data the API accepts and returns.

### Input model:
```python
class BeamDesignRequest(BaseModel):
    b_mm: float = Field(gt=0, description="Section width")
    d_mm: float = Field(gt=0, description="Effective depth")
    fck: float = Field(ge=15, le=80, description="Concrete grade")
    fy: float = Field(default=500, description="Steel grade")
    Mu_kNm: float = Field(gt=0, description="Ultimate moment")
    Vu_kN: float = Field(default=0, ge=0, description="Ultimate shear")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "b_mm": 300, "d_mm": 500, "fck": 25,
                "fy": 500, "Mu_kNm": 150, "Vu_kN": 75
            }]
        }
    }
```

### Output model:
```python
class FlexureResult(BaseModel):
    Ast_required_mm2: float
    Mu_capacity_kNm: float
    xu_mm: float
    xu_max_mm: float
    status: str  # "SAFE" or "UNSAFE"

class BeamDesignResponse(BaseModel):
    flexure: FlexureResult
    shear: ShearResult | None = None
    detailing: DetailingResult | None = None
```

### Where models live in this project:
```
fastapi_app/models/
├── beam.py        ← BeamDesignRequest, BeamDesignResponse
├── column.py      ← Column-related models
├── common.py      ← Shared models (ErrorResponse, etc.)
└── export.py      ← Export-related models
```

---

## Part 7: Environment Configuration

Backends need configuration that changes between environments (dev, staging, production).

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Structural Design API"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]
    jwt_secret: str = "change-me-in-production"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"  # Load from .env file
```

### Different environments:
```bash
# .env (development)
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:5173"]

# .env.production
DEBUG=false
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://your-domain.com"]
```

**Rule:** Never hardcode secrets, URLs, or environment-specific values. Use config.

---

## Part 8: Docker — Running the Backend Anywhere

Docker packages the backend + all its dependencies into a container.

### Dockerfile (simplified):
```dockerfile
FROM python:3.11-slim

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY fastapi_app/ ./fastapi_app/
COPY Python/structural_lib/ ./Python/structural_lib/

# Run the server
CMD ["uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml:
```yaml
services:
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
```

### Running:
```bash
# Start Docker runtime (macOS)
colima start --cpu 4 --memory 4

# Run the stack
docker compose up --build           # Production
docker compose -f docker-compose.dev.yml up  # Development (with hot reload)

# Or just use the project launcher
./run.sh dev --docker
```

---

## Part 9: Backend vs Library — Who Does What?

```
┌──────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                 │
│                                                   │
│  ✅ Receives HTTP requests                        │
│  ✅ Validates input (Pydantic)                    │
│  ✅ Maps API params to library params             │
│  ✅ Handles authentication                        │
│  ✅ Returns HTTP responses                        │
│  ✅ Handles errors, logging                       │
│                                                   │
│  ❌ Does NOT implement IS 456 math                │
│  ❌ Does NOT duplicate library logic              │
│  ❌ Does NOT have business rules                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│              LIBRARY (structural_lib)              │
│                                                   │
│  ✅ Implements IS 456:2000 calculations           │
│  ✅ Pure math functions                           │
│  ✅ Domain types and constants                    │
│  ✅ Can be used without FastAPI                   │
│                                                   │
│  ❌ Does NOT handle HTTP                          │
│  ❌ Does NOT validate JSON                        │
│  ❌ Does NOT format responses                     │
│  ❌ Does NOT do authentication                    │
└──────────────────────────────────────────────────┘
```

**The backend is a thin wrapper.** It translates HTTP into function calls and function results back into HTTP. The real work lives in the library.

---

## Part 10: Exercises

1. **Start the API:** Run `./run.sh dev` and visit `http://localhost:8000/docs`. Try each endpoint.
2. **Read a router:** Open any file in `fastapi_app/routers/`. Identify the route, input model, and library call.
3. **Add a health detail:** Modify `/health` to return the library version and number of endpoints.
4. **Trace an error:** Send invalid data to `/api/v1/design/beam`. Follow the error from Pydantic → HTTPException → JSON response.

---

## Part 11: Self-Check

1. **What does a backend do?** Receives requests, validates input, runs logic, returns responses.
2. **What's a route?** A URL path + HTTP method mapped to a Python function.
3. **What's middleware?** Code that runs on every request before/after the route handler.
4. **Why use Pydantic models?** Automatic validation, documentation, and serialization.
5. **Why separate backend from library?** Library can be used independently (pip install, notebook, CLI).
6. **What's CORS?** Cross-Origin Resource Sharing — allows frontend on port 5173 to call backend on port 8000.

---

## Key Takeaway

> The backend is a **translator** — it translates HTTP requests into function calls, and function results back into HTTP responses. Keep it thin. The real logic belongs in the library, where it can be tested independently and used by anyone.

**Next:** [Module 9 — Git](09-git.md) explains how to track changes, collaborate, and automate your workflow.
