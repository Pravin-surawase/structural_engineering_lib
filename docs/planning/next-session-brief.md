# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: First make the Windows host maintainably ready for this and future
- Completed: Installed and verified Git for Windows, GitHub CLI, `uv`, Node 24/npm, and an; Persisted the repository Python selector and UTF-8 mode for this user,; Repaired the maintained launchers for Windows `.venv/Scripts/python.exe`,
- Git receipt: docs/verification/etabs-excel-beam-w2a-baseline-git-handoff-receipt.json | sha256:797353e473fbb646ae9cc8eded4e19b8bdf7010a38b3a7b6003b0024d6686916 | HOLD
- Git identity: codex/etabs-excel-beam-w2a-baseline@a3f36cb460395eeda32f832963917983e9bc4dfb | upstream=origin/main@a3f36cb460395eeda32f832963917983e9bc4dfb | base=origin/main@a3f36cb460395eeda32f832963917983e9bc4dfb | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub `origin/main` is `a3f36cb460395eeda32f832963917983e9bc4dfb` after PR #895. W2A is a locally verified candidate on `codex/etabs-excel-beam-w2a-baseline`: its transport-neutral baseline/topology/result contract and fake-COM adapter are frozen without opening ETABS or Excel. |
| **Next** | Review and accept or repair the clean W2A candidate only. W2B live-bridge/REST/Excel expansion and W2C installed-Windows acceptance remain unstarted and require separate scope after W2A acceptance. |
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
- W2A did not open ETABS/Excel, run analysis/design, mutate a model, add
  REST/Excel W2 surfaces, optimize, or claim engineering approval. The verdict
  remains `HELD_NOT_SUPPORTED`.
- One historical unmatched parent-pilot usage checkpoint remains preserved; do
  not invent old timing to close it.

## Next objective

Review the exact W2A candidate and its verification evidence. Accept it or make
only a bounded W2A repair. Do not begin W2B or W2C merely because the local gate
is green. The next-phase plan contains the frozen schemas, getter matrix,
topology rules, reason codes, provenance/hash basis, result-row policy, and
`HELD_NOT_SUPPORTED` rationale.

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
