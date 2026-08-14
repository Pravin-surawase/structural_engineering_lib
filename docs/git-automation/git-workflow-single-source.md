---
owner: Main Agent
status: active
last_updated: 2026-08-13
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

## Read-only Git state authority

Use `./scripts/python_runtime.sh scripts/git_state.py` as the sole semantic
authority for local Git state. It uses porcelain v2 and the invoking worktree's
real Git/common paths, disables optional locks, performs no network request by
default, and reports remote freshness as `NOT_CHECKED`.

- `--json` emits typed current-lane evidence;
- `--worktrees --json` adds bounded sibling-worktree summaries;
- `--strict` succeeds only for `READY_LOCAL`;
- `--guard operation` and `--guard branch` provide narrow fail-closed checks.

Task brief, session trust, and the quick Git gate consume this authority.
`READY_LOCAL` is the only trusted local state. `HOLD_MAIN`, `HOLD_DETACHED`,
`HOLD_DIRTY`, `HOLD_OPERATION`, `HOLD_LOCKED`, `HOLD_BEHIND`,
`HOLD_DIVERGED`, and `HOLD_UNKNOWN` are evidence states, not recovery commands.
Ahead and no-upstream are publication facts rather than local-safety failures.
The retained shell entrypoints are compatibility delegates and must not contain
independent Git classification.

## Verification before publication

- Run focused checks while editing.
- Run `./run.sh check --quick` before the reviewed commit.
- Run the full `./run.sh check` gate once at closeout for high-risk, merge, or
  release work.
- Never bypass pre-commit hooks or required GitHub checks.
- A green software gate is evidence about the software, not structural design
  approval or formula certification.

## Fail-closed recovery

When Git is detached, behind, diverged, conflicted, or in the middle of a merge,
rebase, or cherry-pick, Codex must inspect and report the exact state before any
mutation. Preserve staged, unstaged, untracked, and stashed work. Do not run an
automatic reset, clean, checkout, stash/drop, rebase, or force push.

If resolution requires choosing which user changes or commits to keep, stop and
ask the user. A normal implementation request does not authorize discarding
work.

When recovering useful work from a stale or mixed historical branch, preserve
the exact commit first and treat it as evidence rather than applying it as a
unit. Create a fresh worktree from current `main`, recover only the intended
paths or hunks, verify runtime/source identity, and establish any missing domain
evidence before publication. Squash integration changes commit identity, so
cleanup must consider the PR receipt, content, tests, and retained remote refs;
ancestry alone is insufficient.

See the worked [Column PMM recovery case study](git-recovery-case-study-column-pmm.md)
for the complete branch/worktree, script, benchmark, CI, and cleanup sequence.

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
