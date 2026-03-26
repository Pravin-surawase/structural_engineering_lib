# V3 React Migration Roadmap (7-Week Plan)

**Type:** Plan
**Audience:** All Agents
**Status:** Active (V3 IN PROGRESS)
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-27 (Session 81 - Dual CSV + Building Geometry + Rebar Helpers)
**Related Tasks:** TASK-V3-FOUNDATION, TASK-V3-REACT
**Timeline:** 7 weeks (Jan 24 - March 15, 2026)
**Release Target:** March 15, 2026 (V3 Beta Launch)
**Streamlit v0.19.0:** ✅ RELEASED (Jan 24, 2026)

---

## 🚀 Executive Summary

**Streamlit v0.19.0 shipped AHEAD OF SCHEDULE** (original plan: 8 weeks, actual: 2 weeks). Now migrating to V3 architecture:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | FastAPI + WebSocket + SSE | High-performance API, live updates |
| **Frontend** | React 19 + React Three Fiber 9 + Tailwind 4 | Premium workspace UI |
| **3D Engine** | Three.js via R3F + Drei | CAD-quality visualization |
| **State** | React Query 5 + Zustand 5 | Real-time collaboration |
| **UI System** | BentoGrid + FloatingDock + framer-motion | Modern Gen Z design |

**Why V3:** Premium workspace experience (IDE-like), better performance (1000+ beams), richer ecosystem.

**Scope:** Beams only (IS 456 focus) - complete vertical slice before expansion.

### Docker Quickstart (FastAPI)

```bash
# Build + run API
docker build -f Dockerfile.fastapi -t structeng-api:latest .
docker run -p 8000:8000 structeng-api:latest

# Dev (hot reload)
docker compose -f docker-compose.dev.yml up --build
```

---

## 🎯 The Bigger Picture

> **"What was not possible few years back, or only possible for big firms — now everyone can use them free."**

**Vision:** See [democratization-vision.md](democratization-vision.md)
- ✅ **Streamlit AI Chat** — AI assistant for design (v0.19.0)
- 🚧 **V3 React Migration** — Premium workspace UI (THIS PLAN)
- 📋 **User Automation** — Build your own workflows (V3.1)
- 📋 **Library Evolution** — Columns, slabs, multi-code (V4.0)

**Current Focus:** V3 migration with FastAPI + React for premium UX.

---

## 📊 Current Status (Session 81, Jan 27, 2026)

### Streamlit v0.19.0 — ✅ COMPLETE (Shipped Ahead of Schedule!)

| Phase | Original Est | Actual | Status |
|-------|--------------|--------|--------|
| **Phase 1** | Week 1-2 | Week 1 | ✅ Live 3D preview, caching |
| **Phase 2** | Week 3-4 | Week 2 | ✅ CSV import, multi-beam viz |
| **Phase 2.5** | Week 4 | Week 2 | ✅ Interactive controls |
| **Phase 3** | Week 5-6 | Week 3 | ✅ Rebar visualization |
| **Phase AI** | Week 6+ | Week 3 | ✅ AI chat interface |
| **Phase 4** | Week 7-8 | Week 4 | ✅ DXF/PDF export, v0.19.0 |

**Achievement:** Completed 8-week plan in 4 weeks (2x faster) due to automation scripts and AI agents.

### V3 Migration — 🚧 IN PROGRESS (Week 4 of 7)

| Phase | Week | Goal | Status |
|-------|------|------|--------|
| **Phase 1** | 1 | Automation Foundation | ✅ DONE (Sessions 69-72) |
| **Phase 2** | 2-3 | FastAPI Backend + Docker + Testing | ✅ DONE (Sessions 73-75) |
| **Phase 3** | 3-4 | React Shell + 3D Viewport | ✅ DONE (Sessions 75-76) |
| **Phase 4** | 5 | WebSocket + Live Updates | 🟡 PARTIAL |
| **Phase 5** | 6-7 | Multi-Beam Intelligence | 📋 TODO |
| **Launch** | Week 7 | Beta Launch + Documentation | 🎯 TARGET |

### Session 73 Accomplishments (Week 2 - FastAPI Skeleton)

| Category | Deliverable | Status |
|----------|-------------|--------|
| **FastAPI App** | `fastapi_app/` with 19 files, 20 routes | ✅ Complete |
| **Testing** | 24 integration tests (100% passing) | ✅ Complete |
| **Routes** | design, check, optimize, analyze, health | ✅ Complete |
| **OpenAPI** | Auto-docs at `/docs` | ✅ Complete |
| **CORS** | Configured for React frontend | ✅ Complete |
| **Tooling** | `discover_api_signatures.py` | ✅ NEW |
| **Documentation** | API integration analysis doc | ✅ NEW |

**Key Learning:** Created `discover_api_signatures.py` to prevent API signature guessing.
Use `inspect.signature()` BEFORE wrapping library functions.

**PR #404:** Merged with all 8 CI checks passing.

### Session 74 Accomplishments (Week 3 - Real-time Features)

| Category | Deliverable | Status |
|----------|-------------|--------|
| **WebSocket** | `/ws/design/{session}` live design endpoint | ✅ Complete |
| **SSE** | `/stream/batch-design` streaming endpoint | ✅ Complete |
| **Auth** | JWT helpers + token verification | ✅ Complete |
| **Rate Limit** | Request limiting helpers | ✅ Complete |
| **Docs** | Week 3 real-time learning guide | ✅ Complete |
| **Tests** | Auth + streaming tests | ✅ Complete |

**PR #406:** Merged with CI green.

### Session 75 Accomplishments (Week 3 - Testing + Docker + SDKs)

| Category | Deliverable | Status |
|----------|-------------|--------|
| **Load Testing** | `test_load.py` - 8 stress tests | ✅ Complete |
| **Integration Tests** | `test_integration.py` - 17 E2E tests | ✅ Complete |
| **Client SDKs** | Python + TypeScript clients in `clients/` | ✅ Complete |
| **SDK Generator** | `scripts/generate_client_sdks.py` | ✅ Complete |
| **Docker** | `Dockerfile.fastapi`, `docker-compose.yml` | ✅ Complete |
| **Docker Dev** | `docker-compose.dev.yml` with hot reload | ✅ Complete |
| **OpenAPI** | `openapi_baseline.json` refreshed | ✅ Complete |
| **Infrastructure** | V3 gap analysis Phase 3 complete | ✅ Complete |

**Total FastAPI Tests:** 99 (74 existing + 8 load + 17 integration)

**PR #407 + #408:** Merged with CI green.

### Session 69-72 Accomplishments (V3 Foundation)

| Category | Deliverable | Status |
|----------|-------------|--------|
| **Testing** | 41 contract tests (Pydantic schemas) | ✅ All passing |
| **Testing** | Schema snapshot validation | ✅ Baseline created |
| **Architecture** | WebSocket research (hybrid approach) | ✅ Complete |
| **Automation** | `generate_api_routes.py` (FastAPI scaffolding) | ✅ Ready |
| **Automation** | `validate_schema_snapshots.py` (drift detection) | ✅ Ready |
| **Automation** | `check_architecture_boundaries.py` (3-layer lint) | ✅ Ready |
| **Automation** | `check_ui_duplication.py` (AST scanner) | ✅ Ready |
| **Documentation** | 2 learning guides (900+ lines) | ✅ Complete |
| **Documentation** | automation-catalog.md (152 scripts) | ✅ Updated |

**Key Finding:** All 43 API functions are 100% FastAPI-compatible (validated via AST inspection).

**Performance:** API latency 0.01ms median (well under 50ms threshold).

---

## 📐 V3 Architecture Overview

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
│  Next.js + React Three Fiber + Dockview + AG Grid          │
│  - Command palette (cmdk)                                    │
│  - 3D workspace with instanced meshes                        │
│  - Professional data tables (AG Grid)                        │
│  - Keyboard shortcuts (VS Code-like)                         │
└──────────────┬──────────────────────────────────────────────┘
               │ WebSocket (interactive) / SSE (batch)
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  - REST API for design/detailing/optimization               │
│  - WebSocket for live design updates (<100ms)               │
│  - SSE for batch progress streaming                          │
│  - OpenAPI documentation (auto-generated)                    │
└──────────────┬──────────────────────────────────────────────┘
               │ Direct Python calls
               ▼
┌─────────────────────────────────────────────────────────────┐
│                    structural_lib                            │
│  43 API functions (100% FastAPI-compatible)                 │
│  - design_beam_is456(), detail_beam_is456()                 │
│  - optimize_beam_cost(), check_beam_is456()                 │
│  - beam_to_3d_geometry(), generate_bbs()                    │
└─────────────────────────────────────────────────────────────┘
```

### Why V3? (Decision Rationale)

| Capability | Streamlit | V3 React |
|------------|-----------|----------|
| **3D Performance** | 100 beams (Plotly limits) | 1000+ beams (R3F instancing) |
| **UI Flexibility** | Component-based | Full workspace control |
| **Real-time updates** | Full page rerun (100-500ms) | Delta updates (<100ms) |
| **Keyboard shortcuts** | Limited | Full VS Code-like experience |
| **Multi-user sync** | Not available | WebSocket broadcast |
| **Collaboration** | Not available | Command/event audit trail |
| **Offline capability** | No | Service worker cache |

**Key differentiator:** Premium, workspace-first experience (dockable panels, saved layouts, command palette).

### WebSocket Architecture (Hybrid Approach)

Research: [websocket-live-updates-research.md](../_archive/research/pre-v021/websocket-live-updates-research.md)

| Use Case | Technology | Reason |
|----------|------------|--------|
| **Interactive Design** | Native WebSocket | Lowest latency (<10ms), bi-directional |
| **Batch Progress** | Server-Sent Events (SSE) | Simple one-way stream |
| **Config Sync** | SSE | Broadcast to all clients |
| **Fallback** | HTTP REST | Works everywhere |

**Latency target:** <150ms total round-trip (design → API → React update).

---

## 🗓️ 7-Week V3 Migration Roadmap

### **Week 1: Automation Foundation (Jan 24)** ✅ COMPLETE

**Goal:** Prepare infrastructure for FastAPI migration

**Deliverables:**
- ✅ Contract testing suite (41 tests)
- ✅ Schema snapshot baseline (`schema_snapshots.json`)
- ✅ FastAPI route generator (`generate_api_routes.py`)
- ✅ Architecture linter (`check_architecture_boundaries.py`)
- ✅ WebSocket research document
- ✅ Learning guides (automation foundation + V3 basics)

**Evidence:** [SESSION_LOG.md Session 72](../SESSION_LOG.md)

---

### **Week 2-3: FastAPI Backend (Jan 27 - Feb 7)** ✅ COMPLETE (Sessions 73-74)

**Goal:** Create FastAPI wrapper for all 43 structural_lib functions

**Priority 1: FastAPI Skeleton (Week 2)** ✅ COMPLETE (Session 73, PR #404)
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create `fastapi_app/main.py` | 4h | 🔴 Critical | ✅ Done - CORS, middleware |
| Generate routes from `api.py` | 4h | 🔴 Critical | ✅ Done - 20 routes |
| Add health check endpoint | 1h | 🔴 Critical | ✅ Done - `/api/health` |
| Add OpenAPI documentation | 2h | 🔴 Critical | ✅ Done - `/docs` |
| Create Pydantic request models | 4h | 🔴 Critical | ✅ Done - BeamDesignRequest, etc. |
| Write integration tests | 4h | 🔴 Critical | ✅ Done - 24 tests, 100% passing |

**Evidence:** PR #404 merged, all 8 CI checks SUCCESS.

**Priority 2: WebSocket Live Design (Week 3)** ✅ COMPLETE (PR #406)
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create `/ws/design/{session}` endpoint | 4h | 🔴 Critical | ✅ Done - Native WebSocket |
| Add connection manager | 2h | 🟡 High | ✅ Done - Session tracking |
| Implement design request handler | 4h | 🔴 Critical | ✅ Done - structural_lib calls |
| Test with simple client (Python) | 2h | 🟡 High | ✅ Done - `fastapi_app/examples/test_client.py` |
| Add authentication (JWT) | 3h | 🟡 High | ✅ Done - `fastapi_app/auth.py` |
| Add rate limiting | 2h | 🟡 High | ✅ Done - `check_rate_limit` |

**Priority 3: Batch Processing (Week 3)** ✅ COMPLETE (PR #406)
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create `/stream/batch-design` SSE endpoint | 4h | 🟡 High | ✅ Done - SSE stream |
| Stream progress updates | 2h | 🟡 High | ✅ Done - progress events |
| Add error streaming | 2h | 🟡 High | ✅ Done - error events |

**Deliverables Week 2-3:**
- `fastapi_app/main.py` (200+ lines)
- `fastapi_app/routes/` (10 route files)
- `fastapi_app/models/` (Pydantic models)
- Integration tests (100+ tests)
- OpenAPI spec at `/docs`
 - WebSocket + SSE endpoints (live + batch)
 - Auth + rate limiting helpers
 - Learning guide: `docs/guides/week3-realtime-features-guide.md`

**Evidence:** PR #404 + PR #406 merged, CI checks green.

**Demo Ready:** Postman collection calling all 43 functions via FastAPI

---

### **Week 3-4: React Shell + 3D Viewport (Feb 7 - Feb 21)** ✅ COMPLETE

**Goal:** Set up React frontend with basic 3D rendering

**Priority 1: React Project Setup (Week 3)** ✅ COMPLETE (Sessions 75+)
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create Vite + React + TypeScript project | 2h | 🔴 Critical | ✅ Done - `react_app/` with Vite 7 |
| Add React Three Fiber (R3F) | 2h | 🔴 Critical | ✅ Done - R3F 9 + Drei 10.7 |
| Add Dockview layout system | 4h | 🔴 Critical | ✅ Done (replaced with BentoGrid) |
| Add modern UI system | 3h | 🔴 Critical | ✅ Done - Tailwind 4 + framer-motion |
| Add command palette (`cmdk`) | 3h | 🟡 High | ✅ Done - `CommandPalette.tsx` (Session 80) |
| Add AG Grid for tables | 3h | 🟡 High | ✅ Done - `BeamTable.tsx` (Session 80) |
| Set up API client (React Query) | 4h | 🔴 Critical | ✅ Done - React Query 5 + hooks |

**Current React Stack (verified Jan 26, 2026):**
- React 19.2 + Vite 7
- React Three Fiber 9.5 + Drei 10.7.7 (perfect compatibility ✅)
- Tailwind CSS 4.1 + framer-motion 12
- React Query 5.90 + Zustand 5
- AG Grid 32.3 + cmdk (Session 80)
- lucide-react icons

**Priority 2: 3D Viewport (Week 4)** ✅ COMPLETE
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create basic beam mesh renderer | 4h | 🔴 Critical | ✅ Done - `Viewport3D.tsx` |
| Add lighting and materials | 2h | 🔴 Critical | ✅ Done - PBR materials |
| Add camera controls (orbit) | 2h | 🟡 High | ✅ Done - OrbitControls |
| Render rebar visualization | 3h | 🔴 Critical | ✅ Done - `RebarVisualization` |
| Render stirrup visualization | 3h | 🔴 Critical | ✅ Done - `StirrupVisualization` |
| Multi-beam status colors | 2h | 🟡 High | ✅ Done - (Session 80) |

**Priority 3: API Integration Hooks** ✅ COMPLETE
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| `useBeamGeometry` hook | 4h | 🔴 Critical | ✅ Done - Fetches 3D geometry from API |
| `useCSVFileImport` hook | 3h | 🔴 Critical | ✅ Done - CSV via library adapters |
| `useCSVTextImport` hook | 2h | 🔴 Critical | ✅ Done - Clipboard paste |
| `useBatchDesign` hook | 2h | 🔴 Critical | ✅ Done - Batch design all beams |
| `useLiveDesign` hook | 2h | 🔴 Critical | ✅ Done - Live WebSocket workflow (Session 80) |
| `FileDropZone` component | 2h | 🟡 High | ✅ Done - Drag-drop CSV upload |

**Priority 4: Basic UI Components** ✅ COMPLETE
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create design form (moment, width, depth) | 3h | 🔴 Critical | ✅ Done - `BeamForm.tsx` |
| Display results in panel | 3h | 🔴 Critical | ✅ Done - `ResultsPanel.tsx` |
| CSV import panel | 3h | 🔴 Critical | ✅ Done - `CSVImportPanel.tsx` |
| Modern layout (BentoGrid) | 4h | 🔴 Critical | ✅ Done - `BentoGrid.tsx` |
| Bottom dock navigation | 2h | 🟡 High | ✅ Done - `FloatingDock.tsx` |

**Deliverables Week 3-4:**
- ✅ React project (`react_app/`) - Full Vite 7 + React 19 setup
- ✅ 3D viewport with R3F - `Viewport3D.tsx` with rebars/stirrups
- ✅ Modern Gen Z UI - BentoGrid + FloatingDock (replaced Dockview)
- ✅ API integration hooks - 5 hooks connecting to FastAPI
- ✅ Basic design form + live 3D preview
- ✅ Building frame 3D visualization (Session 78)
- ✅ AG Grid data table - `BeamTable.tsx` (Session 80)
- ✅ Command palette - `CommandPalette.tsx` (Session 80)
- ✅ Live design workflow - `useLiveDesign.ts` (Session 80)
- ✅ Real CSV sample data loading (Session 78)

**Evidence:** Commits `f335c22`, `d1b79ef`, `fc3c4ad`, `bb3b2e0`, `d0f968e`, `36c04ea`, `d98a12b`

**Demo Ready:** ✅ Single beam design with live 3D + CSV import + Building frame visualization

### Session 78 Accomplishments (Jan 26, 2026)

| Category | Deliverable | Status |
|----------|-------------|--------|
| **Sample Endpoint** | Load real CSV files (beam_forces + frames_geometry) | ✅ Done |
| **3D Positions** | Merge ETABS forces with 3D geometry (Point1/Point2) | ✅ Done |
| **BuildingFrame** | New component for imported beams visualization | ✅ Done |
| **Auto-detect Mode** | Viewport3D switches to building view automatically | ✅ Done |
| **Click Selection** | Click beams in 3D to select them | ✅ Done |

**Commits Session 78:**
- `36c04ea` - feat(api): replace hardcoded sample data with real CSV loading
- `d98a12b` - feat(react): add 3D building frame visualization for imported beams

**Remaining Week 3-4 Tasks:**
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| End-to-end test flow | 2h | 🔴 Critical | 🔄 IN PROGRESS |

---

### Session 81 Accomplishments (Jan 27, 2026)

| Category | Deliverable | Status |
|----------|-------------|--------|
| **Library** | `batch`, `imports`, `rebar` modules added | ✅ Done |
| **Geometry** | `building_to_3d_geometry` added | ✅ Done |
| **FastAPI** | `/api/v1/import/dual-csv` + SSE uses `design_beams_iter` | ✅ Done |
| **React** | `useDualCSVImport` hook + point1/point2 mapping | ✅ Done |
| **Tests** | Unit tests + dual CSV endpoint test | ✅ Done |

**Commit Session 81:**
- `6ee623f` - feat: add dual-csv import + building geometry + rebar helpers

---

### **Week 5: WebSocket + Live Updates (Feb 21 - Feb 28)** ✅ MOSTLY COMPLETE

**Goal:** Replace HTTP polling with WebSocket for instant updates

**Frontend WebSocket Hook:** ✅ COMPLETE
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Create `useDesignWebSocket` hook | 4h | 🔴 Critical | ✅ Done - `hooks/useDesignWebSocket.ts` |

**Session 79 Accomplishments (2026-01-26):**
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Add `reconnecting-websocket` library | 1h | 🔴 Critical | ✅ Done - npm package installed |
| Handle connection state | 2h | 🟡 High | ✅ Done - `ConnectionStatus` component |
| Add loading states (skeleton) | 2h | 🟡 High | ✅ Done - `Skeleton` components (6 variants) |
| Add error handling | 2h | 🟡 High | ✅ Done - `ErrorBoundary` + `Toast` system |

**New Components Created:**
- `reconnecting-websocket@4.4.0` - Auto-reconnecting WebSocket library
- `ConnectionStatus.tsx` - Visual indicator for WebSocket state
- `Skeleton.tsx` - 6 skeleton variants (table, card, results, viewport, form, generic)
- `ErrorBoundary.tsx` - React error boundary with retry
- `Toast.tsx` - Toast notification system (success/error/warning/info)
- Updated `useDesignWebSocket.ts` to use ReconnectingWebSocket

**Priority 2: Live Design Workflow** 🟡 PARTIAL
| Task | Est | Priority | Status |
|------|-----|----------|--------|
| Parse WebSocket messages | 2h | 🔴 Critical | ✅ Done - `useDesignWebSocket` |
| Update React state from messages | 3h | 🔴 Critical | ✅ Done - `useLiveDesign` |
| Wire live design UI to hooks | 3h | 🔴 Critical | ✅ Done - `DesignView` |

**Priority 2: Live Design Workflow**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Modify input → send via WebSocket | 2h | 🔴 Critical | No page reload |
| Receive result → update 3D instantly | 3h | 🔴 Critical | <100ms latency |
| Add loading states (skeleton) | 2h | 🟡 High | Smooth UX |
| Add error handling | 2h | 🟡 High | Show friendly errors |

**Priority 3: Batch Progress UI**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Connect to SSE `/stream/batch` | 3h | 🟡 High | EventSource API |
| Show progress bar | 2h | 🟡 High | % complete |
| Stream table rows as they complete | 4h | 🟡 High | Incremental results |

**Deliverables Week 5:**
- WebSocket hook + resilience complete
- Live design UI wiring (<100ms updates) complete
- Batch progress streaming working
- Error handling polished

**Demo Ready:** Live design updates (pending QA)

---

### **Week 6-7: Multi-Beam Intelligence + Polish (Feb 28 - Mar 15)** 📋 TODO

**Goal:** Full building visualization and launch-ready polish

**Priority 1: Multi-Beam Visualization (Week 6)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Load 100+ beams in 3D | 4h | 🔴 Critical | Instanced meshes |
| Story-based color coding | 2h | 🔴 Critical | 8-color palette |
| Utilization heat map mode | 3h | 🟡 High | Green → Red gradient |
| Interactive beam selection | 4h | 🔴 Critical | Click → details panel |
| Camera presets (iso/front/top) | 2h | 🟡 High | Quick navigation |
| Story filter dropdown | 2h | 🟡 High | View one story |

**Priority 2: Optimization UI (Week 6)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Beam line detection | 4h | 🟡 High | Group similar beams |
| Optimization table (before/after) | 4h | 🟡 High | AG Grid with diff |
| Apply/revert buttons | 2h | 🟡 High | Confirm changes |
| Cost savings display | 2h | 🟡 High | ₹/m and % savings |

**Priority 3: Launch Polish (Week 7)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Keyboard shortcuts | 4h | 🔴 Critical | VS Code-like |
| Command palette integration | 3h | 🔴 Critical | Cmd+Shift+P |
| Loading states polish | 3h | 🟡 High | Skeletons everywhere |
| Empty states | 2h | 🟡 High | Helpful guidance |
| Error messages | 2h | 🟡 High | Actionable errors |
| Performance optimization | 6h | 🔴 Critical | 1000 beams smooth |
| Browser testing | 4h | 🟡 High | Chrome, Firefox, Safari |
| Documentation | 8h | 🔴 Critical | User guide, API docs |

**Priority 4: Deployment (Week 7)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Deploy FastAPI to Vercel | 4h | 🔴 Critical | Backend live |
| Deploy React to Vercel | 2h | 🔴 Critical | Frontend live |
| Set up environment variables | 2h | 🔴 Critical | Secrets management |
| Add monitoring (Sentry) | 3h | 🟡 High | Error tracking |
| Load testing | 4h | 🟡 High | 100+ concurrent users |

**Deliverables Week 6-7:**
- Full building 3D (1000+ beams)
- Optimization workflow complete
- All UX polished
- Documentation complete
- Deployed to production

**Demo Ready:** Complete V3 beta launch

---

## Strategic Context

### Why React + FastAPI? (Decision Rationale)

**Streamlit Limitations Discovered:**
| Limitation | Impact | V3 Solution |
|------------|--------|-------------|
| Fragment API restrictions | Can't use `st.sidebar` in fragments | React - no restrictions |
| Full page reruns | 100-500ms latency | WebSocket delta updates |
| 3D performance | Max ~100 beams smoothly | R3F instancing (1000+ beams) |
| UI customization | Limited component control | Full workspace control |
| Keyboard shortcuts | Not available | VS Code-like shortcuts |
| Multi-user sync | Not possible | WebSocket broadcast |

**What We Keep:**
- ✅ **structural_lib** - Core design/detailing library (43 functions)
- ✅ **Insights engine** - SmartDesigner intelligence
- ✅ **ETABS adapters** - CSV parsing and normalization
- ✅ **3D geometry logic** - Port to R3F (60% reusable)

**What We Gain:**
- ✅ **Premium UX** - IDE-like workspace with dockable panels
- ✅ **Performance** - 10x more beams (100 → 1000+)
- ✅ **Real-time** - <100ms design updates via WebSocket
- ✅ **Ecosystem** - React Three Fiber, AG Grid, Dockview

### Why 7 Weeks? (Time Allocation)

| Phase | Time | Rationale |
|-------|------|-----------|
| FastAPI Backend | 2 weeks | Complete API wrapper + WebSocket |
| React Frontend | 2 weeks | Basic UI + 3D viewport |
| Live Updates | 1 week | WebSocket integration |
| Polish + Launch | 2 weeks | Multi-beam, optimization, docs |

**Total:** 7 weeks (5 weeks development + 2 weeks polish/launch).

**Why Realistic:**
- We have automation scripts (generate_api_routes.py)
- All API functions validated (100% FastAPI-compatible)
- Contract tests ready (41 passing)
- WebSocket research complete
- AI agents for development

### Core Differentiator (Unchanged)

```
ETABS:    Geometry → Analysis → Design → "SAFE" ← STOPS HERE
Our Tool: Geometry → Analysis → Design → DETAILING → 3D VIZ
                                          ↑ WE OWN THIS SPACE
```

**Premium Workspace:** We're not just analysis software. We're an **IDE for structural detailing**.

### Development Philosophy

```
Build → Test → Polish → Demo → Iterate
  ↑_________________________________|
```

**Core Principles:**
1. **Demo-driven development** - If you can't demo it impressively, it's not done
2. **Visual excellence first** - Every frame must look professional
3. **Performance non-negotiable** - <100ms latency target
4. **Automation everywhere** - Build tools that build features
5. **Quality code** - Readable, documented, tested
6. **Delay gracefully** - Nice-to-haves go to V3.1

### What We're NOT Doing

❌ **Rushing features** - Quality over quantity
❌ **Technical debt** - No shortcuts
❌ **Half-baked releases** - Ship when ready
❌ **Scope creep** - Beams only, no columns/slabs yet
❌ **Over-engineering** - Simple solutions first

---

## Success Metrics (7-Week Targets)

### Technical Excellence
- [ ] **<100ms latency** for WebSocket design updates
- [ ] **1000+ beams** rendered smoothly (60fps)
- [ ] **95%+ test coverage** for FastAPI routes
- [ ] **Zero critical bugs** in beta testing
- [ ] **Cross-browser** working (Chrome, Firefox, Safari)

### Code Quality
- [ ] **All API routes documented** (OpenAPI spec)
- [ ] **Integration tests** for all 43 functions
- [ ] **Performance benchmarks** documented
- [ ] **Security review** passed (JWT, CORS, rate limiting)

### User Experience
- [ ] **10+ beta testers** say "WOW"
- [ ] **5+ demo projects** showcasing features
- [ ] **User guide** clear for non-engineers
- [ ] **Visual quality** rivals commercial software
- [ ] **Keyboard shortcuts** intuitive

### Launch Readiness
- [ ] **Deployed** to Vercel (stable)
- [ ] **Monitoring** set up (Sentry)
- [ ] **Load tested** (100+ concurrent users)
- [ ] **Documentation** complete (user guide + API docs)
- [ ] **Marketing materials** ready (videos, screenshots)

---

## Delayed to V3.1 (Post-Beta Launch)

**Valuable but not MVP-critical:**

### Features (V3.1 - Month 4-5)

| Feature | Why Delayed | V3.1 Timeline |
|---------|-------------|---------------|
| DXF/PDF Drawing Export | Engineers can export screenshots for now | Month 4 |
| Material Quantity Takeoff | Nice-to-have for cost estimation | Month 4 |
| Detailing Automation | Complex, can do manually for now | Month 5 |
| Load Combination Viz | Advanced feature, focus on single load case first | Month 5 |
| Revision History | Version control not critical for beta | Month 5 |

### Module Expansion (V4.0 - Month 7+)

| Feature | Why Delayed | Timeline |
|---------|-------------|----------|
| **Column Design** | Major feature addition | Month 7-8 |
| **Slab Design** | Separate module | Month 8-9 |
| Foundation Design | Separate module | Month 9-10 |
| Eurocode/ACI Support | International expansion | Month 10+ |
| Multi-Span Beams | Scope expansion | Month 6 |

**Rationale:** Do ONE thing exceptionally well before expanding.

---

## Archived: Streamlit v0.19.0 Milestones

## Archived: Streamlit v0.19.0 Milestones

**Status:** ✅ ALL COMPLETE (Jan 15-24, 2026)

<details>
<summary>Click to expand Streamlit achievement details</summary>

### Phase 1-4 Complete (2 weeks instead of 8!)

| Phase | Goals | Status |
|-------|-------|--------|
| **Phase 1** | Live 3D preview | ✅ 839 lines visualizations_3d.py |
| **Phase 2** | CSV import, multi-beam | ✅ VBA integration, solid 3D |
| **Phase 2.5** | Interactive controls | ✅ Story filter, utilization heatmap |
| **Phase 3** | Rebar visualization | ✅ Variable stirrup zones |
| **Phase AI** | AI chat interface | ✅ 9-state workspace |
| **Phase 4** | DXF/PDF export | ✅ v0.19.0 released |

### Key Deliverables (Streamlit)

- `streamlit_app/pages/11_⚡_ai_assistant_v2.py` - AI workspace (1200+ lines)
- `streamlit_app/components/ai_workspace.py` - Dynamic workspace (1800+ lines)
- `streamlit_app/components/visualizations_3d.py` - 3D rendering (839 lines)
- `streamlit_app/components/geometry_3d.py` - Geometry logic (811 lines)
- 41 contract tests (Pydantic model validation)
- DXF/PDF export pages (enabled in v0.19.0)

### Why Ahead of Schedule?

1. **Automation scripts** - `generate_api_routes.py`, `validate_schema_snapshots.py`
2. **AI agents** - Copilot-driven development
3. **Quality-first approach** - Tests prevented rework
4. **Focused scope** - Beams only, no scope creep

</details>

---

## Development Tools & Resources

### Daily Use
- **Git:** `./scripts/ai_commit.sh "message"` (5s commits)
- **Testing:** `cd Python && pytest tests/ -v`
- **FastAPI:** `uvicorn fastapi_app.main:app --reload`
- **React:** `cd react_app && npm run dev`
- **Validation:** `.venv/bin/python scripts/check_architecture_boundaries.py`
- **API Discovery:** `.venv/bin/python scripts/discover_api_signatures.py <function>` (REQUIRED before wrapping)

### Weekly Use
- **Performance:** `.venv/bin/python scripts/benchmark_api_latency.py`
- **Coverage:** `cd Python && pytest --cov=structural_lib tests/`
- **Schema validation:** `.venv/bin/python scripts/validate_schema_snapshots.py`
- **Docs:** `./scripts/generate_all_indexes.sh`

### Before Each Commit
1. Run tests: `pytest`
2. Check architecture: `check_architecture_boundaries.py`
3. Validate schemas: `validate_schema_snapshots.py`
4. Format code: `black . && ruff check --fix .`
5. Update docs: `docs/SESSION_LOG.md`

---

## Communication Guidelines

### For AI Agents

**When starting work on a feature:**
1. Read this plan + [ai-workspace-expansion-v3.md](../_archive/research/pre-v021/ai-workspace-expansion-v3.md)
2. Check current week's priorities
3. Review related technical docs
4. Create tasks in `docs/TASKS.md`
5. Implement with quality focus
6. Test thoroughly (95%+ coverage)
7. Document as you build
8. Create demo if applicable
9. Update session log
10. Commit with `ai_commit.sh`

**Quality checklist:**
- [ ] Code is clean and readable
- [ ] Functions are documented (docstrings)
- [ ] Tests written (95%+ coverage)
- [ ] Performance benchmarked
- [ ] Architecture boundaries respected
- [ ] Demo created (if user-facing)
- [ ] Session log updated

**If blocked:**
- Document the blocker
- Try alternative approaches
- Ask for clarification
- Don't make assumptions

---

## FAQ for AI Agents

**Q: Streamlit feature X needs improvement. Should I work on it?**
A: No. Streamlit is frozen. Focus on V3 migration.

**Q: Should I build FastAPI routes manually?**
A: No. Use `generate_api_routes.py` to scaffold routes automatically.

**Q: React component needs styling. Where?**
A: Use Tailwind CSS utility classes. No custom CSS files.

**Q: WebSocket vs SSE for feature Y?**
A: See [websocket-live-updates-research.md](../_archive/research/pre-v021/websocket-live-updates-research.md). Interactive = WS, Batch = SSE.

**Q: This will take longer than estimated. What do I do?**
A: Document why, provide new estimate, ask for priority adjustment.

**Q: Should I optimize for performance now?**
A: Get it working first, then optimize. But keep performance in mind.

**Q: How much documentation is enough?**
A: Every public function needs docstring. User-facing features need user guide entries.

**Q: Test coverage is at 92%. Is that enough?**
A: Aim for 95%+. Critical paths (design, validation) should be 100%.

---

## Timeline Visualization (V3)

```
Week 1: Automation (DONE)   ████████ [Foundation Ready]
Week 2-3: FastAPI Backend    ████████ [API + WebSocket]
Week 3-4: React Shell        ████████ [UI + 3D Viewport]
─────────── Month 1 Complete ─────────────
Week 5: Live Updates         ████████ [WebSocket Integration]
Week 6-7: Multi-Beam + Polish████████ [Excellence]
─────────── Month 2 Complete ─────────────
Launch:   March 15, 2026     🚀 V3 Beta
```

---

## References

### Core Documentation
- [ai-workspace-expansion-v3.md](../_archive/research/pre-v021/ai-workspace-expansion-v3.md) - V3 architecture
- [websocket-live-updates-research.md](../_archive/research/pre-v021/websocket-live-updates-research.md) - WebSocket details
- [automation-foundation-learning-guide.md](../learning/automation-foundation-learning-guide.md) - Sessions 69-72 deep dive
- [v3-fastapi-learning-guide.md](../learning/v3-fastapi-learning-guide.md) - V3 basics tutorial

### V3 Technology Stack
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Three Fiber](https://docs.pmnd.rs/react-three-fiber/)
- [Dockview Layout](https://dockview.dev/)
- [AG Grid](https://www.ag-grid.com/)
- [cmdk Command Palette](https://cmdk.paco.me/)

### Engineering Patterns
- [ETABS vs STAAD.Pro](https://caddcentre.com/blog/etabs-vs-staadpro-a-beginners-guide-to-structural-design-software/)
- [CAD Software UX Patterns](https://medium.com/@creativenavy/cad-software-ui-design-patterns-benchmarking-97cc7834ad02)
- [Command Palette UX](https://blog.superhuman.com/how-to-build-a-remarkable-command-palette/)

---

## Final Reminders

### For Developers
- **You have 7 weeks.** Use them wisely.
- **Quality > Speed.** We're not rushing.
- **Demo often.** Show progress, get feedback.
- **Document everything.** Future you will thank you.
- **Automate repetitive tasks.** Work smarter.

### For AI Agents
- **Read docs FIRST.** Don't make assumptions.
- **Test thoroughly.** 95%+ coverage is required.
- **Update session logs.** Track decisions and learnings.
- **Stay focused.** Beams only, no scope creep.
- **Ask questions.** Better than wrong assumptions.

### For Users (Post-V3 Launch)
- **Your feedback matters.** Help us prioritize V3.1.
- **Report bugs.** We'll fix them quickly.
- **Share your projects.** We love seeing real-world use.
- **Suggest features.** But understand we have a roadmap.

---

**V3: Premium workspace for structural detailing.** 🚀

**Streamlit Released:** January 24, 2026 (v0.19.0) ✅
**V3 Beta Target:** March 15, 2026 (7 weeks)
**Next Check-in:** January 31, 2026 (FastAPI Week 1 review)
