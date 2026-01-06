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

*(Placeholder - to be added in next step)*

---

## 5. Error Recovery Strategies

*(Placeholder - to be added in next step)*

---

## 6. Exception Context & Debugging

*(Placeholder - to be added in next step)*

---

## 7. Anti-patterns to Avoid

*(Placeholder - to be added in next step)*

---

## 8. Testing Exception Behavior

*(Placeholder - to be added in next step)*

---

## 9. Migration Strategy

*(Placeholder - to be added in next step)*

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
