---
owner: Main Agent
status: active
last_updated: 2026-08-13
doc_type: reference
task: GIT-001
phase: 3
---

# GIT-001 Phase 3 — Outcome-Focused Gap and Risk Matrix

## Decision boundary

This matrix compares five evidence layers:

1. official Git/GitHub/Codex facts from Phase 1;
2. the ten project incident families from Phase 2;
3. current canonical repository policy;
4. live GitHub settings, workflows, scripts, and instructions;
5. observed executable behavior on 2026-08-13.

A gap is retained only when closing it would change the outcome of the main
development, integration, recovery, cleanup, or release process. Optional
hardening, generic test wishes, and cosmetic script improvements are excluded.
This is a non-normative analysis; it changes no policy or implementation.

## Priority model

| Priority | Meaning |
|---|---|
| P0 | Can integrate, overwrite, delete, or validate the wrong work while existing controls appear satisfied |
| P1 | Can block or materially repeat the main process, obscure ownership, or produce an incomplete release/PR receipt |
| P2 | Adds recurring latency or friction but does not independently corrupt or misclassify work |

## Outcome matrix

| ID | Surface | Observed gap | Main-process failure | Priority | Phase 4 design requirement |
|---|---|---|---|---|---|
| G3-01 | GitHub main ruleset | Strict `PR Gate` is required, but no pull-request rule is present and an always-bypass repository role includes the authenticated owner | A direct main update or bypass can integrate without the reviewed PR/check path the repository claims is mandatory | P0 | Server policy must require PR integration and make any emergency bypass explicit, narrow, attributable, and separately reviewed |
| G3-02 | Remote branch cleanup | `cleanup_stale_branches.py` can delete and selects by age/ancestry; Git errors can collapse to empty output and therefore look merged/old | Unpublished or squash-integrated evidence can be nominated or deleted from incomplete proof | P0 | Repository automation becomes inspection-only; disposition requires refreshed refs, attachment, ownership, PR, reachability, patch/tree, approval, and post-action receipt |
| G3-03 | Git state validation | Required quick-gate scripts use `.git/MERGE_HEAD`, which is not the linked-worktree Git directory; rebase/cherry-pick/revert/bisect/lock state is incomplete, divergence counts are mislabeled, and recovery text suggests pull/reset | A linked lane can be reported safe while an operation is in progress, then receive destructive or incorrect recovery guidance | P0 | One worktree-aware read-only state kernel must fail closed and return typed evidence without suggesting mutation |
| G3-04 | Automation CI selection | `scripts/**` changes run syntax/policy checks, but the PR workflow does not run the maintained session/task/runtime outcome regressions; even the Python job runs only a fixed structural subset | A broken intake, trust, generator, or worktree-runtime control can merge with green required CI | P0 | Path classification must route control-plane changes to focused automation tests and keep the aggregator fail closed |
| G3-05 | Task intake | `task brief` reports upstream as its base, omits default-branch ahead/behind, operation state, staged/unstaged/untracked classes, ref freshness, and current PR/check identity | A stale/diverged/operation-active lane can receive the same “safe start” text as a current isolated lane | P1 | Intake must classify local lane, default base, upstream, operation state, sibling ownership, and publication state separately |
| G3-06 | Generated data | `run.sh generate indexes` exposes only all-folder generation; the underlying targeted/dry-run capability is not routed in the canonical command | A bounded edit can rewrite unrelated shared projections and expand conflicts/review scope | P1 | Generation must preview exact owned targets, support explicit targeted mode, refuse unexpected new topology, and produce a changed-path receipt |
| G3-07 | Instruction drift | Live instructions still prescribe unsupported `--dry-run`/`--fix`, direct-main work, or retired command names while `check_codex_git_workflow.py` passes | An agent can follow a maintained-looking document into a failed or prohibited workflow | P1 | One semantic drift check must cover all live instructions against the canonical command/policy vocabulary; historical material stays clearly excluded |
| G3-08 | Fragmented guards and permissions | `validate_git_state.sh`, `check_unfinished_merge.sh`, `check_not_main.sh`, task brief, session trust, and the automation map encode different branch/operation semantics; several permissions are unspecified | Different entrypoints can permit, warn, or block the same state inconsistently | P1 | All consumers must use one typed state model and declared read/write permission; thin commands may format but not reinterpret it |
| G3-09 | Documentation PR proof | Strict MkDocs build runs in a separate workflow that is not required by the main ruleset; its single global concurrency group can cancel another PR's build | Public documentation can merge after `PR Gate` even when its exact-head strict build failed or was cancelled | P1 | Documentation build evidence must bind to the same PR head and be required directly or represented fail-closed in the required aggregator |
| G3-10 | Merge identity | Repository settings allow merge commits, squash, and rebase without a project decision mapping method to lane type and retention | Later synchronization and cleanup repeatedly encounter avoidable patch-versus-ancestry ambiguity | P1 | Phase 4 must choose allowed merge methods by branch/lane class and define the receipt each method requires |
| G3-11 | Task-to-Git handoff | No public Codex guarantee binds a task snapshot/archive/handoff to a commit, branch, worktree, upstream, or PR; current project handoffs are prose | A task can be archived or transferred while recoverable Git state is unknown or misidentified | P1 | Add a project-owned, read-only handoff receipt with exact identities and explicit unknown/dirty/operation holds; do not infer product guarantees |
| G3-12 | Read-only Git monitoring | Task brief invokes normal `git status` across every sibling worktree without disabling optional locks | Background intake can refresh indexes or contend with an active lane despite being described as inspection-only | P1 | Monitoring queries use `GIT_OPTIONAL_LOCKS=0`, bounded timeouts, and explicit unknown results instead of touching another lane's index |
| G3-13 | Quick-gate latency | `validate_git_state.sh` performs a network `ls-remote` and recursive large-file scan; it took 4.05 seconds in the current linked lane | Every quick gate pays remote/filesystem cost unrelated to local commit safety, slowing iteration and creating network-dependent warnings | P2 | Separate sub-second local state classification from opt-in remote freshness and repository-hygiene checks |

## Evidence by gap

### G3-01 — server enforcement does not match the claimed PR boundary

Live repository metadata reported all three merge methods enabled, auto-merge
disabled, and update-branch disabled. Ruleset `main_branch_rule1` is active for
`refs/heads/main` with deletion, non-fast-forward, and strict required-status
rules for `PR Gate`. Its rule list contains no pull-request requirement. It also
contains an `always` bypass for a repository role, and the authenticated owner
reported `current_user_can_bypass: always`. The legacy branch-protection REST
surface returned `404 Branch not protected`, confirming the ruleset is the
active enforcement surface rather than an additional protection layer.

This is not a claim that a bypass occurred. It is a live mismatch between the
server's permitted path and the canonical workflow's required path.

### G3-02 — cleanup combines incomplete classification with mutation

The maintained cleanup script:

- runs `git fetch --prune` even in its default review path;
- ignores Git subprocess return codes;
- treats empty log/date output as merged or 999 days old;
- selects any merged branch older than seven days, task-pattern branch older
  than 30 days, or any branch older than 90 days;
- does not inspect attached worktrees, upstream ownership, PR state,
  patch-equivalence, retained evidence, or exact user approval;
- exposes `--delete` and calls `git push origin --delete`;
- prints a total “cleaned up” count even when individual deletions fail.

That behavior conflicts with the canonical inspection-only script boundary and
with the proven squash/recovery incidents. The automation registry also leaves
this task's permission unspecified and describes candidates as already merged,
although the code admits unmerged old branches.

### G3-03 and G3-08 — there is no single trustworthy state kernel

In the linked GIT-001 worktree, `git rev-parse --git-dir` and
`git rev-parse --git-path MERGE_HEAD` resolved under the primary repository's
`worktrees/<lane>/` administration directory. Literal `.git/MERGE_HEAD` checks
therefore inspect a path below the worktree's `.git` *file*, not the real
operation marker. Both the required validator and unfinished-merge guard use
the literal form.

The validator also labels `HEAD..upstream` as local commits and
`upstream..HEAD` as remote commits, which reverses their meanings, and ends with
`Fix: Pull and resolve, or reset to remote`. `check_not_main.sh` suggests a
noncanonical `feat/` branch and only warns on detached HEAD. Session trust and
the canonical policy already require stricter fail-closed behavior.

### G3-04 — changed automation can pass without its outcome tests

The required PR workflow classifies `Python/**`, `fastapi_app/**`, and
`react_app/**`, while repository validation always runs. For script changes,
repository validation checks shell syntax, the static Codex workflow contract,
and migration-script tests. It does not run
`Python/tests/test_session_automation.py` or the broader prevention controls
that previously found task-brief, generator-help, source-binding, and trust
defects. The Python validation job is triggered by a test-file change but still
runs only a fixed contract/flexure/shear/detailing subset.

This explains how focused local evidence can be essential while required CI
does not independently repeat it.

### G3-05 and G3-12 — intake is useful but overstates classification

On the current research lane, task brief reported:

- branch `codex/git-governance-research` at `845c3fa9`;
- four dirty paths;
- base `51a8a57a` because that is the upstream head;
- upstream `origin/codex/git-governance-research`;
- all six sibling worktrees and their dirty counts.

It did not report that the lane was two commits ahead of its upstream, how it
related to current `origin/main`, whether refs were refreshed, or whether an
operation/lock/PR/check existed. Its sibling status calls use ordinary Git
status rather than `GIT_OPTIONAL_LOCKS=0`, despite Phase 1 evidence that status
may refresh an index unless optional locks are disabled.

### G3-06 — the incident-producing generator scope remains the default

The canonical `./run.sh generate indexes` help documents all-folder generation
only. The underlying generator accepts one folder and `--dry-run`, but that
safer scope is neither exposed nor explained through the preferred entrypoint.
Phase 1 and Spark sessions already proved that all-folder generation can rewrite
23-28 unrelated projections.

### G3-07 — static workflow validation misses semantic drift

The current static checker blocks reintroduced retired wrapper filenames in a
small list of live files. It does not reject these current examples:

- `.github/copilot-instructions.md` and terminal instructions prescribe
  unsupported `cleanup_stale_branches.py --dry-run`;
- `docs/contributing/git-workflow-testing.md` prescribes retired
  `validate_git_state.sh --fix`;
- `docs/contributing/background-agent-guide.md` permits direct commits to main;
- an agent guide chains historical `sync-main` and `cleanup-stale-branches`
  commands.

The checker passed during this audit, so its green result does not prove live
workflow guidance is coherent.

### G3-09 — required PR proof omits the strict documentation build

`PR Gate` correctly aggregates changed-component jobs and repository
validation. The strict MkDocs build is a different `Validate Documentation`
workflow, not a required ruleset context. Its concurrency key is the single
literal `deploy-docs`, with cancellation enabled, so a newer docs event can
cancel an older PR's build. The gap is exact-head proof, not a request for more
generic CI.

### G3-10 — merge-method choice remains unresolved

Phase 1 verifies that merge commit, squash, and rebase create different graph
identities. Phase 2 records repeated synchronization and cleanup work caused by
squash-equivalent branches. The live repository allows all three methods, while
current policy does not map them to lane type. Phase 4 must make that decision;
Phase 3 does not assume squash or merge is universally correct.

### G3-11 — task retention is not Git retention

Phase 1 could not locate a public Codex contract for snapshot-to-commit,
managed-worktree archive cleanup, or task-to-task Git handoff. The project has
strong prose logs, but no single machine-readable receipt binding a handoff to
the exact lane identities and hold state. A project receipt can close the local
evidence gap without claiming anything about Codex product internals.

### G3-13 — quick validation mixes local safety and optional diagnostics

The current validator completed in 4.05 seconds on a clean linked worktree. It
included a live remote probe and recursive search for files over 10 MB. Those
checks may be useful elsewhere, but neither is required to identify branch,
index, working-tree, operation, or local divergence state before a commit.

## Existing controls that pass the comparison

The gap matrix does not discard controls that already change outcomes:

- the canonical workflow forbids automatic Git recovery and history rewriting;
- task brief is read-only and exposes sibling dirty lanes;
- session trust now fails closed for dirty, detached, unknown, or Git-error state;
- `python_runtime.sh --diagnose` proves worktree source identity;
- PR concurrency cancels superseded runs for the same PR;
- `PR Gate` aggregates applicable component jobs and rejects unexpected skips;
- the ruleset requires a strict current-base status context and blocks deletion
  and non-fast-forward updates unless bypassed;
- scheduled CI owns performance and full artifact/dependency/Docker evidence;
- recent PR and documentation runs are mostly green and complete in roughly one
  minute, so Phase 4 should preserve the current fast path.

## Phase 4 routing

The smallest coherent design is four ordered control planes:

1. **State and intake:** G3-03, G3-05, G3-08, G3-12, G3-13.
2. **Publication and server enforcement:** G3-01, G3-04, G3-09, G3-10.
3. **Generated/shared data and cleanup:** G3-02, G3-06.
4. **Guidance and handoff coherence:** G3-07, G3-11.

Phase 4 must define the state machine, ownership, permissions, receipts,
failure messages, and measurable acceptance scenarios for each plane. The first
candidate implementation packet should be the read-only state/intake kernel,
because every later publication, cleanup, and recovery decision depends on its
truthfulness. That is a design ordering, not implementation authorization.

## Phase 3 acceptance gate

- Every retained gap is tied to an incident or a live policy/settings/code
  mismatch that changes the main-process outcome.
- Current strengths are preserved explicitly.
- GitHub settings, local scripts, CI path selection, instructions, and observed
  timing were inspected rather than inferred.
- Gaps are grouped into four bounded control planes with one named first design
  target.
- No policy, setting, script, branch, cleanup, PR, release, or runtime behavior
  changed.

Phase 3 is complete. Phase 4 may design the operating model and implementation
packets; Phase 6 owner review and Phase 7 packet authorization remain required.
