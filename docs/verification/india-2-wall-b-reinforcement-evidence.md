---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-WALL-B
---

# INDIA-2-WALL-B Reinforcement Evidence

## Implemented boundary

WALL-B adds one pure IS 456 provided-reinforcement check to the accepted
Clause 32.2 braced-wall case. It does not select bars. The caller supplies one
vertical and one horizontal bar diameter/spacing pair plus its reinforcement
basis reference, and the result reports required area, provided area, ratio,
spacing limit, directional dispositions, transverse-enclosure boundary, and an
overall `PASS` or `FAIL`.

The wall capability remains `HELD` and `NOT_IMPLEMENTED` until WALL-C publishes
the typed Python workflow and WALL-D completes the FastAPI and capability-truth
contract.

## Public clause references and normalized rules

`check_wall_minimum_reinforcement` is registered to IS 456:2000 Clauses 32.5,
32.5.1, and 32.5.2. The runtime result preserves `IS456-2000-A6` and the caller's
reinforcement-basis reference.

For deformed bars of characteristic strength 415 N/mm2 or greater, and for
welded wire fabric, both with diameter not greater than 16 mm, the minimum
vertical and horizontal gross-area ratios are 0.0012 and 0.0020. For other bar
types they are 0.0015 and 0.0025. Vertical and horizontal spacing are each
limited to the smaller of three wall thicknesses and 450 mm.

The accepted geometry is restricted to 100-200 mm thick one-grid walls. A wall
thicker than 200 mm requires the separately held two-grid route. When caller-
provided vertical reinforcement exceeds 0.01 of gross wall area, this bounded
route returns `FAIL` because the automatic Clause 32.5.2 transverse-enclosure
exception no longer applies.

## Frozen benchmark result

For the 150 mm thick `INDIA-2-WALL-HAND-01` wall:

| Direction | Provided | Required | Provided result | Spacing limit | Status |
|---|---:|---:|---:|---:|---|
| Vertical | 8 mm at 250 mm | 180 mm2/m | 201.061930 mm2/m | 450 mm | `PASS` |
| Horizontal | 10 mm at 250 mm | 300 mm2/m | 314.159265 mm2/m | 450 mm | `PASS` |

No transverse enclosure is required by this bounded result and the overall
reinforcement disposition is `PASS`.

## Fail-closed and unsafe evidence

Focused tests cover all three material categories, the 100 mm and 200 mm wall
spacing limits, insufficient steel, excessive spacing, non-finite and
non-positive bar inputs, the 16 mm category limit, blank provenance, wrong
types, and the vertical-ratio-above-0.01 enclosure boundary. Valid inadequate
detailing returns `FAIL`; malformed or unsupported input raises
`WallContractError`.

Two-grid walls, transverse-enclosure design, bar selection, lap/anchorage,
openings, combined flexure, shear, seismic detailing, services, FastAPI, React,
professional approval, and release remain outside WALL-B.

## Verification

- 33 focused wall tests passed, including the 19 integrated WALL-A tests.
- The combined wall, clause-database, and traceability selection passed 108
  tests.
- Black, Ruff, and mypy passed on the wall package and focused tests.
- Architecture validation found 0 violations across 167 files and import
  validation found 0 broken imports across 204 files.
- The Indian-code manifest was regenerated with Clause 32.5-32.5.2 registered
  while the wall family remains held.
- The packet-level quick gate passed 10/10 and all 1,151 internal links are
  valid.

These results establish bounded software behavior and public-code provenance;
they do not constitute professional design approval or release authorization.
