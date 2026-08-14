# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-14
- Focus: GIT-7B merged; GIT-7C1 required CI topology locally complete and authorized for draft validation
<!-- HANDOFF:END -->

**Current release:** `v0.23.1a1` Alpha

**Integrated GIT-7B receipt:** PR #744 merged as `0fdb48ed`; refresh `main` before work

**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Current** | GIT-7C1 locally complete | Required control-plane/docs routes, fail-closed PR Gate aggregation, scoped cancellation, and 173 control-plane tests pass |
| **Next** | Draft PR exact-head validation | Require Control Plane, Documentation, Repository, and aggregate PR Gate outcomes at the unchanged head |
| **Held** | GIT-7C2 server settings | No ruleset, bypass, merge-method, or branch-deletion change without a fresh exact-delta owner decision after GIT-7C1 is green on `main` |
| **Parallel owner decision** | Excel planning lane | Confirm a named active owner/next action or approve retirement |
| **Approval-gated** | Alpha worktrees and merged branches | Exact evidence is ready; deletion still requires explicit target approval |
| **Separate maintenance** | Seven dependency PRs | Replace one-by-one merging with four current-base compatibility packets |

## Required Reading

1. [Reconciled future-work and disposition plan](../research/git-governance/GIT-001-next-agent-disposition-plan.md)
2. [GIT-001 research index](../research/git-governance/GIT-001-README.md)
3. [Official evidence register](../research/git-governance/GIT-001-official-evidence-register.md)
4. [Lifecycle research](../research/git-governance/GIT-001-lifecycle-research.md)
5. [Phase 2 incident register](../research/git-governance/GIT-001-phase-2-incident-register.md)
6. [Phase 3 gap/risk matrix](../research/git-governance/GIT-001-phase-3-gap-risk-matrix.md)
7. [Phase 4 operating-model proposal](../research/git-governance/GIT-001-phase-4-operating-model.md)
8. [Phase 5 scenario validation](../research/git-governance/GIT-001-phase-5-scenario-validation.md)
9. [Phase 6 canonical-policy proposal](../research/git-governance/GIT-001-phase-6-canonical-policy-proposal.md)
10. [Phase 7B implementation receipt](../research/git-governance/GIT-001-phase-7B-state-intake-kernel.md)
11. [Phase 7C1 required CI topology](../research/git-governance/GIT-001-phase-7C1-required-ci-topology.md)
12. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
13. [AI token-efficiency policy](../guidelines/ai-token-efficiency.md)

## Start command

```bash
./run.sh task brief "validate GIT-7C1 required CI topology at the exact draft PR head"
./run.sh session brief --agent ops
./run.sh session start
```

Then refresh and inspect the branch, upstream, worktree, diff, current PR, and
all linked worktrees before mutation. The dated handoff is evidence, not a
replacement for live inspection.

## Current Git facts

- The dedicated GIT-001 branch was synchronized without history rewriting at
  `54a03557`; its tree exactly matched `origin/main = 69d9f68c`, its quick gate
  passed 10/10, and the merge was fast-forward pushed to its existing remote.
- Phase 1 covers the required Git, GitHub, release/dependency/contributor, and
  Codex lifecycle facts. Product guarantees for task snapshots, managed-
  worktree cleanup, and task-to-task Git handoff remain explicitly unresolved.
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

## Phase 1 through Phase 3 result

The evidence register dispositions are complete and the factual lifecycle map
covers normal, parallel, integration, release, cleanup, and recovery paths.
Two independent read-only reviews passed after local claims were explicitly
labeled and bound to dated observation evidence. Phase 1 changed no canonical
policy, GitHub setting, hook, cleanup behavior, or release state. Phase 2 now
adds ten evidence-backed incident families with main-process impact, confirmed
or explicit unconfirmed root causes, unsafe reactions, recovery, and proof.
Phase 3 adds thirteen outcome-changing gaps. Phase 4 maps them into
state/intake, publication/server enforcement, generated-data/cleanup, and
guidance/handoff control planes, with the read-only state kernel first. Phase 5
reproduces the current abnormal-state defects and defines falsifiable packet
gates. The owner accepted Phase 6 and authorized GIT-7B on 2026-08-13. The
read-only kernel integrated through PR #744 as `0fdb48ed`. On 2026-08-14 the
owner authorized publication of the planned GIT-7C1 workflow packet as a draft
PR. Required control-plane and strict-documentation routes, fail-closed
aggregation, and scoped cancellation are implemented locally. GIT-7C2 GitHub
settings and GIT-7D–7E remain held; no cleanup, deletion, recovery, or release
mutation is authorized.

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
