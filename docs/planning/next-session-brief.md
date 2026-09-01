# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-09-02
- Focus: Audit every local hook and hosted owner, freeze a lower-cost
- Git receipt: docs/verification/commit-pr-validation-consolidation-plan-git-handoff-receipt.json | sha256:3f890f8c75b4fc5d1cdb8ceb1b0db2dc6864b6c130da0e96d2f4a1f200594025 | HOLD
- Git identity: codex/commit-gate-consolidation-plan@16be0db796dc85f0462a3a49a5990dc0232ef0b4 | upstream=origin/main@16be0db796dc85f0462a3a49a5990dc0232ef0b4 | base=origin/main@16be0db796dc85f0462a3a49a5990dc0232ef0b4 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=NOT_CHECKED
- Next action: HOLD_FOR_EXACT_EVIDENCE
<!-- HANDOFF:END -->

## Current boundary

The [commit and PR validation consolidation
plan](commit-pr-validation-consolidation-plan.md) is the next maintenance
authority. It is plan-only in this candidate: `.pre-commit-config.yaml` and
`.github/workflows/fast-checks.yml` are deliberately unchanged.

| State | Next action / claim boundary |
|---|---|
| **Current** | The complete 34-hook disposition, hosted gaps, resolved-merge exception, batching policy, fault matrix and quantitative exit criteria are frozen. The remaining active 150-line direct-commit rule is removed. |
| **Next** | From accepted current `main`, implement hosted parity first and the three-hook commit lane second as two logical commits. Push both together once and use one PR. |
| Commit target | Exactly `check-merge-conflict`, `check-added-large-files --maxkb=500`, and the live Git-operation guard. No formatter, linter, type, security, test, generator, docs or quick/full gate runs on ordinary commits. |
| PR target | Keep strict required `PR Gate`; run complete candidate assurance once for the final batch. Remove `fast-checks.yml` `push: main` only while the strict no-bypass ruleset remains proved. |
| W3 state | Offline A0/B0/B1A/C0 is accepted through PR #947. A1/C1 remains a separate, explicitly authorized installed ETABS evidence boundary and must not share the maintenance branch. |
| Held | ETABS/Excel/COM/model/workbook actions; A1/C1; mutation/analysis/design/export; release/publication; unrelated worktree or branch cleanup. |

## Implementation order

1. Re-prove exact current-main source and the active strict `PR Gate` ruleset.
2. Freeze the machine-readable 34-row coverage matrix and complete-hook timing
   baseline.
3. Add PR parity, path ownership and negative workflow-contract tests while
   the old commit hooks still exist.
4. Reduce the commit stages to the three safety hooks and update the exact
   resolved-merge regression.
5. Update active instructions after executable topology is final; do not add a
   line/file threshold or pre-push hook.
6. Push the two commits together once. On a real hosted failure, reproduce only
   the owning check, make one consolidated repair and push once more.
7. Observe 5-10 successor PRs for routing misses, false failures, wall time and
   exact receipt behavior.

## Cleanup state

- No ETABS, Excel, Git/GitHub, test, Python or frontend-build process remains.
- Codex/MCP Node helpers are unrelated and must remain running.
- The completed `w3-offline-etabs-foundations` worktree and residual junction
  are removed. Its local branch and accepted merge/tree evidence are preserved;
  the shared dependency target is untouched.
- Tiny normal pytest retention was intentionally left alone.

## Required Reading

1. [Commit and PR validation consolidation plan](commit-pr-validation-consolidation-plan.md)
2. [Current task board](../TASKS.md)
3. [Newest session entry](../SESSION_LOG.md)
4. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
5. [W3 and professional beam integrated plan](w3-beam-professional-integrated-execution-plan.md)
