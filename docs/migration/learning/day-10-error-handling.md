# Day 10: Error Handling & Validation (Deep Dive)

**Type:** Learning Module
**Audience:** Solo developer (coder, not a civil engineer)
**Status:** Active
**Importance:** Critical
**Created:** 2026-04-08
**Last Updated:** 2026-04-09
**Prerequisites:** Day 8 (architecture layers), Day 9 (type system)
**Library files:** `Python/structural_lib/core/errors.py`, `Python/structural_lib/core/validation.py`, `Python/structural_lib/services/common_api.py`
**IS 456 Clauses:** Various (referenced in error messages)

---

## What You'll Learn Today

By the end of this module you'll understand:
- The two error systems: exceptions (stop) vs DesignError dataclasses (collect)
- The exception hierarchy (6 exception classes + 3 sub-types)
- The `StructuralLibError` 4-field pattern (message, details, suggestion, clause_ref)
- The "validate at boundaries" philosophy — check once at the gate, not at every seat
- The 8+ validation functions and how they compose to report ALL issues at once
- Why every error message answers three questions: what, why, how to fix
- Pre-defined frozen error constants (`E_INPUT_001`, etc.) and the Severity enum
- **Things to know** — silent swallowing, bare except, exception vs error-value tradeoffs
- **What can be done better** — structured error catalogs, error codes for i18n
- **Innovation** — `result` types (Rust-style), `returns` library, structured logging
- **Next repo must-add** — error taxonomy, machine-readable error catalog

---

## Part 1: Two Error Systems — Why Both?

### 1.1 The Core Problem

A structural beam design involves multiple checks: dimensions, materials, flexure capacity, shear capacity, detailing requirements. What happens when THREE of these fail?

```python
# ❌ Approach 1: Raise on first error (stops at #1, user never sees #2 and #3)
def design_beam(b, d, fck, fy, Mu, Vu):
    if b <= 0: raise ValueError("b must be positive")      # Stops here!
    if fck < 15: raise ValueError("fck must be >= 15")     # Never reached
    if Vu > capacity: raise ValueError("shear fails")      # Never reached

# ✅ Approach 2: Collect all errors, return them together
def design_beam(b, d, fck, fy, Mu, Vu):
    errors = []
    if b <= 0: errors.append(E_INPUT_001)
    if fck < 15: errors.append(E_INPUT_004)
    # ... continue checking everything
    result = FlexureResult(..., errors=errors)
    return result  # User sees ALL 3 issues at once
```

That's why our library has **two** error systems:

### 1.2 System 1: Exceptions — For Stopping Execution

```python
raise ValidationError(
    "Beam width b=150mm is below minimum 200mm",
    details={"b_mm": 150, "minimum": 200},
    suggestion="Increase beam width to at least 200mm",
    clause_ref="Cl. 26.5.1.1"
)
```

Exceptions **halt immediately**. Use them when the input is so wrong that continuing would produce garbage.

### 1.3 System 2: DesignError Dataclasses — For Collecting Issues

```python
error = DesignError(
    code="E_INPUT_001",
    severity=Severity.ERROR,
    message="b must be > 0",
    field="b",
    hint="Check beam width input.",
    recovery="Provide beam width b > 0 mm. Typical: 200–500 mm."
)
```

`DesignError` objects are **data, not exceptions**. They accumulate in a list inside result objects, letting the function report multiple issues at once.

### 1.4 When to Use Which — Decision Table

```
┌─────────────────────────────────────────────────────────────────┐
│  DECISION: Exception or DesignError?                            │
│                                                                 │
│  Can a meaningful result be computed?                            │
│    NO  → EXCEPTION (stop immediately)                           │
│    YES → DESIGN ERROR (collect, attach to result)               │
│                                                                 │
│  Is this at the system boundary (API, service entry)?            │
│    YES → EXCEPTION (reject bad input before processing)          │
│    NO  → DESIGN ERROR (inside math, collect warnings)            │
│                                                                 │
│  Batch processing 1000 beams — should one failure stop all?      │
│    YES → EXCEPTION                                              │
│    NO  → DESIGN ERROR (report per-beam failures, continue)       │
└─────────────────────────────────────────────────────────────────┘
```

| Use Case | System | Why |
|----------|--------|-----|
| Negative dimension (`b = -100`) | Exception at boundary | Can't compute anything meaningful |
| Wrong type (`b = "hello"`) | Exception | Fundamental type error |
| Capacity exceeded (`Mu > Mu_lim`) | DesignError | Design continues, reports `is_safe=False` |
| Steel ratio near max (warning) | DesignError | Design passes but engineer should know |
| Numerical explosion | Exception (`CalculationError`) | Math broke — results unreliable |
| Configuration error | Exception | Library misconfigured |

---

## Part 2: The Exception Hierarchy

### 2.1 The Full Tree

```
StructuralLibError (base — all library exceptions)
│
├── ValidationError (bad inputs)
│   ├── DimensionError (b, d, D problems)
│   ├── MaterialError (fck, fy problems)
│   └── LoadError (moment, shear problems)
│
├── DesignConstraintError (design is infeasible)
│   └── "Moment exceeds section capacity"
│
├── ComplianceError (code requirements not met)
│   └── "Steel ratio below minimum per Cl 26.5.1.1"
│
├── ConfigurationError (library misconfigured)
│   └── "Unknown design code 'ACI318'"
│
└── CalculationError (numerical issues)
    └── "Convergence failed after 100 iterations"
```

### 2.2 Why a Hierarchy? — Granular Catching

```python
# Level 1: Catch EVERYTHING from the library
try:
    result = design_beam_is456(...)
except StructuralLibError as e:
    log.error(f"Library error: {e}")  # Any library issue

# Level 2: Catch only validation problems
try:
    result = design_beam_is456(...)
except ValidationError as e:
    return {"error": "Bad input", "details": e.details}

# Level 3: Catch ONLY dimension problems
try:
    result = design_beam_is456(...)
except DimensionError as e:
    highlight_field("width")  # Frontend can highlight the specific field
```

This is like HTTP status codes: `StructuralLibError` = any 4xx/5xx → `ValidationError` = 400 Bad Request → `DimensionError` = 400 with specific error code for dimensions.

### 2.3 The Rich Base Exception — `StructuralLibError`

Every exception carries **four pieces of context**:

```python
# ACTUAL library code from core/errors.py
class StructuralLibError(Exception):
    def __init__(
        self,
        message: str,                    # 1. What happened
        *,
        details: dict[str, Any] | None = None,  # 2. Machine-readable data
        suggestion: str | None = None,   # 3. How to fix it
        clause_ref: str | None = None,   # 4. IS 456 clause
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
        self.clause_ref = clause_ref
```

**In practice:**

```python
raise DesignConstraintError(
    "Moment Mu=250 kN·m exceeds section capacity Mu,lim=200 kN·m",  # WHAT
    details={"mu_knm": 250, "mu_lim_knm": 200},                     # DATA
    suggestion="Increase section depth or add compression steel",     # FIX
    clause_ref="Cl. 38.1"                                           # CODE REF
)

# The engineer sees:
#   Moment Mu=250 kN·m exceeds section capacity Mu,lim=200 kN·m
#   (Ref: IS 456:2000 Cl. 38.1)
#   Suggestion: Increase section depth or add compression steel
#   [mu_knm=250, mu_lim_knm=200]
```

**Why all four fields?**

| Field | For Humans | For Machines | For Engineers |
|-------|-----------|-------------|--------------|
| `message` | "What went wrong" | Display text | Problem statement |
| `details` | Supporting numbers | JSON error response | Input values |
| `suggestion` | "How to fix it" | Actionable guidance | Design modification |
| `clause_ref` | Code reference | Traceability link | Verify against IS 456 |

---

## Part 3: The DesignError Dataclass — Collected Errors

### 3.1 Structure

```python
# ACTUAL library code from core/errors.py
@dataclass(frozen=True)
class DesignError:
    code: str              # "E_INPUT_001", "E_FLEXURE_002"
    severity: Severity     # ERROR, WARNING, INFO
    message: str           # Human-readable description
    field: str | None = None      # Which input field caused it
    hint: str | None = None       # Short fix suggestion
    clause: str | None = None     # IS 456 clause reference
    recovery: str | None = None   # Step-by-step fix instructions

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON API responses."""
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "field": self.field,
            "hint": self.hint,
            "recovery": self.recovery,
        }
```

### 3.2 Pre-defined Frozen Constants

```python
# ACTUAL library constants — always the same object, always consistent
E_INPUT_001 = DesignError(
    code="E_INPUT_001", severity=Severity.ERROR,
    message="b must be > 0", field="b",
    hint="Check beam width input.",
    recovery="Provide beam width b > 0 mm. Typical rectangular beams: 200–500 mm.",
)

E_INPUT_003a = DesignError(
    code="E_INPUT_003a", severity=Severity.ERROR,
    message="d_total must be > 0", field="D",
    hint="Check overall depth input.",
)

E_FLEXURE_001 = DesignError(
    code="E_FLEXURE_001", severity=Severity.ERROR,
    message="Mu exceeds Mu_lim",
    hint="Section needs doubly reinforced design or increased depth.",
    clause="Cl. 38.1",
)

E_SHEAR_001 = DesignError(
    code="E_SHEAR_001", severity=Severity.ERROR,
    message="tv exceeds tc_max",
    hint="No amount of stirrups can fix this — increase section size.",
    clause="Cl. 40.2.3",
)
```

**Why constants, not inline creation?** Consistency. Every time the library reports "b must be > 0", it's the **exact same** `E_INPUT_001` object. Same code, message, hint, recovery. No developer invents a different message.

### 3.3 Severity Levels

```python
class Severity(Enum):
    ERROR = "error"      # Design fails. Must fix before proceeding.
    WARNING = "warning"  # Design passes but has concerns.
    INFO = "info"        # Informational, no action needed.
```

| Severity | Meaning | Example | Action Required |
|----------|---------|---------|----------------|
| `ERROR` | Cannot proceed safely | "b must be > 0" | **Must fix** |
| `WARNING` | Passes but risky | "Steel ratio 3.8% near max 4%" | **Should review** |
| `INFO` | Just FYI | "Using doubly reinforced design" | None |

### 3.4 How Errors Flow Through Results

```python
# Inside a design function:
result = FlexureResult(
    Mu_lim=200.0,
    Ast_required=0.0,      # Zero because design failed
    is_safe=False,
    errors=[E_FLEXURE_001],  # Error attached to result
    clause_refs={"flexure_check": "Cl. 38.1"},
)

# Caller checks:
if not result.is_safe:
    for error in result.errors:
        print(f"[{error.severity.value}] {error.code}: {error.message}")
        # [error] E_FLEXURE_001: Mu exceeds Mu_lim
```

---

## Part 4: Validation at Boundaries — The Gate Philosophy

### 4.1 The Core Principle

**Check once at the gate, not at every seat.**

```
┌───────────────────────────────────────────────────────────────┐
│                      DATA FLOW                                 │
│                                                                │
│  Raw JSON ──► [GATE 1: Pydantic] ──► [GATE 2: Services]       │
│                                        ──► [TRUSTED: Math]     │
│                                                                │
│  Gate 1: Types, ranges, required fields                        │
│  Gate 2: Cross-field checks, plausibility, unit sanity          │
│  Math:   NO VALIDATION — trusts gates                           │
└───────────────────────────────────────────────────────────────┘
```

### 4.2 Gate 1 — Pydantic (Layer 4)

```python
# FastAPI model — rejects garbage before it reaches business logic
class BeamDesignRequest(BaseModel):
    width: float = Field(gt=0, le=2000)     # Must be positive, max 2m
    depth: float = Field(gt=0, le=3000)     # Must be positive, max 3m
    fck: float = Field(ge=15, le=80)        # IS 456 range: M15-M80
    fy: float = Field(ge=250, le=600)       # Fe250-Fe600
    moment: float = Field(ge=0)             # Non-negative
```

**What Gate 1 catches:** wrong types ("hello" for width), out-of-range (fck=200), missing required fields, negative values.

### 4.3 Gate 2 — Services Layer (Layer 3)

```python
# ACTUAL library code — services/common_api.py
def _validate_plausibility(fck, fy, b, d):
    """Catch likely unit mistakes and physically impossible inputs."""
    if fck > 120:
        raise ValidationError(
            f"fck={fck} N/mm² is unusually high. Did you mean psi?",
            suggestion="IS 456 defines concrete grades M15-M80 (15-80 N/mm²)"
        )
    if b > 5000:
        raise ValidationError(
            f"b={b} mm seems too large. Did you pass micrometers?",
            suggestion="Typical beam widths: 200-500mm"
        )
```

**What Gate 2 catches:** cross-field inconsistencies (d > D), unit confusion (passing psi instead of MPa), physically implausible values.

### 4.4 Math Layer — No Redundant Validation

```python
# codes/is456/beam/flexure.py — TRUSTS inputs from service layer
def design_singly_reinforced(fck, fy, b_mm, d_mm, Mu_kNm):
    # No validation here! Services already checked:
    #   fck > 0, fy > 0, b > 0, d > 0, Mu >= 0
    xu_max_d = get_xu_max_d(fy)
    Mu_lim = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d) * b_mm * d_mm**2 * fck
    # ... pure math continues
```

**Why no validation in math?** Three reasons:
1. **Performance** — batch processing 1000 beams × 3-4 redundant checks = thousands of wasted cycles
2. **Clarity** — one owner (services), one location, one error message
3. **Purity** — math functions should be pure: same inputs → same outputs, no side effects

### 4.5 Composable Validation Functions

```python
# ACTUAL library code from core/validation.py
# Each function returns list[DesignError] — empty if OK

def validate_all_inputs(b, d, D, fck, fy, Mu, cover):
    """Compose multiple validators — report ALL issues at once."""
    errors = []
    errors.extend(validate_dimensions(b, d, D))           # b>0, d>0, d<D
    errors.extend(validate_materials(fck, fy))             # fck>0, fy>0
    errors.extend(validate_cover(cover, D))                # cover < D
    errors.extend(validate_all_positive(Mu=Mu))            # Mu >= 0
    return errors  # User sees ALL issues, not just the first one
```

**Available validators:**

| Function | What It Checks | Returns |
|----------|---------------|---------|
| `validate_dimensions(b, d, D)` | Width, depths > 0, d < D | `list[DesignError]` |
| `validate_materials(fck, fy)` | Concrete/steel strength > 0 | `list[DesignError]` |
| `validate_positive(value, name, ...)` | Any value > 0 | `list[DesignError]` |
| `validate_range(value, min, max, ...)` | Value within bounds | `list[DesignError]` |
| `validate_cover(cover, D)` | Cover < overall depth | `list[DesignError]` |
| `validate_all_positive(**kwargs)` | Multiple values > 0 | `list[DesignError]` |
| `validate_stirrup_parameters(asv, s)` | Stirrup area/spacing valid | `list[DesignError]` |
| `validate_geometry_relationship(d, D, cover)` | D > d + cover | `list[DesignError]` |

---

## Part 5: Error Message Quality

### 5.1 The Three Questions Every Error Must Answer

```
┌─────────────────────────────────────────────────────────────┐
│  ❌ BAD ERROR MESSAGE:                                      │
│     "Error: invalid input"                                   │
│                                                             │
│  ✅ GOOD ERROR MESSAGE (ours):                              │
│     WHAT: "Beam width b=150mm is below minimum 200mm"       │
│     WHY:  "(Ref: IS 456:2000 Cl. 26.5.1.1)"               │
│     FIX:  "Increase beam width to at least 200mm"           │
│     DATA: [b_mm=150, minimum=200]                           │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Error Message Template

```python
# Pattern used throughout the library:
raise ValidationError(
    f"{WHAT_PARAMETER}={ACTUAL_VALUE} is {VIOLATION} {LIMIT}",  # What
    details={PARAM: VALUE, LIMIT_NAME: LIMIT_VALUE},            # Data
    suggestion=f"{ACTION} to at least {MINIMUM}",               # Fix
    clause_ref=f"Cl. {CLAUSE_NUMBER}"                           # Code ref
)

# Real example:
raise ValidationError(
    f"Steel grade fy={fy} N/mm² exceeds IS 456 maximum of 500 N/mm²",
    details={"fy": fy, "max_fy": 500},
    suggestion="Use Fe250, Fe415, or Fe500 as per IS 456 Table 5.6",
    clause_ref="Cl. 5.6.1"
)
```

### 5.3 API Error Response Format

When a `DesignError` reaches FastAPI, it becomes a JSON response:

```json
{
  "success": false,
  "errors": [
    {
      "code": "E_INPUT_001",
      "severity": "error",
      "message": "b must be > 0",
      "field": "b",
      "hint": "Check beam width input.",
      "recovery": "Provide beam width b > 0 mm. Typical: 200–500 mm."
    },
    {
      "code": "E_INPUT_004",
      "severity": "error",
      "message": "fck must be > 0",
      "field": "fck",
      "hint": "Check concrete grade input."
    }
  ]
}
```

The React frontend can: display `message`, highlight `field` in the form, show `recovery` as a tooltip.

---

## Part 6: The `@clause` Decorator — Traceability

### 6.1 Linking Code to IS 456 Clauses

```python
# ACTUAL library code from codes/is456/beam/flexure.py
@clause("38.1", "38.1.1")
def calculate_mu_lim(b: float, d: float, fck: float, fy: float) -> float:
    """
    Calculate limiting moment of resistance.

    Mu_lim = 0.36 × (xu_max/d) × (1 - 0.42 × xu_max/d) × b × d² × fck

    References: IS 456:2000, Cl. 38.1
    """
    xu_max_d = get_xu_max_d(fy)
    return 0.36 * xu_max_d * (1 - 0.42 * xu_max_d) * b * d**2 * fck / 1e6
```

The `@clause("38.1", "38.1.1")` decorator:
1. Tags the function with its IS 456 clause references
2. Makes clauses discoverable programmatically
3. Supports the parity dashboard (`./run.sh parity`) that tracks clause coverage

### 6.2 Error Messages Reference Clauses

```python
# When flexure raises an error, the clause is attached:
if b <= 0:
    raise DimensionError(
        dimension_too_small("beam width b", b, 0, "Cl. 38.1"),
        details={"b": b, "minimum": 0},
        clause_ref="Cl. 38.1"
    )
```

This creates a traceable chain: Error → Clause → IS 456 book → Verification.

---

## Part 7: Exercises

### Exercise 1: Explore the Exception Hierarchy

```python
# Start: .venv/bin/python
from structural_lib.core.errors import (
    StructuralLibError, ValidationError, DimensionError,
    MaterialError, DesignConstraintError,
    ComplianceError, ConfigurationError, CalculationError,
)

# ── 1a: Test the hierarchy ──
print("=== Hierarchy ===")
for exc in [DimensionError, MaterialError]:
    print(f"  {exc.__name__} → ValidationError: {issubclass(exc, ValidationError)}")

for exc in [ValidationError, DesignConstraintError, ComplianceError]:
    print(f"  {exc.__name__} → StructuralLibError: {issubclass(exc, StructuralLibError)}")

# ── 1b: Create and inspect a rich exception ──
err = ValidationError(
    "Steel grade fy=600 N/mm² is above IS 456 maximum",
    details={"fy": 600, "max_fy": 500},
    suggestion="Use Fe250, Fe415, or Fe500",
    clause_ref="Cl. 5.6.1"
)
print(f"\nMessage: {err.message}")
print(f"Details: {err.details}")
print(f"Suggestion: {err.suggestion}")
print(f"Clause: {err.clause_ref}")
```

### Exercise 2: Compose Validators

```python
from structural_lib.core.validation import validate_dimensions, validate_materials

# ── 2a: All valid ──
errors = validate_dimensions(b=300, d=450, D=500)
errors.extend(validate_materials(fck=25, fy=500))
print(f"Valid: {len(errors)} errors")

# ── 2b: Multiple failures at once ──
errors = validate_dimensions(b=-100, d=600, D=500)  # b<0, d>D
errors.extend(validate_materials(fck=0, fy=-100))    # both invalid
print(f"\n{len(errors)} errors found:")
for e in errors:
    print(f"  [{e.severity.value}] {e.code}: {e.message}")
```

### Exercise 3: Serialize for API Response

```python
from structural_lib.core.errors import E_INPUT_001, E_INPUT_004
import json

errors = [E_INPUT_001, E_INPUT_004]
response = {
    "success": False,
    "errors": [e.to_dict() for e in errors],
}
print(json.dumps(response, indent=2))
```

---

## Part 8: Can You Explain? (Self-Check)

### Q1: Why TWO error systems (exceptions + DesignError)?

<details><summary>Answer</summary>

**Exceptions** = "stop everything." Negative beam width, missing parameter, numerical explosion. Can't produce meaningful output.

**DesignError** = "here's the result, but it has issues." Capacity exceeded, steel ratio near max, detailing concern. The function returns a result with errors attached so the caller sees ALL issues at once.

Batch design of 100 beams: exceptions stop at beam #1. DesignErrors process all 100 and report which ones fail.
</details>

### Q2: Why validate at boundaries, not inside math functions?

<details><summary>Answer</summary>

1. **Performance** — batch 1000 beams × redundant checks = wasted cycles
2. **Single owner** — services validates, codes trusts. One location, one error message.
3. **Purity** — math functions should be pure (no I/O, no side effects).

If both layers validate `b > 0` and use different messages, which does the user see? Boundary validation answers: services owns it.
</details>

### Q3: Why frozen error constants?

<details><summary>Answer</summary>

1. **Immutability** — `E_INPUT_001['message'] = 'hacked'` is impossible with frozen dataclass
2. **Consistency** — every "b must be > 0" is the exact same object everywhere
3. **Type safety** — IDE shows `e.code`, `e.message`, `e.severity` with autocomplete
</details>

### Q4: Why `clause_ref` on every exception?

<details><summary>Answer</summary>

Traceability. Structural engineers must verify library errors against IS 456. `clause_ref="Cl. 26.5.1.1"` lets them open the code to that exact clause. This isn't optional — professional practice requires traceable design output.
</details>

---

## Part 9: Things to Know (Critical Knowledge)

### 9.1 Never Swallow Exceptions Silently

```python
# ❌ DEADLY — error disappears, wrong result used silently
try:
    result = design_beam_is456(...)
except Exception:
    pass  # Error swallowed! What result is "result" now? Undefined!

# ✅ CORRECT — handle specifically or re-raise
try:
    result = design_beam_is456(...)
except ValidationError as e:
    log.warning(f"Validation failed: {e.message}")
    return {"success": False, "error": e.message}
except StructuralLibError as e:
    log.error(f"Design error: {e}")
    raise  # Re-raise if you can't handle it
```

**Dev Rule U-1:** Never swallow exceptions silently. Every `except` must either handle the error meaningfully or re-raise.

### 9.2 Never Use Bare `except:`

```python
# ❌ BAD — catches KeyboardInterrupt, SystemExit, MemoryError too!
try:
    result = design_beam(...)
except:  # Bare except
    print("something went wrong")

# ✅ CORRECT — catch specific types
try:
    result = design_beam(...)
except StructuralLibError as e:
    handle_library_error(e)
except (TypeError, ValueError) as e:
    handle_input_error(e)
```

### 9.3 Exception vs Error-Value: The Tradeoff

```
Exceptions are:    ✅ Impossible to ignore (unhandled → crash)
                   ❌ Hard to compose (try/except nesting)
                   ❌ Interrupt control flow

Error values are:  ✅ Composable (list of errors, filter, sort)
                   ✅ Preserve control flow
                   ❌ Easy to ignore (caller might not check `result.errors`)

Our library uses BOTH:
  - Exceptions at boundaries (can't ignore invalid input)
  - Error values in results (composable, batch-friendly)
```

### 9.4 The "Details Dict" is Crucial for APIs

```python
# Without details — frontend can only show a message
raise ValidationError("Width is invalid")

# With details — frontend can highlight the EXACT field
raise ValidationError(
    "Width is invalid",
    details={"field": "b_mm", "value": -100, "minimum": 0}
)
# Frontend: highlight b_mm input, show "minimum: 0" tooltip
```

### 9.5 The `dimension_too_small()` Helper

```python
# Library provides error message builders:
from structural_lib.core.errors import dimension_too_small

msg = dimension_too_small("beam width b", -100, 0, "Cl. 38.1")
# → "beam width b = -100 is too small (minimum: 0, ref: Cl. 38.1)"
```

---

## Part 10: What Can Be Done Better

### 10.1 Current Issues

| Issue | Current State | Better Approach |
|-------|--------------|-----------------|
| **Error catalog is implicit** | Constants scattered in `errors.py` | Single `ERROR_CATALOG.json` file |
| **No error code registry** | `E_INPUT_001` numbering is manual | Auto-generate from catalog |
| **No i18n support** | Messages are English-only | Error codes + translations file |
| **DesignError fields vary** | Some have `recovery`, some don't | Make all fields required |
| **`clause` vs `clause_ref`** | Exception uses `clause_ref`, DesignError uses `clause` | Use same field name |
| **No error aggregation** | Each error is independent | Group by category/severity |

### 10.2 Inconsistent Field Names

```python
# Exception uses clause_ref:
raise ValidationError(..., clause_ref="Cl. 38.1")

# DesignError uses clause:
E_FLEXURE_001 = DesignError(..., clause="Cl. 38.1")

# This inconsistency confuses developers. Next repo: pick ONE name.
```

### 10.3 Missing Error Catalog

```python
# Currently: errors scattered across errors.py
E_INPUT_001 = DesignError(...)
E_INPUT_002 = DesignError(...)
# ... manually numbered, no index

# Better: machine-readable catalog
# errors/catalog.json
{
    "E_INPUT_001": {
        "severity": "error",
        "message_template": "{field} must be > {minimum}",
        "fields": ["b", "d", "D"],
        "clause": null,
        "category": "input_validation"
    }
}
```

---

## Part 11: Innovation Directions

### 11.1 Rust-Style `Result` Type (No Exceptions)

```python
# Using the 'returns' library:
from returns.result import Result, Success, Failure

def design_beam(b, d, fck, fy, Mu) -> Result[FlexureResult, DesignError]:
    if b <= 0:
        return Failure(E_INPUT_001)  # No exception raised!
    # ... computation
    return Success(FlexureResult(...))

# Caller MUST handle both cases:
match design_beam(300, 450, 25, 500, 150):
    case Success(result):
        print(f"Ast = {result.Ast_required}")
    case Failure(error):
        print(f"Failed: {error.message}")
```

**Advantage:** Errors become part of the type signature. The type checker forces callers to handle failures. No surprise exceptions.

### 11.2 Structured Logging with `structlog`

```python
import structlog

log = structlog.get_logger()

# Instead of: print(f"Error: {e}")
log.error("design_failed",
    error_code=e.code,
    beam_id="B-1",
    b_mm=300,
    fck=25,
    clause="Cl. 38.1",
)
# Output: {"event": "design_failed", "error_code": "E_FLEXURE_001", "beam_id": "B-1", ...}
# → Machine-parseable, searchable in log aggregators
```

### 11.3 Error Boundaries in React (Already Used!)

```tsx
// Our App.tsx already wraps with ErrorBoundary:
<ErrorBoundary>
  <QueryClientProvider client={queryClient}>
    <Routes>...</Routes>
  </QueryClientProvider>
</ErrorBoundary>

// This catches React rendering errors that escape component try/catch.
// It prevents the entire app from crashing on one component error.
```

### 11.4 `pydantic` Error Groups (Python 3.11+)

```python
# Python 3.11+ ExceptionGroup — raise MULTIPLE exceptions at once:
errors = [
    ValidationError("b must be > 0"),
    ValidationError("fck must be >= 15"),
]
raise ExceptionGroup("Multiple validation failures", errors)

# Caller can catch selectively:
try:
    ...
except* ValidationError as eg:
    for e in eg.exceptions:
        print(e.message)
```

### 11.5 Innovation Comparison

| Technology | What It Solves | Recommendation |
|-----------|---------------|----------------|
| `returns` Result type | Forces error handling | **Evaluate for next repo** |
| `structlog` | Machine-readable logs | **Use in production** |
| ExceptionGroup | Multiple errors at once | **Use (Python 3.11+)** |
| Error catalogs (JSON) | Consistency, i18n | **Must-add for next repo** |
| Domain error codes | Unique per-error identification | **Must-add** |

---

## Part 12: Next Repo Must-Add

### 12.1 Error Taxonomy Document

Before writing code, define the complete error taxonomy:

```yaml
# errors/taxonomy.yaml
categories:
  INPUT:     # E_INPUT_xxx — bad user inputs
    range: 001-099
    severity_default: ERROR
  FLEXURE:   # E_FLEXURE_xxx — flexure design issues
    range: 100-199
    severity_default: ERROR
  SHEAR:     # E_SHEAR_xxx — shear design issues
    range: 200-299
    severity_default: ERROR
  DETAILING: # E_DETAIL_xxx — detailing violations
    range: 300-399
    severity_default: WARNING
  COMPLIANCE: # E_COMPLY_xxx — code compliance
    range: 400-499
    severity_default: ERROR
```

### 12.2 Machine-Readable Error Catalog

```json
{
  "E_INPUT_001": {
    "category": "INPUT",
    "severity": "ERROR",
    "message_template": "{param_name} = {value} must be > {minimum}",
    "params": ["param_name", "value", "minimum"],
    "clause": null,
    "i18n_key": "error.input.must_be_positive"
  }
}
```

### 12.3 Consistent Exception Fields

```python
# Use SAME field names on both Exception and DesignError:
class StructuralError(Exception):
    code: str           # Same as DesignError.code
    severity: Severity  # Same enum
    message: str
    clause: str | None  # NOT "clause_ref" — consistent!
    details: dict
    suggestion: str | None
```

### 12.4 Day-1 Checklist for Next Repo Errors

- [ ] Define `errors/taxonomy.yaml` — error ranges per category
- [ ] Create `errors/catalog.json` — all error definitions (machine-readable)
- [ ] Use consistent field names (`clause` everywhere, not `clause_ref`)
- [ ] Make all `DesignError` fields required (no optional `recovery`)
- [ ] Add `structlog` for structured JSON logging
- [ ] Evaluate `returns.Result` for Rust-style error handling
- [ ] Use `ExceptionGroup` (Python 3.11+) for multi-error raising
- [ ] Write error message i18n support from day 1
- [ ] Set up error code auto-generation from catalog
- [ ] Add error frequency tracking (which errors occur most?)

---

## Part 13: Summary

| Concept | Purpose | Where Used | Key File |
|---------|---------|------------|----------|
| **`StructuralLibError`** | Base exception (4 fields) | All layers | `core/errors.py` |
| **`ValidationError`** | Bad inputs | Services boundary | `core/errors.py` |
| **`DimensionError`** | Dimension-specific | Codes layer | `core/errors.py` |
| **`DesignConstraintError`** | Infeasible design | Math results | `core/errors.py` |
| **`ComplianceError`** | Code violations | Compliance checks | `core/errors.py` |
| **`CalculationError`** | Numerical issues | Math layer | `core/errors.py` |
| **`DesignError` dataclass** | Collected warnings | Inside results | `core/errors.py` |
| **`Severity` enum** | ERROR/WARNING/INFO | All errors | `core/errors.py` |
| **`validate_dimensions()`** | Check b, d, D | Services | `core/validation.py` |
| **`validate_materials()`** | Check fck, fy | Services | `core/validation.py` |
| **Boundary validation** | Check at gate, trust inside | Architecture pattern | `services/` |
| **Error constants** | `E_INPUT_001`, etc. | All layers | `core/errors.py` |
| **`@clause` decorator** | IS 456 traceability | Codes layer | `codes/is456/` |

---

## 📎 References

- **Exception hierarchy:** `Python/structural_lib/core/errors.py`
- **Validation functions:** `Python/structural_lib/core/validation.py`
- **Plausibility checks:** `Python/structural_lib/services/common_api.py`
- **Clause decorator:** `Python/structural_lib/codes/is456/beam/flexure.py`
- **Dev rule U-1:** Never swallow exceptions silently
- **Dev rule U-2:** No `except Exception:` without specific handling

---

## What's Next?

**Day 11: Services Layer, API & Adapters** — Now that you understand errors and types, we'll explore the orchestration layer. How `design_beam_is456()` coordinates flexure, shear, and detailing. How `GenericCSVAdapter` maps 40+ messy column names to canonical parameters. How `beam_pipeline.py` runs multi-step batch designs. The services layer is where all the pieces come together.