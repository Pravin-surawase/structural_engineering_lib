---
owner: Main Agent
status: active
last_updated: 2026-08-10
doc_type: spec
---

# Parallel Task Policy

This policy allows independent Codex tasks to run at the same time without
sharing a checkout, branch, path owner, or integration decision.

Git worktrees provide separate working files, `HEAD`, and index state while
sharing the repository's commits and refs. Codex Desktop supports one managed
worktree per task for this exact parallel-work use case. A worktree prevents
checkout collisions; the ownership and integration rules below prevent logical
merge collisions.

Official references:

- [Codex worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [Git worktree documentation](https://git-scm.com/docs/git-worktree.html)

## Concurrency limit

- Default to one write task when work overlaps or has an uncertain boundary.
- Allow at most **two independent implementation tasks** at once, plus one
  coordinator/integration lane. This preserves the repository's WIP limit of
  two while still allowing useful parallel work.
- Read-only audits do not consume an implementation slot when they create no
  repository or external-state changes.
- More than two write tasks require an explicit owner decision and a revised
  integration plan.

## Required lane contract

Every write task must have all of the following before editing:

| Field | Required value |
|---|---|
| Task | One concrete objective with explicit non-goals |
| Base | Exact commit or named branch selected before the worktree is created |
| Worktree | One Codex-managed or permanent worktree dedicated to the task |
| Branch | One unique `codex/<task-slug>` branch owned by that worktree |
| Paths | Exact owned files or disjoint directory scopes |
| Shared surfaces | Named integration owner for any required shared file |
| Acceptance | Narrow tests plus the closeout gate |
| Integration | Dependency order and the person/task that resolves conflicts |

No two active write tasks may use the same checkout, branch, or owned path. Git
itself refuses to check out one branch in two worktrees; never override that
safeguard with `--force`.

## Starting a future task in Codex Desktop

1. Start the task with **Worktree**, not Local, when another write task is
   active in the same repository.
2. Base independent work on the latest verified `origin/main`. Base dependent
   work on the exact reviewed feature commit it needs.
3. Run the lane-safe intake once:

   ```bash
   ./run.sh task brief "concrete task description"
   ```

4. Inspect every listed worktree and dirty-state warning. Do not switch, stash,
   reset, clean, or repair another lane.
5. Create the task's unique branch in its worktree, then record the required
   lane contract before editing.
6. Run `./run.sh session brief --agent <role>` and `./run.sh session start`.

Use Local as the foreground/integration lane whenever practical. Use Handoff
when a task must move between Local and its Codex-managed worktree; do not try
to check out the same branch in both places.

## Path ownership and shared surfaces

Independent paths are the safest parallel unit. If two tasks need the same
file, they are not independent and must be serialized or assigned to one owner.

Treat these as collision-prone shared surfaces:

- `AGENTS.md`, `.github/instructions/**`, and cross-agent policy;
- `docs/TASKS.md` and `docs/planning/next-session-brief.md`;
- `docs/SESSION_LOG.md`;
- package and dependency lock files;
- generated indexes, API manifests, and OpenAPI baselines;
- application routes, shared registries, and public export surfaces.

Only the integration owner updates the task board, next-session handoff, shared
policy, and final generated artifacts for a multi-lane packet. Each independent
parent task records its required issue/root-cause entry on its own branch; the
integration owner reconciles append-only `SESSION_LOG.md` entries in dependency
order. Subagents return those fields to their parent rather than editing the log.

## Runtime and process isolation

- Prefer `./run.sh` in every worktree.
- For a direct Python script in a linked worktree, use
  `./scripts/python_runtime.sh scripts/<script>.py`. Do not assume a local
  `.venv/bin/python` exists; the resolver binds the shared interpreter to the
  invoking worktree's `Python/` source.
- Install or build frontend dependencies inside the owning worktree only.
- Run only one default-port development stack at a time. Multiple live stacks
  are allowed only when the commands expose verified, distinct port settings.
- A task stops only the processes it started. Never use a broad process kill to
  clear another lane.

## Integration order

1. Freeze the completed lane and inspect its exact commit, diff, tests, and
   clean status.
2. Integrate dependency-first, one lane at a time, through the normal reviewed
   Git/PR workflow.
3. Recheck the target base before each integration. If the head, base, or
   shared-file ownership changed, stop and revise the plan.
4. Resolve shared generated files in the integration lane after the functional
   commits are combined; do not let multiple workers regenerate them in
   parallel.
5. Run focused checks after each integration and the full gate once at final
   closeout.

Do not rebase, reset, stash, clean, amend, or cherry-pick another lane without
first inspecting its owner, status, expected head, and uncommitted state.

## Cleanup and retention

A worktree is not clutter merely because it is old. Classify it first:

- **Active:** task is running or has uncommitted work; preserve it.
- **Handoff-ready:** clean unique commit exists but is not integrated; preserve
  it and report the exact branch/commit.
- **Integrated:** patch is already on the target branch; eligible for removal
  after owner confirmation.
- **Abandoned:** requires an explicit owner decision before removal.

Safe read-only maintenance commands:

```bash
git worktree list --porcelain
git worktree prune --dry-run --verbose
./scripts/python_runtime.sh scripts/cleanup_stale_branches.py
```

Remove a worktree only after verifying it is clean and its required commit is
recoverable. Deleting local or remote branches still requires explicit user
approval.

## Definition of parallel-safe completion

A lane is complete only when its owned outcome is implemented, narrow tests and
the required gate pass, material issues and root causes are recorded, the diff
contains no foreign paths, the branch/commit is recoverable, and the integration
owner knows whether the lane is pending, integrated, or held. Green checks do
not by themselves authorize a merge, release, or engineering-use claim.
