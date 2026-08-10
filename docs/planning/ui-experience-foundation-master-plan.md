---
task: UIX-001
title: UI Experience Foundation and Structural Workbench Master Plan
status: active
owner: Main Agent and repository owner
created: 2026-08-10
last_updated: 2026-08-10
doc_type: spec
baseline_commit: 32b9f33b204f5175efdf0d3e8d4d99e3634cf46c
branch: codex/ui-capability-platform
implementation_started: true
second_audit_integrated: true
execution_sessions: 2
max_concurrent_subagents: 2
subagent_model: gpt-5.6-terra
owner_accepted: 2026-08-10
current_session: 2
current_wave: complete
---

**Type:** Master Plan
**Audience:** Product owner, frontend, backend, API, structural-library, 3D, reviewer, and tester roles
**Status:** Complete — Session 1 P0-P8 and Session 2 P9-P15 accepted
**Importance:** Critical
**Created:** 2026-08-10
**Last Updated:** 2026-08-10

---

# UIX-001 — UI Experience Foundation and Structural Workbench Master Plan

## 1. Executive decision

The product will move from a collection of equally weighted pages to one compact,
professional structural workbench.

The primary project journey is:

```text
Home -> Workbench -> Import/Input -> 3D Review -> Design -> Resolve -> Export
```

Quick single-beam design remains available, but it is a focused mode inside the
workbench rather than the mental model for the entire product. Import, editor,
batch design, dashboard, and export become contextual stages of one project flow,
not competing destinations in global navigation.

This program has four coupled outcomes:

1. simplify and professionalize the current React interface;
2. make every exposed feature useful in a visible end-to-end workflow;
3. make 3D inspection the center of project work rather than a decorative view;
4. create a schema-driven capability foundation that can later power curated
   no-code workflows and AI tools without duplicating engineering contracts.

This is a staged migration, not a rewrite. Existing routes remain available until
the replacement quick-design and project journeys pass parity and live user
acceptance. The program does not change IS 456 formulas merely to serve the UI.

## 2. Plan authority and relationship to existing work

The repository owner accepted this document on 2026-08-10. It is the execution
authority for UIX-001. Planning and Terra routing merged to `main` through PR
#718. Session 1 finished on `codex/ui-quick-design-p4`; Session 2 uses another
fresh branch after the Session 1 verified green merge. Execution remains exactly
two implementation sessions under sections 12 and 16.1; the already-merged
planning branch does not count as an implementation session.

It supersedes the execution status in
`docs/planning/react-ux-improvement-plan.md`, while preserving that document as
useful implementation history. The older plan correctly established an
import-first, visual-first direction, but its task ledger has drifted: the current
repository already contains `HubPage`, `WorkflowBreadcrumb`, `SettingsPanel`,
load analysis, torsion, Pareto alternatives, project BOQ, and related hooks that
the old document still marks partly or wholly TODO.

This plan is consistent with `docs/planning/democratization-vision.md`, but narrows
that long-term vision into an implementable product sequence. It does not activate
the broad plugin, webhook, AI chat, multi-code, or cloud-platform roadmap.

The architecture authority remains:

```text
core types -> codes/is456 pure math -> services -> FastAPI/React
```

UI metadata, workflow orchestration, transport schemas, persistence, and React
components must not enter `Python/structural_lib/core/` or
`Python/structural_lib/codes/is456/`.

## 3. Product outcome

### 3.1 Product promise

A structural engineer can enter the site, understand the next useful action,
load or create a project, inspect it in 3D, design members, resolve governing
issues, compare alternatives, and export evidence without learning the internal
route structure.

A returning user can resume meaningful work. A non-coding user can eventually
assemble a safe, curated structural workflow from approved capabilities. An AI
assistant can discover the same capabilities and input contracts without a
second hand-maintained parameter catalogue.

### 3.2 Engagement without feature inflation

Time on site must come from a productive loop, not from extra pages or decorative
widgets:

```text
Select critical member
  -> inspect geometry, reinforcement, loads, and checks
  -> compare a bounded alternative
  -> apply or reject the change
  -> see project status update
  -> move to the next governing member
  -> export the reviewed result
```

The product will favor depth, continuity, saved context, and visible consequences
over gamification, feed-like content, or large menus.

### 3.3 Program-level completion definition

UIX-001 is complete only when all of the following are true:

- one primary workbench shell owns navigation and project context;
- the fresh-user, quick-design, imported-project, resume, and export journeys have
  no dead ends or placeholder actions;
- all exposed features pass the usefulness gate in section 5 and dormant
  capabilities have an explicit internal/hold/retire decision;
- project work is anchored by interactive 3D inspection with a non-WebGL fallback;
- status, supported-case limits, units, and provenance remain truthful across
  library, API, UI, saved state, and exports;
- no calculation result, geometry, alternative, project metric, or export is
  treated as current unless it is bound to the current input/project revision;
- delayed responses cannot replace newer results, and stale prior results are
  visibly labelled and never exported as current evidence;
- the capability catalogue has one versioned machine-readable contract consumed
  by the API and one migrated React vertical slice;
- the curated no-code MVP can build, validate, save, reload, and run one approved
  beam workflow within explicit resource and execution limits without executing
  arbitrary code;
- the agreed simplicity, task-flow, browser, responsive, visual, storage-recovery,
  API-contract, and 3D-contract baselines have measurable acceptance evidence;
- current route compatibility is either preserved by redirects or retired through
  an explicit migration decision;
- focused tests, React validation, the repository quick gate, one full integrated
  gate, and live end-to-end acceptance pass.

Passing software gates is not formula certification or professional design
approval.

## 4. Verified current baseline

The original UI observations were captured at `67b85302`. Session 1 starts from
`32b9f33b`, which includes ADOPT-001, the Python/React compatibility packets, the
merge-policy update, the Dependabot Python 3.11 guard, and the accepted UIX plan.
Section 22 refreshes the quantitative and contract-sensitive baseline at that
checkpoint.

| Area | Verified baseline at `67b85302` | Program treatment |
|---|---|---|
| Routes | Eight routes in `react_app/src/App.tsx`: `/`, `/start`, `/design`, `/design/results`, `/import`, `/editor`, `/dashboard`, `/batch` | Consolidate behind one workbench; retain compatibility until cutover |
| Navigation | `TopBar`, `AppDock`/`FloatingDock`, page back buttons, and `WorkflowBreadcrumb` all express overlapping navigation | Create one navigation model rendered appropriately by the shell |
| Quick design | `DesignView.tsx` contains inputs, load analysis, torsion, live design, 3D, results, alternatives, and export | Preserve capability; reduce simultaneous controls and split by responsibility |
| Project editor | `BuildingEditorPage.tsx` contains building 3D, AG Grid, batch actions, detail panel, materials, export, and workflow help | Make it the core project workbench rather than one global destination |
| Results | `DashboardPage`, `BeamDetailPage`, `BeamDetailPanel`, and inline result areas overlap | Use contextual inspector and one project results stage; keep deep links only where useful |
| 3D | Beam, full-rebar, building, material, and cross-section geometry APIs and hooks already exist | Recompose and expose; do not rebuild geometry math in React |
| Large components | `Viewport3D` is about 1,000 lines; `DesignView` about 800; `BuildingEditorPage` about 660 | Decompose only along stable scene/workflow boundaries, not arbitrary file-size targets |
| State | Quick design and imported beams live in separate Zustand stores; only a small session summary is persisted | Introduce versioned workspace/project state without breaking current flows during migration |
| Capability truth | `services/capabilities.py` already publishes supported cases, fields, units, statuses, aliases, and limitations | Extend this source; do not create a rival engineering catalogue |
| Schemas | `services/serialization.py` generates JSON Schema for canonical Pydantic models | Reuse and extend for catalogued workflows |
| Automation | `services/job_runner.py`, `beam_pipeline.py`, batch helpers, CLI, and import adapters already provide execution foundations | Build a curated allowlisted runner; no arbitrary dynamic execution |
| Result freshness | Project edits mark members pending but can leave prior calculated fields present; current exports can still serialize those fields | Bind results to input/project revision and block stale results from current metrics and exports |
| Async requests | Live-design fallback creates cancellation state but the design client does not currently receive an abort signal | Require transport cancellation plus request-revision matching and latest-result-wins |
| API contracts | OpenAPI and path/method checks exist, while React request/response types remain partly hand-maintained | Audit complete shapes and choose one generated-or-validated type source before exposing dormant clients |
| 3D coordinates | Core building coordinates are normally metres, geometry services commonly emit millimetres, and React scales to Three.js world metres | Freeze and test one versioned source/canonical/renderer coordinate contract |
| Browser proof | Component tests run primarily in Vitest/jsdom and do not prove WebGL, responsive layout, or visual hierarchy | Add reviewed wireframes, live browser evidence, and deterministic screenshots/fixtures |
| Visual direction | Dark React/R3F workstation with Bento, floating dock, motion, grid, and multiple feature panels | Reduce ornamental variation; standardize density, hierarchy, and status semantics |

## 5. Feature usefulness contract

No feature is visible merely because an endpoint, hook, or component exists.
P0 classifies visible and dormant capabilities as exposed, internal utility,
dormant candidate, or superseded/dead. Before a feature enters navigation or a
workbench panel, its owner must answer all nine
questions:

1. Who is the user?
2. In what workflow state does the feature become relevant?
3. What input or selection does it require?
4. What action can the user take?
5. What visible outcome changes?
6. What is the next useful action?
7. What state must be saved or exported?
8. What safety, support, or provenance statement must remain visible?
9. Has its live client/API request and response contract been verified?

If any answer is missing, the feature is merged into a relevant flow, kept
internal, or removed from the exposed UI. A feature does not earn a page by
itself. Dormant candidates remain unavailable until their current contract and
workflow role pass this gate.

### 5.1 Tentative keep/merge/retire map

P0 must verify this map against live behavior before implementation.

| Current surface | Decision direction | Target role |
|---|---|---|
| `HomePage` | Keep and reduce | Product orientation, sample, and resume entry only |
| `HubPage` | Merge | Workbench home/recent-project state |
| `DesignView` | Keep and recompose | Quick single-beam mode |
| `ImportView` | Merge | Project intake stage |
| `BuildingEditorPage` | Promote and recompose | Main project review/design workbench |
| `BatchDesignPage` | Merge | Project design/run stage and progress state |
| `DashboardPage` | Merge | Project results, issue queue, quantities, and export stage |
| `BeamDetailPage` | Repurpose or redirect | Optional shareable/deep-link result, not a required step |
| `BeamDetailPanel` | Keep | Contextual selected-member inspector |
| `ModeSelectPage` | Retire after route audit | Superseded entry choice |
| `ModernAppLayout` | Retire or mine for reusable code | Competing unused shell |
| `TopBar` + `FloatingDock` | Merge through shared configuration | One shell, responsive presentations |
| `CommandPalette` | Hold until commands are complete | Contextual power-user access, never dead navigation |

## 6. Users and core journeys

### 6.1 Primary users

- **New evaluator:** wants to understand value and explore a safe sample quickly.
- **Structural engineer doing a quick check:** wants a focused single-member input,
  result, visualization, and export path.
- **Structural engineer reviewing a project:** imports ETABS/SAFE/CSV data, checks
  geometry and forces, designs many members, resolves critical cases, and exports.
- **Returning user:** resumes a locally saved project with selections, filters, and
  results intact.
- **Non-coding workflow author:** combines approved inputs, design, review, and
  export steps without writing Python or JavaScript.
- **AI client:** discovers versioned tools and schemas, proposes inputs or workflows,
  and remains behind the same validation and user-approval boundaries.

### 6.2 Fresh-user journey

```text
Landing
  -> Open sample project
  -> 3D model loads with one short guided hint
  -> Critical member is highlighted
  -> User inspects result and one alternative
  -> User can start a real project or quick design
```

Acceptance:

- no account or upload is required to understand the complete product loop;
- the sample uses real API contracts and the same workbench, not a disconnected demo;
- guidance is dismissible, does not block interaction, and does not reappear after
  dismissal unless reset.

### 6.3 Quick-design journey

```text
Workbench -> Quick design -> Inputs -> Live 3D/result -> Checks/alternatives -> Export
```

Acceptance:

- common dimensions, material, forces, calculate, result, and status are visible
  without opening advanced panels;
- load analysis, torsion, alternatives, detailing, and export appear only when
  their prerequisites exist;
- the result never shows PASS when any required evaluated status is unsafe or not
  evaluated;
- reset and compare actions are explicit and reversible.

### 6.4 Imported-project journey

```text
Create project
  -> Import and map data
  -> Review geometry and validation issues
  -> Run selected/all member design
  -> Resolve critical members in 3D
  -> Review project summary and quantities
  -> Export evidence
```

Acceptance:

- stage availability follows project state; users cannot silently skip required
  validation;
- the selected member is shared between 3D, grid, inspector, issue queue, and
  result views;
- batch completion is not presented as engineering safety;
- an unsafe or unsupported member remains visible until explicitly resolved or
  excluded with a recorded reason.

### 6.5 Resume journey

Acceptance:

- project title, normalized inputs, results, selected stage, filters, and current
  member can be restored after reload;
- storage uses a versioned schema and can fail closed with a clear recovery/export
  path;
- raw uploaded files are not retained without an explicit product decision;
- users can export and re-import a portable project snapshot.

### 6.6 Curated no-code journey

```text
Choose template
  -> Add approved steps
  -> Bind typed inputs/outputs
  -> Validate sequence
  -> Preview with sample data
  -> Save versioned definition
  -> Run
  -> Inspect statuses and exports
```

Acceptance:

- only allowlisted capabilities can run;
- invalid field bindings, unit mismatches, unsupported branches, cycles, or missing
  review steps fail before execution;
- workflow completion and engineering approval remain separate states;
- saved definitions are data, never executable Python/JavaScript.

## 7. Target information architecture

### 7.1 Canonical route model

The route model is proposed and must be finalized in P0/P1 after checking current
deep links and tests.

```text
/
/workbench
/workbench/quick
/workbench/projects/new
/workbench/projects/:projectId/import
/workbench/projects/:projectId/review
/workbench/projects/:projectId/design
/workbench/projects/:projectId/results
/workbench/automations                 # activated only in the no-code phase
```

Current routes must initially redirect or delegate to the matching workbench
surface. They are not deleted in the same packet that introduces the new shell.

### 7.2 Navigation hierarchy

Global navigation must contain only durable product areas:

- Workbench;
- Projects/recent work, once real project persistence exists;
- Automations, only after the composer MVP is functional;
- Help/about/settings as secondary actions.

Import, Review, Design, Results, Export, floor selection, and member selection are
project context, not global navigation.

One typed navigation configuration must feed desktop and compact/mobile
presentations. `TopBar` and `FloatingDock` must not maintain separate destination
arrays.

### 7.3 Workbench layout

Desktop project mode uses four contextual regions:

```text
+------------------------------------------------------------------+
| Project context | standard/units | save state | primary actions   |
+------+---------------------------------------------+---------------+
| Stage|                                             | Inspector     |
| rail |              3D / main canvas               | selected item |
|      |                                             | checks/actions|
+------+---------------------------------------------+---------------+
| Issue/result tray, progress, comparisons, and export status       |
+------------------------------------------------------------------+
```

Panels open because the user selected an object or action, not because every
feature needs permanent screen space. Tablet/mobile supports project review and
critical actions; dense full-project editing remains desktop-oriented unless later
evidence justifies more scope.

## 8. Compact professional visual system

### 8.1 Principles

- Use one density scale, one typography hierarchy, and restrained surface styles.
- Prefer alignment, whitespace discipline, clear grouping, and high information
  value over glass effects, gradients, and animation.
- Reserve color for selection, status, and primary actions.
- Never use color as the only status signal.
- Display units beside values and preserve them in editing, saved state, and export.
- Use plain engineering language; explain acronyms and unsupported states in
  context.
- Motion communicates state changes only and respects reduced-motion preference.

### 8.2 Minimal shared primitives

P2 must create only primitives proven to repeat across at least three product
surfaces. Likely candidates are:

- application/workbench shell;
- toolbar and action groups;
- compact panel/section/disclosure;
- field with label, unit, validation, and help;
- status badge with icon and text;
- metric and utilization display;
- empty/error/loading/not-evaluated state;
- selected-member header;
- export action state.

Do not create a large generic component library, Storybook program, or theme
marketplace in this plan. One validated professional theme is sufficient; tokens
must permit later theming without requiring it now.

### 8.3 Accessibility interaction baseline

The critical workflows must support:

- keyboard traversal and visible focus;
- semantic labels for controls and 3D-adjacent actions;
- text/icon status in addition to color;
- reduced motion;
- readable validation and error recovery;
- a tabular/list alternative for information available only through 3D selection;
- announcements for async design progress and completion.

### 8.4 Pre-implementation visual and simplicity gate

P2 implementation cannot begin until P1 produces and the parent verifies
low-fidelity wireframes for the landing entry, quick workbench, project
import/review/design/results sequence, selected-member inspector, and narrow
review presentation. The same information architecture is shown at three agreed
viewport widths; dense project editing may remain desktop-first, but review and
recovery actions must stay usable on narrow screens.

Acceptance of this plan pre-authorizes the information architecture in section 7.
The parent must request another owner review before P2 only when the P1 wireframes
materially deviate from that accepted target.

P0 records the current top-level destination count, primary actions per surface,
steps from sample to first useful result, steps from import to a selected failed
member, duplicate-navigation count, dead ends, resume success, and task completion
notes. P1 sets improvement targets from that evidence. Each UI packet records
before/after screenshots and a short owner or target-user walkthrough; UIX-001
does not add third-party analytics merely to measure this program.

## 9. 3D product plan

### 9.1 Role of 3D

3D is an inspection and decision surface. It must answer:

- What is selected?
- Where is it in the project?
- What geometry and reinforcement will be built?
- What loads, checks, and utilization govern?
- What changed after an edit or alternative was applied?
- What can the user do next?

### 9.2 Scene layers

The target curated layer registry includes:

- concrete/member geometry;
- longitudinal reinforcement;
- stirrups/ties and zones;
- applied loads and reactions where data exists;
- dimensions, covers, spacing, and bar marks;
- floor/story context;
- pass/fail/not-evaluated/utilization overlay;
- critical-member and selected-member highlight;
- before/after alternative comparison;
- section/cross-section link.

Layers are enabled only when authoritative data exists. React must not invent
reinforcement positions or engineering results that belong to the library/API.

### 9.3 Interaction

- select from 3D, grid, issue queue, or search and synchronize all views;
- isolate selected member, floor, failed set, or high-utilization set;
- fit camera to selection and restore project view;
- expose a compact layer/legend control;
- provide deterministic camera presets for export and comparison;
- allow section/cross-section inspection without leaving the project flow;
- retain current selection and camera intent when moving between project stages.

### 9.4 Scene decomposition

`Viewport3D.tsx` must be decomposed behind its existing public contract before
large new visual features are added. Candidate internal boundaries are:

- scene canvas and fallback;
- building/member geometry layers;
- rebar/stirrup layers;
- load/dimension/result overlays;
- camera and selection controllers;
- lighting/environment;
- layer controls and legend;
- resource disposal/context-loss handling.

File movement must use `scripts/safe_file_move.py` because repository links and
indexes must be preserved.

### 9.5 Performance and fallback

P0 records current 153-beam sample metrics and creates a reproducible larger
synthetic scene fixture before budgets are frozen. The final gate requires:

- no crash or unbounded memory growth during the agreed large-scene fixture;
- no material regression from the P0 baseline without an accepted reason;
- bounded draw calls/geometry through reuse or instancing where profiling proves
  it matters;
- disposal of Three.js resources on route or project changes;
- graceful WebGL unavailable/context-lost states;
- a list/grid/cross-section path for critical information when 3D is unavailable.

Do not adopt a second web renderer or server-side CAD stack in UIX-001.

### 9.6 Authoritative coordinate and identity contract

P7 cannot change or decompose scene behavior until the existing 3D JSON contract
is reconciled with current code and versioned. It must define:

- source space: structural/ETABS-style axes and metres for imported building
  coordinates;
- canonical geometry space: library axes and explicit millimetres for generated
  beam/reinforcement geometry;
- renderer space: Three.js world metres and the one approved axis mapping;
- exactly one unit conversion and one axis mapping at named boundaries;
- stable member ID, source ID, story, frame type, and selection identity;
- schema versions for beam and building geometry.

A deterministic golden fixture must cross Python, FastAPI serialization, React
types, renderer mapping, selection, and overlay alignment. Production geometry
must not rely on fallback IDs, and loads, dimensions, sections, and result
overlays must use the same contract.

### 9.7 Browser and delivery-performance gate

P0 proposes a maintained browser matrix and three viewport widths. At minimum,
the primary Chromium and Safari paths on macOS must be decided before P2; Firefox
support is accepted or explicitly held from evidence. P0 also captures route
chunk sizes, initial shell loading, Three.js/React Three Fiber and grid chunks,
time to a usable viewport, and memory across repeated project switches.

The landing shell must not eagerly load 3D or grid bundles without need. P8
compares against the P0 baseline, verifies slow/API-unavailable behavior, and
uses a deterministic scene fixture plus browser screenshots or interaction
replay. A broad new browser-test framework is not introduced unless P0 proves
that maintained browser/manual verification cannot provide repeatable evidence.

## 10. Schema-driven capability foundation

### 10.1 Decision

Build a **Structural Workflow Catalogue**, not a generic no-code website builder.

The catalogue must describe approved engineering/application capabilities and
their contracts without knowing about React components. React owns layout and
widget selection. FastAPI owns transport. The service layer owns safe orchestration.

### 10.2 Reuse before extension

The existing sources are:

- `Python/structural_lib/services/capabilities.py` for supported cases, fields,
  units, statuses, aliases, and limitations;
- canonical Pydantic models and
  `Python/structural_lib/services/serialization.py` for JSON Schema;
- public service entry points such as `design_from_input` and bounded element APIs;
- `Python/structural_lib/services/job_runner.py` and batch helpers for controlled
  execution;
- geometry service functions and FastAPI geometry endpoints for visualization.

Do not duplicate field names, units, support claims, or status meanings in a new
catalogue.

### 10.3 Target contract layers

```text
IS 456 calculations and canonical models
               |
               v
Supported capability + semantic contract
               |
               v
Application workflow catalogue
  - stable workflow ID and schema version
  - canonical input/output model IDs
  - approved action relationships
  - examples and limitations
  - visualization affordances
               |
               v
FastAPI catalogue and execution transport
          /                 \
         v                   v
Curated React renderer    Generated AI tool manifest
         |
         v
Constrained no-code workflow definitions
```

### 10.4 Workflow catalogue rules

A catalogue entry may contain:

- stable `capability_id` and version;
- element and operation;
- canonical callable/service adapter identifier;
- input and output schema identifiers;
- units/status/limitations references;
- prerequisites and allowed next actions;
- supported visualization modes;
- safe example inputs;
- whether explicit user review is required before downstream execution/export.

It must not contain:

- arbitrary import paths supplied by users;
- executable expressions;
- React component names;
- copied protected clause/table text;
- statements that software completion equals engineering approval.

Catalogue, workflow-definition, project-snapshot, API, and 3D schemas follow an
explicit compatibility policy: additive fields are tolerated within a compatible
version; breaking changes require a new major schema version; consumers declare
supported versions; unsupported versions fail clearly; and deterministic golden
fixtures cover the supported migration window. Existing API routes remain
available through their approved deprecation window.

### 10.5 React renderer rules

The renderer is curated, not fully automatic. It maps known schema shapes and
canonical field IDs to a small widget registry. Unknown fields fail visibly rather
than silently choosing an unsafe input.

The renderer must support:

- groups, order, labels, units, defaults, enums, ranges, and required state;
- inline validation from the canonical schema;
- explicit advanced fields;
- status/result renderers;
- visualization slots;
- safe examples and limitations;
- an escape hatch to a hand-built panel where a schema form is insufficient.

The first migrated vertical slice is quick beam design. Batch/project migration
does not begin until the schema-driven slice matches current behavior.

### 10.6 No-code definition and runner

A saved workflow is versioned data with allowlisted step IDs and explicit field
bindings. The MVP starts as a template-first ordered step list, with only tightly
constrained branching when a reviewed workflow requires it. It is not a free-form
node canvas. An approved flow may be:

```text
Input/import -> validate -> design -> review unsafe/not-evaluated -> export
```

The runner must:

- resolve only registered handlers;
- validate all bindings before starting;
- preserve units and canonical field names;
- stop or route to review on unsafe, unsupported, or not-evaluated results;
- record step status and calculation provenance;
- produce deterministic saved definitions;
- reject cycles and unsupported dynamic code;
- enforce configured maximum steps, input/project size, batch members, execution
  time, concurrency, and output size;
- issue a run ID, support bounded cancellation, and define retry/idempotency
  behavior so repeated requests cannot silently duplicate work;
- sanitize user-visible workflow/project names and reject user-provided filesystem
  paths or import targets;
- clean up partial outputs while preserving a safe audit record.

Plugins, webhooks, external notifications, user-authored formulas, and arbitrary
scripts are deferred. UIX-001 does not turn the existing job runner into a
durable background workflow platform. Any public runner activation requires a
separate authentication/rate-limit decision; until then, execution transport
remains unavailable by default even if local validation/composition is present.

### 10.7 AI readiness

AI tool descriptors may be generated from the same catalogue and JSON Schemas only
after the beam vertical slice is stable. AI can propose inputs or a workflow draft,
but execution still uses the allowlisted runner and normal validation.

AI chat, model/provider selection, autonomous project changes, and autonomous
engineering approval are not part of UIX-001.

## 11. Scope contract

### 11.1 Included

- current React application information architecture and visual system;
- quick beam design and existing imported-beam project flow;
- existing design, analysis, insights, optimization, detailing, geometry, batch,
  dashboard, BOQ, and export capabilities where they pass the usefulness gate;
- local versioned project persistence and portable project snapshots;
- 3D scene decomposition and agreed high-value layers/interactions;
- application workflow catalogue, catalogue API, curated React renderer;
- one constrained no-code beam workflow MVP;
- generated AI-tool manifest readiness;
- redirects/migration for current routes and cleanup after parity.

### 11.2 Explicit non-goals

- changing or expanding IS 456 formulas merely for UI completeness;
- claiming whole-standard coverage or professional design approval;
- a generic website/page builder;
- arbitrary user Python, JavaScript, formulas, imports, or plugins;
- public webhook, Slack, email, or external automation platform;
- AI chat implementation or autonomous design decisions;
- authentication, billing, organizations, cloud collaboration, or multi-device sync;
- new structural elements or multi-code UI expansion;
- PyVista/server-side CAD or replacement of React Three Fiber;
- a full light/dark theme marketplace or a large design-system program;
- mobile parity for dense project editing;
- a durable background workflow service or public unauthenticated runner;
- third-party product analytics added only for this redesign;
- deleting current routes before replacement parity and rollback evidence;
- broad refactors unrelated to the primary workbench outcome.

## 12. Two-session execution model

UIX-001 has exactly two implementation sessions after this planning branch is
accepted. P0-P15 remain the detailed safety and acceptance checklists, but they
are not sixteen scheduling events or seven pull requests.

A session is outcome-gated, not a promise to stop at an arbitrary clock time or
context boundary. It may continue through normal compaction/continuation until
its exit gate passes. If a critical contract, safety, or verification gate fails,
the current session is incomplete or blocked; the gate is not waived and a hidden
third cleanup session is not assumed.

Accepting this plan also accepts the information architecture in section 7 as the
P1 target. The parent requests another owner decision only if P0 live evidence
requires a material route, scope, safety, or data-retention change.

### 12.1 Macro dependency graph

~~~text
Planning branch accepted
  |
  v
SESSION 1 — Compact workbench and essential 3D (P0-P8)
  Wave 0: evidence + IA + API/state/3D contract lock
  Wave 1: shell + revisioned state + quick flow + 3D contract/fixture
  Wave 2: project flow -> viewport parity -> essential 3D + integration/UAT
  |
  | Session 1 exit gate and verified green merge
  v
SESSION 2 — Capability platform and cutover (P9-P15)
  Wave 0: catalogue/client/runner contract lock
  Wave 1: catalogue + thin API + curated beam renderer
  Wave 2: bounded no-code -> beam AI manifest/cutover -> full UAT
  |
  v
Merge when green; owner decision remains for release/hold
~~~

At most two bounded subagents may work concurrently with the parent. Reuse the
same workers through explicit follow-up packets when practical. Every dispatch
contains exact owned paths, non-goals, pitfalls, acceptance, narrow commands, and
the return format in section 19.3. The parent owns integration and independently
reviews every worker result. Luna is unavailable for this program; dispatch Terra
directly without probing Luna first.

### 12.2 Session 1 — Compact workbench and essential 3D

**Outcome:** one coherent landing/workbench experience supports sample, quick
design, import, 3D review, project design, issue resolution, current-revision
results, resume, and truthful export. Essential 3D inspection is integrated and
the previous routes remain available for rollback until the exit gate passes.

**Entry:** this plan and Terra routing were accepted and merged through PR #718.
Session 1 started on `codex/ui-workbench-session-1` from `origin/main` at
`32b9f33b`. Dependency upgrades remain out and external-worktree locks in section
16.2 apply.

**Wave 0 — parallel read-only contract lock**

- **Parent:** run the live journey/usefulness/route baseline; consolidate P0
  evidence; confirm section 7 IA; produce the three-width wireframes and measurable
  targets; own all decisions and update the ledger.
- **Subagent A — application truth audit:** inspect exposed and dormant React
  clients/hooks against FastAPI/OpenAPI shapes; map result freshness, latest-
  request-wins, storage payloads, status/export truth, and existing store adapters.
  It returns evidence only and edits nothing.
- **Subagent B — 3D/browser audit:** reconcile source/canonical/renderer axes,
  units, IDs, and versions; capture current scene/browser/bundle/performance
  evidence; identify which P8 layers already have authoritative data. It returns
  evidence only and edits nothing.
- **Checkpoint:** the parent freezes the route model, workspace/result revision
  contract, API-client contract approach, storage decision inputs, authoritative
  3D contract, essential layer list, owned-path map, and P0/P1 evidence before any
  implementation dispatch.

**Wave 1 — parallel foundations with a mid-wave contract handoff**

- **Parent:** own shared navigation/routes, shell integration, workspace schema and
  migrations, project storage, API client cancellation/revision handling, status
  truth, and cross-feature adapters. Publish the typed workspace and viewport
  boundaries before dependent worker follow-ups.
- **Subagent A — frontend flow:** first implement only approved semantic primitives
  and focused tests; after the parent accepts them and publishes state/client
  contracts, receive a follow-up for P4 quick-design components. It does not edit
  routes, shared stores, API-client contracts, or viewport files.
- **Subagent B — 3D foundation:** version the 3D JSON contract and golden fixture,
  then return a read-only P7 decomposition map. It does not implement P7 or add
  P8 layers before P5/P6 project selection/status/result contracts are accepted.
- **Checkpoint:** parent integrates P2-P4 and the 3D contract/fixture, runs focused
  suites, verifies stale/out-of-order negatives, and then authorizes Wave 2.

**Wave 2 — dependency-gated product flow**

- **Stage A — project contract first:** the parent integrates routes, stores,
  client and export contracts. Subagent A implements P5/P6 within project-stage
  components and focused tests: import/review, selected-member inspector, batch
  progress, issue queue, result resolution, and member/project/draft export
  presentation. Subagent B may perform only read-only P7/P8 profiling and fixture
  preparation. The parent accepts P5/P6 selection/status/result behavior before
  any P7 implementation.
- **Stage B — 3D implementation:** Subagent B receives a follow-up to implement
  P7 decomposition and prove parity; after parent acceptance, it receives the P8
  follow-up for synchronized selection, isolate/filter, fit-to-selection,
  status/utilization overlay and legend, section link, deterministic view, and
  fallback/browser/performance evidence. Loads, dimensions, or comparisons are
  added only when Wave 0 proved authoritative data and the exit gate is not
  endangered.
- **Ownership boundary:** Subagent A owns project-stage inspector presentation.
  Subagent B owns only decomposed viewport layer/control files. The parent alone
  wires selection, status, legend, and inspector integration into shared
  workbench surfaces after both handoffs.
- **Closeout:** workers stop editing; the parent performs integration review,
  live browser UAT, documentation/evidence, frontend validation, and the quick
  repository gate.

**Session 1 must ship**

- accepted P0/P1 evidence, route map, wireframes, targets, and contract ledgers;
- one shell/navigation model and revisioned recoverable workspace state;
- latest-request-wins and fail-closed stale-result/export behavior;
- quick-design and import-to-project-result flows without dead ends;
- versioned 3D axes/units/schema/identity contract and decomposed parity adapter;
- essential selected-member/status inspection with non-WebGL fallback;
- focused tests, live maintained-browser evidence, frontend check, and quick gate.

**Session 1 scope cuts**

- defer decorative motion/effects, generic design-system expansion, mobile parity
  for dense editing, and any dormant feature that lacks live contract proof;
- defer optional 3D loads, dimensions, before/after comparison, or advanced layers
  whose authoritative data or performance is not already proven;
- do not refactor unrelated components, add import formats, change calculations,
  perform dependency upgrades, or begin P9.

**Session 1 parent locks**

- App and route/navigation configuration;
- workspace store/types/schema/migrations and storage adapter;
- API client contract, result revisions, status mapping, and export contract;
- shared layout integration and project selection contract;
- 3D public adapter/contract acceptance;
- planning/task documents, Git, and acceptance.

**Session 1 exit gate**

- P0-P8 must-have acceptance is evidenced; safe/unsafe/unsupported/error/not-
  evaluated/stale states agree across UI/API/export; delayed responses cannot
  replace current results; quick and project journeys pass live;
- 3D golden fixture, selection identity, large-scene baseline, browser widths,
  WebGL fallback, and resource lifecycle pass;
- focused suites, the complete React check, and repository quick gate pass;
- rollback routes/adapters remain usable and the owner controls merge.

**Session 1 stop conditions:** unresolved input/result identity, unsafe status
regression, API/client shape ambiguity on a must-ship flow, 3D unit/identity
ambiguity, unrecoverable storage migration, or a failing main-process gate. Move
optional breadth out first; never waive these conditions to meet the session count.

### 12.3 Session 2 — Capability platform, cutover, and closeout

**Outcome:** the accepted workbench consumes one authoritative beam capability
catalogue through a thin API and curated React renderer; a non-coder can compose,
validate, save, reload, preview, and run one bounded approved beam workflow in an
explicit test/development activation; one AI tool manifest is generated from the
same source; canonical routes cut over only after integrated parity.

**Entry:** Session 1 exit gate passes and its contracts are accepted; Session 2
starts from that accepted base. P14/P15 remain blocked if P4/P6/P8 evidence is
missing.

**Wave 0 — parallel contract lock**

- **Parent:** freeze catalogue/schema version, approved beam adapter, one React
  client/type source, runner definition and quotas, internal feature flag, route
  cutover map, beam parity fixture, and shared-file locks.
- **Subagent A — library audit:** confirm capability/serialization/job-runner reuse
  boundaries and return the smallest P9/P12 service design without editing.
- **Subagent B — UI/API audit:** confirm the curated widget registry, composer
  ordered-step UX, P10 transport boundary, unknown-version behavior, and P11/P12
  fixture needs without editing.
- **Checkpoint:** parent publishes immutable P9-P12 contracts and exact fixtures.

**Wave 1 — catalogue vertical slice**

- **Parent:** own the thin FastAPI models/router registration, OpenAPI baseline,
  generated-or-validated React client contract, and cross-layer integration.
- **Subagent A — library catalogue:** implement P9 with one deterministic beam
  catalogue entry referencing canonical schema, semantics, adapter, examples,
  limitations, and compatibility behavior.
- **Subagent B — curated renderer:** implement the isolated P11 widget/result
  registry against the parent-frozen fixture. It may not invent fields or network
  types; live API integration waits for parent acceptance of P9/P10.
- **Checkpoint:** parent accepts P9, completes/accepts P10, connects P11, and proves
  current safe/unsafe parity plus unknown-field/version failure.

**Wave 2 — bounded workflow, then manifest/cutover**

- **Stage A — P12 first:** the parent integrates the internal feature-flagged
  validation/run transport and client types but may only prepare the cutover map;
  it must not switch canonical routes or begin P14 acceptance. Subagent A
  implements the library-first P12 definition, allowlist, bindings, quotas,
  cancellation/idempotency, and audit record. Subagent B finishes live P11
  integration and implements the P12 template-first ordered composer, validation,
  save/load/export, preview, run progress, review stops, and errors against
  parent-owned contracts. It does not build a free canvas or edit App/routes.
- **P12 checkpoint:** workers stop editing P12; the parent integrates service,
  transport, and UI, then accepts only after safe/unsafe plus tampered, oversized,
  timed-out, cancelled, repeated, and default-disabled transport cases pass.
- **Stage B — P13 and P14:** only after P12 acceptance, Subagent A receives a
  follow-up to generate and validate the one P13 beam AI manifest from the
  accepted catalogue and workflow IDs/schema references. In parallel, the parent
  may execute P14 route cutover/redirect/rollback work. Subagent B performs
  focused parity/UAT corrections only within its owned feature paths.
- **Closeout:** all workers stop editing; the parent accepts P13/P14, runs the
  integrated P15 UAT matrix and one full repository gate, updates evidence/docs,
  and prepares the owner decision packet.

**Session 2 must ship**

- one versioned beam catalogue entry, thin read-only discovery API, and one
  authoritative React client contract;
- one curated schema-driven quick-beam input/result vertical slice with fallback;
- one template-first bounded beam workflow that validates, saves, reloads,
  previews, runs under explicit local/test activation, and stops unsafe/tampered/
  oversized/timed-out/cancelled/repeated cases;
- one deterministic beam AI tool manifest without chat or autonomous execution;
- canonical route cutover/redirect evidence, integrated UAT, quick/frontend/full
  gates, rollback evidence, verified merge readiness, and the owner-held release
  decision.

**Session 2 scope cuts**

- exactly one beam capability and one approved workflow; no broad catalogue or
  renderer migration;
- no generic node canvas, durable/background platform, public unauthenticated
  runner, plugins, webhooks, AI chat, provider selection, auth implementation,
  cloud collaboration, new element, or new calculation;
- additional generated tools, workflow templates, and legacy-code cleanup defer
  unless all must-ship gates already pass.

**Session 2 parent locks**

- capability semantic source and catalogue/schema versions;
- FastAPI main/router registration and OpenAPI/client contract;
- App, routes/navigation, feature flag, and legacy redirect map;
- shared status/result/export semantics;
- planning/task/evidence documents, Git, cutover, and final acceptance.

**Session 2 exit gate**

- P9-P13 single-beam vertical slice and P14 replacement parity pass;
- execution transport remains unavailable by default and is reachable only through
  explicit test/development activation; negative runner cases and review stops pass;
- all final checklist items applicable to the deliberately narrow scope have direct
  evidence; focused suites, frontend check, quick gate, and one full gate pass;
- no merge, release, branch deletion, public activation, or professional-use claim
  occurs without explicit owner approval.

**Session 2 stop conditions:** catalogue/schema duplication, unsafe or unknown field
rendering, reachable default execution transport, arbitrary path/import execution,
unbounded runner behavior, missing Session 1 parity, cutover regression, or a
failing full gate. Optional AI/tool breadth and cleanup are dropped before any
must-ship or safety gate.

## 13. Worker-ready packets

P0-P8 execute inside Session 1; P9-P15 execute inside Session 2. The packet
specifications below remain the exact scope and acceptance references for the
parent and follow-up subagent packets. They do not create additional sessions.

### P0 — Baseline, feature usefulness, and claim lock

**Objective:** establish current live behavior and freeze what is kept, merged,
held, or retired before editing UI.

**Primary paths:**

- `react_app/src/App.tsx`
- `react_app/src/components/pages/`
- `react_app/src/components/design/`
- `react_app/src/components/import/`
- `react_app/src/components/layout/`
- `react_app/src/components/viewport/`
- `react_app/src/hooks/`
- `react_app/src/store/`
- `fastapi_app/routers/`
- `Python/structural_lib/services/capabilities.py`
- fastapi_app/models/
- fastapi_app/openapi_baseline.json
- react_app/src/api/client.ts
- docs/reference/3d-json-contract.md
- this plan

**Required work:**

1. run the current quick-design and import-to-export flows live;
2. map every visible action plus dormant hook/client/endpoint candidate through
   the usefulness contract and classify it as exposed, internal, dormant, or
   superseded/dead;
3. record current deep links, browser history behavior, empty states, dead ends,
   destination/action counts, steps to first useful result, steps from import to
   a selected failed member, duplicate navigation, resume success, and task notes;
4. record 3D metrics on the maintained 153-beam sample, define a reproducible
   larger-scene fixture, and inventory the current source/service/renderer unit,
   axis, schema-version, and identity mappings;
5. verify current status semantics and exports for safe, unsafe, error, unsupported,
   not-evaluated, edited-after-result, and delayed-response cases;
6. audit complete request/response shapes for every exposed or candidate React
   client/hook and its FastAPI/OpenAPI model, not only path and method;
7. capture current route/bundle loading, time to a usable viewport, repeated
   project-switch memory, three viewport widths, and maintained-browser evidence;
8. propose the browser matrix, browser-verification mechanism, storage payload
   measurements, and storage-backend decision inputs for the relevant packets;
9. freeze the route migration map, feature/candidate matrix, contract-mismatch
   ledger, quantitative baseline, and P0 acceptance ledger in this plan.

**Non-goals:** no UI edits, new tests, feature removal, formula changes, or route
cutover.

**Pitfalls:** treating a component's existence as proof of a live feature; exposing
an unused hook whose payload no longer matches the API; treating batch completion
as PASS; trusting the stale prior-plan status table; measuring only jsdom behavior.

**Acceptance:** one evidence-backed visible/dormant keep/merge/hold/retire matrix,
reproducible functional/performance/task-flow baselines, a request/response and 3D
contract ledger, proposed browser/storage decisions, and no unproven claim in
later packets.

**Narrow verification:** current focused React tests, current FastAPI endpoint
smokes, and live browser notes; do not run the full gate for a read-only audit.

### P1 — Information architecture and route contract

**Objective:** finalize the workbench route/state model without changing feature
behavior.

**Owned paths:**

- this plan
- proposed `react_app/src/app/navigation.ts`
- proposed `react_app/src/app/routes.tsx`
- route-focused tests

**Required work:** define canonical routes, stage guards, legacy redirect table,
breadcrumbs/stage model, global versus project navigation, and deep-link behavior.
Produce low-fidelity wireframes for landing, quick workbench, every project stage,
selected-member inspection, and narrow review at the three P0 viewport widths.
Annotate primary action, next action, empty/error state, and progressive disclosure;
set measurable simplification targets from P0 and record conformance to the
owner-accepted section 7 target before P2. Request another owner decision only
for a material deviation.

**Non-goals:** visual restyling, store migration, page deletion, or feature logic.

**Pitfalls:** breaking refresh/deep links; exposing a project stage before its
prerequisite; maintaining separate desktop/mobile route arrays.

**Acceptance:** one typed route/navigation contract feeds all shell presentations;
every legacy route has a keep/redirect/retire decision and rollback route; the
reviewed wireframe set covers every critical journey without a dead end or
unprioritized wall of controls.

**Narrow tests:** route rendering, legacy redirects, active state, stage guards,
back/forward navigation.

### P2 — Visual tokens, primitives, and workbench shell

**Objective:** establish the compact professional shell that prevents further UI
duplication.

**Owned paths:**

- `react_app/src/index.css`
- `react_app/src/components/layout/`
- minimal proven primitives under `react_app/src/components/ui/`
- relevant component tests

**Required work:** introduce semantic tokens, density/typography/status rules,
shared app/workbench shell, toolbar/panel/status/field/empty-state primitives, and
one responsive navigation presentation from P1 configuration. Keep Three.js and
grid bundles lazy when the active route does not need them, and record
before/after browser screenshots at the three accepted widths.

**Non-goals:** migrating every page, creating a generic design system, adding a
theme marketplace, or changing calculations.

**Pitfalls:** global CSS regressions; replacing working components only for visual
uniformity; animation that obscures engineering state.

**Acceptance:** the shell renders current content without semantic change; shared
primitives each have at least three planned consumers; focus/reduced-motion/status
behavior is defined; parent-reviewed screenshots conform to the accepted P1
wireframes and show no material loading or bundle regression from P0. The owner
receives them in the Session 1 decision packet; a material visual/IA deviation
still requires an earlier owner decision.

**Narrow tests:** shell/navigation/primitives; `./run.sh frontend lint` and focused
Vitest files.

### P3 — Versioned workspace and project state

**Objective:** provide one reliable project context for routes, 3D, grid, results,
resume, and later workflow definitions.

**Owned paths:**

- proposed `react_app/src/store/workspaceStore.ts`
- proposed `react_app/src/types/workspace.ts`
- proposed `react_app/src/lib/projectStorage.ts`
- existing stores only where adapters are necessary
- state/storage tests

**Required work:** define project identity, monotonically increasing project/member
revision, schema version, normalized member data, selected member/floor/stage,
filters, dirty/save state, and result records bound to the exact input revision or
hash plus calculation/library/catalogue version. Every engineering edit atomically
invalidates dependent current results, geometry, alternatives, metrics, and export
eligibility. Previous results may remain only as visibly labelled history.

Choose localStorage or IndexedDB from P0 payload evidence; localStorage is limited
to preferences/small summaries if project payloads exceed its reliable role.
Implement atomic revisioned writes, debounced autosave with visible state,
last-known-good recovery, quota/eviction handling, explicit clear/export/import,
a defined schema-migration window, and multi-tab revision-conflict detection.
Provide session-level undo/revert for member inputs and bulk material changes;
raw imported files are not retained silently.

**Non-goals:** cloud sync, authentication, raw-file persistence, collaborative
editing, or deleting existing stores before consumers migrate.

**Pitfalls:** silently loading stale incompatible data; two stores disagreeing on
selection/status; localStorage size limits; non-atomic partial saves; another tab
overwriting a newer revision; persisting transient errors or prior results as
current truth.

**Acceptance:** reload restores an agreed project snapshot and revision; invalid,
unsupported, conflicting, quota-failed, or stale storage fails closed with clear
recovery; no changed input can retain a current/exportable result; quick design
and current project flow continue through adapters during migration.

**Narrow tests:** store transitions, result invalidation, schema migration window,
atomic save/load and last-known-good recovery, corrupt/quota/conflicting-tab
snapshot, selection synchronization, undo/revert, reset/export/import.

### P4 — Quick-design workbench migration

**Objective:** migrate the current single-beam feature set into a focused workbench
mode with progressive disclosure.

**Owned paths:**

- `react_app/src/components/design/DesignView.tsx`
- `react_app/src/hooks/useLiveDesign.ts`
- existing design/load/torsion/insight/export hooks
- new quick-design feature components
- focused tests

**Required work:** preserve normal inputs and live result, separate common from
advanced actions, unify result/status hierarchy, integrate 3D and alternatives,
keep export contextual, and expose clear reset/compare actions. Extend the API
client to accept an abort signal, capture input/request revision at dispatch,
apply a response only when it matches current input, and scope loading/error/finally
state to that request. Any edit invalidates current result and export eligibility;
alternatives are previewed and explicitly applied as a new input revision.

**Non-goals:** schema-driven rendering, project batch redesign, or new calculations.

**Pitfalls:** triggering multiple designs during intermediate edits; an older
response or finally handler overwriting newer result/loading state; hiding an
unsafe or stale result inside a collapsed panel; changing canonical units.

**Acceptance:** current valid/unsafe cases and current-revision exports remain
equivalent; delayed/out-of-order responses are ignored; cancelled requests cannot
alter current state; the common journey needs no advanced panel; every advanced
feature appears only when usable.

**Narrow tests:** existing `DesignView`, live-design, load, torsion, Pareto, export,
and status-focused tests plus cancellation, out-of-order response, and
edit-after-result cases; one live quick-design UAT.

### P5 — Project intake and 3D review migration

**Objective:** make import and validation feed directly into the visual project
workbench.

**Owned paths:**

- `react_app/src/components/import/`
- `react_app/src/components/pages/BuildingEditorPage.tsx`
- imported-beam hooks/store adapters
- workbench project-stage components
- focused tests

**Required work:** compact import/mapping, surface validation issues, create/update
project state, preserve stable source/member identity, open the 3D review stage,
synchronize selected member/floor with the grid and inspector, and preserve manual
correction flow. Imported raw files are processed transiently unless a separately
approved retention policy exists; corrections increment the member/project
revision and invalidate dependent artifacts.

**Non-goals:** new import formats, rewriting AG Grid, or running design before
validation is acknowledged.

**Pitfalls:** importing geometry without forces as ready-to-design; losing row edits
when switching stages; showing inferred/defaulted values without labels.

**Acceptance:** maintained sample and supported imports land in the project review
stage with matching member count, geometry, validation state, and selection across
3D/grid/inspector.

**Narrow tests:** import hooks/components/store selection and one live maintained
sample import-to-review UAT.

### P6 — Integrated project design, issue resolution, results, and export

**Objective:** turn batch design and dashboard into stages of the same project
without losing progress or selected context.

**Owned paths:**

- `react_app/src/components/pages/BatchDesignPage.tsx`
- `react_app/src/components/pages/DashboardPage.tsx`
- `react_app/src/components/design/BeamDetailPanel.tsx`
- batch/insight/export hooks
- project-stage components and tests

**Required work:** integrate selection/run/progress, maintain a visible issue queue,
separate completed/error/unsafe/not-evaluated/stale states, resolve members through
the inspector, update project metrics after changes, and centralize exports.
Tag each batch/run response with run and project/member revision, discard or
quarantine mismatched responses, and keep retry/cancel/idempotency explicit.
Capture server request/run IDs for diagnostics. Preview and explicitly apply
member or bulk changes with undo/revert; increment project revision on commit.
Current exports must contain only current-revision results. A deliberately
requested draft export must label pending/stale/unsupported/not-evaluated members
and cannot present them as evaluated engineering evidence.

**Non-goals:** changing batch-engineering calculations, hiding failed rows, or
adding unrelated dashboard cards.

**Pitfalls:** applying only PASS results while making failures disappear; applying
a late batch to edited members; exporting stale values or one representative beam
as if it were project evidence; inconsistent result stores.

**Acceptance:** the maintained project flows from review through batch to results;
unsafe, not-evaluated, and stale members remain actionable and never count as
current PASS; old-run responses cannot alter the current revision; project/member/
draft exports are clearly separated and truthful; a failure can be correlated to
its member, run, and request.

**Narrow tests:** batch hook/page, dashboard/BOQ, inspector, export, status mapping;
live unsafe and mixed-status project UAT.

### P7 — Viewport decomposition with behavior parity

**Objective:** split the existing large 3D component into stable internal layers
without changing its public behavior.

**Owned paths:**

- `react_app/src/components/viewport/`
- `react_app/src/hooks/useBeamGeometry.ts`
- `react_app/src/hooks/useGeometryAdvanced.ts`
- docs/reference/3d-json-contract.md
- WebGL/resource tests where practical

**Required work:** first reconcile and version the source/canonical/renderer unit,
axis, schema, and stable-identity contract in section 9.6. Establish a Python to
FastAPI to TypeScript golden fixture, then establish scene, layer, camera,
selection, controls, fallback, and resource-lifecycle boundaries; preserve
existing modes and props or provide a reviewed compatibility adapter.

**Non-goals:** visual redesign, new scene layers, renderer replacement, or geometry
math in React.

**Pitfalls:** changing axes/units; losing click selection; GPU resource leaks;
breaking reduced motion or context restoration.

**Acceptance:** beam, full-rebar, and building scenes match the P0 functional
baseline and golden coordinate/identity fixture; selection IDs and all overlays
refer to the same member; route switching and repeated project loads do not show
unbounded resource growth; current consumers require no unreviewed semantic change.

**Narrow tests:** geometry hooks, scene-mode rendering, selection callbacks,
fallback/context-loss behavior, focused React build.

### P8 — 3D inspection layers, interaction, and performance

**Objective:** add the high-value visual inspection capabilities from section 9.

**Owned paths:**

- decomposed viewport layer/control files
- workbench 3D toolbar/legend/inspector integration
- geometry API/hooks only where an authoritative data gap is confirmed
- focused tests/fixtures

**Required work:** layer registry, isolate/filter, fit-to-selection, status and
utilization overlays, loads/dimensions where available, deterministic export views,
before/after comparison, and agreed performance changes based on profiling.
Verify maintained browsers, three accepted viewport widths, slow/API-unavailable
recovery, lazy route delivery, deterministic browser screenshots/interaction, and
route/3D/grid bundle and memory comparisons against P0.

**Non-goals:** decorative effects, invented engineering geometry, PyVista, or adding
all possible layers in one packet.

**Pitfalls:** status color mismatch; excessive meshes/draw calls; unreadable labels;
3D-only access to critical information.

**Acceptance:** each layer has authoritative data and a legend; selected/critical
members synchronize with non-3D views; baseline, delivery, maintained-browser,
responsive, and large-scene gates pass; WebGL fallback preserves critical
information.

**Narrow tests:** layer availability, selection/filter synchronization, status
legend, deterministic camera state, maintained sample and large-scene live UAT.

### P9 — Versioned application workflow catalogue

**Objective:** extend the existing capability/semantic truth into a transport-neutral
catalogue suitable for API discovery, curated UI rendering, and controlled tools.

**Owned paths:**

- `Python/structural_lib/services/capabilities.py`
- proposed `Python/structural_lib/services/workflow_catalog.py`
- `Python/structural_lib/services/serialization.py`
- service exports and focused Python tests

**Required work:** define catalogue/version records and compatibility rules,
reference canonical models and semantic contracts, register one beam design
capability, include prerequisites/next-actions/visualization affordances/examples,
validate registry uniqueness, and provide deterministic serialization plus
supported-version migration fixtures.

**Non-goals:** React metadata, FastAPI imports, arbitrary callable paths, changing
IS 456 math, or registering every capability before the beam slice works.

**Pitfalls:** duplicating field truth; binding directly to unstable implementation
functions; exposing protected text; weakening held-case language.

**Acceptance:** one immutable catalogue entry resolves to canonical schemas and an
approved service adapter; duplicates and unknown schema/handler IDs fail validation;
compatible/additive and breaking-version behavior is explicit and fixture-backed;
existing public capability APIs remain compatible.

**Narrow tests:** registry validation, serialization stability, semantic/field
reference integrity, example-input validation.

### P10 — Thin FastAPI catalogue transport

**Objective:** publish versioned catalogue discovery without moving domain truth
into FastAPI.

**Owned paths:**

- proposed `fastapi_app/models/catalog.py`
- proposed `fastapi_app/routers/catalog.py`
- `fastapi_app/main.py`
- focused FastAPI tests

**Required work:** read-only catalogue endpoint, schema/version fields, deterministic
serialization, cache/compatibility behavior, and explicit limitations/status text.
Update the OpenAPI baseline after handler tests, validate full request/response
shapes, and decide whether the existing generated SDK becomes the React client
source or only a generated type source. There must be one authoritative client
contract, not a second parallel API layer.

**Non-goals:** dynamic execution endpoint, UI hints invented in the router, auth,
or changing existing design routes.

**Pitfalls:** OpenAPI and catalogue schemas drifting; serializing Python callables;
turning discovery into a whole-standard claim.

**Acceptance:** catalogue response round-trips to the library source, unknown
versions fail clearly, generated/validated client shapes match OpenAPI and live
responses, and no duplicated engineering metadata exists in the router.

**Narrow tests:** catalogue response contract and full shape, version, schema
references, OpenAPI snapshot/client-type drift, empty/error behavior, existing
router integration smoke.

### P11 — Curated React schema renderer: beam vertical slice

**Objective:** prove that one catalogue entry can drive a professional quick-design
input/result flow without losing current behavior.

**Owned paths:**

- proposed `react_app/src/features/catalog/`
- proposed `react_app/src/features/workflows/`
- API client/types
- quick-design integration adapter
- focused tests

**Required work:** catalogue client, version handling, curated field/widget registry,
schema validation display, result/status renderer hooks, unsupported-field failure,
and beam quick-design parity comparison. Audit candidate/dormant hooks before reuse
and require a live contract test before exposing one through the renderer.

**Non-goals:** replacing every hand-built form, generic JSON Schema UI, or deleting
the current quick-design implementation.

**Pitfalls:** silently ignoring unknown fields; duplicate defaults/units; generic
forms that are technically complete but unusable; loading catalogue failure
blocking all fallback behavior.

**Acceptance:** the beam slice uses canonical names/units/schema and produces the
same safe/unsafe result semantics; unknown catalogue versions/fields fail visibly;
no dormant client is exposed without a passing live request/response contract; a
reviewed hand-built escape hatch remains possible.

**Narrow tests:** catalogue client, widget mapping, validation, unknown field/version,
beam parity cases, focused live UAT.

### P12 — Constrained no-code composer and allowlisted runner MVP

**Objective:** let a non-coding user assemble and run one approved beam workflow.

**Owned paths:**

- proposed library service workflow-definition/runner modules
- `Python/structural_lib/services/job_runner.py` only where extension is justified
- thin FastAPI models/router for validate/run if required
- proposed `react_app/src/features/automation/`
- focused Python/FastAPI/React tests

**Required work:** versioned workflow definition, curated ordered-step templates,
typed bindings, preflight validation, dry-run/sample preview, save/load/export,
allowlisted execution, review stop states, and execution log/provenance. Define
and enforce maximum steps, definition/input/project/batch/output sizes, timeout,
concurrency, cancellation, run ID, and retry/idempotency behavior. Keep execution
transport disabled/unavailable by default until negative gates and the separate
public-auth/rate-limit decision pass. Reject user filesystem paths/import targets,
sanitize names, and clean partial outputs without losing the audit trail.

**Non-goals:** arbitrary code, plugins, webhooks, free-form conditions, external
integrations, free-form node-canvas composition, a durable background engine, or
a generic drag-and-drop page builder.

**Pitfalls:** unsafe dynamic dispatch; unit mismatch; cycles; unbounded execution
or output; duplicated runs after retry; workflow-complete display masking unsafe
steps; definitions becoming executable code; exposing the route before protection.

**Acceptance:** a user can build `input -> validate -> beam design -> review ->
export`, reload it, run a sample, and inspect each step; unsafe and invalid cases
stop correctly; tampered handler IDs cannot execute. The same flow can be cancelled
and yields deterministic bounded outcomes for oversized, timed-out, and repeated
requests; filesystem/import targets cannot execute; disabled transport is not
reachable through normal navigation.

**Narrow tests:** definition schema, binding/unit validation, cycle rejection,
allowlist enforcement, safe/unsafe/oversized/timed-out/cancelled/retried runs,
run-ID/idempotency behavior, partial-output cleanup, save/load determinism,
composer keyboard and error behavior.

### P13 — Generated AI tool manifest readiness

**Objective:** prove that AI-facing tool descriptions can be generated from the
same catalogue without activating AI chat.

**Owned paths:**

- catalogue serialization/generator module
- generated manifest validation location selected in packet kickoff
- focused tests and documentation

**Required work:** map stable capability IDs and JSON Schemas to deterministic tool
descriptors, preserve limitations, validate manifest drift, and document the
user-review/execution boundary.

**Non-goals:** model integration, prompt orchestration, chat UI, autonomous execution,
or provider-specific product lock-in.

**Pitfalls:** generating descriptions that omit units/held cases; tool names drifting
from execution IDs; protected text exposure.

**Acceptance:** one command regenerates and checks the manifest; no manual duplicate
parameter list exists; manifest inputs validate against the same canonical schema.

**Narrow tests:** deterministic generation, schema identity, limitation presence,
unknown capability failure, drift check.

### P14 — Route cutover and legacy retirement

**Objective:** make the new workbench the default only after replacement parity.

**Owned paths:**

- `react_app/src/App.tsx`
- route/navigation configuration
- legacy pages/components approved for redirect or deletion
- link/index updates and route tests

**Required work:** switch primary CTAs/navigation, preserve agreed redirects, remove
duplicate shells and dead components, update imports safely, and record rollback.

**Non-goals:** removing useful deep links, deleting state migration code prematurely,
or unrelated cleanup.

**Pitfalls:** broken bookmarks; route loops; stale tests/docs; deleting files through
raw shell commands.

**Acceptance:** all canonical journeys use the new shell; legacy URLs resolve as
decided; no duplicated primary navigation or placeholder controls remain; file
deletion uses `scripts/safe_file_delete.py`.

**Narrow tests:** full React route suite, link check, production build, live legacy
URL and canonical-flow UAT.

### P15 — Integrated acceptance, evidence, and closeout

**Objective:** prove the complete product story and freeze evidence before merge or
release decisions.

**Required work:**

1. run fresh-user sample, quick design, imported project, unsafe resolution,
   resume, export, no-code safe/unsafe, and WebGL fallback journeys;
2. verify Python/API/React status and units agree;
3. compare the P0 simplicity/task-flow, route/bundle, 3D, browser, responsive,
   storage, and visual evidence and record known limitations;
4. prove stale-result invalidation, latest-request-wins, batch revision matching,
   full API/client shape compatibility, and 3D golden-fixture identity;
5. verify request/run correlation and useful recovery for API unavailable,
   storage quota/conflict/corruption, WebGL failure, and runner cancellation;
6. run focused suites, `./run.sh frontend check`, `./run.sh check --quick`, and one
   `./run.sh check` at the stable integrated milestone;
7. update user/developer docs and active-plan state;
8. prepare a scoped Git diff, before/after evidence, and owner decision packet.

**Non-goals:** merge, release, branch deletion, issue closure, or professional-use
approval without explicit owner authorization.

**Acceptance:** every program-level completion criterion in section 3.3 has direct
evidence; every current result/export is revision-bound; the accepted maintained
browsers and viewport widths pass; and no critical workflow depends on commentary
or a hidden manual step.

## 14. Verification ladder

### 14.1 During a packet

- run only the tests closest to changed behavior;
- use the pinned Node runtime through `./run.sh frontend ...`;
- use `.venv/bin/python` for direct Python commands;
- inspect live UI only for the flow owned by the packet;
- capture deterministic browser screenshots for visual/layout packets and use
  the P0 scene fixture for 3D packets;
- do not run the full repository gate after every edit.

### 14.2 Before a packet is accepted

- inspect the exact diff and confirm packet-owned paths;
- run focused unit/component/API tests;
- run relevant lint/type/build checks;
- demonstrate the packet's main-process outcome;
- verify no unsafe/not-evaluated status became PASS;
- verify edited/stale results are not current or exportable and delayed responses
  cannot replace a newer revision;
- verify changed API/client contracts by complete shape and perform the packet's
  accepted browser/viewport check where layout, WebGL, or interaction changed;
- return the worker format in section 19.3.

### 14.3 Integrated milestones

Within a wave, run focused checks only. Run the integrated gates at these bounded
points:

- Session 1 Wave 1 checkpoint: focused React/type/build checks for the changed
  shell/state/quick boundaries and the 3D contract/golden fixture;
- Session 1 exit: one `./run.sh frontend check` and one
  `./run.sh check --quick`;
- Session 2 Wave 1 checkpoint: focused Python/FastAPI/React contract and parity
  checks;
- Session 2 before cutover: one `./run.sh frontend check` and one
  `./run.sh check --quick`;
- Session 2 P15 closeout: one full `./run.sh check`.

Do not repeat the full gate inside a wave or run a repository-wide gate for each
individual packet.

### 14.4 Live UAT matrix

| Journey | Positive case | Required negative/recovery case |
|---|---|---|
| Fresh sample | Sample reaches 3D inspector and result | API unavailable shows useful recovery |
| Quick design | Maintained safe beam calculates and exports | Unsafe shear remains FAIL everywhere |
| Result freshness | Current-revision result drives 3D and export | Edit after result invalidates it; delayed old response is ignored |
| Import | Maintained project imports with correct count | Invalid/missing mapping blocks design clearly |
| Project design | Mixed project completes with visible issue queue | Failed/not-evaluated members do not disappear |
| API contract | Exposed client round-trips canonical shape | Dormant/mismatched client remains unavailable and fails visibly |
| Resume | Version-current snapshot restores | Corrupt/old/quota/conflicting-tab state fails closed and can recover |
| 3D | Select/isolate/layers/camera work with stable identity | Unit/axis/schema mismatch and WebGL loss retain a truthful fallback |
| No-code | Approved bounded beam workflow validates/runs | Cycle, unit mismatch, tampered path/handler, oversize, timeout, retry, cancellation, and unsafe result stop |
| Legacy URL | Redirect reaches canonical equivalent | Removed/unknown route shows intentional not-found state |

## 15. Data, safety, and provenance rules

- Canonical units come from the library/API contract and remain explicit.
- UI aliases are presentation-only and never change serialized canonical names.
- Unsafe, unsupported, error, and not-evaluated are distinct states.
- A workflow can complete technically while containing unsafe or review-required
  results; those states must remain visible.
- Saved projects and workflow definitions include schema/catalogue version.
- Every result is associated with the exact input/member/project revision or hash
  plus calculation/library/catalogue version; it is current only while that
  identity matches current inputs.
- Any engineering input edit invalidates dependent result, geometry, alternative,
  project metric, and export eligibility atomically. A retained prior result is
  labelled previous/stale and never counted or exported as current.
- Batch/WebSocket/SSE/REST responses apply only to the matching current run and
  project/member revision; transport cancellation does not replace this check.
- Exports fail closed for stale or pending data. Deliberate draft exports identify
  member versus project scope, revision, and every unsafe, unsupported, error,
  not-evaluated, pending, or stale state.
- User-facing failures have a stable recovery path and capture request/run ID when
  available without exposing raw tracebacks, paths, secrets, or protected text.
- Protected clause/table text must not be copied into public catalogue metadata.
- No UI or AI message may claim professional approval from software status.

## 16. Rollout and rollback strategy

1. Introduce the workbench under new routes while current routes remain intact.
2. Migrate quick design and project flow separately.
3. Keep adapters around existing stores/components until parity tests pass.
4. Add catalogue/API endpoints additively with explicit versions.
5. Migrate one beam schema-driven slice before any broad renderer adoption.
6. Expose the composer only after its validation gates; keep execution transport
   unavailable by default until runner negative tests and the separate public
   authentication/rate-limit decision pass.
7. Switch default navigation in P14.
8. Remove legacy files only after redirects, parity, and rollback evidence exist.

Rollback is packet-scoped:

- shell problems: restore old route target while leaving new route isolated;
- state problems: fall back to current in-memory stores and retain snapshot export;
- 3D problems: keep the existing public viewport adapter and disable the new layer;
- catalogue problems: retain current hand-built quick-design path;
- no-code problems: keep composer/runner route unavailable; saved definitions remain
  inert data;
- cutover problems: revert navigation/route cutover without reverting additive
  foundations.

### 16.1 Two execution branches and wave commits

The accepted planning branch `codex/ui-experience-foundation` merged through PR
#718 at `32b9f33b`. The fresh implementation branch
`codex/ui-workbench-session-1` was then created from that exact `origin/main`
head. The planning branch is history, not one of the two implementation sessions.

1. **Session 1 branch:** continue on `codex/ui-workbench-session-1`. Use separate
   conventional commits for Wave 0 evidence, Wave 1 foundations, Wave 2 product
   flow, and integrated evidence where changes are logically separable.
2. **Session 2 branch:** only after the Session 1 exit gate and verified green merge,
   create `codex/ui-platform-session-2` from updated main. Use separate commits
   for catalogue/API/renderer, bounded workflow/manifest, cutover, and evidence.

There are exactly two implementation branches/sessions, not one long-lived branch
and not seven packet pull requests. Internal wave commits retain rollback and
reviewability without adding merge overhead. Do not mix dependency upgrades,
stack Session 2 on an unaccepted Session 1 branch, rebase/force shared history, or
start later-wave implementation before its contract checkpoint.

If a critical exit condition remains unresolved, keep that session incomplete or
blocked; do not hide it in a third cleanup session. Optional scope removed by
sections 12.2/12.3 becomes explicit backlog only when necessary. Each commit,
push, pull request, merge, release, and branch deletion follows normal owner and
repository controls.

### 16.2 Parallel worktree isolation

Parallel branches are safe only when each is checked out in a separate Git
worktree. A branch is never checked out, staged, committed, merged, rebased, or
cleaned from another branch's worktree. No parallel task may switch the root
checkout away from `codex/ui-workbench-session-1`; it must create or reuse a
separate worktree. Before every implementation wave, the parent rechecks current
branch identity, worktree status, process/port ownership, and changed-path overlap.

The former merge-policy, Python-dependency, and React-dependency locks were
resolved on `main` before the Wave 0 baseline. `codex/social-preview` owns only
separate documentation-image work and has no current UIX overlap. Dependency
manifests remain out of scope by program rule, but `ImportView` and
`BuildingEditorPage` are available for later UIX waves under the normal packet
ownership map. Tests and dev servers must not overwrite another worktree's files
or kill its processes.
Before starting a local server, inspect the intended ports and use an isolated
port or an explicitly identified current-branch process.

## 17. Risk register

| Risk | Outcome | Containment |
|---|---|---|
| Visual cleanup becomes a rewrite | Long branch, regressions, no usable milestone | Staged route migration and packet-owned parity |
| Navigation consolidation hides useful power | Expert workflow slows down | Progressive disclosure, contextual inspector, command palette only after commands work |
| State split creates contradictory UI | 3D, grid, result, and export disagree | Versioned workspace source and temporary explicit adapters |
| Edited input retains an old result | Stale design appears current or is exported | Revision/hash-bound results, atomic invalidation, fail-closed export |
| Older async response arrives last | Newer inputs display older calculation | AbortSignal plus request/run revision and latest-result-wins |
| Status truth regresses | Unsafe result appears acceptable | P0 semantic lock and negative case in every affected packet |
| Dormant client/API schema has drifted | Newly exposed feature fails or sends wrong units/fields | P0 full-shape audit, one generated-or-validated contract source, live contract gate |
| 3D expansion harms performance | Project workflow becomes unusable | Profile first, layer registry, instancing only where proven, large-scene gate |
| 3D units, axes, or IDs drift | Geometry, selection, and overlays disagree | Versioned three-space contract and Python/API/React golden fixture |
| 3D becomes the only access path | Keyboard/non-WebGL users lose critical information | Synchronized grid/issue queue/inspector and fallback |
| Catalogue duplicates domain truth | UI/API/AI parameters drift | Reference existing semantic contract and canonical schemas |
| Generic schema UI is poor | Form is complete but confusing | Curated widget registry and hand-built escape hatch |
| No-code runner enables arbitrary execution | Security and integrity failure | Static allowlist, typed bindings, no import paths/expressions |
| No-code runner is unbounded or repeatable | Resource exhaustion or duplicate work | Explicit size/time/concurrency/output limits, cancellation, run ID, idempotency |
| AI readiness becomes AI product scope | Cost and risk expansion | Manifest generation only; chat/autonomy explicitly deferred |
| Saved projects become unreadable | User loses work after updates | Versioned migrations, portable export/import, fail-closed recovery |
| Local save is partial or overwritten | Project loses current work | Atomic revisioned writes, last-known-good recovery, quota and multi-tab handling |
| Two sessions become two uncontrolled rewrites | Large conflicts and difficult rollback | Two fresh branches, three contract-gated waves each, parent locks, and wave commits |
| Old plan remains mistaken authority | Workers repeat completed work | Mark old plan superseded and link this master plan |

## 18. Decisions deliberately deferred

These evidence-gated execution decisions are made in the named packet and block
dependent implementation:

- P0/P1: maintained browser/version matrix, three viewport widths, and the
  smallest repeatable browser-verification mechanism;
- P0/P3: project persistence technology based on measured payloads and the
  supported schema-migration window;
- P0/P10: generated SDK versus generated/validated type source, with one
  authoritative React API contract;
- P12: exact runner quotas for the approved local/bounded workflow fixture.

The owner must make separate decisions before activating:

- cloud accounts, project sync, organizations, or collaboration;
- raw uploaded-file retention;
- public plugins, webhooks, or external notifications;
- AI chat and model/provider architecture;
- additional element UI migration beyond current beam/project flow;
- server-side CAD/PyVista;
- mobile dense editing;
- public workflow marketplace or user-shared templates.

The owner-held decisions in the second list do not block UIX-001; the first list
does block only the named dependent packet.

## 19. Operating model

### 19.1 Ownership boundaries

- **Parent integrator:** plan authority, `App.tsx`, route cutover, shared contracts,
  cross-packet state/status truth, Git/GitHub, final acceptance.
- **Frontend role:** shell, workbench stages, visual primitives, state adapters,
  schema renderer, composer UI.
- **3D role:** viewport internal architecture, scene layers, performance, fallback;
  no calculation invention.
- **Library role:** capability/workflow catalogue and allowlisted service runner;
  no React/FastAPI imports and no pure-math scope expansion.
- **API role:** thin catalogue/execution transport and OpenAPI models; no duplicated
  domain truth.
- **Reviewer/tester concerns:** main-process parity, unsafe/not-evaluated truth,
  route/state/storage/runner negatives, integrated UAT.

Default to the parent performing integration and shared-boundary work. In each
macro session, Wave 0 uses two read-only audit subagents; later waves reuse at most
two bounded workers through follow-up packets only when contracts are frozen and
paths are disjoint. Do not create false parallelism across P9 -> P10 -> P11 or
P3 -> P4/P5/P6 dependencies. The parent independently inspects every result,
runs the integration gates, and may idle a worker when no safe packet is ready.

### 19.2 Shared-file locks

The parent owns these during integration:

- `react_app/src/App.tsx`
- shared navigation/route contract
- workspace schema and migration version
- React API client/type contract and status/export mappings
- 3D public contract and selection identity
- `Python/structural_lib/services/capabilities.py`
- catalogue schema version
- `fastapi_app/main.py`
- OpenAPI baseline and route registration
- planning/task/handoff documents

Workers must not concurrently edit a shared lock without an explicit handoff.

### 19.3 Required worker return format

```text
Session and Wave:
Packet:
Outcome:
Files changed:
Main-process behavior before/after:
Commands run and exact results:
Unsafe/not-evaluated/status verification:
Revision/freshness and API/3D contract verification:
Browser/viewport evidence when applicable:
Known limitations or follow-ups:
Diff risks for parent review:
Suggested conventional commit:
```

Workers do not merge, push, delete branches, close issues, or publish releases.

## 20. Packet prompt template

```text
Objective:
  Complete packet <ID> inside Session <1|2>, Wave <0|1|2> from UIX-001.

Exact owned paths:
  <paths>

Read first:
  docs/planning/ui-experience-foundation-master-plan.md sections <N>
  <target folder index files>

Constraints:
  - Preserve core -> IS 456 -> services -> FastAPI/React direction.
  - Use explicit units and canonical status semantics.
  - Bind results to current input/project revision and reject delayed stale output.
  - Use the accepted API shape and 3D unit/axis/identity contracts.
  - Keep the change surgical to the packet outcome.
  - Do not expose a feature without a complete workflow use.
  - Do not merge, push, release, or perform destructive Git/GitHub actions.

Non-goals:
  <packet non-goals>

Likely pitfalls:
  <packet pitfalls>

Acceptance:
  <measurable acceptance>

Narrow verification:
  <commands>

Return exactly:
  Session and Wave / Packet / Outcome / Files changed / Before-after /
  Commands and results / Status verification / Revision and contract verification /
  Browser evidence when applicable / Limitations / Diff risks / Suggested commit.
```

## 21. Execution ledger

Do not mark a session, wave, or packet complete from code presence alone. Update
these tables only after the parent reviews evidence.

| Macro session | Scope | State | Required exit |
|---|---|---|---|
| Session 1 | P0-P8 compact workbench and essential 3D | Accepted | Session 1 exit gate in section 12.2 |
| Session 2 | P9-P15 capability platform and cutover | Accepted | Session 2 exit gate in section 12.3 |

| Session | Packet | State | Evidence/commit | Notes |
|---|---|---|---|---|
| 1 | P0 | Accepted | Section 22 | Live baseline, usefulness, browser, API/state, and 3D lock |
| 1 | P1 | Accepted | Section 22 | Route map, targets, and three-width wireframes frozen |
| 1 | P2 | Accepted | `d336803c` | Live shell and typed navigation; three-width reachability and lazy-delivery browser gates pass |
| 1 | P3 | Accepted | `c270b6c1`, `0ccda406` | Durable revisioned state, recovery, autosave, and multi-tab conflict integration pass |
| 1 | P4 | Accepted | `2314bb1f` | Quick design is latest-request-wins and revision safe |
| 1 | P5 | Accepted | `616666f7` | Imported-project identity and durable resume are preserved |
| 1 | P6 | Accepted | `d56eae7c`, `322648f9` | Batch results, stage progression, dashboard, BOQ, and export are revision bound |
| 1 | P7 | Accepted | `024002ca` | GeometrySpaceV1 adapter and viewport decomposition preserve behavior |
| 1 | P8 | Accepted | `024002ca`, `bb5e8958` | Inspection, responsive fallback, resource metrics, and browser gates pass |
| 2 | P9 | Accepted | `54c279bc` | Immutable semantically validated beam workflow catalogue |
| 2 | P10 | Accepted | `54c279bc` | Thin typed discovery API preserves the canonical document |
| 2 | P11 | Accepted | `26e6d0c8` | Curated catalogue renderer owns the quick-beam input surface |
| 2 | P12 | Accepted | `332a2455` | Default-disabled bounded workflow validates, persists, runs, cancels, and stops unsafe output |
| 2 | P13 | Accepted | `50905cbe` | Provider-neutral beam manifest is generated from catalogue truth |
| 2 | P14 | Accepted | `cd48faf5` | Canonical routes, legacy recovery, rollback flag, and safe retirement pass |
| 2 | P15 | Accepted | [Session 2 acceptance](../verification/ui-experience-session-2-acceptance.md) | Integrated closeout and root-cause corrections |

## 22. Session 1 Wave 0 evidence and contract lock

This section is the accepted P0/P1 handoff for Wave 1. It consolidates the
parent live-browser baseline and the two read-only Terra audits. It freezes
product and transport boundaries; it does not claim that the confirmed defects
are already fixed.

### 22.1 Evidence basis

| Evidence | Result |
|---|---|
| Session 1 base | origin/main and the current branch started at 32b9f33b after PR #718 |
| Runtime | Python 3.11; Node 24.19.0; npm 11.17.0; Vite 7.3.6 |
| Primary live browser | Codex in-app Chromium 151 on macOS, DPR 1; no error/warning entries, with two informational WebGL context-loss notices during repeated route changes |
| P0 viewports | 1440 x 900, 1024 x 768, and 390 x 844 |
| API/client audit | Complete-shape inspection of exposed and dormant React clients/hooks against FastAPI models and OpenAPI; route/method coincidence was not treated as shape proof |
| Focused application evidence | Read-only source audit plus live quick, sample, editor, member-selection, empty-deep-link, and recovery journeys |
| Focused 3D checks | 12 Python geometry/sample tests and 4 useBeamGeometry React tests passed |
| Production build | 2,778 modules transformed in 5.14 seconds; TypeScript and Vite build passed |
| Maintained sample | 153 members across 6 stories; API payload 36,634 bytes; proposed minimal WorkspaceSnapshotV1 payload 36,319 bytes before results/history |
| Batch transport/control | Direct 153-member batch returned HTTP 200, 153/153 PASS, and 27,285 bytes in 10.6 ms; the live editor still displayed Designing after more than 34 seconds |

Production gzip baselines from the P0 build are:

- application index JavaScript 36.30 kB and shared CSS 13.12 kB;
- DesignView 11.52 kB;
- BuildingEditorPage JavaScript 9.44 kB and route CSS 32.16 kB;
- Three.js 185.67 kB and React Three Fiber/Drei 136.86 kB;
- AG Grid 224.11 kB.

The production landing route currently loads the application index, HomePage,
Framer Motion, React Three Fiber/Drei, and Three.js: about 1,394.8 kB raw and
404.2 kB gzip of JavaScript, plus the shared CSS. AG Grid remains route-lazy, but
the decorative landing canvas makes the 3D runtime eager. P2 must remove that
landing cost or defer it behind an intentional workbench action. P7/P8 compare
final route delivery against this baseline; no percentage improvement is claimed
before profiling.

### 22.2 Live task-flow and simplicity baseline

| Surface | Current live evidence | Main-process decision |
|---|---|---|
| Landing to quick result | Start Designing reached a visible PASS in one intentional action and 3.052 seconds in the warm local journey | Preserve a one- or two-action quick path, but bind the result to current inputs |
| Quick design desktop | 16 buttons, 11 form controls, 7 links, one Canvas, inputs/result/3D/alternatives/export simultaneously visible | Recompose into Input, Review, and Export states with one emphasized action per state |
| Quick design at 390 | The document reported no horizontal scroll while the right workspace was visibly outside the viewport; the fixed shell prevented recovery | Narrow review is a blocking P2/P4 requirement; dense editing may remain desktop-first |
| Import entry | 14 buttons, 4 controls, 7 links, and three overlapping progress/navigation presentations | Keep single/dual/sample intake, but show one stage model and one next action |
| Sample to editor | `/import?sample=true` reached the 153-member preview in 406 ms; Open Building Editor produced a visible Canvas in 1.766 seconds | Preserve; landing to sample review target is at most three intentional actions |
| Project editor | 15 buttons, 16 controls, 7 links, one Canvas, 153-row grid, materials, export, stage bar, toolbar, and dock in one fixed viewport | Make 3D/grid/inspector contextual regions inside one workbench |
| Project editor at 1024 | Canvas, grid, and actions remained present with no document overflow, but the grid exposed only a clipped subset of columns | Keep review usable; dense editing remains desktop-first |
| Project editor at 390 | No document overflow was reported, but the toolbar and critical actions were clipped by an overflow-hidden fixed workspace | P2 must keep save/recovery/status/next action reachable; do not promise dense grid editing |
| Sample batch completion | The batch API settled 153/153 PASS in 10.6 ms, while the live header and visible rows remained Designing for more than 34 seconds | Treat as a frontend state-settlement blocker in P3/P6; project result and export parity are unaccepted |
| Reload/resume | Reloading the populated editor retained the URL but produced No beams loaded; only a small Hub summary is persisted | Full project resume is absent and P3-blocking |
| Empty deep links | editor, batch, dashboard, and design/results remain on their URLs and provide a recovery CTA | Retain recoverability, then replace with typed stage guards and canonical redirects |
| Current navigation | TopBar and floating dock each expose the same five destinations; project pages add another four-step bar and import adds a second three-step signal | One typed global group plus one contextual project stage group |

The quantitative simplification targets are:

1. reduce five duplicated persistent destinations and ten duplicate entries to
   at most two primary global destinations in Session 1: Workbench and Projects;
2. render Import, Review, Design, and Results exactly once as project context;
3. show at most one emphasized primary action in each workbench state;
4. keep landing to quick useful result at two actions or fewer and landing to
   sample project review at three actions or fewer;
5. make selected failed/held member inspection a direct issue-queue or 3D/grid
   selection, not a route hunt;
6. make 390 px review, recovery, status, and next action fully reachable with no
   clipped critical content; dense grid editing remains desktop-first;
7. restore the last accepted project snapshot after reload and never display a
   retained result as current after inputs change.

### 22.3 Feature usefulness decisions

| Capability/surface | Classification | Wave decision |
|---|---|---|
| Landing orientation, quick entry, sample entry, real resume | Exposed; merge | One restrained landing/workbench entry |
| Quick beam design, checks, selected 3D detail, alternatives, export | Exposed; migrate | Preserve within the quick workbench after freshness repair |
| Single CSV, dual CSV, sample import, material overrides | Exposed; migrate | One project intake stage |
| Building 3D, grid, floor selection, selected member | Exposed; migrate | Core review/design workbench |
| Batch progress, issue resolution, project results, BOQ/export | Exposed; migrate | Contextual Design and Results stages |
| Load calculator and torsion | Exposed only in quick input | Progressive disclosure; no separate destination |
| TopBar, FloatingDock, workflow breadcrumb arrays | Superseded duplication | Replace with one typed navigation source after parity |
| Settings | Secondary exposed action | Retain only settings with an immediate visible effect |
| Beam detail page | Compatibility/deep-link candidate | Keep behind a shareable current-result identity or redirect |
| useAutoDesign duplicate hook | Internal/dormant | Do not expose; consolidate behind the P4 request coordinator |
| SSE useBatchDesign | Dormant/hold | Cannot truthfully represent HOLD, stale, unsupported, or not evaluated |
| useCSVTextImport | Dormant/hold | Sends a JSON body while the endpoint declares query input; reconcile or retire before exposure |
| Serviceability request/response fields | Dormant/hold | React contract is incomplete; no Session 1 UI exposure |
| useGeometryAdvanced | Dormant/hold | Request and response shapes do not match the current API |
| geometry/beam/3d | Legacy/hold | Do not use for the workbench; detailed beam uses geometry/beam/full |
| Cross-section endpoint | Contextual existing utility | No new layer until member/revision identity is proven |
| ModeSelectPage | Superseded/retire after redirects | No independent destination |
| ModernAppLayout | Superseded/retire or mine | Must not become a competing shell |
| Decorative effects, loads layer, comparison layer | Deferred | No Session 1 scope without authoritative data and performance evidence |

No implementation worker may turn a dormant item into a visible feature without a
new live contract and usefulness review.

### 22.4 Frozen route and navigation contract

| Current route | Session 1 canonical destination | Compatibility behavior |
|---|---|---|
| / | / | Keep as restrained landing |
| /start | /workbench | Redirect and preserve history/back behavior |
| /design | /workbench/quick | Delegate first, redirect after parity |
| /design/results | /workbench/quick with current result panel | Empty or stale result goes to quick input with an explicit message |
| /import | /workbench/projects/new | Delegate first, redirect after parity |
| /editor | /workbench/projects/:projectId/review | Missing project uses typed recovery, not an unlabelled empty editor |
| /batch | /workbench/projects/:projectId/design | Guard on imported project and current revision |
| /dashboard | /workbench/projects/:projectId/results | Guard on a settled run; never infer completion |

The stage order is Import -> Review -> Design -> Results. Export is an action in
Results, not a global destination. A selected member, floor, open inspector, and
result/run identity are addressable route or workspace state. Desktop and narrow
navigation consume the same typed configuration. Browser back/forward and refresh
must restore or fail closed through the same guards.

### 22.5 Accepted three-width wireframes

Landing and workbench entry:

~~~text
1440 / 1024
+---------------------------------------------------------------+
| StructLib                         Projects          Settings   |
+---------------------------------------------------------------+
| Structural workbench                                         |
| [Continue last project]  [New project]  [Quick beam]          |
| Recent project: name, saved time, stage, truthful status      |
| Supported scope and evidence statement                        |
+---------------------------------------------------------------+

390
+----------------------------------+
| StructLib              Settings  |
+----------------------------------+
| Continue last project            |
| [Continue]                       |
| [New project] [Quick beam]       |
| Supported scope / recovery note  |
+----------------------------------+
~~~

Quick workbench:

~~~text
1440
+---------------------------------------------------------------+
| Quick beam | save/current state | support/evidence | Export   |
+--------------------+-----------------------------+------------+
| Input groups       | 3D / section               | Result     |
| dimensions         | selected detail             | status     |
| materials          |                             | governing  |
| forces             |                             | checks     |
| [Design]           |                             | next action|
+--------------------+-----------------------------+------------+
| Alternatives or export tray opens only on request              |
+---------------------------------------------------------------+

1024
+---------------------------------------------------------------+
| Quick beam | state | primary action                             |
+--------------------+------------------------------------------+
| Collapsible input  | 3D / result                              |
+--------------------+------------------------------------------+
| Contextual result/check tray                                  |
+---------------------------------------------------------------+

390
+----------------------------------+
| Quick beam | state              |
| Input summary [Edit]            |
| [Design / Recalculate]          |
| Result status + governing check |
| Selected 3D or table fallback   |
| Checks [Open]  Export [Open]    |
+----------------------------------+
~~~

Project workbench:

~~~text
1440
+----------------------------------------------------------------+
| Project | Import Review Design Results | saved | primary action |
+--------+-------------------------------------------+-------------+
| Stage  | 3D / main canvas                          | Inspector   |
| rail   | selection, floor, truthful status layer   | member      |
|        |                                            | checks      |
+--------+-------------------------------------------+-------------+
| Issue queue / grid / run progress / results / export tray       |
+----------------------------------------------------------------+

1024
+---------------------------------------------------------------+
| Project | stage | saved | primary action                      |
+---------------------------------------------------------------+
| 3D / main review                                               |
+-------------------------------+-------------------------------+
| Issue/grid summary            | Selected-member inspector     |
+-------------------------------+-------------------------------+

390 review/recovery
+----------------------------------+
| Project | Review | saved state   |
| Floor/filter [Open]              |
| 3D summary or list fallback      |
| Selected member + status         |
| Governing issue / next action    |
| [Open checks] [Continue]         |
+----------------------------------+
~~~

The narrow layout does not promise dense 153-row editing. It does promise project
identity, save/recovery state, selection, status, critical issue review, and the
next safe action.

### 22.6 Workspace, result, and latest-request-wins contract

P3 owns WorkspaceSnapshotV1 with:

- schema version, project ID, project name, selected stage/member/floor;
- stable source/member IDs, normalized explicit-unit inputs, project revision,
  member revision, and input revision;
- dirty/save state, current snapshot metadata, last-known-good metadata, and
  migration origin;
- explicit member lifecycle: current, stale, pending, error, unsupported, or
  not_evaluated.

Every result, geometry, alternative, metric, and export record carries:

- input hash, input/member/project revision, request/run ID;
- calculation identity and library version;
- evidence and supported-case status;
- its explicit lifecycle and settled decision state.

An engineering input edit atomically makes all dependent records non-current
before a new request starts. A response or finalizer applies only when request ID,
input hash, and all relevant revisions still equal the active workspace. Older
responses may be retained only as labelled history. Every exposed fetch accepts
AbortSignal; abort is an optimization, while identity equality is the correctness
gate.

Export requires a current revision plus supported PASS evidence. Pending, stale,
error, unsupported, not_evaluated, HOLD, and FAIL all fail closed. The server
receives result identity and rejects mismatches; presentation fields alone never
establish exportability.

### 22.7 API-client and persistence decisions

FastAPI Pydantic/OpenAPI remains transport authority. Session 1 keeps one React
transport facade and adds only the exact quick, sample/import, batch, geometry,
and export contracts needed by the maintained journeys. Each migrated method
accepts AbortSignal and crosses a runtime-normalizing boundary with focused
request/response fixtures. The stale standalone generated TypeScript client and
dormant hooks are not treated as current truth. P10 may later replace the narrow
facade with a fully generated client after generator parity is proven.

Full project persistence uses native IndexedDB. The 36,634-byte raw sample is not
the upper bound because results, geometry references, revision history, and
last-known-good metadata must also be stored atomically. localStorage is limited
to small UI preferences and a last-project pointer. P3 uses one versioned project
record transaction, migration functions, a last-known-good record, portable
export/import, and BroadcastChannel conflict notices. Raw uploaded file bytes are
not retained.

### 22.8 Frozen 3D contract and essential layers

GeometrySpaceV1 freezes two explicit coordinate frames rather than pretending
the current building and local-detail paths share one universal transform:

- `GlobalSourceSpaceV1` uses metres with x = plan east, y = plan north, and
  z = elevation/up. Its only renderer boundary is
  `G(x, y, z) = (x, z, -y)` in Three.js world metres.
- `LocalBeamSpaceV1` uses millimetres with x = left support to right support,
  y = section width from center, and z = soffit upward. Its only local renderer
  boundary is `L(x, y, z) = (0.001x, 0.001z, 0.001y)`; placement then uses the
  selected member's global origin and basis. A global negative-y mapping must
  never be applied again to local detail coordinates.
- every transport declares `schemaVersion`, frame, units, axes, `memberId`,
  stable `sourceId`, display label, story, frame type, section, project/member/
  input revisions, and geometry input hash;
- `memberId` is the imported source `UniqueName`, not the current derived
  `Label_Story`. Grid row, selection, result, geometry, inspector, and overlay
  keys use that same identity; production payloads have no generated fallback;
- `geometry/beam/full` is the sole detailed beam contract for P7 and must receive
  the selected `memberId` instead of falling back to `B1/GF`;
- building transport must preserve identity/section and fail closed rather than
  silently skip malformed members before it becomes authoritative.

The golden fixture contains two canonical source members, their normalized
global and local payloads, exact renderer coordinates, and one known detailed
beam with outline, rebar, and stirrup positions. Assertions cover stable source
ID preservation, exactly one conversion per boundary, both transforms,
bounds/center, selection, member count, detail placement, revision/hash matching,
unknown-schema rejection, and visible fallback.

P8 must ship only selection synchronization, floor/frame filtering,
fit-to-selection, deterministic camera, non-WebGL access, and a truthful status
overlay after P6 revision binding. Utilization is conditional on a proven
revision-matched join. Loads, building dimensions, new cross-section inspection,
before/after comparison, decorative effects, and unprofiled instancing are
deferred.

The scene baselines are the maintained 153-member sample and a synthetic,
render-only 1,530-member fixture made by ten deterministic copies of that sample.
Each copy has `perf:<tile>:<source-id>` identity and a fixed source-metre offset;
it never feeds engineering calculations. P8 records load-to-usable time, frame
interaction, draw/resource counts available from the renderer, five project
switches, context loss/recovery, and memory trend before accepting optimizations.

### 22.9 Browser gate and known blockers

Chromium 151 is the maintained primary gate at all three P0 widths. Current
Safari on macOS receives 1440 x 900, 1024 x 768, and 390 px review/recovery smoke
coverage at the Session 1 exit. Firefox support is held, not claimed, until the
same deterministic sample replay exists. The in-app browser remains the smallest
repeatable Chromium mechanism; Safari uses a bounded manual/Web Inspector pass,
and no broad browser framework is added in Wave 1. WebGL loss currently has only
code-path evidence, so live fallback evidence remains an exit-gate requirement.

Wave 1 starts with these confirmed blockers:

1. REST quick hooks create abort controllers but do not pass their signals to
   `designBeam`; older responses and finalizers can replace newer state;
2. WebSocket, SSE, and project batch results carry no request/project/member/input
   revision identity, so delayed output cannot be rejected correctly;
3. current input edits can coexist with retained quick/project results and exports;
4. the stable sample run can remain visually Designing after its HTTP 200 response;
5. full project reload/resume is absent and status records cannot represent every
   non-exportable lifecycle explicitly;
6. the 390 px quick and project workspaces clip critical content without a
   recovery path;
7. imported source `UniqueName` is dropped, selected detail requests can default
   to `B1/GF`, and current building/local geometry use two undocumented frames;
8. the landing route eagerly loads Framer Motion, React Three Fiber/Drei, and
   Three.js for a decorative canvas;
9. `useGeometryAdvanced`, `useCSVTextImport`, serviceability UI fields, and SSE
   batch semantics are not live-contract ready.

### 22.10 Accepted P2/P3 foundation evidence

The parent accepted P2 at `d336803c` and P3 at `c270b6c1` plus `0ccda406` after
independent diff review and integration. The other active UI task first shared
the root checkout; the parent stopped overlapping writes, assigned its P3 work to
an isolated worktree/branch, reviewed its bounded commit, and then cherry-picked
it. Future parallel UI work must retain disjoint worktrees and path ownership.

- P2 exposes only Workbench and Projects globally, preserves the four typed
  project stages, keeps critical actions reachable at 1440, 1024, and 390 px,
  and removes eager Three/R3F, AG Grid, and Framer assets from the production
  landing request path.
- P3 persists WorkspaceSnapshotV1 atomically in IndexedDB, fails closed on an
  unknown schema, recovers the last known good revision, invalidates evidence on
  edits and undo/revert, autosaves dirty revisions, and blocks a higher external
  revision through BroadcastChannel conflict state.
- Focused and full React verification passed 197 tests plus lint and production
  build; `./run.sh check --quick` passed all 10 checks.
- Live Chromium UAT used real IndexedDB and BroadcastChannel behavior to prove
  save, reload/load, conflict notification, and deletion. The synthetic proof
  project was removed after validation.

P4-P8 are accepted in section 22.11. Session 2 remains a fresh-branch packet and
must not begin until the Session 1 reviewed head is merged green. No parallel
worker owns App.tsx, shared contracts, stores, API client, public viewport
contract, or this ledger without a fresh disjoint packet.

### 22.11 Accepted Session 1 P4-P8 closeout evidence

The parent accepted P4-P8 after integrated diff review, focused negative cases,
maintained-browser UAT, and repository gates. Session 1 retains logically
separable commits for quick design, import identity, project evidence, viewport
decomposition, inspection, and the final live-workflow root-cause repairs.

- P4 binds quick-design responses and exports to the exact input revision;
  cancelled, delayed, and superseded responses cannot become current.
- P5 preserves source/project identity through import, IndexedDB recovery, and
  route reload. P6 settles every member against its request, input, member, and
  project revision before enabling dashboard, BOQ, or export.
- The live 153-member batch exposed HTTP 431 because the former EventSource GET
  serialized the whole batch into a 60 KB request target. Large batches now use
  a JSON-body POST while retaining the same SSE event contract; the maintained
  sample settles 153/153 PASS and enables a current-revision 11,330-byte CSV.
- The same live pass found that route position overrode durable stage truth, the
  editor downgraded a restored results workspace to review, and the dashboard
  did not restore its compatibility rows. Navigation now derives completion
  from `WorkspaceSnapshotV1`, never regresses a later stage, and restores the
  153-member results/dashboard/BOQ after a direct reload.
- P7 freezes GeometrySpaceV1 source IDs, axes, units, and schema, fails closed on
  malformed/mismatched detail geometry, and decomposes the previous monolithic
  viewport without changing the public adapter. P8 synchronizes grid and 3D
  selection, floor/frame filtering, isolate, fit, status/utilization legend,
  deterministic camera, and non-WebGL DOM inspection.
- Chromium production UAT passed 1440, 1024, and 390 px with no horizontal
  clipping. The mobile control tray stays collapsed until requested while the
  critical selection and status overlay remains visible. Safari completed the
  desktop sample/editor smoke; exact responsive-width authority remains
  Chromium until Safari responsive automation is available.
- WebGL context loss exposed a truthful interruption state while DOM inspection
  remained available, then recovered one canvas. Five route cycles retained one
  canvas, 155 draw calls, 165 geometries, four textures, and returned to a
  27.4 MB heap after idle collection. The deterministic 1,530-member fixture
  remained interactive at 117.3 ms load-to-usable, 14.8 ms average frame time,
  1,226 draw calls, 1,236 geometries, and four textures.
- Validation passed 222 React tests, 374 FastAPI tests, React lint and production
  build, `./run.sh frontend check`, the 10/10 quick gate, and the integrated full
  repository gate. Optional loads/dimensions/comparison layers, Firefox support,
  GitHub Pages, release actions, and professional-use claims remain held.

### 22.12 Accepted Session 2 P9-P15 closeout evidence

Session 2 began from merged Session 1 commit `49d7780e` and completed the one-beam
capability platform without broadening into public automation or AI execution.

- P9/P10 publish one immutable catalogue and a thin discovery route whose
  complete serialized document equals the library source. P11 consumes curated
  field metadata without inventing engineering semantics; catalogue mode now has
  one input owner, with the manual surface retained only as an explicit fallback.
- P12 runs one allowlisted beam workflow only behind explicit development/test
  activation. It validates bindings and quotas, retains bounded idempotency,
  supports active cancellation, persists reviewed drafts, and stops unsafe
  results before export. P13 deterministically derives one provider-neutral tool
  descriptor without activating chat, a provider, or autonomous execution.
- P14 makes the workbench routes canonical, redirects retained legacy URLs with
  explicit recovery, preserves a build-time quick-route rollback, and retires
  five duplicate shells through the safe-delete workflow.
- P15 found and fixed three outcome-changing integration causes: React Strict
  Mode could cancel initial quick design without replacement; catalogue and
  manual inputs rendered concurrently; and project guards redirected before
  IndexedDB hydration. Focused regressions and live replay prove each corrected
  outcome.
- Live Chromium passed safe, unsafe, stale, recalculate, import, project design,
  direct-results resume, export, bounded workflow, legacy redirect, 390/1024/1440
  px, large-scene, and WebGL interruption flows. The maintained sample settled
  153 PASS / 0 FAIL with revision-bound project evidence.
- Verification includes 91 focused Python/FastAPI tests, 87 focused React tests,
  76 geometry/streaming tests, 29 React/API call signatures, 239 total React
  tests with lint/build, the 10/10 quick gate, and the final integrated gate.
  Detailed evidence and tooling limits are frozen in
  [UIX-001 Session 2 acceptance](../verification/ui-experience-session-2-acceptance.md).

Execution remains default-disabled outside explicit development/test activation.
Firefox, exact Safari responsive automation, GitHub Pages, release/tag/package
publication, and professional-use claims remain held.

## 23. Immediate kickoff checklist

Implementation must not start until the owner accepts this plan or supplies edits.
After acceptance:

1. refresh `origin/main` and confirm the intended branch/base;
2. run `./run.sh session brief --agent orchestrator` and `./run.sh session start`;
3. confirm the accepted plan and Terra-routing commits are present on the current
   Session 1 branch and keep later wave commits logically separable;
4. dispatch the two read-only Session 1 Wave 0 packets, integrate P0/P1 evidence,
   and freeze shared contracts before Wave 1;
5. execute Session 1 Waves 1-2 through follow-up packets and pass its exit gate;
6. merge Session 1 after its reviewed head and required checks are green, then
   create the Session 2 branch from updated main;
7. execute Session 2 Waves 0-2 and pass its full exit gate;
8. keep no-code execution unavailable by default; enable it only for explicit
   test/development UAT until a separate public authentication/rate-limit decision;
9. move only optional scope to backlog; never move a failed critical gate into a
   presumed third cleanup session;
10. do not release, delete branches, or make professional-use claims without the
    required owner approval.

## 24. Final acceptance checklist

- [x] Session 1 P0-P8 exit gate passed before Session 2 began.
- [x] Exactly two implementation sessions/branches were used; wave commits retain
      rollback and no critical work was hidden in optional backlog.
- [x] One canonical workbench shell and navigation model.
- [x] Fresh sample journey has no dead end.
- [x] Quick-design safe and unsafe cases remain truthful.
- [x] Import -> review -> design -> resolve -> results -> export passes live.
- [x] Returning project restores from versioned local state.
- [x] Results, geometry, alternatives, metrics, and exports are bound to the
      current revision; edited/stale data cannot appear current.
- [x] Cancelled, delayed, or prior-run responses cannot replace newer state.
- [x] Every exposed feature passes the usefulness contract.
- [x] Dormant hooks/clients remain unavailable until complete live API contracts pass.
- [x] No dead settings, placeholder, or command-palette action is exposed.
- [x] P1 wireframes and three-width before/after browser evidence are accepted.
- [x] 3D selection synchronizes with grid, issue queue, and inspector.
- [x] Versioned 3D units, axes, schema, and member identity pass the golden fixture.
- [x] Agreed scene layers have authoritative data and legends.
- [x] Browser, responsive, lazy-delivery, large-scene, and WebGL fallback gates pass.
- [x] Project persistence passes revision, migration, atomic-save, quota, corruption,
      last-known-good, and multi-tab conflict recovery.
- [x] Library capability/semantic truth is not duplicated in UI/API.
- [x] Catalogue is versioned and one beam slice is schema-driven.
- [x] No-code beam workflow validates, saves, reloads, runs within quotas, cancels,
      is idempotent where required, and stops unsafe/tampered/oversized cases.
- [x] Exactly one beam AI manifest is generated from the same catalogue, without
      activating AI chat.
- [x] Legacy routes redirect or retire according to the frozen map.
- [x] Focused suites and `./run.sh frontend check` pass.
- [x] `./run.sh check --quick` passes at integrated milestones.
- [x] One final `./run.sh check` passes at P15.
- [x] Live UAT evidence and known limitations are recorded.
- [x] Merge follows the verified-green policy; release, branch deletion, and
      professional-use claims remain owner-held.
