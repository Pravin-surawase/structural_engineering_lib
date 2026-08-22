# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: Complete the 13 confirmed MAINT-011 findings plus any additional
- Git receipt: docs/verification/maint-011-git-handoff-receipt.json | sha256:38d1d1642c7b89e61fe7050c6f3824e28761ea2678853840d26fd7e26617d5a1 | HOLD
- Git identity: codex/maint-011-developer-gate-hygiene@3f61bd93d92b7092a55e25b8ca99eda4b3335ff1 | upstream=NONE@UNKNOWN | base=origin/main@3f61bd93d92b7092a55e25b8ca99eda4b3335ff1 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-005` is merged through PR #837 at `3f61bd93`; MAINT-011 implements 15 developer-gate root-cause dispositions in one separate candidate |
| **Next** | Let the frozen MAINT-011 local gates, exact-head review, required hosted checks, and merge decide acceptance; then select a new library packet separately |
| **Why** | Ordinary staged and all-file hooks must be equally decisive and byte-clean before more library capability work begins |
| **Held** | Remaining 361 unproven parameters, wider route remediation, INDIA-3 implementation, ETABS, package publication, stable/professional claims, and qualified approval remain separate and held |

## Correct next library packet

Do not restart LIB-PRO-005 or MAINT-011 after their merge prerequisites pass.
The next library decision should compare a bounded input-safety successor with
INDIA-3-G0 earthquake-code truth/benchmark intake. It must start from exact
maintained routes and controlled sources, not from the raw count of 361
unproven parameters.

## Other live work

- PR #837 is integrated at `3f61bd93`. `v0.23.1a2` is already public; later
  safety and maintenance work is not in that artifact, so never republish it.
- `INDIA-3-G0` remains a planning/source/benchmark audit only until separately
  activated; no earthquake formulas are part of MAINT-011.
- The unrelated dirty detached worktree at `.codex/worktrees/e54a` remains
  retained and untouched. Dependabot PRs are separate maintenance work.
- The MAINT-011 candidate preserves vendored/frozen bytes, repairs JSONC and
  Bandit dispositions, and makes dependency, discovery, audit, receipt, Excel,
  and performance truth explicit without starting ETABS or Excel feature work.

## Required Reading

1. [MAINT-011 tooling follow-up](maint-011-developer-gate-hygiene-follow-up.md)
2. [LIB-PRO-005 evidence](../verification/lib-pro-005-release-safety-closure-evidence.md)
3. [Current task board](../TASKS.md)
4. [Git workflow single source](../git-automation/git-workflow-single-source.md)
