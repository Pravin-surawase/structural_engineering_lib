---
owner: Main Agent
status: active
last_updated: 2026-08-22
doc_type: verification
complexity: advanced
tags: [safety, validation, beam, column, footing, provenance]
---

# LIB-PRO-003-B Domain and Provenance Evidence

## Identity and scope

- Source base: hosted `main` at
  `e7698a63b86d2db6db2f3970871122af1ce562f6`, the exact-tree merge of
  `LIB-PRO-003-A` PR #832.
- Branch: `codex/public-route-domain-provenance`.
- Scope: beam material/shear-table inputs, column longitudinal-steel limits,
  the unified uniaxial result key, and isolated-footing provenance origins.
- No engineering formulas, code tables, supported footing geometry, package
  version, ETABS, or desktop Excel operation changed.

## Confirmed root causes and corrected outcomes

| Reproduction | Root cause | Corrected outcome |
|---|---|---|
| M10 and Fe700 returned top-level beam `OK` | Service plausibility limits allowed extrapolation and core flexure checked only positive strengths | Service routes reject material strengths outside 15-80 N/mm² concrete and 250-550 N/mm² steel; structured flexure routes return `E_INPUT_018`/`E_INPUT_019` |
| Supplied shear steel `0` or negative was replaced by flexural steel | `ast_mm2_for_shear` was used only when greater than zero; all other supplied values entered the fallback branch | A supplied value must be positive or the route raises a stable input rejection |
| `pt=100%` was clamped to the last Table 19 row and could pass | The lookup helper silently clamped every percentage above 3.0 | Direct shear returns structured `E_SHEAR_006`; beam services reject explicit values outside 0.15-3.0% |
| Concrete outside Table 19 used a nearest bound | `E_SHEAR_004` was warning-only and arithmetic continued | `E_SHEAR_004` is decisive; service routes reject outside 15-40 N/mm² before evidence construction |
| Columns with 0.07% or 14.81% steel returned safe | The 0.8-4.0% limits were warnings only | Shared column validation rejects out-of-domain steel before axial, uniaxial, biaxial, or long-column safety calculation |
| A valid low-axial uniaxial branch raised `KeyError: 'ok'` | Unified orchestration read a removed dictionary key from the typed `ColumnUniaxialResult` | Both axes read the current `is_safe` field and the valid branch returns normally |
| `service_load_origin="invented"` returned footing `PASS` | `Literal` annotations were not enforced at runtime | All three provenance-origin fields must be `provided`, `assumed`, or `verified` before calculation or replay hashing |

## Direct adversarial replay

The original public examples now produce:

- M10, Fe700, `pt_percent=100`, and supplied shear steel `0`: explicit input
  rejection;
- direct `design_shear(..., pt=100)`: `is_safe=False` with `E_SHEAR_006`;
- column steel ratios below 0.8% or above 4.0%: `DimensionError` before a
  safety result;
- the former stale-key branch: normal `uniaxial_x` return with its actual
  `is_safe` value; and
- unknown footing origin: `ValidationError` before a result or provenance
  hash exists.

## Focused and independent verification

- 656 implementation-focused tests were selected. The first consolidated run
  left 649 green and exposed seven affected assertions/paths; after root
  repairs, every failed node and its parameter cases passed while the unchanged
  649 remained green.
- 294 independent tests passed across biaxial and long columns, P-M interaction,
  column golden vectors, the beam verification pack, composed footing
  publication, and public API stability.
- Focused Black and Ruff checks pass, targeted mypy reports no issues in the
  13 changed source modules, and `git diff --check` passes. The consolidated
  quick gate passes 10/10; commit-hook, session, and hosted acceptance remain
  in the candidate sequence.

## Remaining release blockers

This packet closes only `LIB-PRO-003-B`. Packet C remains required for slab,
legacy CSV, and BOQ failure contracts; Packet D remains required for decisive
Excel CI/audit gates and repository truth. A new package and all
stable/professional-use claims remain `HOLD`.
