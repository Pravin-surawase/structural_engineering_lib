---
owner: Main Agent
status: active
last_updated: 2026-08-07
doc_type: guide
complexity: intermediate
tags: []
---

# Agent Bootstrap — structural_engineering_lib

**Type:** Guide | **Audience:** All Agents | **Status:** Approved | **Importance:** Critical

> **This is THE canonical bootstrap for all AI agents.** Entry points (`CLAUDE.md`, `.github/copilot-instructions.md`) link here.

---

## ⚠ Agent Quick-Scan (read this FIRST)

| # | Critical Warning | Why it matters |
|---|-----------------|----------------|
| 1 | **`api.py` is a STUB** — real code is `services/api.py` | Editing the stub wastes time; changes have no effect |
| 2 | **Params are `b_mm`, `d_mm`, `fck`** — NOT `width`, `depth`, `grade` | Wrong names = failed tests. Run `./run.sh find --api <func>` to check |
| 3 | **Codex owns Git/GitHub** — scoped commits, pushes, and PR work | Repository wrappers are retired |
| 4 | **Search hooks/routes/API before coding** — duplication is the #1 agent mistake | Tables in §4 list everything that exists |
| 5 | **Session end is MANDATORY** — update SESSION_LOG + next-session-brief + WORKLOG | Skipping breaks continuity; next agent wastes hours rediscovering state |
| 6 | **Moved modules**: `adapters.py` → `services/adapters.py`, `geometry_3d.py` → `visualization/geometry_3d.py` | Old paths cause import errors |
| 7 | **Log every change in [WORKLOG.md](../WORKLOG.md)** — one line per item, append-only | Compact history prevents rework — agents check before duplicating |
| 8 | **NEVER use `--force` to bypass PR checks** — if `pr status` says PR, use PR | Force-pushing to main has caused 10+ hours of rework and broken CI |

---

## 1. Project Identity

Open-source **IS 456 RC beam design library** for structural engineers.
- **Python core** (`Python/structural_lib/`) — Design, detailing, optimization, BBS, DXF export
- **FastAPI backend** (`fastapi_app/`) — REST + WebSocket API
- **React 19 frontend** (`react_app/`) — 3D visualization with React Three Fiber
- **Current focus:** See [TASKS.md](../TASKS.md) for active work

---

## 2. Codex-Native Git/GitHub

Codex inspects the branch, worktree, diff, and PR; stages only intended paths;
creates a conventional commit; pushes without rewriting history; and creates or
updates the PR through the connected GitHub integration. See
`docs/git-automation/git-workflow-single-source.md`.

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
| **UI/IO** | `react_app/`, `fastapi_app/`, `visualization/` | External interfaces only |

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
| `useTorsionDesign` | Torsion design mutation | `useTorsionDesign.ts` |
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
| `useSimpleBatchDesign` | Lightweight batch-design orchestration | `useSimpleBatchDesign.ts` |
| `useLoadAnalysis` | Load-analysis API state | `useLoadAnalysis.ts` |
| `useParetoDesign` | Pareto optimization request/state | `useParetoDesign.ts` |
| `useProjectBOQ` | Project bill-of-quantities request/state | `useProjectBOQ.ts` |
| `useExportBuildingSummary` | Building-summary export | `useExportBuildingSummary.ts` |
| `useReducedMotion` | Accessibility motion preference | `useReducedMotion.ts` |
| `useWebGLContextLoss` | WebGL context-loss recovery | `useWebGLContextLoss.ts` |

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
| `HomePage`, `HubPage`, `ModeSelectPage` | Entry, workflow hub, and mode-selection routes |
| `BatchDesignPage`, `BeamDetailPage` | Batch and individual beam workflow routes |
| `BeamForm`, `BeamTable`, `CSVImportPanel`, `ResultsPanel` | Core beam input/import/result surfaces |
| `ParetoPanel`, `ProjectBOQPanel`, `SettingsPanel` | Optimization, quantity, and application settings panels |
| `ModernAppLayout`, `WorkspaceLayout`, `TopBar` | Primary application shells and navigation |
| `WorkflowBreadcrumb`, `WorkflowHint`, `ConnectionStatus`, `ToastContainer` | Workflow guidance and system feedback |
| `BentoGrid`, `BentoCard`, `BentoCardHeader` | Dashboard layout primitives |
| `Skeleton`, `SkeletonCard`, `SkeletonForm`, `SkeletonTableRow` | Generic loading-state primitives |
| `SkeletonBeamTable`, `SkeletonResultsPanel`, `SkeletonViewport` | Domain loading states |
| `LandingView` | Legacy/alternate landing surface retained for compatibility |

### FastAPI Endpoints (`fastapi_app/routers/`)

89 OpenAPI HTTP operation endpoints across 26 router modules. The separate
React-contract scanner currently matches 88 OpenAPI paths; that path metric is
not the operation count. The WebSocket route is also outside OpenAPI:

| Router | Endpoint | Purpose |
|--------|----------|---------|
| **design** | `POST /api/v1/design/beam` | Beam design (Mu, Vu, Ast) |
| | `POST /api/v1/design/beam/check` | Check existing beam design |
| | `POST /api/v1/design/beam/torsion` | Torsion design (IS 456 Cl 41) |
| | `POST /api/v1/design/beam/enhanced-shear` | Enhanced shear design |
| | `POST /api/v1/design/beam/ductility-check` | Ductility check |
| | `POST /api/v1/design/beam/slenderness-check` | Slenderness check |
| | `POST /api/v1/design/beam/deflection-check` | Deflection check |
| | `POST /api/v1/design/beam/crack-width-check` | Crack width check |
| | `POST /api/v1/design/beam/compliance` | Full compliance check |
| | `GET  /api/v1/design/limits` | Design parameter limits |
| **detailing** | `POST /api/v1/detailing/beam` | Rebar detailing |
| | `GET  /api/v1/detailing/bar-areas` | Standard bar area lookup |
| | `GET  /api/v1/detailing/development-length/{bar_diameter}` | Development length calc |
| | `POST /api/v1/detailing/anchorage-check` | Anchorage check |
| **analysis** | `POST /api/v1/analysis/loads/simple` | Simple load analysis |
| | `POST /api/v1/analysis/beam/smart` | Smart beam analysis |
| | `GET  /api/v1/analysis/limiting-values` | IS 456 limiting values |
| **imports** | `POST /api/v1/import/csv` | CSV file import (40+ column mappings) |
| | `POST /api/v1/import/csv/text` | CSV text/paste import |
| | `POST /api/v1/import/dual-csv` | ETABS dual CSV import |
| | `POST /api/v1/import/batch-design` | Batch design all beams (returns `utilization_ratio = Mu/Mu_cap`) |
| | `GET  /api/v1/import/formats` | Supported CSV formats |
| | `GET  /api/v1/import/sample` | Sample data for testing |
| **geometry** | `POST /api/v1/geometry/beam/3d` | Basic 3D beam geometry |
| | `POST /api/v1/geometry/beam/full` | Full 3D rebar/stirrup positions |
| | `POST /api/v1/geometry/reference-geometry` | Reference geometry |
| | `POST /api/v1/geometry/building` | Building 3D geometry |
| | `POST /api/v1/geometry/cross-section` | Cross-section visualization |
| **insights** | `POST /api/v1/insights/dashboard` | Batch analytics (pass rate, utilization) |
| | `POST /api/v1/insights/code-checks` | Live IS 456 clause checks |
| | `POST /api/v1/insights/suggestions` | AI rebar suggestions |
| | `POST /api/v1/insights/project-boq` | Project bill of quantities |
| **optimization** | `POST /api/v1/optimization/beam/cost` | Cost-optimized beam design |
| | `GET  /api/v1/optimization/cost-rates` | Material cost rates |
| | `POST /api/v1/optimization/beam/pareto` | Pareto multi-objective design alternatives |
| **rebar** | `POST /api/v1/rebar/validate` | Rebar configuration validation |
| | `POST /api/v1/rebar/apply` | Apply rebar configuration |
| **export** | `POST /api/v1/export/bbs` | BBS CSV download |
| | `POST /api/v1/export/dxf` | DXF drawing download |
| | `POST /api/v1/export/report` | HTML report download |
| | `POST /api/v1/export/building-summary` | Building summary export |
| **column** | `POST /api/v1/design/column/effective-length` | Effective length per IS 456 Table 28 |
| | `POST /api/v1/design/column/classify` | Classify column (short/slender) |
| | `POST /api/v1/design/column/eccentricity` | Minimum eccentricity |
| | `POST /api/v1/design/column/axial` | Short column axial capacity |
| | `POST /api/v1/design/column/uniaxial` | Short column uniaxial bending |
| | `POST /api/v1/design/column/interaction-curve` | P-M interaction curve |
| | `POST /api/v1/design/column/biaxial-check` | Biaxial bending check (Cl 39.6) |
| | `POST /api/v1/design/column/additional-moment` | Additional moment for slender columns (Cl 39.7.1) |
| | `POST /api/v1/design/column/long-column` | Long column design |
| | `POST /api/v1/design/column/helical-check` | Helical reinforcement check |
| | `POST /api/v1/design/column` | Unified column design |
| | `POST /api/v1/design/column/detailing` | Column detailing |
| | `POST /api/v1/design/column/ductile-detailing` | IS 13920 column ductile detailing |
| **health** | `GET  /health` | Basic health check |
| | `GET  /health/ready` | Readiness check |
| | `GET  /health/info` | Version & dependency info |
| **streaming** | `GET  /streaming/batch-design` | SSE batch design progress |
| | `GET  /streaming/job/{job_id}` | SSE job status |
| **websocket** | `WS  /ws/design/{session_id}` | Live WebSocket design updates |

### Library (`Python/structural_lib/`)

| Module | Key Functions |
|--------|---------------|
| `services/api.py` | 97 public API functions; implementations split across `beam_api.py`, `column_api.py`, and `common_api.py` (18 private helpers) |
| `api.py` | **Backward-compat stub only** — imports from `services/api.py` |
| `services/adapters.py` | `GenericCSVAdapter`, `ETABSAdapter`, `SAFEAdapter` |
| `visualization/geometry_3d.py` | `beam_to_3d_geometry()` — 3D rebar/stirrup positions |
| `codes/is456/` | `flexure.py`, `shear.py`, `detailing.py`, `torsion.py`, `serviceability.py` — IS 456:2000 |
| `codes/is456/column/` | `axial.py` (classify, eccentricity, capacity, effective length), `uniaxial.py` (P-M curves), `biaxial.py` (biaxial check) |
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
./run.sh find --api <func>                                   # Exact public API signature
```

---

## 5. Launching the App

### Docker Runtime: Colima (not Docker Desktop)

This project uses **Colima** as the Docker runtime on macOS — not Docker Desktop.

**Why Colima?**
- ~60% less idle RAM than Docker Desktop (~150MB vs ~400MB)
- No heavy GUI app running in the background
- CLI-only — perfect for headless Mac Mini / AI agent workflows
- Open source (MIT), 27K+ GitHub stars, actively maintained
- Native Apple Silicon support, same `docker` / `docker compose` CLI
- Free for all use (Docker Desktop requires paid license for companies >250 employees)

**Start Colima before using Docker:**
```bash
colima start --cpu 4 --memory 4              # Start the VM (first time downloads ~300MB image)
colima status                                 # Verify: "colima is running"
docker info                                   # Should show Colima context
```

**Stop when done (frees RAM):**
```bash
colima stop
```

> **Install (if missing):** `brew install docker docker-compose colima`
> **Full setup guide:** [mac-mini-setup.md](mac-mini-setup.md)

---

### Start Fresh — Kill Everything First

Before starting, kill any old processes so ports 8000 and 5173 are free.

**Step 1 — Resolve the project Python runtime:**
```bash
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib
./scripts/python_runtime.sh --diagnose
```

> The launcher selects the approved `.venv` from this checkout or the primary
> worktree and binds imports to the invoking worktree. A linked worktree does
> not need its own copied or symlinked `.venv`. Use
> `./scripts/python_runtime.sh -m uvicorn ...` for direct server commands.

**Step 2 — Kill old FastAPI (port 8000):**
```bash
lsof -ti :8000 | xargs kill -9 2>/dev/null; echo "port 8000 cleared"
```

**Step 3 — Kill old React / Vite (port 5173):**
```bash
lsof -ti :5173 | xargs kill -9 2>/dev/null; echo "port 5173 cleared"
```

**Step 4 — Stop any running Docker containers for this project:**
```bash
docker compose down 2>/dev/null; echo "docker stopped"
```

Now choose how you want to run the stack:

---

### Option A: Full Stack via Docker (recommended for production/testing)

> **Prerequisite:** Colima must be running (`colima start`). If `docker ps` gives "permission denied" or "cannot connect", start Colima first.

```bash
colima start --cpu 4 --memory 4                      # Start Docker runtime (if not already running)
docker compose up --build                            # FastAPI at http://localhost:8000/docs
```

**Full sequence from scratch (copy-paste ready):**
```bash
# 1. Go to project root
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib

# 2. Activate venv (needed for any Python commands outside Docker)
source .venv/bin/activate

# 3. Kill old processes
lsof -ti :8000 | xargs kill -9 2>/dev/null
lsof -ti :5173 | xargs kill -9 2>/dev/null
docker compose down 2>/dev/null

# 4. Start Colima (Docker runtime)
colima start --cpu 4 --memory 4

# 5. Build and start FastAPI container
docker compose up --build
# FastAPI is now at http://localhost:8000/docs

# 6. Open a NEW terminal for React
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib/react_app
npm run dev
# React is now at http://localhost:5173
```

This builds and runs the FastAPI container with all Python dependencies + sample data (`Etabs_CSV/`). The `/docs` page auto-generates interactive Swagger UI for all 89 current OpenAPI HTTP operations.

For development with hot-reload (code changes reflect without rebuild):
```bash
docker compose -f docker-compose.dev.yml up          # Mounts source + Etabs_CSV as volumes, auto-reloads
```

**Docker includes:**
- FastAPI app + structural_lib + all Python deps
- `Etabs_CSV/` sample data (beam_forces.csv, frames_geometry.csv, beam_design_data.csv)
- WeasyPrint system deps (cairo, pango, fonts) for PDF export
- Non-root user, healthcheck, graceful restart

### Option B: Local Development (FastAPI + React separately)

No Docker needed. Faster for day-to-day code changes.

**Full sequence from scratch (copy-paste ready):**

**Terminal 1 — FastAPI backend:**
```bash
# 1. Go to project root
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib

# 2. Activate venv
source .venv/bin/activate
# Prompt changes to: (.venv) pravinsurawase@macmini-dev ...

# 3. Kill old FastAPI if any
lsof -ti :8000 | xargs kill -9 2>/dev/null

# 4. Start FastAPI
.venv/bin/uvicorn fastapi_app.main:app --host "::" --port 8000 --reload
# Running at http://localhost:8000/docs
# Leave this terminal open — it must keep running
```

**Terminal 2 — React frontend (open a new terminal tab):**
```bash
# 1. Go to react_app folder
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib/react_app

# 2. Kill old React if any
lsof -ti :5173 | xargs kill -9 2>/dev/null

# 3. Start React
npm run dev
# Running at http://localhost:5173
# Leave this terminal open too
```

> No venv needed for React — it uses `node` / `npm`, not Python.

**Check it's working:**
```bash
curl http://localhost:8000/health           # Should return {"status":"ok"}
# Then open http://localhost:5173 in your browser
```

### Option C: Python library only (no UI)

```bash
./scripts/python_runtime.sh -m pip install -e Python/ # Install in dev mode
./scripts/python_runtime.sh -c "from structural_lib import design_beam_is456; print('OK')"
```

### Port Map

| Service | Port | URL |
|---------|------|-----|
| FastAPI (Docker) | 8000 | http://localhost:8000/docs |
| FastAPI (local) | 8000 | http://localhost:8000/docs |
| React (Vite dev) | 5173 | http://localhost:5173 |

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `docker ps` permission denied | Colima not running → `colima start --cpu 4 --memory 4` |
| Colima download/start fails | Run `colima status`, then inspect `~/.colima/_lima/colima/ha.stderr.log`; do not delete the transferred VM without approval |
| Port 8000 already in use | Inspect the listener: `lsof -nP -iTCP:8000 -sTCP:LISTEN` |
| Port 5173 already in use | Inspect the listener: `lsof -nP -iTCP:5173 -sTCP:LISTEN` |
| `uvicorn: command not found` | Use `./scripts/python_runtime.sh -m uvicorn` |
| `ModuleNotFoundError: structural_lib` | Run `./scripts/python_runtime.sh --diagnose`; reinstall only if the worktree source binding is correct |
| React shows blank / "cannot connect" | FastAPI not running — start it first on :8000 |
| React can't reach API | Ensure FastAPI is running on :8000 first |
| "Cannot connect to backend" in browser but `curl` works | macOS resolves `localhost` to IPv6 `::1`; uvicorn not bound to IPv6 — use `--host "::"` not `--host 0.0.0.0` |
| Sample data 404 in Docker | Ensure `Etabs_CSV/` is copied (Dockerfile) or mounted (docker-compose.dev.yml) |
| Python import errors | Use `./scripts/python_runtime.sh`, never bare `python` |

---

## 6. Quick Start (Agent Workflow)

```bash
# Session start
./run.sh session start                               # Verify env, read priorities
./run.sh session usage --checkpoint start --task-id TASK-XXX --task "short scope"

# Validate codebase
./run.sh check --quick                               # Fast validation (10 checks, <30s)
./run.sh check                                       # Full validation (31 checks, parallel)
./run.sh check --category api                        # One category only

# Run tests
./run.sh test                                        # Full pytest suite
./run.sh test -k "test_flexure" -v                   # Specific tests
./run.sh test --ci                                   # Full local CI

# Build & serve
docker compose up --build                            # http://localhost:8000/docs
cd react_app && npm run dev                          # http://localhost:5173
cd react_app && npm run build                        # Build check

# Release preflight
./run.sh release preflight 0.X.Y                     # Pre-release validation
./run.sh release preflight --docker                  # Run preflight in Docker (2GB memory limit)

# Session end
./run.sh session end                                 # Final read-only validation
```

Run `./run.sh --help` or `./run.sh <command> --help` for full usage.

---

## 7. Git Workflow

| Change Type | Strategy |
|-------------|----------|
| Production code (`Python/structural_lib/`) | PR required |
| FastAPI code (`fastapi_app/`) | PR required |
| React code (`react_app/`) | PR required |
| CI workflows / Dependencies | PR required |
| Docker config (`Dockerfile*`, `docker-compose*`) | PR required |
| Docs / tests / scripts (<=150 lines, <=2 files) | Direct commit OK |

Production, FastAPI, React, CI, dependency, Docker, and release changes use a
Codex-managed task branch and PR. Never bypass hooks or checks, automate Git
recovery, or rewrite history. Merge remains an explicit user-confirmation action.

**Commit format:** `type: description` (subject <=72 chars, no period at end)
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore`

**Session docs rule:** Update `SESSION_LOG.md` + `next-session-brief.md` in the
same candidate when their state changes. Include a PR number only when it is
already known before the freeze; never rewrite the candidate solely to add one.
Finish every session/task/handoff/receipt write, validate live repository
context read-only, create the candidate commit, then run plain
`session end` read-only before pushing. Keep later PR, hosted, and merge facts
external so they cannot restart the candidate. Preparation-only
`session end --fix` intentionally exits `2`, never final-success `0`.

### Session Workflow Checklist (MANDATORY)

```
START:  □ ./run.sh session context              ← quick orientation (brief + tasks + git)
        □ ./run.sh session start
        □ ./run.sh session usage --checkpoint start --task-id TASK-XXX --task "scope"
        □ ./run.sh preflight                     ← check branch, venv, ports, conflicts

END:    □ Codex reviews the scoped diff
        □ ./run.sh session usage --checkpoint closeout --elapsed-min N --verification "gate"
        □ ./run.sh session summary --write       ← only if explicitly needed
        □ ./run.sh session sync --fix            ← only if explicitly needed
        □ ./run.sh evolve --status              # P12 burn-in (remove after ~session 20) — OBSERVE only, do NOT run --fix
        □ Append to WORKLOG.md                   ← one line per change (MANDATORY)
        □ Update next-session-brief.md           ← what NEXT agent should do
        □ Update TASKS.md                        ← mark done, add new
        □ Create pre-commit Git handoff receipt
        □ ./run.sh context validate              ← read-only topology check
        □ Commit intended paths                  ← immutable local candidate
        □ ./run.sh session end --agent <role>    ← read-only verdict
        □ Push, hosted checks, merge              ← facts stay external
```

> **Why mandatory?** Skipping session end has caused 10+ hours of wasted rework. SESSION_LOG.md is the project memory — gaps mean lost context.

---

## 8. Key Scripts

**Preferred:** Use `./run.sh` for all common operations (run `./run.sh --help`).

| Action | run.sh | Direct script (fallback) |
|--------|--------|-------------------------|
| Session start | `./run.sh session start` | `./scripts/agent_start.sh --quick` |
| Git/GitHub closeout | Codex | [canonical workflow](../git-automation/git-workflow-single-source.md) |
| Full check | `./run.sh check` | N/A (orchestrator) |
| Quick check | `./run.sh check --quick` | N/A |
| Run tests | `./run.sh test` | `./scripts/python_runtime.sh -m pytest Python/tests/ -v` |
| Test changed | `./run.sh test --changed` | `./scripts/python_runtime.sh scripts/test_changed.py` |
| Pre-flight | `./run.sh preflight` | `./scripts/python_runtime.sh scripts/preflight.py` |
| Session context | `./run.sh session context` | `./scripts/python_runtime.sh scripts/session.py context` |
| Usage checkpoint | `./run.sh session usage ...` | `./scripts/python_runtime.sh scripts/session.py usage ...` |
| Find script | `./run.sh find "task"` | `./scripts/python_runtime.sh scripts/find_automation.py "task"` |
| API signatures | `./run.sh find --api <func>` | `./scripts/python_runtime.sh scripts/discover_api_signatures.py <func>` |
| Move file | N/A | `./scripts/python_runtime.sh scripts/safe_file_move.py old new` |
| Delete file | N/A | `./scripts/python_runtime.sh scripts/safe_file_delete.py file` |
| Create doc | N/A | `./scripts/python_runtime.sh scripts/create_doc.py path "Title"` |
| Fix links | `./run.sh check --category docs --fix` | `./scripts/python_runtime.sh scripts/check_links.py --fix` |
| Session end | `./run.sh session end` | `./scripts/python_runtime.sh scripts/session.py end` |
| Live context | `./run.sh context show <area>` | `./scripts/python_runtime.sh scripts/repo_context.py show <area>` |
| Context summary | `./run.sh context summary <area-or-folder>` | `./scripts/python_runtime.sh scripts/repo_context.py summary <area-or-folder>` |

**Never do:** automated Git recovery, history rewriting, raw `rm`/`mv` for repository docs, or documents without metadata.

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
| Unscoped Git changes | Mixed or lost work | Codex stages only intended paths |
| Using `--force` to bypass PR | Broken CI, lost work | Never bypass required checks |
| Duplicate React code | Broken features, bugs | Check `hooks/` and `components/` first |
| Guess API params (`width` vs `b_mm`) | Failed tests | `discover_api_signatures.py` |
| Import from stub `api.py` | Stale code path | Use `services/api.py` directly |
| Wrong module path (`adapters.py`) | Import error | `services/adapters.py` / `visualization/geometry_3d.py` |
| Manual file move/delete | 870+ broken links | `safe_file_move.py` / `safe_file_delete.py` |
| Skip validation | Runtime errors | Run tests + `check_*` scripts |
| Create duplicate docs | Clutter, confusion | Check `docs-canonical.json` first |
| Mix architecture layers | Import errors | Core → IS456 → Services → UI (one direction only) |
| Use `python` directly | Wrong env, missing deps | Always use `./scripts/python_runtime.sh` |
| Add/move a maintained area without context validation | Stale agent routing | Update `context-manifest.json`, then run `./run.sh context validate` |
| Run `docker` without Colima | "permission denied" errors | Run `colima start` before any `docker` command |
| `uvicorn --host 0.0.0.0` on Mac Mini | Browser "Cannot connect" but `curl` works | macOS resolves `localhost` to IPv6 `::1`; use `--host "::"` for dual-stack |
| `Path.read_text()` without encoding | Windows CI fails with UnicodeDecodeError | Always use `encoding="utf-8"` with `.read_text()` / `.write_text()` |
| Remove Required Reading from next-session-brief | Session check fails in CI | Keep `## Required Reading` section — validated by `scripts/session.py` |
| Add symbol to `api.__all__` without docs | API doc check fails in CI | Add `api.SYMBOL_NAME` usage example in `docs/reference/api.md` |

---

## 11. Domain-Specific Rules (Docs)

These rules auto-load via `.claude/rules/` and `.github/instructions/` for Claude Code and Copilot. For other agents:

| Domain | Key rule | Full reference |
|--------|----------|----------------|
| **New docs** | Must have metadata (Type/Audience/Status/Importance/Created). Use `create_doc.py` or add manually. | `.claude/rules/docs.md` |

---

## 12. VS Code Copilot Agents & Skills

### 16 Custom Agents (`@agent-name` in Copilot Chat)

| Agent | Role | When to Use |
|-------|------|-------------|
| `@orchestrator` | Plan & delegate | Multi-step tasks, unsure where to start |
| `@frontend` | React 19, R3F, Tailwind | Components, hooks, 3D visualization |
| `@backend` | Python structural_lib | IS 456 math, services, adapters |
| `@structural-math` | IS 456 pure math, core types | New structural elements (column, slab, footing) |
| `@api-developer` | FastAPI endpoints | New/modified API routes |
| `@structural-engineer` | IS 456 compliance | Formula validation, code review |
| `@reviewer` | Code review | Pre-commit quality check |
| `@ui-designer` | Visual design (read-only) | Layout planning before coding |
| `@doc-master` | Documentation | Session logs, archives, routing, links |
| `@ops` | Git, CI/CD, Docker | Commits, PRs, environment issues |
| `@tester` | Test creation & coverage | Test suites, coverage analysis |
| `@governance` | Project health & maintenance | Health scans, doc archival |
| `@security` | Security auditing, OWASP Top 10 | Dependency scanning, input validation review |
| `@library-expert` | IS 456 domain expert | Professional standards, usage guidance |
| `@agent-evolver` | Meta-agent: instruction evolution | Performance scoring, drift detection |
| `@innovator` | Research & innovation | Discover missing capabilities, prototype breakthroughs |

### 14 Skills (`/skill-name` in Copilot Chat)

| Skill | Purpose |
|-------|--------|
| `/session-management` | Automate session start/end workflow |
| `/safe-file-ops` | Move/delete files preserving 870+ links |
| `/api-discovery` | Look up exact API function signatures |
| `/is456-verification` | Run IS 456 tests by category |
| `/new-structural-element` | New structural element workflow (column, slab, footing) |
| `/architecture-check` | Validate 4-layer architecture boundaries |
| `/react-validation` | React build, lint, type-check, tests |
| `/function-quality-pipeline` | Mandatory 9-step quality pipeline for IS 456 functions |
| `/agent-evolution` | Agent self-evolution cycle |
| `/innovation-research` | Guided innovation research cycle |
| `/development-rules` | Hard-learned development rules by domain (Python, FastAPI, React, testing, security) |
| `/quality-gate` | 3-level pre-merge quality checks (commit, PR, release) |
| `/release-preflight` | 5-phase pre-release validation (packaging, UAT, security, API/doc, CI) |
| `/user-acceptance-test` | End-user perspective testing (pip install + all workflows) |

### 16 Prompt Files (`#prompt-name` in Copilot Chat)

| Prompt | Purpose |
|--------|---------|
| `#new-feature` | New feature workflow |
| `#bug-fix` | Bug fix workflow |
| `#code-review` | Review checklist |
| `#add-api-endpoint` | FastAPI endpoint workflow |
| `#session-start` | Session start checklist |
| `#session-end` | Session end (mandatory) |
| `#file-move` | Safe file migration |
| `#is456-verify` | IS 456 formula verification |
| `#add-is456-clause` | IS 456 clause implementation |
| `#add-structural-element` | New structural element (column, slab, footing) workflow |
| `#fix-test-failure` | Test failure diagnosis & fix |
| `#performance-optimization` | Profile, optimize, benchmark |
| `#context-recovery` | Resume after context overflow |
| `#master-workflow` | Master workflow orchestration |
| `#function-quality-gate` | IS 456 function quality gate (9-step) |
| `#innovation-research` | Innovation research cycle workflow |

### Handoff Chains

```
New feature:   @orchestrator → @backend → @api-developer → @frontend → @reviewer → @doc-master
IS 456 change: @orchestrator → @structural-engineer → @backend → @api-developer → @reviewer
New element:   @orchestrator → @structural-engineer → @structural-math → @tester → @backend → @api-developer → @frontend → @reviewer
Session end:   any agent → @doc-master → @ops
Innovation:    @orchestrator → @innovator → @structural-engineer (gate) → @structural-math → @tester → @reviewer → @doc-master → @ops
Security:      @orchestrator → @security → @backend/@frontend → @reviewer → @doc-master → @ops
```

> **Full usage guide:** [copilot-agents-usage-guide.md](../guides/copilot-agents-usage-guide.md)
> **Master plan:** [copilot-agent-master-plan.md](../_archive/planning-completed-2026-03/copilot-agent-master-plan.md)

---

## 13. Context Recovery (When LLM Loses Context)

When a conversation gets too long or the LLM loses context mid-session, use this recovery protocol:

### Quick Recovery (paste into new chat)

```
Read these files to recover session context:
1. docs/planning/next-session-brief.md  — what I'm working on
2. docs/TASKS.md (first 60 lines)       — active tasks
3. .github/copilot-instructions.md      — project rules
Then continue from where I left off.
```

### Full Recovery (for complex sessions)

```
Read these in order:
1. docs/planning/next-session-brief.md
2. docs/TASKS.md
3. docs/getting-started/agent-bootstrap.md (§1-4 only)
4. git log --oneline -20                    — recent changes this session
5. git diff --stat                          — uncommitted work
```

### Mid-Session Checkpoint

Before your context gets large, ask the agent:
```
Save a checkpoint: summarize what we've done so far, what's in progress,
and what's left. Write it to docs/planning/next-session-brief.md
```

### Key Principle

The **next-session-brief.md** file is the single source of truth for resuming
work. Update it when the handoff state changes, before the candidate freeze;
plain `session end` validates it without rewriting it. If context is lost, this
file + TASKS.md + recent git log is enough to resume.

---

## 14. On-Demand References

Load these only when working on that specific area:

| Topic | Document |
|-------|----------|
| **Copilot agents guide** | [copilot-agents-usage-guide.md](../guides/copilot-agents-usage-guide.md) |
| **Agent master plan** | [copilot-agent-master-plan.md](../_archive/planning-completed-2026-03/copilot-agent-master-plan.md) |
| Tech stack rationale | [tech-stack-rationale.md](../reference/tech-stack-rationale.md) |
| Command cheat sheet | [agent-quick-reference.md](../agents/guides/agent-quick-reference.md) |
| Deep workflow guide | [agent-workflow-master-guide.md](../agents/guides/agent-workflow-master-guide.md) |
| Current tasks | [TASKS.md](../TASKS.md) |
| Last session context | [next-session-brief.md](../planning/next-session-brief.md) |
| Git automation details | [git-automation/README.md](../git-automation/README.md) |
| API reference | [api.md](../reference/api.md) |
| Folder structure rules | [folder-structure-governance.md](../guidelines/folder-structure-governance.md) |
| Architecture overview | [project-overview.md](../architecture/project-overview.md) |
| Agent roles | [agents/README.md](../../agents/README.md) |

### Machine-Readable Authorities

- `scripts/control-plane.json` — canonical operation, command, alias, and permission registry
- `scripts/automation-map.json` — generated temporary compatibility projection
- `docs/docs-canonical.json` — topic-to-canonical-doc mapping
- `scripts/context-manifest.json` — repository-area roots and read-first routing

---

*Run `./scripts/agent_start.sh --quick` for live project status.*
