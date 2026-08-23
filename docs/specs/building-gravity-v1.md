---
owner: Main Agent
status: active
last_updated: 2026-08-23
doc_type: spec
complexity: advanced
tags: [gravity, building-model, load-model, provenance, reconciliation]
---

# Building Gravity Workflow V1 Contract

## Purpose and boundary

This specification freezes the B1 physical-model and dead/live load-ledger
foundation and the B2 component-orchestration contract built on it. The result
is a deterministic, hand-checkable gravity path with explicit prerequisites,
actions, component dispositions, review surfaces, and calculation-book
evidence.

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
caller-assigned practical actions, source references, inclusion/exclusion
rules, combinations, and balance tolerance. Raw-source serialization is
provenance and does not change the accepted load-model identity.

## Frozen load basis

| Action | Case | Ownership | V1 disposition |
|---|---|---|---|
| Slab self-weight | DL | Gravity ledger | Generated once from thickness and unit weight |
| Superimposed slab dead load | DL | Gravity ledger | Supplied explicitly |
| Beam self-weight | DL | Gravity ledger | Generated once per beam |
| Column self-weight | DL | Gravity ledger | Generated once per column |
| Occupancy live load | LL | Gravity ledger | Supplied explicitly and unreduced |
| Wall line | DL | Caller | Full-span line action assigned to one beam |
| Other beam line | DL or LL | Caller | Full-span line action assigned to one beam |
| Beam point | DL or LL | Caller | Point action and station assigned to one beam |
| Supported slab area | DL or LL | Caller | Area action assigned to the sole declared panel |

Every practical action carries a unique action ID and source identity, a source
category and reference, load case, exact units, destination, magnitude, and
assignment basis. `WALL_LINE` accepts only `WALL` in `DL`. Other practical
sources are limited to facade, equipment, tank, stair, and special-roof gravity
actions. Lateral, soil, footing self-weight, overburden, and live-load reduction
cannot enter through this contract.

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
2. an explicit supported slab-area action follows that same declared support
   path; the caller does not assign it to an inferred panel;
3. full-span wall/beam line and positioned point actions are applied once to
   their caller-assigned beam destination;
4. each simply supported line action transfers half to each end, while a point
   action uses its exact caller-supplied station for unequal reactions;
5. each column adds its own self-weight once; and
6. the column action is handed to its concentric footing destination.

The ledger stores source, destination, magnitude, intensity or point station
where applicable, origin entry identities, caller basis, source reference,
units, and a fixed sign convention. It checks each practical
source-to-destination assignment, slab-to-beam, beam-to-column, column
accumulation, column-to-footing, storey-to-foundation, and
combination-to-foundation balances. The workflow result and calculation book
expose one exact practical-action reconciliation record. Any residual outside
the explicit tolerance blocks the result.

## Approved exclusions and holds

The load model must explicitly list every unsupported or unsupplied V1
category. A category is omitted from `approved_exclusions` only when at least
one practical action of that category is supplied explicitly. This does not
authorize the library to discover, generate, distribute, or complete missing
project actions.

The footing entries are action handoffs, not footing designs. They intentionally
exclude footing self-weight and overburden. A future footing design must remain
on HOLD unless an externally approved soil basis and the complete required
service action basis are supplied according to the footing component contract.

B1 makes no claim for member design, reinforcement, serviceability, whole-frame
analysis, continuity, stiffness distribution, partial-span line loads,
automatic wall/equipment generation, wind, seismic, dynamic loads, load
reduction, multi-storey behavior, live ETABS, Excel, write-back, optimization,
release readiness, or qualified engineering approval.

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

The executable B1 vector is
`Python/tests/unit/test_building_gravity_v1.py`.

## Maintained onboarding example and explicit builder

Users do not need repository tests to construct their first request. The
installed package emits a complete, runnable 10 m x 4 m open-hall example:

```bash
python -m structural_lib gravity-v1 example -o gravity-request.json
python -m structural_lib gravity-v1 gravity-request.json -o gravity-result.json
```

The same request is available through
`get_gravity_workflow_example_request_v1()` as a typed object and
`get_gravity_workflow_example_document_v1()` as strict runnable JSON. The REST
definition embeds the runnable document, and the review UI exposes it through
`Load maintained example`.

`build_rectangular_gravity_workflow_request_v1()` accepts a frozen
`RectangularGravityWorkflowBuilderInputV1`. It generates only topology IDs,
source-record accounting, and model/load hashes. Span, sections, material,
loads, practical-action tuple, support idealizations, inclusion rules, both
load combinations, source hashes and references, exclusions, balance
tolerance, and every component design basis are required inputs. The builder
validates that the explicitly supplied support idealizations match the bounded
V1 topology; it has no engineering defaults. Empty practical-action and
design-basis tuples remain explicit caller choices; missing component bases
lead to the existing fail-closed component `HOLD` outcomes.

The maintained open-hall request supplies reviewed bar-selection constraints
but deliberately does not invent a project bar schedule. Its beam demand is
calculated, a preliminary recommendation is returned, and both beams remain
`HOLD` with `BEAM_SUPPLIED_REINFORCEMENT_NOT_SUPPLIED`. The first aggregate
governing issue is therefore the B1 reinforcement hold; the independent
footing detailing holds remain visible in their component results.

## B2 request boundary

`GravityWorkflowRequestV1` binds all downstream work to the accepted B1
identities. Its supplied `model_hash` must equal the building's computed hash,
its `load_model_hash` must equal the load model's computed hash, and the load
model must point back to that same building. Unknown fields, duplicate design
bases, and bases for unknown component IDs are rejected before calculation.

The request accepts four separate design-basis groups:

| Component | Generated by the workflow | Must be supplied and reviewed |
|---|---|---|
| Slab | spans, thickness, ULS area action, concrete strength | effective depth, steel, provided reinforcement, serviceability limits and acknowledgements |
| Beam | section, concrete strength, ULS moment and shear | effective depth and source, steel, shear-reinforcement basis, bar-selection constraints, source-referenced supplied longitudinal layers |
| Column | section, length, concrete strength, ULS axial action | steel, reinforcement, end condition and source, braced/axial-only acknowledgements |
| Footing | column geometry/strength and superstructure axial handoff | complete external service/factored actions, soil approval, thickness, depth and load-transfer basis |

Missing component bases do not cause invented defaults. They produce a visible
`HOLD` for the affected component.

For beams, a supplied design basis is not the same as completed detailing.
Flexure first calculates required `Ast`/`Asc`. Selection constraints may then
produce a preliminary recommendation, but only exact supplied tension and
compression-or-hanger layers receive area, horizontal and vertical clear
spacing, effective-depth identity, group-clearance, and both-support anchorage
checks. Missing bars retain the calculated result on `HOLD`; inadequate
supplied bars produce `FAIL`; only a complete passing arrangement can advance
the beam component to bounded `PASS`. Square-column support widths may be
resolved from the accepted physical model. Ambiguous or non-square support
orientation remains `HOLD` rather than selecting a hidden dimension.

## Exact member actions

The workflow derives 22 combination actions from the reconciled ledger: one slab, two
beams, four columns, and four footing destinations for each of the two frozen
load combinations. It uses the canonical simply supported load-analysis
function for combined full-span UDL and caller-positioned point-load moment and
shear; it does not introduce a frame solver. Practical actions do not increase
the component-action count. They change only their explicit destination load
path and are separately listed with exact source/destination reconciliation.

For the 6 m x 4 m hand example:

| Component/action | Service DL+LL | ULS 1.5(DL+LL) |
|---|---:|---:|
| Slab area action | 8.25 kN/m2 | 12.375 kN/m2 |
| Each beam line action | 20.25 kN/m | 30.375 kN/m |
| Each beam maximum moment | 91.125 kNm | 136.6875 kNm |
| Each beam support shear | 60.75 kN | 91.125 kN |
| Each footing superstructure handoff | 67.5 kN | 101.25 kN |

Each action records its source ledger-entry IDs and sign convention. The action
set and final workflow result are deterministic for the same accepted request.

## Applicability before calculation

The component applicability matrix is built before any component function is
called. Its exact adapters are:

| Kind | Supported V1 case | Canonical function |
|---|---|---|
| Slab | Simply supported one-way solid slab strip | `design_complete_one_way_slab_is456` |
| Beam | Simply supported rectangular beam under factored explicit actions | `design_beam_is456` |
| Column | Braced rectangular axial-only column | `design_column_is456` |
| Footing | Concentric isolated footing with complete external basis | `design_concentric_isolated_footing_is456` |

The B1 6 m x 4 m panel has a valid, balanced one-way load-transfer direction,
but its X/Y aspect ratio is only 1.5. The current slab component requires the
declared one-way direction itself to have an effective aspect ratio greater
than 2, so slab design remains `HOLD` for that hand example. A 10 m x 4 m
variant with the complete slab basis reaches the component adapter.

The footing ledger value remains a superstructure handoff. It cannot be
relabelled as the complete service action: an accepted footing basis must add
external footing self-weight/overburden and must provide the approved soil and
detailing inputs required by the component API. If the supplied complete
actions do not exceed the handoff within tolerance, the footing remains `HOLD`.

For completed isolated-footing detailing, development-length compliance uses
the exact unrounded Cl. 26.2.1 value. Straight ends, 90-degree bends, and
standard U-hooks are the only supported bottom-bar end arrangements. A bent or
hooked request must include an approved project geometry reference plus its
internal radius and extension. The component reports straight length to the
bend tangent, normalized anchorage value, total available development length,
bend arc, vertical envelope, return-leg envelope for a U-hook, bounded member-
envelope constructability, and total bar length. Missing geometry or an omitted
arrangement needed to close anchorage is
`HOLD`; complete but inadequate anchorage or physical fit is `FAIL`; only a
complete supported arrangement can `PASS`. Other bends, mechanical anchorage,
curtailment, laps, bar-to-bar collision modelling, coordinates, and complete
bar-bending schedules remain held.

The beam adapter additionally calls
`evaluate_supplied_beam_reinforcement_v1` after the canonical flexure/shear
calculation. A canonical design failure always remains `FAIL`; the supplied-bar
evaluation can govern an otherwise passing design as `HOLD` or `FAIL`, but it
cannot convert a design failure to `PASS`.

## Status contract

Every component uses `StructuralResultEnvelopeV2` and keeps these outcomes
distinct:

- input rejection: `BLOCKED`, before the workflow result is created;
- caught component calculation failure: `ERROR` with the component held;
- completed supported check: `PASS` or `FAIL`; and
- incomplete or unsupported prerequisite: `HOLD`.

At workflow level, any unresolved component `HOLD` keeps the aggregate on
`HOLD`, even if another completed component has failed. The individual `FAIL`
remains visible and is never converted to a pass. With no unresolved holds or
errors, any component failure makes the aggregate `FAIL`; otherwise it is
`PASS`. Every non-pass component carries at least one direct issue, and the
aggregate envelope deterministically promotes the first governing component
issue so CLI, REST, and UI users can see the reason beside the overall status.
Every result still requires qualified structural-engineering review.

## Product surfaces and calculation book

The same versioned request and result contracts are exposed through:

- Python package root: `structural_lib.run_gravity_workflow_v1`,
  `structural_lib.run_gravity_workflow_with_book_v1`, the typed request/result
  classes, the explicit builder, and the maintained example;
- CLI example: `python -m structural_lib gravity-v1 example`;
- CLI execution: `python -m structural_lib gravity-v1 REQUEST.json` with JSON
  or Markdown output;
- REST discovery: `GET /api/v1/building-gravity/v1/definition`;
- REST execution: `POST /api/v1/building-gravity/v1/run`; and
- review UI: `/workbench/building-gravity/v1`.

The review UI can load the maintained example or accept one JSON request. It
displays input blocking, the governing failure/hold reason, calculation errors,
component `PASS`/`FAIL`/`HOLD`, exact transferred actions, all four identity
hashes, and the qualified-review warning. It can download the machine-readable
calculation book.

The application catalogue keeps three claims separate: all 10 supported IS 456
component-family records are projected from the canonical capability registry;
the composed gravity workflow is registered with its component IDs and product
surfaces; and the existing beam-only automation adapter remains the only
tool-eligible catalogue capability. Discoverability does not grant autonomous
tool execution or expand engineering support.

`GravityCalculationBookV1` binds the model and load snapshots, reconciled
ledger, residual summary, applicability matrix, actions, component results,
issues, exclusions, limitations, and workflow hash. It is a review dossier,
not a release authorization or professional approval.

The executable B2 vectors are
`Python/tests/unit/test_gravity_builder_v1.py`,
`Python/tests/unit/test_gravity_workflow_v1.py`,
`Python/tests/unit/test_beam_reinforcement.py`,
`fastapi_app/tests/test_building_gravity.py`, and
`react_app/src/features/building-gravity/BuildingGravityReviewPage.test.tsx`.

## B2 exclusions

B2 does not add multi-storey or irregular topology, global stiffness/frame/FE
analysis, continuity, two-way or flat slabs, lateral or dynamic actions, live
load reduction, automatic engineering assumptions, Excel, live ETABS,
write-back, nightly optimization, package publication, release readiness, or
qualified professional approval. Those remain separately gated work.
