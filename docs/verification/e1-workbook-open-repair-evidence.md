---
task: E1-WORKBOOK-OPEN-REPAIR
title: E1 Desktop Excel Workbook-Open Repair Evidence
status: active
owner: Main Agent
created: 2026-08-22
last_updated: 2026-08-22
doc_type: log
---

# E1 Desktop Excel Workbook-Open Repair Evidence

## Candidate boundary

- repair branch: `codex/e1-workbook-open-repair`;
- exact immutable base: `codex/e1-review-bundle-export` at
  `98c60bc1f7c3899c28f662e82399cb25d80bbf26`, tree
  `3ee6772114aaf7979473ebfb35b76c27cfbb80a0`;
- pre-commit Git handoff receipt:
  `docs/verification/e1-workbook-open-repair-git-handoff-receipt.json`;
- scope: diagnose the exact packaged-workbook rejection, regenerate only the
  workbook source/artifact and compatible input-header mapping, and add the
  outcome-changing package regression;
- held: ETABS/VBA, structural formulas, canonical beam arithmetic, Office.js
  export behavior, release, merge, cleanup, and professional approval.

The immutable predecessor worktree and original workbook remain evidence. The
Excel-recovered copy is diagnosis evidence only and is never a supported
artifact or PASS candidate.

## Frozen diagnosis contract

1. Preserve the original workbook and its exact hash.
2. Create one uniquely named diagnostic copy outside OneDrive.
3. Permit Excel recovery only on that copy.
4. Retain every visible prompt, the repair log, hashes, sizes, and package
   before/after evidence.
5. Close the recovered copy without entering cells or treating it as product
   output; stop Excel/services and return the host clean.

## D0 diagnostic receipt

| Field | Result |
|---|---|
| Frozen source/input | 15,204 bytes; SHA-256 `497dd44d8dbe30ca8a6f3154b17d1d3598c517d96ffe0923e3ca44778450ac85` |
| Recovered evidence copy | 21,316 bytes; SHA-256 `52fb6a795f8d66c7e97df63c09211b7b13af660f01da8a16a4853b91d602ce20` |
| Preserved Excel repair log | SHA-256 `6929b41f3be09bdc26a91e2bd957fb7d75c3bdf2755047543c3ade2dea8ca476` |
| Exact Excel report | `Repaired Records: Table from /xl/tables/table1.xml part (Table).` |
| Recovery outcome | Evidence copy opened; no data cells were entered; recovered bytes are not a candidate |
| Windows closeout | Excel and ETABS closed; ports 3000/8000 free; no services; retained candidate worktrees clean |

## Confirmed file-level root cause

`tbl_Beam_Workbench_V1` in `/xl/tables/table1.xml` declared column 7 as
`D (mm)` and column 9 as `d (mm)`. Excel table-column names are compared
case-insensitively, so those names collide. Excel repaired the evidence copy by
renaming column 9 to `d (mm)2`. The `Beam_Workbench` worksheet cells and its
relationship to `table1.xml` corroborate the affected part.

ZIP integrity, all 23 source XML/relationship members, sheet/table presence,
and basic XML parsing had already passed. Therefore truncation and malformed XML
were excluded. The exact cause is the case-insensitive table-header collision;
the content-recovery prompt alone was not used to infer it. PR #829 did not
change workbook bytes and did not create this defect.

The process cause was an earlier artifact gate that proved frozen bytes,
ZIP/XML structure, sheets/tables, absence of formulas/macros, and rendered
appearance, but did not require a real desktop-Excel open before later export
work.

## Repair implementation

- Added maintained `scripts/generate_e1_workbook.mjs` using the approved
  spreadsheet artifact workflow.
- Recreated the exact six sheets, five named tables, labels, sample rows,
  validations, styles, macro-free boundary, and formula-free calculation
  boundary.
- Renamed only the effective-depth source header to `Effective d (mm)` in the
  input and mapping-preview tables; retained the service's legacy `d (mm)`
  alias for older callers.
- Normalized volatile relationship identifiers and ZIP timestamps after the
  artifact-tool export. Two clean generator runs produced byte-identical
  output.
- Added table-package checks that reject case-insensitive duplicate column
  names in both the source artifact and the workbook installed from a built
  wheel.

## Generated artifact receipt

| Field | Result |
|---|---|
| Path | `Python/structural_lib/data/excel/outputs/e1-excel-routine-workbench/structural-lib-rectangular-beam-workbench-v1.xlsx` |
| Size | 15,101 bytes |
| SHA-256 | `4cc492bfcbba456342c6358a8dcfe2749cafd723e9ee4fdaefa585f29e35ce63` |
| Determinism | PASS — two clean generator runs were byte-identical |
| Input table | `Beam_Workbench / tbl_Beam_Workbench_V1 / A4:Q7` |
| Unique depth labels | `D (mm)` and `Effective d (mm)` |
| Structural formulas | none |
| VBA/macros | none |
| Six-sheet visual review | PASS on 2026-08-22 |
| Installed desktop Excel | PASS — exact workbook opened without recovery or silent repair and retained its pre-open bytes |

## Frozen D2 verification

- focused workbook/Open XML/manifest, service, and REST tests;
- generator syntax plus one final six-sheet render/inspection;
- affected Python formatting/lint and documentation/link checks;
- one source-free wheel build and installed workbook/package probe;
- `./run.sh check --quick` exactly once after content freeze;
- normal commit hooks, one immutable candidate commit, source-bound/clean
  proof, and read-only session end.

Office.js, canonical calculation, architecture, import, and broad repository
suites remain unchanged and are not repeated for orientation. A failed or
impact-mapped check may be repaired and rerun once with its exact evidence.

## D2 results through implementation freeze

| Evidence | Result |
|---|---|
| Final spreadsheet inspection | PASS — all six sheets rendered and reviewed; no formulas or spreadsheet-error tokens; `D (mm)` and `Effective d (mm)` are visible and readable |
| Focused workbook/service/REST | PASS — 22 cases, including source artifact identity, exact tables/headers, formula/macro absence, mapping compatibility, and case-insensitive table-name rejection |
| Generator syntax | PASS — maintained Node runtime parses `scripts/generate_e1_workbook.mjs` |
| Python style | PASS — affected Black and Ruff checks; the verifier alone was formatted and only that failed style slice was repeated |
| Source-free wheel | PASS — SHA-256 `0943e277c3ae8cccc607fb43a26bc37a4a2362df41efaebca3401eefb202ba43` |
| Installed identity | PASS — library content `eafb869ad1f8c1e9c25112a89b6f722bf53331e8499b4e85140b91a8bce68ebf`; workbook SHA-256 `4cc492bfcbba456342c6358a8dcfe2749cafd723e9ee4fdaefa585f29e35ce63`, 15,101 bytes |
| Installed E1 probe | PASS — one accepted row, canonical overall `PASS`; 9,007-byte deterministic review bundle with file SHA-256 `e2920253815f26c7ee005fbc4703fca93fc43f87134965400e9cf427f4273551` and logical hash `cb4df94e331247ad0825fb9a4936fc5ca1dd62bd4b882778cf09aabb39882089` |

Documentation/index validation, the single quick gate, normal hooks, immutable
commit, and source-bound clean audit passed before publication. The later
cumulative integration closeout passed 6,508 Python tests, 31/31 repository
checks, and exact-head hosted PR Validation without changing the G3 candidate.

## D3 Windows acceptance

Windows validated exact head
`ede01ef4fb6182a27e3f176e872478304fb5f256`, tree
`bcc7fcf1b22212950ae530ca87c8bab907b6391f`, one source-bound wheel, the
15,101-byte packaged workbook, and the installed library identity. The Windows
wheel SHA-256 was
`a26d7c367e1bea509a4748e35ceae1ea70d9a952f515b0e761b80bed07d9c56f`;
the installed library content identity was
`eafb869ad1f8c1e9c25112a89b6f722bf53331e8499b4e85140b91a8bce68ebf`;
and the packaged workbook SHA-256 was
`4cc492bfcbba456342c6358a8dcfe2749cafd723e9ee4fdaefa585f29e35ce63`.

| Evidence | Result |
|---|---|
| Native workbook open | PASS — no recovery prompt, silent repair, new repair log, or close-without-save byte change |
| Frozen rows | PASS — `5 = 2 accepted + 2 blocked + 1 excluded`; residual zero |
| Required outcomes | derived-depth `PASS`; explicit-depth `FAIL`; numeric-text `BLOCKED`; blank row `EXCLUDED`; populated Torsion `HOLD` |
| Snapshot 1 | two supported pane downloads byte-identical; file SHA-256 `ea120eef575944db059d053f52d3a9389978af406b67e37d61edeaacc860ceb7` |
| Stale boundary | calculation-bearing edit immediately produced `STALE` and disabled Export |
| Snapshot 2 | two downloads byte-identical; file SHA-256 `9db5208a261d23d8c0ccb1104d552e34172502a8c19a01191017c39d5109a08c` |
| Reopen | explicit Freshness returned `CURRENT`; reopened export matched snapshot 2 byte-for-byte |
| Review boundary | `NOT_REVIEWED`; `qualified_review_required=true` |
| Host closeout | `DAY_CLOSE_CLEAN` — Excel/ETABS closed, services stopped, ports free, retained worktrees clean |

The supported pane Blob download completed. No CLI, Python, browser, or manual
copy substituted for the product export.

## Integration receipt

Cumulative PR #830 contained all predecessor E1 commits as ancestors and passed
the required local and hosted gates at the unchanged reviewed head. It merged
to `main` as squash commit
`b720119ea6a22a2b1963be0a0b9b300fca333d4a`. The merged tree is
`bcc7fcf1b22212950ae530ca87c8bab907b6391f`, exactly equal to the accepted
candidate tree. Superseded draft PRs #826-#829 were closed with preservation
comments; no branch, worktree, artifact, or evidence was deleted.

## Current verdict

`E1_COMPLETE / G3_PASS / MERGED / DAY_CLOSE_CLEAN`.
