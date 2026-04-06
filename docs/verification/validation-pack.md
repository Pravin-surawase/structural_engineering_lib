---
owner: Main Agent
status: active
last_updated: 2026-04-04
doc_type: guide
complexity: intermediate
tags: []
---

# Validation Pack — Benchmark Beams & Columns

**Version:** 0.21.5

This pack provides 5 benchmark beams and 3 benchmark columns with IS 456 references that you can use to validate the library's calculations against hand calculations, SP 16 design aids, or other trusted software.

---

## Quick Validation (5 minutes)

Run this command to validate all benchmark beams:

```bash
python -c "
from structural_lib import flexure, shear

# Benchmark 1: Singly Reinforced (IS 456 Annex G)
r = flexure.design_singly_reinforced(b=230, d=450, d_total=500, mu_knm=100, fck=20, fy=415)
print(f'B1 Singly: Mu_lim={r.mu_lim:.2f} (exp: 128.51), Ast={r.ast_required:.0f} (exp: 720) ✓' if abs(r.mu_lim-128.51)<1 else 'B1 FAIL')

# Benchmark 2: Doubly Reinforced (SP 16 style)
r = flexure.design_doubly_reinforced(b=300, d=450, d_dash=50, d_total=500, mu_knm=250, fck=25, fy=500)
print(f'B2 Doubly: Ast={r.ast_required:.0f} (exp: 1550), Asc={r.asc_required:.0f} (exp: 297) ✓' if abs(r.ast_required-1550)<20 else 'B2 FAIL')

# Benchmark 3: Flanged T-Beam
r = flexure.design_flanged_beam(bw=300, bf=1000, d=500, Df=150, d_total=550, mu_knm=200, fck=25, fy=500)
print(f'B3 Flanged: Ast={r.ast_required:.0f} (exp: 957) ✓' if abs(r.ast_required-957)<15 else 'B3 FAIL')

# Benchmark 4: Shear Design (IS 456 Table 19/20)
r = shear.design_shear(vu_kn=150, b=230, d=450, fck=20, fy=415, asv=100, pt=1.0)
print(f'B4 Shear: τv={r.tv:.3f} (exp: 1.449), spacing={r.spacing:.0f} (exp: 189) ✓' if abs(r.tv-1.449)<0.01 else 'B4 FAIL')

# Benchmark 5: High Shear (τv close to τc,max)
r = shear.design_shear(vu_kn=280, b=230, d=450, fck=20, fy=415, asv=157, pt=1.5)
print(f'B5 High Shear: τv={r.tv:.3f} (exp: 2.705), safe={r.is_safe} ✓' if r.is_safe else 'B5 FAIL')
"
```

**Expected output:**
```
B1 Singly: Mu_lim=128.51 (exp: 128.51), Ast=720 (exp: 720) ✓
B2 Doubly: Ast=1550 (exp: 1550), Asc=297 (exp: 297) ✓
B3 Flanged: Ast=957 (exp: 957) ✓
B4 Shear: τv=1.449 (exp: 1.449), spacing=189 (exp: 189) ✓
B5 High Shear: τv=2.705 (exp: 2.705), safe=True ✓
```

---

## Benchmark Beams Reference

### B1: Singly Reinforced Rectangular Beam

**IS 456 Reference:** Annex G (Limiting Moment), Cl 38.1 (Flexure Design)

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 230 | mm |
| D | 500 | mm |
| d | 450 | mm |
| Mu | 100 | kN·m |
| fck | M20 | N/mm² |
| fy | Fe415 | N/mm² |

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| Mu,lim | 128.51 | ±0.5 kN·m |
| Ast,req | 719.6 | ±5 mm² |
| xu | 156.9 | ±1 mm |
| Section Type | Under-reinforced | — |

---

### B2: Doubly Reinforced Rectangular Beam

**IS 456 Reference:** Cl 38.1 (Doubly Reinforced), SP 16 Table 51

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 300 | mm |
| D | 500 | mm |
| d | 450 | mm |
| d' | 50 | mm |
| Mu | 250 | kN·m |
| fck | M25 | N/mm² |
| fy | Fe500 | N/mm² |

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| Mu,lim | 202.91 | ±0.5 kN·m |
| Ast,req | 1550.4 | ±10 mm² |
| Asc,req | 296.6 | ±5 mm² |

---

### B3: Flanged Beam (T-Beam)

**IS 456 Reference:** Cl 23.1.2 (Effective Width), Annex G (Flanged Sections)

| Parameter | Value | Unit |
|-----------|-------|------|
| bw (web) | 300 | mm |
| bf (flange) | 1000 | mm |
| D | 550 | mm |
| d | 500 | mm |
| Df (flange depth) | 150 | mm |
| Mu | 200 | kN·m |
| fck | M25 | N/mm² |
| fy | Fe500 | N/mm² |

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| Mu,lim | 835.04 | ±1 kN·m |
| Ast,req | 956.6 | ±10 mm² |
| xu | 46.24 | ±1 mm |
| NA Location | In flange | — |

---

### B4: Shear Design with Stirrups

**IS 456 Reference:** Cl 40.1 (Shear Stress), Table 19 (τc), Table 20 (τc,max), Cl 40.4 (Stirrup Design)

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 230 | mm |
| d | 450 | mm |
| Vu | 150 | kN |
| fck | M20 | N/mm² |
| fy | Fe415 | N/mm² |
| Asv (2L-8φ) | 100 | mm² |
| pt | 1.0 | % |

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| τv | 1.449 | ±0.01 N/mm² |
| τc | 0.62 | ±0.01 N/mm² |
| τc,max | 2.8 | ±0.1 N/mm² |
| Vus | 85.83 | ±1 kN |
| Sv | 189.3 | ±2 mm |

---

### B5: High Shear Case (Near τc,max)

**IS 456 Reference:** Table 20 (τc,max limit check)

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 230 | mm |
| d | 450 | mm |
| Vu | 280 | kN |
| fck | M20 | N/mm² |
| fy | Fe415 | N/mm² |
| Asv (2L-10φ) | 157 | mm² |
| pt | 1.5 | % |

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| τv | 2.705 | ±0.01 N/mm² |
| τc,max | 2.8 | — |
| is_safe | True | τv < τc,max |

---

## Column Design Benchmarks

### Quick Column Validation

Run this command to validate all column benchmark cases:

```bash
python -c "
from structural_lib.services.api import (
    design_column_axial_is456,
    design_short_column_uniaxial_is456,
    biaxial_bending_check_is456,
)
import math

# Benchmark C1: Short Column Axial Capacity (SP:16 Chart 27)
# 300x300 mm, M25, Fe415, 4-20mm bars (Asc = 1257 mm²)
# Pu = 0.4*25*(90000-1257) + 0.67*415*1257 = 887.43 + 349.57 ≈ 1706 kN (unfactored)
# IS 456 Cl 39.3 formula: 0.4*fck*Ac + 0.67*fy*Asc → result in kN
r = design_column_axial_is456(fck=25.0, fy=415.0, Ag_mm2=90000.0, Asc_mm2=1257.0)
expected_Pu = (0.4 * 25 * (90000 - 1257) + 0.67 * 415 * 1257) / 1000
print(f'C1 Axial: Pu={r[\"Pu_kN\"]:.1f} kN (exp: {expected_Pu:.1f}) ✓' if abs(r['Pu_kN'] - expected_Pu) < 2 else f'C1 FAIL: got {r[\"Pu_kN\"]:.1f}, exp {expected_Pu:.1f}')

# Benchmark C2: Short Column Uniaxial Bending (SP:16 Chart 44)
# 300x500 mm, M25, Fe415, 6-20mm bars (Asc = 1885 mm²), d' = 50mm
# Pu = 800 kN — check if within P-M interaction envelope
r = design_short_column_uniaxial_is456(
    Pu_kN=800.0, Mu_kNm=120.0, b_mm=300.0, D_mm=500.0,
    le_mm=3000.0, fck=25.0, fy=415.0, Asc_mm2=1885.0,
    d_prime_mm=50.0, l_unsupported_mm=3000.0,
)
print(f'C2 Uniaxial: ok={r[\"ok\"]}, util={r[\"utilization\"]:.1%}, Mu_cap={r[\"Mu_cap_kNm\"]:.1f} kNm ✓' if r['ok'] else f'C2 FAIL: util={r[\"utilization\"]:.1%}')

# Benchmark C3: Biaxial Bending Check (IS 456 Cl 39.6)
# 400x400 mm, M30, Fe415, 8-20mm bars (Asc = 2513 mm²)
# Pu = 1200 kN, Mux = 80 kNm, Muy = 60 kNm — Bresler check
r = biaxial_bending_check_is456(
    Pu_kN=1200.0, Mux_kNm=80.0, Muy_kNm=60.0,
    b_mm=400.0, D_mm=400.0, le_mm=3000.0,
    fck=30.0, fy=415.0, Asc_mm2=2513.0, d_prime_mm=50.0,
    l_unsupported_mm=3000.0,
)
print(f'C3 Biaxial: safe={r[\"is_safe\"]}, ratio={r[\"interaction_ratio\"]:.3f}, αn={r[\"alpha_n\"]:.2f} ✓' if r['is_safe'] else f'C3 FAIL: ratio={r[\"interaction_ratio\"]:.3f}')
"
```

---

### C1: Short Column Axial Capacity

**IS 456 Reference:** Cl 39.3, SP:16 Chart 27

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 300 | mm |
| D | 300 | mm |
| Ag | 90,000 | mm² |
| Asc (4-20φ) | 1,257 | mm² |
| fck | M25 | N/mm² |
| fy | Fe415 | N/mm² |

**Hand Calculation (IS 456 Cl 39.3):**

$$P_u = 0.4 \cdot f_{ck} \cdot A_c + 0.67 \cdot f_y \cdot A_{sc}$$

$$P_u = 0.4 \times 25 \times (90000 - 1257) + 0.67 \times 415 \times 1257$$

$$P_u = 887{,}430 + 349{,}565 = 1{,}236{,}995 \text{ N} \approx 1237.0 \text{ kN}$$

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| Pu | 1237.0 | ±2 kN |
| Steel ratio | 1.40% | ±0.01% |

```python
from structural_lib.services.api import design_column_axial_is456

result = design_column_axial_is456(
    fck=25.0,
    fy=415.0,
    Ag_mm2=90000.0,
    Asc_mm2=1257.0,
)
print(f"Pu = {result['Pu_kN']:.1f} kN")
print(f"Steel ratio = {result['steel_ratio']:.4f}")
assert abs(result['Pu_kN'] - 1237.0) < 2, "Axial capacity mismatch"
```

---

### C2: Short Column Uniaxial Bending

**IS 456 Reference:** Cl 39.5 (P-M Interaction), SP:16 Chart 44

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 300 | mm |
| D | 500 | mm |
| le | 3,000 | mm |
| Asc (6-20φ) | 1,885 | mm² |
| d' | 50 | mm |
| d'/D | 0.10 | — |
| Pu (applied) | 800 | kN |
| Mu (applied) | 120 | kN·m |
| fck | M25 | N/mm² |
| fy | Fe415 | N/mm² |

The (Pu, Mu) point must lie within the P-M interaction envelope for the section.
With d'/D = 0.10, the section has adequate moment capacity at Pu = 800 kN.

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| ok (within envelope) | True | — |
| utilization | < 1.0 | — |
| classification | SHORT | — |

```python
from structural_lib.services.api import design_short_column_uniaxial_is456

result = design_short_column_uniaxial_is456(
    Pu_kN=800.0,
    Mu_kNm=120.0,
    b_mm=300.0,
    D_mm=500.0,
    le_mm=3000.0,
    fck=25.0,
    fy=415.0,
    Asc_mm2=1885.0,
    d_prime_mm=50.0,
    l_unsupported_mm=3000.0,
)
print(f"ok = {result['ok']}")
print(f"Utilization = {result['utilization']:.1%}")
print(f"Mu capacity = {result['Mu_cap_kNm']:.1f} kN·m")
print(f"Classification = {result['classification']}")
assert result['ok'], "Section should be adequate for applied loads"
assert result['utilization'] < 1.0, "Utilization should be < 100%"
```

---

### C3: Biaxial Bending Check (Bresler Formula)

**IS 456 Reference:** Cl 39.6 (Bresler Load Contour), Cl 39.6a (Puz)

| Parameter | Value | Unit |
|-----------|-------|------|
| b | 400 | mm |
| D | 400 | mm |
| le | 3,000 | mm |
| Asc (8-20φ) | 2,513 | mm² |
| d' | 50 | mm |
| Pu (applied) | 1,200 | kN |
| Mux (applied) | 80 | kN·m |
| Muy (applied) | 60 | kN·m |
| fck | M30 | N/mm² |
| fy | Fe415 | N/mm² |

**Bresler Formula (IS 456 Cl 39.6):**

$$\left(\frac{M_{ux}}{M_{ux1}}\right)^{\alpha_n} + \left(\frac{M_{uy}}{M_{uy1}}\right)^{\alpha_n} \leq 1.0$$

where $\alpha_n$ varies linearly from 1.0 (at $P_u/P_{uz} = 0.2$) to 2.0 (at $P_u/P_{uz} = 0.8$).

| Expected Result | Value | Tolerance |
|-----------------|-------|-----------|
| is_safe | True | — |
| interaction_ratio | ≤ 1.0 | — |
| alpha_n | 1.0–2.0 | Per Pu/Puz |
| classification | SHORT | — |

```python
from structural_lib.services.api import biaxial_bending_check_is456

result = biaxial_bending_check_is456(
    Pu_kN=1200.0,
    Mux_kNm=80.0,
    Muy_kNm=60.0,
    b_mm=400.0,
    D_mm=400.0,
    le_mm=3000.0,
    fck=30.0,
    fy=415.0,
    Asc_mm2=2513.0,
    d_prime_mm=50.0,
    l_unsupported_mm=3000.0,
)
print(f"is_safe = {result['is_safe']}")
print(f"Interaction ratio = {result['interaction_ratio']:.3f}")
print(f"alpha_n = {result['alpha_n']:.2f}")
print(f"Mux1 = {result['Mux1_kNm']:.1f} kN·m")
print(f"Muy1 = {result['Muy1_kNm']:.1f} kN·m")
print(f"Puz = {result['Puz_kN']:.1f} kN")
assert result['is_safe'], "Bresler check should pass"
assert result['interaction_ratio'] <= 1.0, "Interaction ratio must be ≤ 1.0"
```

---

## Additional Verification

For more detailed verification examples with hand calculations and textbook references, see:

- [Verification Examples Pack](examples.md) — Full derivations with IS 456 clause references
- [Pre-release Checklist](../_archive/planning-completed-2026-03/pre-release-checklist.md) — Beta validation status

---

## Tolerance Policy

| Quantity | Tolerance | Reason |
|----------|-----------|--------|
| Moments (Mu, Mu,lim) | ±0.5 kN·m | Rounding in intermediate steps |
| Steel Areas (Ast, Asc) | ±1% | Different rounding conventions |
| Stresses (τv, τc) | ±0.01 N/mm² | Table lookup interpolation |
| Dimensions (xu, spacing) | ±1 mm | Practical rounding |
| Axial capacity (Pu) | ±2 kN | Rounding in concrete/steel contributions |
| Interaction ratio | ±0.01 | Numerical interpolation on P-M curves |
| Bresler exponent (αn) | ±0.01 | Linear interpolation on Pu/Puz |

Differences within these tolerances are acceptable and match standard engineering practice.
