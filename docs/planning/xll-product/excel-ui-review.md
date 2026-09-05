# Excel/XLL UI review and proposed workflow

Date: 2026-09-05. Status: reviewed proposal; product UI changes are not implemented.
Task: WP09-UI-REVIEW. The owner asked to inspect the Excel/XLL experience and
plan a simpler interface before continuing implementation.

## What exists

The WP09 XLL loads the native C# libraries through Excel-DNA. It provides pure
worksheet functions and commands for workbook validation, calculation,
evaluation of the declared current candidate, JSON calculation-package export
and diagnostics. Its runtime does not require React, Python or ETABS.
The [WP09 record](wp09-standalone-excel.md) retains actual installed acceptance;
that evidence qualifies its stated standalone scope.

The [ribbon source](../../../CSharp/src/StructuralEngineering.ExcelDna/StructAutomateRibbon.cs)
declares five buttons: Create / Validate, Calculate Workbook, Evaluate Current
Candidate, Export Packages, and Measure / Diagnose. ETABS import and a full
multi-member capture consumer remain future WP10 work.

On this review date, Excel was initially closed. The inspected sample
`CSharp/samples/StructAutomate-Standalone-Beam.xlsx` matched the retained WP09
input SHA-256 `2c9385900b2d9e1f5b66f315f1e7928d6e83f602d1c559653bec7bebdcaf5ae9`.
It was opened in real Excel, the overview and SA_Members sheets were inspected,
and it was closed without saving. The hash remained unchanged. The XLL was not
installed or loaded during this review; its ribbon was inspected in source.
Displayed cached version/formula cells do not establish a current loaded XLL.

## Main-process UI findings

1. **Normal inputs require technical JSON.** The sample exposes SA_Project,
   SA_Members and SA_Operations, including member/design/bar-path and operation
   request JSON. It lacks a normal beam-entry sheet with dimensions, explicit
   material basis, actions and actual reinforcement. A technically successful
   workbook command does not make this a usable daily engineering workflow.
2. **Ribbon responses are discarded.** Each callback ignores the string
   returned by WorkbookCommands. Its wrapper converts failures to JSON, so a
   ribbon click has no explicit user-facing completion or rejection result.
   Status-bar progress is cleared at completion. Preserve structured responses
   internally and add visible, persistent command feedback.
3. **The shipped overview is a sample, not a project start screen.** It
   exposes template/table names and still says Optimize, whereas the current
   ribbon correctly describes one-candidate evaluation. Create / Validate in
   an empty workbook seeds one frozen example. New project creation must make
   missing real inputs clear and keep an explicitly labelled example separate.
4. **Results and exports need an engineering presentation.** Internal results,
   freshness and receipts exist, but everyday users need a selected-member
   summary, missing-input list, current checks and readable quantities. The
   existing JSON package export must not be described as a finished printable
   report, PDF or fully formatted bar schedule.

These are outcome-changing workflow limitations. This review does not alter
the engineering kernel or revoke the bounded WP09 software acceptance.

## Owner decision: ribbon first, worksheets on demand

The owner explicitly requested one ribbon with no automatically created
StructAutomate worksheets. This supersedes the initial five-sheet UI proposal.
Excel's existing blank sheet and the user's own worksheets remain ordinary
Excel content. Loading the XLL, opening a project, selecting a beam or running
a check must not create product sheets, including hidden technical sheets.

Use the existing native C# engine behind a compact ribbon. Proposed menus:

| Menu | User purpose |
|---|---|
| Project | New, open and save; project identity, units and design basis in a small dialog |
| ETABS | Explicit live capture or saved-snapshot import when implemented; no automatic capture at startup |
| Beam | Select a beam and edit inputs/reinforcement in small native dialogs |
| Check | Check selected or all; show progress, cancellation and persistent completion or missing-input feedback |
| Outputs | Explicitly create or refresh a requested member list, input sheet, check results, BBS or quantities sheet; supported exports only |
| Help | Usage, settings and advanced diagnostics |

Selected-member execution and these dialogs are proposed routes, not current
ribbon capabilities. Keep routine completion compact; open detailed results
only when needed. A permanent task pane, embedded browser or 3D viewer is not
required. Use visible units: mm, kN, kNm and N/mm2, with explicit conversion to
existing kernel contracts, which can use N/Nmm internally.

An output command creates only its requested worksheet. Repeating it refreshes
the owned output by identity, without multiplying tabs or overwriting user
content. An optional editable input sheet must have a declared apply/validation
route; editing an output is not an implicit change to authoritative project data.
Fewer automatic sheets simplify the interface; startup time, memory and output
write performance still need measurement.

The conversation mockup is an illustrative proposal, not an Excel screenshot
or calculated engineering result. Its example data must not enter a real
project. The revised mockup starts with only Excel's ordinary Sheet1 and
demonstrates ribbon menus, a beam dialog and explicitly creating or refreshing
a check-results worksheet. It performs no engineering calculation.

## Data and command ownership

- Preserve existing stable source/member identities and result provenance.
  Imported facts, user overrides and calculated outputs must remain distinct.
- Keep the working project in C# memory. Design a versioned save/open project
  format outside worksheets, with explicit workbook/project association,
  recovery and source freshness. The exact format and lifecycle must be resolved
  before implementation; this review does not claim that storage exists.
  Preserve the existing WP09 controlled-table path for compatible legacy
  workbooks. New projects must not require hidden worksheet storage.
- Add a typed public-input mapper that generates the existing operation
  requests. No ordinary user should compose request JSON. Missing grades,
  cover, supports or reinforcement remain missing; sample defaults must never
  silently become real source facts.
- Public input/output tables need declared ownership and transaction coverage.
  Preserve the current preflight, preimage, bulk-write, readback and rollback
  guarantees. Do not assume the values-only adapter can restore arbitrary
  formulas, formatting or an undeclared worksheet layout.
- UI state includes Not checked, Missing input, Running, Current pass, Current
  fail, Stale, Unsupported and Cancelled. A completed import or command is not
  a passed design. Edits invalidate dependent displayed checks and exports.
- Bind commands and feedback to the initiating project and selected member;
  bind requested output writes to an explicit target workbook.
  Show progress and a cancellation action. Show completion, rejection and
  cancellation in a visible status area; routine success need not open a modal.
- Retain broad source geometry in the proposed shared C# model. A member-list
  worksheet, when requested, is a projection of that model. Column context does not
  imply a column design capability. Resolve the whole-model contract discussed
  with the owner before freezing the ETABS import UI and storage mapping.

## Proposed implementation order and acceptance

1. **Ribbon and project context:** resolve save/open/recovery and project-to-
   workbook binding; separate the current table-dependent commands from the
   project model and optional output projection. Preserve legacy workbook use.
2. **Manual beam first:** native input dialogs, explicit example mode, typed
   mapping, selected/all command feedback and readable results in a dialog.
   Create a check-results sheet only on request. Preserve result identities.
3. **ETABS source integration:** the agreed whole-model/snapshot contract,
   supported capture/import commands, provenance, source/override separation
   and stale-state handling. Existing WP10-05/05B/05C qualification remains
   required; this proposal is not a substitute for its acquisition proofs.
4. **Construction outputs:** bind actual detailed bars and verified geometry to
   readable quantities and supported export formats. Add other formats only
   with explicit implementation and evidence.
5. **Visual geometry later:** add a section/span sketch first when source axes,
   insertion and support-face mappings are resolved; assess a 3D viewer as a
   separate UI decision after the ribbon workflow works.

The earlier WP10-05 chunk/table storage proposal assumed mandatory snapshot
worksheets. Replan that persistence boundary before implementation: retain
canonical bytes, identities, recovery, freshness, performance and installed
acceptance, while removing the mandatory-sheet assumption. This is an
architectural dependency, not a ribbon-label-only change.

For each bounded implementation, run affected mapper/command checks, then
qualify the integrated frozen candidate in actual Excel. Acceptance must show:

- A new user can enter and check one beam without JSON editing.
- XLL load, project open, beam selection and checks create zero product sheets.
- An explicit output creates only the requested sheet; repeating it refreshes
  the same owned output. Existing unrelated sheets remain intact.
- Selected/all scope is explicit; a second workbook cannot receive the result.
- A missing input points to its dialog field or optional input cell; rejection
  and cancellation are visible.
- Editing an input marks old results stale and prevents a current export.
- A failed write restores every declared controlled value; unrelated cells,
  formulas and formatting survive.
- Project save/reopen reconstructs state with the existing runtime/result
  identities independently of optional output sheets; interrupted writes and
  stale or mismatched project/workbook bindings have explicit recovery behavior.
- Excel at normal laptop scaling has readable headings, usable keyboard/tab
  navigation and no clipped essential fields or actions.
- Columns used for context never appear as passed beam designs, and pending
  import, search or report features never appear as completed capabilities.

Keep the original performance budgets and installed-artifact requirements.
This packet records a UI plan and review; it does not claim new installed
acceptance, publication or an implemented import command.
