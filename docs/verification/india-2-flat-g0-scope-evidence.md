---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FLAT-G0
---

# INDIA-2-FLAT-G0 Scope and Evidence Decision

## Decision

**GO** for one bounded IS 456:2000 flat-slab workflow: a regular square
interior panel in an equal-span orthogonal grid, designed by the direct design
method for uniform gravity loading, with one centred square interior-column
punching check. The initial route has no drop, column head, opening, lateral or
unbalanced moment transfer, or punching-shear reinforcement.

This is a deliberately narrower capability than the full Clause 31 family. It
does not reuse the existing beam/wall-supported solid-slab claim and it does not
claim equivalent-frame, exterior-panel, irregular-grid, or general punching
design.

## Governing public source set

| Source ID | Identity | Use |
|---|---|---|
| `IS456-2000-A5` | Controlled consolidated IS 456:2000 through Amendment 5, SHA-256 `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`; identity retained in [`is456-library-first-evidence.md`](is456-library-first-evidence.md) | Clauses 23.2, 26.3, and 31.1-31.7, including normalized Figure 16 length rules |
| `IS456-AMD6-2024` | Controlled Amendment No. 6, SHA-256 `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881` | Confirmed by complete visual inspection to contain no Clause 31 flat-slab change; coated-bar bond changes remain outside this case |
| `IS456-PUBLIC-DISTRIBUTION-001` | [`is456-public-distribution-permission.json`](is456-public-distribution-permission.json) | Public approved-scope formulas, normalized limits, and references |
| `NPTEL-RCD-FLAT-W8` | [NPTEL Reinforced Concrete Design course](https://www.nptel.ac.in/courses/105103824) and [official syllabus](https://archive.nptel.ac.in/content/syllabus_pdf/105103824.pdf) | Independent instructional-scope cross-check only; the accessible official artifacts expose no reproducible numerical example |
| `INDIA-2-FLAT-HAND-01` | Frozen pre-implementation hand calculation below | Independent numerical benchmark for eligibility, moments, strips, flexure, serviceability, detailing, and punching |

Clause identifiers, normalized formulas and limits, units, assumptions, source
IDs, and benchmark results are public implementation content. Controlled source
PDFs, page images, watermarks, and copied clause prose are not repository
artifacts.

## Confirmed source interpretation

- The direct design method is available only after its grid, panel-shape,
  column-offset, successive-span, end-span, and live/dead applicability
  conditions pass. The bounded route narrows these conditions to at least three
  equal continuous spans in each direction, zero column offsets, identical
  square panels, and equal end spans.
- For a direction under consideration, the clear span is face-to-face but not
  less than `0.65` times the centre-to-centre span. The total static moment is
  `Mo = wu * l2 * ln^2 / 8`, with `wu` in kN/m2 and lengths in m.
- An interior-span `Mo` is divided into `0.65 Mo` negative and `0.35 Mo`
  positive moment. The column strip receives 75 percent of the negative moment
  and 60 percent of the positive moment; the middle strip receives the
  remainder.
- For this square grid, each column strip and middle strip is 3000 mm wide.
  The implementation will still derive the widths from the normalized Clause
  31.1 definitions rather than hard-code the benchmark dimensions.
- The interior-column punching perimeter is geometrically similar to the square
  column and lies `d/2` from its faces. With no moment transfer, nominal shear
  is `V / (b0 d)`. The no-shear-reinforcement limit is
  `ks * 0.25 * sqrt(fck)`, where `ks = min(1, 0.5 + beta_c)`.
- The no-drop serviceability comparison uses the continuous-member base ratio
  `26` multiplied by the Clause 31.2.1 factor `0.9`. Direct deflection and crack
  width remain held.
- The bounded detailing rule uses straight bars only. All bottom bars continue
  through the panel and all support-top bars extend at least `0.30 ln` from
  each support face. This conservative normalization covers the applicable
  no-drop interior-panel Figure 16 minimums without publishing the figure.

## Frozen supported case

The accepted route requires all of the following:

- one solid square interior panel in a column-supported grid with at least
  three equal continuous spans in both orthogonal directions;
- equal 6000 mm centre-to-centre spans in the benchmark, zero column offsets,
  square 500 mm columns, and no marginal beam, wall, drop, or column head;
- 300 mm overall slab depth and one caller-confirmed conservative common
  effective depth of 260 mm for both directions and punching;
- M30 concrete and uncoated deformed Fe500 reinforcement;
- caller-supplied uniform service dead and live loads, a matching governing
  factored load, a non-blank load-basis reference, and explicit confirmation
  that self-weight and the approved load combination are already included;
- identical full gravity loading on the represented panels, service live load
  no greater than one-half the service dead load, and no unbalanced gravity,
  wind, seismic, or other lateral moment transfer;
- supplied straight-bar diameter and spacing for the negative and positive
  regions of both column and middle strips, bottom-bar continuity, and support-
  top extensions of at least `0.30 ln`; and
- one centred interior-column punching check with the full critical perimeter,
  no nearby opening or free edge, and no punching-shear reinforcement.

The software will calculate both orthogonal directions even though the frozen
square benchmark produces equal values. Loads and combinations are not
generated or approved by the library.

## Independent benchmark contract

`INDIA-2-FLAT-HAND-01` uses three equal 6000 mm spans in each direction, a
500 mm square interior column, 300 mm slab thickness, 260 mm common effective
depth, M30 concrete, Fe500 reinforcement, 9 kN/m2 service dead load, 4 kN/m2
service live load, and 19.5 kN/m2 factored uniform load. The dead load is an
external approved carrier that already includes slab self-weight and finishes.

Eligibility and moment arithmetic, identical in each direction, is:

- live/dead ratio `= 4 / 9 = 0.444444444`, within the narrower `0.5` route
  boundary and the direct-design code limit;
- clear span `ln = 6000 - 500 = 5500 mm`, greater than
  `0.65 x 6000 = 3900 mm`;
- design load on the strip `W = 19.5 x 6.0 x 5.5 = 643.5 kN`;
- total static moment `Mo = 19.5 x 6.0 x 5.5^2 / 8 = 442.40625 kN m`;
- total negative/positive moments `= 287.5640625 / 154.8421875 kN m`;
- column-strip negative/positive moments
  `= 215.673046875 / 92.9053125 kN m`; and
- middle-strip negative/positive moments
  `= 71.891015625 / 61.936875 kN m`.

Using the IS 456 rectangular stress block over each 3000 mm strip gives:

| Region | Flexural steel, total strip | Flexural steel, per m | Governing per m | Frozen supplied bars | Supplied per m |
|---|---:|---:|---:|---|---:|
| Column strip, negative | 1993.075996 mm2 | 664.358665 mm2/m | 664.358665 mm2/m | 12 mm at 160 mm | 706.858347 mm2/m |
| Column strip, positive | 836.624293 mm2 | 278.874764 mm2/m | 360.000000 mm2/m | 10 mm at 200 mm | 392.699082 mm2/m |
| Middle strip, negative | 644.654258 mm2 | 214.884753 mm2/m | 360.000000 mm2/m | 10 mm at 200 mm | 392.699082 mm2/m |
| Middle strip, positive | 554.292752 mm2 | 184.764251 mm2/m | 360.000000 mm2/m | 10 mm at 200 mm | 392.699082 mm2/m |

The `360 mm2/m` minimum is `0.12 percent` of the 300 mm gross slab section.
The supplied diameters and spacings pass the applicable general slab and flat-
slab limits. Support-top bars extend `0.30 x 5500 = 1650 mm` from each support
face and all bottom bars are continuous through the panel.

The no-drop span/depth comparison is `6000 / 260 = 23.076923077` against
`26 x 0.9 = 23.4`, utilization `0.986193294`, so the reviewed ratio comparison
passes while direct deflection and crack-width verification remain held.

The centred interior-column punching arithmetic is:

- factored tributary reaction `= 19.5 x 6 x 6 = 702.0 kN`;
- critical-section side `= 500 + 260 = 760 mm`, perimeter
  `b0 = 3040 mm`, and enclosed area `= 577600 mm2`;
- factored load inside the critical section `= 11.2632 kN`, hence
  `V = 690.7368 kN`;
- nominal punching stress `= 0.873907895 N/mm2`;
- `beta_c = 1`, `ks = 1`, and no-reinforcement capacity
  `= 0.25 sqrt(30) = 1.369306394 N/mm2`; and
- punching utilization `= 0.638212090`, which passes without shear
  reinforcement.

The represented aggregate disposition is `PASS`, with qualified review
required and complete engineering approval false. Numeric implementation tests
use absolute tolerance `1e-6` in displayed units; enum, source, clause, scope,
and held-case identities use equality.

## Required dispositions and fail-closed boundaries

- `PASS`: direct-design eligibility, both directional moment distributions,
  every flexural/detailing region, the reviewed span/depth comparison, and the
  no-reinforcement punching check pass.
- `FAIL`: a valid in-domain provided-steel, diameter, spacing, bar-continuity,
  support-extension, span/depth, or punching check is inadequate.
- A punching demand above the no-reinforcement limit fails this route; the
  result distinguishes the code redesign boundary above `1.5` times the basic
  concrete stress, but the route never designs punching reinforcement.
- Unsupported topology, unequal span, offset column, drop/head, exterior or
  edge/corner column, opening, nonuniform/patterned loading, live/dead ratio
  above `0.5`, inconsistent factored action, moment transfer, invalid material,
  non-finite input, or missing external load/qualified-review confirmation
  raises a typed contract error and produces no design disposition.

## Explicit exclusions

Rectangular unequal-sided panels, unequal spans, fewer than three continuous
spans, exterior panels, edge/corner columns, drops, column heads/capitals,
marginal beams/walls, openings, transfer slabs, point or line loads, patterned
live loading, unbalanced gravity or lateral moment transfer, column design,
punching reinforcement, coated bars, bent bars, splices, automated anchorage or
congestion design, automatic depth/bar selection, direct deflection, crack
width, fire, progressive collapse, post-tensioning, prestress, equivalent-frame
analysis, nonlinear analysis, seismic diaphragm/action design, and FEM remain
held.

## Activated packets and validation cadence

- `INDIA-2-FLAT-A`: typed grid/panel/material/load contracts, direct-design
  eligibility, clear spans, and strip definitions.
- `INDIA-2-FLAT-B`: total static moment and bounded interior negative/positive
  and column/middle-strip distribution in both directions.
- `INDIA-2-FLAT-C`: flexure, minimum/provided reinforcement, straight-bar
  detailing, and reviewed no-drop span/depth comparison.
- `INDIA-2-FLAT-D`: centred square interior-column punching demand, concrete
  capacity, redesign boundary, and fail-closed exclusions.
- `INDIA-2-FLAT-E`: one typed public Python workflow, thin API transport,
  capability truth, deterministic manifest promotion, and publication evidence;
  React remains excluded.
- `INDIA-2-FLAT-ACCEPTANCE`: cumulative focused benchmark, unsafe and out-of-
  domain behavior, architecture/import, API/truth, quick, and hosted checks.

The expensive broad Python suite and 30-check repository gate remain deferred
to `INDIA-2-CLOSEOUT` after all intended INDIA-2 families are integrated,
unless a confirmed outcome-changing repository-wide issue appears earlier.

## G0 focused verification

- All 26 frozen eligibility, action, moment, flexure, detailing,
  serviceability, and punching values reproduce to absolute tolerance `1e-9`.
- All 6 deterministic Indian-code manifest tests pass; generated truth remains
  current at 10 supported and 11 held families, with flat slab held until
  implementation and publication.
- Black, Ruff, mypy, and Bandit pass on the changed executable path.
- Architecture reports 0 violations across 177 files and import validation
  reports 0 broken imports across 607 files.
- All 1,192 internal links and all three touched folder-index hashes are valid;
  token efficiency and the 10-check quick gate pass.
- All normal hosted PR checks remain required on the unchanged reviewed head
  before G0 enters `main` and FLAT-A begins.
