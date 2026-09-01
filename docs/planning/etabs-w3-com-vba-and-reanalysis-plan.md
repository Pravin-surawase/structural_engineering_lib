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

1. close the currently mounted live-route boundary first: disabled by default,
   loopback-only, authenticated before HTTP/WebSocket acceptance and rejected
   before any COM import or attachment;
2. repair the existing live bridge so it cannot attach to an arbitrary ETABS
   session, expose live COM beyond a bounded local operator capability, overlap
   another bridge process, hang the host indefinitely or change an attached
   user's units/result selections;
3. route the live pilot through the canonical W3 beam audit instead of its
   separate magnitude-only design calculation;
4. freeze one project criteria/candidate catalogue and make one layer-aware
   evaluator authoritative for bar, cost and Pareto routes;
5. acquire named missing project fields from saved evidence or ETABS 23.3
   SQLite before reopening broad table COM work;
6. choose a proved surrogate envelope or an ETABS-first route for the actual
   building; then permit mutation only in an owned ETABS process that opens a
   hash-bound copy, with getter-only dry run, durable recovery stages,
   per-object readback, fresh result epoch and discard on failure.

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

The initial audit was prepared in the dedicated
`codex/etabs-w3-project-criteria-windows` worktree at `c5357131...`; PR #941
merged its plan and PR #942 integrated it at `35ea6b89...`. Future
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
| Capture/restore output cases and present units | Identifies global state that legacy reads could disturb | Attached observation is getter-only and normalizes from observed units; capture/compare without setters. Owned operations use the complete state guard and verified restoration. |
| Write arrays to Excel in one operation | Good performance and less partial output | Keep bulk normalized results; Excel remains a projection/UI rather than the calculation owner |
| Append-only operation log and formula-safe cell text | Useful trace and workbook safety | Preserve in the UI adapter and bind each row to a typed call/transaction ID |
| Create a new model copy before a section assignment | Correct intent | Create/open the copy in an owned ETABS process; never mutate the attached user session |

### Patterns that must not be ported

| Observed legacy behavior | Root problem | Required control |
|---|---|---|
| `GetObject(...)` accepts whichever instance ETABS exposes | Multiple open sessions are ambiguous | PID-specific target; fail if more than one candidate exists and no exact target resolves it |
| Old column code unlocks the current model and loops over `FrameObj.SetSection` | It mutates the live original with no save/copy identity, readback or rollback | Owned process plus immutable baseline copy, typed change set, old-value check, new-value readback and discard-on-failure |
| Newer VBA copy workflow saves/switches the attached session to a copy | Better than in-place editing, but still disrupts the user's session and has incomplete recovery | Prepare a filesystem copy and open it in a separately owned instance |
| Units are changed without consistent restoration in older beam/column modules | Later API values may be decoded with the wrong units | Never call `SetPresentUnits` in an attached session. Capture the enumeration and normalize offline. Only an owned process may change/restore units. |
| Output cases/combinations are deselected without restoration in older modules and the current Python pilot | A read changes global display state and can affect later extraction | Attached observation uses getters only and holds when the required selection is not already active. Owned transactions snapshot and restore exact selections. |
| Analysis is run because the model is unlocked or some case appears incomplete | Lock is not a complete freshness contract; it may run unintended cases | Capture case status and run flags, authorize an exact case set, call `SetRunCaseFlag`, run once and verify every required case status |
| Beam/column type is inferred only from section rebar type | Section metadata can be stale, generic or inconsistent with the object design procedure | Require object ID, label/story, section, design procedure, orientation/type and expected old value |
| Section assignment is treated as a reinforcement update | `SetSection` changes an analysis/design property, not installed bars or final detailing | Keep section mutation, ETABS design results and supplied reinforcement as separate contracts |
| `SafeAPICall` retries by reconnecting | A retry may attach to a different process/model and repeat a side effect | No blind write retry. Reads may retry only after revalidating the same PID and identity; mutations use idempotent transaction stages |
| Late-bound examples suppress errors with `On Error Resume Next` | Return-code and COM-shape failures become partial or stale data | Record raw calls first, then decode strictly and stop at the first failed boundary |
| Workbook build automation temporarily lowers macro security and the VBA is unsigned | It is unsuitable as the maintained mutation authority | Keep workbook generation separate; the typed Python/.NET bridge owns model operations |

## Current library blockers found by this audit

### P0 — live session ambiguity, exposure and process-local execution

`_ComtypesETABSSession` in `etabs_live_bridge.py` calls
`Helper.GetObject("CSI.ETABS.API.ETABSObject")`. ETABS has supported attachment
to a chosen running process by PID since the v20.2 API enhancement, and the
installed help exposes `cHelper.GetObjectProcess(string typeName, int pid)`.
The current bridge therefore has no reason to remain ambiguous.

`_select_results` deselects all cases/combinations and selects one result, but
the pilot does not capture or restore the predecessor selection. The bridge
serializes threads with one Python `Lock`, but another Uvicorn worker, CLI or
Excel-launched bridge can still enter the same ETABS PID. A stalled COM call can
hold that lock indefinitely. The shared API also describes these routes as
localhost while maintained launch examples bind `0.0.0.0` and development auth
defaults off.

Attached observation must be strictly getter-only, including no temporary unit
or output-selection setters. Add a measured process/runtime identity, an
OS-wide lease keyed by PID plus start time, a supervised dedicated STA broker,
bounded deadline/heartbeat, fenced timeout recovery and a short-lived live-route
capability. Keep live routes disabled by default and refuse non-loopback binds.
Global JWT/CORS configuration is not ETABS operation authorization.

### P0 — disk identity is not live-session freshness

The proposed exact target binds saved path, SHA-256, size and UTC mtime, but an
already-open ETABS process may contain unsaved in-memory changes. A disk hash
therefore proves only the persisted file, not equality with the live session.
The host adapter must expose a separate `ETABSModelFreshnessV1` disposition:
`SAVED_CLEAN_CONFIRMED`, `SESSION_UNSAVED_OR_UNKNOWN`, `FILE_DRIFT` or
`FILE_UNAVAILABLE`. Every attached session defaults to
`SESSION_UNSAVED_OR_UNKNOWN`. `SAVED_CLEAN_CONFIRMED` requires separately
reviewed installed evidence from either an API cleanliness signal or an explicit
operator-saved checkpoint bound to PID, path, hash, mtime and observation timing,
with no intervening edit. Unknown session freshness may support a bounded
read-only observation with explicit limitations, but it cannot become hash-bound
baseline or copied-model evidence. The adapter must never save the attached user
session to manufacture this proof.

### P0 — result freshness is separate from model freshness

A clean file, locked model, `FINISHED` status or `GetResultsAvailable` value
does not prove forces/design summaries were produced from the current change
set. Add `ETABSResultEpochV1` binding uninterrupted process/runtime, copy/change
set, authorized case dependency closure and run flags, pre/post status, exact
analysis/design calls, selection, row/result digest and comparison basis. A
reconnect, broker timeout/restart or unexpected status cannot create a fresh
epoch and must return no accepted candidate evidence.

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

The common evaluator also needs one declared-before-generation
`ProjectBeamCriteriaV1` and `ProjectBeamCandidateCatalogueV1`. They bind the
complete action/service/applicability domain, sensitivity scenarios,
constructability/objectives, permitted materials/bar stock, cost basis and
verified existing ETABS beam properties. Every candidate/evaluation/cache/
shortlist/reanalysis receipt verifies both digests. Effective depth is derived
from the selected serialized layers and strength is rerun.

Finite search is not necessarily complete search. The current Pareto route can
stop after the first bounded feasible entries in traversal order. Add explicit
domain/traversal/pruning/tie-break/count evidence. Only complete enumeration or
proved-safe pruning may claim optimality/Pareto completeness; budget exhaustion
returns a provisional incomplete shortlist. The first W3K route accepts only an
existing verified beam property. New section definitions and column mutations
remain separate held engineering/mutation programmes; columns and joints are
whole-model safeguards in beam W3.

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

Also bind the exact design-combination set, resolved concrete/longitudinal/
transverse material properties, resolved assigned section and auto-select state,
explicit-versus-default overwrite semantics and `ETABSResultEpochV1`. Retain raw
ETABS values, normalized values, units, item type, warnings and the exact call
signature separately.

### P1 — named missing data should use the simplest available source

The prior W3H broad display-table COM route is closed for this model/host after
the correct call still returned CSI 1. ETABS 23.3 adds SQLite table export. For
mesh, support, slab-transfer or design fields that cannot be obtained from the
accepted saved sources or proved object getters, assess one named SQLite export
containing only the necessary tables. Parse it offline and bind schema/table
versions and file hash. Separate the installed export manifest from the offline
parser and label the acquisition `OPERATOR_UI_EXPORT` unless an exact installed
OAPI method is proved. Parse only a completed frozen copy with no pending WAL;
open `mode=ro`/private cache, run an integrity check and enforce schema/field/row
bounds. Do not reopen generic table-catalogue experiments.

### P1 — copied-model mutation is not yet a recoverable transaction

The current library has no W3K owner that binds target objects, expected old
properties, copied-model identity, authorized cases, readback, fresh result
epoch, global safeguards and restart recovery. The legacy section update
demonstrates the useful operation, but also the exact failure mode to avoid.
Persist each next stage before a non-idempotent call; restart may verify or
quarantine but never replay a setter, analysis, design, save or exit call.

## Required contracts

### Connection and state

| Contract | Required fields |
|---|---|
| `ETABSLiveRoutePolicyV1` | disabled-by-default registration, loopback bind, HTTP/WebSocket authentication, offline/live-read/live-mutation classification, scope, mutation enablement and denial reason; request data cannot grant authority |
| `ETABSProcessInstanceV1` | PID, process start time, canonical executable path, executable file version/hash, architecture, discovery/observation time and instance digest |
| `ETABSRuntimeFingerprintV1` | bridge/library, Python executable/version/architecture, `comtypes` and COM-shape runtime, ETABS executable, registered ETABSv1 type library, generated wrapper/managed assembly where used and installed CHM identities |
| `ETABSTargetObservationV1` | observation ID/expiry, exact process instance, expected model intent, observed full model/session identity, runtime fingerprint, freshness and allowed access `ATTACHED_OBSERVE` or `OWNED_COPY_MUTATION` |
| `ETABSSessionIdentityV1` | process instance, connection origin (`ATTACHED_EXISTING` or `STARTED_OWNED`), full model path/name, version, units, lock, saved-file identity and observation time |
| `ETABSModelFreshnessV1` | session/file disposition, saved path identity, before/after file stat/hash evidence where available, observation source, limitations and whether hash-bound baseline use is allowed |
| `ETABSOperationLeaseV1` | transaction, process-instance and OS named-mutex/lease identities, supervisor/worker process, acquired/expiry/heartbeat and release/fence disposition |
| `ETABSStateSnapshotV1` | session identity, units, lock, selected output cases/combinations, case statuses, run flags and named table/display selections used by the operation |
| `ETABSCallRecordV1` | transaction/call/monotonic-sequence ID, previous-record hash, `STARTED`/`RETURNED` stage, method, reviewed signature, redacted arguments, bounded raw projection/shape, return code, start/end time, durable-flush evidence, decoder, error and record hash |
| `ETABSEvidenceBundleV1` | transaction, finalized disposition, call-ledger head/count, target/runtime/model/result identities, artifact paths/hashes, safe-projection policy, retention and atomic-manifest hash |
| `ETABSOperationOutcomeV1` | primary/restoration/broker/deadline outcomes, pre/post state, call-ledger identity and `COMPLETED`, `BLOCKED`, `RESTORATION_UNVERIFIED` or `TRANSACTION_UNCERTAIN` disposition |
| `ETABSResultEpochV1` | model/copy/change-set/runtime/process/transaction identities, uninterrupted-session evidence, authorized cases/dependency closure/run flags, pre/post statuses, analysis/design calls, selection/result digest and design-basis digest where claimed |

An attached session is getter-only: no unit/output/run-flag setter, unlock,
save, analysis/design, mutation or exit. Normalize from observed units and hold
when required outputs are not already available/selected. Only a process started
and tracked by the library may receive model-changing calls, and the library may
exit only that exact PID plus process-start-time owned instance.

### Candidate and mutation

| Contract | Required fields |
|---|---|
| `ProjectBeamCriteriaV1` | code/source/review identities, complete strength/service action/scenario domain, face/action applicability, exclusions, mandatory checks, constructability/sensitivity/objectives/tie-break/stop policy, declaration chronology and digest |
| `ProjectBeamCandidateCatalogueV1` | permitted existing ETABS beam-property IDs/digests, resolved geometry/material/modifier/rebar type, longitudinal/transverse stock and revisions, cost basis/exclusions and digest |
| `BeamMemberReinforcementScheduleV1` | exact TOP/BOTTOM longitudinal layers and revision plus transverse-zone intervals; first scope full-span, single-layer and no mixed/curtailed bars |
| `BeamCandidateDefinitionV2` | section/materials, signed row-bound actions, exact supplied schedule, derived layer-centroid depth, service scenarios, applicability/objectives and criteria/catalogue/property identities |
| `BeamCandidateEvaluationV2` | all mandatory check results, governing rows/clauses, quantities/cost scope, explicit holds and deterministic feasibility |
| `OptimizationSearchBudgetV1` | canonical domain/traversal/pruning/tie-break identities, generated/pruned/evaluated/accepted/ranked counts, finite budget and complete/incomplete terminal status |
| `ETABSObjectIdentityV1` | source unique name, label/story, endpoints/geometry, resolved section/auto-select state, design procedure/type, proved GUID when available and digest |
| `ETABSObjectChangeV1` | exact object identity, property, expected old value, proposed verified existing beam property and readback rule |
| `ETABSChangeSetV1` | baseline/copy/object-set/criteria/catalogue identities, ordered changes, authorized cases/dependencies, safeguards, abort/recovery policy and dry-run digest |
| `ETABSCopyIdentityV1` | immutable baseline identity, create-new local destination, post-copy/open identity, owned process instance, original pre/post identity and disposition |
| `ETABSTransactionJournalV1` | durable transaction stages, next intended stage persisted before call, call records, restart observation and no-replay recovery disposition |
| `ETABSAnalysisTransactionV1` | owned process instance, journal, pre/post state, call records, result epoch, safeguard comparison and final disposition |
| `ETABSSQLiteExportManifestV1` | acquisition mode, target/runtime/model/result epoch, requested table/fields/filter state, create-new destination, completion, byte/hash and pre/post state |

The first supported mutation is `FRAME_SECTION_ASSIGNMENT` for verified beam
objects to verified existing properties. It must call `FrameObj.GetSection` before,
validate `FrameObj.GetDesignProcedure` plus section rebar type, call
`FrameObj.SetSection` once, then read `GetSection` back. Area, point, link,
release, modifier, load, section-definition and column changes stay unsupported
until they receive separate candidate engineering, typed operations and
safeguards. Columns/joints remain whole-model read-only safeguards in beam W3.

## Required functions and changes

### P0 host and adapter functions

1. `enforce_etabs_live_route_policy_v1(...)` — reject disabled, remote,
   unauthenticated or wrong-scope HTTP/WebSocket traffic before importing or
   constructing any COM/session object; `/status` stays nonattaching.
2. `discover_etabs_processes_v1()` — list `ETABSProcessInstanceV1` values
   without COM side effects.
3. `build_etabs_runtime_fingerprint_v1()` — measure the installed/runtime
   identities instead of accepting a caller-projected hash.
4. `observe_etabs_target_v1(process_instance, expected_intent)` — attach with
   `GetObjectProcess`, return one expiring target observation and invoke no
   model/session setter.
5. `list_running_etabs_sessions_v1()` — return deterministic PID/start-ordered
   candidates for the UI.
6. `verify_etabs_target_observation_v1(observation)` — remeasure process,
   runtime and model immediately before/after every live operation.
7. `classify_etabs_model_freshness_v1(session, expected_file)` — distinguish
   persisted-file identity from live in-memory freshness and block baseline use
   when the session is unsaved or unknown.
8. `acquire_etabs_operation_lease_v1(process_instance, transaction_id)` and
   `run_etabs_sta_broker_v1(operation, deadline, lease)` — provide OS-wide
   serialization, dedicated-apartment execution and bounded hang recovery.
9. `issue_etabs_bridge_capability_v1(...)` — create one expiring target/access/
   transaction-bound live-route capability; mutation capability remains separate.
10. `capture_etabs_state_v1(session, operation_scope)` and
   `compare_or_restore_etabs_state_v1(...)` — attached paths compare only;
   owned paths restore declared state and verify postflight.
11. `record_etabs_call_v1(...)` — append and durably flush hash-chained
    `STARTED`, then raw `RETURNED`, before strict decoding can raise.
12. `finalize_etabs_evidence_bundle_v1(...)` and
    `verify_etabs_evidence_bundle_v1(...)` — atomically finalize or reject gaps,
    truncation, hash mismatch, missing artifacts and unfinalized transactions.
13. `build_etabs_result_epoch_v1(...)` — bind fresh analysis/design results to
   the exact uninterrupted owned transaction or return `BLOCKED`.
14. `read_etabs_demand_snapshot_v2(...)` — return signed row-bound forces and
   exact selection/result-epoch identity without running calculations in an
   attached session.
15. Deprecate `run_etabs_beam_pilot_v1` calculation ownership; keep a compatible
   adapter that calls the canonical audit and returns explicit deprecation and
   limitations metadata.

### P0 candidate evaluation functions

1. Add strict canonical builders for `ProjectBeamCriteriaV1`,
   `ProjectBeamCandidateCatalogueV1` and `BeamMemberReinforcementScheduleV1`.
2. Add `evaluate_beam_candidate_v2(candidate, project_criteria, catalogue)` as the single
   strength, layer, serviceability, torsion, detailing, quantity and
   applicability verdict.
3. Add `generate_bar_layer_candidates_v2(...)` that returns exact
   `LongitudinalBarLayersV1` arrangements rather than a count plus layer number.
4. Refactor `optimize_bar_arrangement`, `optimize_beam_cost` and
   `optimize_pareto_front` to generate options, call the common evaluator and
   rank only accepted candidates.
5. Add `verify_beam_candidate_composition_v1(...)` as an independent checker
   for serialized layers/depth/spacing/quantities/cost/face mapping.
6. Preserve predecessor signatures through adapters, but make every omitted
   mandatory check visible in `limitations` and prevent ETABS candidate
   screening until the W3E/H/I criteria gate passes.
7. Use one quantity/cost basis that declares longitudinal steel, transverse
   steel, side-face steel, concrete, formwork, laps/anchorage and exclusions.
8. Report complete-domain/traversal/pruning/count/tie-break evidence; an
   incomplete budget cannot claim an optimum, Pareto front or infeasibility.

### P1 ETABS evidence functions

1. `read_etabs_concrete_design_snapshot_v1(...)` — complete matched basis,
   result epoch, object procedure, resolved section/auto-select/materials,
   preferences/overwrites and beam or column summaries.
2. `parse_etabs_sqlite_export_v1(path, manifest, requested_tables)` — offline,
   read-only, integrity/schema-bound and allowlisted; it never imports into
   ETABS and never accepts a changing/pending-WAL source.
3. `compare_library_to_etabs_design_v1(...)` — diagnostic comparison with
   matched basis and reasons, never an automatic approval.
4. Publish one maintained ETABS API guide from the installed CHM rather than
   scattering signatures through plans and issue logs.

### P1 W3K/L transaction functions

1. `plan_etabs_change_set_v1(...)` — getter-only object/property/auto-select
   diff and digest; first scope existing beam properties only.
2. `prepare_etabs_candidate_copy_v1(...)` — verify a clean saved baseline,
   create a new non-existing copy and bind its initial identity.
3. `start_owned_etabs_session_v1(copy_path)` — launch and record the owned
   process instance,
   open only the copy and verify it before any setter.
4. `apply_etabs_change_set_v1(...)` — ordered, one-shot setters with expected
   old values and readback after every call.
5. `run_etabs_analysis_transaction_v1(...)` — persist stage, set the complete
   approved case dependency closure, run once and build a fresh result epoch.
6. `recover_etabs_transaction_v1(transaction_id)` — verify an already completed
   stage or quarantine/close the exact owned process/copy without replay.
7. `verify_etabs_candidate_v1(...)` — compare affected beams, columns, joints,
   reactions, displacements/drifts and all predeclared global safeguards.
8. `finalize_or_discard_etabs_candidate_v1(...)` — retain a passing evidence
   copy or close the owned process and discard/quarantine the failed copy. Never
   overwrite the baseline.

## Maintained ETABS API guide

Create `docs/guides/etabs-api-integration.md` during the P0 implementation. It
must be versioned to the installed CHM hash and cover:

1. supported ETABS/API version and how signatures are refreshed;
2. process discovery, PID/start-time reuse protection, `GetObjectProcess`,
   target-observation expiry and model identity display;
3. getter-only attached versus owned lifecycle and live-route capability;
4. measured runtime fingerprint, OS lease, supervised STA broker, message-pump/
   deadline/cancellation limits and supported early/late binding shapes;
5. raw return values, integer return codes, by-reference arrays, singleton/null
   shapes and strict decoding;
6. units and sign conventions;
7. object, element, label/story, station and item-type identities;
8. attached capture/compare and offline unit conversion; owned-only selection/
   unit restoration;
9. analysis case dependency closure, status/run flags and result epoch;
10. table catalogue/schema/row APIs, explicit UI/API acquisition mode and the
    read-only SQLite-export route;
11. concrete design combinations, resolved section/auto-select/material basis,
    preferences, overwrites and summary-result epoch;
12. safe getters, copy-only setters, forbidden calls, live-route security and
    the error/recovery register;
13. exact examples backed by fake adapters, lease contention/hang/crash
    injection, plus separately authorized installed
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

Before W3I, `W3-H0-ROUTE-DECISION` must select `SURROGATE_ASSISTED`,
`ETABS_FIRST` or terminal `HOLD`. The surrogate route needs an applicability
envelope covering the complete candidate E/I, load/support/slab and scenario
domain. The ETABS-first route may screen only criteria-complete proposals mapped
to verified existing beam properties and treats clean-copy ETABS reanalysis as
changed-model authority. Baseline calibration alone never validates the changed
candidate range. No new solver physics is scheduled by this plan.

## Execution packets and exits

| Packet | Work | Exit | Planning effort |
|---|---|---|---:|
| G0 — offline live-route gate | Disabled-by-default router, loopback startup, HTTP/WebSocket auth and operation classification | Denied paths prove zero COM import/session construction/attachment; missing WebSocket token rejected before accept | 1–2 focused days |
| A0 — offline runtime/session guard | Process/target/runtime identity, live-route capability, OS lease, supervised STA broker, getter-only attached policy, model/result freshness and call journal through fakes | PID reuse/runtime drift/second process/hung call fail; attached path has zero setters; timeout fences reuse; no COM call | 8–12 focused days |
| A1 — installed getter-only acceptance | Exact target/runtime observation on the Windows/ETABS authority | Selected process/model/runtime is exact; no setter; state/file equal; freshness is not overpromoted | one bounded evidence session after separate authorization |
| B1A/B1B/B2 — criteria/evaluator/search convergence | Canonical criteria/catalogue/schedule, one layer-aware evaluator, independent composition check and complete-search semantics | Same identities produce one hash/verdict across direct/cost/Pareto; incomplete search is provisional; actual project criteria may remain held | 13–23 focused days |
| C0 — offline acquisition contracts | Matched-design/export manifest, generic bounded fixture and scaffolding with no ETABS schema-support claim | Contract/limits are deterministic; zero ETABS/UI call | 2–4 focused days |
| C1 — installed design/export inventory | Target/runtime/epoch-bound design basis, create-new export and actual table/column/type/key inventory | Complete hash-bound artifact; every requested field/table closes a named row or is rejected | 3–5 focused days plus one installed read/export packet |
| C2 — offline exact-schema parser/comparison | Implement allowlisted parser and diagnostic comparison against C1's accepted schema | Integrity/schema/row bounds and canonical evidence are reproducible with zero ETABS/UI call | 3–5 focused days |
| H0 — actual-building route decision | Resolve `SURROGATE_ASSISTED`, `ETABS_FIRST` or terminal `HOLD` | Complete applicability envelope or mutation-ready ETABS-first proposals; no baseline-to-candidate-range inference | 1–2 days for ETABS-first; separately cost surrogate evidence |
| E — W3I screening | Candidate families, scenarios, objectives and all mandatory checks | Deterministic `SCREENED_ONLY` shortlist with no hidden mandatory check | 5–10 focused days |
| F0/F1 — W3K owned-copy transaction | Offline dry run/journal/recovery/failure injection, then installed existing-beam-property transaction and result epoch | No non-idempotent replay; one separately authorized installed copy; original/attached process/file unchanged | 12–20 focused days plus ETABS run/review time |
| G — W3L bounded iteration | Finite budget, cache keys, final clean-baseline repeat and dossier | Budgeted termination and independently repeated final candidate or explicit no-solution outcome | 4–8 focused days plus candidate cycles |

These are engineering planning ranges, not delivery promises. Project evidence,
ETABS runtime and independent review dominate the calendar. Packet A0 should be
done before any new live pilot; A1 remains separately authorized installed
acceptance. Packets B and C0 can proceed without opening ETABS. C2 waits for the
actual C1 schema and does not guess it from generic fixtures. H0 must stop if
the necessary project basis does not
exist; repeated table or solver work is not the default response.

## Acceptance and recurrence controls

- No API function may attach to “the running ETABS” without an unexpired exact
  process-instance/target/runtime observation and operation capability.
- Live routes are disabled by default, loopback-only when enabled and protected
  independently of optional global auth. One OS lease covers target verification
  through postflight; another bridge process cannot overlap it.
- A saved-file hash does not prove live-session cleanliness. Unknown or unsaved
  session state cannot be promoted to hash-bound baseline/copy evidence, and the
  attached user session is never saved to manufacture that proof.
- If more than one process exists, the UI shows PID, version and model name; the
  operation remains blocked until one exact target is chosen.
- An attached operation is getter-only, normalizes observed units offline and
  holds when required output is not already selected/finished. It proves units,
  lock, output selections and saved-model identity unchanged.
- A dedicated STA broker plus OS lease bounds hangs. Timeout never kills an
  attached ETABS process; it fences reuse and retains unmatched call-stage
  evidence until operator verification.
- `STARTED` is hash-chained and durably flushed before invocation; raw
  `RETURNED` is appended/flushed before decoding. The atomic final evidence
  manifest binds ledger head/count and all retained artifacts. Verification
  rejects gaps, truncation, hash mismatch and unfinalized transactions. A
  timeout/decoder failure retains method, arguments, raw shape/return code where
  available and cannot trigger blind reconnect/replay. Proprietary raw records
  stay in the approved local store; Git receives reviewed safe projections only.
- No setter, save, unlock, analysis, design run or exit is permitted in an
  attached user session.
- The dry-run digest names every object identity, expected old value, existing
  proposed beam property and readback rule. Unknown/already-changed/auto-select
  or new-property/column changes fail before the first setter.
- A failed copied-model transaction is never retried blindly. Record the failed
  stage before each call, close only the exact owned process instance, and
  discard/quarantine the copy. Restart verifies or quarantines; it never replays
  a setter, analysis, design, save or exit.
- `SetSection` does not claim installed reinforcement. Library bar layers and
  ETABS section/design metadata remain distinct evidence.
- Every optimizer ranks only candidates accepted by the same evaluator; an
  omitted mandatory check is a hold, not a pass. Criteria/catalogue digests and
  declaration chronology are mandatory; incomplete search cannot claim optimal,
  Pareto-complete or infeasible.
- Use saved evidence and direct getters first. Use one named SQLite export next.
  Separate installed acquisition from offline parsing; require create-new/hash/
  completion/integrity/schema evidence. Do not repeat the broad table COM route
  without a new vendor-supported cause and a required field with no simpler source.
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
- [Microsoft COM processes, threads and apartments](https://learn.microsoft.com/en-us/windows/win32/com/processes--threads--and-apartments)
  and [call cancellation](https://learn.microsoft.com/en-us/windows/win32/com/canceling-method-calls):
  STA ownership/message processing and cancellation do not prove server-side
  work stopped.
- [SQLite URI filenames](https://www.sqlite.org/uri.html): `mode=ro`, private
  cache and the requirement that `immutable=1` only describe a truly immutable
  artifact.
- The legacy source identities and reviewed current-code locations are recorded
  in the safe audit receipt linked above.
