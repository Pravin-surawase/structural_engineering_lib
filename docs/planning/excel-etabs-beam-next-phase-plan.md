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

## Tomorrow's efficient sequence

1. Fetch GitHub and prove the new chat is on current `origin/main`; inspect all
   worktrees and open PRs before creating the W2 branch.
2. Read this plan, the W1 receipt, the pilot guide, the live bridge contract,
   and the existing gravity/frame-analysis services.
3. Inventory any accessible legacy VBA evidence by exact identity; do not run
   macros or copy formulas.
4. Freeze the W2 schema, ETABS calls, result-selection policy, topology rules,
   dispositions, non-goals, and focused tests.
5. Complete W2A only: implement the transport-neutral contract and fake-COM
   adapter/shape evidence, then run affected focused tests and the consolidated
   quick gate once.
6. Stop at a clean W2A candidate and review the diff. Do not begin W2B or
   schedule W2C until W2A is accepted.

## Stop conditions

Stop before mutation and ask for direction if the exact model identity changes,
the open model is not the authorized copy, analysis results are stale/missing,
an ETABS/license/abnormal-condition dialog appears, the requested design basis
changes, or W2 would need setters beyond temporary unit selection.

## New-chat starter

```text
Resume the Excel + ETABS beam programme from the current fetched GitHub main.
Read docs/planning/excel-etabs-beam-next-phase-plan.md, the W1 receipt, and the
pilot guide first. Start W2A only: freeze and implement the transport-neutral
read-only beam baseline/topology/result-provenance contract plus fake-COM shape
tests. Inspect legacy VBA evidence only by exact identity and reuse ideas, not
formulas. The current repository explicitly has no frame solver, so retain
`HELD_NOT_SUPPORTED` unless a different accepted solver authority is found. Do
not open or mutate ETABS, run analysis, add REST/Excel W2 surfaces, write
sections, optimize, or claim engineering approval. Finish at a clean locally
verified W2A candidate and leave W2B/W2C separate.
```
