# Docstring Style Guide

> **Purpose:** Standard docstring format for all Python modules in structural_lib
> **Style:** Google Style (readable, widely adopted in scientific Python)
> **Enforcement:** Manual review + ruff (future: pydocstyle integration)

---

## Quick Reference

```python
def function_name(arg1: type1, arg2: type2) -> return_type:
    """One-line summary ending with period.

    Optional longer description providing context, assumptions, and important
    details. Can span multiple paragraphs.

    Args:
        arg1: Description of arg1 (units if applicable)
        arg2: Description of arg2 (units if applicable)

    Returns:
        Description of return value (units if applicable)

    Raises:
        ErrorType: When this error occurs

    References:
        IS 456:2000, Cl. X.Y.Z
        SP 16:1980, Section A.B

    Examples:
        >>> result = function_name(300, 450)
        >>> print(result)
        123.45
    """
```

---

## Rules

### 1. All Public Functions Must Have Docstrings

**✅ Required for:**
- All public API functions (`api.py`)
- All exported calculation functions
- All user-facing CLI commands

**⚠️ Optional but recommended:**
- Private helper functions (prefix with `_`)
- Simple property getters

### 2. Docstring Components

#### Summary Line (Required)
- **One line**, ends with period
- Imperative mood: "Calculate..." not "Calculates..."
- Max 79 characters
- No argument names in summary

```python
# ✅ Good
"""Calculate limiting moment of resistance."""

# ❌ Bad
"""Calculates the limiting moment of resistance for the given beam"""  # Too long
"""This function calculates Mu_lim"""  # Not imperative
```

#### Extended Description (Optional)
- Blank line after summary
- Explain context, assumptions, limitations
- Reference IS 456 clauses when relevant

#### Args Section (Required if function has parameters)
- Format: `name: Description (units if applicable)`
- Include units for physical quantities
- Explain constraints/valid ranges

```python
Args:
    b: Width of rectangular beam in mm (must be > 0)
    d: Effective depth in mm (must be > 0)
    fck: Characteristic compressive strength in N/mm² (15-100)
    fy: Yield strength of steel in N/mm² (250, 415, or 500)
```

#### Returns Section (Required if function returns value)
- Describe what is returned
- Include units for physical quantities
- For tuples: describe each element

```python
Returns:
    Limiting moment of resistance in kN·m

Returns:
    Tuple of (Ast_required in mm², reinforcement_ratio as decimal)
```

#### Raises Section (Required if function raises exceptions)
- List exception types and conditions

```python
Raises:
    ValueError: If b, d, fck, or fy is non-positive
    DesignError: If reinforcement exceeds maximum ratio (E_FLEXURE_003)
```

#### References Section (Optional but recommended)
- Cite IS 456:2000 clauses
- Include SP 16, SP 34, or other standards
- Reference external papers/books if applicable

```python
References:
    IS 456:2000, Cl. 38.1 (Limiting Moment of Resistance)
    IS 456:2000, Cl. 40.1 (Maximum and Minimum Reinforcement)
    SP 16:1980, Design Aids for Reinforced Concrete
```

#### Examples Section (Optional but helpful for complex functions)
```python
Examples:
    >>> from structural_lib import api
    >>> result = api.calculate_mu_lim(b=300, d=450, fck=25, fy=415)
    >>> print(f"{result:.2f}")
    186.75
```

---

## Module Docstrings

Every module should have a docstring at the top:

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       flexure
Description:  Flexural design and analysis functions

This module implements IS 456:2000 provisions for flexural design of RC beams,
including singly reinforced, doubly reinforced, and flanged sections.

Key Functions:
    - calculate_mu_lim: Limiting moment of resistance
    - calculate_ast_required: Tension reinforcement calculation
    - calculate_asc_required: Compression reinforcement calculation

References:
    IS 456:2000, Cl. 38 (Limit State of Collapse - Flexure)
"""
```

---

## Class Docstrings

```python
class DesignResult:
    """Container for beam design calculation results.

    Attributes:
        Mu_lim: Limiting moment in kN·m
        Ast_req: Required tension steel in mm²
        num_bars: Number of bars required
        bar_dia: Bar diameter in mm
        status: "SAFE" or "FAIL"

    Examples:
        >>> result = DesignResult(Mu_lim=180.5, Ast_req=1200, ...)
        >>> print(result.status)
        SAFE
    """
```

---

## Units Convention

**Always specify units in docstrings:**

| Quantity | Unit | Symbol |
|----------|------|--------|
| Length | mm | mm |
| Area | mm² | mm² |
| Force | kN | kN |
| Moment | kN·m | kN·m |
| Stress | N/mm² | N/mm² |
| Ratio | dimensionless | (as decimal, not %) |

**Examples:**
```python
Args:
    b: Width in mm
    fck: Concrete strength in N/mm²
    moment: Applied moment in kN·m
    rho: Reinforcement ratio (as decimal, e.g., 0.012 for 1.2%)
```

---

## Common Patterns

### 1. Calculation Functions (Core Layer)

```python
def calculate_xu_max_d(fy: float) -> float:
    """Calculate maximum neutral axis depth ratio.

    Args:
        fy: Yield strength of steel in N/mm² (250, 415, or 500)

    Returns:
        xu_max/d ratio (dimensionless)

    References:
        IS 456:2000, Cl. 38.1, Table 38.1
    """
```

### 2. Validation Functions

```python
def validate_beam_geometry(b: float, d: float, D: float) -> None:
    """Validate beam geometric dimensions.

    Args:
        b: Width in mm
        d: Effective depth in mm
        D: Overall depth in mm

    Raises:
        ValueError: If b, d, or D is non-positive
        ValueError: If d >= D (effective depth must be less than overall depth)
    """
```

### 3. API Functions (High-Level)

```python
def design_beam(
    b: float,
    d: float,
    fck: float,
    fy: float,
    moment: float,
    beam_type: str = "rectangular"
) -> dict:
    """Design RC beam for given loading and material properties.

    Performs complete flexural design per IS 456:2000, including:
    - Moment capacity check
    - Reinforcement calculation
    - Detailing requirements
    - Ductility checks

    Args:
        b: Width in mm
        d: Effective depth in mm
        fck: Concrete grade in N/mm² (15-100)
        fy: Steel grade in N/mm² (250, 415, or 500)
        moment: Design moment in kN·m
        beam_type: "rectangular" or "flanged" (default: "rectangular")

    Returns:
        Dictionary with keys:
            - Ast_req: Required tension steel in mm²
            - num_bars: Number of bars
            - bar_dia: Bar diameter in mm
            - status: "SAFE" or "FAIL"
            - utilization: Moment utilization ratio (0-1)

    Raises:
        ValueError: If input parameters are invalid
        DesignError: If design fails IS 456 requirements

    References:
        IS 456:2000, Cl. 38 (Flexure), Cl. 26 (Detailing)

    Examples:
        >>> result = design_beam(300, 450, 25, 415, 120)
        >>> print(result['status'])
        SAFE
        >>> print(f"Required steel: {result['Ast_req']:.0f} mm²")
        Required steel: 850 mm²
    """
```

---

## Enforcement

### During Development
1. **Write docstrings as you code** - don't defer
2. **Run `ruff check`** to catch missing docstrings (future: add D rules)
3. **Peer review** - check docstrings in PR reviews

### Pre-Commit
Currently: Manual review
Future (v1.0): Add pydocstyle/ruff docstring rules (D1**, D2**, D3**)

### CI
Future (v1.0): Fail CI if public functions lack docstrings

---

## Migration Plan

### Phase 1: High-Traffic Modules (TASK-189 - Current)
- ✅ `api.py` - All public functions
- ✅ `report.py` - Report generation functions
- ✅ `dxf_export.py` - DXF export functions

### Phase 2: Core Calculations (v0.15)
- `flexure.py` - All public calculation functions
- `shear.py` - All public calculation functions
- `detailing.py` - All public detailing functions

### Phase 3: Complete Coverage (v1.0)
- All remaining public functions
- Add pydocstyle enforcement to CI
- Generate API docs from docstrings

---

## Tools

### Check Docstring Coverage
```bash
# Using interrogate (install: pip install interrogate)
interrogate -v Python/structural_lib

# Target: 100% coverage for public functions in v1.0
```

### Generate API Docs
```bash
# Using pdoc (install: pip install pdoc)
pdoc --html --output-dir docs/api Python/structural_lib
```

---

## References

- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [NumPy Docstring Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- [interrogate Documentation](https://interrogate.readthedocs.io/)

---

**Last Updated:** 2026-01-06 (TASK-189)
