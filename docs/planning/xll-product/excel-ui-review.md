# Excel/XLL UI review and proposed workflow

Date: 2026-09-05. Status: revised overall product proposal; UI changes are not implemented.
Task: WP09-UI-REVIEW. The owner asked to inspect the Excel/XLL experience and
plan a simpler interface before continuing implementation.

The subsequent [ETABS workflow refinement](etabs-design-workflow.md) connects
this UI to capture, local design/search, copied-model reanalysis and savings.
The latest owner decision adds explicit connection/force/design/search/solver
steps, prefilled demo inputs and an overnight Auto Run. Heavy model/results data
stay in memory for v1; a small durable trial history supports morning review.
This replaces the earlier combined five-action proposal with grouped controls.

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

Loading the XLL creates no sheets. The first explicit Connect ETABS or Assumptions
command creates one small **Assumptions** sheet if absent. Design
creates/refreshes **Results** when needed; requested reports create only their
own outputs. Existing user sheets remain intact. There are no mandatory hidden
model, joint, force, operation or JSON-request sheets in the new workflow.

Keep actions grouped by workflow. Manual steps and Auto Run use the same services;
stage buttons do not require a click for every automated step.

| Group | Action | Behavior |
|---|---|---|
| Model | Connect ETABS | Attach to an identified running model, or launch installed ETABS and choose a model through its native Open dialog; fetch metadata/context, not forces |
| Model | Get Forces | Check required case results/currentness; if missing, prepare an owned analysis copy and analyse it, then acquire complete required actions |
| Design | Design | Validate inputs; design current sections, resolve actual bars/layers and every required member check; show Results |
| Design | Optimise | Search permitted section/bar alternatives per physical span/group; old-action resizing remains provisional |
| Design | Solver Check | Evaluate qualified local beam models and compare compatible actions; record unsupported or disagreement separately |
| Run | Update & Recheck | Apply an eligible proposal to an owned ETABS copy, analyse, reacquire and redesign; return a verified candidate or explicit failure |
| Run | Auto Run | Execute the same bounded loop unattended; show Stop/Pause while relevant |
| Review | Compare Runs | Per-run/per-frame history, best verified choice, quantities and check reasons; a compact menu contains reports/export/help |
| Review | Assumptions | Open the editable input sheet; no separate Apply button |

Use Excel's ordinary Save/Open for the workbook. Keep project menus, permanent
task panes, solver tolerances, polling settings and per-check switches out of the
routine interface. Auto Run asks only for meaningful scope, permitted changes
and duration/preset when not already bound; engineering inputs stay on Assumptions.
Display one compact model/scope/status
line, including **No model loaded**, **In memory**, **Needs input**,
**Provisional sizes**, **Recheck required** or **Verified for stated scope**.

Model details show filename/path, ETABS version, source/display units, result
status, stories and counts of beams, columns, joints and reconstructed spans.
Unknowns remain unknown. Acquire definitions/connectivity/axes/offsets in the
background with progress; any 3D view uses that same geometry. Native Open is an
interactive setup step completed before unattended work starts.

Results carry a physical span/group row, existing/proposed section, bar summary,
governing reason, quantity/cost difference and state. Select rows to scope an
update; absent a selection, the update summary names the eligible proposed set.
Show the exact target and changes once per run, honoring standing authorization;
do not request a click for each internal candidate. Group details/exceptions open
only when needed. Unsupported or unresolved groups show a reason instead of
silently joining an automatic update.

## One transparent Assumptions sheet

Use five columns: **Item | Value | Unit | Basis | State**. Organize rows into
project/model facts, design basis, practical design preferences and optional
rates. Normal worksheet cells support editing, tab navigation and copying.
Use clear read-only styling for source facts and derived requirements, editable
styling for supported overrides, and text labels for missing/conflicting inputs.

| Kind | Examples | Resolution rule |
|---|---|---|
| Imported facts | Member material assignment, verified strengths, model units, case definitions | Show verified ETABS source; never infer strength from a material name; proposed material changes are separate design overrides |
| Required project basis | Exposure, fire basis, architectural limits, seismic/system context when applicable | Use verified project/profile values; missing required facts remain visible |
| Named editable defaults | Display units, available section/bar catalogue, constant section per physical span, grouping preference | Identify office/product template and revision; retained values remain explicitly defaulted |
| Derived code requirements | Cover requirement, mandatory detailing limits and applicability | Show the governing basis; proposed inputs cannot bypass enforced checks |
| Project rates | Concrete, steel, formwork and supported labor/waste costs | Use sourced rates; if absent, quantities remain available but monetary savings are unavailable |

"Industry default" is not a universal source. Qualify any numeric engineering
preset against the named project/profile and supplier basis before use. Do not
describe demo grades, exposure, cover or seismic assumptions as real-project facts.
A proposed 50 mm section-size step in the UI is an editable product/office
catalogue preference, not a code minimum or a claim of universal practice.

Resolve explicit scoped overrides over named defaults only for fields that
permit overrides. Preserve imported facts separately and return effective values
with origin. Preserve member/material-specific assignments when the model uses
multiple grades; a global default must not replace heterogeneous source facts.
Blank never becomes zero. One bad field prevents accepting the
affected input snapshot. Design and Auto Run read and validate the sheet themselves;
no separate Apply/Validate ribbon action is needed. Edits immediately mark
dependent displayed results stale; a run uses its frozen input revision.
Mandatory checks and internal search tolerances are not routine user toggles.

### Prefilled development example

The owner explicitly authorizes initial demo/development inputs. The canonical
example is [demo-rc-beam-v1](demo-beam-preset.json), labelled **DEMO**. It includes
M25 concrete, Fe500 longitudinal/link steel, 30 mm nominal cover to outermost
reinforcement, mild exposure, a 60 minute fire assumption, 20 mm aggregate,
12/16/20/25/32 mm longitudinal choices, 8/10 mm links, two preferred layers,
12 m stock, and section choices in 50 mm increments. These are example inputs;
checks may reject them. They are not universal minima or project approval.

The example also supplies explicitly synthetic rates: INR 7,500/m3 concrete,
75/kg steel and 900/m2 formwork. No market quotation or construction saving is
claimed. Real imported assignments remain source facts; changing from demo to a
real project requires a resolved project basis, not automatic promotion of the
demo values. Retained defaults keep their origin; changing a cell never silently
removes the overall demo designation.

Demo Auto Run defaults are bounded at 8 hours, 20 ETABS analyses and 10,000 local
candidate evaluations, with a stop after three non-improving verified trials.
These are development limits, not performance or convergence promises. Required
solver comparison criteria come from qualified profiles, not an adjustable
accuracy slider.

The revised mockup illustrates populated assumptions, staged model/force actions
and a labelled simulation of trial history. It performs no engineering or ETABS
operation and starts no actual overnight job. It is not installed acceptance.

## Data and command ownership

- Preserve existing stable source/member identities and result provenance.
  Imported facts, user overrides and calculated outputs must remain distinct.
- Keep heavy model/joint/action data in memory for v1. Save only assumptions,
  requested outputs and small identity/state records in the workbook. A reopened
  workbook has no loaded force snapshot and requests Connect/Get Forces; saved results
  remain historical until the source and inputs are revalidated. A full durable
  project store and automatic cross-session optimization resume are later improvements.
  Auto Run does persist small per-run/per-frame/check records outside worksheets
  after each trial so morning review survives a workbook/process failure.
  Retain existing acquisition/transaction evidence obligations and legacy WP09
  compatibility; this removes the new runtime archive prerequisite, not evidence.
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

1. **Connection and assumptions:** one transparent sheet and demo preset, typed
   input mapping, exact model details and lightweight geometry; preserve legacy use.
2. **Forces and design:** current result checks and memory capture; baseline design,
   actual bar arrangements and all required checks. Missing-analysis preparation
   uses a separate owned-copy service once qualified; it is not a WP10 getter.
3. **Practical optimisation and solver:** bounded section-pair/bar
   alternatives, uniform physical spans, explicit group exceptions and Results.
   Qualify local solver applicability and discrepancy handling before using it.
4. **Update and overnight operation:** one copied-model transaction first, then
   a bounded orchestrator reusing all stage commands, durable trial history,
   safe pause/stop and actual unattended acceptance.
5. **Comparison and construction outputs:** complete per-frame/check records,
   quantities and supported exports from the same accepted result identities.
6. **Visual geometry:** add a section/span sketch when source axes,
   insertion and support-face mappings are resolved; assess a 3D viewer as a
   separate UI decision after the ribbon workflow works.

Replan WP10-05 around the declared memory-only v1 lifecycle and one Assumptions
sheet. Retain canonical identities, safe acquisition, workbook-write recovery,
freshness, performance and installed proof. A new durable heavy-data store is
not a prerequisite. Later coupled mutation retains its own durable transaction
records and original model; those records are not a workbook force database.

For each bounded implementation, run affected mapper/command checks, then
qualify the integrated frozen candidate in actual Excel. Acceptance must show:

- A new user can enter and check one beam without JSON editing.
- XLL load creates no sheets; first setup creates Assumptions only; design
  creates Results when needed. No hidden heavy-data sheets appear.
- An explicit output creates only the requested sheet; repeating it refreshes
  the same owned output. Existing unrelated sheets remain intact.
- Selected/all scope is explicit; a second workbook cannot receive the result.
- A missing input points to its assumption cell or member-detail field; rejection
  and cancellation are visible.
- Editing an input marks old results stale and prevents a current export.
- A failed write restores every declared controlled value; unrelated cells,
  formulas and formatting survive.
- Workbook save/reopen preserves assumptions and historical output. Heavy memory
  is released on close; design/update needs a newly validated source snapshot.
  A stale or mismatched binding never restores a current-result claim.
- Span/group section candidates satisfy every required station/member check;
  fixed-action size proposals cannot appear as ETABS-verified final designs.
- Connect alone reads no forces and never analyses. Get Forces reuses only
  complete current case results; missing analysis operates on an identified copy.
- Demo defaults are explicit and cannot masquerade as imported or approved data.
- Auto Run and manual stages share one implementation; per-trial records survive
  interruption, while lost heavy memory requires reacquisition. Solver mismatch,
  analysis failure and engineering failure have distinct outcomes.
- Excel at normal laptop scaling has readable headings, usable keyboard/tab
  navigation and no clipped essential fields or actions.
- Columns used for context never appear as passed beam designs, and pending
  import, search or report features never appear as completed capabilities.

Keep the original performance budgets and installed-artifact requirements.
This packet records a UI plan and review; it does not claim new installed
acceptance, publication or an implemented import command.
