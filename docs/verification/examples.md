# Verification Examples Pack

**Version:** 1.0  
**Last Updated:** 2025-12-26  
**Purpose:** Build trust through traceable, verifiable benchmark calculations.

---

## 1. Overview

This document provides benchmark examples that engineers can use to verify the library's calculations against:
- Hand calculations
- SP 16 design aids
- Textbook examples
- Other trusted software

Each example includes:
- Input parameters with explicit units
- Expected outputs with tolerances
- IS 456 clause references
- Calculation trace for manual verification

---

## 2. Flexure Design Examples

### Example F1: Singly Reinforced Rectangular Beam (Under-Reinforced)

**Source:** Standard IS 456 design problem

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| b (width) | 230 | mm |
| D (overall depth) | 500 | mm |
| d (effective depth) | 450 | mm |
| Mu (design moment) | 100 | kN·m |
| fck | 20 | N/mm² |
| fy | 415 | N/mm² |

**Expected Output:**
| Result | Value | Tolerance | IS 456 Reference |
|--------|-------|-----------|------------------|
| Mu,lim | 128.51 | ±0.5 kN·m | Annex G |
| Ast,req | 719.6 | ±5 mm² | Cl 38.1 |
| xu | 156.9 | ±1 mm | Cl 38.1 |
| xu,max | 216.0 | ±0.1 mm | Cl 38.1 |
| Section Type | Under-reinforced | — | — |

**Verification Command:**
```python
from structural_lib import flexure

result = flexure.design_singly_reinforced(
    b=230, d=450, d_total=500,
    mu_knm=100, fck=20, fy=415
)
print(f"Mu,lim = {result.mu_lim:.2f} kN·m")
print(f"Ast,req = {result.ast_required:.1f} mm²")
```

**Hand Calculation Check:**
```
xu,max/d = 0.48 (for Fe415, IS 456 Cl 38.1)
xu,max = 0.48 × 450 = 216 mm

Mu,lim = 0.36 × fck × b × xu,max × (d - 0.42×xu,max)
       = 0.36 × 20 × 230 × 216 × (450 - 90.72)
       = 128.51 kN·m

Since Mu (100) < Mu,lim (128.51), section is under-reinforced.
```

---

### Example F2: Doubly Reinforced Rectangular Beam

**Source:** SP 16 style problem

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| b | 300 | mm |
| D | 500 | mm |
| d | 450 | mm |
| d' | 50 | mm |
| Mu | 250 | kN·m |
| fck | 25 | N/mm² |
| fy | 500 | N/mm² |

**Expected Output:**
| Result | Value | Tolerance |
|--------|-------|-----------|
| Mu,lim | 202.91 | ±0.5 kN·m |
| Ast,req | 1550.4 | ±10 mm² |
| Asc,req | 296.6 | ±5 mm² |
| Section Type | Over-reinforced | — |

**Verification Command:**
```python
from structural_lib import flexure

result = flexure.design_doubly_reinforced(
    b=300, d=450, d_dash=50, d_total=500,
    mu_knm=250, fck=25, fy=500
)
print(f"Ast,req = {result.ast_required:.1f} mm²")
print(f"Asc,req = {result.asc_required:.1f} mm²")
```

---

### Example F3: Flanged Beam (T-Beam)

**Source:** IS 456 T-beam design

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| bw (web width) | 300 | mm |
| bf (flange width) | 1000 | mm |
| D | 550 | mm |
| d | 500 | mm |
| Df (flange depth) | 150 | mm |
| Mu | 200 | kN·m |
| fck | 25 | N/mm² |
| fy | 500 | N/mm² |

**Expected Output:**
| Result | Value | Tolerance |
|--------|-------|-----------|
| Mu,lim | 835.04 | ±1 kN·m |
| Ast,req | 956.6 | ±10 mm² |
| xu | 46.24 | ±1 mm |
| NA Location | In flange | — |

**Verification Command:**
```python
from structural_lib import flexure

Df = 150
result = flexure.design_flanged_beam(
    bw=300, bf=1000, d=500, Df=Df, d_total=550,
    mu_knm=200, fck=25, fy=500
)
print(f"Mu,lim = {result.mu_lim:.2f} kN·m")
print(f"Ast,req = {result.ast_required:.1f} mm²")
print(f"xu = {result.xu:.2f} mm")
print(f"NA in flange: {result.xu <= Df}")
```

---

## 3. Shear Design Examples

### Example S1: Shear with Stirrup Design

**Source:** IS 456 shear design

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| b | 230 | mm |
| d | 450 | mm |
| Vu | 150 | kN |
| fck | 20 | N/mm² |
| fy | 415 | N/mm² |
| Asv (2L-8φ) | 100 | mm² |
| pt | 1.0 | % |

**Expected Output:**
| Result | Value | Tolerance | IS 456 Reference |
|--------|-------|-----------|------------------|
| τv | 1.449 | ±0.01 N/mm² | Cl 40.1 |
| τc | 0.62 | ±0.01 N/mm² | Table 19 |
| τc,max | 2.8 | ±0.1 N/mm² | Table 20 |
| Vus | 85.83 | ±1 kN | Cl 40.4 |
| Sv (spacing) | 189.3 | ±2 mm | Cl 40.4 |

**Verification Command:**
```python
from structural_lib import shear

result = shear.design_shear(
    vu_kn=150, b=230, d=450,
    fck=20, fy=415, asv=100, pt=1.0
)
print(f"τv = {result.tv:.3f} N/mm²")
print(f"τc = {result.tc:.2f} N/mm²")
print(f"Spacing = {result.spacing:.1f} mm")
```

**Hand Calculation Check:**
```
τv = Vu / (b × d) = 150,000 / (230 × 450) = 1.449 N/mm²

From IS 456 Table 19 for M20, pt=1.0%:
τc = 0.62 N/mm²

Since τv > τc, shear reinforcement required.
Vus = Vu - τc × b × d = 150 - 0.62 × 230 × 450/1000 = 85.83 kN

Sv = 0.87 × fy × Asv × d / Vus
   = 0.87 × 415 × 100 × 450 / 85830 = 189.3 mm
```

---

## 4. Serviceability Examples

### Example SV1: Deflection Check (Span/Depth Ratio)

**Source:** IS 456 Cl 23.2.1

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| Span | 4000 | mm |
| d (effective depth) | 450 | mm |
| Support condition | Simply supported | — |

**Expected Output:**
| Result | Value | Reference |
|--------|-------|-----------|
| L/d (actual) | 8.89 | — |
| L/d (allowable) | 20 | IS 456 Cl 23.2.1 |
| Status | OK | — |

**Verification Command:**
```python
from structural_lib import serviceability

result = serviceability.check_deflection_span_depth(
    span_mm=4000, d_mm=450, support_condition="simply_supported"
)
print(f"L/d = {result.computed['ld_ratio']:.2f}")
print(f"Allowable = {result.computed['allowable_ld']}")
print(f"Status: {'OK' if result.is_ok else 'FAIL'}")
```

---

### Example SV2: Crack Width Check (Annex F)

**Source:** IS 456 Annex F

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| Exposure class | Moderate | — |
| Limit | 0.3 | mm |
| acr | 50 | mm |
| cmin | 25 | mm |
| h | 500 | mm |
| x | 200 | mm |
| εm | 0.001 | — |

**Expected Output:**
| Result | Value | Tolerance |
|--------|-------|-----------|
| wcr (calculated) | 0.129 | ±0.01 mm |
| Status | OK | — |

---

## 5. Detailing Examples

### Example D1: Development Length

**Source:** IS 456 Cl 26.2.1

**Input:**
| Parameter | Value | Unit |
|-----------|-------|------|
| Bar diameter | 16 | mm |
| fck | 25 | N/mm² |
| fy | 500 | N/mm² |
| Bar type | Deformed | — |

**Expected Output:**
| Result | Value | Formula |
|--------|-------|---------|
| τbd | 2.24 | Table 5.3 × 1.6 |
| Ld | 752 | φ × 0.87fy / (4 × τbd) |

**Verification Command:**
```python
from structural_lib import detailing

ld = detailing.calculate_development_length(
    bar_dia=16, fck=25, fy=500, bar_type="deformed"
)
print(f"Ld = {ld:.0f} mm")
```

**Hand Calculation:**
```
τbd = 1.4 × 1.6 = 2.24 N/mm² (M25, deformed bars)
Ld = (φ × 0.87 × fy) / (4 × τbd)
   = (16 × 0.87 × 500) / (4 × 2.24)
   = 752 mm
```

---

## 6. Compliance Check Example

### Example C1: Multi-Case Compliance Report

**Input:**
```json
{
  "beam": {
    "b_mm": 300, "D_mm": 500, "d_mm": 450,
    "fck_nmm2": 25, "fy_nmm2": 500
  },
  "cases": [
    {"case_id": "DL+LL", "mu_knm": 80, "vu_kn": 60},
    {"case_id": "1.5(DL+LL)", "mu_knm": 120, "vu_kn": 200}
  ]
}
```

**Expected Output:**
| Case | Flexure | Shear | Overall |
|------|---------|-------|---------|
| DL+LL | OK | OK | OK |
| 1.5(DL+LL) | OK | OK | OK |
| **Governing** | — | — | 1.5(DL+LL) |

---

## 7. Running Verification Tests

### Full Verification Suite
```bash
cd Python/
python -m pytest tests/test_verification_pack.py -v
```

### Quick Smoke Test
```bash
python -m pytest tests/test_verification_pack.py -v -k "case_01 or case_04"
```

### Generate Verification Report
```bash
python -m pytest tests/test_verification_pack.py -v --tb=short > verification_report.txt
```

---

## 8. Comparison with Other Tools

| Check | This Library | SP 16 Chart | Hand Calc | ETABS |
|-------|-------------|-------------|-----------|-------|
| Mu,lim (Ex F1) | 128.51 | 128.5 | 128.51 | — |
| Ast (Ex F1) | 719.6 | ~720 | 719.6 | — |
| τc (Ex S1) | 0.62 | 0.62 | 0.62 | — |

---

## 9. Tolerances and Rounding

| Quantity | Tolerance | Rounding |
|----------|-----------|----------|
| Moment (kN·m) | ±0.5 | 2 decimals |
| Area (mm²) | ±5 | 1 decimal |
| Stress (N/mm²) | ±0.01 | 3 decimals |
| Spacing (mm) | ±2 | Integer |
| Development length (mm) | ±5 | Integer |

These tolerances account for:
- Different interpolation methods for Table 19/20
- Rounding at intermediate steps
- Floating-point precision

---

## 10. Adding New Verification Cases

To add a new benchmark:

1. Add test to `tests/test_verification_pack.py`:
```python
def test_verification_new_case_XX():
    """Description with source reference."""
    result = module.function(inputs)
    assert r9(result.field) == expected_value
```

2. Document in this file with hand calculation trace.

3. Run and verify:
```bash
python -m pytest tests/test_verification_pack.py::test_verification_new_case_XX -v
```
---

## Appendix A: Detailed Worked Examples with Full IS 456 Derivations

These examples show complete hand calculations matching IS 456:2000 methodology, allowing engineers to verify the library's accuracy step-by-step.

### A.1 Singly Reinforced Beam — Complete Derivation

**Problem:** Design a simply supported rectangular beam for a residential building.

**Given:**
- Beam size: 230 mm × 450 mm (b × D)
- Clear cover: 40 mm, Stirrup: 8 mm diameter
- Effective depth: d = 450 - 40 - 8 = 402 mm (use 400 mm for calculation)
- Concrete: M20 (fck = 20 N/mm²)
- Steel: Fe415 (fy = 415 N/mm²)
- Factored moment: Mu = 60 kN·m
- Factored shear: Vu = 80 kN

**Step 1: Check Limiting Moment (Mu,lim)**

From IS 456:2000, Annex G, Table E:
- For Fe415: xu,max/d = 0.48

```
xu,max = 0.48 × 400 = 192 mm
```

Limiting moment of resistance (IS 456, Annex G):
```
Mu,lim = 0.36 × fck × b × xu,max × (d - 0.42 × xu,max)
       = 0.36 × 20 × 230 × 192 × (400 - 0.42 × 192)
       = 0.36 × 20 × 230 × 192 × (400 - 80.64)
       = 0.36 × 20 × 230 × 192 × 319.36
       = 101,540,044.8 N·mm
       = 101.54 kN·m
```

**Check:** Mu = 60 kN·m < Mu,lim = 101.54 kN·m → **Singly reinforced section** ✓

**Step 2: Calculate Neutral Axis Depth (xu)**

From moment equilibrium:
```
Mu = 0.36 × fck × b × xu × (d - 0.42 × xu)
```

Rearranging into quadratic form:
```
0.36 × fck × b × 0.42 × xu² - 0.36 × fck × b × d × xu + Mu = 0
```

Substituting values:
```
a = 0.36 × 20 × 230 × 0.42 = 695.52
b = -0.36 × 20 × 230 × 400 = -662,400
c = 60 × 10⁶ = 60,000,000

xu = [-b - √(b² - 4ac)] / 2a
   = [662,400 - √(438,773,760,000 - 166,809,600,000)] / 1391.04
   = [662,400 - √271,964,160,000] / 1391.04
   = [662,400 - 521,501.5] / 1391.04
   = 101.3 mm
```

**Step 3: Calculate Required Steel Area (Ast)**

From force equilibrium (compression = tension):
```
0.36 × fck × b × xu = 0.87 × fy × Ast

Ast = (0.36 × fck × b × xu) / (0.87 × fy)
    = (0.36 × 20 × 230 × 101.3) / (0.87 × 415)
    = 167,648.4 / 361.05
    = 464.3 mm²
```

**Step 4: Library Verification**

```python
from structural_lib import api

result = api.design_beam_is456(
    units="IS456",
    case_id="Example-A1",
    b_mm=230, D_mm=450, d_mm=400,
    fck_nmm2=20, fy_nmm2=415,
    mu_knm=60, vu_kn=80,
)

print(f"Mu,lim = {result.flexure.mu_lim:.2f} kN·m")  # 101.54
print(f"xu = {result.flexure.xu:.1f} mm")            # 101.2
print(f"Ast = {result.flexure.ast_required:.1f} mm²") # 464.3
```

**Comparison:**
| Parameter | Hand Calc | Library | Δ |
|-----------|-----------|---------|---|
| Mu,lim | 101.54 kN·m | 101.54 kN·m | 0% |
| xu | 101.3 mm | 101.2 mm | 0.1% |
| Ast | 464.3 mm² | 464.3 mm² | 0% |

**Result: ✅ PASS**

---

### A.2 Doubly Reinforced Beam — Complete Derivation

**Problem:** Design a beam where applied moment exceeds limiting moment.

**Given:**
- Beam size: 300 mm × 500 mm (b × D)
- Effective depth: d = 450 mm
- Compression steel depth: d' = 50 mm
- Concrete: M25 (fck = 25 N/mm²)
- Steel: Fe500 (fy = 500 N/mm²)
- Factored moment: Mu = 280 kN·m

**Step 1: Check Limiting Moment**

From IS 456, Table E:
- For Fe500: xu,max/d = 0.46

```
xu,max = 0.46 × 450 = 207 mm

Mu,lim = 0.36 × 25 × 300 × 207 × (450 - 0.42 × 207)
       = 0.36 × 25 × 300 × 207 × (450 - 86.94)
       = 0.36 × 25 × 300 × 207 × 363.06
       = 202,914,234 N·mm
       = 202.91 kN·m
```

**Check:** Mu = 280 kN·m > Mu,lim = 202.91 kN·m → **Doubly reinforced section required** ✓

**Step 2: Calculate Excess Moment (Mu2)**

```
Mu2 = Mu - Mu,lim = 280 - 202.91 = 77.09 kN·m
```

**Step 3: Calculate Compression Steel Stress (fsc)**

Strain at compression steel level (from strain diagram):
```
εsc = 0.0035 × (1 - d'/xu,max)
    = 0.0035 × (1 - 50/207)
    = 0.0035 × 0.7585
    = 0.002655
```

**Important:** For HYSD bars, stress is NOT simply Es × ε. We must use SP:16 Table A (design stress-strain curve).

SP:16 Table A for Fe500:
| Strain | Stress (N/mm²) |
|--------|----------------|
| 0.00174 | 347.8 |
| 0.00195 | 369.6 |
| 0.00226 | 391.3 |
| 0.00277 | 413.0 |
| 0.00380 | 434.8 |

Interpolating for ε = 0.002655 (between 0.00226 and 0.00277):
```
fsc = 391.3 + (413.0 - 391.3) × (0.002655 - 0.00226) / (0.00277 - 0.00226)
    = 391.3 + 21.7 × 0.000395 / 0.00051
    = 391.3 + 16.8
    = 408.1 N/mm² (library uses 407.89)
```

**Note:** The simplified formula fsc = min(Es × ε, 0.87 × fy) = 435 N/mm² overestimates stress. SP:16 interpolation is more accurate.

**Step 4: Calculate Compression Steel Area (Asc)**

Concrete stress at compression steel level:
```
fcc = 0.446 × fck = 0.446 × 25 = 11.15 N/mm²
```

From moment equilibrium for Mu2:
```
Mu2 = Asc × (fsc - fcc) × (d - d')

Asc = Mu2 / [(fsc - fcc) × (d - d')]
    = 77.09 × 10⁶ / [(407.89 - 11.15) × (450 - 50)]
    = 77,090,000 / [396.74 × 400]
    = 77,090,000 / 158,696
    = 485.8 mm²
```

**Step 5: Calculate Tension Steel Area (Ast)**

Ast consists of two parts:
- Ast1: For resisting Mu,lim
- Ast2: For balancing Asc

```
Ast1 = (0.36 × fck × b × xu,max) / (0.87 × fy)
     = (0.36 × 25 × 300 × 207) / (0.87 × 500)
     = 558,900 / 435
     = 1284.8 mm²

Ast2 = Asc × (fsc - fcc) / (0.87 × fy)
     = 485.8 × 396.74 / 435
     = 443.1 mm²

Ast = Ast1 + Ast2 = 1284.8 + 443.1 = 1727.9 mm²
```

**Step 6: Library Verification**

```python
from structural_lib import api

result = api.design_beam_is456(
    units="IS456",
    b_mm=300, D_mm=500, d_mm=450, d_dash_mm=50,
    fck_nmm2=25, fy_nmm2=500,
    mu_knm=280, vu_kn=120,
)

print(f"Mu,lim = {result.flexure.mu_lim:.2f} kN·m")  # 202.91
print(f"Ast = {result.flexure.ast_required:.1f} mm²") # 1722.8
print(f"Asc = {result.flexure.asc_required:.1f} mm²") # 485.5
```

**Comparison:**
| Parameter | Hand Calc | Library | Δ |
|-----------|-----------|---------|---|
| Mu,lim | 202.91 kN·m | 202.91 kN·m | 0% |
| Asc | 485.8 mm² | 485.5 mm² | 0.06% |
| Ast | 1727.9 mm² | 1722.8 mm² | 0.3% |

**Result: ✅ PASS**

**Key Insight:** The library uses SP:16 stress-strain interpolation for HYSD bars, which is more accurate than the simplified elastic-perfectly-plastic model used in many textbooks.

---

### A.3 Why Library Results Differ from Simplified Textbook Formulas

Some textbooks use simplified formulas that can differ by 5-10% from rigorous IS 456 calculations. The library implements the more accurate approach:

| Aspect | Simplified (Textbook) | Library (IS 456 Rigorous) |
|--------|----------------------|---------------------------|
| **Compression steel stress (fsc)** | fsc = min(Es × ε, 0.87 × fy) | SP:16 Table A interpolation |
| **Concrete at comp. steel** | Often ignored | fcc = 0.446 × fck deducted |
| **xu,max/d ratios** | Approximate values | Exact IS 456 Table E values |
| **Shear τc** | Linear interpolation | Table 19 with proper pt clamping |

**Why this matters:**
- Simplified formulas can underestimate compression steel by ~10%
- Overestimating fsc leads to unconservative designs
- SP:16 curves account for actual HYSD bar behavior

---
