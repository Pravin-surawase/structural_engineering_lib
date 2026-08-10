---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: guide
complexity: intermediate
tags: [git, github, codex, workflow]
---

# Codex-Native Git and GitHub Workflow

This repository uses Codex's native local-Git capability and connected GitHub
access. Legacy shell wrappers that staged, committed, pushed, created pull
requests, merged, recovered, or deleted branches have been retired.

## Ownership boundary

Codex owns the normal development path after the user requests a change:

1. inspect the branch, worktree, diff, upstream, and current pull request;
2. create or switch to a `codex/<task-slug>` branch when a new branch is needed;
3. stage only the intended paths and preserve unrelated user changes;
4. create a conventional commit;
5. push without rewriting history;
6. create or update a draft pull request through connected GitHub;
7. inspect required checks and report their exact state.

Use commit messages in the form:

```text
feat|fix|docs|refactor|test|chore|ci(scope): description
```

Do not add a repository script that automates this lifecycle. Validation scripts
may inspect Git state, but they must not stage, commit, push, merge, reset,
checkout, clean, stash, delete branches, or mutate GitHub state.

## Verified repository defaults

As checked on 2026-08-10:

- the default branch is `main`;
- task branches use the `codex/<task-slug>` prefix;
- the active `main_branch_rule1` ruleset blocks deletion and non-fast-forward
  updates and requires the strict `PR Gate` status check;
- merge commits, squash merges, and rebase merges are enabled in GitHub;
- automatic head-branch deletion is disabled; and
- administrators can technically bypass the ruleset, but this repository's
  policy forbids using that bypass.

These are live settings, not timeless assumptions. Recheck them before changing
repository policy, performing a release, or relying on a specific merge method.

## Branch strategy

Use one short-lived branch for one reviewable outcome. A branch name should say
what changes, not who happens to be working on it:

```text
codex/slab-api-passport
codex/fix-csv-unit-validation
codex/docs-git-workflow
```

Start independent work from the latest verified `origin/main`. Start dependent
work from the exact reviewed commit it requires, and record that dependency in
the task contract. Do not keep using a task branch after it has been squash
merged; start the next task from refreshed `origin/main` so old commits do not
reappear in the next pull request.

| Situation | Branch/base | Preferred integration |
|---|---|---|
| Feature, fix, docs, or maintenance packet | New `codex/<task-slug>` from `origin/main` | Squash PR into `main` |
| Two independent tasks | Separate worktrees and branches from the same verified base | Review and integrate one PR at a time |
| Task B depends on Task A | Serialize when practical; otherwise base B on A's exact reviewed commit | Integrate A first, then reconcile B against refreshed `main` |
| Emergency fix | Fresh narrow branch from `origin/main` | Normal PR and required checks; never push directly to `main` |
| Experiment | Explicitly named experimental branch | Preserve until accepted or explicitly abandoned; do not merge by accident |

Avoid long-lived development branches and stacked pull requests unless the
dependency is real and documented. They increase repeated conflict resolution,
base drift, and cleanup ambiguity.

## Practical task flow

### 1. Inspect before editing

```bash
git fetch --prune origin
git status --short --branch
git worktree list --porcelain
git log --oneline --decorate -8
./run.sh task brief "concrete task description"
```

Confirm the exact base, worktree, branch, owned paths, dirty state, upstream,
and current PR. A clean-looking branch is not enough if another worktree owns
the same files or the branch contains unpublished commits.

### 2. Create the task lane

- Use a Codex-managed Worktree whenever another write task is active.
- Use Local for the foreground or integration lane when practical.
- Give every worktree a unique branch. Never override Git's protection against
  checking out one branch in two worktrees.
- Record shared-file ownership before editing generated indexes, task ledgers,
  lock files, manifests, routes, registries, or session handoffs.

### 3. Commit intentionally

Before every commit:

```bash
git status --short
git diff
git diff --cached
```

- Stage only task-owned paths.
- Keep each commit logically complete and buildable where practical.
- Put generated artifacts in the same commit as the source change that
  requires them.
- Keep secrets, virtual environments, caches, build output, editor files, and
  unrelated formatting out of commits.
- Never use `--no-verify`; fix the root cause of a failing hook.

### 4. Keep the branch current deliberately

Fetch first; do not use an ambiguous `git pull` as a repair command. Inspect
divergence explicitly:

```bash
git fetch --prune origin
git status --short --branch
git log --left-right --cherry-pick --oneline origin/main...HEAD
```

For a pushed or shared task branch, prefer a deliberate base update that does
not rewrite commits other work may reference, then rerun the affected checks.
Never rebase, reset, or force-push another task's branch. If a local unpublished
branch must be rebuilt, its owner first proves the commits are recoverable and
records the exact replacement plan.

### 5. Publish through a pull request

- Run focused tests while editing and the required closeout gate before push.
- Push the task branch without rewriting history.
- Open a draft PR early enough for the diff and checks to be visible.
- In the PR body, state what changed, why, user impact, root cause when
  applicable, verification, and explicit holds/non-goals.
- Recheck the expected head SHA, base branch, mergeability, review threads, and
  required checks immediately before integration.

### 6. Choose the merge method

Use **squash merge by default** for bounded task branches. It produces one
revertable `main` commit and removes work-in-progress commit noise. Use a merge
commit only when preserving a meaningful multi-commit or dependency boundary
is more valuable than linear history. Use rebase merge only for an intentionally
curated commit series; do not confuse GitHub's rebase-merge option with
rewriting a shared local branch.

Whatever method is selected, required checks must pass and the exact reviewed
head must remain unchanged. Never use the administrator bypass.

### 7. Close the lane

After the PR is integrated:

1. verify the PR is merged and the result is present on refreshed `origin/main`;
2. verify no open PR uses the branch as its head or base;
3. verify the worktree is clean and the task commit is recoverable from the
   merged PR or another retained ref;
4. remove the linked worktree;
5. delete the exact local and remote task branches with owner approval; and
6. run `git fetch --prune origin` and `git worktree prune --dry-run --verbose`.

Do not classify a branch as stale from age alone. A clean branch can still be a
handoff-ready lane containing the only reference to required work.

## Daily Git checklist

| Need | Command or evidence |
|---|---|
| Current lane | `git status --short --branch` |
| Recent history | `git log --oneline --decorate -8` |
| Unstaged/staged review | `git diff` / `git diff --cached` |
| Remote truth | `git fetch --prune origin` |
| Base divergence | `git log --left-right --cherry-pick --oneline origin/main...HEAD` |
| Worktree ownership | `git worktree list --porcelain` |
| Recoverable unpublished work | clean branch plus exact commit SHA and remote/retained ref |
| PR state | exact head/base, mergeability, reviews, and required checks |
| Cleanup candidate | merged/closed PR, no dependent open PR, clean worktree, recoverable commit |

## Failure and recovery tips

- **Detached HEAD:** identify the expected task and commit before creating or
  switching any branch.
- **Behind or diverged:** fetch and inspect both sides; do not guess whether to
  merge, rebase, or discard.
- **Conflict in progress:** record the operation and conflicted paths, then
  resolve only with known ownership. Never use `git rebase --skip`.
- **Dirty foreign files:** stop and find the owning task. Do not stash, reset,
  clean, or check out over another lane.
- **Hook rewrote generated files:** inspect the exact change, stage it only when
  it belongs to the task, and retry the commit without bypassing the hook.
- **Squash-merged branch looks unmerged locally:** use the merged PR and patch
  evidence, not ancestry alone, before cleanup.
- **Unsure whether work is recoverable:** preserve the branch and worktree.

## Official references

- [Git basic branching and merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging.html)
- [Git worktree documentation](https://git-scm.com/docs/git-worktree.html)
- [GitHub merge methods](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github)
- [GitHub rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [Keeping a PR branch in sync](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/keeping-your-pull-request-in-sync-with-the-base-branch)
- [Deleting and restoring merged PR branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/deleting-and-restoring-branches-in-a-pull-request)

## Verification before publication

- Run focused checks while editing.
- Run `./run.sh check --quick` before the reviewed commit.
- Run the full `./run.sh check` gate once at closeout for high-risk, merge, or
  release work.
- Never bypass pre-commit hooks or required GitHub checks.
- A green software gate is evidence about the software, not structural design
  approval or formula certification.

## Parallel worktrees

Concurrent tasks follow the canonical
[parallel-task policy](../guidelines/parallel-task-policy.md). Each write task
uses a dedicated worktree and unique `codex/` branch from an exact base, owns
disjoint paths, and names one integration owner. The Local checkout should
normally remain the foreground/integration lane.

Git worktrees isolate working files, `HEAD`, and index state; they do not make
overlapping logical changes safe. Treat task boards, session handoffs, lock
files, generated indexes, API manifests, and public registries as single-writer
surfaces. Never bypass Git's one-branch-per-worktree safeguard with `--force`.

## Fail-closed recovery

When Git is detached, behind, diverged, conflicted, or in the middle of a merge,
rebase, or cherry-pick, Codex must inspect and report the exact state before any
mutation. Preserve staged, unstaged, untracked, and stashed work. Do not run an
automatic reset, clean, checkout, stash/drop, rebase, or force push.

If resolution requires choosing which user changes or commits to keep, stop and
ask the user. A normal implementation request does not authorize discarding
work.

## Owner-approved operations

The following require explicit user confirmation immediately before execution:

- closing an issue or pull request;
- deleting a local or remote branch;
- publishing a release or package;
- rewriting pushed history.

Codex may mark an in-scope pull request ready and merge it without additional
user confirmation when the reviewed head commit is unchanged, required checks
pass, and there are no conflicts or unresolved blockers. Re-inspect the PR if
its head or base changes. Never use administrator bypasses, `--no-verify`,
`--force`, or an equivalent escape hatch.

## Local hooks

The standard `pre-commit` framework may validate a commit. Repository hooks must
not block Codex-native Git merely because a legacy wrapper environment variable
is absent. `core.hooksPath` must not point to the retired enforcement hooks.

## Historical material

Older session logs, audits, learning chapters, and archived documents may name
the retired shell workflow. Those records are historical evidence, not current
instructions. This file, `AGENTS.md`, and the current session instructions are
authoritative.
