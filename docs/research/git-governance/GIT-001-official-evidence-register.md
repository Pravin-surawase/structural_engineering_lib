---
owner: Main Agent
status: in-progress
last_updated: 2026-08-12
doc_type: research-register
task: GIT-001
phase: 1
---

# GIT-001 Phase 1 — Official Evidence Register

## Register contract

Only primary, official sources belong in this register. A verified source can
support a factual finding; it cannot by itself create project policy. Project
applicability and proposed decisions remain separate columns. `Open` means the
finding needs more research before Phase 1 coverage can close.

| ID | Authority / source | Verified | Factual finding | Project applicability | Decision status |
|---|---|---|---|---|---|
| GIT-F01 | Git, [glossary](https://git-scm.com/docs/gitglossary) | 2026-08-12 | Objects are immutable content-addressed units; refs name objects; the index is a stored working-tree version and can contain merge stages. | Foundation for saved-work, staging, and recovery language. | Fact verified; policy open |
| GIT-F02 | Git, [`git status`](https://git-scm.com/docs/git-status) | 2026-08-12 | Status distinguishes HEAD-to-index, index-to-working-tree, and untracked paths. Background status may refresh the index unless optional locks are disabled. | Baseline and monitoring commands must distinguish the three states and avoid background lock interference. | Fact verified; policy open |
| GIT-F03 | Git, [`git worktree`](https://git-scm.com/docs/git-worktree) | 2026-08-12 | Linked worktrees have separate working trees and administrative metadata, while some refs and repository configuration remain shared. Git commands should resolve Git paths instead of assuming `.git/<name>`. | Directly explains branch/ref collisions and linked-worktree marker mistakes in this project. | Fact verified; project rule open |
| GIT-F04 | Git, [revision syntax](https://git-scm.com/docs/gitrevisions) | 2026-08-12 | A revision can name an object through a full/unique object ID or ref; range notation expresses reachability sets, not patch equivalence. | Ahead/behind and ancestry evidence must not be treated as proof that squash-merged patches are absent or present. | Fact verified; decision open |
| GIT-F05 | Git, [`git reflog`](https://git-scm.com/docs/git-reflog) | 2026-08-12 | Reflogs record local ref-tip updates and can identify prior positions; retention is finite and expiry differs for reachable and unreachable entries. | Recovery may use reflogs as time-limited local evidence, not guaranteed permanent backup. | Fact verified; retention rule open |
| GH-F01 | GitHub, [status checks](https://docs.github.com/en/pull-requests/reference/status-checks) | 2026-08-12 | Required checks gate merging when configured; check conclusions include success, neutral, skipped, failure, cancellation, timeout, and others. | A green-looking workflow needs exact required-check and conclusion interpretation. | Fact verified; decision open |
| GH-F02 | GitHub, [troubleshooting required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks) | 2026-08-12 | Required checks must pass for the latest relevant commit SHA; depending on workflow reporting, the head or test-merge commit may be authoritative. | Supports exact-head reinspection before integration and after any push/base change. | Fact verified; current control to audit |
| GH-F03 | GitHub, [ruleset rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) | 2026-08-12 | Rulesets can require PRs/status checks, restrict merge types, and block force pushes; strict checks require the branch to be current with its base. | Candidate enforcement mechanism; current ruleset must be compared with intended workflow. | Fact verified; no settings change authorized |
| GH-F04 | GitHub, [merging a pull request](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request) | 2026-08-12 | Draft PRs cannot merge; repository rules may require reviews, checks, or an up-to-date branch. | Supports draft-as-active-work and merge-readiness state distinctions. | Fact verified; merge-method choice open |
| OAI-F01 | OpenAI, [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/) | 2026-08-12 | The Codex app supports isolated worktrees for parallel tasks, while task threads retain separate context. | Product behavior must be reconciled with Git's shared repository state and this project's ownership rules. | Fact verified; lifecycle details open |

## Open source coverage

Phase 1 still needs official-source coverage for:

- commits, branches, upstreams, fetch, pull, and push;
- merge, rebase, cherry-pick, revert, reset, restore, stash, and clean;
- hooks, configuration scope, pruning, garbage collection, and worktree repair;
- tags, signatures, release ancestry, submodules, and partial/shallow clones where applicable;
- GitHub merge methods, auto-merge/merge queues, branch protection versus
  rulesets, environments, releases, Dependabot, forks, and external contributors;
- current Codex task/worktree lifecycle, archival/snapshots, and safe handoff
  behavior from official documentation or verified product evidence.

No Phase 1 completion claim is made until these areas are dispositioned as
covered, not applicable, or explicitly unresolved.
