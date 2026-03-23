# Folder Audit — Repository Health & Documentation

**Type:** Planning
**Audience:** All Agents
**Status:** Complete
**Importance:** High
**Created:** 2026-03-23
**Last Updated:** 2026-03-24 (Session 91)

---

## Purpose

Systematic audit of every folder and subfolder in the repository to:
- Document what each folder contains and its purpose
- Identify stale, duplicate, or misplaced content
- Find cleanup opportunities (archive, delete, consolidate)
- Verify README/index coverage
- Plan improvements per area

## Scope

**Total:** ~369 directories, ~3,719 files (excluding caches/build artifacts)

### Top-Level Folder Inventory

| # | Folder | Files | Has README | Has index.json | Status |
|---|--------|------:|:----------:|:--------------:|--------|
| 1 | `Python/` | 279 | Yes | Yes (stale) | Batch 2 ✅ |
| 2 | `react_app/` | 79 | Yes | Partial (3) | Batch 3 ✅ |
| 3 | `fastapi_app/` | 35 | No | No | Batch 3 ✅ |
| 4 | `streamlit_app/` | 249 | Yes | No | Batch 3 ✅ |
| 5 | `scripts/` | 191 | Yes | Yes | Batch 5 ✅ |
| 6 | `docs/` | 2504 | Yes | Yes | Batches 7-10 ✅ |
| 7 | `Excel/` | 12 | Yes | No | Batch 4 ✅ |
| 8 | `VBA/` | 85 | Yes | No | Batch 4 ✅ |
| 9 | `agents/` | 39 | Yes | Yes | Batch 11 ✅ |
| 10 | `clients/` | 5 | No | No | Batch 1 ✅ |
| 11 | `tests/` | 26 | No | No | Batch 6 ✅ |
| 12 | `logs/` | 204 | Yes | No | Batch 1 ✅ |
| 13 | `metrics/` | 2 | No | No | Batch 1 ✅ |
| 14 | `git_operations_log/` | 3 | No | No | Batch 1 ✅ |
| 15 | `tmp/` | 6 | No | No | Batch 1 ✅ |
| 16 | `.github/` | ~15 | Partial | No | Batch 1 ✅ |
| 17 | `.claude/` | ~5 | No | No | Batch 1 ✅ |

### docs/ Subfolder Breakdown (largest area — 2504 files)

| Subfolder | Files | Notes |
|-----------|------:|-------|
| `reference/` | 1788 | 1760 are vendor/ETABS CHM files (30MB) |
| `_archive/` | 253 | Old sessions, planning, research |
| `research/` | 186 | 73 in navigation_study alone |
| `_internal/` | 47 | copilot-tasks, quality assessments |
| `planning/` | 40 | Active planning docs |
| `contributing/` | 33 | Contribution guides |
| `getting-started/` | 21 | Bootstrap, onboarding |
| `agents/` | 21 | Agent guides, session logs |
| `guidelines/` | 18 | Coding guidelines |
| `architecture/` | 13 | Architecture docs |
| `publications/` | 10 | Blog posts, findings |
| `learning/` | 9 | Learning materials |
| `verification/` | 8 | Verification docs |
| `guides/` | 7 | User guides |
| `git-automation/` | 7 | Git workflow docs |
| `_active/` | 5 | Active work items |
| `blog-drafts/` | 5 | Draft blog posts |
| `developers/` | 5 | Developer docs |
| `cookbook/` | 4 | Code recipes |
| `adr/` | 4 | Architecture Decision Records |
| `audit/` | 4 | Audit reports |
| `specs/` | 3 | Specifications |
| `legal/` | 3 | License, legal |
| `vba/` | 2 | VBA docs |
| `images/` | 1 | Images |
| `_references/` | 1 | External references |

---

## Audit Batches

Realistic plan — one batch per session, prioritized by impact.

### Batch 1: Quick Wins — Small Folders ✅
**Scope:** `clients/`, `metrics/`, `git_operations_log/`, `tmp/`, `logs/`, `.github/`, `.claude/`
**Goal:** Document purpose, flag cleanup, ~30 min

| Folder | Purpose | Files | Findings | Action |
|--------|---------|------:|----------|--------|
| `clients/` | Auto-generated SDK clients | 5 | No README, likely stale vs API | Add README, regenerate |
| `metrics/` | Historical project metrics | 2 | No README, only 2 snapshots ever | Add README, low priority |
| `git_operations_log/` | Manual git logs (Jan 2026) | 3 | Obsolete — superseded by `logs/` | Archive or delete |
| `tmp/` | Temporary files | 6 | Completed task artifacts, not gitignored | Clean + add to `.gitignore` |
| `logs/` | Hook output + CI logs | 204 | 181 hook logs, no rotation, tracked in git | Add rotation, consider `.gitignore` |
| `.github/` | GH config, CI, templates | ~30 | Stub claims "900+ lines" (actual: 95) | Fix stale claim |
| `.claude/` | Claude AI per-filetype rules | 6 | Duplicates `.github/instructions/` | Document or consolidate |

### Batch 2: Code Folders — Python Core ✅
**Scope:** `Python/structural_lib/` deep dive (codes, core, services, insights, reports, visualization)
**Goal:** Verify architecture layers, check for dead code, document module purposes
**Completed:** Session 91

### Batch 3: Code Folders — UI Layers ✅
**Scope:** `fastapi_app/`, `react_app/`, `streamlit_app/`
**Goal:** Component inventory, dead route detection, hook/component coverage
**Completed:** Session 91

### Batch 4: Excel & VBA ✅
**Scope:** `Excel/`, `VBA/` (all subfolders)
**Goal:** Document workbook/module inventory, check Python parity
**Completed:** Session 91

### Batch 5: Scripts Deep Dive ✅
**Scope:** `scripts/` (tiers, _lib, _archive, git-hooks)
**Goal:** Verify tier classification, find unused scripts, check _archive relevance
**Completed:** Session 91

### Batch 6: Tests ✅
**Scope:** `Python/tests/`, `tests/`, `fastapi_app/tests/`, `streamlit_app/tests/`
**Goal:** Test coverage map, find gaps, dead fixtures
**Completed:** Session 91

### Batch 7: Docs — Active Content ✅
**Scope:** `docs/planning/`, `docs/getting-started/`, `docs/architecture/`, `docs/contributing/`, `docs/agents/`, `docs/guidelines/`, plus `guides/`, `cookbook/`, `adr/`, `specs/`, `developers/`, `verification/`
**Goal:** Find stale docs, overlapping content, update outdated material
**Completed:** Session 91

### Batch 8: Docs — Research & Publications ✅
**Scope:** `docs/research/`, `docs/publications/`, `docs/blog-drafts/`, `docs/learning/`, plus `legal/`, `vba/`, `git-automation/`, `audit/`, `images/`
**Goal:** Archive completed research, consolidate findings
**Completed:** Session 91

### Batch 9: Docs — Archive & Internal ✅
**Scope:** `docs/_archive/`, `docs/_internal/`, `docs/_active/`, `docs/_references/`
**Goal:** Verify archive is organized, internal docs still relevant
**Completed:** Session 91

### Batch 10: Docs — Reference (Largest) ✅
**Scope:** `docs/reference/` (1788 files, 30MB)
**Goal:** Assess vendor/ CHM files, check reference docs freshness
**Completed:** Session 91

### Batch 11: Agents & Misc ✅
**Scope:** `agents/`, `agents/agent-9/`, `agents/roles/`
**Goal:** Document agent configuration, check for stale agent data
**Completed:** Session 91

---

## Audit Template (per folder)

For each folder audited, record:

```
### folder/path/

- **Purpose:** What is this folder for?
- **Files:** N files, M subfolders
- **README:** Yes/No/Stale
- **index.json:** Yes/No/Stale
- **Owner:** Who maintains this?
- **Freshness:** Last meaningful change date
- **Issues Found:**
  - [ ] Issue description
- **Actions:**
  - [ ] Action description
```

---

## Completed Audits

### Batch 1 — Quick Wins (Session 91)

#### `clients/`

- **Purpose:** Auto-generated SDK clients for the FastAPI backend
- **Files:** 5 files, 2 subfolders (python/, typescript/)
- **README:** No
- **index.json:** No
- **Owner:** Generated by `scripts/generate_client_sdks.py`
- **Freshness:** Initial scaffolds, never updated since creation
- **Content:** Python client (173 lines), TypeScript client (120 lines)
- **Issues Found:**
  - [ ] No README.md — agents won't know what this is
  - [ ] No `.gitignore` for generated output
  - [ ] Likely stale — clients may not match current API (35 endpoints, 75 schemas)
- **Actions:**
  - [ ] Add README explaining these are generated SDKs
  - [ ] Regenerate clients from current OpenAPI spec
  - [ ] Consider if these should be in `.gitignore` (generated artifacts)

#### `metrics/`

- **Purpose:** Historical project metrics snapshots
- **Files:** 2 JSON files
- **README:** No
- **index.json:** No
- **Owner:** `scripts/collect_metrics.sh`
- **Freshness:** Last updated 2026-01-23 (2 months stale)
- **Content:** `doc_consolidation_metrics.json` (consolidation baseline from Jan 13), `metrics_2026-01-10.json` (velocity, tech debt, coverage snapshot)
- **Issues Found:**
  - [ ] No README — purpose unclear to new agents
  - [ ] Only 2 snapshots ever taken — metrics collection not habitual
  - [ ] No automation to refresh periodically
- **Actions:**
  - [ ] Add README explaining metrics purpose and how to collect
  - [ ] Consider adding `collect_metrics.sh` to session end workflow
  - [ ] Low priority — functional but underused

#### `git_operations_log/`

- **Purpose:** Manual git operation logs from early sessions (Jan 2026)
- **Files:** 3 files (2 logs, 1 markdown narrative)
- **README:** No
- **index.json:** No
- **Owner:** None (manual, discontinued)
- **Freshness:** Last entry 2026-01-08 (11 weeks stale). Superseded by `logs/` hook output
- **Issues Found:**
  - [ ] Obsolete — `logs/` + `git_workflow.log` + hook output logs now serve this purpose
  - [ ] Only 1 day of logs ever captured
- **Actions:**
  - [ ] Archive to `docs/_archive/` or delete entirely
  - [ ] Low priority — 3 small files, no harm keeping

#### `tmp/`

- **Purpose:** Temporary working files
- **Files:** 6 files (1 script, 4 backup files, 1 PR body)
- **README:** No
- **index.json:** No
- **Owner:** None (ad-hoc)
- **Content:** `add_when_to_use.py` (completed task helper), `deleted_backups/` (4 safe_file_delete backups from Jan), `pr-body.md` (leftover PR template)
- **Issues Found:**
  - [ ] `add_when_to_use.py` — task completed, script no longer needed
  - [ ] `deleted_backups/` — SECURITY.md backups from Jan 23, safe to clean
  - [ ] `pr-body.md` — leftover from a PR workflow
  - [ ] No `.gitignore` rule for `tmp/` — these get tracked
- **Actions:**
  - [ ] Clean all files (they're historical artifacts)
  - [ ] Add `tmp/` to `.gitignore` to prevent future tracking
  - [ ] Low effort, minor cleanup

#### `logs/`

- **Purpose:** Git hook output logs and CI monitor
- **Files:** 204 files (181 hook_output logs, git_workflow.log, ci_monitor.log, README, migration-rollbacks/)
- **README:** Yes
- **index.json:** No
- **Owner:** `scripts/install_git_hooks.sh` (auto-generated by hooks)
- **Freshness:** Active — latest log is from today (2026-03-23)
- **Content:** Hook output logs span Jan 23 – Mar 23 (139 from Jan, 27 from Feb, 12 from Mar). Also `migration-rollbacks/` with 9 rollback folders from Feb 11-27.
- **Issues Found:**
  - [ ] 181 hook log files is excessive — no rotation policy
  - [ ] Jan alone accounts for 139 logs (77%)
  - [ ] Migration rollbacks from Feb — can these be archived?
  - [ ] `logs/` is tracked in git — these bloat the repo
- **Actions:**
  - [ ] Add log rotation: keep last 30 days, archive older
  - [ ] Consider adding `logs/hook_output_*.log` to `.gitignore`
  - [ ] Archive migration-rollbacks older than 60 days
  - [ ] Medium priority — actively growing, will become a problem

#### `.github/`

- **Purpose:** GitHub configuration — workflows, templates, instructions
- **Files:** ~30 files across 4 subfolders
- **README:** Partial (workflows/ has one)
- **index.json:** No
- **Owner:** Maintainers
- **Freshness:** Active — instructions updated regularly
- **Structure:**
  - `workflows/` — 16 CI/CD workflows (tests, security, governance, docker, etc.)
  - `instructions/` — 5 per-filetype instruction files (docs, python-core, react, streamlit, vba)
  - `copilot/` — Redirect stub → `copilot-instructions.md`
  - `ISSUE_TEMPLATE/` — 3 templates (bug, feature, support) + config
- **Issues Found:**
  - [ ] `copilot/instructions.md` is a redirect stub (30 lines) → `copilot-instructions.md` (95 lines). The stub says "900+ lines" but actual canonical file is 95 lines
  - [ ] `.claude/rules/` and `.github/instructions/` serve similar purposes (per-filetype rules). Some duplication between the two
  - [ ] `DEVELOPMENT_TIMELINE.md` in `.github/` — odd location, may belong in `docs/`
- **Actions:**
  - [ ] Fix "900+ lines" claim in copilot stub — actual is 95 lines
  - [ ] Audit overlap between `.claude/rules/` and `.github/instructions/`
  - [ ] Consider moving `DEVELOPMENT_TIMELINE.md` to `docs/`
  - [ ] Low priority — functional, minor inaccuracies

#### `.claude/`

- **Purpose:** Claude Code (claude.ai) per-filetype rules
- **Files:** 6 files in `rules/` subfolder
- **README:** No
- **index.json:** No
- **Owner:** Maintainers
- **Freshness:** Active — rules are current
- **Content:** 6 rule files matching `.github/instructions/` topics: docs, fastapi, python-core, react, streamlit, vba
- **Issues Found:**
  - [ ] Duplicates `.github/instructions/` — both define per-filetype rules for AI agents
  - [ ] Claude rules use `globs:` frontmatter; GitHub instructions use `applyTo:` — different formats, same intent
  - [ ] Content is largely identical between the two sets
- **Actions:**
  - [ ] Document the intentional dual-format setup (Claude vs Copilot)
  - [ ] Or consolidate into one canonical source with a sync script
  - [ ] Low priority — both work, just duplicated maintenance

### Batch 2 — Python Core (Session 91)

#### `Python/structural_lib/` — Overview

- **Purpose:** IS 456 RC beam design library — pure math, no I/O
- **Architecture:** 4-layer strict (core → codes/is456 → services → UI)
- **Files:** ~100 Python files + 3 Jinja2 templates + README
- **Total code lines:** ~32,000 (excluding stubs)
- **README:** Yes
- **index.json:** Yes (at `Python/index.json`) — STALE (file_count: 0, last_updated: 2026-01-21)

#### `Python/structural_lib/codes/is456/` — IS 456 Implementation

- **Purpose:** Pure math IS 456:2000 code implementations
- **Files:** 14 Python files, 6,927 lines
- **Key modules:** serviceability.py (1356), detailing.py (1189), flexure.py (923), torsion.py (533), shear.py (454), bond.py (391), durability.py (335), materials.py (369), column.py (326)
- **Issues:** None — well-structured, no I/O

#### `Python/structural_lib/codes/aci318/` & `codes/ec2/`

- **Purpose:** Placeholder stubs for future ACI 318 and Eurocode 2 implementations
- **Files:** 1 `__init__.py` each (2+2 lines, commented-out code)
- **Status:** Empty placeholders, planned for v1.0+
- **Issues:**
  - [ ] Consider removing until real implementation begins (or document clearly as "planned")

#### `Python/structural_lib/core/`

- **Purpose:** Base classes, data types, constants, validation — no IS 456 math
- **Files:** 15 files, 4,415 lines
- **Key modules:** validation.py (632), inputs.py (614), models.py (524), errors.py (523), data_types.py (497), types.py (321), results.py (313), constants.py (162), beam.py (273)
- **Issues:** None — clean foundation layer

#### `Python/structural_lib/services/`

- **Purpose:** Orchestration layer — api, adapters, export, BBS, pipeline
- **Files:** 27 files, 17,395 lines (LARGEST layer)
- **Key modules:** api.py (1980), adapters.py (1973), dxf_export.py (1820), report.py (1735), bbs.py (1134), beam_pipeline.py (924), stream_design.py (684)
- **Issues:**
  - [ ] 4 files over 1500 lines each — consider splitting if they grow more
  - [ ] api.py + adapters.py together are ~4K lines of orchestration

#### `Python/structural_lib/insights/`

- **Purpose:** Design intelligence — suggestions, optimization, code checks
- **Files:** 10 files, 2,742 lines
- **Key modules:** design_suggestions.py (685), smart_designer.py (635), code_checks.py (388), rebar_suggestions.py (344)
- **Issues:** None

#### `Python/structural_lib/reports/`

- **Purpose:** Jinja2 HTML report generation
- **Files:** 2 Python files (generator.py: 347, __init__.py: 46) + 3 Jinja2 templates
- **Issues:** None — compact module

#### `Python/structural_lib/visualization/`

- **Purpose:** 3D geometry generation for beam rebar/stirrup visualization
- **Files:** 2 files, 983 lines (geometry_3d.py: 939)
- **Issues:** None

#### `Python/structural_lib/_migration_fixtures/`

- **Purpose:** Test helper for migration scripts (fixture data)
- **Files:** 2 files, 10 lines
- **Issues:** None — correct location for test infra

#### `Python/structural_lib/` — Top-Level Files

- **43 backward-compat stubs:** Each <50 lines, re-exports from `services/`. Exist for `from structural_lib import X` compatibility. Examples: `flexure.py`, `shear.py`, `detailing.py`, etc.
- **Real top-level files:**
  - `__init__.py` (89 lines) — Package exports
  - `__main__.py` (1503 lines) — CLI entrypoint with full design workflow
  - `bbs.py` (50), `dxf_export.py` (53), `errors.py` (51) — Thin stubs
- **Issues:**
  - [ ] 43 stubs are legacy from flat→layered migration. Consider deprecation timeline
  - [ ] `__main__.py` at 1503 lines is large for a CLI — consider splitting into CLI subcommands

#### `Python/` — Supporting Folders

- **tests/:** 98 test files — unit (26), integration (40), performance (1), property (8), regression (8), data (4), fixtures (11)
- **examples/:** 18 files — CSV samples, workflow demos, example scripts
- **scripts/:** 2 files — `pre_release_check.sh`, `regenerate_golden_files.py`
- **Config:** pyproject.toml, pytest.ini, setup.cfg, .coveragerc, test_stats.json

#### Architecture Violations Found

- **2 RED violations:** `streamlit_app/utils/api_wrapper.py` and `rebar_optimization.py` import directly from `structural_lib.codes.is456.shear` — should go through services layer
- **28 YELLOW warnings:** Implicit unit conversions (`* 1000`, `* 1e6` patterns)
- **Actions:**
  - [ ] Fix 2 red violations — route through services/api.py instead
  - [ ] Audit 28 yellow warnings for correctness

### Batch 3 — UI Layers (Session 91)

#### `fastapi_app/` — FastAPI Backend

- **Purpose:** REST API + WebSocket bridge between React frontend and Python structural_lib
- **Files:** 35 files (4 root, 12 routers, 6 models, 7 tests, 2 examples, plus __init__ files)
- **README:** No
- **index.json:** No
- **Total lines:** ~7,500

**Routers (12):**

| Router | Lines | Purpose |
|--------|------:|---------|
| imports.py | 749 | CSV/ETABS import with GenericCSVAdapter |
| geometry.py | 625 | 3D rebar/stirrup geometry |
| insights.py | 371 | Design suggestions, checks |
| detailing.py | 317 | Rebar detailing |
| design.py | 308 | Beam design (IS 456) |
| websocket.py | 305 | Live design WebSocket |
| streaming.py | 289 | SSE streaming |
| rebar.py | 246 | Rebar editing/validation |
| analysis.py | 233 | Structural analysis |
| export.py | 233 | BBS/DXF/report export |
| optimization.py | 228 | Cross-section optimization |
| health.py | 170 | Health check + diagnostics |

**Models (5):** geometry.py (367), beam.py (319), optimization.py (208), analysis.py (172), common.py (149)

**Tests (7):** security (406), integration (387), endpoints (346), load (285), auth (242), streaming (174), websocket (165)

- **Issues:**
  - [ ] No README.md — should explain endpoints, Docker usage, auth setup
  - [ ] No index.json — agents can't quickly scan structure
  - [ ] `openapi_baseline.json` exists (good — used by `check_openapi_snapshot.py`)
  - [ ] auth.py (343 lines) at root — consider moving to a middleware/ folder if it grows

#### `react_app/` — React 19 + R3F Frontend

- **Purpose:** Modern 3D beam visualization and design interface
- **Files:** 65 source files (39 components, 10 hooks, 2 stores, 2 types, 3 utils, 1 api, etc.)
- **README:** Yes
- **index.json:** Partial (3 — components/, design/, viewport/)
- **Total TS/TSX lines:** ~8,500

**Hooks (9):**

| Hook | Lines | Purpose |
|------|------:|---------|
| useCSVImport.ts | 414 | CSV file/text/dual import + batch design |
| useInsights.ts | 241 | Design insights + code checks |
| useDesignWebSocket.ts | 236 | WebSocket live updates |
| useLiveDesign.ts | 208 | Live design state management |
| useGeometryAdvanced.ts | 170 | Building + cross-section geometry |
| useBeamGeometry.ts | 160 | 3D beam geometry |
| useRebarEditor.ts | 157 | Rebar editing |
| useExport.ts | 131 | BBS/DXF/report export |
| useAutoDesign.ts | 68 | Auto-trigger design on param change |

**Pages (5):** BuildingEditorPage (696), DashboardPage (178), BeamDetailPage (162), ModeSelectPage (123), HomePage (121)

**Key components:** Viewport3D.tsx (1036), ImportView.tsx (456), DesignView.tsx (435), FileDropZone.tsx (291), CommandPalette.tsx (271)

**Stores (2):** designStore.ts (87), importedBeamsStore.ts (53)

- **Issues:**
  - [ ] Viewport3D.tsx at 1036 lines — largest component, may benefit from splitting
  - [ ] `__fixtures__/migration/` (3 files) — test migration helpers, verify still needed
  - [ ] Missing index.json for hooks/, store/, pages/ subfolders
  - [ ] `dist/` folder is present — verify `.gitignore` includes it

#### `streamlit_app/` — Streamlit UI (Legacy/Parallel)

- **Purpose:** Multi-page Streamlit app for beam design, cost optimization, compliance, AI assistant
- **Files:** ~155 Python files + 120+ docs + static assets
- **README:** Yes (+ QUICK_START.md, API_INDEX.md)
- **Total Python lines:** ~28,000+

**Pages (8 active + 12 hidden/archived):**

| Page | Lines | Topic |
|------|------:|-------|
| 06_multi_format_import.py | 1985 | CSV/ETABS import (LARGEST) |
| 01_beam_design.py | 1180 | Main beam design |
| 02_cost_optimizer.py | 1035 | Cost optimization |
| 08_ai_assistant.py | 628 | AI chatbot |
| 03_compliance.py | 617 | IS 456 compliance checker |
| 04_documentation.py | 462 | Library docs viewer |
| 90_feedback.py | 385 | Feedback/contact |
| 05_3d_viewer_demo.py | 359 | 3D beam viewer |

**Components (12):**

| Component | Lines | Purpose |
|-----------|------:|---------|
| ai_workspace.py | **5103** | AI workspace (ENORMOUS) |
| visualizations_3d.py | 1148 | 3D Plotly visualizations |
| visualizations.py | 1111 | 2D Plotly charts |
| visualization_export.py | 698 | Export visualizations |
| beam_viewer_3d.py | 548 | Three.js beam viewer |
| preview.py | 499 | Design preview |
| inputs.py | 452 | Input forms |
| results.py | 426 | Results display |
| report_export.py | 408 | PDF/HTML report export |
| polish.py | 395 | UI polish helpers |
| smart_dashboard.py | 365 | Dashboard overview |

**Utils (37 files, ~12,500 lines):**

| Top utils by size | Lines |
|-------------------|------:|
| pdf_generator.py | 1147 |
| error_handler.py | 922 |
| api_wrapper.py | 910 |
| lod_manager.py | 862 |
| layout.py | 792 |
| session_manager.py | 732 |
| global_styles.py | 711 |
| styled_components.py | 625 |
| design_system.py | 580 |
| loading_states.py | 495 |

**AI module (4 files):** handlers.py (718), tools.py (313), context.py (173)

**Tests:** 45 test files

**Docs within streamlit_app/:** 105 archive files (agent-6 sessions, completed tasks), 12 research files

- **Issues:**
  - [ ] `ai_workspace.py` at **5103 lines** — CRITICAL, needs splitting into multiple components
  - [ ] `06_multi_format_import.py` at 1985 lines — page too large, extract logic to components
  - [ ] 105 archive docs inside `streamlit_app/docs/_archive/` — should be moved to `docs/_archive/streamlit/`
  - [ ] 12 hidden pages in `pages/_hidden/` + 2 in `pages/_archived/` — dead code? audit for removal
  - [ ] 37 utils files is large — some may be consolidatable (e.g., 3 separate plotly-related utils)
  - [ ] `utils/api_wrapper.py` has RED architecture violation (imports codes/is456 directly)
  - [ ] No index.json anywhere in streamlit_app/

### Batch 4 — Excel & VBA (Session 91)

#### `Excel/`

- **Purpose:** Excel-facing deliverables — workbooks, add-in, templates, snapshots
- **Files:** 12 files (4 workbooks, 1 add-in, 3 docs, 2 templates, 1 snapshot CSV, 1 README)
- **README:** Yes — clear and accurate
- **index.json:** No
- **Owner:** Maintainers

**Workbooks:**

| File | Size | Purpose |
|------|-----:|---------|
| BeamDesignApp.xlsm | 100 KB | App-style workbook for beam design flows |
| StructEngLib.xlam | 85 KB | User-facing add-in (intentionally versioned) |
| BEAM_IS456_CORE.xlsm | 22 KB | Core macro-enabled prototype |
| BEAM_IS456_CORE.xlsx | — | Macro-free variant |
| StructEng_BeamDesign_v0.5.xlsm | 18 KB | v0.5 milestone workbook |

**Subfolders:**

- `Templates/` — 2 files: `BeamDesignSchedule_vba.bas` (618 lines batch design VBA), README. Planned: QuickDesignSheet, ComplianceReport
- `snapshots/` — 1 file: `baseline_beam_design_v0.9.1.csv` (regression baseline), README
- `DevTemplate_Instructions.md` — 265-line developer template guide

- **Issues:**
  - [ ] 3 `.xlsm` workbooks — unclear which is the "current" primary. README lists all but doesn't indicate which to use
  - [ ] Templates/ has only 1 of 3 planned templates (Phase 1 incomplete)
  - [ ] No index.json for agent discovery
  - [ ] Snapshot is v0.9.1 — current version is v0.19.0, snapshot may be very outdated

#### `VBA/`

- **Purpose:** VBA implementation of IS 456:2000 beam design for Excel
- **Files:** 85 files across 6 subfolders + 2 top-level docs
- **README:** Yes — comprehensive (131 lines, includes module table, Mac safety guide, testing instructions)
- **index.json:** No
- **Owner:** Maintainers
- **Total VBA code lines:** ~13,400 (modules + ETABS + legacy + tests)

**Modules/ (20 files, ~5,146 lines) — Core calculation modules:**

| Module | Lines | Purpose |
|--------|------:|---------|
| M16_DXF.bas | 1329 | DXF drawing export |
| M15_Detailing.bas | 679 | Reinforcement detailing + anchorage |
| M06_Flexure.bas | 492 | Flexural design |
| M18_BBS.bas | 453 | Bar Bending Schedule |
| M13_Integration.bas | 412 | Integration layer |
| M09_UDFs.bas | 399 | Excel User Defined Functions |
| M17_Serviceability.bas | 387 | Deflection, cracking, slenderness |
| M19_Compliance.bas | 384 | IS 456 compliance checks |
| M14_Reporting.bas | 273 | Report generation |
| M11_AppLayer.bas | 243 | Application layer |
| M99_Setup.bas | 217 | Setup/installation |
| M02_Types.bas | 213 | User-defined types |
| M03_Tables.bas | 137 | IS 456 table lookups |
| M07_Shear.bas | 115 | Shear design |
| M05_Materials.bas | 114 | Material properties |
| M10_Ductile.bas | 107 | IS 13920 ductile detailing |
| M08_API.bas | 68 | Public API functions |
| M12_UI.bas | 66 | UI helpers |
| M01_Constants.bas | 29 | Constants |
| M04_Utilities.bas | 29 | Utility helpers |

**Tests/ (11 files, ~3,010 lines):**

| Test | Lines | Scope |
|------|------:|-------|
| Test_DXF.bas | 493 | DXF export |
| Test_Structural.bas | 484 | Core structural calcs |
| Test_Parity.bas | 384 | Python-VBA parity checks |
| Test_Detailing.bas | 304 | Detailing functions |
| Test_BBS.bas | 297 | Bar Bending Schedule |
| Test_Compliance.bas | 251 | Compliance checks |
| Test_RunAll.bas | 245 | Test runner |
| Test_Flanged.bas | 189 | Flanged beam calcs |
| Integration_TestHarness.bas | 127 | Integration tests |
| Test_Serviceability.bas | 125 | Serviceability |
| Test_Ductile.bas | 111 | Ductile detailing |

**ETABS_Export/ (10 files, ~1,740 lines):** v1 ETABS data export modules
**ETABS_Export_v2/ (30 files):** v2 ETABS export with production, config, one-click. Includes:
- 6 active `.bas` files (~2,157 lines)
- `Etabs_output/` — 5 sample CSV files from Jan 17 export
- `_archive/` — 15 files: session 31 diagnostics, trials, solutions
- 4 docs (README, GUIDE, 2 checklists)

**Legacy_2019_2021/ (9 files, ~3,244 lines):** Original 2019-2021 VBA modules. Has README, includes BeamType.bas (958), COLUMNS.bas (752), ShearWall.bas (487)

**Examples/ (2 files):** Example_Usage.bas (61), Installer_ImportAllModules.bas (167)

- **Issues:**
  - [ ] 2 corrupt artifact files: `VBA/ETABS_Export/.!34470!mod_Types.bas` and `.!35354!mod_Types.bas` — binary corruption residue, should be deleted
  - [ ] `ETABS_Export_v2/Etabs_output/` — 5 sample CSV files tracked in git. Should be in `.gitignore` or `examples/`
  - [ ] `ETABS_Export_v2/_archive/` — 15 session-31 debug files. Consider moving to `docs/_archive/vba/`
  - [ ] `Legacy_2019_2021/` — 3,244 lines of old code. README exists but no clear deprecation plan
  - [ ] `VBA_CRITICAL_GUIDE.md` (337 lines) at VBA root — significant overlap with README safety section
  - [ ] No index.json for agent discovery
  - [ ] Python parity: `Test_Parity.bas` exists (384 lines) — good, but unclear if it covers all 20 modules

### Batch 5 — Scripts Deep Dive (Session 91)

#### `scripts/` — Overview

- **Purpose:** Automation scripts for development, CI/CD, maintenance, and governance
- **Files:** 83 active scripts (60 Python, 23 Shell) + supporting files
- **README:** Yes — comprehensive (lists categories, key scripts)
- **index.json:** Yes — well-structured (tier0, 15 categories, workflows, deprecated)
- **automation-map.json:** Yes — task→script mapping, 83/83 coverage verified
- **Owner:** All contributors
- **Total active code lines:** ~24,500

**Tier 0 — Essential (5 scripts, used 95% of the time):**

| Script | Lines | Purpose |
|--------|------:|---------|
| ai_commit.sh | 184 | Commit and push (ALWAYS use this) |
| agent_start.sh | 315 | Session start |
| should_use_pr.sh | 439 | PR vs direct commit decision |
| recover_git_state.sh | 161 | Emergency git recovery |
| session.py | 1259 | Unified session management |

**Index categories (84 scripts mapped):**

| Category | Count | Key scripts |
|----------|------:|-------------|
| code_validation | 12 | check_streamlit (2366), check_governance (846), check_architecture (500) |
| git_workflow | 11 | ai_commit, safe_push (408), should_use_pr (439) |
| project_structure | 9 | generate_enhanced_index (799), validate_imports, check_scripts_index |
| documentation | 9 | check_docs (533), create_doc, generate_docs_index |
| v3_migration | 8 | migrate_python_module (511), migrate_react (469), batch_migrate (438) |
| testing | 7 | benchmark_api (798), external_cli_test, test_api_parity |
| session_management | 6 | session.py (1259), agent_start, validate_session_state |
| code_migration | 4 | safe_file_move (483), safe_file_delete (354) |
| api_validation | 3 | validate_api_contracts (607), check_api, check_openapi_snapshot |
| release | 3 | release, bump_version, check_version_consistency |
| ci_cd | 3 | ci_local, pre_commit_check, install_git_hooks |
| governance | 3 | governance_health_score, check_governance, audit_readiness_report |
| file_operations | 3 | safe_file_move, safe_file_delete, archive_old_files |
| streamlit_dev | 2 | check_streamlit (2366), profile_streamlit_page (632) |
| vba | 1 | run_vba_smoke_tests |

**Top 10 largest active scripts:**

| Script | Lines |
|--------|------:|
| check_streamlit.py | 2366 |
| session.py | 1259 |
| check_governance.py | 846 |
| audit_readiness_report.py | 814 |
| generate_enhanced_index.py | 799 |
| benchmark_api.py | 798 |
| profile_streamlit_page.py | 632 |
| check_ui_duplication.py | 618 |
| validate_api_contracts.py | 607 |
| check_performance_issues.py | 596 |

#### `scripts/_lib/` — Shared Library

- **Purpose:** Reusable utility modules for scripts
- **Files:** 4 Python files (722 lines total)
- `__init__.py` (75) — Package init with common imports
- `ast_helpers.py` (332) — AST parsing for Python analysis scripts
- `output.py` (206) — Colored terminal output formatting
- `utils.py` (109) — Shared file/path utilities
- **Issues:** None — clean, well-factored. Phase 4b plans to migrate 38 more scripts to use _lib

#### `scripts/_archive/` — Archived Scripts

- **Purpose:** Superseded or obsolete scripts preserved for reference
- **Files:** 93 files (61 Python, 32 Shell), ~26,447 lines total
- **Notable:** check_streamlit_issues.py (2204), worktree_manager.sh (454), end_session.py (441)
- **Issues:**
  - [ ] 93 archived scripts is a LOT — 26K lines. Consider periodic purge of truly obsolete ones
  - [ ] Some archived scripts may have been replaced by active versions (e.g., `end_session.py` → `session.py`)
  - [ ] No INDEX.md in _archive/ to explain what replaced what

#### `scripts/_vba_tools_archive_2025-01-17/`

- **Purpose:** Completed VBA Unicode repair tools (project done Jan 2025)
- **Files:** 5 files — 3 Python tools + README + INDEX
- **Status:** Completed project, properly archived with explanation
- **Issues:** None — well-documented archive

#### `scripts/git-hooks/` and `scripts/hooks/`

- **Purpose:** Git hooks installed by `install_git_hooks.sh`
- **git-hooks/:** `pre-commit` (72) blocks manual git commit, `pre-push` (69) blocks manual git push
- **hooks/:** `commit-msg` (111) validates commit message format
- **Issues:**
  - [ ] Two separate hook directories (`git-hooks/` and `hooks/`) — confusing. Should consolidate into one
  - [ ] `install_git_hooks.sh` (149 lines) — verify it installs from both dirs correctly

#### Scripts Health Summary

- **Validation:** `check_scripts_index.py` passes: 83/83 scripts mapped, 60/60 Python scripts have docstrings
- **automation-map.json:** Covers all 83 active scripts via `tasks` and `categories` entries
- **Coverage gap:** The unmapped-scripts check flagged 20 scripts — these are mapped via `categories` in `index.json` but not in the `tasks` section of `automation-map.json`. Both indexes agree on 83 total, so this is a cross-reference format difference, not a real gap
- **README claims 152 total scripts** — this counts active (83) + archived (93) - some overlap. Consider updating to clarify

- **Overall Issues:**
  - [ ] `check_streamlit.py` at 2366 lines is the largest script — consider splitting
  - [ ] Two hook directories (`git-hooks/` + `hooks/`) should be consolidated
  - [ ] `_archive/` at 93 files (26K lines) could use an INDEX explaining replacements
  - [ ] README says "152 scripts" — should clarify "83 active + 93 archived"

### Batch 6 — Tests (Session 91)

**4 test directories, ~65,500 total test lines, ~176 test files**

#### `Python/tests/` — Main Test Suite

- **Purpose:** Unit, integration, property, regression, and performance tests for structural_lib
- **Files:** 98 Python files across 7 subdirectories + 17 root-level test files
- **README:** No
- **index.json:** No
- **Total lines:** ~38,640
- **conftest.py:** 57 lines (shared fixtures)

**Subdirectories:**

| Directory | Files | Lines | Purpose |
|-----------|------:|------:|---------|
| unit/ | 26 | ~8,500 | Unit tests for individual modules |
| integration/ | 39 | ~14,500 | Integration tests across layers |
| property/ | 8 | ~2,100 | Hypothesis property-based tests |
| regression/ | 8 | ~2,400 | IS 456 critical regression, VBA parity |
| performance/ | 1 | 266 | Benchmark tests |
| data/ | 4 | — | Golden vectors (JSON), parity vectors, insights benchmark |
| fixtures/ | 11 | — | CLI fixtures, report golden HTML/JSON/CSV |

**Top unit tests by size:**

| File | Lines | Scope |
|------|------:|-------|
| test_models.py | 683 | Core models |
| test_serviceability.py | 669 | Deflection, cracking |
| test_adapters.py | 615 | GenericCSVAdapter |
| test_detailing.py | 593 | Rebar detailing |
| test_validation.py | 534 | Input validation |
| test_serialization.py | 514 | JSON serialization |

**Top integration tests by size:**

| File | Lines | Scope |
|------|------:|-------|
| test_cli.py | 1370 | CLI end-to-end (LARGEST test file) |
| test_bbs.py | 994 | Bar Bending Schedule |
| test_dxf_export_edges.py | 837 | DXF export edge cases |
| test_report.py | 709 | HTML report generation |
| test_api_contracts.py | 688 | API contract validation |

**Root-level "orphan" tests (17 files, ~7,500 lines):**

| File | Lines | Scope |
|------|------:|-------|
| test_visualization_geometry_3d.py | 764 | 3D geometry |
| test_testing_strategies.py | 646 | Meta-test strategies |
| test_calculation_report.py | 611 | Calculation report |
| test_clause_traceability.py | 488 | IS 456 clause tracing |
| test_audit.py | 467 | Readiness audit |
| test_performance_edge_cases.py | 450 | Perf edge cases |
| test_enhanced_inputs.py | 408 | Enhanced inputs |
| test_serialization_formats.py | 376 | Serialization formats |
| test_error_handling.py | 366 | Error handling |

**Property tests (Hypothesis-based):**
- `strategies.py` (335) — Shared Hypothesis strategies
- `test_slenderness_hypothesis.py` (352), `test_property_invariants.py` (310)

**Regression tests:**
- `test_critical_is456.py` (529) — Critical IS 456 regression vectors
- `test_parity_vectors.py` (410), `test_vba_parity.py` (261) — Python↔VBA parity

- **Issues:**
  - [ ] 17 root-level test files (~7,500 lines) not categorized into unit/integration/etc — orphans
  - [ ] No README.md or index.json — test organization undocumented
  - [ ] `test_testing_strategies.py` (646 lines) is a meta-test file — unusual, verify if still needed
  - [ ] `data/` and `fixtures/` contain golden files but no documentation on regeneration process

#### `tests/` — Top-Level Test Directory

- **Purpose:** Cross-cutting tests — Streamlit smoke tests, migration tests, script tests
- **Files:** 26 files, ~7,469 lines
- **README:** No
- **index.json:** No

**Structure:**

| Path | Files | Lines | Purpose |
|------|------:|------:|---------|
| apptest/ | 6 | ~1,060 | Streamlit page smoke + integration tests |
| fixtures/migration/ | 7 | — | Golden files for migration tests |
| integration/ | 1 | ~220 | Migration integration test |
| Root test files | 10 | ~5,600 | Script + component tests |

**Root-level test files:**

| File | Lines | Scope |
|------|------:|-------|
| test_check_streamlit_issues.py | 615 | check_streamlit.py validations |
| test_lod_manager.py | 564 | LOD manager (streamlit component) |
| test_visualizations_3d.py | 545 | 3D visualizations |
| test_session_manager.py | 517 | Session manager component |
| test_error_handling_safe_patterns.py | 499 | Error handling patterns |
| test_design_system_components.py | 497 | Design system components |

**apptest/ (Streamlit smoke tests):**
- `conftest.py` (312) — Streamlit page fixtures + browser helpers
- `test_integration_workflows.py` (261) — Cross-page workflows
- `test_all_pages_smoke.py` (161) — Smoke test all pages load

- **Issues:**
  - [ ] No README — unclear which tests belong here vs `Python/tests/` vs `streamlit_app/tests/`
  - [ ] Ownership ambiguous: root-level tests test streamlit utils, scripts, and components — split across concerns
  - [ ] `fixtures/migration/` — 7 golden files for migration tests — verify still needed post-migration
  - [ ] `apptest/` duplicates purpose of `streamlit_app/tests/` — consolidation candidate

#### `fastapi_app/tests/` — FastAPI Tests

- **Purpose:** FastAPI endpoint, auth, WebSocket, streaming, and load tests
- **Files:** 7 test files, ~2,150 lines
- **Already documented in Batch 3** — 7 files (security 406, integration 387, endpoints 346, load 285, auth 242, streaming 174, websocket 165)
- **Issues:** None additional beyond Batch 3 findings

#### `streamlit_app/tests/` — Streamlit Tests

- **Purpose:** Streamlit component, page, and integration tests
- **Files:** 45 test files, ~17,212 lines
- **Already documented in Batch 3** — briefly noted

**Top test files by size:**

| File | Lines | Scope |
|------|------:|-------|
| test_visualizations.py | 732 | Plotly visualization tests |
| test_session_manager.py | 703 | Session manager |
| test_page_smoke.py | 688 | Full page smoke tests |
| test_error_handler.py | 656 | Error handler |
| test_design_system_integration.py | 636 | Design system |
| test_ai_page.py | 609 | AI assistant page |
| test_loading_states.py | 543 | Loading states |
| test_cost_optimizer.py | 508 | Cost optimizer |
| test_enhanced_visualizations.py | 460 | Enhanced viz |
| test_multi_format_import.py | 453 | CSV import page |

- **Issues:**
  - [ ] 45 test files is comprehensive but overlap with `tests/` root-level tests (both test Streamlit components)
  - [ ] `test_session_manager.py` exists both here (703 lines) AND in `tests/` (517 lines) — DUPLICATION

#### Tests Health Summary

| Location | Files | Lines | README | index.json |
|----------|------:|------:|:------:|:----------:|
| Python/tests/ | 98 | 38,640 | No | No |
| tests/ | 26 | 7,469 | No | No |
| fastapi_app/tests/ | 7 | 2,150 | No | No |
| streamlit_app/tests/ | 45 | 17,212 | No | No |
| **Total** | **176** | **65,471** | — | — |

**Cross-cutting Issues:**
- [ ] Test files spread across **4 separate directories** — no single entry point or test guide
- [ ] Zero README files across all 4 test dirs — bad for discoverability
- [ ] `test_session_manager.py` duplicated (tests/ + streamlit_app/tests/) — 1,220 lines total
- [ ] `tests/` overlaps with `streamlit_app/tests/` for Streamlit component testing
- [ ] 17 "orphan" tests in Python/tests/ root — should be categorized
- [ ] No test data documentation — golden files in data/ and fixtures/ lack regen instructions
- **Actions:**
  - [ ] Add README to each test directory explaining scope and ownership
  - [ ] Consolidate Streamlit tests — decide between `tests/` and `streamlit_app/tests/`
  - [ ] Move 17 orphan root tests into appropriate Python/tests/ subdirs
  - [ ] Document golden file regeneration process (e.g., `regenerate_golden_files.py`)
  - [ ] Deduplicate `test_session_manager.py`

### Batch 7 — Docs Active Content (Session 91)

**12 active docs subdirectories, ~199 files total**

#### `docs/planning/` — Project Planning

- **Purpose:** Project plans, roadmaps, assessments, this audit doc
- **Files:** 41 files (38 .md + README + index.json + 3 research subdirs)
- **README:** Yes
- **index.json:** Yes
- **Subdirs:** `research-findings-validation/` (1), `research-platform/` (1), `research-visual-design/` (1) — each has 1 research summary

**Largest files:**

| File | Lines | Topic |
|------|------:|-------|
| ui-layout-implementation-plan.md | 1602 | UI layout plan |
| folder-audit.md | 753+ | This audit (growing) |
| project-needs-assessment.md | 1089 | Needs assessment |
| hygiene-suggestions.md | 1000 | Code hygiene |
| 8-week-dev-plan.md | 825 | Development plan |

- **Issues:**
  - [ ] 38 planning docs — some may be stale or completed (e.g., "8-week-dev-plan" from early sessions)
  - [ ] 3 research subdirs feel misplaced — research belongs in `docs/research/`
- **Actions:**
  - [ ] Review each plan for staleness, archive completed plans
  - [ ] Move `research-*` subdirs to `docs/research/`

#### `docs/getting-started/` — Onboarding & Tutorials

- **Purpose:** Bootstrap, installation, first-run guides, release notes
- **Files:** 21 files
- **README:** Yes
- **index.json:** Yes

**Key files:**

| File | Lines | Topic |
|------|------:|-------|
| colab-workflow.ipynb | 1886 | Google Colab tutorial (DUPLICATE in cookbook/) |
| releases.md | 894 | Release history |
| insights-guide.md | 536 | Design insights guide |
| colab-workflow.md | 514 | Colab tutorial (markdown) |
| design-suggestions-guide.md | 452 | Design suggestions |
| agent-bootstrap.md | ~380 | Agent bootstrap guide |

- **Issues:**
  - [ ] `colab-workflow.ipynb` duplicated in `docs/cookbook/` (1886 lines each)
  - [ ] `colab-workflow.md` AND `colab-workflow.ipynb` — two formats of same content
- **Actions:**
  - [ ] Remove duplicate `.ipynb` from cookbook/ (keep canonical in getting-started/)
  - [ ] Consider if both `.md` and `.ipynb` formats are needed

#### `docs/architecture/` — Architecture Documentation

- **Purpose:** Architecture diagrams, principles, data formats
- **Files:** 13 files (including dependencies.png)
- **README:** Yes
- **index.json:** Yes

**Key files:** `canonical-data-format.md` (360), `mission-and-principles.md` (291), `deep-project-map.md` (270)

- **Issues:** None — clean, well-indexed
- **Actions:** None needed

#### `docs/contributing/` — Contribution Guides

- **Purpose:** Development guide, coding standards, maintenance guides
- **Files:** 33 files (LARGEST active docs dir)
- **README:** Yes
- **index.json:** Yes

**Largest files:**

| File | Lines | Topic |
|------|------:|-------|
| development-guide.md | 1511 | Comprehensive dev guide |
| streamlit-maintenance-guide.md | 757 | Streamlit maintenance |
| agent-coding-standards.md | 743 | Agent coding standards |
| agent-collaboration-framework.md | 665 | Agent collaboration |
| streamlit-prevention-system-review.md | 607 | Prevention system review |
| streamlit-comprehensive-prevention-system.md | 503 | Prevention system docs |
| quickstart-checklist.md | 499 | Quick start checklist |

- **Issues:**
  - [ ] 33 files is large — potential overlap between guides (3 Streamlit-related docs)
  - [ ] `agent-coding-standards.md` may overlap with `.github/instructions/` and `.claude/rules/`
  - [ ] Multiple "prevention system" docs — consolidation candidate
- **Actions:**
  - [ ] Audit 3 Streamlit docs for overlap → merge if redundant
  - [ ] Cross-reference agent standards with instruction files

#### `docs/agents/` — Agent Guides & Sessions

- **Purpose:** Agent-specific onboarding, workflow guides, session history
- **Files:** 21 files across 2 subdirs
- **README:** Yes
- **index.json:** **No** ❌
- **Subdirs:** `guides/` (17 files), `sessions/` (2 subdirs with 3 files in `2026-01/`)

**Key files in guides/:**
- `agent-quick-reference.md`, `onboarding.md`, `error-resolution-guide.md`, `context-optimization.md`
- Various agent-specific guides (git-workflow, pr-workflow, test-strategy, etc.)

- **Issues:**
  - [ ] No `index.json` — agent discovery blocked
  - [ ] `sessions/` only has 3 files from Jan 2026 — abandoned? SESSION_LOG.md is now the canonical log
  - [ ] 17 guide files — some may be outdated from early sessions
- **Actions:**
  - [ ] Generate `index.json` for agents/
  - [ ] Archive `sessions/` if SESSION_LOG.md replaced it
  - [ ] Audit guides for staleness

#### `docs/guidelines/` — Coding & API Standards

- **Purpose:** Comprehensive coding guidelines and API standards
- **Files:** 18 files
- **README:** Yes
- **index.json:** Yes

**Heavy standards docs (all >1000 lines):**

| File | Lines | Topic |
|------|------:|-------|
| api-design-guidelines.md | 2616 | API design (LARGEST) |
| error-handling-standard.md | 1925 | Error handling |
| api-evolution-standard.md | 1681 | API versioning |
| documentation-standard.md | 1604 | Documentation standard |
| result-object-standard.md | 1427 | Result object pattern |
| function-signature-standard.md | 1342 | Function signatures |

- **Issues:**
  - [ ] 6 files over 1000 lines each — very dense. May be hard for agents to consume
  - [ ] `api-design-guidelines.md` at 2616 lines — consider splitting into focused docs
  - [ ] May overlap with `docs/contributing/` dev guide sections
- **Actions:**
  - [ ] Consider TOC or summary sections for lengthy standards
  - [ ] Cross-reference with contributing/ to eliminate overlap

#### `docs/guides/` — User Guides

- **Purpose:** User-facing guides for AI agents, ETABS VBA, code reuse
- **Files:** 7 files
- **README:** **No** ❌
- **index.json:** **No** ❌

**Files:** `ai-agent-coding-guide.md` (993), `etabs-vba-user-guide.md` (650), `code-reuse-and-library-structure.md` (591), plus 4 smaller guides

- **Issues:**
  - [ ] No README or index.json — discoverable only by browsing
  - [ ] `ai-agent-coding-guide.md` overlaps with `docs/agents/guides/` content
- **Actions:**
  - [ ] Add README + index.json
  - [ ] Consolidate AI agent guides into `docs/agents/guides/`

#### `docs/cookbook/` — Code Recipes

- **Purpose:** Quick recipes, CLI reference, Colab workflow
- **Files:** 4 files (README + 3 recipes)
- **README:** Yes
- **index.json:** **No** ❌

**Files:** `cli-reference.md` (469), `colab_workflow.ipynb` (1886 — **DUPLICATE**), `python-recipes.md` (392)

- **Issues:**
  - [ ] `colab_workflow.ipynb` is identical to `docs/getting-started/colab-workflow.ipynb` — 1886-line duplicate
  - [ ] No index.json
- **Actions:**
  - [ ] Remove duplicate `.ipynb`, add symlink or cross-reference
  - [ ] Generate index.json

#### `docs/adr/` — Architecture Decision Records

- **Purpose:** Architecture Decision Records (ADRs) for significant design choices
- **Files:** 4 files (README + 3 ADRs)
- **README:** Yes
- **index.json:** **No** ❌

**ADRs:** `001-csv-adapter-architecture.md`, `002-api-parameter-naming.md`, `003-result-object-standard.md`

- **Issues:**
  - [ ] Only 3 ADRs for a project this size — underused
  - [ ] No index.json
  - [ ] Many decisions documented elsewhere (guidelines, architecture) should have ADRs
- **Actions:**
  - [ ] Add retrospective ADRs for key past decisions (4-layer architecture, backward-compat stubs, Streamlit→React migration)
  - [ ] Generate index.json

#### `docs/specs/` — Specifications

- **Purpose:** Technical specifications for data formats
- **Files:** 3 files
- **README:** **No** ❌
- **index.json:** **No** ❌

**Files:** `csv-import-schema.md` (316), `v0.7-data-mapping.md` (306), `v0.9-job-schema.md` (126)

- **Issues:**
  - [ ] No README or index.json — invisible to agents
  - [ ] Versioned specs (v0.7, v0.9) — current version is v0.19.0, these may be very stale
- **Actions:**
  - [ ] Add README + index.json
  - [ ] Check if specs still match current implementation, archive if obsolete

#### `docs/developers/` — Developer Documentation

- **Purpose:** Platform guide, extension guide, integration examples
- **Files:** 5 files
- **README:** Yes
- **index.json:** Yes

**Files:** `platform-guide.md` (990), `extension-guide.md` (651), `integration-examples.md` (465)

- **Issues:** None — clean, well-indexed
- **Actions:** None needed

#### `docs/verification/` — Verification & Validation

- **Purpose:** Engineering verification examples and validation packs
- **Files:** 8 files
- **README:** Yes
- **index.json:** Yes

**Key files:** `examples.md` (1540), `validation-pack.md` (185)

- **Issues:** None — well-documented, critical for engineering trust
- **Actions:** None needed

#### Docs Active Content Summary

| Directory | Files | README | index.json | Issues |
|-----------|------:|:------:|:----------:|--------|
| planning/ | 41 | ✅ | ✅ | Stale plans, misplaced research |
| getting-started/ | 21 | ✅ | ✅ | Duplicate colab.ipynb |
| architecture/ | 13 | ✅ | ✅ | Clean |
| contributing/ | 33 | ✅ | ✅ | Overlap, 3 streamlit docs |
| agents/ | 21 | ✅ | ❌ | Missing index, stale sessions |
| guidelines/ | 18 | ✅ | ✅ | 6 files >1000 lines |
| guides/ | 7 | ❌ | ❌ | Invisible, overlaps agents/ |
| cookbook/ | 4 | ✅ | ❌ | Duplicate ipynb |
| adr/ | 4 | ✅ | ❌ | Only 3 ADRs, underused |
| specs/ | 3 | ❌ | ❌ | Likely stale, invisible |
| developers/ | 5 | ✅ | ✅ | Clean |
| verification/ | 8 | ✅ | ✅ | Clean |

**Cross-cutting Issues:**
- [ ] 5 directories missing `index.json` (agents, guides, cookbook, adr, specs) — agents can't auto-discover
- [ ] 2 directories missing README (guides, specs) — invisible to browsing
- [ ] Duplicate `colab_workflow.ipynb` across `getting-started/` and `cookbook/`
- [ ] Overlapping AI guide content across `guides/`, `agents/guides/`, `contributing/`
- [ ] `docs/guidelines/` has 10,595 lines in 6 standards docs alone — dense, consider summaries
- **Actions:**
  - [ ] Generate index.json for 5 missing dirs
  - [ ] Add README to guides/ and specs/
  - [ ] Deduplicate colab notebook
  - [ ] Consolidate AI agent documentation into `docs/agents/`
  - [ ] Add TOC/summary sections to lengthy guidelines

### Batch 8 — Docs Research & Publications (Session 91)

#### `docs/research/` — Research Studies

- **Purpose:** Research explorations, technology deep dives, design pattern analysis
- **Files:** 186 files (83 root .md files + 6 subdirectories)
- **README:** Yes
- **index.json:** Yes

**Subdirectories:**

| Directory | Files | Purpose |
|-----------|------:|---------|
| navigation_study/ | 73 | Raw JSON trial data from navigation UX study |
| literature-review/ | 12 | Academic literature reviews |
| 01-function-catalog-research/ | 7 | Function catalog research |
| _online-research/ | 6 | Online research summaries |
| in-progress/ | 4 | Active research topics |
| structural-automation-platform/ | 1 | Platform research |

**Top root-level research files by size:**

| File | Lines | Topic |
|------|------:|-------|
| live-3d-visualization-architecture.md | 3299 | 3D viz architecture (LARGEST) |
| 3d-technology-deep-dive-research.md | 2429 | Three.js, R3F deep dive |
| index-per-folder-efficiency-research.md | 2169 | Index per folder efficiency |
| api-design-pattern-analysis.md | 1593 | API design patterns |
| blogging-strategy-research.md | 1310 | Blog strategy |
| etabs-vba-implementation-plan.md | 1209 | ETABS VBA plan |
| agent-8-git-automation-comprehensive-research.md | 1191 | Git automation research |
| documentation-handoff-analysis.md | 1129 | Doc handoff analysis |

- **Issues:**
  - [ ] **navigation_study/ — 73 files of raw JSON trial data** — massive bloat, should not be in git. Total ~3MB of trial data
  - [ ] 83 root-level .md files — no categorization beyond filename, hard to navigate
  - [ ] Many research topics already implemented (3D viz, CSV import, API design) — findings should be archived
  - [ ] `live-3d-visualization-architecture.md` at 3299 lines — extremely long research doc
  - [ ] Mix of actionable findings and pure exploration — unclear which are "done"
- **Actions:**
  - [ ] Move `navigation_study/` raw data to `.gitignore` or external storage — 73 JSON files shouldn't be tracked
  - [ ] Archive completed research (3D viz, API patterns, CSV import) → `docs/_archive/research/`
  - [ ] Categorize remaining root files into subdirs by theme
  - [ ] Add "Status: Complete|Active|Abandoned" metadata to research files

#### `docs/publications/` — Blog Posts & Published Content

- **Purpose:** Polished blog posts and content strategy
- **Files:** 10 files across structured subdirectories
- **README:** Yes
- **Structure:**
  - `content-strategy.md` (420) — Publishing strategy
  - `01-smart-library/` — Blog post: intro to IS 456 library (draft 261 + outline 172)
  - `02-deterministic-ml/` — Blog post: deterministic vs ML (draft 253 + outline 191)
  - `03-sensitivity-analysis/` — Blog post: sensitivity analysis (draft 261 + outline 180)
  - `findings/` — 2 summary files

- **Issues:**
  - [ ] Well-structured but separate from `blog-drafts/` — potential overlap
  - [ ] `findings/` may overlap with research findings
- **Actions:**
  - [ ] Verify blog-drafts/ vs publications/ — should one be the canonical location?

#### `docs/blog-drafts/` — Draft Blog Posts

- **Purpose:** Blog post drafts (earlier stage than publications/)
- **Files:** 5 files (4 drafts + README)
- **README:** Yes

**Drafts:** All short (176-285 lines), covering topics like RC beam library, sensitivity analysis, deterministic vs ML

- **Issues:**
  - [ ] Overlaps with `docs/publications/` — both contain RC beam library and sensitivity analysis drafts
  - [ ] Unclear workflow: do drafts start here and graduate to publications/?
- **Actions:**
  - [ ] Define clear pipeline: `blog-drafts/` → `publications/` → published
  - [ ] Or consolidate into single `publications/` with status metadata

#### `docs/learning/` — Learning Materials

- **Purpose:** Internal learning guides for technologies used in the project
- **Files:** 9 files
- **README:** Yes

**Key files:** `docker-fundamentals-guide.md` (778), `v3-fastapi-learning-guide.md` (569), `automation-foundation-learning-guide.md` (469)

- **Issues:** None — appropriate size, well-organized
- **Actions:** None needed

#### `docs/legal/` — Legal Documents

- **Purpose:** Engineering certification templates, usage guidelines, verification checklists
- **Files:** 3 files
- **README:** No
- **Issues:**
  - [ ] No README — purpose unclear
- **Actions:**
  - [ ] Add brief README

#### `docs/vba/` — VBA Documentation

- **Purpose:** ETABS VBA journey narrative and production plan
- **Files:** 2 files (~762 lines combined)
- **README:** No
- **Issues:**
  - [ ] No README
  - [ ] May overlap with `VBA/README.md` and `docs/guides/etabs-vba-user-guide.md`
- **Actions:**
  - [ ] Cross-reference with VBA/ docs to avoid duplication

#### `docs/git-automation/` — Git Workflow Docs

- **Purpose:** Git automation documentation and research
- **Files:** 7 files
- **README:** Yes
- **Subdirs:** `research/` (2 files)
- **Issues:** None — compact, well-organized
- **Actions:** None needed

#### `docs/audit/` — Audit Reports

- **Purpose:** Audit readiness template and evidence bundles
- **Files:** 4 files (README, audit-readiness doc, evidence template, .gitkeep)
- **README:** Yes
- **Issues:** None — clean scaffold, awaiting first real audit
- **Actions:** None needed

#### `docs/images/` — Documentation Images

- **Purpose:** Images for documentation
- **Files:** 1 file (README.md only)
- **Issues:**
  - [ ] Contains only README — `architecture/dependencies.png` is the only image and it's stored in architecture/
- **Actions:**
  - [ ] Consider if this empty dir is needed, or move architecture images here

#### Docs Research & Publications Summary

| Directory | Files | README | Issues |
|-----------|------:|:------:|--------|
| research/ | 186 | ✅ | 73 raw JSON files (navigation_study), 83 uncategorized root files |
| publications/ | 10 | ✅ | Overlaps with blog-drafts/ |
| blog-drafts/ | 5 | ✅ | Overlaps with publications/ |
| learning/ | 9 | ✅ | Clean |
| legal/ | 3 | ❌ | No README |
| vba/ | 2 | ❌ | No README, potential overlap |
| git-automation/ | 7 | ✅ | Clean |
| audit/ | 4 | ✅ | Clean (scaffold) |
| images/ | 1 | ✅ | Empty (README only) |

**Cross-cutting Issues:**
- [ ] `docs/research/navigation_study/` — 73 raw JSON files is the single biggest repo bloat in docs/
- [ ] `blog-drafts/` vs `publications/` overlap — need clear pipeline or consolidation
- [ ] 83 uncategorized research files at docs/research/ root — hard to navigate
- [ ] 3 directories missing README (legal, vba, images)
- **Actions:**
  - [ ] Remove or .gitignore `navigation_study/` raw data (73 JSON files)
  - [ ] Archive completed research to `docs/_archive/research/`
  - [ ] Consolidate blog-drafts/ into publications/ with status workflow
  - [ ] Add README to legal/ and vba/
  - [ ] Add research file status metadata (Complete/Active/Abandoned)

### docs/ Root Files

| File | Lines | Purpose |
|------|------:|---------|
| SESSION_LOG.md | 10,217 | **Canonical session history** (91 sessions) — LARGEST file in repo |
| docs-index.json | 7,033 | Full docs index (auto-generated) |
| TASKS.md | 81 | Active task tracking |
| README.md | 263 | Docs overview and navigation |
| index.json | 128 | Folder index |
| docs-canonical.json | 96 | Canonical doc registry |

- **Issues:**
  - [ ] `SESSION_LOG.md` at 10,217 lines — will keep growing. Consider rotation (archive older sessions)

### Batch 9 — Docs Archive & Internal (Session 91)

#### `docs/_archive/` — Archived Documentation

- **Purpose:** Historical docs, completed research, old planning, superseded content
- **Files:** 253 files (247 .md files) across 14 subdirectories + 12 root files
- **README:** Yes (155 lines — documents archive structure and conventions)
- **index.json:** No

**Subdirectories:**

| Directory | Files | Content |
|-----------|------:|---------|
| 2026-01/ | 100 | 62 root session docs + agent-9-governance-legacy/ (38 files) |
| planning/ | 47 | Completed/superseded planning docs |
| research-completed/ | 32 | Completed research (all root files, no subdirs) |
| publications/ | 12 | Research summary, blog outlines, claims verification |
| planning-20260119/ | 8 | Planning snapshot from Jan 19 |
| research-sessions/ | 8 | Research session records |
| misc/ | 7 | Miscellaneous (ETABS, Excel FAQ, merge conflict guide) |
| research-phases/ | 6 | Research phase summaries |
| research-completed-2026-01/ | 5 | Jan 2026 completed research |
| research/ | 7 | Archived research docs |
| agents/ | 3 | Archived agent docs |
| contributing/ | 2 | Archived contributing docs |
| 2026-02/ | 1 | Feb archive (1 migration doc) |

**Root-level files (12):**

| File | Lines | Content |
|------|------:|---------|
| automation-improvements.md | 1497 | Automation improvement proposals |
| research-and-findings.md | 1018 | Compiled research findings |
| backward-compat-automation.md | 690 | Backward compat automation plan |
| session-log-2025-12-28.md | 640 | Old session log |
| tasks-2025-12-27.md | 577 | Old task list |
| TASKS_old_20260119.md | 471 | Old TASKS snapshot |
| tasks-history.md | 330 | Task tracking history |
| session-8-automation-review.md | 254 | Session 8 review |
| VALIDATION_COMPLETE.md | 238 | Validation milestone |
| v0.8-execution-checklist.md | 193 | v0.8 checklist |
| README.md | 155 | Archive overview |
| v0.7-requirements.md | 129 | v0.7 requirements |

- **Issues:**
  - [ ] 253 files is very large for an archive — some subdirs may contain duplicates across time periods
  - [ ] Multiple `research-*` subdirs (research/, research-completed/, research-completed-2026-01/, research-phases/, research-sessions/) — fragmented
  - [ ] `2026-01/` has 100 files — a full month of session docs, could be further compressed
  - [ ] No index.json — hard to search programmatically
  - [ ] Root-level files mix different time periods and topics
- **Actions:**
  - [ ] Consolidate research archives: merge `research-*` subdirs into single `research/` with date subdirs
  - [ ] Consider compressing `2026-01/` session docs into a summary + key artifacts only
  - [ ] Add index.json for programmatic search if needed
  - [ ] Low priority — archive is functional, just messy

#### `docs/_internal/` — Internal Project Documentation

- **Purpose:** Internal-only docs: copilot task specs, cost optimizer audits, quality assessments, strategic roadmap
- **Files:** 47 files
- **README:** Yes (60 lines)
- **index.json:** Yes (137 lines)

**Content areas:**

| Area | Files | Description |
|------|------:|-------------|
| copilot-tasks/ | 13 | VBA/xlwings copilot task specs and workflows |
| cost-optimizer-* | 8 | Cost optimizer audit, fix plans, prevention system |
| quality-assessments/ | 9 | 2026-01-04 quality assessment scripts + .gitignore |
| Root docs | 17 | Strategic roadmap, milestones, agent workflow, git governance |

**Top root files by size:**

| File | Lines | Topic |
|------|------:|-------|
| cost-optimizer-issues-round3.md | 1655 | Cost optimizer issues (round 3) |
| quality-gaps-assessment.md | 1292 | Quality gap assessment |
| project-milestones.md | 788 | Project milestones |
| cost-optimizer-complete-audit.md | 742 | Cost optimizer audit |
| cost-optimizer-fix-plan.md | 691 | Fix plan |
| cost-optimizer-issues-round2.md | 664 | Round 2 issues |

- **Issues:**
  - [ ] 8 cost-optimizer docs (3,959 lines total) — extensive debugging history. Consider consolidating into single summary + lessons-learned
  - [ ] `copilot-tasks/` — 13 files of VBA/xlwings task specs. May be stale if tasks are complete
  - [ ] `quality-assessments/2026-01-04/scripts/` — 8 Python scripts inside docs (unusual location). Should these be in `scripts/` or `tests/`?
  - [ ] `SESSION_13_PART_8_SUMMARY.md` — very specific session artifact, should be in _archive
- **Actions:**
  - [ ] Consolidate cost-optimizer docs into 1-2 summary docs
  - [ ] Verify copilot-tasks/ completion status — archive if done
  - [ ] Move quality assessment scripts to `scripts/` or `tests/` (code shouldn't live in docs)

#### `docs/_active/` — Active Work Items

- **Purpose:** Currently active work context docs
- **Files:** 5 files
- **README:** Yes (52 lines)

**Files:**

| File | Lines | Content |
|------|------:|---------|
| scripts-consolidation-plan.md | 419 | Scripts consolidation plan |
| session-30-summary.md | 499 | Session 30 summary |
| resumption-feb-27-2026.md | 169 | Feb 27 resumption context |
| next-moves-session-88.md | 115 | Session 88 next moves |
| README.md | 52 | Overview |

- **Issues:**
  - [ ] `session-30-summary.md` (499 lines) — session 30 is far in the past (current: 91). Should be archived
  - [ ] `next-moves-session-88.md` — 3 sessions stale. Superseded by `docs/planning/next-session-brief.md`?
  - [ ] `resumption-feb-27-2026.md` — ~1 month old, likely stale
  - [ ] Purpose overlaps with `docs/planning/` — unclear what belongs here vs planning/
- **Actions:**
  - [ ] Archive `session-30-summary.md` and `resumption-feb-27-2026.md`
  - [ ] Clarify _active/ vs planning/ — define which docs go where
  - [ ] Consider if this dir is even needed given planning/ exists

#### `docs/_references/` — External References

- **Purpose:** External reference materials and links
- **Files:** 1 file (README.md only — 64 lines)
- **README:** Yes
- **Issues:**
  - [ ] Contains only a README — effectively empty placeholder
- **Actions:**
  - [ ] Either populate with actual references or remove the empty dir

#### Docs Archive & Internal Summary

| Directory | Files | README | index.json | Issues |
|-----------|------:|:------:|:----------:|--------|
| _archive/ | 253 | ✅ | ❌ | Fragmented research archives, 100 files in 2026-01/ |
| _internal/ | 47 | ✅ | ✅ | 8 cost-optimizer docs, scripts in docs/ |
| _active/ | 5 | ✅ | ❌ | 3 of 4 docs are stale, purpose unclear vs planning/ |
| _references/ | 1 | ✅ | ❌ | Empty placeholder (README only) |

### Batch 10 — Docs Reference (Session 91)

#### `docs/reference/` — Reference Documentation

- **Purpose:** API reference, contracts, vendor documentation, deprecation policies
- **Files:** 1788 files (28 root files + vendor/ 1760 files)
- **README:** Yes (86 lines)
- **index.json:** Yes (212 lines)

**Root-level reference docs (28 files):**

| File | Lines | Topic |
|------|------:|-------|
| api.md | 2979 | **Main API reference** (LARGEST reference doc) |
| automation-catalog.md | 2833 | Automation script catalog |
| insights-api.md | 984 | Insights API reference |
| sdk-api-contract-v1.md | 918 | SDK API contract |
| vba-api-reference.md | 864 | VBA API reference |
| vba-udt-reference.md | 709 | VBA UDT reference |
| agent-automation-pitfalls.md | 623 | Agent automation pitfalls |
| fastapi-rest-api.md | 576 | FastAPI REST API reference |
| dxf-layer-standards.md | 462 | DXF layer standards |
| 3d-json-contract.md | 440 | 3D JSON data contract |
| api-stability.md | 395 | API stability guarantees |
| streamlit-validation.md | 388 | Streamlit validation reference |
| deprecation-policy.md | 358 | Deprecation policy |
| troubleshooting.md | 312 | Troubleshooting guide |
| error-schema.md | 255 | Error schema reference |
| is456-formulas.md | 233 | IS 456 formula reference |
| api-manifest.json | 203 | API manifest (machine-readable) |
| 3d-visualization-performance.md | 164 | 3D visualization performance notes |
| deferred-integrations.md | 140 | Deferred integrations list |
| known-pitfalls.md | 125 | Known pitfalls |
| bbs-dxf-contract.md | 106 | BBS/DXF data contract |
| library-contract.md | 92 | Library public contract |
| repo-health-baseline-2026-01-07.md | 53 | Health baseline (stale) |
| third-party-licenses.md | 41 | Third-party license list |

**Root reference total:** ~13,500 lines across 28 files — comprehensive and well-organized.

#### `docs/reference/vendor/etabs/etabs-chm/` — ETABS CHM Documentation

- **Purpose:** Decompiled ETABS API CHM (Compiled Help Manual) for offline reference
- **Files:** 1760 files (1680 .htm, 36 .gif, 19 .css, 7 .png, 2 .js, plus hhk/hhc/ico/meta files)
- **Size:** 30 MB
- **Origin:** CSI API ETABS v1.chm decompiled into browsable HTML

**File type breakdown:**

| Extension | Count | Purpose |
|-----------|------:|---------|
| .htm | 1680 | API documentation pages |
| .gif | 36 | Images |
| .css | 19 | Stylesheets |
| .png | 7 | Images |
| .js | 2 | Scripts |
| Other | 16 | Index (hhk, hhc), favicon, meta |

- **Issues:**
  - [ ] **30 MB of vendor documentation tracked in git** — this is the single biggest repo size contributor
  - [ ] 1760 files inflate file counts dramatically (accounts for 47% of all repo files)
  - [ ] CHM source file (`CSI API ETABS v1.chm`) also exists at `docs/reference/` root — double storage
  - [ ] This is a static vendor reference — never changes, doesn't need version control
  - [ ] Git LFS or external hosting would be more appropriate
- **Actions:**
  - [ ] **HIGH PRIORITY:** Move vendor CHM to Git LFS or external storage (S3, project wiki, etc.)
  - [ ] Remove decompiled `etabs-chm/` from git history (rewrite or add to `.gitignore`)
  - [ ] Keep only `CSI API ETABS v1.chm` as the single reference artifact, or link to CSI's official docs
  - [ ] This single change would reduce repo from ~3700 files to ~1940 files and save ~30MB

#### Reference Health Summary

| Area | Files | Lines | Status |
|------|------:|------:|--------|
| Root reference docs | 28 | ~13,500 | Well-maintained, comprehensive |
| vendor/etabs/etabs-chm/ | 1760 | N/A | **30 MB bloat — needs LFS or removal** |

**Cross-cutting Issues:**
- [ ] `api.md` at 2979 lines — very large, but authoritative and frequently referenced. Consider TOC if not present
- [ ] `automation-catalog.md` (2833 lines) may overlap with `scripts/index.json` and `scripts/automation-map.json`
- [ ] `repo-health-baseline-2026-01-07.md` — 11 weeks stale, single snapshot never updated
- **Actions:**
  - [ ] **Vendor CHM removal is the #1 repo health improvement** — 30MB + 1760 files
  - [ ] Verify automation-catalog.md vs scripts/ indexes for duplication
  - [ ] Update or archive stale health baseline

### Batch 11 — Agents (Session 91)

#### `agents/` — Top-Level Agent Configuration

- **Purpose:** Multi-agent collaboration framework — agent roles, workflow configurations, research knowledge bases
- **Files:** 39 files across 3 areas (root, agent-9/, roles/)
- **README:** Yes (125 lines)
- **index.json:** Yes (18 lines — minimal)
- **index.md:** Yes (11 lines)

#### `agents/agent-9/` — Governance Agent

- **Purpose:** Agent-9 is the automation/governance specialist — research, metrics, session management
- **Files:** 21 files (10 root docs, 3 archive, 6 research, 1 workflow, plus index.json/index.md)
- **README:** Yes (407 lines — comprehensive)
- **index.json:** Yes (87 lines)
- **index.md:** Yes (25 lines)

**Root docs:**

| File | Lines | Purpose |
|------|------:|---------|
| AGENT_9_IMPLEMENTATION_ROADMAP.md | 1158 | Full implementation plan |
| SESSION_TEMPLATES.md | 974 | Session start/end templates |
| AUTOMATION.md | 839 | Automation guidelines |
| RESEARCH_PLAN.md | 810 | Research plan |
| WORKFLOWS.md | 645 | Workflow definitions |
| KNOWLEDGE_BASE.md | 630 | Accumulated knowledge |
| METRICS.md | 597 | Metrics tracking |
| CHECKLISTS.md | 503 | Quality checklists |
| README.md | 407 | Agent overview |
| RESEARCH_QUICK_REF.md | 258 | Quick reference |

**Subdirectories:**

| Directory | Files | Purpose |
|-----------|------:|---------|
| research/ | 6 | Research findings, constraints, templates, process docs |
| _archive/ | 3 | Completed summaries (CURRENT_STATE, RESEARCH_COMPLETE, RESEARCH_PLAN) |
| workflows/ | 1 | LINK_GOVERNANCE.md (205 lines) |

- **Issues:**
  - [ ] 10 root docs totaling ~6,821 lines — very heavy for a single agent. Consider if all are current
  - [ ] `SESSION_TEMPLATES.md` (974 lines) may overlap with `scripts/session.py` automated session management
  - [ ] `RESEARCH_PLAN.md` and `RESEARCH_QUICK_REF.md` — are these still active or should results be archived?
  - [ ] `_archive/` has 3 completed summaries — proper use of archive pattern
- **Actions:**
  - [ ] Verify which docs are still actionable vs historical reference
  - [ ] Cross-reference SESSION_TEMPLATES with scripts/session.py to check for duplication

#### `agents/roles/` — Agent Role Definitions

- **Purpose:** Define 12 agent roles with responsibilities and capabilities
- **Files:** 14 files (12 role definitions + index.json + index.md)
- **README:** No (roles defined in individual files)
- **index.json:** Yes (92 lines)
- **index.md:** Yes (21 lines)

**Roles defined:**

| Role | Lines | Scope |
|------|------:|-------|
| GOVERNANCE.md | 831 | Governance specialist (**much larger than others**) |
| PM.md | 143 | Project management |
| DEVOPS.md | 140 | DevOps/infrastructure |
| DEV.md | 99 | Core development |
| TESTER.md | 97 | Testing |
| ARCHITECT.md | 79 | Architecture |
| RESEARCHER.md | 58 | Research |
| CLIENT.md | 51 | Client/SDK |
| UI.md | 51 | UI/frontend |
| INTEGRATION.md | 48 | Integration |
| DOCS.md | 31 | Documentation |
| SUPPORT.md | 31 | Support |

- **Issues:**
  - [ ] `GOVERNANCE.md` at 831 lines is 6x larger than the average role file (~90 lines) — disproportionate
  - [ ] No top-level README in roles/ — purpose only inferred from file contents
  - [ ] Role files vary wildly in detail (31 lines for DOCS vs 831 for GOVERNANCE)
- **Actions:**
  - [ ] Normalize role file depth — either expand small ones or trim GOVERNANCE
  - [ ] Add README to roles/ explaining the role framework

#### Agents Health Summary

| Directory | Files | README | index.json | Issues |
|-----------|------:|:------:|:----------:|--------|
| agents/ (root) | 3 | ✅ | ✅ | Minimal index |
| agent-9/ | 21 | ✅ | ✅ | Heavy docs (~7K lines), possible overlap with scripts/ |
| roles/ | 14 | ❌ | ✅ | No README, GOVERNANCE.md disproportionate |

**Cross-cutting Issues:**
- [ ] `agents/` vs `docs/agents/` — two separate agent documentation locations. `agents/` has role configs + agent-9 knowledge; `docs/agents/` has workflow guides and session logs. This split may confuse agents
- [ ] agent-9 has ~7K lines of docs for a single agent role — heavier than some entire modules
- **Actions:**
  - [ ] Clarify `agents/` vs `docs/agents/` — consider consolidating or adding clear cross-references
  - [ ] Trim agent-9 if any docs are superseded by centralized scripts/session tooling

---

## Full Audit Complete — Summary

### All 11 Batches ✅

| Batch | Scope | Key Finding |
|-------|-------|-------------|
| 1 | Small folders (7) | `logs/` needs rotation, `tmp/` needs .gitignore |
| 2 | Python core | 4-layer architecture solid, 2 RED violations, 43 stubs |
| 3 | UI layers | `ai_workspace.py` 5103 lines, fastapi lacks README |
| 4 | Excel/VBA | 2 corrupt artifacts, unclear primary workbook |
| 5 | Scripts | 83 active well-indexed, 2 hook dirs need consolidation |
| 6 | Tests | 4 dirs / 176 files / 65K lines, zero READMEs, duplication |
| 7 | Docs active (12 dirs) | 5 missing index.json, duplicate colab notebook, AI docs fragmented |
| 8 | Docs research | navigation_study 73 raw JSON files, 83 uncategorized research files |
| 9 | Docs archive/internal | 253 archive files fragmented, 8 cost-optimizer docs, stale _active/ |
| 10 | Docs reference | **30 MB / 1760 files in vendor CHM — #1 repo health issue** |
| 11 | Agents | `agents/` vs `docs/agents/` split confusing, agent-9 heavy |

### Top 5 High-Priority Actions

1. **Remove vendor CHM from git** — 30 MB, 1760 files (47% of all files). Move to Git LFS or external storage
2. ~~**Archive/remove navigation_study raw data**~~ ✅ Done — untracked + .gitignore rule added
3. ~~**Fix 2 RED architecture violations**~~ ✅ Done — `api_wrapper.py` now imports through backward-compat stubs
4. **Split ai_workspace.py** — 5103 lines is unsustainable for maintenance
5. ~~**Add READMEs to test directories**~~ ✅ Done — READMEs added to all 4 test dirs + 5 more dirs

### Fixes Applied (Session 91 — Post-Audit)

| Fix | Files Changed |
|-----|---------------|
| Deleted 2 corrupt VBA artifacts | `VBA/ETABS_Export/.!34470!`, `.!35354!` |
| Fixed "900+ lines" stale claim | `.github/copilot/instructions.md` |
| Untracked 73 navigation_study JSON files | `.gitignore` + `git rm --cached` |
| Untracked 5 ETABS output CSVs | `.gitignore` + `git rm --cached` |
| Removed duplicate colab notebook | `docs/cookbook/colab_workflow.ipynb` |
| Fixed architecture violation | `streamlit_app/utils/api_wrapper.py` (imports via stubs now) |
| Archived 3 stale _active/ docs | Moved to `docs/_archive/misc/` |
| Added .gitignore rules | Corrupt VBA patterns, ETABS output, navigation_study |
| Added 9 missing READMEs | test dirs (3), docs dirs (4), agents/roles, fastapi_app |

### Repository Metrics (Post-Audit + Fixes)

| Metric | Before | After |
|--------|--------|-------|
| Total tracked files | ~3,719 | ~3,638 |
| Corrupt files | 2 | 0 |
| Duplicate notebooks | 1 | 0 |
| Architecture violations | 2 RED | 1 RED (test file only) |
| Missing test READMEs | 4 | 1 (Python/tests/ already had one) |
| README coverage | 13/17 top-level | 14/17 top-level |
| Stale _active/ docs | 3 | 0 |

---

## Workflow Status (for context)

All workflow tooling is green as of Session 91:
- `check_scripts_index.py` — 83/83 scripts indexed, 60/60 docstrings
- `sync_numbers.py` — All doc numbers match codebase
- `check_openapi_snapshot.py` — Baseline matches (35 endpoints, 75 schemas)
- `session.py end` — 9-step end check including TASKS archival
- `ai_commit.sh` — Post-commit hooks: stale numbers + broken link detection
- `generate_enhanced_index.py` — Content hash watermarks + `--check` staleness

### Remaining Workflow Items
- [ ] `--dry-run` as universal default for mutating scripts
- [ ] Consistent `--json` output across remaining `check_*` scripts
- [ ] Migrate 38 more scripts to `_lib/` (Phase 4b)
- [ ] Add `sync_numbers` to GitHub Actions CI
