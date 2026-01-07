# API Design Guidelines

**Status:** DRAFT → IN REVIEW → APPROVED
**Version:** 1.0
**Last Updated:** 2026-01-07
**Owner:** ARCHITECT
**Synthesizes:** TASK-200 through TASK-207 research (~9300 lines)

---

## Document Purpose

This document consolidates all Phase 1 and Phase 2 API research into a **single, actionable reference** for developing structural_engineering_lib APIs. Use this as the "north star" for all API design decisions.

**What This Document Provides:**
1. **Unified design principles** from 8 research documents
2. **Concrete code templates** for common patterns
3. **Decision frameworks** for design choices
4. **PR review checklist** (30+ validation points)
5. **Migration strategies** for existing code

**Who Should Read This:**
- Developers implementing new features
- Reviewers checking PRs for API quality
- Architects making design decisions
- New contributors learning the codebase

---

## Executive Summary

### The 5 Core Principles

Every API design decision must satisfy these principles (in priority order):

1. **🎯 Engineering Domain Fit**
   APIs must match how structural engineers think and work. Use domain terminology (moment, shear, stirrups), not CS abstractions. Units must be explicit. Calculations must be traceable to IS 456 clauses.

2. **🛡️ Safety Through Design**
   Prevent errors at design time, not runtime. Use type hints, keyword-only parameters, immutable results, and clear error messages. Invalid states should be unrepresentable.

3. **📖 Self-Documenting**
   Code should be readable without documentation. Parameter names include units (`span_mm` not `span`), result objects have named fields (not tuples), functions are verbs (`calculate_moment` not `moment`).

4. **🔄 Evolution-Friendly**
   APIs must evolve without breaking users. Add optional parameters at the end, use result objects (not tuples), provide 2-version deprecation warnings, batch breaking changes in major releases.

5. **⚡ IDE-First Experience**
   Optimize for autocomplete and type checkers. Use keyword-only params for >3 args, dataclasses over dicts, `Literal` types for choices, comprehensive docstrings with examples.

### Key Decisions Summary

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **Return values** | Dataclasses (frozen) | Discoverability, type safety, extensibility |
| **Parameters** | Keyword-only if >3 | Prevents order errors, IDE-friendly |
| **Units** | Suffix naming (`_mm`, `_kn`) | Explicit, prevents confusion |
| **Defaults** | Only for optional params | Type system expresses intent |
| **Errors** | Custom exceptions + context | Clear diagnosis, actionable messages |
| **Documentation** | Google-style docstrings | Readable, IDE-compatible, executable examples |
| **Versioning** | Semantic versioning | Breaking changes only in majors |
| **Validation** | Explicit `.validate()` | User controls when to check |

---

## Table of Contents

1. [Function Signatures](#1-function-signatures)
2. [Parameter Design](#2-parameter-design)
3. [Type Hints & Annotations](#3-type-hints--annotations)
4. [Result Objects](#4-result-objects)
5. [Error Handling](#5-error-handling)
6. [Documentation Standard](#6-documentation-standard)
7. [API Evolution](#7-api-evolution)
8. [Engineering Domain Patterns](#8-engineering-domain-patterns)
9. [UX & Discoverability](#9-ux--discoverability)
10. [Implementation Guide](#10-implementation-guide)
11. [PR Review Checklist](#11-pr-review-checklist)

**Appendices:**
- A. Code Templates (10 common patterns)
- B. Decision Trees (5 design choices)
- C. Migration Examples
- D. Anti-Patterns Catalog

---

## 1. Function Signatures

### 1.1 The Three-Parameter Rule

**Rule:** Functions with ≤3 parameters MAY use positional arguments. Functions with >3 parameters MUST use keyword-only arguments (enforced by `*`).

**Why:** Based on Miller's Law (7±2 items in working memory). Beyond 3 parameters, users cannot remember order without looking up documentation. Type checkers and IDEs work best with explicit keyword arguments.

```python
# ✅ GOOD: 3 or fewer parameters (positional OK)
def calculate_moment(load_kn: float, span_m: float, factor: float = 1.5) -> float:
    """Calculate bending moment."""
    return load_kn * span_m ** 2 * factor / 8

# ✅ EXCELLENT: More than 3 parameters (keyword-only enforced)
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,  # ← Force keyword-only after this
    width_mm: float,
    depth_mm: float,
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415',
    exposure: str = 'moderate'
) -> BeamDesignResult:
    """Design beam with many parameters."""
    ...

# ❌ BAD: 7 positional parameters (impossible to remember)
def design_beam(span, load, width, depth, concrete, steel, exposure):
    ...  # Which parameter is which? Must check docs every time!
```

**When to use positional:**
- ✅ Simple calculations with obvious order: `calculate_area(width, height)`
- ✅ Mathematical operations: `add(a, b)`
- ✅ Domain-obvious ordering: `calculate_moment(load, span)`

**When to require keywords:**
- ✅ Configuration parameters: `width_mm=`, `concrete_grade=`
- ✅ Similar types: `width_mm=`, `depth_mm=` (both floats, easy to swap)
- ✅ Optional parameters with defaults
- ✅ More than 3 total parameters

### 1.2 Parameter Ordering

**Rule:** Order parameters from most important to least important, grouping by purpose.

**Standard Order:**
1. **Primary inputs** (what you're calculating with)
2. **Geometry** (dimensions)
3. **Materials** (concrete, steel grades)
4. **Configuration** (exposure, support conditions)
5. **Behavioral flags** (validate, strict_mode)

```python
# ✅ GOOD: Logical ordering
def design_flexure(
    # 1. Primary inputs (what we're designing for)
    moment_knm: float,
    # 2. Geometry
    width_mm: float,
    depth_mm: float,
    *,
    # 3. Materials
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415',
    # 4. Configuration
    exposure: str = 'moderate',
    cover_mm: float = 25.0,
    # 5. Behavioral
    validate: bool = True
) -> FlexureResult:
    ...

# ❌ BAD: Random ordering
def design_flexure(validate, concrete_grade, moment, cover, depth, exposure, width, steel_grade):
    ...  # No logical grouping, hard to remember
```

### 1.3 Naming Conventions

**Rule:** Function names must be verbs, parameter names must include units, result fields must be nouns.

```python
# ✅ GOOD: Clear, unambiguous names
def calculate_reinforcement(
    moment_knm: float,      # Unit suffix: kilonewton-meters
    width_mm: float,        # Unit suffix: millimeters
    depth_mm: float,
    *,
    concrete_grade: str,    # Descriptive: not just "grade" or "fck"
    steel_grade: str
) -> ReinforcementResult:  # Noun: describes what it is
    ...

result = calculate_reinforcement(...)  # Verb: describes action
area = result.area_mm2                 # Noun + unit: what it represents

# ❌ BAD: Ambiguous names
def reinforcement(m, b, d, c, s):  # What are these? Must check docs
    return (area, count, dia)      # Which is which?

x = reinforcement(150, 230, 450, 'M20', 'Fe415')  # Mystery values
```

**Unit Suffix Standard:**
- Distance: `_mm`, `_m`, `_cm`
- Force: `_kn`, `_n`, `_mpa`, `_nmm2` (N/mm²)
- Moment: `_knm`, `_nmm`
- Area: `_mm2`, `_m2`
- Ratio: `_ratio`, `_percent`
- Angle: `_deg`, `_rad`
- No suffix: dimensionless (counts, IDs, flags)

---

## 2. Parameter Design

### 2.1 Required vs Optional

**Rule:** Required parameters have no default value. Optional parameters have sensible IS 456 defaults with clause references.

```python
# ✅ GOOD: Clear intent
def calculate_development_length(
    bar_diameter_mm: float,              # Required (no default)
    concrete_grade: str,                 # Required (no default)
    *,
    stress_condition: str = 'tension',   # Optional (common case)
    anchorage_condition: str = 'normal', # Optional (common case)
    validate: bool = True                # Optional (sensible default)
) -> float:
    """
    Calculate development length per IS 456:2000 Cl. 26.2.1.

    Defaults assume:
    - stress_condition='tension' (most common, conservative)
    - anchorage_condition='normal' (most common)
    """
    ...

# ❌ BAD: Required parameter with None default
def calculate_development_length(
    bar_diameter_mm: float = None,  # Type checker allows None, runtime error!
    concrete_grade: str = None
) -> float:
    if bar_diameter_mm is None:
        raise ValueError("bar_diameter_mm required")  # Should have been caught by type checker
    ...
```

**When to provide defaults:**
- ✅ IS 456 has a standard value (e.g., load factor 1.5)
- ✅ 80%+ of users use the same value
- ✅ Default is conservative (safer side)

**When to require explicit:**
- ✅ No universal standard (varies by project)
- ✅ Value is critical to safety (exposure class, seismic zone)
- ✅ Wrong default causes silent errors

### 2.2 Parameter Validation

**Rule:** Validate inputs eagerly at function entry. Provide clear error messages with expected ranges and units.

```python
# ✅ GOOD: Comprehensive validation
def calculate_moment_capacity(
    width_mm: float,
    depth_mm: float,
    *,
    concrete_grade: str = 'M20'
) -> float:
    """Calculate moment capacity."""

    # Validate at entry (fail fast)
    if not (100 <= width_mm <= 2000):
        raise DesignError(
            f"width_mm must be 100-2000 mm, got {width_mm} mm. "
            f"Typical beam widths: 230mm, 300mm, 400mm."
        )

    if not (150 <= depth_mm <= 4000):
        raise DesignError(
            f"depth_mm must be 150-4000 mm, got {depth_mm} mm. "
            f"Depth should be ≥width for beams."
        )

    if concrete_grade not in ('M15', 'M20', 'M25', 'M30', 'M35', 'M40'):
        raise DesignError(
            f"concrete_grade must be M15-M40, got '{concrete_grade}'. "
            f"Common grades: M20 (residential), M25 (commercial), M30 (industrial)."
        )

    # Now proceed with calculation
    ...

# ❌ BAD: No validation (garbage in, garbage out)
def calculate_moment_capacity(width, depth, concrete_grade='M20'):
    # Proceeds with width=-100, produces nonsense result
    ...
```

**Validation checklist:**
1. ✅ Range checks (min/max with engineering rationale)
2. ✅ Unit mentions in error message
3. ✅ Typical values suggestion
4. ✅ Relationships between parameters (depth ≥ width for beams)
5. ✅ Enum validation (concrete grade, steel grade, exposure)

### 2.3 Configuration Objects (When You Have Too Many Parameters)

**Rule:** If >7 parameters even with keyword-only, consider a configuration object. But keep common cases simple.

```python
# ✅ GOOD: Hybrid approach (simple case + config object)
from dataclasses import dataclass

@dataclass(frozen=True)
class BeamConfig:
    """Configuration for beam design."""
    concrete_grade: str = 'M20'
    steel_grade: str = 'Fe415'
    exposure: str = 'moderate'
    cover_mm: float = 25.0
    redistribution: bool = False
    phi_compression: float = 0.8  # IS 456 Cl. 53.2
    phi_tension: float = 0.87     # IS 456 Cl. 53.2
    # ... 10 more parameters

# Simple case (common usage)
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    width_mm: float,
    depth_mm: float
) -> BeamDesignResult:
    """Design with default IS 456 assumptions."""
    return design_beam_detailed(
        span_mm, load_kn_per_m, width_mm, depth_mm,
        config=BeamConfig()  # All defaults
    )

# Advanced case (custom configuration)
def design_beam_detailed(
    span_mm: float,
    load_kn_per_m: float,
    width_mm: float,
    depth_mm: float,
    *,
    config: BeamConfig = BeamConfig()
) -> BeamDesignResult:
    """Design with custom configuration."""
    ...

# Usage:
# Simple (95% of users)
result = design_beam(6000, 25, 230, 450)

# Advanced (5% of users)
custom_config = BeamConfig(
    concrete_grade='M30',
    exposure='severe',
    redistribution=True
)
result = design_beam_detailed(6000, 25, 230, 450, config=custom_config)
```

---

## 3. Type Hints & Annotations

### 3.1 Basic Type Annotations

**Rule:** All public functions MUST have type hints for parameters and return values. Use precise types, not `Any`.

```python
from typing import Optional, Union, Literal

# ✅ GOOD: Complete type hints
def calculate_ast_required(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,
    concrete_grade: Literal['M15', 'M20', 'M25', 'M30', 'M35', 'M40'],
    steel_grade: Literal['Fe250', 'Fe415', 'Fe500', 'Fe550']
) -> float:
    """Calculate required steel area (mm²)."""
    ...

# ❌ BAD: No type hints (IDE can't help)
def calculate_ast_required(moment, width, depth, concrete_grade, steel_grade):
    ...

# ❌ BAD: Imprecise types
def calculate_ast_required(
    moment: float,
    width: float,
    depth: float,
    concrete_grade: str,  # Any string? 'M20' or 'Grade20' or 'twenty'?
    steel_grade: str
) -> float:
    ...
```

### 3.2 Literal Types for Choices

**Rule:** Use `Literal` types for string parameters with fixed choices. This enables IDE autocomplete and catches typos at type-check time.

```python
from typing import Literal

# ✅ EXCELLENT: IDE shows options, catches typos
def design_shear(
    shear_kn: float,
    *,
    stirrup_type: Literal['2-legged', '4-legged', '6-legged'] = '2-legged',
    stirrup_diameter: Literal[6, 8, 10, 12, 16] = 8
) -> ShearDesignResult:
    """
    Design shear reinforcement.

    stirrup_type: Number of legs (typically 2 for simple beams)
    stirrup_diameter: Bar diameter in mm (typically 8mm)
    """
    ...

# Usage: IDE autocomplete shows the 3 options!
result = design_shear(150, stirrup_type='2-legged')  # ✅
result = design_shear(150, stirrup_type='3-legged')  # ❌ Type error! Not in Literal

# ❌ BAD: Plain string (no autocomplete, typos pass type check)
def design_shear(shear_kn: float, *, stirrup_type: str = '2-legged'):
    ...

result = design_shear(150, stirrup_type='2-leged')  # Typo! Passes type check, fails at runtime
```

### 3.3 Optional vs Union

**Rule:** Use `Optional[T]` for "may be None". Use `Union[A, B]` for "either A or B". Never use `Union[T, None]` (use `Optional[T]` instead).

```python
from typing import Optional, Union

# ✅ GOOD: Optional for nullable
def calculate_capacity(
    width_mm: float,
    depth_mm: float,
    ast_provided_mm2: Optional[float] = None  # If None, will calculate minimum
) -> float:
    if ast_provided_mm2 is None:
        ast_provided_mm2 = calculate_minimum_steel(width_mm, depth_mm)
    ...

# ✅ GOOD: Union for alternatives
def load_beam_data(
    source: Union[str, dict]  # Either filename (str) or data dict
) -> BeamData:
    if isinstance(source, str):
        # Load from file
        ...
    else:
        # Parse dict
        ...

# ❌ BAD: Union[T, None] instead of Optional[T]
def calculate_capacity(ast_provided_mm2: Union[float, None] = None):
    ...  # Use Optional[float] instead
```

### 3.4 Return Type Precision

**Rule:** Return concrete types, not generic containers. Use dataclasses for structured results.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class FlexureResult:
    """Result of flexural design."""
    ast_required_mm2: float
    ast_provided_mm2: float
    area_ratio_percent: float
    is_under_reinforced: bool
    moment_capacity_knm: float
    neutral_axis_depth_mm: float

# ✅ GOOD: Returns concrete type
def design_flexure(...) -> FlexureResult:
    ...
    return FlexureResult(
        ast_required_mm2=ast_req,
        ast_provided_mm2=ast_prov,
        area_ratio_percent=100 * ast_prov / (width_mm * depth_mm),
        is_under_reinforced=xu < xu_max,
        moment_capacity_knm=mu_capacity,
        neutral_axis_depth_mm=xu
    )

# ❌ BAD: Returns generic dict (no autocomplete)
def design_flexure(...) -> dict:
    return {
        'ast_req': ast_req,
        'ast_prov': ast_prov,
        # ... what keys exist? IDE doesn't know!
    }

# ❌ BAD: Returns tuple (must remember order)
def design_flexure(...) -> tuple:
    return (ast_req, ast_prov, ratio, under_reinforced, capacity, xu)
    # Which is which? Must check docs!
```

---

## 4. Result Objects

### 4.1 Dataclasses Over Dicts

**Rule:** NEVER return bare dicts or tuples. Always use frozen dataclasses for structured results.

```python
from dataclasses import dataclass

# ✅ EXCELLENT: Self-documenting result object
@dataclass(frozen=True)
class ReinforcementResult:
    """Result of reinforcement calculation.

    All areas in mm², all dimensions in mm.
    """
    area_required_mm2: float
    area_provided_mm2: float
    bar_count: int
    bar_diameter_mm: int
    spacing_mm: float
    # Self-validation
    def __post_init__(self):
        if self.area_provided_mm2 < self.area_required_mm2:
            raise DesignError(
                f"Provided area ({self.area_provided_mm2:.1f} mm²) < "
                f"required ({self.area_required_mm2:.1f} mm²)"
            )

def calculate_reinforcement(...) -> ReinforcementResult:
    ...
    return ReinforcementResult(
        area_required_mm2=ast_req,
        area_provided_mm2=ast_prov,
        bar_count=n_bars,
        bar_diameter_mm=dia,
        spacing_mm=spacing
    )

# Usage: IDE autocomplete works!
result = calculate_reinforcement(...)
print(f"Required: {result.area_required_mm2} mm²")  # ✅ Discoverable
print(f"Bars: {result.bar_count}-#{result.bar_diameter_mm}")

# ❌ CATASTROPHIC: Dict return (no autocomplete, no type safety)
def calculate_reinforcement(...) -> dict:
    return {
        'ast_req': ast_req,     # What keys exist?
        'ast_prov': ast_prov,   # What units?
        'n': n_bars,            # What is 'n'?
        'dia': dia              # Typo-prone access
    }

result = calculate_reinforcement(...)
print(result['ast_req'])   # ✅ Works
print(result['ast_reqd'])  # ❌ KeyError at runtime! (Typo)
print(result.ast_req)      # ❌ AttributeError (not a real attribute)

# ❌ CATASTROPHIC: Tuple return (must remember order)
def calculate_reinforcement(...) -> tuple:
    return (ast_req, ast_prov, n_bars, dia, spacing)

ast, n, dia, spacing, prov = calculate_reinforcement(...)  # ❌ Wrong order!
# Runtime: nonsense results, hard to debug
```

**Why frozen:**
- Results represent completed calculations (facts, not mutable state)
- Immutability enables safe caching and sharing
- Prevents accidental modification: `result.area_mm2 = 999  # Error!`

### 4.2 Essential Methods

**Rule:** Result dataclasses SHOULD provide these methods for common operations:

```python
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class BeamDesignResult:
    """Complete beam design result."""
    moment_capacity_knm: float
    shear_capacity_kn: float
    flexure: FlexureResult
    shear: ShearResult
    detailing: DetailingResult

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return asdict(self)

    def summary(self) -> str:
        """Human-readable summary for reports."""
        return f"""
Beam Design Summary:
  Moment Capacity: {self.moment_capacity_knm:.2f} kN·m
  Shear Capacity:  {self.shear_capacity_kn:.2f} kN
  Main Steel:      {self.flexure.bar_count}-#{self.flexure.bar_diameter_mm}
  Stirrups:        #{self.shear.stirrup_diameter_mm} @ {self.shear.spacing_mm:.0f} mm c/c
"""

    def validate(self) -> None:
        """Check internal consistency."""
        if self.moment_capacity_knm <= 0:
            raise ValueError("Moment capacity must be positive")
        if self.shear_capacity_kn <= 0:
            raise ValueError("Shear capacity must be positive")
        # Delegate to nested results
        self.flexure.validate()
        self.shear.validate()
```

**When to add methods:**
- ✅ `to_dict()` - always (for JSON, pandas, Excel export)
- ✅ `summary()` - for user-facing results (reports, CLI output)
- ✅ `validate()` - for complex results with invariants
- ✅ Domain methods: `is_adequate()`, `utilization_ratio()`, `safety_factor()`
- ❌ Don't add computation in result objects (that belongs in functions)

---

## 5. Error Handling

### 5.1 Exception Hierarchy

**Rule:** Use a 3-level exception hierarchy. Never raise bare `ValueError` or `Exception`.

```python
# Base exception (catch all library errors)
class StructuralLibError(Exception):
    """Base exception for structural_lib."""
    pass

# Second level (error categories)
class DesignError(StructuralLibError):
    """Design requirements not met (e.g., over-reinforced section)."""
    pass

class ValidationError(StructuralLibError):
    """Invalid input parameters."""
    pass

class ConvergenceError(StructuralLibError):
    """Iterative calculation did not converge."""
    pass

# Third level (specific errors, optional)
class OverReinforcedError(DesignError):
    """Section is over-reinforced (brittle failure mode)."""
    pass

class InsufficientDepthError(DesignError):
    """Beam depth insufficient for required moment capacity."""
    pass
```

**Usage:**
```python
# ✅ GOOD: Specific exception with context
def design_flexure(...) -> FlexureResult:
    xu = calculate_neutral_axis(...)
    xu_max = calculate_xu_max(...)

    if xu > xu_max:
        raise OverReinforcedError(
            f"Section is over-reinforced: xu ({xu:.1f} mm) > xu_max ({xu_max:.1f} mm). "
            f"Increase depth to {xu / 0.48:.0f} mm or reduce moment."
        )
    ...

# User can catch specifically
try:
    result = design_flexure(...)
except OverReinforcedError as e:
    print(f"Need deeper beam: {e}")
except DesignError as e:
    print(f"Design failed: {e}")
except StructuralLibError as e:
    print(f"Library error: {e}")

# ❌ BAD: Generic exception (can't distinguish error types)
def design_flexure(...):
    if xu > xu_max:
        raise ValueError("Over-reinforced")  # What does this mean? How to fix?
```

### 5.2 Error Message Standard

**Rule:** Error messages MUST follow the "Three Questions Framework":

1. **What went wrong?** (Diagnosis)
2. **Why is this a problem?** (Context)
3. **How to fix it?** (Actionable suggestion)

```python
# ✅ EXCELLENT: Complete error message
def calculate_development_length(bar_diameter_mm: float, ...) -> float:
    if not (8 <= bar_diameter_mm <= 40):
        raise ValidationError(
            # 1. WHAT: Specific diagnosis
            f"bar_diameter_mm must be 8-40 mm, got {bar_diameter_mm} mm. "
            # 2. WHY: Context
            f"IS 456:2000 Cl. 26.2.1 covers bars from 8mm to 40mm diameter. "
            # 3. HOW: Actionable fix
            f"Common sizes: 10mm, 12mm, 16mm, 20mm, 25mm, 32mm."
        )
    ...

# ✅ GOOD: Engineering-focused message
def check_deflection(...):
    if actual_deflection > limit:
        raise DesignError(
            f"Deflection check failed: "
            f"Actual ({actual_deflection:.2f} mm) > Limit ({limit:.2f} mm). "
            f"Increase depth to {suggested_depth:.0f} mm or reduce span/load."
        )

# ❌ BAD: Vague message (no actionable guidance)
def calculate_development_length(bar_diameter_mm: float, ...) -> float:
    if bar_diameter_mm > 40:
        raise ValueError("Invalid diameter")  # What's invalid? How to fix?
```

**Error message checklist:**
- ✅ Include parameter name and actual value
- ✅ Include expected range with units
- ✅ Reference IS 456 clause if applicable
- ✅ Suggest typical/common values
- ✅ Suggest how to fix (increase depth, reduce load, etc.)
- ❌ Don't use jargon without explanation
- ❌ Don't just say "invalid" without details

---

## Next Steps

This is **step 1/4** of the unified guidelines document. Remaining sections:

- **Step 2**: Sections 6-7 (Documentation Standard, API Evolution)
- **Step 3**: Sections 8-9 (Engineering Domain Patterns, UX & Discoverability)
- **Step 4**: Section 10-11 + Appendices (Implementation Guide, PR Checklist, Templates, Anti-Patterns)

**Current Progress:** ~1050 lines created
**Target:** ~2000 lines total (50% complete)
