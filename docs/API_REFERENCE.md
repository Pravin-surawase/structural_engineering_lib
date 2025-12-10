# IS 456 RC Beam Design Library — API Reference

**Document Version:** 1.0.0  
**Last Updated:** December 10, 2025  
**Scope:** Public APIs for VBA and Python implementations (signatures, inputs/outputs, units, status codes).

---

## 1. Conventions
- **Units:**
  - Moments (`Mu`, `Mu_Lim`): **kN·m**
  - Shear Forces (`Vu`, `Vus`): **kN**
  - Dimensions (`b`, `d`, `D`): **mm**
  - Areas (`Ast`, `Asv`): **mm²**
  - Stresses (`fck`, `fy`, `Tv`, `Tc`): **N/mm²** (MPa)
  - Percentages (`pt`): **%** (e.g., 1.2 for 1.2%)
- **Sign Conventions:**
  - Inputs are generally treated as absolute values for design checks.
  - UI/Application layer is responsible for handling signs before calling these libraries.
- **Return Values:**
  - VBA functions return User Defined Types (UDTs) for complex results, or simple types (`Double`) for helpers.
  - Python functions return `dataclasses` or simple types (`float`).
  - Excel UDFs return `Variant` (Value or Error String).

---

## 2. Flexure Module (`M06_Flexure` / `flexure.py`)

### 2.1 Calculate Limiting Moment (`Mu_Lim`)
Calculates the maximum moment a singly reinforced section can resist.

**VBA:**
```vba
Public Function Calculate_Mu_Lim( _
    ByVal b As Double, _
    ByVal d As Double, _
    ByVal fck As Double, _
    ByVal fy As Double _
) As Double
```

**Python:**
```python
def calculate_mu_lim(
    b: float, 
    d: float, 
    fck: float, 
    fy: float
) -> float
```

### 2.2 Calculate Required Steel (`Ast_Required`)
Calculates tension steel area for a given moment. Returns `-1` if `Mu > Mu_Lim`.

**VBA:**
```vba
Public Function Calculate_Ast_Required( _
    ByVal b As Double, _
    ByVal d As Double, _
    ByVal Mu_kNm As Double, _
    ByVal fck As Double, _
    ByVal fy As Double _
) As Double
```

**Python:**
```python
def calculate_ast_required(
    b: float, 
    d: float, 
    mu_knm: float, 
    fck: float, 
    fy: float
) -> float
```

### 2.3 Design Singly Reinforced Beam
Performs full design check including under/over-reinforced status, min/max steel checks, and deflection control (Xu).

**VBA:**
```vba
Public Function Design_Singly_Reinforced( _
    ByVal b As Double, _
    ByVal d As Double, _
    ByVal D_total As Double, _
    ByVal Mu_kNm As Double, _
    ByVal fck As Double, _
    ByVal fy As Double _
) As FlexureResult
```

**Python:**
```python
def design_singly_reinforced(
    b: float, 
    d: float, 
    d_total: float, 
    mu_knm: float, 
    fck: float, 
    fy: float
) -> FlexureResult
```

**Return Type (`FlexureResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `Mu_Lim` | Double | Limiting moment capacity (kN·m) |
| `Ast_Required` | Double | Required steel area (mm²) |
| `Pt_Provided` | Double | Percentage of steel provided |
| `SectionType` | Enum | `UnderReinforced` (0) or `OverReinforced` (1) |
| `Xu` | Double | Actual neutral axis depth (mm) |
| `Xu_max` | Double | Max neutral axis depth (mm) |
| `IsSafe` | Boolean | True if design is valid |
| `ErrorMessage` | String | Details if unsafe (e.g., "Mu > Mu_lim") |

---

## 3. Shear Module (`M07_Shear` / `shear.py`)

### 3.1 Calculate Nominal Shear Stress (`Tv`)
Calculates $\tau_v = \frac{V_u}{bd}$.

**VBA:**
```vba
Public Function Calculate_Tv( _
    ByVal Vu_kN As Double, _
    ByVal b As Double, _
    ByVal d As Double _
) As Double
```

**Python:**
```python
def calculate_tv(
    vu_kn: float, 
    b: float, 
    d: float
) -> float
```

### 3.2 Design Shear Reinforcement
Performs full shear design: checks $\tau_v$ vs $\tau_{c,max}$, calculates concrete capacity $\tau_c$, and determines stirrup spacing.

**VBA:**
```vba
Public Function Design_Shear( _
    ByVal Vu_kN As Double, _
    ByVal b As Double, _
    ByVal d As Double, _
    ByVal fck As Double, _
    ByVal fy As Double, _
    ByVal Asv As Double, _
    ByVal pt As Double _
) As ShearResult
```

**Python:**
```python
def design_shear(
    vu_kn: float, 
    b: float, 
    d: float, 
    fck: float, 
    fy: float, 
    asv: float, 
    pt: float
) -> ShearResult
```

**Return Type (`ShearResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `Tv` | Double | Nominal shear stress (N/mm²) |
| `Tc` | Double | Design shear strength of concrete (N/mm²) |
| `Tc_max` | Double | Max shear stress limit (N/mm²) |
| `Vus` | Double | Shear force to be resisted by stirrups (kN) |
| `Spacing` | Double | Required stirrup spacing (mm) |
| `IsSafe` | Boolean | True if $\tau_v \le \tau_{c,max}$ |
| `Remarks` | String | Design status (e.g., "Shear reinforcement required") |

---

## 4. Excel User Defined Functions (UDFs)
These functions are exposed directly to Excel cells via `M09_UDFs.bas`.

| Function Name | Arguments | Returns | Description |
|---------------|-----------|---------|-------------|
| `IS456_MuLim` | `b, d, fck, fy` | `Double` | Limiting moment (kN·m) |
| `IS456_AstRequired` | `b, d, Mu, fck, fy` | `Double` or `String` | Ast (mm²) or "Over-Reinforced" |
| `IS456_ShearSpacing` | `Vu, b, d, fck, fy, Asv, pt` | `Double` or `String` | Spacing (mm) or Error Message |
| `IS456_Tc` | `fck, pt` | `Double` | $\tau_c$ from Table 19 |
| `IS456_TcMax` | `fck` | `Double` | $\tau_{c,max}$ from Table 20 |

---

## 5. Usage Examples

### 5.1 Python Example
```python
from structural_lib.flexure import design_singly_reinforced

# Design a beam for 150 kNm moment
result = design_singly_reinforced(
    b=230, 
    d=450, 
    d_total=500, 
    mu_knm=150.0, 
    fck=25, 
    fy=500
)

if result.is_safe:
    print(f"Ast Required: {result.ast_required:.2f} mm²")
    print(f"Pt Provided: {result.pt_provided:.2f}%")
else:
    print(f"Design Failed: {result.error_message}")
```

### 5.2 VBA Example
```vba
Sub TestBeam()
    Dim res As FlexureResult
    ' Design for 150 kNm
    res = Design_Singly_Reinforced(230, 450, 500, 150, 25, 500)
    
    If res.IsSafe Then
        Debug.Print "Ast Required: " & res.Ast_Required
    Else
        Debug.Print "Design Failed: " & res.ErrorMessage
    End If
End Sub
```
