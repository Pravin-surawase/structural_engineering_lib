---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-WALL-G0
---

# INDIA-2-WALL-G0 Braced Wall Scope and Evidence Decision

## Decision

**GO** for one bounded IS 456:2000 Clause 32 wall family. The repository owner
activated the remaining INDIA-2 work on 2026-08-16 by asking that INDIA-2 be
implemented and finished. Each later family still has to pass its own G0 source,
scope, and benchmark decision before calculation code is written.

The first wall workflow is the empirical limit-state check of one regular,
laterally supported, braced concrete wall subjected only to caller-supplied
factored in-plane vertical compression. It intentionally does not accept an
applied moment or horizontal action.

## Governing public source set

| Source ID | Identity | Use |
|---|---|---|
| `IS456-2000-A6` | IS 456:2000 through Amendment 6; controlled BIS copies and SHA-256 identities are retained in [`is456-library-first-evidence.md`](is456-library-first-evidence.md) | Clauses 32.1, 32.2.1-32.2.5, and 32.5-32.5.2 |
| `IS456-PUBLIC-DISTRIBUTION-001` | [`is456-public-distribution-permission.json`](is456-public-distribution-permission.json) | Public use and distribution of approved-scope normalized formulas, limits, and references |
| `INDIA-2-WALL-HAND-01` | Frozen pre-implementation hand calculation below | Independent benchmark for effective height, eccentricity, capacity, reinforcement, and disposition |

The public implementation will expose clause identifiers, normalized formulas
and limits, units, assumptions, and source IDs. Raw source PDFs, page images,
and copied clause prose are not repository artifacts.

The Amendment 6 review does not alter the selected Clause 32 provisions.

## Frozen supported case

The accepted main process is one rectangular wall strip satisfying all of the
following:

- the caller confirms the Clause 32.2.1 bracing, diaphragm/load-transfer, and
  connection conditions;
- lateral restraint is supplied by floors and/or intersecting walls, with the
  rotation-restraint case stated explicitly;
- unsupported height, horizontal lateral-restraint spacing, wall length, wall
  thickness, and load eccentricity are explicit in mm;
- thickness is from 100 mm through 200 mm, so the accepted detailing model uses
  one reinforcement grid; walls thicker than 200 mm require a later two-grid
  extension;
- concrete is normal-weight reinforced concrete from M20 through M60;
- reinforcement is deformed bar not larger than 16 mm with characteristic
  strength at least 415 N/mm2;
- the library applies the Clause 32.2.2 minimum transverse eccentricity even
  when the caller supplies a smaller value;
- the only action is a positive factored axial compression in kN; and
- the result checks empirical axial capacity, wall slenderness, minimum vertical
  and horizontal reinforcement, bar spacing, and the provided-bar disposition.

The result is a code check of supplied geometry, action, and bars. It does not
generate building loads, choose wall thickness, select reinforcement, or prove
the global bracing system.

## Independent benchmark contract

`INDIA-2-WALL-HAND-01` was frozen before implementation. It uses a wall
3,000 mm high between floors, 4,000 mm between intersecting lateral restraints,
4,000 mm long, and 150 mm thick. Both ends are rotationally restrained. The
concrete is M20, the factored axial load is 2,000 kN, the supplied eccentricity
is zero, and the supplied reinforcement is 8 mm vertical bars at 250 mm and
10 mm horizontal bars at 250 mm in one grid.

The independent arithmetic is:

- effective height = `min(0.75 x 3000, 0.75 x 4000) = 2250 mm`;
- design eccentricity = `max(0, 0.05 x 150) = 7.5 mm`;
- additional eccentricity = `2250^2 / (2500 x 150) = 13.5 mm`;
- effective compression thickness = `150 - 1.2 x 7.5 - 2 x 13.5 = 114 mm`;
- axial capacity = `0.3 x 114 x 20 = 684 N/mm = 684 kN/m`;
- axial demand = `2000 / 4 = 500 kN/m`, utilization `0.7309941520`;
- minimum vertical steel = `0.0012 x 150 x 1000 = 180 mm2/m`;
- minimum horizontal steel = `0.0020 x 150 x 1000 = 300 mm2/m`;
- provided vertical steel = `201.061930 mm2/m`;
- provided horizontal steel = `314.159265 mm2/m`; and
- maximum spacing = `min(3 x 150, 450) = 450 mm`.

The accepted benchmark disposition is `PASS`. Numeric implementation tests use
an absolute tolerance of `1e-6` in the displayed units; exact enum, clause, and
source identities use equality.

## Required dispositions

- `PASS`: geometry, slenderness, axial capacity, reinforcement area, and spacing
  all satisfy the frozen boundary.
- `FAIL`: a valid in-domain axial demand or provided-bar check is unsafe.
- unsupported topology, actions, materials, bracing assertions, wall thickness,
  slenderness, or a non-positive effective compression zone raises a typed
  contract error and produces no design disposition.

## Explicit exclusions

Unbraced walls, walls thicker than 200 mm, multiple reinforcement grids,
retaining and liquid-retaining walls, openings, flanged or irregular sections,
concentrated bearing checks, applied moments, in-plane or out-of-plane
horizontal actions, shear, flexural interaction, global stability, lateral-load
analysis, seismic/shear-wall behavior, IS 13920 detailing, fire, FEM, automatic
sizing, and automatic bar selection are held.

## Activated packets and gates

- `INDIA-2-WALL-A`: typed geometry/action contracts, effective height,
  eccentricity, slenderness, and axial-capacity kernel.
- `INDIA-2-WALL-B`: minimum/provided reinforcement and spacing checks plus the
  composed pure-math disposition.
- `INDIA-2-WALL-C`: typed public Python workflow and executable benchmark.
- `INDIA-2-WALL-D`: thin FastAPI route, capability truth, generated manifest,
  and evidence reconciliation; React remains excluded.
- `INDIA-2-WALL-ACCEPTANCE`: focused benchmark, unsafe/out-of-domain,
  architecture/import, quick-gate, and hosted-check evidence for the integrated
  wall family.

The expensive broad Python suite and 30-check repository gate are deferred to
`INDIA-2-CLOSEOUT` after all accepted INDIA-2 families are integrated, unless a
confirmed repository-wide issue appears earlier.
