# Agent Bootstrap — structural_engineering_lib

**Type:** Guide | **Audience:** All Agents | **Status:** Approved | **Importance:** Critical

> **This is THE canonical bootstrap for all AI agents.** Entry points (`CLAUDE.md`, `.github/copilot-instructions.md`) link here.

---

## ⚠ Agent Quick-Scan (read this FIRST)

| # | Critical Warning | Why it matters |
|---|-----------------|----------------|
| 1 | **`api.py` is a STUB** — real code is `services/api.py` | Editing the stub wastes time; changes have no effect |
| 2 | **Params are `b_mm`, `d_mm`, `fck`** — NOT `width`, `depth`, `grade` | Wrong names = failed tests. Run `./run.sh find --api <func>` to check |
| 3 | **Never manual git** — always `./scripts/ai_commit.sh "type: msg"` | Manual git causes 10-30 min merge conflicts |
| 4 | **Search hooks/routes/API before coding** — duplication is the #1 agent mistake | Tables in §4 list everything that exists |
| 5 | **Session end is MANDATORY** — update SESSION_LOG + next-session-brief | Skipping breaks continuity; next agent wastes hours rediscovering state |
| 6 | **Moved modules**: `adapters.py` → `services/adapters.py`, `geometry_3d.py` → `visualization/geometry_3d.py` | Old paths cause import errors |

---

## 1. Project Identity

Open-source **IS 456 RC beam design library** for structural engineers.
- **Python core** (`Python/structural_lib/`) — Design, detailing, optimization, BBS, DXF export
- **FastAPI backend** (`fastapi_app/`) — REST + WebSocket API
- **React 19 frontend** (`react_app/`) — 3D visualization with React Three Fiber
- **Streamlit app** (`streamlit_app/`) — Legacy UI (maintained, not primary)
- **Current focus:** See [TASKS.md](../TASKS.md) for active work

---

## 2. THE ONE RULE

```bash
./scripts/ai_commit.sh "type: message"    # ALL commits
```

**NEVER** use `git add`, `git commit`, `git push`, `git pull` manually.

---

## 3. V3 Architecture

```
React 19 + R3F + Tailwind  ──HTTP/WS──>  FastAPI  ──Python──>  structural_lib
   react_app/                              fastapi_app/           Python/structural_lib/
```

### 4-Layer Rule (STRICT, never mix)

| Layer | Location | Rule |
|-------|----------|------|
| **Core types** | `Python/structural_lib/core/` | Base classes, types, constants — no IS 456 math |
| **IS 456 Code** | `codes/is456/flexure.py`, `shear.py`, `detailing.py` | Pure math, NO I/O, explicit units (mm, N/mm², kN, kNm) |
| **Services** | `services/api.py`, `services/adapters.py`, `services/beam_pipeline.py` | Orchestration, no formatting |
| **UI/IO** | `react_app/`, `streamlit_app/`, `fastapi_app/`, `visualization/` | External interfaces only |

> `Python/structural_lib/api.py` is a **backward-compat stub** — real code is in `services/api.py`.
> `adapters.py` → `services/adapters.py` | `geometry_3d.py` → `visualization/geometry_3d.py`

Core CANNOT import from Services or UI. Services CANNOT import from UI. Units always explicit.

> **Tech stack rationale** (why each tech was chosen, efficiency, safety): [tech-stack-rationale.md](../reference/tech-stack-rationale.md)

---

## 4. What Exists — DON'T Reinvent

### React Hooks (`react_app/src/hooks/`)

| Hook | Purpose | File |
|------|---------|------|
| `useCSVFileImport` | CSV file import via API adapters (40+ columns) | `useCSVImport.ts` |
| `useCSVTextImport` | CSV text/paste import | `useCSVImport.ts` |
| `useDualCSVImport` | ETABS geometry+forces import | `useCSVImport.ts` |
| `useBatchDesign` | Batch design all beams | `useCSVImport.ts` |
| `useBeamGeometry` | 3D rebar/stirrup geometry from API | `useBeamGeometry.ts` |
| `useLiveDesign` | WebSocket live design | `useLiveDesign.ts` |
| `useAutoDesign` | Auto-trigger on input change | `useAutoDesign.ts` |
| `useBuildingGeometry` | Building 3D geometry | `useGeometryAdvanced.ts` |
| `useCrossSectionGeometry` | Cross-section visualization | `useGeometryAdvanced.ts` |
| `useRebarValidation` | Rebar edit validation | `useRebarEditor.ts` |
| `useRebarApply` | Apply rebar configuration | `useRebarEditor.ts` |
| `useExportBBS` / `useExportDXF` / `useExportReport` | File downloads (BBS CSV, DXF, HTML report) | `useExport.ts` |
| `useDashboardInsights` | Batch analytics (pass/fail, utilization) | `useInsights.ts` |
| `useCodeChecks` | Live IS 456 clause check badges | `useInsights.ts` |
| `useRebarSuggestions` | AI rebar suggestion options | `useInsights.ts` |
| `useDesignWebSocket` | Low-level WebSocket connection | `useDesignWebSocket.ts` |
| `useBatchProgress` | SSE batch design progress tracking | `useBatchProgress.ts` |

### React Components (`react_app/src/components/`)

| Component | Purpose |
|-----------|---------|
| `Viewport3D` | 3D beam/building visualization (R3F) — supports `overrideDimensions` prop for non-store beams |
| `BuildingEditorPage` | AG Grid beam editor — click beam → BeamDetailPanel slides in |
| `BeamDetailPanel` | **NEW** Inline detail panel: 3D rebar + cross-section + results + redesign + export |
| `DesignView` | Single beam design page — dynamic layout (3D expands when no result), export dropdown |
| `DashboardPage` | BentoGrid analytics layout + export buttons in header |
| `ImportView` | CSV/JSON import UI |
| `ExportPanel` | BBS CSV / DXF / HTML report download buttons |
| `CrossSectionView` | Annotated SVG — accepts `ascRequired`, `barDia`, `barCount`, `utilization` props |
| `FloatingDock` | **ACTIVATED** macOS-style spring dock — bottom nav on all pages except `/` |
| `FileDropZone` | Drag-drop CSV upload |
| `CommandPalette` | Global keyboard-driven command palette |
| `BatchProgressBar` | SSE-driven batch design progress bar |

### FastAPI Endpoints (`fastapi_app/routers/`)

35 endpoints across 12 routers + 1 WebSocket:

| Router | Endpoint | Purpose |
|--------|----------|---------|
| **design** | `POST /api/v1/design/beam` | Beam design (Mu, Vu, Ast) |
| | `POST /api/v1/design/beam/check` | Check existing beam design |
| | `GET  /api/v1/design/limits` | Design parameter limits |
| **detailing** | `POST /api/v1/detailing/beam` | Rebar detailing |
| | `GET  /api/v1/detailing/bar-areas` | Standard bar area lookup |
| | `GET  /api/v1/detailing/development-length/{bar_diameter}` | Development length calc |
| **analysis** | `POST /api/v1/analysis/beam/smart` | Smart beam analysis |
| | `GET  /api/v1/analysis/code-clauses` | IS 456 code clauses reference |
| **imports** | `POST /api/v1/import/csv` | CSV file import (40+ column mappings) |
| | `POST /api/v1/import/csv/text` | CSV text/paste import |
| | `POST /api/v1/import/dual-csv` | ETABS dual CSV import |
| | `POST /api/v1/import/batch-design` | Batch design all beams (returns `utilization_ratio = Mu/Mu_cap`) |
| | `GET  /api/v1/import/formats` | Supported CSV formats |
| | `GET  /api/v1/import/sample` | Sample data for testing |
| **geometry** | `POST /api/v1/geometry/beam/3d` | Basic 3D beam geometry |
| | `POST /api/v1/geometry/beam/full` | Full 3D rebar/stirrup positions |
| | `GET  /api/v1/geometry/materials` | Material properties lookup |
| | `POST /api/v1/geometry/building` | Building 3D geometry |
| | `POST /api/v1/geometry/cross-section` | Cross-section visualization |
| **insights** | `POST /api/v1/insights/dashboard` | Batch analytics (pass rate, utilization) |
| | `POST /api/v1/insights/code-checks` | Live IS 456 clause checks |
| | `POST /api/v1/insights/rebar-suggest` | AI rebar suggestions |
| **optimization** | `POST /api/v1/optimization/beam/cost` | Cost-optimized beam design |
| | `GET  /api/v1/optimization/cost-rates` | Material cost rates |
| **rebar** | `POST /api/v1/rebar/validate` | Rebar configuration validation |
| | `POST /api/v1/rebar/apply` | Apply rebar configuration |
| **export** | `POST /api/v1/export/bbs` | BBS CSV download |
| | `POST /api/v1/export/dxf` | DXF drawing download |
| | `POST /api/v1/export/report` | HTML report download |
| **health** | `GET  /health` | Basic health check |
| | `GET  /health/ready` | Readiness check |
| | `GET  /health/info` | Version & dependency info |
| **streaming** | `GET  /streaming/batch-design` | SSE batch design progress |
| | `GET  /streaming/job/{job_id}` | SSE job status |
| **websocket** | `WS  /ws/design/{session_id}` | Live WebSocket design updates |

### Library (`Python/structural_lib/`)

| Module | Key Functions |
|--------|---------------|
| `services/api.py` | 23 public functions + 6 private helpers — key entry points: `design_beam_is456()`, `detail_beam_is456()`, `optimize_beam_cost()`, `smart_analyze_design()` |
| `api.py` | **Backward-compat stub only** — imports from `services/api.py` |
| `services/adapters.py` | `GenericCSVAdapter`, `ETABSAdapter`, `SAFEAdapter` |
| `visualization/geometry_3d.py` | `beam_to_3d_geometry()` — 3D rebar/stirrup positions |
| `codes/is456/` | `flexure.py`, `shear.py`, `detailing.py`, `torsion.py`, `serviceability.py` — IS 456:2000 |
| `services/bbs.py` | Bar bending schedule generation |
| `services/dxf_export.py` | DXF drawing export |
| `insights/` | `smart_designer.py`, `design_suggestions.py`, `sensitivity.py`, `cost_optimization.py` |

### State Stores (`react_app/src/store/`)

| Store | Purpose |
|-------|---------|
| `useDesignStore` | Single beam design inputs/results |
| `useImportedBeamsStore` | Imported CSV beams + selection |

### Recent Bug Fixes & Features (Session 98)

| Fix/Feature | Details |
|-------------|----------|
| **3D vs 2D top bar mismatch** | CrossSectionView now uses `ascRequired` prop (matching API's `0.25*Ast` logic) instead of `Math.min(2, ceil(numBars*0.3))` |
| **Utilization formula corrected** | Backend `BatchDesignResult` now returns `utilization_ratio = Mu/Mu_cap` — not `Ast/Ast_max` |
| **Stirrup spacing 275 vs 300** | Not a bug — IS 456 Cl 26.5.1.5: `max_sv = min(0.75d, 300mm)`. UI now shows governing limit |
| **Single-beam redesign** | BeamDetailPanel has "Redesign" button → calls `/api/v1/design/beam` for one beam |
| **Editable rebar** | BeamDetailPanel has inline edit mode with `useRebarValidation` for live IS 456 checks |
| **FloatingDock activated** | macOS spring dock in App.tsx — nav on all pages except `/` |
| **BentoGrid on Dashboard** | DashboardPage rewritten with BentoGrid layout + export buttons in header |
| **DesignView dynamic layout** | 3D viewport fills 100% when no result; collapses to 55% when result appears |
| **CrossSectionView annotations** | `utilization` color coding (emerald/amber/rose), actual `barDia`/`barCount` props |


**Quick check before coding:**
```bash
ls react_app/src/hooks/                                         # React hooks
grep -r "@router" fastapi_app/routers/ | head -30               # FastAPI routes
grep "^def " Python/structural_lib/services/api.py | head -20   # Library functions
```

---

## 5. Launching the App

### Option A: Full Stack via Docker (recommended for production/testing)

```bash
docker compose up --build                            # FastAPI at http://localhost:8000/docs
```

This builds and runs the FastAPI container with all Python dependencies. The `/docs` page auto-generates interactive Swagger UI for all 35 endpoints.

For development with hot-reload (code changes reflect without rebuild):
```bash
docker compose -f docker-compose.dev.yml up          # Mounts source as volumes, auto-reloads
```

### Option B: Local Development (FastAPI + React separately)

```bash
# Terminal 1 — FastAPI backend
.venv/bin/uvicorn fastapi_app.main:app --reload --port 8000
# → http://localhost:8000/docs (Swagger UI)
# → http://localhost:8000/health (health check)

# Terminal 2 — React frontend
cd react_app && npm install && npm run dev
# → http://localhost:5173 (Vite dev server, HMR enabled)
```

The React app proxies API calls to `:8000`. Both must be running for full functionality.

### Option C: Streamlit (legacy UI)

```bash
cd streamlit_app && ../.venv/bin/streamlit run app.py --server.port 8501
# → http://localhost:8501
```

### Option D: Python library only (no UI)

```bash
pip install -e Python/                               # Install in dev mode
python -c "from structural_lib import design_beam_is456; print('OK')"
```

### Port Map

| Service | Port | URL |
|---------|------|-----|
| FastAPI (Docker) | 8000 | http://localhost:8000/docs |
| FastAPI (local) | 8000 | http://localhost:8000/docs |
| React (Vite dev) | 5173 | http://localhost:5173 |
| Streamlit | 8501 | http://localhost:8501 |

### Troubleshooting

| Problem | Fix |
|---------|-----|
| Port 8000 in use | `lsof -i :8000` → kill the process, or use `--port 8001` |
| React can't reach API | Ensure FastAPI is running on :8000 first |
| Python import errors | Use `.venv/bin/python`, never bare `python` |

---

## 6. Quick Start (Agent Workflow)

```bash
# Session start
./run.sh session start                               # Verify env, read priorities

# Validate codebase
./run.sh check --quick                               # Fast validation (8 checks, <30s)
./run.sh check                                       # Full validation (28 checks, parallel)
./run.sh check --category api                        # One category only

# Run tests
./run.sh test                                        # Full pytest suite
./run.sh test -k "test_flexure" -v                   # Specific tests
./run.sh test --ci                                   # Full local CI

# Build & serve
docker compose up --build                            # http://localhost:8000/docs
cd react_app && npm run dev                          # http://localhost:5173
cd react_app && npm run build                        # Build check

# Session end
./run.sh session end                                 # Wrap up (logs, sync, handoff)
```

Run `./run.sh --help` or `./run.sh <command> --help` for full usage.

---

## 7. Git Workflow

```bash
# Decision: PR or direct commit?
./run.sh pr status
```

| Change Type | Strategy |
|-------------|----------|
| Production code (`Python/structural_lib/`) | PR required |
| VBA / CI workflows / Dependencies | PR required |
| Docs / tests / scripts (<=150 lines, <=2 files) | Direct commit OK |

```bash
# Direct commit
./run.sh commit "docs: update guide"

# PR workflow
./run.sh pr create TASK-XXX "description"
./run.sh commit "feat: implement X"              # Repeat as needed
./run.sh pr finish                                # Polls CI, auto-merges

# Emergency recovery
./scripts/recover_git_state.sh
```

**Commit format:** `type: description` (subject <=72 chars, no period at end)
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore`

**Session docs rule:** Update `SESSION_LOG.md` + `next-session-brief.md` in same PR. Log the **PR number** (not merge hash). One docs commit at end of session.

### Session Workflow Checklist (MANDATORY)

```
START:  □ ./run.sh session context              ← quick orientation (brief + tasks + git)
        □ ./run.sh session start
        □ ./run.sh preflight                     ← check branch, venv, ports, conflicts

END:    □ ./run.sh commit "type: message"        ← commit all work
        □ ./run.sh session summary               ← auto-log to SESSION_LOG.md
        □ ./run.sh session sync                  ← fix stale doc numbers
        □ Update next-session-brief.md           ← what NEXT agent should do
        □ Update TASKS.md                        ← mark done, add new
        □ ./run.sh commit "docs: session end"    ← commit doc updates
```

> **Why mandatory?** Skipping session end has caused 10+ hours of wasted rework. SESSION_LOG.md is the project memory — gaps mean lost context.

---

## 8. Key Scripts

**Preferred:** Use `./run.sh` for all common operations (run `./run.sh --help`).

| Action | run.sh | Direct script (fallback) |
|--------|--------|-------------------------|
| Session start | `./run.sh session start` | `./scripts/agent_start.sh --quick` |
| Commit | `./run.sh commit "msg"` | `./scripts/ai_commit.sh "msg"` |
| Full check | `./run.sh check` | N/A (orchestrator) |
| Quick check | `./run.sh check --quick` | N/A |
| Run tests | `./run.sh test` | `cd Python && .venv/bin/pytest tests/ -v` |
| Test changed | `./run.sh test --changed` | `.venv/bin/python scripts/test_changed.py` |
| Pre-flight | `./run.sh preflight` | `.venv/bin/python scripts/preflight.py` |
| Session context | `./run.sh session context` | `.venv/bin/python scripts/session.py context` |
| PR decision | `./run.sh pr status` | `./scripts/should_use_pr.sh --explain` |
| Find script | `./run.sh find "task"` | `.venv/bin/python scripts/find_automation.py "task"` |
| API signatures | `./run.sh find --api <func>` | `.venv/bin/python scripts/discover_api_signatures.py <func>` |
| Move file | N/A | `.venv/bin/python scripts/safe_file_move.py old new` |
| Delete file | N/A | `.venv/bin/python scripts/safe_file_delete.py file` |
| Create doc | N/A | `.venv/bin/python scripts/create_doc.py path "Title"` |
| Fix links | `./run.sh check --category docs --fix` | `.venv/bin/python scripts/check_links.py --fix` |
| Session end | `./run.sh session end` | `.venv/bin/python scripts/session.py end` |
| Gen indexes | `./run.sh generate indexes` | `./scripts/generate_all_indexes.sh` |

**Never do manually:** `git add/commit/push`, `rm/mv` docs, create docs without metadata.

---

## 9. Golden Rules

1. **Search before coding** — Check hooks, components, routes, API functions first
2. **Never parse CSV manually** — Use `useCSVFileImport` or `GenericCSVAdapter`
3. **Never calculate bar positions** — Use `useBeamGeometry` or `geometry_3d`
4. **Never create duplicate docs** — Check `docs/docs-canonical.json` first
5. **Verify outdated info online** — AI model names, library versions, framework APIs
6. **Test before commit** — Run build/tests for the stack you changed
7. **Discover API signatures before wrapping** — Never guess parameter names
8. **Small, deterministic changes** — No hidden defaults, no assumptions
9. **Update docs with code** — Doc changes go in the same PR as code changes
10. **No micro-commits** — Batch small related changes into one meaningful commit

---

## 10. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Manual git commands | 10-30min conflicts | `ai_commit.sh` |
| Duplicate React code | Broken features, bugs | Check `hooks/` and `components/` first |
| Guess API params (`width` vs `b_mm`) | Failed tests | `discover_api_signatures.py` |
| Import from stub `api.py` | Stale code path | Use `services/api.py` directly |
| Wrong module path (`adapters.py`) | Import error | `services/adapters.py` / `visualization/geometry_3d.py` |
| Manual file move/delete | 870+ broken links | `safe_file_move.py` / `safe_file_delete.py` |
| Skip validation | Runtime errors | Run tests + `check_*` scripts |
| Create duplicate docs | Clutter, confusion | Check `docs-canonical.json` first |
| Mix architecture layers | Import errors | Core → IS456 → Services → UI (one direction only) |
| Use `python` directly | Wrong env, missing deps | Always use `.venv/bin/python` |
| Forget to update indexes | Out-of-sync navigation | Run `generate_all_indexes.sh` after structural changes |

---

## 11. Domain-Specific Rules (Streamlit, VBA, Docs)

These rules auto-load via `.claude/rules/` and `.github/instructions/` for Claude Code and Copilot. For other agents:

| Domain | Key rule | Full reference |
|--------|----------|----------------|
| **Streamlit** | NEVER `st.sidebar` inside `@st.fragment` (crashes). Safe patterns: `data.get()`, `session_state.get()`. Module-level imports only. | `.claude/rules/streamlit.md` |
| **VBA/Excel** | Python + VBA parity required. Mac safety: `CDbl()` wraps. Always PR. | `.claude/rules/vba.md` |
| **New docs** | Must have metadata (Type/Audience/Status/Importance/Created). Use `create_doc.py` or add manually. | `.claude/rules/docs.md` |

---

## 12. On-Demand References

Load these only when working on that specific area:

| Topic | Document |
|-------|----------|
| Tech stack rationale | [tech-stack-rationale.md](../reference/tech-stack-rationale.md) |
| Command cheat sheet | [agent-quick-reference.md](../agents/guides/agent-quick-reference.md) |
| Deep workflow guide | [agent-workflow-master-guide.md](../agents/guides/agent-workflow-master-guide.md) |
| Current tasks | [TASKS.md](../TASKS.md) |
| Last session context | [next-session-brief.md](../planning/next-session-brief.md) |
| Git automation details | [git-automation/README.md](../git-automation/README.md) |
| API reference | [api.md](../reference/api.md) |
| Streamlit fragment rules | [streamlit-fragment-best-practices.md](../guidelines/streamlit-fragment-best-practices.md) |
| Folder structure rules | [folder-structure-governance.md](../guidelines/folder-structure-governance.md) |
| Architecture overview | [project-overview.md](../architecture/project-overview.md) |
| Agent roles | [agents/README.md](../../agents/README.md) |

### Machine-Readable Indexes

- `scripts/automation-map.json` — task-to-script mapping
- `docs/docs-canonical.json` — topic-to-canonical-doc mapping
- `scripts/index.json` — full automation catalog

---

*Run `./scripts/agent_start.sh --quick` for live project status.*
