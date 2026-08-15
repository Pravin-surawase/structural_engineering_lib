---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-WALL-A
---

# INDIA-2-WALL-A Geometry and Axial-Capacity Evidence

## Implemented boundary

WALL-A implements the pure IS 456 layer for the accepted Clause 32.2 braced
wall case. It resolves effective height, enforces the maximum effective-height
to thickness ratio, applies minimum transverse eccentricity, calculates the
additional slenderness eccentricity, and checks caller-supplied factored axial
compression against the empirical capacity.

The wall capability remains `HELD` and `NOT_IMPLEMENTED` in the runtime
capability registry until WALL-B-D complete the reinforcement, public workflow,
FastAPI, and evidence contract.

## Public code references and normalized rules

| Function | IS 456:2000 references | Normalized result |
|---|---|---|
| `resolve_braced_wall_geometry` | 32.2.1, 32.2.3, 32.2.4 | Effective height components and `Hwe/t` with the limit of 30 |
| `check_braced_wall_axial_capacity` | 32.2.2, 32.2.5 | Design eccentricity, slenderness eccentricity, empirical axial capacity, demand, utilization, and `PASS`/`FAIL` |

All dimensions are mm, concrete strength is N/mm2, total factored load is kN,
capacity and demand per unit length are exposed as N/mm and their numerically
equivalent kN/m values, and full-wall capacity is kN. Runtime results retain
`IS456-2000-A6` plus caller bracing/action references.

The Clause 32 metadata was corrected from coarse shifted labels to the exact
32.2.1-32.2.5 and 32.5-32.5.2 identifiers. The generated Indian-code manifest
therefore records five exact registered wall subclauses while keeping the wall
family itself held.

## Frozen benchmark result

The `INDIA-2-WALL-HAND-01` input frozen in WALL-G0 returns:

| Quantity | Expected | Software result | Acceptance |
|---|---:|---:|---:|
| Effective height | 2250 mm | 2250 mm | `1e-6` mm |
| Effective-height/thickness ratio | 15.0 | 15.0 | `1e-6` |
| Design eccentricity | 7.5 mm | 7.5 mm | `1e-6` mm |
| Additional eccentricity | 13.5 mm | 13.5 mm | `1e-6` mm |
| Effective compression thickness | 114 mm | 114 mm | `1e-6` mm |
| Axial capacity | 684 N/mm | 684 N/mm | `1e-6` N/mm |
| Full-wall capacity | 2736 kN | 2736 kN | `1e-6` kN |
| Axial demand | 500 N/mm | 500 N/mm | `1e-6` N/mm |
| Utilization | 0.7309941520 | 0.7309941520 | `1e-10` |
| Strength disposition | `PASS` | `PASS` | exact |

## Fail-closed and unsafe evidence

Focused tests prove the exact slenderness boundary of 30 is accepted and a
larger ratio is rejected; each Clause 32.2.1 bracing confirmation is mandatory;
wall thickness outside 100-200 mm is rejected; non-finite geometry, unsupported
concrete grades, invalid action/reference inputs, and a non-positive empirical
compression zone are rejected. A valid axial overload returns `FAIL` rather
than raising or being promoted to `PASS`.

Applied moment, horizontal action, wall shear, combined flexure, openings,
two-grid walls, seismic behavior, global analysis, load generation,
reinforcement design/checking, public service, FastAPI, and React remain outside
WALL-A.

## Verification

- 19 focused wall tests passed.
- The combined wall, clause-database, and traceability selection passed 94 tests.
- Black, Ruff, and mypy passed on the new wall package and tests.
- Architecture-boundary validation found 0 violations across 166 files.
- Structural-library import validation found 0 broken imports across 203 files.
- The generated Indian-code manifest is current and truthfully retains the wall
  family as held.

These results establish bounded software behavior and public code provenance;
they do not constitute professional design approval or release authorization.
