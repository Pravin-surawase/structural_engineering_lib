---
owner: Main Agent
status: active
last_updated: 2026-09-02
doc_type: spec
complexity: intermediate
tags: [etabs, excel, vba, data-lifecycle, beams, optimization]
---

# Legacy VBA data-flow and workflow lessons

## Decision and authority

Adopt the useful operating pattern proved by the legacy Excel/VBA work:

```text
bounded ETABS query
        -> transient typed arrays
        -> validate and reduce near the source
        -> evaluate the beam or beam line
        -> retain the decision evidence
        -> release the unused raw rows
```

The normal product does **not** need to copy the complete ETABS database or
write every force station into Excel. Geometry and topology may remain in a
phase cache because many consumers reuse them. Large force/design-result arrays
should normally live only for the beam, beam line or bounded batch currently
being processed.

This does not mean “save nothing.” A final engineering result must retain the
small, exact evidence needed to identify, reproduce and review the decision.
When independent replay of an envelope requires its complete input slice, retain
that bounded slice or reacquire it before the ETABS model/result epoch changes.

The human-facing phase authority remains the
[beam design and ETABS optimization master plan](beam-design-optimization-master-plan.md).
The [ETABS COM and W3 reanalysis plan](etabs-w3-com-vba-and-reanalysis-plan.md)
continues to own connection, state, call-ledger and copied-model transaction
safety. This document records the data-lifetime decision and a reusable idea
inventory; it does not activate a later phase or authorize ETABS/Excel use.

## Evidence and claim boundary

The review was static. It did not open Excel or ETABS, attach to a process, run
analysis/design, select output cases, change units, update a section or save a
model.

| Preserved package | SHA-256 | What it can support |
|---|---|---|
| `01_Legacy_ETABS_2019_2021.zip` | `e927f57c9203a55bfe83b00a341eedcc31b6f34266a11322cc6b665d9f276b68` | Historical production-workflow evidence for beam, column, wall, reaction, displacement and load-combination operations |
| `02_ETABS_Export_VBA.zip` | `28771d28de96142d3d53a0ab82c9d343ff801b8cae407d88b7b2f195ca750e8a` | Later export, filtering, logging, progress and metadata prototypes |
| `03_Structural_Design_VBA.zip` | `3ab9719e68f9a8f901ab48040b26147ee0ff35cdd8fad24fe39d2b9897970acc` | Later typed design, compliance, detailing, schedule, BBS and DXF prototypes |
| `04_Excel_Legacy_Workbooks.zip` | `1d9cc925db7af09cca7ff7f89b06bda97ecf7b68921283bf990a3bdf058f3d46` | Historical workbook/add-in packaging context |

The 2019-2021 modules demonstrate that the workflow was used, but they are not
an independent formula oracle. The later export and design modules are useful
prototypes, not proof of current ETABS compatibility or engineering acceptance.
All formulas and API signatures still require their current maintained owners
and evidence.

## What the old code actually retained

| Routine | ETABS/API working data | Reduced result retained |
|---|---|---|
| `BEAMS_FROM_ETABS` | One `GetAllFrames` response containing names, properties, joints, coordinates, offsets and angles | Selected-story beam identity, section size, endpoints and plan coordinates |
| `BeamReinf` | Per-beam station arrays from `GetSummaryResultsBeam_2` | Top steel in end/mid regions, maximum bottom steel, shear and torsion reinforcement summaries |
| `Column_Detailing` | All-frame inventory plus per-frame column design arrays | Column identity/geometry, maximum longitudinal-steel requirement, coordinates, length and warnings |
| `Get_Base_Reactions` | Reaction arrays for each selected case/combination | The reaction components used by the scaling worksheet |
| `Jt_Disp` | Full displacement/rotation arrays for the requested joint | One requested displacement component and step |
| `Piers` | Pier result arrays across stories and stations | Maximum wall reinforcement and shear values per grouped pier/story |
| `ETABS_OneClick_Export.GetBeamData` | Per-frame `FrameForce` arrays | A small `Mu_max`, `Mu_min`, `Vu_max` beam record |

Most force/design arrays were local procedure variables and disappeared when
the procedure ended or were replaced on the next member. Some geometry and
summary arrays such as `AllBEAMS`, `Column_Data` and `Colum_XYZ` were module
variables and could remain alive for the Excel session. Worksheets were also a
small persistent working store. Therefore the precise lesson is not “all data
was temporary”; it is “large raw result arrays were usually reduced before
persistence.”

Separate export routines could write all force rows to CSV. That should remain
an explicit diagnostic/audit mode, not the default interactive workflow.

## Adopted data-lifetime model

| Data class | Normal lifetime | Normal storage | Examples |
|---|---|---|---|
| Target and result identity | Whole job and durable result | Durable | ETABS PID/runtime, model path/hash, units, lock state, result epoch, query scope |
| Geometry/topology | Phase or whole job | Typed memory cache; optional canonical snapshot | Stories, joints, frames, sections, axes, releases, offsets, connected elements |
| Raw result batch | One beam line or bounded batch | Memory only by default | Signed force stations, ETABS design rows, joint displacements |
| Normalized action slice | One evaluation or phase | Typed memory cache | Same-row actions with station, combination, sign and physical face |
| Candidate scratch data | One search batch | Memory only | Layer arrangements, section alternatives, intermediate checks and objectives |
| Decision evidence | Durable | Canonical result/dossier | Governing rows, failed/held gates, selected schedule, quantities, savings and limitations |
| Full raw export | Explicit diagnostic request | External bounded artifact with identity and retention policy | Complete selected force table or exact accepted-candidate replay slice |

### Minimum durable evidence

For each accepted, failed or held design decision, retain at least:

- model, runtime, catalogue, criteria and result-epoch identities;
- the exact member/beam-line identity and normalized geometry used;
- acquisition scope, requested cases/combinations, units, row count and digest;
- every governing signed row with station, step, combination, physical face and
  concurrent action components;
- any additional bounded input rows required to replay the claimed envelope or
  check without ETABS;
- the complete check ledger, including `HOLD` and excluded conditions;
- the selected section and reinforcement layers/zones;
- deterministic quantities, objectives and tie-break result; and
- final ETABS verification identity for any stiffness-changing candidate.

A digest of discarded rows proves only that a byte set had an identity; it does
not make the discarded values independently replayable. The final dossier must
therefore either retain the complete bounded input needed by its claim or state
that fresh reacquisition from the unchanged result epoch is required.

### Normal processing unit

The preferred runtime unit is a connected beam line, not one scalar and not the
entire building:

1. read or reuse its geometry, supports and connected-element context;
2. acquire all required action/design rows for that line in one bounded call or
   table slice;
3. validate return status, units, identities, station mapping and completeness;
4. normalize and derive signed, same-row governing references;
5. run the applicable design gates and candidate evaluator;
6. retain the decision evidence and any required replay slice; and
7. release the raw API/table arrays before loading the next batch.

Batch size is an implementation choice and must not change the result. The same
input processed as one line, ten lines or a complete bounded set must produce
the same canonical decisions and hashes.

## Why this is efficient

The main cost to control is boundary traffic, not merely RAM:

- use one bulk inventory call or bounded table read instead of one COM call per
  coordinate or force component;
- perform filtering, grouping, envelope selection and design in Python/.NET
  memory rather than through cell-by-cell Excel operations;
- reuse geometry/topology while its model identity is unchanged;
- cache a result only under the exact model, result epoch, criteria, catalogue,
  scope and algorithm identities;
- write compact Excel tables in blocks and load detailed rows only on demand;
- preallocate or append to native collections rather than repeatedly using
  `ReDim Preserve` inside inner loops; and
- discard transient arrays at phase/batch completion and on cancellation.

This keeps the old VBA responsiveness while adding explicit invalidation and
traceability.

## Additional useful ideas found in the old code

These are workflow ideas to reuse through maintained owners, not instructions
to copy the VBA implementation.

| Legacy idea | Product value | Maintained direction | Phase |
|---|---|---|---|
| Story and X/Y scope controls | Lets the engineer start with a comprehensible subset | Provide explicit model/story/beam-line/selection scopes with visible counts and identity | 1-3 |
| Beam continuity from shared joints | Treats support steel across adjacent spans as one physical problem | Build a topology graph, resolve member orientation and coordinate reinforcement across the whole beam line | 3-4 |
| `BeamNumbers` similarity grouping | Reduces unique beam types, bar marks and formwork changes | Add criteria-bound design-family clustering; every family adopts a schedule that passes its worst member and reports the standardization cost | 5 |
| Column grouping by vertical story/section sequence | Recognizes repeated stacks rather than isolated members | Use column stacks as support context and whole-model safeguards; full column optimization remains separate | 3 and 6 |
| Model-native section dropdown | Prevents proposing properties that ETABS cannot apply | Build the Phase 5 candidate domain from the verified project property catalogue; first loop uses existing properties only | 1 and 5 |
| Envelope, critical-station and all-station modes | Matches data volume to the question | Make acquisition detail an explicit typed mode: design evidence, drill-down or diagnostic export; never silently change the claim | 1-2 |
| Same-row envelope tracking | Preserves companion actions at the governing moment/shear row | Reuse current `BeamActionsV1`/governing-reference owners and retain sign, station, step and physical face | 2 and 4 |
| Progress, cancellation and checkpoints | Makes long jobs operable from Excel | Expose stage/item progress and cancel only at safe boundaries; resume from verified immutable inputs, never replay an uncertain ETABS mutation | All |
| Multi-case compliance with governing utilization | Gives one result while keeping per-check reasons | Reuse the common candidate evaluator; unchecked mandatory gates return `HOLD`, not a synthetic pass | 4-5 |
| Start/mid/end reinforcement and stirrup zones | Produces construction-oriented output | Retain exact longitudinal layers and transverse intervals; derive zones from actions/detailing rules rather than fixed percentages | 4 |
| Beam schedule, BBS, quantities and DXF | Connects design to drawings, material and savings | Reuse existing schedule/BBS/DXF services and their bar-mark consistency checks; extend them from the accepted physical schedule | 4-6 |
| Worksheet-to-ETABS member highlighting | Helps the engineer visually inspect a proposed set | Consider a separately controlled review command with exact target and reversible selection state; it is not part of getter-only acquisition | Review UI |
| Reaction-scaling read/calculate/update/rerun loop | Demonstrates a general closed-loop automation shape | Reuse only the transaction pattern—observe, calculate, propose, authorize, mutate owned copy, reanalyse, verify—for separately scoped future operations | Separate programme |
| Home/input/design/schedule/log separation | Makes Excel a workflow surface instead of a raw dump | Use the ribbon/task pane for commands and status; worksheets hold compact review tables, schedules and logs | UI |

Several of these capabilities already exist in part. In particular, same-row
governing actions, typed reinforcement schedules, candidate evaluation, BBS,
DXF and similar-beam drawing grouping have maintained Python owners. Extend
those owners; do not create a second VBA-style calculation route.

## Legacy implementation patterns to reject

| Do not port | Why it changes the engineering or operational outcome |
|---|---|
| Reduce a result to `Max(...)` only | Loses governing combination, station, sign, face and concurrent components |
| Convert maximum absolute shear to a positive value | Loses shear direction and can break physical-face or interaction logic |
| Assume result rows are already grouped by combination | A changed provider ordering can mix envelopes; group explicitly by typed identity |
| Apply a moment threshold before tracking shear | A high-shear/low-moment row can disappear from the shear envelope |
| Define end/mid regions only as fixed thirds or 20/60/20 percentages | Physical supports, offsets, discontinuities and design zones may not align with those percentages |
| Substitute sample data, zero forces, default dimensions/materials or fallback effective depth | Missing evidence becomes a plausible-looking design instead of `HOLD` |
| Mark an optional or unexecuted mandatory check as safe | Produces a false overall pass; use `HOLD`/`NOT_EVALUATED` |
| Attach with generic `GetObject(...)` | Can select the wrong ETABS process/model |
| Change units/output selections or run analysis during attached observation | A read workflow silently mutates the engineer's session and may invalidate result identity |
| Unlock the current model, delete/recreate combinations or call `SetSection` directly | Has no owned-copy isolation, readback, recovery or bounded retry safety |
| Use `On Error Resume Next` across API/decoding work | Converts COM/signature failures into partial or stale data |
| Store bar layouts as strings such as `3 T 20` and parse with `Left`/`Right` | Cannot reliably represent multiple layers, mixed diameters, double-digit counts, face or centroid geometry |
| Use module globals or worksheet positions as data identity | Old values can survive a rerun and cell layout changes can silently remap fields |
| Restore Excel calculation/screen state only on the happy path | A failure can leave the user's workbook altered; cleanup must be unconditional and exact |

## Excel add-in implication

When UI implementation is authorized, the old workbook suggests a compact
ribbon/task-pane journey rather than a large raw-data workbook:

| Ribbon group | Primary commands and views |
|---|---|
| Connection | Choose exact ETABS process, verify model, show read-only/mutation capability and freshness |
| Data | Acquire minimum scope, refresh selected beam line, show identity/counts and optional diagnostic export |
| Structure | Build/review beam lines, joints, supports and connected columns/slabs; show unresolved topology |
| Design | Check selected line or declared batch; show governing gates, layers/zones and `PASS`/`FAIL`/`HOLD` |
| Optimize | Generate candidates, standardize families, rank feasible results and explain rejected options |
| ETABS verify | Prepare owned copy, apply/read back, analyse, compare safeguards and retain/quarantine result |
| Deliver | Produce schedule, BBS/DXF, quantities, savings, limitations and review dossier |

Excel remains the operator and review surface. The Windows host owns controlled
ETABS communication, Python owns engineering calculations, and the optional
evidence store owns only canonical decision artifacts—not an uncontrolled copy
of the ETABS database.

## Acceptance requirements for future implementation

1. No normal command writes all force stations to Excel or a database.
2. A complete raw export occurs only through an explicit diagnostic/audit
   command with a visible scope and retention destination.
3. Changing batch size or processing order does not change decisions or hashes.
4. Every displayed governing value opens a drill-down containing its exact
   source row, combination, station, sign, face and result epoch.
5. Cache reuse is impossible after any relevant model/result/criteria/catalogue
   identity changes.
6. Cancellation releases transient data and either leaves no external change or
   records a recoverable/quarantined owned-copy transaction.
7. The final accepted candidate retains enough bounded inputs for its stated
   replay/review claim.
8. Excel summaries, BBS/DXF and savings all derive from the same accepted
   physical schedule and candidate identity.

## Immediate programme effect

Phase 1 remains the only active phase. Its C2 parser and acquisition
orchestrator should support explicit scope, chunking and retained-evidence
projection, but the current task does not add new public functions. Beam-family
standardization, continuity coordination, add-in commands and copied-model
iteration remain later-phase requirements until their predecessor gates pass.
