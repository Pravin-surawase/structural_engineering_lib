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
installed Windows stack. W2A's read-only beam baseline/topology contract is
merged through PR #896 at `0f5c918e...`. The Windows static signature audit now
proves the installed ETABS 23.3.1 COM surface needed by that contract. The
authorized next work is the bounded W2B transport/review surface followed by
guarded W2C installed read-only acceptance—not section optimization or model
write-back.

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
| #895 | Closed W1 and froze the W2A/W2B/W2C next-phase contract | `a3f36cb4...` |
| #896 | Merged the reviewed W2A baseline and unknown-story fail-closed repair | `0f5c918e...` |

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

## Machine roles and exact W2A handoff

The machine roles are now explicit:

| Machine | Role | Normal work | Held work |
|---|---|---|---|
| **Mac** | Primary development and integration machine | Planning, normal Python/FastAPI/React/Excel source work, cross-platform tests, candidate review, PR/check follow-up, merge verification, and current `main` ownership | It cannot supply installed ETABS/Excel COM evidence and must not claim that fake-COM tests are installed acceptance |
| **Windows** | Installed Excel/ETABS testing and evidence machine | Exact copied-model/workbook runs, COM/API behavior, direct-vs-Excel reconciliation, device-safe receipts, and only the bounded host-specific repairs needed to make those tests trustworthy | It does not own normal `main`, general feature development, merge decisions, or unreviewed application/model mutation |
| **GitHub** | Shared tracked-history authority | Task branches, PR review, checks, merge history, and exact writer-device handoff | It does not contain proprietary models/workbooks, credentials, or unapproved external evidence |

The Windows primary checkout remains a clean but deliberately stale/protected
`HOLD_MAIN` lane. W2A was independently reviewed on Mac and merged unchanged
with its bounded repair through PR #896: reviewed head `0972e1af...`, merge
`0f5c918eb87b658448737fd6bf023ccb4bd07c74`. Windows fetched and verified that
exact merge before creating the dedicated static-audit worktree and branch
`codex/etabs-w2c-com-signature-audit`; neither protected `main` nor the retained
W2A worktree was changed.

The user has authorized one cumulative Windows W2 campaign after the static
audit checkpoint. The transfer rule is now:

1. Windows finishes, verifies, commits, and pushes the metadata-only static
   audit branch as a durable checkpoint.
2. Windows creates `codex/etabs-excel-beam-w2-campaign` from that exact pushed
   audit head, remains its sole writer, and freezes/pushes W2B before any
   installed W2C execution.
3. W2C may start only when all static-audit preconditions pass against the
   exact W2B checkpoint and the approved copied model. It remains read-only and
   aborts before results if identity, freshness, topology, case/combination, or
   unit restoration cannot be proved.
4. Windows pushes the final clean campaign branch and stops writing. Mac then
   performs one cumulative review, PR/check follow-up, and integration.
5. Source moves only through GitHub; model/workbook/vendor bytes and detailed
   result payloads remain device-local and hash-bound.

## Windows host setup snapshot

The W2A preparation established and verified this development/evidence
toolchain on Windows:

| Component | Observed version/state |
|---|---|
| Git for Windows | `2.55.0.windows.3`; Git Bash available |
| GitHub CLI | `2.98.0`; authenticated as `Pravin-surawase`; HTTPS repository access verified |
| `uv` | `0.12.7` |
| Node/npm | Node `24.19.0`; npm `11.17.0` |
| Python | `3.11.15` in the primary checkout `.venv` |
| Key Python runtime | `comtypes 1.4.16`, `pydantic 2.13.5`, `fastapi 0.141.1`, `numpy 2.4.6` |
| Hooks | `pre-commit 4.6.2` installed in the shared Git common hooks directory |
| Source binding | Linked-worktree launcher imports the invoking W2A source and reports `source_bound=true` |
| User runtime controls | `STRUCTURAL_LIB_PYTHON` points to the primary `.venv` interpreter; `PYTHONUTF8=1` |
| Checkout normalization | System Git has `core.autocrlf=true`; tracked E2K/XML/CSV/JSON/Python/docs and shell scripts are protected by explicit LF attributes where byte identity/execution matters |

The previous unusable virtual environment is recoverably retained as
`.venv-broken-20260829`; it was not deleted. WSL and Docker were not installed
because W2A/W2C do not require them, and adding a heavyweight restart/licensing
surface would not improve ETABS/Excel evidence.

Use these host checks from the exact task worktree before future Windows
evidence:

```bash
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/node_runtime.py --show-runtime
./scripts/agent_start.sh --quick
gh api user --jq .login
git status --short --branch
```

Open a fresh terminal/Codex process after machine-level installation so it
inherits the updated user `PATH`. The maintained launchers remain authoritative
and now handle Windows virtual-environment paths, executable suffixes, UTF-8
output, and MSYS/Windows source-path normalization.

## Root-cause and solution ledger

| Symptom | Root cause | Implemented solution | Future control |
|---|---|---|---|
| Initial task opened in an empty no-commit workspace | Desktop task root was not the retained source repository | Located the exact repository read-only, fetched GitHub, inspected all worktrees, and created a separate W2A worktree from `origin/main` | Always prove repository root, branch, worktrees, and fetched base before edits |
| Project Python/Bash/tooling unavailable | New Windows host had missing CLI tools, Store-Python aliases, and an unusable inherited `.venv` | Installed maintained Git/GitHub/uv/Node/Python toolchains and rebuilt the canonical primary `.venv` with required extras | Use only repository launchers; diagnose source binding before evidence |
| Unicode commands crashed under `cp1252` | Existing desktop process inherited the legacy Windows console encoding | Persisted `PYTHONUTF8=1` and made `python_runtime.sh` default child Python to UTF-8 | Status symbols and JSON output must work in a fresh and already-running Windows shell |
| Node runtime and React build failed on Windows | Shared code assumed extensionless `node`/`npm` and POSIX inline environment assignment | Resolve executables with `shutil.which`; invoke explicit Node memory flags for TypeScript/Vite | Runtime tests cover `.exe`/`.cmd`; production build must pass on Windows |
| Frozen ETABS snapshot hashes changed and shell hooks rewrote `.sh` files | System `core.autocrlf=true` converted formats that lacked explicit checkout policy | Added LF attributes for E2K/XML, `.gitattributes`, and shell scripts; restored exact index-equal bytes | Never regenerate expected hashes to hide checkout conversion; compare blob/worktree hashes and require shell scripts to remain LF |
| Correct linked-worktree source was rejected as shadowing | Git Bash/MSYS and Windows Python returned equivalent paths with different drive/separator forms | `agent_start.sh` canonicalizes both paths with `cygpath -m` on Windows before comparison | `agent_start.sh --quick` and governance regression must prove `Python source binding: current worktree` |
| First W2A freshness draft could not prove temporal order | It accepted a preassembled “after” observation before the COM read occurred | Adapter now calls a supplied read-only file observer immediately before and after COM extraction and checks path/hash/size/timestamp/order | W2B must supply the actual observer; W2C must reconcile its evidence with external file hashes |
| Windows CLI auth was uncertain after account reconnection | GitHub CLI credential state had changed outside the repository | Completed official browser/device authentication and verified the exact user/repository/main queries | Recheck `gh api user` and repository access before push/PR; never log the token |
| npm reports one high advisory | Dev-only `nanoid 3.3.17` arrives transitively through `postcss`/Vite and is below fixed `3.3.18`; production-only audit is clean | Recorded but did not mix an unrelated lockfile rewrite into W2A | Resolve in a separate dependency-maintenance candidate, run frontend tests/build/audit, and review the exact lockfile diff |
| W2A display signatures did not show every typelib input/default detail | The frozen matrix describes the adapter call/result contract, while the installed typelib also exposes optional `LoadCases.GetNameList(CaseType=0)` and requires the explicitly supplied `FrameForce(..., ItemTypeElm)` | Bound all 19 operations to the exact x64 typelib/generated wrapper and recorded both details without changing working behavior | Re-audit the exact typelib hash after any ETABS/comtypes drift; keep the runtime call explicit and fail closed on shape/return drift |

This ledger records software/tooling causes and controls. It does not upgrade
software checks into engineering approval or authorize model mutation.

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

### Windows static COM-signature audit

The Phase A audit is recorded in
[`etabs-excel-beam-w2c-com-signature-audit-evidence.json`](../verification/etabs-excel-beam-w2c-com-signature-audit-evidence.json).
It inspected only installed registry/file/type-library/generated-wrapper
metadata. It did not create a COM object, attach to the pre-existing ETABS
process, call `SapModel`, open a model/workbook, or run analysis/design.

The exact installed authority is ETABS `23.3.1.4563`, x64 `ETABSv1.tlb` LIBID
`{542F7A9D-3A7D-4061-97B3-3A1276FF83BD}` version `1.0`, SHA-256
`3823416b...24ef0e`, inspected with 64-bit Python `3.11.15` and `comtypes`
`1.4.16`. All 18 frozen getters plus `SetPresentUnits` are `PROVED` for name,
argument/output order, types, defaults, return-code form, and installed Python
container behavior. No outcome-changing adapter mismatch was found.

Two precision notes remain visible: `LoadCases.GetNameList` has an optional
trailing input `CaseType=0`, so the no-argument W2A call correctly requests the
unfiltered inventory; and `FrameForce` requires `ItemTypeElm`, for which W2A
explicitly supplies enum value 0 (`ObjectElm`) rather than relying on a default.
The installed provider produces list-shaped outer multi-output results and
tuple-shaped one-dimensional SAFEARRAYs by default; W2A's tuple/list decoder is
a compatible superset. Actual data, return-code values, counts, file identity,
lock/unit restoration, topology, dispositions, results, and hashes remain
installed-session proof—not static inference. ETABS design summary remains
`BLOCKED` because it is not a frozen W2A operation, and frame analysis remains
`HELD_NOT_SUPPORTED`.

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

### Remaining W2 ledger

| Gate | Owner machine | Status | Required exit evidence |
|---|---|---|---|
| W2A integration | Mac | Complete | PR #896 merged reviewed head `0972e1af...` as `0f5c918e...` |
| Phase A installed signature audit | Windows | Complete locally; branch checkpoint pending push | Exact ETABS/type-library/comtypes identities, 19 operation verdicts, limitations, and W2C preflight/abort evidence |
| Dev-only `nanoid` advisory | Mac maintenance lane | Open, non-production and separate from W2A | Reviewed lockfile-only or dependency update, frontend tests/lint/build, full npm audit and production-only audit |
| W2B contract and implementation | Windows campaign, then Mac review | Authorized; not started at Phase A checkpoint | Actual observer/orchestration/COM-thread boundary, REST/Excel schemas, error and row limits, deterministic reconciliation, focused checks, quick gate, clean pushed checkpoint |
| W2C evidence plan | Windows campaign | Static plan complete; live identities pending Phase B | Exact approved candidate, copied-model/workbook/output identities, result selections, lock/units/state checks, safe external evidence location |
| W2C installed acceptance | Windows campaign | Authorized only after frozen/pushed Phase B and all preflight gates; not started | Direct/REST/Excel reconciliation, exhaustive rows, pre/post model hash-size-time-lock-units proof, no analysis/save/mutation, tracked safe receipt |
| W2 close decision | Mac | Not started | Review W2A-W2C evidence, document accepted limitations, decide whether W3 may begin; no automatic progression |

W2B design must explicitly resolve these currently held adapter boundaries:

- implement the real read-only Windows model-file observer required by W2A and
  bracket the COM extraction with its observations;
- preserve COM apartment/thread ownership without launching ETABS or selecting
  result cases through setters;
- decide the bounded response/Excel row-volume policy for potentially large
  complete station inventories;
- map blocked dispositions and transport errors without returning a partial
  accepted baseline;
- keep advanced local axes, non-rectangular/unsupported frames, slab/area
  adjacency, and incomplete connected topology visibly excluded or blocked;
- make locked-model state an explicit W2C acceptance requirement rather than
  merely a retained field; and
- reconcile canonical JSON and hashes across direct service, REST, and Excel
  without changing the W2A hash basis.

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

1. Windows pushes the clean Phase A static-audit checkpoint and creates
   `codex/etabs-excel-beam-w2-campaign` from that exact remote head.
2. Windows freezes and implements only the documented W2B observer,
   orchestration, REST, Excel review/reconciliation, error, collision, and row-
   volume boundaries; it runs focused/architecture/docs checks and one quick
   gate, then commits and pushes the clean Phase B checkpoint.
3. Windows revalidates every static preflight identity against that exact Phase
   B head. Only then may it launch/use installed ETABS/Excel for the approved
   copied-model read-only W2C journey.
4. W2C must prove direct/transport/Excel equality, exhaustive topology/result
   accounting, unchanged file/hash/time/lock/units, and every abort boundary.
   Full payloads stay external; only safe hashes and summaries enter Git.
5. Windows freezes final evidence and documentation, runs proportionate final
   gates, commits/pushes the campaign branch, and stops writing it.
6. Mac performs one cumulative branch review and normal PR/check/integration.
   The npm advisory and W3+ remain separate.

## Stop conditions

Stop before mutation and ask for direction if the exact model identity changes,
the open model is not the authorized copy, analysis results are stale/missing,
an ETABS/license/abnormal-condition dialog appears, the requested design basis
changes, or W2 would need setters beyond temporary unit selection.

## New-chat starter

```text
On the Windows evidence machine, verify the pushed Phase A audit branch and
create `codex/etabs-excel-beam-w2-campaign` from its exact remote head. Read the
static audit receipt, this plan, the next-session brief, pilot guide, W2A source,
and Git workflow. Implement only W2B's read-only observer/orchestration,
REST/Excel contracts, reconciliation, collision/error/row limits, and focused
fake-COM coverage; preserve `HELD_NOT_SUPPORTED` and all W1/W2A behavior. Freeze,
validate, commit, and push Phase B. Begin installed W2C only after every static
preflight identity passes against that exact checkpoint and only against the
approved copied model/case/combination. Prove exhaustive row reconciliation and
unchanged model hash/time/lock/units without analysis, design, save, mutation,
optimization, or write-back. Push the final clean campaign branch without a PR,
then stop for one cumulative Mac review.
```
