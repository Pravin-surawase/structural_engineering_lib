# Module 4: APIs — How Software Talks to Software

## The Big Idea

An **API** (Application Programming Interface) is a contract between two pieces of software. One side says "give me data in THIS format" and the other says "I'll respond with data in THAT format." Without APIs, frontend can't talk to backend, services can't talk to each other, and nothing works together.

---

## Part 1: What Is an API?

Think of an API like a restaurant menu:

```
┌──────────────────────────────────────────────┐
│                  RESTAURANT MENU              │
│  (This is the API)                            │
│                                               │
│  Order #1: Margherita Pizza                   │
│    → Give me: size (small/medium/large)       │
│    → You get: pizza object                    │
│                                               │
│  Order #2: Caesar Salad                       │
│    → Give me: dressing (yes/no)               │
│    → You get: salad object                    │
│                                               │
│  You DON'T need to know:                      │
│    - How the kitchen works                    │
│    - Where ingredients come from               │
│    - What oven temperature is used            │
└──────────────────────────────────────────────┘
```

**Key insight:** The menu (API) tells you WHAT you can order and WHAT you'll get back. It hides HOW it's made.

### APIs exist at every level:

```
LEVEL 1 — Function API (within code):
   result = calculate_ast(width_mm=300, fck=25)

LEVEL 2 — Library API (between packages):
   from structural_lib import design_beam_is456
   result = design_beam_is456(b_mm=300, d_mm=500, ...)

LEVEL 3 — Web API (between systems over HTTP):
   POST /api/v1/design/beam
   Body: {"b_mm": 300, "d_mm": 500, ...}
   Response: {"Ast_mm2": 1206.5, ...}
```

---

## Part 2: HTTP — The Language of the Web

When your browser loads a page or a frontend talks to a backend, they use **HTTP** (HyperText Transfer Protocol).

### An HTTP request has:
```
METHOD  URL                         ← what you want to do + where
Host: api.example.com               ← which server
Content-Type: application/json       ← what format the body is in

{                                    ← the body (data you're sending)
  "width_mm": 300,
  "depth_mm": 500
}
```

### HTTP Methods (verbs):

| Method | Purpose | Example | Has Body? |
|--------|---------|---------|-----------|
| **GET** | Read data | Get beam details | No |
| **POST** | Create / compute | Design a beam | Yes |
| **PUT** | Replace entirely | Update beam config | Yes |
| **PATCH** | Update partially | Change one field | Yes |
| **DELETE** | Remove | Delete a design | No |

### HTTP Status Codes (the server's answer):

| Code | Meaning | When |
|------|---------|------|
| **200** | OK | Request succeeded |
| **201** | Created | New resource created |
| **400** | Bad Request | Your input is wrong |
| **404** | Not Found | URL doesn't exist |
| **422** | Unprocessable | Data format wrong |
| **500** | Server Error | Bug on the server side |

```
REQUEST:                           RESPONSE:
POST /api/v1/design/beam           200 OK
{"b_mm": 300, "d_mm": 500}   →    {"Ast_mm2": 1206.5}

POST /api/v1/design/beam           422 Unprocessable
{"b_mm": -300}                →    {"detail": "width must be positive"}
```

---

## Part 3: REST — A Design Pattern for APIs

**REST** (REpresentational State Transfer) is a set of conventions for organizing web APIs.

### REST principles:
1. **Resources are nouns:** `/api/v1/beams`, not `/api/v1/getBeam`
2. **Methods are verbs:** `GET /beams` (read), `POST /beams` (create)
3. **Stateless:** Each request contains everything needed — no "remember my last request"
4. **Consistent URLs:** Follow a pattern

### REST URL patterns:

```
GET    /api/v1/beams              → List all beams
POST   /api/v1/beams              → Create a new beam
GET    /api/v1/beams/42           → Get beam #42
PUT    /api/v1/beams/42           → Replace beam #42
DELETE /api/v1/beams/42           → Delete beam #42

Nested resources:
GET    /api/v1/beams/42/rebars    → Get rebars for beam #42
```

### This project's API:
```
POST /api/v1/design/beam          → Design a beam (IS 456)
POST /api/v1/design/column        → Design a column
POST /api/v1/import/csv           → Import CSV data
POST /api/v1/geometry/beam/full   → Get 3D geometry
POST /api/v1/export/bbs           → Export bar bending schedule
GET  /health                      → Health check
```

---

## Part 4: JSON — The Data Format

**JSON** (JavaScript Object Notation) is how APIs send and receive data. It's human-readable text.

### JSON types:
```json
{
  "string": "hello",
  "number": 42,
  "decimal": 3.14,
  "boolean": true,
  "null_value": null,
  "array": [1, 2, 3],
  "object": {
    "nested": "value"
  }
}
```

### Real example — beam design request:
```json
{
  "b_mm": 300,
  "d_mm": 500,
  "fck": 25,
  "fy": 500,
  "Mu_kNm": 150,
  "Vu_kN": 75,
  "clear_cover_mm": 25,
  "exposure_condition": "moderate"
}
```

### Real example — beam design response:
```json
{
  "flexure": {
    "Ast_required_mm2": 1206.5,
    "Mu_capacity_kNm": 152.3,
    "status": "SAFE"
  },
  "shear": {
    "Vus_kN": 45.2,
    "stirrup_spacing_mm": 150,
    "status": "SAFE"
  }
}
```

---

## Part 5: Request → Response Cycle

Here's what happens when the React frontend asks the FastAPI backend to design a beam:

```
1. User fills form in React
   ┌──────────────┐
   │  Width: 300  │
   │  Depth: 500  │
   │  [Design]    │  ← User clicks button
   └──────┬───────┘
          │
2. React sends HTTP POST
          │  POST /api/v1/design/beam
          │  Body: {"b_mm": 300, "d_mm": 500, ...}
          ▼
3. FastAPI receives request
   ┌──────────────┐
   │  Validates   │  ← Pydantic checks all fields
   │  input data  │
   └──────┬───────┘
          │
4. FastAPI calls Python library
          │  design_beam_is456(b_mm=300, d_mm=500, ...)
          ▼
5. Library does math (IS 456)
   ┌──────────────┐
   │  flexure.py  │  ← Calculate Ast
   │  shear.py    │  ← Calculate stirrups
   └──────┬───────┘
          │
6. Result flows back up
          │  return {"Ast_mm2": 1206.5, ...}
          ▼
7. FastAPI sends HTTP response
   ┌──────────────┐
   │  200 OK      │
   │  JSON body   │
   └──────┬───────┘
          │
8. React shows results
          ▼
   ┌──────────────┐
   │  Steel:      │
   │  1206.5 mm²  │
   │  Status: ✅  │
   └──────────────┘
```

---

## Part 6: FastAPI — Building APIs in Python

**FastAPI** is a Python framework for building web APIs. It auto-generates documentation and validates input.

### Basic endpoint:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Define the input schema
class BeamInput(BaseModel):
    b_mm: float         # Width in mm
    d_mm: float         # Effective depth in mm
    fck: float          # Concrete grade (N/mm²)
    fy: float           # Steel grade (N/mm²)
    Mu_kNm: float       # Bending moment (kNm)

# Define the endpoint
@app.post("/api/v1/design/beam")
def design_beam(input: BeamInput):
    """Design an RC beam per IS 456:2000"""
    result = structural_lib.design_beam_is456(
        b_mm=input.b_mm,
        d_mm=input.d_mm,
        fck=input.fck,
        fy=input.fy,
        Mu_kNm=input.Mu_kNm,
    )
    return result
```

### What FastAPI gives you for free:
1. **Input validation** — Pydantic checks types, ranges, required fields
2. **Auto documentation** — Visit `/docs` for interactive API explorer
3. **Error responses** — Returns 422 with clear messages for invalid input
4. **Type safety** — Editor auto-complete works from the schema
5. **Async support** — Handle thousands of concurrent requests

### Auto-generated docs:
```
Visit http://localhost:8000/docs to see:

┌─────────────────────────────────────────┐
│  Swagger UI — Interactive API Docs      │
│                                         │
│  POST /api/v1/design/beam               │
│    [Try it out]                         │
│    Body:                                │
│    {                                    │
│      "b_mm": 300,                       │
│      "d_mm": 500,                       │
│      ...                                │
│    }                                    │
│    [Execute]                            │
│                                         │
│    Response: 200                        │
│    {"flexure": {"Ast_mm2": 1206.5}}     │
└─────────────────────────────────────────┘
```

---

## Part 7: API Communication Patterns

### Pattern 1: Request-Response (most common)
```
Client → Request → Server → Response → Client
```
One question, one answer. Most API calls use this.

### Pattern 2: Server-Sent Events (SSE)
```
Client → Request → Server
                   Server → Event 1 → Client
                   Server → Event 2 → Client
                   Server → Event 3 → Client
                   Server → [done]  → Client
```
Server streams multiple updates. Used for batch design (designing 50 beams).

### Pattern 3: WebSocket
```
Client ←→ Server (bidirectional, persistent connection)
Client → "design this beam"
Server → "progress: 25%"
Server → "progress: 50%"
Client → "change width to 400"
Server → "progress: 75%"
Server → "done: {result}"
```
Real-time, two-way communication. Used for live design updates.

### When to use which:

| Pattern | Use When | Example |
|---------|----------|---------|
| Request-Response | Single operation | Design one beam |
| SSE | Server sends multiple updates | Batch design 50 beams |
| WebSocket | Real-time two-way | Live design with sliders |

---

## Part 8: API Errors — What Goes Wrong

### Frontend calling an API:
```typescript
// React hook calling the backend
async function designBeam(input: BeamInput) {
  try {
    const response = await fetch("/api/v1/design/beam", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });

    if (!response.ok) {
      // Server returned an error (400, 422, 500, etc.)
      const error = await response.json();
      throw new Error(error.detail);
    }

    return await response.json();
  } catch (error) {
    // Network error, server down, etc.
    console.error("API call failed:", error);
    throw error;
  }
}
```

### Common API error types:

| Error | Code | Cause | Fix |
|-------|------|-------|-----|
| Validation error | 422 | Bad input data | Check required fields, types |
| Not found | 404 | Wrong URL | Check endpoint path |
| Server error | 500 | Bug in backend | Check server logs |
| Network error | — | Server is down | Start the server |
| CORS error | — | Frontend/backend on different ports | Configure CORS in FastAPI |
| Timeout | 408 | Request took too long | Optimize the calculation |

---

## Part 9: Testing APIs

### With curl (command line):
```bash
curl -X POST http://localhost:8000/api/v1/design/beam \
  -H "Content-Type: application/json" \
  -d '{"b_mm": 300, "d_mm": 500, "fck": 25, "fy": 500, "Mu_kNm": 150}'
```

### With the Swagger UI:
Visit `http://localhost:8000/docs`, click an endpoint, fill in the form, click "Execute."

### With pytest:
```python
from fastapi.testclient import TestClient
from fastapi_app.main import app

client = TestClient(app)

def test_beam_design():
    response = client.post("/api/v1/design/beam", json={
        "b_mm": 300, "d_mm": 500, "fck": 25, "fy": 500, "Mu_kNm": 150
    })
    assert response.status_code == 200
    data = response.json()
    assert data["flexure"]["Ast_required_mm2"] > 0
```

---

## Part 10: Exercises

1. **Read the docs:** Start the backend (`./run.sh dev`) and visit `http://localhost:8000/docs`. Try designing a beam.
2. **Trace a request:** Use browser DevTools (Network tab) when clicking "Design" in the React app. What URL, method, and body is sent?
3. **Handle an error:** Send a request with `b_mm: -100`. What status code and message do you get?
4. **Map the endpoints:** Run `grep -r "@router" fastapi_app/routers/ | head -20` and list all available endpoints.

---

## Part 11: Self-Check

1. **What does API stand for?** Application Programming Interface.
2. **What's the difference between GET and POST?** GET reads data (no body). POST sends data (has body).
3. **What does a 422 status code mean?** Input data is wrong or invalid.
4. **What's JSON?** A text format for structured data exchange.
5. **What's REST?** A convention for organizing web APIs around resources and HTTP methods.
6. **Why does FastAPI auto-generate docs?** From Pydantic models and type hints in your code.
7. **When use SSE vs WebSocket?** SSE for one-way server→client streaming. WebSocket for two-way real-time.

---

## Key Takeaway

> An API is a **contract**. The frontend says "I'll send you THIS data in THIS format." The backend says "I'll respond with THAT data in THAT format." Everything in between — the math, the database, the caching — is hidden behind that contract.

**Next:** [Module 5 — Types and Schemas](05-types-and-schemas.md) explains how to define and validate the data that crosses API boundaries.
