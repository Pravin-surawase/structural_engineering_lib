# Function Signature Design Standard

**Type:** Guideline
**Audience:** Developers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-07
**Last Updated:** 2026-01-13

---

**Version:** 1.0
**Owner:** RESEARCHER
**Related:** [API Design Guidelines](api-design-guidelines.md), [Professional API Patterns](../research/professional-api-patterns.md), [UX Patterns](../research/ux-patterns-for-technical-apis.md)

---

## Purpose

This document defines the standard for function signatures in the structural_engineering_lib to ensure:
- **Discoverability**: IDE autocomplete and type checkers work effectively
- **Clarity**: No ambiguity about parameter purpose, order, or units
- **Safety**: Prevent common usage errors through type system and naming
- **Consistency**: Predictable patterns across all modules

**Target Audience**: All developers contributing to the library (Python or VBA)

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Parameter Ordering](#2-parameter-ordering)
3. [Keyword-Only Parameters](#3-keyword-only-parameters)
4. [Type Hints](#4-type-hints)
5. [Default Values](#5-default-values)
6. [Unit Suffix Naming](#6-unit-suffix-naming)
7. [Validation Parameters](#7-validation-parameters)
8. [Special Cases](#8-special-cases)
9. [Anti-Patterns](#9-anti-patterns)
10. [Migration Guide](#10-migration-guide)
11. [Examples](#11-examples)

---

## 1. Core Principles

### 1.1 The "Three-Parameter Rule"

**Rule:** Functions with ≤3 parameters MAY use positional arguments. Functions with >3 parameters MUST use keyword-only arguments.

**Rationale:**
- Based on Miller's Law (7±2 items in working memory)
- Beyond 3 parameters, users cannot remember order without documentation lookup
- Type checkers and IDEs work best with explicit keyword arguments

**Example:**
```python
# ✅ GOOD: 3 or fewer parameters (positional OK)
def calculate_moment(load_kn: float, span_m: float, factor: float = 1.5) -> float:
    """Simple calculation with obvious parameter order."""
    return load_kn * span_m ** 2 * factor / 8

# ✅ GOOD: More than 3 parameters (keyword-only enforced)
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,  # Force keyword-only after this point
    width_mm: float,
    depth_mm: float,
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415',
    exposure: str = 'moderate'
) -> DesignResult:
    """Complex function with many parameters."""
    ...

# ❌ BAD: 7 positional parameters (impossible to remember order)
def design_beam(span, load, width, depth, concrete, steel, exposure):
    ...
```

### 1.2 Required vs Optional Paradigm

**Rule:** Parameters MUST be categorized clearly:
- **Required**: No default value, user must provide
- **Optional**: Has sensible default, user may override

**Anti-Pattern:** Using `None` as default for required parameters:
```python
# ❌ BAD: Required parameter with None default
def calculate_moment(load: float = None, span: float = None) -> float:
    if load is None or span is None:
        raise ValueError("load and span are required")
    ...

# ✅ GOOD: Required parameters have no default
def calculate_moment(load: float, span: float) -> float:
    ...

# ✅ GOOD: Optional parameters have meaningful defaults
def calculate_moment(
    load: float,
    span: float,
    load_factor: float = 1.5  # IS 456 Cl. 36.4
) -> float:
    ...
```

### 1.3 Explicit Over Implicit

**Rule:** No "magic" behavior based on parameter absence. If a parameter affects behavior significantly, make it explicit.

```python
# ❌ BAD: Hidden behavior change
def design_beam(span, load, steel_grade='Fe415'):
    if steel_grade == 'Fe500':
        # Completely different calculation path
        return design_with_high_strength_steel(span, load)
    ...

# ✅ GOOD: Explicit mode parameter
def design_beam(
    span: float,
    load: float,
    *,
    steel_grade: Literal['Fe415', 'Fe500', 'Fe550'],
    high_strength_mode: bool = False  # Explicit flag
) -> DesignResult:
    ...
```

---

## 2. Parameter Ordering

### 2.1 Standard Order (Mandatory)

All functions MUST follow this parameter order:

```python
def function_name(
    # 1. Primary inputs (required, positional-or-keyword)
    primary_input_1: Type,
    primary_input_2: Type,

    # 2. Secondary inputs (required, positional-or-keyword)
    secondary_input: Type,

    # 3. Keyword-only separator (if >3 total params)
    *,

    # 4. Configuration (optional, keyword-only)
    config_param: Type = default,

    # 5. Behavior flags (optional, keyword-only)
    flag: bool = False,

    # 6. Advanced options (optional, keyword-only)
    advanced_option: Type = default
) -> ReturnType:
    ...
```

### 2.2 Primary Input Identification

**Rule:** Primary inputs are those WITHOUT which the function has no purpose.

**Decision Tree:**
1. Can the calculation be performed without this parameter? → No → **Primary**
2. Does this parameter change the fundamental nature of the result? → Yes → **Primary**
3. Is this a refinement or optimization setting? → Yes → **Configuration/Advanced**

**Examples:**

```python
# Beam design: Primary inputs are span, load, geometry
def design_beam_flexure(
    span_mm: float,           # PRIMARY: defines problem
    moment_knm: float,        # PRIMARY: defines problem
    width_mm: float,          # PRIMARY: defines geometry
    depth_mm: float,          # PRIMARY: defines geometry
    *,
    concrete_grade: str = 'M20',    # CONFIGURATION: material choice
    steel_grade: str = 'Fe415',     # CONFIGURATION: material choice
    cover_mm: float = 25,           # CONFIGURATION: detailing
    exposure: str = 'moderate'      # CONFIGURATION: durability
) -> FlexureResult:
    ...

# Shear design: Primary inputs are shear force, section properties
def design_beam_shear(
    shear_force_kn: float,    # PRIMARY: load
    width_mm: float,          # PRIMARY: geometry
    depth_mm: float,          # PRIMARY: geometry
    *,
    concrete_grade: str = 'M20',
    stirrup_grade: str = 'Fe415',
    max_spacing_mm: float = None  # Optional override
) -> ShearResult:
    ...
```

### 2.3 Parameter Grouping

**Rule:** For functions with 5+ configuration parameters, consider parameter objects.

```python
# ❌ BAD: Flat parameter list (8 config params)
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,
    width_mm: float = 230,
    depth_mm: float = 450,
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415',
    cover_mm: float = 25,
    exposure: str = 'moderate',
    fire_rating_minutes: int = 60,
    seismic_zone: str = None
) -> DesignResult:
    ...

# ✅ GOOD: Grouped into logical objects
from dataclasses import dataclass

@dataclass
class BeamGeometry:
    width_mm: float = 230
    depth_mm: float = 450
    cover_mm: float = 25

@dataclass
class DesignCriteria:
    concrete_grade: str = 'M20'
    steel_grade: str = 'Fe415'
    exposure: str = 'moderate'
    fire_rating_minutes: int = 60
    seismic_zone: Optional[str] = None

def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,
    geometry: BeamGeometry = None,
    criteria: DesignCriteria = None
) -> DesignResult:
    geometry = geometry or BeamGeometry()
    criteria = criteria or DesignCriteria()
    ...
```

---

## 3. Keyword-Only Parameters

### 3.1 When to Use `*` Separator

**Mandatory:** Use `*` separator when:
- Total parameters > 3
- Any parameter could be confused with another (same type, similar meaning)
- Function is part of public API (even if only 2-3 params now)

**Example:**
```python
# ✅ GOOD: Public API with clear intent
def calculate_reinforcement_area(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,  # Everything after this is keyword-only
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415'
) -> float:
    ...

# Usage (clear and unambiguous):
area = calculate_reinforcement_area(
    150,      # moment_knm
    230,      # width_mm
    450,      # depth_mm
    concrete_grade='M25'  # Must use keyword
)
```

### 3.2 Positional-Only Parameters (Python 3.8+)

**Guideline:** Use `/` separator for low-level functions where parameter names might change but position is stable.

```python
# ✅ GOOD: Mathematical functions with canonical order
def calculate_stress(force: float, area: float, /) -> float:
    """
    Calculate stress = force / area.

    Parameters are positional-only because:
    - Canonical mathematical order (stress = F/A)
    - Parameter names might change (force vs load, area vs section)
    - Position is more stable than names
    """
    return force / area

# Usage:
stress = calculate_stress(1000, 0.1)  # Clear from context
```

**Anti-Pattern:** Don't use `/` for domain functions:
```python
# ❌ BAD: Domain function with positional-only (loses clarity)
def design_beam(span: float, load: float, width: float, depth: float, /) -> DesignResult:
    ...

# Usage is unclear:
result = design_beam(5000, 10, 230, 450)  # Which is which?
```

---

## 4. Type Hints

### 4.1 Mandatory Type Hints (Non-Negotiable)

**Rule:** ALL public function parameters and return types MUST have type hints. No exceptions.

```python
# ❌ BAD: No type hints
def calculate_moment(load, span, factor=1.5):
    return load * span ** 2 * factor / 8

# ✅ GOOD: Complete type hints
def calculate_moment(
    load_kn: float,
    span_m: float,
    factor: float = 1.5
) -> float:
    """
    Calculate mid-span moment for simply supported beam.

    Args:
        load_kn: Uniformly distributed load in kN/m
        span_m: Clear span in meters
        factor: Load factor (default: 1.5 per IS 456)

    Returns:
        Mid-span moment in kN-m
    """
    return load_kn * span_m ** 2 * factor / 8
```

### 4.2 Use `Literal` for Enumerated Choices

**Rule:** When parameter accepts specific string/int values, use `Literal` to enable IDE autocomplete.

```python
from typing import Literal

# ✅ EXCELLENT: IDE shows all valid options
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,
    concrete_grade: Literal['M20', 'M25', 'M30', 'M35', 'M40'] = 'M20',
    steel_grade: Literal['Fe415', 'Fe500', 'Fe550'] = 'Fe415',
    exposure: Literal['mild', 'moderate', 'severe', 'very_severe', 'extreme'] = 'moderate'
) -> DesignResult:
    ...

# When user types: design_beam(5000, 10, concrete_grade='<cursor>
# IDE shows: 'M20' | 'M25' | 'M30' | 'M35' | 'M40'
```

### 4.3 Use `Optional` Correctly

**Rule:** `Optional[T]` means "T or None". Only use when `None` is a valid input.

```python
# ✅ GOOD: None means "calculate default"
def design_stirrups(
    shear_force_kn: float,
    *,
    max_spacing_mm: Optional[float] = None  # None → use code default
) -> StirrupResult:
    if max_spacing_mm is None:
        max_spacing_mm = min(0.75 * effective_depth, 300)  # IS 456 Cl. 26.5.1.5
    ...

# ❌ BAD: None has no semantic meaning (just use default value)
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,
    concrete_grade: Optional[str] = None  # Why None? Just use default!
) -> DesignResult:
    if concrete_grade is None:
        concrete_grade = 'M20'
    ...

# ✅ GOOD: Direct default
def design_beam(
    span_mm: float,
    load_kn_per_m: float,
    *,
    concrete_grade: str = 'M20'  # Clear default
) -> DesignResult:
    ...
```

### 4.4 Use NewType for Semantic Types

**Advanced:** For large projects, create semantic types for units.

```python
from typing import NewType

# Define semantic types
Millimeters = NewType('Millimeters', float)
Kilonewtons = NewType('Kilonewtons', float)
Megapascals = NewType('Megapascals', float)

def design_beam(
    span: Millimeters,
    load: Kilonewtons,
    *,
    concrete_strength: Megapascals = Megapascals(20.0)
) -> DesignResult:
    ...

# Usage (explicit unit conversion):
result = design_beam(
    span=Millimeters(5000),
    load=Kilonewtons(10.0),
    concrete_strength=Megapascals(25.0)
)
```

**Trade-off:** More verbose, but eliminates unit confusion entirely.

---

## 5. Default Values

### 5.1 Safe Defaults Only

**Rule:** Default values MUST be the most conservative or most common choice.

**Priority Order:**
1. **Code default** (from IS 456, SP:16) - highest priority
2. **Industry standard** (e.g., M20 concrete, Fe415 steel)
3. **Conservative value** (e.g., higher load factor, stricter tolerance)

```python
# ✅ GOOD: Conservative defaults from IS 456
def design_beam_flexure(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,
    concrete_grade: str = 'M20',      # Minimum grade for RC (IS 456 Cl. 5.1)
    steel_grade: str = 'Fe415',       # Most common in India
    cover_mm: float = 25,             # Minimum for moderate exposure (IS 456 Cl. 26.4)
    exposure: str = 'moderate',       # Most common condition
    load_factor_dead: float = 1.5,    # IS 456 Cl. 36.4.1
    load_factor_live: float = 1.5     # IS 456 Cl. 36.4.1
) -> FlexureResult:
    ...
```

### 5.2 Never Use Mutable Defaults

**Critical:** Never use mutable objects (list, dict) as default values.

```python
# ❌ CATASTROPHIC BUG: Shared mutable default
def add_load(
    beam: Beam,
    loads: list = []  # DANGER! Same list shared across all calls
) -> None:
    loads.append(beam)

# ✅ CORRECT: Use None + create new list
def add_load(
    beam: Beam,
    loads: Optional[list] = None
) -> None:
    if loads is None:
        loads = []
    loads.append(beam)

# ✅ BETTER: Make immutable or require explicit passing
def add_load(
    beam: Beam,
    loads: list  # Required, no default
) -> None:
    loads.append(beam)
```

### 5.3 Document Default Source

**Rule:** For defaults from codes/standards, include clause reference in docstring.

```python
def calculate_development_length(
    bar_diameter_mm: float,
    concrete_grade: str,
    steel_grade: str,
    *,
    stress_ratio: float = 0.87,  # IS 456 Cl. 26.2.1 (design stress)
    k_factor: float = 1.0        # IS 456 Cl. 26.2.1 (type of steel)
) -> float:
    """
    Calculate development length per IS 456 Cl. 26.2.1.

    Args:
        bar_diameter_mm: Nominal diameter of reinforcement bar
        concrete_grade: Concrete grade (M20, M25, etc.)
        steel_grade: Steel grade (Fe415, Fe500, Fe550)
        stress_ratio: Ratio of design stress to characteristic strength
                      (default: 0.87 per IS 456 Cl. 26.2.1)
        k_factor: Factor for steel type (1.0 for Fe415, 1.25 for Fe500)

    Returns:
        Development length in mm
    """
    ...
```

---

## 6. Unit Suffix Naming

### 6.1 Mandatory Unit Suffixes

**Rule:** All dimensional parameters MUST have unit suffixes. No exceptions for public API.

**Standard Suffixes:**

| Dimension | Suffix | Example |
|-----------|--------|---------|
| Length | `_mm` | `span_mm`, `depth_mm`, `cover_mm` |
| Force | `_kn` | `load_kn`, `shear_kn` |
| Moment | `_knm` | `moment_knm`, `mu_knm` |
| Stress | `_mpa` | `fck_mpa`, `fy_mpa` |
| Area | `_mm2` | `area_mm2`, `ast_mm2` |
| Force per length | `_kn_per_m` | `load_kn_per_m` |
| Mass | `_kg` | `weight_kg` |
| Time | `_sec`, `_min`, `_hr` | `duration_sec` |

```python
# ✅ EXCELLENT: Crystal clear units
def calculate_flexural_capacity(
    width_mm: float,
    depth_mm: float,
    ast_mm2: float,
    fck_mpa: float,
    fy_mpa: float
) -> float:  # Returns moment in kN-m (document in docstring)
    """
    Calculate flexural capacity per IS 456 Cl. 38.1.

    Returns:
        Moment capacity in kN-m
    """
    ...

# ❌ BAD: Ambiguous units (mm? m? inches?)
def calculate_flexural_capacity(
    width: float,
    depth: float,
    ast: float,
    fck: float,
    fy: float
) -> float:
    ...
```

### 6.2 Dimensionless Parameters

**Rule:** Dimensionless parameters (ratios, factors, counts) don't need suffixes but should be clear from name.

```python
# ✅ GOOD: Clear dimensionless names
def calculate_reinforcement(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,
    load_factor: float = 1.5,        # Dimensionless multiplier
    steel_ratio_min: float = 0.0015, # Dimensionless ratio (Ast/bd)
    bar_count: int = 3,              # Integer count
    ductility_class: str = 'high'    # Categorical
) -> ReinforcementResult:
    ...
```

### 6.3 Internal Calculations

**Rule:** Internal calculations use consistent units (mm, N, N-mm). Convert at function boundaries.

```python
def design_beam_is456(
    span_mm: float,          # User provides mm
    load_kn_per_m: float,    # User provides kN/m
    *,
    width_mm: float = 230,
    depth_mm: float = 450
) -> DesignResult:
    """
    Design beam per IS 456.

    All calculations internally use: mm, N, N-mm
    """
    # Convert to internal units at entry
    load_n_per_mm = load_kn_per_m * 1000 / 1000  # kN/m → N/mm

    # Internal calculations in mm, N, N-mm
    moment_nmm = (load_n_per_mm * span_mm ** 2) / 8

    # Convert to user units at exit
    return DesignResult(
        moment_capacity_knm=moment_nmm / 1e6,  # N-mm → kN-m
        ...
    )
```

---

## 7. Validation Parameters

### 7.1 `validate` Flag Pattern

**Rule:** For functions that may be called in batch/optimization loops, provide `validate` flag.

```python
def calculate_reinforcement_area(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415',
    validate: bool = True  # Disable for performance in trusted loops
) -> float:
    """
    Calculate required reinforcement area.

    Args:
        validate: If True, validate all inputs (default).
                  Set False only when inputs are pre-validated
                  (e.g., in optimization loops).

    Raises:
        InputError: If validate=True and inputs are invalid
    """
    if validate:
        if moment_knm <= 0:
            raise InputError("Moment must be positive")
        if width_mm <= 0 or depth_mm <= 0:
            raise InputError("Dimensions must be positive")
        # ... more validation

    # Calculation (assumes valid inputs if validate=False)
    ...
```

**Usage:**
```python
# Normal usage: validation enabled
area = calculate_reinforcement_area(150, 230, 450)

# Optimization loop: validation disabled for performance
for depth in range(200, 600, 10):
    area = calculate_reinforcement_area(
        150, 230, depth,
        validate=False  # Skip validation (already validated range)
    )
```

### 7.2 `strict` Mode Pattern

**Rule:** For compliance checks, provide `strict` mode to escalate warnings to errors.

```python
def check_deflection(
    calculated_deflection_mm: float,
    limit_mm: float,
    *,
    strict: bool = False  # If True, warnings become errors
) -> ComplianceResult:
    """
    Check deflection compliance per IS 456 Cl. 23.2.

    Args:
        strict: If True, treat warnings as failures.
                If False (default), only hard limits cause failure.
    """
    ratio = calculated_deflection_mm / limit_mm

    if ratio > 1.0:
        # Hard failure: exceeds absolute limit
        return ComplianceResult(
            passed=False,
            message=f"Deflection {calculated_deflection_mm:.1f}mm exceeds limit {limit_mm:.1f}mm"
        )
    elif ratio > 0.95:
        # Soft warning: close to limit
        if strict:
            return ComplianceResult(
                passed=False,
                message=f"Deflection {calculated_deflection_mm:.1f}mm too close to limit (strict mode)"
            )
        else:
            return ComplianceResult(
                passed=True,
                warning=f"Deflection {calculated_deflection_mm:.1f}mm is 95% of limit"
            )
    else:
        return ComplianceResult(passed=True)
```

---

## 8. Special Cases

### 8.1 Builder Functions

For complex configuration, provide builder-style functions.

```python
from __future__ import annotations  # For self-referencing type hints

class BeamDesignBuilder:
    """Fluent builder for beam design configuration."""

    def __init__(self) -> None:
        self._span_mm: Optional[float] = None
        self._load_kn_per_m: Optional[float] = None
        self._geometry: BeamGeometry = BeamGeometry()
        self._materials: Materials = Materials()

    def with_span(self, span_mm: float) -> BeamDesignBuilder:
        """Set beam span in millimeters."""
        self._span_mm = span_mm
        return self  # Return self for chaining

    def with_load(self, load_kn_per_m: float) -> BeamDesignBuilder:
        """Set uniformly distributed load in kN/m."""
        self._load_kn_per_m = load_kn_per_m
        return self

    def with_rectangular_section(
        self,
        width_mm: float,
        depth_mm: float,
        cover_mm: float = 25
    ) -> BeamDesignBuilder:
        """Configure rectangular cross-section."""
        self._geometry = BeamGeometry(width_mm, depth_mm, cover_mm)
        return self

    def design(self) -> DesignResult:
        """Execute design and return result."""
        if self._span_mm is None or self._load_kn_per_m is None:
            raise ValueError("Span and load are required")

        return design_beam_is456(
            self._span_mm,
            self._load_kn_per_m,
            geometry=self._geometry,
            materials=self._materials
        )

# Usage:
result = (BeamDesignBuilder()
    .with_span(5000)
    .with_load(10.0)
    .with_rectangular_section(width_mm=230, depth_mm=450)
    .design()
)
```

### 8.2 Batch Processing Functions

**Pattern:** Accept `List[Input]` and return `List[Result]` or `BatchResult`.

```python
from typing import List

def design_beam_batch(
    inputs: List[BeamInput],
    *,
    parallel: bool = False,       # Enable parallel processing
    progress_callback: Optional[Callable[[int, int], None]] = None,
    stop_on_error: bool = False   # If True, stop on first error
) -> BatchDesignResult:
    """
    Design multiple beams in batch.

    Args:
        inputs: List of beam input specifications
        parallel: If True, use multiprocessing for speedup
        progress_callback: Optional callback(current, total) for progress updates
        stop_on_error: If True, raise exception on first failure.
                       If False (default), continue and collect all errors.

    Returns:
        BatchDesignResult with successful/failed designs
    """
    result = BatchDesignResult()

    for i, beam_input in enumerate(inputs):
        if progress_callback:
            progress_callback(i + 1, len(inputs))

        try:
            design = design_beam_is456(**beam_input.dict())
            result.successful[beam_input.id] = design
        except Exception as e:
            if stop_on_error:
                raise
            result.failed[beam_input.id] = e

    return result
```

### 8.3 Context Manager Functions

**Pattern:** For resource management or temporary state changes.

```python
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def error_handling_mode(
    mode: Literal['raise', 'warn', 'ignore']
) -> Iterator[None]:
    """
    Temporarily change error handling mode.

    Args:
        mode: How to handle errors:
              - 'raise': Raise exceptions (default)
              - 'warn': Log warnings but continue
              - 'ignore': Silent operation

    Example:
        >>> with error_handling_mode('warn'):
        ...     design_beam(...)  # Invalid inputs → warning instead of error
    """
    old_mode = get_error_mode()
    set_error_mode(mode)
    try:
        yield
    finally:
        set_error_mode(old_mode)
```

---

## 9. Anti-Patterns

### 9.1 Avoid Boolean Flags

**Problem:** Boolean parameters don't show intent.

```python
# ❌ BAD: What does True/False mean here?
result = design_beam(5000, 10, True, False)

# ✅ GOOD: Use enums or explicit parameters
result = design_beam(
    5000, 10,
    design_mode='optimize',  # or 'conservative'
    include_shear=False
)
```

### 9.2 Avoid `**kwargs` in Public API

**Problem:** Hides available options from IDE.

```python
# ❌ BAD: No autocomplete, no type checking
def design_beam(span: float, load: float, **options) -> DesignResult:
    concrete = options.get('concrete', 'M20')  # Typo-prone
    steel = options.get('steel', 'Fe415')
    ...

# ✅ GOOD: Explicit parameters with types
def design_beam(
    span: float,
    load: float,
    *,
    concrete_grade: str = 'M20',
    steel_grade: str = 'Fe415'
) -> DesignResult:
    ...
```

**Exception:** `**kwargs` is acceptable for:
- Internal functions
- Wrapper functions that forward to multiple backends
- Decorator implementations

### 9.3 Avoid Overloading Parameter Meaning

**Problem:** Same parameter changes behavior based on type/value.

```python
# ❌ BAD: Parameter type changes meaning
def calculate_load(
    value: Union[float, tuple, LoadEnvelope]  # Too flexible!
) -> float:
    if isinstance(value, float):
        return value
    elif isinstance(value, tuple):
        return value[0] + value[1]  # What do tuple elements mean?
    elif isinstance(value, LoadEnvelope):
        return value.maximum
    ...

# ✅ GOOD: Separate parameters or separate functions
def calculate_load_from_envelope(envelope: LoadEnvelope) -> float:
    return envelope.maximum

def calculate_combined_load(dead_load: float, live_load: float) -> float:
    return dead_load + live_load
```

### 9.4 Avoid Output Parameters

**Problem:** Functions that modify passed objects are hard to test and reason about.

```python
# ❌ BAD: Mutates input (side effect)
def calculate_reinforcement(beam: Beam) -> None:
    """Calculates reinforcement and modifies beam in place."""
    beam.ast = calculate_ast(beam.mu, beam.b, beam.d)
    beam.bars = select_bars(beam.ast)

# ✅ GOOD: Pure function returning new value
def calculate_reinforcement(beam: Beam) -> ReinforcementResult:
    """Calculates reinforcement and returns result."""
    ast = calculate_ast(beam.mu, beam.b, beam.d)
    bars = select_bars(ast)
    return ReinforcementResult(ast=ast, bars=bars)
```

---

## 10. Migration Guide

### 10.1 Phased Migration Strategy

**Phase 1: New Functions** (v0.16+)
- All NEW functions must follow this standard
- No exceptions

**Phase 2: High-Traffic Functions** (v0.17)
- Refactor top 20 most-called functions
- Add deprecation warnings to old signatures
- Provide adapter functions for compatibility

**Phase 3: Complete Migration** (v1.0)
- All public API functions comply
- Remove deprecated signatures
- Update all documentation and examples

### 10.2 Deprecation Pattern

```python
import warnings
from typing import Any

def design_beam_old(
    span: float,
    load: float,
    width: float = 230,
    depth: float = 450
) -> Any:
    """
    DEPRECATED: Use design_beam_is456() instead.

    This function will be removed in v1.0.
    """
    warnings.warn(
        "design_beam_old() is deprecated, use design_beam_is456() with "
        "explicit unit suffixes (span_mm, load_kn_per_m, width_mm, depth_mm). "
        "Will be removed in v1.0.",
        DeprecationWarning,
        stacklevel=2
    )

    # Forward to new function
    return design_beam_is456(
        span_mm=span,
        load_kn_per_m=load,
        width_mm=width,
        depth_mm=depth
    )
```

### 10.3 Adapter Functions

For complex migrations, provide adapter layer:

```python
# Old API (deprecated)
def calculate_ast(mu: float, b: float, d: float, fck: float = 20, fy: float = 415) -> float:
    warnings.warn("Use calculate_ast_flexure() with keyword args", DeprecationWarning)
    return calculate_ast_flexure(
        moment_knm=mu,
        width_mm=b,
        depth_mm=d,
        concrete_grade=f'M{int(fck)}',
        steel_grade=f'Fe{int(fy)}'
    )

# New API (compliant)
def calculate_ast_flexure(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,
    concrete_grade: Literal['M20', 'M25', 'M30', 'M35', 'M40'] = 'M20',
    steel_grade: Literal['Fe415', 'Fe500', 'Fe550'] = 'Fe415'
) -> float:
    """Calculate required tension reinforcement area."""
    ...
```

---

## 11. Examples

### 11.1 Simple Calculation Function

```python
def calculate_balanced_reinforcement_ratio(
    fck_mpa: float,
    fy_mpa: float,
    /  # Positional-only: math formula with canonical order
) -> float:
    """
    Calculate balanced reinforcement ratio per IS 456 Cl. 38.1.

    Args:
        fck_mpa: Characteristic compressive strength of concrete (MPa)
        fy_mpa: Characteristic strength of steel (MPa)

    Returns:
        Balanced reinforcement ratio (dimensionless)

    Example:
        >>> ratio = calculate_balanced_reinforcement_ratio(20, 415)
        >>> print(f"{ratio:.4f}")
        0.0296
    """
    return 0.36 * fck_mpa / fy_mpa  # IS 456 Cl. 38.1
```

### 11.2 Module-Level Design Function

```python
def design_beam_flexure(
    moment_knm: float,
    width_mm: float,
    depth_mm: float,
    *,
    concrete_grade: Literal['M20', 'M25', 'M30', 'M35', 'M40'] = 'M20',
    steel_grade: Literal['Fe415', 'Fe500', 'Fe550'] = 'Fe415',
    cover_mm: float = 25,
    redistribution_factor: float = 1.0
) -> FlexureDesignResult:
    """
    Design beam for flexure per IS 456 Cl. 38.

    Args:
        moment_knm: Factored design moment in kN-m
        width_mm: Width of beam in mm
        depth_mm: Total depth of beam in mm
        concrete_grade: Concrete grade (default: M20 per IS 456 Cl. 5.1)
        steel_grade: Reinforcement grade (default: Fe415, most common)
        cover_mm: Effective cover to tension steel (default: 25mm for moderate exposure)
        redistribution_factor: Moment redistribution factor (1.0 = no redistribution)

    Returns:
        FlexureDesignResult containing:
        - ast_required_mm2: Required tension steel area
        - ast_provided_mm2: Provided steel area (after bar selection)
        - bar_configuration: Bar arrangement (e.g., "3-#16")
        - neutral_axis_depth_mm: Depth of neutral axis
        - moment_capacity_knm: Actual moment capacity with provided steel
        - steel_ratio: Provided steel ratio (dimensionless)
        - compliance: Compliance checks (min/max steel, spacing)

    Raises:
        InputError: If inputs violate IS 456 constraints
        ComplianceError: If design cannot satisfy code requirements

    Examples:
        >>> # Simple residential beam
        >>> result = design_beam_flexure(
        ...     moment_knm=150,
        ...     width_mm=230,
        ...     depth_mm=450
        ... )
        >>> print(result.bar_configuration)
        '3-#16'

        >>> # High-strength concrete with redistribution
        >>> result = design_beam_flexure(
        ...     moment_knm=200,
        ...     width_mm=300,
        ...     depth_mm=500,
        ...     concrete_grade='M35',
        ...     steel_grade='Fe500',
        ...     redistribution_factor=0.9
        ... )
    """
    # Input validation
    if moment_knm <= 0:
        raise InputError("Moment must be positive")

    # ... implementation
```

### 11.3 Top-Level API Function

```python
def design_beam_is456(
    span_mm: float,
    load_kn_per_m: float,
    *,
    geometry: Optional[BeamGeometry] = None,
    materials: Optional[Materials] = None,
    loads: Optional[LoadCombinations] = None,
    design_options: Optional[DesignOptions] = None,
    validate_inputs: bool = True
) -> CompleteDesignResult:
    """
    Complete beam design per IS 456:2000 (full workflow).

    This is the primary entry point for beam design. It performs:
    1. Load calculations and envelope generation
    2. Flexural design (tension and compression reinforcement)
    3. Shear design (stirrups and spacing)
    4. Deflection check (span/depth ratio)
    5. Detailing (cutoffs, anchorage, development length)
    6. Compliance verification against all IS 456 requirements

    Args:
        span_mm: Clear span between supports (mm)
        load_kn_per_m: Uniformly distributed load (kN/m)
        geometry: Beam geometry configuration. If None, uses defaults:
                  width=230mm, depth=450mm, cover=25mm
        materials: Material specifications. If None, uses defaults:
                   concrete='M20', steel='Fe415'
        loads: Advanced load combinations. If None, uses simple UDL from load_kn_per_m
        design_options: Advanced design options (optimization, tolerance, etc.)
        validate_inputs: Enable input validation (disable only for batch processing)

    Returns:
        CompleteDesignResult containing:
        - flexure: FlexureDesignResult (reinforcement, capacity)
        - shear: ShearDesignResult (stirrups, spacing)
        - deflection: DeflectionCheckResult (calculated vs limit)
        - detailing: DetailingResult (cutoffs, development lengths)
        - compliance: Overall compliance status
        - efficiency: Design efficiency metrics
        - drawings: Geometry for CAD export

    Raises:
        InputError: Invalid input parameters
        CalculationError: Convergence or numerical issues
        ComplianceError: Design violates IS 456 requirements

    Examples:
        >>> # Minimal usage (all defaults)
        >>> result = design_beam_is456(
        ...     span_mm=5000,
        ...     load_kn_per_m=10.0
        ... )
        >>> print(f"Design: {result.summary()}")
        >>> print(f"Passed: {result.compliance.all_passed}")

        >>> # Custom geometry and materials
        >>> result = design_beam_is456(
        ...     span_mm=6000,
        ...     load_kn_per_m=15.0,
        ...     geometry=BeamGeometry(width_mm=300, depth_mm=550, cover_mm=30),
        ...     materials=Materials(concrete='M30', steel='Fe500')
        ... )

        >>> # Advanced: Full load combinations
        >>> loads = LoadCombinations(
        ...     dead_load_kn_per_m=8.0,
        ...     live_load_kn_per_m=5.0,
        ...     wind_load_kn_per_m=2.0
        ... )
        >>> result = design_beam_is456(
        ...     span_mm=8000,
        ...     load_kn_per_m=0,  # Not used when loads provided
        ...     loads=loads
        ... )

    See Also:
        - design_beam_flexure(): Flexure-only design
        - design_beam_shear(): Shear-only design
        - optimize_beam_dimensions(): Find optimal beam size

    References:
        IS 456:2000 - Code of Practice for Plain and Reinforced Concrete
        SP:16 - Design Aids for Reinforced Concrete to IS 456
    """
    # Set defaults
    geometry = geometry or BeamGeometry()
    materials = materials or Materials()
    design_options = design_options or DesignOptions()

    # Validate inputs
    if validate_inputs:
        validate_beam_inputs(span_mm, load_kn_per_m, geometry, materials)

    # ... full implementation
```

---

## Appendix A: Quick Reference Card

**Print this for your desk:**

### Function Signature Checklist

- [ ] ≤3 params → positional OK; >3 params → use `*` separator
- [ ] All parameters have type hints (including return type)
- [ ] Dimensional parameters have unit suffixes (`_mm`, `_kn`, `_mpa`)
- [ ] String choices use `Literal['option1', 'option2']`
- [ ] Optional parameters have sensible defaults (not `None` unless meaningful)
- [ ] Default values are conservative/code-compliant
- [ ] No mutable defaults (`list=[]`, `dict={}`)
- [ ] Docstring has Args/Returns/Raises/Examples sections
- [ ] Default values reference code clauses in docstring
- [ ] Primary inputs come first, configuration later

### Type Hint Quick Reference

```python
# Basic types
param: int
param: float
param: str
param: bool

# Optional (can be None)
param: Optional[float] = None

# Literal choices (IDE autocomplete)
param: Literal['M20', 'M25', 'M30'] = 'M20'

# Collections
param: list[float]
param: dict[str, int]
param: tuple[float, float, float]

# Union (multiple types - use sparingly)
param: float | int

# Callable (function parameter)
param: Callable[[int, int], None]

# Custom types
param: BeamGeometry
param: DesignResult
```

---

## Appendix B: Review Checklist for PRs

Use this checklist when reviewing function signature changes:

**Signature Structure**
- [ ] Parameter order follows standard (primary → secondary → config → flags)
- [ ] `*` separator used for >3 parameters
- [ ] Required parameters have no defaults
- [ ] Optional parameters have defaults

**Type Safety**
- [ ] All parameters have type hints
- [ ] Return type is specified
- [ ] `Literal` used for string/int choices
- [ ] No `Any` types in public API

**Naming**
- [ ] Dimensional parameters have unit suffixes
- [ ] Parameter names are clear and unambiguous
- [ ] Names match domain conventions (IS 456 terminology)

**Defaults**
- [ ] Defaults are conservative
- [ ] No mutable defaults
- [ ] Code defaults reference clauses in docstring

**Documentation**
- [ ] Docstring has complete Args section
- [ ] Docstring has Returns section
- [ ] Docstring has Raises section
- [ ] Docstring has at least one Example
- [ ] Units are documented for return value

**Compatibility**
- [ ] Breaking changes have deprecation warnings
- [ ] Migration path is documented
- [ ] Adapter functions provided if needed

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-07 | Initial version based on TASK-200/201 research |

---

## References

1. [Professional API Patterns Research](../research/professional-api-patterns.md) - NumPy, SciPy, Pandas patterns
2. [UX Patterns for Technical APIs](../research/ux-patterns-for-technical-apis.md) - Cognitive load, discoverability
3. PEP 484 -- Type Hints: https://peps.python.org/pep-0484/
4. PEP 3102 -- Keyword-Only Arguments: https://peps.python.org/pep-3102/
5. PEP 570 -- Positional-Only Parameters: https://peps.python.org/pep-0570/
6. Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
7. IS 456:2000 - Code of Practice for Plain and Reinforced Concrete
8. Miller, G. A. (1956). "The Magical Number Seven, Plus or Minus Two"

---

**END OF DOCUMENT**
