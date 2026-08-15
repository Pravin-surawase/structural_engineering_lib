---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: INDIA-2B
---

# INDIA-2B Staircase Geometry and Action Evidence

INDIA-2B implements only the typed geometry, concrete self-weight, and
three-segment simply supported action contract selected by INDIA-2A. It adds no
public service or FastAPI route and does not change the capability manifest from
`HELD`.

## Implemented calculation boundary

`resolve_straight_flight_geometry()` accepts one cast-in-situ solid,
longitudinally spanning, stringer-free waist slab with collinear landing
segments. It resolves the Clause 33 horizontal effective span, inclined step
length, slope factor, slope angle, and inclined going length.

`analyze_straight_flight_actions()` calculates waist, step, and landing
self-weight from explicit geometry and concrete unit weight. It consumes
caller-supplied superimposed loads, landing shares, ultimate factor, and load
basis. It then solves support reactions, maximum shear, the zero-shear location,
maximum sagging moment, and per-metre design actions for three contiguous UDL
segments.

The calculation does not choose occupancy actions, infer IS 875 loads, generate
load combinations, or analyse a non-collinear or indeterminate stair system.

## Independent benchmark

For `NPTEL-M9L20-EX9.1`, the unrounded software result is:

| Quantity | Software | Published target |
|---|---:|---:|
| Effective span | 5100.0 mm | 5100 mm |
| Inclined step length | 313.8471 mm | 313.85 mm |
| Waist self-weight | 7.26498 kN/m2 | 7.265 kN/m2 |
| Factored flight load | 22.89747 kN/m2 | 22.9 kN/m2 |
| Total factored load | 142.85350 kN | 142.86 kN |
| Lower reaction | 69.75472 kN | 69.76 kN |
| Upper reaction | 73.09877 kN | 73.10 kN |
| Zero-shear location | 2510.703 mm | 2510 mm |
| Maximum sagging moment | 102.07350 kNm | 102.08 kNm |
| Upper flight boundary moment | 86.92204 kNm | 86.92 kNm |
| Equilibrium residual | 0.0 kN | 0 kN |

The benchmark test retains published-rounding tolerances while also asserting
the full-width/per-metre identity and exact reaction equilibrium.

## Fail-closed evidence

Focused tests reject zero, negative, or non-finite geometry; transverse span;
beam-at-riser and stringer support models; and landing shares above one. Zero
superimposed actions remain valid because explicit concrete self-weight still
produces a physical positive action result.

Alternate support cases, structural design, serviceability acceptance, public
facades, FastAPI, React, capability promotion, qualified review, and release
remain outside this packet.

## Verification cadence

This packet receives focused tests, architecture/import checks, the quick gate,
commit hooks, and hosted PR checks. Broad Python and the full repository gate
remain deferred until INDIA-2B through INDIA-2D are integrated.
