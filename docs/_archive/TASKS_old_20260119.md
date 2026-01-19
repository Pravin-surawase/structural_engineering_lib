# Task Board

> Single source of truth for work. Keep it short and current.

**Updated:** 2026-01-24 (Session 43 - LOD Threshold Validation)

> **Session 41-42 Progress:**
> ✅ PR #381 MERGED (dd4296f7) - Multi-format import system complete
> - 17 commits total on PR branch
> - Fixed black 26.1.0 formatting (pyproject.toml line-length)
> - Fixed mypy type annotations for all adapters
> - Fixed Pydantic v2 compatibility (ConfigDict, field serialization)
> - Fixed governance (kebab-case naming, root file count ≤10)
> - Fixed security path handling in feedback page
> - 111 passing tests with 85%+ coverage

> **Session 43 Progress:**
> 🔄 PR #385 IN PROGRESS - LOD Threshold Validation & Adjustment
> - Research: Validated 200-beam full-detail visualization feasibility
> - Created comprehensive performance analysis doc (500+ lines)
> - Adjusted LOD thresholds to match real-world projects:
>   - OLD: FULL(1), HIGH(≤50), MEDIUM(≤200), LOW(≤1000)
>   - NEW: HIGH(1-150), MEDIUM(151-400), LOW(401-1000), ULTRA_LOW(1000+)
> - Updated 24 unit tests (all passing)
> - Full test suite: 3165 passed

> **Note:** For detailed specifications, see [docs/planning/](planning/) folder.

---

## Rules (read first)
- **WIP = 2** (max 2 active tasks). Use WIP=2 only for independent tasks.
- Definition of Done: tests pass, docs updated, scanner passes.
- **Commit quality:** Batch session docs (TASKS, SESSION_LOG, handoff) into ONE commit at session end. Never pad commits.
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items.

---

## Current Release

- **Version:** v0.17.5 ✅ Released
- **Focus:** 3D Visualization Excellence (8-Week Plan)
- **Next:** v0.18.0 (March 2026)

---

## Active

### TASK-DATA-002: Complete Import System Integration 📋 NEXT

> **Goal:** Integrate new adapters with existing etabs_import.py and Streamlit pages
> **Timeline:** Session 43 (2026-01-20)
> **Dependencies:** PR #381 merged ✅

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-DATA-002.1** | Update etabs_import.py to use new adapters | MAIN | 2h | 🔴 CRITICAL | 📋 TODO |
| **TASK-DATA-002.2** | Update Streamlit pages for multi-format input | MAIN | 2h | 🔴 CRITICAL | 📋 TODO |
| **TASK-DATA-002.3** | Integration tests with real CSV data | MAIN | 1h | 🟠 HIGH | 📋 TODO |
| **TASK-DATA-002.4** | Update API documentation | MAIN | 1h | 🟡 MEDIUM | 📋 TODO |

---

### TASK-3D-003: 3D Visualization Enhancement ✅ IN PROGRESS

> **Goal:** Improve 3D visualization with LOD, performance optimization for 1000+ beams
> **Timeline:** Week 5-6 of 8-week plan
> **Dependencies:** TASK-DATA-002 complete

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-3D-003.1** | Add LOD (Level of Detail) for 1000+ beams | MAIN | 2h | 🔴 HIGH | ✅ Done (`b649316f`, PR #385) |
| **TASK-3D-003.2** | Add column toggle and building stats | MAIN | 30m | 🟡 MEDIUM | 📋 TODO |
| **TASK-3D-003.3** | Performance profiling and optimization | MAIN | 2h | 🟡 MEDIUM | 📋 TODO |

**Session 42 Deliverables:**
- `streamlit_app/utils/lod_manager.py` - LOD system (5 levels, 23 tests)
- `streamlit_app/pages/07_📥_multi_format_import.py` - Multi-format import page

---

## Completed (Archive after 20 items)

### TASK-DATA-001: Canonical Data Format Architecture ✅ COMPLETE (PR #381 MERGED)

> **PR:** #381 (dd4296f7)
> **Merged:** 2026-01-19

**Deliverables:**
- `Python/structural_lib/models.py` - 10 Pydantic model classes (44 tests)
- `Python/structural_lib/adapters.py` - 4 adapters: ETABS, SAFE, STAAD, Excel (39 tests)
- `Python/structural_lib/serialization.py` - JSON save/load utilities (29 tests)

**Key Achievements:**
- Multi-format import system with adapter pattern
- Pydantic v2 models with validation
- 111 passing tests with 85%+ coverage
- Full CI compliance (black, mypy, governance, security)

---

### TASK-3D-002: ETABS Real 3D Building Visualization ✅ COMPLETE (PR #381 MERGED)

> **Goal:** Complete production-ready ETABS VBA export macro for beam forces
> **Timeline:** Session 36 (2026-01-17)
> **Status:** ✅ PR #379 merged successfully

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-VBA-001.1** | Create 7 VBA modules (2,302 lines) | MAIN | 2h | 🔴 CRITICAL | ✅ Done |
| **TASK-VBA-001.2** | Add comprehensive user setup guide | MAIN | 1h | 🔴 HIGH | ✅ Done |
| **TASK-VBA-001.3** | Test on Windows with ETABS v22 | USER | 1h | 🟠 MEDIUM | ⏳ Pending user |
| **TASK-VBA-001.4** | Create Excel workbook template | MAIN | 30m | 🟠 MEDIUM | 📋 Backlog |

**Completed:** 7 VBA modules (2,302 lines), user guide (345 lines), CSV schema documented.

---

### TASK-604: Focus App on Core Features (Session 28 Cont.)

> **Goal:** Focus app on 4 core pages, hide secondary features, improve beam design UX
> **Timeline:** Session 28 (2026-01-15)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-604.1** | Hide 8 secondary pages (underscore prefix) | MAIN | 15m | 🔴 HIGH | ✅ Done (`1194f37`) |
| **TASK-604.2** | Update sidebar navigation messaging | MAIN | 5m | 🔴 HIGH | ✅ Done (`1194f37`) |
| **TASK-604.3** | Add input validation improvements to beam_design.py | MAIN | 30m | 🟠 MEDIUM | ✅ Done |
| **TASK-604.4** | Add Pareto explanation tooltips to cost_optimizer.py | MAIN | 30m | 🟠 MEDIUM | ✅ Done |

**Focus Pages (4 Visible):**
- ✅ 01_beam_design.py - Core design functionality
- ✅ 02_cost_optimizer.py - Key differentiator
- ✅ 03_compliance.py - Essential for engineers
- ✅ 04_documentation.py - User reference

**Hidden Pages (8 with underscore prefix):**
- _05_bbs_generator.py, _06_dxf_export.py, _07_report_generator.py
- _08_batch_design.py, _09_advanced_analysis.py, _10_learning_center.py
- _11_demo_showcase.py, _12_clause_traceability.py

---

### TASK-603: Remaining Modern Patterns ✅ COMPLETE (Session 30)

> **Goal:** Continue modern Streamlit patterns across remaining pages
> **Estimated:** 4-6 hours across 2-3 sessions
> **Actual:** 3 hours across 2 sessions (Sessions 29-30)
> **Completion:** 2026-01-15

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-603.1** | Add st.fragment to input sections (3 pages) | MAIN | 2h | 🟠 MEDIUM | ✅ Done (commits 9251430, 707c79a, 82d40f7) |
| **TASK-603.2** | Add st.dialog for export modals | MAIN | 1h | 🟠 MEDIUM | ⏭️ Skipped (download buttons more appropriate) |
| **TASK-603.3** | Apply CacheStatsFragment to cached pages | MAIN | 1h | 🟡 LOW | ✅ Done (commit 4834cda) |
| **TASK-603.4** | Performance optimization with fragments | MAIN | 1h | 🟡 LOW | ✅ Done (via 603.1-603.3) |

**Achievements:**
- ✅ **Fragment pattern applied:** beam_design.py, cost_optimizer.py, compliance.py
- ✅ **Performance improvement:** 80-90% faster input responsiveness
- ✅ **Cache visibility:** Auto-refreshing cache stats in cost_optimizer
- ✅ **User experience:** Partial page updates eliminate full reruns
- ⏭️ **Dialog pattern:** Skipped - current download button approach is cleaner for simple exports

**Technical Impact:**
- Input sections now use `@st.fragment` decorator for partial updates
- CacheStatsFragment shows real-time cache performance (5s refresh)
- Reduces CPU load by avoiding unnecessary full page reruns
- Better UX with instant feedback on input changes

**Critical Bug Discovery & Resolution (2026-01-13):**
- ❌ **Bug Found:** Session 30 fragments violated Streamlit API (st.sidebar in fragments)
- ✅ **Root Cause:** AST scanner couldn't detect indirect violations through function calls
- ✅ **Solution:** Built specialized fragment validator (290 lines)
- ✅ **Prevention:** Added to pre-commit hooks + CI workflow
- ✅ **Documentation:** Best practices guide (413 lines) + technical analysis (776 lines)
- ✅ **Commits:** 7 substantial commits (research, fixes, automation, docs, summary)
- ✅ **Result:** 0 violations, future bugs blocked, complete automation coverage

---

### TASK-605: Fragment API Violation Crisis Resolution ✅ COMPLETE (Session 30 Cont.)

> **Goal:** Fix critical bug where fragments called st.sidebar, build prevention automation
> **Context:** Session 30 fragments (commits 707c79a, 82d40f7) were broken at commit time
> **Timeline:** 2026-01-13 (single request, 7 commits)
> **Completion:** 2026-01-13

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-605.1** | Research why scanners missed violation | MAIN | 1h | 🔴 CRITICAL | ✅ Done (`90f035d`, 400 lines) |
| **TASK-605.2** | Fix beam_design theme toggle in fragment | MAIN | 20m | 🔴 CRITICAL | ✅ Done (`9cd4d1c`) |
| **TASK-605.3** | Fix cost_optimizer + compliance fragments | MAIN | 40m | 🔴 CRITICAL | ✅ Done (`45bc7c5`) |
| **TASK-605.4** | Create fragment API validator (automation) | MAIN | 1h | 🔴 CRITICAL | ✅ Done (`45bc7c5`, 290 lines) |
| **TASK-605.5** | Integrate validator into pre-commit + CI | MAIN | 30m | 🟠 MEDIUM | ✅ Done (`95bd87f`) |
| **TASK-605.6** | Document fragment best practices | MAIN | 45m | 🟠 MEDIUM | ✅ Done (`a3691d8`, 413 lines) |
| **TASK-605.7** | Comprehensive technical analysis | MAIN | 1h | 🟠 MEDIUM | ✅ Done (`fe826e0`, 776 lines) |

**Problem:**
- Session 30 added `@st.fragment` to cost_optimizer and compliance
- Fragments called `st.sidebar.subheader()` and `st.sidebar.form()` - **FORBIDDEN** by Streamlit API
- Runtime error: `StreamlitAPIException: Calling st.sidebar in a function wrapped with st.fragment is not supported`
- No existing automation detected this (AST scanner, AppTest, pylint, pre-commit, CI)

**Root Cause:**
- AST scanner sees function calls, not internal implementations
- Fragments called helper functions that used st.sidebar internally
- Cannot trace across function boundaries without full call-graph analysis

**Solution:**
1. **Research:** 400-line analysis of why automation failed, Streamlit rules, detection strategies
2. **Fix beam_design:** Remove theme toggle from fragment (uses sidebar internally)
3. **Fix cost_optimizer + compliance:** Move fragments inside `with st.sidebar:` context
4. **Build validator:** 290-line AST-based checker for fragment API violations
5. **Automate:** Add validator to pre-commit hooks + CI (blocks bad code)
6. **Document:** 413-line best practices guide with patterns, debugging, migration
7. **Summarize:** 776-line technical analysis with lessons learned

**Validation:**
- Validator found 4 violations in Session 30 code (lines 636, 638, 478, 480)
- After fixes: 0 violations detected
- Pre-commit hook passes: `check-fragment-violations`
- CI job added: `fragment-validator`
- All pages load without errors

**Impact:**
- ✅ 3 broken pages fixed (beam_design, cost_optimizer, compliance)
- ✅ Future violations blocked (pre-commit + CI)
- ✅ Complete documentation (best practices + troubleshooting)
- ✅ Process improvement (prevention > detection)
- ✅ 7 substantial commits (~2,000 LOC)

**Lessons Learned:**
1. **Domain-specific validation:** Generic tools miss domain-specific rules
2. **Prevention > detection:** Automation blocks bugs before commit
3. **Specialization matters:** Streamlit-specific checker catches what generic AST scanner misses
4. **Test what you deploy:** AppTest didn't exercise fragment code paths
5. **Documentation is automation:** Guides enable future agents to self-serve fixes

**Files Created/Modified:**
- `docs/research/fragment-api-restrictions-analysis.md` (400 lines)
- `scripts/check_fragment_violations.py` (290 lines)
- `docs/guidelines/streamlit-fragment-best-practices.md` (413 lines)
- `docs/planning/session-30-fragment-crisis-resolution.md` (776 lines)
- `.pre-commit-config.yaml` (1 hook added)
- `.github/workflows/streamlit-validation.yml` (1 job added)
- `streamlit_app/pages/01_beam_design.py` (simplified header)
- `streamlit_app/pages/02_cost_optimizer.py` (fragment moved inside sidebar)
- `streamlit_app/pages/03_compliance.py` (fragment moved inside sidebar)

---

## Up Next (Session 34+)

> **Session 34 Progress:** TASK-081 (Level C Serviceability) and TASK-138 (ETABS Import) completed. All PRs merged.

### 3D Visualization Program — Phase 0 (Feasibility + Library Prep) ✅ COMPLETE

> **Goal:** Prove Streamlit iframe/postMessage in production, ship a professional 3D data contract, and prep core library geometry.
> **Decision:** If iframe is blocked, ship Plotly 3D MVP while continuing library geometry work.
> **Completion:** PR #373 merged 2026-01-16 (Session 35)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-3D-01** | Streamlit Cloud iframe + postMessage POC (go/no-go) | DEVOPS | 1d | 🔴 HIGH | ✅ Complete (PR #373) |
| **TASK-3D-02** | Define 3D JSON contract + sample payload + api.md entry | DOCS | 1d | 🔴 HIGH | ✅ Complete (PR #373) |
| **TASK-3D-03** | Add `structural_lib.visualization.geometry_3d` core dataclasses + compute functions | DEV | 2d | 🔴 HIGH | ✅ Complete (PR #373) |
| **TASK-3D-04** | Implement `BeamDetailingResult.to_3d_json()` | DEV | 1d | 🟠 MEDIUM | ✅ Complete (PR #373) |
| **TASK-3D-05** | Geometry tests (>=90% module coverage) | TESTER | 1d | 🟠 MEDIUM | ✅ Complete (PR #373) |
| **TASK-3D-06** | Automation: `check_3d_payload.py` + pre-commit/CI hook | DEVOPS | 1d | 🟠 MEDIUM | ⏳ Backlog (V1.1) |

**Technical Achievements:**
- ✅ **Core Module:** `structural_lib/visualization/geometry_3d.py` (~700 LOC)
  - 5 dataclasses: Point3D, RebarSegment, RebarPath, StirrupLoop, Beam3DGeometry
  - 5 compute functions: rebar positions, stirrup paths, beam outline
  - Full JSON serialization via `to_dict()` methods
- ✅ **JSON Contract:** `docs/reference/3d-json-contract.md` with TypeScript types
- ✅ **Three.js Viewer:** `streamlit_app/static/beam_viewer_3d.html` (CDN Three.js r128)
- ✅ **Streamlit Component:** `streamlit_app/components/beam_viewer_3d.py`
- ✅ **Demo Page:** `streamlit_app/pages/05_3d_viewer_demo.py`
- ✅ **Tests:** 59 tests (48 unit + 11 integration), all passing
- ✅ **API Exports:** Added to `structural_lib/api.py`
- ✅ **API Docs:** Section 15 in `docs/reference/api.md`

**Coordinate System:**
- X = along span (0 to span_length)
- Y = across width (-width/2 to +width/2)
- Z = height (0 at bottom, depth at top)
- Units: millimeters throughout

---

### 3D Visualization Program — Phase 1 (Live Preview Foundation) ✅ COMPLETE

> **Goal:** Live 3D preview on beam design page with <100ms latency
> **Timeline:** Week 1-2 of 8-week plan (Jan 16 - Jan 31, 2026)
> **Reference:** [8-week-development-plan.md](planning/8-week-development-plan.md)
> **Completed:** Session 36-37 (PR #376 + PR #377)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-3D-07** | Plotly 3D mesh generation - concrete beam, rebar, stirrups | DEV | 2-3d | 🔴 HIGH | ✅ Done (Session 36, PR #376) |
| **TASK-3D-08** | Integrate 3D preview into `01_beam_design.py` (two-column layout) | DEV | 1d | 🔴 HIGH | ✅ Done (Session 36, PR #376) |
| **TASK-3D-09** | Add `@st.fragment` for live updates + debouncing | DEV | 1d | 🔴 HIGH | ✅ Done (Session 36, PR #376) |
| **TASK-3D-10** | Performance optimization (<50ms mesh generation) | DEV | 1d | 🟠 MEDIUM | ✅ Done (Session 36, 26 tests) |
| **TASK-3D-11** | Add status display (safe/unsafe, utilization %) | DEV | 0.5d | 🟠 MEDIUM | ✅ Done (Session 37, 2ac6e26) |
| **TASK-3D-12** | Performance benchmarks documentation | DOCS | 0.5d | 🟡 LOW | ✅ Done (Session 37, eef5fd9) |

**Deliverables:**
- ✅ `streamlit_app/components/visualizations_3d.py` (650+ lines, Plotly mesh generation)
- ✅ Updated `pages/01_beam_design.py` (live preview + status display)
- ✅ Unit tests (26 tests, 100% passing)
- ✅ Performance benchmarks documented (`docs/reference/3d-visualization-performance.md`)

---

### 3D Visualization Program — Phase 2 (CSV Import + Multi-Beam) 🔵 UP NEXT

> **Goal:** Import 1000+ beams from CSV, render multi-beam views, batch processing
> **Timeline:** Week 3-4 of 8-week plan (Feb 1 - Feb 14, 2026)
> **Reference:** [8-week-development-plan.md](planning/8-week-development-plan.md)
> **Depends on:** Phase 1 complete ✅

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-CSV-01** | CSV schema definition (ETABS/SAFE format compatibility) | DEV | 0.5d | 🔴 HIGH | ✅ Done (Session 38) |
| **TASK-CSV-02** | CSV parser with validation + error reporting | DEV | 1d | 🔴 HIGH | ⏳ Ready |
| **TASK-CSV-03** | File uploader UI with progress feedback | DEV | 0.5d | 🔴 HIGH | ⏳ Blocked by CSV-02 |
| **TASK-CSV-04** | Multi-beam 3D scene (grid layout, camera controls) | DEV | 1-2d | 🔴 HIGH | ⏳ Blocked by CSV-03 |
| **TASK-CSV-05** | Batch design processing (100+ beams/sec target) | DEV | 1d | 🟠 MEDIUM | ⏳ Blocked by CSV-04 |
| **TASK-CSV-06** | Results export (JSON summary, pass/fail report) | DEV | 0.5d | 🟠 MEDIUM | ⏳ Blocked by CSV-05 |
| **TASK-CSV-07** | Integration tests (large CSV files, edge cases) | DEV | 1d | 🟠 MEDIUM | ⏳ Blocked by CSV-05 |
| **TASK-CSV-08** | Documentation (CSV format spec, workflow guide) | DOCS | 0.5d | 🟡 LOW | ⏳ Blocked by CSV-07 |

**Technical Approach:**
- Leverage existing ETABS import foundation (TASK-138, PR #369)
- Plotly multi-trace for beam grid (5x5, 10x10 layouts)
- WebGL instancing for 1000+ beam performance
- Progress callbacks for large file feedback

---

### TASK-145: BMD/SFD Visualization Stack ✅ COMPLETE (Session 34)

> **Goal:** Add load diagram computation and visualization
> **Timeline:** Session 34 (2026-01-15)
> **PR:** #371 (Ready to merge)

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-145.1** | Add load diagram types (LoadType, LoadDefinition, CriticalPoint, LoadDiagramResult) | DEV | 30m | 🔴 HIGH | ✅ Done (2c72df2) |
| **TASK-145.2** | Implement load_analysis.py core (5 functions, ~450 LOC) | DEV | 2h | 🔴 HIGH | ✅ Done (2c72df2) |
| **TASK-145.3** | Add load_analysis tests (25 tests) | DEV | 1h | 🔴 HIGH | ✅ Done (2c72df2) |
| **TASK-145.4** | Export compute_bmd_sfd + types from api.py | DEV | 15m | 🔴 HIGH | ✅ Done (2c72df2) |
| **TASK-145.5** | Add API documentation for BMD/SFD | DOCS | 30m | 🟠 MEDIUM | ✅ Done (30bb874) |
| **TASK-145.6** | Add Plotly visualization helper (create_bmd_sfd_diagram) | DEV | 1h | 🟠 MEDIUM | ✅ Done (bba061c) |
| **TASK-145.7** | Add visualization tests (7 tests) | DEV | 30m | 🟠 MEDIUM | ✅ Done (bba061c) |
| **TASK-145.8** | (Future) Triangular load + applied moment support | DEV | 2h | 🟡 LOW | ⏳ Backlog |
| **TASK-145.9** | Integrate BMD/SFD into Streamlit beam design page | DEV | 1h | 🟠 MEDIUM | ✅ Done (9e16973) |

**Technical Implementation:**
- `compute_bmd_sfd()`: Superposition-based load combination
- Simply supported: UDL + Point load
- Cantilever: UDL + Point load
- Critical points: max BM, max/min SF, zero SF crossing
- Visualization: Plotly subplots with filled area + annotations

| ID | Task | Agent | Est | Priority | Status |
|----|------|-------|-----|----------|--------|
| **TASK-606** | Sync api.md to v0.17.5 (currently shows 0.16.6) | DOCS | 2h | 🟠 MEDIUM | ✅ Done (70a5290) |
| **TASK-087** | Complete anchorage details (hooks, bends, bundled bars) | DEV | 4h | 🟠 MEDIUM | ✅ Done (fed2740) |
| **TASK-085** | Torsion design module (IS 456 Cl 41) | DEV | 2-3d | 🟡 MEDIUM | ✅ Done (PR #366) |
| **TASK-082** | VBA parity - slenderness + anchorage | DEV | 1-2d | 🟡 MEDIUM | ✅ Done (PR #367) |
| **TASK-081** | Level C Serviceability (separate creep/shrinkage) | DEV | 1-2d | 🟡 MEDIUM | ✅ Done (PR #368, Session 34) |
| **TASK-138** | ETABS CSV Import mapping | DEV | 1-2d | 🟡 MEDIUM | ✅ Done (PR #369, Session 34) |
| **TASK-139** | ETABS API exports + documentation | DEV | 2h | 🟠 MEDIUM | ✅ Done (PR #370, Session 34) |

---

## Backlog

### v1.0+ Long-Term (March 2026+)

**Agent 9 - Advanced Optimization:**
| ID | Task | Est | Priority | Status |
|----|------|-----|----------|--------|
| ~~**TASK-287**~~ | ~~Predictive Velocity Modeling~~ | - | - | ✅ **DONE** (Session 34, 59925cc) |
| ~~**TASK-288**~~ | ~~Release Cadence Optimization~~ | - | - | ✅ **DONE** (Session 34, 59925cc) |
| ~~**TASK-289**~~ | ~~Governance Health Score~~ | - | - | ✅ **DONE** (Session 34, 59925cc) |
| **TASK-290** | Context Optimization for AI Agents | 6h | 🔵 P3-Low | 📋 Up Next |
| **TASK-291** | Technical Debt Dashboard | 5h | 🔵 P3-Low | ⏳ Blocked by 290 |

**Visualization & Developer Tools:**
| ID | Task | Est | Priority | Status |
|----|------|-----|----------|--------|
| **TASK-305** | Re-run navigation study | 1h | 🟡 P2-Medium | 📋 Up Next |
| ~~**TASK-145**~~ | ~~Visualization Stack (BMD/SFD, etc.)~~ | - | - | ✅ **DONE** (PR #371, Session 34) |
| **TASK-146** | DXF Quality Polish | 2-3 days | 🟡 MEDIUM | ⏳ Blocked (needs human CAD QA) |
| ~~**TASK-147**~~ | ~~Developer Documentation~~ | - | - | ✅ **DONE** (Session 34 cont., 7 commits)

**Beam Scope Extensions:**
| ID | Task | Est | Priority | Status |
|----|------|-----|----------|--------|
| ~~**TASK-081**~~ | ~~Level C Serviceability~~ | - | - | ✅ **DONE** (PR #368, Session 34) |
| ~~**TASK-138**~~ | ~~ETABS mapping~~ | - | - | ✅ **DONE** (PR #369, Session 34) |
| ~~**TASK-082**~~ | ~~VBA parity harness~~ | - | - | ✅ **DONE** (PR #367, Session 33) |
| ~~**TASK-085**~~ | ~~Torsion design~~ | - | - | ✅ **DONE** (PR #366, Session 33) |
| ~~**TASK-087**~~ | ~~Anchorage check~~ | - | - | Moved to Up Next |
| ~~**TASK-088**~~ | ~~Slenderness check~~ | - | - | ✅ **DONE** (validated Session 32) |

### Research Tasks (Deferred - User Validation Required)

> **Status:** Removed from active backlog until v1.0 ships
> **Research IDs:** TASK-220-227, TASK-231-234, TASK-241-244, TASK-250-253, TASK-262

---

## Recently Done

> **Archive Rule:** Move items to [tasks-history.md](_archive/tasks-history.md) after 20+ items or 14+ days old. Keep last 10-15 items.

| ID | Task | Agent | Status |
|----|------|-------|--------|
| **TASK-287** | Predictive Velocity Modeling: EMA-based velocity prediction + burnout risk assessment | MAIN | ✅ Session 34 (59925cc) |
| **TASK-288** | Release Cadence Optimization: Analyze releases + recommend optimal cadence | MAIN | ✅ Session 34 (59925cc) |
| **TASK-289** | Governance Health Score: 0-100 composite score + 5-component breakdown | MAIN | ✅ Session 34 (59925cc) |
| **TASK-147** | Developer Documentation: platform guide, integration examples, extension guide, API stability | MAIN | ✅ 7 commits 2026-01-15 |
| **TASK-145** | BMD/SFD Visualization: 1514 LOC module + tests + docs | DEV | ✅ PR #371 2026-01-15 |
| **TASK-139** | API exports for ETABS + Level C/ETABS docs (339 LOC) | DEV | ✅ PR #370 2026-01-15 |
| **TASK-081** | Level C Serviceability: 5 functions, 18 tests, separate creep/shrinkage per Annex C | DEV | ✅ PR #368 2026-01-15 |
| **TASK-138** | ETABS Import: 6 functions, 23 tests, CSV-first workflow | DEV | ✅ PR #369 2026-01-15 |
| **TASK-085** | Torsion module: IS 456 Cl 41 - 6 functions, 30 tests, API docs | DEV | ✅ PR #366 2026-01-15 |
| **TASK-082** | VBA parity: slenderness + anchorage functions (7 functions) | DEV | ✅ PR #367 2026-01-15 |
| **TASK-087** | Anchorage functions: hooks (90°/135°/180°), bends, stirrup anchorage | DEV | ✅ 2026-01-15 (fed2740) |
| **TASK-606** | API docs sync: version 0.17.5, check_beam_slenderness | DOCS | ✅ 2026-01-15 (70a5290) |
| **SESSION-32** | Deep library audit: validated 3 completed tasks wrongly in backlog (TASK-088, 520, 522) | MAIN | ✅ 2026-01-15 |
| **TASK-088** | Slenderness check (IS 456 Cl 23.3) - **Was wrongly in backlog** | DEV | ✅ Validated 2026-01-15 |
| **TASK-522** | Jinja2 report templates (3 templates: beam_design, summary, detailed) | DEV | ✅ PR #360 2026-01-14 |
| **TASK-284** | Weekly governance session: validation + link fixes + index refresh | MAIN | ✅ 2026-01-15 |
| **TASK-502** | VBA smoke test automation (script + docs + index update) | MAIN | ✅ 2026-01-15 |
| **TASK-601** | Enhanced AppTest framework: integration tests (14 new), fragment utilities, nightly workflow, code quality research | MAIN | ✅ PR #TBD 2026-01-16 |
| **TASK-600** | Streamlit fixes: stirrup diameter selection, PDF report data, AppTest automation (46 tests) | MAIN | ✅ PR #TBD 2026-01-15 |
| **REL-0175** | Release v0.17.5: Multi-Objective Pareto Optimization, API Signature Validation CI, 1317 tests | MAIN | ✅ 2026-01-15 |
| **INFRA-01** | Add check-api-signatures hook to pre-commit + CI api-signature-check job | DEVOPS | ✅ 2026-01-15 |
| **IMPL-008** | Fix Streamlit API issues and UI improvements (advanced analysis, utilization display, session state) | DEV | ✅ PR #361 2026-01-14 |
| **TASK-520** | Hypothesis property-based testing (strategies + 43 tests for flexure/shear/ductile) | DEV | ✅ 2026-01-14 |
| **TASK-521** | Fix deprecated error_message/remarks test patterns (10 tests → all 2742 pass) | DEV | ✅ 2026-01-14 |
| **TASK-523** | Hypothesis docs + CI integration (testing-strategy.md, nightly.yml) | DOCS | ✅ PR #358 2026-01-14 |
| **TASK-506** | Session 20-21 Validation & Test Fixes (17 broken tests → all pass, lint fixes) | MAIN | ✅ PR #357 2026-01-13 |
| **IMP-02** | Add diagnostics reminders to agent_start.sh + end_session.py | DEVOPS | ✅ 2026-01-13 |
| **IMP-03** | Add debug snapshot checklist to handoff docs | DOCS | ✅ 2026-01-13 |
| **API-01** | Generate API manifest (public functions + signatures) | DEVOPS | ✅ 2026-01-13 |
| **API-02** | Pre-commit check: API changes require manifest update | DEVOPS | ✅ 2026-01-13 |
| **API-03** | Onboarding “API touchpoints” checklist | DOCS | ✅ 2026-01-13 |
| **IMP-01** | Guardrail: fail CI if new scripts are added without updating `scripts/index.json` | DEVOPS | ✅ 2026-01-13 |
| **DEBUG-01** | Diagnostics bundle script (env, versions, git, logs) | DEVOPS | ✅ 2026-01-13 |
| **DEBUG-02** | Debug mode toggle + logging guidance (Streamlit + CLI) | DEV | ✅ 2026-01-13 |
| **TASK-460** | Fix Streamlit runtime errors (page_header signature, reportlab, width="stretch" migration, import checker) | DEV | ✅ PR #354 2026-01-13 |
| **TASK-457-P2** | Documentation Consolidation Phase 2: Archive 3 session-specific research files | DOCS | ✅ 2026-01-13 |
| **GITDOC-15-28** | Hook enforcement system: versioned hooks, git_ops.sh router, automation-first recovery, health check, test suite (14 tasks, 4 commits) | MAIN | ✅ 2026-01-12 |
| **GITDOC-01-14** | Git workflow automation-first: error clarity, hook capture, CI monitor, docs consolidation (14 tasks, PR #345) | MAIN | ✅ 2026-01-12 |
| **SESSION-19P4** | Git workflow improvements: error clarity, policy-aware merge, docs consistency, enforcement hook | MAIN | ✅ 2026-01-12 |
| **SESSION-19** | Python 3.11 Baseline Complete: v0.16.6 released, PR #343 merged | MAIN | ✅ 2026-01-12 |

> **Full History:** [docs/_archive/tasks-history.md](_archive/tasks-history.md)

---

## Archive

See full task history in [docs/_archive/tasks-history.md](_archive/tasks-history.md)
