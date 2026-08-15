---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: guide
complexity: intermediate
tags: [git, github, worktree, cleanup, learning]
---

# Git governance case study: GIT-7D2 and the cleanup audit

## Why this case matters

GIT-7D2 replaced a deletion-capable stale-branch script with an inspection-only
classifier. The implementation was correct only after several reviews exposed
a deeper pattern: a list of passing examples is not the same as a complete
invariant, and fresh-looking prose is not fresh evidence.

The follow-on cleanup audit deliberately deleted nothing. It tested whether the
new evidence model could describe real retained lanes without converting
manually gathered facts into authority. The result was a useful mix of exact
integration receipts, preserved unknowns, owner decisions, and future
candidates that are still not deletion-ready.

## The observed state

- `origin/main` was refreshed at `bf4065f0`.
- PRs #744-#748 were merged at their exact reviewed heads, required checks were
  green, their squash-result trees equal the reviewed trees, and both push
  workflows passed at each merge SHA.
- The desktop task added one clean detached worktree to the earlier audit
  count; the packet then added one explicitly owned branch/worktree.
- `e54a` remained detached at `0fdb48ed` with one unique dirty session-log
  patch. Its exact blobs, patch ID, diff hash, path, and hold were recorded
  without touching it.
- The GIT research, Excel planning, and Alpha policy lanes remained preserved
  for three different reasons: unique divergence, owner decision, and dual-head
  evidence.
- Eight other branches were unattached, remote-matching, main-reachable, and
  linked to merged PRs. They remained future disposition candidates because
  complete owner/PR-dependency/retention evidence and exact approval were not
  supplied to the classifier.

## Examples, invariants, and the misses

| Symptom and impact | Confirmed root cause or boundary | Resolution and proof |
|---|---|---|
| Scenario examples passed while a configured nonstandard default branch could enter the candidate path. The default integration anchor could have been nominated. | The implementation encoded familiar examples (`main`/`master`) instead of the invariant “the branch named by `default_ref` is retained.” | Derive the branch from the supplied configured default ref. A focused regression proves both `main` and custom `develop` receive `DEFAULT_BRANCH_INTEGRATION_ANCHOR`. |
| An `ABSENT` remote observation and “no retention” assertion looked complete without proving which target/head/time they described. A receipt could authorize the wrong identity. | Evidence presence was checked, but ref/head/time/freshness binding was incomplete. | Require exact target ref for present or absent remote evidence and fresh, target-head-bound PR/retention evidence. Mismatch, stale, future, missing, or failed evidence becomes `UNKNOWN`. |
| The semantic check passed after executable names changed, but a live agent guide still promised deletion. A later agent could restore the retired behavior. | The static checker used a hand-maintained surface/token list; replacement searched command strings but not headings and prose. | Search the full maintained guidance surface for semantic deletion claims. GIT-7E must own indexed live-surface selection; GIT-7D2 does not broaden that checker here. |
| A same-day handoff still said “in validation” after PR #748 was on `main`. Intake could repeat completed work despite a current date. | Calendar freshness and lifecycle freshness were conflated; the handoff was not bound to exact branch/head/PR/check/merge identities. | Reconcile the board, handoff, phase ledger, projections, and session record together. GIT-7E must make identity-bound handoff data durable. |
| Detached `e54a` carried a unique dirty session record that current indexed guidance did not name. Removing the worktree could destroy the only copy. | The evidence-producing session stayed on a deliberately non-mutated detached pre-merge lane, and no durable task-to-Git receipt existed. | Record exact path, head, diff stats, working/HEAD blobs, patch ID, diff hash, and preservation hold on current `main`; do not attach, checkout, stage, copy, reset, stash, or remove `e54a`. |
| Closeout commands guessed two test filenames, one index-checker filename, and a positional classifier selector. Required evidence stopped before collection. | Descriptive labels and remembered signatures were treated as maintained paths/CLI schema. | Discover with `rg --files`, repository find commands, and `--help`. Correct paths and `--branch` selector passed the intended gates. |
| A malformed GraphQL query failed, but a later semicolon-separated command made the composite shell command look successful. Review-thread evidence could have been falsely reported. | Semicolon sequencing returned the final command's status; the query was manually composed with unbalanced braces. | Run required hosted-evidence queries standalone or in a fail-fast chain and validate their output shape before using it. The corrected query reported zero threads at the unchanged PR head. |
| Independent review found the configured-default and evidence-binding defects late in closeout. Rework occurred after the first “done” narrative. | Review was scheduled after implementation examples rather than before the stable invariant was declared complete. | Use a bounded read-only reviewer before the full gate for outcome-changing evidence contracts; the parent still verifies and writes the final surfaces. |
| After squash merge, feature branches were `HOLD_DIVERGED` even though their content was integrated. An ancestry-only cleanup would either repeat work or erase evidence. | Squash creates a new commit identity. Reachability, patch identity, and tree identity answer different questions. | Bind PR reviewed head and merge SHA, compare trees/patches, verify integrated workflows, and retain attached or evidence-bearing lanes until separate disposition. |
| The personal learning package explained detached state and squash, but not the GIT-7D2 receipt schema. The implementation lesson lagged behind the repository control. | Learning-artifact update was not part of the earlier closeout definition. No timing trend can be inferred from one lag event. | Add one separately verifiable study addendum with evidence identity, `NOT_CHECKED`, default refs, schema discovery, teach-back, and 1/3/7-day prompts. |
| A zsh probe lost command lookup after assigning to `path`. Later evidence commands became unavailable. | In zsh, lowercase `path` is tied to `PATH`; it is not an ordinary scratch variable. | Use names such as `target_path` or `marker_target`. Run each evidence command from an explicit worktree root. |
| A review script queried `.branches` in classifier output and could silently see an empty set. | The same noun appears in two different schemas: caller evidence uses `.branches`; classifier receipts return `.targets`. | Inspect `--help` and one real JSON sample. Use `.targets[]` for receipt output and reserve `.branches` for the supplied evidence input. |

## Example tests versus invariants

An example asks whether a named case works:

```text
main is held
dirty branch is held
open-PR branch is held
```

An invariant asks what must remain true for every configuration:

```text
branch(default_ref) is always held
failed_or_unbound_evidence always becomes UNKNOWN
age never changes authority
classifier execution never mutates Git, GitHub, config, refs, or worktrees
```

Both are necessary. Examples make failures understandable; invariants prevent a
new name, configured default, or evidence variant from bypassing the rule.

## Evidence identity and freshness

Treat remote or hosted evidence as a tuple, not a sentence:

```text
(target ref, target head, observed_at_utc, freshness status, query outcome)
```

`NOT_CHECKED` is truthful evidence about what did not happen. It is never a
synonym for absent, current, merged, clean, or safe. A locally cached
`origin/*` ref can support local graph comparison, but it cannot be represented
as a fresh remote observation unless the caller actually refreshed it.

## Schema and shell discovery card

```bash
# Discover the maintained script and CLI contract.
rg --files scripts Python/tests | rg 'branch_disposition|git_state'
./scripts/python_runtime.sh scripts/classify_branch_disposition.py --help

# Receipt output uses .targets.
./scripts/python_runtime.sh scripts/classify_branch_disposition.py \
  --branch codex/example --json | jq '.targets[]'

# The caller-supplied evidence file uses .branches.
jq '.branches["codex/example"]' refreshed-evidence.json
```

For required external queries, prefer standalone commands or `&&`/explicit
exit checking. Do not use a later success to mask an earlier failure. In zsh,
never use `path` as a scratch variable because it changes `PATH`.

## Cleanup disposition ladder

```text
observed fact
  -> identity-bound evidence
  -> classifier disposition
  -> RETIREMENT_READY_PENDING_APPROVAL (only if complete)
  -> separate exact local / remote / worktree approvals
  -> same-session reinspection
  -> one approved action
  -> post-action receipt
```

At any unknown, dirty, attached, operation, divergence, open/dependent PR,
unique-work, or retention state, stop. A candidate table is a work queue, not
deletion authority.

## Eight-branch proposal: authority is not retention evidence

The next exact proposal refreshed eight unattached merged tips. Local, tracking,
and live remote heads matched; every tip was reachable from current `main`;
the exact PRs were merged; and no open PR used or referenced a target. Those
facts completed integration and dependency evidence, but not retention intent.

An initial draft treated authority to inspect, publish the proposal, and use the
normal PR lifecycle as `NO_RETENTION`. Orchestrator review caught the outcome-
changing inference before publication. The controlling instruction said delete
nothing until exact approval and never said these historical tips were unneeded.
All eight inputs were corrected to retention `UNKNOWN`; the integrated
classifier then returned `HOLD_UNKNOWN_OWNER` with
`RETENTION_EVIDENCE_UNKNOWN` for every exact SHA.

The lesson is narrower than “ask more often”:

```text
authority to orchestrate != evidence that history is unneeded
authority to publish a proposal != approval to delete its targets
known owner != known retention disposition
```

The generic `HOLD_UNKNOWN_OWNER` label is retained as the classifier's current
unknown-evidence disposition; its exact reason code states the actual missing
fact. GIT-7E remains not started.

## Teach-back

1. Why does `NOT_CHECKED` prevent a retirement-ready result even if `git
   status` is clean?
2. How would you prove the configured default branch is protected without
   naming `main` or `master` in the rule?
3. Which identities must an absent-remote observation carry?
4. Why can a squash-integrated branch be both `HOLD_DIVERGED` and fully
   integrated?
5. Why was `e54a` summarized on current `main` instead of copied, attached, or
   committed in place?
6. Which JSON path is input (`.branches`) and which is output (`.targets`)?
7. How can a semicolon-separated shell sequence produce a false green story?
8. What belongs to GIT-7E, and what would accidentally reimplement cleanup?

## 1/3/7-day review

- **Day 1:** From memory, write the evidence tuple and explain `NOT_CHECKED`.
  Run `--help`, then identify `.branches` and `.targets` in their correct roles.
- **Day 3:** Draw the squash graph for PR #747 and explain why equal trees do
  not authorize deletion of an attached worktree. Add the configured-default
  invariant using `develop`.
- **Day 7:** Given `e54a`, Excel, the Alpha policy lane, and one unattached
  merged branch, classify which facts are known, unknown, owner-gated, or
  approval-gated. Teach the full disposition ladder without using age or
  cleanliness as authority.

This review schedule is a learning aid. It makes no claim about elapsed task
time, token use, productivity trend, or improvement rate.
