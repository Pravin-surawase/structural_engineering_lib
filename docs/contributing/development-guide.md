# IS 456 RC Beam Design Library — Development Guide

**Type:** Guide
**Audience:** Developers
**Status:** Approved
**Importance:** High
**Version:** 0.16.6
**Created:** 2025-06-01
**Last Updated:** 2026-01-15<br>
**Related Tasks:** IMPL-003
**Tags:** contributing, development, vba, python, standards

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [VBA Coding Standards](#3-vba-coding-standards)
4. [Python Coding Standards](#4-python-coding-standards)
5. [Naming Conventions](#5-naming-conventions)
6. [Units and Conversions](#6-units-and-conversions)
7. [Input Validation](#7-input-validation)
8. [Error Handling](#8-error-handling)
9. [Documentation Standards](#9-documentation-standards)
10. [Testing Guidelines](#10-testing-guidelines)
11. [Version Control and Git Workflow](#11-version-control-and-git-workflow)
12. [Versioning and Governance](#12-versioning-and-governance)
13. [Packaging and Distribution](#13-packaging-and-distribution)
14. [Code Review Checklist](#14-code-review-checklist)
15. [Common Pitfalls to Avoid](#15-common-pitfalls-to-avoid)
16. [Release Checklist and Quality Gates](#16-release-checklist-and-quality-gates)

---

## 1. Overview

### 1.1 Purpose of This Guide

This document establishes the coding standards, conventions, and workflows for developing and maintaining the IS 456 RC Beam Design Library. Following these guidelines ensures:

- **Consistency** across VBA and Python implementations
- **Portability** — code works in any Excel workbook or Python environment
- **Maintainability** — easy to understand, modify, and extend
- **Reliability** — thorough testing and validation
- **Traceability** — clear references to IS 456 clauses

### 1.2 Core Principles

| Principle | Description |
|-----------|-------------|
| **Pure Functions** | Functions receive inputs, return outputs — no side effects, no hidden state |
| **No UI Dependencies** | No MsgBox, InputBox, ActiveSheet, Range, Cells — pure calculations only |
| **Strict Units** | All inputs/outputs use documented units (mm, N/mm², kN, kN·m) |
| **Fail Fast** | Validate inputs early, return structured errors immediately |
| **Code = Documentation** | IS 456 clause references in comments; self-documenting names |

### 1.3 Language Parity

The VBA and Python implementations must:
- Have **identical public API signatures** (adjusted for language conventions)
- Use **identical formulas and logic**
- Produce **identical results** for the same inputs
- Share **identical test cases**

### 1.4 Supported Environments
- **Excel/VBA:** Office 2016+ (Windows and Mac), 64-bit preferred. Avoid Windows-only APIs.
- **Python:** 3.9+ (target 3.9–3.12). No hard dependencies beyond standard library unless documented.
- **OS:** Windows/macOS supported; avoid platform-specific file paths in code.
- **Rounding/tolerances:** Default to 3 decimal places for stresses and capacities when reporting; see Testing Guidelines for numeric tolerances.

---

## 2. Project Structure

### 2.1 Directory Layout

```
structural_engineering_lib/
├── docs/
│   ├── README.md                   ← Docs index (start here)
│   ├── getting-started/            ← Quickstart guides
│   ├── reference/                  ← API, formulas, troubleshooting
│   ├── contributing/               ← This document lives here
│   ├── architecture/               ← Project structure, design decisions
│   ├── planning/                   ← Roadmaps, research notes
│   └── verification/               ← Test examples, benchmark data
│
├── VBA/
│   ├── Modules/                    ← Core library (.bas files)
│   │   ├── M01_Constants.bas
│   │   ├── M02_Types.bas
│   │   ├── M03_Tables.bas
│   │   ├── M04_Utilities.bas
│   │   ├── M05_Materials.bas
│   │   ├── M06_Flexure.bas
│   │   ├── M07_Shear.bas
│   │   ├── M08_API.bas
│   │   ├── M09_UDFs.bas
│   │   └── M10_Ductile.bas
│   ├── Examples/
│   │   └── Example_Usage.bas
│   └── Tests/
│       └── Test_Structural.bas
│
├── Python/
│   ├── structural_lib/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── types.py
│   │   ├── tables.py
│   │   ├── utilities.py
│   │   ├── materials.py
│   │   ├── flexure.py
│   │   ├── shear.py
│   │   ├── ductile.py
│   │   └── api.py
│   ├── tests/
│   │   ├── test_structural.py
│   │   ├── test_ductile.py
│   │   └── ...
│   ├── examples/
│   ├── pyproject.toml
│   ├── setup.cfg
│   └── requirements.txt
│
├── CHANGELOG.md
├── LICENSE
└── README.md
```

### 2.2 Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `M01_Constants` | Version info, unit conversion constants, code limits |
| `M02_Types` | User-Defined Types (FlexureResult, ShearResult, enums) |
| `M03_Tables` | Table 19, Table 20 data; lookup and interpolation functions |
| `M04_Utilities` | Validation, linear interpolation, clamping, unit conversion |
| `M05_Materials` | Concrete/steel grade validation and properties |
| `M06_Flexure` | Flexural design calculations (Mu_limit, Ast, etc.) |
| `M07_Shear` | Shear design calculations (tau_v, tau_c, stirrups, etc.) |
| `M08_API` | Public façade functions that orchestrate internal modules |
| `M09_UDFs` | Worksheet function wrappers (VBA only) |
| `M10_Ductile` | IS 13920 Ductile Detailing checks |

---

## 3. VBA Coding Standards

### 3.1 Module Header

Every VBA module must start with:

```vba
Attribute VB_Name = "IS456_ModuleName"
'===============================================================================
' IS456_ModuleName.bas
' Part of: IS 456 RC Beam Design Library
' Version: 0.9.1
' Purpose: [Brief description]
'
' References: IS 456:2000, SP:16-1980
' Author: [Your name/team]
' Last Modified: [Date]
'===============================================================================
Option Explicit
```

### 3.2 Option Explicit (Mandatory)

**Every module must have `Option Explicit`** at the top, immediately after the header comment.

```vba
Option Explicit  ' Forces explicit variable declaration
```

This catches typos at compile time instead of runtime.

### 3.3 Option Private Module

For internal-only modules (not exposed to other workbooks):

```vba
Option Explicit
Option Private Module  ' Hides module from Object Browser in other projects
```

### 3.4 Variable Declarations

```vba
' GOOD: Explicit types, meaningful names
Dim Mu_Nmm As Double          ' Moment in N·mm (internal units)
Dim pt_percent As Double      ' Tension steel percentage
Dim fck_index As Long         ' Index into table array

' BAD: Variant, single letters, no suffix
Dim x                         ' Variant - avoid!
Dim m                         ' What is m? Moment? Mass?
Dim i As Integer              ' Use Long instead of Integer
```

### 3.5 Use Long Instead of Integer

VBA's `Integer` is 16-bit (-32,768 to 32,767). Always use `Long` (32-bit) for integer values:

```vba
Dim i As Long           ' GOOD
Dim count As Long       ' GOOD
Dim legs As Long        ' GOOD

Dim i As Integer        ' AVOID - can overflow
```

### 3.6 Avoid Variant

`Variant` is slow and hides type errors. Use explicit types:

```vba
Dim value As Double     ' GOOD
Dim result As FlexureResult  ' GOOD

Dim value As Variant    ' AVOID unless absolutely necessary
```

### 3.7 Constants

Use `Const` for fixed values; use `Public Const` in the Constants module:

```vba
' In IS456_Constants.bas
Public Const kN_TO_N As Double = 1000
Public Const kNm_TO_Nmm As Double = 1000000
Public Const LIB_VERSION As String = "0.9.1"

' Private constants within a module
Private Const MAX_PT_PERCENT As Double = 3#
Private Const MIN_PT_PERCENT As Double = 0.15
```

### 3.8 Function Structure

```vba
'-------------------------------------------------------------------------------
' FunctionName
' Purpose: [What the function does]
'
' Inputs:
'   param1 - [Description] (units)
'   param2 - [Description] (units)
'
' Returns:
'   [Description] (units)
'   Returns -1 if [error condition]
'
' Reference: IS 456:2000, Clause X.X.X / Table X
'-------------------------------------------------------------------------------
Public Function FunctionName( _
    param1 As Double, _
    param2 As Double _
) As Double

    ' --- Input validation ---
    If param1 <= 0 Then
        FunctionName = -1
        Exit Function
    End If

    ' --- Unit conversion (if needed) ---
    Dim param1_internal As Double
    param1_internal = param1 * kNm_TO_Nmm

    ' --- Core calculation ---
    ' [Formula implementation with comments]

    ' --- Return result ---
    FunctionName = result

End Function
```

### 3.9 Line Continuation

Use `_` for long lines, align parameters:

```vba
Public Function IS456_FlexureDesign( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    D_mm As Double, _
    fck As Double, _
    fy As Double _
) As FlexureResult
```

### 3.10 Comments

```vba
' Single-line comment for brief notes

' Multi-line comments for explanations:
' This implements the IS 456 formula for limiting moment.
' The factor 0.36 comes from the parabolic-rectangular stress block.

' Inline comments after code (sparingly)
xu_max = k * d  ' Limiting neutral axis depth (mm)
```

---

## 4. Python Coding Standards

### 4.1 Module Header

```python
"""
IS 456 RC Beam Design Library - Module Name

Purpose: [Brief description]
References: IS 456:2000, SP:16-1980

Author: [Your name/team]
Version: 0.9.1
"""

from __future__ import annotations
from typing import NamedTuple
from dataclasses import dataclass
```

### 4.2 Type Hints (Mandatory)

All functions must have type hints:

```python
def ast_singly_is456(
    mu_knm: float,
    b_mm: float,
    d_mm: float,
    fck_nmm2: float,
    fy_nmm2: float
) -> float:
    """Calculate required tension steel for singly reinforced beam."""
    ...
```

### 4.3 Dataclasses for Result Types

```python
from dataclasses import dataclass

@dataclass
class FlexureResult:
    """Result of flexural design calculation."""
    ast_required: float      # Required tension steel (mm²)
    ast_min: float           # Minimum steel (mm²)
    ast_max: float           # Maximum steel (mm²)
    xu: float                # Actual neutral axis depth (mm)
    xu_max: float            # Limiting neutral axis depth (mm)
    mu_lim: float            # Limiting moment capacity (kN·m)
    is_doubly_reinforced: bool
    design_status: str       # "OK", "DOUBLY_REQUIRED", "ERROR"
    error_message: str
```

### 4.4 Docstrings (Google Style)

```python
def tau_c_is456(fck: float, pt_percent: float) -> float:
    """
    Get design shear strength of concrete from IS 456 Table 19.

    Uses linear interpolation for intermediate pt values.
    Clamps pt to valid range [0.15%, 3.0%].

    Args:
        fck: Characteristic compressive strength of concrete (N/mm²).
            Valid values: 15, 20, 25, 30, 35, 40.
        pt_percent: Percentage of tension reinforcement (%).

    Returns:
        Design shear strength τc (N/mm²).

    Raises:
        ValueError: If fck is not a valid concrete grade.

    Reference:
        IS 456:2000, Table 19

    Example:
        >>> tau_c_is456(20, 1.0)
        0.62
    """
    ...
```

### 4.5 Import Order

```python
# Standard library
import math
from typing import Optional, Tuple

# Third-party
import numpy as np  # Only if needed

# Local
from .constants import kN_TO_N, kNm_TO_Nmm
from .types import FlexureResult, ShearResult
from .tables import get_tau_c, get_tau_c_max
```

### 4.6 Constants

```python
# constants.py

# Unit conversions
KN_TO_N: float = 1000.0
KNM_TO_NMM: float = 1_000_000.0
M_TO_MM: float = 1000.0

# Version info
LIB_VERSION: str = "0.9.1"
LIB_BUILD_DATE: str = "2025-12-25"
IS456_CODE_YEAR: str = "2000"

# Code limits
MAX_PT_PERCENT: float = 3.0
MIN_PT_PERCENT: float = 0.15
```

---

## 5. Naming Conventions

### 5.1 Summary Table

| Element | VBA | Python | Example |
|---------|-----|--------|---------|
| Module/File | `M06_Flexure.bas` | `flexure.py` | — |
| Public Function | `PascalCase` | `snake_case` | `Design_Beam_IS456` / `design_beam_is456` |
| Private Function | `PascalCase` | `_snake_case` | `Get_Tau_C` / `_get_tau_c` |
| Constant | `ALL_CAPS` | `ALL_CAPS` | `kN_TO_N` / `kN_TO_N` |
| Type/Class | `PascalCase` | `PascalCase` | `FlexureResult` |
| Enum | `PascalCase` | `PascalCase` | `IS456_ErrorCode` / `ErrorCode` |
| Variable | `camelCase` or descriptive | `snake_case` | `Mu_kNm` / `mu_knm` |

### 5.2 Nomenclature Glossary

Use these abbreviations consistently in code and docs.

| Term | Meaning | Units/Notes |
|------|---------|-------------|
| Mu | Factored bending moment | kN·m (input), N·mm internal |
| Vu | Factored shear force | kN (input), N internal |
| Ast | Area of tension reinforcement | mm² |
| Asc | Area of compression reinforcement | mm² |
| Asv | Area of shear reinforcement | mm² |
| fck | Characteristic compressive strength of concrete | N/mm² |
| fy | Yield strength of steel | N/mm² |
| b | Beam width | mm |
| D | Overall depth | mm |
| d | Effective depth | mm |
| xu / xu_max | Neutral axis depth / maximum depth | mm |
| pt | Tension steel percentage | % |
| tv / tc | Nominal shear stress / concrete shear capacity | N/mm² |
| Ld | Development length | mm |
| BBS | Bar Bending Schedule | Acronym |
| DXF | Drawing Exchange Format | Acronym |

Notes:
- Use **IS 456** in prose; use **IS456** only in identifiers.
- Use **kN·m** in prose; use `_knm` in identifiers (e.g., `mu_knm`).
- Use **N/mm²** in prose; use `_nmm2` in identifiers (e.g., `fck_nmm2`).

### 5.3 Parameter Naming with Units

Always suffix **boundary/API** parameters with units. Core/internal helpers may omit
suffixes if units are documented in the docstring.

Unit suffix conventions:
- `_mm`, `_kn`, `_knm`, `_nmm2`, `_mm2`, `_percent`

```vba
' VBA
Mu_kNm As Double        ' Moment in kN·m
b_mm As Double          ' Width in mm
Vu_kN As Double         ' Shear in kN
fck_Nmm2 As Double      ' Concrete strength in N/mm²
fy_Nmm2 As Double       ' Steel strength in N/mm²
tau_Nmm2 As Double      ' Stress in N/mm²
Ast_mm2 As Double       ' Area in mm²
```

```python
# Python
mu_knm: float           # Moment in kN·m
b_mm: float             # Width in mm
vu_kn: float            # Shear in kN
fck_nmm2: float         # Concrete strength in N/mm²
fy_nmm2: float          # Steel strength in N/mm²
tau_nmm2: float         # Stress in N/mm²
ast_mm2: float          # Area in mm²
```

### 5.4 Function Naming Patterns

| Pattern | Usage | Python Example | VBA Example |
|---------|-------|----------------|-------------|
| `calculate_*` | Deterministic formula output | `calculate_mu_lim` | `Calculate_Mu_Lim` |
| `check_*` | Compliance/boolean check | `check_shear_limit` | `Check_Shear_Limit` |
| `design_*` | Full design routine | `design_beam_is456` | `Design_Beam_IS456` |
| `compute_*` | Orchestration wrapper | `compute_detailing` | `Compute_Detailing` |
| `get_*` | Lookup/constant retrieval | `get_tau_c` | `Get_Tau_C` |
| `validate_*` | Input validation | `validate_geometry` | `Validate_Geometry` |
| `export_*` / `load_*` | I/O boundaries only | `export_bbs` | `Export_BBS` |

### 5.5 Avoid These Names

```vba
' BAD: Ambiguous or too short
Dim M As Double         ' Moment? Mass? What unit?
Dim A As Double         ' Area? What?
Dim x As Double         ' Too generic

' GOOD: Clear and explicit
Dim Mu_kNm As Double    ' Factored moment in kN·m
Dim Ast_mm2 As Double   ' Tension steel area in mm²
Dim xu_mm As Double     ' Neutral axis depth in mm
```

---

## 6. Units and Conversions

### 6.1 Standard Units

| Quantity | Input/Output Unit | Internal Unit |
|----------|-------------------|---------------|
| Length, depth, cover | mm | mm |
| Bar diameter | mm | mm |
| Concrete strength fck | N/mm² (MPa) | N/mm² |
| Steel strength fy | N/mm² (MPa) | N/mm² |
| Bending moment Mu | **kN·m** | **N·mm** |
| Shear force Vu | **kN** | **N** |
| Steel area | mm² | mm² |
| Stress | N/mm² | N/mm² |
| Stirrup spacing | mm | mm |

### 6.2 Conversion at Boundaries

Convert units **immediately on entry** and **before return**:

```vba
Public Function Ast_singly_IS456( _
    Mu_kNm As Double, _    ' Input in kN·m
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy As Double _
) As Double

    ' --- Convert to internal units ---
    Dim Mu_Nmm As Double
    Mu_Nmm = Mu_kNm * kNm_TO_Nmm   ' Convert kN·m to N·mm

    ' --- All calculations in N, mm ---
    ' ... formula uses Mu_Nmm, b_mm, d_mm ...

    ' --- Return in mm² (no conversion needed) ---
    Ast_singly_IS456 = Ast_mm2

End Function
```

### 6.3 Conversion Constants

```vba
' IS456_Constants.bas
Public Const kN_TO_N As Double = 1000           ' 1 kN = 1000 N
Public Const kNm_TO_Nmm As Double = 1000000     ' 1 kN·m = 10^6 N·mm
Public Const m_TO_mm As Double = 1000           ' 1 m = 1000 mm
Public Const N_TO_kN As Double = 0.001          ' 1 N = 0.001 kN
Public Const Nmm_TO_kNm As Double = 0.000001    ' 1 N·mm = 10^-6 kN·m
```

### 6.4 Never Mix Units in Formulas

```vba
' BAD: Mixed units, confusing
result = Mu_kNm / (b_mm * d_mm)  ' What unit is result?

' GOOD: All in base units
Mu_Nmm = Mu_kNm * kNm_TO_Nmm
result_Nmm2 = Mu_Nmm / (b_mm * d_mm)  ' N/mm² clearly
```

---

## 7. Input Validation

### 7.1 Validation Philosophy

1. **Validate at module boundaries** (public functions)
2. **Fail fast** — check inputs before calculations
3. **Return structured errors** — don't silently proceed
4. **Be specific** — tell the caller what's wrong

### 7.2 Geometry Validation

```vba
Private Function ValidateGeometry( _
    b_mm As Double, _
    d_mm As Double, _
    D_mm As Double _
) As String
    ' Returns empty string if valid, error message if invalid

    If b_mm <= 0 Then
        ValidateGeometry = "Width b must be positive"
        Exit Function
    End If

    If d_mm <= 0 Then
        ValidateGeometry = "Effective depth d must be positive"
        Exit Function
    End If

    If D_mm <= 0 Then
        ValidateGeometry = "Overall depth D must be positive"
        Exit Function
    End If

    If d_mm >= D_mm Then
        ValidateGeometry = "Effective depth d must be less than overall depth D"
        Exit Function
    End If

    ValidateGeometry = ""  ' Valid
End Function
```

### 7.3 Material Validation

```vba
Public Function IsValidConcreteGrade(fck As Double) As Boolean
    Select Case fck
        Case 15, 20, 25, 30, 35, 40, 45, 50
            IsValidConcreteGrade = True
        Case Else
            IsValidConcreteGrade = False
    End Select
End Function

Public Function IsValidSteelGrade(fy As Double) As Boolean
    Select Case fy
        Case 250, 415, 500
            IsValidSteelGrade = True
        Case Else
            IsValidSteelGrade = False
    End Select
End Function
```

### 7.4 Range Clamping

For Table 19 lookups, clamp pt% to valid range:

```vba
Private Function ClampPt(pt_percent As Double) As Double
    If pt_percent < MIN_PT_PERCENT Then
        ClampPt = MIN_PT_PERCENT
    ElseIf pt_percent > MAX_PT_PERCENT Then
        ClampPt = MAX_PT_PERCENT
    Else
        ClampPt = pt_percent
    End If
End Function
```

---

## 8. Error Handling

### 8.1 Error Codes Enum

```vba
' IS456_Types.bas
Public Enum IS456_ErrorCode
    ERR_NONE = 0
    ERR_NEGATIVE_DIMENSION = 1
    ERR_ZERO_DIMENSION = 2
    ERR_INVALID_CONCRETE_GRADE = 3
    ERR_INVALID_STEEL_GRADE = 4
    ERR_MOMENT_EXCEEDS_LIMIT = 5
    ERR_SHEAR_EXCEEDS_MAX = 6
    ERR_INVALID_REINFORCEMENT_RATIO = 7
    ERR_COVER_EXCEEDS_DEPTH = 8
    ERR_NEGATIVE_MOMENT = 9
    ERR_CALCULATION_FAILED = 10
End Enum
```

### 8.2 Simple Functions: Return Sentinel

For simple numeric functions, return `-1` on error:

```vba
Public Function Ast_singly_IS456(...) As Double
    ' Returns -1 if Mu exceeds limiting moment

    If Mu_kNm > Mu_lim Then
        Ast_singly_IS456 = -1
        Exit Function
    End If

    ' ... calculation ...
End Function
```

### 8.3 Complex Functions: Return Structured Result

For main API functions, populate the result type:

```vba
Public Function IS456_FlexureDesign(...) As FlexureResult
    Dim result As FlexureResult

    ' Validate inputs
    Dim errMsg As String
    errMsg = ValidateGeometry(b_mm, d_mm, D_mm)
    If errMsg <> "" Then
        result.DesignStatus = "ERROR"
        result.ErrorMessage = errMsg
        IS456_FlexureDesign = result
        Exit Function
    End If

    ' ... design calculation ...

    result.DesignStatus = "OK"
    result.ErrorMessage = ""
    IS456_FlexureDesign = result
End Function
```

### 8.4 Design Status Values

| Status | Meaning |
|--------|---------|
| `"OK"` | Design successful |
| `"DOUBLY_REQUIRED"` | Moment exceeds singly reinforced limit |
| `"SECTION_INADEQUATE"` | Shear exceeds maximum (increase section) |
| `"MIN_SHEAR_ONLY"` | Only minimum shear reinforcement needed |
| `"ERROR"` | Invalid inputs or calculation failure |

### 8.5 Never Use MsgBox or Err.Raise

```vba
' BAD: UI interaction in library
If b_mm <= 0 Then
    MsgBox "Invalid width!"  ' NO!
    Exit Function
End If

' BAD: Raises error that may crash caller
If b_mm <= 0 Then
    Err.Raise 1001, , "Invalid width"  ' AVOID
End If

' GOOD: Return error in result
If b_mm <= 0 Then
    result.DesignStatus = "ERROR"
    result.ErrorMessage = "Width must be positive"
    IS456_FlexureDesign = result
    Exit Function
End If
```

---

## 9. Documentation Standards

### 9.1 Function Documentation (VBA)

```vba
'-------------------------------------------------------------------------------
' Ast_singly_IS456
' Calculate required tension steel for a singly reinforced rectangular beam.
'
' Uses IS 456 limit state flexure design with parabolic-rectangular stress
' block. Returns -1 if moment exceeds limiting moment for singly reinforced
' section (doubly reinforced design required).
'
' Inputs:
'   Mu_kNm  - Factored bending moment (kN·m). Use absolute value.
'   b_mm    - Width of beam (mm)
'   d_mm    - Effective depth (mm)
'   fck     - Characteristic compressive strength of concrete (N/mm²)
'   fy      - Yield strength of steel (N/mm²)
'
' Returns:
'   Required tension steel area Ast (mm²)
'   Returns -1 if Mu > Mu_lim (doubly reinforced required)
'
' Formula:
'   Ast = (0.5 * fck / fy) * [1 - sqrt(1 - 4.6*Mu/(fck*b*d²))] * b * d
'
' Reference:
'   IS 456:2000, Clause 38.1 (Limit State of Collapse: Flexure)
'   SP:16-1980, Table 2
'
' Example:
'   Ast = Ast_singly_IS456(150, 300, 450, 25, 415)
'   ' Returns approximately 1050 mm²
'-------------------------------------------------------------------------------
Public Function Ast_singly_IS456( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy As Double _
) As Double
```

### 9.2 Inline Comments

Use inline comments for:
- IS 456 clause references
- Non-obvious formula steps
- Unit conversions

```vba
' Limiting neutral axis ratio (IS 456 Annex G.1.1)
k = xu_max_ratio(fy)

' Limiting moment capacity (IS 456 Clause 38.1)
' Mu_lim = 0.36 * fck * b * xu_max * (d - 0.42 * xu_max)
xu_max = k * d_mm
Mu_lim_Nmm = 0.36 * fck * b_mm * xu_max * (d_mm - 0.42 * xu_max)
Mu_lim_kNm = Mu_lim_Nmm * Nmm_TO_kNm  ' Convert to kN·m for output
```

### 9.3 API Reference Document

Maintain `docs/reference/api.md` with:
- All public function signatures
- Input/output descriptions with units
- IS 456 clause references
- Usage examples
- Error conditions

### 9.4 Keep Docs in Sync

When you change:
- A formula → Update `is456-quick-reference.md`
- A function signature → Update `api-reference.md`
- A behavior → Update both docs and code comments

---

## 10. Testing Guidelines

### 10.1 Test Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **Nominal** | Typical use cases | Standard beam, M25, Fe415 |
| **Boundary** | Edge of valid range | pt = 0.15%, pt = 3.0% |
| **Error** | Invalid inputs | b = 0, invalid grade |
| **Consistency** | Ast → back-calculate Mu | Verify round-trip |
| **Regression** | Bug fixes | Original failing input |

### 10.2 Test Case Format (VBA)

```vba
'-------------------------------------------------------------------------------
' Test_Ast_singly_nominal
' Verify Ast calculation against SP:16 worked example
'-------------------------------------------------------------------------------
Public Sub Test_Ast_singly_nominal()
    Dim Ast As Double
    Dim expected As Double
    Dim tolerance As Double

    ' Test case: SP:16 Example
    ' b=300, d=450, fck=20, fy=415, Mu=150 kN·m
    expected = 1050  ' mm² (approximate)
    tolerance = 50   ' Allow ±50 mm² for rounding

    Ast = Ast_singly_IS456(150, 300, 450, 20, 415)

    Debug.Assert Abs(Ast - expected) < tolerance
    Debug.Print "Test_Ast_singly_nominal: PASSED (Ast=" & Ast & ")"
End Sub
```

### 10.3 Test Case Format (Python)

```python
import pytest
from structural_lib.flexure import ast_singly_is456

def test_ast_singly_nominal():
    """Verify Ast against SP:16 worked example."""
    # b=300, d=450, fck=20, fy=415, Mu=150 kN·m
    ast = ast_singly_is456(150, 300, 450, 20, 415)
    assert ast == pytest.approx(1050, abs=50)

def test_ast_singly_exceeds_limit():
    """Verify -1 returned when Mu > Mu_lim."""
    ast = ast_singly_is456(300, 300, 450, 20, 415)  # Very high moment
    assert ast == -1
```

### 10.4 Test Data from Standards

Use worked examples from:
- **SP:16-1980** — Design Aids for Reinforced Concrete
- **P.C. Varghese** — Limit State Design of Reinforced Concrete
- **Pillai & Menon** — Reinforced Concrete Design

Document the source for each test case.

### 10.5 Table Lookup Tests

```vba
Public Sub Test_TauC_exact_values()
    ' Test exact table values (no interpolation)
    Debug.Assert Abs(tau_c_IS456(20, 0.15) - 0.28) < 0.001
    Debug.Assert Abs(tau_c_IS456(20, 1.0) - 0.62) < 0.001
    Debug.Assert Abs(tau_c_IS456(20, 3.0) - 0.82) < 0.001
    Debug.Assert Abs(tau_c_IS456(25, 1.0) - 0.64) < 0.001
    Debug.Print "Test_TauC_exact_values: PASSED"
End Sub

Public Sub Test_TauC_interpolation()
    ' Test interpolation between table values
    Dim tau As Double
    tau = tau_c_IS456(20, 0.5)  ' Between 0.25 and 0.50
    ' Should be between 0.36 and 0.48
    Debug.Assert tau > 0.36 And tau < 0.49
    Debug.Print "Test_TauC_interpolation: PASSED (tau=" & tau & ")"
End Sub

Public Sub Test_TauC_clamping()
    ' Test clamping at boundaries
    Debug.Assert Abs(tau_c_IS456(20, 0.1) - 0.28) < 0.001  ' Below min
    Debug.Assert Abs(tau_c_IS456(20, 5.0) - 0.82) < 0.001  ' Above max
    Debug.Print "Test_TauC_clamping: PASSED"
End Sub
```

### 10.6 Running Tests

**VBA:**
```vba
Public Sub RunAllTests()
    Test_Ast_singly_nominal
    Test_Ast_singly_exceeds_limit
    Test_TauC_exact_values
    Test_TauC_interpolation
    Test_TauC_clamping
    Test_Consistency
    Debug.Print "=== ALL TESTS PASSED ==="
End Sub
```

**Python:**
```bash
pytest tests/ -v
```

### 10.7 Rounding and Tolerances
- Calculations: keep full precision internally; round only when presenting results (default 3 decimal places for stresses/capacities, 1 decimal for spacing).
- Tests: use absolute tolerances of ±0.5 kN·m for moments, ±1% of value or explicit bounds for shear stresses/areas. Prefer `pytest.approx(..., rel=0.01)` or VBA `Abs(actual - expected) < tolerance`.
- Table lookup tests: exact comparisons for table points; inequality bounds for interpolation cases.
- Avoid binary floating point surprises by normalizing units (N, N·mm, mm) before comparisons.

---

## 11. Version Control and Git Workflow

### 11.1 Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Stable, tested releases |
| `develop` | Integration branch for features |
| `feature/xxx` | Individual features |
| `fix/xxx` | Bug fixes |

### 11.2 Pre-Commit Hooks (Required)

This project uses pre-commit hooks to enforce formatting and linting **before** commits. This prevents CI failures.

**First-time setup:**
```bash
cd structural_engineering_lib
pip install pre-commit   # or: pip install -e ".[dev]"
pre-commit install
```

**What happens on `git commit`:**
1. **black** — Auto-formats Python code
2. **ruff** — Checks for lint errors (unused imports, variables, etc.)
3. If issues found, commit is blocked and fixes are shown

**Run manually on all files:**
```bash
pre-commit run --all-files
```

### 11.3 Commit Messages

Format: `type(scope): description`

```
feat(flexure): add Ast_singly_IS456 function
fix(tables): correct M30 tau_c value at pt=2.0%
docs(api): add usage examples for shear design
test(shear): add boundary tests for tau_c clamping
refactor(utilities): extract validation helpers
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`

### 11.4 VBA Files and Git

VBA `.bas` files are plain text and work well with Git. Export modules regularly:

1. In VBA Editor, right-click module → **Export File...**
2. Save to `VBA/Modules/` folder
3. Commit changes

Consider using a tool like [vba-blocks](https://github.com/vba-blocks/vba-blocks) or [Rubberduck](https://rubberduckvba.com/) for automated export.

### 11.5 Pull Request and Merge Guidelines

#### When to Create a PR
- Create PRs for logical units of work (features, bug fixes, doc updates)
- Multiple related commits can go in one PR
- Keep PRs focused — one concern per PR

#### When to Merge PRs

**DO merge after:**
- Completing a feature or significant enhancement
- Fixing a bug with tests
- Adding meaningful test coverage (e.g., 10+ tests)
- Documentation updates that complete a section
- Release preparation

**DON'T merge for:**
- Single-line typo fixes (batch with other changes)
- Formatting-only changes (these should be caught by pre-commit)
- WIP or incomplete work
- Every small incremental change

**Batching guideline:** Accumulate small related changes into one PR rather than creating separate PRs for each tiny edit. Example:
- ❌ PR #1: "fix typo in README", PR #2: "fix typo in API docs", PR #3: "fix typo in guide"
- ✅ PR #1: "docs: fix typos across documentation"

#### Merge Workflow
```bash
# 1. Create PR
gh pr create --title "feat: add X" --body "..."

# 2. WAIT for CI — don't try to merge immediately!
gh pr checks <num> --watch

# 3. Only merge AFTER all checks pass
gh pr merge <num> --squash --delete-branch
```

### 11.6 Code Ownership and Reviews
- Minimum 1 reviewer for core changes; 2 reviewers for releases or table/formula edits.
- Merge criteria: tests pass, changelog updated for user-visible changes, docs updated (API/quick ref) when signatures or behavior change.
- Record non-trivial decisions in an ADR (add `docs/adr/`) or log in `research-ai-enhancements.md`.
- No merges to `main` without green tests for both VBA (manual run note acceptable) and Python.

---

## 12. Versioning and Governance

### 12.1 Semantic Versioning

Format: `MAJOR.MINOR.PATCH`

- **MAJOR** — Breaking API changes
- **MINOR** — New features, backward compatible
- **PATCH** — Bug fixes, backward compatible

Pre-1.0: `0.x.y` — API may change between minor versions.

### 12.2 Governance Rules
To prevent history revisionism and ensure stability:
1.  **Immutable History:** Never edit past entries in `CHANGELOG.md` or `docs/releases.md`.
2.  **Release Ledger:** `docs/releases.md` is the single source of truth for locked versions.
3.  **Explicit Bumps:** Version numbers are only incremented with explicit user approval.

### 12.3 Version Constants

```vba
' IS456_Constants.bas
Public Const LIB_VERSION As String = "0.9.1"
Public Const LIB_BUILD_DATE As String = "2025-12-25"
Public Const IS456_CODE_YEAR As String = "2000"
```

```python
# constants.py
__version__ = "0.9.1"
LIB_BUILD_DATE = "2025-12-25"
IS456_CODE_YEAR = "2000"
```

### 12.3 Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [0.9.1] - 2025-12-25

### Added
- Initial release
- Flexure design for singly reinforced rectangular beams
- Shear design with stirrup spacing calculation
- Table 19 (τc) and Table 20 (τc,max) lookup with interpolation
- UDF wrappers for Excel worksheet use

### Reference
- IS 456:2000 Clauses 38.1, 40, 26.5.1
- SP:16-1980 Tables 2, 19, 20
```

---

## 13. Packaging and Distribution

### 13.1 VBA: .bas Files

For development and version control:
1. Export all modules as `.bas` files
2. Store in `VBA/Modules/` folder
3. Commit to Git

### 13.2 VBA: Excel Add-in (.xlam)

For end-user distribution:

1. Create new Excel workbook
2. Import all `.bas` modules from `VBA/Modules/`
3. **File → Save As → Excel Add-in (.xlam)**
4. Save to: `C:\Users\<user>\AppData\Roaming\Microsoft\AddIns\` (Windows)
5. In Excel: **File → Options → Add-ins → Manage: Excel Add-ins → Go → Browse**

### 13.3 Python: Package Structure

```
Python/
├── structural_lib/
│   ├── __init__.py
│   └── ...
├── pyproject.toml
├── setup.cfg
├── requirements.txt
└── README.md
```

**pyproject.toml + setup.cfg:**
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "structural-lib-is456"
version = "0.9.1"
description = "IS 456 RC Beam Design Library"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.9",
]

[project.optional-dependencies]
dev = ["pytest", "black", "mypy", "pre-commit"]
```

**setup.cfg:**
```ini
[metadata]
name = structural-lib-is456
version = 0.9.1
description = IS 456 RC Beam Design Library
long_description = file: README.md
long_description_content_type = text/markdown
license = MIT

[options]
packages = find:
python_requires = >=3.9
install_requires =
    # add runtime deps if any

[options.extras_require]
dev =
    pytest
    black
    mypy
```

### 13.4 Build and Publish

```bash
# Build wheel
python -m build

# Install locally
pip install -e .

# Publish to PyPI (when ready)
twine upload dist/*
```

### 13.5 Build/Test Automation
- **VBA:** Use Rubberduck test explorer or a VBA script to run `RunAllTests`; export modules automatically on build (vba-blocks or custom PowerShell/VBScript).
- **Python:** Provide `make test` or `nox/tox` sessions for lint + tests (`pytest -q`).
- **CI (active):** GitHub Actions runs on PRs and pushes to `main`.
    - Workflows: `.github/workflows/python-tests.yml` and `.github/workflows/codeql.yml`
    - Policy: keep workflow `GITHUB_TOKEN` permissions least-privilege (jobs can widen only when needed).
    - If branch ruleset requires “up to date with main”, update PR branches before merge.
- Keep scripts in `scripts/` or `Makefile` to ensure repeatability.

**Formatting (Black):**
```bash
cd Python
python -m black .
python -m black --check .
```

**Type checking (Mypy):**
```bash
cd Python
python -m mypy structural_lib
```

**Pre-commit hooks (recommended):**
```bash
cd Python
python -m pip install -e ".[dev]"

cd ..
pre-commit install
pre-commit run --all-files
```

**Optional extras:**
```bash
# Add optional report + validation helpers (Jinja2/jsonschema)
cd Python
python -m pip install -e ".[dev,report,validation]"
```

**Repo automation:**
- Dependabot runs weekly updates (Actions + Python deps best-effort).
    - Grouped updates reduce PR noise (configured in `.github/dependabot.yml`).
    - These PRs may be blocked from merge until brought “up to date” with `main` (use `gh pr update-branch`).
- CodeQL runs weekly and on PRs.

### 13.6 Professional-grade Testing Checklist

**Goal:** Catch regressions, prove code intent (IS clauses), and make contributions safe.

**Python (automated):**
- Unit tests for every public function and every table lookup edge.
- Boundary tests: Mu≈Mu_lim, pt clamp boundaries, Vus≈0, minimum spacing rules, cover/d invalid inputs.
- Golden-reference tests: compare against hand-calculated examples with explicit tolerances.
- Coverage reporting in CI (informational first; add a threshold once stable).
- Packaging smoke test in CI (wheel build must succeed).

**VBA (repeatable):**
- Single macro entrypoint `RunAllTests` that runs all test modules.
- Deterministic output: pass/fail counts + list of failures.
- Manual run log attached to PRs until VBA CI automation exists.

**Parity (Python ↔ VBA):**
- Shared test vector file(s) (CSV/JSON) with expected outputs + tolerances.
- Same vectors executed by Python `pytest` and the VBA harness.

**Integration tests:**
- CSV/JSON ingestion → detailing → DXF generation (smoke tests).
- Ensure errors are clear (status + message) for invalid inputs.

---

## 14. Code Review Checklist

Before merging any code, verify:

### Correctness
- [ ] Formulas match IS 456 clauses cited in comments
- [ ] Unit conversions are correct
- [ ] Edge cases handled (pt clamping, Mu > Mu_lim, etc.)
- [ ] Tests pass for nominal, boundary, and error cases

### Style
- [ ] `Option Explicit` present (VBA)
- [ ] Type hints present (Python)
- [ ] Naming follows conventions
- [ ] Function header comments complete

### Documentation
- [ ] IS 456 clause references in comments
- [ ] Input/output units documented
- [ ] api-reference.md updated if signatures changed
- [ ] Examples work correctly

### Testing
- [ ] New tests added for new functionality
- [ ] Regression test added for bug fixes
- [ ] All existing tests still pass

### Parity
- [ ] VBA and Python implementations match
- [ ] Same test cases in both languages

---

## 15. Common Pitfalls to Avoid

### 15.1 Unit Confusion

```vba
' WRONG: Mixed units in formula
Ast = Mu_kNm / (0.87 * fy * d_mm)  ' Units don't match!

' RIGHT: Convert first
Mu_Nmm = Mu_kNm * kNm_TO_Nmm
Ast = Mu_Nmm / (0.87 * fy * (d_mm - 0.42 * xu_mm))
```

### 15.2 Integer Division

```vba
' WRONG: Integer division truncates
Dim ratio As Double
ratio = 3 \ 4    ' Integer divide -> 0

' RIGHT: Use floating point
ratio = 3 / 4    ' Floating divide -> 0.75
ratio = 3# / 4#  ' Also correct
ratio = CDbl(3) / CDbl(4)
```

### 15.3 Missing Option Explicit

```vba
' Without Option Explicit:
Dim calculated_Ast As Double
calculatedAst = 500  ' Typo creates NEW variable!
' calculated_Ast is still 0 — silent bug

' With Option Explicit:
' Compile error: Variable not defined
```

### 15.4 Worksheet Access in Library

```vba
' WRONG: Library function accesses worksheet
Public Function BadFunction() As Double
    BadFunction = Range("A1").Value  ' NOT portable!
End Function

' RIGHT: Pass data as parameter
Public Function GoodFunction(value As Double) As Double
    GoodFunction = value * 2
End Function
```

### 15.5 Forgetting to Handle Errors

```vba
' WRONG: Caller doesn't check for error
Ast = Ast_singly_IS456(500, 300, 450, 20, 415)
' If Ast = -1, this proceeds with wrong value!

' RIGHT: Always check return value
Ast = Ast_singly_IS456(500, 300, 450, 20, 415)
If Ast < 0 Then
    ' Handle error - doubly reinforced required
End If
```

### 15.6 Hardcoded Table Values

```vba
' WRONG: Hardcoded in calculation function
tau_c = 0.62  ' What if pt or fck changes?

' RIGHT: Call lookup function
tau_c = tau_c_IS456(fck, pt_percent)
```

### 15.7 Operational Friction Notes

For recent “gotchas” and fixes (release script quirks, CI timeouts, PR update steps),
see `docs/contributing/session-issues.md`.

---

## 16. Release Checklist and Quality Gates

Before tagging a release or distributing an add-in/wheel:
- [ ] Version bumped in Python (`pyproject.toml`, `structural_lib/__init__.py`, `structural_lib/api.py`) and VBA (`M08_API.Get_Library_Version`).
- [ ] `CHANGELOG.md` updated (add entry under release version) and `README.md`/API docs refreshed.
- [ ] Quality gates (Python):
    - `python -m black --check .`
    - `python -m ruff check .`
    - `python -m mypy`
 - [ ] Clean-venv release verification: `.venv/bin/python scripts/verify_release.py --version X.Y.Z --source pypi`
    - `python -m pytest`
    - `python -m build`
    - wheel smoke test: `python -m pip install --force-reinstall dist/*.whl && python -c "import structural_lib"`
- [ ] VBA modules exported cleanly; `.xlam` add-in rebuilt if distributing.
- [ ] Tag annotated (e.g., `v0.8.1`) and pushed with release notes.

Tip: run the full Python gate locally with `Python/scripts/pre_release_check.sh`.

---

## Appendix A: Quick Reference Card

### VBA Module Template

```vba
Attribute VB_Name = "IS456_ModuleName"
'===============================================================================
' IS456_ModuleName.bas
' Part of: IS 456 RC Beam Design Library
' Version: 0.9.1
' Purpose: [Description]
'===============================================================================
Option Explicit

' --- Constants ---
Private Const SOME_CONSTANT As Double = 1.5

' --- Public Functions ---

'-------------------------------------------------------------------------------
' FunctionName - [Brief description]
' Reference: IS 456:2000, Clause X.X
'-------------------------------------------------------------------------------
Public Function FunctionName(param As Double) As Double
    ' Implementation
End Function

' --- Private Helpers ---

Private Function HelperFunction(param As Double) As Double
    ' Implementation
End Function
```

### Python Module Template

```python
"""
IS 456 RC Beam Design Library - Module Name

Purpose: [Description]
Reference: IS 456:2000
"""

from __future__ import annotations

# --- Constants ---
SOME_CONSTANT: float = 1.5

# --- Public Functions ---

def function_name(param: float) -> float:
    """
    Brief description.

    Reference: IS 456:2000, Clause X.X
    """
    pass

# --- Private Helpers ---

def _helper_function(param: float) -> float:
    """Internal helper."""
    pass
```

---

**End of Development Guide**
