# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-29
- Focus: Consolidate the accepted Windows Excel + ETABS W1 work, the
- Completed: Recorded the five merged W1/multi-device PRs and the exact installed-Windows; Kept the accepted macro-free architecture: Excel Office.js calls trusted; Distinguished what W1 proves from the missing whole-model inventory,
- Git receipt: docs/verification/etabs-excel-beam-day-close-git-handoff-receipt.json | sha256:5b41d62ceba1720e04ea8531a53243c4f7214eafe2130f6f16e942f1685f083f | HOLD
- Git identity: codex/etabs-pilot-day-close-plan@45ef7c29428f172878a2157425509003c57b5363 | upstream=NONE@UNKNOWN | base=origin/main@45ef7c29428f172878a2157425509003c57b5363 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

| State | Exact boundary |
|---|---|
| **Public** | `v0.24.0` remains the immutable current normal software release; no new release is selected or authorized. |
| **Current** | GitHub and the Mac primary checkout are synchronized at merge `45ef7c29428f172878a2157425509003c57b5363`. `ETABS-EXCEL-PILOT-W1` is an installed-software PASS on the exact copied, locked, already-analyzed Windows model. PRs #890–#894 are merged and the multi-device rule is active. |
| **Next** | Start W2A of `ETABS-EXCEL-BEAM-W2-BASELINE` from freshly fetched `origin/main`: freeze and implement only the transport-neutral beam/model topology, result-provenance, fake-COM shape, and frame-solver feasibility contract. W2B REST/Excel and W2C Windows acceptance stay separate. |
| **Held** | ETABS analysis, unlock/save, section/load write-back, optimization, complete solver parity, expanded design/detailing/site-practice automation, release, and professional or construction-use approval. |

## Today closeout

- The Office.js -> FastAPI/Python -> ETABS route is installed-Windows accepted
  for an exact one-/five-beam read-only sample.
- Direct API and Excel rows reconcile exactly; unit restoration and unchanged
  copied-model identity are recorded in the W1 receipt.
- The remaining installed COM identity, result-name, inventory-call, and
  Windows launcher defects were repaired and merged.
- GitHub is now the shared history authority across devices. One task branch has
  one active writer device; every other device fetches and fast-forwards local
  `main` before new work.
- The next-phase roadmap now separates baseline, design/detailing,
  construction-practice checks, offline optimization, controlled write-back,
  reanalysis, and bounded iteration.
- One historical unmatched parent-pilot usage checkpoint remains preserved; do
  not invent old timing to close it.

## Tomorrow objective

Work only on W2's local read-only contract:

1. verify fetched Git/PR/worktree state and create a fresh task branch;
2. inspect the live bridge, ETABS snapshot/gravity services, and exact legacy
   VBA evidence identities without running macros;
3. freeze exhaustive member/result/topology schemas, dispositions, unit and
   provenance rules, non-goals, and focused tests;
4. implement and locally verify W2A only;
5. stop at a clean W2A candidate, leaving W2B and W2C unstarted.

Do not open or mutate ETABS during the local packet. Do not optimize sections or
claim independent frame-analysis support. The current code explicitly excludes
a stiffness/frame solver, so W2A should retain `HELD_NOT_SUPPORTED` unless a
different accepted authority is found.

## New-chat starter

Use the copy-ready prompt in
[the next-phase plan](excel-etabs-beam-next-phase-plan.md#new-chat-starter).

## Preservation rules

- Do not open or mutate the Windows evidence clone, Excel, ETABS, copied model,
  workbooks, system toolchains, or external evidence during the local W2 packet.
- Preserve every unrelated worktree, staged/dirty/untracked/ignored/stashed
  item, retained source, branch, ref, and archive. The detached dirty `e54a`
  lane remains untouched.
- Do not copy repository files between devices; push/PR/fetch through GitHub.
- Do not rewrite history, bypass checks, delete branches/worktrees/refs/data,
  rebuild a public version, or broaden software/engineering claims.

## Required Reading

1. [Excel + ETABS beam next-phase plan](excel-etabs-beam-next-phase-plan.md)
2. [W1 installed Windows receipt](../verification/etabs-excel-python-pilot-w1-evidence.json)
3. [Excel/Python/ETABS pilot guide](../guides/excel-etabs-python-bridge-pilot.md)
4. [Multi-device Git workflow](../git-automation/git-workflow-single-source.md#multi-device-rule-one-branch-one-writer-device)
5. [Current task board](../TASKS.md)
