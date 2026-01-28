# Agent Essentials — Critical Rules

**Type:** Guide
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-01-23
**Last Updated:** 2026-01-26

---

> **Load this FIRST.** Everything else is optional context.

## 🚨 THE ONE RULE

```bash
./scripts/ai_commit.sh "type: message"   # ALL commits
```

**NEVER use:** `git add`, `git commit`, `git push`, `git pull` manually.

## ⚡ Session Start

```bash
./scripts/agent_start.sh --quick         # 6 seconds, validates everything
```

## 🏗️ V3 Architecture — Know What Exists Before Coding!

**STOP duplicating code!** We have a mature stack:

### FastAPI Backend (`fastapi_app/`)
| Endpoint | Purpose | Use Instead Of |
|----------|---------|----------------|
| `POST /api/v1/import/csv` | CSV import via adapters (40+ columns) | Manual CSV parsing |
| `POST /api/v1/import/csv/text` | Clipboard CSV import | Parsing in React |
| `POST /api/v1/geometry/beam/full` | 3D rebar/stirrup geometry | Manual bar calculations |
| `POST /api/v1/design/beam` | Beam design (Mu/Vu) | Calling library directly |
| `/docs` | OpenAPI documentation | Guessing API schemas |

### React App (`react_app/src/`)

**Hooks** (`hooks/index.ts` — barrel export):
| Hook | Purpose | File |
|------|---------|------|
| `useBeamGeometry` | 3D rebar/stirrup geometry from API | `useBeamGeometry.ts` |
| `useCSVFileImport` | CSV file import via adapters | `useCSVImport.ts` |
| `useCSVTextImport` | CSV text/paste import | `useCSVImport.ts` |
| `useDualCSVImport` | ETABS geometry+forces import | `useCSVImport.ts` |
| `useBatchDesign` | Batch design all beams | `useCSVImport.ts` |
| `useLiveDesign` | WebSocket-based live design | `useLiveDesign.ts` |
| `useAutoDesign` | Auto-trigger design on input change | `useAutoDesign.ts` |
| `useBuildingGeometry` | Building 3D geometry | `useGeometryAdvanced.ts` |
| `useCrossSectionGeometry` | Cross-section visualization | `useGeometryAdvanced.ts` |
| `useRebarValidation` | Rebar edit validation | `useRebarEditor.ts` |
| `useRebarApply` | Apply rebar changes | `useRebarEditor.ts` |
| `useDashboardInsights` | Dashboard data | `useInsights.ts` |
| `useCodeChecks` | IS 456 code checks | `useInsights.ts` |
| `useRebarSuggestions` | AI-driven rebar suggestions | `useInsights.ts` |

**Key Components**:
| Component | Purpose | File |
|-----------|---------|------|
| `Viewport3D` | 3D beam/building visualization (R3F) | `components/Viewport3D.tsx` |
| `BuildingEditorPage` | AG Grid beam editor | `components/pages/BuildingEditorPage.tsx` |
| `DesignView` | Single beam design page | `components/DesignView.tsx` |
| `FileDropZone` | Drag-drop CSV upload | `components/ui/FileDropZone.tsx` |
| `BentoGrid` | Modern card layout | `components/ui/BentoGrid.tsx` |
| `FloatingDock` | Bottom navigation dock | `components/ui/FloatingDock.tsx` |

**State Stores** (`store/`):
| Store | Purpose | File |
|-------|---------|------|
| `useDesignStore` | Single beam design inputs/results | `designStore.ts` |
| `useImportedBeamsStore` | Imported CSV beams + selection | `importedBeamsStore.ts` |

### Library (`Python/structural_lib/`)
| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `api.py` | Main entry - 43 functions | `design_beam_is456()`, `detail_beam_is456()` |
| `adapters.py` | CSV parsing (ETABS, SAFE, Generic) | `GenericCSVAdapter`, `ETABSAdapter` |
| `geometry_3d.py` | 3D rebar/stirrup positions | `beam_to_3d_geometry()` |
| `codes/is456/` | IS 456 design code | `flexure.py`, `shear.py`, `detailing.py` |

## 📋 Before Manual Work — Use Scripts Instead

| Action | USE THIS SCRIPT |
|--------|-----------------|
| Commit code | `./scripts/ai_commit.sh "msg"` |
| Move file | `.venv/bin/python scripts/safe_file_move.py old.md new.md` |
| Delete file | `.venv/bin/python scripts/safe_file_delete.py file.md` |
| Create doc | `.venv/bin/python scripts/create_doc.py path/file.md "Title"` |
| Fix links | `.venv/bin/python scripts/fix_broken_links.py --fix` |
| Check Streamlit | `.venv/bin/python scripts/check_streamlit_issues.py --all-pages` |
| **Wrap API function** | `.venv/bin/python scripts/discover_api_signatures.py <func>` |

## 🔌 API Wrapper Rule

**BEFORE wrapping ANY `structural_lib.api` function:**
```bash
.venv/bin/python scripts/discover_api_signatures.py design_beam_is456
```
**NEVER guess** parameter names (`b_mm` not `width`) or return types.
See: [api-integration-mistakes-analysis.md](../research/api-integration-mistakes-analysis.md)

## 🎯 Golden Rules

1. **NEVER duplicate React code** — Check `react_app/src/hooks/` and `components/` first
2. **NEVER parse CSV manually** — Use `useCSVFileImport` hook → API → adapters
3. **NEVER calculate bar positions** — Use `useBeamGeometry` hook → API → geometry_3d
4. **Never create duplicate docs** — Check [docs-canonical.json](../docs-canonical.json) first
5. **Verify outdated info online** — AI models, library versions, frameworks
6. **Test before commit** — `cd react_app && npm run build` or `pytest Python/tests`

## 📖 Load More Context When Needed

| Task | Load This |
|------|-----------|
| React hooks | `react_app/src/hooks/` directory |
| Git decisions | [git-automation/workflow-guide.md](../git-automation/workflow-guide.md) |
| Streamlit UI | [guidelines/streamlit-fragment-best-practices.md](../guidelines/streamlit-fragment-best-practices.md) |
| API changes | [reference/api.md](../reference/api.md) |
| Architecture | [architecture/project-overview.md](../architecture/project-overview.md) |

## ⚠️ Knowledge Cutoff Warning

**Your training data is outdated!** Before using:
- AI model names → Verify via `fetch_webpage` to official docs
- Library versions → Check actual `pyproject.toml`
- Framework APIs → Verify current documentation

**Verified (2026-01-26):** `gpt-4o`, `gpt-4o-mini`, `claude-sonnet-4-20250514`

---

**Next:** [agent-bootstrap.md](agent-bootstrap.md) for full onboarding
