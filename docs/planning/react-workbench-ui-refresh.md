# StructLib React workbench UI refresh plan

**Type:** Plan
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-11-22
**Last Updated:** 2026-11-22
**Related Tasks:** None
**Abstract:** Scope, acceptance criteria, and implementation sequence for the independent React browser workbench refresh.

---

## Scope

On 22 November 2026 the owner separated the React workbench refresh from the 0.31.1 slab correction. This branch starts with the UI plan. Its release version will be selected separately. The slab fix stays in [draft PR #1126](https://github.com/Pravin-surawase/structural_engineering_lib/pull/1126).

The update covers the browser app, from first entry through completion,
review and existing exports. Use the current React, Tailwind and Dockview
components as the starting point. Define shared styles and patterns for
layout, labels and units, fields, buttons, tables, focus, feedback and
engineering status. Keep route identities, API and export contracts, stored
projects, feature flags and engineering scope compatible with 0.31.0. The
app uses the library and service as the calculation and validation owners.
[Route inventory](../../react_app/src/App.tsx) ·
[Layout and theme](../../react_app/src/index.css) ·
[Result and import boundaries](pre-release-input-safety-and-professional-readiness-plan.md)

## S1 proposed design and workflow decisions

### App shell and workbench

- Keep **Open workbench** as the landing page’s primary action. Give the workbench
  a compact **Design tools** list for Quick Beam, Slabs, Rectangular Column,
  Isolated Footing and Building Gravity, each with a short scope description.
  Make **Projects** the entry for starting an import or resuming the last local
  workspace. Show the available project name, member count and last stage. The
  empty state offers **New project** and names the upload step that follows.
- Use the same **Workbench** and **Projects** destination labels and active state
  in the desktop header and mobile dock. Put **Settings** in the app header at
  both widths. Use the active tool or project stage as the narrow-screen title
  and link only to routable parents. Keep the existing canonical and legacy URLs,
  route guards, query parameters and Back behavior. Include the column and
  enabled automation routes in the Workbench active state.
- Reuse `WorkbenchShell`, `WorkbenchHeader` and `WorkbenchPanel`. Keep the dark
  Tailwind and Dockview base with a single blue primary action per view, clear
  focus, and meaning conveyed by status text. On wide screens, put the editing
  surface on the left and the result summary or selected member on the right.
  On narrow screens, use one scrollable page with inputs, run action, then
  current result and outputs. Reserve space for the mobile dock. Keep horizontal
  scrolling inside tables or technical diagrams. Use the existing viewport and
  Dockview where they serve the 3D and member-review tasks.
- Keep Settings as a drawer for the configured API endpoint, app version and
  design standard. Use measured connection status where available. Move focus
  inside on open, support Escape, and return focus to the opener on close.

[Navigation and stage definitions](../../react_app/src/app/navigation.ts) ·
[Route guards](../../react_app/src/app/RouteGuards.tsx) ·
[Workbench components](../../react_app/src/components/workbench)

### Projects and imported-beam results

| Step | What the screen shows and does |
| --- | --- |
| Start or resume | Show the last local workspace and its actual saved stage after restore. Distinguish restoring, unsaved, saving, saved on this device, and save or restore error. Use a conflict-specific explanation when the existing persistence flow identifies a newer revision. Keep the existing conflict handling, project ID and saved snapshot format. |
| Import | Offer **Single CSV** and **Paired CSV (Geometry + Forces)**, with format and units beside the relevant file inputs. Generic CSV needs a finite positive span in a recognized unit-bearing column such as `Span (mm)` or `Span_m`. Show detected format, accepted members and returned warnings in the preview. For a blocked file, show the returned file/row/field where available and the correction the user can make. Read the structured `422` detail from the existing import response, which the current client can render as a generic object string. Keep a failed import at the file step. |
| Review and Design | Use one stage indicator for **Import → Review → Design → Results**, driven by the existing guard and workspace state. Review shows members, units and editable inputs before running. Design shows progress and member counts by disposition. An interruption preserves settled rows and resumes an unfinished row as **Not evaluated** when restored from disk. |
| Results | Show counts for current passing, failed, held or blocked, and unevaluated or stale members, with a way to inspect each held member. Distinguish a settled batch from a fully checked project. Use the existing current checked-layout gate for project export and BOQ, and the existing member gate for individual outputs. Show the held count and reason next to unavailable actions. |

[Import client](../../react_app/src/hooks/useCSVImport.ts) ·
[Import response](../../fastapi_app/routers/imports.py) ·
[Workspace persistence](../../react_app/src/workspace/WorkspacePersistenceBridge.tsx) ·
[Project result eligibility](../../react_app/src/workspace/resultRecords.ts)

### Calculators, shared controls and flagged workflows

Put units on labelled controls and result columns. Group geometry, loads,
materials and required review evidence under their own headings. Show field
errors next to the input and a short summary at submission when several fields
need correction. Announce load/save/run changes in place and keep actionable
errors available after any toast closes. Show request state, result freshness,
engineering disposition and qualified-review requirements as separate facts
where the feature provides them. Use feature-owned evidence and eligibility
for each download. Show the governing check before detailed tables, drawings
and evidence, with a visible reason beside unavailable actions.

| Surface | First layout and output decision |
| --- | --- |
| Quick beam | Present geometry, actions, materials and detailing together, with one primary **Run design** action and the existing auto-design control. Put the governing result and export state before section/reinforcement and 3D controls. `/workbench/quick` uses catalogue inputs by default and manual inputs when `VITE_CATALOGUE_QUICK_ENABLED=false`. The explicit manual URL and catalogue alias keep their current behavior. Use the existing per-format gates for checked BBS, DXF and reports, including combined-case restrictions. |
| Slabs | Show simply supported, continuous and two-way modes with their existing inputs, strip widths and units. Put the returned coefficient table/case and any interpolation next to the governing checks. Show a failed reinforcement check as a returned result and rejected input as an intake error. Keep preset review references visibly tied to the untouched example. Editing leaves any previous response stale and applies the existing review-evidence invalidation. The passport is evidence for a current response, including a returned failure or hold. |
| Rectangular column | Pair the supplied-member form with the governing result, separate adequacy and detailing checks, and the existing clause and request/revision references. Export the review packet only for a current record that passes both checks. Keep the qualified-review requirement visible with a passing result. |
| Concentric isolated footing | Group service and factored loads separately and put approval controls with the soil, supporting-area and optional detailing evidence they affect. Show aggregate, calculation and detailing dispositions separately, including retained stale evidence and detailing holds. This screen provides on-screen evidence. |
| Building gravity V1 | Keep the JSON request and **Load example** entry. Lead with aggregate disposition, governing issue and load reconciliation, then show components, transferred actions and evidence identity. Tie the displayed result to the submitted request. If the request text changes during or after the run, present that bundle as a previous result. Keep its immutable book downloadable under the existing returned-bundle rule, including returned `HOLD` and mixed component results. |
| Workflow composer | Keep the existing fixed template, bindings, validation, run, review stop and cancellation. Show **Validate** and **Run workflow** with persistent step results and a clear next action at a review stop. Keep local draft save/load and definition JSON distinct from project persistence and calculation outputs. The entry and route remain available only in development with `VITE_WORKFLOW_RUNNER_ENABLED=true`; check the production build with the flag set as well. |

[Quick beam view](../../react_app/src/components/design/DesignView.tsx) ·
[Slab workbench](../../react_app/src/features/slabs/SlabWorkbenchPage.tsx) ·
[Column review](../../react_app/src/features/columns/ColumnResultReviewer.tsx) ·
[Footing workbench](../../react_app/src/features/footing/ConcentricIsolatedFootingPage.tsx) ·
[Gravity review](../../react_app/src/features/building-gravity/BuildingGravityReviewPage.tsx) ·
[Workflow composer](../../react_app/src/features/automation/WorkflowComposerPage.tsx)

### Baseline to capture before implementation

Capture current first-use, editable input, blocked or failed, and result screens
at **1440 × 900** and **390 × 844**. Check core actions at **320 CSS px**,
including keyboard reachability, dialog focus return, reduced motion, and no
page-wide horizontal scrolling. Record the candidate base, flag settings,
fixture, displayed disposition, and expected request and output behavior for
each replay. The following existing cases are anchors for the baseline.

| Replay | Evidence to pin |
| --- | --- |
| Navigation and resume | Verify direct, legacy and guarded URLs, preserved query strings, Back, and restore after reload. Reload a saved mixed batch with settled and unfinished members, account for every member, and confirm the project export stays held. [Route tests](../../react_app/src/app/__tests__/RouteGuards.test.tsx) · [Persistence tests](../../react_app/src/workspace/__tests__/persistence.test.ts) · [Batch tests](../../react_app/src/hooks/__tests__/useBatchDesign.test.ts) |
| Generic and ETABS import | Use the combined Generic fixture with `d_mm=470`, the paired ETABS matched-ID fixture, and a Generic file with an invalid span in its second data row. Assert that the valid files reach review with their real member count and that the invalid file shows the field and source row with no stage advance. [Import transport fixtures](../../fastapi_app/tests/test_imports_formats.py) · [Strict-span fixtures](../../Python/tests/unit/test_generic_span.py) |
| Quick beam and slabs | Run one case through both quick input modes, then edit an input and check the output lock. Include an invalid quick input and one unchanged slab request per mode, a returned inadequate-reinforcement result, rejected input and stale passport after editing. [Quick tests](../../react_app/src/components/__tests__/DesignView.test.tsx) · [Slab tests](../../react_app/src/features/slabs/SlabWorkbenchPage.test.tsx) |
| Column, footing and gravity | Replay passing and failing column checks and the stale packet lock, footing blocked approvals and returned detailing `HOLD`, and gravity malformed JSON plus a bundle with mixed dispositions and its calculation book. [Column tests](../../react_app/src/features/columns/__tests__/ColumnReviewWorkspace.test.tsx) · [Footing tests](../../react_app/src/features/footing/__tests__/ConcentricIsolatedFootingPage.test.tsx) · [Gravity tests](../../react_app/src/features/building-gravity/BuildingGravityReviewPage.test.tsx) |
| Workflow composer | Verify entry and route availability across the flag states. Validate and run the existing beam template to its review stop, cancel one active request, and round-trip the local draft. [Composer tests](../../react_app/src/features/automation/__tests__/WorkflowComposerPage.test.tsx) · [Draft tests](../../react_app/src/features/automation/__tests__/draft.test.ts) |

This draft records source-reviewed decisions and acceptance targets. Browser
captures and fixture replays are pending.

## Journeys and acceptance

| Surface | Planned change | Acceptance evidence |
| --- | --- | --- |
| Home, Workbench, project list and settings | Use consistent navigation in the desktop top bar and mobile dock. Show project entry and settings plus the next action in empty and loading states. | Direct links, refresh, back navigation, old route redirects and saved-project recovery work. A keyboard user can start and resume a project. |
| Quick beam design and catalogue | Group input, units and validation, the check result, section and reinforcement views, and existing outputs. Cover manual and catalogue paths. | A supported beam can be entered, checked and exported. Invalid data maps to visible field errors. Existing geometry and 3D controls stay usable. |
| Projects and import through results | Make import, review, design and results easy to follow. Show combined and paired CSV guidance, source-row errors, member counts and save or restore feedback. | Valid Generic and supported ETABS examples reach the appropriate stage. An invalid Generic span shows its row and field. Mixed rows and interrupted work keep their actual states. Guarded deep links, autosave, recovery and save conflicts work with existing projects. |
| Slab workbench | Use common input and result patterns for simply supported, continuous and two-way slabs. Surface the strip width, coefficient source, units and governing checks carried by the existing built-in requests. | Exercise the supported browser flows and show a failed reinforcement check separately from rejected input. Confirm requests and units match the existing HTTP route. Freeze evidence for each supported mode on the UI candidate's actual base. |
| Rectangular column, concentric isolated footing and building gravity | Use the same input, review, result and evidence patterns within each supported route. Expose the governing checks, on-screen evidence and available downloads. | Replay one valid journey per workbench and the applicable blocked, failure or review-held controls. Each evidence reference or download still reaches its original output. |
| Workflow composer and shared 3D/result surfaces | Apply the common layout where the workflow flag permits access. Align shared tables, drawers, dialogs, viewport actions and download feedback. | The flag controls availability. A supported workflow and existing result controls work. Focus returns after dialogs and status feedback remains readable with reduced motion. |

All journeys must show loading, empty, validation and request-error states
where applicable. Status text must distinguish intake, calculation,
engineering `PASS` / `FAIL` / `HOLD`, and qualified review. A completed
calculation, partial batch or missing result cannot be displayed as an
accepted design. Mark results stale after input changes and apply existing
export locks, with a reason shown when an action is unavailable. Use readable
units, visible keyboard focus, text with status colour, and layouts that
keep primary actions and results reachable
on narrow screens. Allow contained scrolling for dense tables and viewports.

## Work sequence

| Stage | UI and combined-candidate work |
| --- | --- |
| S0 — Scope | Inventory enabled routes, shared components, existing tests and user journeys. Include landing, workbench, project, results and feature-flagged app surfaces from the table. |
| S1 — Design and acceptance | Capture current desktop and narrow-screen states. Prepare the navigation, common components and visual examples for first use, input, failure and results. Pin representative pass, fail, hold, blocked-import and saved-project fixtures to the existing contracts before changing their presentation. |
| S2 — Implement | First prove the shell and shared controls with one complete Quick Beam journey. Then apply the patterns to Projects and import through results, the other calculators, and the flagged composer. Reuse route guards, state stores, request hooks and result components. Keep app logic limited to presentation and interaction. |
| S3 — Guidance | Update UI walkthroughs and screenshots for changed steps. Explain strict CSV span input where users select files, and identify the library entry points in the existing help surfaces. |
| S4 — Verify and freeze | Run the relevant React route, state, form and result tests, then `./run.sh frontend check` on the integrated UI. Replay the table journeys at desktop and narrow sizes, with keyboard and reduced-motion checks. Confirm current requests, outputs and stored-project behavior. Bind independent review to the UI candidate's exact head. |
| S5 — Handoff | Record the successful production build, hosted checks, browser journeys and any remaining user-facing decisions. Select the release target after the implementation scope is known. |

Keep new engineering methods, native-host expansion, server-side batch
recovery, changes to public contracts and unrelated dependency upgrades in
their separate tracks. Any UI work that requires a breaking contract change
must be brought back for a scope decision. Record UI design, implementation, review and hosted verification time separately.
