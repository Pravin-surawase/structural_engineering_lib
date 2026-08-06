# Module 5: Types, Schemas, and Data Validation

## The Big Idea

**Types** describe what kind of data a variable holds. **Schemas** describe the shape of a data object. **Validation** makes sure data matches expectations before you use it. Together, they prevent the #1 cause of bugs: wrong data passing silently through the system.

---

## Part 1: Why Types Matter

### Without types:
```python
def calculate_area(width, height):
    return width * height

# These all "work" but are wrong:
calculate_area("hello", "world")  # TypeError at runtime
calculate_area(300, None)          # TypeError at runtime
calculate_area(-300, 500)          # Returns -150000 (nonsense)
calculate_area(0.3, 500)           # Returns 150 (is 0.3 meters or mm?)
```

### With types:
```python
def calculate_area(width_mm: float, height_mm: float) -> float:
    """Calculate area in mm². Both inputs must be in millimeters."""
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Dimensions must be positive")
    return width_mm * height_mm
```

**Types give you:**
1. **Documentation** — You know what to pass without reading the code
2. **Editor autocomplete** — Your IDE suggests correct methods
3. **Error detection** — Type checkers find bugs before you run the code
4. **Self-documenting units** — `width_mm` tells you it's in millimeters

---

## Part 2: Python Type Hints

Python is dynamically typed (you CAN skip types), but type hints are strongly recommended.

### Basic types:
```python
name: str = "Beam"
width: float = 300.0
count: int = 4
is_safe: bool = True
nothing: None = None
```

### Collection types:
```python
from typing import Optional

# Lists
rebar_sizes: list[float] = [12.0, 16.0, 20.0]

# Dictionaries
properties: dict[str, float] = {"width": 300, "depth": 500}

# Optional (can be None)
cover: Optional[float] = None   # Same as: float | None

# Tuples
coordinates: tuple[float, float, float] = (0.0, 1.5, 3.0)
```

### Function types:
```python
def design_beam(
    b_mm: float,        # width in mm
    d_mm: float,        # effective depth in mm
    fck: float,         # concrete grade N/mm²
    fy: float = 500.0,  # steel grade (default 500)
) -> dict[str, float]:  # returns a dictionary
    ...
```

### Type checking:
```bash
# Pyright (used in this project)
pyright                          # Check all files
pyright my_file.py               # Check one file
```

---

## Part 3: TypeScript Types

TypeScript adds types to JavaScript. Types are REQUIRED (not optional like Python).

### Basic types:
```typescript
const name: string = "Beam";
const width: number = 300;  // No int/float distinction — just 'number'
const isSafe: boolean = true;
const nothing: null = null;
```

### Object types (interfaces):
```typescript
// Define the shape of a beam input
interface BeamInput {
  b_mm: number;
  d_mm: number;
  fck: number;
  fy: number;
  Mu_kNm: number;
  Vu_kN?: number;  // ? means optional
}

// Use it
const input: BeamInput = {
  b_mm: 300,
  d_mm: 500,
  fck: 25,
  fy: 500,
  Mu_kNm: 150,
};
```

### Type aliases:
```typescript
type Status = "SAFE" | "UNSAFE" | "CHECK";  // Only these 3 values allowed

type BeamResult = {
  Ast_mm2: number;
  status: Status;
  warnings: string[];
};
```

### Generic types:
```typescript
// A response that can wrap any data type
type ApiResponse<T> = {
  data: T;
  errors: string[];
  timestamp: string;
};

// Usage
type BeamResponse = ApiResponse<BeamResult>;
```

---

## Part 4: Pydantic — Validation at the Boundary

**Pydantic** is Python's most popular data validation library. It defines schemas and validates data automatically.

### Basic model:
```python
from pydantic import BaseModel, Field

class BeamInput(BaseModel):
    b_mm: float = Field(gt=0, description="Width in mm")
    d_mm: float = Field(gt=0, description="Effective depth in mm")
    fck: float = Field(ge=15, le=80, description="Concrete grade N/mm²")
    fy: float = Field(default=500, ge=250, le=600)
    Mu_kNm: float = Field(gt=0, description="Bending moment kNm")
```

### What Pydantic does:
```python
# ✅ Valid data — works fine
beam = BeamInput(b_mm=300, d_mm=500, fck=25, Mu_kNm=150)

# ❌ Missing required field — clear error
beam = BeamInput(b_mm=300, d_mm=500, fck=25)
# ValidationError: Mu_kNm field required

# ❌ Wrong type — clear error
beam = BeamInput(b_mm="hello", d_mm=500, fck=25, Mu_kNm=150)
# ValidationError: b_mm: value is not a valid float

# ❌ Out of range — clear error
beam = BeamInput(b_mm=-300, d_mm=500, fck=25, Mu_kNm=150)
# ValidationError: b_mm: ensure this value is greater than 0

# ✅ Auto-conversion — Pydantic converts compatible types
beam = BeamInput(b_mm="300", d_mm=500, fck=25, Mu_kNm=150)
# Works! "300" is converted to 300.0
```

### Pydantic in FastAPI:

```python
@app.post("/api/v1/design/beam")
def design_beam(input: BeamInput):    # ← Pydantic validates automatically
    # If you reach this line, input is guaranteed to be valid
    result = calculate(input.b_mm, input.d_mm)
    return result
```

FastAPI + Pydantic = automatic input validation at the API boundary. Invalid requests never reach your business logic.

---

## Part 5: Validation at Every Boundary

The key principle: **validate data when it crosses a boundary.**

```
┌──────────────────────────────────────────────────────┐
│                      FRONTEND                         │
│  Form validation: "Width must be a positive number"   │
│                        │                              │
│  ─── Boundary 1: HTTP Request ───────────────         │
│                        ▼                              │
│                      BACKEND                          │
│  Pydantic validation: b_mm > 0, fck in [15, 80]      │
│                        │                              │
│  ─── Boundary 2: Function Call ──────────────         │
│                        ▼                              │
│                    LIBRARY                             │
│  Assert: d_mm > cover_mm, Mu > 0                      │
│                        │                              │
│  ─── Boundary 3: Math Return ────────────────         │
│                        ▼                              │
│                      RESULT                           │
│  Type-checked: Ast_mm2 is float, status is str        │
└──────────────────────────────────────────────────────┘
```

**Why validate at multiple levels?**
- Frontend catches obvious mistakes instantly (no server round-trip)
- Backend catches anything frontend missed (or if someone sends raw HTTP)
- Library catches domain-specific violations (engineering constraints)

---

## Part 6: Dataclasses — Structured Data Without Validation

Python's `dataclass` gives you structured data but WITHOUT automatic validation.

```python
from dataclasses import dataclass

@dataclass
class BeamSection:
    width_mm: float
    depth_mm: float
    cover_mm: float = 25.0

    @property
    def effective_depth_mm(self) -> float:
        return self.depth_mm - self.cover_mm

# Usage
section = BeamSection(width_mm=300, depth_mm=500)
print(section.effective_depth_mm)  # 475.0
```

### Dataclass vs Pydantic:

| Feature | dataclass | Pydantic BaseModel |
|---------|-----------|-------------------|
| Validation | No | Yes (automatic) |
| Type coercion | No | Yes ("300" → 300.0) |
| JSON serialization | Manual | Built-in (.model_dump()) |
| Performance | Faster | Slightly slower |
| Use when | Internal data structures | API boundaries |

**Rule:** Use Pydantic at boundaries (API, file I/O). Use dataclass for internal structures.

---

## Part 7: Enums — Restricted Choices

When a value can only be one of a few options, use an **enum**.

```python
from enum import Enum

class ConcreteGrade(str, Enum):
    M15 = "M15"
    M20 = "M20"
    M25 = "M25"
    M30 = "M30"
    M40 = "M40"

class ExposureCondition(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"
    EXTREME = "extreme"
```

```typescript
// TypeScript equivalent
type ConcreteGrade = "M15" | "M20" | "M25" | "M30" | "M40";
type ExposureCondition = "mild" | "moderate" | "severe" | "very_severe" | "extreme";
```

**Why enums?** They prevent typos: `"moderaet"` is caught at validation time.

---

## Part 8: Units in Types — The Engineering Pattern

In structural engineering, mixing up units causes catastrophic failures (Mars Climate Orbiter crashed because of a unit mismatch).

### Bad — no units:
```python
def design_beam(width, depth, moment):
    # Is width in mm? cm? inches?
    # Is moment in kNm? Nm? lb-ft?
    ...
```

### Good — units in names:
```python
def design_beam(
    b_mm: float,          # millimeters
    d_mm: float,          # millimeters
    Mu_kNm: float,        # kilonewton-meters
    fck: float,           # N/mm² (implied by convention)
) -> dict:
    ...
```

### Best — units in types:
```python
from dataclasses import dataclass

@dataclass
class Length_mm:
    value: float

    def to_m(self) -> float:
        return self.value / 1000

@dataclass
class Moment_kNm:
    value: float

    def to_Nm(self) -> float:
        return self.value * 1e6

# Now you CAN'T mix them up
def design_beam(width: Length_mm, moment: Moment_kNm): ...
```

This project uses the "units in names" approach (e.g., `b_mm`, `Mu_kNm`, `Ast_mm2`).

---

## Part 9: The Type Gap Problem

A common problem: Python types and TypeScript types get out of sync.

```python
# Backend (Python)
class BeamResult(BaseModel):
    Ast_mm2: float
    status: str
    warnings: list[str]
```

```typescript
// Frontend (TypeScript) — MUST match exactly
interface BeamResult {
  Ast_mm2: number;
  status: string;
  warnings: string[];
}
```

If the backend adds a new field `crack_width_mm` but the frontend doesn't update, bugs happen silently.

**Solutions:**
1. **Manual sync** — Keep both in sync by hand (error-prone)
2. **Generate types** — Auto-generate TypeScript from Pydantic (ideal)
3. **OpenAPI schema** — Use the auto-generated API spec as the source of truth

---

## Part 10: Exercises

1. **Add validation:** Write a Pydantic model for column input (width, height, axial_load, fck, fy) with appropriate constraints.
2. **Type hint a function:** Take an untyped Python function and add type hints. Run pyright to check.
3. **Find the types:** Browse `react_app/src/types/` and `fastapi_app/models/`. How do they correspond?
4. **Break validation:** Send a request to the API with invalid data. Read the error message. What validation caught it?

---

## Part 11: Self-Check

1. **What's the difference between a type and a schema?** A type is for a single value (string, number). A schema is the shape of an entire object (which fields, what types).
2. **Why use Pydantic instead of plain dataclass?** Automatic validation and type coercion at boundaries.
3. **Where should you validate?** At every boundary — form, API, function call.
4. **Why include units in variable names?** To prevent unit confusion (mm vs cm vs m).
5. **What's the type gap problem?** Python and TypeScript types getting out of sync.
6. **When to use enums?** When a value can only be one of a few fixed options.

---

## Key Takeaway

> Types are not bureaucracy — they're **documentation that the computer can check**. Every type hint is a guarantee: "this variable WILL be this kind of data." That guarantee prevents an entire category of bugs.

**Next:** [Module 6 — Testing](06-testing.md) explains how to prove your code actually works.
