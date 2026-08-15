---
owner: Main Agent
status: active
last_updated: 2026-08-15
doc_type: reference
task: GIT-001
phase: 7C2
owner_decision: authorized-and-applied-2026-08-15
---

# GIT-001 Phase 7C2 — Server Enforcement

## Authorization and prerequisite

The owner explicitly authorized the documented GIT-7C2 settings delta and
autonomous verification/rollback on 2026-08-15. The change was applied only
after PR [#745](https://github.com/Pravin-surawase/structural_engineering_lib/pull/745)
integrated GIT-7C1 and both post-merge workflows passed on `main`.

## GIT-7C1 integration receipt

| Evidence | Exact result |
|---|---|
| Reviewed base | `0fdb48edbb73114288feb8a246d6f30b80ac4d95` |
| Reviewed head | `c3edd24783df0f14efe1854f411dbc6735b44f40` |
| Review state | no comments, reviews, unresolved threads, conflicts, or essential blocker; required `PR Gate` passed |
| Merge method | squash |
| Resulting `main` | `729cc41bfb68e1381ddf3125d6365f40d9ff8738` |
| Content equivalence | reviewed-head and squash-result trees both `33d94f67834ea8cc669f73678022e89a927c0b02` |
| Post-merge workflows | [PR Validation 31864615708](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/31864615708) and [Validate Documentation 31864615731](https://github.com/Pravin-surawase/structural_engineering_lib/actions/runs/31864615731), both successful at the resulting `main` SHA |

## Applied current-to-target delta

Ruleset [`11390214`](https://github.com/Pravin-surawase/structural_engineering_lib/rules/11390214)
remains active and scoped to `refs/heads/main`.

| Surface | Before | Applied/current |
|---|---|---|
| Pull requests | no pull-request rule | required; zero approving reviews; no code-owner, last-push, stale-review, or thread-resolution requirement |
| Required check | strict `PR Gate`, integration `15368` | retained unchanged |
| History/deletion | deletion and non-fast-forward blocked | retained unchanged |
| Standing bypass | repository role `actor_id=5`, mode `always`; current owner could always bypass | `bypass_actors=[]`; `current_user_can_bypass=never` |
| Ruleset merge methods | not applicable without a PR rule | `merge` and `squash` only |
| Repository merge methods | merge, squash, and rebase enabled | merge and squash retained; rebase disabled |
| Delete branch on merge | disabled | preserved disabled |
| Auto-merge/update branch | disabled/disabled | preserved disabled/disabled |

The effective branch-rule API independently reports deletion,
non-fast-forward, strict `PR Gate`, and pull-request enforcement from this
ruleset. The repository API reports squash and merge-commit enabled, rebase
disabled, and branch deletion after merge disabled.

## Transaction, rollback, and risk receipt

The first guarded update was rejected by the exact postcondition because
GitHub added the normalized empty field `required_reviewers: []`. The
transaction automatically restored the original three rules and standing
bypass before repository merge settings changed. A controlled
apply/read/rollback probe confirmed the normalization, then the final guarded
transaction included that field and passed every postcondition.

The preserved rollback is the exact inverse: restore the three original rules,
restore `{actor_id: 5, actor_type: RepositoryRole, bypass_mode: always}`, and
set `allow_rebase_merge=true`; keep the other repository settings unchanged.
Rollback is appropriate only if PR creation or required-check integration is
proven unusable, and must use the same read-before/write/exact-readback guard.

Primary risks are a misnamed required context blocking integration, loss of a
routine direct-main escape path, and server normalization causing false
postcondition failures. GIT-7C1 proved the exact `PR Gate` context; the owner
accepted deliberate ruleset edit plus dated rollback as the emergency path;
and the normalized response is now part of the verifier.

## Phase 5 acceptance status

| Scenario | Evidence/status |
|---|---|
| Control-plane and docs routes gate the exact PR head | passed on PR #745 |
| Failed, cancelled, skipped, or timeout-like applicable work fails `PR Gate` | executable GIT-7C1 result-matrix tests passed |
| Same-PR cancellation is scoped | GIT-7C1 workflow contract passed |
| Main requires a PR with strict `PR Gate` | current ruleset and effective branch rules confirm |
| Standing bypass is absent | current ruleset reports empty actors and `never` |
| Deletion/non-fast-forward protections remain | current effective rules confirm |
| Merge methods and branch deletion match target | current repository and ruleset APIs confirm |
| Before/after settings match the authorized delta | guarded postcondition passed; remote `main` and both workflows remained unchanged/green |

The owner phrase that authorized the mutation was: “Adopt the standing Git
authorization model and apply the documented GIT-7C2 settings delta now.
Proceed autonomously through verification and rollback if needed.”

No branch, worktree, release, cleanup target, or product code was changed by
the settings transaction.
