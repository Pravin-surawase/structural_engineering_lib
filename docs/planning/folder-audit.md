# Folder Audit — Repository Health & Documentation

**Type:** Planning
**Audience:** All Agents
**Status:** In Progress
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
| 5 | `scripts/` | 191 | Yes | Yes | — |
| 6 | `docs/` | 2504 | Yes | Yes | — |
| 7 | `Excel/` | 12 | Yes | No | — |
| 8 | `VBA/` | 85 | Yes | No | — |
| 9 | `agents/` | 39 | Yes | Yes | — |
| 10 | `clients/` | 5 | No | No | Batch 1 ✅ |
| 11 | `tests/` | 26 | No | No | — |
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

### Batch 4: Excel & VBA
**Scope:** `Excel/`, `VBA/` (all subfolders)
**Goal:** Document workbook/module inventory, check Python parity

### Batch 5: Scripts Deep Dive
**Scope:** `scripts/` (tiers, _lib, _archive, git-hooks)
**Goal:** Verify tier classification, find unused scripts, check _archive relevance

### Batch 6: Tests
**Scope:** `Python/tests/`, `tests/`, `fastapi_app/tests/`, `streamlit_app/tests/`
**Goal:** Test coverage map, find gaps, dead fixtures

### Batch 7: Docs — Active Content
**Scope:** `docs/planning/`, `docs/getting-started/`, `docs/architecture/`, `docs/contributing/`, `docs/agents/`, `docs/guidelines/`
**Goal:** Find stale docs, overlapping content, update outdated material

### Batch 8: Docs — Research & Publications
**Scope:** `docs/research/`, `docs/publications/`, `docs/blog-drafts/`, `docs/learning/`
**Goal:** Archive completed research, consolidate findings

### Batch 9: Docs — Archive & Internal
**Scope:** `docs/_archive/`, `docs/_internal/`, `docs/_active/`, `docs/_references/`
**Goal:** Verify archive is organized, internal docs still relevant

### Batch 10: Docs — Reference (Largest)
**Scope:** `docs/reference/` (1788 files, 30MB)
**Goal:** Assess vendor/ CHM files, check reference docs freshness

### Batch 11: Agents & Misc
**Scope:** `agents/`, `agents/agent-9/`, `agents/roles/`
**Goal:** Document agent configuration, check for stale agent data

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
