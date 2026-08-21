---
task: E1-WINDOWS-W0-SETUP
title: E1 Windows W0 Setup and Handoff Evidence
status: active
owner: Main Agent
created: 2026-08-21
last_updated: 2026-08-22
doc_type: log
---

# E1 Windows W0 Setup and Handoff Evidence

## Verdict

`SETUP_BLOCKED` — the Windows host/catalog setup now passes, but the exact E1
candidate fails the required blank-workbook pane check and needs one software
repair before W0 can become `READY_FOR_G3`.

This is not `READY_FOR_G3` and is not `G3 PASS`. The E1 workbook was not
opened, the frozen G3 journey was not run, and no ETABS operation, repository
edit, publication, or release action occurred on the Windows host.

## Windows host receipt

| Item | Observed result |
|---|---|
| Codex host label | `Laptop-360-Pravin` |
| Windows user identity used by the share command | `LAPTOP-360-PRAV\P` |
| Excel | Microsoft 365 x64 Click-to-Run, Current Channel, `16.0.20228.20190` |
| Active Office entitlement | `O365HomePremRetail`, `User|Subscription`, `Licensed`, `Provisioned` |
| Earlier `OOB_GRACE` signal | Parallel legacy/grace SKU, not the active vNext Excel entitlement |
| Candidate branch/head | `codex/e1-excel-routine-workbench` / `ef5ee05c785904e1a01c2d09cc65649edc8745ab` |
| Candidate tree | `30d8eb7916c05fc69fd4074ae0ada2db2db201c1` |
| Candidate preservation | Clean before and after setup; no candidate file changed |
| Workbook SHA-256 | `497dd44d8dbe30ca8a6f3154b17d1d3598c517d96ffe0923e3ca44778450ac85` |
| Built wheel | `structural_lib_is456-0.23.1a2-py3-none-any.whl`; remote summary recorded SHA-256 `10a65cff…abf52` |
| Installed library content | `6b2d8f43c4fecd8eaa0c3ec692db13db4118ac04fe141458307e114421ab1764` |
| Add-in manifest SHA-256 | `5b38538e6ab6cb28855542065e5de2ed06bc3e583e3c76248b1b2c3d16099970` |
| Restricted catalog share | `\\localhost\E1W0Addin` resolves to `C:\CodexWork\office-addin-catalog`; read access only for `LAPTOP-360-PRAV\P`; no `Everyone` grant; access-based enumeration enabled |
| Excel trusted catalog | Existing catalog persisted with `Flags=1` (`Show in Menu`); `SHARED FOLDER` displayed the exact `Excel Routine Workbench V1` add-in |
| HTTPS | Trusted localhost certificate created outside Git; certificate verification passed |
| Service readiness | FastAPI and task-pane checks passed over loopback only; both services stopped cleanly |
| Final process state | Excel and ETABS closed; no listeners remained on ports 3000 or 8000 |

The Windows checkout materialized `excel_addin/manifest.xml` with CRLF line
endings because of Git's Windows configuration. The immutable LF Git blob
matched the frozen add-in hash. The catalog copy uses those exact LF Git bytes;
the clean checkout was not edited to hide the platform line-ending difference.

## Blank-workbook outcome and confirmed root cause

The blank workbook exposed the exact trusted add-in and loaded its pane over
HTTPS. Initialization then stopped before the definition API request with:

```text
WORKBOOK CONTRACT ERROR — The requested resource doesn't exist.
```

The source-bound Windows diagnosis traced startup from `Office.onReady()` to
`ensureWorkbookId()` and then `registerInputChange()`. The settings read is not
the cause: an absent `Office.Settings` key returns no value and can be created.
The failing batch instead calls
`worksheets.getItem("Beam_Workbench")` in a workbook containing only `Sheet1`;
the following `context.sync()` raises Office `ItemNotFound`, whose documented
message matches the observation. The failure occurs before the local API
definition request.

Runtime `error.code`/`debugInfo` was not captured during W0, so the exact source
line is bound by the observed message, workbook contents, source order, and
absence of an API request rather than a JavaScript stack. The repair uses
`getItemOrNullObject()` for the intentionally absent sheet/table path and keeps
unexpected Office errors strict. See the
[blank-workbook guard evidence](e1-blank-workbook-guard-evidence.md).

## Legacy VBA/API handoff on Windows

The historical reference packet is preserved at
`C:\CodexWork\reference\etabs-vba-handoff`. It was recovered from source
snapshot `b7b83dec6c1153d71c51dfc4be4297c36513dd1a`, immediately before commit
`ae5a07fea2751c080f750f99b057e8aeae9eaaae` removed the old VBA/Excel tree from
the main checkout.

| File | SHA-256 | Purpose |
|---|---|---|
| `01_Legacy_ETABS_2019_2021.zip` | `e927f57c9203a55bfe83b00a341eedcc31b6f34266a11322cc6b665d9f276b68` | Nine production-era ETABS modules for beams, columns, walls, reactions, combinations, scaling, and irregularity |
| `02_ETABS_Export_VBA.zip` | `28771d28de96142d3d53a0ab82c9d343ff801b8cae407d88b7b2f195ca750e8a` | ETABS exporters, experiments, guide, plan, and API notes |
| `03_Structural_Design_VBA.zip` | `3ab9719e68f9a8f901ab48040b26147ee0ff35cdd8fad24fe39d2b9897970acc` | Beam design, UDF, detailing, BBS, DXF, reporting, tests, and references |
| `04_Excel_Legacy_Workbooks.zip` | `1d9cc925db7af09cca7ff7f89b06bda97ecf7b68921283bf990a3bdf058f3d46` | Historical XLSM, XLAM, XLSX, template VBA, and snapshots |

The packet also contains `README.md`,
`API_AND_CONNECTION_QUICK_REFERENCE.md`, and `FETCH_ON_WINDOWS.ps1`. Local
ETABS COM uses `ETABSv1.Helper`, `CSI.ETABS.API.ETABSObject`, and the `ETABSv1`
type library; it needs no server URL, API key, password, or firewall port.

These archives are reference/parity material, not a validated ETABS 23 add-in.
Open old workbooks with macros disabled, use a copied disposable model outside
OneDrive, and do not run routines that unlock, analyze, redesign, change
sections/combinations, save, or exit ETABS. Live ETABS remains separately held.

## Disconnect and recovery record

### Visible symptom and impact

The Mac controller lost readable access to the remote Codex task while Windows
work was running. A later direct read returned `No Codex thread found` for the
recorded remote task ID. This interrupted live monitoring and continuation, but
did not interrupt the Windows setup commands or corrupt the candidate.

### Root cause and resolution

Root cause: `unconfirmed`. The evidence localizes the failure to the Codex
remote-control/task-visibility path: the Windows task continued to completion,
produced its final receipt, left Git clean, and shut down its services. A full
Windows build failure or candidate failure is therefore not supported by the
evidence. Network/app/remote-host synchronization is the working diagnosis,
not a confirmed cause.

Resolution: preserve and reuse the completed W0 evidence; do not rebuild or
repeat passing checks. The original remote task was recovered, the restricted
share and trusted catalog were completed, and a separate context-light Windows
task produced the read-only source diagnosis. New work uses a fresh task with
an exact handoff instead of extending the long setup history.

## Next controlled sequence

1. Freeze and review the stacked blank-workbook guard repair.
2. Reuse the passing Windows host/catalog evidence and rerun only the blank-
   workbook pane check against the exact repair head.
3. If W0 returns `READY_FOR_G3`, run G3 in a fresh task against that unchanged
   repair head; otherwise preserve the new blocker and stop.
4. Review the G3 receipt, then decide whether the stacked E1 PR sequence can
   leave draft and integrate.
5. Only after E1 integration, plan the bounded ETABS snapshot/CSV intake packet;
   live COM write-back, analysis control, and optimization remain held.
