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
design re-planning before more implementation. Installed evidence is generated
only after the functional source candidate is stable. Before the final commit,
run `./run.sh check --candidate-integrity`, rebind any repository-facing
identity affected by normalization, and rerun the command clean. The final
read-only `session end` precedes the push; the task timing closeout follows
post-merge verification.

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
  ordered keys, preserved array order, canonical enum strings, and their own
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
pass and the task records are final, candidate integrity runs once before the
immutable reviewed candidate is created. WP10-02 may consume these records but
may not change their version-1 meaning while binding installed getter
signatures.

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
