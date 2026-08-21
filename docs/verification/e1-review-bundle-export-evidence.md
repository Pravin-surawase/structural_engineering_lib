---
task: E1-REVIEW-BUNDLE-EXPORT
title: E1 Complete Review Bundle Export Evidence
status: active
owner: Main Agent
created: 2026-08-22
last_updated: 2026-08-22
doc_type: log
---

# E1 Complete Review Bundle Export Evidence

## Candidate boundary

- branch: `codex/e1-review-bundle-export`;
- exact stacked base: `codex/e1-blank-workbook-guard` at
  `514155b266af6dff3e30bf39ee28671c17345454`, tree
  `57e563909f84736a0d3b1a161d2e4d02ee4a4fe3`;
- predecessor PR: draft PR #828;
- Git handoff receipt:
  `docs/verification/e1-review-bundle-export-git-handoff-receipt.json`;
- scope: complete deterministic review-bundle service, REST, and installed-pane
  export only.

Workbook bytes, Office manifest, beam formulas, canonical calculation results,
ETABS/VBA, professional approval, release, merge, and cleanup remain unchanged
or held.

## G3 blocker and confirmed root cause

Windows W0 returned `READY_FOR_G3` on the exact predecessor. The frozen G3
preflight then stopped before creating or opening a disposable workbook because
the installed pane exposed only Preview, Review, Run, and Freshness, while the
REST router exposed only definition, mapping-preview, run, and freshness.

The existing deterministic Markdown renderer is service/CLI-only and contains
hashes, counts, and a status table. It omits the complete mapping, structured
results, calculation passports, raw ledger details, and issues required by the
frozen G3 contract. The root cause was treating renderer determinism as proof
of a complete pane-accessible export journey.

## Repair contract

1. Add `excel-review-bundle-export-request/v1` containing the exact current
   selected-table snapshot, four-hash retained evidence, and confirmed mapping
   hash.
2. Recompute mapping and freshness, regenerate the canonical result from the
   current snapshot, and require its result bundle hash to match retained
   evidence.
3. Return `excel-review-bundle/v1` containing `CURRENT` freshness plus the full
   `ExcelWorkbookRunResultV1`. Preserve `NOT_REVIEWED`,
   `qualified_review_required=true`, and every limitation.
4. Serialize sorted compact ASCII-safe JSON plus one LF. Expose exact file,
   logical review-bundle, and result-bundle SHA-256 identities and a
   deterministic filename.
5. Enable the pane Export control only after a current run or an explicit
   `CURRENT` reopen-time freshness check. Any edit, busy state, unavailable
   workbook, missing evidence, stale result, mapping mismatch, engine mismatch,
   result mismatch, response mismatch, or byte-hash mismatch blocks download.
6. Use same-origin POST/fetch, WebCrypto verification, and one temporary Blob
   download. Do not use the Office File API, which represents the workbook
   document rather than this separate evidence artifact.

## Frozen verification selection

| Evidence | Exact command |
|---|---|
| Python contract/service | `./scripts/python_runtime.sh -m pytest Python/tests/unit/test_excel_workbench_v1.py -q` |
| REST endpoint/OpenAPI semantics | `./scripts/python_runtime.sh -m pytest fastapi_app/tests/test_excel_workbench.py -q` |
| Office.js export and predecessor guards | `npm test --prefix excel_addin` |
| JavaScript/XML parse | `node --check excel_addin/taskpane-core.mjs && node --check excel_addin/taskpane-office.mjs && node --check excel_addin/taskpane.mjs && node --check excel_addin/serve.mjs && xmllint --noout excel_addin/manifest.xml` |
| Python format/lint/types | Affected-file Black, Ruff, and configured core/service mypy |
| Architecture/import/OpenAPI | Maintained architecture and import scripts, then the updated OpenAPI snapshot check |
| Source-free wheel | Build one exact wheel in a temporary directory, then run `scripts/verify_excel_workbench_artifact.py` on it |
| Documentation | Strict docs and link checks |
| Repository gate | `./run.sh check --quick` once after content freeze |
| Closeout | Normal hooks once, immutable commit, then read-only `session end` once |

Only failed or impact-mapped evidence may be repeated after an
outcome-changing repair. Broad Python/full repository gates remain reserved for
cumulative M4 closeout.

## Windows acceptance after local closeout

1. Install the exact new wheel and serve the exact new pane files; record
   head/tree/wheel/file identities.
2. Run one impact-mapped blank-workbook guard check because `taskpane.mjs`
   changed; do not repeat W0 entitlement/catalog setup.
3. Open the unchanged packaged workbook, preview/review mapping, and run the
   frozen PASS, FAIL, HOLD, blocked, and blank-row vectors.
4. Export twice from one current snapshot and require identical bytes, logical
   hashes, complete mapping/results/passports/issues, and the qualified-review
   boundary.
5. Edit a calculation-bearing cell and require visible `STALE` plus disabled
   export. Recalculate and require deterministic new-snapshot exports.
6. Close/reopen, require explicit `CURRENT` freshness, export again, and match
   the last same-snapshot bytes. Capture G3 receipt and stop; do not start
   ETABS.

## Current verdict

`FOCUSED LOCAL PASS / CLOSEOUT PENDING / G3 HELD`.

## Focused results through implementation freeze

| Evidence | Result |
|---|---|
| Python/REST/Open XML | PASS — 22 total focused cases; 21 passed in the first batch and the single repaired OpenAPI assertion passed impact-mapped |
| Office.js | PASS — 21 tests, including export eligibility, request identity, byte/hash rejection, single-download behavior, installed-pane wiring, and all blank-workbook guards |
| JavaScript/XML | PASS — four modules parse and `manifest.xml` validates |
| Style/types | PASS — affected Black and Ruff; configured mypy reports no issues in the core/service modules |
| Architecture/import | PASS — 217 files with zero boundary violations; 685 files and 4,732 imports with zero broken imports |
| OpenAPI | PASS — 89 endpoints and 434 schemas match the refreshed baseline; the fifth E1 route has typed `ExcelReviewBundleV1` JSON content |
| Source-free wheel | PASS — wheel SHA-256 `1cda121103d6e07653fdf0b97875cc9835493d7c31fb9c16f3075c7b5ac702b3`; installed library content `87ae4fbe362143186703fd1873a8882b92e0217523638db3f05f0af2ff3d57a5` |
| Installed bundle probe | PASS — 8,987 bytes; file SHA-256 `73ce28e6730bb403ce1564bf6e917db621d6fbdccd7fe2dbfe377846c90dac06`; logical hash `2f80a1cc7a2b7c7f47a22386b71b33ee2fecfec3e4dca1912dff6f466116a900`; structured result/passport present |
| Workbook package data | UNCHANGED — SHA-256 `497dd44d8dbe30ca8a6f3154b17d1d3598c517d96ffe0923e3ca44778450ac85`, 15,204 bytes |

The first focused batch found two integration issues. Declaring generic
`Response` as the route's decorator response class allowed exact runtime bytes
but suppressed typed OpenAPI response content. The route now retains its
`ExcelReviewBundleV1` response model for documentation while returning a raw
`Response` instance at runtime. A new import pair was also out of Ruff order,
which stopped the chained type check. Only the OpenAPI assertion/baseline and
affected style/type checks were repeated; Office.js, architecture, imports,
and unchanged behavior tests were not rerun.
