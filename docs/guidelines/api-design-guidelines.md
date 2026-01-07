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

---

## 6. Documentation Standard

### 6.1 Google-Style Docstrings

**Rule:** All public functions MUST use Google-style docstrings with complete sections.

**Template sections (in order):**
1. **Summary** (1 line, <80 chars, imperative mood)
2. **Description** (2-4 sentences, optional for obvious functions)
3. **Args** (one per parameter with units, constraints, defaults)
4. **Returns** (structure, units, what the values mean)
5. **Raises** (all exceptions with trigger conditions)
6. **Example** (1-3 examples from simple to advanced)
7. **Note** (caveats, IS 456 clause references, optional)
8. **See Also** (related functions, optional)

```python
def calculate_development_length(
    bar_diameter_mm: float,
    concrete_grade: Literal['M15', 'M20', 'M25', 'M30', 'M35', 'M40'],
    *,
    stress_condition: Literal['tension', 'compression'] = 'tension'
) -> float:
    """Calculate development length per IS 456:2000 Cl. 26.2.1.

    Development length is the embedded length required to develop full
    tensile strength of reinforcement bar by bond stresses. This accounts
    for stress condition and concrete grade.

    Args:
        bar_diameter_mm: Nominal diameter of reinforcement bar in mm.
            Typical values: 10, 12, 16, 20, 25, 32 mm.
        concrete_grade: Concrete compressive strength grade per IS 456 Table 2.
            Common: M20 (residential), M25 (commercial), M30 (industrial).
        stress_condition: Whether bar is in tension or compression.
            Default: 'tension' (conservative, most common case).

    Returns:
        Development length in millimeters. Minimum value is 12 × bar_diameter_mm
        per IS 456 Cl. 26.2.1(a).

    Raises:
        ValidationError: If bar_diameter_mm not in [8, 10, 12, 16, 20, 25, 32, 40].
        ValidationError: If concrete_grade not in standard grades.

    Example:
        >>> # Simple case: 16mm bar in M25 concrete
        >>> ld = calculate_development_length(16, 'M25')
        >>> print(f"{ld:.0f} mm")
        752 mm

        >>> # Compression: 20mm bar in M30 concrete
        >>> ld = calculate_development_length(20, 'M30', stress_condition='compression')
        >>> print(f"{ld:.0f} mm")
        600 mm

    Note:
        Per IS 456:2000 Cl. 26.2.1:
        - Ld = φ × σs / (4 × τbd)
        - τbd from Table 21 (design bond stress)
        - Minimum Ld = 12φ for deformed bars

    See Also:
        calculate_anchorage_length: For hook/bend development
        calculate_lap_length: For splicing bars
    """
    ...
```

### 6.2 Documentation Quality Checklist

Before marking documentation complete, verify:

**Completeness (8 checks):**
- ✅ Summary line exists and is <80 characters
- ✅ All parameters documented with units
- ✅ Return value structure documented with units
- ✅ All possible exceptions documented
- ✅ At least one example provided
- ✅ Example is runnable (passes doctest or pytest)
- ✅ IS 456 clause references included (if applicable)
- ✅ Type hints present in signature

**Clarity (5 checks):**
- ✅ Parameter descriptions explain constraints (ranges, enum values)
- ✅ Units are explicit (mm, kN, MPa, not generic "number")
- ✅ Examples show realistic values (not foo/bar/baz)
- ✅ Error messages suggest typical values
- ✅ Technical terms defined on first use

**Discoverability (3 checks):**
- ✅ Function name is a verb (calculate_*, design_*, check_*)
- ✅ Related functions cross-referenced (See Also section)
- ✅ Module docstring explains what functions are available

### 6.3 Examples: The Three-Level Hierarchy

**Level 1: Hello World** (Dead simple, instant gratification)
```python
Example:
    >>> # Design 6m beam with 25 kN/m UDL
    >>> result = design_beam(span_mm=6000, load_kn_per_m=25)
    >>> print(f"Steel: {result.ast_required_mm2:.0f} mm²")
    Steel: 2145 mm²
```

**Level 2: Realistic** (Real project scenario, 80% of use cases)
```python
Example:
    >>> # Design beam for residential building
    >>> result = design_beam(
    ...     span_mm=6000,
    ...     load_kn_per_m=25,
    ...     width_mm=230,
    ...     depth_mm=450,
    ...     concrete_grade='M20',
    ...     steel_grade='Fe415'
    ... )
    >>> print(result.summary())
    Beam: 230×450 mm, Span: 6000 mm
    Steel: 4-#20 (1256 mm²)
    Stirrups: #8 @ 150 mm c/c
```

**Level 3: Advanced** (Edge case, expert usage)
```python
Example:
    >>> # Custom configuration for special case
    >>> config = BeamConfig(
    ...     concrete_grade='M30',
    ...     exposure='severe',
    ...     redistribution=True,
    ...     redistribution_factor=0.15
    ... )
    >>> result = design_beam_detailed(
    ...     span_mm=8000,
    ...     load_kn_per_m=35,
    ...     width_mm=300,
    ...     depth_mm=600,
    ...     config=config
    ... )
```

**When to use which level:**
- All functions: Level 1 (minimal complexity)
- Common functions: Levels 1+2 (realistic scenario)
- Complex functions: All 3 levels (guide users from simple to advanced)

### 6.4 Doctest Integration

**Rule:** Simple, deterministic examples SHOULD be runnable doctests. Complex examples with external dependencies SHOULD be manual.

```python
# ✅ GOOD: Simple calculation (perfect for doctest)
def calculate_area(width_mm: float, depth_mm: float) -> float:
    """Calculate rectangular area.

    Example:
        >>> calculate_area(230, 450)
        103500.0
    """
    return width_mm * depth_mm

# ✅ GOOD: Complex example (manual, not doctest)
def design_beam(...) -> BeamDesignResult:
    """Design beam.

    Example:
        # For runnable example, see examples/basic_beam_design.py
        result = design_beam(span_mm=6000, load_kn_per_m=25)
        assert result.is_adequate
    """
    ...
```

**Doctest directives for edge cases:**
```python
Example:
    >>> result = calculate_moment(1.5, 6.0)  # doctest: +ELLIPSIS
    67.5...

    >>> result = design_beam(...)  # doctest: +SKIP
    # Skipped: requires database connection
```

### 6.5 Module-Level Documentation

**Rule:** Every module MUST have a docstring explaining its purpose and listing key functions.

```python
"""Flexural design per IS 456:2000.

This module provides functions for designing reinforced concrete beam sections
in flexure (bending). Covers singly reinforced, doubly reinforced, and
T-beam sections per IS 456 clauses 36-39.

Key Functions:
    - design_singly_reinforced: Most common case (tension steel only)
    - design_doubly_reinforced: When Mu > Mu,lim (compression steel needed)
    - design_t_beam: For beams with monolithic slab
    - check_deflection: Span-to-depth ratio check (IS 456 Cl. 23.2)

Typical Usage:
    >>> from structural_lib.flexure import design_singly_reinforced
    >>> result = design_singly_reinforced(b_mm=230, d_mm=450, mu_kn_m=150, ...)

See Also:
    - shear: Shear design (stirrups, spacing)
    - detailing: Bar spacing, development length, hooks
    - serviceability: Deflection, crack width calculations
"""

# Module constants
MU_LIM_FACTOR = 0.138  # IS 456 Cl. 38.1 (for Fe415)
XU_MAX_FACTOR = 0.48   # IS 456 Cl. 38.1 (for Fe415)

# ... function definitions
```

**Package-level documentation** (`__init__.py`):
```python
"""structural_lib_is456 - IS 456:2000 beam design library.

Public API:
    Design Functions:
        - design_beam_is456: Complete beam design (all-in-one)
        - design_singly_reinforced: Flexure (tension steel only)
        - design_shear: Stirrup design

    Analysis Functions:
        - check_deflection: Span/depth ratio check
        - calculate_moment_capacity: Given section, find capacity

    Optimization:
        - optimize_bar_arrangement: Find optimal bar size/count
        - optimize_beam_cost: Minimize material cost

Quick Start:
    >>> from structural_lib import design_beam_is456
    >>> result = design_beam_is456(span_mm=6000, load_kn_per_m=25)

Documentation:
    - User Guide: https://docs.structural-lib.com/guide
    - API Reference: https://docs.structural-lib.com/api
    - Examples: https://github.com/user/repo/tree/main/examples
"""

__version__ = "0.15.0"
__all__ = [
    "design_beam_is456",
    "design_singly_reinforced",
    "design_shear",
    # ... all public functions
]
```

---

## 7. API Evolution

### 7.1 Semantic Versioning (SemVer)

**Rule:** Strictly follow SemVer `MAJOR.MINOR.PATCH` format.

```
MAJOR.MINOR.PATCH
  │     │     │
  │     │     └─ Bug fixes (backward compatible)
  │     └─────── New features (backward compatible)
  └───────────── Breaking changes (NOT backward compatible)
```

**Version bumping rules:**

| Change | Example | Version |
|--------|---------|---------|
| **Bug fix** | Fix calculation error in `calculate_moment` | 1.2.3 → 1.2.4 |
| **New feature** | Add `design_t_beam` function | 1.2.4 → 1.3.0 |
| **New optional param** | Add `exposure='moderate'` default | 1.3.0 → 1.3.1 |
| **Deprecate API** | Mark `calculate_steel()` deprecated | 1.3.1 → 1.4.0 |
| **Remove deprecated** | Delete `calculate_steel()` (warned since 1.4) | 1.9.0 → 2.0.0 |
| **Rename parameter** | `b_mm` → `width_mm` (breaking) | 1.9.0 → 2.0.0 |
| **Change return type** | Return `Result` instead of dict (breaking) | 1.9.0 → 2.0.0 |

**Pre-1.0 rules (current 0.15.0):**
- 0.x.0 → 0.x.y: Patches only (bug fixes)
- 0.x.y → 0.(x+1).0: Features OR breaking changes (more flexible)
- We SHOULD minimize breaks even in 0.x, but allowed

**Post-1.0 rules (future):**
- Strict SemVer: Breaking changes ONLY in major versions
- Deprecation period: Minimum 2 minor versions before removal
- Example: Deprecate in 1.4.0, remove in 2.0.0 (after 1.5, 1.6, 1.7, 1.8, 1.9)

### 7.2 Deprecation Process

**Rule:** Use the `@deprecated` decorator with clear migration guidance. Maintain deprecated APIs for at least 2 minor versions.

```python
from typing import TypeVar, Callable
import warnings
import functools

def deprecated(
    version: str,
    removal_version: str,
    replacement: str,
    instructions: str
) -> Callable:
    """Mark function as deprecated with migration guidance.

    Args:
        version: Version when deprecation added (e.g., '1.5.0')
        removal_version: Version when will be removed (e.g., '2.0.0')
        replacement: Name of replacement function
        instructions: How to migrate (one sentence)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__}() is deprecated since v{version} "
                f"and will be removed in v{removal_version}. "
                f"Use {replacement}() instead. {instructions}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage:
@deprecated(
    version='1.5.0',
    removal_version='2.0.0',
    replacement='calculate_reinforcement',
    instructions='Simply rename: calculate_steel() → calculate_reinforcement()'
)
def calculate_steel(b_mm: float, d_mm: float, mu: float) -> float:
    """Deprecated: Use calculate_reinforcement() instead."""
    return calculate_reinforcement(b_mm, d_mm, mu)
```

**Warning types:**
- `DeprecationWarning`: Function/parameter will be removed
- `FutureWarning`: Behavior will change (not removal)
- `PendingDeprecationWarning`: Will be deprecated soon (advance notice)

### 7.3 Backward Compatibility Strategies

**Strategy 1: Add optional parameters at the end**
```python
# v1.0: Original function
def design_beam(span_mm: float, load_kn: float) -> BeamResult:
    ...

# v1.5: Add optional parameter (backward compatible!)
def design_beam(
    span_mm: float,
    load_kn: float,
    exposure: str = 'moderate'  # ← New param with default
) -> BeamResult:
    ...

# Old code still works:
result = design_beam(6000, 25)  # ✅ Still valid
```

**Strategy 2: Parameter aliases (accept both old and new names)**
```python
def design_beam(
    width_mm: float = None,    # New name (preferred)
    b_mm: float = None,        # Old name (deprecated)
) -> BeamResult:
    # Accept both, warn on old
    if b_mm is not None:
        warnings.warn("b_mm is deprecated, use width_mm", DeprecationWarning)
        if width_mm is None:
            width_mm = b_mm

    if width_mm is None:
        raise ValueError("width_mm is required")

    # Implementation uses width_mm
    ...
```

**Strategy 3: Result object compatibility layers**
```python
# v1.0: Returned dict
def calculate_moment(...) -> dict:
    return {'moment': 150.0, 'capacity': 200.0}

# v2.0: Return dataclass, but support dict-like access
@dataclass
class MomentResult:
    moment_knm: float
    capacity_knm: float

    # Backward compat: allow dict-like access
    def __getitem__(self, key: str):
        warnings.warn("Dict access deprecated, use attributes", DeprecationWarning)
        if key == 'moment':
            return self.moment_knm
        if key == 'capacity':
            return self.capacity_knm
        raise KeyError(key)

# Old code works with warning:
result = calculate_moment(...)
m = result['moment']  # ⚠️ Warning, but works

# New code uses attributes:
m = result.moment_knm  # ✅ Preferred
```

### 7.4 Breaking Changes Policy

**Rule:** Breaking changes are ONLY allowed in major version releases (1.0 → 2.0). They must be batched (not scattered across minors).

**When breaking changes are justified:**
1. ✅ **Security**: Old API has vulnerability
2. ✅ **Correctness**: Old API produces wrong results
3. ✅ **Usability**: Old API causes frequent user errors
4. ✅ **Maintainability**: Old API blocks critical features

**When to AVOID breaking:**
1. ❌ "Nice to have" refactoring
2. ❌ Personal preference ("I like X better than Y")
3. ❌ Small improvements (cost > benefit)
4. ❌ If compatibility layer is feasible

**Breaking change process:**
1. **Announce** (v1.5): Add deprecation warning
2. **Maintain both** (v1.6-1.9): Old API warns, new API available
3. **Release candidate** (v2.0-rc): Test with removed API
4. **Remove** (v2.0): Old API gone, migration guide published

### 7.5 Version Communication

**CHANGELOG.md template:**
```markdown
# Changelog

## [2.0.0] - 2026-03-15

### ⚠️ Breaking Changes
- Removed `calculate_steel()` (deprecated since 1.5.0)
  - Use `calculate_reinforcement()` instead
  - Migration: Just rename the function
- Changed `design_beam()` return type from dict to `BeamResult`
  - Old: `result['ast']` → New: `result.ast_mm2`
  - See migration guide: docs/migration/v1-to-v2.md

### Added
- New `design_t_beam()` for T-sections
- Added `exposure` parameter to all design functions

### Changed
- `b_mm` parameter renamed to `width_mm` (old name still works with warning)

### Fixed
- Fixed development length calculation for compression bars
- Corrected stirrup spacing limits per IS 456 Cl. 26.5.1.5

## [1.9.0] - 2026-02-01

### Deprecated
- `calculate_steel()` → Use `calculate_reinforcement()` (will remove in v2.0)

### Added
- New `optimize_beam_cost()` function

### Fixed
- Fixed rounding error in moment capacity calculation
```

**GitHub Release description:**
```markdown
# v2.0.0 - Major Release

## 🎉 Highlights
- Complete beam design API redesign
- 30% faster calculations
- Type-safe result objects

## ⚠️ Migration Required

This is a BREAKING release. **Read the migration guide**:
https://docs.structural-lib.com/migration/v1-to-v2

### Quick Migration (90% of users):
1. Rename `calculate_steel()` → `calculate_reinforcement()`
2. Change result access: `result['ast']` → `result.ast_mm2`
3. Run tests, fix deprecation warnings

### What's New
- 🏗️ T-beam design support
- 🎨 Exposure classification parameter
- ⚡ NumPy vectorization for batch operations

## 📦 Installation
```bash
pip install structural-lib-is456==2.0.0
```

## 📚 Documentation
- [Migration Guide](docs/migration/v1-to-v2.md)
- [API Reference](https://docs.structural-lib.com/api/v2)
- [Examples](examples/)
```

---

## Next Steps

This is **step 2/4** of the unified guidelines document. Remaining sections:

- **Step 3**: Sections 8-9 (Engineering Domain Patterns, UX & Discoverability)
- **Step 4**: Section 10-11 + Appendices (Implementation Guide, PR Checklist, Templates, Anti-Patterns)

**Current Progress:** ~1500 lines created (sections 1-7 complete)
**Target:** ~2000 lines total (75% complete)

---

## 8. Engineering Domain Patterns

### 8.1 Unit Handling Philosophy

**Rule:** Units MUST be explicit in parameter/field names. Never rely on documentation alone.

**Three strategies (in order of preference):**

**Strategy 1: Unit suffix naming** (RECOMMENDED - our choice)
```python
def calculate_moment(
    load_kn: float,        # Clear: kilonewtons
    span_m: float,         # Clear: meters
    factor: float = 1.5    # Dimensionless (no suffix)
) -> float:
    """Returns moment in kN·m."""
    return load_kn * span_m ** 2 * factor / 8
```

**Strategy 2: Type-based units** (ADVANCED - consider for v2.0)
```python
from pint import UnitRegistry
ureg = UnitRegistry()

def calculate_moment(
    load: ureg.Quantity,   # Must have units
    span: ureg.Quantity
) -> ureg.Quantity:
    """Requires pint.Quantity with units."""
    moment = load * span ** 2 / 8
    return moment.to('kN*m')

# Usage:
m = calculate_moment(load=25 * ureg.kN, span=6 * ureg.m)
print(f"{m:.2f}")  # 112.50 kilonewton * meter
```

**Strategy 3: Unit enum parameter** (VERBOSE - avoid)
```python
def calculate_moment(
    load: float,
    span: float,
    load_unit: Literal['kN', 'N', 'kip'] = 'kN',
    span_unit: Literal['m', 'mm', 'ft'] = 'm'
) -> float:
    # Too many parameters, error-prone
    ...
```

**Our standard units:**
- Distance: `_mm` (millimeters - IS 456 standard)
- Force: `_kn` (kilonewtons)
- Stress: `_mpa` (megapascals = N/mm²)
- Moment: `_knm` (kilonewton-meters)
- Area: `_mm2` (square millimeters)
- Angle: `_deg` (degrees)
- Ratio: `_ratio` or `_percent`
- Dimensionless: no suffix

### 8.2 IS 456 Terminology Mapping

**Rule:** Use IS 456 notation where engineers expect it, but make it IDE-friendly.

| IS 456 Symbol | Our Parameter Name | Rationale |
|---------------|-------------------|-----------|
| b | `width_mm` or `b_mm` | Both acceptable; width is clearer for beginners |
| d | `depth_mm` or `d_mm` | Both acceptable; depth clearer |
| D | `overall_depth_mm` | Explicit (vs effective depth) |
| f<sub>ck</sub> | `concrete_grade` (string) | Use 'M20', 'M25' not raw MPa |
| f<sub>y</sub> | `steel_grade` (string) | Use 'Fe415', 'Fe500' |
| A<sub>st</sub> | `ast_mm2` or `steel_area_mm2` | Both acceptable |
| M<sub>u</sub> | `moment_knm` or `mu_knm` | Both acceptable |
| V<sub>u</sub> | `shear_kn` or `vu_kn` | Both acceptable |
| τ<sub>bd</sub> | `bond_stress_mpa` | Explicit (no Greek) |
| l<sub>d</sub> | `dev_length_mm` | Common abbreviation |
| φ | `bar_diameter_mm` | Explicit (no Greek) |

**Examples:**
```python
# ✅ GOOD: Mix of textbook notation and clarity
def design_singly_reinforced(
    b_mm: float,              # Engineers recognize "b"
    d_mm: float,              # Engineers recognize "d"
    mu_knm: float,            # Engineers recognize "Mu"
    *,
    concrete_grade: str,      # Clearer than "fck_mpa"
    steel_grade: str          # Clearer than "fy_mpa"
) -> FlexureResult:
    ...

# ✅ ALSO GOOD: Fully explicit (for beginners)
def design_singly_reinforced(
    width_mm: float,
    effective_depth_mm: float,
    moment_knm: float,
    *,
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415'
) -> FlexureResult:
    ...

# ❌ BAD: Too cryptic
def design(b, d, mu, fck, fy):  # What are these?
    ...

# ❌ BAD: Inconsistent notation
def design(width, d, bending_moment, f_ck, steel_fy):  # Mixed styles
    ...
```

### 8.3 Material Grade Representation

**Rule:** Use string grades ('M20', 'Fe415') not raw MPa values. This matches how engineers think and prevents confusion.

```python
# ✅ EXCELLENT: String grades with validation
from typing import Literal

def calculate_capacity(
    *,
    concrete_grade: Literal['M15', 'M20', 'M25', 'M30', 'M35', 'M40', 'M45', 'M50'],
    steel_grade: Literal['Fe250', 'Fe415', 'Fe500', 'Fe550']
) -> float:
    """
    Calculate capacity.

    Args:
        concrete_grade: IS 456 concrete grade (Table 2).
            M20 = 20 MPa characteristic strength at 28 days.
        steel_grade: IS 456 steel grade (Cl. 6.2).
            Fe415 = 415 MPa yield strength.
    """
    # Internal: convert to MPa if needed
    fck_mpa = float(concrete_grade[1:])  # 'M20' → 20.0
    fy_mpa = float(steel_grade[2:])      # 'Fe415' → 415.0
    ...

# ✅ GOOD: Expose both interfaces
def calculate_capacity_from_grades(
    concrete_grade: str,
    steel_grade: str
) -> float:
    """User-friendly interface with grade strings."""
    fck = float(concrete_grade[1:])
    fy = float(steel_grade[2:])
    return calculate_capacity_from_strengths(fck, fy)

def calculate_capacity_from_strengths(
    fck_mpa: float,
    fy_mpa: float
) -> float:
    """Low-level interface with raw MPa (for advanced users)."""
    ...

# ❌ BAD: Only MPa interface (user must look up values)
def calculate_capacity(fck: float, fy: float) -> float:
    """fck: concrete strength in MPa (what's M20? Must look up!)"""
    ...
```

**Grade validation:**
```python
CONCRETE_GRADES = {
    'M15': 15.0, 'M20': 20.0, 'M25': 25.0, 'M30': 30.0,
    'M35': 35.0, 'M40': 40.0, 'M45': 45.0, 'M50': 50.0
}

STEEL_GRADES = {
    'Fe250': 250.0, 'Fe415': 415.0, 'Fe500': 500.0, 'Fe550': 550.0
}

def validate_concrete_grade(grade: str) -> float:
    """Validate and convert concrete grade to MPa."""
    if grade not in CONCRETE_GRADES:
        raise ValidationError(
            f"Invalid concrete grade '{grade}'. "
            f"Must be one of: {', '.join(CONCRETE_GRADES.keys())}. "
            f"Common: M20 (residential), M25 (commercial), M30 (industrial)."
        )
    return CONCRETE_GRADES[grade]
```

### 8.4 Code Clause References

**Rule:** Always reference IS 456 clauses in docstrings and error messages. This enables engineers to verify calculations.

```python
def calculate_xu_max(
    depth_mm: float,
    steel_grade: str = 'Fe415'
) -> float:
    """Calculate maximum neutral axis depth per IS 456:2000 Cl. 38.1.

    Ensures under-reinforced section (ductile failure mode) by limiting
    neutral axis depth xu to xu,max = 0.48d for Fe415 (Cl. 38.1a).

    Args:
        depth_mm: Effective depth of section (mm).
        steel_grade: Steel grade per IS 456 Table 19.
            Fe415: xu,max = 0.48d (Cl. 38.1a)
            Fe500: xu,max = 0.46d (Cl. 38.1b)

    Returns:
        Maximum neutral axis depth in mm per IS 456 Cl. 38.1.

    Note:
        IS 456:2000 Cl. 38.1:
        "For ensuring ductile failure, the neutral axis depth xu
        shall not exceed xu,max given by:
        - For Fe415: xu,max = 0.48d
        - For Fe500: xu,max = 0.46d"

    See Also:
        IS 456:2000 Cl. 38.1 (Limiting values for xu/d)
        SP:16-1980 Cl. 5.3 (Under-reinforced sections)
    """
    xu_max_factors = {'Fe250': 0.53, 'Fe415': 0.48, 'Fe500': 0.46, 'Fe550': 0.44}
    if steel_grade not in xu_max_factors:
        raise ValidationError(f"Unknown steel grade: {steel_grade}")

    return xu_max_factors[steel_grade] * depth_mm
```

**In error messages:**
```python
if xu > xu_max:
    raise DesignError(
        f"Section is over-reinforced (brittle failure mode). "
        f"Neutral axis xu ({xu:.1f} mm) exceeds xu,max ({xu_max:.1f} mm). "
        f"Per IS 456:2000 Cl. 38.1, xu ≤ {xu_max/depth_mm:.2f}d for {steel_grade}. "
        f"Solutions: (1) Increase depth to ≥{xu/0.48:.0f} mm, or "
        f"(2) Use compression steel (doubly reinforced section)."
    )
```

### 8.5 Engineering Workflow Integration

**Rule:** Design APIs for real engineering workflows, not just isolated calculations.

**Common workflows:**

**Workflow 1: Iterative design** (try different sections)
```python
# ✅ GOOD: Stateless functions enable easy iteration
sections = [
    (230, 400), (230, 450), (230, 500),
    (300, 400), (300, 450), (300, 500)
]

for width, depth in sections:
    result = design_beam(
        span_mm=6000,
        load_kn_per_m=25,
        width_mm=width,
        depth_mm=depth
    )
    if result.is_adequate:
        print(f"✅ {width}×{depth}: OK")
        break
    else:
        print(f"❌ {width}×{depth}: {result.failure_reason}")
```

**Workflow 2: Batch processing** (analyze many beams)
```python
# ✅ GOOD: Vectorized or batch API
from structural_lib import run_job_is456

results = run_job_is456([
    {'id': 'B1', 'span': 6000, 'load': 25, 'width': 230, 'depth': 450},
    {'id': 'B2', 'span': 7000, 'load': 30, 'width': 230, 'depth': 500},
    {'id': 'B3', 'span': 5000, 'load': 20, 'width': 230, 'depth': 400},
    # ... 100 more beams
])

# Export to Excel/CSV for review
results_df = pd.DataFrame([r.to_dict() for r in results])
results_df.to_excel('beam_designs.xlsx')
```

**Workflow 3: Integration with analysis software** (ETABS, SAP2000)
```python
# ✅ GOOD: Import from common formats
from structural_lib import import_from_etabs

beams = import_from_etabs('analysis.e2k')  # Parse ETABS export

for beam in beams:
    result = design_beam(
        span_mm=beam.length,
        moment_knm=beam.max_moment,
        shear_kn=beam.max_shear,
        width_mm=beam.width,
        depth_mm=beam.depth
    )
    beam.design_result = result

# Export back to CAD
export_to_dxf(beams, 'beam_details.dxf')
```

---

## 9. UX & Discoverability

### 9.1 The "Pit of Success" Pattern

**Principle:** Make correct usage the easiest path. Make mistakes hard or impossible.

```python
# ✅ EXCELLENT: Pit of success (hard to use wrong)
def design_beam(
    span_mm: float,           # Required, explicit units
    load_kn_per_m: float,     # Required, explicit units
    *,                        # Force keyword-only after this
    width_mm: float,          # Explicit units
    depth_mm: float,          # Explicit units
    concrete_grade: Literal['M15', 'M20', 'M25', 'M30'] = 'M20',  # Enum catches typos
    steel_grade: Literal['Fe250', 'Fe415', 'Fe500'] = 'Fe415',
    validate: bool = True     # Defaults to safe option
) -> BeamDesignResult:        # Returns structured object, not tuple
    """Design beam per IS 456:2000."""
    if validate:
        # Eagerly validate at entry
        if span_mm <= 0:
            raise ValidationError(f"span_mm must be positive, got {span_mm}")
        if load_kn_per_m <= 0:
            raise ValidationError(f"load_kn_per_m must be positive, got {load_kn_per_m}")
        # ... more validation

    # Calculation code
    ...

    return BeamDesignResult(
        is_adequate=True,
        ast_required_mm2=1250.5,
        # ... more fields
    )

# Usage: IDE autocomplete shows all options!
result = design_beam(
    span_mm=6000,
    load_kn_per_m=25,
    width_mm=230,
    depth_mm=450,
    concrete_grade='M20',  # ← IDE shows: 'M15', 'M20', 'M25', 'M30'
)

# ❌ BAD: Easy to misuse
def design(s, l, w, d, c='M20', st='Fe415'):  # What are s, l, w, d?
    # No validation
    return (1250.5, True, 'OK')  # Mystery tuple
```

### 9.2 Progressive Disclosure

**Principle:** Simple tasks should be simple. Complex tasks should be possible.

**Three levels of API:**

**Level 1: Simple (80% of users)**
```python
# Minimal parameters, sensible defaults
from structural_lib import design_beam_is456

result = design_beam_is456(
    span_mm=6000,
    load_kn_per_m=25
)
# Uses defaults: 230×450 section, M20 concrete, Fe415 steel, moderate exposure
```

**Level 2: Intermediate (15% of users)**
```python
# Common customizations
result = design_beam_is456(
    span_mm=6000,
    load_kn_per_m=25,
    width_mm=300,         # Custom section
    depth_mm=500,
    concrete_grade='M25', # Higher grade
    exposure='severe'     # Coastal environment
)
```

**Level 3: Advanced (5% of users)**
```python
# Full control with config object
from structural_lib import design_beam_detailed, BeamConfig

config = BeamConfig(
    concrete_grade='M30',
    steel_grade='Fe500',
    exposure='very_severe',
    cover_mm=40,
    redistribution=True,
    redistribution_factor=0.10,
    phi_compression=0.75,
    phi_tension=0.87,
    use_exact_formula=True,
    optimization_enabled=False
)

result = design_beam_detailed(
    span_mm=6000,
    load_kn_per_m=25,
    width_mm=300,
    depth_mm=500,
    config=config
)
```

### 9.3 IDE Autocomplete Optimization

**Rule:** Optimize for IDE discoverability. Most users explore via autocomplete, not docs.

**Techniques:**

**1. Module organization**
```python
# ✅ GOOD: Hierarchical imports
from structural_lib.design import beams, columns, slabs
from structural_lib.analysis import moment, shear, deflection
from structural_lib.detailing import bar_bending, anchorage

# User types: structural_lib. [autocomplete shows: design, analysis, detailing]
# User types: structural_lib.design. [shows: beams, columns, slabs]
# User types: structural_lib.design.beams. [shows: design_singly_reinforced, design_doubly_reinforced, ...]

# ❌ BAD: Flat namespace
from structural_lib import (
    design_beam, design_column, design_slab,
    calculate_moment, calculate_shear, calculate_deflection,
    # ... 50 more functions in one namespace
)
```

**2. Consistent naming prefixes**
```python
# ✅ GOOD: Verb prefixes group related functions
calculate_moment_capacity()
calculate_shear_capacity()
calculate_deflection()
calculate_crack_width()

design_singly_reinforced()
design_doubly_reinforced()
design_t_beam()

check_minimum_steel()
check_maximum_steel()
check_spacing_limits()

# User types: "calc" [autocomplete shows all calculate_* functions]
# User types: "design" [shows all design_* functions]
# User types: "check" [shows all check_* functions]
```

**3. Docstring first line**
```python
def calculate_moment_capacity(...) -> float:
    """Calculate moment capacity of reinforced concrete section.  ← Shows in autocomplete!

    Detailed explanation here...
    """
    ...

# ❌ BAD: Vague first line
def calculate_moment_capacity(...) -> float:
    """
    This function does calculations.  ← Not helpful in autocomplete!

    Actually calculates moment capacity (user has to read further)
    """
    ...
```

### 9.4 Error Messages as UI

**Rule:** Error messages are user interface. Treat them with the same care as function signatures.

**Three-part error message structure:**

1. **What went wrong** (diagnosis)
2. **Why it's a problem** (context)
3. **How to fix it** (actionable guidance)

```python
# ✅ EXCELLENT: Complete error message
def design_beam(width_mm: float, depth_mm: float, ...):
    if depth_mm < width_mm:
        raise ValidationError(
            # 1. WHAT: Specific diagnosis
            f"Beam depth ({depth_mm} mm) is less than width ({width_mm} mm). "
            # 2. WHY: Context
            f"For rectangular beams, depth should be ≥ width to resist bending efficiently. "
            # 3. HOW: Actionable fix
            f"Typical depth/width ratios: 1.5-2.5. Try depth={width_mm * 2:.0f} mm."
        )

    if width_mm < 200:
        raise ValidationError(
            f"Beam width ({width_mm} mm) is below minimum. "
            f"IS 456:2000 Cl. 26.5.1.1 requires width ≥ 200 mm for RC beams. "
            f"Increase width to ≥ 200 mm."
        )

# ❌ BAD: Vague error (user doesn't know what to do)
def design_beam(width_mm: float, depth_mm: float, ...):
    if depth_mm < width_mm:
        raise ValueError("Invalid dimensions")  # What's invalid? How to fix?

    if width_mm < 200:
        raise ValueError("Width too small")  # How small? What's the limit?
```

**Error message checklist:**
- ✅ Include parameter name and actual value
- ✅ Include expected range or constraint
- ✅ Include units (mm, kN, MPa)
- ✅ Reference IS 456 clause if applicable
- ✅ Suggest typical/common values
- ✅ Explain *why* it's a problem (not just *what*)
- ❌ Don't use jargon without explanation
- ❌ Don't just say "invalid" without specifics

### 9.5 Example-Driven Learning

**Rule:** Provide runnable examples at three levels of complexity in docstrings and examples/ directory.

**In docstrings:**
```python
def design_singly_reinforced(...) -> FlexureResult:
    """Design singly reinforced section.

    Example:
        >>> # Level 1: Minimal (Hello World)
        >>> result = design_singly_reinforced(width_mm=230, depth_mm=450, moment_knm=150)
        >>> print(f"Steel required: {result.ast_required_mm2:.0f} mm²")
        Steel required: 1256 mm²

        >>> # Level 2: Realistic (Real project)
        >>> result = design_singly_reinforced(
        ...     width_mm=230,
        ...     depth_mm=450,
        ...     moment_knm=150,
        ...     concrete_grade='M25',
        ...     steel_grade='Fe415',
        ...     cover_mm=30
        ... )
        >>> print(result.summary())
        Section: 230×450 mm
        Steel: 3-#20 + 1-#16 (1256 mm²)
        Adequate: ✅ Yes

        >>> # Level 3: Advanced (Edge case)
        >>> try:
        ...     result = design_singly_reinforced(width_mm=230, depth_mm=300, moment_knm=250)
        ... except DesignError as e:
        ...     print(f"Design failed: {e}")
        Design failed: Section is over-reinforced. Increase depth to ≥450 mm.
    """
    ...
```

**In examples/ directory:**
```python
# examples/01_hello_world.py
"""Minimal beam design example."""
from structural_lib import design_beam_is456

result = design_beam_is456(span_mm=6000, load_kn_per_m=25)
print(f"Steel area: {result.ast_mm2:.0f} mm²")

# examples/02_residential_building.py
"""Realistic residential building beam."""
from structural_lib import design_beam_is456

result = design_beam_is456(
    span_mm=6000,
    load_kn_per_m=25,
    width_mm=230,
    depth_mm=450,
    concrete_grade='M20',
    exposure='moderate'
)
print(result.summary())
result.export_dxf('beam_detail.dxf')

# examples/03_advanced_optimization.py
"""Advanced: Optimize beam dimensions for minimum cost."""
from structural_lib import optimize_beam_cost

result = optimize_beam_cost(
    span_mm=6000,
    load_kn_per_m=25,
    constraints={'max_depth_mm': 500, 'deflection_limit': 'l/250'},
    material_costs={'concrete_per_m3': 5000, 'steel_per_kg': 60}
)
print(f"Optimal: {result.width_mm}×{result.depth_mm} mm")
print(f"Cost: ₹{result.total_cost:.2f}")
```

---

## Next Steps

This is **step 3/4** of the unified guidelines document. Final section:

- **Step 4**: Sections 10-11 + Appendices (Implementation Guide, PR Checklist, Templates, Anti-Patterns)

**Current Progress:** ~1850 lines created (sections 1-9 complete)
**Target:** ~2100 lines total (88% complete)
