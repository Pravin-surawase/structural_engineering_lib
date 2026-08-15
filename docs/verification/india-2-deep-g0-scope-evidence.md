---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-DEEP-G0
---

# INDIA-2-DEEP-G0 Scope and Evidence Decision

## Decision

**GO** for one bounded IS 456:2000 Clause 29 software check: a simply
supported, solid rectangular, top-loaded deep beam without openings, under one
caller-supplied governing positive factored moment. The route checks the
positive tension-tie reinforcement and the Clause 29 detailing needed for the
bounded shear-deemed-satisfied statement. It is not a generalized strut-and-tie
or complete transfer-girder design.

## Governing public source set

| Source ID | Identity | Use |
|---|---|---|
| `IS456-2000-A6` | IS 456:2000 through Amendment 6; controlled BIS identities are retained in [`is456-library-first-evidence.md`](is456-library-first-evidence.md) | Clauses 29.1-29.3.4, 26.2.1-26.2.1.1, 32.5-32.5.2, 36.4.2.1, and 38.1(e) |
| `IS456-AMD3-DEEP-SIDEFACE` | Amendment No. 3 correction to Clause 29.3.4 | The side-face minimum-reinforcement cross-reference is Clause 32.5, not the original printed 32.4 |
| `IS456-PUBLIC-DISTRIBUTION-001` | [`is456-public-distribution-permission.json`](is456-public-distribution-permission.json) | Public approved-scope formulas, limits, and references |
| `NPTEL-RCD-DEEP-W7` | [NPTEL Reinforced Concrete Design syllabus](https://archive.nptel.ac.in/content/syllabus_pdf/105103824.pdf) | Independent instructional-scope cross-check only; no numerical value is taken from the syllabus |
| `INDIA-2-DEEP-HAND-01` | Frozen pre-implementation hand calculation below | Independent benchmark for classification, lever arm, tie steel, placement, anchorage, and side-face steel |

Clause identifiers, normalized formulas and limits, units, assumptions, source
IDs, and benchmark results are public implementation content. Watermarked
source PDFs, page images, and copied clause prose are not repository artifacts.

## Confirmed source interpretation

- Effective span `l` is the lesser of centre-to-centre support distance and
  `1.15` times clear span.
- A simply supported member is a deep beam only when `l / D < 2.0`, where `D`
  is overall depth. Equality is outside this route.
- For `1 <= l / D < 2`, lever arm `z = 0.2(l + 2D)`. For `l / D < 1`,
  `z = 0.6l`. Visual source inspection confirmed the second expression; scan
  text can misread the italic span symbol as the digit one.
- Required positive tie steel follows equilibrium using the Clause 29.2 lever
  arm and limit-state design steel stress: `Ast = Mu / (0.87 fy z)`.
- Positive reinforcement continues without curtailment between supports, has
  at least `0.8 Ld` embedment beyond each support face, and lies within the
  tension-face zone `0.25D - 0.05l`.
- Development length uses `Ld = phi sigma_s / (4 tau_bd)`, with
  `sigma_s = 0.87 fy` and the normalized Clause 26.2.1.1 bond-stress lookup for
  deformed tension bars.
- Clause 29.3.4 invokes the Clause 32.5 wall minimums after the Amendment No. 3
  correction. The bounded side-face check uses the applicable vertical and
  horizontal material ratios, maximum spacing, one/two-grid rule, and retained
  transverse-enclosure boundary.

## Frozen supported case

The accepted route requires all of the following:

- one simply supported, single-span, solid rectangular reinforced-concrete
  member with explicit centre-to-centre span, clear span, overall depth, and web
  width in mm;
- no opening, dapped end, corbel, hollow section, prestress, or section change;
- top-applied gravity loading with no hanging action and no negative moment;
- one finite positive factored sagging moment in kN m supplied by the caller,
  with a non-blank action-basis reference;
- M20-M60 concrete and deformed Fe415 or Fe500 main reinforcement;
- one same-diameter positive bar group, its furthest distance from the tension
  face, continuity confirmation, and embedment beyond both support faces;
- caller-provided vertical and horizontal side-face bar diameters/spacings on
  the required face grid count; and
- explicit caller confirmation and a non-blank qualified reference that local
  bearing, support geometry, compression struts/nodal regions, load paths, and
  reactions have been verified outside this bounded route.

The software does not generate loads or reactions and does not calculate a
concrete bearing or nodal-zone capacity. The external verification is a
fail-closed prerequisite, not a library approval claim.

## Independent benchmark contract

`INDIA-2-DEEP-HAND-01` uses centre-to-centre span 3000 mm, clear span 2800 mm,
overall depth 2000 mm, web width 300 mm, M30 concrete, Fe500 reinforcement,
and a caller-supplied positive factored moment of 900 kN m. Four 22 mm main bars
are continuous between supports, the furthest bar is 250 mm from the tension
face, and embedment beyond each support face is 850 mm. Side-face steel is two
grids: 10 mm vertical bars at 300 mm and 10 mm horizontal bars at 250 mm on
each face.

The independent arithmetic is:

- effective span `l = min(3000, 1.15 x 2800) = 3000 mm`;
- `l / D = 1.5`, hence the member is within the simply supported deep-beam
  boundary;
- `z = 0.2(3000 + 2 x 2000) = 1400 mm`;
- required positive steel `= 900 x 10^6 / (0.87 x 500 x 1400)`
  `= 1477.832512 mm2`;
- provided positive steel `= 4 x pi x 22^2 / 4 = 1520.530844 mm2`;
- tension-zone depth `= 0.25 x 2000 - 0.05 x 3000 = 350 mm`, so the furthest
  bar at 250 mm is within the zone;
- M30 deformed-bar design bond stress `= 1.5 x 1.6 = 2.4 N/mm2`;
- `Ld = 22 x 435 / (4 x 2.4) = 996.875 mm`, so required embedment is
  `0.8 Ld = 797.5 mm` and 850 mm passes;
- required/provided vertical side-face steel is `360 / 523.598776 mm2/m`;
- required/provided horizontal side-face steel is `600 / 628.318531 mm2/m`;
  and
- the 450 mm maximum side-face spacing, two-grid rule, and retained one-percent
  vertical-ratio boundary all pass.

The accepted benchmark disposition is `PASS` for the represented checks, with
qualified review required and complete engineering approval false. Numeric
implementation tests use absolute tolerance `1e-6` in displayed units; enum,
clause, source, and held-case identities use equality.

## Required dispositions and fail-closed boundaries

- `PASS`: classification, lever arm, positive tie area, placement, continuity,
  both anchorages, and both side-face directions pass, with the external
  bearing/nodal prerequisite confirmed.
- `FAIL`: a valid in-domain provided-steel, placement, anchorage, or side-face
  check is inadequate.
- unsupported support type, span ratio, topology, action sign/type, material,
  hanging action, missing external verification, non-finite input, invalid face
  grid count, or transverse-enclosure case raises a typed contract error and
  produces no design disposition.

## Explicit exclusions

Continuous or cantilever deep beams, negative moment, openings, dapped ends,
corbels, coupling beams, hollow/flanged/irregular sections, prestressing,
hanging loads or suspension reinforcement, support/reaction analysis, bearing
and nodal-zone capacity, automatic section or bar selection, bar bundles,
splices, crack width, deflection, fire, cyclic/seismic design, IS 13920,
generalized strut-and-tie modelling, nonlinear analysis, and FEM remain held.

## Activated packets and validation cadence

- `INDIA-2-DEEP-A`: typed geometry, material, action, effective-span,
  classification, lever-arm, and fail-closed contracts.
- `INDIA-2-DEEP-B`: positive tie, placement, continuity, anchorage, side-face,
  and composed pure-math dispositions.
- `INDIA-2-DEEP-C`: typed public Python workflow and executable benchmark.
- `INDIA-2-DEEP-D`: thin FastAPI route, capability truth, manifest promotion,
  and publication evidence; React remains excluded.
- `INDIA-2-DEEP-ACCEPTANCE`: cumulative focused benchmark, unsafe cases,
  architecture/import, API/truth, quick, and hosted checks.

The expensive broad Python suite and 30-check repository gate remain deferred
to `INDIA-2-CLOSEOUT` after all intended INDIA-2 families are integrated,
unless a confirmed outcome-changing repository-wide issue appears earlier.

## G0 focused verification

- All 13 frozen benchmark intermediate values reproduce to absolute tolerance
  `1e-9`; the documented pass boundary is internally consistent.
- All 6 deterministic Indian-code manifest tests pass; the generated manifest
  remains truthful at 9 supported and 12 held families, with deep beam held
  until implementation and publication.
- Black, Ruff, mypy, and Bandit pass on the changed executable path.
- Architecture validation reports 0 violations across 170 files and import
  validation reports 0 broken imports across 205 files.
- All 1,164 internal links and touched folder-index hashes are valid; the token-
  efficiency check and quick repository gate pass, with the latter at 10/10.
- Required hosted PR checks must pass on the unchanged reviewed head before G0
  enters `main` and DEEP-A begins.
