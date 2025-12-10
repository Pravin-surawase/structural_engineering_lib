# IS 456 RC Beam Design Library — API Reference

**Document Version:** 0.1 (in development)  
**Last Updated:** December 10, 2025  
**Scope:** Public APIs for current Python implementation and planned VBA parity (signatures, inputs/outputs, units, status codes).

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
Planned in `M09_UDFs.bas` to wrap core functions for worksheet use. Align signatures/units with helpers above (TBD).

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
