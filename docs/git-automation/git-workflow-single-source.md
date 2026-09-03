---
owner: Main Agent
status: active
last_updated: 2026-09-03
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

Before publishing or merging any side packet, run an active-candidate
dependency check across task-owned worktrees: bind each unmerged candidate's
base/head, compare changed paths, and identify shared/generated owners. If the
side packet would advance `main` ahead of an active candidate or overlaps its
shared/generated paths, hold the side merge until the predecessor integrates
or the candidate is explicitly replanned and rebound. Worktree isolation
protects working files and indexes; it does not freeze shared refs or make
merge ordering independent.

Use commit messages in the form:

```text
feat|fix|docs|refactor|test|chore|ci(scope): description
```

Do not add a repository script that automates this lifecycle. Validation scripts
may inspect Git state, but they must not stage, commit, push, merge, reset,
checkout, clean, stash, delete branches, or mutate GitHub state.

## Multi-device rule: one branch, one writer device

GitHub is the shared authority for tracked repository history; an open checkout
on a Mac or Windows laptop is not. Use this simple default:

> One task branch has one active writer device. Merge through GitHub. Every
> other device fetches and fast-forwards its local `main` before new work.

### Primary-development and installed-evidence devices

A programme may name different machine roles without changing GitHub's
authority or the one-writer rule:

| Role | Owns | Must not assume |
|---|---|---|
| Primary development/integration device | Normal source work, planning, local cross-platform tests, candidate review, PR creation, hosted-check follow-up, and integration | That a clean local checkout contains device-only installed evidence |
| Installed-evidence device | Exact installed-application runs, device-only APIs, copied models/workbooks, screenshots/logs, safe external evidence, and bounded host-specific repairs | That its local `main`, open checkout, application state, or unpushed branch is shared history |
| GitHub | Tracked branch/PR/merge history and the exact transfer boundary between devices | Device-local models, workbooks, credentials, or external evidence bytes |

The Excel + ETABS programme designates the **Mac as the primary development and
integration device** and **Windows as the installed Excel/ETABS evidence
device**. The programme-specific scope and evidence rules live in
[`excel-etabs-beam-next-phase-plan.md`](../planning/excel-etabs-beam-next-phase-plan.md).
Windows may implement a bounded host-specific repair on its own task branch,
but it becomes the sole writer for that branch until it commits, verifies,
pushes, and explicitly hands writer ownership back to the Mac.

Use this handoff sequence:

1. The originating device proves a clean candidate, pushes its exact task
   branch, records the remote head, then stops writing that branch.
2. The receiving device fetches and verifies `origin/<task-branch>` and the
   advertised commit before creating a worktree or continuing it.
3. The Mac performs normal review/integration. If it repairs the same branch,
   Windows remains read-only until the Mac pushes and hands it back.
4. Windows installed acceptance uses an exact fetched candidate or merged
   commit in a dedicated evidence worktree; it never relies on a stale local
   `main` or copies source files through OneDrive/SMB.
5. Application models, workbooks, credentials, and proprietary evidence remain
   device-local. Only approved hash-bound receipts and safe summaries enter
   Git.

At the start of work on each device:

First verify the actual command working directory, repository root and remote.
A saved app project folder or display label can differ from an existing task's
working directory. In the September XLL handoff, changing the project folder
left the running task in its old OneDrive workspace. Select the verified
checkout explicitly for commands and edits, or reopen the task there; do not
initialize another repository or infer identity from a folder name. A local
intake folder is not shared history until its intended documents are committed
and the exact remote branch is verified.

```bash
git rev-parse --show-toplevel
git remote get-url origin
git fetch origin
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Confirm the exact current branch, working-tree state, upstream, open pull
request, and fetched `origin/main`. A clean checkout can still be stale. If the
local `main` is clean and is an ancestor of `origin/main`, synchronize it only
by fast-forward:

```bash
git switch main
git merge --ff-only origin/main
```

Create the next `codex/<task-slug>` branch from that synchronized `main`. Do not
continue new work on an old merged branch merely because it is clean.

If another device has pushed work that is not merged, review and integrate it
through its pull request; do not copy files between devices. Keep writing on
the originating device, or make an explicit one-writer handoff after confirming
that its branch is clean and fully pushed. Concurrent devices use distinct
branches, and overlapping/shared paths require an explicit merge order.

If `git_state.py` reports dirty, detached, behind, diverged, locked, or an
active Git operation, stop before switching or pulling. Inspect the exact diff,
PR, and remote branch first. For a squash-merged branch, `git cherry
origin/main HEAD` can show that a different commit identity already has the
same patch; this is evidence for planning, never automatic reset or deletion
authority.

After a merge from any device:

1. verify the PR, required checks, merge commit, and candidate/merge tree;
2. close the originating task's session-usage checkpoint while its timing is
   still available;
3. fetch on every device before its next task, then fast-forward local `main`;
4. keep device-local ETABS models, workbooks, credentials, and external evidence
   outside Git unless their tracked contract explicitly requires otherwise;
5. retain old branches and worktrees until deletion is separately authorized.

Fetching updates remote-tracking references but does not update the checked-out
files. A device is current only after its intended checkout is verified against
the fetched commit.

A single-branch evidence clone may fetch only `main`. In that case `push -u`
can record an upstream name without creating its remote-tracking ref; a later
local report of upstream `NONE` is not proof that the remote branch is absent.
Inspect the configured fetch refspec and exact remote head. On a receiving
device, fetch the advertised branch explicitly into its remote-tracking ref
before binding a worktree. Do not silently broaden another clone's fetch
configuration, move its checkout or treat an unqueried Mac as synchronized.

Before implementation, the maintained `session begin` preflight verifies
source binding, local Git state and the active standard pre-commit hook. Use
`./run.sh preflight --environment-only --json` for a standalone read-only
diagnostic. A missing/custom hook is an inspection hold, never authority to
overwrite it. Host-local environment setup must preserve cwd unless an exact
repository is explicitly requested; portable repository scripts contain no
Mac/Windows owner-specific absolute root.

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
   freezes, the sole writer updates already-maintained generated projections
   and reruns the affected focused checks.
3. **Immutable local audit:** only then commit a clean local candidate and pause
   before push. Give the auditor its exact base, head, tree, diff, focused
   evidence, and any explicit risk-driven local-gate result.
4. **Consolidated decision:** the auditor returns either `PASS <head> <tree>` or
   one deduplicated blocker list with reproduction, main-process impact, and
   required outcome after completing the whole matrix.
5. **Candidate ceiling:** allow the initial candidate and at most one
   consolidated repair candidate. A second rejection triggers contract/design
   re-planning; do not start another patch cycle.
6. **Final local gate:** after local PASS on the unchanged head, use the
   verification ladder in `AGENTS.md`: full gate once at cumulative milestone
   closeout, or earlier for repository-wide risk. Do not interpret this step as
   an additional full-suite run for every dependency-stable packet.
7. **Hosted closeout and merge:** push once, complete one hosted CI/review
   closeout, and immediately recheck the exact head/tree, base, required checks,
   reviews, unresolved threads, conflicts, and mergeability. Merge only the
   unchanged auditor-approved head; a changed head returns to local audit.
8. **Post-merge verification:** refresh `main` without destructive cleanup and
   verify the merge identity, reviewed-tree equivalence where relevant,
   integrated checks, and task/handoff/receipt truth. Retain branches and
   worktrees unless deletion is separately authorized.

At closeout, record the seven non-overlapping wall-time phases, exact candidate
heads, rejection/repair/retry counters, full-gate count, and hosted-run count in
the Git-common ignored `session usage` ledger. The total is derived from the
task's unmatched `session begin` timestamp, not entered independently. Hosted
closeout binds the PR and reachable merge commit and requires final
candidate/merged-tree equality; this successor external observation can mask a
frozen pre-push task row from later compact briefs without changing the
candidate.

The mutation cutoff is strict: finish versioned session/task/handoff records,
local evidence, and the pre-commit receipt first; refresh only affected
maintained indexes once as the final repository write; then commit the immutable
candidate. PR numbers, hosted-check results, and merge identities are external
facts and must not be appended to that same candidate after push. A material
post-push defect creates an explicit repair candidate and invalidates the prior
audit; routine status reporting never creates a second documentation commit.

An authorized merge-resolution candidate is the narrow exception handled by
the commit operation guard: `git_state.py` must report `HOLD_OPERATION` until
the resolving merge commit exists. After all conflicts are resolved and the
unmerged-path set is empty, the pre-commit operation guard accepts completion only
on a named non-main branch when HEAD plus the pending merge parent contain
every required default/upstream ref. Locks, unknown queries, other operations,
and unrelated behind/diverged refs remain blockers. The completion flag never
weakens ordinary operation-free validation. Run focused/content checks, create the merge commit
through the normal safety hooks, then continue to independent audit or the
batched PR. A content or hook failure remains
a blocker; this exception never permits bypassing hooks or auditing an open
merge.

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

Run the final read-only session closeout while the transition receipt is fresh,
before push. A later freshness failure means that the retained observation has
aged; it does not corrupt the historical artifact or authorize a candidate
rewrite. Final hosted and merge facts belong only to the successor external
closeout observation.

## Verification before publication

- Follow the compact audited-integration gates above when independent acceptance
  is required. Routine work uses focused diagnostics locally and one batched PR
  for comprehensive assurance. Run `./run.sh check --quick` or the full local
  gate only when a named cumulative/release boundary or investigation requires it.
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

The standard `pre-commit` framework protects the local mutation boundary with
exactly three ordinary-commit hooks: merge-conflict markers, newly added files
over 500 KB, and the live Git-operation guard. The six generic file-integrity
hooks use the manual stage and run in PR Repository Validation. Formatting,
linting, type checks, security scans, tests, generated-contract checks, and the
quick gate are not commit hooks. Repository hooks must not block Codex-native
Git merely because a legacy wrapper environment variable is absent.
`core.hooksPath` must not point to the retired enforcement hooks.

## Historical material

Older session logs, audits, learning chapters, and archived documents may name
the retired shell workflow. Those records are historical evidence, not current
instructions. This file, `AGENTS.md`, and the current session instructions are
authoritative.
