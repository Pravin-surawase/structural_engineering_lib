---
task: E1-BLANK-WORKBOOK-GUARD
title: E1 Blank Workbook Guard Repair Evidence
status: active
owner: Main Agent
created: 2026-08-22
last_updated: 2026-08-22
doc_type: log
---

# E1 Blank Workbook Guard Repair Evidence

## Candidate boundary

- repair branch: `codex/e1-blank-workbook-guard`;
- stacked base: `codex/e1-w0-maintenance-plan` at
  `654e40b1370d098fca4d001146a030b9937536a8`;
- original E1 identity preserved: head
  `ef5ee05c785904e1a01c2d09cc65649edc8745ab`, tree
  `30d8eb7916c05fc69fd4074ae0ada2db2db201c1`;
- scope: Office.js blank-workbook startup only.

No structural calculation, API contract, workbook artifact, manifest, Python
package, ETABS/VBA, G3, release, or professional-approval behavior changes.

## Observed failure and root cause

The supported Windows host loaded the exact trusted add-in in a new blank
workbook. Its pane then reported `WORKBOOK CONTRACT ERROR — The requested
resource doesn't exist` before contacting the definition API.

Read-only diagnosis on the exact source showed:

1. `Office.onReady()` invokes `initialize()`.
2. The old startup created/saved the workbook ID before proving the E1 surface.
3. `registerInputChange()` called
   `worksheets.getItem("Beam_Workbench")` and then `context.sync()`.
4. The blank workbook contained only `Sheet1`; Office therefore returned the
   documented `ItemNotFound` message before the API request.

An absent document-setting key is not the cause. Office settings return no
value for an absent key, and the application can then create it. W0 did not
capture the JavaScript stack or Office `error.code`, so source-line binding is
supported by the exact message, source order, blank-workbook contents, and
absence of the subsequent API call.

The behavior is bound to Microsoft's maintained documentation for
[persisted add-in settings](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/persisting-add-in-state-and-settings),
[application-specific API errors](https://learn.microsoft.com/en-us/office/dev/add-ins/testing/application-specific-api-error-handling),
and
[worksheet collection lookup](https://learn.microsoft.com/en-us/javascript/api/excel/excel.worksheetcollection).
The manifest's ExcelApi 1.7 requirement is above the 1.4 requirement for
`getItemOrNullObject()`.

## Repair contract

- Probe `Beam_Workbench` and `tbl_Beam_Workbench_V1` with
  `getItemOrNullObject()` before writing document settings or registering an
  event handler.
- In a blank or wrong workbook, show the connected local library/workbook
  identity and a precise `E1 WORKBOOK NOT OPEN` hold.
- Keep Preview, Review, Run, and freshness controls disabled.
- Do not create/save the workbook ID and do not register worksheet events.
- In the complete packaged E1 workbook, retain the existing ID, persistence,
  stale, event, preview, and run behavior.
- Preserve real settings, permission, and `context.sync()` failures, including
  Office code and debug location when supplied.
- Distinguish workbook-surface, local-API, and workbook-initialization failures.

## Implementation and focused evidence

| Surface | Result |
|---|---|
| `excel_addin/taskpane-office.mjs` | Adds testable workbook-surface inspection, settings persistence, ID creation, strict event registration, and Office error details |
| `excel_addin/taskpane.mjs` | Reorders startup so blank-workbook inspection and API identity precede any workbook mutation; controls remain disabled until strict initialization completes |
| `excel_addin/serve.mjs` | Serves the new Office helper from the same trusted HTTPS origin; a dependency-map test prevents future local module imports from returning 404 |
| Office.js focused suite | PASS — 16 tests: 7 retained core cases, 8 blank/surface/settings/event cases, and 1 HTTPS module-map case |
| JavaScript and manifest parsing | PASS — four maintained modules parse; `manifest.xml` validates |
| Architecture boundaries | PASS — 217 files, zero violations |

Focused tests prove missing worksheet, missing table, complete surface,
missing/existing workbook ID, settings failure metadata, unexpected sync
failure propagation, and strict change-handler registration.

## First W2 exact-head result and consolidated repair

The first Windows revalidation used clean head
`a52233a29f3461e9931c500ee39cd72d6b20a3bc` and tree
`7bd259dfd30e8cfbfa6903410eae6aa66a4c5677`. File and manifest identities
matched, but `/taskpane-office.mjs` returned HTTP 404. The pane therefore
remained at `INITIALIZING`, made no definition request, and could not execute
the guarded startup path.

Confirmed root cause: `taskpane.mjs` imported the new module, while the static
file map in `serve.mjs` still listed only the original module graph. The
consolidated repair adds the missing same-origin route plus a focused test that
derives every local import from `taskpane.mjs` and requires a matching HTTPS
server-map entry.

Closing the blank workbook displayed a save prompt even though the repaired
module never executed. Inserting the add-in itself can dirty an unsaved
workbook, so the presence or absence of a save prompt is not accepted as
evidence of document-settings mutation. The workbook was discarded, Excel and
ETABS closed, services stopped, ports freed, and both Git worktrees remained
clean.

## Remaining Windows revalidation

Against the exact immutable repair head:

1. Reuse the installed entitlement, restricted SMB catalog, certificate, wheel,
   workbook, and local API identities already proven by W0.
2. Update only the trusted catalog and served add-in files to the exact repair
   head; require HTTP 200 for every local module before opening Excel.
3. Start the two loopback services and load the add-in in one unsaved blank
   workbook.
4. Require connected identity plus `E1 WORKBOOK NOT OPEN`, disabled controls,
   no generic contract error, and a completed definition API request.
5. Close and discard the unsaved blank workbook; record any prompt without
   treating it as settings evidence. Stop services and verify clean Git and no
   orphan processes.

G3 remains held until this narrow W0 revalidation returns `READY_FOR_G3`.
