# Next Session Briefing

**Type:** Handoff
**Audience:** All Agents
**Status:** Active
**Importance:** Critical
**Created:** 2025-01-01
**Last Updated:** 2026-01-26

---

## Latest Handoff (auto)

<!-- HANDOFF:START -->
- Date: 2026-01-26
- Focus: React Library Integration Complete, Agent Bootstrap Updated
<!-- HANDOFF:END -->

| Release | Version | Status |
|---------|---------|--------|
| **Current** | v0.19.0 | ✅ Released |
| **Next** | v0.20.0 | 🚧 V3 Foundation (FastAPI + React + WebSocket) |

**Last Session:** Session 76 | **Focus:** Viewport3D wiring, agent bootstrap update

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
| `useCSVFileImport` | CSV import via library adapters |
| `useCSVTextImport` | Clipboard CSV import |
| `useBatchDesign` | Batch design all beams |
| `useDesignWebSocket` | WebSocket live design (partial) |

### FastAPI Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/import/csv` | CSV file import |
| `POST /api/v1/import/csv/text` | CSV text import |
| `POST /api/v1/geometry/beam/full` | Full 3D geometry |
| `POST /api/v1/design/beam` | Beam design |
| `/ws/design/{session}` | WebSocket live updates |

### Library Functions
| Module | Key Functions |
|--------|---------------|
| `api.py` | `design_beam_is456()`, `detail_beam_is456()` |
| `adapters.py` | `GenericCSVAdapter`, `ETABSAdapter` |
| `geometry_3d.py` | `beam_to_3d_geometry()` |

---

## 🔥 Next Session Priorities

### Priority 1: End-to-End Test (Required)

**Goal:** Verify FastAPI + React work together

```bash
# Terminal 1: Start FastAPI
docker compose -f docker-compose.dev.yml up --build

# Terminal 2: Start React
cd react_app && npm run dev

# Test: Open http://localhost:5173
# 1. Design a beam → View 3D
# 2. Import CSV → View multiple beams
```

### Priority 2: WebSocket Polish

**Goal:** Complete live design updates

| Task | Status |
|------|--------|
| Add reconnecting-websocket library | 📋 TODO |
| Handle connection state (online/offline) | 📋 TODO |
| Add loading skeleton states | 📋 TODO |
| Error handling | 📋 TODO |

### Priority 3: AG Grid (Optional)

**Goal:** Professional data tables for beam list

### Priority 4: Command Palette (Optional)

**Goal:** Keyboard shortcuts (Cmd+Shift+P)

---

## 📊 V3 Migration Progress

| Phase | Week | Goal | Status |
|-------|------|------|--------|
| **Phase 1** | 1 | Automation Foundation | ✅ DONE |
| **Phase 2** | 2-3 | FastAPI Backend | ✅ DONE |
| **Phase 3** | 3-4 | React Shell + 3D | ✅ DONE |
| **Phase 4** | 5 | WebSocket Live Updates | 🟡 PARTIAL |
| **Phase 5-6** | 6-7 | Multi-Beam + Polish | 📋 TODO |
| **Launch** | 7 | Beta Launch | 🎯 TARGET |

**Target:** March 15, 2026 (V3 Beta)

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
| 3D visualization | [react_app/src/components/Viewport3D.tsx](../../react_app/src/components/Viewport3D.tsx) |
| API hooks | [react_app/src/hooks/](../../react_app/src/hooks/) |
