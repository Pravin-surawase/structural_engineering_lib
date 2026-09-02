# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-02
- Focus: Preserve the legacy VBA transient-data pattern and useful ETABS/Excel workflow lessons in the six-phase beam programme.
- Git receipt: docs/verification/legacy-vba-dataflow-lessons-git-handoff-receipt.json | sha256:385a39db0780f7b5ebb1c96c7649e96963f93595ab4797e00d7408d881216228 | HOLD
- Git identity: codex/legacy-vba-data-flow-lessons@a3487e02400cf65d4b8934f484ef4b3882e3a9d9 | upstream=origin/main@a3487e02400cf65d4b8934f484ef4b3882e3a9d9 | base=origin/main@a3487e02400cf65d4b8934f484ef4b3882e3a9d9 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

The
[Beam Design and ETABS Optimization Master Plan](beam-design-optimization-master-plan.md)
is the human-facing programme authority. It freezes six sequential phases and
makes Phase 1 the only active phase.

PR #952 is merged at `c29a468a`. It accepted the supervised getter-only A1
state/file preservation and the exact C1 SQLite schema inventory. All required
hosted checks passed. The installed run found 160 tables/62,133 rows, all 10
requested tables and all 80 requested fields. The 3,502 IS 456 beam-summary rows
matched 3,502 direct getter items across 153/153 beams. The comparison result
epoch remains `BLOCKED`, so those values remain diagnostic rather than fresh
project comparison truth.

| State | Next action / claim boundary |
|---|---|
| **Current** | Phase 1 is active. A0/A1/C0/C1 foundations and installed schema evidence are accepted. B1B/B2 later-phase evaluator/search code is retained but does not advance the active phase. |
| **Next** | Freeze the minimum baseline allowlist/output contract and implement C2 for only the accepted C1 schema, entirely offline. |
| Commit lane | Exactly the three accepted mutation-safety hooks from PR #949; no broad gate is repeated per commit. |
| PR lane | Formatting, linting, typing, security, tests, generated contracts, docs and API parity run once for the complete batch. |
| Phase 1 exit | Exact process/runtime/model identity, fresh result epoch, explicit types/units, signed forces with physical-face identity, unchanged original model and repeatable normalized acquisition. |
| Held | Fresh project comparison truth until the result epoch is proved. Installed ETABS work requires separate authorization. Setters, save, unlock, further analysis/design, application exit, model input mutation, Excel automation, original-model changes, release/publication and unrelated cleanup remain excluded from C2. |

## Next decision order

1. Freeze the minimum Phase 1 baseline fields and canonical output contract.
2. Implement the C2 parser for only the accepted C1 tables and fields.
3. Prove schema, integrity, bounds, units, identity and deterministic
   normalization offline while preserving the result-epoch `HOLD`.
4. Add one acquisition/repeatability receipt rather than more independent
   extraction paths.
5. Request separate authorization before obtaining fresh installed result-epoch
   evidence, then repeat acquisition and close Phase 1 only if every gate passes.

## Cleanup state

- Urgent cleanup removed 40 clean merged-PR worktrees and 266 closed/merged-PR
  cache records. Five protected worktrees, all branches, open-PR/default-branch
  caches and dirty user work remain.
- No task-owned stale Python/test/dev/ETABS/Excel process remained. Codex/MCP
  and remote-desktop helpers are unrelated and must remain running.
- The hygiene-documentation worktree was removed after PR #951 was accepted;
  its branch remains preserved because deletion was not authorized.
- The dirty Excel-pilot and W3F live-foundation worktrees are suspended
  preservation lanes with zero commits ahead and overlapping historical docs.
  Preserve their exact dirty files and rebind deliberately before resumption;
  do not merge, reset, stash or rebase them as cleanup.

## Required Reading

1. [Beam Design and ETABS Optimization Master Plan](beam-design-optimization-master-plan.md)
2. [W3 and professional beam integrated plan](w3-beam-professional-integrated-execution-plan.md)
3. [Current task board](../TASKS.md)
4. [Newest session entry](../SESSION_LOG.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
6. [Commit and PR validation consolidation plan](commit-pr-validation-consolidation-plan.md)
