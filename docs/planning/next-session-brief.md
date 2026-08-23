# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-24
- Focus: Converge maintained compatibility callers after P1-P6, prove every
- Git receipt: docs/verification/lib-pro-007-p7-compatibility-convergence-git-handoff-receipt.json | sha256:ad5d7e13b351b2e8c510de0f02260ecd3c621998c2b825f7bab50f834eaa0b0e | HOLD
- Git identity: codex/lib-pro-007-p7-compatibility-convergence@6cb4722103bfc018dc3889fcc1a5a437e3579897 | upstream=NONE@UNKNOWN | base=origin/main@6cb4722103bfc018dc3889fcc1a5a437e3579897 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-007-P7` has an implementation-complete compatibility ledger and caller migration from exact hosted P6 base `6cb47221` / tree `d2b3efa3` |
| **Next** | Freeze P7 evidence, run the focused/static/API batch, quick gate and staged hooks once, then merge only the unchanged green candidate |
| **Why** | P7 proves facade volume is intentional projection over canonical owners, removes maintained caller ambiguity, and preserves incompatible older ETABS shapes as held contracts |
| **Held** | M0 broad suites, installed Windows Excel rerun, live ETABS automation, EDB parsing, analysis control, model save/write-back, INDIA-3 engineering, release, public deletion, branch/worktree deletion, and professional approval |

## P7 candidate outcome

- P6 merged through PR #858 at hosted `6cb47221`, reviewed candidate
  `9647fedd`, and exact candidate/merged tree `d2b3efa3`; P7 starts from that
  exact tree and preserves the held INDIA-3 lane plus every unrelated lane.
- Live remeasurement finds 222 root, 199 service, and 199 legacy declared
  exports. The 620 facade projections reconcile exactly with classification;
  498 compatibility entries are projections, not independent calculators.
- The ledger records 222 canonical owners, exact function/class/value identity,
  symbol-by-symbol module namespace ownership, 45 root stubs, the 87-name
  `api_hub` subset, existing deprecation warnings, and every maintained caller.
- Maintained internal source/scripts and current examples/docs now use owning
  modules or the deliberate package-root facade. Compatibility tests, migration
  evidence, archives, fixtures, and vendor/reference content remain preserved.
- `structural_lib.api` stays import-compatible without a warning or removal
  schedule. Four historical ETABS helpers remain `HELD_COMPATIBILITY`; they do
  not produce the accepted P5 snapshot or gain fabricated project defaults.
- No second structural calculation path, ambiguous owner, or retirement
  candidate was found. Deletion and public contract breaks remain unauthorized.

## P7 verification boundary

- Run focused facade/package/P5 and representative P1-P6 vectors together,
  then changed-source Ruff/mypy, architecture/import/circular and API
  classification/manifest checks.
- Run the consolidated quick gate exactly once outside normal hook reuse and
  the normal staged hooks once on the immutable candidate.
- React and Office.js were not changed; installed Windows Excel is
  `NOT_REQUIRED_UNCHANGED_SURFACE`. Broad Python/FastAPI/React and full
  repository gates remain reserved for cumulative M0.

## Required Reading

1. [Product-foundation convergence plan](lib-pro-007-product-foundation-convergence.md)
2. [P7 compatibility migration](../migration/lib-pro-007-p7-compatibility-convergence.md)
3. [P7 compatibility ledger](../reference/api-compatibility-ledger.json)
4. [P7 machine evidence](../verification/lib-pro-007-p7-compatibility-convergence-evidence.json)
5. [P6 cross-surface parity evidence](../verification/lib-pro-007-p6-cross-surface-parity-evidence.json)
6. [Current task board](../TASKS.md)
7. [Git workflow single source](../git-automation/git-workflow-single-source.md)
