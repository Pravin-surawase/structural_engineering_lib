# Day 15: FastAPI Basics — Turning Pure Math into a Live API

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** High
**Created:** 2026-04-08
**Last Updated:** 2026-04-08
**Prerequisites:** Days 1-11 (core library), Day 12 (insights — you know what `api.py` returns)
**Library files:** `fastapi_app/main.py`, `fastapi_app/routers/design.py`, `fastapi_app/routers/column.py`, `fastapi_app/models/beam.py`, `fastapi_app/models/response.py`, `fastapi_app/error_utils.py`, `fastapi_app/config.py`
**IS 456 Clauses:** N/A — this day is about the API layer, not the math

---

## What You'll Learn Today

By the end of this module you'll understand:
- What FastAPI is and why it beats Flask/Django for a typed math library
- How the full request lifecycle works: HTTP → Pydantic → Router → structural_lib → Response
- The "Waiter Pattern" — why routers are thin wrappers that NEVER duplicate math
- How `main.py` acts as an application factory wiring middleware, routers, and exception handlers
- How Pydantic V2 models validate inputs before your code even sees them
- How `error_utils.py` prevents CWE-209 information leakage
- Why CORS exists and how two different ports (`:5173` and `:8000`) talk to each other
- How OpenAPI docs at `/docs` are generated with zero manual effort

---

## Part 1: Why FastAPI? — The Right Tool for a Math Library

When you have a pure-math Python library (like `structural_lib`), you need a web framework that:
1. **Validates inputs automatically** — engineers send beam dimensions via JSON, and bad values must be rejected before any calculation runs
2. **Documents itself** — 60+ endpoints with typed request/response schemas generate Swagger docs at `/docs` automatically
3. **Stays out of the way** — the framework should be a thin wrapper, not a monolith

FastAPI is built on three pillars that match these needs exactly:

| Pillar | What It Gives You | Why It Matters for Us |
|--------|-------------------|-----------------------|
| **Python type hints** | `def foo(x: int)` — FastAPI validates `x` is int automatically | No manual parsing of JSON fields |
| **Pydantic V2** | Request/response bodies are Pydantic models — validated, typed, documented | `width: -5` is rejected before the router runs |
| **OpenAPI 3.1** | Swagger UI at `/docs`, ReDoc at `/redoc` — zero manual docs | 60+ endpoints documented for free |

> **Think of it like...** a POST office. Flask is the old-school counter where the clerk eyeballs your handwritten form and hopes the zip code is valid. FastAPI is the modern kiosk — it validates each field in real-time, autocompletes known values, and hands you a tracking number before you walk away.

**Why not Flask?** Flask would work, but you'd write validation code by hand for every endpoint. With 60+ endpoints, that's thousands of lines of manual `if not isinstance(width, (int, float)): return error(...)`.

**Why not Django?** Django brings an ORM, admin panel, template engine — we don't need any of that. Our "database" is IS 456:2000 formulas. Django would add complexity with zero benefit.

### The One-Direction Rule

Data flows in one direction through the FastAPI layer:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  HTTP Request │────▶│ Pydantic     │────▶│ Router       │────▶│ structural_  │────▶│ HTTP         │
│  (JSON body)  │     │ Validates    │     │ (thin wrapper)│     │ lib (math)   │     │ Response     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                      Rejects bad input    Passes values        Returns dict         Wraps in JSON
                      with 422 error       to library           of results           with success/error
```

**No math happens in the FastAPI layer. Ever.** If you find a router computing $M_u = 0.138 \cdot f_{ck} \cdot b \cdot d^2$, something is architecturally wrong.

---

## Part 2: Our API Structure — 13 Routers, 60+ Endpoints

Here's the full `fastapi_app/` layout with what each piece does:

```
fastapi_app/
├── main.py          # Application factory — creates app, mounts middleware + routers
├── config.py        # Settings: CORS origins, rate limits, auth toggle, environment
├── auth.py          # JWT token handling + rate limiting middleware
├── error_utils.py   # Sanitize exceptions → safe HTTP error messages (CWE-209)
├── models/          # Pydantic request/response models (the "contracts")
│   ├── beam.py      # BeamDesignRequest, BeamDesignResponse
│   ├── column.py    # ColumnClassifyRequest, ColumnAxialResponse, etc.
│   ├── compliance.py # ComplianceCheckRequest, ComplianceResult
│   ├── response.py  # success_response(), error_response() wrappers
│   └── ...
├── routers/         # 13 router files → 60+ endpoints
│   ├── design.py    # POST /design/beam — flexure, shear, torsion
│   ├── column.py    # POST /design/column/* — 10+ column endpoints
│   ├── detailing.py # POST /detailing/beam — rebar layout, dev lengths
│   ├── imports.py   # POST /import/csv — ETABS/STAAD file import
│   ├── export.py    # POST /export/bbs|dxf|report — file downloads
│   ├── geometry.py  # POST /geometry/beam/full — 3D mesh generation
│   ├── insights.py  # POST /insights/dashboard — code checks, suggestions
│   ├── analysis.py  # Smart analysis, limiting values
│   ├── optimization.py # Cost/multi-objective optimization
│   ├── rebar.py     # Validate/apply rebar selections
│   ├── streaming.py # SSE batch processing (multiple beams)
│   ├── websocket.py # Live design WebSocket (real-time updates)
│   └── health.py    # GET /health — health, readiness, system info
└── tests/           # 86+ API tests (TestClient-based)
```

Each router file creates an `APIRouter` with its own prefix. The `main.py` mounts all routers under `/api/v1`, so:
- `design.py` has `prefix="/design"` → final URL: `/api/v1/design/beam`
- `column.py` has `prefix="/design/column"` → final URL: `/api/v1/design/column/classify`
- `health.py` is mounted at root → final URL: `/health`

---

## Part 3: `main.py` — The Application Factory

The `main.py` file is where everything gets wired together. Think of it as a restaurant's floor plan — it decides where the kitchen door is, which tables are available, and what rules the waiters follow.

```python
# 1. Create the FastAPI instance with OpenAPI metadata
app = FastAPI(
    title="Structural Engineering API",
    description="IS 456:2000 Compliant Structural Engineering Library",
    version=__version__,          # Pulled from structural_lib version
    docs_url="/docs",             # Swagger UI lives here
    redoc_url="/redoc",           # Alternative docs view
)

# 2. Middleware stack (order matters — last added runs FIRST)
app.add_middleware(RequestIDMiddleware)   # Unique X-Request-ID per request
app.add_middleware(CORSMiddleware, ...)   # Allow React on :5173
app.add_middleware(RateLimitMiddleware)   # 120 requests/minute per IP
app.add_middleware(AuthMiddleware)        # JWT auth (opt-in, disabled by default)

# 3. Mount routers — each gets the /api/v1 prefix
app.include_router(design.router,    prefix="/api/v1")
app.include_router(column.router,    prefix="/api/v1")
app.include_router(detailing.router, prefix="/api/v1")
# ... 10 more routers

# 4. Global exception handlers — catch anything routers miss
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(status_code=422, content={...})
```

### Middleware execution order

Middleware wraps around the request like layers of an onion. The **last** middleware added runs **first** on incoming requests:

```
Incoming request:
  → AuthMiddleware (check JWT)
    → RateLimitMiddleware (check rate)
      → CORSMiddleware (add headers)
        → RequestIDMiddleware (assign ID)
          → Router handles request
        ← RequestIDMiddleware
      ← CORSMiddleware
    ← RateLimitMiddleware
  ← AuthMiddleware
← Response sent
```

If AuthMiddleware rejects the request, RateLimitMiddleware never sees it. This is important because expensive operations (like database lookups in auth) should short-circuit early.

### Prefix composition

The `prefix="/api/v1"` from `include_router` combines with each router's own prefix:

| Router file | Router prefix | include_router prefix | Final URL pattern |
|------------|--------------|----------------------|-------------------|
| `design.py` | `/design` | `/api/v1` | `/api/v1/design/beam` |
| `column.py` | `/design/column` | `/api/v1` | `/api/v1/design/column/classify` |
| `health.py` | (none) | (none) | `/health` |
| `imports.py` | `/import` | `/api/v1` | `/api/v1/import/csv` |

---

## Part 4: The Waiter Pattern — Why Routers Never Do Math

Every router endpoint in this codebase follows the same pattern. The analogy is a restaurant:

| Restaurant Role | FastAPI Equivalent | Responsibility |
|----------------|--------------------|----------------|
| Customer's order | `BeamDesignRequest` (Pydantic model) | What the client wants — validated before reaching the kitchen |
| Waiter | Router function (`design_beam`) | Takes order, relays to kitchen, handles complaints, serves the dish |
| Kitchen | `structural_lib` (pure math) | Does the actual cooking — flexure, shear, detailing calculations |
| Plated dish | `success_response(BeamDesignResponse)` | Formatted result served to the customer |

**The waiter never cooks.** If you find a router doing `Ast = 0.5 * fck / fy * (1 - sqrt(...)) * b * d`, something is architecturally broken. The router's job is:

1. **Receive** validated input (Pydantic already checked ranges)
2. **Translate** field names (`request.width` → `b_mm=request.width`)
3. **Call** the library function (`design_beam_is456(...)`)
4. **Wrap** the result in a standardized response envelope
5. **Handle** errors gracefully (no stack traces in responses)

This separation means:
- The library can be tested without HTTP (just call the function)
- The API can be tested without real math (mock the library)
- New frontends (CLI, mobile, etc.) can reuse the same library

---

## Part 5: Beam Design Endpoint — Full Walkthrough

Here's the actual `design_beam` endpoint from `routers/design.py` (simplified for clarity):

```python
# fastapi_app/routers/design.py
from structural_lib.services.api import design_beam_is456

router = APIRouter(prefix="/design", tags=["design"])

@router.post(
    "/beam",
    summary="Design Beam Section",
    description="Calculate required reinforcement for a beam section per IS 456.",
)
async def design_beam(request: BeamDesignRequest):
    try:
        # 1. Calculate effective depth if not provided
        effective_depth = request.effective_depth
        if effective_depth is None:
            effective_depth = (request.depth - request.clear_cover
                              - request.stirrup_dia_mm - request.main_bar_dia_mm / 2)

        # 2. Call structural_lib — the ONLY place math happens
        result = design_beam_is456(
            units="IS456",
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=effective_depth,
            mu_knm=request.moment,
            vu_kn=request.shear,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
        )

        # 3. Format and return
        return success_response(BeamDesignResponse.from_result(result))

    except (ValueError, TypeError):
        return JSONResponse(
            status_code=422,
            content=error_response("Invalid input parameters"),
        )
    except Exception as e:
        msg = sanitize_error(e, context="beam design")
        return JSONResponse(
            status_code=500,
            content=error_response(msg),
        )
```

**Step-by-step breakdown:**

| Line | What happens | Why |
|------|-------------|-----|
| `@router.post("/beam")` | Registers this function as handler for POST `/design/beam` | FastAPI routing |
| `request: BeamDesignRequest` | Pydantic validates JSON body — rejects `width: -5` with 422 | Validation at boundary |
| `effective_depth` calculation | Derives `d` from `D`, cover, stirrup, bar dia if not given | Convenience for clients |
| `design_beam_is456(...)` | Calls pure math — all IS 456 formulas run here | 4-layer architecture |
| `success_response(...)` | Wraps result in `{"success": true, "data": {...}}` | Consistent API contract |
| `sanitize_error(e, ...)` | Strips stack traces, assigns reference ID | Security (CWE-209) |

**Notice the field name translation:** The client sends `"width"` (human-friendly), but the library expects `b_mm` (engineering notation). The router handles this mapping.

---

## Part 6: Pydantic Request Models — Validation at the Gate

The `BeamDesignRequest` is the "bouncer" at the door. Bad inputs never reach the library:

```python
# fastapi_app/models/beam.py
class BeamDesignRequest(BaseModel):
    # Section dimensions — with hard validation limits
    width: float = Field(
        gt=0, le=2000.0,
        description="Beam width b (mm)",
        examples=[230.0, 300.0, 400.0],
    )
    depth: float = Field(
        gt=0, le=3000.0,
        description="Overall beam depth D (mm)",
        examples=[450.0, 600.0, 750.0],
    )

    # Loading
    moment: float = Field(ge=0, description="Factored design moment Mu (kN·m)")
    shear:  float = Field(default=0.0, ge=0, description="Factored shear Vu (kN)")

    # Material properties — sensible defaults + range guards
    fck: float = Field(default=25.0, ge=15.0, le=80.0,
                       description="Concrete strength (N/mm²)")
    fy:  float = Field(default=500.0, ge=250.0, le=600.0,
                       description="Steel yield strength (N/mm²)")

    # Optional with smart defaults
    clear_cover:    float = Field(default=25.0, ge=20.0, le=75.0)
    stirrup_dia_mm: float = Field(default=8.0, ge=6, le=16)
    main_bar_dia_mm: float = Field(default=20.0, ge=8, le=36)
```

**What each `Field(...)` constraint does:**

| Constraint | Example | Rejection scenario |
|-----------|---------|-------------------|
| `gt=0` | `width > 0` | `width: 0` → 422: "greater than 0" |
| `le=2000.0` | `width ≤ 2000` | `width: 50000` → 422: "less than or equal to 2000" |
| `ge=15.0, le=80.0` | `15 ≤ fck ≤ 80` | `fck: 5` → 422: "greater than or equal to 15" |
| `default=25.0` | Omit `fck` → M25 concrete | Client can skip common values |
| `description=` | Appears in Swagger UI | Self-documenting API |
| `examples=` | Dropdown in "Try it out" | Guides new users |

**The critical insight:** Pydantic validation runs **before** your router function is called. If width is -10, the function body never executes — FastAPI returns a 422 automatically. This means the library can trust its inputs.

---

## Part 7: Standardized Responses and Error Sanitization

### The Response Envelope

Every endpoint wraps its output in the same shape:

```python
# fastapi_app/models/response.py
def success_response(data, clause_refs=None):
    result = {"success": True, "data": data}
    if clause_refs:
        result["clause_refs"] = clause_refs
    return result

def error_response(error: str):
    return {"success": False, "data": None, "error": error}
```

This means every client sees a predictable shape:

```json
// Success
{"success": true,  "data": {"Ast_mm2": 603.2, "is_safe": true}, "error": null}

// Failure
{"success": false, "data": null, "error": "Invalid input parameters"}
```

**Why not just return the raw dict?** Because:
- Clients can always check `response.success` before processing data
- Error handling is identical across all 60+ endpoints
- The `clause_refs` field lets endpoints attach IS 456 references

### Error Sanitization (CWE-209 Prevention)

When an exception escapes the library, `error_utils.py` strips dangerous details:

```python
# fastapi_app/error_utils.py
def sanitize_error(e: Exception, context: str = "operation") -> str:
    request_id = uuid.uuid4().hex[:8]
    logger.error("Error in %s [%s]: %s", context, request_id, e, exc_info=True)

    if isinstance(e, (ValueError, TypeError)):
        msg = str(e)
        # Check if the error message leaks file paths or stack traces
        if "/" in msg or "\\" in msg or "Traceback" in msg:
            return f"Invalid input for {context}. Reference: {request_id}"
        return msg  # Safe to expose user-input errors

    # All other exceptions → generic message + reference ID
    return f"Internal error during {context}. Reference: {request_id}"
```

**What this prevents:**
- File paths like `/Users/dev/structural_lib/codes/is456/flexure.py line 142` never reach clients
- Stack traces with internal function names stay server-side
- The `request_id` lets support find the full error in server logs

**The two-tier approach:**
1. `ValueError`/`TypeError` with clean messages → safe to expose (e.g., "Beam width must be positive")
2. Everything else → generic message with tracking ID

---

## Part 8: CORS — Why Two Ports Need Permission to Talk

React runs on `localhost:5173` (Vite dev server). FastAPI runs on `localhost:8000`. These are **different origins** (same host, different port), so the browser blocks requests by default. This is the Same-Origin Policy — a browser security feature.

CORS (Cross-Origin Resource Sharing) tells the browser "yes, this origin is allowed to talk to me":

```python
# fastapi_app/config.py — origins come from settings, not hardcoded
cors_origins: list[str] = [
    "http://localhost:5173",     # Vite dev server
    "http://localhost:3000",     # Alternate React port
]

# fastapi_app/main.py — middleware reads from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    max_age=600,   # Cache preflight for 10 minutes
)
```

**How preflight works:**
1. React sends a POST to `localhost:8000/api/v1/design/beam`
2. Browser first sends an `OPTIONS` request (preflight): "Am I allowed?"
3. FastAPI responds with `Access-Control-Allow-Origin: http://localhost:5173`
4. Browser sees the permission and sends the actual POST
5. `max_age=600` means the browser caches this permission for 10 minutes — no preflight on subsequent requests

**Why origins come from config.py:**
- Development: allow `localhost:5173`
- Production: allow `https://your-domain.com`
- One file to change, not scattered across middleware calls

---

## Part 9: OpenAPI Docs — Self-Documenting API

Open `http://localhost:8000/docs` and you see every endpoint, every request schema, every response schema — generated automatically from your Pydantic models and route decorators:

```
┌─────────────────────────────────────────────────────┐
│  Structural Engineering API  v0.21.6                │
│  ─────────────────────────────────────────────────  │
│                                                     │
│  ▼ design (8 endpoints)                             │
│    POST /api/v1/design/beam                         │
│    POST /api/v1/design/column/classify              │
│    POST /api/v1/design/column/effective-length      │
│    POST /api/v1/design/column/eccentricity          │
│    ... (more)                                       │
│                                                     │
│  ▼ detailing (3 endpoints)                          │
│    POST /api/v1/detailing/beam                      │
│                                                     │
│  ▼ export (3 endpoints)                             │
│    POST /api/v1/export/bbs                          │
│    POST /api/v1/export/dxf                          │
│    POST /api/v1/export/report                       │
│                                                     │
│  ▼ health (1 endpoint)                              │
│    GET /health                                      │
└─────────────────────────────────────────────────────┘
```

**Where the docs come from:**
- Endpoint names → `summary=` and `description=` in `@router.post()`
- Request schemas → `BeamDesignRequest` Pydantic model fields
- Response schemas → `BeamDesignResponse` model (if you use `response_model=`)
- Field descriptions → `description=` in `Field(...)`
- Example values → `examples=` in `Field(...)`

You get "Try it out" buttons for free — click one, fill in values, and send a real request from the browser.

---

## Part 10: Testing with curl — Hands-On

Start the server:
```bash
./run.sh dev --no-react
```

### Health check
```bash
curl http://localhost:8000/health | python -m json.tool
```
```json
{
    "status": "healthy",
    "version": "0.21.6",
    "timestamp": "2026-04-08T10:30:00Z",
    "uptime_seconds": 42.5
}
```

### Design a beam
```bash
curl -X POST http://localhost:8000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{
    "width": 300,
    "depth": 500,
    "moment": 150,
    "shear": 75,
    "fck": 25,
    "fy": 500
  }' | python -m json.tool
```
```json
{
    "success": true,
    "data": {
        "Ast_mm2": 923.4,
        "Asc_mm2": 0.0,
        "is_safe": true,
        "design_type": "singly_reinforced",
        "xu_mm": 102.3,
        "xu_max_mm": 228.0
    }
}
```

### Column effective length
```bash
curl -X POST http://localhost:8000/api/v1/design/column/effective-length \
  -H "Content-Type: application/json" \
  -d '{"l_mm": 3000, "end_condition": "fixed_fixed"}' | python -m json.tool
```

### Trigger a validation error
```bash
curl -X POST http://localhost:8000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{"width": -10, "depth": 500, "moment": 100}'
```
```json
{
    "detail": [
        {
            "type": "greater_than",
            "loc": ["body", "width"],
            "msg": "Input should be greater than 0",
            "input": -10
        }
    ]
}
```

Pydantic rejected `width: -10` **before** the router function even ran.

---

## Part 11: Exercises

**Goal:** Start the API server and deeply explore the request lifecycle.

### Exercise 1: Health → Design → Validate
1. Start: `./run.sh dev --no-react`
2. `curl http://localhost:8000/health` — confirm `"status": "healthy"`
3. Design a beam: `curl -X POST http://localhost:8000/api/v1/design/beam -H "Content-Type: application/json" -d '{"width": 230, "depth": 450, "moment": 80, "shear": 40, "fck": 25, "fy": 415}'`
4. Verify the response is wrapped in `{"success": true, "data": {...}}`
5. Send `width: 99999` — does Pydantic reject it with a 422?

### Exercise 2: Explore the Swagger UI
1. Open `http://localhost:8000/docs` in a browser
2. Find the column endpoints — count how many there are
3. Use "Try it out" on `/api/v1/design/column/classify`
4. Send `{"b_mm": 300, "D_mm": 500, "l_mm": 3000, "end_condition": "fixed_hinged"}`
5. Read the response — what classification did it return?

### Exercise 3: Trace the error path
1. Send a request with `fck: 5` (below the ge=15 minimum)
2. Observe the 422 response — which layer caught it?
3. Now send `fck: 25` but with all other fields missing — what happens?
4. Check: does the `default=` on `fy`, `clear_cover` etc. fill in missing values?

---

## Part 12: Self-Check Q&A

Test yourself — can you answer these without looking back?

1. **What are FastAPI's three pillars?** How does each one reduce code you'd write in Flask?
2. **What's the "Waiter Pattern"?** Why don't routers compute bending moments themselves?
3. **What does `Field(ge=15.0, le=80.0)` do on `fck`?** What happens if a client sends `fck: 5`?
4. **Why do we use `success_response()` / `error_response()` wrappers** instead of returning raw dicts?
5. **What does `sanitize_error()` prevent?** Why not just send `str(e)` to the client?
6. **Why does CORS configuration live in `config.py`** instead of being hardcoded in `main.py`?
7. **What's the difference between a 422 and a 500 response?** When does each occur?
8. **What does `max_age=600` in CORS middleware do?** Why does it improve performance?
9. **Name the field name translation** from client to library for beam width. Why is it different?
10. **What is the middleware execution order?** Why does `AuthMiddleware` run first?

---

## Part 13: Things to Know — Deep Insights

### 13.1: `async def` doesn't mean concurrent
FastAPI endpoints use `async def`, but `design_beam_is456()` is CPU-bound math. When the math runs, the event loop is blocked. This is fine for our use case (computations take <50ms), but if you add database queries or slow I/O, you'd need `await` or `run_in_executor`.

### 13.2: Pydantic V2 vs V1 — breaking changes
This library uses Pydantic V2. If you see old tutorials with `.dict()`, `.schema()`, or `validator`, those are V1 patterns. In V2:
- `.dict()` → `.model_dump()`
- `.schema()` → `.model_json_schema()`
- `@validator` → `@field_validator`
- `Config` inner class → `model_config = ConfigDict(...)`

### 13.3: The 422 vs 500 distinction
- **422 Unprocessable Entity:** Pydantic rejected the input. The client sent bad data. The fix is on the client side.
- **500 Internal Server Error:** The library threw an unexpected exception. The fix is on the server side.
- **Never return 500 for bad input.** If a `ValueError` from the library escapes because Pydantic didn't catch it, your Pydantic model is missing a constraint.

### 13.4: The `prefix` composition trap
If your router has `prefix="/design/column"` and you mount it with `prefix="/api/v1"`, every endpoint is at `/api/v1/design/column/...`. But if you accidentally also add a path in the decorator like `@router.post("/design/column/classify")`, you get `/api/v1/design/column/design/column/classify` — a doubled prefix. Always check the final URL in `/docs`.

### 13.5: `response_model` vs manual wrapping
FastAPI supports `response_model=BeamDesignResponse` in the decorator, which auto-validates the response and strips extra fields. Our codebase mostly uses manual `success_response()` wrapping instead. This means response validation is looser — if the library returns unexpected fields, they pass through.

### 13.6: The error sanitization edge case
`sanitize_error` checks for `/` and `\` in error messages to detect file paths. But engineering messages like "depth/width ratio exceeded" contain `/` and get sanitized to a generic message. This is a known trade-off — false positives are safer than information leaks.

---

## Part 14: What Can Be Done Better

### 14.1: No response model validation
Most endpoints don't use `response_model=` in the decorator, so FastAPI doesn't validate outgoing data. If the library returns an unexpected field or wrong type, the client gets it as-is. Adding `response_model=BeamDesignResponse` would catch these issues.

### 14.2: Manual error handling in every endpoint
Every router has the same `try/except ValueError/except Exception` pattern copied. This could be a decorator or dependency that handles it once:
```python
# Potential improvement — not currently implemented
@catch_and_sanitize("beam design")
async def design_beam(request: BeamDesignRequest):
    result = design_beam_is456(...)
    return success_response(result)
```

### 14.3: No request/response logging middleware
Individual endpoints log errors, but there's no middleware that logs every request/response pair with timing. This makes debugging production issues harder — you can see the error but not what the full request looked like.

### 14.4: Hardcoded rate limit
The rate limit (120 req/min) is set in config but not configurable per-endpoint. Compute-heavy endpoints (optimization, batch design) should have lower limits than simple lookups (health check, column classify).

### 14.5: No API versioning strategy
The `/api/v1` prefix exists, but there's no plan for `/api/v2`. When breaking changes are needed (different field names, different response shapes), there's no deprecation or migration path.

---

## Part 15: Innovation Directions

### 15.1: GraphQL or tRPC alongside REST
For the React frontend, GraphQL or tRPC could replace REST for some use cases. The frontend could request exactly the fields it needs (e.g., just `Ast_mm2` and `is_safe` for a summary view, full results for the detail view), reducing payload sizes.

### 15.2: OpenTelemetry distributed tracing
Adding OpenTelemetry spans around library calls would enable distributed tracing. You could visualize that `design_beam` takes 45ms total: 2ms in Pydantic validation, 38ms in `design_beam_is456()`, 5ms in response serialization.

### 15.3: API SDK generation
Since FastAPI generates an OpenAPI 3.1 spec at `/openapi.json`, tools like `openapi-generator` or `openapi-typescript-codegen` can auto-generate typed clients for TypeScript, Python, Java, etc. The React frontend could use a generated TypeScript SDK instead of raw `fetch()`.

### 15.4: Async computation with task queues
For large batch operations (100+ beams), instead of synchronous processing or SSE streaming, a Celery/Redis task queue could handle computation asynchronously. The client submits a job, gets a task ID, and polls for results.

### 15.5: Feature flags per endpoint
A feature flag system (like LaunchDarkly or even a simple JSON config) could enable/disable experimental endpoints, toggle between algorithm versions, or A/B test new response formats without redeploying.

---

## Part 16: Next Repo Must-Add

### Concrete items to add

1. **Error handling decorator** — A `@catch_and_sanitize(context)` decorator that eliminates the duplicated try/except pattern across all 60+ endpoints
2. **Response model enforcement** — Add `response_model=` to all endpoints so FastAPI validates outgoing data, not just incoming
3. **Request/response logging middleware** — Log every request body, response status, and timing for debugging
4. **Per-endpoint rate limiting** — Heavy compute endpoints (optimization, batch) should have separate rate limits
5. **API versioning plan** — Document how `/api/v2` will coexist with `/api/v1` when breaking changes arrive
6. **Generated TypeScript SDK** — Auto-generate a typed client from `/openapi.json` for the React frontend
7. **Health check with dependency status** — Include library version, last successful computation, memory usage in `/health`

### Day-1 checklist for a new FastAPI endpoint

```
□ 1. Create Pydantic request model in fastapi_app/models/ with Field(...) constraints
□ 2. Create Pydantic response model with all expected output fields
□ 3. Add router function in fastapi_app/routers/ using the Waiter Pattern
□ 4. Use response_model= in the @router.post() decorator
□ 5. Call structural_lib function — NEVER compute math in the router
□ 6. Translate field names (client-friendly → library notation, e.g., width → b_mm)
□ 7. Wrap response with success_response() / error_response()
□ 8. Add error handling with sanitize_error() for CWE-209 compliance
□ 9. Write at least 3 tests: valid input, invalid input (422), edge case
□ 10. Check /docs — verify the endpoint appears with correct schema
```

---

## 📎 References

- [FastAPI official docs](https://fastapi.tiangolo.com/) — Tutorial, advanced topics
- [Pydantic V2 docs](https://docs.pydantic.dev/) — Model validation, Field options
- [OpenAPI 3.1 spec](https://spec.openapis.org/oas/v3.1.0) — What `/openapi.json` produces
- [CWE-209: Information Exposure Through Error Message](https://cwe.mitre.org/data/definitions/209.html) — Why `sanitize_error` exists
- `fastapi_app/main.py` — Application factory, middleware stack
- `fastapi_app/routers/design.py` — Beam design endpoints
- `fastapi_app/models/beam.py` — Pydantic request/response models
- `fastapi_app/error_utils.py` — Error sanitization
- `fastapi_app/config.py` — CORS, rate limits, settings
- **Next:** Day 16 covers WebSocket live design, SSE batch processing, and file imports/exports
