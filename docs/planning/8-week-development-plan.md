# V3 React Migration Roadmap (7-Week Plan)

**Type:** Plan
**Audience:** All Agents
**Status:** Active (V3 IN PROGRESS)
**Importance:** Critical
**Created:** 2026-01-15
**Last Updated:** 2026-01-24 (Session 72 - V3 Update)
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
| **Frontend** | React + React Three Fiber + Dockview | Premium workspace UI |
| **3D Engine** | Three.js via R3F | CAD-quality visualization |
| **Data Grid** | AG Grid | Professional engineering tables |
| **State** | React Query + Command/Event model | Real-time collaboration |

**Why V3:** Premium workspace experience (IDE-like), better performance (1000+ beams), richer ecosystem.

**Scope:** Beams only (IS 456 focus) - complete vertical slice before expansion.

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

## 📊 Current Status (Session 72, Jan 24, 2026)

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

### V3 Migration — 🚧 IN PROGRESS (Week 1 of 7)

| Phase | Week | Goal | Status |
|-------|------|------|--------|
| **Phase 1** | 1 | Automation Foundation | ✅ DONE (Sessions 69-72) |
| **Phase 2** | 2-3 | FastAPI Backend + Routes | 📋 NEXT |
| **Phase 3** | 3-4 | React Shell + 3D Viewport | 📋 TODO |
| **Phase 4** | 5 | WebSocket + Live Updates | 📋 TODO |
| **Phase 5** | 6-7 | Multi-Beam Intelligence | 📋 TODO |
| **Launch** | Week 7 | Beta Launch + Documentation | 🎯 TARGET |

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

Research: [websocket-live-updates-research.md](../research/websocket-live-updates-research.md)

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

### **Week 2-3: FastAPI Backend (Jan 27 - Feb 7)** 📋 NEXT

**Goal:** Create FastAPI wrapper for all 43 structural_lib functions

**Priority 1: FastAPI Skeleton (Week 2)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Create `fastapi_app/main.py` | 4h | 🔴 Critical | FastAPI app with CORS |
| Generate routes from `api.py` | 4h | 🔴 Critical | Use `generate_api_routes.py` |
| Add health check endpoint | 1h | 🔴 Critical | `/api/health` |
| Add OpenAPI documentation | 2h | 🔴 Critical | Auto-generated at `/docs` |
| Create Pydantic request models | 4h | 🔴 Critical | BeamDesignRequest, etc. |
| Write integration tests | 4h | 🔴 Critical | All 43 functions tested |

**Priority 2: WebSocket Live Design (Week 3)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Create `/ws/design/{session}` endpoint | 4h | 🔴 Critical | Native WebSocket |
| Add connection manager | 2h | 🟡 High | Track connected clients |
| Implement design request handler | 4h | 🔴 Critical | Call structural_lib |
| Test with simple client (Python) | 2h | 🟡 High | Verify round-trip |
| Add authentication (JWT) | 3h | 🟡 High | Secure WebSocket |
| Add rate limiting | 2h | 🟡 High | Prevent abuse |

**Priority 3: Batch Processing (Week 3)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Create `/stream/batch-design` SSE endpoint | 4h | 🟡 High | Server-Sent Events |
| Stream progress updates | 2h | 🟡 High | Real-time progress % |
| Add error streaming | 2h | 🟡 High | Stream validation errors |

**Deliverables Week 2-3:**
- `fastapi_app/main.py` (200+ lines)
- `fastapi_app/routes/` (10 route files)
- `fastapi_app/models/` (Pydantic models)
- Integration tests (100+ tests)
- OpenAPI spec at `/docs`

**Demo Ready:** Postman collection calling all 43 functions via FastAPI

---

### **Week 3-4: React Shell + 3D Viewport (Feb 7 - Feb 21)** 📋 TODO

**Goal:** Set up React frontend with basic 3D rendering

**Priority 1: React Project Setup (Week 3)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Create Vite + React + TypeScript project | 2h | 🔴 Critical | `npm create vite@latest` |
| Add React Three Fiber (R3F) | 2h | 🔴 Critical | 3D scene rendering |
| Add Dockview layout system | 4h | 🔴 Critical | IDE-like panels |
| Add AG Grid for tables | 3h | 🔴 Critical | Professional data grid |
| Add command palette (`cmdk`) | 3h | 🟡 High | Cmd+Shift+P shortcuts |
| Set up API client (Axios + React Query) | 4h | 🔴 Critical | Type-safe API calls |

**Priority 2: 3D Viewport (Week 4)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Create basic beam mesh renderer | 4h | 🔴 Critical | Solid 3D boxes |
| Add lighting and materials | 2h | 🔴 Critical | Realistic appearance |
| Add camera controls (orbit) | 2h | 🟡 High | Three.js OrbitControls |
| Render sample beams (10 beams) | 3h | 🔴 Critical | Multi-beam scene |
| Add hover tooltips | 3h | 🟡 High | Beam details on hover |

**Priority 3: Basic UI Integration (Week 4)**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Create design form (moment, width, depth) | 3h | 🔴 Critical | Input panel |
| Connect form to FastAPI | 2h | 🔴 Critical | POST /api/design-beam |
| Display results in panel | 3h | 🔴 Critical | Show Ast, status |
| Show 3D visualization of result | 4h | 🔴 Critical | Live preview |

**Deliverables Week 3-4:**
- React project (`react_app/`)
- 3D viewport with R3F
- Dockview layout working
- Basic design form + live 3D
- API integration tested

**Demo Ready:** Single beam design with live 3D update

---

### **Week 5: WebSocket + Live Updates (Feb 21 - Feb 28)** 📋 TODO

**Goal:** Replace HTTP polling with WebSocket for instant updates

**Priority 1: Frontend WebSocket Client**
| Task | Est | Priority | Deliverable |
|------|-----|----------|------------|
| Add `reconnecting-websocket` library | 1h | 🔴 Critical | Auto-reconnect |
| Create `useDesignWebSocket` hook | 4h | 🔴 Critical | React hook for WS |
| Handle connection state | 2h | 🟡 High | Show online/offline |
| Parse WebSocket messages | 2h | 🔴 Critical | Type-safe parsing |
| Update React state from messages | 3h | 🔴 Critical | Real-time updates |

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
- WebSocket integration complete
- <100ms design update latency
- Batch progress streaming working
- Error handling polished

**Demo Ready:** Instant design updates (modify input → 3D updates in <100ms)

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
1. Read this plan + [ai-workspace-expansion-v3.md](../research/ai-workspace-expansion-v3.md)
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
A: See [websocket-live-updates-research.md](../research/websocket-live-updates-research.md). Interactive = WS, Batch = SSE.

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
- [ai-workspace-expansion-v3.md](../research/ai-workspace-expansion-v3.md) - V3 architecture
- [websocket-live-updates-research.md](../research/websocket-live-updates-research.md) - WebSocket details
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
