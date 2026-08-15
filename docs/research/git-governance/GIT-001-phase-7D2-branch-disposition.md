---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: GIT-001
phase: 7D2
---

# GIT-001 Phase 7D2 — Inspection-Only Branch Disposition

## Scope and migration decision

GIT-7D2 replaces the deletion-oriented
`scripts/cleanup_stale_branches.py` path with
`scripts/classify_branch_disposition.py`. A new command name is intentional:
the maintained route now classifies evidence and cannot perform cleanup.

The replaced script combined incomplete classification with mutation. It
fetched with prune during review, ignored subprocess return codes, interpreted
empty results as merged/old, treated missing dates as 999 days old, let age
nominate branches, and exposed direct remote deletion. This could change the
main-process outcome by presenting unpublished or squash-integrated evidence as
stale and then removing it.

This packet changes no branch, remote ref, worktree, GitHub setting, issue,
release, or product behavior. Actual retirement remains outside GIT-7D2.

## Preferred command

```text
./scripts/python_runtime.sh scripts/classify_branch_disposition.py \
  --branch codex/example \
  --evidence refreshed-evidence.json \
  --json
```

`--all-local` can inspect every non-default local branch. Without a supplied,
SHA-bound remote/PR receipt, remote freshness is `NOT_CHECKED` and every target
holds as `UNKNOWN`.

## Evidence boundary

The classifier obtains these facts with bounded, optional-lock-safe local Git
queries:

- exact local and remote-tracking refs and heads;
- attachment plus dirty/operation/query state from the worktree-aware state
  authority;
- default reachability and directional commit counts;
- `git cherry` unique/equivalent patch facts;
- exact branch/default tree identities and equality;
- last-commit age as metadata only.

The caller supplies remote and GitHub facts after refreshing them:

- observation timestamp, default ref, and exact default SHA;
- named owner;
- exact present/absent remote-ref evidence and SHA when present;
- open/dependent/no-open-PR state bound to the inspected head;
- explicit retain/no-retention evidence bound to the inspected head and a fresh
  observation timestamp.

Missing, malformed, inconsistent, older than 15 minutes, future-dated,
timed-out, or failed evidence is an `UNKNOWN` hold. The command never represents
local remote-tracking data as a fresh remote observation.

## Outcomes

| Disposition | Meaning |
|---|---|
| `HOLD_ATTACHED_OR_DIRTY` | An attached lane exists; reason codes distinguish clean attachment, dirt, and active operations |
| `HOLD_UNKNOWN_OWNER` | Ownership, remote/PR/retention evidence, target identity, or a required query is unknown |
| `HOLD_OPEN_OR_DEPENDENT_PR` | Refreshed evidence reports an open or dependent pull request |
| `HOLD_UNIQUE_OR_UNPUBLISHED_WORK` | Exact commit/patch or local/remote-head evidence contains unique/unpublished work |
| `HOLD_EVIDENCE_RETENTION` | The target is explicitly retained as project/forensic evidence |
| `PATCH_EQUIVALENT_REVIEW_REQUIRED` | Patch or tree equivalence needs human/Codex receipt review; equivalence is not retirement authority |
| `RETIREMENT_READY_PENDING_APPROVAL` | Every required input is known and no earlier hold applies; separate exact-target approval is still required |

Every receipt declares `mutation_policy=INSPECTION_ONLY` and
`authorization=SEPARATE_EXACT_TARGET_APPROVAL_REQUIRED`.

The configured default branch is always an integration-anchor retention hold,
including a custom default such as `develop`; it cannot become a retirement
candidate through the zero-ahead path.

## Non-mutation controls

- `GIT_OPTIONAL_LOCKS=0` and `GIT_TERMINAL_PROMPT=0` apply to every local Git
  subprocess.
- The CLI exposes no deletion/execution/apply action flag and no receipt output
  path.
- The classifier has no fetch, prune, push, update-ref, checkout, reset, stash,
  rebase, clean, configuration-write, worktree-mutation, or GitHub command.
- The maintained semantic Git-workflow check requires the classifier, its
  dispositions, its CI regression family, the absence of the former script,
  and inspection-only routing on live guidance surfaces.

## Acceptance evidence

The focused regression family proves:

1. filesystem, refs, index, and Git configuration are unchanged before/after;
2. a simulated Git query failure returns `UNKNOWN`;
3. age is marked non-authoritative and cannot overcome missing evidence;
4. attached, dirty, open-PR, unique, patch-equivalent, retained, and fully
   evidenced candidates are distinguishable;
5. `NOT_CHECKED` is preserved and cannot produce a candidate;
6. observed commands are local read-only queries and the CLI has no action
   flag;
7. the JSON receipt carries exact identities, facts, holds, and the separate
   authorization boundary.

The Control Plane Validation job runs this regression family at the exact PR
head. Strict documentation, semantic Git workflow, quick, and full repository
gates remain required before integration.

## Integration completion

GIT-7D2 completed through two unchanged-head squash integrations:

| Evidence | Exact result |
|---|---|
| Implementation PR | #747, reviewed head `8742061604f75ad0807cb012a1192ebf997143bf` |
| Implementation merge | `0a784de5cd519b661105846c4dfb2cf5bac51928` |
| Implementation tree | reviewed and merged tree `c6f4a6f7f65eaf3561ab226a2e9b28dfd6436eae` |
| Closeout-lessons PR | #748, reviewed head `cb2750b9f2c0eaf2cbecff33f3ed09db1b82585e` |
| Closeout-lessons merge | `bf4065f071f1245461df6d3c42f1cc070efbae70` |
| Closeout-lessons tree | reviewed and merged tree `2b8e3cdb32e342c43a41af98e868c717feaca646` |
| Required checks | `PR Gate` passed at both unchanged reviewed heads |
| Post-merge workflows | `PR Validation` and `Validate Documentation` passed at both merge SHAs |

The original feature and lessons branches/worktrees remain retained. Squash
tree equivalence proves integrated content but does not make either attached
lane a deletion candidate. The Phase 7D cleanup reconciliation records the
current preservation and disposition boundary without performing deletion.

## Non-goals and retained state

No local/remote branch or worktree is deleted, detached, pruned, cleaned, or
rewritten. No settings, bypass actors, releases, product code, or GIT-7E durable
handoff work are included. The GIT-7D2 feature branch/worktree remains retained
after integration until a later exact disposition and authorization.
