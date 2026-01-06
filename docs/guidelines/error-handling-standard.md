# Error Handling & Exception Design Standard

> **Standard for exception design, error messages, and validation patterns**
> Created: 2026-01-07 | Status: Active | Part of: API Improvement Research (TASK-204)

---

## Purpose

This document establishes standards for error handling in the structural engineering library to ensure:
- **Clear diagnosis**: Users understand what went wrong
- **Actionable guidance**: Users know how to fix issues
- **Appropriate severity**: Errors match the actual problem level
- **Consistent patterns**: Predictable exception behavior across the library

**Target audience**: Library developers implementing calculations, API functions, and validation logic.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Exception Hierarchy Design](#2-exception-hierarchy-design)
3. [Error Message Quality](#3-error-message-quality)
4. [Validation Patterns](#4-validation-patterns)
5. [Error Recovery Strategies](#5-error-recovery-strategies)
6. [Exception Context & Debugging](#6-exception-context--debugging)
7. [Anti-patterns to Avoid](#7-anti-patterns-to-avoid)
8. [Testing Exception Behavior](#8-testing-exception-behavior)
9. [Migration Strategy](#9-migration-strategy)
10. [Complete Examples](#10-complete-examples)
11. [Integration with Logging](#11-integration-with-logging)
12. [Performance Considerations](#12-performance-considerations)

**Appendices:**
- [A: Quick Reference Checklist](#appendix-a-quick-reference-checklist)
- [B: Complete Exception Catalog](#appendix-b-complete-exception-catalog)

---

## 1. Core Principles

### 1.1 The Three Questions Framework

Every exception must answer three questions:
1. **What went wrong?** (clear description)
2. **Why did it fail?** (context: values, constraints)
3. **How to fix it?** (actionable guidance)

```python
# ❌ BAD: Fails all three questions
raise ValueError("Invalid input")

# ✅ GOOD: Answers all three questions
raise ValidationError(
    "Beam width b=150mm is below minimum 200mm required by IS 456:2000 Cl. 26.5.1.1. "
    "Increase beam width to at least 200mm."
)
```

### 1.2 Fail Fast, Fail Loud

**Validate early**: Check inputs at API boundaries before expensive computation.

```python
def design_beam_is456(b_mm: float, d_mm: float, ...) -> BeamDesignResult:
    # ✅ Validate immediately at entry
    if b_mm < 200:
        raise ValidationError(f"Beam width b={b_mm}mm < 200mm minimum (IS 456 Cl. 26.5.1.1)")

    if d_mm < 150:
        raise ValidationError(f"Effective depth d={d_mm}mm < 150mm minimum")

    # Now proceed with expensive calculations
    ...
```

**Don't return error codes or None**: Use exceptions for exceptional conditions.

```python
# ❌ BAD: Silent failure, error codes
def calculate_ast(mu_kn_m: float, ...) -> tuple[float | None, str]:
    if mu_kn_m < 0:
        return None, "Negative moment"
    ...

# ✅ GOOD: Clear exception
def calculate_ast(mu_kn_m: float, ...) -> float:
    if mu_kn_m < 0:
        raise ValidationError(
            f"Moment Mu={mu_kn_m} kN·m cannot be negative. "
            "Check load combination signs."
        )
    ...
```

### 1.3 Appropriate Exception Types

Match exception type to the failure category:

| Failure Type | Exception | When to Use |
|--------------|-----------|-------------|
| Invalid user input | `ValidationError` | Bad dimensions, materials, out of range |
| Design cannot satisfy code | `DesignError` | Exceeds capacity, insufficient space |
| Code compliance violation | `ComplianceError` | Minimum reinforcement, spacing, detailing |
| Configuration/state issues | `ConfigurationError` | Missing setup, invalid state |
| Calculation instability | `CalculationError` | Convergence failure, numerical issues |
| Internal bugs | `AssertionError` | Impossible states, contract violations |

### 1.4 Separate Validation from Business Logic

```python
# ✅ GOOD: Validation layer → Business logic layer
def design_singly_reinforced(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
    *,
    validate: bool = True,
) -> FlexureResult:
    """Design singly reinforced beam section."""

    # Validation layer (optional for batch processing)
    if validate:
        _validate_flexure_inputs(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)

    # Business logic (assumes valid inputs)
    mu_lim = calculate_mu_lim(b_mm, d_mm, fck_mpa)
    if mu_kn_m > mu_lim:
        raise DesignError(
            f"Moment Mu={mu_kn_m:.1f} kN·m exceeds limit moment "
            f"Mu,lim={mu_lim:.1f} kN·m. Requires compression reinforcement."
        )
    ...
```

---

## 2. Exception Hierarchy Design

### 2.1 Standard Hierarchy

```python
# Base exception for all library errors
class StructuralLibError(Exception):
    """Base exception for structural_lib_is456."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        suggestion: str | None = None,
        clause_ref: str | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
        self.clause_ref = clause_ref

    def __str__(self) -> str:
        parts = [self.message]
        if self.clause_ref:
            parts.append(f"(Ref: IS 456:2000 {self.clause_ref})")
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " ".join(parts)


# Level 1: Input problems (user error)
class ValidationError(StructuralLibError):
    """Raised when input validation fails."""
    pass


# Level 1: Design constraints violated (not user error, but design limitation)
class DesignError(StructuralLibError):
    """Raised when design requirements cannot be satisfied."""
    pass


# Level 1: Code compliance issues
class ComplianceError(StructuralLibError):
    """Raised when IS 456:2000 requirements are not met."""
    pass


# Level 1: Configuration/state issues
class ConfigurationError(StructuralLibError):
    """Raised when library is misconfigured or in invalid state."""
    pass


# Level 1: Calculation problems (numerical issues)
class CalculationError(StructuralLibError):
    """Raised when calculation cannot complete (convergence, numerical instability)."""
    pass


# Level 2: Specific validation failures
class DimensionError(ValidationError):
    """Raised when dimensions are invalid or out of range."""
    pass


class MaterialError(ValidationError):
    """Raised when material properties are invalid."""
    pass


class LoadError(ValidationError):
    """Raised when loads are invalid."""
    pass
```

### 2.2 Exception Hierarchy Tree

```
Exception (Python built-in)
└── StructuralLibError
    ├── ValidationError (user input problems)
    │   ├── DimensionError
    │   ├── MaterialError
    │   └── LoadError
    ├── DesignError (design constraints violated)
    ├── ComplianceError (code requirements not met)
    ├── ConfigurationError (library setup issues)
    └── CalculationError (numerical problems)
```

### 2.3 When to Create New Exception Types

**Create a new exception type when:**
- Users need to catch it specifically for different handling
- It represents a distinct failure category
- It needs different context/details than the parent

**Don't create new types when:**
- Only changing the message is sufficient
- No user would catch this specific type
- It's a one-off case

```python
# ❌ BAD: Too specific, no one will catch this
class BeamWidthTooSmallError(ValidationError):
    pass

# ✅ GOOD: Use general type with specific message
raise ValidationError(
    f"Beam width b={b_mm}mm < 200mm minimum",
    details={"b_mm": b_mm, "minimum": 200},
    clause_ref="Cl. 26.5.1.1",
)
```

---

## 3. Error Message Quality

### 3.1 Message Template

**Standard format:**
```
{What went wrong} {value/context}. {Why it failed} {constraint/rule}. {How to fix} {actionable guidance}.
```

**Examples:**

```python
# Dimension error
raise DimensionError(
    f"Beam width b={b_mm}mm is below minimum 200mm required by IS 456:2000 Cl. 26.5.1.1. "
    f"Increase beam width to at least 200mm."
)

# Material error
raise MaterialError(
    f"Concrete grade fck={fck_mpa}MPa is not in standard grades [20, 25, 30, 35, 40, 45, 50]. "
    f"Use a standard grade from IS 456:2000 Table 2."
)

# Design capacity exceeded
raise DesignError(
    f"Factored moment Mu={mu_kn_m:.1f} kN·m exceeds section capacity "
    f"Mu,lim={mu_lim:.1f} kN·m (xu,max={xu_max:.1f}mm, actual xu={xu:.1f}mm). "
    f"Options: (1) increase section depth, (2) use compression reinforcement, "
    f"(3) increase concrete grade."
)

# Compliance error with options
raise ComplianceError(
    f"Minimum reinforcement Ast,min={ast_min:.0f}mm² exceeds provided "
    f"Ast={ast_provided:.0f}mm² (IS 456 Cl. 26.5.1.1). "
    f"Add {ast_min - ast_provided:.0f}mm² reinforcement or increase bar diameter."
)
```

### 3.2 Units in Error Messages

**Always include units** to avoid ambiguity:

```python
# ❌ BAD: No units
raise ValidationError(f"Beam width {b} is too small")

# ✅ GOOD: Units explicit
raise ValidationError(f"Beam width b={b_mm}mm < 200mm minimum")
```

### 3.3 Include Relevant Values

Show both **actual** and **expected/limit** values:

```python
# ✅ GOOD: Shows actual, limit, and magnitude of violation
raise ComplianceError(
    f"Spacing s={spacing_mm:.0f}mm exceeds maximum {max_spacing:.0f}mm "
    f"(IS 456 Cl. 26.3.3). Over by {spacing_mm - max_spacing:.0f}mm."
)
```

### 3.4 Progressive Detail Levels

Use exception attributes for machine-readable details:

```python
raise DesignError(
    # Human-readable summary
    f"Section capacity insufficient: Mu={mu_kn_m:.1f} > Mu,lim={mu_lim:.1f} kN·m",
    # Machine-readable details for debugging/logging
    details={
        "mu_kn_m": mu_kn_m,
        "mu_lim_kn_m": mu_lim,
        "xu_mm": xu,
        "xu_max_mm": xu_max,
        "b_mm": b_mm,
        "d_mm": d_mm,
        "fck_mpa": fck_mpa,
    },
    # Actionable suggestion
    suggestion="Increase section depth or use compression reinforcement",
    # Code reference
    clause_ref="Cl. 38.1 (xu,max limit)",
)
```

### 3.5 Avoid Jargon in User-Facing Messages

```python
# ❌ BAD: Technical jargon
raise CalculationError("Neutral axis iteration diverged at step 47")

# ✅ GOOD: Clear explanation
raise CalculationError(
    "Could not determine required reinforcement area. "
    "Section may be over-reinforced or inputs may be unrealistic. "
    "Check: (1) moment is within reasonable range, "
    "(2) material grades are correct, (3) section dimensions."
)
```

---

## 4. Validation Patterns

### 4.1 Input Validation Function Pattern

Create dedicated validation functions that are reusable and testable:

```python
def _validate_flexure_inputs(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
) -> None:
    """Validate flexure design inputs.

    Raises:
        DimensionError: If dimensions are invalid
        MaterialError: If material grades are invalid
        LoadError: If loads are invalid
    """
    # Dimension checks
    if b_mm < 200:
        raise DimensionError(
            f"Beam width b={b_mm}mm < 200mm minimum (IS 456 Cl. 26.5.1.1)",
            details={"b_mm": b_mm, "minimum": 200},
            suggestion="Increase beam width to at least 200mm",
            clause_ref="Cl. 26.5.1.1",
        )

    if d_mm < 150:
        raise DimensionError(
            f"Effective depth d={d_mm}mm < 150mm practical minimum",
            details={"d_mm": d_mm, "minimum": 150},
            suggestion="Increase effective depth to at least 150mm",
        )

    if d_mm > 2000:
        raise DimensionError(
            f"Effective depth d={d_mm}mm > 2000mm seems unrealistic. Verify input.",
            details={"d_mm": d_mm, "maximum_typical": 2000},
            suggestion="Check if depth was entered in wrong units (cm instead of mm?)",
        )

    # Material grade checks
    STANDARD_GRADES_FCK = [20, 25, 30, 35, 40, 45, 50]
    if fck_mpa not in STANDARD_GRADES_FCK:
        raise MaterialError(
            f"Concrete grade fck={fck_mpa}MPa not in standard grades {STANDARD_GRADES_FCK}",
            details={"fck_mpa": fck_mpa, "valid_grades": STANDARD_GRADES_FCK},
            suggestion="Use a standard grade from IS 456 Table 2",
            clause_ref="Table 2",
        )

    STANDARD_GRADES_FY = [250, 415, 500, 550]
    if fy_mpa not in STANDARD_GRADES_FY:
        raise MaterialError(
            f"Steel grade fy={fy_mpa}MPa not in standard grades {STANDARD_GRADES_FY}",
            details={"fy_mpa": fy_mpa, "valid_grades": STANDARD_GRADES_FY},
            suggestion="Use Fe250, Fe415, Fe500, or Fe550 steel",
            clause_ref="Cl. 6.2",
        )

    # Load checks
    if mu_kn_m < 0:
        raise LoadError(
            f"Factored moment Mu={mu_kn_m} kN·m cannot be negative",
            details={"mu_kn_m": mu_kn_m},
            suggestion="Check load combination signs. Use absolute value if needed.",
        )

    if mu_kn_m == 0:
        raise LoadError(
            "Zero moment - no flexural design required",
            details={"mu_kn_m": mu_kn_m},
            suggestion="Provide nominal reinforcement per IS 456 Cl. 26.5.1.1",
        )
```

### 4.2 Range Validation Helper

```python
def validate_range(
    value: float,
    min_val: float | None = None,
    max_val: float | None = None,
    *,
    name: str,
    units: str = "",
    clause_ref: str | None = None,
) -> None:
    """Validate that value is within specified range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value (None = no minimum)
        max_val: Maximum allowed value (None = no maximum)
        name: Parameter name for error message
        units: Units string (e.g., "mm", "MPa")
        clause_ref: IS 456 clause reference

    Raises:
        ValidationError: If value is out of range

    Example:
        >>> validate_range(150, 200, 600, name="b", units="mm", clause_ref="Cl. 26.5.1.1")
        ValidationError: Beam width b=150mm < 200mm minimum (IS 456 Cl. 26.5.1.1)
    """
    unit_str = units if units else ""

    if min_val is not None and value < min_val:
        msg = f"{name}={value}{unit_str} < {min_val}{unit_str} minimum"
        if clause_ref:
            msg += f" (IS 456 {clause_ref})"
        raise ValidationError(
            msg,
            details={"value": value, "minimum": min_val, "parameter": name},
            suggestion=f"Increase {name} to at least {min_val}{unit_str}",
            clause_ref=clause_ref,
        )

    if max_val is not None and value > max_val:
        msg = f"{name}={value}{unit_str} > {max_val}{unit_str} maximum"
        if clause_ref:
            msg += f" (IS 456 {clause_ref})"
        raise ValidationError(
            msg,
            details={"value": value, "maximum": max_val, "parameter": name},
            suggestion=f"Reduce {name} to at most {max_val}{unit_str}",
            clause_ref=clause_ref,
        )
```

### 4.3 Optional Validation Flag Pattern

Allow disabling validation for performance-critical batch operations:

```python
def design_beam_is456(
    b_mm: float,
    d_mm: float,
    ...,
    *,
    validate: bool = True,  # ← Optional validation
) -> BeamDesignResult:
    """Design beam per IS 456:2000.

    Args:
        validate: If True, validate all inputs before calculation.
                 Set to False for batch operations where inputs are pre-validated.
                 Default: True (safe default)
    """
    if validate:
        _validate_flexure_inputs(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)
        _validate_shear_inputs(vu_kn, ...)
        # ... all validation checks

    # Proceed with calculations (assumes valid inputs if validate=False)
    ...
```

**Usage:**

```python
# Single beam: validate for safety
result = design_beam_is456(b_mm=300, d_mm=550, ..., validate=True)

# Batch operation: validate once, disable per-beam
beams = [...]  # 1000 beams
_validate_batch_inputs(beams)  # Pre-validate entire batch
results = [
    design_beam_is456(**beam, validate=False)  # Skip redundant checks
    for beam in beams
]
```

### 4.4 Strict Mode for Extra Checks

Add optional strict mode for pedantic validation:

```python
def design_beam_is456(
    ...,
    *,
    validate: bool = True,
    strict: bool = False,  # ← Extra pedantic checks
) -> BeamDesignResult:
    """Design beam per IS 456:2000.

    Args:
        strict: If True, apply extra pedantic checks:
               - Warn on unusual ratios (L/d, b/d)
               - Check for likely unit errors
               - Validate realistic load magnitudes
               Default: False
    """
    if validate:
        _validate_flexure_inputs(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)

    if strict:
        _strict_validation(b_mm, d_mm, mu_kn_m, span_mm, ...)
```

### 4.5 Multiple Validation Errors

Collect all errors before raising (better UX for form validation):

```python
def validate_all_inputs(...) -> None:
    """Validate all inputs and report ALL errors at once."""
    errors = []

    # Check all conditions
    if b_mm < 200:
        errors.append(f"Beam width b={b_mm}mm < 200mm minimum")

    if d_mm < 150:
        errors.append(f"Effective depth d={d_mm}mm < 150mm minimum")

    if fck_mpa not in [20, 25, 30, 35, 40, 45, 50]:
        errors.append(f"Concrete grade fck={fck_mpa}MPa not standard")

    # Raise with all errors
    if errors:
        raise ValidationError(
            f"Found {len(errors)} validation error(s):\n" +
            "\n".join(f"  {i+1}. {err}" for i, err in enumerate(errors))
        )
```

---

## 5. Error Recovery Strategies

### 5.1 Graceful Degradation

When a calculation fails, provide partial results if useful:

```python
@dataclass(frozen=True)
class BeamDesignResult:
    """Beam design result with success/failure tracking."""

    success: bool
    flexure: FlexureResult | None
    shear: ShearResult | None
    error: str | None = None
    warnings: list[str] = field(default_factory=list)

    def is_valid(self) -> bool:
        """Check if design is valid."""
        return self.success and self.error is None

    def has_warnings(self) -> bool:
        """Check if design has warnings."""
        return len(self.warnings) > 0


def design_beam_is456(...) -> BeamDesignResult:
    """Design beam, returning partial results on failure."""
    warnings = []

    try:
        flexure_result = design_flexure(...)
    except DesignError as e:
        return BeamDesignResult(
            success=False,
            flexure=None,
            shear=None,
            error=str(e),
        )

    try:
        shear_result = design_shear(...)
    except ComplianceError as e:
        warnings.append(f"Shear design warning: {e}")
        # Continue with flexure result only
        return BeamDesignResult(
            success=True,
            flexure=flexure_result,
            shear=None,
            warnings=warnings,
        )

    return BeamDesignResult(
        success=True,
        flexure=flexure_result,
        shear=shear_result,
        warnings=warnings,
    )
```

### 5.2 Retry with Relaxed Constraints

```python
def optimize_bar_arrangement(...) -> BarArrangement:
    """Optimize bar arrangement, trying multiple strategies."""

    # Try ideal arrangement first
    try:
        return _optimize_ideal(ast_req_mm2, b_mm, ...)
    except DesignError:
        pass  # Fall through to relaxed constraints

    # Try with minimum spacing
    try:
        return _optimize_minimum_spacing(ast_req_mm2, b_mm, ...)
    except DesignError:
        pass

    # Last resort: use smaller bars
    try:
        return _optimize_smaller_bars(ast_req_mm2, b_mm, ...)
    except DesignError as e:
        raise DesignError(
            f"Cannot fit required reinforcement Ast={ast_req_mm2:.0f}mm² "
            f"in beam width b={b_mm}mm even with minimum spacing. {str(e)}"
        ) from e
```

### 5.3 Warning System

Use warnings for non-critical issues:

```python
import warnings
from structural_lib.types import StructuralWarning


def check_deflection(...) -> DeflectionResult:
    """Check deflection with warnings for borderline cases."""

    span_depth_ratio = span_mm / d_mm
    max_ratio = get_max_span_depth_ratio(support_condition, ...)

    if span_depth_ratio > max_ratio:
        # Critical: raise exception
        raise ComplianceError(
            f"Span/depth ratio {span_depth_ratio:.1f} > {max_ratio:.1f} maximum "
            f"(IS 456 Cl. 23.2.1)"
        )
    elif span_depth_ratio > max_ratio * 0.9:
        # Warning: close to limit
        warnings.warn(
            f"Span/depth ratio {span_depth_ratio:.1f} is close to limit "
            f"{max_ratio:.1f} (90% of maximum). Consider increasing depth.",
            StructuralWarning,
        )

    return DeflectionResult(...)
```

---

## 6. Exception Context & Debugging

### 6.1 Exception Chaining

Use `raise ... from ...` to preserve original exception:

```python
def design_beam_is456(...) -> BeamDesignResult:
    """Design beam with exception chaining for debugging."""

    try:
        flexure = design_flexure(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa)
    except ValidationError as e:
        raise ValidationError(
            f"Flexure design failed for beam b={b_mm}mm d={d_mm}mm: {str(e)}"
        ) from e  # ← Preserves original exception
```

### 6.2 Rich Debug Context

Add context for debugging without cluttering user message:

```python
def calculate_ast_required(...) -> float:
    """Calculate required steel area."""

    try:
        # Complex calculation
        k = mu_n_mm / (fck_mpa * b_mm * d_mm**2)
        ...
    except (ValueError, ZeroDivisionError) as e:
        raise CalculationError(
            f"Cannot calculate required steel area for Mu={mu_kn_m} kN·m",
            details={
                # Full context for debugging
                "mu_kn_m": mu_kn_m,
                "mu_n_mm": mu_n_mm,
                "b_mm": b_mm,
                "d_mm": d_mm,
                "fck_mpa": fck_mpa,
                "fy_mpa": fy_mpa,
                "k": k if 'k' in locals() else None,
                "original_error": str(e),
            },
            suggestion="Check that inputs are in correct units and within reasonable ranges",
        ) from e
```

### 6.3 Traceback Enhancement

Custom `__str__` method for rich exception output:

```python
class StructuralLibError(Exception):
    """Base exception with rich debugging info."""

    def __str__(self) -> str:
        """Format exception with all context."""
        parts = [self.message]

        # Code reference
        if self.clause_ref:
            parts.append(f"(Ref: IS 456:2000 {self.clause_ref})")

        # User guidance
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")

        # Debug details (only if non-empty)
        if self.details:
            parts.append("\nDebug details:")
            for key, value in self.details.items():
                parts.append(f"  {key} = {value}")

        return "\n".join(parts)
```

**Output example:**

```
DesignError: Section capacity insufficient: Mu=250.0 > Mu,lim=180.5 kN·m (Ref: IS 456:2000 Cl. 38.1)
Suggestion: Increase section depth or use compression reinforcement
Debug details:
  mu_kn_m = 250.0
  mu_lim_kn_m = 180.5
  xu_mm = 285.7
  xu_max_mm = 247.5
  b_mm = 300.0
  d_mm = 550.0
  fck_mpa = 30.0
```

---

## 7. Anti-patterns to Avoid

### 7.1 Silent Failures

```python
# ❌ BAD: Returns None on error, silent failure
def calculate_ast(mu_kn_m: float, ...) -> float | None:
    if mu_kn_m < 0:
        return None  # Silent, user must check return value
    ...

# ✅ GOOD: Explicit exception
def calculate_ast(mu_kn_m: float, ...) -> float:
    if mu_kn_m < 0:
        raise ValidationError(f"Moment Mu={mu_kn_m} kN·m cannot be negative")
    ...
```

### 7.2 Generic Error Messages

```python
# ❌ BAD: Vague, unhelpful
raise ValueError("Invalid input")
raise Exception("Error in calculation")
raise RuntimeError("Failed")

# ✅ GOOD: Specific, actionable
raise DimensionError(
    f"Beam width b={b_mm}mm < 200mm minimum (IS 456 Cl. 26.5.1.1). "
    f"Increase beam width to at least 200mm."
)
```

### 7.3 Swallowing Exceptions

```python
# ❌ BAD: Catches and hides errors
def design_beam(...):
    try:
        result = design_flexure(...)
    except Exception:
        return None  # Lost all error information!

# ✅ GOOD: Let exceptions propagate or re-raise with context
def design_beam(...):
    try:
        result = design_flexure(...)
    except ValidationError as e:
        raise ValidationError(f"Beam design failed: {str(e)}") from e
```

### 7.4 Exception for Control Flow

```python
# ❌ BAD: Using exceptions for normal control flow
def find_bar_size(ast_req_mm2: float) -> int:
    for dia in [12, 16, 20, 25, 32]:
        try:
            arrangement = try_bar_size(ast_req_mm2, dia)
            return dia
        except DesignError:
            continue  # Try next size

# ✅ GOOD: Use explicit return values
def find_bar_size(ast_req_mm2: float) -> int | None:
    for dia in [12, 16, 20, 25, 32]:
        if can_fit_bars(ast_req_mm2, dia):
            return dia
    return None  # No suitable size found
```

### 7.5 Misleading Exception Types

```python
# ❌ BAD: Using ValueError for non-input errors
def design_flexure(...):
    if mu_kn_m > mu_lim:
        raise ValueError("Moment exceeds capacity")  # Not a validation error!

# ✅ GOOD: Use correct exception type
def design_flexure(...):
    if mu_kn_m > mu_lim:
        raise DesignError(  # Design capacity issue
            f"Moment Mu={mu_kn_m:.1f} > Mu,lim={mu_lim:.1f} kN·m. "
            f"Requires compression reinforcement."
        )
```

### 7.6 Bare `assert` for Validation

```python
# ❌ BAD: Assert can be disabled with python -O
def design_beam(b_mm: float, ...):
    assert b_mm >= 200, "Width too small"  # Disappears with -O flag!
    ...

# ✅ GOOD: Explicit validation
def design_beam(b_mm: float, ...):
    if b_mm < 200:
        raise ValidationError(f"Beam width b={b_mm}mm < 200mm minimum")
    ...

# ✅ OK: Assert for internal invariants only
def _internal_calculation(...):
    result = complex_math(...)
    assert result >= 0, "Bug: result should never be negative"  # Programming error
    return result
```

### 7.7 Error Codes Instead of Types

```python
# ❌ BAD: C-style error codes
def design_beam(...) -> tuple[BeamDesignResult | None, int]:
    if b_mm < 200:
        return None, ERROR_DIMENSION  # User must decode error code
    if mu_kn_m > mu_lim:
        return None, ERROR_CAPACITY
    return result, SUCCESS

# ✅ GOOD: Use exception types
def design_beam(...) -> BeamDesignResult:
    if b_mm < 200:
        raise DimensionError("...")
    if mu_kn_m > mu_lim:
        raise DesignError("...")
    return result
```

---

## 8. Testing Exception Behavior

### 8.1 Test Expected Exceptions

```python
import pytest
from structural_lib.exceptions import DimensionError, MaterialError


def test_beam_width_validation():
    """Test that beam width below 200mm raises DimensionError."""
    with pytest.raises(DimensionError) as exc_info:
        design_flexure(
            b_mm=150,  # Too small
            d_mm=500,
            mu_kn_m=100,
            fck_mpa=30,
            fy_mpa=415,
        )

    # Check error message content
    assert "b=150mm" in str(exc_info.value)
    assert "200mm minimum" in str(exc_info.value)
    assert "Cl. 26.5.1.1" in str(exc_info.value)


def test_concrete_grade_validation():
    """Test that invalid concrete grade raises MaterialError."""
    with pytest.raises(MaterialError, match=r"fck=.*not in standard grades"):
        design_flexure(
            b_mm=300,
            d_mm=500,
            mu_kn_m=100,
            fck_mpa=33,  # Not a standard grade
            fy_mpa=415,
        )
```

### 8.2 Test Exception Attributes

```python
def test_exception_details():
    """Test that exception includes rich debugging details."""
    with pytest.raises(DimensionError) as exc_info:
        design_flexure(b_mm=150, ...)

    exc = exc_info.value
    assert exc.details["b_mm"] == 150
    assert exc.details["minimum"] == 200
    assert exc.suggestion is not None
    assert "200mm" in exc.suggestion
    assert exc.clause_ref == "Cl. 26.5.1.1"
```

### 8.3 Test Exception Chaining

```python
def test_exception_chaining():
    """Test that exceptions are chained with context."""
    with pytest.raises(ValidationError) as exc_info:
        design_beam_is456(b_mm=150, ...)  # Top-level function

    # Check that original exception is chained
    assert exc_info.value.__cause__ is not None
    assert isinstance(exc_info.value.__cause__, DimensionError)
```

### 8.4 Test Error Messages Don't Break

```python
def test_error_message_formatting():
    """Test that error messages format correctly."""
    # Use parameterized tests for multiple cases
    test_cases = [
        (150, "b=150mm"),
        (199.5, "b=199.5mm"),
        (0, "b=0mm"),
    ]

    for b_mm, expected_in_message in test_cases:
        with pytest.raises(DimensionError) as exc_info:
            design_flexure(b_mm=b_mm, ...)

        assert expected_in_message in str(exc_info.value)
```

### 8.5 Test Validation Flag

```python
def test_validation_flag_enabled():
    """Test that validation=True catches invalid inputs."""
    with pytest.raises(DimensionError):
        design_beam_is456(b_mm=150, ..., validate=True)


def test_validation_flag_disabled():
    """Test that validation=False skips input validation."""
    # This should NOT raise (though calculation may fail later)
    # Only use for performance testing, not recommended in production
    try:
        result = design_beam_is456(b_mm=150, ..., validate=False)
    except DimensionError:
        pytest.fail("validation=False should not raise DimensionError at input check")
```

---

## 9. Migration Strategy

### 9.1 Phased Rollout

**Phase 1: Create exception hierarchy** (v0.15.0)
- Add new exception classes to `structural_lib/exceptions.py`
- No breaking changes yet, old code still works

```python
# New file: structural_lib/exceptions.py
class StructuralLibError(Exception):
    """Base exception for structural_lib_is456."""
    ...

class ValidationError(StructuralLibError):
    """Raised when input validation fails."""
    ...
```

**Phase 2: Add new exceptions alongside old** (v0.16.0)
- Start using new exceptions in new code
- Keep old error handling for backward compatibility

```python
def design_flexure_new(...) -> FlexureResult:
    """New function using new exceptions."""
    if b_mm < 200:
        raise DimensionError("...")
    ...

def design_flexure(...) -> tuple:
    """Old function still using tuples/None."""
    if b_mm < 200:
        return None, "Width too small"
    ...
```

**Phase 3: Add deprecation warnings** (v0.17.0)
- Keep old functions but warn about deprecation

```python
import warnings

def design_flexure(...) -> tuple:
    """
    DEPRECATED: Use design_flexure_v2() instead.

    This function will be removed in v1.0.0.
    """
    warnings.warn(
        "design_flexure() is deprecated and will be removed in v1.0.0. "
        "Use design_flexure_v2() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    ...
```

**Phase 4: Remove old code** (v1.0.0)
- Remove deprecated functions
- All code uses new exception system

### 9.2 Wrapper for Backward Compatibility

```python
def design_beam_is456_legacy(
    b_mm: float,
    d_mm: float,
    ...,
) -> tuple[BeamDesignResult | None, str]:
    """
    Legacy wrapper that returns (result, error_message) tuple.

    DEPRECATED: Use design_beam_is456() which raises exceptions.
    This function will be removed in v1.0.0.
    """
    warnings.warn(
        "design_beam_is456_legacy() is deprecated. "
        "Use design_beam_is456() and handle exceptions instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        result = design_beam_is456(b_mm, d_mm, ...)
        return result, ""
    except StructuralLibError as e:
        return None, str(e)
```

### 9.3 Migration Checklist

For each function being migrated:

- [ ] Replace return tuples with exceptions
- [ ] Add validation at function entry
- [ ] Use appropriate exception types (ValidationError, DesignError, etc.)
- [ ] Include units in error messages
- [ ] Add `details` dict for debugging
- [ ] Add `suggestion` for user guidance
- [ ] Add `clause_ref` for IS 456 clauses
- [ ] Update docstring with `Raises:` section
- [ ] Add unit tests for exceptions
- [ ] Update usage examples in docs
- [ ] Keep old function with deprecation warning (if public API)
- [ ] Update CHANGELOG with migration notes

### 9.4 Documentation Updates

Update docs to show exception-based usage:

```python
# OLD (to be removed)
result, error = design_beam_is456(b_mm=300, d_mm=550, ...)
if error:
    print(f"Error: {error}")
    return
print(f"Steel required: {result.ast_required_mm2:.0f} mm²")

# NEW (recommended)
try:
    result = design_beam_is456(b_mm=300, d_mm=550, ...)
    print(f"Steel required: {result.ast_required_mm2:.0f} mm²")
except ValidationError as e:
    print(f"Input error: {e}")
    print(f"Suggestion: {e.suggestion}")
except DesignError as e:
    print(f"Design failed: {e}")
    print(f"Details: {e.details}")
```

---

## 10. Complete Examples

*(Placeholder - to be added in next step)*

---

## 11. Integration with Logging

*(Placeholder - to be added in next step)*

---

## 12. Performance Considerations

*(Placeholder - to be added in next step)*

---

## Appendix A: Quick Reference Checklist

*(Placeholder - to be added in next step)*

---

## Appendix B: Complete Exception Catalog

*(Placeholder - to be added in next step)*
