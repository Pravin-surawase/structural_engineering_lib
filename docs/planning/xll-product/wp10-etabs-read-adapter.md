**Type:** Architecture
**Audience:** Developers
**Status:** Ready
**Importance:** Critical
**Created:** 2026-09-04
**Last Updated:** 2026-09-04

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

The six delivery slices are separate bounded tasks. They are not one combined
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
later session. WP10-02 is the next such session. Later slices may share the
IMP-M3 milestone branch only when their accepted authority and installed-host
gate are unchanged; they retain separate task timers and acceptance decisions.

| Session | Complete outcome | Must not leak into the session |
| --- | --- | --- |
| WP10-02 | exact-version getter port, binding, fake-host proof, and one live getter-only matrix | broker retries, normalization, Excel, performance |
| WP10-03 | STA lease, deadlines, durable raw capture, call ledger, postflight, cleanup | normalization and workbook writes |
| WP10-04 | complete offline normalization and row conservation from captured raw artifacts | COM and Excel |
| WP10-05 | transactional `XL-CMD-02` import, readback, rollback, and freshness | ETABS mutation and qualification claims |
| WP10-06 | E5-02–E5-04 plus small/medium installed acquisition qualification | WP11 copied-model mutation or release |

The operating target for every session is one candidate, zero repair batches,
zero focused-check retries, one candidate-integrity run, one final closeout,
one hosted run, and less than ten percent writer-rework time. A real defect is
not hidden to meet the target; the delivery state machine records it and stops
after its bounded repair allowance.

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
