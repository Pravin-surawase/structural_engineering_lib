---
owner: Main Agent
status: active
last_updated: 2026-08-15
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

## Compact audited integration

Use three roles for work that needs independent acceptance:

- the **orchestrator** freezes scope, non-goals, acceptance rows, maintained
  callers, shared/generated owners, commands, timing labels, and the candidate
  ceiling, then decides acceptance;
- the **single writer** alone edits implementation, tests, receipts, shared
  documents, session records, and generated indexes; and
- the **independent auditor** stays read-only, derives falsification cases from
  the frozen contract rather than writer fixtures, and audits one exact commit
  and tree across every acceptance row before reporting.

The stage gates are:

1. **Contract freeze:** record the complete acceptance and schema/cross-field
   matrices, adversarial cases, maintained callers, non-goals, path ownership,
   focused commands, and evidence expected at closeout.
2. **Focused implementation:** use focused checks while writing. After content
   freezes, the sole writer updates already-maintained generated projections,
   reruns focused checks, and runs the sole quick gate.
3. **Immutable local audit:** only then commit a clean local candidate and pause
   before push. Give the auditor its exact base, head, tree, diff, focused
   evidence, and quick-gate result.
4. **Consolidated decision:** the auditor returns either `PASS <head> <tree>` or
   one deduplicated blocker list with reproduction, main-process impact, and
   required outcome after completing the whole matrix.
5. **Candidate ceiling:** allow the initial candidate and at most one
   consolidated repair candidate. A second rejection triggers contract/design
   re-planning; do not start another patch cycle.
6. **Final local gate:** only after independent local PASS on the unchanged
   head, run one final full gate.
7. **Hosted closeout and merge:** push once, complete one hosted CI/review
   closeout, and immediately recheck the exact head/tree, base, required checks,
   reviews, unresolved threads, conflicts, and mergeability. Merge only the
   unchanged auditor-approved head; a changed head returns to local audit.
8. **Post-merge verification:** refresh `main` without destructive cleanup and
   verify the merge identity, reviewed-tree equivalence where relevant,
   integrated checks, and task/handoff/receipt truth. Retain branches and
   worktrees unless deletion is separately authorized.

The mutation cutoff is strict: finish versioned session/task/handoff records,
local evidence, and the pre-commit receipt first; refresh only affected
maintained indexes once as the final repository write; then commit the immutable
candidate. PR numbers, hosted-check results, and merge identities are external
facts and must not be appended to that same candidate after push. A material
post-push defect creates an explicit repair candidate and invalidates the prior
audit; routine status reporting never creates a second documentation commit.

Do not claim a candidate is complete, final, ready, or merge-eligible before the
independent PASS bound to its unchanged head and tree. Do not start hosted CI
before that PASS.

Record every material issue in the task-owned session entry with this minimal
shape (use `unconfirmed` until the root cause is proved):

```markdown
### <issue title>
- Symptom:
- Main-process impact:
- Confirmed root cause:  # or `unconfirmed`
- Fix:
- Proof:
- Recurrence control:
```

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

## Durable task-to-Git handoff

Use `scripts/git_handoff_receipt.py` for a versioned machine-readable handoff.
It consumes local facts only from `scripts/git_state.py`; remote, PR, review,
check, integration, retention, authorization, and next-action facts must be
caller-supplied and identity-bound. The receipt records its
`local_state_receipt_hash`, exact branch/head/upstream/base/worktree/tree/
operation state, hosted identities or explicit `UNKNOWN`/`NOT_CHECKED`, reviewed
head/base/tree, retention evidence, and authorization boundaries.

The receipt records authority evidence but grants no authority itself;
`receipt_grants_authority` must be `false`. Authorization evidence requires a
named external source plus exact task, branch, head, and action binding.
Authorization observations and the nested external-source evidence must each
retain caller-supplied status/query/time and be fresh and query-successful;
validation never fabricates or upgrades those facts. The next action must be
either a closed safe hold/wait action
or one of the externally authorized actions bound to that exact target;
destructive or merge actions cannot be injected as an unbound next action.
Serialized `holds` and `receipt_status` are not trusted: validation independently
recomputes the required hold set from evidence and rejects missing holds, false
`READY`, malformed next actions, or action/provenance contradictions. External
authorization never erases remote, PR, review, check, retention, or local-state
holds.

Missing, malformed, stale, query-failed, or contradictory facts are holds.
`NOT_APPLICABLE` requires a reason and cannot replace unknown evidence. A
squash-merged PR requires reviewed-tree/merged-tree equivalence and never makes
ancestry or task archive state into retirement authority. Receipt validation is
read-only and performs no fetch, prune, ref/worktree mutation, or GitHub query.

Session handoff validates the versioned receipt, embeds its path/hash and exact
identity summary into `next-session-brief.md`, and fails closed if the receipt
is missing or invalid. The full JSON remains the audit contract; prose and PR
numbers alone are not a durable Git receipt.

A task-to-Git handoff receipt is a time-bound transition observation, not a
permanent final-merge receipt. Its external authorization, retention, remote,
review, and check evidence is expected to become stale and fail closed later;
never rewrite the historical file merely to make it validate as current. A
fresh successor closeout observation must bind the final reviewed head, hosted
checks, merge commit, and merged tree. This separation is unavoidable for a
squash merge because the unchanged pre-merge candidate cannot know its future
merge identity.

## Verification before publication

- Follow the compact audited-integration gates above when independent acceptance
  is required. Routine low-risk work still uses focused checks, then
  `./run.sh check --quick` before publication and the full `./run.sh check` once
  at closeout when its risk or release scope requires it.
- Never bypass pre-commit hooks or required GitHub checks.
- A green software gate is evidence about the software, not structural design
  approval or formula certification.

## Inspection-only branch disposition

Use `./scripts/python_runtime.sh scripts/classify_branch_disposition.py` to
inspect exact branch targets. The classifier performs local, optional-lock-safe
Git reads and consumes caller-supplied, timestamped remote/PR/retention evidence.
It does not fetch, prune, mutate GitHub, change refs/config/worktrees, or delete.
`NOT_CHECKED`, missing ownership, inconsistent SHAs, and query failures are
`UNKNOWN` holds. Age is receipt metadata only.

Even a fully evidenced target is only
`RETIREMENT_READY_PENDING_APPROVAL`. Local branch, remote branch, and worktree
actions remain separate exact-target authorization decisions followed by a
same-session reinspection and post-action receipt.

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
