---
task: E1-EXCEL-ROUTINE-WORKBENCH
title: Excel Routine Workbench V1 Evidence
status: active
owner: Main Agent
created: 2026-08-18
last_updated: 2026-08-22
doc_type: log
---

# Excel Routine Workbench V1 Evidence

## Candidate boundary

- branch: `codex/e1-excel-routine-workbench`;
- merged base: `c127e4b2325fceb9adebf3d29d59e549f7ae4aa6`;
- contract: `excel-workbook-contract/v1`;
- template: `structural-lib-rectangular-beam-workbench` version `1.0`;
- canonical function/result: `design_beam_is456` / `canonical-beam-result/v1`;
- workbook trust: `MACRO_FREE_OFFICE_JS`;
- installed Windows Excel evidence: `G3_BLOCKED_WORKBOOK_OPEN / D0_ROOT_CAUSE_CONFIRMED`.

ETABS file/live access, write-back, optimization, nightly execution, release publication, and professional approval are outside this candidate.

## Frozen verification selection

The following commands are frozen before the consolidated batch. A failed command is diagnosed once, repaired by root cause, and only its failed or impact-mapped evidence is repeated.

| Evidence | Exact command | Purpose |
|---|---|---|
| Python E1 contract/parity | `./scripts/python_runtime.sh -m pytest Python/tests/unit/test_excel_workbench_v1.py Python/tests/unit/test_excel_workbook_artifact.py -q` | Mapping, typed intake, counts, PASS/FAIL/HOLD/blocked vectors, passports, freshness, determinism, CLI parity, and workbook Open XML identity |
| REST semantics | `./scripts/python_runtime.sh -m pytest fastapi_app/tests/test_excel_workbench.py -q` | Definition, preview/run/freshness wrappers and rejected mapping |
| Office.js logic | `npm test --prefix excel_addin` | Exact table selection request, edit/snapshot invalidation, mapping hash, transport, reconciliation, and output projections |
| Office.js syntax/XML | `node --check excel_addin/taskpane-core.mjs && node --check excel_addin/taskpane.mjs && node --check excel_addin/serve.mjs && xmllint --noout excel_addin/manifest.xml` | Parse maintained JavaScript and manifest without requiring Excel |
| Architecture | `./scripts/python_runtime.sh scripts/check_architecture_boundaries.py` | Preserve Core to IS 456 to Services to UI direction |
| Imports | `./scripts/python_runtime.sh scripts/validate_imports.py` | Resolve maintained Python imports |
| Python style | `./scripts/python_runtime.sh -m black --check Python/structural_lib/core/excel_workbook.py Python/structural_lib/services/excel_workbench.py Python/structural_lib/__main__.py Python/tests/unit/test_excel_workbench_v1.py Python/tests/unit/test_excel_workbook_artifact.py fastapi_app/routers/excel_workbench.py fastapi_app/tests/test_excel_workbench.py` and the same path list with `-m ruff check` plus `fastapi_app/main.py` | Freeze affected Python formatting and lint |
| Python types | From `Python/`: `../scripts/python_runtime.sh -m mypy --config-file pyproject.toml structural_lib/core/excel_workbook.py structural_lib/services/excel_workbench.py` | Type-check the new core/service boundary in its configured package context |
| OpenAPI | `./scripts/python_runtime.sh scripts/check_openapi_snapshot.py` | Freeze four E1 endpoints and their schemas |
| CLI inventory/UAT | `./scripts/python_runtime.sh -m pytest Python/tests/test_release_uat.py -q` | Prove `excel-v1` is an owned advertised command |
| Built wheel | Temporary-directory `python -m build --wheel`, then `./scripts/python_runtime.sh scripts/verify_excel_workbench_artifact.py --wheel <exact-wheel>` | Prove the exact workbook/manifest and explicit capability are installed, not source-imported |
| Docs | `./scripts/python_runtime.sh scripts/check_links.py` and `./scripts/python_runtime.sh scripts/check_docs.py --all --strict` | Prove maintained links, metadata, frontmatter, and indexes |
| Consolidated gate | `./run.sh check --quick` | One post-freeze repository quick gate |
| Closeout | Normal hooks, immutable candidate commit, then `./run.sh session end --agent orchestrator` | One hook run and one exact-head read-only audit |

Broad Python and full repository validation are reserved for cumulative M4 closeout as required by the master plan; they are not repeated after ordinary E1 edits.

## Implemented evidence surfaces

1. Frozen Pydantic core contracts reject extra fields, non-finite numbers, invalid identities, inconsistent row counts, and unrecognized modes.
2. Strict service intake preserves all source rows, blocks numeric strings/default conflicts/duplicates, derives depth only from a complete explicit basis, and calls only `design_beam_is456` for accepted rows.
3. Passports bind row, normalized input, calculation, result, library content, selection, and mapping identities.
4. Four-hash retained evidence avoids storing a potentially large result bundle in Office settings while keeping reopen-time freshness verifiable.
5. The single workbook artifact is installed package data. Its manifest and definition endpoint fail on byte/hash/size mismatch.
6. The task pane clears approval on worksheet edits, requires exact preview snapshot plus mapping hash, and writes separate ledger/result/passport tables.
7. The original OpenAPI baseline contains 88 endpoints and 432 schemas after
   adding the first four E1 endpoints. The authorized export successor adds a
   fifth typed E1 endpoint and records its new baseline separately.

## Consolidated focused results

| Evidence | Result |
|---|---|
| Python workbook/service/CLI/Open XML | PASS — 13 tests |
| REST | PASS — 3 tests |
| Office.js | PASS — 7 tests; three maintained modules and manifest parse |
| Advertised CLI UAT | PASS — 14-command inventory includes `excel-v1` |
| Architecture/import | PASS — 217 files with zero layer violations; 685 files and 4,729 imports with zero broken imports |
| OpenAPI | PASS — 88 endpoints and 432 schemas match baseline |
| Style/types | PASS — Black, Ruff, and configured mypy for both new modules |
| Source-free wheel | PASS — wheel `c4c5d09872d080ac5b1bee9e72c5af87e52df65c893358a15cc478cc4b5753b9`; installed library content `6b2d8f43c4fecd8eaa0c3ec692db13db4118ac04fe141458307e114421ab1764`; installed row result `PASS` |

The first architecture/import selections used nonexistent guessed script names,
and the first mypy command used the wrong package workdir. The maintained
automation registry identified the exact commands. Corrected mypy then exposed
and drove repairs to literal constant typing, request-schema inheritance, and
typed result construction. Only those failed/impact-mapped checks and affected
Python/REST/OpenAPI/wheel evidence were repeated; all pass.

## Workbook artifact receipt

| Field | Value |
|---|---|
| Path | `Python/structural_lib/data/excel/outputs/e1-excel-routine-workbench/structural-lib-rectangular-beam-workbench-v1.xlsx` |
| Original SHA-256 | `497dd44d8dbe30ca8a6f3154b17d1d3598c517d96ffe0923e3ca44778450ac85` |
| Repair candidate SHA-256 | `4cc492bfcbba456342c6358a8dcfe2749cafd723e9ee4fdaefa585f29e35ce63` |
| Repair candidate size | `15101` bytes |
| Sheets | `Workbook_Info`, `Beam_Workbench`, `Mapping_Preview`, `Row_Ledger`, `Results`, `Passports` |
| Input table | `Beam_Workbench / tbl_Beam_Workbench_V1 / A4:Q7`; distinct `D (mm)` and `Effective d (mm)` headers |
| Structural formulas | none |
| VBA/macros | none |
| Visual review | PASS on all six regenerated sheets, 2026-08-22 |
| Installed Windows Excel | `G3_BLOCKED_WORKBOOK_OPEN / D0_ROOT_CAUSE_CONFIRMED`; see [workbook-open repair evidence](e1-workbook-open-repair-evidence.md) |

## Focused implementation diagnostics already completed

- the initial header mapper incorrectly case-folded `D` and `d`, causing seven of ten new service vectors to fail; exact depth aliases now preserve structural notation and the focused file passed;
- the initial REST test requested a nonexistent local `unwrap` fixture; it now imports the maintained helper and all three endpoint vectors passed;
- the first workbook placeholder populated two dropdown cells, so it was not truly blank; the final artifact leaves all 17 cells blank and preserves dropdown validation;
- the first artifact builder path landed in the primary checkout because the patch helper used the session root; only that untracked temporary file/link was safely removed and the primary checkout was reverified clean;
- the first visual render exposed a 204-row used range and cramped workflow text; the final six-sheet render is compact and readable.

These diagnostics are recorded separately from the passing consolidated batch.

## Current verdict

`WORKBOOK-OPEN REPAIR CONTENT READY / D2 PENDING / G3 HELD`.

The focused batch, source-free wheel proof, immutable candidate closeout, and
hosted PR #826 checks pass. Windows W0 subsequently proved the active Microsoft
365 entitlement, exact clean candidate, isolated installed wheel identity,
restricted trusted catalog, localhost HTTPS, and loopback service readiness.
The exact add-in loaded in a blank workbook but exposed a pre-API
`ItemNotFound` defect in eager `Beam_Workbench` event registration. The stacked
[blank-workbook guard repair](e1-blank-workbook-guard-evidence.md) was then
repaired for its missing static-module route and returned `READY_FOR_G3` on
Windows at exact head `514155b2`.

The authorized [export successor](e1-review-bundle-export-evidence.md) closes
the missing source-to-pane review-bundle path. The next frozen Windows journey
then reached the unchanged product workbook and stopped at Excel's content-
recovery prompt before mapping or calculation. Recovery was accepted only on a
diagnostic copy. Excel's retained repair log identifies `table1.xml`, and its
repaired evidence copy changed the ninth table header from `d (mm)` to
`d (mm)2`; the seventh was `D (mm)`. The exact file-level cause is therefore a
case-insensitive duplicate table-column name, not a copy failure, generic
workbook corruption, or export-code change.

The [workbook-open repair](e1-workbook-open-repair-evidence.md) regenerates the
same bounded artifact from maintained source with `Effective d (mm)`, preserves
the legacy service alias, and adds a package regression that rejects case-
colliding table columns. Its deterministic local artifact must still pass the
consolidated D2 checks and the exact installed-Excel D3 journey.
