# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Make the W2A result, Windows setup, machine roles, root causes,
- Completed: Fetched GitHub and verified authenticated account `Pravin-surawase`, remote; Reinspected both retained Windows worktrees. The W2A worktree is the only; Made the machine ownership explicit in the canonical Git workflow and ETABS
- Git receipt: docs/verification/etabs-excel-beam-w2a-machine-handoff-git-handoff-receipt.json | sha256:fe900eb16b4441e38bfad4cd0ebaf787700f14ff5f9f7e662290df74973e23dc | HOLD
- Git identity: codex/etabs-excel-beam-w2a-baseline@c629e362b4b93c915422ba2c1a6fb1cf3d56dadd | upstream=origin/main@a3f36cb460395eeda32f832963917983e9bc4dfb | base=origin/main@a3f36cb460395eeda32f832963917983e9bc4dfb | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub `origin/main` is `a3f36cb460395eeda32f832963917983e9bc4dfb` after PR #895. Windows produced W2A implementation candidate `c629e362...` plus a documentation/setup successor on `codex/etabs-excel-beam-w2a-baseline`. Windows is handing the fully pushed branch to the Mac and then stops writing it. |
| **Machine roles** | Mac is the primary development/integration machine. Windows is the installed Excel/ETABS testing and evidence machine. GitHub is the tracked handoff authority; proprietary model/workbook/evidence bytes remain on Windows. |
| **Next** | On Mac, fetch and verify `origin/codex/etabs-excel-beam-w2a-baseline`, review the full diff, rerun proportionate checks, and accept or make one bounded W2A review repair. W2B and W2C remain unstarted. |
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

On the Mac primary machine:

1. `git fetch origin` and verify the final remote branch head plus current
   `origin/main`; do not use the Windows-local `c629e362` as the final head.
2. Create a clean review worktree from
   `origin/codex/etabs-excel-beam-w2a-baseline` and inspect the complete
   `origin/main...HEAD` diff.
3. Run the W2A focused set and proportionate runtime/governance/quick checks.
4. Accept W2A or make one bounded Mac-owned review repair, then use the normal
   PR/check/integration path.
5. Keep W2B, W2C, installed ETABS/Excel execution, model mutation, and the
   separate dev-only npm advisory repair outside this review packet.

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
