# Agent Bootstrap — structural_engineering_lib

**Type:** Guide | **Audience:** All Agents | **Status:** Approved | **Importance:** Critical

> **This is THE canonical bootstrap for all AI agents.** Entry points (`CLAUDE.md`, `.github/copilot-instructions.md`) link here.

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

### React Components (`react_app/src/components/`)

| Component | Purpose |
|-----------|---------|
| `Viewport3D` | 3D beam/building visualization (R3F) |
| `BuildingEditorPage` | AG Grid beam editor |
| `DesignView` | Single beam design page (live 3D + code checks + rebar suggestions) |
| `DashboardPage` | Batch design analytics (pass/fail, utilization, stories) |
| `ImportView` | CSV/JSON import UI |
| `ExportPanel` | BBS CSV / DXF / HTML report download buttons |
| `FileDropZone` | Drag-drop CSV upload |
| `CommandPalette` | Global keyboard-driven command palette |

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
| | `POST /api/v1/import/batch-design` | Batch design all beams |
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


**Quick check before coding:**
```bash
ls react_app/src/hooks/                                         # React hooks
grep -r "@router" fastapi_app/routers/ | head -30               # FastAPI routes
grep "^def " Python/structural_lib/services/api.py | head -20   # Library functions
```

---

## 5. Quick Start

```bash
# Session start
./scripts/agent_start.sh --quick                     # 6s validation

# FastAPI backend (Docker)
docker compose up --build                            # http://localhost:8000/docs
docker compose -f docker-compose.dev.yml up          # Dev with hot reload

# React frontend
cd react_app && npm run dev                          # http://localhost:5173

# Python tests (CI requires 85% branch coverage)
cd Python && .venv/bin/pytest tests/ -v

# React build check
cd react_app && npm run build

# Streamlit app
./scripts/launch_streamlit.sh
```

---

## 6. Git Workflow

```bash
# Decision: PR or direct commit?
./scripts/should_use_pr.sh --explain
```

| Change Type | Strategy |
|-------------|----------|
| Production code (`Python/structural_lib/`) | PR required |
| VBA / CI workflows / Dependencies | PR required |
| Docs / tests / scripts (<=150 lines, <=2 files) | Direct commit OK |

```bash
# Direct commit
./scripts/ai_commit.sh "docs: update guide"

# PR workflow
./scripts/create_task_pr.sh TASK-XXX "description"
./scripts/ai_commit.sh "feat: implement X"          # Repeat as needed
./scripts/finish_task_pr.sh TASK-XXX "description"   # Polls CI, auto-merges

# Emergency recovery
./scripts/recover_git_state.sh
```

**Commit format:** `type: description` (subject <=72 chars, no period at end)
Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore`

**Session docs rule:** Update `SESSION_LOG.md` + `next-session-brief.md` in same PR. Log the **PR number** (not merge hash). One docs commit at end of session.

---

## 7. Key Scripts

| Action | Script |
|--------|--------|
| Commit | `./scripts/ai_commit.sh "msg"` |
| PR decision | `./scripts/should_use_pr.sh --explain` |
| Move file | `.venv/bin/python scripts/safe_file_move.py old new --dry-run` (then without flag) |
| Delete file | `.venv/bin/python scripts/safe_file_delete.py file` |
| Create doc | `.venv/bin/python scripts/create_doc.py path "Title"` |
| Fix links | `.venv/bin/python scripts/check_links.py --fix` |
| Find automation | `.venv/bin/python scripts/find_automation.py "task"` |
| API signatures | `.venv/bin/python scripts/discover_api_signatures.py <func>` |
| Streamlit check | `.venv/bin/python scripts/check_streamlit.py --all-pages` |
| Fragment check | `.venv/bin/python scripts/check_streamlit.py --fragments` |
| Streamlit launch | `./scripts/launch_streamlit.sh` |
| Session end | `.venv/bin/python scripts/session.py end` |

**Never do manually:** `git add/commit/push`, `rm/mv` docs, create docs without metadata.

---

## 8. Golden Rules

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

## 9. Common Mistakes

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

## 10. Scoped Rules (auto-loaded for Claude Code & Copilot)

Claude Code and GitHub Copilot load domain-specific rules automatically:
- `.claude/rules/` — Scoped by file path (Streamlit, React, Python core, VBA, FastAPI, docs)
- `.github/instructions/` — Scoped by `applyTo` glob patterns

If using other tools, the rules below apply. If using Claude Code or Copilot, you get these automatically.

## 11. Streamlit Safety (if working on Streamlit)

- **NEVER** use `st.sidebar` inside `@st.fragment` functions — causes `StreamlitAPIException`
- Use safe patterns: `data.get('key', default)` not `data['key']`, check `len()` before index access
- Imports at module level only — never `import` inside functions
- Use `st.session_state.get('key', default)` not `st.session_state.key`
- Run `check_streamlit.py --fragments` + `check_streamlit.py --all-pages` before committing
- Full rules: [streamlit-fragment-best-practices.md](../guidelines/streamlit-fragment-best-practices.md)

---

## 12. VBA Rules (if working on VBA/Excel)

- **Python + VBA parity** — Same formulas, units, edge-case behavior
- VBA import order matters — see [vba-guide.md](../contributing/vba-guide.md)
- Mac safety: wrap dimension multiplications in `CDbl()` to prevent overflow
- VBA changes always require PR

---

## 13. Document Metadata (required for new files)

Use `create_doc.py` which adds this automatically, or add manually:
```markdown
**Type:** [Guide|Research|Reference|Architecture|Decision]
**Audience:** [All Agents|Developers|Users]
**Status:** [Draft|Approved|Deprecated]
**Importance:** [Critical|High|Medium|Low]
**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
```

---

## 14. On-Demand References

Load these only when working on that specific area:

| Topic | Document |
|-------|----------|
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
