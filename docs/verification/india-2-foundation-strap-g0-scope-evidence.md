---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-FOUNDATION-STRAP-G0
---

# INDIA-2-FOUNDATION-STRAP-G0 Scope and Evidence Decision

## Decision

**GO** for one bounded property-line strap-footing workflow: two separate
rectangular constant-depth footings on soil, one exterior square column
eccentric to its footing centroid and one interior square column centred on its
footing, connected by one straight prismatic reinforced-concrete strap beam.
The accepted rigid idealization requires equal uniform net soil pressure under
the two footings and no soil reaction under the clear strap. The workflow
checks system statics, gross service bearing, the clear-strap shear and moment
envelope, and the strap member's flexure, shear reinforcement, minimum/side-
face reinforcement, spacing, cover, and anchorage.

This is not a complete automatic foundation design. Both footing slabs,
column-to-footing transfer regions, bearing capacity, and settlement remain
caller-verified prerequisites. The route must say so in every result and later
capability claim. It does not reuse the combined- or isolated-footing support
claim and it does not generate loads, footing sizes, soil capacity, or
reinforcement.

## Governing source set

| Source ID | Identity | Use |
|---|---|---|
| `IS456-2000-A5` | Controlled consolidated IS 456:2000 through Amendment 5, SHA-256 `964e270593392a0dea28b8c7c9ff1e0e730bbea912f8a903e8a86c7bb34d9264`; identity retained in [`is456-library-first-evidence.md`](is456-library-first-evidence.md) | Clauses 23.2, 26.2.1, 26.2.1.1, 26.3, 26.4, 26.5.1.1, 26.5.1.3, 26.5.1.5, 26.5.1.6, 34.1, 34.1.2, 38.1, 40.1, 40.2, 40.4, Tables 19/20, and Annex G-1.1 |
| `IS456-AMD6-2024` | Controlled Amendment No. 6, SHA-256 `4fc24999d133d6197088d6998da4ac4020f08bfd24c7bbcf9c24e8aa1a388881` | Complete three-page review found no Clause 34 or strap-model change; the revised coated-bar bond case remains excluded |
| `NPTEL-AFE-C3-STRAP` | [IISc Bangalore NPTEL Advanced Foundation Engineering, Chapter 3](https://archive.nptel.ac.in/content/storage2/courses/105108069/mod03/lec03.pdf), Section 3.6.1 and Fig. 3.2 | Independent public model: infinitely stiff strap, equal uniform pressure under both footings, no strap-soil reaction, reactions by statics, and strap shear/moment design |
| `IS456-PUBLIC-DISTRIBUTION-001` | [`is456-public-distribution-permission.json`](is456-public-distribution-permission.json) | Public approved-scope normalized formulas, limits, and references |
| `INDIA-2-STRAP-HAND-01` | Frozen pre-implementation calculation below | Independent numerical benchmark for equilibrium, pressure, clear-strap actions, and strap strength/detailing |

Clause identifiers, normalized formulas and limits, units, assumptions, source
IDs, and benchmark results are public implementation content. Controlled source
PDFs, page images, watermarks, and copied clause prose are not repository
artifacts.

## Confirmed source interpretation

- The independent model treats the strap as infinitely stiff and as a pure
  flexural member. It transfers actions between the two footings but takes no
  soil reaction. The clear strap therefore has an explicit downward line load
  and zero upward pressure.
- The exterior footing reaction acts at its plan centroid. The interior column
  and interior footing reaction share one longitudinal centreline. Reactions
  are solved from vertical and moment equilibrium, not assigned from the
  isolated- or combined-footing kernels.
- For zero strap line load, the model reduces exactly to the independent-source
  equations `R1 = Q1(1 + e/LR)` and `R2 = Q2 - Q1 e/LR`, where `e` is the
  exterior column-to-reaction eccentricity and `LR` is the distance between
  footing reactions.
- The accepted extension includes a caller-supplied uniform clear-strap action
  `W = w Ls` at the clear-span centroid. Reactions satisfy
  `R1 + R2 = Q1 + Q2 + W` and full-system moment equilibrium. This action is
  stated separately so strap self-weight is never hidden inside a column load.
- Equal net pressure is an eligibility check, not an outcome forced by
  averaging: `q1 = R1/A1` and `q2 = R2/A2` must agree within the frozen relative
  tolerance. Gross service pressure adds each explicitly approved uniform
  footing self-weight/overburden carrier and must not exceed the caller's
  allowable gross pressure.
- Service and factored column, strap-line, and footing-carrier actions must use
  one common positive load factor. This preserves the accepted reaction and
  equal-pressure geometry at the strength combination; patterned or
  independently factored actions fail closed.
- From the exterior footing's left free edge, the longitudinal cut uses the
  actual exterior-footing upward line load and exterior column action. Across
  the clear strap, `V(x) = V0 - w x` and
  `M(x) = M0 + V0 x - w x^2/2`. Both full-system free edges must close to zero
  shear and moment within tolerance.
- The strap is a rectangular beam for IS 456 strength checks. Negative moment
  denotes top tension. Flexure uses Clause 38.1/Annex G stress-block equilibrium
  without relying on the repository's separately logged stale `38.2` identity.
  Beam shear uses Clauses 40.1/40.2/40.4 and Tables 19/20; minimum, side-face,
  spacing, cover, and development checks remain distinct.
- The library does not infer footing-slab adequacy from uniform pressure.
  Separate qualified references must confirm both footing slabs, punching/
  one-way shear, bearing/load transfer, footing reinforcement/anchorage, soil
  capacity, settlement, rigidity, and the strap-to-footing connection.

## Frozen supported case

The first route requires all of the following:

- exactly two separate rectangular constant-depth reinforced-concrete footings
  on soil, with parallel edges and positive clear separation;
- one exterior square column wholly inside the exterior footing and eccentric
  toward the property-line edge, plus one interior square column centred on
  the interior footing; both columns and the strap share one longitudinal
  centreline and both footing reactions act at their plan centroids;
- one straight rectangular constant-section strap spanning only the clear gap,
  centred across both footing widths, explicitly isolated from soil bearing;
- positive concentric vertical service/factored column compression only, one
  explicit service/factored clear-strap uniform line load, a common factor for
  all action pairs, and no column moment, lateral action, uplift, reversal, or
  patterned/reduced-live-load mismatch;
- caller-approved equal uniform net pressure at service and factored levels,
  approved uniform footing carriers, allowable gross bearing, settlement and
  rigidity bases, and explicit full-system equilibrium closure;
- M20-M40 concrete, uncoated deformed Fe415 or Fe500 reinforcement, a
  rectangular strap with clear-span-to-overall-depth ratio greater than 2.5,
  complete top/bottom/side-face bars, vertical stirrups, cover, spacing, and
  straight anchorage into both footings; and
- external qualified verification references for both footing slabs,
  column-to-footing and strap-to-footing transfer, supporting areas, footing
  reinforcement and anchorage, bearing capacity, settlement, and construction
  clearances.

Loads, load combinations, tributary areas, footing sizes, strap self-weight,
soil capacity, settlement, durability/exposure selection, footing strength,
connection design, and construction approval are not generated by the library.

## Independent benchmark contract

`INDIA-2-STRAP-HAND-01` uses global longitudinal coordinate `x = 0` at the
property-line edge of the exterior footing:

- exterior footing `2400 x 2500 mm`, centroid/reaction at `x = 1200 mm`, and a
  `500 mm` square exterior column at `x = 400 mm`;
- interior footing `2500 x 3200 mm`, centred with its `500 mm` square column at
  `x = 6400 mm`, hence edges at `x = 5150/7650 mm`;
- clear strap length `2750 mm` from `x = 2400` to `5150 mm`, width `500 mm`,
  overall/effective depth `950/850 mm`, M30 concrete, and Fe500 steel;
- service column loads `Q1 = 1025.5625 kN` and `Q2 = 1741.4375 kN`, service
  clear-strap load `w = 12 kN/m`, and a common factored multiplier `1.5`;
- `20/30 kN/m2` service/factored footing carriers and `250 kN/m2` allowable
  gross bearing pressure; and
- six 25 mm top bars, four 16 mm bottom bars, four 12 mm side-face bars on each
  face at no more than 250 mm, two-leg 10 mm stirrups at 250 mm, 50 mm nominal
  cover, and 1200 mm top-bar anchorage beyond each clear-strap face.

### Equilibrium and bearing

The exterior/interior areas are `6.0/8.0 m2`. Equal `200 kN/m2` service net
pressure gives `R1 = 1200 kN` and `R2 = 1600 kN`. The clear-strap action is
`W = 12 x 2.75 = 33 kN` at `x = 3.775 m`, so:

- vertical closure is `1200 + 1600 - 1025.5625 - 1741.4375 - 33 = 0 kN`;
- upward moment about `x = 0` is
  `1200 x 1.2 + 1600 x 6.4 = 11680 kN m`;
- downward moment is
  `1025.5625 x 0.4 + 1741.4375 x 6.4 + 33 x 3.775 = 11680 kN m`;
- both gross service pressures are `200 + 20 = 220 kN/m2`, utilization
  `220/250 = 0.88`; and
- the common `1.5` factor gives factored reactions `1800/2400 kN`, net
  pressure `300 kN/m2`, clear-strap load `18 kN/m`, gross pressure
  `330 kN/m2`, and the same zero equilibrium residuals.

With `w = 0`, `e = 0.8 m`, and `LR = 5.2 m`, the implemented statics must also
reproduce the independent-source reaction equations exactly.

### Clear-strap actions

At the exterior footing's inner face `x = 2.4 m`, the service cut gives:

- `V0 = 200 x 6.0 - 1025.5625 = 174.4375 kN`; and
- `M0 = (200 x 2.5)(2.4^2)/2 - 1025.5625(2.4 - 0.4)`
  `= -611.125 kN m`.

Across the `2.75 m` clear strap, the interior-face values are
`V = 174.4375 - 12 x 2.75 = 141.4375 kN` and
`M = -611.125 + 174.4375 x 2.75 - 12 x 2.75^2/2`
`= -176.796875 kN m`. Factored values are exactly `1.5` times these values:
the governing strap demand is `916.6875 kN m` top tension with
`261.65625 kN` shear at the exterior face. The full right free edge closes to
zero shear and moment.

### Strap strength and detailing

For the `500 x 950 mm` strap with `d = 850 mm`, M30/Fe500:

- limiting singly reinforced moment is `1447.955892 kN m`;
- exact stress-block required top tension steel is `2788.774500 mm2`; six 25 mm bars provide
  `2945.243113 mm2`, have `46 mm` clear spacing in one layer, and give
  `961.337320 kN m` resistance;
- Clause 26.5.1.1 minimum beam steel is `722.5 mm2`; four 16 mm bottom bars
  provide `804.247719 mm2`;
- required total side-face steel is `0.1% x 500 x 950 = 475 mm2`; four 12 mm
  bars on each face provide `904.778684 mm2` total at no more than `250 mm`;
- top-steel percentage is `0.692998379%`; Table 19 gives
  `tau_c = 0.569479417 N/mm2`, while
  `tau_v = 261.65625 x 1000/(500 x 850) = 0.615661765 N/mm2`, below the M30
  Table 20 maximum;
- required stirrup-carried shear is `19.627498 kN`; two-leg 10 mm stirrups at
  `250 mm` provide `157.079633 mm2` per spacing, exceed the minimum
  `114.942529 mm2`, and provide `232.320777 kN`; and
- M30 uncoated-deformed-bar tension development for a 25 mm bar is
  `1132.8125 mm`; `1200 mm` straight anchorage is supplied into each footing.

The benchmark aggregate disposition is `PASS`, qualified review is required,
and complete engineering approval is false. Numeric implementation tests use
absolute tolerance `1e-6` in displayed units; enum, source, clause, scope,
approval-reference, and held-case identities use equality.

## Required dispositions and fail-closed boundaries

- `PASS`: topology/approval prerequisites, both equilibrium closures, equal
  net pressure, service bearing, clear-strap envelope, flexure, minimum and
  side-face steel, shear/stirrups, spacing, cover, and both anchorages pass.
- `FAIL`: a valid in-domain service bearing, provided strap steel, stirrup,
  spacing, cover, or anchorage check is inadequate.
- Unsupported input produces no design disposition: pressure inequality,
  equilibrium drift, missing external footing/connection verification,
  inconsistent service/factored multipliers, strap soil contact, overlapping
  footings, alternate column alignment, moment/lateral/uplift/patterned action,
  deep-beam ratio, invalid material, coated/bundled/spliced/curtailed bars,
  non-finite input, or missing approval/reference must fail closed.

## Explicit exclusions

Automatic footing sizing or iteration, footing-slab flexure/one-way shear/
punching/bearing/dowel/anchorage design, strap-to-footing joint design,
pedestals, library evaluation of edge/incomplete punching perimeters, unequal
or nonuniform soil pressure, strap soil bearing, more than two footings,
crossed/skewed/offset straps, alternate column alignments,
column moments, lateral/seismic action, uplift, load reversal, independently
factored or patterned live loads, flexible-soil interaction, settlement or
bearing-capacity calculation, sliding, overturning, liquefaction, scour,
sloped/stepped/pile footings, haunched/deep straps, torsion, prestress,
openings, coated/bundled/spliced/curtailed bars, automatic reinforcement,
direct deflection/crack-width/fire checks, construction-stage analysis,
professional approval, React, and release remain held.

## Activated packets and validation cadence

- `INDIA-2-FOUNDATION-STRAP-A`: typed geometry/action/approval contracts,
  common-factor and equal-pressure eligibility, reactions, bearing,
  clear-strap envelope, and equilibrium closure.
- `INDIA-2-FOUNDATION-STRAP-B`: exact strap flexure, minimum/provided and side-
  face steel, shear/stirrups, cover/spacing, anchorage, and composed result.
- `INDIA-2-FOUNDATION-STRAP-C`: typed
  `design_property_line_strap_footing_is456` Python workflow, executable
  benchmark, provenance, review boundary, and public documentation.
- `INDIA-2-FOUNDATION-STRAP-D`: thin
  `POST /api/v1/design/strap-footing/property-line` transport,
  capability/semantic truth, deterministic manifest promotion, and
  publication evidence; React remains excluded.
- `INDIA-2-FOUNDATION-STRAP-ACCEPTANCE`: cumulative focused benchmark,
  independent non-frozen replay, valid failures, every fail-closed boundary,
  architecture/import/API/truth, quick, exact-head audit, and hosted checks.

Using the accepted cadence, focused gates run for every packet. The expensive
broad Python suite and full 30-check repository gate remain deferred to the
final INDIA-2 integration boundary unless a confirmed repository-wide failure
forces either gate earlier.

## G0 focused verification

- Every frozen equilibrium, pressure, action, flexure, shear, detailing, and
  anchorage value reproduces independently to absolute tolerance `1e-9`.
- All seven deterministic manifest tests and a direct semantic assertion pass.
  Generated truth remains `12 supported / 9 held`; strap footing has no
  workflow and remains `NOT_IMPLEMENTED` until publication.
- Architecture reports `0` violations across 193 files. Import validation
  reports `0` broken imports across 635 Python files and 2,018 internal imports.
  All 1,258 internal links and touched folder indexes pass.
- Touched frontmatter, plan/task semantic assertions, source binding, token
  efficiency, and the 10/10 quick repository gate pass.
- An independent exact-head audit and every applicable hosted PR check must
  pass before G0 enters `main` unchanged and STRAP-A begins.
