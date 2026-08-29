# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Complete the bounded W2 campaign on the Windows evidence machine:
- Completed: Fetched GitHub and proved PR #896 merge `0f5c918e...`, reviewed W2A head; Bound installed ETABS `23.3.1.4563` to the registered x64 `ETABSv1.tlb`; Proved all 18 W2A getters plus `SetPresentUnits` for interface/method,
- Git receipt: docs/verification/etabs-excel-beam-w2c-git-handoff-receipt.json | sha256:fc76cb7d0cec40ed483b81cd31b45c6012f8e534f0995ff9fa2cfae94193366f | HOLD
- Git identity: codex/etabs-excel-beam-w2-campaign@18926ef48c620213abbb931449cda9e8049eee7c | upstream=origin/codex/etabs-excel-beam-w2-campaign@18926ef48c620213abbb931449cda9e8049eee7c | base=origin/main@0f5c918eb87b658448737fd6bf023ccb4bd07c74 | tree=dirty | operation=none
- Hosted evidence: remote=UNKNOWN | PR=NOT_APPLICABLE#UNKNOWN | review=NOT_APPLICABLE | retention=UNKNOWN
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub `origin/main` remains exactly `0f5c918eb87b658448737fd6bf023ccb4bd07c74` after PR #896. Phase A is pushed at `4841ab2a...`, W2B at `395f0618...`, and the installed `GetStories` repair at `18926ef4...`. Direct/REST/installed Excel all stopped before force reads on the inactive approved combination; model/workbook bytes, lock, and units remained unchanged. |
| **Machine roles** | Mac is the primary development/integration machine. Windows is the installed Excel/ETABS testing and evidence machine. GitHub is the tracked handoff authority; proprietary model/workbook/evidence bytes remain on Windows. |
| **Next** | Mac performs one cumulative campaign review and may open the integration PR. W2C remains held—not accepted. A separately authorized installed retry requires the exact approved combination already active before Codex attaches and every identity/preflight check repeated. |
| **Held** | ETABS analysis, unlock/save, section/load write-back, optimization, complete solver parity, expanded design/detailing/site-practice automation, release, and professional or construction-use approval. |

## Today closeout

- Fetched GitHub, verified exact PR #896 merge `0f5c918e...`, preserved the
  stale/protected Windows `main` and retained W2A worktree, and created the
  dedicated Phase A branch/worktree from exact `origin/main`.
- Bound installed ETABS `23.3.1.4563` to x64 `ETABSv1.tlb` LIBID
  `{542F7A9D-3A7D-4061-97B3-3A1276FF83BD}` version `1.0`, SHA-256
  `3823416b...24ef0e`, using 64-bit Python `3.11.15` and `comtypes 1.4.16`.
- Proved every frozen W2A operation for interface/name, argument order and
  defaults, output order/count, enum values, return-code form, and installed
  scalar/list/SAFEARRAY tuple shapes. No outcome-changing adapter mismatch was
  found.
- Recorded the optional `LoadCases.GetNameList(CaseType=0)` detail and required
  explicit `FrameForce(..., ItemTypeElm=0)` input without changing the correct
  W2A behavior.
- Froze exact W2C preconditions, proof points, abort criteria, and live-only
  questions in the tracked static-audit evidence. ETABS design summary is not a
  frozen operation; frame analysis remains `HELD_NOT_SUPPORTED`.
- An ETABS process pre-existed the audit. It was only observed read-only and
  remained the same process; no COM object was created/attached, no `SapModel`
  getter ran, and no model/workbook/application was opened by this audit.
- The Windows primary checkout is clean but intentionally stale/protected. It
  remains `HOLD_MAIN`; exact task/evidence work uses fetched dedicated
  worktrees. Mac owns current `main` and normal integration.
- The dev-only npm advisory remains a separate maintenance packet.
- One historical unmatched parent-pilot usage checkpoint remains preserved; do
  not invent old timing to close it.
- Phase A is committed and pushed at exact remote head `4841ab2a...`; no PR was
  opened. The campaign branch was created from that exact remote checkpoint.
- W2B implements the real read-only EDB observer, process-wide ETABS COM
  serialization, getter-only preflight, preflight-bound run request, exact
  post-read lock/unit proof, and bounded no-truncation transport envelope.
- The FastAPI surface adds typed `/beam-baseline/preflight` and
  `/beam-baseline` operations. Domain-blocked results expose no baseline;
  connection/data/capacity failures map to 409/422/413.
- Excel now preflights all seven controlled W2 tables before mutation and
  retains summary, stories, frames, endpoint connections, every force station,
  every disposition, and reconstructable server-canonical hash-basis JSON.
- An outcome-changing W2A ordering defect was traced and repaired: topology or
  selection blockers now stop before `FrameForce`. Fake-COM regressions prove
  zero force calls on those paths while accepted deterministic hashes remain
  unchanged.
- Phase B passed the consolidated quick gate and every normal hook, committed
  as exact head `395f0618...`, and was pushed with local/remote equality and no
  PR.
- Phase C matched the approved model hash/size/time, locked state, units,
  runtime, binaries, type library, generated wrappers, finished case inventory,
  and normal ETABS window. CSI's documented Base-row array convention exposed
  and justified one narrow `GetStories` repair. The approved exact combination
  is present but inactive, so the maintained path returns blocked with no
  baseline/hash basis/stations and leaves file/lock/units unchanged.
- The narrow installed repair is committed and pushed as exact checkpoint
  `18926ef48c620213abbb931449cda9e8049eee7c`; no getter/setter scope changed.
- Direct service and source-bound REST independently returned the same typed
  `RESULT_SELECTION_NOT_ACTIVE` hold, 846 exhaustive dispositions, zero force
  stations, no baseline/hash basis, and restored units.
- Installed Excel displayed the same hold and wrote no `ETABS_W2_*` sheet or
  table. After a normal unchanged close, workbook SHA-256/bytes exactly matched
  their pre-run values; model hash/size/time/lock/units also remained exact.
- Safe counts, identities, hashes, limitations, and retry preconditions are
  frozen in the tracked W2C receipt. Proprietary model/workbook/result payloads
  remain external and hash-bound.

## Next objective

1. On Mac, fetch the exact cumulative campaign branch and compare it with exact
   `origin/main`; review Phase A, W2B, the installed story-shape repair, the safe
   W2C hold receipt, and all retained boundaries.
2. If review passes, open one cumulative PR and run the normal hosted checks.
   Describe W2C as `BLOCKED_SAFE_NO_FORCE_READ`, not an acceptance pass.
3. Do not start W3 or retry installed W2C without separate authorization. Any
   retry must begin with exact combination `117.(1.5DL+1.5LL)` already active
   and must repeat every source/runtime/model/unit/lock/result preflight.

## New-chat starter

Use the copy-ready prompt in
[the next-phase plan](excel-etabs-beam-next-phase-plan.md#new-chat-starter).

## Preservation rules

- Installed W2C work is complete at the safe hold. Do not change result
  selection or resume force reads under this authorization.
- Preserve every unrelated worktree, staged/dirty/untracked/ignored/stashed
  item, retained source, branch, ref, and archive. Protected `main` remains a
  `HOLD_MAIN` lane.
- Do not copy repository files between devices; push/PR/fetch through GitHub.
- Windows remains sole writer for the cumulative campaign until its final push;
  then it stops and Mac owns review/integration.
- Do not rewrite history, bypass checks, delete branches/worktrees/refs/data,
  rebuild a public version, or broaden software/engineering claims.

## Required Reading

1. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
2. [Phase A static COM-signature evidence](../verification/etabs-excel-beam-w2c-com-signature-audit-evidence.json)
3. [W1 installed Windows receipt](../verification/etabs-excel-python-pilot-w1-evidence.json)
4. [W2B contract evidence](../verification/etabs-excel-beam-w2b-contract-evidence.json)
5. [W2C installed safe-hold evidence](../verification/etabs-excel-beam-w2c-installed-acceptance-evidence.json)
6. [Excel/Python/ETABS pilot guide](../guides/excel-etabs-python-bridge-pilot.md)
7. [Multi-device Git workflow](../git-automation/git-workflow-single-source.md#multi-device-rule-one-branch-one-writer-device)
8. [Current task board](../TASKS.md)
9. `Python/structural_lib/services/etabs_beam_baseline.py`
10. `Python/structural_lib/services/etabs_beam_bridge.py`
11. `Python/tests/unit/test_etabs_beam_baseline.py`
12. [Newest W2 campaign session entry](../SESSION_LOG.md)
