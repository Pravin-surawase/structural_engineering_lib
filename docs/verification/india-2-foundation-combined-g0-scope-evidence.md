---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-COMBINED-G0
---

# INDIA-2-FOUNDATION-COMBINED-G0 Scope and Evidence Decision

## Decision

**GO** for one bounded IS 456:2000 combined-footing workflow: two identical
square reinforced-concrete columns carrying equal concentric axial compression,
located symmetrically on the longitudinal centreline of one rigid rectangular,
constant-depth footing on soil. The supported analysis uses an externally
approved planar uniform-pressure model, whole-width longitudinal equilibrium,
and transverse spread-footing cantilever action.

This is not a general combined-footing solver. The route requires an approved
allowable gross bearing pressure, settlement/uniformity review, rigidity basis,
load combination, and distributed self-weight/overburden carrier from the
caller. It does not calculate soil capacity or settlement and it does not reuse
the supported concentric isolated-footing capability claim.

## Governing source set

| Source ID | Identity | Use |
|---|---|---|
| `IS456-2000-A5` | Controlled consolidated IS 456:2000 through Amendment 5, SHA-256 `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`; identity retained in [`is456-library-first-evidence.md`](is456-library-first-evidence.md) | Clauses 26.2.1.1, 26.2.3, 26.3, 31.6.1, 31.6.3, 34.1, 34.1.2, 34.2.3.1, 34.2.4.1, 34.2.4.3, 34.3, 34.4, 34.4.1-34.4.4, and 34.5.1 |
| `IS456-AMD6-2024` | Controlled Amendment No. 6, SHA-256 `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881` | Complete three-page review found no Clause 34 change; the coated-bar bond revision remains outside this uncoated-bar case |
| `NPTEL-AFE-C3` | [IISc Bangalore NPTEL Advanced Foundation Engineering, Chapter 3](https://archive.nptel.ac.in/content/storage2/courses/105108069/mod03/lec03.pdf), Sections 3.7, 3.8, and 3.14 | Independent public rigid-method source: planar pressure, load-resultant/area alignment, full-width shear/moment diagrams, continuous-beam longitudinal action, and spread-footing transverse action |
| `IS456-PUBLIC-DISTRIBUTION-001` | [`is456-public-distribution-permission.json`](is456-public-distribution-permission.json) | Public approved-scope formulas, normalized limits, and references |
| `INDIA-2-COMBINED-HAND-01` | Frozen pre-implementation hand calculation below | Independent numerical benchmark for equilibrium, bearing, actions, flexure, shear, punching, load transfer, and detailing |

Clause identifiers, normalized formulas and limits, units, assumptions, source
IDs, and benchmark results are public implementation content. Controlled source
PDFs, page images, watermarks, and copied clause prose are not repository
artifacts.

## Confirmed source interpretation

- Clause 34.1 requires the applied actions and induced reactions to be carried
  without exceeding the externally established soil bearing boundary, while
  settlement uniformity remains a geotechnical/project review.
- Clause 34.2.3.1 determines a footing-section moment from all forces on one
  side of a vertical plane across the complete footing. Clause 34.2.3.2 is
  explicitly isolated-footing-specific, so this route does not mislabel it as
  the combined-footing analysis rule.
- The NPTEL rigid method supplies the missing combined-footing analysis model:
  the footing is idealized as rigid, pressure is planar, pressure resultant and
  applied-load resultant coincide, longitudinal shear/moment follow full-width
  equilibrium, the footing is designed longitudinally as a continuous beam,
  and transverse action follows spread-footing cantilever behavior.
- This route narrows planar pressure to uniform pressure by requiring equal
  symmetric columns and equal axial loads. The applied resultant must coincide
  with the rectangular footing centroid for service and factored column loads.
- Gross service bearing includes column service loads plus a separately stated
  uniform service footing-self-weight/overburden pressure. Structural actions
  use the net factored column pressure because the matching factored distributed
  downward carrier is locally supported and cancels from footing flexure. Both
  carriers and the cancellation basis require caller approval.
- Longitudinal action uses upward line load `w = q_net,u B` and, from the left
  free edge, `V(x) = wx - sum(Pui)` and
  `M(x) = wx^2/2 - sum[Pui(x-xi)]` for columns left of the section. Positive
  reported demand denotes bottom tension at an exterior column face; the
  negative inter-column demand denotes top tension.
- Wide-beam shear is checked at `d` from a column face, two-way shear on a full
  perimeter at `d/2` from a column face, and transverse moment per metre is
  `q_net,u a_t^2/2`, where `a_t` is the column-face-to-footing-edge cantilever.
- Clause 34.3/34.5.1 flexural and solid-slab minimum reinforcement, Clause 34.4
  bearing/dowel transfer, and Clause 26 anchorage remain separate checks over
  the accepted analysis actions.

## Frozen supported case

The initial route requires all of the following:

- exactly two identical square concrete columns, centred across the footing
  width, with equal longitudinal end projections and equal centre spacing;
- equal positive concentric service axial loads and equal factored axial loads,
  with no column moment, horizontal action, uplift, eccentricity, or load
  reversal;
- one rectangular, uniform-thickness footing on soil with both complete column
  punching perimeters inside the footing and not overlapping;
- caller confirmation that the footing is adequately rigid for the conventional
  planar-pressure model and that allowable gross bearing pressure, settlement,
  differential settlement, and founding level are approved externally;
- one explicit uniform service self-weight/overburden pressure, its consistent
  factored carrier, and confirmation that this distributed action cancels
  locally from the net structural pressure;
- M20-M40 concrete and uncoated deformed Fe415 or Fe500 reinforcement, with
  explicit overall/effective depths, cover, bars, supporting-area basis, and
  column-to-footing transfer inputs; and
- complete bottom longitudinal/transverse steel, inter-column top steel,
  anchorage, bearing/dowels, one-way shear, and concrete-only punching checks.

Loads, load combinations, rigidity, bearing capacity, settlement, founding
depth, durability/exposure selection, and construction approval are not
generated by the library.

## Independent benchmark contract

`INDIA-2-COMBINED-HAND-01` uses a `6000 x 2500 x 850 mm` rectangular footing,
`750 mm` common effective depth, two `500 x 500 mm` columns at `x = 1000` and
`5000 mm`, M30 concrete, and uncoated Fe500 reinforcement. Each column supplies
`900 kN` service and `1350 kN` factored compression. A caller-approved uniform
`25 kN/m2` service distributed carrier covers footing self-weight and
overburden; allowable gross bearing pressure is `150 kN/m2`.

### Equilibrium, pressure, and longitudinal actions

- plan area `= 6.0 x 2.5 = 15.0 m2`;
- gross service pressure
  `= (2 x 900 + 25 x 15) / 15 = 145 kN/m2`, utilization
  `145 / 150 = 0.966666667`;
- service and factored column resultants act at `x = 3000 mm`, exactly the
  footing centroid, so the accepted pressure is uniform and has no tension;
- net factored structural pressure `= 2 x 1350 / 15 = 180 kN/m2` and upward
  longitudinal line load `= 180 x 2.5 = 450 kN/m`;
- exterior/inner faces of the left column are at `x = 0.75 / 1.25 m`;
  their whole-width moments are `126.5625 / 14.0625 kN m` bottom-tension
  demand under the benchmark sign convention; and
- shear is zero between columns at `x = 3.0 m`, where the governing
  inter-column top-tension moment is `675.0 kN m`.

The inner wide-beam section at `d` from the column face is `x = 2.0 m`.
Its shear magnitude is `450.0 kN`, nominal stress is `0.24 N/mm2`, and the M30
Table 19 value at the minimum registered percentage is `0.29 N/mm2`, giving
utilization `0.827586207`. The outer critical plane coincides with the free
edge and has zero demand.

### Transverse action, flexure, and provided steel

The transverse column-face cantilever is `(2.5 - 0.5) / 2 = 1.0 m`, producing
`90.0 kN m/m`. IS stress-block solutions at `d = 750 mm` give:

| Region | Flexural steel | Clause 34.5.1 minimum | Frozen provided |
|---|---:|---:|---:|
| Inter-column top, full 2500 mm width | `2109.099058 mm2` | `2550 mm2` | 16 mm at 190 mm, `2645.551708 mm2` over the width |
| Exterior column-face bottom, full width | `389.298381 mm2` | `2550 mm2` | 16 mm at 190 mm, `2645.551708 mm2` over the width |
| Transverse, per metre | `277.600243 mm2/m` | `1020 mm2/m` | 12 mm at 110 mm, `1028.157596 mm2/m` |

Minimum steel governs all three benchmark regions. Spacing, cover, anchorage,
bar termination, and congestion remain explicit checks; the table does not
authorize automatic bar selection.

### Punching and column-to-footing transfer

For either column, the square `d/2` punching section has side `1250 mm`, area
`1.5625 m2`, and perimeter `5000 mm`. Net punching shear is
`1350 - 180 x 1.5625 = 1068.75 kN`; nominal stress is `0.285 N/mm2` against
`0.25 sqrt(30) = 1.369306394 N/mm2`, utilization `0.208134572`.

Column bearing stress is `5.4 N/mm2` against the conservative `13.5 N/mm2`
capacity obtained without any supporting-area enhancement (`A1/A2 = 1.0`).
Four 20 mm dowels provide `1256.637061 mm2` against the
`1250 mm2` minimum. With the frozen uncoated deformed-bar bond basis, required
compression development length is `725 mm`; `800 mm` is supplied into the
footing.

The represented aggregate disposition is `PASS`, qualified review is required,
and complete engineering approval is false. Numeric implementation tests use
absolute tolerance `1e-6` in displayed units; enum, source, clause, scope, and
held-case identities use equality.

## Required dispositions and fail-closed boundaries

- `PASS`: service bearing, both equilibrium/resultant checks, longitudinal and
  transverse flexure/detailing, both inner wide-beam shear sections, both full
  punching perimeters, and both column-transfer checks pass.
- `FAIL`: a valid in-domain provided-steel/detailing, bearing, wide-beam shear,
  concrete-only punching, or column-transfer check is inadequate.
- Unsupported geometry or action produces no design disposition: unequal
  loads, unequal/end-asymmetric column locations, non-square/different columns,
  more or fewer than two columns, moment/horizontal action/uplift, nonuniform or
  tensile pressure, missing distributed-load cancellation, invalid material,
  overlapping/edge punching perimeter, non-finite input, or missing external
  approvals must fail closed.

## Explicit exclusions

Unequal column loads, edge/property-line eccentricity, trapezoidal or irregular
plans, more than two columns, different column sizes, rectangular/round
columns, pedestals, column moments, horizontal/lateral/seismic action, uplift,
partial contact, nonlinear soil response, variable pressure, elastic-line,
Winkler, plate, FEM, settlement or bearing-capacity calculation, sliding,
overturning, liquefaction, scour, sloped/stepped/pile footings, openings,
nonuniform thickness, shear reinforcement, coated/bundled/spliced bars,
automatic sizing, durability design, direct deflection, crack width, fire,
construction-stage analysis, professional approval, React, and release remain
held.

## Activated packets and validation cadence

- `INDIA-2-FOUNDATION-COMBINED-A`: typed geometry/action contracts, rigid-model
  eligibility, gross/net pressure, resultant, shear, moment, and transverse
  action generation.
- `INDIA-2-FOUNDATION-COMBINED-B`: flexure/minimum/provided steel, wide-beam
  shear, concrete-only punching, bearing/dowels/anchorage, and composed result.
- `INDIA-2-FOUNDATION-COMBINED-C`: one typed public Python workflow, executable
  benchmark, provenance, review boundary, and public documentation.
- `INDIA-2-FOUNDATION-COMBINED-D`: thin FastAPI transport, capability/semantic
  truth, deterministic manifest promotion, and publication evidence; React
  remains excluded.
- `INDIA-2-FOUNDATION-COMBINED-ACCEPTANCE`: cumulative focused benchmark,
  unsafe/out-of-domain, architecture/import, API/truth, quick, and hosted gates.

The expensive broad Python suite and 30-check repository gate remain deferred
to `INDIA-2-CLOSEOUT` after all intended INDIA-2 families are integrated,
unless a confirmed outcome-changing repository-wide issue appears earlier.

## G0 focused verification

- All frozen equilibrium, pressure, action, flexure, detailing, shear,
  punching, bearing, dowel, and anchorage values reproduce independently to
  absolute tolerance `1e-9`.
- Deterministic manifest tests pass; generated truth remains 11 supported and
  10 held families, with combined footing held until implementation and
  publication.
- Architecture reports 0/186 violations, imports 0/623 broken, all 1,218
  internal links valid, touched indexes current, token efficiency PASS, and
  the quick repository gate 10/10.
- Required hosted PR checks must pass on the unchanged reviewed head before G0
  enters `main` and COMBINED-A begins.
