# StructLib React workbench UI refresh plan

**Type:** Plan
**Audience:** All Agents
**Status:** Draft
**Importance:** High
**Created:** 2026-11-22
**Last Updated:** 2026-11-22
**Related Tasks:** None
**Abstract:** Library-first public experience, browser workbench priorities, and acceptance criteria for the independent React refresh.

---

## Public experience

**StructLib is an open-source Python library for reinforced-concrete design and
checking under IS 456:2000.** The browser workbench lets people try a supported
case, see what the library checked, and take the same calculation into their own
scripts or tools. A visitor should be able to choose a path from the first screen.

| Visitor's task | First useful action |
| --- | --- |
| Learn or evaluate | **Try a beam example** opens Quick Beam with maintained sample inputs ready to run. The result explains the governing check, shows the cross-section, and links to the worked example. |
| Check a member or review a batch | **Browse workbench** leads to the supported member checks. **Import a beam project** leads to the combined or paired CSV flow, with a sample and a clear resume action for existing local work. |
| Use StructLib in my own code | **Use the Python library** opens a short install-and-run guide with the package name, `structural_lib` import, expected result and a copyable example. Put CLI, HTTP API, and GitHub links in the same guide. |

Lead with **Try a beam example** and **Use the Python library**. Keep **Import a
beam project** one clear action away. Use the first useful engineering image in
context, such as a labelled beam section next to the example outcome. Show 3D on
demand for inspecting reinforcement or locating imported members. Keep units,
the result and the next action readable on a phone with 3D unavailable. Use a
quiet, consistent hierarchy, with detailed checks and provenance available
from the summary. Let visitors go straight to the form, example or documentation.

Make these existing strengths visible in the journey:

- **Use it where you work.** The Python API, CLI, HTTP service and workbench use
  the same calculation library. Show the exact entry point for each featured case
  and identify the checks and fields that actually match across surfaces.
- **See why the result governs.** Show explicit units, the governing check and
  margin where returned, and the applicable clause or source reference. Keep
  checked scope, input rejection, engineering outcome and qualified review clear.
- **Inspect and take the work with you.** Connect the condition of an imported row
  to its member and drawing. Make checked BBS, DXF, reports and other evidence
  easy to find where the existing workflow makes them available.
- **Find supported cases quickly.** One sentence per tool states what it accepts,
  what it returns and its most relevant limit. Put the detailed supported scope
  and release evidence in the library docs. Use a verified package artifact for
  install copy and display the browser build and package version separately when
  both are shown. On the planning date, PyPI and GitHub show 0.31.0 while the
  quick start in this branch still points to 0.30.0. Resolve that distinction
  before reusing its install copy in the browser.
  [PyPI 0.31.0](https://pypi.org/project/structural-lib-is456/0.31.0/) ·
  [GitHub release](https://github.com/Pravin-surawase/structural_engineering_lib/releases/tag/v0.31.0)

[Library README](../../README.md) · [Python quick start](../getting-started/python-quickstart.md) ·
[API chooser](../reference/api-levels.md) · [Cross-surface parity](../guides/cross-surface-parity-v1.md)

## Research and tool choices

| Reference | What to use for StructLib |
| --- | --- |
| `concreteproperties` | Its worked examples put runnable code beside a domain-specific plot. Pair one StructLib example with a labelled section and a short reading of the result. [Worked concrete example](https://concrete-properties.readthedocs.io/en/latest/examples/moment_curvature.html) |
| `sectionproperties` | Its examples include validation cases and downloadable notebooks. Use the same discoverability pattern with approved StructLib normal, failure and held cases and their evidence links. [Examples and validation](https://sectionproperties.readthedocs.io/en/stable/examples.html) |
| OpenSeesPy and SciPy | OpenSeesPy starts with a short script and groups further examples by task. SciPy keeps learning material and API lookup distinct. Make the first Python example short and link experienced users directly to the API. [OpenSeesPy](https://openseespydoc.readthedocs.io/en/latest/) · [SciPy documentation](https://docs.scipy.org/doc/scipy/index.html) |

Keep React, TypeScript, Vite, Tailwind, React Query and Zustand. Reuse the current
inputs, sections, status controls and 3D scenes. Use ordinary HTML tables for
small result sets, AG Grid for dense project tables and Dockview where split
panes help with desktop review. Keep the initial landing and text/2D result path
light. Measure which production chunks load before the example result and keep
Three.js, AG Grid and Dockview out of paths that do not use them.
[Current dependencies](../../react_app/package.json) · [Chunk settings](../../react_app/vite.config.ts) ·
[Vite code splitting](https://vite.dev/guide/features.html#css-code-splitting)

| Need | Choice and adoption criterion |
| --- | --- |
| Forms and overlays | Start with native labelled inputs, disclosures and `<dialog>` for the settings drawer. If keyboard and browser checks establish a gap that a shared primitive can solve, evaluate Radix Dialog for that gap. Keep engineering validation with the existing request and service owners. [Native dialog](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog) · [Radix Dialog](https://www.radix-ui.com/primitives/docs/components/dialog) |
| Browser and accessibility verification | Keep Vitest and Testing Library for state and component checks. Pilot Playwright with `@axe-core/playwright` as development tooling for the landing-to-result and blocked-import journeys. Keep manual keyboard, mobile reflow and screen-reader checks alongside automation. Use WCAG 2.2 AA as the design target. [Playwright accessibility testing](https://playwright.dev/docs/accessibility-testing) · [WCAG 2.2](https://www.w3.org/TR/WCAG22/) |
| Docs and examples | Link to the existing Markdown, MkDocs configuration and notebook from the browser. Use verified GitHub docs links until a hosted docs destination has been checked. Give each featured example one maintained source for its inputs, scope and expected outcome. [MkDocs configuration](../../mkdocs.yml) · [Existing notebook](../getting-started/colab-workflow.ipynb) |
| Developer tooling later | Consider `openapi-typescript` for one REST client if type drift justifies it, retaining runtime validation and separate streaming contracts. Consider Storybook when shared states need independent preview often enough to justify another build. [OpenAPI TypeScript](https://openapi-ts.dev/introduction) · [Storybook accessibility testing](https://storybook.js.org/docs/writing-tests/accessibility-testing) |

## Priorities and new ideas

| Priority | Proposal and evidence of value |
| --- | --- |
| **First public slice** | Refresh Home, the workbench entry and one complete Quick Beam journey. Add the library and API links, a ready-to-run sample, a 2D section and a concise result. A first-time visitor can reach a result or a field-specific correction in three actions from Home and can find the Python quick start directly. Then reuse the pattern in Import → Results and the other calculators in the main refresh. |
| **Next — runnable examples** | Add a small **Examples** collection, starting with a normal and a failed beam case and a held case. Let users open the same example in the browser and copy or download a matching Python snippet. Add an HTTP example where the maintained parity contract applies. Re-run the snippets on the named package version and check the stated outcome and units. Expand to other members after the first cases hold up. |
| **Next — project intake** | Provide a blank Generic CSV template, a filled example and a paired-file checklist beside upload. Use the existing import ledger to make a row issue easy to find and fix. After correction, users can re-upload and review the accounted member list before designing. |
| **Next — reproduce or report a result** | Trial a compact **Copy case details** action with the calculation identity, library version, units and current status. Allow sharing links for public examples by stable example ID. Keep user imports, project identifiers and demand values out of generated URLs, and show exactly what a user is copying. |
| **Explore — compare two runs** | Prototype a session-only comparison of two results from one supported workflow. Show the input differences and returned values side by side with each run’s status and identity. Keep this only if it helps a user explain the effect of an input change. |
| **Explore — browser notebooks** | Pilot the existing notebook with a single named Python package release before considering a JupyterLite/Pyodide demo. Prove runtime support for the package and its dependencies, reproduce the same expected outcome and measure cold-load cost. [JupyterLite](https://jupyterlite.readthedocs.io/en/stable/) · [Pyodide package compatibility](https://pyodide.org/en/stable/usage/loading-packages.html) |

The new ideas are proposals. The first slice uses the existing calculation
routes and needs no new production dependency. Future engineering methods and
additional calculation coverage follow the library’s separate approval and
evidence process.

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

- Give the workbench a compact **Design tools** list for Quick Beam, Slabs, Rectangular Column,
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
  Tailwind base with a single primary action per view, clear
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
| Home, Workbench, project list and settings | Give the public entry two clear paths into the example and Python docs. Use consistent navigation, with project entry, settings and a next action in empty and loading states. | One first-time visitor can run the example, explain the displayed status and find Python without help. Direct links, refresh, Back, old redirects and saved-project recovery work. A keyboard user can start and resume a project. |
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
| S1 — Design and acceptance | Capture current desktop and narrow-screen states. Prepare Home and the first example view, then walk through them with a first-time visitor and a technical user if available. Pin representative pass, fail, hold, blocked-import and saved-project fixtures before changing presentation. |
| S2 — Implement | First prove the public entry, Python path and shared controls with one complete Quick Beam journey. Then apply the patterns to Projects and import through results, the other calculators, and the flagged composer. Reuse route guards, state stores, request hooks and result components. Keep app logic limited to presentation and interaction. |
| S3 — Guidance | Update the public walkthrough and screenshots for changed steps. Verify the current install and API links, exact example release and expected result. Put strict CSV span guidance at upload. |
| S4 — Verify and freeze | Run the relevant React route, state, form and result tests, then `./run.sh frontend check` on the integrated UI. Replay the table journeys at desktop and narrow sizes, with keyboard and reduced-motion checks. Confirm current requests, outputs and stored-project behavior. Bind independent review to the UI candidate's exact head. |
| S5 — Handoff | Record the successful production build, hosted checks, browser journeys and any remaining user-facing decisions. Select the release target after the implementation scope is known. |

Keep new engineering methods, native-host expansion, server-side batch
recovery, changes to public contracts and unrelated dependency upgrades in
their separate tracks. Any UI work that requires a breaking contract change
must be brought back for a scope decision. Record UI design, implementation, review and hosted verification time separately.
