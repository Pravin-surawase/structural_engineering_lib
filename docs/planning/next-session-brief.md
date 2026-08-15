# Next Session Briefing

## Latest Handoff

<!-- HANDOFF:START -->
- Date: 2026-08-15
- Focus: GIT-7D complete and non-destructively reconciled; GIT-7E semantic guidance and durable handoff is next
<!-- HANDOFF:END -->

**Current release:** `v0.23.1a1` Alpha

**Refreshed GIT-7D anchor:** `origin/main = bf4065f071f1245461df6d3c42f1cc070efbae70`

**Task board:** [TASKS.md](../TASKS.md)

| State | Target | Decision |
|---|---|---|
| **Complete** | GIT-7B, GIT-7C, and GIT-7D | State kernel, exact-head CI/server enforcement, targeted generation, and inspection-only disposition are integrated |
| **Complete** | GIT-7D2 | PR #747 merged as `0a784de5`; closeout lessons PR #748 merged as `bf4065f0`; both reviewed/merge trees were equal |
| **Current** | Preservation/disposition audit | GIT-7D is reconciled without deletion or cleanup; every attached, dirty, diverged, dual-head, owner-unresolved, and incomplete-evidence lane remains held |
| **Next** | GIT-7E | Semantic live-guidance coherence and durable read-only task-to-Git handoff receipt only |
| **Owner decision** | Excel planning lane | Name an active owner/next action or separately authorize a complete retirement assessment |
| **Separate maintenance** | Seven dependency PRs | Do not close or merge the existing Dependabot PRs in GIT-001 |

## Required Reading

1. [Phase 7D cleanup reconciliation](../research/git-governance/GIT-001-phase-7D-cleanup-reconciliation.md)
2. [Machine-readable preservation receipt](../research/git-governance/GIT-001-phase-7D-cleanup-reconciliation.json)
3. [GIT-001 research and phase ledger](../research/git-governance/GIT-001-README.md)
4. [Phase 7D2 branch disposition](../research/git-governance/GIT-001-phase-7D2-branch-disposition.md)
5. [Reconciled future disposition plan](../research/git-governance/GIT-001-next-agent-disposition-plan.md)
6. [GIT-7D2 cleanup-audit case study](../git-automation/git-governance-case-study-git-7d2-cleanup-audit.md)
7. [Canonical Git workflow](../git-automation/git-workflow-single-source.md)
8. [Phase 5 GIT-7E acceptance](../research/git-governance/GIT-001-phase-5-scenario-validation.md)

## Start commands

```bash
./run.sh session brief --agent ops
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Refresh and verify `origin/main` before relying on this handoff. Create a fresh
`codex/<task-slug>` branch/worktree from verified current main for separately
authorized GIT-7E work. Do not extend, reset, rebase, merge into, or reconcile a
preserved squash-diverged lane.

## Verified current Git facts

- PRs #744-#748 are merged at their exact reviewed heads with successful
  `PR Gate`. Each reviewed-head tree equals its squash-result tree, and both
  `PR Validation` and `Validate Documentation` passed after every merge.
- GIT-7D1 is integrated through PR #746. GIT-7D2 is integrated through PRs
  #747-#748. The old deletion-oriented route is absent; the classifier remains
  local, inspection-only, fail-closed, and non-authorizing.
- The clean primary `main` worktree remains at `0fdb48ed`, four commits behind
  refreshed `origin/main = bf4065f0`. Synchronizing it was outside the packet.
- The delegated prior audit counted 18 local `codex/*` branches and 12
  worktrees. Live intake found 18 and 13 because the clean detached `b94c`
  desktop task worktree existed; the authorized reconciliation lane alone made
  the task totals 19 and 14.
- Active ruleset `11390214` still requires a PR and strict `PR Gate`, protects
  deletion/non-fast-forward, has no bypass actor, allows merge/squash, and
  excludes rebase. Repository branch deletion after merge remains disabled.
- The only pre-existing open PRs are Dependabot #683, #684, and #713-#717.
  There are no open issues. None was changed by the audit.

## Preservation and disposition holds

- Detached `e54a` at `0fdb48ed` still has exactly one dirty path,
  `docs/SESSION_LOG.md` (119 insertions, 7 deletions; patch ID `be157118`;
  binary-diff SHA-256 begins `cf70f18f`). Preserve it byte-for-byte. Do not
  attach, checkout, stage, copy, reset, stash, clean, or remove it.
- `codex/git-governance-research` remains attached at local `65703736`, differs
  from remote `51a8a57a`, and contains three locally unique patches. Preserve.
- `codex/excel-product-planning` remains attached at `a0e115e1`, has no feature
  remote or PR, and needs an owner decision. Git evidence cannot make it
  deletion-ready.
- `codex/release-preflight-alpha-policy` remains attached at local `5da9c66a`
  while its remote is `20180a40`. Both are integrated, but the dual-head lane is
  separate preserved evidence.
- GIT-7B, GIT-7C1, GIT-7D1, GIT-7D2, GIT-7D2 lessons, Alpha closeout, and Alpha
  integration branches remain attached worktree holds even where integration
  evidence is complete.
- Eight other local branches are unattached, remote-matching, main-reachable,
  and linked to merged PRs. They are future disposition candidates only; owner,
  dependent-PR, retention, classifier, and separate exact-approval gates remain.
- Running the classifier without a supplied evidence receipt truthfully reports
  `remote_freshness=NOT_CHECKED` and `UNKNOWN`. Never translate manually
  gathered facts into deletion authority.

## GIT-7E exact boundary

GIT-7E must prove:

1. every live indexed instruction rejects retired command and flag fixtures;
2. archive/historical exclusions are explicit rather than accidental;
3. branch, head, upstream, default base, tree, and operation identity survives
   session handoff;
4. remote, PR, reviewed-head, and required-check fields are exact or explicitly
   unknown;
5. task/transcript archive state is never represented as Git retention proof;
6. aliases resolve maintained commands without permitting obsolete mutations.

GIT-7E does not refresh remote state, mutate GitHub, change disposition logic,
authorize cleanup/deletion, synchronize preserved lanes, modify GIT-7D1/7D2
behavior, publish a release, or change product code. It requires separate owner
authorization before implementation.

## Destructive-action holds

- No branch, remote ref, or worktree deletion is authorized.
- No prune, reset, rebase, stash/drop, clean, force push, or primary-main sync.
- A future action needs a same-session refresh, complete identity-bound evidence,
  `RETIREMENT_READY_PENDING_APPROVAL`, separate exact local/remote/worktree
  authorization, immediate drift recheck, and post-action receipt.

## Session closeout

Discover maintained tests/scripts with `rg --files`. Run focused checks, the
semantic Git check, strict docs, quick gate, full gate once stable, session end,
and `git diff --check`. Record every material issue with symptom/impact, root
cause or explicit unconfirmed boundary, resolution, and proving evidence in the
newest task-owned `docs/SESSION_LOG.md` entry.
