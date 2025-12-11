# IS 456 RC Beam Design Library — API Reference

**Document Version:** 0.4.0  
**Last Updated:** December 11, 2025  
**Scope:** Public APIs for current Python/VBA implementations (flexure, shear, ductile detailing).

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
  - VBA (planned): User Defined Types (UDTs) for complex results, or simple types (`Double`) for helpers.
  - Python: `dataclasses` or simple types (`float`).
  - Excel UDFs: wrapper functions (VBA) to expose selected helpers (TBD).

---

## 2. Flexure Module (`M06_Flexure` / `flexure.py`)

### 2.1 Calculate Limiting Moment (`Mu_Lim`)
Calculates the maximum moment a singly reinforced section can resist.

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
Performs full design check including under/over-reinforced status and min/max steel checks; flags when Mu exceeds Mu_lim.

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

### 2.4 Design Doubly Reinforced Beam
Designs a beam that can be singly or doubly reinforced. If `Mu > Mu_lim`, calculates compression steel (`Asc`) and additional tension steel.

**Python:**
```python
def design_doubly_reinforced(
    b: float, 
    d: float, 
    d_dash: float, 
    d_total: float, 
    mu_knm: float, 
    fck: float, 
    fy: float
) -> FlexureResult
```

**Return Type (`FlexureResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `mu_lim` | float | Limiting moment capacity (kN·m) |
| `ast_required` | float | Required tension steel area (mm²) |
| `asc_required` | float | Required compression steel area (mm²) |
| `pt_provided` | float | Percentage of tension steel provided |
| `section_type` | Enum | `UNDER_REINFORCED`, `BALANCED`, `OVER_REINFORCED` |
| `xu` | float | Actual neutral axis depth (mm) |
| `xu_max` | float | Max neutral axis depth (mm) |
| `is_safe` | bool | True if design is valid |
| `error_message` | str | Details if unsafe |

---

## 3. Shear Module (`M07_Shear` / `shear.py`)

*(See existing documentation)*

---

## 4. Ductile Detailing Module (`M10_Ductile` / `ductile.py`)

### 4.1 Check Beam Ductility
Performs comprehensive checks for IS 13920:2016 compliance (geometry, min/max steel, confinement spacing).

**Python:**
```python
def check_beam_ductility(
    b: float, 
    D: float, 
    d: float, 
    fck: float, 
    fy: float, 
    min_long_bar_dia: float
) -> DuctileBeamResult
```

**Return Type (`DuctileBeamResult`):**
| Field | Type | Description |
|-------|------|-------------|
| `is_geometry_valid` | bool | True if b >= 200 and b/D >= 0.3 |
| `min_pt` | float | Min tension steel % (Cl 6.2.1) |
| `max_pt` | float | Max tension steel % (2.5%) |
| `confinement_spacing` | float | Max hoop spacing in plastic hinge zone (mm) |
| `remarks` | str | Compliance status or error details |

### 4.2 Helper Functions
- `check_geometry(b, D)`
- `get_min_tension_steel_percentage(fck, fy)`
- `calculate_confinement_spacing(d, min_long_bar_dia)`

---

### 2.5 Calculate Limiting Moment (Flanged)
Calculates the limiting moment of resistance for a T-beam section.

**Python:**
```python
def calculate_mu_lim_flanged(
    bw: float, 
    bf: float, 
    d: float, 
    Df: float, 
    fck: float, 
    fy: float
) -> float
```

### 2.6 Design Flanged Beam
Designs a flanged beam (T-beam). Handles neutral axis in flange (rectangular behavior), neutral axis in web (singly reinforced T), and doubly reinforced T-beams.

**Python:**
```python
def design_flanged_beam(
    bw: float, 
    bf: float, 
    d: float, 
    Df: float, 
    d_total: float, 
    mu_knm: float, 
    fck: float, 
    fy: float,
    d_dash: float = 50.0
) -> FlexureResult
```

---

## 3. Shear Module (`M07_Shear` / `shear.py`)

### 3.1 Calculate Nominal Shear Stress (`Tv`)
Calculates $\tau_v = \frac{V_u}{bd}$.

**Python:**
```python
def calculate_tv(
    vu_kn: float, 
    b: float, 
    d: float
) -> float
```

### 3.2 Design Shear Reinforcement
Performs shear design: checks $\tau_v$ vs $\tau_{c,max}$, gets $\tau_c$ (Table 19), computes $V_{us}$ and stirrup spacing with code limits.
- Table 19 policy: clamp pt to 0.15–3.0%; use nearest lower concrete grade column (no fck interpolation).
- Table 20: if $\tau_v > \tau_{c,max}$, section is inadequate.

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
| `tv` | float | Nominal shear stress (N/mm²) |
| `tc` | float | Design shear strength of concrete (N/mm²) |
| `tc_max` | float | Max shear stress limit (N/mm²) |
| `vus` | float | Shear to be resisted by stirrups (kN) |
| `spacing` | float | Governing stirrup spacing (mm) |
| `is_safe` | bool | True if $\tau_v \le \tau_{c,max}$ |
| `remarks` | str | Design status (e.g., "Shear reinforcement required") |

---

## 4. Excel User Defined Functions (UDFs)
Implemented in `M09_UDFs.bas` for direct worksheet use.

| Function | Description | Returns |
|----------|-------------|---------|
| `IS456_MuLim(b, d, fck, fy)` | Limiting Moment of Resistance | kN·m |
| `IS456_AstRequired(b, d, Mu, fck, fy)` | Required Tension Steel | mm² or "Over-Reinforced" |
| `IS456_ShearSpacing(Vu, b, d, fck, fy, Asv, pt)` | Stirrup Spacing | mm or "Unsafe..." |
| `IS456_MuLim_Flanged(bw, bf, d, Df, fck, fy)` | Limiting Moment (T-Beam) | kN·m |
| `IS456_Design_Rectangular(...)` | Full Design (Singly/Doubly) | Array [Ast, Asc, Xu, Status] |
| `IS456_Design_Flanged(...)` | Full Design (T-Beam) | Array [Ast, Asc, Xu, Status] |
| `IS456_Check_Ductility(b, D, d, fck, fy, db)` | IS 13920 Compliance Check | "Compliant" or Error Msg |
| `IS456_Tc(fck, pt)` | Table 19 Shear Strength | N/mm² |
| `IS456_TcMax(fck)` | Table 20 Max Shear Stress | N/mm² |

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

---

## 6. Ductile Detailing (IS 13920:2016) — `ductile.py` / `M10_Ductile.bas`

### 6.1 Geometry Check
**Python:**
```python
check_geometry(b: float, D: float) -> Tuple[bool, str]
```
- Valid if b ≥ 200 mm and b/D ≥ 0.3.

**VBA:**
```vba
Public Function Check_Geometry(b As Double, D As Double, ByRef ErrorMsg As String) As Boolean
```

### 6.2 Minimum/Maximum Tension Steel
**Python:**
```python
get_min_tension_steel_percentage(fck: float, fy: float) -> float  # returns %
get_max_tension_steel_percentage() -> float  # 2.5%
```

**VBA:**
```vba
Public Function Get_Min_Tension_Steel_Percentage(fck As Double, fy As Double) As Double
Public Function Get_Max_Tension_Steel_Percentage() As Double
```

### 6.3 Confinement Spacing (Plastic Hinge Zones)
**Python:**
```python
calculate_confinement_spacing(d: float, min_long_bar_dia: float) -> float  # mm
```
Spacing = min(d/4, 8*db_min, 100 mm).

**VBA:**
```vba
Public Function Calculate_Confinement_Spacing(d As Double, min_long_bar_dia As Double) As Double
```

### 6.4 Aggregate Check
**Python:**
```python
check_beam_ductility(
    b: float, D: float, d: float,
    fck: float, fy: float,
    min_long_bar_dia: float
) -> DuctileBeamResult
```

**VBA:**
```vba
Public Function Check_Beam_Ductility( _
    b As Double, D As Double, d As Double, _
    fck As Double, fy As Double, _
    min_long_bar_dia As Double _
) As DuctileBeamResult
```

**DuctileBeamResult Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `is_geometry_valid` | bool | Geometry check result |
| `min_pt` | float | Minimum tension steel (%) |
| `max_pt` | float | Maximum tension steel (%) |
| `confinement_spacing` | float | Max hoop spacing in hinge zone (mm) |
| `remarks` | str | "Compliant" or reason for failure |

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

### 5.3 Worked Examples (Reference Values)

Use these to sanity-check outputs (within typical rounding tolerance: ±0.5 kN·m for moments, ±1% for areas/stresses, spacing capped to code limits).

1) **Flexure — singly reinforced**
- Inputs: b=230 mm, d=450 mm, D=500 mm, Mu=150 kN·m, fck=25, fy=500.
- Expected: Mu_lim ≈ 163 kN·m; Ast_required ≈ 1040–1100 mm²; Pt ≈ 1.0–1.1%; xu_max = 0.46d.

2) **Shear — stirrups required**
- Inputs: b=230 mm, d=450 mm, Vu=100 kN, fck=20, fy_stirrup=415, pt=1.0%, 2-legged 8 mm stirrups (Asv≈100.5 mm²).
- Expected: τv ≈ 0.97 N/mm²; τc (M20, pt=1.0%) = 0.62 N/mm²; τv < τc,max=2.8; Vus ≈ 35–36 kN; spacing governed by max limits → 300 mm.

3) **Shear — unsafe section**
- Inputs: b=230 mm, d=450 mm, Vu=300 kN, fck=20, fy_stirrup=415, pt=1.0%, Asv=100.5 mm².
- Expected: τv ≈ 2.9 N/mm² > τc,max=2.8 → DesignStatus/remarks indicate section inadequate (increase b or d).

4) **Flexure — minimum steel governed**
- Inputs: b=230 mm, d=450 mm, D=500 mm, Mu=5 kN·m, fck=20, fy=415.
- Expected: Ast_min = 0.85*b*d/fy ≈ 212 mm²; result should return Ast = Ast_min with a “Minimum steel” note.
