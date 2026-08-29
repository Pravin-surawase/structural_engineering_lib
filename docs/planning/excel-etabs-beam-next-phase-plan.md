---
owner: Main Agent
status: draft
last_updated: 2026-08-29
doc_type: spec
complexity: advanced
tags: [excel, etabs, beams, windows, optimization, construction]
---

# Excel + ETABS Beam Workflow — Next-Phase Plan

## Decision summary

The bounded read-only Excel -> Python -> live ETABS pilot is accepted on the
installed Windows stack. The next task is **W2: a read-only beam baseline and
topology contract**, not section optimization or model write-back.

The sequence is deliberate:

```text
W1 accepted read path
  -> W2 trustworthy model/force/topology baseline
  -> W3 beam design and detailing audit
  -> W4 construction-practice checks
  -> W5 offline section/rebar optimization proposals
  -> W6 controlled copied-model write-back and reanalysis
  -> W7 bounded iteration and qualified review
```

Changing beam stiffness can redistribute actions and global response. The
copied model permits controlled experiments, but it does not remove the need to
measure those effects or preserve columns, joints, slabs, foundations, drift,
and seismic-response dependencies.

## Completed foundation

| PR | Outcome | Merge |
|---|---|---|
| #890 | Added the Office.js -> FastAPI/Python -> live ETABS beam pilot | `d6e83cfd...` |
| #891 | Accepted installed `comtypes` list-shaped COM outputs | `57ba94af...` |
| #892 | Proved the exact open saved model with `GetModelFilename(True)` | `3ff3c80a...` |
| #893 | Completed installed Windows one-/five-beam acceptance and repaired remaining COM/launcher blockers | `c959775d...` |
| #894 | Added the one-branch/one-writer multi-device synchronization rule | `45ef7c29...` |

The tracked W1 receipt is
[`etabs-excel-python-pilot-w1-evidence.json`](../verification/etabs-excel-python-pilot-w1-evidence.json).
It records:

- Windows 11, Excel 64-bit, ETABS 23.3.1, Python 3.11.15, and `comtypes`
  1.4.16;
- copied model digest `99b7f3f1...fa6948b`, 702,831 bytes, locked after the
  run, with all 15 cases finished and original units restored;
- exact combination `117.(1.5DL+1.5LL)` and explicit M25/Fe500/detailing
  inputs;
- one beam and five beams reconciled between direct API and installed Excel,
  including every retained force station; and
- no analysis, unlock, save, section/load mutation, write-back, optimization,
  or professional approval.

The proprietary model path, force payloads, workbook contents, and external
evidence remain on the Windows evidence host and are referenced only by hashes
in Git.

## Architecture and VBA decision

Keep the accepted route:

```text
Excel Office.js -> trusted localhost -> FastAPI/Python -> ETABS COM
```

No VBA module is required for this route. Python remains the single calculation
owner and Excel remains the operator/review surface.

Legacy VBA/ETABS bundles are historical reference evidence, not runtime truth.
They may still help identify proven operator workflows, ETABS object/table
names, stable identifiers, export layouts, adjacency heuristics, error messages,
and drawing/report conventions. Before reusing any idea:

1. identify the exact external bundle and hash;
2. distinguish ETABS transport/UI logic from structural calculation logic;
3. map useful behavior to the canonical Python service contract;
4. verify it against the installed ETABS API and current model; and
5. add deterministic tests instead of copying old VBA formulas.

The repository does not currently track the old `.bas` modules themselves.
Their absence must not be filled with reconstructed or guessed code.

## What W1 proves—and does not prove

| Proven | Not yet proven |
|---|---|
| Exact open-model connection | Complete building/member inventory |
| Exact case/combination selection | Governing envelopes across approved combinations |
| Rectangular beam geometry and force stations | Reliable beam continuity and slab/column adjacency |
| Canonical beam design for explicit inputs | Provided-rebar verification and serviceability for the model |
| Controlled Excel projection | Congestion, layers, curtailment, anchorage, laps, and site sequence |
| Unit restoration and unchanged copied model | Independent frame-analysis parity |
| Bounded one-/five-beam installed acceptance | Economical section families and global-model optimization |
| Software acceptance | Engineering or construction-use approval |

## W2 — next-day bounded packet

### Objective

Create and locally verify a versioned, read-only contract that can describe the
beam baseline needed for later design and optimization. Only after the local
contract passes should a separate installed-Windows W2 acceptance run read the
copied model.

W2 is split to keep each candidate reviewable:

| Packet | Scope | Exit |
|---|---|---|
| **W2A — contract and adapter feasibility** | Exact schemas, ETABS getter inventory, topology/disposition rules, source identities, fake-COM shapes, frame-solver verdict | Local Python contract and focused tests; no REST/Excel/Windows run |
| **W2B — transport and review surface** | Live-bridge orchestration, FastAPI contract, controlled Excel tables, reconciliation and collision guards | Local focused checks and one immutable candidate |
| **W2C — installed Windows acceptance** | Exact copied model, direct API/Excel reconciliation, state/hash/unit proof | Tracked safe receipt plus external hash-bound evidence |

### W2A frozen local contract

W2A is implemented locally in
`Python/structural_lib/services/etabs_beam_baseline.py`. It accepts an already
supplied `SapModel`-shaped object and a caller-owned read-only model-file
observer. It does not connect to or launch ETABS. The observer is called before
and after the COM reads; the open-model path must equal the authorized absolute
`.edb` path, and path, SHA-256, byte count, and modified timestamp must remain
identical across both observations. The post-read observation cannot precede
the pre-read observation.

The versioned transport-neutral schemas are:

| Schema | Frozen responsibility |
|---|---|
| `etabs-beam-baseline-request/v1` | Authorized file identity, runtime/source provenance, unique explicit case/combination selections, and the 1 mm default orientation tolerance |
| `etabs-beam-baseline-build-result/v1` | Either one accepted baseline with no issues or a blocked result with stable issues and no partial baseline |
| `etabs-beam-baseline/v1` | Model/file/lock identity, restored units, stories, accepted frames, endpoint topology, every retained force station, exhaustive dispositions, runtime identity, getter-matrix hash, limitations, and frame-analysis verdict |
| `etabs-beam-baseline-hash/v1` | Canonical sorted-key UTF-8 JSON SHA-256 over every baseline field except the digest field itself |

Stable story, member, connection, station, disposition-row, result-selection,
getter-matrix, and whole-baseline identities are derived from canonical JSON and
SHA-256. A member identity binds the exact source unique name to the authorized
model digest. Runtime provenance keeps the adapter version, library version and
content identity, Python version, platform, and COM provider identity.

The exact getter matrix accepts both tuple- and list-shaped fake/live-COM
outputs and requires a trailing zero return code unless marked as a direct
value:

| Area | Frozen getters |
|---|---|
| Model | `GetModelFilename(True)`, `GetVersion()`, `GetModelIsLocked()`, `GetPresentUnits()` |
| Stories | `Story.GetStories()` |
| Frames and points | `FrameObj.GetNameList()`, `GetLabelFromName(Name)`, `GetPoints(Name)`, `GetSection(Name)`, `GetLocalAxes(Name)`, `PointObj.GetCoordCartesian(Name)` |
| Sections | `PropFrame.GetRectangle(Name)` |
| Result identity/status | `LoadCases.GetNameList()`, `RespCombo.GetNameList()`, `Analyze.GetCaseStatus()`, `Results.Setup.GetCaseSelectedForOutput(Name)`, `GetComboSelectedForOutput(Name)` |
| Force rows | `Results.FrameForce(Name, ItemTypeElm=0)` with all 14 outputs and every declared array length checked |

W2A does not call either output-selection setter. The only setter is temporary
`SetPresentUnits(kN_mm_C=5)`. Its return code is checked, the original unit enum
is restored after success or failure, and even a reported normalization failure
triggers a restoration attempt before the error propagates.

Accepted topology is endpoint-exact: horizontal members within tolerance are
beams, vertical members within tolerance are columns, and only shared ETABS
point names establish `BEAM_TO_BEAM` or `BEAM_TO_COLUMN` connectivity. No
coordinate-proximity, support, slab, material-grade, reinforcement, or design-
basis inference is permitted. Rectangular members retain labels, stories,
endpoints, normalized line direction, length, rotation, advanced-axis flag,
section dimensions, auto-select label, and material-property label. Diagonal
members, unavailable/non-rectangular sections, and frames with advanced local
axes are explicitly excluded; a retained beam connected to any excluded frame
blocks the baseline because the topology would be incomplete.

The frozen disposition reason codes are:

- accepted: `STORY_ACCEPTED`, `FRAME_ACCEPTED_BEAM`,
  `FRAME_ACCEPTED_COLUMN`, `CONNECTIVITY_ACCEPTED_BEAM_TO_BEAM`,
  `CONNECTIVITY_ACCEPTED_BEAM_TO_COLUMN`, `RESULT_SELECTION_ACCEPTED`, and
  `RESULT_STATION_ACCEPTED`;
- excluded: `FRAME_ORIENTATION_UNSUPPORTED`,
  `FRAME_ADVANCED_LOCAL_AXES_UNSUPPORTED`,
  `SECTION_NOT_RECTANGULAR_OR_UNAVAILABLE`,
  `NO_FRAME_ENDPOINT_CONNECTION`, and `RESULT_SELECTION_NOT_REQUESTED`; and
- blocked: `CONNECTED_FRAME_EXCLUDED`, `RESULT_SELECTION_NOT_AVAILABLE`,
  `RESULT_SELECTION_NOT_ACTIVE`, `RESULT_CASE_NOT_FINISHED`,
  `RESULT_SELECTION_EMPTY_FOR_BEAM`, and `BEAM_INVENTORY_EMPTY`.

An explicit case must exist, already be selected for output, and have finished
status code 4. An explicit combination must exist and already be selected;
every accepted beam must then return at least one row for it. Every
`FrameForce` row is length-checked and retained or dispositioned. Retained rows
preserve object/element names and stations, case/combination identity, step
type/number, signed `P`, `V2`, `V3`, `T`, `M2`, and `M3`, source row index, and
stable station identity. Moment/torsion units are normalized from kN-mm to
kN.m.

The independent-analysis audit remains exactly `HELD_NOT_SUPPORTED`:
`gravity_workflow` and `gravity_loads` are documented closed-form gravity
paths, serviceability defers continuous behavior to frame analysis, and no
accepted stiffness/frame solver exists. W2A adds no solver or parity claim.
Focused tuple/list, getter/return-code, topology/disposition, result-completeness,
file-freshness, deterministic-hash, JSON round-trip, and unit-restoration tests
live in `Python/tests/unit/test_etabs_beam_baseline.py`. W2B REST/Excel work and
W2C installed execution remain unstarted.

### Required read-only inventory

- exact model/version/hash/lock/unit identity;
- stories and elevations;
- frame IDs, stable unique names, endpoints, orientation/local axes, story,
  section assignment, rectangular dimensions, and material-property labels;
- beam-to-beam and beam-to-column endpoint connectivity;
- slab/area context only where ETABS provides a deterministic association;
- load cases and combinations with explicit type/status metadata;
- every retained force station for each explicitly approved result selection;
- accepted, excluded, and blocked row dispositions with reason codes; and
- source/runtime identity and freshness hashes.

W2 must not infer concrete grade, reinforcement grade, cover, bar sizes, design
standard, or construction assumptions from ETABS property names.

### Independent frame-analysis feasibility audit

W2 must inspect the existing gravity/frame-analysis capabilities before making
any solver claim. The decision must be one of:

- `SUPPORTED_BOUNDED`: enough data and an accepted solver exist for one clearly
  defined planar/gravity verification model;
- `ADAPTER_REQUIRED`: the solver exists but the ETABS-to-solver contract is
  incomplete; or
- `HELD_NOT_SUPPORTED`: the repository cannot independently reproduce the
  selected ETABS behavior without a separately approved solver scope.

No result may be described as full ETABS parity merely because reactions or one
moment value are similar.

The current source scan indicates that `gravity_workflow` and
`gravity_loads` intentionally use closed-form gravity actions and explicitly
exclude a stiffness/frame solver; the beam serviceability code likewise says
multi-span continuous beams require frame analysis. Existing beam cost/Pareto
optimizers evaluate member-design candidates but do not reanalyze the building.
Therefore W2 starts with `HELD_NOT_SUPPORTED` as the expected frame-analysis
verdict unless the audit finds a different accepted solver authority. A new
matrix/frame solver would be a separate approved programme, not an adapter
hidden inside W2.

### W2 acceptance rows

1. Source starts from freshly fetched `origin/main` on a new task branch.
2. Local contract and fake-COM tests pass without Windows or ETABS.
3. Every ETABS output shape and return code is validated fail-closed.
4. Units are restored on success and every failure path.
5. No ETABS setter is permitted except temporary present-unit selection.
6. Result selections are explicit and every force row retains its provenance.
7. Member/connectivity inventory is exhaustive for the bounded model or carries
   explicit exclusions; “first beams” is not W2 completeness.
8. Excel projection has stable schemas, row identities, and collision guards.
9. Direct API and Excel reconcile exactly on the installed Windows acceptance
   sample.
10. Model hash, size, timestamp, lock, cases, and units are unchanged afterward.

### W2 non-goals

- running analysis or design inside ETABS;
- unlocking, saving, or changing the copied model;
- changing sections, materials, modifiers, releases, loads, diaphragms, meshes,
  or result combinations;
- optimizing beam sizes or reinforcement;
- designing columns, joints, slabs, walls, or foundations;
- claiming a general 2D/3D frame solver; or
- professional or construction-use approval.

## Later phases after W2

### W3 — beam design and detailing audit

- freeze approved ULS/SLS result combinations and envelope rules;
- design/check all accepted beams with explicit IS 456/IS 13920 applicability;
- retain support, span, sign, station, and combination provenance;
- check flexure, shear, torsion, minimum/maximum steel, serviceability, anchorage,
  and supplied reinforcement where trustworthy inputs exist; and
- report missing dependencies as blocked—not assumed.

### W4 — construction-practice layer

- group beams into practical section/rebar families;
- coordinate top/bottom bars through adjacent spans and supports;
- check bar layers, clear spacing, cover, stirrup fit, congestion, curtailment,
  lap/anchorage zones, column-joint conflicts, and erection sequence;
- distinguish code failure, constructability warning, and preference; and
- retain an engineer-editable approval/override ledger.

### W5 — offline optimization proposals

- generate candidate section/rebar families without touching ETABS;
- minimize concrete, steel, formwork variety, congestion, and construction
  complexity under explicit safety/serviceability constraints;
- compare every candidate with the W2 baseline using transparent quantities and
  rates; and
- reject local beam savings that worsen governed global/member constraints.

### W6 — controlled copied-model write-back and reanalysis

This phase requires a separately reviewed mutation contract:

- exact copied-model allowlist plus pre-run digest and recoverable backup;
- explicit frame/old-section/new-section change ledger and section-property
  definitions;
- no unexpected dialogs, license warnings, or abnormal-condition dismissal;
- unlock only for the bounded mutation window;
- save only the authorized copy, run only approved cases, restore units, and
  record post-run identity;
- compare member actions, reactions, drift, modal/seismic metrics, and affected
  columns/joints/slabs/foundations against frozen tolerances; and
- abort or revert the candidate when any guard fails.

### W7 — bounded iteration and review

Iterate only over accepted candidate families, with a finite evaluation budget,
deterministic stopping rules, full mutation/evidence ledgers, and qualified
structural-engineer review before engineering or construction use.

## Next efficient sequence

1. Review the clean W2A candidate on
   `codex/etabs-excel-beam-w2a-baseline` against the frozen contract above.
2. Confirm the affected focused checks and consolidated quick-gate receipt for
   the exact candidate; W2A intentionally has no live ETABS/Excel evidence.
3. Accept or repair W2A as its own bounded packet.
4. Only after W2A acceptance, scope W2B separately for live-bridge
   orchestration, REST/Excel projection, reconciliation, and collision guards.
5. Keep W2C unscheduled until W2B has a separately accepted immutable
   candidate and an exact authorized copied-model evidence plan.

## Stop conditions

Stop before mutation and ask for direction if the exact model identity changes,
the open model is not the authorized copy, analysis results are stale/missing,
an ETABS/license/abnormal-condition dialog appears, the requested design basis
changes, or W2 would need setters beyond temporary unit selection.

## New-chat starter

```text
Review W2A of the Excel + ETABS beam programme on
`codex/etabs-excel-beam-w2a-baseline`. Read the frozen W2A contract in
docs/planning/excel-etabs-beam-next-phase-plan.md, the W1 receipt, and the pilot
guide. Verify the transport-neutral schemas, pre/post model-file observation,
getter/return-code matrix, exhaustive topology/result dispositions,
deterministic hashes, tuple/list fake-COM shapes, and success/failure unit
restoration. Keep `HELD_NOT_SUPPORTED`: the repository has no accepted frame
solver. Do not open or mutate ETABS, run analysis, add W2B REST/Excel surfaces,
schedule W2C, optimize, write sections, or claim engineering approval. Accept
or repair only this clean W2A candidate.
```
