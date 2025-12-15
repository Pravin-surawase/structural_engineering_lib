# IS 456 RC Beam Design Library — Research and Findings

**Document Version:** 1.0  
**Last Updated:** December 10, 2025  
**Status:** Historical research + reference material (some early sections may be out-of-date)

> Note: This file started as an early-stage “design + research” doc. The repo now has working Python/VBA implementations.
> For current scope/architecture and how to use the library, prefer:
> - [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
> - [API_REFERENCE.md](API_REFERENCE.md)
> - [TASKS.md](TASKS.md) and [NEXT_SESSION_BRIEF.md](NEXT_SESSION_BRIEF.md)

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Workspace Status](#2-workspace-status)
3. [VBA Module Architecture Research](#3-vba-module-architecture-research)
4. [IS 456:2000 Code Formulas and References](#4-is-4562000-code-formulas-and-references)
5. [Complete Table Data](#5-complete-table-data)
6. [Unit System and Conventions](#6-unit-system-and-conventions)
7. [Error Handling Strategy](#7-error-handling-strategy)
8. [API Design and Function Signatures](#8-api-design-and-function-signatures)
9. [Using the Library in Excel VBA](#9-using-the-library-in-excel-vba)
10. [Development Guidelines](#10-development-guidelines)
11. [Implementation Plan](#11-implementation-plan)
12. [Future Extensibility](#12-future-extensibility)
13. [Testing Strategy](#13-testing-strategy)
14. [Open Questions and Decisions](#14-open-questions-and-decisions)

---

## 1. Project Overview

### 1.1 Goal

Build a **reusable, UI-agnostic structural engineering library** for RC rectangular beam design per IS 456:2000 (Indian Standard for Plain and Reinforced Concrete).

### 1.2 Scope for V0

| In Scope | Out of Scope (Future) |
|----------|----------------------|
| Rectangular beams | Flanged beams (T, L) |
| Singly reinforced flexure | Doubly reinforced (stub only) |
| Shear design with stirrups | Prestressed beams |
| Limit state design | Deep beams |
| IS 456:2000 provisions | IS 13920 ductile detailing |
| VBA + Python implementations | Serviceability (deflection, crack width) |

### 1.3 Design Principles

1. **Pure Functions:** All functions receive inputs and return outputs — no hidden state
2. **No UI Dependencies:** No MsgBox, InputBox, ActiveSheet, Range, Cells — pure calculations only
3. **Strict Units:** Clear conventions for all inputs/outputs (mm, N/mm², kN, kN·m)
4. **Well Documented:** IS 456 clause references in code comments
5. **Portable:** Easy to import into any Excel workbook or Python project
6. **Future-Proof:** Designed for easy extension to flanged beams, IS 13920, etc.

---

## 2. Workspace Status

### 2.1 Current State

The project has progressed beyond the initial research phase and is implemented in both Python and VBA.

Current high-level structure (simplified):

```
structural_engineering_lib/
├── docs/                 # Guides, API docs, research logs
├── Python/               # Python package + tests
├── VBA/                  # VBA modules + tests + build artifacts
└── Excel/                # Example workbooks/add-ins
```

### 2.2 Recommended Final Structure

```
/structural_engineering_lib/
├── docs/
│   ├── RESEARCH_AND_FINDINGS.md      ← This document
│   ├── API_REFERENCE.md              ← Function documentation
│   └── IS456_QUICK_REFERENCE.md      ← Formulas cheat sheet
│
├── VBA/
│   ├── Modules/
│   │   ├── IS456_Constants.bas       ← Constants, version, units
│   │   ├── IS456_Types.bas           ← User-Defined Types (UDTs)
│   │   ├── IS456_Tables.bas          ← Table 19, 20, xu_max data
│   │   ├── IS456_Utilities.bas       ← Validation, interpolation
│   │   ├── IS456_Materials.bas       ← Grade validation
│   │   ├── IS456_Flexure.bas         ← Flexural design functions
│   │   ├── IS456_Shear.bas           ← Shear design functions
│   │   └── IS456_API.bas             ← Public façade functions
│   ├── Examples/
│   │   └── Example_Usage.bas         ← Demo code snippets
│   └── Tests/
│       └── IS456_Tests.bas           ← Unit tests
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
│   │   └── api.py
│   ├── tests/
│   │   ├── test_flexure.py
│   │   ├── test_shear.py
│   │   └── test_tables.py
│   ├── examples/
│   │   └── beam_design_example.py
│   ├── requirements.txt
│   └── setup.py
│
└── README.md
```

---

## 3. VBA Module Architecture Research

### 3.1 Key VBA Best Practices

#### Option Explicit (Mandatory)
```vba
Option Explicit  ' Must appear at top of every module
```
- Forces explicit variable declaration
- Catches typos at compile time, not runtime
- **Always use this** — single most important VBA practice

#### Module-Level Organization
- Use **standard modules** (`.bas` files) for all library code
- Avoid class modules for simple data structures — use `Type` instead
- Keep modules focused on single responsibility
- Use `Private` for internal helpers, `Public` for API functions

### 3.2 User-Defined Types (UDTs)

VBA `Type` structures allow grouping related return values:

```vba
Public Type FlexureResult
    Ast_required As Double      ' Required tension steel (mm²)
    Ast_min As Double           ' Minimum steel (mm²)
    Ast_max As Double           ' Maximum steel (mm²)
    xu As Double                ' Actual neutral axis depth (mm)
    xu_max As Double            ' Limiting neutral axis depth (mm)
    Mu_lim As Double            ' Limiting moment capacity (kN·m)
    IsDoublyReinforced As Boolean
    DesignStatus As String      ' "OK", "DOUBLY_REQUIRED", "ERROR"
    ErrorMessage As String
End Type
```

**UDT Limitations:**
- Can only be returned from functions in **standard modules** (not class modules)
- Cannot contain dynamic arrays (only fixed-size)
- Cannot be used directly as UDF return values in worksheets
- **Workaround for UDFs:** Create wrapper functions that return individual values

### 3.3 Making Modules Portable

**Avoid these (not portable):**
- `ThisWorkbook` — ties code to specific workbook
- Hardcoded sheet names or ranges
- Named ranges specific to one workbook
- Early binding to external libraries

**Do this instead:**
- All functions receive data as parameters
- No worksheet/workbook references inside library functions
- Use late binding if external libraries needed (not needed for this lib)

### 3.4 Distribution Options

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Import .bas files** | Version control friendly, transparent, easy to customize | Must import to each workbook, code duplicated | Development, open source |
| **Excel Add-in (.xlam)** | Single install, available to all workbooks, easy updates | Harder to debug, requires Trust Center settings | Production distribution |
| **Hybrid approach** | Best of both worlds | Requires two workflows | Recommended |

**Recommendation:** Develop with `.bas` files (Git-friendly), distribute as `.xlam` for end users.

---

## 4. IS 456:2000 Code Formulas and References

### 4.1 Stress Block Parameters (Clause 38.1, Annex G)

IS 456 uses a **parabolic-rectangular** stress distribution:

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Design stress at compression face | $0.446 f_{ck}$ | $\frac{0.67 f_{ck}}{1.5}$ |
| Total compression force | $C = 0.36 \times f_{ck} \times b \times x_u$ | Integration of stress block |
| Centroid of compression from top | $\bar{y} = 0.42 \times x_u$ | Centroid of parabolic-rectangular area |
| Design steel stress | $0.87 f_y$ | $\frac{f_y}{1.15}$ |

**Where the factors come from:**
- **0.36** = area factor of parabolic-rectangular stress block
- **0.42** = centroid factor of the same stress block
- **0.87** = steel partial safety factor (1/1.15)

### 4.2 Neutral Axis Depth Limits (Annex G.1.1)

| Steel Grade | $f_y$ (N/mm²) | $x_{u,max}/d$ |
|-------------|---------------|---------------|
| Fe 250 | 250 | **0.53** |
| Fe 415 | 415 | **0.48** |
| Fe 500 | 500 | **0.46** |

**Derivation formula:**
$$\frac{x_{u,max}}{d} = \frac{0.0035}{0.0035 + \varepsilon_{sy} + 0.002}$$

where $\varepsilon_{sy} = \frac{0.87 f_y}{E_s}$ and $E_s = 2 \times 10^5$ N/mm²

### 4.3 Effective Depth (Clause 23.2)

$$d = D - c_{clear} - \phi_{stirrup} - \frac{\phi_{main}}{2}$$

where:
- $D$ = overall depth (mm)
- $c_{clear}$ = clear cover (mm) — typically 25-50mm per Table 16
- $\phi_{stirrup}$ = stirrup diameter (mm)
- $\phi_{main}$ = main bar diameter (mm)

### 4.4 Limiting Moment of Resistance (Clause 38.1)

$$M_{u,lim} = 0.36 \times f_{ck} \times b \times x_{u,max} \times (d - 0.42 \times x_{u,max})$$

Or using the ratio $k = x_{u,max}/d$:

$$M_{u,lim} = 0.36 \times k \times (1 - 0.42k) \times f_{ck} \times b \times d^2$$

**Pre-computed coefficients $R_u$ where $M_{u,lim} = R_u \times f_{ck} \times b \times d^2$:**

| Steel Grade | $k$ | $R_u = 0.36k(1-0.42k)$ |
|-------------|-----|------------------------|
| Fe 250 | 0.53 | 0.149 |
| Fe 415 | 0.48 | 0.138 |
| Fe 500 | 0.46 | 0.133 |

### 4.5 Area of Steel — Singly Reinforced (Clause 38.1)

From moment equilibrium, solving the quadratic:

$$A_{st} = \frac{0.5 \times f_{ck}}{f_y} \times \left[1 - \sqrt{1 - \frac{4.6 \times M_u}{f_{ck} \times b \times d^2}}\right] \times b \times d$$

**Important:** $M_u$ must be in **N·mm** for this formula when $f_{ck}$, $f_y$ are in N/mm² and $b$, $d$ are in mm.

**Alternative percentage form:**
$$p_t = \frac{50 \times f_{ck}}{f_y} \times \left[1 - \sqrt{1 - \frac{4.6 \times M_u}{f_{ck} \times b \times d^2}}\right]$$

### 4.6 Reinforcement Limits (Clause 26.5.1)

| Requirement | Formula | Clause |
|-------------|---------|--------|
| Minimum tension steel | $A_{s,min} = \frac{0.85 \times b \times d}{f_y}$ | 26.5.1.1 |
| Maximum tension steel | $A_{s,max} = 0.04 \times b \times D$ | 26.5.1.2 |
| Side face reinforcement | Required when $D > 750$ mm; $A_{sf} = 0.1\%$ of web area | 26.5.1.3 |

### 4.7 Shear Design (Clause 40)

#### Nominal Shear Stress
$$\tau_v = \frac{V_u}{b \times d}$$

#### Design Shear Strength (Table 19)
$\tau_c$ depends on concrete grade and percentage tension steel $p_t = \frac{100 \times A_{st}}{b \times d}$

See Section 5 for complete table.

#### Maximum Shear Stress (Table 20)
If $\tau_v > \tau_{c,max}$, the section is inadequate — must increase dimensions.

| Concrete Grade | M15 | M20 | M25 | M30 | M35 | M40+ |
|----------------|-----|-----|-----|-----|-----|------|
| $\tau_{c,max}$ (N/mm²) | 2.5 | 2.8 | 3.1 | 3.5 | 3.7 | 4.0 |

#### Shear Reinforcement Design (Clause 40.4)

When $\tau_v > \tau_c$:
$$V_{us} = V_u - \tau_c \times b \times d$$

For vertical stirrups:
$$\frac{A_{sv}}{s_v} = \frac{V_{us}}{0.87 \times f_y \times d}$$

Rearranged for spacing:
$$s_v = \frac{0.87 \times f_y \times A_{sv} \times d}{V_{us}}$$

#### Maximum Stirrup Spacing (Clause 26.5.1.5)
$$s_{v,max} = \min(0.75d, 300 \text{ mm})$$

#### Minimum Shear Reinforcement (Clause 26.5.1.6)
$$\frac{A_{sv}}{b \times s_v} \geq \frac{0.4}{0.87 \times f_y}$$

---

## 5. Complete Table Data

### 5.1 Table 19 — Design Shear Strength τc (N/mm²)

| $p_t$ (%) | M15 | M20 | M25 | M30 | M35 | M40+ |
|-----------|-----|-----|-----|-----|-----|------|
| ≤0.15 | 0.28 | 0.28 | 0.29 | 0.29 | 0.29 | 0.30 |
| 0.25 | 0.35 | 0.36 | 0.36 | 0.37 | 0.37 | 0.38 |
| 0.50 | 0.46 | 0.48 | 0.49 | 0.50 | 0.50 | 0.51 |
| 0.75 | 0.54 | 0.56 | 0.57 | 0.59 | 0.59 | 0.60 |
| 1.00 | 0.60 | 0.62 | 0.64 | 0.66 | 0.67 | 0.68 |
| 1.25 | 0.64 | 0.67 | 0.70 | 0.71 | 0.73 | 0.74 |
| 1.50 | 0.68 | 0.72 | 0.74 | 0.76 | 0.78 | 0.79 |
| 1.75 | 0.71 | 0.75 | 0.78 | 0.80 | 0.82 | 0.84 |
| 2.00 | 0.71 | 0.79 | 0.82 | 0.84 | 0.86 | 0.88 |
| 2.25 | 0.71 | 0.81 | 0.85 | 0.88 | 0.90 | 0.92 |
| 2.50 | 0.71 | 0.82 | 0.88 | 0.91 | 0.93 | 0.95 |
| 2.75 | 0.71 | 0.82 | 0.90 | 0.94 | 0.96 | 0.98 |
| ≥3.00 | 0.71 | 0.82 | 0.92 | 0.96 | 0.99 | 1.01 |

**Notes:**
- For $p_t < 0.15\%$: use $p_t = 0.15\%$ value (conservative)
- For $p_t > 3.0\%$: use $p_t = 3.0\%$ value (code limit)
- For M15: τc is capped at 0.71 regardless of $p_t$
- Use **linear interpolation** for intermediate $p_t$ values

### 5.2 Table 20 — Maximum Shear Stress τc,max (N/mm²)

| Concrete Grade | M15 | M20 | M25 | M30 | M35 | M40+ |
|----------------|-----|-----|-----|-----|-----|------|
| $\tau_{c,max}$ | 2.5 | 2.8 | 3.1 | 3.5 | 3.7 | 4.0 |

### 5.3 Neutral Axis Ratios (Annex G.1.1)

| Steel Grade | $f_y$ (N/mm²) | $x_{u,max}/d$ |
|-------------|---------------|---------------|
| Fe 250 | 250 | 0.53 |
| Fe 415 | 415 | 0.48 |
| Fe 500 | 500 | 0.46 |

---

## 6. Unit System and Conventions

### 6.1 Input/Output Units

| Quantity | Input Unit | Internal Unit | Output Unit |
|----------|------------|---------------|-------------|
| Width, depth, cover | mm | mm | mm |
| Bar diameters | mm | mm | mm |
| Concrete strength $f_{ck}$ | N/mm² (MPa) | N/mm² | N/mm² |
| Steel strength $f_y$ | N/mm² (MPa) | N/mm² | N/mm² |
| Bending moment $M_u$ | **kN·m** | N·mm | kN·m |
| Shear force $V_u$ | **kN** | N | kN |
| Steel area | mm² | mm² | mm² |
| Shear stress | N/mm² | N/mm² | N/mm² |
| Stirrup spacing | mm | mm | mm |

### 6.2 Unit Conversion Constants

```vba
Public Const kN_TO_N As Double = 1000           ' 1 kN = 1000 N
Public Const kNm_TO_Nmm As Double = 1000000     ' 1 kN·m = 10^6 N·mm
Public Const m_TO_mm As Double = 1000           ' 1 m = 1000 mm
```

### 6.3 Sign Convention

| Moment Sign | Meaning | Tension Face |
|-------------|---------|--------------|
| Positive $M_u$ | Sagging moment | Bottom fibre |
| Negative $M_u$ | Hogging moment | Top fibre |

**Library convention:** Functions use **absolute value** of moment for design calculations. The UI layer determines which face is in tension based on sign.

---

## 7. Error Handling Strategy

### 7.1 Error Codes (Enum)

```vba
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

### 7.2 Edge Cases and Handling

| Edge Case | Detection | Handling |
|-----------|-----------|----------|
| $M_u > M_{u,lim}$ | Compare after calculating | Return `DesignStatus = "DOUBLY_REQUIRED"` |
| $\tau_v > \tau_{c,max}$ | Compare after calculating | Return `DesignStatus = "SECTION_INADEQUATE"` |
| $p_t > 3\%$ for Table 19 | Check before lookup | Clamp to 3.0% |
| $p_t < 0.15\%$ for Table 19 | Check before lookup | Use 0.15% value |
| $b \leq 0$ or $d \leq 0$ | Validate on entry | Return error immediately |
| Invalid $f_{ck}$ | Validate on entry | Return error with valid options |
| Discriminant < 0 in Ast formula | Check before sqrt | Should not occur if $M_u < M_{u,lim}$ |

### 7.3 Error Handling Philosophy

1. **No MsgBox or user interaction** — library is pure
2. **Return error information in result struct** — caller decides how to handle
3. **Use sentinel values (-1) for simple numeric functions** — document in comments
4. **Validate inputs early** — fail fast with clear error messages
5. **Never silently proceed with invalid data**

---

## 8. API Design and Function Signatures

### 8.1 Public API Functions (Main Entry Points)

```vba
' FLEXURE DESIGN - Main entry point
Public Function IS456_FlexureDesign( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    D_mm As Double, _
    fck As Double, _
    fy As Double _
) As FlexureResult

' SHEAR DESIGN - Main entry point
Public Function IS456_ShearDesign( _
    Vu_kN As Double, _
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy_stirrup As Double, _
    Ast_provided_mm2 As Double, _
    Optional stirrup_dia_mm As Double = 8, _
    Optional stirrup_legs As Long = 2 _
) As ShearResult
```

### 8.2 Geometry/Material Helpers

```vba
Public Function d_effective( _
    D_mm As Double, _
    cover_mm As Double, _
    dia_main_mm As Double, _
    dia_stirrup_mm As Double _
) As Double

Public Function pt_from_Ast( _
    Ast_mm2 As Double, _
    b_mm As Double, _
    d_mm As Double _
) As Double

Public Function Ast_min_IS456( _
    b_mm As Double, _
    d_mm As Double, _
    fy As Double _
) As Double

Public Function Ast_max_IS456( _
    b_mm As Double, _
    D_mm As Double _
) As Double
```

### 8.3 Flexure Functions

```vba
Public Function Ast_singly_IS456( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy As Double _
) As Double  ' Returns -1 if Mu > Mu_lim

Public Function Mu_limit_IS456( _
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy As Double _
) As Double  ' Returns kN·m

Public Function xu_max_ratio( _
    fy As Double _
) As Double  ' Returns 0.53, 0.48, or 0.46
```

### 8.4 Shear Functions

```vba
Public Function tau_v( _
    Vu_kN As Double, _
    b_mm As Double, _
    d_mm As Double _
) As Double  ' Returns N/mm²

Public Function tau_c_IS456( _
    fck As Double, _
    pt_percent As Double _
) As Double  ' Returns N/mm² (interpolated from Table 19)

Public Function tau_cmax_IS456( _
    fck As Double _
) As Double  ' Returns N/mm² (from Table 20)

Public Function Vuc_IS456( _
    b_mm As Double, _
    d_mm As Double, _
    tau_c As Double _
) As Double  ' Returns kN

Public Function Vus_req_IS456( _
    Vu_kN As Double, _
    Vuc_kN As Double _
) As Double  ' Returns kN (min 0)

Public Function StirrupSpacing_IS456( _
    Vus_kN As Double, _
    dia_stirrup_mm As Double, _
    legs As Long, _
    fy As Double, _
    d_mm As Double, _
    sv_max_mm As Double _
) As Double  ' Returns mm
```

---

## 9. Using the Library in Excel VBA

### 9.1 Method 1: Import .bas Files Directly

This is the recommended approach for development and customization.

**Steps:**
1. Open your Excel workbook
2. Press `Alt + F11` to open VBA Editor
3. Right-click on your VBA Project → **Import File...**
4. Select all `.bas` files from the `VBA/Modules/` folder:
   - `IS456_Constants.bas`
   - `IS456_Types.bas`
   - `IS456_Tables.bas`
   - `IS456_Utilities.bas`
   - `IS456_Materials.bas`
   - `IS456_Flexure.bas`
   - `IS456_Shear.bas`
   - `IS456_API.bas`
5. Save workbook as `.xlsm` (macro-enabled)

**Calling from your own code:**
```vba
Sub MyBeamDesign()
    Dim result As FlexureResult
    Dim b As Double, d As Double, D As Double
    Dim fck As Double, fy As Double, Mu As Double
    
    ' Input values
    b = 300: d = 450: D = 500
    fck = 25: fy = 415
    Mu = 150  ' kN·m
    
    ' Call the library
    result = IS456_FlexureDesign(Mu, b, d, D, fck, fy)
    
    ' Use the results
    If result.DesignStatus = "OK" Then
        Debug.Print "Ast required: " & result.Ast_required & " mm²"
        Debug.Print "Ast min: " & result.Ast_min & " mm²"
        Debug.Print "Mu limit: " & result.Mu_lim & " kN·m"
    Else
        Debug.Print "Design failed: " & result.ErrorMessage
    End If
End Sub
```

### 9.2 Method 2: Excel Add-in (.xlam)

For production distribution to end users.

**Creating the Add-in:**
1. Create new Excel workbook
2. Import all `.bas` modules
3. Save as **Excel Add-in (.xlam)** in the Add-ins folder:
   - Windows: `C:\Users\<username>\AppData\Roaming\Microsoft\AddIns\`
   - Mac: `/Users/<username>/Library/Group Containers/UBF8T346G9.Office/User Content/Add-Ins/`
4. In Excel, go to **File → Options → Add-ins → Manage: Excel Add-ins → Go**
5. Browse and enable your add-in

**Using from any workbook:**
Once installed, functions are available in any workbook without importing.

### 9.3 Method 3: Worksheet Functions (UDFs)

The library can be exposed as **User-Defined Functions (UDFs)** callable from cells.

**Limitation:** VBA UDTs (Types) cannot be returned directly to cells.

**Solution:** Create wrapper functions that return individual values:

```vba
' Wrapper for worksheet use - returns Ast required
Public Function UDF_Ast_Required( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    D_mm As Double, _
    fck As Double, _
    fy As Double _
) As Double
    Dim result As FlexureResult
    result = IS456_FlexureDesign(Mu_kNm, b_mm, d_mm, D_mm, fck, fy)
    UDF_Ast_Required = result.Ast_required
End Function

' Wrapper - returns Mu limit
Public Function UDF_Mu_Limit( _
    b_mm As Double, _
    d_mm As Double, _
    fck As Double, _
    fy As Double _
) As Double
    UDF_Mu_Limit = Mu_limit_IS456(b_mm, d_mm, fck, fy)
End Function
```

**Usage in Excel cell:**
```
=UDF_Ast_Required(150, 300, 450, 500, 25, 415)
=UDF_Mu_Limit(300, 450, 25, 415)
```

Ensure `d_mm` is the **effective depth** (use `d_effective` helper once implemented to derive it from cover/stirrup/main bar sizes).

### 9.4 Referencing from Other VBA Modules

Within the same workbook, all public functions are directly accessible:

```vba
' In your own module (e.g., mod_BeamSchedule)
Option Explicit

Sub GenerateBeamSchedule()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("BeamInput")
    
    Dim i As Long
    For i = 2 To 100  ' Loop through beam data rows
        Dim Mu As Double, b As Double, d As Double
        Mu = ws.Cells(i, 3).Value  ' kN·m
        b = ws.Cells(i, 4).Value   ' mm
        d = ws.Cells(i, 5).Value   ' mm
        
        ' Call library function
        Dim Ast As Double
        Ast = Ast_singly_IS456(Mu, b, d, 25, 415)
        
        ' Write result back to sheet
        ws.Cells(i, 10).Value = Ast
    Next i
End Sub
```

### 9.5 Summary: How to Use

| Use Case | Method | Complexity |
|----------|--------|------------|
| Development/testing | Import .bas files | Easy |
| Single workbook tool | Import .bas files | Easy |
| Distribute to team | Excel Add-in (.xlam) | Medium |
| Cell formulas | UDF wrappers | Medium |
| ETABS integration macro | Import + call from your code | Easy |

---

## 10. Development Guidelines

> **📘 Full documentation:** See **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** for comprehensive coding standards, naming conventions, testing guidelines, and packaging instructions.

### 10.1 Summary

| Topic | Key Points |
|-------|------------|
| **VBA Standards** | `Option Explicit` mandatory; PascalCase for public functions; explicit `Double` types; no `Variant` |
| **Python Standards** | Type hints mandatory; snake_case naming; dataclasses for result types |
| **Units** | Convert to base units (N, mm, N·mm) at function entry; convert back at return |
| **Validation** | Validate at module boundaries; fail fast with structured errors; no MsgBox |
| **Testing** | Nominal + boundary + error cases; use SP:16 examples; document sources |
| **Versioning** | Semantic versioning (0.x.y); maintain CHANGELOG.md |
| **Distribution** | VBA: .bas files for dev, .xlam for release; Python: pip-installable package |

### 10.2 Quick Reference

**VBA function template:**
```vba
'-------------------------------------------------------------------------------
' FunctionName - Brief description
' Inputs: param1 (units), param2 (units)
' Returns: result (units); -1 on error
' Reference: IS 456:2000, Clause X.X
'-------------------------------------------------------------------------------
Public Function FunctionName(param1 As Double, param2 As Double) As Double
    ' Validation → Unit conversion → Calculation → Return
End Function
```

**Python function template:**
```python
def function_name(param1: float, param2: float) -> float:
    """Brief description. Reference: IS 456:2000, Clause X.X."""
    # Validation → Unit conversion → Calculation → Return
```

For detailed standards on naming, error handling, testing, Git workflow, and packaging, refer to the [Development Guide](DEVELOPMENT_GUIDE.md).

---

## 11. Implementation Plan

### 11.1 Phase Outline
1) **Scaffold**: Create `VBA/Modules`, `Python/structural_lib`, tests, examples; add `CHANGELOG.md` and `docs/API_REFERENCE.md` stub.  
2) **Data & Types**: Implement constants, enums, UDTs, Table 19/20 datasets, and neutral-axis ratios.  
3) **Utilities**: Units/conversion helpers, effective depth, pt calc, validation, linear interpolation.  
4) **Flexure**: `Mu_limit_IS456`, `Ast_singly_IS456`, wrapper `IS456_FlexureDesign`, plus tests against SP:16 cases.  
5) **Shear**: `tau_v`, `tau_c_IS456`, `tau_cmax_IS456`, `StirrupSpacing_IS456`, wrapper `IS456_ShearDesign`, plus tests.  
6) **API & UDFs**: Public façade module, worksheet UDF wrappers, and example module.  
7) **Packaging**: `.xlam` build script; Python packaging skeleton and publish workflow (optional until code parity).  
8) **QA**: Run boundary/regression suites, refresh docs (quick ref + API), and update version/changelog.

### 11.2 Definition of Done (per feature)
- Inputs validated with clear error codes/messages; no MsgBox/UI.
- Units documented and enforced; conversions centralized.
- Tests added/updated (nominal + boundary + failure) and passing.
- Docs/examples updated; public signatures stable and mirrored in Python/VBA.
- Version/changelog touched when API/behavior changes.

---

## 12. Future Extensibility

### 12.1 Flanged Beams (T-beam, L-beam)

Design API to accommodate future extension:

```vba
Public Enum BeamType
    RECTANGULAR = 0
    T_BEAM = 1
    L_BEAM = 2
End Enum

' Future signature (v2)
Public Function IS456_FlexureDesign_Flanged( _
    Mu_kNm As Double, _
    bw_mm As Double, _          ' Web width
    bf_mm As Double, _          ' Flange width
    Df_mm As Double, _          ' Flange depth
    d_mm As Double, _
    D_mm As Double, _
    fck As Double, _
    fy As Double, _
    beamType As BeamType _
) As FlexureResult
```

### 12.2 IS 13920 Ductile Detailing

Hook for future seismic provisions:

```vba
Public Type DuctileDetailingResult
    MinTopSteel_Ratio As Double       ' 0.24√(fck/fy)
    MaxSteel_Ratio As Double          ' 2.5%
    CriticalZoneLength_mm As Double   ' 2d from face of support
    MaxHoopSpacing_mm As Double
    HoopArea_mm2 As Double
End Type

' Future function
Public Function IS13920_DuctileDetailing( _
    b_mm As Double, d_mm As Double, _
    fck As Double, fy As Double _
) As DuctileDetailingResult
```

### 12.3 Doubly Reinforced Beams

Stub for v0.2:

```vba
' TODO: Implement in v0.2
Public Function Ast_doubly_IS456( _
    Mu_kNm As Double, _
    b_mm As Double, _
    d_mm As Double, _
    d_prime_mm As Double, _     ' Cover to compression steel
    fck As Double, _
    fy As Double _
) As DoublyReinforcedResult
```

### 12.4 Version Control

```vba
' In IS456_Constants.bas
Public Const LIB_VERSION As String = "0.1.0"
Public Const LIB_BUILD_DATE As String = "2025-12-10"
Public Const IS456_CODE_YEAR As String = "2000"

Public Function GetLibraryVersion() As String
    GetLibraryVersion = "IS456_RC_Lib v" & LIB_VERSION
End Function
```

---

## 13. Testing Strategy

### 13.1 Test Cases from SP:16 / Textbooks

| Test ID | Description | b | d | fck | fy | Mu | Expected Ast | Source |
|---------|-------------|---|---|-----|----|----|--------------|--------|
| F001 | Standard case | 300 | 450 | 20 | 415 | 150 | ~1050 mm² | SP:16 |
| F002 | Higher grade | 250 | 400 | 25 | 500 | 100 | ~720 mm² | Calc |
| F003 | Larger section | 300 | 500 | 30 | 415 | 200 | ~1300 mm² | Calc |
| F004 | Exceeds limit | 300 | 450 | 20 | 415 | 250 | DOUBLY | — |

### 13.2 Shear Test Cases

| Test ID | b | d | fck | pt% | Vu | Expected τc | Expected Status |
|---------|---|---|-----|-----|-----|-------------|-----------------|
| S001 | 300 | 450 | 20 | 1.0 | 150 | 0.62 | STIRRUPS_REQ |
| S002 | 300 | 450 | 25 | 0.5 | 50 | 0.49 | MIN_SHEAR |
| S003 | 300 | 450 | 20 | 1.0 | 400 | — | SECTION_INAD |

### 13.3 Boundary Tests

```vba
Public Sub Test_Boundaries()
    ' Table 19 exact values
    Debug.Assert Abs(tau_c_IS456(20, 0.15) - 0.28) < 0.001
    Debug.Assert Abs(tau_c_IS456(20, 3.0) - 0.82) < 0.001
    
    ' Clamping
    Debug.Assert Abs(tau_c_IS456(20, 0.1) - 0.28) < 0.001  ' Below min
    Debug.Assert Abs(tau_c_IS456(20, 5.0) - 0.82) < 0.001  ' Above max
    
    ' xu_max ratios
    Debug.Assert Abs(xu_max_ratio(250) - 0.53) < 0.001
    Debug.Assert Abs(xu_max_ratio(415) - 0.48) < 0.001
    Debug.Assert Abs(xu_max_ratio(500) - 0.46) < 0.001
    
    Debug.Print "All boundary tests passed!"
End Sub
```

### 13.4 Consistency Tests

Verify that calculated Ast produces the same moment when back-calculated:

```vba
Public Sub Test_Consistency()
    Dim Ast As Double, Mu_check As Double
    Ast = Ast_singly_IS456(150, 300, 450, 20, 415)
    
    ' Back-calculate moment
    Dim xu As Double
    xu = (0.87 * 415 * Ast) / (0.36 * 20 * 300)
    Mu_check = 0.87 * 415 * Ast * (450 - 0.42 * xu) / 1000000
    
    Debug.Assert Abs(150 - Mu_check) < 0.5  ' Within 0.5 kN·m
    Debug.Print "Consistency test passed!"
End Sub
```

---

## 14. Open Questions and Decisions

### 14.1 Decisions Needed Before Implementation

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | **Module structure:** Single mega-module vs. multiple modules? | A) Single `mod_SE_Lib_IS456.bas` <br> B) Multiple specialized modules | **B) Multiple modules** — better organization, easier to maintain |
| 2 | **Doubly reinforced:** Implement basic version or stub? | A) Implement now <br> B) Stub with TODO | **B) Stub** — focus on singly reinforced for v0 |
| 3 | **UDF wrappers:** Include in v0? | A) Yes, include wrappers <br> B) No, add in v0.2 | **A) Yes** — makes library immediately usable in worksheets |
| 4 | **Error return style:** Sentinel values vs. error codes? | A) Return -1 for errors <br> B) Use ErrorCode enum in Type | **Both** — -1 for simple functions, enum for complex results |
| 5 | **Distribution format:** .bas only vs. .xlam included? | A) .bas files only <br> B) Both .bas and .xlam | **B) Both** — .bas for development, .xlam for distribution |
| 6 | **Python priority:** Implement alongside VBA or after? | A) VBA first, Python later <br> B) Both simultaneously | **A) VBA first** — complete and test VBA, then port to Python |

### 14.2 Assumptions Made

1. **Cover calculation:** Using `d = D - cover - stirrup_dia - main_dia/2` (single layer of steel)
2. **Valid concrete grades:** M15, M20, M25, M30, M35, M40, M45, M50
3. **Valid steel grades:** Fe 250, Fe 415, Fe 500
4. **Table 19 interpolation:** Linear interpolation between pt% values; no interpolation between fck values (use next lower grade column)
5. **Moment sign:** Absolute value used for design; UI handles positive/negative distinction

### 14.3 References

- **IS 456:2000** — Indian Standard: Plain and Reinforced Concrete — Code of Practice
- **SP:16-1980** — Design Aids for Reinforced Concrete to IS 456
- **Limit State Design of Reinforced Concrete** — P.C. Varghese
- **Reinforced Concrete Design** — Pillai & Menon

---

## Appendix A: Quick Reference — Key Formulas

### Flexure (Singly Reinforced)

$$d = D - c - \phi_{st} - \frac{\phi_{main}}{2}$$

$$\frac{x_{u,max}}{d} = \begin{cases} 0.53 & \text{Fe 250} \\ 0.48 & \text{Fe 415} \\ 0.46 & \text{Fe 500} \end{cases}$$

$$M_{u,lim} = 0.36 f_{ck} \cdot b \cdot x_{u,max} \cdot (d - 0.42 x_{u,max})$$

$$A_{st} = \frac{0.5 f_{ck}}{f_y} \left[1 - \sqrt{1 - \frac{4.6 M_u}{f_{ck} b d^2}}\right] b \cdot d$$

### Shear

$$\tau_v = \frac{V_u}{b \cdot d}$$

$$p_t = \frac{100 \cdot A_{st}}{b \cdot d}$$

$$V_{us} = V_u - \tau_c \cdot b \cdot d$$

$$s_v = \frac{0.87 f_y \cdot A_{sv} \cdot d}{V_{us}}$$

$$s_{v,max} = \min(0.75d, 300 \text{ mm})$$

### Reinforcement Limits

$$A_{st,min} = \frac{0.85 \cdot b \cdot d}{f_y}$$

$$A_{st,max} = 0.04 \cdot b \cdot D$$

---

**End of Research Document**

## 15. ETABS Integration Research

### 15.1 Objective
To import beam forces (Mu, Vu) and geometry from ETABS into `tbl_BeamInput` for design verification.

### 15.2 Target Data (tbl_BeamInput)
We need to populate these columns for each beam:
*   **ID:** Beam Label (e.g., B1)
*   **Span:** Length (mm)
*   **Width (b):** mm
*   **Depth (D):** mm
*   **Mu (Start, Mid, End):** kN·m (Hogging/Sagging)
*   **Vu (Start, Mid, End):** kN

### 15.3 Source Data (ETABS CSV Export)
We recommend users export the **"Frame Assignments - Summary"** (for geometry) and **"Element Forces - Frames"** (for forces). However, a simpler approach for v0.6 is to use a single **"Beam Design Forces"** custom table or a specific standard table.

#### Recommended Standard Export: "Element Forces - Frames"
*   **Filter:** Select Design Combinations (e.g., 1.5(DL+LL)) or Envelope.
*   **Columns:**
    *   `Story`: Story Level (e.g., Story1)
    *   `Label`: Beam Name (e.g., B1)
    *   `Unique Name`: Unique ID (useful for joining, but Label is more user-friendly)
    *   `Station`: Distance from start (m or mm)
    *   `Output Case`: Load Combination
    *   `P`: Axial Force (kN) - *Ignore for pure beam design unless significant*
    *   `V2`: Major Shear (kN) - *Critical*
    *   `M3`: Major Moment (kN·m) - *Critical*

#### Geometry Source: "Frame Section Assignments"
*   **Columns:**
    *   `Story`
    *   `Label`
    *   `Analysis Section`: Section Property Name (e.g., "B230x450")
    *   `Length`: Clear span or center-to-center

### 15.4 Mapping Challenges & Logic
1.  **Station Mapping:** ETABS gives results at multiple stations (0, 0.5, 1.0, etc.).
    *   *Logic:*
        *   **Start:** Station = 0 (or min station)
        *   **End:** Station = Length (or max station)
        *   **Mid:** Station ≈ Length / 2
2.  **Sign Convention:**
    *   ETABS M3: Sagging is usually positive (check local axes).
    *   Our Lib: Sagging (+), Hogging (-).
    *   *Action:* User must confirm sign convention or we detect it.
3.  **Section Parsing:**
    *   ETABS Section Name: "B230x450" or "230x450 M25".
    *   *Logic:* Regex parse `(\d+)x(\d+)` to extract `b` and `D`.

### 15.5 Proposed CSV Schema (Intermediate Format)
To simplify the VBA parser, we can ask the user to prepare a "Cleaned CSV" or handle the raw export if it follows a strict template.

**Decision:** Support **Raw ETABS "Element Forces" CSV** but require the user to map headers in a config sheet or use standard ETABS header names.

**Standard ETABS Headers (v0.6 target):**
*   `Story`
*   `Label`
*   `Station`
*   `Output Case`
*   `V2`
*   `M3`
