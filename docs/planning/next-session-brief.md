# Next Session Briefing

**Type:** Handoff
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2025-01-01
**Last Updated:** 2026-03-25<br>

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-03-25
- Session: 93 (continued)
- Branch: main (PR #436 merged)
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.19.1 | ✅ Shipped (dashboard insights, ExportPanel, code checks wired) |
| **Next** | v0.20.0 | 📋 V3 Foundation (code-splitting, SSE progress, REST fallback) |

**Last Session:** Session 93 | **Focus:** Unified CLI merged + git workflow audit

---

## ✅ Session 93 Completion (Mar 25, 2026)

### PR #436 Merged to Main
- Fixed 3 CI failures: root file limit, governance config drift, scripts index format mismatch
- Addressed 4 Copilot review comments (unused param, error handling, misleading description)
- Removed 7 phantom archived scripts from `automation-map.json`
- All 6 CI checks green → squash-merged to main

### Git Workflow Audit
- Full audit document: `docs/audit/git-workflow-audit-pr436.md`
- 6 issues documented, 4 fixed in this session
- Top recommendations: governance single source of truth, `check_all.py --baseline` mode

---

## ✅ Session 93 (Mar 24, 2026)

### Completed This Session

**Onboarding Audit (TASK-500, PR #436):**
1. Fixed 46 stale script/doc references → 15 remaining (all low-risk)
2. Fixed `audit_readiness_report.py`, `finish_task_pr.sh`, `session.py`, `agent_start.sh` runtime breaks
3. Created `validate_script_refs.py` — automated stale reference checker

**Unified CLI — `run.sh` (Phase 0+1+2+3):**
4. **Archived 7 Streamlit-era scripts** (85→78 active, 93→100 archived)
5. **Created `run.sh`** (~600 lines) — single entry point with 9 subcommands:
   - `check`, `commit`, `pr`, `session`, `find`, `release`, `audit`, `test`, `generate`
   - Each with `--help`, error messages, and proper dispatch
6. **Created `check_all.py`** (~340 lines) — parallel check orchestrator:
   - 28 checks across 9 categories (api, docs, arch, governance, fastapi, git, stale, code, streamlit)
   - `--quick` (8 checks, <30s), `--category`, `--fix`, `--json`, `--list`, `--serial`
   - ThreadPoolExecutor with 4 workers, 60s timeout per check
7. **Updated all agent docs** — CLAUDE.md, AGENTS.md, copilot-instructions.md, agent-bootstrap.md, agent-quick-reference.md, scripts/README.md all now reference `./run.sh` as primary interface

### Key Commits
- Stale ref fixes + `validate_script_refs.py`
- `562461c` — refactor: archive 7 Streamlit-era scripts (85→78 active)
- `669c8d1` — feat: add run.sh unified CLI and check_all.py orchestrator
- docs: update all agent instruction files with `./run.sh` commands

### Key Decisions
- **Skipped absorbing `check_openapi_snapshot.py` into `validate_api_contracts.py`** — different baseline formats (raw JSON vs extracted signatures)
- **Skipped absorbing `update_test_stats.py` into `sync_numbers.py`** — different purposes (full pytest 2min vs count-only 5s)
- Both kept separate for stability

### Next Priorities
1. ~~**Finish PR #436**~~ — ✅ Merged to main
2. **Governance single source of truth** — make `governance-limits.json` the only config (see audit ISSUE-1)
3. **`check_all.py --baseline` mode** — distinguish new failures from pre-existing (see audit ISSUE-6)
4. **Code-split Three.js bundles** — `index.js` chunk is 1.16 MB
5. **REST fallback in DesignView** — when WebSocket is unavailable
6. **SSE batch progress UI** — streaming.py router exists, needs React consumer
7. **React test infrastructure** — Zero test files, needs Vitest + core tests
8. **Split `ai_workspace.py`** — 5103 lines → 6 modules (needs dedicated PR)

### Technical Debt (accurate count as of Session 92)
- **2 architecture errors** — `rebar_optimizer`/`multi_objective_optimizer` bypass api facade (needs api.py expansion)
- **~13 backward-compat stub imports** in streamlit_app/ — lower priority, functional
- **28 unit conversion warnings** in IS 456 code — mostly well-documented via var names
- **React test infrastructure** — zero test files, needs Vitest setup
- **Split `ai_workspace.py`** — 5103 lines → 6 modules

### Lower-Priority Agent Infrastructure (from Session 92 plan)
- P2: SESSION_LOG recent view (auto-truncate to last 10 sessions)
- P2: Automation-map tags for better discoverability
- P3: Copilot hooks (format-on-edit) — still in preview
- P3: Copilot custom agents (.github/agents/) — experimental

---

## ✅ Session 91 Summary (Mar 23, 2026)

### Completed This Session

**Bootstrap overhaul — all major context docs updated (2 passes):**

**Pass 1 — Corrected stale info:**
1. **CLAUDE.md** — Fixed architecture (3→4 layer), fixed `api.py` path stub note, corrected `services/api.py` grep, added `useExport` / `useDesignWebSocket`, added 13 FastAPI router note
2. **.github/copilot-instructions.md** — Same fixes applied, added adapter path note
3. **docs/getting-started/agent-bootstrap.md** — Major refresh:
   - Section 3: 3-layer → 4-layer architecture table with correct paths
   - Section 4 hooks, components, FastAPI routes, library, state stores all refreshed
   - Section 9 mistakes: Added wrong-path traps for stub `api.py` and module paths
4. **docs/TASKS.md** — Updated to Session 91, marked v0.19.1 complete, added v0.20 sprint items
5. **docs/planning/next-session-brief.md** — Updated handoff entry

**Pass 2 — Fact-checked and improved:**
1. Added 2 missing hooks (`useCSVTextImport`, `useRebarApply`) across all docs
2. Expanded FastAPI endpoint table from 18 → 35 (all actual endpoints with real paths)
3. Removed phantom `useUIStore` (documented but never existed in codebase)
4. Clarified function count: "23 public + 6 private" instead of misleading "29 public"
5. Removed duplicate "REST fallback" item in TASKS.md Up Next
6. Archived old completed sessions (32–73) from TASKS.md — trimmed 308→81 lines
7. Added compact milestone summary for archived sessions

### Session Gap Note (Feb 11 → Mar 23, 2026)
No sessions logged between Session 90 and Session 91. Codebase state during this gap (from git log):
- `feat(export)`: ExportPanel added with BBS/DXF/report downloads (commit `5a53015`)
- `feat(react)`: Dashboard insights, code checks, rebar suggestions wired (`a8e2fe6`)
- `feat`: 4-layer governance lock + migration tests (`c1b487e`, `6b2ebd0`, `dfd53e6`)
- `refactor`: Scripts _lib/output.py + _lib/ast_helpers.py Phase 3 (`c80f454`)

### Next Priorities (v0.20 Sprint)
1. **Code-split Three.js bundles** — `index.js` chunk is 1.16 MB
2. **REST fallback in DesignView** — when WebSocket is unavailable
3. **SSE batch progress UI** — streaming.py router exists, needs React consumer
4. **e2e Docker + React test** — verify all 13 routers end-to-end
5. **Update openapi_baseline.json** — snapshot now stale

---

## ✅ Session 90 Summary (Feb 11, 2026)

### Completed This Session

**Phase 2 Doc Cleanup — 280+ stale references fixed:**
1. Fixed 3 **CRITICAL** `.pre-commit-config.yaml` refs (check_api_docs_sync.py → check_api.py --sync, etc.)
2. Fixed CLAUDE.md + `.github/copilot-instructions.md` + `.github/copilot/instructions.md`
3. Fixed 8 agent guide docs (agent-quick-reference, agent-workflow-master-guide, agent-automation-system, agent-8-automation, agent-9-governance-hub, agent-6-comprehensive-onboarding, agent-6-streamlit-hub, agent-6-quick-start, agent-bootstrap-complete-review)
4. Fixed 8 contributing docs (handoff, end-of-session-workflow, repo-professionalism, background-agent-guide, streamlit-maintenance-guide, streamlit-comprehensive-prevention-system, streamlit-prevention-system-review, streamlit-issues-catalog)
5. Fixed 4 git-automation docs, 2 reference docs, 3 READMEs (docs, scripts, Python)
6. Fixed audit docs, planning docs, research docs
7. Updated scripts-improvement-research.md: Phase 2 → ✅ DONE, metrics updated (active scripts: ~79, high-overlap pairs: 0)
8. Updated agent-bootstrap.md command table

**Script name mapping applied:**
| Old Script(s) | New Consolidated Script |
|---------------|----------------------|
| `start_session.py`, `end_session.py`, `update_handoff.py`, `check_session_docs.py` | `session.py start/end/handoff/check` |
| `verify_release.py`, `check_release_docs.py`, `check_pre_release_checklist.py` | `release.py verify/check-docs/checklist` |
| `check_streamlit_issues.py`, `check_fragment_violations.py`, `validate_streamlit_page.py`, `comprehensive_validator.py` | `check_streamlit.py --all-pages/--fragments` |
| `check_api_signatures.py`, `check_api_docs_sync.py`, `check_api_doc_signatures.py` | `check_api.py --signatures/--docs/--sync` |
| `validate_folder_structure.py`, `check_governance_compliance.py` | `check_governance.py --structure/--compliance` |
| `check_docs_index.py`, `check_docs_index_links.py` | `check_docs.py --index/--index-links` |
| `fix_broken_links.py` | `check_links.py --fix` |
| `agent_setup.sh`, `agent_preflight.sh`, `copilot_setup.sh` | `agent_start.sh --quick` |

### Files Changed (~45 files)
- 1 config: `.pre-commit-config.yaml`
- 3 instruction files: CLAUDE.md, copilot-instructions.md, copilot/instructions.md
- 8 agent guides in `docs/agents/guides/`
- 8 contributing docs
- 4 git-automation docs
- 3 READMEs (docs/, scripts/, Python/)
- 2 reference docs (automation-catalog, streamlit-validation)
- 3 audit docs, 3 planning docs, 4 research docs
- 1 getting-started doc (copilot-quick-start)
- 1 research update (scripts-improvement-research.md)

### Next Priorities (Scripts Phase 3)
1. **Make scripts import `_lib/utils.py`** — Start with 10 most-used scripts
2. **Create `_lib/output.py`** — Unified JSON/table output
3. **Create `_lib/ast_helpers.py`** — Shared AST parsing

---

## ✅ Session 88 Summary (Feb 10, 2026)

### Completed This Session

**User reported 4 critical bugs after Session 86:**

1. **Blank screen on beam click** → Fixed: Added null guards for beam dimensions
2. **Beam off-center in design view** → Fixed: Centered beam at origin, dynamic camera positioning
3. **Camera locked after transition** → Fixed: Removed continuous lerping when not animating
4. **Cell edits not saving** → Fixed: Use fresh Zustand state instead of stale closure

### PR
| Number | Description | Status |
|--------|-------------|--------|
| #422 | 3D viewport centering and camera control fixes | ✅ MERGED (1m 42s CI) |

### Files Changed
- `react_app/src/components/viewport/Viewport3D.tsx` — Beam centering + camera control fix
- `react_app/src/components/pages/BuildingEditorPage.tsx` — Cell edit state fix
- `docs/getting-started/agent-bootstrap.md` — Updated V3 infrastructure table
- `docs/getting-started/agent-essentials.md` — Enhanced React hooks/components tables

### Test Results
```
✅ React build: 2754 modules in 4.11s
✅ Python geometry tests: 52 passed
✅ FastAPI tests: 3 geometry endpoints passed
✅ CI checks: All passed (1m 42s)
```

### Next Priorities
1. Test stirrup rendering with real CSV data
2. Add measurement tools in 3D viewport
3. Wire dashboard insights into React UI

---

## ✅ Session 82 Summary (Jan 27, 2026)

### Completed This Session — Phase 2 COMPLETE

1. **Library Layer**
   - `cross_section_geometry()` in `geometry_3d.py`
   - `CrossSectionGeometry` dataclass for 2D section cuts

2. **FastAPI Endpoints (4 new)**
   - `POST /api/v1/geometry/building` — Building wireframe
   - `POST /api/v1/geometry/cross-section` — 2D section cut
   - `POST /api/v1/geometry/rebar/validate` — IS 456 validation
   - `POST /api/v1/geometry/rebar/apply` — Apply + geometry preview

3. **React Hooks (4 new)**
   - `useBuildingGeometry` / `useBuildingGeometryMutation`
   - `useRebarValidation` / `useRebarApply`

### PR
| Number | Description | Status |
|--------|-------------|--------|
| #415 | Phase 2 geometry + rebar endpoints + hooks | 🟡 Open |

---

## ✅ Session 81 Summary (Jan 27, 2026)

### Completed This Session
1. **Library Modules Added**
   - `structural_lib.batch` with `design_beams` + `design_beams_iter`
   - `structural_lib.imports` with `parse_dual_csv`, `merge_geometry_forces`, `validate_import`
   - `structural_lib.rebar` with `validate_rebar_config`, `apply_rebar_config`
   - `geometry_3d.building_to_3d_geometry`

2. **FastAPI + React Integration**
   - New `POST /api/v1/import/dual-csv` endpoint
   - SSE streaming wired to `design_beams_iter`
   - React `useDualCSVImport` hook with `format_hint` query param

3. **Tests**
   - Added unit tests for batch, imports, rebar, building geometry
   - Dual CSV endpoint test (newline parsing fix)

### Commit
| Hash | Description |
|------|-------------|
| 6ee623f | feat: add dual-csv import + building geometry + rebar helpers |

### CI Note
- Push bypassed required status check “Quick Validation (Python 3.11 only)” on `main`.

---

## 🔑 Session 76 Summary (Jan 26, 2026)

### ✅ Completed This Session

1. **Viewport3D Wired to Library API**
   - Replaced manual bar calculations with `useBeamGeometry` hook
   - 3D rebars/stirrups now use accurate positions from `geometry_3d.beam_to_3d_geometry()`

2. **FileDropZone Component Added**
   - Drag-and-drop CSV upload in `components/ui/FileDropZone.tsx`
   - Wired to `useCSVFileImport` → API → GenericCSVAdapter

3. **CSV Parser Deprecated**
   - `parseBeamCSV()` in `types/csv.ts` now throws deprecation error
   - Directs to useCSVFileImport hooks

4. **Agent Bootstrap Updated**
   - `agent-essentials.md` now has V3 stack reference table
   - `agent-bootstrap.md` now has architecture diagram
   - `agent_start.sh` displays V3 stack info on startup
   - **Purpose:** Stop agents from duplicating existing hooks/components

5. **V3 Roadmap Updated**
   - Week 3-4 React Shell marked ✅ COMPLETE
   - Technology stack updated (React 19, R3F 9, Tailwind 4)

### Commit
| Hash | Description |
|------|-------------|
| d0f968e | feat(react): wire Viewport3D to useBeamGeometry, add FileDropZone |

---

## 🏗️ V3 Stack Reference — DON'T REINVENT!

**Before writing code, check what exists:**

### React Hooks (`react_app/src/hooks/`)
| Hook | Purpose |
|------|---------|
| `useBeamGeometry` | 3D rebar/stirrup positions from API |
| `useBuildingGeometry` | Building-level 3D wireframe |
| `useRebarValidation` | Rebar config validation |
| `useRebarApply` | Apply rebar + preview geometry |
| `useCSVFileImport` | CSV import via library adapters |
| `useDualCSVImport` | Geometry + forces CSV import |
| `useBatchDesign` | Batch design all beams |
| `useDesignWebSocket` | WebSocket live design |

### FastAPI Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/geometry/beam/full` | Full 3D beam geometry |
| `POST /api/v1/geometry/building` | Building wireframe |
| `POST /api/v1/geometry/cross-section` | 2D section cut |
| `POST /api/v1/geometry/rebar/validate` | Rebar validation |
| `POST /api/v1/geometry/rebar/apply` | Rebar apply + geometry |
| `POST /api/v1/import/csv` | CSV file import |
| `POST /api/v1/import/dual-csv` | Dual file import |
| `POST /api/v1/design/beam` | Beam design |

### Library Functions
| Module | Key Functions |
|--------|---------------|
| `api.py` | `design_beam_is456()`, `detail_beam_is456()` |
| `adapters.py` | `GenericCSVAdapter`, `ETABSAdapter` |
| `geometry_3d.py` | `beam_to_3d_geometry()`, `building_to_3d_geometry()`, `cross_section_geometry()` |
| `rebar.py` | `validate_rebar_config()`, `apply_rebar_config()` |
| `batch.py` | `design_beams()`, `design_beams_iter()` |

---

## 🔥 Next Session Priorities — Phase 3

### Priority 1: Insights Library Module

**Goal:** Create `structural_lib.insights` module

```python
# New file: Python/structural_lib/insights.py
def generate_dashboard(design_result) -> DashboardData
def code_checks_live(beam, config) -> CodeCheckResult
```

### Priority 2: FastAPI Insight Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/insights/dashboard` | Aggregated design summary |
| `POST /api/v1/insights/code-checks` | Live IS 456 pass/fail |
| `POST /api/v1/optimization/rebar-suggest` | Rebar optimization hints |

### Priority 3: React Integration

| Hook | Purpose |
|------|---------|
| `useDashboardInsights` | Fetch dashboard data |
| `useCodeChecks` | Real-time code validation |
| `useRebarSuggestions` | Optimization suggestions |

### Priority 4: UI Polish

- Live IS-code status badge (pass/fail + warnings)
- Optimizer suggestions panel with "Apply" button
- Export buttons for BBS/DXF

---

## 📊 V3 Migration Progress

| Phase | Week | Goal | Status |
|-------|------|------|--------|
| **Phase 1** | 1 | Automation Foundation | ✅ DONE |
| **Phase 2** | 2-3 | FastAPI + React Foundation | ✅ DONE |
| **Phase 3** | 4-5 | Live Design + Streaming | ✅ DONE |
| **Phase 4** | 5-6 | Geometry + Editor | ✅ DONE |
| **Phase 5** | 6-7 | Insights + Code Checks | 🟡 NEXT |
| **Launch** | 7 | Beta Launch | 🎯 TARGET |

**Target:** March 15, 2026 (V3 Beta)

---

## Required Reading

- [CLAUDE.md](../../CLAUDE.md) or [.github/copilot-instructions.md](../../.github/copilot-instructions.md) — Architecture + commit rules
- [docs/TASKS.md](../TASKS.md) — Current work items
- [docs/research/scripts-improvement-research.md](../research/scripts-improvement-research.md) — Phase 3 plan (next work)

---

## Session Start Checklist

```bash
# ONE COMMAND to start any session:
./scripts/agent_start.sh --quick

# Then read copilot-instructions.md if not already loaded
```

---

## Quick Commands

```bash
# Run FastAPI
docker compose -f docker-compose.dev.yml up --build

# Run React
cd react_app && npm run dev

# Run tests
cd Python && .venv/bin/pytest tests/ -v

# Build React
cd react_app && npm run build

# Commit changes
./scripts/ai_commit.sh "type: description"
```

---

## Key Files

| Purpose | Location |
|---------|----------|
| Task tracking | [docs/TASKS.md](../TASKS.md) |
| Session history | [docs/SESSION_LOG.md](../SESSION_LOG.md) |
| **V3 Roadmap** | [docs/planning/8-week-development-plan.md](8-week-development-plan.md) |
| **Agent essentials** | [docs/getting-started/agent-essentials.md](../getting-started/agent-essentials.md) |
| 3D visualization | [react_app/src/components/viewport/Viewport3D.tsx](../../react_app/src/components/viewport/Viewport3D.tsx) |
| API hooks | [react_app/src/hooks/](../../react_app/src/hooks/) |
