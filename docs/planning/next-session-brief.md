# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: Close the confirmed post-LIB-PRO-004 release-safety defects
- Git receipt: docs/verification/lib-pro-005-git-handoff-receipt-2.json | sha256:d6b5c82505613e89407032fd5a29f894b2dc2f85ff9c02ca43a73fe96ed5f567 | HOLD
- Git identity: codex/lib-pro-005-release-safety-closure@f1a9937cfdba4c72c22e6219ffaf02f94809f1a5 | upstream=origin/main@f1a9937cfdba4c72c22e6219ffaf02f94809f1a5 | base=origin/main@f1a9937cfdba4c72c22e6219ffaf02f94809f1a5 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-005` local candidate from merged PR #836 base `f1a9937c`: confirmed WebSocket, BOQ, lower-level scalar, PMM packaging, root-export, React status, and two active documentation-count defects are repaired |
| **Next** | Finish the pre-commit handoff receipt and one affected-index refresh, run cumulative read-only gates, create one immutable commit, push one PR, and let exact-head hosted checks decide merge eligibility |
| **Why** | Direct runtime replay proved specific unsafe behaviors; performance and Excel claims were dispositioned without unnecessary CI rewiring |
| **Held** | Remaining 361 unproven parameters, wider route remediation, INDIA-3, ETABS, package publication, stable/professional claims, and qualified approval remain separate and held |

## Correct next library packet

Do not restart the confirmed defect repairs. The maintained input auditor now
assigns equivalent shear, development length, and beam outline to explicit
validator/delegation evidence while truthfully exiting 1 for 361 unresolved
parameters. Any successor must start from runtime reproducers and an
outcome-changing maintained-route scope, not the raw static count.

## Other live work

- PR #836 is integrated at `f1a9937c`. `v0.23.1a2` is already public; later
  safety work is not in that artifact, so never republish that version.
- `INDIA-3-G0` remains deferred until route-safety disposition is complete.
- The unrelated dirty detached worktree at `.codex/worktrees/e54a` remains
  retained and untouched. Dependabot PRs are separate maintenance work.
- `MAINT-011` preserves the all-file hook/JSONC/Bandit/vendor-normalization,
  stale gate-count, command-discovery, shell, index, audit-summary, receipt, and
  CI-semantics issues found here. Handle it only in a separate clean lane.

## Required Reading

1. [LIB-PRO-005 plan](lib-pro-005-release-safety-closure-plan.md)
2. [LIB-PRO-005 evidence](../verification/lib-pro-005-release-safety-closure-evidence.md)
3. [Current task board](../TASKS.md)
4. [Git workflow single source](../git-automation/git-workflow-single-source.md)
5. [MAINT-011 tooling follow-up](maint-011-developer-gate-hygiene-follow-up.md)
