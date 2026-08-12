---
owner: Main Agent
status: active
last_updated: 2026-08-13
doc_type: reference
task: GIT-001
phase: 1
---

# GIT-001 Phase 1 — Official Evidence Register

## Register contract

Only primary, official sources belong in the source tables. A source supports a
bounded external fact; it does not create project policy. Project observations,
unresolved choices, and not-applicable findings are separated below. `Covered`
means the named Phase 1 question has enough factual support for lifecycle
mapping, not that a later policy choice has been made.

## Git sources

| ID | Official source | Verified | Bounded external fact | Project applicability | Decision status |
|---|---|---|---|---|---|
| GIT-F01 | Git, [glossary](https://git-scm.com/docs/gitglossary) | 2026-08-12 | Objects are immutable content-addressed units; refs name objects; the index is a stored working-tree version and can contain merge stages. | Foundation for saved-work, staging, and recovery language. | Fact verified; policy open |
| GIT-F02 | Git, [`git status`](https://git-scm.com/docs/git-status) | 2026-08-12 | Status distinguishes HEAD-to-index, index-to-working-tree, and untracked paths. Background status may refresh the index unless optional locks are disabled. | Baseline and monitoring must distinguish the three states and avoid background lock interference. | Fact verified; policy open |
| GIT-F03 | Git, [`git worktree`](https://git-scm.com/docs/git-worktree) | 2026-08-12 | Linked worktrees have separate working trees, `HEAD`, indexes, and operation metadata while sharing repository data and most refs. The command defines add, move, lock, remove, prune, and repair operations. | Explains both useful filesystem isolation and remaining shared-state collisions. | Fact verified; lifecycle rules open |
| GIT-F04 | Git, [revision syntax](https://git-scm.com/docs/gitrevisions) | 2026-08-12 | Revision ranges express reachability sets, not patch equivalence. | Ahead/behind and ancestry cannot prove whether squash-, cherry-pick-, or manually reproduced changes are integrated. | Fact verified; evidence standard open |
| GIT-F05 | Git, [`git reflog`](https://git-scm.com/docs/git-reflog) | 2026-08-12 | Reflogs record local ref-tip updates; retention is finite and differs for reachable and unreachable entries. | Reflogs are time-limited local recovery evidence, not durable publication. | Fact verified; retention rule open |
| GIT-F06 | Git, [`git commit`](https://git-scm.com/docs/git-commit) | 2026-08-12 | A commit records the current index as a new commit, normally updates the current branch, and does not automatically include untracked files. Amending creates a replacement commit and can rewrite published history. | Defines the first durable local-history boundary and why staged scope matters. | Fact verified; commit policy open |
| GIT-F07 | Git, [`git branch`](https://git-scm.com/docs/git-branch) | 2026-08-12 | A branch is a ref; tracking configuration records an upstream relationship used by status and integration commands. Branch deletion and worktree attachment are distinct constraints. | Supports explicit branch, upstream, and attachment inspection. | Fact verified; naming/cleanup choices open |
| GIT-F08 | Git, [`git fetch`](https://git-scm.com/docs/git-fetch) | 2026-08-12 | Fetch downloads objects and updates configured remote-tracking refs; pruning removes stale remote-tracking refs, not the remote branches themselves. | A refresh changes local evidence and must precede current-state conclusions. | Fact verified; fetch cadence open |
| GIT-F09 | Git, [`git pull`](https://git-scm.com/docs/git-pull) | 2026-08-12 | Pull first fetches and then integrates using merge or rebase according to options/configuration; a diverged history requires an integration choice. | Pull is not a read-only refresh and must not be treated as equivalent to fetch. | Fact verified; integration method open |
| GIT-F10 | Git, [`git push`](https://git-scm.com/docs/git-push) | 2026-08-12 | Push updates remote refs according to refspecs; non-fast-forward updates are rejected by default for branches unless overriding rules permit them. | Defines remote publication and the shared-history rewrite boundary. | Fact verified; publication timing open |
| GIT-F11 | Git, [`git merge`](https://git-scm.com/docs/git-merge) | 2026-08-12 | Merge joins development histories, can stop with staged conflict entries, and provides `--continue`, `--abort`, and `--quit` paths. A merge commit retains both parents. | Supports explicit in-progress holds and parent/tree receipts. | Fact verified; merge strategy open |
| GIT-F12 | Git, [`git rebase`](https://git-scm.com/docs/git-rebase) | 2026-08-12 | Rebase reapplies commits onto a new base, producing new commits; conflicts can require continue, abort, skip, or quit decisions. Published rebases affect downstream history. | Establishes why rebase is a history-rewriting operation, not routine synchronization for a shared branch. | Fact verified; permitted uses open |
| GIT-F13 | Git, [`git cherry-pick`](https://git-scm.com/docs/git-cherry-pick) and [`git revert`](https://git-scm.com/docs/git-revert) | 2026-08-12 | Cherry-pick applies changes introduced by existing commits as new commits; revert records new commits that reverse earlier patches. Both may use sequencer state and stop on conflicts. | Explains patch-equivalent commits and recovery without ref rewrites. | Fact verified; selection rules open |
| GIT-F14 | Git, [`git reset`](https://git-scm.com/docs/git-reset) and [`git restore`](https://git-scm.com/docs/git-restore) | 2026-08-12 | Reset can move `HEAD` and, by mode, change the index and working tree; restore copies content into the index and/or working tree without moving the branch. Some modes discard uncommitted work. | These commands require exact target, scope, and ownership evidence. | Fact verified; authorization policy open |
| GIT-F15 | Git, [`git stash`](https://git-scm.com/docs/git-stash) and [`git clean`](https://git-scm.com/docs/git-clean) | 2026-08-12 | Stash records working-tree/index state in stash commits and resets selected state; clean removes untracked files and normally requires force unless interactive/configured otherwise. | A stash is shared repository state, while clean can destroy untracked work. | Fact verified; use remains approval-sensitive |
| GIT-F16 | Git, [`git config`](https://git-scm.com/docs/git-config) and [hooks](https://git-scm.com/docs/githooks) | 2026-08-12 | Configuration has system, global, local, worktree, and command scopes; hooks run from the configured hooks directory and can affect commits, pushes, merges, rebases, and other operations. | Worktree isolation does not imply isolated local configuration or hooks. | Fact verified; configuration policy open |
| GIT-F17 | Git, [`git gc`](https://git-scm.com/docs/git-gc) | 2026-08-12 | Garbage collection optimizes storage and may prune unreachable objects subject to expiry and concurrent-write safeguards. | Recovery horizons depend on reachability, reflog retention, and maintenance timing. | Fact verified; retention period open |
| GIT-F18 | Git, [`git tag`](https://git-scm.com/docs/git-tag) | 2026-08-12 | Lightweight tags are refs to objects; annotated tags are tag objects with metadata and optional signatures. Published tag replacement is not automatically propagated and can create conflicting identities. | Release evidence must bind the tag name to its exact object and publication receipt. | Fact verified; signing/release policy open |
| GIT-F19 | Git, [`git clone`](https://git-scm.com/docs/git-clone) and [`git submodule`](https://git-scm.com/docs/git-submodule) | 2026-08-12 | Shallow clones truncate history; partial clones may omit object contents until needed; submodules are separate repositories recorded by a superproject gitlink and configuration. | Relevant to evidence completeness, but not present in the current topology. | Fact verified; current topology N/A below |

## GitHub sources

| ID | Official source | Verified | Bounded external fact | Project applicability | Decision status |
|---|---|---|---|---|---|
| GH-F01 | GitHub, [status checks](https://docs.github.com/en/pull-requests/reference/status-checks) | 2026-08-12 | Required checks gate merging when configured; conclusions include success, neutral, skipped, failure, cancellation, timeout, and others. | A green-looking workflow still needs required-check interpretation. | Fact verified; settings choice open |
| GH-F02 | GitHub, [troubleshooting required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks) | 2026-08-12 | Required checks must pass for the latest relevant commit SHA; the authoritative SHA can be the head or test-merge commit depending on workflow reporting. | Supports exact-head/base reinspection after a push or base change. | Fact verified; current control to audit |
| GH-F03 | GitHub, [ruleset rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) | 2026-08-12 | Rulesets can require PRs and checks, restrict merge types, require a current base, and block force pushes. | Candidate enforcement surface; no setting change is authorized in Phase 1. | Fact verified; settings choice open |
| GH-F04 | GitHub, [merging a pull request](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-a-pull-request) | 2026-08-12 | Draft PRs cannot merge; repository rules can require reviews, checks, and an up-to-date branch. | Separates active/draft work from merge-ready state. | Fact verified; PR timing open |
| GH-F05 | GitHub, [pull request merges](https://docs.github.com/en/pull-requests/reference/pull-request-merges) | 2026-08-12 | Merge-commit, squash, and rebase methods create different commit-graph identities; indirect merges can close a PR without using its merge button. | Exact patch/PR receipts are needed after squash or selective recovery. | Fact verified; merge method open |
| GH-F06 | GitHub, [auto-merge](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request) and [merge queue](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) | 2026-08-12 | Auto-merge waits for configured requirements; a merge queue validates queued changes against the latest target branch and other queued changes. | Both are factual integration mechanisms; adoption is a later decision. | Fact verified; use open |
| GH-F07 | GitHub, [protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) and [rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) | 2026-08-12 | One branch-protection rule applies at a time, while multiple rulesets can layer and expose rule evaluation; force push and deletion are blocked by default when protection applies unless enabled. | The two governance mechanisms must be inspected separately. | Fact verified; configuration open |
| GH-F08 | GitHub, [deployment environments](https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments) | 2026-08-12 | Environments can gate jobs by approval, branch, custom rules, and secret access; protection must pass before the job is sent to a runner. | Applies to deployment/release evidence, not ordinary branch integration. | Fact verified; configuration open |
| GH-F09 | GitHub, [managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) | 2026-08-12 | A release is created for a selected tag/target and can be draft, prerelease, or published with notes and assets. A release and a Git tag are related but distinct objects. | Applies directly to the repository's release lifecycle. | Fact verified; procedure open |
| GH-F10 | GitHub, [Dependabot security updates](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependabot-security-updates) and [configuration options](https://docs.github.com/en/code-security/reference/supply-chain-security/dependabot-options-reference) | 2026-08-12 | Security-update PRs address known vulnerabilities; version-update PRs address outdated dependencies. Configuration can schedule, group, limit, and target updates. | Applies to the current dependency backlog; compatibility still needs current-base testing. | Fact verified; grouping strategy open |
| GH-F11 | GitHub, [forking a repository](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo) | 2026-08-12 | A fork is a separate repository connected to an upstream; contributors can synchronize it and propose changes through pull requests. | Applies to the open-source external-contributor path. | Fact verified; contributor policy open |

## OpenAI Codex sources

| ID | Official source | Verified | Bounded external fact | Project applicability | Decision status |
|---|---|---|---|---|---|
| OAI-F01 | OpenAI, [Introducing the Codex app](https://openai.com/index/introducing-the-codex-app/) | 2026-08-12 | Codex app tasks run in separate project threads and have built-in worktree support so agents can work from isolated code copies while changes remain reviewable per thread. | Product isolation must still be reconciled with Git's shared refs/configuration. | Fact verified; project mapping open |
| OAI-F02 | OpenAI Help, [Using Codex with your ChatGPT plan](https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan) | 2026-08-12 | Codex is available across app, CLI, IDE, and cloud surfaces under a ChatGPT plan; execution context and capabilities vary by surface and configuration. | A task handoff cannot assume all surfaces have identical local Git state. | Fact verified; handoff contract unresolved |
| OAI-F03 | OpenAI Help, [archive and delete Codex chats](https://help.openai.com/en/articles/20001333) | 2026-08-12 | Archiving hides and retains a Codex chat; deletion requires prior archiving, removes it from history, schedules permanent deletion, and is not recoverable through UI, APIs, or support. | Chat retention is distinct from Git commit/ref/worktree retention. | Fact verified; project retention choice open |

## Current project observations

These are dated local observations, not external facts or policy:

- **OBS-01 — project observation:** on 2026-08-12, `git submodule status`
  returned no entries; the current repository does not use Git submodules.
- **OBS-02 — project observation:** on 2026-08-12,
  `git rev-parse --is-shallow-repository` returned `false`; targeted config
  inspection found no partial-clone promisor or partial-clone extension.
- **OBS-03 — project observation:** the live worktree inventory contained six
  attached branch worktrees and no detached, locked, or prunable entry.
- **OBS-04 — project observation:** the synchronized GIT-001 branch at
  `54a03557` had a tree exactly equal to `origin/main` while retaining the prior
  squash-equivalent research commit as its other ancestry line.
- **OBS-05 — project observation:** the 2026-08-12 synchronization receipt
  recorded a clean branch at its upstream before mutation, a non-rewriting
  merge, a 10/10 quick gate, and a fast-forward push to the existing research
  remote. Evidence: merge commit `54a03557` and this session's command receipt.
- **OBS-06 — current-policy observation:** the current
  [canonical Git workflow](../../git-automation/git-workflow-single-source.md)
  requires branch/worktree/diff/upstream/PR inspection, intended-path staging,
  conventional commits, non-rewriting push, focused checks, a quick pre-commit
  gate, exact check inspection, and fail-closed recovery.
- **OBS-07 — current-policy observation:** the current
  [token-efficiency policy](../../guidelines/ai-token-efficiency.md) limits
  concurrent agents to independent work and avoids parallel writes to
  overlapping files; the future ownership model remains undecided by Phase 1.
- **OBS-08 — project observation:** the
  [GIT-001 disposition plan](GIT-001-next-agent-disposition-plan.md) records the
  prior research squash integration, exact Alpha/Excel/branch cleanup holds,
  retained PMM/workflow refs, and the explicit owner-approval boundary.
- **OBS-09 — project observation:** the current
  [release guidance](../../getting-started/releases.md) and canonical Git
  workflow separate software/artifact gates from owner authorization to publish
  a release or package.
- **OBS-10 — project observation:** the
  [PMM recovery case study](../../git-automation/git-recovery-case-study-column-pmm.md)
  and [Packet 7A](GIT-001-phase-7A-preservation-workflow-recovery.md) record
  preservation-first selective recovery for PMM and PR #723 instead of applying
  either stale mixed branch as a unit.

## Explicitly unresolved product facts

- **UNRESOLVED-OAI-01 — unresolved:** no located public OpenAI contract defines
  how a Codex task snapshot maps to a Git commit, branch, ref, or worktree.
- **UNRESOLVED-OAI-02 — unresolved:** no located public OpenAI contract defines
  when archiving a task removes, snapshots, or retains a managed worktree.
- **UNRESOLVED-OAI-03 — unresolved:** no located public OpenAI contract defines
  a complete task-to-task handoff or recovery guarantee for local Git state.

These gaps may later be addressed by a dated, reproducible product observation,
but Phase 1 does not infer them from the general worktree announcement.

## Coverage disposition

| Required Phase 1 topic | Disposition | Evidence |
|---|---|---|
| Commits, branches, upstreams, fetch, pull, push | Covered | GIT-F06–F10 |
| Merge, rebase, cherry-pick, revert, reset, restore, stash, clean | Covered | GIT-F11–F15 |
| Worktree add/remove/move/lock/prune/repair | Covered | GIT-F03 |
| Hooks, configuration scope, pruning, garbage collection | Covered | GIT-F16–F17 |
| Tags, signatures, release ancestry | Covered | GIT-F18, GH-F09 |
| Submodules, shallow clones, partial clones | Not applicable to current topology; risks covered | GIT-F19, OBS-01–OBS-02 |
| GitHub merge methods, auto-merge, merge queue | Covered | GH-F04–F06 |
| Branch protection, rulesets, status checks | Covered | GH-F01–F03, GH-F07 |
| Environments and releases | Covered | GH-F08–F09 |
| Dependabot | Covered | GH-F10 |
| Forks and external contributors | Covered | GH-F11 |
| Codex parallel task/worktree capability | Covered to the published product boundary | OAI-F01–F02 |
| Codex archive/delete retention | Covered | OAI-F03 |
| Codex snapshot, cleanup, and handoff guarantees | Explicitly unresolved | UNRESOLVED-OAI-01–03 |

## Phase 1 coverage gate

The source register is ready for coverage review when every required topic is
`Covered`, `Not applicable` with dated topology evidence, or `Explicitly
unresolved`. Passing this gate does not approve a Git method, GitHub setting,
cleanup action, or canonical-policy change. Final pass/fail is recorded only
after the factual lifecycle map is independently checked against this register.
