# Next Session Briefing

## Latest handoff

<!-- HANDOFF:START -->
- Date: 2026-08-17
- Focus: start M4 / Packet E1 Excel Routine Workbench V1; no implementation was started in this handoff session
- Worktree: `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-e1-excel-workbench`
- Branch: `codex/e1-excel-routine-workbench`
- Merged base: `c127e4b2325fceb9adebf3d29d59e549f7ae4aa6` (B2 / PR #825)
- Execution plan: `docs/planning/e1-excel-routine-workbench-v1-plan.md`
- Git handoff receipt: `docs/verification/e1-excel-routine-workbench-git-handoff-receipt.json`
- Scope: one selected rectangular-beam Excel table, mapping preview, strict row ledger, canonical results, calculation passports, stale detection, review/export, and explicit installation/capability truth
- Exact next action: recover this branch with `./run.sh session brief --handoff`, confirm `source_bound=true`, then implement the E1 contract and strict row-mapping service before any workbook or task-pane UI
- Held: ETABS file/live integration, ETABS analysis, write-back, optimization, nightly work, release publication, and professional approval
<!-- HANDOFF:END -->

| State | Boundary |
|---|---|
| **Current** | A1, A2, B1, and B2 are merged through PR #825; exactly ten deprecated documents remain recoverably archived under `docs/_archive/2026-08` |
| **Next** | E1 software implementation on the isolated branch, followed by one consolidated focused verification batch |
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

## First implementation batch

1. Read the core/service/test folder indexes and inspect only the current
   `result_contract.py`, `beam_api.py`, `evidence.py`, `excel_bridge.py`, and
   `excel_integration.py` boundaries.
2. Add `ExcelWorkbookContractV1`, mapping, row-ledger, passport, capability, and
   bundle types without Excel I/O or IS 456 math in core.
3. Implement strict row normalization and count reconciliation in one service.
   No blank-to-zero conversion, calculation-bearing defaults, printed-and-skipped
   rows, or mixed string/numeric status.
4. Bind accepted rows to `design_beam_is456` and transport its
   `StructuralResultEnvelopeV2` unchanged.
5. Add deterministic stale/passport/review-bundle behavior before workbook or
   Office.js presentation work.
6. Complete the macro-free workbook, task pane, packaging, focused tests, docs,
   and evidence before the one post-freeze verification sequence.

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

## Known starting defects

- xlwings absence is hidden behind no-op decorators, so import success is not an
  installation capability proof.
- Excel UDFs return mixed numbers/status strings, while the generated status
  formula checks numeric cells.
- the legacy Excel/CSV integration silently defaults some calculation-bearing
  fields and skips invalid rows;
- no tracked workbook/task-pane artifact currently has a versioned identity or
  a real installed Excel acceptance receipt.

Close these root causes through the contract, intake, identity, and capability
boundaries. Do not patch only the visible worksheet formula.
