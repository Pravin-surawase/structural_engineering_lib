# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: Make Excel-only CI, public-route safety evidence, readiness exits,
- Git receipt: docs/verification/lib-pro-003-d-git-handoff-receipt.json | sha256:7f46984750c4f5ade6e5d5c1b16d7d4b27599496885dc9b588615e393e9264d0 | HOLD
- Git identity: codex/public-route-decisive-gates@027554457c58303f435dc4a9940dc683def22895 | upstream=origin/main@027554457c58303f435dc4a9940dc683def22895 | base=origin/main@027554457c58303f435dc4a9940dc683def22895 | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | `LIB-PRO-003-D` local candidate is accepted from exact Packet C merge `02755445`: 78 safety, 21 Excel, 6,653 Python, 479 FastAPI, 276 React, quick 10/10, and full 31/31 pass |
| **Next** | Create the immutable candidate, pass hosted checks, verify exact candidate/merged tree equality, then resume read-only `INDIA-3-G0` |
| **Why** | Direct replay reproduced 13 outcome-changing behaviours still exposed outside the newer bounded Gravity/E1 workflows |
| **Held** | INDIA-3, new formulas/support claims, ETABS, package publication, stable/professional claims, and qualified approval remain separate and held |

## E1 final acceptance

- Desktop Excel opened the exact 15,101-byte workbook without recovery, silent
  repair, or byte mutation.
- Frozen row accounting passed: five source rows equal two accepted, two
  blocked, and one excluded row, with zero residual.
- Expected results were preserved: derived-depth `PASS`, explicit-depth
  `FAIL`, numeric-text width `BLOCKED`, blank row `EXCLUDED`, and
  populated Torsion `HOLD`.
- Same-snapshot pane exports were byte-identical. Editing a calculation-bearing
  input produced `STALE` and disabled Export; rerun restored `CURRENT`.
- Save, close, reopen, explicit Freshness, and export reproduced the second
  snapshot byte-for-byte.
- Excel and ETABS were closed, services stopped, ports 3000/8000 freed, and
  every retained Windows Git lane remained clean.
- Cumulative local acceptance passed 6,508 Python tests and 31/31 repository
  checks. Exact-head hosted PR Validation passed before merge.

The workbook remains macro-free and formula-free. Python remains the calculation
authority. Results remain `NOT_REVIEWED` with
`qualified_review_required=true`.

## Correct next library packet

`LIB-PRO-003-D` is locally accepted and awaiting hosted/exact-tree closure.
Packets A-C were
exact-tree merged through PRs #832-#834 at `e7698a63`, `e19b757c`, and
`02755445`.

The implemented outcomes are: every `excel_addin/**` change reaches all add-in
tests and the PR gate; frozen public-route regressions are required readiness
evidence; `PARTIAL` is nonzero; release/API metrics are synchronized; and the
owner-selected 500-file documentation cap is enforced. Readiness remains
`PARTIAL` because two heuristic diagnostics are unresolved, so release and
professional-use claims remain held.

Do not start
new engineering formulas, IS 13920 expansion, IS 875, IS 1893, FEM, or ETABS.

## Other live work

- `v0.23.1a2` is already public. Gravity and E1 were merged afterward, so any
  next package must use a new version and fresh exact-artifact evidence; never
  republish `0.23.1a2`.
- `INDIA-3-G0` remains the next capability-truth packet, but it is deferred
  until the reproduced public-route safety closure is complete.
- `SPARK-001-G0` remains an owner-review proposal. Its model/preview assumptions
  date from 2026-08-11 and must be refreshed or rejected before a wave starts.
- Dependabot PRs are separate maintenance work and do not outrank the
  capability-truth packet.
- ETABS T1 remains a separate read-only file/snapshot program. E1 completion
  makes it possible, but does not activate it.
- INDIA-4 cumulative qualified review remains downstream of the frozen INDIA-3
  scope and is not yet ready.

## Required Reading

1. [Public route safety closure plan](public-route-safety-closure-plan.md)
2. [Current task board](../TASKS.md)
3. [Pre-release input safety plan](pre-release-input-safety-and-professional-readiness-plan.md)
4. [Git workflow single source](../git-automation/git-workflow-single-source.md)
