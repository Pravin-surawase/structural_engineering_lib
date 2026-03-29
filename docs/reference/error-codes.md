# Error Code Reference

**Type:** Reference
**Audience:** Developers, API Consumers
**Status:** Auto-generated
**Last Updated:** 2026-03-29

> Auto-generated from `Python/structural_lib/core/errors.py`.
> Run `scripts/generate_error_docs.py` to regenerate.

---

**Total error codes:** 29

## Categories

- [DUCTILE](#ductile) (3 codes)
- [FLEXURE](#flexure) (4 codes)
- [INPUT](#input) (17 codes)
- [SHEAR](#shear) (4 codes)
- [TORSION](#torsion) (1 codes)

---

## DUCTILE

| Code | Severity | Message | Field | Hint | IS 456 Clause |
|------|----------|---------|-------|------|---------------|
| `E_DUCTILE_001` | error | Width < 200 mm | b | Increase beam width to ≥ 200 mm. | IS 13920 Cl. 6.1.1 |
| `E_DUCTILE_002` | error | Width/Depth ratio < 0.3 | b/D | Increase width or reduce depth. | IS 13920 Cl. 6.1.2 |
| `E_DUCTILE_003` | error | Invalid depth | D | Depth must be > 0. | — |

## FLEXURE

| Code | Severity | Message | Field | Hint | IS 456 Clause |
|------|----------|---------|-------|------|---------------|
| `E_FLEXURE_001` | error | Mu exceeds Mu_lim | Mu | Use doubly reinforced or increase depth. | Cl. 38.1 |
| `E_FLEXURE_002` | info | Ast < Ast_min. Minimum steel provided. | Ast | Increase steel to meet minimum. | Cl. 26.5.1.1 |
| `E_FLEXURE_003` | error | Ast > Ast_max (4% bD) | Ast | Reduce steel or increase section. | Cl. 26.5.1.2 |
| `E_FLEXURE_004` | error | d' too large for doubly reinforced design | d_dash | Reduce compression steel cover. | — |

## INPUT

| Code | Severity | Message | Field | Hint | IS 456 Clause |
|------|----------|---------|-------|------|---------------|
| `E_INPUT_001` | error | b must be > 0 | b | Check beam width input. | — |
| `E_INPUT_002` | error | d must be > 0 | d | Check effective depth input. | — |
| `E_INPUT_003` | error | d_total must be > d | d_total | Ensure D > d + cover. | — |
| `E_INPUT_003a` | error | d_total must be > 0 | d_total | Check overall depth input. | — |
| `E_INPUT_004` | error | fck must be > 0 | fck | Use valid concrete grade (15-80 N/mm²). | — |
| `E_INPUT_005` | error | fy must be > 0 | fy | Use valid steel grade (250/415/500/550). | — |
| `E_INPUT_006` | error | Mu must be >= 0 | Mu | Check moment input sign. | — |
| `E_INPUT_007` | error | Vu must be >= 0 | Vu | Check shear input sign. | — |
| `E_INPUT_008` | error | asv must be > 0 | asv | Provide stirrup area. | — |
| `E_INPUT_009` | error | pt must be >= 0 | pt | Check tension steel percentage. | — |
| `E_INPUT_010` | error | d_dash must be > 0 | d_dash | Check compression steel cover input. | — |
| `E_INPUT_011` | error | min_long_bar_dia must be > 0 | min_long_bar_dia | Provide smallest longitudinal bar diameter. | — |
| `E_INPUT_012` | error | bw must be > 0 | bw | Check web width input. | — |
| `E_INPUT_013` | error | bf must be > 0 | bf | Check flange width input. | — |
| `E_INPUT_014` | error | Df must be > 0 | Df | Check flange thickness input. | — |
| `E_INPUT_015` | error | bf must be >= bw | bf | Ensure flange width is not smaller than web width. | — |
| `E_INPUT_016` | error | Df must be < d | Df | Ensure flange thickness is less than effective depth. | — |

## SHEAR

| Code | Severity | Message | Field | Hint | IS 456 Clause |
|------|----------|---------|-------|------|---------------|
| `E_SHEAR_001` | error | tv exceeds tc_max | tv | Increase section size. | Cl. 40.2.3 |
| `E_SHEAR_002` | warning | Spacing exceeds maximum | spacing | Reduce stirrup spacing. | Cl. 26.5.1.6 |
| `E_SHEAR_003` | info | Nominal shear < Tc. Provide minimum shear reinforcement. | tv | Minimum stirrups per Cl. 26.5.1.6. | Cl. 26.5.1.6 |
| `E_SHEAR_004` | warning | fck outside Table 19 range (15-40). Using nearest bound values. | fck | Use fck within 15-40 for Table 19 or confirm conservative design. | Table 19 |

## TORSION

| Code | Severity | Message | Field | Hint | IS 456 Clause |
|------|----------|---------|-------|------|---------------|
| `E_TORSION_001` | error | Equivalent shear stress exceeds τc,max. Section must be redesigned. | tv_equiv | Increase section size (b or D). | Cl. 41.3 |
