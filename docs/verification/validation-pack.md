# Validation Pack — Benchmark Beams

**Version:** 0.9.6  
**Purpose:** Engineers can verify library accuracy using these benchmark beams

This pack provides 5 benchmark beams with IS 456 references that you can use to validate the library's calculations against hand calculations, SP 16 design aids, or other trusted software.

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

## Additional Verification

For more detailed verification examples with hand calculations and textbook references, see:

- [Verification Examples Pack](examples.md) — Full derivations with IS 456 clause references
- [Pre-release Checklist](../planning/pre-release-checklist.md) — Beta validation status

---

## Tolerance Policy

| Quantity | Tolerance | Reason |
|----------|-----------|--------|
| Moments (Mu, Mu,lim) | ±0.5 kN·m | Rounding in intermediate steps |
| Steel Areas (Ast, Asc) | ±1% | Different rounding conventions |
| Stresses (τv, τc) | ±0.01 N/mm² | Table lookup interpolation |
| Dimensions (xu, spacing) | ±1 mm | Practical rounding |

Differences within these tolerances are acceptable and match standard engineering practice.
