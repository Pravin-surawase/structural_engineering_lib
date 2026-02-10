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

### 3-Layer Rule (never mix)

| Layer | Location | Rule |
|-------|----------|------|
| **Core** | `codes/is456/flexure.py`, `shear.py`, `detailing.py` | Pure math, NO I/O, explicit units (mm, N/mm2, kN, kNm) |
| **App** | `api.py`, `beam_pipeline.py`, `job_runner.py` | Orchestration, no formatting |
| **UI/IO** | `react_app/`, `streamlit_app/`, `fastapi_app/`, `dxf_export.py` | External interfaces only |

Core CANNOT import from App or UI. Units always explicit.

---

## 4. What Exists — DON'T Reinvent

### React Hooks (`react_app/src/hooks/`)

| Hook | Purpose | File |
|------|---------|------|
| `useCSVFileImport` | CSV import via API adapters (40+ columns) | `useCSVImport.ts` |
| `useDualCSVImport` | ETABS geometry+forces import | `useCSVImport.ts` |
| `useBatchDesign` | Batch design all beams | `useCSVImport.ts` |
| `useBeamGeometry` | 3D rebar/stirrup geometry from API | `useBeamGeometry.ts` |
| `useLiveDesign` | WebSocket live design | `useLiveDesign.ts` |
| `useAutoDesign` | Auto-trigger on input change | `useAutoDesign.ts` |
| `useBuildingGeometry` | Building 3D geometry | `useGeometryAdvanced.ts` |
| `useCrossSectionGeometry` | Cross-section visualization | `useGeometryAdvanced.ts` |
| `useRebarValidation` | Rebar edit validation | `useRebarEditor.ts` |

### React Components (`react_app/src/components/`)

| Component | Purpose |
|-----------|---------|
| `Viewport3D` | 3D beam/building visualization (R3F) |
| `BuildingEditorPage` | AG Grid beam editor |
| `DesignView` | Single beam design page |
| `ImportView` | CSV/JSON import UI |
| `FileDropZone` | Drag-drop CSV upload |

### FastAPI Endpoints (`fastapi_app/routers/`)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/import/csv` | CSV parsing with adapters (40+ column mappings) |
| `POST /api/v1/import/dual-csv` | ETABS dual CSV import |
| `POST /api/v1/import/batch-design` | Batch design all beams |
| `POST /api/v1/geometry/beam/full` | 3D rebar/stirrup positions |
| `POST /api/v1/design/beam` | Beam design (Mu, Vu, Ast) |
| `/ws/design/{session}` | Live WebSocket updates |
| `GET /api/v1/import/sample` | Sample data for testing |

### Library (`Python/structural_lib/`)

| Module | Key Functions |
|--------|---------------|
| `api.py` | `design_beam_is456()`, `detail_beam_is456()` — 43 public functions |
| `adapters.py` | `GenericCSVAdapter`, `ETABSAdapter`, `SAFEAdapter` |
| `geometry_3d.py` | `beam_to_3d_geometry()` — 3D rebar/stirrup positions |
| `codes/is456/` | `flexure.py`, `shear.py`, `detailing.py` — IS 456:2000 code |
| `bbs.py` | Bar bending schedule generation |
| `dxf_export.py` | DXF drawing export |
| `insights/` | Smart designer, suggestions, sensitivity analysis |

### State Stores (`react_app/src/store/`)

| Store | Purpose |
|-------|---------|
| `useDesignStore` | Single beam design inputs/results |
| `useImportedBeamsStore` | Imported CSV beams + selection |

**Quick check before coding:**
```bash
ls react_app/src/hooks/                              # React hooks
grep -r "@router" fastapi_app/routers/ | head -20    # FastAPI routes
grep -r "^def " Python/structural_lib/api.py | head -20  # Library functions
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
cd react_app && npm install && npm run dev           # http://localhost:5173

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
./scripts/finish_task_pr.sh TASK-XXX "description" --async

# Emergency recovery
./scripts/recover_git_state.sh
./scripts/git_ops.sh --status
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
| Manual file move/delete | 870+ broken links | `safe_file_move.py` / `safe_file_delete.py` |
| Skip validation | Runtime errors | Run tests + `check_*` scripts |
| Create duplicate docs | Clutter, confusion | Check `docs-canonical.json` first |
| Mix architecture layers | Import errors | Core cannot import App or UI |
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
