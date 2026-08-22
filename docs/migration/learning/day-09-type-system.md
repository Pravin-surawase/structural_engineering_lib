# Day 9: Type System — Dataclasses, Pydantic, and TypedDicts (Deep Dive)

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Prerequisites:** Day 8 (4-layer architecture)
**Library files:** `Python/structural_lib/core/data_types.py`, `Python/structural_lib/core/inputs.py`, `Python/structural_lib/core/models.py`, `Python/structural_lib/core/result_base.py`, `Python/structural_lib/core/numerics.py`, `fastapi_app/models/beam.py`
**IS 456 Clauses:** N/A — this module is about software architecture, not code clauses

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why Python's duck typing isn't safe enough for structural calculations
- The three type tools we use: frozen dataclasses, Pydantic v2 models, and TypedDicts
- How `DictCompatMixin` gives us backward compatibility without sacrificing safety
- The `BaseResult` ABC pattern and why every result must implement `summary()`
- The parameter naming convention (`b_mm`, `fck_nmm2`) and why it prevents 1000x errors
- The canonical data flow: `dict → Pydantic validates → dataclass carries → dict out`
- Computed fields, `model_validator`, and `__post_init__` — validation at creation time
- Numeric safety: `safe_divide()`, `approx_equal()`, and floating-point gotchas
- **What can be done better** in the next repo
- **Innovation directions** for modern Python type systems
- **Things you must know** for building production-grade typed libraries

---

## Part 1: Why Strong Types in Python? (The Problem)

### 1.1 The Danger of Duck Typing in Engineering

Python is dynamically typed. "If it quacks like a duck, it's a duck." For web apps, that's usually fine — a string is a string, and if you mix up a username with an email, you'll see the mistake on screen.

For structural engineering, duck typing is **dangerous.** Consider this:

```python
# What if someone passes force in Newtons instead of kN?
result = design_beam(Mu=150000, vu=100000)  # N·mm and N?
result = design_beam(Mu=150, vu=100)         # kN·m and kN?
```

Both calls look valid. Both will execute without errors. But if the function expects kN·m and you pass N·mm, the result is off by a factor of $10^6$. The beam is designed for a moment 1,000,000 times too large (or too small). No exception. No warning. Just a wrong answer that could cause a building collapse.

### 1.2 Three Real-World Type Bugs

**Bug 1: Mars Climate Orbiter (1999)**
NASA lost a $125 million spacecraft because one team used pound-force seconds and another used newton-seconds. No type system caught the mismatch. The orbiter entered Mars' atmosphere instead of orbiting it.

**Bug 2: The "width" Ambiguity**
```python
# Developer A writes:
def analyze_section(width, depth):   # Assumes mm
    area = width * depth / 1e6       # Converts to m²
    ...

# Developer B calls:
analyze_section(width=0.3, depth=0.5)  # Passes meters!
# Result: area = 0.3 * 0.5 / 1e6 = 1.5e-7 m² (should be 0.15 m²)
# Off by 1,000,000x. No error raised.
```

**Bug 3: Mutable Result Mutation**
```python
results = [design_beam(case) for case in load_cases]

# Later, someone "normalizes" results for a report:
for r in results:
    r["Ast_required"] = round(r["Ast_required"], 0)  # Lost decimal precision!

# Now the rebar optimizer uses rounded values → wrong bar selection
optimizer.select_bars(results[0]["Ast_required"])  # 985 instead of 985.3
```

### 1.3 Our Solution: A Three-Tool Type System

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE TYPE SYSTEM TOOLBOX                           │
├──────────────────┬──────────────────────┬───────────────────────────┤
│  FROZEN          │  PYDANTIC v2         │  TYPEDDICT               │
│  DATACLASSES     │  MODELS              │                          │
├──────────────────┼──────────────────────┼───────────────────────────┤
│ For: Results     │ For: API inputs      │ For: Lightweight dicts   │
│ (math output)    │ (HTTP boundary)      │ (backward compat)        │
│                  │                      │                          │
│ Immutable ✅     │ Validates ✅         │ Just type hints ✅       │
│ IDE autocomplete │ Type coercion ✅     │ Works with plain dicts   │
│ DictCompatMixin  │ JSON ↔ object ✅     │ No runtime overhead      │
│                  │ Range checks ✅      │                          │
│                  │                      │                          │
│ Layers 1-3      │ Layer 4 (FastAPI)    │ Layers 1-3 (legacy)     │
└──────────────────┴──────────────────────┴───────────────────────────┘
```

---

## Part 2: Frozen Dataclasses — Immutable Results

### 2.1 The Concept

All *result* types use `@dataclass(frozen=True)`. Frozen means immutable — once created, you can't change any field. Period.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class FlexureResult:
    Mu_lim: float        # kNm — limiting moment capacity
    Ast_required: float  # mm² — required tension steel
    xu: float            # mm — neutral axis depth
    xu_max: float        # mm — maximum allowed neutral axis
    section_type: str    # "UNDER_REINFORCED" or "DOUBLY_REINFORCED"
    is_safe: bool
```

### 2.2 Why Frozen? (5 Reasons)

| Reason | Without Frozen | With Frozen |
|--------|---------------|-------------|
| **Mutation bugs** | `result.Ast = 0` silently changes it | `FrozenInstanceError` — caught immediately |
| **Data integrity** | Result can drift from calculation | Result is a permanent fact |
| **Hashability** | Can't use as dict key or in sets | Can cache, deduplicate results |
| **Thread safety** | Concurrent access → race conditions | Multiple threads share safely |
| **Debugging** | "Who changed this value?" is hard to trace | Value never changes — no mystery |

### 2.3 Real Library Code — `FlexureResult`

From `core/data_types.py` (the actual code):

```python
@dataclass
class FlexureResult:
    """Result of IS 456 flexure design.

    Note: Ast_required=0.0 with is_safe=False indicates a design failure,
    not a valid zero-steel design. Always check is_safe and errors
    before consuming the steel area.
    """
    Mu_lim: float                    # Limiting moment (kN·m)
    Ast_required: float              # Tension steel area (mm²)
    pt_provided: float               # Steel percentage
    section_type: DesignSectionType  # Enum: UNDER_REINFORCED, BALANCED, etc.
    xu: float                        # Neutral axis depth (mm)
    xu_max: float                    # Max neutral axis depth (mm)
    is_safe: bool                    # Design check pass?
    Asc_required: float = 0.0       # Compression steel (mm²)
    errors: list[DesignError] = field(default_factory=list)  # Structured errors
    Ast_min: float = 0.0            # Min steel per Cl 26.5.1.1 (mm²)
    Ast_max: float = 0.0            # Max steel per Cl 26.5.1.2 (mm²)
    clause_refs: dict[str, str] = field(default_factory=dict)
```

**Key design decisions visible here:**

1. **`section_type` is an Enum, not a string** — `DesignSectionType.UNDER_REINFORCED` can't be misspelled like `"UNDER_REINFRCED"`.
2. **`errors` is a list of structured `DesignError`** — not a string message. Machine-readable.
3. **`clause_refs` maps operation → IS 456 clause** — traceability built into the result.
4. **Default values use `field(default_factory=list)`** — avoids the mutable default argument trap.
5. **`Ast_min` and `Ast_max`** — not just the required area, but the code limits too.

### 2.4 The `BaseResult` ABC — A Contract for All Results

Every result type should implement the `BaseResult` interface:

```python
# ACTUAL code from core/result_base.py
@dataclass(frozen=True)
class BaseResult(ABC):
    """Abstract base for all result objects.

    All result dataclasses MUST:
    - Be frozen (immutable)
    - Implement summary() for human-readable output
    - Support to_dict() for serialization
    """

    @abstractmethod
    def summary(self) -> str:
        """Return human-readable summary."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
```

**Why `summary()` is abstract:** Every result must be printable in a human-readable way. You can't forget — the ABC forces it.

```python
# Example: a result that forgets summary() won't even instantiate
@dataclass(frozen=True)
class MyResult(BaseResult):
    value: float
    # Missing summary() → TypeError: Can't instantiate abstract class
```

### 2.5 The Mutable Default Trap (Important Python Gotcha)

```python
# ❌ WRONG — all instances share the SAME list!
@dataclass
class BadResult:
    errors: list = []  # This is shared across ALL instances!

r1 = BadResult()
r2 = BadResult()
r1.errors.append("error!")
print(r2.errors)  # ['error!'] ← r2 has r1's error! Bug!

# ✅ CORRECT — each instance gets a fresh list
@dataclass
class GoodResult:
    errors: list = field(default_factory=list)

r1 = GoodResult()
r2 = GoodResult()
r1.errors.append("error!")
print(r2.errors)  # [] ← independent
```

**Rule:** Always use `field(default_factory=list)` or `field(default_factory=dict)` for mutable defaults.

---

## Part 3: Pydantic v2 Models — Input Validation

### 3.1 Where Pydantic Lives

Pydantic models guard the **API boundary** (Layer 4). They sit between the outside world (HTTP, JSON) and the inside world (typed Python functions).

```
  Outside World          Pydantic Boundary           Inside World
  (messy JSON)    ──────►  (validates)  ──────►    (clean types)
  ─────────────          ───────────────           ─────────────
  {"width": "300"}  →  BeamDesignRequest(width=300.0)  →  b_mm=300.0
  {"fck": -5}       →  ValidationError: fck >= 15     →  ✗ rejected
  {"fck": "25"}     →  BeamDesignRequest(fck=25.0)     →  fck_nmm2=25.0
```

### 3.2 Real Library Code — `BeamDesignRequest`

From `fastapi_app/models/beam.py`:

```python
class BeamDesignRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "width": 300.0, "depth": 500.0, "moment": 150.0,
                "shear": 75.0, "fck": 25.0, "fy": 415.0,
            }]
        }
    )

    width: float = Field(gt=0, le=2000.0,
        description="Beam width b (mm)", examples=[230.0, 300.0, 400.0])

    depth: float = Field(gt=0, le=3000.0,
        description="Overall beam depth D (mm)", examples=[450.0, 600.0])

    moment: float = Field(ge=0,
        description="Factored design moment Mu (kN·m)")

    fck: float = Field(default=25.0, ge=15.0, le=80.0,
        description="Concrete compressive strength (N/mm²)")

    fy: float = Field(default=500.0, ge=250.0, le=600.0,
        description="Steel yield strength (N/mm²)")

    clear_cover: float = Field(default=25.0, ge=20.0, le=75.0,
        description="Clear cover to reinforcement (mm)")
```

### 3.3 What Pydantic Gives You (Feature by Feature)

**Feature 1: Type Coercion**
```python
# User sends string "300" — Pydantic converts to float 300.0
request = BeamDesignRequest(width="300", depth="500", moment="150")
print(type(request.width))  # <class 'float'>
```

**Feature 2: Range Validation**
```python
# fck=-5 → immediate rejection with clear error
try:
    BeamDesignRequest(width=300, depth=500, moment=150, fck=-5)
except ValidationError as e:
    print(e)
    # 1 validation error for BeamDesignRequest
    # fck
    #   Input should be greater than or equal to 15 [type=greater_than_equal, ...]
```

**Feature 3: `computed_field` — Derived Values**
```python
# ACTUAL code from core/models.py
class SectionProperties(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    width_mm: float = Field(..., gt=0, le=2000)
    depth_mm: float = Field(..., gt=0, le=3000)
    cover_mm: float = Field(40.0, gt=0, le=100)
    stirrup_dia_mm: float = Field(default=8.0, gt=0, le=20)
    bar_dia_mm: float = Field(default=20.0, gt=0, le=40)

    @computed_field
    @property
    def effective_depth_mm(self) -> float:
        """d = D - cover - stirrup - bar/2"""
        return self.depth_mm - self.cover_mm - self.stirrup_dia_mm - self.bar_dia_mm / 2
```

The `effective_depth_mm` is automatically calculated and included in JSON serialization. Users don't need to compute it.

**Feature 4: `model_validator` — Cross-Field Validation**
```python
# ACTUAL code from core/models.py
class BeamGeometry(BaseModel):
    point1: Point3D
    point2: Point3D

    @model_validator(mode="after")
    def validate_length(self) -> BeamGeometry:
        """Ensure beam has non-zero length."""
        if self.length_m < 0.1:  # Minimum 100mm
            raise ValueError(f"Beam length must be >= 0.1m, got {self.length_m:.3f}m")
        return self
```

This catches errors that single-field validation can't: "The beam's two endpoints are the same point" → length = 0 → caught.

**Feature 5: `ConfigDict(frozen=True, extra="forbid")`**
```python
class Point3D(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    x: float
    y: float
    z: float

# Can't add unexpected fields:
Point3D(x=0, y=0, z=0, w=1)  # ❌ ValidationError: extra fields not permitted

# Can't modify after creation:
p = Point3D(x=0, y=0, z=0)
p.x = 5  # ❌ FrozenInstanceError
```

**Feature 6: Automatic OpenAPI Schema**
```python
# FastAPI generates API documentation from Pydantic models automatically:
# POST /api/v1/design/beam
# Request body schema shows:
#   width: number (0 < x ≤ 2000), description: "Beam width b (mm)"
#   depth: number (0 < x ≤ 3000), description: "Overall beam depth D (mm)"
#   ... with examples [230.0, 300.0, 400.0]
```

Every `Field(description=...)` becomes documentation. Users see it at `/docs`.

### 3.4 Pydantic v2 vs v1 — Key Differences

| Feature | v1 (old) | v2 (current) |
|---------|----------|-------------|
| Speed | Python-based | Rust core (5-50x faster) |
| Config | `class Config:` | `model_config = ConfigDict()` |
| Serialization | `.dict()` | `.model_dump()` |
| JSON | `.json()` | `.model_dump_json()` |
| Computed | `@validator` | `@computed_field` + `@model_validator` |
| Extra fields | `Config.extra = "forbid"` | `ConfigDict(extra="forbid")` |

---

## Part 4: TypedDicts — Lightweight Dict Hints

### 4.1 When to Use TypedDicts

TypedDicts are simple type hints on regular Python dicts. No runtime validation. No immutability. Just "this dict should have these keys with these types."

```python
from typing import TypedDict

class BarDict(TypedDict):
    count: int
    diameter: float
    callout: str

class StirrupDict(TypedDict):
    diameter: float
    spacing: float
    callout: str
```

### 4.2 Optional Fields with `total=False`

```python
# ACTUAL library code
class DeflectionParams(TypedDict, total=False):
    """All fields are optional (total=False)."""
    span_mm: float
    d_mm: float
    support_condition: str  # "CANTILEVER", "SIMPLY_SUPPORTED", "CONTINUOUS"

class CrackWidthParams(TypedDict, total=False):
    exposure: str
    max_crack_width_mm: float
```

`total=False` means all fields are optional. This is used for parameters where callers might only provide some fields.

### 4.3 TypedDict vs Dataclass — Decision Table

| Factor | TypedDict | Dataclass |
|--------|-----------|-----------|
| Runtime type checking | ❌ None | ❌ None (unless `__post_init__`) |
| Immutability | ❌ Mutable dict | ✅ With `frozen=True` |
| IDE autocomplete | ✅ Yes | ✅ Yes |
| JSON serialization | ✅ Already a dict | Needs `asdict()` |
| Backward compat | ✅ Works with existing `dict[str, Any]` | ❌ Breaks callers expecting dicts |
| `in` operator | ✅ `"key" in d` | Needs `DictCompatMixin` |
| Memory overhead | Minimal (plain dict) | Slightly more (object) |

**Library convention:** Use TypedDict for intermediate structures (bar info, stirrup layout) that callers treat as plain dicts. Use frozen dataclasses for important results that need immutability.

---

## Part 5: DictCompatMixin — The Bridge Pattern

### 5.1 The Problem It Solves

Our library v0.1–v0.12 returned plain dicts everywhere:
```python
# Old API (v0.12 and below)
result = design_beam(b=300, d=450, fck=25, fy=500, Mu=150)
print(result["Ast_required"])  # Dict access
```

We wanted to migrate to frozen dataclasses, but hundreds of callers used `result["key"]` syntax. Changing all at once would break everything.

### 5.2 The Solution — Make Dataclasses Quack Like Dicts

```python
# ACTUAL code from core/data_types.py
class DictCompatMixin:
    """Mixin providing dict-style access on frozen dataclasses."""

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    def __setitem__(self, key: str, value: Any) -> None:
        object.__setattr__(self, key, value)  # Bypasses frozen for internal use

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and hasattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def keys(self) -> list[str]:
        return [f.name for f in fields(self)]

    def values(self) -> list[Any]:
        return [getattr(self, f.name) for f in fields(self)]

    def items(self) -> list[tuple[str, Any]]:
        return [(f.name, getattr(self, f.name)) for f in fields(self)]

    def __iter__(self) -> Any:
        return iter(f.name for f in fields(self))
```

### 5.3 Both Access Styles Work

```python
result = design_singly_reinforced(fck=25, fy=500, b_mm=300, d_mm=450, Mu_kNm=150)

# ── New code uses attribute access ──
print(result.Ast_required)       # 985.3
print(result.is_safe)            # True

# ── Legacy code uses dict access ──
print(result["Ast_required"])    # 985.3 (same value)
print(result.get("xu_max"))      # 207.0
print("is_safe" in result)       # True
print(list(result.keys())[:5])   # ['Mu_lim', 'Ast_required', 'pt_provided', ...]

# ── Iteration works ──
for key, value in result.items():
    print(f"  {key}: {value}")
```

### 5.4 The Migration Path

```
Phase 1: All results are plain dicts              (v0.1–v0.12)
Phase 2: Results become dataclass + DictCompatMixin (v0.13–current)
         → Old code still works: result["Ast"]
         → New code uses: result.Ast
Phase 3: Deprecate dict access, remove DictCompatMixin (future v1.0)
         → Only result.Ast works
```

This is a **gradual migration** — you never break existing callers.

---

## Part 6: Parameter Naming Convention — Units in Names

### 6.1 The Naming Standard

Every parameter encodes its physical unit in the name:

```
┌─────────────────────────────────────────────────────────────┐
│  FORMAT:  <symbol>_<unit>                                   │
│                                                             │
│  Examples:                                                  │
│    b_mm       → beam width in millimeters                   │
│    D_mm       → overall depth in millimeters                │
│    fck_nmm2   → concrete strength in N/mm²                  │
│    fy_nmm2    → steel yield strength in N/mm²               │
│    mu_knm     → factored moment in kN·m                     │
│    vu_kn      → factored shear in kN                        │
│    cover_mm   → clear cover in millimeters                  │
│    span_mm    → span length in millimeters                  │
│    fck_mpa    → same as nmm2 (alias for Pydantic models)    │
│    fy_mpa     → same as nmm2 (alias for Pydantic models)    │
│    length_m   → length in meters (computed field)            │
│    asv_mm2_m  → stirrup area per meter (mm²/m)              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Two Tiers of Naming

**Layer 2 (codes/) — Short IS 456 notation:**
```python
# Familiar to structural engineers who read IS 456 daily
def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    ...
```

**Layer 3 (services/) — Explicit unit suffixes:**
```python
# Clear at the API boundary where confusion is most likely
def design_beam_is456(*, b_mm: float, D_mm: float, d_mm: float,
                      fck_nmm2: float, fy_nmm2: float,
                      mu_knm: float, vu_kn: float) -> ComplianceCaseResult:
    ...
```

**Layer 4 (Pydantic) — Uses `_mpa` alias for clarity:**
```python
class SectionProperties(BaseModel):
    width_mm: float = Field(..., gt=0, le=2000)
    fck_mpa: float = Field(25.0, gt=0, le=100)  # MPa = N/mm²
```

### 6.3 Why This Prevents Disasters

```python
# ── Without unit naming ──
design_beam(width=300, depth=500, moment=150)
# Is moment in N·mm (150), kN·m (150), or kN·cm (150)?
# All are valid floats. No way to know without reading docs.

# ── With unit naming ──
design_beam_is456(b_mm=300, D_mm=500, mu_knm=150)
# Unambiguous. The name IS the documentation.
# If someone passes mu_knm=150000 (accidentally using N·mm),
# the value 150000 kN·m is absurdly large, and plausibility
# checks in the service layer catch it.
```

### 6.4 The Plausibility Check (Defense in Depth)

Unit naming alone doesn't prevent ALL errors. The services layer adds a second line of defense:

```python
# In services/common_api.py
def _validate_plausibility(fck: float, fy: float, b: float, d: float):
    """Sanity check — are values in plausible ranges?"""
    if fck > 100:
        raise ValueError(f"fck={fck} N/mm² seems too high. Did you pass Pa instead of MPa?")
    if b > 5000:
        raise ValueError(f"b={b} mm seems too large. Did you pass micrometers?")
    if d < 50:
        raise ValueError(f"d={d} mm seems too small. Check units.")
```

---

## Part 7: The Canonical Data Flow (End-to-End)

### 7.1 Complete Flow Diagram

```
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 1: Raw JSON from user/browser                              │
 │                                                                 │
 │   {"width": "300", "depth": 500, "fck": 25, "moment": 150}     │
 │   Types: mixed (string "300", int 500, etc.)                    │
 │   Validation: none                                              │
 └───────────────────────┬─────────────────────────────────────────┘
                         │ HTTP POST /api/v1/design/beam
                         ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 2: Pydantic validation (Layer 4 — FastAPI)                 │
 │                                                                 │
 │   BeamDesignRequest(                                            │
 │     width=300.0,    # "300" → coerced to float                  │
 │     depth=500.0,    # int 500 → coerced to float                │
 │     fck=25.0,       # validated: 15 ≤ 25 ≤ 80 ✅                │
 │     moment=150.0,   # validated: ≥ 0 ✅                         │
 │   )                                                             │
 │   Types: all float, all validated                               │
 └───────────────────────┬─────────────────────────────────────────┘
                         │ Extract fields, compute effective_depth
                         ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 3: Service call (Layer 3 — beam_api.py)                    │
 │                                                                 │
 │   design_beam_is456(                                            │
 │     units="IS456",                                              │
 │     b_mm=300.0, D_mm=500.0, d_mm=442.0,                        │
 │     fck_nmm2=25.0, fy_nmm2=500.0,                              │
 │     mu_knm=150.0, vu_kn=0.0                                    │
 │   )                                                             │
 │   ↪ _require_is456_units() validates code                       │
 │   ↪ _validate_plausibility() sanity checks                     │
 └───────────────────────┬─────────────────────────────────────────┘
                         │ Calls math functions with clean numbers
                         ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 4: Pure math (Layer 2 — codes/is456)                       │
 │                                                                 │
 │   flexure.design_singly_reinforced(                             │
 │     fck=25, fy=500, b_mm=300, d_mm=442, Mu_kNm=150             │
 │   )                                                             │
 │   → Returns FlexureResult (frozen dataclass):                    │
 │     Mu_lim=201.8, Ast_required=985.3, is_safe=True              │
 │                                                                 │
 │   shear.design_shear(...)                                       │
 │   → Returns ShearResult (frozen dataclass)                       │
 └───────────────────────┬─────────────────────────────────────────┘
                         │ Results flow back up
                         ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 5: Service assembles (Layer 3)                             │
 │                                                                 │
 │   ComplianceCaseResult(                                         │
 │     flexure=FlexureResult(...),                                 │
 │     shear=ShearResult(...),                                     │
 │     compliance=ComplianceReport(...)                             │
 │   )                                                             │
 └───────────────────────┬─────────────────────────────────────────┘
                         │ asdict() or .to_dict()
                         ▼
 ┌─────────────────────────────────────────────────────────────────┐
 │ STEP 6: JSON response (Layer 4)                                 │
 │                                                                 │
 │   {"success": true, "data": {                                   │
 │     "flexure": {"Mu_lim": 201.8, "Ast_required": 985.3, ...},  │
 │     "shear": {"stirrup_spacing": 200, ...},                     │
 │     "compliance": {"is_compliant": true, ...}                   │
 │   }}                                                            │
 └─────────────────────────────────────────────────────────────────┘
```

### 7.2 Type at Each Step

| Step | Type | Mutable? | Validated? |
|------|------|----------|------------|
| 1. Raw JSON | `dict[str, Any]` | Yes | No |
| 2. Pydantic | `BeamDesignRequest` | Yes* | Yes |
| 3. Service params | `float`, `str` kwargs | — | Yes (plausibility) |
| 4. Math results | `FlexureResult`, `ShearResult` | **No** (frozen) | Inputs validated |
| 5. Composite | `ComplianceCaseResult` | **No** (frozen) | — |
| 6. Response JSON | `dict[str, Any]` | Yes (copy) | Original safe |

*Pydantic models can be frozen with `ConfigDict(frozen=True)`.

---

## Part 8: Numeric Safety — Floating-Point Gotchas

### 8.1 The Problem

```python
# Classic floating-point surprise:
print(0.1 + 0.2 == 0.3)  # False!  (0.30000000000000004)

# In structural engineering, this matters:
xu = 0.48 * 450  # 216.00000000000003 instead of 216.0
if xu == 216.0:   # False! Comparison fails.
    print("Balanced section")
```

### 8.2 Library Solution — `core/numerics.py`

```python
# ACTUAL library code
ZERO_THRESHOLD: float = 1e-12

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide — returns default if denominator is near zero."""
    if abs(denominator) < ZERO_THRESHOLD:
        return default
    return numerator / denominator

def approx_equal(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    """Check approximate equality (wraps math.isclose)."""
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
```

### 8.3 When to Use Each

```python
# ── Division by zero protection ──
# Shear stress: τ = V / (b × d)
# If d=0 (invalid), don't crash — return safe default
tau_v = safe_divide(Vu * 1000, b * d, default=float('inf'))

# ── Float comparison ──
# Don't use == for floats!
if approx_equal(xu, xu_max):  # ✅ Safe
    section = "BALANCED"
# NOT: if xu == xu_max:       # ❌ Fragile
```

---

## Part 9: Enums — Type-Safe Constants

### 9.1 Why Enums Instead of Strings

```python
# ── Without enums — fragile ──
result.section_type = "UNDER_REINFRCED"  # Typo! Silently wrong.
if result.section_type == "UNDER_REINFORCED":  # Never true!
    ...

# ── With enums — safe ──
class DesignSectionType(Enum):
    UNDER_REINFORCED = 1
    BALANCED = 2
    OVER_REINFORCED = 3

result.section_type = DesignSectionType.UNDER_REINFRCED  # ❌ AttributeError! (caught)
```

### 9.2 Library Enums

```python
# Beam types
class BeamType(Enum):
    RECTANGULAR = 1
    FLANGED_T = 2
    FLANGED_L = 3

# Load types
class LoadType(Enum):
    UDL = auto()
    POINT = auto()
    TRIANGULAR = auto()
    MOMENT = auto()

# Exposure classes
class ExposureClass(Enum):
    MILD = auto()
    MODERATE = auto()
    SEVERE = auto()
    VERY_SEVERE = auto()

# Design status (StrEnum — prints as string)
class DesignStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_CHECKED = "NOT_CHECKED"

# Support conditions
class SupportCondition(Enum):
    CANTILEVER = auto()
    SIMPLY_SUPPORTED = auto()
    CONTINUOUS = auto()
```

### 9.3 `StrEnum` vs Regular `Enum`

```python
# Regular Enum — prints as Enum name
print(DesignSectionType.UNDER_REINFORCED)  # DesignSectionType.UNDER_REINFORCED

# StrEnum — prints as string (better for JSON)
print(DesignStatus.PASS)  # "PASS"

# StrEnum works in JSON serialization without custom encoders
json.dumps({"status": DesignStatus.PASS})  # '{"status": "PASS"}' ✅
```

---

## Part 10: Deprecation Utilities — Evolving APIs Safely

### 10.1 The Problem: Changing APIs Breaks Users

```python
# v0.12 API:
result = design_beam(width=300, ...)
print(result.error_message)  # string error

# v0.14 API (better):
result = design_beam(b_mm=300, ...)
print(result.errors)  # list[DesignError] (structured)
```

How do you transition without breaking existing users?

### 10.2 Library Solution — `@deprecated` decorator + `deprecated_field`

```python
# ACTUAL code from core/deprecation.py
@deprecated("0.14.0", "1.0.0", alternative="errors")
def get_error_message(result):
    """Use result.errors instead."""
    return result.error_message

# Inside FlexureResult.__post_init__:
def __post_init__(self):
    if self.error_message:
        deprecated_field(
            "FlexureResult", "error_message", "0.14.0", "1.0.0",
            alternative="errors"
        )
```

Users see:
```
DeprecationWarning: FlexureResult.error_message was deprecated in v0.14.0
and will be removed in v1.0.0. Use 'errors' instead.
```

### 10.3 The Compat Shim Pattern

```python
# core/types.py — backward compatibility shim
# Old code: from structural_lib.types import FlexureResult
# New code: from structural_lib.core.data_types import FlexureResult
# Both work! types.py re-exports from data_types.py

from .data_types import (
    FlexureResult, ShearResult, ComplianceCaseResult, ...
)
```

---

## Part 11: Composite Input Types — Building Complex Inputs from Simple Pieces

### 11.1 The Composition Pattern

Instead of one giant function with 20 parameters, we compose small input types:

```python
# ACTUAL code from core/inputs.py

@dataclass(frozen=True)
class BeamGeometryInput:
    b_mm: float         # Beam width
    D_mm: float         # Overall depth
    span_mm: float      # Clear span
    d_mm: float | None = None  # Effective depth (auto-calculated if None)
    cover_mm: float = 40.0     # Default 40mm per IS 456
    stirrup_dia_mm: float = 8.0
    bar_dia_mm: float = 20.0

@dataclass(frozen=True)
class MaterialsInput:
    fck_nmm2: float     # Concrete strength
    fy_nmm2: float      # Steel yield strength
    es_nmm2: float = 200000.0  # Steel modulus

@dataclass(frozen=True)
class LoadsInput:
    mu_knm: float       # Factored moment
    vu_kn: float        # Factored shear

@dataclass(frozen=True)
class BeamInput:
    geometry: BeamGeometryInput
    materials: MaterialsInput
    loads: LoadsInput
```

### 11.2 Why Composition > Flat Parameters

```python
# ❌ BAD: 15+ parameters, easy to confuse order
design_beam(300, 500, 5000, 25, 500, 150, 80, 40, 8, 20, ...)

# ✅ GOOD: Grouped by concern, IDE shows field names
beam = BeamInput(
    geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
    materials=MaterialsInput(fck_nmm2=25, fy_nmm2=500),
    loads=LoadsInput(mu_knm=150, vu_kn=80),
)
# Clear what each group means. Impossible to pass moment instead of width.
```

### 11.3 Smart Defaults and Auto-Calculation

```python
geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)
# d_mm not provided → auto-calculated:
# d = D - cover - stirrup - bar/2 = 500 - 40 - 8 - 10 = 442.0
print(geom.effective_depth)  # 442.0

# L/d ratio for serviceability:
print(geom.span_depth_ratio)  # 5000 / 442 = 11.31

# Conversion helpers:
d = geom.to_dict()                               # → plain dict
geom2 = BeamGeometryInput.from_dict(d)            # → back to dataclass
geom3 = BeamGeometryInput.from_dict({"b": 300, "D": 500, "span": 5000})  # legacy keys
```

---

## Part 12: Things to Know (Critical Knowledge)

### 12.1 Python Type Hints Are NOT Runtime Checks

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")  # No error! Returns "helloworld"
# Type hints are only for static analysis (mypy, Pyright), not runtime.
```

That's why we use:
- **`__post_init__`** in dataclasses for runtime validation
- **Pydantic** for runtime validation at API boundaries
- **Explicit `if` checks** in math functions

### 12.2 `asdict()` Creates a Deep Copy

```python
from dataclasses import asdict

result = FlexureResult(Mu_lim=200, Ast_required=1200, ...)
d = asdict(result)

# d is a completely NEW dict — modifying it doesn't affect the original
d["Ast_required"] = 0
print(result.Ast_required)  # Still 1200 ✅
```

### 12.3 `frozen=True` Doesn't Prevent Mutable Field Contents

```python
@dataclass(frozen=True)
class Result:
    errors: list[str] = field(default_factory=list)

r = Result()
r.errors = ["new"]     # ❌ FrozenInstanceError (can't reassign)
r.errors.append("new") # ⚠️ Works! (mutates the list IN-PLACE)
```

Frozen prevents *reassignment* of fields, not *mutation* of their contents. For truly immutable lists, you'd need tuples.

### 12.4 The `__all__` Pattern for Controlled Exports

```python
# core/types.py — controls what gets imported with `from types import *`
__all__ = [
    "FlexureResult", "ShearResult", "ComplianceCaseResult",
    "BeamGeometry", "BeamType", "DesignSectionType",
    # ... 104 exports total
]
```

### 12.5 The `DesignError` Sentinel Pattern

Instead of raising exceptions for every validation issue, we collect errors as data:

```python
@dataclass
class DesignError:
    code: str         # "E_INPUT_001"
    severity: str     # "ERROR", "WARNING"
    message: str      # Human-readable
    suggestion: str   # Actionable fix

# Usage: collect errors instead of crashing
errors = validate_dimensions(b=-100, d=450, D=500)
# Returns: [DesignError(code="E_INPUT_001", ...)]
# → No crash, caller decides what to do with errors
```

---

## Part 13: What Can Be Done Better (Next Repo)

### 13.1 Issues in Current Implementation

| Issue | Current State | Better Approach |
|-------|--------------|-----------------|
| **FlexureResult not frozen** | Has a TODO comment: `# TODO(SM-6): Freeze FlexureResult` | Should be `@dataclass(frozen=True)` |
| **Mixed naming** | Layer 2 uses `fck`, Layer 3 uses `fck_nmm2` — mapping needed | Use consistent naming everywhere |
| **DictCompatMixin `__setitem__`** | Bypasses frozen with `object.__setattr__` | Remove — defeats the purpose of frozen |
| **TypedDicts lack runtime validation** | `BarDict` is just hints, you can put anything | Use Pydantic for all structured input |
| **No `NewType` for units** | `b_mm: float` — tooling can't catch `b_mm=fck_nmm2` | Use `NewType("Millimeters", float)` |
| **DesignError is a dataclass, not frozen** | Errors can be mutated after creation | Make it frozen |

### 13.2 Concrete Migrations for Next Repo

**1. Use `NewType` for Physical Units**
```python
from typing import NewType

Millimeters = NewType("Millimeters", float)
KiloNewtonMeters = NewType("KiloNewtonMeters", float)
MegaPascals = NewType("MegaPascals", float)

def calculate_mu_lim(
    b: Millimeters, d: Millimeters,
    fck: MegaPascals, fy: MegaPascals,
) -> KiloNewtonMeters:
    ...

# mypy/Pyright catches this:
width: Millimeters = Millimeters(300)
strength: MegaPascals = MegaPascals(25)
calculate_mu_lim(b=strength, d=width, ...)  # ← Type checker warns!
```

**2. Replace DictCompatMixin with `__getattr__` Protocol**
```python
# Instead of mixin, use Python's mapping protocol
from collections.abc import Mapping

@dataclass(frozen=True)
class FlexureResult(Mapping):
    Mu_lim: float
    Ast_required: float
    ...

    def __getitem__(self, key): return getattr(self, key)
    def __len__(self): return len(fields(self))
    def __iter__(self): return iter(f.name for f in fields(self))
```

**3. Use `attrs` Instead of `dataclasses` for Richer Validation**
```python
import attrs

@attrs.frozen  # Like @dataclass(frozen=True) but with validators
class FlexureResult:
    Mu_lim: float = attrs.field(validator=attrs.validators.gt(0))
    Ast_required: float = attrs.field(validator=attrs.validators.ge(0))
    # Built-in validators, no __post_init__ needed
```

**4. Use `msgspec` for 10x Faster Serialization**
```python
import msgspec

class FlexureResult(msgspec.Struct, frozen=True):
    Mu_lim: float
    Ast_required: float
    # 10-75x faster than dataclasses + asdict()
    # Built-in JSON serialization
```

---

## Part 14: Innovation Directions — Modern Python Type Systems

### 14.1 Runtime Type Checking with `beartype`

```python
from beartype import beartype

@beartype
def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    ...

calculate_mu_lim(b="300", d=450, fck=25, fy=500)
# ❌ BeartypeCallHintParamViolation: parameter b="300" is not float
# Caught at RUNTIME, not just static analysis!
```

### 14.2 Phantom Types for Unit Safety (Cutting Edge)

```python
# Using phantom-types library
from phantom import Phantom

class Millimeters(float, Phantom, predicate=lambda x: x >= 0):
    ...

class MegaPascals(float, Phantom, predicate=lambda x: 0 < x <= 100):
    ...

b: Millimeters = Millimeters.parse(300)   # ✅
b: Millimeters = Millimeters.parse(-100)  # ❌ TypeCheckError
```

### 14.3 `pint` — Physical Quantity Library

```python
import pint
ureg = pint.UnitRegistry()

b = 300 * ureg.mm
fck = 25 * ureg.MPa
Mu = 150 * ureg.kN * ureg.m

# Automatic unit conversion!
b_m = b.to(ureg.m)  # 0.3 m
# Catches unit errors at runtime
Mu_wrong = 150 * ureg.N  # If used where kN·m expected → DimensionalityError
```

### 14.4 Structural Pattern Matching (Python 3.10+)

```python
# Pattern matching for result types
match result.section_type:
    case DesignSectionType.UNDER_REINFORCED:
        print("Good — economical design")
    case DesignSectionType.BALANCED:
        print("Warning — at the limit")
    case DesignSectionType.OVER_REINFORCED:
        print("Reduce section or add compression steel")
```

### 14.5 `TypeGuard` for Smart Narrowing

```python
from typing import TypeGuard

def is_safe_result(result: FlexureResult) -> TypeGuard[FlexureResult]:
    """After this check, type checker knows result.is_safe is True."""
    return result.is_safe and result.Ast_required > 0

if is_safe_result(result):
    # Type checker KNOWS result.is_safe is True here
    proceed_with_detailing(result)
```

### 14.6 Innovation Comparison Table

| Technology | What It Solves | Maturity | Recommendation |
|-----------|---------------|----------|----------------|
| `NewType` | Prevents mixing units at type-check time | Stable | **Use in next repo** |
| `beartype` | Runtime type checking | Stable | **Use for critical paths** |
| `pint` | Full dimensional analysis | Stable | Consider for v2 |
| `phantom` | Constrained types (non-negative, ranges) | Experimental | Watch |
| `msgspec` | 10x faster serialization | Stable | **Replace `asdict()`** |
| `attrs` | Better dataclasses with validators | Stable | **Evaluate vs dataclasses** |
| `cattrs` | Structured/unstructured conversion | Stable | Pair with attrs |
| Pattern matching | Cleaner result handling | Python 3.10+ | **Use everywhere** |

---

## Part 15: Things Needed in the Next (Separate Library) Repo

### 15.1 Architecture Decisions to Lock In Early

```
1. Choose: dataclasses vs attrs vs msgspec (pick ONE, not three)
2. Choose: Pydantic vs msgspec for validation (or both?)
3. Decide on unit strategy: NewType vs pint vs naming convention
4. Decide on error strategy: exceptions vs error-values vs Result type
5. Set up strict mypy/Pyright from day 1 (not later)
```

### 15.2 The Ideal Type Stack for a v2 Library

```
┌────────────────────────────────────────────────────────────┐
│  Layer 4 (API): Pydantic v2 models                         │
│  → Input validation, JSON schema, OpenAPI docs             │
│  → ConfigDict(frozen=True, extra="forbid")                 │
├────────────────────────────────────────────────────────────┤
│  Layer 3 (Services): msgspec.Struct or attrs classes        │
│  → Fast serialization, composable inputs                   │
│  → Replaces hand-written to_dict() / from_dict()           │
├────────────────────────────────────────────────────────────┤
│  Layer 2 (Math): NewType + beartype for units               │
│  → b: Millimeters, fck: MegaPascals                        │
│  → Runtime type checking on critical paths                 │
├────────────────────────────────────────────────────────────┤
│  Layer 1 (Core): Plain frozen dataclasses + Enums           │
│  → Simple, no dependencies                                 │
│  → StrEnum for JSON-friendly enums                         │
└────────────────────────────────────────────────────────────┘
```

### 15.3 Day-1 Checklist for New Repo

- [ ] Set up `pyproject.toml` with `[tool.mypy]` strict mode
- [ ] Create `core/units.py` with `NewType` definitions
- [ ] Create `core/result_base.py` with frozen `BaseResult` ABC
- [ ] Choose attrs or dataclasses — document the decision in an ADR
- [ ] Set up `beartype` on all Layer 2 functions
- [ ] Create `core/numerics.py` with `safe_divide`, `approx_equal`
- [ ] Use `StrEnum` for all status/category enums
- [ ] Set up `pre-commit` hook that runs `mypy --strict`
- [ ] Write type tests (`reveal_type()` assertions)
- [ ] Document naming convention in `CONTRIBUTING.md`

---

## Part 16: Exercises

### Exercise 1: Explore the Type System

```python
# Start: .venv/bin/python
from structural_lib.core.data_types import FlexureResult, DictCompatMixin, BarDict
from dataclasses import fields

# ── 1a: Inspect FlexureResult fields ──
print("=== FlexureResult fields ===")
for f in fields(FlexureResult):
    print(f"  {f.name}: {f.type}")

# ── 1b: Test DictCompatMixin ──
from structural_lib.codes.is456.beam.flexure import design_singly_reinforced
result = design_singly_reinforced(fck=25, fy=500, b_mm=300, d_mm=450, Mu_kNm=150)

print("\n=== Dict-style access ===")
print(f"result['Ast_required'] = {result['Ast_required']}")
print(f"result.get('xu_max') = {result.get('xu_max')}")
print(f"'is_safe' in result = {'is_safe' in result}")
print(f"Keys: {list(result.keys())[:5]}...")

# ── 1c: Test immutability ──
print("\n=== Immutability test ===")
try:
    result.Ast_required = 0
except AttributeError as e:
    print(f"Frozen! Error: {e}")
```

### Exercise 2: Validate Inputs

```python
from structural_lib.core.inputs import BeamGeometryInput

# ── 2a: Valid geometry ──
geom = BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000)
print(f"Effective depth: {geom.effective_depth}")

# ── 2b: Try invalid inputs — what errors do you get? ──
invalid_cases = [
    {"b_mm": -100, "D_mm": 500, "span_mm": 5000},
    {"b_mm": 300, "D_mm": 0, "span_mm": 5000},
    {"b_mm": 300, "D_mm": 500, "span_mm": -1000},
]

for case in invalid_cases:
    try:
        BeamGeometryInput(**case)
    except ValueError as e:
        print(f"  {case} → ✅ Caught: {e}")
```

### Exercise 3: Pydantic vs Dataclass

```python
# Compare Pydantic model and frozen dataclass behavior:

# ── 3a: Pydantic coerces types ──
from fastapi_app.models.beam import BeamDesignRequest
req = BeamDesignRequest(width="300", depth="500", moment="150")
print(f"width type: {type(req.width)}")  # float, not str!

# ── 3b: Pydantic rejects bad ranges ──
try:
    BeamDesignRequest(width=300, depth=500, moment=150, fck=-5)
except Exception as e:
    print(f"Pydantic caught: {e}")

# ── 3c: Dataclass doesn't coerce ──
from structural_lib.core.inputs import BeamGeometryInput
try:
    # This might work or fail depending on __post_init__
    geom = BeamGeometryInput(b_mm="300", D_mm=500, span_mm=5000)
    print(f"b_mm type: {type(geom.b_mm)}")  # str! No coercion.
except Exception as e:
    print(f"Dataclass caught: {e}")
```

### Exercise 4: Build Your Own Result Type

```python
from dataclasses import dataclass, field, asdict, fields

# Build a DictCompatMixin from scratch
class MyDictMixin:
    def __getitem__(self, key):
        try: return getattr(self, key)
        except AttributeError: raise KeyError(key) from None
    def keys(self):
        return [f.name for f in fields(self)]

@dataclass(frozen=True)
class ColumnResult(MyDictMixin):
    Pu_capacity_kN: float
    utilization: float
    is_safe: bool

r = ColumnResult(Pu_capacity_kN=1500, utilization=0.85, is_safe=True)
print(r.Pu_capacity_kN)        # Attribute access
print(r["Pu_capacity_kN"])     # Dict access
print(list(r.keys()))          # ['Pu_capacity_kN', 'utilization', 'is_safe']
print(asdict(r))               # Full dict copy
```

---

## Part 17: Can You Explain? (Self-Check)

### Q1: Why use frozen dataclasses for results instead of regular dicts?

<details>
<summary>Answer</summary>

Three reasons:

1. **Immutability.** A dict can be modified anywhere in the pipeline. With a frozen dataclass, once the calculation produces `Ast_required=1200`, no downstream code can accidentally change it to 0. For structural calculations, data integrity is critical.

2. **IDE support.** With a dict, your IDE doesn't know what keys exist. With a dataclass, you get autocomplete: type `result.` and see all fields. Prevents typos like `result['Ast_requried']` which would be a silent `KeyError`.

3. **Documentation.** Each field has a name, type, and description. A dict is opaque — what keys does it have? A dataclass is self-documenting code.

</details>

### Q2: Why `b_mm` instead of `width`?

<details>
<summary>Answer</summary>

Because `width` doesn't encode the unit. Is it mm, cm, m, inches, or feet? In structural engineering, mixing up mm and m is a 1000x error. By naming the parameter `b_mm`, the unit is part of the API contract. `b_mm=0.3` is obviously wrong (0.3mm beam?), but `width=0.3` could be valid in meters.

</details>

### Q3: When TypedDict vs frozen dataclass?

<details>
<summary>Answer</summary>

**TypedDict**: backward compat with existing dict consumers, short-lived intermediate data, when you need mutability.

**Frozen dataclass**: computation results, public API types, when you need immutability and IDE support.

In our library: results → frozen dataclass + DictCompatMixin. Intermediate data → TypedDict. API inputs → Pydantic.

</details>

### Q4: Pydantic models vs frozen dataclasses?

<details>
<summary>Answer</summary>

**Pydantic** = inputs (Layer 4). Validates, coerces types, generates JSON schema. Used in FastAPI request models.

**Frozen dataclasses** = outputs (Layers 2-3). Carry computed results. Immutable. No validation (inputs already validated). Have DictCompatMixin.

The split mirrors the architecture: Pydantic at the boundary, dataclasses in the core.

</details>

### Q5: What does `frozen=True` NOT protect against?

<details>
<summary>Answer</summary>

Frozen prevents *reassignment* of fields (`r.x = 5` → error), but does NOT prevent *mutation of mutable field contents*:

```python
r.errors = ["new"]      # ❌ FrozenInstanceError (reassignment blocked)
r.errors.append("new")  # ⚠️ Works! (in-place mutation of the list)
```

For true deep immutability, use tuples instead of lists, or `frozenset` instead of `set`.

</details>

### Q6: Why is `BaseResult.summary()` abstract?

<details>
<summary>Answer</summary>

Because every result type MUST be printable. Without the ABC, developers forget to add a `summary()` method, and when someone tries to print a result, they get `<FlexureResult object at 0x...>` — useless.

Making it abstract means you literally cannot instantiate a result class without implementing `summary()`. The compiler forces it.

</details>

---

## Part 18: Summary — What You Now Know

| Concept | Purpose | Where Used | Key File |
|---------|---------|------------|----------|
| **Frozen dataclasses** | Immutable results | Layers 1-3 | `core/data_types.py` |
| **Pydantic v2 models** | Input validation + JSON | Layer 4 | `fastapi_app/models/` |
| **TypedDicts** | Lightweight dict hints | Legacy compat | `core/data_types.py` |
| **DictCompatMixin** | Dict-style access on dataclasses | All results | `core/data_types.py` |
| **BaseResult ABC** | Forces `summary()` + `to_dict()` | Abstract base | `core/result_base.py` |
| **Unit naming** | Prevent unit confusion | All layers | Convention (PY-1) |
| **Enums** | Type-safe constants | All layers | `core/data_types.py` |
| **Numeric safety** | Float comparison, safe division | Math functions | `core/numerics.py` |
| **Deprecation utils** | Evolve APIs without breaking users | Cross-cutting | `core/deprecation.py` |
| **Composite inputs** | Group related parameters | Services layer | `core/inputs.py` |
| **Compat shims** | Redirect old imports to new locations | Migration | `core/types.py` |

### Quick Decision Matrix

```
I need to...                       → Use
─────────────────────────────────────────────
Return a calculation result        → frozen dataclass + DictCompatMixin
Accept HTTP/JSON input             → Pydantic BaseModel (Layer 4)
Type-hint a plain dict             → TypedDict
Represent a fixed set of options   → Enum or StrEnum
Safely divide numbers              → safe_divide() from numerics.py
Compare floats                     → approx_equal() from numerics.py
Deprecate an old field/function    → @deprecated or deprecated_field
Group 10+ function parameters      → Composite frozen dataclass (BeamInput)
Rename a module without breaking   → Compatibility shim (re-export)
```

---

## 📎 References

- **Core types:** `Python/structural_lib/core/data_types.py` (DictCompatMixin, FlexureResult, TypedDicts, Enums)
- **Input types:** `Python/structural_lib/core/inputs.py` (BeamGeometryInput, MaterialsInput, LoadsInput, BeamInput)
- **Pydantic models:** `fastapi_app/models/beam.py` (BeamDesignRequest, RebarLayerConfig)
- **Canonical models:** `Python/structural_lib/core/models.py` (Point3D, SectionProperties, BeamGeometry, BeamForces)
- **Result base:** `Python/structural_lib/core/result_base.py` (BaseResult ABC)
- **Numeric safety:** `Python/structural_lib/core/numerics.py` (safe_divide, approx_equal)
- **Deprecation:** `Python/structural_lib/core/deprecation.py` (@deprecated, deprecated_field)
- **Compat shim:** `Python/structural_lib/core/types.py` (re-exports from data_types)
- **Dev rule PY-1:** Explicit units in parameter names
- **Dev rule PY-5:** Return dataclasses, not dicts

---

## What's Next?

**Day 10: Error Handling & Validation** — Now that you know the types, we'll explore what happens when things go wrong. The exception hierarchy (`StructuralLibError` → 6 categories → 2 specific types), the structured `DesignError` dataclass, parametric error templates like `E_INPUT_001`, and the "validate at boundaries" philosophy. You'll see why our errors say "Beam width b=150mm is below minimum 200mm per Cl 26.5.1.1 — increase width to at least 200mm" instead of just "invalid input."
