# Next Session Briefing

## Current boundary

| State | Evidence and scope |
|---|---|
| **Current** | [StructLib 0.31.1 is published and verified](../getting-started/releases.md#v0311-published-and-verified). Use the [current release guidance](../getting-started/release-status.md) for the exact install and affected continuous one-way slab reruns. |
| **Next** | Start with the [offline maintenance queue](#next-work), beginning with APP-01 reproduction. |
| **Merged development work** | [Gross-section footing minimum steel #1133](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1133), [bounded ETABS 21.0 pair intake #1117](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1117), and [local floor review #1131](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1131) are on `main` after the 0.31.1 release. [Element guide #1127](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1127) and [contributor guide #1128](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1128) were verified using the public wheel. |
| **Draft review** | [Workbench #1129](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1129) still needs the physical-device, manual screen-reader, and deployed-host checks. [Upload demo #1132](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1132) has local browser and hosted evidence on its recorded head. Recheck the base and affected evidence when each draft resumes. |
| **ETABS** | Access was unavailable on 24 November. Use saved exports and synthetic fixtures for offline checks. Installed Windows qualification and fresh model captures wait for access. Real-floor acceptance and PROJECT01/02 require the matched project evidence defined in the [beam and column programme](beam-column-programme-delivery.md). |

## Next work

1. Reproduce **APP-01** through the batch application entry point. Interrupt a
   run, poll the same job ID, and record the job state and completed results.
   Compare with ordinary completion before deciding the repair scope.
2. Replay **SETUP-01**, **SETUP-02**, and **DOC-02** on the published wheel.
   Check partial extras, an interpreter path with spaces, and the runtime
   dependency reference. Use confirmed outcomes to bound one setup change.

The [0.31.1 follow-ups](structlib-0311-patch-plan.md#other-confirmed-issues-and-release-observations)
hold the original reproducers. The [task board](../TASKS.md#up-next) holds
the queue. Use the [canonical Git workflow](../git-automation/git-workflow-single-source.md)
when resuming an existing branch or starting a separate task.

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-11-08
- Focus: Reconcile the published 0.27 release/session records and qualify the lab's single-pass serializer on a fresh current base.
- Completed: Verified prior publication receipts and refreshed current install/status, append-only release ledger, artifact record, task board and handoff.; Inspected the latest lab handoff and R01-A1/A2/A3 evidence. BBS L01 is already released; historical serializer timing was superseded by fresh current-base evidence.; Replayed R01-A3 on the published wheel and recorded the deliberately relabelled S1-only/S2 evidence contract gap as a separate compatibility/design follow-up. No normal qualified-member journey failure or scope-contract repair is claimed.
<!-- HANDOFF:END -->

## Merged development work — qualified serializer integration

The owner selected this update after publication. The lab handoff is
`structlib-coding-lab/docs/pending-single-pass-integration.md`; its historical
LIB-LAB-003 base is `4eebc897f084e71165061c9d17ce89a867dadafa`. Its patch
changes only `beam/semantics.py` to traverse declared dataclass fields once.
The old measurements are historical. Fresh C1 `498d5c32` / C2 `0a3e57d9`
installed-wheel evidence matches 16 workflows, 633 result records, 230 exports
and 525 canonical outcomes. All 494 selected tests pass per wheel; the broader
Python suite passes 9018 tests (four skipped/six deselected). Three rounds of ten
alternating pairs reduce median ordinary/T workflow time by 28.23%/13.53% and
export time by 44.16%/29.08%, for these local selected paths only.

Pinned formatting successor `969a4904` changes one line wrap only. Whole-module
AST and executable-code equivalence pass, as do all 43 final-source WP01/WP06
checks. Measured wheels remain identified as C2, separate from that successor.
The [qualification record](../verification/library-serializer-optimization.json)
includes exact identities, test/measurement boundaries and all 30 timing pairs.

[PR #1066](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1066)
merged the source update. The 0.28.0 release includes it with the later
performance work listed in the changelog.

## Station evidence repair

[PR #1086](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1086)
repaired `LIB-MEMBER-EVIDENCE-001` in 0.29.2. The published 0.30.0 wheel still
rejects relabelled, missing-source and mismatched station evidence and accepts
a genuine two-station batch. The serializer work and its measurements retain
their original scope.

## Evidence and sequencing

The [release ledger](../getting-started/releases.md#v0270-published-and-verified),
[public verification receipt](https://github.com/Pravin-surawase/structural_engineering_lib/releases/download/v0.27.0/public-install-verification.json),
[artifact record](../verification/library-0270-release-artifacts.json), and
[plan](library-usability-improvement.md#post-release-serializer-optimization)
retain the source/artifact and scope boundaries. The 9a78/5c79 pairs remain
rejected baselines; the invalidated 423 intermediate is not deliverable.

[PR #1064](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1064)
merged the bounded 0.29.0 cases. The [0.30.0 plan](beam-column-programme-delivery.md)
tracks the remaining cases. Solver and native-host tracks retain their own plans.

## Required Reading

For Python work, start with the [API chooser](../reference/api-levels.md),
[executable examples](https://github.com/Pravin-surawase/structural_engineering_lib/tree/main/Python/examples), and
[completed usability scope](library-usability-improvement.md).
For installed Excel/ETABS work, use the
[WP10 plan](xll-product/wp10-etabs-read-adapter.md),
[PF11 blueprint](https://github.com/Pravin-surawase/structural_engineering_lib/tree/main/docs/planning/xll-product/library-definition/pf11), and
[current XLL plan](xll-product/current-plan.md).
All deliveries follow the [canonical Git workflow](../git-automation/git-workflow-single-source.md).
