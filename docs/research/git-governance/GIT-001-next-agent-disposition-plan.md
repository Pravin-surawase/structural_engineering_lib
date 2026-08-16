---
owner: Main Agent
status: active
last_updated: 2026-08-15
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

- Original plan inspection date: `2026-08-12`; current disposition claims are
  superseded by the 2026-08-15 Phase 7D cleanup reconciliation.
- Refreshed 2026-08-15 integration anchor: `origin/main = bf4065f0`; the clean
  primary `main` worktree remains intentionally four commits behind at
  `0fdb48ed`.
- The current worktree inventory includes preserved dirty detached evidence;
  never reuse the older “all linked worktrees clean” observation as live proof.
- Ahead/behind counts below are commit-graph facts only. Squash integration is
  checked separately with patch equivalence, PR receipts, and main reachability.
- Older “ready to retire” wording in this plan is not a current classifier
  result. The current gate is complete identity-bound evidence followed by
  `RETIREMENT_READY_PENDING_APPROVAL` and separate exact-target approval.
- Planning refresh on 2026-08-16: `origin/main = f56e1ec3`; the primary is now
  nine commits behind with only `.codex/config.toml` dirty; GIT-7E PR #751 and
  compact orchestration PR #752 are merged. The dated topology tables below
  remain historical evidence until Phase 8 refreshes them read-only.
- Phase 8 refresh on 2026-08-16: fetched `origin/main = 86f92ed1`, tree
  `1bb7e448`; primary is clean/equal, retained detached `e54a` still has only
  its 119-insertion/7-deletion session-log patch, and the one fresh Excel
  classifier result is `HOLD_UNKNOWN_OWNER`. The complete current snapshot is
  [the Phase 8 closeout](GIT-001-phase-8-adoption-closeout.md); every older
  topology table remains historical rather than mutation authority.

## Outcome first: the revised order

The old list mixed completed recovery with future work. The current order is:

1. **GIT-001 Phase 8 closes on merge of its unchanged packet.** Phases 1-7E
   remain integrated; adoption, stale status, transition-receipt semantics,
   and preservation holds are reconciled without mutating retained lanes.
2. **Decide Excel planning ownership.** It has no unique commits and no PR, so
   one owner decision determines whether it remains active or may enter a
   separately evidenced retirement assessment.
3. **Preserve the three attached Alpha worktrees pending a complete refreshed
   disposition and exact approval.** Treat the dual-head Alpha policy lane
   separately; no current deletion-ready claim is made.
4. **Keep eight unattached merged branches as future disposition candidates.**
   Their merge/reachability facts are refreshed, but owner, dependent-PR,
   retention, classifier, and exact-approval gates remain incomplete.
5. **Handle the seven remaining dependency PRs as five compatibility groups.** Do
   not merge old, behind Dependabot branches one by one.

Column PMM preservation/recovery and the useful portion of PR #723 are complete.
They stay in the completed ledger below so a future agent does not repeat them.

## What changed from the original priorities

| Original priority | Current result | Updated disposition |
|---|---|---|
| 1 — protect unique PMM work | Complete and superseded by safe integration | Keep remote forensic refs; no Git recovery action remains |
| 2 — complete Phase 1 and study PR #723 | Complete; lifecycle research and selective recovery are integrated | Preserve the diverged research lane; do not synchronize or rewrite it |
| 3 — decide Excel ownership | Still open | Ask for a named owner/next action before any retirement assessment |
| 4 — retire merged Alpha worktrees | Historical integration evidence exists; all remain attached and the policy lane is dual-head | Preserve; rerun complete disposition before requesting any exact action |
| 5 — branch cleanup packet for seven branches | Count changed from seven to eight | Keep as future candidates until the classifier receives complete evidence and returns pending approval |
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
| Primary / `main` | `0fdb48ed` | Clean; four commits behind refreshed `origin/main = bf4065f0` | Preserve integration anchor; no synchronization in this packet |
| GIT-001 / `codex/git-governance-research` | `65703736` | Local differs from remote `51a8a57a`; three locally unique patches | Preserve diverged evidence unchanged |
| Excel / `codex/excel-product-planning` | `a0e115e1` | 67 behind; no feature remote or PR | Attached; ownership decision required |
| Alpha closeout / `codex/alpha-0231-release-closeout` | `127afb64` | Matching remote; ancestor of main | Attached hold; complete evidence and approval required |
| Alpha integration / `codex/alpha-0231-integration` | `e3b9a6cb` | Matching remote; ancestor of main | Attached hold; complete evidence and approval required |
| Alpha policy / `codex/release-preflight-alpha-policy` | `5da9c66a` | Local differs from remote `20180a40`; both integrated | Preserve attached dual-head evidence separately |

The GIT-001 branch looks “ahead” only because its research commit was
squash-merged. `git cherry origin/main codex/git-governance-research` reports
`- 3be4790d`, which means an equivalent patch already exists on `main`. This is
why ahead/behind alone cannot decide integration or cleanup.

## Priority 1 — preserve completed GIT-001 evidence and start fresh

### Current state

GIT-001 Phases 1-7D are complete through the integrated research, state,
enforcement, generator, classifier, and reconciliation receipts. The local
`codex/git-governance-research` head is now `65703736`, differs from remote
`51a8a57a`, and has three locally unique patches relative to refreshed `main`.
That exact lane is historical evidence, not the next write lane.

### Required continuation rule

1. Preserve the existing research branch/worktree and remote ref unchanged.
2. Refresh and verify `origin/main` in an existing checkout.
3. Create a fresh `codex/<task-slug>` worktree from the verified current main.
4. Recover only explicitly scoped current-compatible facts when needed; do not
   extend, merge into, reset, rebase, or reconcile the preserved research lane.
5. Keep GIT-7E limited to semantic live-guidance and durable read-only handoff
   acceptance. Cleanup/deletion remains a separate exact-target workflow.

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

## Priority 3 — preserve and reassess merged Alpha worktrees

### Historical integration evidence and current hold

All three Alpha worktrees were clean when refreshed and their meaningful heads
retain PR/main-reachability evidence. They remain attached, so none is a branch-
deletion candidate. Disk size is context only and cannot change disposition.

| Worktree | Local head | Remote/PR evidence | Main evidence | Approx. size |
|---|---:|---|---|---:|
| Alpha closeout | `127afb64` | Matching remote; PR #733 merged | Head is ancestor of `origin/main` | 508 MB |
| Alpha integration | `e3b9a6cb` | Matching remote; PR #730 merged | Head is ancestor of `origin/main` | 65 MB |
| Alpha policy | `5da9c66a` | Remote/PR #731 head is `20180a40`; local is one commit ahead of that remote | Both `20180a40` and local `5da9c66a` are ancestors of `origin/main` | 78 MB |

The Alpha policy explanation is resolved: `5da9c66a` is unpublished relative
to its own remote branch, but it is not lost or unintegrated because that exact
commit is reachable from current `main`. Record both heads; do not “fix” the
old remote by rewriting it.

### Prerequisites before any future execution proposal

Before asking the owner about any exact path:

1. Refresh and repeat the clean/head/attachment/reachability checks.
2. Supply exact owner, remote-ref, PR/dependency, retention, and freshness
   evidence to the inspection-only classifier.
3. Require `RETIREMENT_READY_PENDING_APPROVAL`; every other result remains a
   hold.
4. Keep Alpha policy separate and retain both local and remote heads.
5. Obtain separate exact approval for worktree, local branch, and remote branch
   actions. No approval is granted by this plan.

Use Git's worktree removal for the validated exact worktree, not a recursive
filesystem deletion. Do not prune first, because pruning is not a substitute
for proving or removing the actual worktree.

## Priority 4 — future branch-disposition packet

### Updated candidate count

The original count of seven is obsolete. Eight unattached local branches were
refreshed on 2026-08-15 as exact ancestors of `origin/main`, with matching
remote heads and merged PR receipts. Those facts make them future disposition
candidates, not deletion-ready targets:

| Local branch | Head | Merged PR | Local decision | Remote decision |
|---|---:|---:|---|---|
| `codex/alpha-0231-candidate-evidence` | `adb161b8` | #732 | Hold: retention unknown | Hold: retention unknown |
| `codex/ci-fastapi-load-lane-fix` | `21b9df1f` | #729 | Hold: retention unknown | Hold: retention unknown |
| `codex/column-rectangular-e2e` | `007dfa0c` | #725 | Hold: retention unknown | Hold: retention unknown |
| `codex/footing-isolated-v1` | `886871ae` | #727 | Hold: retention unknown | Hold: retention unknown |
| `codex/gpt-5-3-spark-work-program` | `6cd22dcb` | #734 | Hold: retention unknown | Hold: retention unknown |
| `codex/is456-beam-primary-route` | `aa4fe606` | #726 | Hold: retention unknown | Hold: retention unknown |
| `codex/is456-slabs-closeout` | `d79a1558` | #724 | Hold: retention unknown | Hold: retention unknown |
| `codex/is456-slabs-plan` | `7e623984` | #728 | Hold: retention unknown | Hold: retention unknown |

The 2026-08-15 exact proposal refreshed every row for worktree attachment,
local/remote head identity, main reachability, PR state/dependencies, owner,
retention, and new activity, then ran the maintained classifier. Every row
returned `HOLD_UNKNOWN_OWNER` / `RETENTION_EVIDENCE_UNKNOWN`: proposal authority
did not establish that a historical tip was unneeded. Before any new approval
request, obtain an authoritative exact-SHA retention decision and rerun fresh.
A branch becoming attached, advancing, diverging, gaining an open/dependent PR,
or carrying a retention hold remains outside any action batch.

### Why the cleanup script did not list them

The historical `cleanup_stale_branches.py` result is superseded. The maintained
`classify_branch_disposition.py` performs local inspection only and preserves
`NOT_CHECKED`/missing supplied evidence as `UNKNOWN`. The explicit table above
is an audit queue, not authorization and not a substitute for its complete
identity-bound receipt.

### Approval and execution rules

- Ask separately for local deletion and remote deletion; one does not imply the
  other.
- Delete only the exact approved rows and only after a same-session refresh.
- Local deletion follows worktree-detachment proof.
- No repository cleanup workflow performs deletion. After a pending-approval
  receipt and explicit exact authorization, Codex performs only the approved
  native Git action and records it.
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
2. Run `./run.sh session brief --agent ops`, `./run.sh session start`, and the
   worktree-bound runtime/state diagnostics.
3. Refresh refs, inspect all worktrees read-only, and compare the result with
   this dated snapshot. Record drift; do not normalize it away.
4. For GIT-001 Phase 8, create exactly one fresh current-main write lane; do
   not reuse the preserved GIT research or completed GIT-7E lane.
5. Keep Phase 8 to adoption evidence, status reconciliation, and refreshed
   preservation holds. It does not authorize cleanup.
6. Ask the owner the single Excel ownership question when disposition work is
   separately resumed:
   “Is the Excel planning task still active with a named next action?”
7. Do not delete Alpha lanes or branches until a complete pending-approval
   receipt and separate exact-target approval exist.
8. At handoff, record issues, confirmed root causes, solutions, and command/test
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
| `scripts/classify_branch_disposition.py` | Inspection-only local/worktree, reachability, patch/tree, and caller-supplied remote/PR evidence receipt | Remote freshness when `NOT_CHECKED`, deletion authority, or post-action proof |
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

## Phase 8 closeout and reactivation

Phase 8 is fulfilled when its unchanged adoption packet merges with focused,
hosted, and exact-tree closeout evidence. Unknown retained topology is a safe
closeout state, not an instruction to keep GIT-001 active indefinitely.

Future disposition work reactivates only after new authority or evidence:

- Excel needs a named owner/next action and exact retention decision;
- Alpha and the historical branch table need fresh classifier inputs plus
  separate exact-target approval before any action;
- dependency groups remain separate compatibility packets after INDIA-2;
- completed PMM and PR #723 recovery stays closed absent new evidence; and
- no hold, candidate, or merged PR authorizes cleanup by itself.
