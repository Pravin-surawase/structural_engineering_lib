---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-DEEP-B
---

# INDIA-2-DEEP-B Reinforcement Evidence

## Implemented boundary

DEEP-B implements the remaining pure-math checks for the G0-approved simply
supported solid rectangular top-loaded deep beam. It accepts one caller-
provided same-diameter positive tie group, bar placement and continuity,
straight embedment beyond both support faces, and vertical/horizontal side-
face bar grids. It selects no bars, generates no loads or reactions, and makes
no bearing or compression-nodal capacity calculation.

The input explicitly rejects bundles, splices, side-face bars over 16 mm,
invalid face-grid counts, and the retained transverse-enclosure case. A false
continuity confirmation or valid but inadequate provided reinforcement returns
`FAIL`; an unsupported contract returns no disposition.

## Public clause formulas and limits

The implementation retains these public normalized rules and identities:

- Clause 29.2 positive tie area `Ast = Mu / (0.87 fy z)`;
- Clause 29.3.1 placement within `0.25D - 0.05l`, continuity between supports,
  and at least `0.8Ld` beyond each support face;
- Clauses 26.2.1-26.2.1.1 development length
  `Ld = phi(0.87fy)/(4 tau_bd)` and deformed tension bond stresses;
- Clause 29.3.4 with Amendment No. 3's corrected reference to Clauses
  32.5-32.5.2; and
- deformed-bar minimum side-face ratios `0.0012` vertical and `0.0020`
  horizontal, maximum spacing `min(3b, 450 mm)`, one grid through 200 mm and
  two grids above 200 mm, plus the held vertical-ratio-above-one-percent
  transverse-enclosure boundary.

Runtime results expose all clause/source IDs, the four caller evidence
references, every required/provided intermediate, per-check disposition,
qualified-review requirement, and `complete_engineering_approval = false`.
The bounded shear-deemed-satisfied statement is true only for the composed
`PASS` result and does not represent bearing, nodal, or complete design approval.

## Benchmark and unsafe evidence

`INDIA-2-DEEP-HAND-01` reproduces required/provided positive tie steel
`1477.832512 / 1520.530844 mm2`, permitted tie zone `350 mm`, M30 deformed bond
stress `2.4 N/mm2`, development length `996.875 mm`, required embedment
`797.5 mm`, vertical side-face steel `360 / 523.598776 mm2/m`, and horizontal
side-face steel `600 / 628.318531 mm2/m`. Its placement, continuity, both
anchorages, both side-face directions, two-grid rule, and external prerequisite
compose to `PASS`.

Focused tests separately prove inadequate tie area, outside-zone placement,
discontinuity, either short anchorage, inadequate side-face area, excess
spacing, both width/grid branches, the exact supported bond-stress lookup,
invalid/non-finite reinforcement, bundles, splices, large side bars, and the
transverse-enclosure hold. The direct deep-beam package passes 42 tests; the
combined deep-beam, clause-database, traceability, and deterministic-manifest
selection passes 131 tests.
Black, Ruff, mypy, and Bandit pass; architecture reports 0 violations across
174 files and imports report 0 broken imports across 602 scanned files.

Deep beam remains `HELD`/`NOT_IMPLEMENTED` in generated capability truth until
the typed workflow and transport/publication packets are integrated. The
manifest is current at 9 supported and 12 held families, all 1,172 internal
links are valid, touched indexes are current, and quick gate passes 10/10.
Required hosted checks must pass on the unchanged reviewed head. The broad
Python suite and 30-check repository gate remain deferred to the one whole-
INDIA-2 closeout unless an outcome-changing repository-wide issue appears.
The next packet is `INDIA-2-DEEP-C`.
