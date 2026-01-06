# API Documentation & Discoverability Standard

> **Standard for documentation, docstrings, and API discoverability**
> Created: 2026-01-07 | Status: Active | Part of: API Improvement Research (TASK-206)

---

## Purpose

This document establishes standards for API documentation to ensure:
- **Discoverability**: Users can find functions and understand capabilities without reading source code
- **Clarity**: Documentation explains purpose, usage, and constraints clearly
- **Completeness**: All public APIs have comprehensive, accurate documentation
- **Consistency**: Documentation follows uniform patterns and conventions

**Target audience**: Library developers writing public APIs, docstrings, and examples.

---

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Docstring Standard (Google Style)](#2-docstring-standard-google-style)
3. [Type Hints & Annotations](#3-type-hints--annotations)
4. [Example-Driven Documentation](#4-example-driven-documentation)
5. [IDE Integration & Autocomplete](#5-ide-integration--autocomplete)
6. [Module-Level Documentation](#6-module-level-documentation)
7. [API Reference Generation](#7-api-reference-generation)
8. [Error Documentation](#8-error-documentation)
9. [Code Examples Best Practices](#9-code-examples-best-practices)
10. [Documentation Testing](#10-documentation-testing)

**Appendices:**
- [A: Quick Reference Card](#appendix-a-quick-reference-card)
- [B: Docstring Templates](#appendix-b-docstring-templates)

---

## 1. Core Principles

### 1.1 The Documentation Pyramid

Good API documentation has three levels:

```
                 ┌─────────────────────┐
                 │   Quick Start       │  ← Fastest path to first success
                 │   (1 example)       │
                 └─────────────────────┘
                          ▲
                 ┌─────────────────────┐
                 │   Common Patterns   │  ← 80% of use cases
                 │   (5-10 examples)   │
                 └─────────────────────┘
                          ▲
        ┌────────────────────────────────────┐
        │   Complete Reference              │  ← Every parameter, edge case
        │   (Comprehensive API docs)        │
        └────────────────────────────────────┘
```

**Users start at the top** (quick start) and **drill down as needed** (patterns → reference).

### 1.2 The Four Questions Framework

Every function's documentation must answer:

1. **What does it do?** (One-sentence summary)
2. **When should I use it?** (Use cases, constraints)
3. **How do I use it?** (Parameters, returns, examples)
4. **What can go wrong?** (Exceptions, edge cases, validation)

### 1.3 Write for Three Audiences

| Audience | Needs | Documentation Focus |
|----------|-------|---------------------|
| **Beginner** | Getting started, common patterns | Quick examples, clear explanations, avoid jargon |
| **Intermediate** | Solving specific problems | Use cases, parameter options, common pitfalls |
| **Expert** | Edge cases, performance, internals | Full parameter details, constraints, performance notes |

### 1.4 Documentation as Code

- **Docstrings are part of the API contract** (not optional comments)
- **Examples must be runnable** (tested with doctest or pytest)
- **Documentation failures = code failures** (CI enforces completeness)
- **Keep docs close to code** (docstrings > separate markdown files)

---

## 2. Docstring Standard (Google Style)

### 2.1 Why Google Style?

**Chosen over NumPy/Sphinx styles because:**
- ✅ More readable in plain text (no excessive formatting)
- ✅ Works well with type hints (types in signature, not docstring)
- ✅ Better IDE support (VSCode, PyCharm parse correctly)
- ✅ Widely adopted (Pydantic, FastAPI, Google's internal codebases)

### 2.2 Function Docstring Template

```python
def design_singly_reinforced(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
    *,
    validate: bool = True,
) -> FlexureResult:
    """Design singly reinforced rectangular beam section per IS 456:2000.

    Calculates required tension reinforcement for a rectangular beam section
    subjected to sagging (positive) moment. Checks minimum and maximum steel
    requirements per IS 456 Cl. 26.5.1.1.

    Args:
        b_mm: Beam width in millimeters. Must be ≥ 200mm per IS 456 Cl. 26.5.1.1.
        d_mm: Effective depth in millimeters. Distance from compression face
            to centroid of tension reinforcement.
        mu_kn_m: Factored bending moment in kilonewton-meters. Must be positive
            (sagging moment).
        fck_mpa: Characteristic compressive strength of concrete in megapascals.
            Must be one of [20, 25, 30, 35, 40, 45, 50] per IS 456 Table 2.
        fy_mpa: Characteristic yield strength of steel in megapascals.
            Must be one of [250, 415, 500, 550] per IS 456 Cl. 6.2.
        validate: If True, validate all inputs before calculation. Set to False
            for batch operations where inputs are pre-validated. Default: True.

    Returns:
        FlexureResult with fields:
            - ast_required_mm2: Required tension steel area (mm²)
            - ast_min_mm2: Minimum steel per IS 456 Cl. 26.5.1.1
            - ast_max_mm2: Maximum steel per IS 456 Cl. 26.5.1.1
            - mu_lim_kn_m: Section capacity with xu = xu,max
            - reinforcement_ratio: Ast / (b × d)

    Raises:
        DimensionError: If b_mm < 200mm or d_mm < 150mm
        MaterialError: If fck_mpa or fy_mpa not in standard grades
        LoadError: If mu_kn_m ≤ 0
        DesignError: If mu_kn_m > mu_lim (requires compression steel)
        ComplianceError: If ast_required < ast_min or ast_required > ast_max

    Example:
        >>> from structural_lib import design_singly_reinforced
        >>> result = design_singly_reinforced(
        ...     b_mm=300,
        ...     d_mm=550,
        ...     mu_kn_m=180,
        ...     fck_mpa=30,
        ...     fy_mpa=415,
        ... )
        >>> print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
        Required steel: 1245 mm²

    Note:
        For doubly reinforced sections (compression steel required), use
        design_doubly_reinforced() instead. This function assumes xu ≤ xu,max.

    See Also:
        - design_doubly_reinforced: For sections requiring compression steel
        - calculate_mu_lim: To check section capacity before design
        - FlexureResult: Complete documentation of result object

    References:
        IS 456:2000 Clauses:
        - Cl. 38.1: Limiting depth of neutral axis
        - Cl. 26.5.1.1: Minimum and maximum reinforcement
        - Cl. G-1.1: Design equations (Annex G)
    """
    # Implementation...
```

### 2.3 Docstring Section Rules

#### Summary Line (Required)

**Rules:**
- First line, one sentence, imperative mood ("Calculate" not "Calculates")
- End with period
- < 80 characters
- Describes WHAT the function does, not implementation details

```python
# ✅ GOOD: Clear, actionable, < 80 chars
"""Design singly reinforced beam section per IS 456:2000."""

# ❌ BAD: Too long, passive voice, implementation detail
"""This function is used to calculate the required area of steel reinforcement
for a singly reinforced rectangular beam section using the limit state design
method as specified in IS 456:2000."""

# ❌ BAD: Not imperative mood
"""Designs a beam section."""  # "Design" not "Designs"
```

#### Description (Optional but Recommended)

**When to include:**
- Function is not obvious from name
- Need to explain use cases or context
- Important constraints or assumptions

**Keep it brief:** 2-4 sentences maximum.

```python
"""Design singly reinforced rectangular beam section per IS 456:2000.

Calculates required tension reinforcement for a rectangular beam section
subjected to sagging (positive) moment. Checks minimum and maximum steel
requirements per IS 456 Cl. 26.5.1.1.
"""
```

#### Args Section (Required for functions with parameters)

**Format:**
```
Args:
    param_name: Description. Constraints/units/defaults.
        Additional context on second line (indented).
    another_param: Description...
```

**Rules:**
- List ALL parameters (required + optional)
- Describe constraints (ranges, valid values, units)
- Explain optional parameters and defaults
- Multi-line descriptions indent second+ lines
- Don't repeat type (already in signature)

```python
"""
Args:
    b_mm: Beam width in millimeters. Must be ≥ 200mm per IS 456 Cl. 26.5.1.1.
    d_mm: Effective depth in millimeters. Distance from compression face
        to centroid of tension reinforcement.
    fck_mpa: Characteristic compressive strength of concrete in megapascals.
        Must be one of [20, 25, 30, 35, 40, 45, 50] per IS 456 Table 2.
    validate: If True, validate all inputs before calculation. Set to False
        for batch operations where inputs are pre-validated. Default: True.
"""
```

#### Returns Section (Required for functions that return)

**Format:**
```
Returns:
    Type: Description of what is returned.
        Additional details (fields, structure).
```

**Rules:**
- Describe the return value, not the type (type is in signature)
- For dataclasses/objects: List key fields
- For simple types: Describe value and units

```python
"""
Returns:
    FlexureResult with fields:
        - ast_required_mm2: Required tension steel area (mm²)
        - ast_min_mm2: Minimum steel per IS 456 Cl. 26.5.1.1
        - ast_max_mm2: Maximum steel per IS 456 Cl. 26.5.1.1
        - mu_lim_kn_m: Section capacity with xu = xu,max
        - reinforcement_ratio: Ast / (b × d)
"""

# For simple returns:
"""
Returns:
    Limiting moment capacity in kN·m. This is the maximum moment the
    section can resist with xu = xu,max per IS 456 Cl. 38.1.
"""
```

#### Raises Section (Required if function raises exceptions)

**Format:**
```
Raises:
    ExceptionType: When this exception is raised. Conditions.
    AnotherException: When this is raised.
```

**Rules:**
- List ALL exception types the function can raise
- Explain WHEN each exception is raised
- Order by likelihood (most common first)

```python
"""
Raises:
    DimensionError: If b_mm < 200mm or d_mm < 150mm
    MaterialError: If fck_mpa or fy_mpa not in standard grades
    LoadError: If mu_kn_m ≤ 0
    DesignError: If mu_kn_m > mu_lim (requires compression steel)
    ComplianceError: If ast_required < ast_min or ast_required > ast_max
"""
```

#### Example Section (Highly Recommended)

**Rules:**
- Show REALISTIC usage (not toy examples)
- Use doctest format (>>> prompts)
- Must be runnable (tested in CI)
- Show imports if not obvious
- Include expected output

```python
"""
Example:
    >>> from structural_lib import design_singly_reinforced
    >>> result = design_singly_reinforced(
    ...     b_mm=300,
    ...     d_mm=550,
    ...     mu_kn_m=180,
    ...     fck_mpa=30,
    ...     fy_mpa=415,
    ... )
    >>> print(f"Required steel: {result.ast_required_mm2:.0f} mm²")
    Required steel: 1245 mm²
"""
```

#### Note Section (Optional)

**When to use:**
- Important caveats or assumptions
- Performance considerations
- Behavioral quirks

```python
"""
Note:
    For doubly reinforced sections (compression steel required), use
    design_doubly_reinforced() instead. This function assumes xu ≤ xu,max.

    Performance: For batch operations with 1000+ beams, set validate=False
    and pre-validate inputs to save ~13% execution time.
"""
```

#### See Also Section (Optional)

**When to use:**
- Related functions users might need
- Alternative approaches
- Prerequisite or follow-up functions

```python
"""
See Also:
    - design_doubly_reinforced: For sections requiring compression steel
    - calculate_mu_lim: To check section capacity before design
    - FlexureResult: Complete documentation of result object
"""
```

#### References Section (Optional but Recommended for engineering functions)

**When to use:**
- Code clause references (IS 456, ACI, Eurocode)
- Research papers
- Standard design procedures

```python
"""
References:
    IS 456:2000 Clauses:
    - Cl. 38.1: Limiting depth of neutral axis
    - Cl. 26.5.1.1: Minimum and maximum reinforcement
    - Cl. G-1.1: Design equations (Annex G)
"""
```

---

## 3. Type Hints & Annotations

### 3.1 Type Hints as Documentation

**Type hints ARE documentation** - they appear in IDE tooltips and help users understand parameter types.

```python
# ✅ GOOD: Clear types, users know what to pass
def design_beam(
    b_mm: float,
    d_mm: float,
    mu_kn_m: float,
    fck_mpa: float,
    fy_mpa: float,
) -> FlexureResult:
    ...

# ❌ BAD: No types, users must guess
def design_beam(b_mm, d_mm, mu_kn_m, fck_mpa, fy_mpa):
    ...
```

### 3.2 Advanced Type Annotations

**Use Union for alternative types:**
```python
from typing import Union

def get_reinforcement(
    ast_mm2: float,
    bar_dia_mm: Union[int, list[int]] = 16,  # Single size or multiple
) -> BarArrangement:
    """Get bar arrangement for required steel area.

    Args:
        ast_mm2: Required steel area in mm²
        bar_dia_mm: Bar diameter(s) in mm. Can be single diameter (e.g., 16)
            or list of allowed diameters (e.g., [12, 16, 20]). Default: 16.
    """
```

**Use Literal for constrained choices:**
```python
from typing import Literal

def calculate_stress_block_factor(
    fck_mpa: float,
    code: Literal['IS456', 'ACI318', 'EC2'] = 'IS456',
) -> float:
    """Calculate stress block factor α per design code.

    Args:
        fck_mpa: Concrete strength in MPa
        code: Design code to use. One of 'IS456', 'ACI318', 'EC2'. Default: 'IS456'.
    """
```

**Use Optional for None defaults:**
```python
from typing import Optional

def design_beam(
    ...,
    cover_mm: Optional[float] = None,  # None = use default
) -> FlexureResult:
    """Design beam section.

    Args:
        cover_mm: Clear cover in mm. If None, uses default per IS 456 Table 16
            (25mm for beams in mild exposure). Default: None.
    """
```

### 3.3 Return Type Documentation

**Always annotate return types:**
```python
def calculate_mu_lim(b_mm: float, d_mm: float, fck_mpa: float) -> float:
    """Calculate limiting moment capacity.

    Returns:
        Limiting moment in kN·m.
    """
    # IDE shows: calculate_mu_lim(...) -> float
```

**For complex returns, use dataclasses:**
```python
@dataclass(frozen=True)
class FlexureResult:
    """Result of flexural design calculation."""
    ast_required_mm2: float
    ast_min_mm2: float
    ast_max_mm2: float
    mu_lim_kn_m: float
    reinforcement_ratio: float

def design_flexure(...) -> FlexureResult:
    """Design flexure.

    Returns:
        FlexureResult with design outputs.
    """
    # IDE shows all fields when user types `result.`
```

---

## 4. Example-Driven Documentation

*(To be added in Step 2)*

---

## 5. IDE Integration & Autocomplete

*(To be added in Step 2)*

---

## 6. Module-Level Documentation

*(To be added in Step 2)*

---

## 7. API Reference Generation

*(To be added in Step 2)*

---

## 8. Error Documentation

*(To be added in Step 2)*

---

## 9. Code Examples Best Practices

*(To be added in Step 2)*

---

## 10. Documentation Testing

*(To be added in Step 2)*

---

## Appendix A: Quick Reference Card

*(To be added in Step 2)*

---

## Appendix B: Docstring Templates

*(To be added in Step 2)*
