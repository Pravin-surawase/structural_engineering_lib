---
task: E1-EXCEL-ROUTINE-WORKBENCH
title: Excel Routine Workbench V1
status: active
owner: Main Agent
created: 2026-08-18
last_updated: 2026-08-18
doc_type: spec
---

# Excel Routine Workbench V1

## Outcome

Excel Routine Workbench V1 is one bounded, macro-free rectangular-beam workflow. Excel supplies typed cells and presents review evidence; all structural arithmetic runs through the existing `design_beam_is456` service and retains `canonical-beam-result/v1` plus `structural-result-envelope/v2` unchanged.

The software surface is available. Installed Windows Excel evidence remains `TO_VERIFY_WINDOWS`, so Gate G3 and any installed-Excel product claim remain held.

## Architecture and trust boundary

| Layer | Responsibility | Explicit non-responsibility |
|---|---|---|
| Core | Frozen workbook, selection, mapping, ledger, passport, retained-evidence, freshness, and definition models | Excel I/O and IS 456 arithmetic |
| Service | Strict header mapping, typed-cell intake, row reconciliation, canonical beam calls, passports, hashes, freshness, and deterministic review bundle | Office UI and duplicate beam math |
| FastAPI/CLI | Versioned transport for definition, preview, run, and freshness | Status reinterpretation |
| Workbook/task pane | Exact named-table read, mapping review, stale blocking, structured result writes, and local HTTPS transport | VBA, UDF calculation, ETABS access, or professional approval |

The workbook contains labels, tables, validations, conditional formatting, and sample inputs. It contains no structural-design formulas or VBA project. Unknown columns remain visible as excluded metadata. Populated known held-scope columns block calculation with a canonical `HOLD`; they never become an implicit supported input.

## Exact artifact and installed identity

The single workbook is package data at:

`Python/structural_lib/data/excel/outputs/e1-excel-routine-workbench/structural-lib-rectangular-beam-workbench-v1.xlsx`

Its sibling `workbook-manifest.json` freezes the file SHA-256, byte size, template/contract identity, visual review, trust mode, and Windows-evidence state. `get_excel_workbench_definition_v1`, `excel-v1 definition`, and `GET /api/v1/excel-workbench/v1/definition` read the installed resources and fail if the workbook bytes disagree with the manifest.

The workbook contract fixes:

- template `structural-lib-rectangular-beam-workbench` version `1.0`;
- worksheet/table `Beam_Workbench / tbl_Beam_Workbench_V1`;
- output sheets `Mapping_Preview`, `Row_Ledger`, `Results`, and `Passports`;
- unit system `IS456` and trust mode `MACRO_FREE_OFFICE_JS`;
- torsion and serviceability modes `DISABLED_E1`.

## Selected-table intake

The task pane reads the table header and data-body values as typed by Excel. It records workbook instance ID, template and table identity, first source row, locale, decimal convention, Excel calculation mode, unit system, and trust mode.

Required mapped fields are `row_id`, `beam_id`, `case_id`, `mu_knm`, `vu_kn`, `b_mm`, `D_mm`, `depth_basis_mode`, `d_mm`, `clear_cover_mm`, `stirrup_dia_mm`, `tension_bar_dia_mm`, `d_dash_mm`, `asv_mm2`, `fck_nmm2`, `fy_nmm2`, and `shear_basis_mode`.

Safety rules:

- numeric text is not converted to a number;
- required blanks, booleans, non-finite values, non-positive dimensions/materials, duplicate row IDs, and row-width mismatches are blocked;
- `EXPLICIT_D` requires `d_mm` and `d_dash_mm` and rejects a competing derived-depth basis;
- `DERIVED_FROM_BARS` requires clear cover plus stirrup and tension-bar diameters and rejects explicit depths;
- `AUTO_FROM_FLEXURE` is the only E1 shear-basis token;
- every source row becomes exactly one `ACCEPTED`, `BLOCKED`, or `EXCLUDED` ledger row.

The invariant is:

`source_rows = accepted_rows + blocked_rows + excluded_rows`

## Review, passports, and freshness

Preview produces the exact canonical mapping and a deterministic mapping hash. Run is disabled until that mapping is reviewed. The task pane also compares the current selected-table snapshot to the previewed snapshot immediately before calculation.

Each accepted row receives a calculation passport binding row, normalized input, calculation identity, canonical result, library version/content identity, workbook selection, and reviewed mapping. Complete ledgers, results, and passports persist in workbook tables.

Office document settings retain only the workbook instance ID, stale flag, and a four-hash freshness record: bundle, source table, mapping, and library content. Any edit on `Beam_Workbench` immediately clears mapping approval and marks retained evidence stale. The freshness endpoint recomputes the source/mapping/engine identities and returns `CURRENT` or `STALE` with explicit reasons.

## User surfaces

CLI:

```bash
python -m structural_lib excel-v1 definition
python -m structural_lib excel-v1 preview workbook-table.json
python -m structural_lib excel-v1 run workbook-table.json --mapping-hash HASH
```

REST:

- `GET /api/v1/excel-workbench/v1/definition`
- `POST /api/v1/excel-workbench/v1/mapping-preview`
- `POST /api/v1/excel-workbench/v1/run`
- `POST /api/v1/excel-workbench/v1/freshness`

The Office add-in manifest points to `https://localhost:3000/taskpane.html`. The local Node transport serves only an explicit static-file allowlist and proxies same-origin `/api/` requests to FastAPI on `127.0.0.1:8000`. Certificate and key paths are explicit environment inputs; no secret or certificate is stored in the repository. Microsoft requires an HTTPS `SourceLocation` for Office add-ins: <https://learn.microsoft.com/en-us/javascript/api/manifest/sourcelocation>.

## Capability truth and held scope

Software capability is `AVAILABLE`; installed Windows evidence is not inferred from imports, macOS, Open XML, Node tests, or hosted CI. The required Windows 11 x64 and Microsoft 365 Excel x64 journey remains the separate G3 cell defined in the execution plan.

E1 does not implement or claim:

- torsion, serviceability, flanged beams, or non-beam components;
- ETABS file import, live ETABS, analysis, or write-back;
- optimization, nightly work, release publication, or professional approval;
- VBA/macros or legacy mixed string/number UDF status.

All outputs remain `qualified_review_required=true` until the separate qualified engineering review is completed.

## Verification authority

The exact focused commands, artifact receipt, frozen vectors, issue/root-cause record, and current external hold are maintained in [E1 evidence](../verification/e1-excel-routine-workbench-v1-evidence.md). Open XML and browser-independent tests prove the software contract but do not prove installed Excel.
