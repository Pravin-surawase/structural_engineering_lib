**Type:** Review
**Audience:** Developers
**Status:** Complete
**Importance:** Critical
**Created:** 2026-09-04
**Last Updated:** 2026-09-04

# WP09 duration and rework postmortem

## Decision

WP09 reached the correct product outcome, but its delivery shape caused
avoidable rework. It combined six substantial surfaces in one milestone:

1. the native Excel-DNA adapter and public functions;
2. workbook transactions, freshness, migration, rollback, and caching;
3. the sample workbook and user commands;
4. package, signing, install, repair, and uninstall automation;
5. installed Excel functional, performance, and lifecycle qualification; and
6. evidence, review, repository closeout, and the WP10 handoff.

The merged change contained 60 files, 7,553 insertions, and 210 deletions. The
first product commit was followed by 13 product repair commits before the
installed source candidate stabilized, then evidence/session repairs and one
hosted-integrity repair. The usage closeout records 14 repair batches across the
whole milestone. This was not a small adapter edit. The scope should
have been executed as bounded tasks under one milestone branch, with the
installed application and final candidate as explicit boundaries.

The strict installed checks were valuable. They found real defects in startup
registration, COM lifetime, currentness, legacy migration, controlled-sheet
handling, rollback comparison, and cold readiness. Weakening those gates would
have produced an unreliable add-in. The avoidable cost came from discovering
acceptance and host assumptions after implementation, freezing evidence more
than once, and deferring one hosted-equivalent repository check until after the
PR was opened.

## Evidence and time interpretation

The user-visible record reports about 6 hours 30 minutes. The repository usage
ledger later reconstructed 396.381 minutes from task start through exact
post-merge closeout. These figures are wall/session observations, not a precise
measure of active coding time. The transcript was compacted repeatedly, so
minute-level attribution would be false precision.

The defensible attribution is:

| Category | Estimate | Basis |
|---|---:|---|
| Necessary implementation and real installed qualification | about 3 h 15 m to 4 h | adapter/package construction plus valid Excel lifecycle, migration, rollback, performance, and cleanup failures |
| Preventable rework | about 2 h to 2 h 45 m | late host preflight, serial contract discoveries, repeated evidence freeze/rebind, session-document repairs, and the second hosted cycle |
| Environment, coordination, and timing uncertainty | about 30 m to 1 h | Windows/PowerShell command retries, review coordination, CI/network wait, and transcript timing limits |

The ranges express uncertainty and are not additive endpoints. They support the
main conclusion: at least roughly two hours could have been avoided without
removing any engineering assurance.

## Timeline

| Time | Outcome | Classification |
|---|---|---|
| 10:01–11:51 | plan reconciliation and first complete adapter/package candidate | mostly necessary implementation |
| 11:51–12:28 | PowerShell defaults, active-workbook registration, preflight location, and startup loading | preventable late host/lifecycle discovery mixed with valid repair |
| 12:28–14:44 | COM cleanup, cold boundary, runtime currentness, schema migration, controlled-sheet reuse, matching rollback evidence, and final cold fix | mostly necessary installed qualification; several acceptance contracts arrived too late |
| 14:44–15:50 | immutable installed candidate, repeated acceptance, cleanup, evidence, full repository gate, and audit closeout | necessary qualification plus avoidable evidence/session sequencing |
| 15:50–16:17 | PR, hosted EOF failure, normalization, evidence rebind, second hosted run, and merge | preventable hosted rework |

## Root causes and durable controls

| Root cause | Observed consequence | Control from this review |
|---|---|---|
| One task bundled several product boundaries. | Each repaired layer invalidated assumptions and evidence in later layers. | Execute the existing delivery slices as separate bounded tasks on one milestone branch. Use one cumulative PR only after the intended slices are complete. |
| The executable acceptance matrix was completed during implementation. | Runtime fingerprinting, legacy migration, controlled-sheet semantics, rollback comparison, and cold-ready boundaries appeared as serial repairs. | Freeze contracts, failure rows, fixtures, performance boundaries, and commands before production code for each slice. |
| Installed-host assumptions were tested after the package existed. | PowerShell 5.1 defaults, active-workbook requirements, startup registration, and COM automation behavior caused repeated package repairs. | Run an exact-host micro-probe before the host adapter: versions, signatures, attachment/loading, one smoke operation, cleanup, and forbidden-call audit. |
| Evidence was written before the source and installed behavior were stable. | Later fixes made earlier receipts stale and forced repeated freeze/rebind cycles. | Generate completion evidence only after functional acceptance passes on a stable source candidate. Treat an outcome-changing repair as a new candidate and rerun only affected evidence. |
| Local broad validation omitted the hosted manual all-files hooks. | PR #963 first failed only for missing terminal newlines in two NuGet lock files and one rollback receipt. Normalization then changed a hash-bound receipt and required a second hosted run. | `./run.sh check --candidate-integrity` now executes the exact hosted manual hook stage before candidate commit. If it writes, rebind only affected repository identities and rerun clean. |
| Independent findings arrived across repeated candidate states. | Thirteen source repairs plus later closeout repairs obscured the point at which the candidate was actually frozen. | Audit one locally passing immutable candidate and return one consolidated blocker list. Allow one consolidated repair candidate; a second rejection triggers re-planning. |
| `session end` sounded final while timing remained open. | The next task initially could not start because WP09 still had an unmatched timing checkpoint. | The command and duplicate-start error now state that timing remains open. Record exact closeout after merge before starting the next task. |
| Windows shell assumptions were embedded in ad hoc commands. | Variable expansion, wildcard, execution-policy, revision-suffix, and certificate-store commands had to be retried. | Use maintained scripts for product operations, literal PowerShell blocks for nested commands, exact discovered paths, and one shell from discovery through mutation. |

## Detailed issue and recurrence ledger

The compact [rework and recurrence index](../../verification/rework-recurrence-index.json)
stores each recurring pattern's ID, count, observed-time basis, short control,
and links back to this detailed record. Future session logs reference the ID and
current count/time rather than copying the explanation or solution again.

No source records active minutes per defect. The cost column therefore records
retries, invalidated evidence, or repeated repair stages instead of invented
durations. A product defect is a useful acceptance finding. A process mistake
is work that an earlier contract, preflight, or maintained command could have
prevented.

| Area | Class | Issue or mistake | Observed cost or repetition | Prevention now required |
|---|---|---|---|---|
| Scope | Process mistake | WP09 combined adapter, workbook engine, sample, packaging, installed qualification, and closeout. | One defect could invalidate work across six surfaces. | Execute bounded delivery slices on one milestone branch. |
| Planning | Process mistake | The plan still described adapter work as future after part of that surface existed. | Reconciliation occurred at task start and product boundaries changed during delivery. | Reconcile plan, current source, and acceptance rows before the first edit. |
| Architecture | Product defect caused by late boundary review | The first adapter retained demo/application orchestration instead of projecting reusable library contracts. | The public Excel surface required restructuring and a fresh kernel/bridge review. | Freeze the application-versus-library responsibility matrix before adapter code. |
| Batch state | Product defect | Early batches used unstable grouping or repeated result identities. | Calculation, export, and rollback evidence had to be regenerated. | Define stable member, operation, result, and batch identities in fixtures first. |
| Export | Product defect | A failed export path could overwrite or mis-bind prior successful content. | Failure-path repair and focused rerun. | Freeze preimage, write transactionally, read back, and bind the export receipt. |
| Excel limits | Product defect | Cell-size and content-verification behavior was discovered in the live workbook path. | Workbook command repair and repeat acceptance. | Include maximum cell payload and exact readback examples in the workbook contract. |
| Freshness/cache | Product defect | Cache and currentness identity initially omitted engine/runtime facts. | Several repairs culminated in runtime-fingerprint invalidation. | Define every freshness input and invalidation example before optimization. |
| COM lifetime | Product defect | Excel/.NET COM objects outlived their intended scope. | Orphan-process and memory investigations plus repeated installed runs. | Make every acquired COM object and process owner explicit in the host micro-probe. |
| PowerShell compatibility | Process mistake | Packaging defaults relied on PowerShell 7 or invocation-sensitive `$PSScriptRoot` behavior. | One package repair immediately after the first feature commit. | Parse and smoke every packaging script in PowerShell 5.1 and 7 before packaging logic expands. |
| Excel registration | Process mistake | `AddIns.Add` was attempted without the active workbook state required by Excel. | One package repair and installed rerun. | Put active-workbook creation and cleanup in the host preflight fixture. |
| Excel startup | Process mistake | COM automation did not reproduce normal startup loading, so explicit registration/loading was added late. | One startup repair and lifecycle rerun. | Prove startup registration, direct load, repair, and uninstall in the first package smoke. |
| Host cleanup | Product defect | COM resource ownership and cleanup evidence were initially imprecise. | Resource-release repair and repeat installed run. | Require postflight process count and deterministic release in every smoke result. |
| Cold performance | Late acceptance boundary | Prerequisite scans, AddIns checks, and other post-ready work entered the cold timer before the ready boundary was fixed. | Three cold-readiness repairs, followed by ten-sample reruns. | Name start/stop events and keep prerequisite/postflight probes outside the timed interval. |
| Cold performance | Product defect | The ready path created an unnecessary bootstrap workbook. | Final source repair before the immutable installed candidate. | Profile only after the boundary is frozen; remove work that is not needed for the declared ready state. |
| Schema migration | Late acceptance contract | Legacy 9/13-column tables had no route to the new 10/14-column runtime identity. | Audit rejection, migration repair, and installed rerun. | Freeze every supported old schema and expected migrated bytes before implementation. |
| Controlled sheets | Product defect | Formatting-only `UsedRange` cells were mistaken for user content. | Installed migration false failure and source repair. | Distinguish values/formulas from formatting in controlled-sheet preimages. |
| Rollback comparison | Harness defect | Legacy recalculation was compared with a later candidate-evaluation result set. | False acceptance failure and harness repair. | Capture and compare evidence at the same named calculation boundary. |
| Percentile | Prevented process mistake | A p95 relaxation was considered when ten samples made nearest-rank p95 equal the maximum. | Review rejected the change before the gate was weakened. | Freeze the percentile rule and sample count with the budget. |
| Memory | Real measurement uncertainty | Identical final-candidate runs recorded 136.418, 275.438, and 202.059 MiB. | Three full installed observations; one failed only memory. | Retain all samples and investigate only with an unchanged boundary and candidate. |
| Certificate cleanup | Host/tooling issue | Standard trusted-store removal opened a confirmation dialog. | Two blocked cleanup attempts before exact registry-key removal and readback. | Preflight a noninteractive exact-thumbprint cleanup path and verify all stores read-only. |
| Change classification | Expected fail-closed control encountered late | Intended new text was still untracked when the API-classification guard ran. | One 31/32 broad-gate result and focused rerun after staging. | Stage intended paths before candidate-level classification; do not weaken the guard. |
| Line endings | Process mistake | Windows receipts were first hashed before repository LF normalization. | Repository identities had to be recomputed separately from packaged bytes. | Normalize checked-in evidence before repository identity freeze; label raw artifact hashes separately. |
| Session log | Process mistake | The WP09 block was inserted inside an older entry. | First clean closeout failed and the handoff had to be regenerated. | Insert only at the top reverse-chronological boundary and run preparation before commit. |
| Session log | Process mistake | The WP09 entry omitted the explicit `**Completed:**` list. | Second closeout repair. | Let `session end --fix` validate the complete newest entry before candidate freeze. |
| Hosted integrity | Missing local control | Two lock files and one rollback receipt lacked final newlines. | First hosted run failed; normalization changed evidence; second candidate and hosted run were required. | Run `check --candidate-integrity` before repository evidence and commit freeze. |
| Task timing | Control messaging defect | `session end` passed while the WP09 timer remained open. | The next task's first `session begin` failed. | Close usage after merge and before starting the next task; the CLI now explains this. |
| Handoff wrapping | Control parser defect found in this review | Wrapped focus and completion text was truncated in the generated next-session brief. | One incomplete handoff generation and explicit regeneration. | Join bounded Markdown continuations; keep a regression for wrapped fields and bullets. |
| Shell commands | Repeated tooling friction | Nested PowerShell expansion, wildcard use, execution policy, `HEAD^{tree}`, certificate-provider deletion, and piping to Unix `tail` each used the wrong command shape. | At least seven small command retries and repeated context switching. | Use literal blocks, exact paths, maintained launchers, `git show --format=%T`, native PowerShell output selection, and one shell through each operation. |

The repeated families were more expensive than any one small mistake:

- cold-ready scope changed three times;
- session/handoff state required placement, completion-marker, timer, and wrapped
  text repairs;
- repository bytes crossed two normalization boundaries, first CRLF/LF and then
  missing EOF in hosted validation;
- Windows command-shape mistakes caused at least seven short retries; and
- evidence was rebound after multiple candidate states instead of once after a
  stable installed result.

Future closeout reports should record these families as repair batches even when
each individual retry takes only a few minutes. That makes cumulative rework
visible without treating valid engineering failures as waste.

## Corrected candidate sequence

For future Excel and ETABS milestones:

1. freeze the bounded contract, examples, failure rows, non-goals, and focused
   acceptance commands;
2. run host-free fixtures first, then the exact-host micro-probe when the slice
   reaches a host boundary;
3. complete implementation, then run the changed domain's formatter/linter and
   consolidated focused gate;
4. run the installed path as smoke, functional matrix, postflight/cleanup, and
   performance, stopping at the first failing layer;
5. obtain one consolidated independent review of the locally passing candidate;
6. generate raw installed evidence only after functional behavior is stable;
7. finish session/handoff records and run `./run.sh check
   --candidate-integrity` before calculating final repository-facing hashes;
8. if normalization writes, review it, rebind only affected repository
   identities, and rerun candidate integrity to a clean pass;
9. create the immutable candidate commit, run read-only `session end`, push once,
   and use one hosted validation cycle; and
10. after merge verification, record the task usage closeout before beginning
    the next task.

WP10 applies this sequence through its six delivery slices. `WP10-01` freezes
portable contracts and shared Python/.NET fixtures without CSI or Excel. The
next slice begins with the ETABS host micro-probe. Live acquisition, offline
normalization, Excel import, and installed performance remain later boundaries,
so a defect in one layer cannot repeatedly invalidate evidence for every layer.

## What must remain strict

WP09 also demonstrated controls that should not be relaxed:

- nearest-rank p95 for ten samples remains the maximum sample; the rejected
  attempt to reinterpret p95 would have hidden a failed performance gate;
- all three exact-candidate memory observations remain recorded, including the
  275.438 MiB failure between the 136.418 MiB and 202.059 MiB passes;
- installed acceptance continues to require the actual loaded signed XLL,
  transactional rollback, save/reopen, runtime invalidation, migration,
  cleanup, and one unchanged accepted candidate; and
- hosted checks remain required even after local parity is added.

These checks made WP09 professional. The new controls reduce repeated work by
putting those checks at the right boundary and by keeping each task small enough
that a failure invalidates only one slice.
