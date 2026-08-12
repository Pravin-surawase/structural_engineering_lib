---
owner: Main Agent and repository owner
status: draft
last_updated: 2026-08-13
doc_type: spec
task: GIT-001
phase: 6
owner_decision: pending
implementation_authorized: false
---

# GIT-001 Phase 6 — Canonical Policy Proposal and First Packet

## Recommended owner decision

**Accept the proposed operating model and authorize only GIT-7B, the read-only
state and intake kernel, as the first implementation packet.**

Do not yet authorize GitHub ruleset changes, CI topology changes, generated-data
contract changes, cleanup migration, branch/worktree deletion, or the handoff
schema. Those remain GIT-7C, GIT-7D, and GIT-7E after GIT-7B integrates and its
receipt is reviewed.

This split fixes the root dependency first: every later decision needs one
truthful, worktree-aware state model. GIT-7B has no destructive or server-setting
authority.

## Evidence supporting acceptance

- Phase 1 completed official Git/GitHub/Codex factual coverage with two passing
  independent reviews.
- Phase 2 traced ten incident families through symptom, impact, root cause,
  unsafe reaction, control, recovery, and proof.
- Phase 3 retained thirteen outcome-changing gaps across current scripts,
  settings, CI, instructions, and behavior.
- Phase 4 maps every gap to four bounded control planes and four ordered packets.
- Phase 5 reproduced the current linked-worktree merge and detached-HEAD false
  safety results in a disposable repository, proved the required Git primitives
  are available, and defined falsifiable packet gates.
- Live PR/CI is currently fast and mostly green, so the proposal preserves the
  changed-path fast path rather than replacing the whole workflow.

## Exact canonical decisions proposed

### CP-01 — one task/lane/owner identity

Normal implementation uses one task, one `codex/<task-slug>` branch, one
attached worktree, and one named integration owner. Primary `main` stays a clean
integration anchor. Shared/session/generated surfaces have one writer.

### CP-02 — one read-only Git state authority

All task intake, trust, quick-gate, handoff, and disposition consumers use one
typed, worktree-aware state kernel. Unknown, detached, locked, operation-active,
dirty-unowned, behind, and diverged states fail closed with named holds. No
repository validator performs or recommends recovery mutation.

### CP-03 — preservation before synchronization

Dirty work is classified and durably checkpointed within owned scope before a
topology change. No reset, clean, stash, checkout, rebase, skip, force-push, or
automatic conflict resolution is used to escape uncertain state.

### CP-04 — scripts inspect; Codex owns lifecycle mutation

Repository workflow scripts may inspect, validate, classify, generate approved
project artifacts, and emit receipts. They do not stage, commit, fetch/prune as
part of a claimed read-only check, pull, merge, rebase, reset, restore, stash,
clean, switch/checkout, create/remove worktrees, push, create/merge/close PRs,
delete branches, or mutate GitHub settings. Approved release automation remains
separately bounded by its existing release policy.

### CP-05 — PR-required server enforcement

Main requires a PR and strict exact-head `PR Gate`; deletion and non-fast-forward
updates remain blocked. The standing always-bypass role is removed. Emergency
recovery requires an explicit, dated ruleset change and restoration receipt,
not a permanent bypass.

### CP-06 — two retained merge methods

- Squash is default for one-packet ephemeral branches; a squash-merged branch is
  terminal and never reused as a new packet base.
- Merge commit is allowed for named integration, recovery, release, or
  long-lived governance lanes where ancestry is evidence.
- Rebase merge is disabled.

No published branch is rewritten to fit the chosen method.

### CP-07 — outcome-routed required CI

Keep current path-based parallelism and the fail-closed `PR Gate` aggregator.
Control-plane changes run their maintained outcome tests; strict documentation
build becomes an applicable exact-head dependency. Correctness stays
deterministic; performance/artifact/dependency/Docker breadth remains scheduled
or release-specific.

### CP-08 — targeted generated data

Preferred generators require an explicit owned target or `--all`, support
non-writing preview, refuse unexpected topology without opt-in, and emit exact
changed-path receipts. Canonical output is not authority to accept unowned churn.

### CP-09 — inspection-only cleanup disposition

Age and ancestry are metadata, not cleanup authority. The maintained classifier
does not fetch/prune or delete. Retirement-ready requires exact attachment,
dirty/operation, ownership, PR, reachability, patch/tree, evidence-retention,
and approval facts. Codex performs separately approved exact targets and records
the post-action inventory.

### CP-10 — explicit task-to-Git handoff

Session closeout records or explicitly marks unknown the branch, head, upstream,
default base, tree/operation state, remote head, PR, reviewed SHA, required
checks, merge identity, and retention holds. Task archive/transcript state is not
represented as Git retention proof.

### CP-11 — measurable speed and truth budgets

- local current-worktree state p95 <= 0.50 seconds;
- six-worktree intake p95 <= 2.0 seconds;
- docs/policy PR Gate p95 <= 90 seconds;
- control-plane PR Gate p95 <= 2 minutes;
- zero false ready states in abnormal scenarios;
- zero unowned generated paths or ancestry/age-only cleanup candidates.

## Proposed canonical-file disposition

After owner acceptance, GIT-7B may add only the CP-01 through CP-04 state/intake
language needed for its implementation. Later packets own the rest:

| Policy surface | Packet owner |
|---|---|
| `docs/git-automation/git-workflow-single-source.md` state/intake model | GIT-7B |
| `AGENTS.md` and platform instruction state/intake wording | GIT-7B, narrowly |
| GitHub ruleset and merge settings | GIT-7C |
| Required CI topology | GIT-7C |
| Generator and cleanup/disposition policy | GIT-7D |
| Live-instruction semantic drift and handoff receipt | GIT-7E |

Historical documents remain evidence and are not bulk rewritten. Live stale
instructions are corrected only in the packet that owns their executable
contract.

## GIT-7B — exact first implementation packet

### Objective

Replace contradictory local Git classification with one read-only,
worktree-aware, typed state kernel and make task brief, session trust, and the
quick Git gate consume it.

### Authorized files

- new `scripts/git_state.py`;
- `scripts/prompt_router.py`;
- `scripts/session.py`;
- `scripts/check_all.py`;
- `scripts/automation-map.json`;
- `scripts/check_codex_git_workflow.py`;
- focused state/intake tests under `Python/tests/`;
- `.github/workflows/fast-checks.yml` only to run those focused tests for the
  changed control-plane paths;
- the narrow canonical/agent instruction text required to name the kernel;
- task/session/handoff and owned generated indexes for the packet receipt.

If implementation proves another file essential, stop and amend the packet
before editing it.

### Required behavior

1. Use porcelain-v2 and `git rev-parse --git-path`/`--git-common-dir`.
2. Disable optional locks for every inspection command.
3. Distinguish default-base and upstream reachability.
4. Distinguish staged, unstaged, untracked, conflicted, operation, lock,
   detached, no-upstream, behind, ahead, diverged, and unknown state.
5. Return typed JSON plus concise human output.
6. Use no network by default.
7. Emit holds, never recovery mutations.
8. Make sibling queries bounded; timeout/error becomes unknown.
9. Keep session trust fail closed.
10. Preserve `task brief` routing/tool-discovery behavior while correcting its
    Git evidence.
11. Route control-plane CI to the exact focused tests.
12. Retire old shell semantics only after every consumer and scenario passes.

### Non-goals

- No fetch, pull, merge, rebase, reset, restore, stash, clean, checkout/switch,
  commit, worktree mutation, push, PR/GitHub mutation, or branch deletion.
- No GitHub ruleset or merge-setting change.
- No cleanup classifier or generator rewrite.
- No broad documentation modernization.
- No release, product runtime, structural calculation, API, or React change.
- No generic test expansion beyond the outcome scenarios.

### Likely pitfalls

- treating `.git` as a directory in linked worktrees;
- reversing `A..B` direction labels;
- using upstream as a substitute for default base;
- making network freshness a local trust prerequisite;
- refreshing another worktree's index during background inspection;
- collapsing command failure or timeout to clean/empty;
- letting compatibility wrappers preserve divergent semantics;
- editing shared generated/session surfaces from more than one lane.

### Acceptance

All twelve GIT-7B scenarios in the Phase 5 report pass, including normal and
linked-worktree operation markers, detached/dirty/conflicted/locked/unknown
states, directional reachability, optional-lock sibling observation, no
before/after Git mutation, and both performance budgets. Focused control-plane
CI must run and pass at the exact PR head. Quick and full repository gates pass
once at closeout.

### Implementation recovery boundary

Implement on a fresh branch/worktree from refreshed exact main. If the kernel
cannot classify the active lane or conflicts with current shared surfaces, stop;
do not use the old validator to override the new result. No compatibility file
is deleted until its callers are enumerated and the replacement scenarios pass.

## Held packets

- **GIT-7C:** workflow and GitHub settings; requires fresh owner confirmation
  immediately before server mutation.
- **GIT-7D:** generator/disposition migration; contains no deletion, while any
  later cleanup still requires exact target approval.
- **GIT-7E:** semantic guidance and handoff receipt.

The three held packets are not implicitly authorized by acceptance of this
proposal or GIT-7B.

## Owner response contract

The owner may choose exactly one route:

1. **Accept Phase 6 and authorize GIT-7B** — recommended; implementation may
   start exactly within the packet above.
2. **Accept Phase 6, hold GIT-7B** — policy direction accepted; no implementation.
3. **Revise** — name the decision or packet boundary to change; no implementation
   until the revision is accepted.
4. **Reject** — current canonical policy remains unchanged and the program stops
   before implementation.

Until one route is explicitly recorded, Phase 6 remains pending and no broader
Phase 7 work is authorized.
