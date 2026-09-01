---
owner: Main Agent
status: active
last_updated: 2026-09-01
doc_type: spec
complexity: advanced
tags: [etabs, com, vba, api, beams, columns, solver, optimization, w3]
---

# ETABS COM, legacy VBA and W3 reanalysis plan

## Decision

Use ETABS as the global analysis engine and make every live operation target an
explicit process and saved model identity. Reuse the good ideas in the old VBA
workbooks—model-name display, bulk frame reads, design-result checks, exact
case selection, array processing, copy-before-edit and append-only logging—but
do not port their live mutation paths.

The shortest safe route is:

1. repair the existing live bridge so it cannot attach to an arbitrary ETABS
   session or leave units/result selections changed;
2. route the live pilot through the canonical W3 beam audit instead of its
   separate magnitude-only design calculation;
3. make one layer-aware candidate evaluator authoritative for bar, cost and
   Pareto routes;
4. acquire named missing project fields from saved evidence or ETABS 23.3
   SQLite before reopening broad table COM work;
5. permit mutation only in an owned ETABS process that opens a hash-bound copy,
   with typed preflight, per-object readback, analysis verification and discard
   on failure.

Do not extend the local beam-line solver merely to avoid ETABS integration. It
remains a bounded comparison surrogate. Add solver physics only after a W3H
candidate has complete independent inputs and a named unsupported feature is
the sole remaining obstacle.

This plan is a static code, installed-help and legacy-source audit. It did not
attach to ETABS, call COM, open Excel, run analysis/design, export tables, or
change a model. The safe audit receipt is
[here](../verification/etabs-w3-com-vba-plan-audit-evidence.json).

## Ownership boundary and Git isolation

The parallel `LIB-PRO-015` beam capability audit owns the professional public
beam façade, documentation and Sourcebook/StructProof comparison. This plan
does not edit that audit's capability matrix or public beam documentation. It
owns the ETABS host/session adapter, preservation contracts, legacy VBA lessons,
candidate-evaluation convergence and the future W3K/L copied-model transaction.

The work was prepared in the dedicated
`codex/etabs-w3-project-criteria-windows` worktree at `c5357131...`. Future
implementation should use one packet and one writer at a time. If the other
audit changes shared task or handoff files first, refresh Git authority and
integrate its exact head before freezing this candidate; do not switch either
task to the primary checkout.

## What the legacy code proves

### Sources inspected

The audit covered three generations of local source:

- the current `ETABS_Automation.bas` v2.0.1 Excel controller and its staged
  packaging/smoke-test script;
- the separate `project2/Column_Design_Module.bas` column workflow;
- the earlier `COLUMNS.bas`, `BEAM_DESIGN.bas`, `BeamType.bas`,
  `BASE_REACTIONS.bas` and modular ETABS export sources.

Hashes are retained in the audit receipt so later work can detect source drift.
The files remain outside this repository and are evidence, not maintained
library code.

### Patterns to retain

| Legacy pattern | Value to retain | Maintained replacement |
|---|---|---|
| Attach to a running ETABS process and display the current model name | The operator can see which model is active | Enumerate candidate PIDs, attach with `cHelper.GetObjectProcess`, read the full saved path/version/lock/units, and require an exact target contract |
| `FrameObj.GetAllFrames` plus local array filtering | One bulk read avoids thousands of Excel/COM calls | Normalize one inventory snapshot, then classify frames from reviewed section/design metadata |
| `PropFrame.GetTypeRebar` for beam/column filtering | Useful design-orientation signal | Combine it with `FrameObj.GetDesignProcedure`, current section, geometry and caller scope; do not treat it as complete object identity |
| `DesignConcrete.GetResultsAvailable` and beam/column summaries | ETABS design can be compared with the library | Add a read-only design snapshot with exact code, preferences, overwrites, section rebar data, item type and warnings |
| Capture/restore output cases and present units | Prevents a read from changing the user's display state | Put this in a general state guard used by every live adapter |
| Write arrays to Excel in one operation | Good performance and less partial output | Keep bulk normalized results; Excel remains a projection/UI rather than the calculation owner |
| Append-only operation log and formula-safe cell text | Useful trace and workbook safety | Preserve in the UI adapter and bind each row to a typed call/transaction ID |
| Create a new model copy before a section assignment | Correct intent | Create/open the copy in an owned ETABS process; never mutate the attached user session |

### Patterns that must not be ported

| Observed legacy behavior | Root problem | Required control |
|---|---|---|
| `GetObject(...)` accepts whichever instance ETABS exposes | Multiple open sessions are ambiguous | PID-specific target; fail if more than one candidate exists and no exact target resolves it |
| Old column code unlocks the current model and loops over `FrameObj.SetSection` | It mutates the live original with no save/copy identity, readback or rollback | Owned process plus immutable baseline copy, typed change set, old-value check, new-value readback and discard-on-failure |
| Newer VBA copy workflow saves/switches the attached session to a copy | Better than in-place editing, but still disrupts the user's session and has incomplete recovery | Prepare a filesystem copy and open it in a separately owned instance |
| Units are changed without consistent restoration in older beam/column modules | Later API values may be decoded with the wrong units | Capture exact units before every operation and restore in `finally`; verify postflight |
| Output cases/combinations are deselected without restoration in older modules and the current Python pilot | A read changes global display state and can affect later extraction | Snapshot all selected cases/combinations and restore them exactly |
| Analysis is run because the model is unlocked or some case appears incomplete | Lock is not a complete freshness contract; it may run unintended cases | Capture case status and run flags, authorize an exact case set, call `SetRunCaseFlag`, run once and verify every required case status |
| Beam/column type is inferred only from section rebar type | Section metadata can be stale, generic or inconsistent with the object design procedure | Require object ID, label/story, section, design procedure, orientation/type and expected old value |
| Section assignment is treated as a reinforcement update | `SetSection` changes an analysis/design property, not installed bars or final detailing | Keep section mutation, ETABS design results and supplied reinforcement as separate contracts |
| `SafeAPICall` retries by reconnecting | A retry may attach to a different process/model and repeat a side effect | No blind write retry. Reads may retry only after revalidating the same PID and identity; mutations use idempotent transaction stages |
| Late-bound examples suppress errors with `On Error Resume Next` | Return-code and COM-shape failures become partial or stale data | Record raw calls first, then decode strictly and stop at the first failed boundary |
| Workbook build automation temporarily lowers macro security and the VBA is unsigned | It is unsuitable as the maintained mutation authority | Keep workbook generation separate; the typed Python/.NET bridge owns model operations |

## Current library blockers found by this audit

### P0 — live session ambiguity and incomplete preservation

`_ComtypesETABSSession` in `etabs_live_bridge.py` calls
`Helper.GetObject("CSI.ETABS.API.ETABSObject")`. ETABS has supported attachment
to a chosen running process by PID since the v20.2 API enhancement, and the
installed help exposes `cHelper.GetObjectProcess(string typeName, int pid)`.
The current bridge therefore has no reason to remain ambiguous.

`_select_results` deselects all cases/combinations and selects one result, but
the pilot does not capture or restore the predecessor selection. The bridge
already serializes operations with a process lock; the missing control is a
complete state guard, not another lock.

### P0 — the old live pilot bypasses the repaired signed-face route

`_design_beam` sends absolute governing M3, V2 and T to a separate
`design_and_detail` request and does not set `primary_tension_face`. The signed
M3 face repair accepted in PR #940 therefore does not protect this old live
path. Deprecate the separate calculation step and compose:

```text
explicit ETABS target
  -> guarded normalized frame/demand snapshot
  -> canonical BeamDesignInputV1 / W3 audit input
  -> canonical strength, serviceability, supplied-bar and detailing owners
  -> evidence projection
```

Do not duplicate face, cover, material, layer, shear or torsion decisions in
the COM adapter.

### P0 — optimizer feasibility is split across three meanings

`optimize_bar_arrangement`, `optimize_beam_cost` and
`optimize_pareto_front` do not evaluate the same candidate. The bar optimizer
can return a multi-layer recommendation while explicitly leaving exact
layer-by-layer distribution, vertical spacing and effective-depth identity to
the caller. The cost and Pareto routes separately calculate flexure/shear and
omit different quantities and checks. This can make the same section feasible
in one API and unavailable in another.

One `evaluate_beam_candidate_v2` must own engineering feasibility. Optimizers
may generate candidates and objectives, but they must call the same evaluator
before ranking. A preliminary recommendation remains labelled as such until an
explicit `LongitudinalBarLayersV1` arrangement passes centroid, horizontal and
vertical spacing, strength, serviceability, torsion/detailing and applicability
checks.

### P1 — ETABS design comparison lacks its calculation basis

The old VBA reads beam/column summary results but does not freeze the ETABS
design code, code preferences, member overwrites, design procedure or section
rebar definition. A numerical area comparison without those fields can diagnose
a difference but cannot establish a like-for-like calculation.

Add a read-only snapshot using installed interfaces including:

- `DesignConcrete.GetResultsAvailable` and `GetCode`;
- `FrameObj.GetDesignProcedure`;
- `DesignConcrete.Indian_IS_456_2000.GetPreference` and `GetOverwrite`;
- `PropFrame.GetRebarBeam` for beam reinforcement metadata;
- `DesignConcrete.GetSummaryResultsBeam` and the corresponding column summary
  only when the object procedure and code are in scope.

Retain raw ETABS values, normalized values, units, item type, warnings and the
exact call signature separately.

### P1 — named missing data should use the simplest available source

The prior W3H broad display-table COM route is closed for this model/host after
the correct call still returned CSI 1. ETABS 23.3 adds SQLite table export. For
mesh, support, slab-transfer or design fields that cannot be obtained from the
accepted saved sources or proved object getters, assess one named SQLite export
containing only the necessary tables. Parse it offline and bind schema/table
versions and file hash. Do not reopen generic table-catalogue experiments.

### P2 — copied-model mutation is not yet a transaction

The current library has no W3K owner that binds target objects, expected old
properties, copied-model identity, authorized cases, readback, fresh result
identity, global safeguards and recovery. The legacy section update demonstrates
the useful operation, but also the exact failure mode to avoid.

## Required contracts

### Connection and state

| Contract | Required fields |
|---|---|
| `ETABSProcessCandidateV1` | PID, executable path/version, process start time, architecture and discovery source |
| `ETABSConnectionTargetV2` | exact PID; expected ETABS major/build; expected saved model path, SHA-256, size and UTC mtime; allowed access `READ_ONLY` or `OWNED_COPY_MUTATION` |
| `ETABSSessionIdentityV1` | PID, connection origin (`ATTACHED_EXISTING` or `STARTED_OWNED`), full model path/name, version, units, lock, saved-file identity and observation time |
| `ETABSStateSnapshotV1` | session identity, units, lock, selected output cases/combinations, case statuses, run flags and named table/display selections used by the operation |
| `ETABSCallRecordV1` | transaction/call ID, method, reviewed signature ID, redacted arguments, raw return projection, return code, start/end time, decoder version and error |

An attached session is read-only. Only a process started and tracked by the
library may receive model-changing calls, and the library may exit only that
owned process. Detach from an existing session without calling
`ApplicationExit`.

### Candidate and mutation

| Contract | Required fields |
|---|---|
| `BeamCandidateDefinitionV2` | section/materials, signed row-bound actions, exact supplied bar layers, transverse reinforcement, service scenarios, constructability/applicability limits and objective inputs |
| `BeamCandidateEvaluationV2` | all mandatory check results, governing rows/clauses, quantities/cost scope, explicit holds and deterministic feasibility |
| `ETABSObjectChangeV1` | object kind, unique ID plus label/story, property, expected old value, proposed value, design procedure/type and readback rule |
| `ETABSChangeSetV1` | baseline/copy identities, ordered object changes, authorized cases, required safeguards, abort policy and digest |
| `ETABSAnalysisTransactionV1` | owned PID, stage ledger, pre/post state, call records, analysis/design statuses, fresh result identity, safeguard comparison and final disposition |

The first supported mutation may be `FRAME_SECTION_ASSIGNMENT` for verified
beam and column frame objects. It must call `FrameObj.GetSection` before,
validate `FrameObj.GetDesignProcedure` plus section rebar type, call
`FrameObj.SetSection` once, then read `GetSection` back. Area, point, link,
release, modifier, load and section-definition changes stay unsupported until
they receive separate typed operations and safeguards.

## Required functions and changes

### P0 host and adapter functions

1. `discover_etabs_processes_v1()` — list candidate ETABS processes without
   COM side effects.
2. `probe_etabs_session_identity_v1(pid)` — attach with `GetObjectProcess` and
   return the visible model name plus full identity; no model mutation.
3. `list_running_etabs_sessions_v1()` — return deterministic PID-ordered
   candidates for the UI.
4. `connect_etabs_target_v2(target)` — resolve exactly one PID/model and reject
   ambiguity or drift.
5. `capture_etabs_state_v1(session, operation_scope)` and
   `restore_etabs_state_v1(...)` — implement the state guard and postflight.
6. `record_etabs_call_v1(...)` — persist the raw call projection before strict
   decoding can raise.
7. `read_etabs_demand_snapshot_v2(...)` — return signed row-bound forces and
   exact selection identity without running design calculations.
8. Deprecate `run_etabs_beam_pilot_v1` calculation ownership; keep a compatible
   adapter that calls the canonical audit and returns explicit deprecation and
   limitations metadata.

### P0 candidate evaluation functions

1. Add `evaluate_beam_candidate_v2(candidate, project_criteria)` as the single
   strength, layer, serviceability, torsion, detailing, quantity and
   applicability verdict.
2. Add `generate_bar_layer_candidates_v2(...)` that returns exact
   `LongitudinalBarLayersV1` arrangements rather than a count plus layer number.
3. Refactor `optimize_bar_arrangement`, `optimize_beam_cost` and
   `optimize_pareto_front` to generate options, call the common evaluator and
   rank only accepted candidates.
4. Preserve predecessor signatures through adapters, but make every omitted
   mandatory check visible in `limitations` and prevent ETABS candidate
   screening until the W3E/H/I criteria gate passes.
5. Use one quantity/cost basis that declares longitudinal steel, transverse
   steel, side-face steel, concrete, formwork, laps/anchorage and exclusions.

### P1 ETABS evidence functions

1. `read_etabs_concrete_design_snapshot_v1(...)` — code, result availability,
   object procedure, preferences/overwrites, section rebar definition and beam
   or column summaries.
2. `import_etabs_sqlite_snapshot_v1(path, requested_tables)` — offline,
   schema-bound and allowlisted; no generic import of every table.
3. `compare_library_to_etabs_design_v1(...)` — diagnostic comparison with
   matched basis and reasons, never an automatic approval.
4. Publish one maintained ETABS API guide from the installed CHM rather than
   scattering signatures through plans and issue logs.

### P2 W3K/L transaction functions

1. `prepare_etabs_candidate_copy_v1(...)` — verify a clean saved baseline,
   create a new non-existing copy and bind its initial identity.
2. `start_owned_etabs_session_v1(copy_path)` — launch and record the owned PID,
   open only the copy and verify it before any setter.
3. `apply_etabs_change_set_v1(...)` — ordered, one-shot setters with expected
   old values and readback after every call.
4. `run_etabs_analysis_transaction_v1(...)` — set only approved run flags, run
   once, collect statuses/log identity and preserve the call ledger.
5. `verify_etabs_candidate_v1(...)` — compare affected beams, columns, joints,
   reactions, displacements/drifts and all predeclared global safeguards.
6. `finalize_or_discard_etabs_candidate_v1(...)` — retain a passing evidence
   copy or close the owned process and discard/quarantine the failed copy. Never
   overwrite the baseline.

## Maintained ETABS API guide

Create `docs/guides/etabs-api-integration.md` during the P0 implementation. It
must be versioned to the installed CHM hash and cover:

1. supported ETABS/API version and how signatures are refreshed;
2. process discovery, `GetObjectProcess`, active-instance behavior and model
   identity display;
3. attached versus owned process lifecycle;
4. COM apartment/thread serialization and supported early/late binding shapes;
5. raw return values, integer return codes, by-reference arrays, singleton/null
   shapes and strict decoding;
6. units and sign conventions;
7. object, element, label/story, station and item-type identities;
8. result case/combo selection capture and restore;
9. analysis case status/run flags and freshness;
10. table catalogue/schema/row APIs and the preferred SQLite route;
11. concrete design code, preferences, overwrites and summary-result basis;
12. safe read-only calls, copy-only setters, forbidden calls and the error
    register;
13. exact examples backed by fake adapters, plus separately authorized installed
    acceptance evidence.

The installed CHM is authoritative for signatures. Older CSI web pages are
conceptual references only. CSI's current enhancements page confirms both
PID attachment and ETABS 23.3 SQLite export.

## Solver decision

The current beam-line solver is useful only when loads, supports, member
properties, releases and comparison components are independently specified.
The saved W3 candidates still lack an accepted support/mesh/slab-transfer basis,
so adding more equations now would not make them comparable.

Use this decision rule:

| Need | First route | Do not do |
|---|---|---|
| Global response after section changes | Owned copied-model ETABS analysis | Claim the 2D solver represents the building |
| Independent check of a supported beam line | Existing pure solver and comparator | Fit supports or loads to ETABS results after seeing the answer |
| One named unsupported physical feature with complete inputs | Cost and specify a bounded solver extension | Start a general 3D frame/slab solver inside W3 |
| Missing mesh/support/slab input | Saved source, proved getter, then named SQLite table | Add solver complexity to compensate for missing data |

A future solver extension needs an immutable input contract, independent
references, convergence and equilibrium checks, declared applicability and a
new calibration packet. It does not belong in the P0 COM repair.

## Execution packets and exits

| Packet | Work | Exit | Planning effort |
|---|---|---|---:|
| A — P0 session target and guard | PID discovery/selection, identity, raw call ledger, units/selections postflight | Multiple-instance fake tests; exact target or fail; pre/post state equal after success and every injected failure | 3–5 focused days |
| B — canonical pilot/evaluator convergence | Remove pilot calculation ownership; exact signed face; common layer-aware candidate evaluator used by three optimizers | Same candidate has one feasibility verdict across direct, cost and Pareto routes; predecessor adapters remain deterministic | 5–9 focused days |
| C — design and named data snapshot | Concrete design basis plus allowlisted SQLite importer | Matched-basis comparison available; every requested table closes a named W3 row or is rejected | 3–6 focused days plus one installed read/export packet |
| D — W3H project decision | Resolve or retain support/mesh/slab-transfer and applicability criteria | Explicit comparable scope, bounded extension decision, or `NOT_COMPARABLE` with no further generic acquisition | 2–5 focused days if evidence exists |
| E — W3I screening | Candidate families, scenarios, objectives and all mandatory checks | Deterministic `SCREENED_ONLY` shortlist with no hidden mandatory check | 5–10 focused days |
| F — W3K owned-copy transaction | Change set, owned ETABS process, analysis, safeguards and recovery | Rehearsed failure injection plus one separately authorized installed copy; original process/file unchanged | 8–15 focused days plus ETABS run/review time |
| G — W3L bounded iteration | Finite budget, cache keys, final clean-baseline repeat and dossier | Budgeted termination and independently repeated final candidate or explicit no-solution outcome | 4–8 focused days plus candidate cycles |

These are engineering planning ranges, not delivery promises. Project evidence,
ETABS runtime and independent review dominate the calendar. Packet A should be
done before any new live pilot. Packets B and the offline parts of C can proceed
without opening ETABS. D must stop if the necessary project basis does not
exist; repeated table or solver work is not the default response.

## Acceptance and recurrence controls

- No API function may attach to “the running ETABS” without a target PID or an
  exact unique identity rule.
- If more than one process exists, the UI shows PID, version and model name; the
  operation remains blocked until one exact target is chosen.
- A read-only operation proves units, lock, output selections and saved-model
  identity unchanged after both success and injected failure.
- Raw call evidence is written before decoding. A decoder failure must still
  retain method, arguments, raw shape and return code.
- No setter, save, unlock, analysis or design run is permitted in an attached
  user session.
- Each mutation names one object kind, expected old value and readback rule.
  Unknown or already-changed objects fail before the first setter.
- A failed copied-model transaction is never retried blindly. Record the failed
  stage, close only the owned process, and discard or quarantine the copy.
- `SetSection` does not claim installed reinforcement. Library bar layers and
  ETABS section/design metadata remain distinct evidence.
- Every optimizer ranks only candidates accepted by the same evaluator; an
  omitted mandatory check is a hold, not a pass.
- Use saved evidence and direct getters first. Use one named SQLite export next.
  Do not repeat the broad table COM route without a new vendor-supported cause
  and a required field that has no simpler source.
- Do not change the local solver merely because ETABS acquisition is difficult.
  Missing evidence remains missing evidence.
- Installed acceptance gets its own exact-authority packet. This plan does not
  authorize ETABS, Excel, UI, export or model calls.

## Sources

- Installed `docs/reference/CSI API ETABS v1.chm`, SHA-256
  `a730756ccd283ffc17f592a2e21c973d50b5a14ed3489244fca1524e58f3a700`.
- [CSI ETABS enhancements](https://www.csiamerica.com/products/etabs/enhancements):
  PID-specific attachment and ETABS 23.3 SQLite table export.
- [CSI OAPI FAQ](https://web.wiki.csiamerica.com/wiki/spaces/kb/pages/2000456/OAPI%2BFAQ):
  installed API help is the maintained signature source.
- [CSI Choose Tables](https://docs.csiamerica.com/help-files/etabs/Keyboard_Commands_and_Special_Features/Choose_Tables_form.htm):
  table availability and selection are model/display-state dependent.
- The legacy source identities and reviewed current-code locations are recorded
  in the safe audit receipt linked above.
