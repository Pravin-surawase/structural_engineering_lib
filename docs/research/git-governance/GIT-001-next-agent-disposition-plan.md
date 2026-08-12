---
owner: Main Agent
status: active
last_updated: 2026-08-12
doc_type: reference
task: GIT-001
---

# GIT-001 — Reconciled Future-Work and Disposition Plan

## Purpose

This packet converts the original six-priority cleanup and recovery list into a
current, evidence-backed handoff. It tells the next agent what is already done,
what remains, why the order changed, which actions need owner approval, and what
evidence must exist before any destructive Git operation.

This is a planning and forensic record, not new Git policy. The canonical
workflow remains
[`git-workflow-single-source.md`](../../git-automation/git-workflow-single-source.md).

## Snapshot and reading rule

- Live refresh and inspection date: `2026-08-12`.
- Refreshed integration anchor: `main = origin/main = 951f5e1d`.
- The primary worktree was clean when inspected.
- All five linked worktrees were clean when inspected.
- Ahead/behind counts below are commit-graph facts only. Squash integration is
  checked separately with patch equivalence, PR receipts, and main reachability.
- “Ready to retire” means the evidence packet is complete enough to request the
  owner's destructive-action approval. It does not itself authorize removal.

## Outcome first: the revised order

The old list mixed completed recovery with future work. The current order is:

1. **Synchronize and continue GIT-001 Phase 1 research.** The active research
   lane is clean but behind current `main`; bring current receipts into view,
   finish official-source coverage, then write the factual lifecycle map.
2. **Decide Excel planning ownership.** It has no unique commits and no PR, so
   one owner decision determines whether it remains active or becomes a safe
   retirement candidate.
3. **Retire the three merged Alpha worktrees after explicit approval.** Their
   exact heads are preserved and reachable; this is the largest immediate disk
   recovery, roughly 650 MB.
4. **Prepare and execute a separately approved branch-cleanup packet.** The old
   count of seven is stale; eight unattached merged local branches are now
   verified candidates. Local and remote deletion are separate decisions.
5. **Handle the seven remaining dependency PRs as four coordinated tasks.** Do
   not merge old, behind Dependabot branches one by one.

Column PMM preservation/recovery and the useful portion of PR #723 are complete.
They stay in the completed ledger below so a future agent does not repeat them.

## What changed from the original priorities

| Original priority | Current result | Updated disposition |
|---|---|---|
| 1 — protect unique PMM work | Complete and superseded by safe integration | Keep remote forensic refs; no Git recovery action remains |
| 2 — complete Phase 1 and study PR #723 | PR #723 study/recovery complete; Phase 1 incomplete | Continue only the remaining official research and lifecycle map |
| 3 — decide Excel ownership | Still open | Make this the first ownership decision after research-lane synchronization |
| 4 — retire merged Alpha worktrees | Evidence now complete; no deletion performed | Request exact approval, then retire in a controlled sequence |
| 5 — branch cleanup packet for seven branches | Count changed from seven to eight | Publish the refreshed table and obtain separate local/remote approval |
| 6 — dependency maintenance | Still open; all seven PRs are behind `main` | Replace one-by-one merging with four tested compatibility packets |

## Completed ledger — do not repeat

### A. Column PMM preservation and recovery

The historical branch `codex/column-pmm-experimental` was published unchanged
at `8a52ed0f` before integration work. Its single large stale-base commit was not
blindly merged or cherry-picked. The engineering surface was selectively
recovered on current code, checked against an independent closed-form oblique
benchmark, reviewed, and integrated through:

- feature PR #738, reviewed head `a481d1ab`, squash merge `402bf22c`;
- closeout PR #739, reviewed head `04f789de`, squash merge `d106ff59`;
- Git-learning closeout PR #740, now included in `main` at `951f5e1d`.

The old PMM local worktree and local branch were removed only after exact merge
and integrated-main receipts. The remote historical and recovery refs remain
available as forensic evidence. PMM is still experimental and not part of the
stable root, services, FastAPI, or React contract. Promoting it is a separate
engineering decision, not unfinished Git recovery.

**Lesson:** publish irreplaceable history first; then recover the intended
outcome onto a fresh base and prove it independently. A clean old branch is not
automatically safe to merge, and a merged replacement does not make the
historical evidence useless.

### B. PR #723 selective workflow recovery

PR #723 (`codex/parallel-task-policy`, head `75d66681`) was closed without merge.
It was used as incident and design evidence, not as a conflict-resolution task.
The useful current-compatible behavior was selectively reimplemented:

- `./run.sh task brief <description>` for read-only lane intake;
- worktree-bound Python runtime use during index generation;
- a read-only `generate indexes --help` path.

These changes merged through PR #736 at reviewed head `aec9fbb2` and merge
`30ec598d`; PR #737 added the closeout record at merge `b069428b`. Broad parallel
policy text, unrelated generated surfaces, registry churn, and stale session
automation were deliberately not copied.

**Lesson:** a conflicted PR can still be valuable as a requirements source.
Recover the behavior that remains correct; do not use conflict resolution to
silently import obsolete architecture.

## Current worktree topology

| Worktree / branch | Head | Relation to current `main` | Disposition |
|---|---:|---|---|
| Primary / `main` | `951f5e1d` | Exact `origin/main` | Clean integration anchor |
| GIT-001 / `codex/git-governance-research` | `3be4790d` | 1 commit ahead, 6 behind by ancestry; patch already squash-integrated | Active; synchronize before continuing |
| Excel / `codex/excel-product-planning` | `a0e115e1` | 0 ahead, 59 behind; head is ancestor of main | Ownership decision required |
| Alpha closeout / `codex/alpha-0231-release-closeout` | `127afb64` | 0 ahead, 12 behind; ancestor of main | Retirement-ready after approval |
| Alpha integration / `codex/alpha-0231-integration` | `e3b9a6cb` | 0 ahead, 30 behind; ancestor of main | Retirement-ready after approval |
| Alpha policy / `codex/release-preflight-alpha-policy` | `5da9c66a` | Local head is ancestor of main | Retirement-ready after dual-head receipt |

The GIT-001 branch looks “ahead” only because its research commit was
squash-merged. `git cherry origin/main codex/git-governance-research` reports
`- 3be4790d`, which means an equivalent patch already exists on `main`. This is
why ahead/behind alone cannot decide integration or cleanup.

## Priority 1 — synchronize and complete GIT-001 Phase 1

### Why this is first

GIT-001 is the active governance program. Its research lane predates the PMM
and PR #723 closeouts, so continuing without synchronization would cause the
agent to repeat old facts or contradict current receipts. The lane is clean,
published, and shared; preserving its history is preferable to silently
replacing it.

### Recommended lane action

1. Refresh `origin` and prove the GIT-001 worktree is clean, attached to
   `codex/git-governance-research`, and exactly at its upstream head.
2. Verify again that `3be4790d` is patch-equivalent to work already on `main`.
3. Merge refreshed `origin/main` into the research branch. Do not rebase or
   force-push the shared research branch.
4. If the merge conflicts, stop and classify each conflict against the current
   Phase 7A and PMM receipts. Do not choose “ours” or “theirs” across the tree.
5. Run the documentation and quick gates, commit only deliberate reconciliation
   edits if required, and push without history rewriting.

If the existing lane has become unavailable or externally owned, create a
fresh `codex/git-governance-phase1-continuation` worktree from current `main`
and record the old branch as predecessor. Do not have two writers in the same
research directory.

### Research scope after synchronization

Complete the open coverage listed in
[`GIT-001-official-evidence-register.md`](GIT-001-official-evidence-register.md):

- commits, branches, upstreams, fetch, pull, and push;
- merge, rebase, cherry-pick, revert, reset, restore, stash, and clean;
- hooks, configuration scope, pruning, garbage collection, and worktree repair;
- tags, signatures, release ancestry, submodules, shallow and partial clones;
- GitHub merge methods, merge queue/auto-merge, rulesets and branch protection,
  environments, releases, Dependabot, forks, and external contributors;
- verified Codex task/worktree lifecycle, archival, snapshot, and handoff facts.

Then write one source-backed factual map for normal work, parallel work,
integration, release, cleanup, and recovery. Label every statement as external
fact, project observation, unresolved choice, or not applicable.

### Non-goals

- Do not change canonical Git policy, GitHub settings, hooks, or cleanup rules.
- Do not delete historical branches or worktrees during research.
- Do not advance to Phase 2 merely because a source list is long; each open
  area must be covered, declared not applicable, or explicitly unresolved.
- Treat PR #723 and the PMM incident as Phase 2 inputs, not as permission to
  rewrite policy during Phase 1.

### Acceptance evidence

- Research worktree clean and current with its remote before mutation.
- Current `origin/main` integrated without history rewriting.
- Evidence register has no silent coverage gaps.
- Factual lifecycle map exists and separates facts from decisions.
- Phase 1 coverage review explicitly passes before Phase 2 begins.

## Priority 2 — decide Excel planning ownership

### Live finding

`codex/excel-product-planning` is clean at `a0e115e1`, has no branch-only commit,
is 59 commits behind current `main`, has no matching remote branch, and has no
PR. It is configured against `origin/main`, which does not make it a published
feature branch. Git evidence says there is no unique committed work at its tip;
Git cannot tell whether an external planning task still intends to use the
folder.

### Decision routes

**If the planning task remains active:**

1. Name the current owner and expected next action.
2. Prefer a fresh current-main worktree if new implementation is about to
   begin; the old lane provides no unique commit to preserve.
3. If the old branch is deliberately retained, give it a matching dedicated
   remote upstream only when there is real branch-owned work to publish.
4. Record an expiry or review date so “active” does not mean indefinite.

**If the planning task is inactive:**

1. Recheck clean state, branch attachment, `0` branch-only commits, absence of
   an open PR, and absence of a remote feature branch.
2. Ask the owner for explicit approval to remove the worktree and local branch.
3. Remove the worktree first; delete the local branch only after Git no longer
   reports it as attached.
4. Verify the planning path is gone and the primary repository remains clean.

### Stop conditions

Stop if the worktree becomes dirty, an operation marker exists, a new remote or
PR appears, the task owner says it is active, or branch-only commits appear.
Never stash, reset, clean, or copy files out as an implicit retirement method.

## Priority 3 — retire merged Alpha worktrees after approval

### Why they are now retirement-ready

All three Alpha worktrees are clean. Their meaningful heads have exact PR and
main-reachability receipts. Together they occupy about 651 MB; approximately
418 MB is the old Alpha candidate's `react_app/node_modules`.

| Worktree | Local head | Remote/PR evidence | Main evidence | Approx. size |
|---|---:|---|---|---:|
| Alpha closeout | `127afb64` | Matching remote; PR #733 merged | Head is ancestor of `origin/main` | 508 MB |
| Alpha integration | `e3b9a6cb` | Matching remote; PR #730 merged | Head is ancestor of `origin/main` | 65 MB |
| Alpha policy | `5da9c66a` | Remote/PR #731 head is `20180a40`; local is one commit ahead of that remote | Both `20180a40` and local `5da9c66a` are ancestors of `origin/main` | 78 MB |

The Alpha policy explanation is resolved: `5da9c66a` is unpublished relative
to its own remote branch, but it is not lost or unintegrated because that exact
commit is reachable from current `main`. Record both heads; do not “fix” the
old remote by rewriting it.

### Approved execution sequence

After the owner explicitly approves these exact three paths:

1. Refresh and repeat the clean/head/attachment/reachability checks.
2. Retire Alpha closeout first because it reclaims the most space.
3. Retire Alpha integration second.
4. Retire Alpha policy last, preserving the dual-head receipt in the handoff.
5. For each lane, remove the worktree before deleting its local branch.
6. Verify the remaining worktree inventory and primary clean state after every
   removal. Stop on the first unexpected result.
7. Leave remote branches untouched until the separate branch-cleanup approval.

Use Git's worktree removal for the validated exact worktree, not a recursive
filesystem deletion. Do not prune first, because pruning is not a substitute
for proving or removing the actual worktree.

## Priority 4 — branch-cleanup approval packet

### Updated candidate count

The original count of seven is obsolete. Eight unattached local branches are
exact ancestors of current `origin/main`, have matching remote heads, and have
merged PR receipts:

| Local branch | Head | Merged PR | Local decision | Remote decision |
|---|---:|---:|---|---|
| `codex/alpha-0231-candidate-evidence` | `adb161b8` | #732 | Awaiting approval | Awaiting approval |
| `codex/ci-fastapi-load-lane-fix` | `21b9df1f` | #729 | Awaiting approval | Awaiting approval |
| `codex/column-rectangular-e2e` | `007dfa0c` | #725 | Awaiting approval | Awaiting approval |
| `codex/footing-isolated-v1` | `886871ae` | #727 | Awaiting approval | Awaiting approval |
| `codex/gpt-5-3-spark-work-program` | `6cd22dcb` | #734 | Awaiting approval | Awaiting approval |
| `codex/is456-beam-primary-route` | `aa4fe606` | #726 | Awaiting approval | Awaiting approval |
| `codex/is456-slabs-closeout` | `d79a1558` | #724 | Awaiting approval | Awaiting approval |
| `codex/is456-slabs-plan` | `7e623984` | #728 | Awaiting approval | Awaiting approval |

Before seeking approval, refresh every row for worktree attachment, local/remote
head identity, main reachability, PR state, and new activity. A branch becoming
attached, advancing, diverging, or gaining an open PR removes it from the batch.

### Why the cleanup script did not list them

The dry-run `cleanup_stale_branches.py` reported no stale branches because its
current selection is age-oriented and remote-oriented with a minimum-age rule.
That output does not prove that recently merged, unattached local branches do
not exist. For this packet, the authoritative evidence is the explicit
worktree/ref/reachability/PR table above.

### Approval and execution rules

- Ask separately for local deletion and remote deletion; one does not imply the
  other.
- Delete only the exact approved rows and only after a same-session refresh.
- Local deletion follows worktree-detachment proof.
- Remote deletion uses the maintained cleanup workflow and a reviewed dry run;
  do not issue an ad hoc remote-delete command.
- Preserve a receipt containing branch name, local head, remote head, PR,
  reachability result, approval scope, action result, and post-action inventory.
- Do not include GIT-001, Excel, Alpha attached branches, PMM forensic refs, or
  PR #723 evidence refs in this eight-branch batch.

## Priority 5 — coordinated dependency maintenance

### Current open set

All seven remaining Dependabot PRs are behind current `main`. Their older green
checks are not merge authority for today's base. Treat the PRs as update notices
and patch inputs, then construct fresh tested lanes from current `main`.

| Packet | Existing PRs | Decision and reason |
|---|---|---|
| Python typing major | #715 constraint `<3`; #717 mypy 2.3.0 | One coherent task: these overlap semantically and must not both merge independently |
| ESLint 10 toolchain | #713 ESLint 10; #683 `@eslint/js` 10 | One coordinated compatibility task with TypeScript-ESLint and React lint plugins |
| React build major | #684 Vite plugin React 6 | Hold until a compatible Vite/toolchain plan; its prior React Validation and PR Gate failed |
| Node type/runtime policy | #714 `@types/node` 26 | Hold while runtime pin is Node 24; decide runtime major before accepting type-major mismatch |
| Motion library major | #716 Framer Motion 13 | Independent frontend packet after current-main refresh and live motion verification |

### Required workflow for each packet

1. Create a dedicated branch and worktree from refreshed `main`.
2. State the compatibility hypothesis, affected lock/config files, and explicit
   non-goals before changing versions.
3. Apply one coherent dependency group, regenerate only its owned lockfiles,
   and inspect the actual transitive change.
4. Run targeted tests while iterating and the appropriate complete gate before
   publication. Frontend majors require lint, tests, TypeScript, production
   build, and a focused live user-path check. Mypy majors require current
   package typing and repository validation.
5. Publish a fresh PR or update only a still-correct candidate. Required checks
   must pass at the exact reviewed head on the current base.
6. Close or supersede old overlapping PRs only with explicit owner authority
   where closure is required.

Dependency work can run independently from the research program, but each
packet needs its own writer. Lockfiles, workflow files, generated indexes, and
session/task records are single-writer surfaces.

## Next-agent first-hour checklist

1. Read `AGENTS.md`, this packet, the GIT-001 index, evidence register, and
   lifecycle research.
2. Run `./run.sh task brief "continue GIT-001 Phase 1 official research"`.
3. Refresh refs, inspect all worktrees read-only, and compare the result with
   this dated snapshot. Record drift; do not normalize it away.
4. Take ownership of exactly one write lane. The preferred first lane is the
   existing GIT-001 research worktree after clean/upstream verification.
5. Synchronize the research lane with current `main` using a normal merge; stop
   and classify if conflicts appear.
6. Complete the official-source register and factual lifecycle map.
7. Ask the owner the single Excel ownership question while research proceeds:
   “Is the Excel planning task still active with a named next action?”
8. Do not delete Alpha lanes or branches until exact-target approval is given.
9. At handoff, record issues, confirmed root causes, solutions, and command/test
   evidence in the newest `docs/SESSION_LOG.md` entry.

## Maintained script guide

These repository scripts reduce repeated mistakes, but they do not replace Git
judgment or Codex's native branch/commit/PR lifecycle.

| Command | What it helps prove | What it does not prove |
|---|---|---|
| `./run.sh task brief "task"` | Read-only branch/head/dirty/base/upstream/worktree context, task route, and matching automation before work starts | That the suggested route owns the task, or that an old lane is safe to reuse/delete |
| `./run.sh session brief --agent ops` | Bounded role context, recent commits, task focus, and expected validation | Live remote freshness or merge readiness |
| `./run.sh session start` | Environment, clean-state trust, lane-bound runtime, and current session setup | Permission for destructive cleanup or publication |
| `./scripts/python_runtime.sh --diagnose` | Which Python is selected and whether imports resolve to the invoking worktree | That the code is correct or fully tested |
| `./run.sh check --quick` | Fast 10-check repository validation before commit | Full product, release, or exact-head GitHub CI acceptance |
| `./run.sh check` | Full local repository gate at closeout | GitHub ruleset state or unchanged-head remote checks after a push |
| `scripts/cleanup_stale_branches.py` | Maintained, dry-run-first remote stale-branch cleanup path | Recently merged local candidates outside its age/remote selection rules |
| `scripts/safe_file_delete.py` | Validated in-repository file deletion with reference checks | Git worktree or branch retirement; use Git's own worktree/ref operations |
| `./run.sh generate indexes --help` | Read-only usage information | Index freshness; actual generation is intentionally write-capable |
| `./run.sh generate indexes` | Regenerates maintained documentation indexes through the invoking lane's Python runtime | Authority to create new index topology or overwrite another lane's shared output |

Use `git status`, `git worktree list --porcelain`, `git for-each-ref`,
`git rev-list`, `git cherry`, exact object IDs, and PR metadata together for
disposition. No single script answers the ownership and recoverability question.

## Common mistakes this plan prevents

- **Mistaking clean for safe.** Clean says no visible file change; it says
  nothing about unpublished commits, wrong upstreams, or task ownership.
- **Mistaking ahead/behind for content identity.** Squash merges change the
  graph; use patch equivalence and PR receipts as well as reachability.
- **Treating an upstream as publication.** Excel tracks `origin/main`, not a
  matching feature ref. That configuration does not publish Excel work.
- **Fixing a historical remote unnecessarily.** Alpha policy's local extra
  commit is already on main; rewriting the remote would add risk without
  protecting work.
- **Using age as the only cleanup test.** A new merged branch may be safe to
  retire, while an old branch may contain irreplaceable work.
- **Merging stale dependency bots individually.** Major updates interact through
  runtimes, peer constraints, configs, and lockfiles; group by compatibility.
- **Editing shared surfaces from parallel lanes.** Generated indexes, task and
  session records, registries, routes, manifests, and lockfiles need one owner.

## Completion definition for this plan

This plan is fulfilled when:

- Phase 1 coverage and the factual lifecycle map pass review;
- Excel has a named active owner/next action or an approved retirement receipt;
- the three Alpha worktrees are either explicitly retained or safely retired
  under exact approval;
- the eight-branch table has an owner decision and any approved actions have
  post-action receipts;
- each dependency group is completed, held with a named reason, or deliberately
  superseded on a current base;
- completed PMM and PR #723 recovery is not reopened without new evidence.
