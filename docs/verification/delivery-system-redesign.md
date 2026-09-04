# Delivery System Redesign

**Frozen:** 2026-09-04
**Scope:** repository delivery controls only; no WP10 product feature work

## Audited evidence

The authoritative ignored Git-common usage ledger and the merged histories of
[PR #964](https://github.com/Pravin-surawase/structural_engineering_lib/pull/964)
and [PR #965](https://github.com/Pravin-surawase/structural_engineering_lib/pull/965)
show the delivery pattern below.

| Packet | Elapsed | Candidates | Audit rejections | Repairs | Focused retries | Integrity runs | Session-end runs | Hosted runs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| WP09 standalone | 396.381 min | 7 | 2 | 14 | 14 | historical | historical | 2 |
| WP09 postmortem controls | 65.235 min | 2 | 0 | 1 | 1 | repeated | repeated | 2 |
| WP10-01 | 86.37 min | 4 | 2 | 2 | 3 | 5 | 6 | 1 |

Historical phase allocations were caller-supplied. Elapsed time, candidate Git
objects, and integration trees were mechanically validated. PR #964 merged
three commits after ten successful checks; PR #965 merged four commits after
one applicable hosted run. Neither PR recorded an independent GitHub review.

## Causal model

1. Oversized or late cross-runtime packets widened the invalidation radius.
2. Candidate and review ceilings existed only in prose, so commands could not
   stop repeated candidate, integrity, or closeout cycles.
3. Mutation-capable integrity hooks and live-state receipts changed bytes or
   identities after the supposed freeze.
4. Whole-tree/solution formatters and shell-specific command shapes produced
   unrelated churn and delayed failures.
5. Local and hosted formatting/integrity boundaries were not equivalent.
6. Manually entered closeout counters described waste after the fact but could
   not prevent it.

## Frozen disposition

| Decision | Controls |
|---|---|
| Keep | branch protection, required hosted checks, `git_state.py`, impact routing, permission/routing registries, release authorization, historical receipt validation |
| Update | session admission/closeout, preflight, usage accounting, changed-path formatting, hosted formatting, governing instructions/skills |
| Merge | six manual mutation-capable hygiene fixers into the read-only `verification.py integrity` owner |
| Narrow | Git receipts to real device/worktree/installed-artifact/authority transitions |
| Remove | `session end --fix`, hidden end telemetry, per-commit quick-gate ritual, whole-solution formatting, raw operation-count assertions |
| Add | persisted delivery transitions and one idempotent pre-push guard |

## Executable lifecycle

```text
INTAKE → BOUNDED_UNITS → CONTENT_FROZEN → FORMATTED
       → FOCUSED_VERIFIED → PREPARED → CANDIDATE
       → AUDIT_ACCEPTED → INTEGRITY_VERIFIED → FINAL_CLOSED
       → PUSHED → HOSTED_PASSED → MERGED → usage CLOSEOUT

first rejection:  CANDIDATE → REPAIR → ... → REPAIRED_CANDIDATE
second rejection: REPAIRED_CANDIDATE → REPLAN
REPLAN → BOUNDED_UNITS only after the acceptance digest changes
```

The ignored Git-common ledger stores transitions, so the guard survives process
boundaries without changing the candidate. `FINAL_CLOSED` is recorded once by
pre-push after read-only `session end`; a repeated push of the same head reuses
that transition. Hosted and merge identities are recorded only after push.

## Acceptance contract

| Requirement | Machine check |
|---|---|
| Safe intake on clean synchronized `main` | preflight admits `HOLD_MAIN_INTAKE_ONLY`; `BOUNDED_UNITS` still requires a feature branch |
| No post-freeze formatter spill | `verification.py format` selects changed source paths and compares all other repository bytes before/after |
| Immutable integrity boundary | consolidated manual integrity owner performs read-only syntax/whitespace/line-ending/conflict checks |
| One independent decision | audit transition is bound to the latest exact candidate head and evidence |
| Initial plus one repair candidate | third candidate in one design revision is rejected |
| Second rejection forces design change | `REPLAN` cannot advance until an acceptance-file digest changes |
| One final closeout | idempotent pre-push transition counts exactly one `FINAL_CLOSED` state |
| One hosted cycle | a second `HOSTED_PASSED` transition is rejected |
| Merged content is reviewed content | merge commit must be reachable from `origin/main` and its tree must equal the accepted candidate tree |
| Exact efficiency report | phases and counters derive from transition timestamps, timed commands, and Git objects; caller-entered counters are rejected for managed tasks |

The target operating envelope is one candidate, zero repair batches, one
integrity run, one final closeout, one hosted run, and less than ten percent of
elapsed time in the writer-rework phase. An essential failure may use the one
repair candidate; the target is diagnostic, not permission to hide a defect.
