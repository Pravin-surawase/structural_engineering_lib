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

## Journeys and acceptance

| Surface | Planned change | Acceptance evidence |
| --- | --- | --- |
| Home, Workbench, project list and settings | Use consistent navigation in the desktop top bar and mobile dock. Show project entry and settings plus the next action in empty and loading states. | Direct links, refresh, back navigation, old route redirects and saved-project recovery work. A keyboard user can start and resume a project. |
| Quick beam design and catalogue | Group input, units and validation, the check result, section and reinforcement views, and existing outputs. Cover manual and catalogue paths. | A supported beam can be entered, checked and exported. Invalid data maps to visible field errors. Existing geometry and 3D controls stay usable. |
| Projects and import through results | Make import, review, design and results easy to follow. Show combined and paired CSV guidance, source-row errors, member counts and save or restore feedback. | Valid Generic and supported ETABS examples reach the appropriate stage. An invalid Generic span shows its row and field. Mixed rows and interrupted work keep their actual states. Guarded deep links, autosave, recovery and save conflicts work with existing projects. |
| Slab workbench | Use common input and result patterns for simply supported, continuous and two-way slabs. Surface the strip width, coefficient source, units and governing checks carried by the existing built-in requests. | Exercise the supported browser flows and show a failed reinforcement check separately from rejected input. Confirm requests and units match the existing HTTP route. Freeze evidence for each supported mode on the UI candidate's actual base. |
| Rectangular column, concentric isolated footing and building gravity | Use the same input, review, result and evidence patterns within each supported route. Expose the governing checks and available reports. | Replay one valid journey per workbench and the applicable blocked, failure or review-held controls. Report downloads and evidence references still reach their original outputs. |
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
| S2 — Implement | Update the app shell and shared controls first, then apply them to each workbench, project stage and workflow composer. Reuse route guards, state stores, request hooks and result components. Keep app logic limited to presentation and interaction. |
| S3 — Guidance | Update UI walkthroughs and screenshots for changed steps. Explain strict CSV span input where users select files, and identify the library entry points in the existing help surfaces. |
| S4 — Verify and freeze | Run the relevant React route, state, form and result tests, then `./run.sh frontend check` on the integrated UI. Replay the table journeys at desktop and narrow sizes, with keyboard and reduced-motion checks. Confirm current requests, outputs and stored-project behavior. Bind independent review to the UI candidate's exact head. |
| S5 — Handoff | Record the successful production build, hosted checks, browser journeys and any remaining user-facing decisions. Select the release target after the implementation scope is known. |

Keep new engineering methods, native-host expansion, server-side batch
recovery, changes to public contracts and unrelated dependency upgrades in
their separate tracks. Any UI work that requires a breaking contract change
must be brought back for a scope decision. Record UI design, implementation, review and hosted verification time separately.
