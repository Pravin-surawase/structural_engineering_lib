# Agent Coding Standards for structural_lib

**Type:** Guide
**Audience:** AI Agents, Developers
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-15
**Related Tasks:** All development tasks

---

## Purpose

This guide ensures AI agents write code that is:
- ✅ Compatible with existing structural_lib code
- ✅ Follows established patterns
- ✅ Passes all validation (tests, lint, type checks)
- ✅ Easy for other agents to understand and modify

**Read this BEFORE writing any code.**

---

## Quick Checklist

```
┌─────────────────────────────────────────────────────────────┐
│  BEFORE WRITING CODE:                                        │
│  □ Read existing similar module for patterns                 │
│  □ Check types.py/data_types.py for existing dataclasses    │
│  □ Verify function doesn't already exist (grep_search)       │
│  □ Understand which layer you're working in                  │
│                                                              │
│  WRITING CODE:                                               │
│  □ Follow 3-layer architecture (Core → App → UI)            │
│  □ Use explicit units (mm, N/mm², kN·m)                      │
│  □ Add type hints to ALL functions                           │
│  □ Write Google-style docstrings (see docstring-style-guide) │
│  □ Reference IS 456 clauses in comments and docstrings       │
│  □ Use existing error types from errors.py                   │
│  □ Return dataclasses, not dicts (for new functions)         │
│  □ Use validate_* functions from validation.py               │
│                                                              │
│  AFTER WRITING CODE:                                         │
│  □ Add unit tests (1 happy path + 2 edge cases minimum)      │
│  □ Run: cd Python && pytest tests/ -v                        │
│  □ Run: ruff check . && ruff format .                        │
│  □ Run: mypy structural_lib/                                 │
│  □ Update __all__ in module's __init__.py                    │
│  □ Update api.py if adding public function                   │
│  □ Commit with: ./scripts/ai_commit.sh "type: message"       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Architecture Rules

### 3-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  UI/I-O Layer                                                │
│  streamlit_app/, excel_integration.py, dxf_export.py        │
│  • External interfaces ONLY                                  │
│  • No calculations here                                      │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                           │
│  api.py, beam_pipeline.py, job_runner.py                    │
│  • Orchestrates core functions                               │
│  • Handles user-facing workflows                             │
│  • No formatting/display logic                               │
├─────────────────────────────────────────────────────────────┤
│  Core Layer                                                  │
│  codes/is456/*.py, errors.py, validation.py                 │
│  • Pure calculation functions                                │
│  • NO I/O (no file reads, no prints)                        │
│  • Explicit units, no assumptions                            │
│  • Self-contained (no upward imports)                        │
└─────────────────────────────────────────────────────────────┘
```

### Import Rules

```python
# ❌ FORBIDDEN: Core importing from Application
# In codes/is456/flexure.py
from structural_lib.api import some_function  # WRONG!

# ❌ FORBIDDEN: Core importing from UI
# In codes/is456/flexure.py
import streamlit as st  # WRONG!

# ✅ CORRECT: Core is self-contained
# In codes/is456/flexure.py
from structural_lib.constants import STEEL_MODULUS
from structural_lib.errors import DesignError
```

---

## 2. File Structure

### New Module Template

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       module_name
Description:  Brief description of what this module does

This module implements IS 456:2000 provisions for [feature].

Key Functions:
    - function_one: Description
    - function_two: Description

References:
    IS 456:2000, Cl. XX (Section Name)
"""

from __future__ import annotations

# Standard library
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Local imports
from structural_lib.errors import DesignError, ValidationError
from structural_lib.validation import validate_positive

if TYPE_CHECKING:
    from structural_lib.types import SomeType


# Constants (module-level, UPPERCASE)
MAX_REINFORCEMENT_RATIO = 0.04  # 4% per IS 456 Cl. 26.5.1


@dataclass(frozen=True)
class ModuleResult:
    """Result container for module calculations.

    Attributes:
        value: Calculated value in [units]
        status: "SAFE" or "FAIL"
        clause_ref: IS 456 clause reference
    """
    value: float
    status: str
    clause_ref: str


def calculate_something(
    param1: float,
    param2: float,
    *,
    optional_param: float = 1.0,
) -> ModuleResult:
    """Calculate something per IS 456.

    Args:
        param1: Description with units
        param2: Description with units
        optional_param: Description with default

    Returns:
        ModuleResult with calculated value and status

    Raises:
        ValidationError: If inputs are invalid
        DesignError: If design fails IS 456 requirements

    References:
        IS 456:2000, Cl. X.Y.Z

    Examples:
        >>> result = calculate_something(300, 450)
        >>> result.status
        'SAFE'
    """
    # Validate inputs
    validate_positive(param1, "param1")
    validate_positive(param2, "param2")

    # Core calculation with IS 456 reference
    # Per IS 456 Cl. X.Y.Z: formula description
    value = param1 * param2 / 1.15

    # Status determination
    limit = 100.0  # Per IS 456 Cl. A.B
    status = "SAFE" if value <= limit else "FAIL"

    return ModuleResult(
        value=value,
        status=status,
        clause_ref="IS 456:2000, Cl. X.Y.Z",
    )


# Module exports
__all__ = ["ModuleResult", "calculate_something"]
```

---

## 3. Naming Conventions

### Functions

```python
# ✅ CORRECT: Verb + noun, snake_case
def calculate_moment_capacity(...)
def check_deflection_limit(...)
def design_beam_flexure(...)
def validate_beam_geometry(...)

# ❌ WRONG
def momentCapacity(...)      # camelCase
def calc_M(...)              # Unclear abbreviation
def beam(...)                # Too vague
```

### Classes

```python
# ✅ CORRECT: PascalCase, descriptive
class FlexureResult:
class BeamDesignOutput:
class ValidationError:

# ❌ WRONG
class flexure_result:        # snake_case
class BDO:                   # Unclear abbreviation
```

### Variables

```python
# ✅ CORRECT: Descriptive with units
width_mm = 300
effective_depth_mm = 450
span_m = 5.0
moment_kNm = 120.0
fck_MPa = 25.0              # or fck_Nmm2
ast_required_mm2 = 804.5
reinforcement_ratio = 0.012  # dimensionless

# ❌ WRONG: Ambiguous units
width = 300                  # mm? m? inches?
M = 120                      # kN·m? N·mm?
```

### Constants

```python
# ✅ CORRECT: UPPERCASE with units in name or comment
STEEL_MODULUS_MPA = 200000   # Es in N/mm²
GAMMA_C = 1.5                # Partial safety factor for concrete
MAX_XU_D_RATIO_FE415 = 0.48  # IS 456 Table 38.1
```

---

## 4. Type Hints

### Required Everywhere

```python
# ✅ CORRECT: Full type hints
def calculate_ast(
    moment: float,
    width: float,
    depth: float,
    fck: float,
    fy: float,
) -> float:
    ...

# ❌ WRONG: Missing type hints
def calculate_ast(moment, width, depth, fck, fy):
    ...
```

### Common Patterns

```python
from typing import Any, Literal, TypeAlias
from collections.abc import Sequence

# Literal for fixed choices
SteelGrade: TypeAlias = Literal[250, 415, 500]
Status: TypeAlias = Literal["SAFE", "FAIL", "WARNING"]

# Optional with default
def func(value: float, option: str = "default") -> float:
    ...

# Multiple return types (prefer dataclass instead)
def func(...) -> tuple[float, str]:
    ...

# Sequences
def func(values: Sequence[float]) -> list[float]:
    ...
```

---

## 5. Docstrings

### Google Style (Required)

```python
def calculate_mu_lim(
    b: float,
    d: float,
    fck: float,
    fy: float,
) -> float:
    """Calculate limiting moment of resistance.

    Computes Mu_lim for singly reinforced rectangular section
    using balanced section properties per IS 456.

    Args:
        b: Width of beam in mm (must be > 0)
        d: Effective depth in mm (must be > 0)
        fck: Characteristic concrete strength in N/mm² (15-100)
        fy: Yield strength of steel in N/mm² (250, 415, 500)

    Returns:
        Limiting moment of resistance in kN·m

    Raises:
        ValidationError: If any input is non-positive
        ValueError: If fck or fy is outside valid range

    References:
        IS 456:2000, Cl. 38.1 (Limiting Moment of Resistance)
        SP 16:1980, Table 2

    Examples:
        >>> mu_lim = calculate_mu_lim(300, 450, 25, 415)
        >>> print(f"{mu_lim:.2f}")
        186.75
    """
```

### Key Sections

| Section | Required? | When to Use |
|---------|-----------|-------------|
| Summary line | ✅ Always | First line, imperative mood |
| Extended description | Optional | Complex functions |
| Args | ✅ If parameters exist | Include units |
| Returns | ✅ If returns value | Include units |
| Raises | ✅ If can raise | List all exceptions |
| References | Recommended | IS 456 clause citations |
| Examples | Recommended | Public API functions |

---

## 6. Error Handling

### Use Existing Error Types

```python
from structural_lib.errors import (
    DesignError,
    ErrorCode,
    ErrorSeverity,
    ValidationError,
    StructuralLibError,
)
from structural_lib.error_messages import (
    dimension_too_small,
    capacity_exceeded,
    reinforcement_exceeds_limit,
)
```

### Validation Pattern

```python
from structural_lib.validation import (
    validate_positive,
    validate_in_range,
    validate_material_grade,
)

def my_function(width: float, fck: float) -> float:
    # Use existing validators - they raise ValidationError
    validate_positive(width, "width")
    validate_in_range(fck, 15, 100, "fck")

    # Continue with calculation...
```

### Design Error Pattern

```python
from structural_lib.errors import DesignError, ErrorCode, ErrorSeverity

def check_reinforcement(ast: float, ast_max: float) -> None:
    if ast > ast_max:
        raise DesignError(
            code=ErrorCode.E_FLEXURE_003,
            severity=ErrorSeverity.ERROR,
            message=f"Reinforcement {ast:.1f} mm² exceeds maximum {ast_max:.1f} mm²",
            suggestions=[
                "Increase beam depth",
                "Use higher concrete grade",
                "Consider doubly reinforced section",
            ],
            clause_ref="IS 456:2000, Cl. 26.5.1",
        )
```

### Never Create New Exception Types

```python
# ❌ WRONG: Custom exception
class MyBeamError(Exception):
    pass

# ✅ CORRECT: Use existing hierarchy
from structural_lib.errors import DesignError
```

---

## 7. Testing

### Test File Location

```
Python/
├── structural_lib/
│   └── new_module.py
└── tests/
    └── test_new_module.py    # Same name with test_ prefix
```

### Test Structure

```python
# tests/test_new_module.py
"""Tests for new_module."""

import pytest
from structural_lib.new_module import calculate_something, SomeResult
from structural_lib.errors import ValidationError, DesignError


class TestCalculateSomething:
    """Tests for calculate_something function."""

    def test_nominal_case(self):
        """Test with typical input values (happy path)."""
        result = calculate_something(300, 450)

        assert isinstance(result, SomeResult)
        assert result.value > 0
        assert result.status == "SAFE"
        assert "IS 456" in result.clause_ref

    def test_edge_case_minimum_values(self):
        """Test with minimum valid inputs."""
        result = calculate_something(100, 100)
        assert result.status == "SAFE"

    def test_edge_case_maximum_values(self):
        """Test near upper limits."""
        result = calculate_something(1000, 1000)
        # Verify behavior at limits

    def test_invalid_negative_input(self):
        """Test that negative inputs raise ValidationError."""
        with pytest.raises(ValidationError):
            calculate_something(-1, 450)

    def test_invalid_zero_input(self):
        """Test that zero inputs raise ValidationError."""
        with pytest.raises(ValidationError):
            calculate_something(300, 0)

    def test_design_failure_case(self):
        """Test when design fails requirements."""
        result = calculate_something(50, 50)  # Undersized
        assert result.status == "FAIL"
```

### Minimum Test Coverage

| Function Type | Minimum Tests |
|---------------|---------------|
| Public API function | 5+ tests |
| Core calculation | 3+ tests |
| Validation helper | 2+ tests |
| Private helper | 1+ tests |

### Running Tests

```bash
cd Python

# Run all tests
pytest tests/ -v

# Run specific module tests
pytest tests/test_new_module.py -v

# Run with coverage
pytest tests/ --cov=structural_lib --cov-report=html
```

---

## 8. Import Order

```python
# 1. Future imports (always first)
from __future__ import annotations

# 2. Standard library (alphabetical)
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

# 3. Third-party (alphabetical)
import numpy as np
from pydantic import BaseModel

# 4. Local imports - absolute paths (alphabetical)
from structural_lib.constants import STEEL_MODULUS
from structural_lib.errors import DesignError
from structural_lib.validation import validate_positive

# 5. Type checking only imports
if TYPE_CHECKING:
    from structural_lib.types import BeamGeometry
```

---

## 9. Common Patterns

### Calculation with Clause Reference

```python
def calculate_xu_max(d: float, fy: float) -> float:
    """Calculate maximum neutral axis depth.

    Per IS 456:2000, Cl. 38.1, Table 38.1
    """
    # Neutral axis depth ratio from Table 38.1
    xu_d_ratios = {
        250: 0.53,
        415: 0.48,
        500: 0.46,
    }

    ratio = xu_d_ratios.get(int(fy))
    if ratio is None:
        raise ValueError(f"Unsupported steel grade: {fy}")

    # xu_max = (xu/d) × d
    return ratio * d
```

### Result Dataclass

```python
@dataclass(frozen=True)
class FlexureResult:
    """Result of flexural design calculation.

    Attributes:
        ast_required: Required tension steel area in mm²
        ast_min: Minimum steel per IS 456 Cl. 26.5.1.1 in mm²
        ast_max: Maximum steel per IS 456 Cl. 26.5.1.1 in mm²
        mu_capacity: Moment capacity in kN·m
        status: "SAFE" if design is adequate, "FAIL" otherwise
        utilization: Mu/Mu_capacity ratio (0 to 1+)
        warnings: List of design warnings
        clause_refs: IS 456 clauses used
    """
    ast_required: float
    ast_min: float
    ast_max: float
    mu_capacity: float
    status: str
    utilization: float
    warnings: list[str]
    clause_refs: list[str]
```

### Optional Parameters

```python
def design_beam(
    width: float,
    depth: float,
    moment: float,
    *,  # Force keyword-only after this
    fck: float = 25.0,
    fy: float = 500.0,
    cover: float = 40.0,
    include_suggestions: bool = False,
) -> BeamResult:
    """Design beam with sensible defaults.

    Args:
        width: Beam width in mm
        depth: Beam overall depth in mm
        moment: Design moment in kN·m
        fck: Concrete grade in N/mm² (default: 25)
        fy: Steel grade in N/mm² (default: 500)
        cover: Clear cover in mm (default: 40)
        include_suggestions: Whether to include improvement suggestions
    """
```

---

## 10. Validation Commands

### Before Committing

```bash
cd Python

# 1. Run tests
pytest tests/ -v

# 2. Check linting
ruff check .

# 3. Format code
ruff format .

# 4. Type check
mypy structural_lib/

# 5. If adding Streamlit code
cd ..
.venv/bin/python scripts/check_streamlit_issues.py --all-pages
.venv/bin/python scripts/check_fragment_violations.py
```

### All-in-One

```bash
# From project root
cd Python && pytest tests/ -v && ruff check . && ruff format . && mypy structural_lib/
```

---

## 11. Adding to Public API

### Steps

1. **Create function in appropriate module** (core layer)
2. **Add to module's `__all__`**
3. **Import and re-export from `api.py`**
4. **Add to `api.py`'s `__all__`**
5. **Update API documentation** if needed

### Example

```python
# 1. In codes/is456/new_feature.py
__all__ = ["new_function", "NewResult"]

# 2. In api.py (imports section)
from .codes.is456.new_feature import new_function, NewResult

# 3. In api.py (__all__ list)
__all__ = [
    # ... existing exports ...
    "new_function",
    "NewResult",
]
```

---

## Quick Reference Card

```
╔═══════════════════════════════════════════════════════════════╗
║  structural_lib Coding Standards - Quick Reference            ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  ARCHITECTURE                                                 ║
║  • Core layer: NO I/O, NO upward imports                      ║
║  • Units: ALWAYS explicit (mm, N/mm², kN·m)                   ║
║                                                               ║
║  NAMING                                                       ║
║  • Functions: calculate_*, check_*, validate_*, design_*      ║
║  • Classes: PascalCase (FlexureResult)                        ║
║  • Variables: width_mm, moment_kNm (include units)            ║
║                                                               ║
║  FUNCTIONS                                                    ║
║  • Type hints on ALL parameters and return                    ║
║  • Google-style docstrings with Args, Returns, Raises         ║
║  • IS 456 clause references in docstrings                     ║
║                                                               ║
║  ERRORS                                                       ║
║  • Use validate_* from validation.py                          ║
║  • Use DesignError from errors.py                             ║
║  • NEVER create new exception types                           ║
║                                                               ║
║  TESTING                                                      ║
║  • 1 happy path + 2 edge cases minimum                        ║
║  • Test file: tests/test_<module>.py                          ║
║                                                               ║
║  VALIDATION                                                   ║
║  • pytest tests/ -v                                           ║
║  • ruff check . && ruff format .                              ║
║  • mypy structural_lib/                                       ║
║                                                               ║
║  COMMIT                                                       ║
║  • ./scripts/ai_commit.sh "type: description"                 ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Related Documents

- [Docstring Style Guide](docstring-style-guide.md)
- [Naming Conventions](naming-conventions.md)
- [Testing Strategy](testing-strategy.md)
- [Git Workflow for AI Agents](git-workflow-ai-agents.md)
