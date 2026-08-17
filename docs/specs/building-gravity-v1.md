---
owner: Main Agent
status: active
last_updated: 2026-08-17
doc_type: spec
complexity: advanced
tags: [gravity, building-model, load-model, provenance, reconciliation]
---

# Building Gravity V1 Model and Load Contract

## Purpose and boundary

This specification freezes the B1 physical-model and dead/live load-ledger
foundation. It establishes a deterministic, hand-checkable load path before
any gravity component design, workflow, REST, CLI, or UI orchestration begins.

`BuildingModelV1` is an engineering model contract. Existing
`/geometry/building` data remains visualization-only and cannot be promoted to
this contract without explicit validation and complete source accounting.

## Accepted topology

V1 accepts exactly:

- one rectangular storey with eight unique nodes in a right-handed coordinate
  system where X/Y are horizontal and Z is up;
- one rectangular one-way solid slab spanning in Y;
- two simply supported beams on the opposite Y edges, each spanning in X;
- four vertical, short, braced, axial-only columns, one at each beam end;
- four concentric axial-only footing action destinations, one at each column
  base;
- one concrete material and one slab, beam, and column section; and
- unique physical, load-path, and render identities.

Every material, section, node, panel, member, and footing destination must map
to one accepted raw-source record. Duplicate, orphan, disconnected, ambiguous,
or partially accounted input is rejected before calculation.

## Identity and determinism

The accepted model hash includes normalized physical content and excludes raw
serialization order and the raw-source hash. The raw source records remain
available as provenance. Harmless reordering cannot change the accepted model
hash, while a physical change must change it.

The load-model hash binds the accepted model hash, supplied load values,
source references, inclusion/exclusion rules, combinations, and balance
tolerance. Raw-source serialization is provenance and does not change the
accepted load-model identity.

## Frozen load basis

| Action | Case | Ownership | V1 disposition |
|---|---|---|---|
| Slab self-weight | DL | Gravity ledger | Generated once from thickness and unit weight |
| Superimposed slab dead load | DL | Gravity ledger | Supplied explicitly |
| Beam self-weight | DL | Gravity ledger | Generated once per beam |
| Column self-weight | DL | Gravity ledger | Generated once per column |
| Occupancy live load | LL | Gravity ledger | Supplied explicitly and unreduced |

The aggregate category `COMBINED_DEAD` is used only after separate dead-load
sources are transferred and combined. It is not a new source and cannot appear
as an inclusion rule.

The exact combinations are:

- `SERVICE_DL_LL`: `1.0 DL + 1.0 LL`; and
- `ULS_1_5_DL_LL`: `1.5 DL + 1.5 LL`.

Every factor and inclusion rule carries a source-reference identity. V1 does
not infer a missing load, factor, or basis.

## Load path and reconciliation

The deterministic closed-form path is:

1. slab area actions are split equally to the two supporting edge beams;
2. beam self-weight is added once to its owning beam;
3. each simply supported uniformly loaded beam transfers half of its total to
   each end column;
4. each column adds its own self-weight once; and
5. the column action is handed to its concentric footing destination.

The ledger stores source, destination, magnitude, intensity where applicable,
origin entry identities, formula basis, and a fixed sign convention. It checks
slab-to-beam, beam-to-column, column accumulation, column-to-footing,
storey-to-foundation, and combination-to-foundation balances. Any residual
outside the explicit tolerance blocks the result.

## Approved exclusions and holds

The load model must explicitly list all V1 exclusions: walls, facade,
equipment, tanks, stairs, special roof loads, lateral loads, soil, footing
self-weight, overburden, and live-load reduction.

The footing entries are action handoffs, not footing designs. They intentionally
exclude footing self-weight and overburden. A future footing design must remain
on HOLD unless an externally approved soil basis and the complete required
service action basis are supplied according to the footing component contract.

B1 makes no claim for member design, reinforcement, serviceability, whole-frame
analysis, continuity, stiffness distribution, walls, wind, seismic, dynamic
loads, load reduction, multi-storey behavior, live ETABS, Excel, write-back,
optimization, release readiness, or qualified engineering approval.

## Hand example

The frozen example uses a 6 m x 4 m slab, 3 m storey, 150 mm slab, 300 mm x
500 mm beams, 300 mm x 300 mm columns, and concrete unit weight 25 kN/m3. The
supplied loads are 1.5 kN/m2 superimposed dead and 3.0 kN/m2 live.

| Check | Exact value |
|---|---:|
| Slab self-weight | 90 kN |
| Slab superimposed dead load | 36 kN |
| Two beam self-weights | 45 kN |
| Four column self-weights | 27 kN |
| Total dead load at foundations | 198 kN |
| Total live load at foundations | 72 kN |
| Dead action per footing destination | 49.5 kN |
| Live action per footing destination | 18 kN |
| Service DL+LL per footing destination | 67.5 kN |
| Factored 1.5(DL+LL) per footing destination | 101.25 kN |

The executable vector is
`Python/tests/unit/test_building_gravity_v1.py`.
