**Type:** Architecture
**Audience:** Developers
**Status:** Active
**Importance:** Critical
**Created:** 2026-09-04
**Last Updated:** 2026-09-05

# WP10 — read-only ETABS snapshot adapter

WP10 connects an identified ETABS 23.3.1 model to the reusable native beam
libraries without moving engineering calculations into COM or Excel. It owns
AO16 (`etabs.beam_snapshot.import/v1`) and Excel command `XL-CMD-02`. Its output
is an immutable vendor-neutral `structural.analysis_snapshot/v1` artifact that
can be normalized, tested, replayed, designed, optimized, and reported without
ETABS.

The primary installed tuple is Windows x64, ETABS `23.3.1.4563`,
`CSiAPIv1.dll`/ETABSv1 `2.16.0.0`, .NET 10, and the WP09 64-bit Excel host.
Other ETABS versions do not inherit this compatibility claim.

WP10-01 through WP10-04 are complete. WP10-02 proved the exact-version getter
boundary and one unchanged-model live matrix; WP10-03 added the bounded STA
operation-control and durable evidence boundary; WP10-04 added offline
normalization and cross-runtime replay. WP10-05 Excel import is next. The
remaining slices use the plan-driven delivery contract below as a
pilot of the repository-wide workflow. That contract orchestrates existing
controls; it does not create a second WP10-only delivery system.

## Boundary and package layout

- Portable AO16 request/result, raw-capture, call-ledger, snapshot, row
  disposition, unit/axis/mapping, provenance, and diagnostic contracts belong
  in the host-free `StructuralEngineering.*` packages.
- `StructuralEngineering.Etabs` is the only library that references CSI interop.
  It is optional, Windows-specific, exact-version checked, and usable outside
  Excel.
- A bounded STA broker owns COM attachment, deadlines, the operation lease,
  call ledger, artifact writes, postflight, and process cleanup. Excel invokes
  the broker through a versioned file/message contract; CSI COM never runs in a
  worksheet function or leaks into the pure packages.
- `StructuralEngineering.ExcelDna` adds only the explicit `XL-CMD-02` adapter.
  The command imports a completed snapshot through controlled workbook tables,
  readback, rollback, freshness, and a hash-bound receipt.

## Review of the previous ETABS work

The older Python services provide useful source material, especially
`etabs_installed_readonly.py`, `etabs_operation_control.py`,
`etabs_result_catalogue_adapter.py`, `etabs_beam_baseline.py`, and
`etabs_snapshot.py`. Their strict return-shape checks, call ledgers, result-row
identity, offline fixtures, and installed signature evidence should be ported
semantically and compared through shared conformance fixtures.

Several older paths are application-specific and must not become the new
library boundary. `etabs_live_bridge.py` and parts of the baseline flow change
present units or result selections. An attached WP10 acquisition issues no
`SetPresentUnits`, selection, unlock, analysis, design, save, close, or exit
call. The old Python/Excel bridge and its prior installed receipts remain
migration evidence; they do not qualify the new C# candidate. The existing
`EtabsForceBatch.schema.json` is also narrower than AO16 and cannot substitute
for the complete snapshot contract.

Prior failures become explicit regression cases: incorrect COM signatures,
unequal parallel result arrays, ambiguous object/element stations, missing or
drifted output selection, formula-sensitive JSON written through Excel, stale
process/model identity, and partial canonical output after a failed getter.

## Delivery slices

1. **Portable contract and fixtures.** Freeze the AO16 request/result and
   `structural.analysis_snapshot/v1` schemas, canonical identity rules, raw
   capture format, row dispositions, and Python/.NET conformance fixtures.
2. **Exact getter adapter.** Bind the installed 2.16.0.0 signatures and permit
   only the reviewed getter matrix for process/model identity, version, lock,
   units, analysis/result epoch, selected cases/combinations, stories, points,
   frame connectivity, sections/materials/modifiers/offsets/releases/local
   axes, object/element mapping, and `Results.FrameForce`.
3. **Operation control.** Implement the STA broker, single operation lease,
   deadlines, hash-chained started/completed call records, exact return-code and
   array-shape checks, state fencing, durable raw artifact, postflight equality,
   and close receipt. A timed-out or uncertain call is never replayed
   automatically.
4. **Offline normalization.** Convert source units once, retain signed
   P/V2/V3/T/M2/M3 from the same result row, preserve case/combo/step and both
   station identities, resolve axes/faces from evidence, account for every raw
   row, and emit no partial accepted snapshot when any required row is blocked.
5. **Excel import.** Add `XL-CMD-02`, declared snapshot/action/mapping tables,
   transactional table writes, exact readback/rollback, freshness, progress,
   cancellation, and a receipt that binds raw and normalized artifact hashes.
6. **Installed qualification.** Replay captured artifacts without CSI, then run
   the unchanged candidate against the exact installed ETABS/Excel tuple for
   PF8 E5-02 through E5-04 and the small/medium
   `PERF-ETABS-ACQUISITION` datasets.

## Execution controls carried forward from WP09

The six delivery slices are separate bounded scopes. The WP10-05 preparation
review below adds explicit production-handoff and multi-member prerequisites
before qualification; these each receive their own bounded task. They are not one combined
implementation and acceptance session. `WP10-01` remains host-free. Before the
exact getter adapter begins, a read-only host micro-probe must establish the
installed assembly and ETABS versions, attachment path, approved getter
signatures, return shapes, active-model identity, and deterministic cleanup.
The probe records no compatibility claim and changes no ETABS state.

Each slice freezes its request/result contract, failure rows, acceptance
examples, non-goals, and focused commands before implementation. Offline
fixtures and replay qualify the portable logic first. Live work then advances
through host preflight, one getter smoke path, the functional getter matrix,
postflight state equality, Excel import, and performance in that order. A later
stage does not run while a cheaper earlier stage is failing.

Independent review starts only after the slice's acceptance matrix passes and
returns one consolidated blocker list. The initial reviewed candidate may have
one consolidated repair candidate; a second rejection triggers contract or
design re-planning before more implementation. Installed qualification evidence
is generated only after the functional source candidate is stable. After the
slice content freezes, run its formatter and focused matrix once, create the
candidate, obtain one independent decision, and run the read-only
`./run.sh check --candidate-integrity` once on the accepted head. Pre-push owns
the one final read-only `session end`; task closeout follows post-merge proof.

## Delivery decision — one clean session per bounded slice

PF11 estimates all of WP10 at 10–15 engineer-days and classifies it high risk.
The remaining work crosses distinct installed-ETABS, offline-normalization,
installed-Excel, and external qualification gates. Combining those gates into
one coding session would recreate WP09's oversized-packet failure mode.

For delivery purposes, **one session** therefore means that each remaining
slice starts and closes one parent task without carrying repair work into a
later session where feasible; an application hold never becomes a fabricated
pass to meet this target. WP10-04 completed this boundary; WP10-05 is next. Later slices
may share the IMP-M3 milestone branch only when their accepted authority and
installed-host gate are unchanged; they retain separate task timers and
acceptance decisions.

| Session | State | Complete outcome | Must not leak into the session |
| --- | --- | --- | --- |
| WP10-02 | Complete | exact-version getter port, binding, fake-host proof, and one live getter-only matrix | broker retries, normalization, Excel, performance |
| WP10-03 | Complete | STA lease, deadlines, durable raw capture, call ledger, postflight, cleanup | normalization and workbook writes |
| WP10-04 | Complete, PR #972 | complete offline normalization and row conservation from captured raw artifacts | COM and Excel |
| WP10-05 | Next; plan below | transactional completed-file `XL-CMD-02` import, installed Excel readback/rollback, and freshness | live acquisition, automatic design-input synthesis and acquisition performance claims |
| WP10-05B | Planned prerequisite | production acquisition host and versioned file handoff to the same Excel importer | ETABS setters, automatic reconnect/retry and scale claims |
| WP10-05C | Planned prerequisite | multi-member acquisition/normalization profile and representative datasets for PF9 | silently weakening source contracts or performance budgets |
| WP10-06 | After all prerequisites | integrated E5-02–E5-04 plus small/medium installed acquisition qualification | WP11 copied-model mutation or release |

The operating target for every session is one candidate, zero repair batches,
zero focused-check retries, one candidate-integrity run, one final closeout,
one hosted run, and less than ten percent writer-rework time. A real defect is
not hidden to meet the target; the delivery state machine records it and stops
after its bounded repair allowance.

## Plan-driven delivery contract for WP10-03 through WP10-06

The main process risk is a plan that describes the intended feature but does
not bind the existing scripts, hooks, affected domains, evidence, and stop
conditions before implementation. Each remaining slice therefore begins with
one compact executable plan card. The card is the slice-specific input to the
repository controls, not a replacement for those controls.

### One owner for each kind of truth

| Concern | Existing project owner | WP10 supplies |
| --- | --- | --- |
| Task identity, timing, base state, and delivery states | `./run.sh session` and `scripts/session.py` | one task ID and the accepted WP10 plan path |
| Changed paths and affected validation domains | `scripts/verification.py` and `scripts/verification-manifest.json` | no separate WP10 routing table |
| Maintained command discovery and permissions | `scripts/control-plane.json` | operation names to reuse, never a copied script catalogue |
| Formatting, text hygiene, and candidate integrity | `./run.sh format`, `.gitattributes`, and the installed hooks | the exact immutable task-base SHA and bounded changed paths |
| Product and installed-host acceptance | this plan, portable contracts, and task evidence | ETABS/Excel tuple, request, model, artifact, and proof identities |
| Rework recurrence | `docs/verification/rework-recurrence-index.json` | references to applicable `RR-NNN` rows, not duplicated counts or solutions |
| Hosted assurance | the change-domain PR workflow and required `PR Gate` | one frozen candidate and its exact run ID |

ETABS process IDs, model paths, members, result selections, combinations,
workbook identities, and CSI calls remain WP10 evidence. They must never be
added to the generic session, verification, hook, or control-plane contracts.
Conversely, WP10 must not introduce another formatter, Git wrapper, impact
map, test scheduler, or delivery state machine.

### Required executable plan card

Before opening a slice's implementation timer, freeze all of these rows. A
missing or ambiguous row is an intake hold. The card may cite an existing
authority instead of copying it.

| Plan row | Required content |
| --- | --- |
| Outcome | one complete user/developer-visible result and explicit non-goals |
| Starting identity | fetched default-base ref and exact SHA, feature branch, initial head/tree, clean state, and overlap disposition |
| Impact | provisional product/control domains plus the authoritative `verification plan` result once changed paths exist |
| Reuse | existing contracts, source APIs, scripts, hooks, fixtures, and prior evidence that will be consumed without reinvention |
| Inputs and external state | exact files/artifacts and, when applicable, process/model/workbook/runtime identities plus who may change them |
| Bounded writes | intended product, test, documentation, evidence, and generated paths; an unplanned path requires an acceptance update |
| Acceptance-to-proof map | every outcome claim names a focused test, deterministic artifact check, installed observation, or explicit manual decision |
| Ordered units | implementation order, the cheapest failing gate before each expensive or live gate, and the content-freeze point |
| Command matrix | maintained commands, exact working directory, filters, runtime, expected output, and retry/repair rule |
| Stop/replan rules | ambiguity, changed authority, host drift, unexpected write, failed cleanup, or second rejected candidate |
| Efficiency target | one candidate, zero repair batches/retries, one integrity/closeout/hosted run, and writer rework below ten percent |

### Existing automation sequence

Until a repository-wide candidate-preparation command is separately designed,
implemented, and accepted, WP10 uses the current maintained controls directly:

1. Fetch and inspect Git through the canonical workflow, then run `session
   begin`; admission must pass before the task timer opens.
2. Enter `BOUNDED_UNITS` with this plan and any slice-specific acceptance file.
   Preserve the exact default-base SHA recorded at intake for the whole slice;
   do not substitute a later candidate or moving branch reference during a
   repair.
3. Implement the bounded product, tests, documentation, evidence, and required
   projections. Run only a narrow diagnostic needed to answer an active
   question.
4. Before freeze, run `./run.sh verification plan --base <exact-task-base>` and
   reconcile its full changed-path/domain result with the plan card. Unknown
   impact remains fail-closed to all domains.
5. Enter `CONTENT_FROZEN`; run the changed-path formatter once with the same
   exact task base, then run the slice's consolidated focused matrix once.
   Check every task-touched text path from the original base, including paths
   introduced by an earlier candidate.
6. Finish all task-owned versioned evidence before `PREPARED`, commit one
   immutable candidate, obtain one consolidated audit decision, and run the
   read-only candidate-integrity gate once on the accepted head.
7. Let pre-push own the idempotent final closeout, publish once, bind the exact
   hosted verdict, verify candidate/merge tree equality, and record the derived
   efficiency result.

Hooks remain final safety boundaries; they are not the first place to discover
ordinary formatting, line-ending, command-shape, or missing-domain problems.
The future generic automation may consolidate steps 4–5 only after shadow-mode
proof across every validation domain. WP10 does not claim that command exists
today.

### WP10-03 executable plan card

| Plan row | Frozen WP10-03 value |
| --- | --- |
| Outcome | one host-independent operation-control boundary providing an STA lease, bounded deadlines, durable raw capture, hash-chained call records, postflight fencing, and deterministic cleanup around the accepted WP10-02 getter adapter |
| Non-goals | no normalization, workbook import/write, ETABS setter, analysis/design/save/close/exit action, performance qualification, WP11 mutation, or release |
| Starting identity | record the exact fetched `origin/main` SHA and clean `codex/wp10-03-*` feature head/tree at intake; never reuse WP10-02's historical base as the new task base |
| Expected impact | `dotnet`, `docs`, and always-run `repository`; the live verification plan is authoritative, and any generic workflow edit is a separate control-plane packet |
| Reuse | WP10-01 wire/canonical contracts, WP10-02 exact getter matrix and nullable-array rule, its accepted live raw capture, existing C# solution, locked dependencies, repository session/verification controls, and the applicable recurrence rows |
| External state | offline fake-host work first; one final live path may use only the freshly preflighted exact ETABS tuple, selected unchanged saved model, output selection, request, and evidence destination |
| Bounded writes | the existing `StructuralEngineering.Etabs` project, one focused WP10 operation-control test file, this plan/status, one task evidence record, newest session entry, recurrence index only when an issue actually repeats, and maintained generated handoff/projection files when required |
| Proof map | lease exclusivity, ordered start/return ledger, deadline and uncertain-call fencing, partial-artifact rejection, all-resource cleanup, postflight equality, and deny-listed effects each require a deterministic fake-host assertion; the final installed path additionally requires exact call/artifact identities and unchanged host/model state |
| Order | freeze broker contract and failure states; implement fake host and offline broker; pass negative paths; replay the accepted getter capture; run one live smoke/final path; prove postflight/cleanup; freeze and verify once |
| Command shape | use repository launchers and literal paths; run the locked .NET 10 restore/build/test sequence from `CSharp`; freeze the exact focused test class/filter before product writes; do not assemble wildcard or cross-shell probes |
| Stop/replan | stop on ambiguous lease ownership, unsafe timeout semantics, missing message pumping, unpaired ledger entries, partial durable output, cleanup uncertainty, model/selection drift, a required CSI effect, or any change to WP10-01/02 accepted meanings |
| Efficiency | one live acquisition, one candidate, zero command-shape corrections, zero focused retries, one integrity/closeout/hosted run, and writer rework below ten percent |

WP10-03 is the pilot, not proof that the same plan automation is already safe
for every repository domain. Its closeout must compare planned versus actual
paths, commands, gates, candidates, rework, and live runs. Only generic rules
that reduce a measured failure without importing WP10 facts may move into the
project-wide control plane; that promotion is a separate maintenance scope.

### WP10-03 implementation review — 2026-09-05

State: merged in [PR 970](https://github.com/Pravin-surawase/structural_engineering_lib/pull/970).
The WP10-04 preparation review below verifies the delivered identity and records
the measured outcome; the implementation observations here remain historical.

Confirmed outcomes:

- `StructuralEngineering.Etabs` now owns a process-keyed single-operation
  lease, dedicated STA worker, explicit Windows message pumping, absolute
  deadline, no-retry timeout fence, and a quiescence handle that retains the
  lease until any late provider call and cleanup finish.
- Each getter writes and flushes one `started` record before dispatch and one
  `returned` record after the provider returns. Records use the WP10-01
  canonical hash functions, form one continuous SHA-256 chain, and are paired
  into a finalized ledger only after every getter succeeds.
- The final raw acquisition artifact is written to a write-through temporary
  path and moved without overwrite only after exact host identity, protected
  pre/post state, ledger, host disposal, and lease release are proved. Timeout,
  cancellation, cleanup uncertainty, identity drift, denied effects, failed
  return, or existing evidence emits no accepted final artifact.
- Exact-SHA recorded capture replay reconstructs the proved managed scalar and
  array kinds in order without ETABS. The broker itself requires complete source
  consumption before publication, so a callback cannot accept a partial replay.
  The accepted WP10-02 capture replayed all 410 calls and reproduced its
  protected-state digest exactly.
- One final live run on process `7316` completed 410 calls across all 48 frozen
  getters and 820 hash-chained records. It retained STA execution and message
  pumping, released all acquired COM references and the lease, left the ETABS
  process alive, and preserved model bytes, model SHA-256, lock, units,
  analysis/result state, and output selection.

The committed receipt is
`docs/verification/wp10-03-operation-broker-evidence.json`; the hash-bound raw
artifact and journals remain outside Git. This slice performs no normalization,
workbook write, ETABS setter, analysis/design action, performance qualification,
general-version claim, engineering approval, or release.

One implementation-stage replay comparison exposed that `DateTimeOffset` used
`+00:00` while the accepted protected-state digest used canonical UTC `Z`.
The host-independent inspection now formats the same UTC instants identically;
the affected replay was regenerated before the only live run. No candidate had
been created, so this was not a candidate repair.

The first immutable-candidate audit found that complete replay consumption was
asserted by the configured test callback instead of the broker. The one admitted
repair moved that invariant behind a small host capability checked by the broker
before postflight and publication, removed the harness-owned assertion, and
added an early-return rejection case. No live behavior or evidence identity was
changed, so the accepted one-run ETABS evidence was not repeated.

The affected verification selectors are the source-discovered
`Wp10GetterAdapterTests` and `Wp10OperationBrokerTests` classes. A descriptive
note had used the stale name `EtabsGetterAdapterTests`; its zero-test exit was
rejected rather than counted as evidence, and the exact maintained selector ran
all 10 getter cases. Future plan cards must freeze test identifiers from current
source, not narrative labels.

### WP10-04 next-plan review after WP10-03

#### Delivered-work check — 2026-09-05

Preparation task `WP10-04-PREP` checked the predecessor before any product work:

| Check | Observed evidence |
| --- | --- |
| Integration | PR 970 is merged. Reviewed head `9d3cf00aef3c772d4e37df080fa850318b1acf5a` and fetched merge `31974b34d6bfc589d506648cd73ac5431b095638` have identical tree `ae92ea494173264343ad48338bf35eaec904e44b`. |
| Hosted proof | [PR Validation 33916559572](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/33916559572) completed successfully on the reviewed head. |
| Product evidence | The committed [broker receipt](../../verification/wp10-03-operation-broker-evidence.json) records 410 calls, 48 getter operations, 820 journal records, 13 force rows, unchanged protected state, and cleanup. The prior focused result is 12 broker and 10 getter cases; this planning review does not rerun installed tests. |
| Retained input | Both external artifact files are present and their byte counts and SHA-256 match the receipt. Preparation inspects JSON offline; WP10-04 must still invoke the production artifact validator before projection. |
| Efficiency | The Git-common usage closeout under historical task ID `WP10-COMPLETION` records 74.699 minutes, one audit rejection/repair, 15.817 rework minutes (21.17%), zero focused-gate retries, zero broad local gates, one integrity gate, one final closeout, and one hosted run. |

The bounded slice, exact replay, one installed run, source-bound receipt, and
single hosted cycle worked well. The less-than-ten-percent rework target was
not met. Several formatter invocations and command corrections also occurred;
zero recorded focused-gate retries does not mean zero repeated work. Preserve
the useful controls and move semantic decisions, dependency projections, exact
test selectors, and lifecycle argument discovery before content freeze.

The essential audit lesson is **production ownership of completeness**. A test
callback must not be able to make an incomplete projection look successful.
WP10-04's public normalization path must itself enforce coverage, row accounting,
and no accepted partial snapshot. A test independently checks those invariants.

#### WP10-04 executable plan card

Status: implemented after the semantic intake recorded below. Exact retained
normalization and Python replay pass; subsequent publication/merge facts belong
to the task delivery ledger and PR. The entry matrix remains the source of
truth for the distinctions between getter facts and declared policy.

| Plan row | WP10-04 value |
| --- | --- |
| Outcome | An offline production path validates the durable acquisition, projects complete portable raw records, and emits a deterministic validated `structural.analysis_snapshot/v1`, or a typed failure with no accepted snapshot. |
| Non-goals | No COM attachment, broker/STA execution, installed application work, Excel import, ETABS setters, engineering design, performance qualification, WP11, release, or generic workflow redesign. |
| Starting identity | This preparation starts at merged `31974b34d6bfc589d506648cd73ac5431b095638` on clean `codex/wp10-04-prep`. Implementation must fetch and bind its own exact current default base, clean `codex/wp10-04-*` head/tree, writer device, and candidate-overlap disposition; the preparation base is not a permanent implementation base. |
| Authority and reuse | PF11 and AO16; existing `AnalysisSnapshotContracts.cs`, `AnalysisSnapshotCodec`, `operations/wp10.json`, `schemas/wp10.schema.json`, and `conformance/wp10-vectors.json`; `EtabsAcquisitionArtifactCodec.ParseAndValidate`, getter matrix, and broker receipt. Preserve WP10-01 meanings and golden identities. |
| Layer ownership | Optional ETABS package decodes vendor records offline. Contracts carry typed portable inputs; Analysis owns unit conversion, topology/axis/face checks, row dispositions, and canonical construction. Analysis must never reference Etabs or Excel. |
| Expected impact | `dotnet`, `python` for shared conformance checks if affected, `docs`, and `repository`; the maintained verification plan decides actual domains. A shared-contract edit may route more domains and must not be overridden manually. |
| Inputs | Exact durable artifact plus receipt, AO16 scope/source context, explicit normalization policy and any required evidence mapping. Files are read-only; output uses a new external task directory. No lookup against today's ETABS process, model file, or clock. |
| Bounded writes | Existing Contracts/Analysis/Etabs projects only for required projection and normalization; focused tests in the two existing C# test projects; additive shared conformance vectors and affected Python WP10 tests only when needed; this plan, implementation status, one safe WP10-04 receipt, newest session entry and maintained handoff. Dependency locks only for actual graph changes. |
| Proposed new files | `CSharp/src/StructuralEngineering.Etabs/EtabsCaptureProjector.cs`, `CSharp/src/StructuralEngineering.Analysis/AnalysisSnapshotNormalizer.cs`, `CSharp/tests/StructAutomate.Tests/Wp10CaptureProjectionTests.cs`, and `CSharp/tests/StructuralEngineering.Tests/Wp10NormalizationTests.cs`. These names are planned, not existing callable APIs. Freeze any required context type in Contracts during intake. |
| Control ownership | Reuse `session`, `verification plan`, changed-path `format`, docs checks, hooks, candidate integrity and required hosted checks. No WP10-specific Git wrapper, scheduler, duplicate impact map, or new agent infrastructure. |
| Skill and roles | Use the beam-automation skill and scoped C#/documentation rules. One parent performs implementation, verification, essential review and operations passes; no automatic agent fan-out. Separate read-only audit only if explicitly delegated, using a compact acceptance packet and exact candidate identity. |
| Efficiency | One candidate, zero repair batches/command corrections, one frozen focused matrix, one integrity gate, one final closeout, one hosted cycle, zero live runs; rework target below ten percent. Report actuals honestly. |

#### Input and semantic entry matrix

The primary input is `external:WP10-03/wp10-03-live-broker-artifact.json`,
schema `structural.etabs_durable_raw_artifact/v1`, 1,268,036 bytes, file SHA-256
`5a24ef94ca511a248d4897c54cf5e779c2cdc5eef9753c14795e055540f39135` and
embedded artifact SHA-256
`193a3c84cf52af1be4426c53a0e8f603c137be90144aea3532f91892e8a207c5`.
The receipt separately binds its journal and the secondary offline replay
artifact. Resolve the device-local file location at intake; never commit the
raw capture, model paths, vendor binaries, or private project data as fixtures.

Freeze the following in one acceptance record before implementation. A source
fact and a chosen interpretation must remain distinguishable.

| Topic | Observed input / required decision | Acceptance consequence |
| --- | --- | --- |
| Artifact boundary | Use the durable artifact validator, then bind every projected getter to the retained call ID, operation, inputs, outputs, signature digest and ordinal. `EtabsRecordedGetterHost.Load` accepts the earlier getter-capture format, not this durable envelope. | Consume the durable content directly offline; do not start a broker merely to normalize it. Reject wrong file/hash/schema, incomplete or failed ledger, changed identity, or missing cleanup proof. |
| Coverage before projection | 410 calls across 48 operations include repeated pre/post observations and catalogs beyond the selected scope. The portable record-kind set has no separate story/load-pattern/insertion/spring record. | Freeze a complete getter-output-to-field/evidence/disposition map, grouping repeated observations without losing provenance. Freeze the expected projected model-record count. Never drop unsupported facts before the portable row ledger and call that conservation. |
| Units | Captured present/database enum is `6`; the component-unit getters must agree. CSI documents `6` as `kN_m_C`. Dimensional conversion is m→mm ×1000, kN→kN ×1, kNm→kNm ×1, stress kN/m²→N/mm² ×0.001, area ×10^6, fourth moments ×10^12. | Bind the mass-density unit independently to the getter's mass output and use its force/length/time basis; do not infer mass from weight using an assumed gravity. Freeze every quantity factor before code. |
| Existing normalizer | `ActionNormalizer` implements the WP03 N/Nmm output contract; AO16 action rows require kN/kNm. | Reuse validation ideas, not its unit-labelled output as an AO16 row. Prevent both double conversion and mixed-unit reuse. |
| Section/material | Rectangle dimensions and `GetMaterial` are explicit; section and material names differ and cannot prove grades or material kind. `GetMPIsotropic`/`GetWeightAndMass` do not provide a material-type enum. | Use returned dimensions/properties, not name parsing. Bind material kind to approved retained evidence or explicit typed mapping; unresolved required classification blocks. No invented concrete grade. |
| Assignments | Preserve object and section modifiers separately, offsets, insertion point, mirroring and release spring values. Only boolean releases have direct portable fields. | Define whether each extra fact is represented in raw fields/provenance or requires blocking for the chosen scope; nonzero springs or eccentric/mirrored assignments cannot silently become a simple centered member. |
| Stories | `SimilarToStory` contains six CLR nulls; `IsMasterStory` is true for those captured rows. | Preserve null in raw evidence. Freeze its semantic handling; do not turn it into an empty string or fabricate a story reference. |
| Selection and enums | There are 15 case-type records and 62 combination definitions; the selected combination lists five case factors. | Map case type/subtype, combination type and case/combo reference enum explicitly; follow the selected dependency closure with ordered factors. No name-based inference of linearity or concurrency. Freeze disposition of out-of-scope definitions. |
| Steps and concurrent actions | All 13 captured force rows have `Single Value` and numeric step `0`. The portable validator requires null for a non-step action and equality between portable raw and normalized step. | After proving static concurrency from the dependency graph, project the vendor sentinel to null in both portable rows; retain original `0` in immutable getter evidence and record the rule. Step-based/envelope rows need their own explicit basis or a blocking result. |
| Axes and faces | Retained element matrix is `[0,0,1,1,0,0,0,1,0]`. Endpoint direction is global +Y. Both a matrix and its transpose can pass an orthonormality check. | Freeze matrix layout with exact-version documentation and geometry. Check e1 against I→J and transform unit vectors; explicitly define physical top/left and viewing direction. An orthonormal matrix alone does not prove axis meaning. |
| Stations | The retained member is about 2.75 m between its endpoints, with 0.225 m end offsets; 13 object/element stations run from about 0.225 to 2.525 m. `LineElm.GetObj` supplies parent and relative distances. | Define physical origin, interval and ratio using topology. Preserve separate object/element stations. Never set the first force station to zero or equate a meshed element station to the physical station by default. |
| Identity and freshness | Capture has acquisition, model, protected-state and selection evidence, but does not supply a portable project ID or a native analysis revision/epoch identifier. | Freeze project/source context and deterministic evidence-derived revision/epoch rules, labelled as such. No random ID, current timestamp or claim to know today's live-model state. |
| Exclusions | Every projected model record and force row needs exactly one accepted/approved-exclusion/blocked disposition. | Freeze exclusion reasons and real approval references. For this selected beam, expect 13 accepted same-row actions; do not manufacture approval to discard a difficult row. Any required blocked row withholds the whole snapshot. |

The material-kind evidence, axis/physical-face convention, deterministic
revision context and complete projection/disposition count are explicit entry
decisions. If retained evidence cannot settle one, produce a bounded revised
contract or a precise missing-input request before product writes; do not
reopen live acquisition under WP10-04. Historical CSI documentation is a
semantic cross-check, not proof of the installed 2.16 signature:
[eUnits](https://docs.csiamerica.com/help-files/etabs-api-2016/html/cff40d28-9b1a-7f00-cfb9-0386da2464cc.htm).

#### Acceptance-to-proof map and ordered units

WP10-04 intake accepted on 2026-09-05, base
`e95a11414cfbb43cc7fecd0581720447d7b83798`, Windows writer on
`codex/wp10-04-normalization`. Fetched main equals the clean starting checkout;
the five detached sibling worktrees retain historical WP09 evidence. Open PRs
are unrelated dependency updates. The owner supplied concrete classification
for `M25FE500`, then delegated remaining decisions. This is explicitly a
user-declared classification, not a captured material enum or strength grade.

The bounded normalization policy is `wp10-offline-horizontal-frame/v1`:

- Retain all 410 getter calls, their ordinals, inputs, outputs (including null),
  signatures and ledger IDs. Group them into nine portable record kinds using
  metadata for catalog/story/pattern/protected-state evidence. Accept all 15
  cases and 62 combinations as definitions; concurrency is proved only for the
  selected dependency closure. Expected model count is 97: metadata 1, points
  2, material 1, section 1, member 1, cases 15, combinations 62, selection 1,
  stations 13. Add the 13 force rows for 110 dispositions; zero exclusions.
- Source units are m, kN, kNm, kN/m2 and kN*s2/m4. Factors are 1000, 1, 1,
  0.001 and 1000 respectively; density comes from mass, never weight/gravity.
  Section area and fourth moments use length squared and fourth power.
- Use row-major local-to-global direction cosines, columns e1/e2/e3. The
  installed 2.16 help has an undocumented LineElm parameter page; its LinkObj
  page explicitly defines the matrix equation. This cross-interface convention
  is a chosen bounded policy, independently checked against I-to-J geometry,
  all element directions, orthogonality, handedness and global Z. It is not a
  claim that the LineElm page documents that equation. Physical top is global
  +Z, left is cross(+Z, I-to-J), viewed from I toward J. Nonhorizontal or
  obliquely rotated sections block; no transpose guessing.
- Physical stations originate at object I, ratio uses full I-to-J length,
  and element stations use retained relative element endpoints. End offsets
  do not shift the station origin. Unresolved topology blocks.
- Cardinal point 8 means top centre. Preserve cardinal point, separate section
  modifiers, offsets and stiffness-transform flag in typed raw member/section
  evidence. No centroid relocation or eccentric action transformation occurs.
  Consumers must honor that reference line. Mirroring, nonzero joint offsets,
  transformed stiffness or nonzero release springs block this bounded policy.
- All selected cases are linear static with zero initial conditions (`None`),
  selected combination type 0 is linear-add, and factors reference case enum
  0. Only after recursive static proof, `Single Value`/0 becomes portable null;
  original step zero remains in getter evidence. Unsupported selected bases block.
- Project identity is an explicit evidence-project context, model revision is
  model-file-SHA-derived; analysis revision binds model and retained status;
  epoch binds acquisition, protected state and force evidence. Created time is
  retained completion time. Freshness means consistent at capture only.
- Installed help SHA-256 is
  `0108deeb19fd054ea03a9be89244dac5c8f5995cc44865eaa508b17f675b9d88`.
  Exact pages are `ab496301-f4fe-d09c-eae8-77bf4824ca59` (matrix),
  `ea3cc193-4efa-195e-db7d-39ab7678fffb` (insertion),
  `35a593d3-423d-53f1-47be-c3aebb058e2e` (mass), and
  `f7701fac-9d31-4e45-be6b-57a3ac47745b` (initial conditions).
  Extracted help and tooling stay external; no vendor content enters Git.
- The retained broker ledger uses offset timestamps. Preserve that original
  ledger in acquisition evidence, convert equivalent instants to the portable
  schema's required UTC `Z`, and recompute only the portable chain and digest.
  Call IDs, method, arguments, return values and signature identity stay bound.

Additive path allowance: `AnalysisNormalizationContracts.cs` in Contracts,
synthetic fixture support beside the two planned test files, a new shared
`wp10-normalization-vectors.json`, the existing Python WP10 test, reference
page and TASKS row. No wire-contract meanings change. `Wp10NormalizationTests`
proves dimensions, topology, faces and conservation; `Wp10CaptureProjectionTests`
proves the durable boundary, complete coverage, selected graph and deterministic
output. Its explicit `WP10_OFFLINE_ARTIFACT`, `WP10_OFFLINE_SHA256` and
`WP10_OFFLINE_OUTPUT` retained-input test must run with all three supplied.
Shared synthetic output and the retained output are independently replayed by
Python. The original frozen vectors must remain byte-for-byte unchanged.

Cross-runtime replay exposed the existing .NET serializer's uppercase exponent
spelling, contrary to the frozen Python/PF4 canonical representation. The path
allowance includes a correction in `AnalysisSnapshotCodec.cs` and preservation
of the already-issued durable artifact v1 numeric spelling inside
`EtabsAcquisitionArtifactCodec` in `EtabsOperationBroker.cs`. This fixes
implementation parity without changing the portable wire meaning or old golden
identities. Exact retained artifact validation and offline broker-codec
regressions are required; no live broker test is selected.

| ID | Required proof on the production path |
| --- | --- |
| N1 | Exact-file hash plus production durable validation; wrong bytes/schema/ledger/state fail before any portable output. |
| N2 | All getter facts have traceable coverage and projected raw records have deterministic IDs; deleting a required fact cannot be masked by a smaller projected input count. |
| N3 | Independent dimensional examples cover geometry, section properties, elastic modulus, density and all six signed force components; no rounding, absolute-value conversion or cross-row envelope is introduced. |
| N4 | Geometry verifies transform layout, I/J direction, faces and physical/object/element station relationships; reversed and meshed examples expose transposition or origin errors. |
| N5 | Selection dependency closure proves action basis; vendor zero→portable null is explicit for non-step rows; unsupported/ambiguous selections or steps block. |
| N6 | Model records plus force rows equal accepted + approved exclusions + blocked, each source identity exactly once. One blocked required row yields no accepted snapshot. The normalizer enforces this without harness assistance. |
| N7 | Repeating the same validated artifact with identical context/policy/build inputs yields identical raw, row, snapshot and canonical-byte hashes. Live and replay artifacts have distinct acquisition identities, so their snapshot hashes need not match. |
| N8 | Both Python and .NET accept the emitted portable snapshot and agree on canonical identity. Existing WP10-01 vectors remain unchanged; additive synthetic vectors cover new normalization behavior without private raw data. |
| N9 | Exact 13-row retained-input normalization runs with no COM/Excel access and binds artifact, policy, projected counts and output hashes in a safe receipt. This proves offline normalization only. |

1. **Semantic intake:** resolve the entry decisions and bind every N1–N9 row
   to a named test/example or exact retained-artifact observation. Inspect the
   graph, nullable fields and unsupported facts before building a projector.
2. **Projection and normalization:** implement one complete production route,
   typed context/policy, synthetic fixtures and failure results. Use only a
   narrow diagnostic when it answers a current implementation question.
3. **Offline retained-input proof:** invoke the new production route on the
   exact primary artifact, compare repeat identities, then independently
   validate the portable output with Python. Preserve source files unchanged.
4. **Finish writes:** complete tests, receipt, docs, session/issues, actual
   dependency locks and generated handoff. Run the live impact plan from the
   original task-base SHA; reconcile every changed path. Freeze content.
5. **Verify and deliver once:** changed-path formatter, consolidated focused
   matrix, immutable candidate, consolidated essential audit, one read-only
   integrity check, pre-push closeout, required hosted checks and merge proof.
   Keep post-push status external. One rejection admits one repair; a second
   requires a changed acceptance digest before further implementation.

#### Command and recurrence controls

These are the command shapes for the implementation card. Run shell examples
from repository root unless `workdir: CSharp` is stated. In this Windows
checkout, use literal PowerShell paths and explicit `bash` for repository
launchers. Fetch exact refs if a stale narrow refspec blocks ordinary fetch;
never broaden refspec configuration or delete old branches as incidental cleanup.
WP10-04 registers only its exact new task-branch fetch mapping because the
delivery ledger requires a resolved upstream equal to the pushed candidate;
existing mappings and all historical branches/worktrees remain untouched.

```text
git fetch origin refs/heads/main:refs/remotes/origin/main
bash scripts/python_runtime.sh scripts/git_state.py --json --worktrees
bash run.sh session begin --task-id WP10-04 --agent codex
bash run.sh session delivery --help
bash run.sh verification plan --base <exact-task-base-sha>
bash run.sh format --write --base <exact-task-base-sha>

workdir: CSharp
dotnet restore StructAutomate.slnx --locked-mode
dotnet build StructAutomate.slnx -c Release --no-restore
dotnet test --project tests/StructuralEngineering.Tests/StructuralEngineering.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Wp10
dotnet test --project tests/StructAutomate.Tests/StructAutomate.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Wp10CaptureProjectionTests

workdir: repository root
bash scripts/python_runtime.sh scripts/validate_structural_engineering_contracts.py
bash scripts/python_runtime.sh -m pytest Python/tests/unit/test_structural_engineering_wp10.py -q
bash run.sh check --category docs
git diff --check
bash run.sh session check
bash run.sh efficiency check
```

The new projection selector becomes executable only after its named source
exists. Discover exact names with `rg` before freezing the test command. Require
a positive test count and evidence that the retained-artifact case actually ran;
an optional environment-gated test returning early is not acceptance. Bind the
new offline test's input/output arguments during semantic intake. Do not run
the entire broker test class: it contains
`ConfiguredExactEtabsHostCompletesOneFinalBrokerAcquisition`. Existing getter or
broker regression cases are added only if affected, with an explicit exclusion
of live entry points. Default .NET build must need no vendor installation.

Use `session delivery --to <state> --evidence <proof>` for every transition,
`--acceptance-path` at bounded intake, and exact head/run/PR/merge arguments
where required by the current CLI. Poll yielded terminal sessions to completion
before advancing the state. After audit acceptance, run
`bash run.sh check --candidate-integrity` exactly once; pre-push owns the final
`session end`. Record the seven non-overlapping timing phases and actual retry,
candidate, repair, broad-gate and hosted counts through `session usage`.
The broad Python suite and full 32-check gate remain at the named cumulative
programme gate unless a demonstrated cross-domain change requires them sooner.

Apply [recurrence controls](../../verification/rework-recurrence-index.json)
RR-001/002 for bounded scope and entry evidence; RR-003/011/012/013 for locks,
formatting and full-task-base hygiene; RR-005/015/016 for exact commands,
nonzero test discovery and complete lifecycle arguments; RR-007/014 for
canonical Unicode and UTC identities; RR-004/006/008 for one governed closeout
and the repair ceiling; RR-010 for consistent issue provenance. These references
reuse the maintained controls rather than copying their counters into the card.

Stop/replan on a changed WP10-01 meaning, unavailable semantic evidence,
unaccounted input, required COM call, hidden unit/axis assumption, unexpected
write outside the path budget, or a second rejected candidate. The review
question stays: would fixing this change the main normalization outcome?
Ignore adjacent hardening and do not add tests during the audit pass.

The owner subsequently authorized a library-wide delivery repair after this
preparation candidate's final closeout exposed inconsistent completion parsing
and a missing recovery transition. Its separate maintained authority is
[closeout recovery and early-check parity](../../verification/delivery-system-redesign.md#closeout-recovery-and-early-check-parity--2026-09-05).
That repair shares this unpublished planning branch and original task history;
it changes no WP10 engineering contract and does not start normalization.

## WP10-05 preparation review and executable plan — 2026-09-05

**Later owner decision:** the [ribbon-first UI decision](excel-ui-review.md#owner-decision-ribbon-first-worksheets-on-demand)
requires zero automatically created product worksheets. The mandatory snapshot
worksheet/chunk-table storage proposal below is retained as earlier preparation,
and is superseded on its worksheet requirement. Replan project persistence and
optional Excel output mapping before implementing WP10-05. Preserve canonical
snapshot bytes, identities, recovery, freshness, performance and real installed
acceptance; save/reopen must work independently of output sheets. The source
acquisition evidence remains valid, but the old storage mapping is not the new
implementation contract.

Preparation base: `0d790b56ba92a059b2cac574be970a2cf9106821`, the merged
[WP10-04 PR #972](https://github.com/Pravin-surawase/structural_engineering_lib/pull/972).
This is a source-backed implementation plan, not installed acceptance of a
command that does not exist yet. It changes no PF8/PF9 engineering requirement.

### What has actually used the applications

| Boundary | Evidence already retained | Next proof still required |
| --- | --- | --- |
| WP09 standalone Excel | [Installed acceptance](../../verification/wp09-excel-installed-acceptance.json) passed command, saved/reopened reconstruction, rollback and runtime-invalidation checks. The later [cleanup receipt](../../verification/wp09-excel-cleanup.json) records uninstall and removal of startup registration. | Load the new candidate XLL and test the new import in real Excel; do not assume the old XLL is installed. |
| WP10-02/03 ETABS | [Broker receipt](../../verification/wp10-03-operation-broker-evidence.json) binds a real getter-only acquisition: 410 calls, 48 operations, 820 journal records, 13 force rows, equal protected pre/post state and cleanup. | New live runs require fresh target/runtime/model/selection evidence; an old process ID is not current permission or identity proof. |
| WP10-04 normalization | [Receipt](../../verification/wp10-04-normalization-evidence.json) binds all 110 records and exact Python/.NET canonical replay without either application. | WP10-05 must preserve those bytes through Excel storage, reopening and reconstruction. |

Offline tests isolate conversion and failure logic; real application tests
prove the host boundary. Neither substitutes for the other. The review observed
an ETABS process and no Excel process, without attaching to either. This is
inventory only, not model readiness or a current installation verdict.

### Confirmed plan gaps and decisions

1. `WorkbookCommandKind`, `WorkbookCommands` and `StructAutomateRibbon` contain
   no `XL-CMD-02`. `WorkbookInputReader` reads only the three WP09 input tables.
   The private `WorkbookCommandEngine.Transaction` is reusable behavior, not
   a public importer. Implement the missing path and reuse one transaction
   owner; do not write an unrelated second rollback algorithm.
2. The retained snapshot is **1,669,798 bytes**, including large raw metadata.
   Microsoft specifies **32,767 characters per cell** and 15-digit numeric
   precision ([Excel limits](https://support.microsoft.com/en-us/excel/excel-specifications-and-limits)).
   Store canonical UTF-8 bytes as ordered base64 text chunks, at most 24,000
   characters each; do not put whole JSON in a cell or coerce canonical values
   through Excel numbers. An in-memory preparation diagnostic produced 93
   chunks and reconstructed SHA-256
   `b0379473f0e195c4a8e947b89218e0af4e1294f80e72824bd731d7fa65af627c`,
   equal to the receipt. This is byte-storage feasibility, not an Excel test.
3. Current WP09 cache identity covers its input records and runtime. A new
   snapshot must enter the linked-member input identity and all calculate,
   optimize, export and reconstruction checks. Merely writing an additional
   table would leave the existing cache unaware of the imported source.
4. The ETABS project is a library; source callers do not yet provide the
   versioned external acquisition host promised in the architecture above.
   WP10-05 imports a completed snapshot file. **WP10-05B** must provide the
   production acquisition entry point and connect its completed output to that
   importer before claiming the integrated Excel-to-ETABS workflow.
5. The current capture request names one member, and the projector requires
   one force getter. PF9 requires 100-member/10,000-row and
   1,000-member/100,000-row workloads. **WP10-05C** must freeze and implement
   a compatible multi-member profile and datasets before WP10-06 qualification.
   A repeated one-member fixture cannot satisfy either workload.

### WP10-05 plan card

| Plan row | Accepted planning decision |
| --- | --- |
| Outcome | `XL-CMD-02` imports one completed portable snapshot into a compatible saved workbook, displays its member/action/source facts, and reconstructs the same snapshot after save/reopen. Import completeness and design readiness remain separate. |
| Start | Open task `WP10-05`; fetch main explicitly, inspect canonical Git state, upstream, PR and sibling candidates, bind the then-current base SHA and create `codex/wp10-05-*`. Preparation's base is historical, not the future implementation base. |
| Scope | Initially one snapshot per workbook, with explicit snapshot-member to workbook-member bindings. Reimport atomically replaces the whole snapshot set; no mixed epochs. Preserve unrelated standalone members and user sheets. |
| Input | Canonical completed snapshot JSON, explicit expected file SHA-256, workbook/project identity and explicit member mapping. Use the exact WP10-04 retained output plus the invented shared normalization vector. A raw acquisition file or incomplete AO16 result is rejected, not normalized silently by Excel. |
| Reuse | `AnalysisSnapshotCodec.ParseAndValidate` and canonical hashing; WP09 table store, transaction/readback/rollback, input reader, cache checks, host-effect ledger, command/ribbon conventions and packaging helpers. Excel has no dependency on the optional ETABS assembly. |
| Product writes | Existing `StructuralEngineering.ExcelDna` project: contracts, table store, input reader, command engine, commands and ribbon; narrowly named snapshot reader/importer files and a shared transaction helper if extraction is needed. Existing Analysis API is consumed unchanged unless a confirmed blocking defect is separately planned. |
| Proof writes | `CSharp/tests/StructAutomate.Tests/Wp10WorkbookImportTests.cs` (planned), affected existing workbook tests, an additive `CSharp/packaging/excel/Invoke-SnapshotImportAcceptance.ps1` (planned) reusing `Common.ps1`, and a synthetic sample only if required. No private capture enters Git. Update only affected locks if the graph changes. |
| Records | This plan, implementation status, task/session/handoff and an installed-transition source declaration before final candidate. Candidate-bound installed receipts, workbook copies and hashes stay external after candidate. No post-push documentation commit. |
| Impact | .NET product/tests, documentation and repository checks; `verification plan` is authoritative when paths exist. Python WP10 evidence is included for reconstructed-snapshot parity, without unrelated Python/FastAPI/React suites. |
| Roles | One parent performs implementation, verification, essential review and delivery. No automatic subagents, new workflow engine, recurring automation or broad skill changes. |
| Non-goals | Live attachment, changing ETABS units/selections/lock/model, automatic design/check generation from material names, inferred strengths, centered geometry, automatic save of user workbooks, performance qualification, WP11 and release. |

### Storage, identity and transaction contract

Use an additive workbook extension ID `structural-excel-analysis-import/v1`;
keep WP09's standalone template usable. The following are planned controlled
tables, not names already supported by `ExcelWorkbookTableStore`:

| Table | Required role |
| --- | --- |
| `StructuralSnapshots` | Extension version, workbook/project and snapshot IDs, canonical/file/raw hashes, acquisition/model/analysis/epoch identities, chunk count/byte count, source version, import state and limitations. |
| `StructuralSnapshotChunks` | Snapshot ID, zero-based chunk index, base64 text and chunk digest. Reassembly requires contiguous unique indices, exact total length/hash and successful canonical snapshot validation. |
| `StructuralSnapshotMembers` | Member/object/element/section/material/axis and station mapping for review; preserve references to raw insertion point, releases, offsets and separate modifiers. |
| `StructuralSnapshotActions` | Every source row and canonical row ID, member/element/station/selection, action basis, step and all six signed components in explicit units. Numeric text uses invariant canonical spelling. |
| `StructuralSnapshotBindings` | Explicit source-member/workbook-member mapping, snapshot/action revision, binding state and unresolved design prerequisites. No label/name-based automatic match. |

Assign fixed `SA_` sheet names in the existing table-store registry, below Excel's
31-character sheet-name limit. The tables are projections of the canonical
payload. Readback must both reconstruct and validate the payload and rederive
the projected tables/bindings; matching chunks alone cannot approve edited
action cells. Persist references and bounded columns, not the oversized raw
metadata JSON. Blank/null and `Single Value`/null step semantics remain frozen.

The public command accepts a source file picker or explicit path/digest for the
installed harness and binds the target workbook once. Picker cancellation is
a no-write result. Read and validate the entire bounded file and build all
table values before the first mutation. Bind the limits below in the typed
importer contract; the initial profile admits the retained 1.67 MB file and the
synthetic vector and explicitly rejects larger unqualified scope, with no
truncation. Excel worksheet limits are not a
performance budget.

The initial file limit is 16 MiB, one source member and at most 10,000 action
rows; reject before mutation when any limit is exceeded. These are bounded
import admission limits, not qualified speed claims. Decode chunks only after
validating their total encoded length/count against those limits.

Preflight requires a saved writable local workbook, compatible template,
explicit project/member mapping, editable dedicated controlled ranges, and
room for every declared table. Reject conflicting sheets, unexpected table
headers/locations, formulas or unrelated content in a write footprint before
mutation. `IWorkbookTableStore` snapshots values; do not promise restoration of
arbitrary formulas/formatting by that interface. Preserve sentinel formulas,
comments and unrelated sheet content outside the declared footprint in the
installed proof.

One transaction covers the five snapshot tables, affected freshness records
and the receipt. Capture existing values and absent-table state, bulk-write,
read back, reconstruct, compare hashes/identities and only then return
`completed`. Failure restores every existing controlled value/table and
removes newly created controlled sheets; verify the restored state. Failed
restoration is `restoration_unverified`, never current or successful. Keep
failure receipts externally if writing a receipt would violate exact rollback.
Detect target closure or identity/content drift after progress yielding and
before commit; retain the original target rather than looking up a new
`ActiveWorkbook` midway through the operation.

Reuse the command's progress/cancellation mechanism on Excel's main thread.
Any background parsing must return to a macro context before Office access
([Excel-DNA guidance](https://excel-dna.net/docs/guides-advanced/performing-asynchronous-work/)).
Cancellation before mutation leaves all tables unchanged; during controlled
writes it completes verified rollback at the next safe boundary. Do not abort
inside a COM call or launch a second import from progress message processing.

### Freshness and engineering meaning

`import_verified` means the workbook matches a validated captured snapshot;
it does not mean the live model is current, or that the member design passes.
The existing source's owner-declared concrete classification contains no
proved concrete/rebar strength, cover, support design scope or selected bars.
Retain those missing prerequisites explicitly. Import may complete for review
while design readiness is blocked.

Linked calculations must bind the snapshot digest, mapping digest, action
revision and execution fingerprint into `WorkbookInputSnapshot`/cache identity.
Changing any binding, chunk, action projection, project or runtime invalidates
linked results, optimization and export. Existing WP09 standalone inputs with
no snapshot binding retain their behavior. Until a supported explicit action
mapping and complete design basis exist, linked Calculate/Optimize/Export
must return an actionable not-ready result; they may not run old sample actions
and label them as an ETABS-derived result. Automatic AO16-to-leaf-check request
synthesis is a separate later feature, not a hidden dependency of import.

### Acceptance-to-proof matrix

The class and harness named below are implementation deliverables; they do not
exist at preparation. Each test name/filter must be verified from source before
the freeze run. No zero-discovery or skipped retained-input pass is accepted.

| ID | Required proof |
| --- | --- |
| X1 | Public importer rejects wrong file SHA, corrupt/incomplete snapshot, incompatible workbook and ambiguous mapping before any table write. |
| X2 | Synthetic and exact retained inputs reconstruct identical canonical bytes from bounded text chunks; all 110 retained records and 13 actions remain accounted for. Missing/duplicate/edited chunks and edited projections block acceptance. |
| X3 | All six signs/units, source IDs, static step sentinel, stations, faces, insertion and separate modifiers survive import and reconstruction without another unit conversion. |
| X4 | Memory-store fault injection at each mutation boundary proves existing-table and new-table rollback, receipt behavior and explicit unverified restoration. Installed Excel repeats representative existing and newly created table failures. |
| X5 | Reimport and edited mapping/source/runtime invalidate linked calculate/optimize/export caches; incomplete design basis blocks linked operations. Existing standalone workbook cases remain passing. |
| X6 | Picker/prewrite cancellation has zero writes; cancellation after mutation rolls back; a second command or changed active workbook cannot redirect writes. Progress/cancel observations name actual safe boundaries. |
| X7 | The candidate's actual Ribbon and command registration load in installed x64 Excel. Import the retained file into a disposable saved workbook, save/reopen and reconstruct with the external source unavailable. Snapshot SHA and all projected rows match. |
| X8 | Installed forced failure preserves outside-scope formula/comment sentinels and existing tables, removes only created controlled sheets, and restores host settings. Record exact workbook/XLL/runtime/source/receipt hashes and owned-process cleanup. |
| X9 | Reconstructed UTF-8 JSON independently passes the existing Python WP10 validator/canonical replay. This and X7/X8 satisfy the new import's PF8 E5-05/E5-06 portion; fake Office tests alone do not. |
| X10 | New import causes zero ETABS calls; pure worksheet recalculation still has zero host effects. Evidence states import readiness separately from live freshness, engineering approval and acquisition performance. |

### Ordered implementation and verification

1. Freeze the extension's exact headers, size/scope bounds, typed request/result,
   receipt, binding/freshness rules and X1–X10 test mapping. Inspect current
   installed runtime/certificate availability without opening user workbooks.
2. Implement pure snapshot-to-table projection/reconstruction and the shared
   transaction use. Implement source binding/cache invalidation before adding
   the command/ribbon. Use narrow diagnostics only while fixing active issues.
3. Finish command, sample/harness, declared installed-transition source record
   and all versioned task docs. The planned harness must use explicit input
   and output paths and require actual execution of X7/X8; it must not rerun the
   entire WP09 cold/warm performance campaign. The existing broad
   `Invoke-InstalledAcceptance.ps1` has no snapshot-import parameters today.
4. Freeze content, format once from the original task base, and run the focused
   union below. Commit one immutable candidate after software evidence passes.
5. Package/sign **that exact clean candidate** using the maintained helpers;
   their packager already requires committed source. Install/load it, execute
   X7/X8/X9 against disposable copies, and retain new receipts externally.
   Versioned docs prepared in step 3 describe the required evidence and locator,
   not an unobserved installed pass. Installed failure consumes the ordinary
   consolidated rejection/repair path; never edit the candidate silently.
6. Review the unchanged candidate using software plus installed evidence,
   record acceptance, run one read-only integrity gate, let pre-push own final
   closeout, pass hosted CI, merge unchanged and record derived usage. No
   task-owned versioned writes follow `CANDIDATE` except explicit repair.

All commands below run from repository root unless the row says `CSharp`:

| Command / owner | Purpose and expectation |
| --- | --- |
| `bash ./run.sh verification plan --base <intake-sha>` | Route the entire changed candidate; reconcile all actual paths before freeze. |
| `bash ./run.sh format --write --base <intake-sha>` | Single affected-source formatting and full-task-base text hygiene. |
| `dotnet restore StructAutomate.slnx --locked-mode`, then `dotnet build StructAutomate.slnx -c Release --no-restore` in `CSharp` | Locked graph and packed x64 XLL; a build is not installed acceptance. |
| `dotnet test --project tests/StructAutomate.Tests/StructAutomate.Tests.csproj -c Release --no-build --filter 'FullyQualifiedName~Wp10WorkbookImportTests\|FullyQualifiedName~WorkbookCommandEngineTests\|FullyQualifiedName~WorkbookInputReaderTests\|FullyQualifiedName~ExcelAdapterTests'` in `CSharp` | New importer plus directly affected existing workbook behavior; verify the new class exists and test count is nonzero. The backslash shown before each pipe is Markdown table escaping, not a literal CLI argument. |
| `dotnet test --project tests/StructuralEngineering.Tests/StructuralEngineering.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Wp10` in `CSharp` | Frozen portable contract and normalization compatibility. |
| `bash ./scripts/python_runtime.sh scripts/validate_structural_engineering_contracts.py` and `bash ./scripts/python_runtime.sh -m pytest Python/tests/unit/test_structural_engineering_wp10.py -q` | Contract and cross-runtime fixture parity. Separately validate the actual reconstructed installed output through the same production Python codec. |
| `bash ./run.sh check --category docs`, `bash ./run.sh efficiency check`, `bash ./run.sh session handoff`, `bash ./run.sh session check` | Run handoff/check after final session writes and before candidate; no global doc sync. |
| Existing packaging scripts under `CSharp/packaging/excel` | `New-Distribution.ps1 -OutputDirectory <fresh-repo-tmp-path> -CertificateThumbprint <verified-current-cert> -SkipBuild`; `Test-Preflight.ps1 -DistributionDirectory <path> -ReceiptPath <per-user-receipt-path>`; `Install-PerUser.ps1 -DistributionDirectory <path>`. Verify the current signatures before execution. |
| Planned `Invoke-SnapshotImportAcceptance.ps1` | Implement and freeze explicit XLL/workbook/snapshot/digest/receipt arguments in step 1. Default output stays under the permitted per-user receipt root; immutable evidence copies may then be retained externally. Do not call guessed parameters on the existing WP09 harness. |

No entire broker test class runs on this installed workstation: it contains
live ETABS entry points. No unchanged broad Python/full-32 gate is added here;
the final WP10 cumulative gate belongs to WP10-06 after prerequisites. Hosted
required checks are never bypassed.

### Installed entry, unattended work and remaining sequence

At the application gate, establish Windows/Excel x64 build, .NET Desktop runtime,
actual XLL hash/signature, certificate trust, package manifest and exact saved
disposable workbook path/hash. Historical validation-certificate and WP09
installation receipts are not current installation proof. Preserve any existing
add-in installation and registration preimage before replacement; target only
the task-owned workbook and Excel process. Preserve source artifacts read-only.

The owner has authorized ordinary in-scope implementation and application work.
Routine decisions do not require another permission question. Expected file
pickers are avoided by explicit harness paths. License/sign-in, trust/protected
view, a locked session, unexpected save/recovery dialogs, busy Excel, unknown
target identity or user-owned unsaved work are real entry/runtime conditions:
record a hold, retain evidence, and request assistance only if they cannot be
resolved within existing authorization. Never click through an unknown dialog,
alter global trust, or terminate a user application to force unattended success.
Long waits return status without speculative retries. One implementation
session is a target after host readiness, not a guarantee of completion while
the user sleeps.

**WP10-05B** then owns the missing production acquisition host: a small optional
Windows executable/file protocol around existing broker and normalization APIs,
exact target/request/output identities, terminal-state/cancellation semantics,
and handoff into the same importer. No CSI/Office access in worksheet functions;
no new Git/session automation. Freeze its own plan and tests before coding and
prove one real getter-only end-to-end smoke run after host preflight. A test
method is not the released acquisition entry point.

**WP10-05C** owns a separately frozen multi-member profile. Resolve collection
scope, shared catalogue acquisition, per-member material/geometry/element
coverage, complete row accounting and one coherent analysis epoch without
changing the meaning of existing v1 evidence. Create actual small/medium
dataset manifests with member/row counts and hash-bound source identities;
do not just loop the retained one-member sample and report a building-scale
result. Profile stage costs before choosing batch sizes. Any schema extension
receives explicit compatibility vectors and its own acceptance update.

**WP10-06** starts only after 05/05B/05C have passed their own boundaries. It
qualifies the unchanged integrated candidate against PF8 E5-02/E5-03/E5-04 and
rechecks the connected Excel E5-05/E5-06 path. PF9 remains the authority:
small 100 members/10,000 rows p95 <= 5 s; medium 1,000 members/100,000 rows
p95 <= 30 s; incremental medium adapter working set <= 512 MB, with getter,
transfer, normalization and persistence times separate. These are unproved
targets today. Run the named cumulative broad Python/full-32 gate there once
the whole candidate freezes; preserve every failed performance verdict and
profile its cause instead of reducing required counts or weakening correctness.

Stop/replan on an unsupported workbook schema, source/storage ambiguity,
unresolved linked action semantics, host drift, outside-scope write, failed
cleanup, absent installed proof or a second rejected candidate. The plan is
feasible for the supported import boundary; it does not yet prove full-model
coverage, unattended host operation or the final performance targets.

## WP10-02 single-session execution contract

### Entry card — pass before opening the implementation timer

WP10-02 does not start until every entry row is known. A missing row is a
preflight hold, not an invitation to start coding and repair later.

| Entry row | Required evidence |
| --- | --- |
| Repository | clean feature-lane base, local/remote/live `main` equality, no operation, and no overlapping active candidate |
| Delivery controls | efficiency policy plus focused replan, derived-state, pre-push, hosted-rejection, and automatic-closeout tests pass |
| Frozen portable authority | `operations/wp10.json`, `schemas/wp10.schema.json`, and `conformance/wp10-vectors.json` validate and their version-1 meaning is unchanged |
| Runtime | Windows x64, .NET SDK 10.0.400, ETABS 23.3.1.4563, ETABSv1.dll file version 2.16.0.0, and x64 type library identities are freshly measured |
| Active host | exactly one user-selected ETABS process has the intended saved, analysed model open; its process start, executable, model path, file identity, lock, units, analysis status, and output selection are recordable |
| Request | exact model expectation, member selection, station mode, result cases/combinations, required result kinds, deadline, and evidence path are fixed before attachment |
| Prior evidence | W3B/W3C/W3D evidence is discovery material only; it is never reused as a current process, model, result-epoch, or compatibility claim |

Passive readiness observed on 2026-09-04 found the expected executable,
managed assembly, and x64 type library at their installed paths. Their versions,
byte counts, and SHA-256 values match the retained W3B static evidence, and
.NET SDK 10.0.400 is available. No ETABS process was running. This proves that
the machine can be prepared; it does not pass the active-host row or establish
live compatibility. Before WP10-02 begins, the user must open exactly one saved
model with current analysis results and the intended output selections already
set. The adapter is forbidden from creating that state.

### Fixed source and evidence budget

The intended product paths are fixed before implementation:

- `CSharp/src/StructuralEngineering.Etabs/StructuralEngineering.Etabs.csproj`;
- a narrow getter port, exact host probe, and exact-version getter adapter under
  `CSharp/src/StructuralEngineering.Etabs/`;
- `CSharp/tests/StructAutomate.Tests/Wp10GetterAdapterTests.cs` and one project
  reference from its existing Windows test project;
- one project entry in `CSharp/StructAutomate.slnx`;
- `docs/verification/wp10-02-host-microprobe-evidence.json`;
- this plan, implementation status, newest session entry, and generated handoff.

No vendor DLL, generated interop wrapper, model, workbook, result export, or
machine-specific absolute dependency is committed. The default locked solution
must restore, build, and run fake-host tests on a clean Windows runner without
ETABS installed. The live binding separately loads and verifies the exact
installed assembly identity. If the micro-probe proves that this build strategy
cannot preserve the installed parameter directions and return shapes, change
the contract before implementation instead of adding an unreviewed workaround.

### Ordered work — no speculative implementation

1. **Admit the lane.** Start `WP10-02`, create its feature lane, bind this
   acceptance file, and record the exact base before any product write.
2. **Run the micro-probe.** Inspect file/assembly/type-library identities, bind
   the exact selected process, establish the supported attachment path, reflect
   the proposed getter signatures and enum values, read model identity, and
   release all acquired references deterministically. Record no compatibility
   claim and make no model or selection call that can mutate state.
3. **Freeze the getter matrix.** For every allowed call, record interface,
   member, parameter order/direction/type, enum values, output order and shape,
   CSI return-code position, required input identity, and normalized evidence
   destination. Freeze a deny list covering setters, unlock, analysis, design,
   save, close, and exit before writing the adapter.
4. **Build the host boundary offline first.** Implement the port, strict result
   decoders, exact version guard, call whitelist, and fake scalar/list/array,
   failed-return, unequal-array, timeout, and identity-drift cases. Consume the
   WP10-01 records without changing their wire meaning.
5. **Run one getter smoke path.** Attach to the exact process; prove runtime,
   model filename, lock, units, analysis status and output selection; call no
   force getter while any readiness value is absent, stale, or unexpected.
6. **Run the reviewed functional matrix.** Read the approved metadata,
   topology, assignment, axis/mapping, selection, and `Results.FrameForce`
   getters. Persist exact raw outputs and call identities; do not normalize or
   expose a partial accepted snapshot in WP10-02.
7. **Prove postflight equality.** Re-read process/model/file/lock/units,
   analysis/result and output-selection state, require byte/identity equality,
   close the call ledger, and release the broker/COM boundary. Any uncertain
   cleanup is `RESTORATION_UNVERIFIED`, never success or automatic retry.
8. **Freeze once.** Finish product, tests, evidence, status, session record and
   handoff; run changed-path formatting once and the focused checks below once.
9. **Review and publish once.** Create one candidate, obtain one consolidated
   independent decision, run candidate integrity once, let pre-push close the
   session once, and use one hosted PR cycle. A rejection uses the one bounded
   repair; another rejection requires a changed-contract replan.

### Stop rules that prevent repair cycles

Stop before product writes when the active host, saved model, request, output
selection, version/hash, attachment path, or full getter matrix is ambiguous.
After product writes, stop and replan rather than patch around any of these:

- installed signature, parameter direction, enum, return-code, or output-shape
  mismatch;
- a required setter or a hosted build that needs an unavailable vendor binary;
- unsaved/multiple/wrong model identity, stale results, or absent/drifted
  selection;
- any setter, unlock, analysis, design, save, close or exit entry in the ledger;
- process, file, lock, units, analysis/result, or selection postflight drift;
- unpaired calls, timeout/COM uncertainty, failed cleanup, or partial evidence;
- any semantic or canonical-identity change to the frozen WP10-01 authority;
- changed files outside the fixed budget without an explicit acceptance update.

### WP10-02 installed getter-matrix replan — 2026-09-04

The exact-version C# micro-probe attached successfully to the prepared process,
but the first functional attempt stopped when `FrameObj.GetElm("82")` returned
CSI status `1`. Earlier W3H material proved only that member's installed static
signature; it did not prove a successful live return for this model. No force
call had been issued by that stopped attempt and no partial capture was
accepted.

The frozen WP10-02 whitelist therefore excludes `FrameObj.GetElm`. The already
reviewed `Results.FrameForce` return shape supplies the source object, object
station, analysis element and element station on every force row. After the
readiness gate, the probe obtains the exact analysis-element identities from
those same rows and verifies each one with `LineElm.GetObj`, `GetPoints`,
`GetLocalAxes`, and `GetTransformationMatrix`. A direct bounded getter check
proved 13 rows for object `82`, all owned by object/element `82` and the exact
selected combination `117.(1.5DL+1.5LL)`. This is the required mapping evidence,
not a fallback inference or retry. Any failure or disagreement in those paired
fields still blocks the complete capture.

The first candidate-bound shape pass then stopped before force access because
`Story.GetStories_2` returned a correctly counted managed `String[]` whose
`SimilarToStory` array contains CLR-null reference elements. Static reflection
cannot establish element nullability. WP10-02 therefore permits and retains
null elements only for this proved `SimilarToStory` managed string-array
output; it neither coerces them to blank strings nor interprets them. Nulls in
scalar strings, other string arrays, or value-type arrays remain invalid, and
WP10-04 must explicitly normalize or block the semantic destination. A focused
fake-host case freezes this exact raw-shape rule.

### WP10-02 candidate audit repair — 2026-09-04

The first immutable candidate was rejected once by the consolidated essential
review. One bounded repair now backs the public whitelist with a true read-only
dictionary, binds the sole nullable string-array index into the matrix digest,
checks exact installed parameter names as well as type and direction, attempts
release of every acquired COM reference before aggregating any cleanup errors,
and makes the live matrix enforce its cross-getter evidence rather than merely
record it. The force rows must all name the requested object and exact selected
case/combo set; returned analysis elements must form one connected graph across
the two frame endpoints; the basic and extended case-type getters must agree;
and the section/material getters must agree. The repaired candidate must repeat
only its affected build, ten fake-host tests, changed-path formatting, and one
final installed matrix. A second rejection still requires `REPLAN`.

The first repaired candidate then reached the mandatory read-only integrity
gate, which found mixed line endings in the solution, test project, and test
lock file plus a missing final newline in the adapter lock file. Those files
entered with the original candidate, while the repair formatter correctly
selected only the five source files changed since that candidate. This is a
delivery-path defect, not an ETABS behavior defect. Design revision 2 therefore
adds the full task base (`419941c7d361c6ad2ba240b3c4d7662923ef59d5`) to the
text-hygiene selection, normalizes only the four reported files to repository
LF/EOF policy, repeats only the affected build/test/session evidence, and then
creates one replacement candidate. Another rejection remains a hard stop.

Hosted run `33905189848` then reproduced the remaining platform boundary: the
Windows checkout converted the five changed `.cs` files to CRLF because
`.gitattributes` declared them only through `text=auto`, while the maintained
.NET formatter requires LF. Local source files had been LF and all product
checks passed, so this was not a source-format or ETABS behavior defect. The
bounded hosted repair adds explicit LF policy for `.cs`, `.csproj`, and `.slnx`
files, renormalizes the full task diff, repeats only changed-.NET formatting and
the directly affected build/tests, then republishes one replacement head.

### Focused freeze matrix

Run this union only after content freezes; use a narrow reproducer earlier only
to diagnose the current implementation. Do not add an unchanged quick/full gate
between these checks and the candidate.

```bash
./scripts/python_runtime.sh scripts/validate_structural_engineering_contracts.py
./scripts/python_runtime.sh -m pytest Python/tests/unit/test_structural_engineering_wp10.py -q
(cd CSharp && dotnet restore StructAutomate.slnx --locked-mode)
(cd CSharp && dotnet build StructAutomate.slnx -c Release --no-restore)
(cd CSharp && dotnet test --project tests/StructAutomate.Tests/StructAutomate.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Wp10GetterAdapterTests)
./run.sh format --check --scope dotnet
git diff --check
./run.sh session check
```

The candidate is acceptable only when the matrix passes, the exact live getter
ledger and postflight equality pass, the default solution remains independent
of installed vendor binaries, WP10-01 fixture identities are unchanged, and
the evidence states its exact-host limitation. Comprehensive cross-domain
assurance remains the single hosted PR run.

### Recurrence controls applied to WP10-02

| Recurrence | Preventive rule |
| --- | --- |
| RR-001/RR-002 | one bounded slice and one frozen getter matrix; do not combine broker, normalizer, Excel or qualification work |
| RR-003 | format changed source once before candidate; integrity is read-only and runs once after audit acceptance |
| RR-004 | admit intake before the timer and use only executable delivery transitions through post-merge closeout |
| RR-005 | use repository-root maintained launchers, exact literal Windows paths, and one shell shape per command; no wildcard or mixed-shell probes |
| RR-006 | no preparation closeout; pre-push owns one idempotent final session verdict |
| RR-007 | preserve the already-qualified PF4 Unicode canonicalization and shared fixture identity |
| RR-008 | one candidate plus one repair ceiling; changed acceptance digest is required after a second rejection |
| RR-009 | add/fetch the exact task-branch refspec before asserting upstream equality |
| RR-010 | update recurrence count, basis, last-seen task, session row, and generated handoff as one pre-freeze set |
| RR-011 | use the maintained changed-path formatter; never replace it with a whole-solution or ad hoc formatting command |
| RR-012 | every repair and replan retains the original task-base SHA and full task-touched path union |
| RR-013 | formatter-owned C# extensions retain explicit repository LF policy and local/hosted formatter parity |

## Frozen performance workloads

`BENCH-ETABS-SMALL` contains 100 physical members and 10,000 force rows;
`BENCH-ETABS-MEDIUM` contains 1,000 physical members and 100,000 force rows.
Rows may not be duplicated or padded to meet those sizes. Before timing, each
workload freezes the source-model byte identity, analysis/result epoch, output
selection, requested members, expected raw-row count, and normalized snapshot
identity. Run at least one untimed acquisition and ten measured acquisitions
per workload, retain every sample, and calculate p95 by the repository's named
percentile rule.

The certified-host budget is small p95 at most 5 seconds and medium p95 at most
30 seconds. Report getter, COM transfer, validation, raw persistence, offline
normalization, and final persistence separately. The medium adapter working-set
increase must be at most 512 MiB. A timing sample counts only when its return
codes, array shapes, row accounting, snapshot identity, and postflight state all
pass; a faster incomplete acquisition is a failed correctness sample.

## First implementation packet

`WP10-01` freezes the portable boundary before any CSI or Excel code is added.
It will add the AO16 request/result, raw capture, call-ledger, source identity,
row disposition, action row, unit/axis/mapping, diagnostic, and
`structural.analysis_snapshot/v1` contracts to the host-free .NET surface. It
will derive shared strict JSON fixtures from the existing Python contracts and
retained ETABS evidence, then require Python and .NET to accept the same valid
fixtures, reject the same malformed/partial fixtures, produce the same
canonical snapshot digest, and detect payload tampering. The packet contains no
CSI reference, COM call, workbook mutation, or live compatibility claim.

The next packet may start only from those versioned schemas and conformance
fixtures. This prevents installed API details, workbook cells, or an older
application-specific force batch from becoming the reusable library contract.

## WP10-01 frozen contract and acceptance matrix

WP10-01 owns only portable records and offline replay. The authored authority
is `contracts/structural-engineering`: `operations/wp10.json` fixes AO16's
meaning, `schemas/wp10.schema.json` fixes the strict wire shape, and
`conformance/wp10-vectors.json` is the one shared Python/.NET fixture. Python
projects those records through `structural_lib.analysis_snapshot`; .NET keeps
the records in `StructuralEngineering.Contracts` and replay/validation in
`StructuralEngineering.Analysis`. None of those packages references CSI,
Excel-DNA, COM, a workbook, a process-attachment API, or a filesystem adapter.

The snapshot contract freezes these boundaries:

- AO16 requests use explicit source expectations, member/station selection
  modes, selected result identities, required result kinds, deadline, and
  optional evidence records. `absent`, `null`, `blank`, and zero are never
  interchangeable; optional engineering evidence carries its state, value,
  and reason instead of relying on a language default.
- Raw capture retains source/runtime/model/analysis/result identity, original
  units and conversion factors, ordered model records, ordered force rows, and
  a hash-chained `started`/`returned` getter ledger. A returned call has one
  reviewed signature identity, exact return code, and raw shape. An unmatched
  start, non-getter effect, failed return, gap, or digest mismatch fences the
  operation and emits no canonical snapshot.
- The normalized snapshot uses millimetres, kN, kNm, N/mm2, and kg/m3. It
  contains model metadata, points, materials, sections, member assignments,
  modifiers, offsets, releases, axes/face evidence, load cases, combinations,
  selected results, physical/object/element stations, and same-row signed
  P/V2/V3/T/M2/M3 actions with force-result provenance.
- Every raw model or force record has exactly one `accepted`,
  `approved_exclusion`, or `blocked` disposition. Accepted rows bind a
  canonical identity; an exclusion requires a reason and approval reference;
  any blocked row prevents `complete_for_scope` and exposes no partial
  canonical snapshot.
- Snapshot and raw-capture SHA-256 values use PF4 canonical UTF-8 JSON with
  ordered keys, preserved array order, canonical enum strings, unescaped
  non-ASCII text including U+2028/U+2029, negative zero normalized to `0`, and their own
  derived id/digest fields omitted from the corresponding hash basis. Arrays
  use deterministic identity/ordinal ordering. Acquisition time remains in the
  artifact identity but does not become a normalized engineering input.
- AO16 results keep execution, applicability, engineering, completeness,
  freshness, approval, and operation state independent. Snapshot acquisition
  is not an engineering pass: a valid replay is `completed`, `applicable`,
  `not_evaluated`, `complete_for_scope`, `current`, and `unreviewed`.

| Acceptance row | Required outcome |
| --- | --- |
| Valid shared fixture | Both languages accept the exact payload, reconstruct the same snapshot id/digest and produce identical canonical full-payload byte hash and length. |
| Strict structure | Missing required or unknown fields, duplicate JSON keys, invalid enum tokens, non-finite numbers, and invalid conditional optional values return `rejected_input` with `INPUT.SCHEMA`. |
| Tamper detection | A changed engineering/source/ledger value without the corresponding identities returns the matching hash/ledger diagnostic and no snapshot. |
| Source and result freshness | Model, analysis, result epoch, and selected-result identities must agree throughout the source, freshness, selections, stations, actions, and raw capture. |
| Units and axes | Conversion factors are positive and consistent; axes and transforms are orthonormal/right-handed; physical-face evidence is explicit. Failure returns `AXIS.UNRESOLVED` or `UNITS.INVALID`. |
| Mapping and row conservation | Every reference resolves, every raw row is dispositioned once, accepted/excluded counts reconcile, and blocked/unresolved data cannot yield a partial accepted snapshot. |
| Dependency boundary | Pure Python/.NET projects load and test without CSI, ETABS, Excel, COM, model mutation, solver, or optimization dependencies. |
| Documentation | Normal Python and .NET callers can load, validate, serialize, and replay the portable fixture without an installed host. |

The focused freeze commands are the structural-contract validator, the WP10
Python tests, the host-free .NET test project, Python format/lint for changed
files, `dotnet format --verify-no-changes`, and `git diff --check`. After those
pass and the task records are final, create the immutable candidate, obtain its
independent audit decision, and run candidate integrity once on the accepted
head. WP10-02 may consume these records but may not change their version-1
meaning while binding installed getter signatures.

## Acceptance

WP10 closes when one unchanged candidate proves all of the following:

- the CSI dependency exists only in the optional adapter/broker and pure
  Python/.NET snapshot consumers run without ETABS or Excel;
- the exact installed assembly signatures, parameter directions, return codes,
  enum values, and parallel-array shapes match the reviewed getter matrix;
- attached acquisition records identical process, model, file, lock, units,
  analysis epoch, and output-selection state before and after, with a call
  ledger containing no setter, analysis, design, save, close, or exit call;
- missing selection, stale results, identity drift, timeout, COM loss, invalid
  units, unequal arrays, mapping ambiguity, or unresolved axes fail closed
  before an accepted snapshot and leave no partial canonical result;
- every accepted force row retains source object/element/station, case or
  combination, step type/number, concurrency basis, and all six signed action
  components in explicit units;
- the captured raw artifact deterministically replays to the same Python and
  .NET snapshot identity without COM, and tampering changes or invalidates that
  identity;
- `XL-CMD-02` imports the snapshot through the WP09 transaction boundary,
  survives save/reopen, and restores the exact workbook preimage on forced
  failure; and
- installed E5-02/E5-03/E5-04 evidence and raw small/medium acquisition timing,
  memory, source/artifact hashes, runtime fingerprints, and budget verdicts are
  retained.

WP10 does not apply a candidate, change the attached model, invoke analysis or
design, or claim compatibility beyond the exact qualified tuple. WP11 first
exposes useful multi-option fixed-action candidate domains in Excel, then adds
controlled copied-model mutation and reanalysis. Public package publication
remains subject to the separate release authorization and gates.
