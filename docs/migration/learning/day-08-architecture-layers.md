# Day 8: The 4-Layer Architecture — A Deep Dive

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Prerequisites:** Days 1-7 (material properties, flexure, shear, detailing, columns, serviceability, load analysis)
**Library files:** `Python/structural_lib/core/`, `Python/structural_lib/codes/is456/`, `Python/structural_lib/services/`, `fastapi_app/`, `react_app/`
**Key scripts:** `scripts/check_architecture_boundaries.py`, `scripts/validate_imports.py`

---

## What You'll Learn Today

By the end of this module you'll understand:
- Why a structural engineering library needs strict architectural layers
- What each of the 4 layers does (and what it must NOT do)
- The import rule that prevents circular dependencies and untestable code
- How data flows through the entire stack — from HTTP request to math to response
- How to verify architecture compliance with automated tools
- Why this design makes multi-code support (ACI 318, Eurocode 2) possible
- **Practical patterns** you can copy into your next project from day one
- How to recognize and fix architecture violations before they become costly

---

## Part 1: Why Layers Exist (The Big Picture)

### 1.1 The Pizza Shop Analogy

Before we touch code, let's build intuition with an everyday example.

Imagine you're building a pizza ordering app. Naively, you might write something like:

```python
# ❌ Everything in one file — "spaghetti code"
def order_pizza(request):
    # Parse the HTTP request (UI concern)
    toppings = json.loads(request.body)["toppings"]

    # Calculate price (business logic)
    price = 200
    for t in toppings:
        price += 30

    # Apply tax (business rule)
    tax = price * 0.18
    total = price + tax

    # Save to database (persistence concern)
    db.execute("INSERT INTO orders (total) VALUES (?)", total)

    # Send email (notification concern)
    send_email(f"Your order total: ₹{total}")

    # Return HTTP response (UI concern)
    return JsonResponse({"total": total})
```

This works... until it doesn't:
- Want to test the price calculation? You need a database AND an email server AND an HTTP request.
- Want to change from email to SMS? You have to edit the same function that calculates prices.
- Want to use the price calculation from a CLI tool? Impossible — it's welded to HTTP.

**Layered architecture solves this by giving each concern its own home.**

### 1.2 Now Replace Pizza with Structural Engineering

In our library, the concerns are:

| Concern | Pizza Shop | Structural Library |
|---------|-----------|-------------------|
| **What things look like** (types) | Pizza, Topping, Order | `FlexureResult`, `ShearResult`, `BeamGeometry` |
| **How to calculate** (math) | Price formula, tax rules | IS 456 Cl 38.1 flexure, Cl 40 shear |
| **How to coordinate** (orchestration) | Take order → cook → deliver | `design_beam_is456()` → flexure → shear → report |
| **How users interact** (interface) | Website, phone app | FastAPI REST endpoints, React 3D viewer |

Each goes in its own layer. Here's why this matters *more* for structural engineering than for a typical web app:

> **A wrong pizza price costs you ₹30. A wrong beam design calculation can cause a building to collapse.**

When math lives in one clean place, you can:
- **Verify it** against IS 456 textbook examples
- **Test it** with 5 lines of code (numbers in, numbers out)
- **Audit it** — every formula traces to a specific IS 456 clause
- **Trust it** — no hidden conversions, no surprise dependencies

---

## Part 2: The 4 Layers — A Complete Tour

### 2.1 Architecture Overview

```
                    ┌─────────────────────────────────────────────────┐
                    │                USER / BROWSER                    │
                    └─────────────┬───────────────────┬───────────────┘
                                  │  HTTP / WebSocket  │
                    ┌─────────────▼───────────────────▼───────────────┐
Layer 4: UI/IO      │  fastapi_app/routers/design.py                  │
                    │  react_app/src/components/                       │
                    │  Job: Accept input, return output (NO math)      │
                    └─────────────┬───────────────────────────────────┘
                                  │  Function calls
                    ┌─────────────▼───────────────────────────────────┐
Layer 3: Services   │  services/beam_api.py                           │
                    │  services/adapters.py, beam_pipeline.py          │
                    │  Job: Coordinate. Call math. Collect results.    │
                    └─────────────┬───────────────────────────────────┘
                                  │  Function calls
                    ┌─────────────▼───────────────────────────────────┐
Layer 2: Codes      │  codes/is456/beam/flexure.py                    │
                    │  codes/is456/beam/shear.py                      │
                    │  codes/is456/column/, footing/                   │
                    │  Job: Pure math. Numbers in → numbers out.       │
                    └─────────────┬───────────────────────────────────┘
                                  │  Uses types from
                    ┌─────────────▼───────────────────────────────────┐
Layer 1: Core       │  core/data_types.py  (FlexureResult, ShearResult)│
                    │  core/errors.py      (StructuralLibError tree)   │
                    │  core/validation.py  (validate_dimensions)       │
                    │  core/materials.py   (Concrete, Steel)           │
                    │  core/base.py        (DesignCode, FlexureDesigner)│
                    │  core/constants.py   (GAMMA_C=1.5, Es=200000)   │
                    │  Job: Define vocabulary. NO calculations.        │
                    └─────────────────────────────────────────────────┘
```

### 2.2 Layer 1 — Core: The Dictionary

**Location:** `Python/structural_lib/core/`
**Files:** 20 files (~16 .py files + indexes)
**Rule:** Can ONLY import from Python's standard library. Zero imports from codes/, services/, or fastapi_app/.

**What it holds:**

| File | Purpose | Real Example |
|------|---------|-------------|
| `data_types.py` | Result containers (dataclasses, TypedDicts) | `FlexureResult`, `ShearResult`, `ComplianceCaseResult` |
| `errors.py` | Exception hierarchy | `DimensionError`, `MaterialError`, `DesignConstraintError` |
| `validation.py` | Reusable validators | `validate_dimensions(b, d, D)`, `validate_materials(fck, fy)` |
| `materials.py` | Code-agnostic material models | `Concrete(fck=25)`, `Steel(fy=500)` |
| `base.py` | Abstract base classes | `DesignCode` (ABC), `FlexureDesigner` (ABC) |
| `constants.py` | Physical constants | `GAMMA_C = 1.5`, `GAMMA_S = 1.15`, `Es = 200000` |
| `inputs.py` | Input dataclasses | `BeamGeometryInput`, `MaterialsInput`, `LoadsInput` |

**Think of it this way:** Core defines *what things are*, not *how to calculate them*.

#### Real Code — `core/data_types.py`

```python
# This is ACTUAL code from our library
class DictCompatMixin:
    """Lets frozen dataclasses behave like dicts (backward compat)."""
    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def keys(self) -> list[str]:
        return [f.name for f in fields(self)]
```

Why does this matter? Because `FlexureResult` can be used two ways:
```python
result = design_singly_reinforced(fck=25, fy=500, b_mm=300, d_mm=450, Mu_kNm=150)

# Way 1: Like a normal object
print(result.Ast_required)

# Way 2: Like a dictionary (backward compat for old code)
print(result["Ast_required"])
```

#### Real Code — `core/errors.py` (Exception Hierarchy)

```
StructuralLibError                    ← Base (catch-all)
├── ValidationError                   ← Bad input
│   ├── DimensionError                ← Negative width, d > D
│   └── MaterialError                 ← fck < 0, invalid grade
├── DesignConstraintError             ← Can't fit rebar
├── ComplianceError                   ← Code violation
├── ConfigurationError                ← Bad setup
└── CalculationError                  ← Convergence failed
```

Every exception carries context:
```python
raise DimensionError(
    "Beam width b=150mm is below minimum 200mm",
    details={"b_mm": 150, "minimum": 200},     # Machine-readable
    suggestion="Increase beam width to at least 200mm",  # Actionable
    clause_ref="Cl. 26.5.1.1"                  # IS 456 reference
)
```

#### Real Code — `core/materials.py` (Code-Agnostic)

```python
@dataclass
class Concrete:
    """Works with ANY design code — IS 456, ACI 318, Eurocode 2."""
    fck: float              # Characteristic strength (N/mm²)
    Ec: float | None = None # Auto-calculated if not given
    density: float = 25.0   # kN/m³
    aggregate_size: float = 20.0  # mm

    def __post_init__(self):
        if self.Ec is None:
            self.Ec = 5000 * (self.fck ** 0.5)  # Generic formula

@dataclass
class Steel:
    fy: float               # Yield strength (N/mm²)
    Es: float = 200000.0    # Elastic modulus (N/mm²)
    steel_type: str = "Fe500"
```

Notice: `Concrete` and `Steel` don't mention IS 456. They could be used by any design code.

#### Real Code — `core/base.py` (The Interface Contract)

```python
class DesignCode(ABC):
    """Every design code must implement this interface."""

    @property
    @abstractmethod
    def code_id(self) -> str:      # "IS456", "ACI318"
        ...

    @property
    @abstractmethod
    def code_name(self) -> str:    # "IS 456:2000"
        ...

    @property
    @abstractmethod
    def code_version(self) -> str: # "2000"
        ...

class FlexureDesigner(ABC):
    """Every code must provide a flexure designer."""

    @abstractmethod
    def design(self, b, d, fck, fy, Mu) -> DesignResult:
        ...
```

**Why this matters for your next repo:** If you ever need to support multiple calculation standards, this pattern lets you swap implementations without touching the rest of the codebase.

---

### 2.3 Layer 2 — Codes: The Pure Math Engine

**Location:** `Python/structural_lib/codes/is456/`
**Sub-packages:** `beam/`, `column/`, `footing/`, `common/`
**Rule:** Can ONLY import from `core/` and siblings within `codes/`. NO services, NO fastapi, NO file I/O.

**What it holds:**

```
codes/is456/
├── beam/
│   ├── flexure.py       # Cl 38.1 — bending design
│   ├── shear.py         # Cl 40   — shear design
│   └── detailing.py     # Cl 26.5 — rebar spacing, cover
├── column/
│   ├── axial.py         # Cl 39.3 — short column
│   ├── interaction.py   # Cl 39.5 — P-M curve
│   └── slender.py       # Cl 39.7 — long columns
├── footing/             # Footings
├── materials.py         # xu_max/d ratios, modulus
├── compliance.py        # IS 456 limit checks
├── serviceability.py    # Deflection, cracking
├── tables.py            # τ_c values (Table 19)
└── traceability.py      # @clause decorator
```

#### The `@clause` Decorator — Traceability Magic

Every math function is tagged with the IS 456 clause it implements:

```python
from structural_lib.codes.is456.traceability import clause

@clause("38.1", "38.1.1")
def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    """IS 456 Cl 38.1 — limiting moment of resistance."""
    xu_max_d = materials.get_xu_max_d(fy)  # From materials.py (same layer)
    return 0.36 * xu_max_d * (1 - 0.42 * xu_max_d) * b * d**2 * fck / 1e6
```

This means you can later ask: "Which functions implement Clause 38.1?" and get a definitive answer programmatically. This is critical for code audits.

#### Real Code — The Flexure Module

Let's walk through the actual `calculate_mu_lim` function. This is the IS 456 formula:

$$M_{u,lim} = 0.36 \times \frac{x_{u,max}}{d} \times \left(1 - 0.42 \times \frac{x_{u,max}}{d}\right) \times b \times d^2 \times f_{ck}$$

```python
# ACTUAL code from codes/is456/beam/flexure.py
@clause("38.1", "38.1.1")
def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    # Step 1: Validate at the math boundary
    if b <= 0:
        raise DimensionError(
            dimension_too_small("beam width b", b, 0, "Cl. 38.1"),
            details={"b": b, "minimum": 0},
            clause_ref="Cl. 38.1",
        )
    # ... similar checks for d, fck, fy

    # Step 2: Get the xu_max/d ratio for this steel grade
    xu_max_d = materials.get_xu_max_d(fy)
    #   fy=250 → 0.53,  fy=415 → 0.48,  fy=500 → 0.46

    # Step 3: Apply the IS 456 formula (Cl 38.1)
    Mu_lim = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d) * b * d**2 * fck / 1e6
    return Mu_lim  # kN·m
```

**Key observations:**
1. **No import from services or UI** — just `core/` types and sibling `materials.py`
2. **No file I/O** — doesn't read CSV, doesn't call APIs
3. **Explicit units** — inputs in mm and N/mm², output in kN·m, with `/1e6` conversion visible
4. **Validation at boundary** — raises rich errors with clause references
5. **Pure function** — same inputs always produce the same output

#### Real Code — The Materials Module

```python
# ACTUAL code from codes/is456/materials.py

def get_xu_max_d(fy: float) -> float:
    """xu_max/d ratio based on steel grade (IS 456 Cl 38.1)"""
    if fy <= 0:
        raise ValueError(f"fy must be positive, got {fy}")
    if abs(fy - 250) < 0.5:   return 0.53
    elif abs(fy - 415) < 0.5: return 0.48
    elif abs(fy - 500) < 0.5: return 0.46
    else:
        return 700 / (1100 + 0.87 * fy)  # General formula

def get_ec(fck: float) -> float:
    """Modulus of Elasticity (IS 456 Cl 6.2.3.1)"""
    return 5000 * math.sqrt(fck)  # N/mm²

def get_fcr(fck: float) -> float:
    """Flexural Strength (IS 456 Cl 6.2.2)"""
    return 0.7 * math.sqrt(fck)   # N/mm²
```

**Notice:** This file imports only `math` from the standard library. No dependencies on anything in our project except core/.

#### The Shear Module — Practical Standards

```python
# ACTUAL code from codes/is456/beam/shear.py

# Real-world stirrup spacings used on construction sites
STANDARD_STIRRUP_SPACINGS = [75, 100, 125, 150, 175, 200, 225, 250, 275, 300]
STANDARD_STIRRUP_DIAMETERS = [6, 8, 10, 12]

def round_to_practical_spacing(spacing_mm: float, round_down: bool = True) -> float:
    """Round calculated spacing to what a mason can actually build."""
    # If calculated = 241.3mm → rounds down to 225mm (conservative, safe)
```

Even practical concerns like "what stirrup sizes exist on the market" live in Layer 2, because they're part of the engineering domain, not orchestration.

---

### 2.4 Layer 3 — Services: The Coordinator

**Location:** `Python/structural_lib/services/`
**Files:** 35 files (orchestration, adapters, reports, export)
**Rule:** Can import from `core/` and `codes/`. CANNOT import from `fastapi_app/` or `react_app/`.

**What it holds:**

| File | Purpose |
|------|---------|
| `beam_api.py` | Full beam design: flexure → shear → compliance → report |
| `column_api.py` | Column design orchestration |
| `adapters.py` | CSV/Excel column-name mapping (40+ mappings) |
| `beam_pipeline.py` | Multi-step design pipeline |
| `bbs.py` | Bar Bending Schedule generation |
| `dxf_export.py` | AutoCAD DXF file generation |
| `report.py` | PDF/text design reports |
| `optimization.py` | Section optimization |
| `batch.py` | Batch design (100s of beams) |

#### The Key Insight: Services DON'T Do Math

```python
# ACTUAL code from services/beam_api.py

def design_beam_is456(*, units, b_mm, D_mm, d_mm, fck_nmm2, fy_nmm2, mu_knm, vu_kn, ...):
    """Full beam design: flexure → shear → compliance."""

    # Step 1: Validate at the service boundary
    _require_is456_units(units)
    _validate_plausibility(fck_nmm2, fy_nmm2, b_mm, d_mm)

    # Step 2: Call Layer 2 math functions
    flexure = flexure_mod.design_singly_reinforced(fck_nmm2, fy_nmm2, b_mm, d_mm, mu_knm)
    shear = shear_mod.design_shear(fck_nmm2, fy_nmm2, b_mm, d_mm, vu_kn, ...)

    # Step 3: Collect everything into a unified result
    return ComplianceCaseResult(flexure=flexure, shear=shear, ...)
```

The service function:
- **Validates** inputs (boundary check)
- **Calls** math functions (delegates to Layer 2)
- **Collects** results (assembles the response)
- **Does NOT** contain any IS 456 formulas itself

#### Adapter Pattern — Handling Messy Real-World Data

Real users upload CSV files from ETABS (structural analysis software) with column names like:
```
Story,Bay,Unique Name,Station,Mu3,Vu2,B,D
```

The adapter translates these to our clean parameter names:
```python
# Conceptual flow in services/adapters.py:
# CSV column "B"   → b_mm = 300
# CSV column "D"   → D_mm = 500
# CSV column "Mu3" → mu_knm = 150
# CSV column "Vu2" → vu_kn = 80
```

This messy translation lives in **services** (Layer 3), NOT in codes/ (Layer 2). The math layer never sees CSV files — it only sees clean numbers.

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   CSV File   │ ──► │ services/         │ ──► │ codes/is456/     │
│   "B": 300   │     │ adapters.py       │     │ flexure.py       │
│   "Mu3": 150 │     │ maps to b_mm,     │     │ calculate_mu_lim │
│              │     │ mu_knm, etc.      │     │ (b=300, d=450,   │
│              │     │                   │     │  fck=25, fy=500) │
└──────────────┘     └──────────────────┘     └──────────────────┘
       Layer 4 input     Layer 3 translation     Layer 2 pure math
```

---

### 2.5 Layer 4 — UI/IO: The Interface

**Locations:** `fastapi_app/` (backend API) + `react_app/` (frontend)
**Rule:** Can import from `services/` and `core/`. Should NOT import directly from `codes/`.

#### FastAPI Router — Thin HTTP Wrapper

```python
# ACTUAL code from fastapi_app/routers/design.py

@router.post("/beam", summary="Design Beam Section")
async def design_beam(request: BeamDesignRequest):
    """Design a beam section for flexure and shear."""
    try:
        from structural_lib.services.api import design_beam_is456

        effective_depth = request.effective_depth
        if effective_depth is None:
            effective_depth = (
                request.depth - request.clear_cover
                - request.stirrup_dia_mm - request.main_bar_dia_mm / 2
            )

        result = design_beam_is456(
            units="IS456",
            b_mm=request.width,
            D_mm=request.depth,
            d_mm=effective_depth,
            mu_knm=request.moment,
            vu_kn=request.shear,
            fck_nmm2=request.fck,
            fy_nmm2=request.fy,
            # ...
        )
        return success_response(result)
    except Exception as e:
        return error_response(str(e))
```

**The router's ONLY jobs:**
1. Receive HTTP request → extract fields from Pydantic model
2. Call a service function
3. Return the result as JSON

It contains **zero** IS 456 formulas. If you wanted to add a CLI interface, you'd write a new Layer 4 component that calls the same `design_beam_is456()` service function.

---

## Part 3: The Import Rule — The One Law

### 3.1 The Rule (Visual)

```
                     CAN IMPORT FROM (arrows point to what you import)
                     ═══════════════

    Layer 4 (UI)  ────────►  Layer 3 (Services)
         │                        │
         │                        │
         ▼                        ▼
    Layer 1 (Core) ◄──────  Layer 2 (Codes)
         ▲                        │
         │                        │
         └────────────────────────┘

    ✅ Arrows go DOWN or to the LEFT (toward Core)
    ❌ Arrows NEVER go UP or to the RIGHT (toward UI)
```

### 3.2 The Rule (Table)

| Layer | Can Import From | CANNOT Import From |
|-------|----------------|-------------------|
| **Core (1)** | Python stdlib only (`math`, `dataclasses`, `enum`, `typing`) | Codes, Services, UI |
| **Codes (2)** | Core + siblings in codes/ | Services, UI |
| **Services (3)** | Core + Codes | UI (fastapi_app, react_app) |
| **UI (4)** | Core + Codes + Services | — (top of the stack) |

### 3.3 Why This Rule is Non-Negotiable (5 Reasons)

**Reason 1: Testability**

```python
# ✅ With layers — 5-line test, runs in < 1ms
def test_flexure():
    result = calculate_mu_lim(b=300, d=450, fck=25, fy=500)
    assert abs(result - 201.8) < 0.5

# ❌ Without layers — need HTTP server, database, CSV files...
def test_flexure_without_layers():
    csv_file = create_temp_csv(...)  # Need file system
    server = start_fastapi(...)      # Need HTTP server
    response = http.post("/beam", files={"csv": csv_file})
    assert response.json()["flexure"]["Mu_lim"] == 201.8
    # 20 lines, 500ms, fragile, and testing 3 things at once
```

**Reason 2: No Circular Dependencies**

```
services/beam_api.py  ─imports─►  codes/is456/flexure.py
   ▲                                      │
   │            ❌ CIRCULAR!               │
   └────────────imports───────────────────┘

Python says: ImportError: cannot import name 'design_beam_is456'
             from partially initialized module
```

The one-way rule makes circular imports **structurally impossible**.

**Reason 3: Reuse Across Interfaces**

```
┌─────────────┐
│ FastAPI      │──┐
│ (web API)    │  │
└─────────────┘  │
                  ▼
┌─────────────┐  ┌──────────────────────────────┐
│ CLI Tool     │──► services/beam_api.py          │
│ (terminal)   │  │ design_beam_is456(...)        │
└─────────────┘  └──────────────────────────────┘
                  ▲
┌─────────────┐  │
│ Jupyter      │──┘
│ (notebook)   │
└─────────────┘
```

Three different UIs, one service function. If services imported from `fastapi_app`, only the web API would work.

**Reason 4: Safe Parallelism**

Different developers can work on different layers *simultaneously* without merge conflicts:
- Developer A modifies `codes/is456/flexure.py` (new formula)
- Developer B modifies `fastapi_app/routers/design.py` (new endpoint)
- No overlap. No conflicts. No stepping on each other's toes.

**Reason 5: Multi-Code Future**

```python
# Future — same service, different codes:
def design_beam(*, code="IS456", b_mm, d_mm, fck, fy, Mu):
    if code == "IS456":
        return codes.is456.flexure.design(b_mm, d_mm, fck, fy, Mu)
    elif code == "ACI318":
        return codes.aci318.flexure.design(b_mm, d_mm, fck, fy, Mu)
    # Same service, same types, different math
```

---

## Part 4: Data Flow — Following a Request End-to-End

### 4.1 Complete Request Lifecycle (Flowchart)

Let's trace what happens when a user designs a beam through the web UI:

```
 USER clicks "Design" in React app
          │
          ▼
 ┌────────────────────────────────────────────────────────────┐
 │ LAYER 4A: React Component                                  │
 │                                                            │
 │   const response = await fetch('/api/v1/design/beam', {    │
 │     method: 'POST',                                        │
 │     body: JSON.stringify({                                  │
 │       width: 300, depth: 500, fck: 25, fy: 500,            │
 │       moment: 150, shear: 80                                │
 │     })                                                      │
 │   });                                                       │
 └────────────────────┬───────────────────────────────────────┘
                      │ HTTP POST
                      ▼
 ┌────────────────────────────────────────────────────────────┐
 │ LAYER 4B: FastAPI Router (design.py)                        │
 │                                                            │
 │   1. Pydantic validates the JSON body → BeamDesignRequest   │
 │   2. Computes effective_depth if not given                  │
 │   3. Calls service function:                                │
 │      result = design_beam_is456(                            │
 │          units="IS456", b_mm=300, D_mm=500, d_mm=442,      │
 │          fck_nmm2=25, fy_nmm2=500,                         │
 │          mu_knm=150, vu_kn=80                               │
 │      )                                                      │
 │   4. Returns JSON: {"success": true, "data": result}        │
 └────────────────────┬───────────────────────────────────────┘
                      │ Function call
                      ▼
 ┌────────────────────────────────────────────────────────────┐
 │ LAYER 3: Service (beam_api.py)                              │
 │                                                            │
 │   1. _require_is456_units("IS456")  → validates code        │
 │   2. _validate_plausibility(fck=25, fy=500, b=300, d=442)  │
 │   3. flexure = flexure_mod.design_singly_reinforced(        │
 │          fck=25, fy=500, b_mm=300, d_mm=442, Mu_kNm=150)   │
 │   4. shear = shear_mod.design_shear(                        │
 │          fck=25, fy=500, b_mm=300, d_mm=442, Vu_kN=80)     │
 │   5. compliance = compliance_mod.check_code_compliance(...)  │
 │   6. Return ComplianceCaseResult(flexure, shear, compliance) │
 └────────────────────┬───────────────────────────────────────┘
                      │ Function calls
                      ▼
 ┌────────────────────────────────────────────────────────────┐
 │ LAYER 2: IS 456 Math (flexure.py, shear.py)                │
 │                                                            │
 │   flexure.py:                                               │
 │   1. xu_max_d = get_xu_max_d(500) → 0.46                   │
 │   2. Mu_lim = 0.36 × 0.46 × (1-0.42×0.46) × 300 ×        │
 │                442² × 25 / 1e6 = 201.8 kN·m                │
 │   3. Mu_kNm(150) < Mu_lim(201.8) → singly reinforced       │
 │   4. Ast_required = 1012 mm²                                │
 │   5. Return FlexureResult(Ast_required=1012, ...)            │
 │                                                            │
 │   shear.py:                                                 │
 │   1. τ_v = Vu × 1000 / (b × d) → 0.60 N/mm²              │
 │   2. τ_c = lookup_table_19(fck=25, pt=0.76) → 0.56 N/mm²  │
 │   3. Stirrup spacing = 200mm @ 8mm dia                      │
 │   4. Return ShearResult(...)                                 │
 └────────────────────┬───────────────────────────────────────┘
                      │ Uses types from
                      ▼
 ┌────────────────────────────────────────────────────────────┐
 │ LAYER 1: Core Types                                         │
 │                                                            │
 │   FlexureResult(frozen=True):                               │
 │     Mu_lim: 201.8 kNm                                      │
 │     Ast_required: 1012.0 mm²                                │
 │     xu: 180.3 mm                                            │
 │     section_type: "UNDER_REINFORCED"                        │
 │     is_safe: True                                           │
 │                                                            │
 │   ShearResult(frozen=True):                                 │
 │     stirrup_dia: 8 mm                                       │
 │     stirrup_spacing: 200 mm                                 │
 │     is_safe: True                                           │
 └────────────────────────────────────────────────────────────┘
```

### 4.2 The Key Distinction: Data Flow vs Import Direction

```
 IMPORTS go DOWN only (enforced by tools):
    UI → Services → Codes → Core

 DATA flows both ways (calls go down, results come back up):
    UI ──request──► Services ──params──► Codes ──types──► Core
    UI ◄──JSON──── Services ◄──result── Codes ◄──types── Core
```

---

## Part 5: Why This Design Will Help Your Next Repo

### 5.1 The Pattern is Universal

The 4-layer pattern works for **any** domain-logic-heavy project:

| Our Library | Financial App | Medical Calc | Game Engine |
|-------------|--------------|-------------|-------------|
| **Core:** FlexureResult | Core: TransactionResult | Core: DosageResult | Core: PhysicsResult |
| **Codes:** IS 456 math | Rules: Tax calculation | Rules: Drug interaction | Rules: Gravity, collision |
| **Services:** beam_api | Services: payment_flow | Services: prescription_api | Services: game_loop |
| **UI:** FastAPI + React | UI: Flask + React | UI: Django + mobile | UI: OpenGL + menus |

### 5.2 Decision Algorithm — Where Does New Code Go?

When you write a new function, use this decision tree:

```
START: I have new code to write.
  │
  ├── Is it a TYPE definition (dataclass, enum, TypedDict, exception)?
  │     YES → core/
  │
  ├── Is it a PURE CALCULATION (numbers in → numbers out)?
  │   ├── Does it reference a specific standard (IS 456, ACI)?
  │   │     YES → codes/<standard>/
  │   └── Is it general math (not tied to a standard)?
  │         YES → core/ or a shared utility
  │
  ├── Does it COORDINATE multiple calculations or handle I/O?
  │   ├── Does it parse files (CSV, Excel, JSON)?
  │   │     YES → services/adapters.py
  │   ├── Does it call multiple Layer 2 functions and combine results?
  │   │     YES → services/
  │   └── Does it generate reports, exports, or formatted output?
  │         YES → services/
  │
  └── Does it handle HTTP requests, render UI, or manage state?
        YES → fastapi_app/ or react_app/
```

### 5.3 Checklist for Starting a New Layered Project

When you create your next repo, follow this order:

```
Step 1: Define Core Types First
   └── What data structures does your domain need?
   └── What errors can occur?
   └── What constants are universal?

Step 2: Write Pure Math / Business Rules
   └── Each function: parameters in → result out
   └── NO imports from outside core/
   └── Tag every function with its source reference

Step 3: Build Service Orchestration
   └── One function per "use case" (design_beam, check_column)
   └── Call math functions, collect results
   └── Handle I/O (file parsing, report generation) HERE

Step 4: Add UI Last
   └── Thin wrappers around service functions
   └── HTTP routing, form rendering, API documentation
   └── NEVER duplicate business logic
```

### 5.4 Common Mistakes to Avoid (Learned the Hard Way)

| Mistake | Why It's Bad | Where It Should Be |
|---------|-------------|--------------------|
| Math formula in a FastAPI router | Can't test without HTTP | `codes/` |
| CSV parsing in a math module | Can't test math without files | `services/adapters.py` |
| FastAPI import in services | Service only works in web context | Remove it |
| `print()` in a math function | Pollutes output, breaks pipelines | `services/` logging |
| `config.json` read in codes/ | Path-dependent, fails in CI | `services/` or `core/` defaults |
| Duplicate math in JavaScript | Drifts out of sync, wrong formulas | Call the API instead |

### 5.5 The "Can I Test This With Just Numbers?" Rule

Before committing any code in Layer 2 (`codes/`), ask yourself:

> **Can I test this function by calling it with literal numbers and checking the output?**

```python
# ✅ YES — this is perfect Layer 2 code
def test_mu_lim():
    result = calculate_mu_lim(b=300, d=450, fck=25, fy=500)
    assert abs(result - 199.16) < 1.0

# ❌ NO — this needs file system, so it's Layer 3
def test_batch_design():
    results = batch_design_from_csv("beams.csv")  # Needs a file!
    assert len(results) == 10
```

If the answer is NO, the function belongs in Layer 3 (services), not Layer 2 (codes).

---

## Part 6: Real Violations and How to Fix Them

### 6.1 Violation Gallery

**Violation 1: Codes importing from Services (circular dependency)**
```python
# ❌ BAD: codes/is456/flexure.py
from structural_lib.services.api import design_beam_is456

def enhanced_flexure(...):
    base = design_beam_is456(...)  # BOOM: circular import
```
**Fix:** If you need to compose multiple calculations, do it in services/, not codes/.

**Violation 2: Codes doing file I/O**
```python
# ❌ BAD: codes/is456/materials.py
import json
with open("config.json") as f:
    config = json.load(f)
```
**Fix:** Pass configuration as function parameters. Read files in services/.

**Violation 3: Services importing from UI**
```python
# ❌ BAD: services/beam_api.py
from fastapi import HTTPException  # Importing UI framework!

def design_beam_is456(...):
    if fck <= 0:
        raise HTTPException(status_code=400, detail="Bad fck")
```
**Fix:** Raise `ValidationError` (from core/errors.py). Let the FastAPI router catch it and convert to HTTP response.

**Violation 4: UI duplicating math**
```typescript
// ❌ BAD: react_app/src/utils/calcShear.ts
export function calcShear(fck: number, b: number, d: number) {
    return 0.85 * Math.sqrt(0.8 * fck) * b * d / 6;
    // This is ACI 318, not IS 456! Wrong code entirely.
}
```
**Fix:** Delete the JS math. Call `POST /api/v1/design/beam` instead.

### 6.2 How to Check for Violations

```bash
# Check import boundaries — catches wrong-direction imports
.venv/bin/python scripts/check_architecture_boundaries.py

# Validate all imports resolve — catches broken imports after moves
.venv/bin/python scripts/validate_imports.py --scope structural_lib

# Full architecture check (includes duplication scan)
./run.sh check --quick
```

---

## Part 7: Comparisons with Other Architectures

### 7.1 How Our Layers Map to Famous Patterns

```
┌───────────────────┬──────────────────┬──────────────────┬─────────────────┐
│   Our Library     │   Clean Arch     │      MVC         │   Hexagonal     │
├───────────────────┼──────────────────┼──────────────────┼─────────────────┤
│ Core (Layer 1)    │ Entities         │ Model (types)    │ Domain Model    │
│ Codes (Layer 2)   │ Use Cases        │ Model (logic)    │ Domain Services │
│ Services (Layer 3)│ Interface Adapt. │ Controller       │ Application     │
│ UI (Layer 4)      │ Frameworks       │ View             │ Adapters        │
└───────────────────┴──────────────────┴──────────────────┴─────────────────┘
```

**Our unique twist:** We split "Model" into Core (code-agnostic types) and Codes (code-specific math). Most MVC apps don't need this, but domain-specific calculation libraries benefit enormously from this separation — it's what makes multi-code support possible.

### 7.2 When You DON'T Need 4 Layers

Not every project needs this:
- **Simple CRUD apps** — 2-3 layers suffice (routes + models + database)
- **Scripts** — One file is fine
- **Prototypes** — Speed matters more than structure

**You need 4 layers when:**
- Your domain has **complex calculations** (engineering, finance, science)
- You need **multiple interfaces** (API + CLI + notebook)
- **Correctness is critical** (wrong answers cost money or lives)
- You plan to support **multiple standards/rulesets** in the future

---

## Part 8: Hands-On Exercises

### Exercise 1: Identify the Layer

For each file, identify which layer it belongs to and what it can import:

```
1. Python/structural_lib/core/data_types.py       → Layer ?
2. Python/structural_lib/codes/is456/beam/shear.py → Layer ?
3. Python/structural_lib/services/beam_api.py      → Layer ?
4. fastapi_app/routers/design.py                   → Layer ?
5. Python/structural_lib/codes/is456/materials.py  → Layer ?
6. Python/structural_lib/core/errors.py            → Layer ?
7. Python/structural_lib/services/adapters.py      → Layer ?
8. react_app/src/components/design/BeamForm.tsx     → Layer ?
```

<details>
<summary>Answers</summary>

1. **Layer 1 (Core)** — Defines types. Can import: standard library only.
2. **Layer 2 (Codes)** — Pure IS 456 shear math. Can import: core/ and other codes/.
3. **Layer 3 (Services)** — Orchestration. Can import: core/ and codes/.
4. **Layer 4 (UI)** — HTTP interface. Can import: services/ and core/.
5. **Layer 2 (Codes)** — Material properties. Can import: core/ only.
6. **Layer 1 (Core)** — Error types. Can import: standard library only.
7. **Layer 3 (Services)** — CSV/Excel adapters. Can import: core/ and codes/.
8. **Layer 4 (UI)** — React component. Talks to API, never imports Python code.

</details>

### Exercise 2: Spot the Violation

Which of these imports are architecture violations?

```python
# File: codes/is456/beam/flexure.py
from structural_lib.core.data_types import FlexureResult     # A
from structural_lib.services.api import design_beam_is456    # B
from structural_lib.codes.is456.materials import get_xu_max_d  # C
import json                                                   # D

# File: services/beam_api.py
from structural_lib.codes.is456.beam import flexure          # E
from fastapi import FastAPI                                   # F
from structural_lib.core.inputs import BeamInput             # G
```

<details>
<summary>Answers</summary>

- **A:** ✅ OK — codes/ importing from core/ (downward)
- **B:** ❌ VIOLATION — codes/ importing from services/ (upward!)
- **C:** ✅ OK — codes/ importing from sibling in same layer
- **D:** ✅ OK — standard library import (but be careful — `json` is fine, `open()` would suggest I/O which is a smell in Layer 2)
- **E:** ✅ OK — services/ importing from codes/ (downward)
- **F:** ❌ VIOLATION — services/ importing from UI framework (upward!)
- **G:** ✅ OK — services/ importing from core/ (downward)

</details>

### Exercise 3: Design a New Feature

You're asked to add **slab design** to the library. Where does each piece go?

```
a) SlabResult dataclass (fields: thickness_mm, Ast_x, Ast_y, is_safe)  → ?
b) one_way_slab_design(fck, fy, lx, ly, load, ...) → SlabResult        → ?
c) design_slab_is456(*, units, ...) that calls one_way + two_way        → ?
d) POST /api/v1/design/slab endpoint                                     → ?
e) SlabDesignRequest Pydantic model                                      → ?
```

<details>
<summary>Answers</summary>

- **a)** `core/data_types.py` — Layer 1 (it's a type definition, code-agnostic)
- **b)** `codes/is456/slab/one_way.py` — Layer 2 (pure math, IS 456 specific)
- **c)** `services/slab_api.py` — Layer 3 (orchestration, calls multiple math functions)
- **d)** `fastapi_app/routers/slab.py` — Layer 4 (HTTP wrapper)
- **e)** `fastapi_app/models/slab.py` — Layer 4 (Pydantic model for HTTP validation)

</details>

### Exercise 4: Run the Architecture Checker

```bash
# From workspace root:
.venv/bin/python scripts/check_architecture_boundaries.py
.venv/bin/python scripts/validate_imports.py --scope structural_lib

# Expected: no violations. If you see any, they're real bugs!
```

---

## Part 9: Quick Reference Cards

### Card 1: Where Does My Code Go?

```
┌──────────────────────────────────────────────────────┐
│  "Is it a TYPE?"          → core/                    │
│  "Is it PURE MATH?"       → codes/<standard>/        │
│  "Does it COORDINATE?"    → services/                │
│  "Does it TALK TO USERS?" → fastapi_app/ or react_app │
└──────────────────────────────────────────────────────┘
```

### Card 2: Import Rules Cheat Sheet

```
┌─────────────┬───────────────────────────────────────┐
│ I'm in...   │ I can import from...                   │
├─────────────┼───────────────────────────────────────┤
│ core/       │ stdlib ONLY (math, dataclasses, enum)  │
│ codes/      │ core/ + other codes/ siblings          │
│ services/   │ core/ + codes/                         │
│ fastapi/    │ core/ + codes/ + services/             │
│ react/      │ Calls API endpoints (no Python import) │
└─────────────┴───────────────────────────────────────┘
```

### Card 3: The Three Questions Before Committing

```
1. "Can I test this with just numbers?"
   NO → It doesn't belong in codes/

2. "Does this import from a layer above?"
   YES → Architecture violation, move the code

3. "Is there already a function that does this?"
   CHECK → .venv/bin/python scripts/discover_api_signatures.py <name>
```

---

## Part 10: Can You Explain? (Self-Check)

### Q1: Why can't Layer 2 (codes/) import from Layer 3 (services/)?

<details>
<summary>Answer</summary>

Three reasons:

1. **Circular imports.** `services/api.py` already imports from `codes/is456/flexure.py`. If `flexure.py` also imports from `services/api.py`, Python hits a circular dependency at startup and crashes with `ImportError`.

2. **Testability.** Pure math functions should be testable with just numbers. If `flexure.py` depends on `services/`, your test must set up the entire services layer — adapters, CSV parsing, report generation — just to test a formula.

3. **Reuse.** The pure math can be used by CLI tools, notebooks, other services, even other projects. If it depends on our services layer, it only works within our specific orchestration framework.

</details>

### Q2: A new developer puts CSV parsing code inside `codes/is456/flexure.py`. What's wrong?

<details>
<summary>Answer</summary>

CSV parsing is I/O — it belongs in Layer 3 (services/adapters.py). The codes/ layer must be pure math: numbers in, numbers out.

Putting CSV parsing in codes/ means:
- The flexure module needs `csv` and `pathlib` imports (file system access)
- Tests must create temporary CSV files to test flexure formulas
- The function can't be called from a web API without first writing a CSV file
- It violates the rule: "Layer 2: NO I/O"

The correct fix: CSV parsing in `services/adapters.py`, which extracts numbers from the CSV, then passes those numbers to `codes/is456/flexure.py`.

</details>

### Q3: Why do we split Core (Layer 1) from Codes (Layer 2)?

<details>
<summary>Answer</summary>

Because types are code-agnostic but formulas are code-specific.

`FlexureResult` has the same fields whether the flexure was calculated per IS 456 or ACI 318 — both need `Ast_required`, `xu`, `Mu_lim`, etc. By putting `FlexureResult` in `core/`, both `codes/is456/flexure.py` and future `codes/aci318/flexure.py` can use it.

If `FlexureResult` lived inside `codes/is456/`, ACI 318 would need to import from IS 456's module — wrong and confusing.

It's like database ORMs — models are defined separately from queries. The shape of data is one concern; the logic that produces it is another.

</details>

### Q4: Could you have just 3 layers (merge Core into Codes)?

<details>
<summary>Answer</summary>

You could, but you'd lose two benefits:

1. **Error types would be tied to IS 456.** `ValidationError`, `DesignConstraintError`, etc. are code-agnostic. They're useful for ACI 318 or Eurocode 2 too. If they lived in `codes/is456/`, other codes would import from `codes/is456/errors.py` — semantically wrong.

2. **Base classes for polymorphism.** `core/base.py` defines `DesignCode` (ABC) and `FlexureDesigner` (ABC). These define the contract that all codes must implement. They can't live inside any specific code because they're the *interface* that codes implement.

The Core layer is small (~20 files) but crucial for extensibility.

</details>

### Q5: We allow UI (Layer 4) to import from codes/ (Layer 2). Isn't that dangerous?

<details>
<summary>Answer</summary>

It's allowed but **discouraged in practice**. The rule says Layer 4 *can* import from any layer below it, but our convention is:

- **Prefer:** UI → Services (services orchestrate everything)
- **Acceptable:** UI → Core (for type definitions, error types)
- **Avoid:** UI → Codes directly (bypasses orchestration, risks duplicating validation)

The only common case for direct codes/ import in UI is accessing constants or enums, not calling math functions.

</details>

---

## Summary — What You Now Know

| Concept | Key Point |
|---------|-----------|
| **Layer 1: Core** | Types, errors, base classes, constants — no formulas, no I/O |
| **Layer 2: Codes** | Pure math — numbers in → numbers out, tagged with @clause |
| **Layer 3: Services** | Orchestration — calls math, handles I/O, collects results |
| **Layer 4: UI** | HTTP/React — thin wrappers, never contains formulas |
| **Import rule** | Core ← Codes ← Services ← UI (never upward) |
| **Why layers?** | Testing, no circular deps, reuse, parallelism, multi-code |
| **Decision rule** | "Can I test with just numbers?" → Yes = codes/, No = services/ |
| **How to check** | `check_architecture_boundaries.py`, `validate_imports.py` |
| **For your next repo** | Define types → Write math → Orchestrate → Add UI (in that order) |

---

## 📎 References

- **Architecture doc:** `docs/architecture/unified-architecture-v1.md` (the authoritative source)
- **Boundary checker:** `scripts/check_architecture_boundaries.py`
- **Import validator:** `scripts/validate_imports.py`
- **Core types:** `Python/structural_lib/core/data_types.py`
- **Core errors:** `Python/structural_lib/core/errors.py`
- **Core materials:** `Python/structural_lib/core/materials.py`
- **Core base classes:** `Python/structural_lib/core/base.py`
- **IS 456 flexure:** `Python/structural_lib/codes/is456/beam/flexure.py`
- **IS 456 materials:** `Python/structural_lib/codes/is456/materials.py`
- **Services API:** `Python/structural_lib/services/beam_api.py`
- **FastAPI router:** `fastapi_app/routers/design.py`

---

## What's Next?

**Day 9: Type System** — Now that you understand the layers, we'll dive into the types that flow between them. Dataclasses, Pydantic models, TypedDicts, frozen immutability, and the `DictCompatMixin` that lets dataclasses behave like dicts. You'll see why `b_mm` is not called `width` and how the type system catches bugs at both compile time and runtime.