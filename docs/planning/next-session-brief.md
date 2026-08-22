# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: freeze and validate one generated workbook-open repair, then rerun the frozen Windows G3 journey once
- Exact predecessor: `codex/e1-review-bundle-export` at `98c60bc1f7c3899c28f662e82399cb25d80bbf26`, tree `3ee6772114aaf7979473ebfb35b76c27cfbb80a0`
- Repair lane: `codex/e1-workbook-open-repair`, stacked directly on that immutable predecessor
- Evidence: `docs/verification/e1-workbook-open-repair-evidence.md`
- Git handoff receipt: `docs/verification/e1-workbook-open-repair-git-handoff-receipt.json` (`HOLD`; file SHA-256 `c48e7e206e658e12611882de2c3810e8c4756b9842848dfd26fe37509cb94ff8`)
- Current verdict: `D0 ROOT CAUSE CONFIRMED / REPAIR CONTENT READY / D2 PENDING / G3 HELD`
- Held: Windows G3 until the repair is an immutable locally accepted candidate; all ETABS/VBA, write-back, optimization, nightly work, publication, release, merge, cleanup, and professional approval
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | The export successor is locally complete. Desktop Excel blocked G3 before workbook open; diagnostic recovery confirmed a case-insensitive collision between input-table headers `D (mm)` and `d (mm)` |
| **Next** | Freeze and verify the maintained artifact-tool generator, unique `Effective d (mm)` header, manifest identity, and regression that rejects case-colliding table names |
| **After local closeout** | Push one stacked draft PR, run hosted checks, then send the exact head/tree/wheel/workbook/manifest identities to Windows for the no-recovery open gate and the full frozen G3 journey |
| **Held** | ETABS/VBA execution, real model access, analysis control, write-back, optimization, publication, release, and professional approval remain outside this packet |

## Confirmed workbook-open blocker and repair

The exact export candidate's blank-workbook guard passed on Windows. Opening an
unchanged disposable product workbook then produced Excel's content-recovery
prompt before any mapping or calculation. Recovery was accepted only on a
uniquely named diagnostic copy. Excel's saved repair log identifies
`/xl/tables/table1.xml`, and the repaired evidence copy renamed the ninth table
column from `d (mm)` to `d (mm)2`. The source table's seventh column was
`D (mm)`, confirming a case-insensitive duplicate-name violation.

The repair never promotes Excel's recovered file. A maintained
`@oai/artifact-tool` generator now rebuilds the six-sheet, five-table,
macro-free, formula-free workbook with `Effective d (mm)`, deterministic
relationship IDs, fixed ZIP timestamps, and a refreshed manifest. The service
retains the old alias for compatibility while the packaged workbook and tests
use the unique label.

## Frozen Windows G3 journey after successor closeout

1. Reuse the proven entitlement, certificate, restricted catalog, loopback,
   pane, and blank-workbook evidence; install only the exact repair wheel.
2. Verify the new workbook and manifest identities, then open one unchanged
   disposable copy. Require no recovery prompt, silent repair, or byte change.
3. Run the frozen PASS, FAIL, HOLD,
   blocked, and blank-row vectors with full reconciliation.
4. Export twice from one current snapshot and require identical bytes and
   complete mapping/results/passports/issues.
5. Edit one calculation-bearing input; require `STALE` and disabled export.
6. Recalculate, export twice, close/reopen, pass freshness, and export again;
   same-snapshot bytes and identities must match.
7. Capture G3 receipt and stop. Do not start ETABS.

## Required Reading

1. [Workbook-open repair evidence](../verification/e1-workbook-open-repair-evidence.md)
2. [Review-bundle export evidence](../verification/e1-review-bundle-export-evidence.md)
3. [Blank-workbook guard evidence](../verification/e1-blank-workbook-guard-evidence.md)
4. [Windows W0 evidence](../verification/e1-windows-w0-setup-evidence.md)
5. [E1 evidence](../verification/e1-excel-routine-workbench-v1-evidence.md)
6. [E1 execution plan](e1-excel-routine-workbench-v1-plan.md)
7. [Current task board](../TASKS.md)
8. [Git workflow single source](../git-automation/git-workflow-single-source.md)

Historical VBA/API reference files remain preserved at
`C:\CodexWork\reference\etabs-vba-handoff`. They are not part of this repair.
Keep macros disabled and do not run ETABS or legacy VBA until a separately
approved, bounded packet begins.
