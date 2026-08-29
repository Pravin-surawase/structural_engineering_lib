# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Independently review the exact Windows W2A branch, repair the one
- Completed: Verified live GitHub/local identity, exact two-commit ancestry, full diff,; Reproduced an accepted baseline containing frame story `MISSING` while the; Passed the frozen story-name set into frame extraction and now raise stable
- Git receipt: docs/verification/etabs-excel-beam-w2a-mac-review-git-handoff-receipt.json | sha256:bb7129e98d1e5fdb60d3674c4a758de0e7bd2ee40d7deda7d03de782120525e6 | HOLD
- Git identity: codex/etabs-excel-beam-w2a-baseline@9bd29fbeb2993985b6f4f5e0b5d680df1cb7c47e | upstream=origin/codex/etabs-excel-beam-w2a-baseline@9bd29fbeb2993985b6f4f5e0b5d680df1cb7c47e | base=origin/main@a3f36cb460395eeda32f832963917983e9bc4dfb | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub `origin/main` is `a3f36cb460395eeda32f832963917983e9bc4dfb` after PR #895. Mac fetched exact Windows W2A head `9bd29fbe...`, reproduced the unknown-story acceptance defect, and repaired it by binding every frame story to `Story.GetStories`; PR/integration remains pending. |
| **Machine roles** | Mac is the primary development/integration machine. Windows is the installed Excel/ETABS testing and evidence machine. GitHub is the tracked handoff authority; proprietary model/workbook/evidence bytes remain on Windows. |
| **Next** | Mac freezes, verifies, and integrates the bounded W2A repair. After the merge, Windows independently audits the installed ETABS type-library/generated-wrapper signatures and prepares exact W2C evidence/abort criteria on one new branch without launching ETABS/Excel. W2B and W2C execution remain unstarted. |
| **Held** | ETABS analysis, unlock/save, section/load write-back, optimization, complete solver parity, expanded design/detailing/site-practice automation, release, and professional or construction-use approval. |

## Today closeout

- W2A now binds an already-supplied `SapModel` shape to an authorized absolute
  `.edb` identity and brackets all COM reads with caller-supplied read-only
  hash/size/timestamp observations.
- The contract exhaustively retains or dispositions stories, horizontal beams,
  vertical columns, exact endpoint connectivity, explicit result selections,
  and every `FrameForce` station. Advanced-axis or excluded connected members
  fail closed instead of producing partial topology.
- The frozen getter matrix accepts exact tuple/list shapes, validates every
  trailing return code and array length, uses no result-selection setter, and
  restores original units on successful and failed reads.
- Runtime/source provenance, stable row/member/connection/station identities,
  the getter-matrix digest, and the whole baseline digest use deterministic
  canonical JSON SHA-256.
- Windows development setup is repaired for future work: maintained launchers
  discover Windows virtual environments and executable suffixes, the React
  build is cross-platform, byte-frozen E2K/XML fixtures stay LF, and the active
  GitHub CLI account is `Pravin-surawase`.
- Windows onboarding now canonicalizes MSYS and Windows/Python paths, fixing the
  false `Python source shadowing detected` result while preserving the real
  source-bound fail-closed check.
- The Windows primary checkout is clean but intentionally stale/protected. It
  remains `HOLD_MAIN`; exact task/evidence work uses fetched dedicated
  worktrees. Mac owns current `main` and normal integration.
- The full root-cause ledger, tool versions, setup/recovery commands, npm
  dev-only advisory, machine handoff, and remaining W2 gates are recorded in
  the next-phase plan and pilot guide.
- W2A did not open ETABS/Excel, run analysis/design, mutate a model, add
  REST/Excel W2 surfaces, optimize, or claim engineering approval. The verdict
  remains `HELD_NOT_SUPPORTED`.
- One historical unmatched parent-pilot usage checkpoint remains preserved; do
  not invent old timing to close it.

## Next objective

1. Mac completes the bounded W2A candidate, normal PR/check path, merge, and
   exact local-main synchronization.
2. Windows then creates `codex/etabs-w2c-com-signature-audit` from the fetched
   W2A merge and works independently until one clean pushed handoff exists.
3. That Windows packet inspects installed ETABS 23.3.1 type-library or generated
   wrapper definitions for the frozen W2A getters and sole unit setter, records
   exact host/tool/source identities, and prepares W2C evidence/abort criteria.
4. It must not launch ETABS, open a model/workbook, call live-model getters,
   run analysis, mutate anything, begin W2B/W2C execution, or create/merge a PR.
5. Windows pushes the completed branch once and stops; Mac performs one review
   pickup. The dev-only npm advisory stays a separate maintenance packet.

## New-chat starter

Use the copy-ready prompt in
[the next-phase plan](excel-etabs-beam-next-phase-plan.md#new-chat-starter).

## Preservation rules

- Do not open or mutate the Windows evidence clone, Excel, ETABS, copied model,
  workbooks, system toolchains, or external evidence during the local W2 packet.
- Preserve every unrelated worktree, staged/dirty/untracked/ignored/stashed
  item, retained source, branch, ref, and archive. Protected `main` remains a
  `HOLD_MAIN` lane.
- Do not copy repository files between devices; push/PR/fetch through GitHub.
- Windows stops writing the W2A branch after push; Mac becomes its sole writer.
- Do not rewrite history, bypass checks, delete branches/worktrees/refs/data,
  rebuild a public version, or broaden software/engineering claims.

## Required Reading

1. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
2. [W1 installed Windows receipt](../verification/etabs-excel-python-pilot-w1-evidence.json)
3. [Excel/Python/ETABS pilot guide](../guides/excel-etabs-python-bridge-pilot.md)
4. [Multi-device Git workflow](../git-automation/git-workflow-single-source.md#multi-device-rule-one-branch-one-writer-device)
5. [Current task board](../TASKS.md)
6. `Python/structural_lib/services/etabs_beam_baseline.py`
7. `Python/tests/unit/test_etabs_beam_baseline.py`
8. [Newest W2A Windows/setup session entry](../SESSION_LOG.md)
