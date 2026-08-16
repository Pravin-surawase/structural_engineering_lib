---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-COMBINED-B
---

# INDIA-2-FOUNDATION-COMBINED-B Strength Evidence

## Accepted outcome

COMBINED-B implements only the G0-frozen pure IS 456 strength composition for
two identical square columns carrying equal concentric axial compression on one
symmetric rigid rectangular constant-depth footing. It checks caller-supplied
longitudinal and transverse flexural reinforcement, footing cover and spacing,
tension anchorage, longitudinal/transverse one-way shear, concrete-only
punching, and bearing/compression-dowel transfer.

Valid but inadequate provision returns `FAIL`. Unsupported geometry, material,
load, pressure, source-basis, approval, or supporting-area input raises
`CombinedFootingContractError` without producing a design disposition. A
represented `PASS` still requires qualified engineering review and is never
complete engineering approval.

This packet does not publish a service or FastAPI workflow, promote combined
footing to supported capability truth, select bars, design shear/punching
reinforcement, or calculate soil capacity or settlement.

## Implementation identity

- Material, reinforcement, supporting-area, transfer, and composed design
  inputs: `Python/structural_lib/codes/is456/combined_footing/models.py`.
- Strength and detailing composition:
  `Python/structural_lib/codes/is456/combined_footing/strength.py`.
- Package exports:
  `Python/structural_lib/codes/is456/combined_footing/__init__.py`.
- Benchmark, unsafe, fail-closed, determinism, and traceability tests:
  `Python/tests/codes/is456/combined_footing/test_strength.py`.

The composed function consumes the COMBINED-A input and recomputes its action
result. It cannot accept a detached or caller-mutated action carrier.

## Exact source and registry binding

The controlled consolidated source SHA-256 is
`964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`.
The complete Amendment 6 source SHA-256 is
`4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881`;
its coated-bar bond change remains outside this uncoated-bar route.

COMBINED-B exact-registers the implemented logic to:

- Clauses 26.2.1/26.2.1.1, 26.3.2/26.3.3, 26.4.2.2,
  26.5.2.1/26.5.2.2;
- Clauses 31.6.1, 31.6.2.1 and 31.6.3.1;
- Clauses 34.1, 34.2.3.1, 34.2.4.1, 34.2.4.3, 34.3,
  34.4/34.4.1-34.4.3 and 34.5.1;
- Clause 38.1 and Annex G-1.1 for the exact rectangular stress-block solution;
  and
- Clauses 40.1/40.2 with normalized Table 19 lookup.

The distributable identifier registry now includes the four exact footing/slab
identifiers that the implemented checks require: 26.4.2.2, 26.5.2.2,
34.2.4.3, and 34.5.1. The existing Annex G-1.1 metadata title was corrected
from a doubly reinforced label to the represented rectangular section without
compression reinforcement. The strength function does not repeat the stale
repository `38.2` registration because the controlled standard binds this
solution to Clause 38.1 and Annex G-1.1.

No source PDF, scan, page image, watermark, or copied clause prose is a
repository artifact.

## Typed eligibility and provision contract

The strength composition requires:

- M20-M40 footing and column concrete and Fe415 or Fe500 reinforcement;
- explicit confirmation that all flexural bars and dowels are straight,
  uncoated deformed bars;
- approved effective-depth and reinforcement-schedule bases;
- explicit top/bottom longitudinal and transverse bar diameters, spacings,
  nominal cover, aggregate size, and available straight anchorage;
- an approved effective supporting area for each column using only the largest
  wholly contained 1V:2H frustum lower-base basis; and
- explicit dowel count, diameter, column-bar diameter, and available
  compression development into both footing and column.

Three provided dowels, inadequate area/spacing/cover/anchorage, excessive
one-way or punching stress, and inadequate dowel diameter/development remain
valid in-domain `FAIL` results. A non-approved basis, coated-bar case,
unsupported grade, non-finite scalar, invalid nested type, supporting area
smaller than the loaded column area, or alternate COMBINED-A topology fails
closed before a result.

## Frozen benchmark replay

`INDIA-2-COMBINED-HAND-01` reproduces:

| Check | Implemented result |
|---|---:|
| Inter-column top flexural / minimum / provided steel | `2109.099058 / 2550 / 2645.551708 mm2` |
| Exterior-face bottom flexural / minimum / provided steel | `389.298381 / 2550 / 2645.551708 mm2` |
| Transverse flexural / minimum / provided steel | `277.600243 / 1020 / 1028.157596 mm2/m` |
| 16 mm tension development / supplied anchorage | `725 / 800 mm` |
| 12 mm tension development / supplied anchorage | `543.75 / 800 mm` |
| Inner longitudinal nominal shear / Table 19 capacity | `0.24 / 0.29 N/mm2` |
| Inner longitudinal one-way utilization, each side | `0.827586207` |
| Transverse nominal shear / utilization | `0.06 N/mm2 / 0.206896552` |
| Punching demand / stress / capacity, each column | `1068.75 kN / 0.285 / 1.369306394 N/mm2` |
| Punching utilization, each column | `0.208134572` |
| Column bearing stress / conservative capacity | `5.4 / 13.5 N/mm2` |
| Minimum / provided dowel area, each column | `1250 / 1256.637061 mm2` |
| Compression development / supplied embedment | `725 / 800 mm` |

The actual longitudinal and transverse reinforcement percentages are retained
separately from the explicit `0.15 percent` lower Table 19 lookup boundary.
All represented checks pass, aggregate disposition is `PASS`, qualified review
is true, and complete engineering approval is false.

## Retained holds

The public Python service workflow, FastAPI route, semantic/capability truth,
and family acceptance remain for COMBINED-C/D/ACCEPTANCE. Unequal/eccentric
loads, property-line layouts, trapezoidal or irregular plans, flexible or
variable soil pressure, settlement and bearing-capacity calculation, alternate
columns, pedestals, openings, variable depth, shear or punching reinforcement,
coated/bundled/spliced/curtailed bars, automatic sizing, durability selection,
construction approval, React, release, and professional approval remain held.

## Focused verification

- 28 direct COMBINED-B tests, all 71 COMBINED-A/B tests, and the 192-test
  combined clause, traceability, manifest, and function-quality selection pass.
  Generated capability truth remains deterministic at 11 supported and 10
  held families, with combined footing still held.
- The strict function-quality check reports the one new composed calculation
  function passing; Ruff and focused mypy pass.
- Architecture reports 0/190 violations, imports 0/630 broken, all 1,224
  internal links are valid, touched indexes are current, source binding is
  true, token efficiency passes, and the quick gate is 10/10.
- Independent exact-head audit and hosted-check receipts are recorded at
  packet closeout.

The broad Python suite and full 30-check repository gate remain deferred to
`INDIA-2-CLOSEOUT` under the accepted cadence.
