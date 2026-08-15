---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-2A
---

# INDIA-2A Straight-Flight Staircase Scope and Evidence Decision

## Decision

**GO** for one bounded IS 456:2000 straight-flight staircase family. The owner
activated INDIA-2A through INDIA-2D on 2026-08-15 by requesting that INDIA-2 be
started and finished. This decision selects only the case below; it does not
activate another held structural family, a release, or engineering-use approval.

## Governing source set

| Source ID | Identity | Use |
|---|---|---|
| `IS456-2000-A6` | Controlled IS 456:2000 corpus through Amendment 6; hashes retained in `is456-library-first-evidence.md` | Clauses 23.2.1, 26.3.3, 26.5.2.1, 33.1-33.3, 38.1, and 40.1-40.2 |
| `NPTEL-M9L20-EX9.1` | IIT Kharagpur, NPTEL Module 9 Lesson 20, Example 9.1 | Independent geometry, load, action, flexure, shear, and provided-bar benchmark |
| `IS456-PUBLIC-DISTRIBUTION-001` | `is456-public-distribution-permission.json` | Owner authority for approved-scope normalized formulas and limits |

The BIS Amendment 6 review changes material provisions but does not alter the
selected Clause 33 staircase rules. Protected clause prose and page images will
not be copied into the repository.

## Frozen supported case

The accepted main process is one cast-in-situ, solid, longitudinally spanning
waist-slab flight with one collinear landing segment at each end. The flight and
landings act as one simply supported member between caller-identified outer
beam or wall support centres.

- geometry is a horizontal effective-span model with explicit lower-landing,
  going, upper-landing, flight-width, riser, tread, waist, landing, cover, and
  provided-bar dimensions in mm;
- section depth is the waist thickness perpendicular to the soffit;
- the library calculates waist and step self-weight from explicit concrete unit
  weight, but consumes caller-supplied landing load shares, finishes, imposed
  actions, and the ultimate load factor;
- all area actions are stated on horizontal plan projection in kN/m2;
- the action kernel analyses three contiguous uniform-load segments and reports
  support reactions, maximum shear, zero-shear location, maximum sagging moment,
  and per-metre design actions;
- the design kernel checks a singly reinforced rectangular waist strip,
  caller-provided main/distribution bars, ordinary one-way shear, and the basic
  simply supported span/depth boundary; and
- results retain source/clause provenance and never assert professional approval.

The supported load carrier is explicit engineering input. It is not IS 875 load
generation and does not decide occupancy, finishes, combinations, patterns, or
project load envelopes.

## Independent benchmark contract

`NPTEL-M9L20-EX9.1` fixes a 1.5 m wide longitudinal member with 750 mm,
2700 mm, and 1650 mm loaded segments, 160 mm risers, 270 mm treads, a 250 mm
waist, a 200 mm landing, M20 concrete, and Fe415 steel. Its accepted targets are:

| Quantity | Expected | Acceptance |
|---|---:|---:|
| Inclined step length | 313.85 mm | 0.02 mm |
| Waist self-weight on plan | 7.265 kN/m2 | 0.002 kN/m2 |
| Step self-weight on plan | 2.000 kN/m2 | 0.001 kN/m2 |
| Factored flight load | 22.900 kN/m2 | 0.02 kN/m2 |
| Total factored load | 142.86 kN | 0.03 kN |
| Lower and upper reactions | 69.76 kN, 73.10 kN | 0.03 kN |
| Zero-shear location | 2.51 m | 0.01 m |
| Maximum sagging moment | 102.08 kNm | 0.05 kNm |
| Waist nominal shear stress | 0.217 N/mm2 | 0.002 N/mm2 |
| Required main steel | 920.64 mm2/m | 2.0 mm2/m |
| Provided main steel | 12 mm at 120 mm centres | exact input |
| Provided distribution steel | 8 mm at 160 mm centres | exact input |

The tolerances retain the example's published rounding; calculation tests also
check unrounded hand-derived values at tighter tolerances.

## Required dispositions

- `PASS`: flexure, provided bars, shear, and basic span/depth checks all pass.
- `REVIEW_REQUIRED`: strength/detailing checks pass but the basic span/depth
  limit is exceeded; the library does not invent a modification factor.
- `FAIL`: a strength, shear, or provided-bar requirement is not satisfied.
- invalid or unsupported geometry/action inputs raise a typed contract error.

## Explicit exclusions

Transverse-spanning, cantilever, open-well load redistribution, dog-legged
system analysis, helical, folded tread-riser, isolated tread, precast, ribbed,
stringer-supported, non-collinear, continuous, and seismic staircase cases are
held. Landing torsion, openings, concentrated loads, moment redistribution,
automatic bar selection, development-length layouts, crack width, direct
deflection, fire, vibration, 3D geometry, BOQ/BBS, React UI, and IS 875/IS 1893
generation are also outside INDIA-2.

## Packet sequence and gates

- INDIA-2B: typed geometry, self-weight, and three-segment action kernel.
- INDIA-2C: flexure, supplied-bar detailing, shear, and serviceability disposition.
- INDIA-2D: typed Python service/facade and thin FastAPI route, then capability
  truth and evidence reconciliation.
- INDIA-2-CUMULATIVE: broad Python, full repository, manifest, provenance, and
  essential-review gates once B-D are integrated.

Each packet receives focused tests, benchmark proof, architecture/import checks,
the quick gate, and required hosted checks. Qualified engineering review and
release authorization remain separate holds.
