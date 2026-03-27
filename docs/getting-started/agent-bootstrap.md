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

38 endpoints across 12 routers + 1 WebSocket:

| Router | Endpoint | Purpose |
|--------|----------|---------|
| **design** | `POST /api/v1/design/beam` | Beam design (Mu, Vu, Ast) |
| | `POST /api/v1/design/beam/check` | Check existing beam design |
| | `POST /api/v1/design/beam/torsion` | Torsion design (IS 456 Cl 41) |
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

**Step 1 — Activate the Python virtual environment (do this once per terminal session):**
```bash
cd /Users/pravinsurawase/VS_code_project/structural_engineering_lib
source .venv/bin/activate
# Your prompt will change to: (.venv) pravinsurawase@macmini-dev ...
# Verify: which python  →  should show .venv/bin/python
```

> **Never skip this.** Without it, `uvicorn` and `python` commands use the system Python (3.9) and won't find the project's packages.
> **Shortcut:** Instead of `source .venv/bin/activate`, you can always call `.venv/bin/uvicorn` and `.venv/bin/python` directly by full path — same result.

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

This builds and runs the FastAPI container with all Python dependencies + sample data (`Etabs_CSV/`). The `/docs` page auto-generates interactive Swagger UI for all 38 endpoints.

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
pip install -e Python/                               # Install in dev mode
python -c "from structural_lib import design_beam_is456; print('OK')"
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
| Colima download fails | Network issue → `colima delete -f && colima start` (retries download) |
| Colima won't start | `colima delete && colima start` (fresh VM) |
| Port 8000 already in use | `lsof -ti :8000 \| xargs kill -9` |
| Port 5173 already in use | `lsof -ti :5173 \| xargs kill -9` |
| `uvicorn: command not found` | Venv not activated → `source .venv/bin/activate` or use `.venv/bin/uvicorn` |
| `ModuleNotFoundError: structural_lib` | Venv not active or re-install → `source .venv/bin/activate && pip install -e Python/` |
| React shows blank / "cannot connect" | FastAPI not running — start it first on :8000 |
| React can't reach API | Ensure FastAPI is running on :8000 first |
| "Cannot connect to backend" in browser but `curl` works | macOS resolves `localhost` to IPv6 `::1`; uvicorn not bound to IPv6 — use `--host "::"` not `--host 0.0.0.0` |
| Sample data 404 in Docker | Ensure `Etabs_CSV/` is copied (Dockerfile) or mounted (docker-compose.dev.yml) |
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
| FastAPI code (`fastapi_app/`) | PR required |
| React code (`react_app/`) | PR required |
| VBA / CI workflows / Dependencies | PR required |
| Docker config (`Dockerfile*`, `docker-compose*`) | PR required |
| Docs / tests / scripts (<=150 lines, <=2 files) | Direct commit OK |

### ⚠ PR Enforcement (STRICT — do NOT bypass)

When `./run.sh pr status` or `should_use_pr.sh` says **"PR required"**, you MUST use a PR.

**NEVER use `--force` to bypass the PR check.** The `--force` flag exists for rare human-approved batching only.

Agents have historically:
- Used `--force` to skip PR checks and push directly to main
- Invented reasons like "small change" or "just a fix" to avoid PRs
- Caused merge conflicts, broken CI, and lost work (10+ hours wasted)

**The rule is simple:** If the script says PR, use PR. No exceptions. No `--force`. No excuses.

```bash
# Direct commit (only when script confirms it's OK)
./run.sh commit "docs: update guide"

# PR workflow (ALWAYS for production code)
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
        □ Append to WORKLOG.md                   ← one line per change (MANDATORY)
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
| Using `--force` to bypass PR | Broken CI, lost work | If script says PR, use PR. Never `--force`. |
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
| Run `docker` without Colima | "permission denied" errors | Run `colima start` before any `docker` command |
| `uvicorn --host 0.0.0.0` on Mac Mini | Browser "Cannot connect" but `curl` works | macOS resolves `localhost` to IPv6 `::1`; use `--host "::"` for dual-stack |

---

## 11. Domain-Specific Rules (Streamlit, VBA, Docs)

These rules auto-load via `.claude/rules/` and `.github/instructions/` for Claude Code and Copilot. For other agents:

| Domain | Key rule | Full reference |
|--------|----------|----------------|
| **Streamlit** | NEVER `st.sidebar` inside `@st.fragment` (crashes). Safe patterns: `data.get()`, `session_state.get()`. Module-level imports only. | `.claude/rules/streamlit.md` |
| **VBA/Excel** | Python + VBA parity required. Mac safety: `CDbl()` wraps. Always PR. | `.claude/rules/vba.md` |
| **New docs** | Must have metadata (Type/Audience/Status/Importance/Created). Use `create_doc.py` or add manually. | `.claude/rules/docs.md` |

---

## 12. VS Code Copilot Agents & Skills

### 9 Custom Agents (`@agent-name` in Copilot Chat)

| Agent | Role | When to Use |
|-------|------|-------------|
| `@orchestrator` | Plan & delegate | Multi-step tasks, unsure where to start |
| `@frontend` | React 19, R3F, Tailwind | Components, hooks, 3D visualization |
| `@backend` | Python structural_lib | IS 456 math, services, adapters |
| `@api-developer` | FastAPI endpoints | New/modified API routes |
| `@structural-engineer` | IS 456 compliance | Formula validation, code review |
| `@reviewer` | Code review | Pre-commit quality check |
| `@ui-designer` | Visual design (read-only) | Layout planning before coding |
| `@doc-master` | Documentation | Session logs, archives, indexes |
| `@ops` | Git, CI/CD, Docker | Commits, PRs, environment issues |

### 4 Skills (`/skill-name` in Copilot Chat)

| Skill | Purpose |
|-------|---------|
| `/session-management` | Automate session start/end workflow |
| `/safe-file-ops` | Move/delete files preserving 870+ links |
| `/api-discovery` | Look up exact API function signatures |
| `/is456-verification` | Run IS 456 tests by category |

### 8 Prompt Files (`#prompt-name` in Copilot Chat)

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

### Handoff Chains

```
New feature:   @orchestrator → @backend → @api-developer → @frontend → @reviewer → @doc-master
IS 456 change: @orchestrator → @structural-engineer → @backend → @api-developer → @reviewer
Session end:   any agent → @doc-master → @ops
```

> **Full usage guide:** [copilot-agents-usage-guide.md](../guides/copilot-agents-usage-guide.md)
> **Master plan:** [copilot-agent-master-plan.md](../planning/copilot-agent-master-plan.md)

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

The **next-session-brief.md** file is the single source of truth for resuming work. Every session end must update it. If context is lost, this file + TASKS.md + recent git log is enough to resume.

---

## 14. On-Demand References

Load these only when working on that specific area:

| Topic | Document |
|-------|----------|
| **Copilot agents guide** | [copilot-agents-usage-guide.md](../guides/copilot-agents-usage-guide.md) |
| **Agent master plan** | [copilot-agent-master-plan.md](../planning/copilot-agent-master-plan.md) |
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

### Machine-Readable Indexes

- `scripts/automation-map.json` — task-to-script mapping
- `docs/docs-canonical.json` — topic-to-canonical-doc mapping
- `scripts/index.json` — full automation catalog

---

*Run `./scripts/agent_start.sh --quick` for live project status.*
