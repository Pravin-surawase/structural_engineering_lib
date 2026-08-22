# Next Session Briefing

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: Close accepted E1, reconcile release/task truth, and select the next bounded library decision packet without ETABS or new engineering implementation.
- Git receipt: docs/verification/e1-g3-closeout-git-handoff-receipt.json | sha256:7237912b87c081142c2bda364d639fb96f4c9a1eca48a4c520586f048a34ef85 | HOLD
- Git identity: codex/e1-g3-closeout@b720119ea6a22a2b1963be0a0b9b300fca333d4a | upstream=origin/main@b720119ea6a22a2b1963be0a0b9b300fca333d4a | base=origin/main@b720119ea6a22a2b1963be0a0b9b300fca333d4a | tree=dirty | operation=none
- Hosted evidence: remote=NOT_CHECKED | PR=NOT_CHECKED#UNKNOWN | review=NOT_CHECKED | retention=OBSERVED
- Next action: COMMIT_INTENDED_PATHS
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | E1 passed the real installed Windows Excel journey and is integrated into `main` |
| **Next** | Owner may activate `INDIA-3-G0`: audit existing IS 13920 beam/column/joint truth and freeze one bounded acceptance sequence |
| **Why** | INDIA-0, INDIA-1, and bounded INDIA-2 are complete; INDIA-4 depends on a frozen INDIA-3 scope |
| **Held** | No new formulas, support claims, IS 875/IS 1893 work, ETABS work, package publication, or professional approval in G0 |

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

`INDIA-3-G0` is a decision and truth-audit packet, not implementation.

1. Inventory the currently implemented and advertised IS 13920 beam, column,
   and joint checks.
2. Bind every claimed case to exact source provenance, units, applicability,
   result/status contracts, and independent benchmarks.
3. Identify false registration, missing cross-layer exposure, or unsupported
   claims that change user outcomes.
4. Freeze one small acceptance sequence and explicit exclusions before any new
   calculation, API, or UI work.
5. Return `ACCEPT`, `REVISE`, or `HOLD` plus the exact first implementation
   packet.

Do not start IS 13920 wall/foundation expansion, IS 875, IS 1893, response
spectrum, FEM, or ETABS during G0.

## Other live work

- `v0.23.1a2` is already public. Gravity and E1 were merged afterward, so any
  next package must use a new version and fresh exact-artifact evidence; never
  republish `0.23.1a2`.
- `SPARK-001-G0` remains an owner-review proposal. Its model/preview assumptions
  date from 2026-08-11 and must be refreshed or rejected before a wave starts.
- Dependabot PRs are separate maintenance work and do not outrank the
  capability-truth packet.
- ETABS T1 remains a separate read-only file/snapshot program. E1 completion
  makes it possible, but does not activate it.
- INDIA-4 cumulative qualified review remains downstream of the frozen INDIA-3
  scope and is not yet ready.

## Required Reading

1. [Indian-code completion plan](indian-code-completion-plan.md)
2. [IS 456 library-first master plan](is456-library-first-master-plan.md)
3. [E1 workbook-open repair evidence](../verification/e1-workbook-open-repair-evidence.md)
4. [Current task board](../TASKS.md)
5. [Git workflow single source](../git-automation/git-workflow-single-source.md)
