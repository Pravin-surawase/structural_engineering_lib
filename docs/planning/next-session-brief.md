# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-12
- Focus: GIT-001 Phase 1 continuation and evidence-gated repository disposition
<!-- HANDOFF:END -->

**Current release:** `v0.23.1a1` Alpha

**Published plan receipt:** PR #741 merged as `52ac5f58`; refresh `main` before work

**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | GIT-001 Phase 1 | Synchronize the research lane, finish official-source coverage, and write the factual lifecycle map |
| **Next** | Excel planning lane | Confirm a named active owner/next action or approve retirement |
| **Approval-gated** | Alpha worktrees and merged branches | Exact evidence is ready; deletion still requires explicit target approval |
| **Separate maintenance** | Seven dependency PRs | Replace one-by-one merging with four current-base compatibility packets |

## Required Reading

1. [Reconciled future-work and disposition plan](../research/git-governance/GIT-001-next-agent-disposition-plan.md)
2. [GIT-001 research index](../research/git-governance/GIT-001-README.md)
3. [Official evidence register](../research/git-governance/GIT-001-official-evidence-register.md)
4. [Lifecycle research](../research/git-governance/GIT-001-lifecycle-research.md)
5. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
6. [AI token-efficiency policy](../guidelines/ai-token-efficiency.md)

## Start command

```bash
./run.sh task brief "continue GIT-001 Phase 1 official research"
./run.sh session brief --agent ops
./run.sh session start
```

Then refresh and inspect the branch, upstream, worktree, diff, current PR, and
all linked worktrees before mutation. The dated handoff is evidence, not a
replacement for live inspection.

## Current Git facts

- The dedicated GIT-001 worktree is clean at `3be4790d`, one commit ahead and
  six behind current `main` by ancestry. `git cherry` shows its patch is already
  squash-integrated. Merge current `origin/main` into this shared branch after
  exact clean/upstream checks; do not rebase or force-push it.
- Column PMM preservation, selective recovery, independent benchmark,
  integration, closeout, and learning update are complete through PRs #738-#740.
  Historical remote refs remain evidence; PMM remains experimental.
- PR #723 is closed without merge. Its useful behavior was selectively rebuilt
  through PRs #736-#737. Use #723 as incident evidence, not a merge target.
- Excel planning has no unique commit, remote feature branch, or PR. Git supports
  retirement, but task ownership still needs an owner decision.
- Three merged Alpha worktrees are clean and retirement-ready after explicit
  approval. They occupy roughly 651 MB, mainly old `node_modules`.
- Eight unattached merged local branches, not seven, now have exact PR and main
  reachability receipts. Local and remote deletion require separate approval.
- All seven remaining Dependabot PRs are behind current `main`; their old green
  checks are stale for integration.

## Phase 1 boundary

Finish official coverage for core Git operations and recovery, GitHub merging
and governance, dependency automation, releases/contributors, and verified
Codex task/worktree behavior. Then produce the source-backed lifecycle map for
normal, parallel, integration, release, cleanup, and recovery paths.

Every statement must be labeled as an external fact, project observation,
unresolved choice, or not applicable. Do not change canonical policy, GitHub
settings, hooks, or cleanup behavior during Phase 1. Do not advance to Phase 2
until the coverage review explicitly passes.

## Destructive-action holds

- Do not remove Excel until the owner decides whether the planning task is active.
- Do not remove Alpha worktrees until the owner approves the three exact paths.
- Do not delete local or remote branches without an exact refreshed table and
  explicit approval for that deletion scope.
- Stop if a lane becomes dirty, attached unexpectedly, diverged, conflicted, or
  gains new commits/PR activity. Never reset, clean, stash, rebase, or force-push
  as a shortcut around uncertain ownership.

## Dependency grouping

- Python typing: PRs #715 and #717 together.
- ESLint 10: PRs #713 and #683 together.
- React build: hold #684 for coordinated Vite/toolchain compatibility.
- Node types: hold #714 while repository runtime remains Node 24.
- Motion: #716 can be an independent current-base frontend task.

Each group gets a fresh worktree, a compatibility hypothesis, targeted checks,
the complete relevant gate, and exact-head CI. Do not merge the seven old PRs
as unrelated updates.

## Session closeout

Run the quick gate and the full relevant gate once at closeout. Record every
material issue as symptom, impact, confirmed root cause, solution, and evidence
in the newest `docs/SESSION_LOG.md` entry. Preserve shared-surface ownership:
session/task records, generated indexes, registries, routes, manifests, and
lockfiles have one writer at a time.
