---
task: E1-EXCEL-ROUTINE-WORKBENCH
title: Excel Routine Workbench V1 Execution Plan
status: active
owner: Main Agent
created: 2026-08-17
last_updated: 2026-08-17
doc_type: spec
---

# Excel Routine Workbench V1 Execution Plan

## 1. Outcome and start boundary

The next session starts Milestone M4, Packet E1, from merged Gravity Workflow
V1 commit `c127e4b2325fceb9adebf3d29d59e549f7ae4aa6` on the isolated branch
`codex/e1-excel-routine-workbench`.

E1 delivers one selected rectangular-beam table that uses the existing
canonical `design_beam_is456` calculation and
`StructuralResultEnvelopeV2`. Excel remains an input, review, and export
surface; it does not implement structural formulas or create a second safety
status.

This planning handoff makes no implementation change. The next session may
implement E1 without another ordinary approval. It must not start ETABS file
ingestion, live ETABS, model write-back, analysis, optimization, nightly work,
release publication, or professional-approval claims.

## 2. Accepted first user journey

1. The engineer opens the versioned macro-free workbook and selects the named
   rectangular-beam input table.
2. The Excel task pane shows the exact workbook, worksheet, table, row count,
   header mapping, units, depth basis, library version, and connection state.
3. The engineer reviews the mapping before calculation.
4. Each nonblank source row becomes exactly one ledger entry: `ACCEPTED`,
   `BLOCKED`, or `EXCLUDED` with a reason. Blank separators are counted and
   explicitly excluded; they are never silently dropped.
5. Accepted rows call the canonical beam service. The workbench displays the
   canonical intake, calculation, engineering, review, freshness, and overall
   statuses without translating an error string into `PASS`.
6. Every calculated row receives a calculation passport bound to its normalized
   input hash, result identity, library/content identity, workbook contract,
   and selected table.
7. Editing any calculation-bearing input, mapping, workbook contract, or engine
   identity changes the current hash and marks the retained result `STALE`.
8. Review/export produces a deterministic bundle containing the mapping,
   reconciled row ledger, structured results, passports, issues, and hashes.

## 3. Frozen `ExcelWorkbookContractV1`

### 3.1 Workbook and table identity

- contract: `structural-lib/excel-workbook-contract/v1`;
- template ID: `structural-lib-rectangular-beam-workbench`;
- template version: `1.0`;
- input worksheet: `Beam_Workbench`;
- named input table: `tbl_Beam_Workbench_V1`;
- metadata worksheet: `Workbook_Info`;
- mapping worksheet: `Mapping_Preview`;
- row-ledger worksheet: `Row_Ledger`;
- structured-result worksheet: `Results`;
- passport worksheet: `Passports`;
- trust mode: macro-free workbook plus a separately installed Office.js task
  pane; xlwings UDFs are not the E1 calculation or status path.

The contract records workbook/template ID and version, worksheet/table/range,
locale, decimal convention, Excel calculation mode, canonical unit system,
source hash, normalized-input hash, result hash, engine/capability identity,
review state, and freshness state.

### 3.2 Selected-table input columns

The mapping preview resolves these canonical fields:

| Field | Rule |
|---|---|
| `row_id` | Required, nonblank, unique within the table |
| `beam_id` | Required, nonblank user identity |
| `case_id` | Required, nonblank action-case identity |
| `mu_knm` | Required finite factored moment in kN m |
| `vu_kn` | Required finite factored shear in kN |
| `b_mm` | Required finite positive beam width in mm |
| `D_mm` | Required finite positive overall depth in mm |
| `depth_basis_mode` | Required: `EXPLICIT_D` or `DERIVED_FROM_BARS` |
| `d_mm` | Required only for `EXPLICIT_D`; blank for derived mode |
| `clear_cover_mm` | Required only for derived mode |
| `stirrup_dia_mm` | Required finite positive value |
| `tension_bar_dia_mm` | Required only for derived mode |
| `d_dash_mm` | Required for explicit-depth mode; derived from the complete bar basis otherwise |
| `asv_mm2` | Required finite positive stirrup-leg area |
| `fck_nmm2` | Required finite positive concrete strength |
| `fy_nmm2` | Required finite positive steel strength |

E1 fixes `units=IS456`, `tu_knm=0`, and serviceability disabled in versioned
workbook metadata. A row that requests torsion, serviceability, a flanged
section, or another component is a visible `HOLD/UNSUPPORTED_E1_SCOPE`, not an
implicit conversion. Optional shear inputs use explicit mode tokens such as
`AUTO_FROM_FLEXURE` rather than blank-cell meaning.

Headers may use contract-listed aliases, but aliases must be displayed in the
mapping preview. Unknown columns remain visible as excluded metadata. Duplicate
canonical mappings or missing required mappings block the batch.

### 3.3 Row accounting and status

The source table produces these exact counts:

`source_rows = accepted_rows + blocked_rows + excluded_rows`

Each ledger entry retains source row number, row ID when available, raw-cell
snapshot hash, mapping disposition, normalized input or blocking issues, and
result/passport identity when calculated. Invalid text, blank required cells,
non-finite numbers, duplicate IDs, and conflicting depth fields never become
zero, a default material, or a skipped row.

The workbench transports the canonical status axes unchanged:

- intake: `VALID`, `PARTIAL`, or `BLOCKED`;
- calculation: `NOT_EVALUATED`, `COMPLETED`, or `ERROR`;
- engineering: `NOT_EVALUATED`, `PASS`, `FAIL`, or `HOLD`;
- freshness: `CURRENT` or `STALE`;
- review: separate qualified-review status;
- overall: derived only by `derive_overall_status`.

Workbook review state (`NOT_REVIEWED`, `REVIEW_ACCEPTED`, or
`REVIEW_REJECTED`) is a separate human workflow label and cannot change the
canonical engineering result or imply professional approval.

## 4. Implementation map

The next session should confirm names against the folder indexes, then keep the
change within these boundaries:

1. Core contract types in `Python/structural_lib/core/` for workbook, mapping,
   row-ledger, passport, capability, and bundle identities. Core contains no
   Excel I/O and no IS 456 arithmetic.
2. `Python/structural_lib/services/excel_workbench.py` for strict table
   normalization, row reconciliation, canonical beam calls, passport creation,
   stale comparison, and deterministic review-bundle export.
3. A versioned macro-free workbook template/generator and golden fixtures in a
   dedicated maintained Excel artifact folder. The workbook contains labels,
   tables, validation, and display formulas only; structural results are written
   from canonical structured responses.
4. A bounded Office.js task-pane client in a dedicated `excel_addin/` package.
   It reads only the explicitly selected named table, previews the mapping, sends
   canonical requests to the local service, and writes structured results. It
   contains no structural formulas and no ETABS access.
5. A narrow local HTTP transport only if the existing FastAPI beam route cannot
   carry the complete table/ledger contract. Any new route wraps the same E1
   service and result types; it does not duplicate calculation logic.
6. The existing `services/excel_bridge.py` UDF module remains compatibility-only.
   E1 must replace its import-success-as-installation signal with an explicit
   capability result and must not use its mixed number/string UDF returns for
   row status.
7. Package metadata adds only the dependency/extra required for the exact
   workbook artifact path. Installation evidence must come from the built wheel,
   not a source checkout accidentally importing optional packages.

## 5. Root causes E1 must close

- `services/excel_bridge.py` currently substitutes no-op decorators when
  xlwings is absent, so an import can be mistaken for installed Excel support.
- Its UDFs mix numbers with strings such as `Error`, `Over-Reinforced`, and
  `Shear Failure`; a worksheet numeric test can therefore misclassify status.
- `services/excel_integration.py` silently defaults cover, compression steel,
  and status, derives effective depth from incomplete information, and prints
  and skips invalid CSV rows.
- That older integration is a detailing/DXF helper, not the canonical design
  result, row-ledger, passport, or stale-state workflow.
- The repository currently has no tracked, versioned Excel workbook/add-in
  artifact whose identity and installed journey can be verified.

E1 fixes these causes at the intake, identity, capability, and canonical-service
boundaries. It does not merely change the visible status formula.

## 6. Implementation sequence

1. Reconfirm source binding and inspect the maintained core/service/test indexes.
2. Add frozen contract types and direct serialization/hash tests.
3. Implement strict row mapping and reconciliation before workbook I/O.
4. Bind accepted rows to `design_beam_is456` and its canonical result envelope;
   add parity vectors against Python, CLI, and REST.
5. Add deterministic passports, stale detection, and review-bundle export.
6. Generate the macro-free workbook and golden reopen/recalculate fixtures.
7. Add the selected-table task pane and explicit installation/capability view.
8. Complete code, tests, docs, fixtures, packaging, and evidence before the one
   post-freeze verification batch.
9. Freeze records, refresh only affected indexes once, create the immutable
   candidate, run the read-only audit, and publish one PR for hosted validation.

## 7. Frozen validation selection

### Local and hosted software evidence

- contract serialization, hash determinism, alias/mapping, duplicate, blank,
  invalid-text, non-finite, depth-conflict, and count-reconciliation tests;
- canonical Python/CLI/REST/Excel parity for frozen `PASS`, `FAIL`, `HOLD`, and
  blocked rows;
- workbook golden generation, Open XML reopen, result write, edit-to-stale,
  recalculate-to-current, and deterministic export-bundle tests;
- Office.js selected-table mapping and safe writeback unit/component tests;
- built-wheel install smoke proving the exact package identity and explicit
  Excel capability response;
- affected architecture/import/type/style/documentation checks;
- `./run.sh check --quick` once after content freeze;
- normal commit hooks once; exact-head read-only session audit once;
- broad Python and full repository gates only at the cumulative M4 closeout or
  when an outcome-changing shared-surface failure requires them.

The next session must write the exact test paths and command lines into the E1
evidence record before the first consolidated batch. Failed checks are
root-caused, repaired together, and only failed/impact-mapped evidence is
repeated.

### Required real Excel matrix cell

The first supported cell is Windows 11 x64, Microsoft 365 Excel x64 current
stable channel, and the repository-supported x64 Python runtime. The receipt
must capture exact Windows build, Excel version/build/channel/bitness, task-pane
manifest hash, workbook hash, wheel hash, Python version, and library/content
identity.

Required journey: install exact wheel and task pane, open exact workbook, select
the named table, preview mapping, run frozen vectors, edit one input, observe
`STALE`, recalculate, export the review bundle, close/reopen, and prove identities
and statuses persist.

macOS, Linux, Open XML, jsdom, and hosted CI checks do not prove installed Excel.
If the Windows cell is unavailable, record `TO_VERIFY_WINDOWS`; the software
candidate may be locally complete, but Gate G3 and any installed-Excel product
claim remain held.

## 8. Gate G3 and stop rules

G3 passes only when:

- all source rows reconcile with zero silent drops or defaults;
- empty/error/string results cannot become `PASS`;
- Python, CLI, REST, and Excel match for frozen canonical vectors;
- edits and identity changes visibly stale retained results and block current
  export until recalculation;
- the exact installed wheel, task pane, workbook, engine, and result identities
  are recorded;
- the supported real Windows Excel journey passes once for the frozen candidate.

After G3, stop for an E1 acceptance review. T1 ETABS file/snapshot work begins in
its own fresh packet. E1 does not authorize T2 live ETABS or any write-back.
