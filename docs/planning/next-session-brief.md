# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Complete the bounded W2 campaign on the Windows evidence machine:
- Git receipt: docs/verification/etabs-excel-beam-w2c-com-signature-audit-git-handoff-receipt.json | sha256:1a5720ee52c7e075c6a995f8b466d73796012880fab53d30ce38b8f8549cd868 | HOLD
- Git identity: codex/etabs-w2c-com-signature-audit@0f5c918eb87b658448737fd6bf023ccb4bd07c74 | upstream=origin/main@0f5c918eb87b658448737fd6bf023ccb4bd07c74 | base=origin/main@0f5c918eb87b658448737fd6bf023ccb4bd07c74 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_APPLICABLE | PR=NOT_APPLICABLE#UNKNOWN | review=NOT_APPLICABLE | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub `origin/main` is exactly `0f5c918eb87b658448737fd6bf023ccb4bd07c74` after PR #896 merged reviewed W2A head `0972e1af...`. The Windows Phase A branch statically proves all 18 W2A getters plus `SetPresentUnits` against installed ETABS 23.3.1 metadata; checkpoint validation/push is next. |
| **Machine roles** | Mac is the primary development/integration machine. Windows is the installed Excel/ETABS testing and evidence machine. GitHub is the tracked handoff authority; proprietary model/workbook/evidence bytes remain on Windows. |
| **Next** | Push the clean Phase A audit checkpoint; create `codex/etabs-excel-beam-w2-campaign` from its exact remote head; freeze/push W2B; then execute guarded read-only W2C only after every preflight gate passes. Mac performs one cumulative review after the final campaign push. |
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

## Next objective

1. Finish Phase A documentation/session/governance, run proportionate focused
   checks and the quick gate once, commit with normal hooks, push, and verify the
   exact remote checkpoint.
2. Create `codex/etabs-excel-beam-w2-campaign` from that exact pushed head.
3. Implement only maintained W2B observer/orchestration, REST/Excel review,
   reconciliation/collision/error/row-limit contracts and fake-COM coverage;
   freeze, validate, commit, and push the Phase B checkpoint.
4. Revalidate every static identity/precondition against the Phase B head. Then
   run the approved copied-model W2C read-only journey, retaining full evidence
   externally and only safe hashes/counts/verdicts in Git.
5. Freeze final evidence/docs, run final gates, commit/push the clean campaign,
   stop writing, and give Mac one cumulative review/PR pickup.

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
4. [Excel/Python/ETABS pilot guide](../guides/excel-etabs-python-bridge-pilot.md)
5. [Multi-device Git workflow](../git-automation/git-workflow-single-source.md#multi-device-rule-one-branch-one-writer-device)
6. [Current task board](../TASKS.md)
7. `Python/structural_lib/services/etabs_beam_baseline.py`
8. `Python/tests/unit/test_etabs_beam_baseline.py`
9. [Newest W2 campaign session entry](../SESSION_LOG.md)
