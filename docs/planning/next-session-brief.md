# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-22
- Focus: freeze the blank-workbook guard repair, then rerun only the final W0 blank-workbook check on Windows
- Original E1 candidate: `codex/e1-excel-routine-workbench` at `ef5ee05c785904e1a01c2d09cc65649edc8745ab`
- Ordered predecessor: `codex/e1-w0-maintenance-plan` at `654e40b1370d098fca4d001146a030b9937536a8`
- Repair lane: `codex/e1-blank-workbook-guard`, stacked on the predecessor
- Evidence: `docs/verification/e1-blank-workbook-guard-evidence.md`
- Git handoff receipt: `docs/verification/e1-blank-workbook-guard-git-handoff-receipt.json` (`HOLD`; file SHA-256 `925d8017af0f24e21652502466301361eb0e43c9c87df7183891b6e928c456cb`)
- Current verdict: `LOCAL_REPAIR_VALIDATION_PASS / W0_REVALIDATION_PENDING`; G3 has not started
- Held: product-workbook G3 until W0 passes; all ETABS file/live work, write-back, optimization, nightly work, publication, release, and professional approval
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | Windows entitlement, candidate identity, wheel, restricted catalog, trusted HTTPS, loopback API, and add-in discovery pass; the original E1 pane exposed an eager missing-sheet lookup before its API call |
| **Next** | Commit and independently inspect the local repair, then send its exact immutable head to a fresh Windows task for the single blank-workbook revalidation |
| **After W0** | Run the frozen product-workbook G3 journey only if the unchanged repair head returns `READY_FOR_G3` |
| **Held** | ETABS/VBA execution, real model access, analysis control, write-back, optimization, publication, release, and professional approval remain outside this packet |

## Confirmed failure and repair

The original pane loaded from Excel's trusted `SHARED FOLDER` catalog but then
reported `WORKBOOK CONTRACT ERROR — The requested resource doesn't exist`.
Read-only source tracing proved that `registerInputChange()` eagerly called
`worksheets.getItem("Beam_Workbench")` in a blank workbook containing only
`Sheet1`. The next `context.sync()` therefore failed with the documented Office
`ItemNotFound` message before the definition API request. Missing document
settings were not the cause.

The repair:

- probes the exact sheet and table with `getItemOrNullObject()`;
- contacts the local definition endpoint but leaves a blank/wrong workbook
  read-only with `E1 WORKBOOK NOT OPEN`;
- disables every calculation control until the complete workbook surface,
  settings initialization, and event registration succeed;
- preserves genuine settings, permission, and Office sync errors with useful
  code/debug details;
- leaves Python calculations, REST contracts, workbook bytes, manifest, and
  structural-engineering behavior unchanged.

Local focused evidence passes 15 Office.js tests, JavaScript/manifest parsing,
and all 217 architecture files with zero violations.

## Frozen Windows W0 revalidation

Use a fresh Windows task and the exact immutable repair head. Reuse all passing
host, entitlement, share/catalog, certificate, wheel, workbook, and service
evidence; do not repeat setup.

1. Update only the catalog task-pane files to the exact repair head and verify
   their Git blob/content identities.
2. Start FastAPI and the trusted HTTPS pane on loopback only.
3. Open one unsaved blank workbook and load `Excel Routine Workbench V1` from
   `SHARED FOLDER`.
4. Require the connected library/workbook identity and the precise
   `E1 WORKBOOK NOT OPEN` hold.
5. Require Preview, Review, Run, and freshness controls to remain disabled.
6. Close the blank workbook without saving; require no save prompt, no orphan
   Excel process, and no listeners on ports 3000 or 8000.
7. Stop with exactly `READY_FOR_G3` or `SETUP_BLOCKED` and one compact receipt.

Do not open the packaged product workbook during W0 and do not start G3 in the
repair-validation task.

## Frozen G3 journey after `READY_FOR_G3`

1. Open the exact packaged workbook.
2. Select `tbl_Beam_Workbench_V1` and preview the visible mapping.
3. Run the frozen PASS, FAIL, HOLD, and blocked vectors.
4. Reconcile every source row with the ledger and canonical result/passport.
5. Edit one calculation-bearing input and observe `STALE`.
6. Recalculate to `CURRENT` and export the deterministic review bundle.
7. Close and reopen Excel; prove identities, results, and freshness persist.
8. Capture the receipt and stop. Do not start ETABS in the G3 task.

## Required Reading

1. [Blank-workbook guard evidence](../verification/e1-blank-workbook-guard-evidence.md)
2. [Windows W0 evidence](../verification/e1-windows-w0-setup-evidence.md)
3. [E1 evidence](../verification/e1-excel-routine-workbench-v1-evidence.md)
4. [E1 execution plan](e1-excel-routine-workbench-v1-plan.md)
5. [Current task board](../TASKS.md)
6. [Git workflow single source](../git-automation/git-workflow-single-source.md)

Historical VBA/API reference files remain preserved at
`C:\CodexWork\reference\etabs-vba-handoff`. They are not part of this repair.
Keep macros disabled and do not run ETABS or legacy VBA until a separately
approved, bounded packet begins.
