# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Complete the bounded W2 campaign on the Windows evidence machine:
- Completed: Fetched GitHub and proved PR #896 merge `0f5c918e...`, reviewed W2A head; Bound installed ETABS `23.3.1.4563` to the registered x64 `ETABSv1.tlb`; Proved all 18 W2A getters plus `SetPresentUnits` for interface/method,
- Git receipt: docs/verification/etabs-excel-beam-w2b-git-handoff-receipt.json | sha256:00fd77e9a3465aa4b8e162e21ffd992749a29d2cd81b48d62852ac057aa6026f | HOLD
- Git identity: codex/etabs-excel-beam-w2-campaign@4841ab2a37504fa009842a812e1a0fa9e8b95d8f | upstream=NONE@UNKNOWN | base=origin/main@0f5c918eb87b658448737fd6bf023ccb4bd07c74 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_APPLICABLE | PR=NOT_APPLICABLE#UNKNOWN | review=NOT_APPLICABLE | retention=UNKNOWN
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub `origin/main` remains exactly `0f5c918eb87b658448737fd6bf023ccb4bd07c74` after PR #896. Phase A is pushed at `4841ab2a...` and frozen W2B is pushed at exact campaign head `395f0618...`. Installed W2C repaired CSI's documented `GetStories` Base-row shape locally, then stopped before force reads because the approved combination is present but inactive. |
| **Machine roles** | Mac is the primary development/integration machine. Windows is the installed Excel/ETABS testing and evidence machine. GitHub is the tracked handoff authority; proprietary model/workbook/evidence bytes remain on Windows. |
| **Next** | Finish the installed REST/Excel fail-closed proof without changing result selections, freeze the safe blocked receipt and exact retry prerequisite, run final gates, and push the cumulative campaign. Mac then performs one cumulative review; an accepted force baseline requires a separately authorized ETABS session that already has the exact approved combination active. |
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

## Next objective

1. Exercise the installed REST and Excel blocked paths against the exact repair
   checkpoint, proving no W2 table write and no force read.
2. Freeze the safe W2C hold receipt, external evidence hashes, unchanged model/
   lock/units proof, and exact already-selected-combination retry prerequisite.
3. Run final gates, commit/push the clean campaign, stop writing, and give Mac
   one cumulative review/PR pickup.

## New-chat starter

Use the copy-ready prompt in
[the next-phase plan](excel-etabs-beam-next-phase-plan.md#new-chat-starter).

## Preservation rules

- During Phase A/B, do not attach to ETABS or open/use Excel/model/workbooks.
  During Phase C, use only the approved copied model/workbook through the exact
  guarded read-only workflow and abort on any identity/preflight failure.
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
5. [Excel/Python/ETABS pilot guide](../guides/excel-etabs-python-bridge-pilot.md)
6. [Multi-device Git workflow](../git-automation/git-workflow-single-source.md#multi-device-rule-one-branch-one-writer-device)
7. [Current task board](../TASKS.md)
8. `Python/structural_lib/services/etabs_beam_baseline.py`
9. `Python/structural_lib/services/etabs_beam_bridge.py`
10. `Python/tests/unit/test_etabs_beam_baseline.py`
11. [Newest W2 campaign session entry](../SESSION_LOG.md)
