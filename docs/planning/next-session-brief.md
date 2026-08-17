# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-18
- Focus: retain the completed E1 software candidate and execute only the separate installed-Windows Excel G3 cell or hosted review closeout
- Worktree: `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-e1-excel-workbench`
- Branch: `codex/e1-excel-routine-workbench`
- Merged base: `c127e4b2325fceb9adebf3d29d59e549f7ae4aa6` (B2 / PR #825)
- Execution plan: `docs/planning/e1-excel-routine-workbench-v1-plan.md`
- Git handoff receipt: `docs/verification/e1-excel-routine-workbench-git-handoff-receipt.json`
- Scope completed locally: one selected rectangular-beam Excel table, mapping preview, strict row ledger, canonical results, calculation passports, stale detection, review/export, and explicit installed-artifact/capability truth
- Exact next action: use the immutable reviewed E1 head and execute the frozen Windows 11 x64 + Microsoft 365 Excel x64 G3 journey; do not edit the candidate merely to record hosted or external status
- Held: ETABS file/live integration, ETABS analysis, write-back, optimization, nightly work, release publication, and professional approval
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | E1 software candidate is complete locally on the B2 base with one exact workbook, Office.js task pane, Python/CLI/REST parity, passports, freshness, and source-free wheel proof |
| **Next** | Immutable hosted review and the separately controlled real Windows Excel G3 cell |
| **External evidence** | One real Windows 11 x64 + Microsoft 365 Excel x64 installed journey is mandatory for G3; until available, record `TO_VERIFY_WINDOWS` |
| **Held** | T1/T2 ETABS, O2-O4 write-back/nightly, tag/package publication, and professional approval |

## Required Reading

1. [E1 execution plan](e1-excel-routine-workbench-v1-plan.md)
2. [Current task board](../TASKS.md)
3. [Canonical result contract](../reference/canonical-result-contract.md)
4. [B2 gravity specification](../specs/building-gravity-v1.md)
5. [Git workflow single source](../git-automation/git-workflow-single-source.md)

The accepted master plan and Excel/ETABS annex remain external evidence:

- `/Users/pravinsurawase/.codex/attachments/6bca7c88-5347-4a9b-94c1-9f22d39636ac/integrated-structural-library-excel-etabs-master-plan.md`
- `/Users/pravinsurawase/.codex/attachments/6bca7c88-5347-4a9b-94c1-9f22d39636ac/excel-etabs-product-program-discovery-plan.md`

## Resume safely

Use the existing isolated E1 worktree; do not update the older primary `main`
or reuse the historical `codex/excel-product-planning` lane.

```bash
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib-e1-excel-workbench
./run.sh session brief --handoff
./run.sh session brief --agent orchestrator
./run.sh session start
./scripts/python_runtime.sh --diagnose
./scripts/python_runtime.sh scripts/git_state.py --json --worktrees
```

Require the E1 branch to be clean, operation-free, and source-bound. Preserve
all other worktrees and branches; do not reset, stash, clean, rebase, retire, or
delete them.

## Completed implementation batch

1. Inspected the core/service/test folder indexes and only the current
   `result_contract.py`, `beam_api.py`, `evidence.py`, `excel_bridge.py`, and
   `excel_integration.py` boundaries.
2. Added `ExcelWorkbookContractV1`, mapping, row-ledger, passport, capability, and
   bundle types without Excel I/O or IS 456 math in core.
3. Implemented strict row normalization and count reconciliation in one service.
   No blank-to-zero conversion, calculation-bearing defaults, printed-and-skipped
   rows, or mixed string/numeric status.
4. Bound accepted rows to `design_beam_is456` and transported its
   `StructuralResultEnvelopeV2` unchanged.
5. Added deterministic stale/passport/review-bundle behavior before workbook and
   Office.js presentation work.
6. Completed the macro-free workbook, task pane, packaging, focused tests,
   source-free wheel proof, docs, and evidence in the post-freeze sequence.

## Validation economy

- During implementation, run only a failing reproducer or narrow diagnostic
  needed to guide the change.
- After content freezes, run the exact E1 focused batch once, quick gate once,
  normal hooks once, and the exact-head session audit once.
- Run broad Python/full repository validation only at cumulative M4 closeout or
  when a shared outcome-changing failure requires it.
- Diagnose failures; repair related causes together; repeat only failed or
  impact-mapped evidence.
- Do not represent Open XML/jsdom/macOS evidence as installed Windows Excel.

## Closed starting defects

- The new E1 capability endpoint proves installed workbook/engine identity and
  does not infer support from the legacy xlwings import shim.
- E1 ignores legacy mixed number/status UDF output and writes only canonical
  structured statuses.
- E1 strict intake has no calculation-bearing defaults or printed-and-skipped
  rows.
- The tracked workbook and task pane now have versioned identities and
  source-free wheel evidence. Real installed Excel evidence remains held.

These causes were closed through the contract, intake, identity, and capability
boundaries rather than a visible worksheet formula patch.
