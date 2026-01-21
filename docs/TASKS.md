# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-01-22 (Session 62b)

---

## Rules
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items

---

## Current Focus

- **Version:** v0.19.0 ✅ RELEASED → v0.20 (V3 Foundation)
- **Focus:** Library API additions for React V3 migration
- **Target:** March 2026 Launch → V3 React migration
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution

---

## Release Roadmap

| Version | Focus | Status | Key Deliverables |
|---------|-------|--------|------------------|
| **v0.18.1** | AI v2 Bugfix | ✅ DONE | PR #393 (CSV import fix) |
| **v0.19.0** | Phase 4 + Launch | ✅ RELEASED | DXF polish, AI model fix, Streamlit API index |
| **v0.19.1** | AI Tools + UX | 🚧 IN PROGRESS | DXF/report AI tools, rebar optimization |
| **v0.20** | V3 Foundation | 📋 NEXT | Library API additions for React migration |
| **v0.21+** | V3 React | 📋 PLANNED | React + R3F + FastAPI (6-week migration) |

---

## Session 62b Completed (2026-01-22)

| Task | Status | Commit |
|------|--------|--------|
| Fix bar spacing for multi-layer rebar | ✅ Done | `4f3bdfde` |
| Add DXF export AI tool | ✅ Done | `4f3bdfde` |
| Add report generation AI tool | ✅ Done | `4f3bdfde` |
| Add optimization button | ✅ Done | `5e44773c` |
| Add constructability score | ✅ Done | `5e44773c` |
| Industry report research | ✅ Done | `e7b15959` |
| Update agent bootstrap (indexes) | ✅ Done | `ece436ca` |

---

## Active Tasks

### TASK-AI-IMPORT-FIX: AI v2 CSV Import Fix ✅ COMPLETE

**Goal:** Fix AI v2 CSV import to use proven adapter infrastructure from multi-format import page

**Problem:** AI v2 page showed "0 inf% ❌ FAIL" for all beams because it used simple
auto_map_columns() instead of the robust adapter system.

| Sub-task | Status | Notes |
|----------|--------|-------|
| Research multi-format import adapters | ✅ Done | Session 56 - Identified root cause |
| Refactor to use adapters | ✅ Done | Session 56 - `56602b28` |
| Update copilot-instructions (AI model names) | ✅ Done | Session 56 - `bf06c66f` |
| Add lesson about reusing infrastructure | ✅ Done | Session 56 - `f05b6753` |
| Add adapter integration tests | ✅ Done | Session 56 - `0bba1afd` |
| Update TASKS.md + SESSION_LOG.md | ✅ Done | Session 61 |
| Create PR and merge | ✅ Done | PR #393 |

**Root Cause:** Depth column showed "5" instead of "500" due to incorrect column mapping.
The adapter system handles format-specific column detection and unit handling.

### TASK-AI-V2: AI Assistant v2 with Dynamic Workspace ✅ COMPLETE

**Goal:** Redesign AI chat with single dynamic workspace panel (35% chat / 65% workspace)

| Sub-task | Status | Notes |
|----------|--------|-------|
| AI workspace component | ✅ Done | Session 52 - `ai_workspace.py` |
| State machine (9 states) | ✅ Done | Session 53 - Added BUILDING_3D, CROSS_SECTION, REBAR_EDIT |
| Auto-column-mapping | ✅ Done | Session 52 - Detect ETABS columns |
| Sample data (10 beams) | ✅ Done | Session 52 - Built-in demo |
| AI v2 page | ✅ Done | Session 52 - `11_⚡_ai_assistant_v2.py` |
| Chat commands | ✅ Done | Session 53 - building 3d, edit rebar, cross section, select |
| Page 07 beam detail 3D | ✅ Done | Session 52 - `e1189937` |
| **Building 3D view** | ✅ Done | Session 53 - Full building visualization |
| **Interactive rebar editor** | ✅ Done | Session 53 - Live design checks |
| **Cross-section view** | ✅ Done | Session 53 - Professional 2D with dimensions |
| **Material takeoff** | ✅ Done | Session 53 - Concrete m³, steel kg, cost |
| **Cost estimation** | ✅ Done | Session 53 - ₹/m³, ₹/kg, per-meter cost |

**Session 52-53 Commits: 12 total**

### TASK-AI-V2-POLISH: AI v2 Production Polish ✅ COMPLETE

**Goal:** Bug fixes, edge cases, polish for production

| Sub-task | Status | Notes |
|----------|--------|-------|
| Safety fixes (zero-division) | ✅ Done | Session 54 - Guards for fy, progress calc |
| Loading states/spinners | ✅ Done | Session 54 - Sample load, CSV processing |
| Feature highlights | ✅ Done | Session 54 - 5-column icons |
| Chat tips | ✅ Done | Session 54 - Info box with workflow |
| Helpful tooltips | ✅ Done | Session 54 - All action buttons |
| Cross-section button | ✅ Done | Session 54 - Added to results navigation |
| Failed beam warning | ✅ Done | Session 54 - Contextual guidance |
| CSV/Summary export | ✅ Done | Session 54 - Dashboard export tab |

**Session 54 Commits: 5 on PR + 2 on main**

### TASK-PHASE4: CAD Quality + Launch Prep (v0.19) 🚧 IN PROGRESS

**Goal:** Polish for production launch, CAD-quality rendering
**Target:** March 2026 Launch

| Sub-task | Status | Priority | Est | Notes |
|----------|--------|----------|-----|-------|
| Merge PR #393 (CSV import fix) | ✅ DONE | 🔴 High | 1h | Merged 2026-01-20 |
| PyVista evaluation | ✅ DONE | 🔴 High | 2d | Hybrid: Plotly+PyVista export |
| DXF/PDF export pages | ✅ DONE | 🔴 High | 4d | Session 59 - Pages 08/09 enabled |
| DXF quick export in beam design | ✅ DONE | 🔴 High | 1h | Session 59 - Tab5 integration |
| LOD performance optimization | ✅ DONE | 🟡 Medium | 2d | Session 59 - 1000+ beams support |
| Print-ready reports | ✅ DONE | 🟡 Medium | 2d | PDF generator complete |
| Export component tests | ✅ DONE | 🟡 Medium | 1h | Session 59 - 14 tests |
| User testing + feedback | 📋 TODO | 🟡 Medium | 3d | Beta testing cycle |
| Documentation polish | 📋 TODO | 🟡 Medium | 2d | User guide, tutorials |

**Session 59 Progress (Phase 3):**
- Enabled DXF export page (08_📐_dxf_export.py) - 608 lines
- Enabled PDF report page (09_📄_report_generator.py) - 505 lines
- Added show_dxf_export() to beam design export tab
- Integrated LOD manager into multi-beam 3D visualization
- Added 14 tests for export components

### TASK-V3-FOUNDATION: Library APIs for V3 (v0.20) 📋 PLANNED

**Goal:** Add library functions needed for React V3 migration
**Prerequisite:** Complete v0.19 launch first

| API Function | Status | Priority | Notes |
|--------------|--------|----------|-------|
| `modify_beam_reinforcement()` | 📋 TODO | 🔴 P0 | Edit rebar API |
| `validate_beam_design()` | 📋 TODO | 🔴 P0 | Real-time validation (<100ms) |
| `compare_beam_designs()` | 📋 TODO | 🔴 P0 | Before/after diff |
| `compute_beam_cost()` | 📋 TODO | 🔴 P0 | Standardized cost calc |
| `detect_beam_lines()` | 📋 TODO | 🟡 P1 | Multi-beam intelligence |
| `analyze_beam_line()` | 📋 TODO | 🟡 P1 | Line analysis |
| `optimize_beam_line()` | 📋 TODO | 🟡 P1 | Line optimization |
| `score_constructability()` | 📋 TODO | 🟡 P1 | Congestion scoring |
| Professional API docs | 📋 TODO | 🔴 P0 | OpenAPI-ready docs |

**Why Before V3:** V3 FastAPI wrapper needs stable, well-documented APIs.
See: [ai-workspace-expansion-v3.md](research/ai-workspace-expansion-v3.md)

### TASK-V3-REACT: React Migration (v0.21+) 📋 POST-LAUNCH

**Goal:** 6-week React + R3F + FastAPI migration
**Status:** DO NOT START before March 2026 launch
**Stack:** React + React Three Fiber + Dockview + AG Grid + FastAPI

See: [ai-workspace-expansion-v3.md](research/ai-workspace-expansion-v3.md)

### TASK-REBAR-3D: Phase 3 - Rebar Visualization ✅ COMPLETE

**Goal:** Show actual reinforcement bars from design in 3D view

| Sub-task | Status | Notes |
|----------|--------|-------|
| `calculate_rebar_layout()` function | ✅ Done | Session 51 - From Ast → nTdia |
| Variable stirrup zones (2d rule) | ✅ Done | Session 51 - Tighter at supports |
| Integrate with AI 3D tab | ✅ Done | Session 51 - Shows actual bars |
| Rebar summary display | ✅ Done | Session 51 - "4T16 + 2T16 hanger" |
| Development length (Ld) | ✅ Done | Session 51 - IS 456 Cl 26.2.1 |
| Lap length calculation | ✅ Done | Session 51 - 1.3 × Ld |
| Add to Beam Design page | ✅ Done | Session 51 - Variable stirrups |
| Bar marks/schedules | 📋 Next | Generate bar mark IDs |

---

### TASK-AI-CHAT: AI Chat Assistant Interface ✅ MVP COMPLETE

**Goal:** ChatGPT-like UI with 40% chat / 60% workspace split

| Sub-task | Status | Notes |
|----------|--------|-------|
| AI Assistant page (10_🤖_ai_assistant.py) | ✅ Done | Split layout working |
| SmartDashboard component | ✅ Done | Score gauges, issues |
| LLM tool definitions | ✅ Done | 7 tools for function calling |
| **Fix SmartDesigner geometry bug** | ✅ Done | Session 51 - Wrapper object |
| **Fix number_input type mismatch** | ✅ Done | Session 51 - All floats |
| **Fix GPT model name (gpt-4o-mini)** | ✅ Done | Session 51 - Corrected |
| **Multi-file CSV import** | ✅ Done | Session 51 - Geom + Forces |
| **Phase 3 rebar visualization** | ✅ Done | Session 51 - `4a89dc9a` |
| Streaming responses | 📋 V1.1 | Typewriter effect |
| Tool execution handlers | 📋 V1.1 | Map tools to library functions |

**Why:** Make structural engineering accessible through natural language.
Users can say "Design a beam for 150 kN·m" and get results + 3D view.

### TASK-3D-008: Smart Insights Dashboard (Phase 3.5) ✅ MERGED

**Goal:** Expose existing AI-like intelligence in the UI
**Status:** Merged into TASK-AI-CHAT — SmartDesigner now displayed in AI workspace

---

### TASK-3D-007: 3D View Interactive Controls ✅ COMPLETE

**Goal:** Make 3D view useful, not just pretty. Differentiate from ETABS.

| Sub-task | Status | Notes |
|----------|--------|-------|
| Story filter dropdown | ✅ Done | `a20e9419` - View one story at a time |
| Color mode selector | ✅ Done | Design Status / By Story / Utilization |
| Camera presets | ✅ Done | Isometric / Front / Top / Side |
| Show/Hide edges toggle | ✅ Done | Reduce visual noise when needed |
| Utilization heat map | ✅ Done | Green → Yellow → Red gradient |

---

### TASK-3D-004: 3D Building Visualization ✅ COMPLETE

| Sub-task | Status | Notes |
|----------|--------|-------|
| Add 3D View tab to multi-format import | ✅ Done | Session 46 |
| Story-based color coding | ✅ Done | 8-color palette |
| Design status coloring (pass/fail) | ✅ Done | Green/Red/Orange |
| Hover tooltips with beam details | ✅ Done | Mu, Vu, bars, status |
| **Solid 3D beam boxes** | ✅ Done | `7414a7e0` - Upgraded from lines! |
| **BuildingStatistics integration** | ✅ Done | `9351bdc8` - Volume metrics |

---

### TASK-VBA-001: VBA ETABS Export Integration ✅ COMPLETE

| Sub-task | Status | Notes |
|----------|--------|-------|
| VBA macro for beam forces export | ✅ Done | 7 modules, 2,302 lines |
| CSV format documentation | ✅ Done | envelope format (Mu_max_kNm) |
| Fix page 06 VBA format detection | ✅ Done | Session 46 - redirect to page 07 |
| Fix page 07 DesignDefaults error | ✅ Done | Session 46 - remove invalid fields |

---

## Backlog (Prioritized)

### High Priority 🔥 THE KILLER FEATURE

| ID | Task | Est | Notes |
|----|------|-----|-------|
| TASK-3D-008 | **Rebar visualization in 3D** | 8h | Show actual bars from design! |
| TASK-3D-009 | Stirrup rendering with zones | 6h | Variable spacing near supports |
| TASK-3D-010 | Cross-section view mode | 4h | Click beam → see 2D section |
| TASK-PERF-001 | LOD optimization for 1000+ beams | 2h | Performance critical |

### Medium Priority

| ID | Task | Est | Notes |
|----|------|-----|-------|
| TASK-DOC-001 | User guide for VBA workflow | 2h | Step-by-step with screenshots |
| TASK-TEST-001 | Integration tests with real VBA CSV | 2h | End-to-end validation |
| TASK-EXPORT-001 | DXF drawing export | 4h | V1.1 feature |

### Low Priority (V1.1+)

| ID | Task | Est | Notes |
|----|------|-----|-------|
| TASK-REPORT-001 | PDF report generation | 4h | Delayed to V1.1 |
| TASK-BBS-001 | Bar bending schedule | 4h | Delayed to V1.1 |
| TASK-MULTI-001 | Multi-span continuous beams | 8h | Delayed to V1.1 |

---

## Recently Completed (Last 7 Days)

| Date | Task | Commit | Notes |
|------|------|--------|-------|
| 2026-01-20 | AI v2 workspace component | `1e9061b4` | Session 52 - State machine |
| 2026-01-20 | AI v2 page | `6ba16b62` | Session 52 - Dynamic workspace |
| 2026-01-20 | Page 07 beam detail 3D | `e1189937` | Session 52 - Rebar viz |
| 2026-01-20 | Fix AI page bugs | `c5fd8bc8` | Session 51 - geometry/type errors |
| 2026-01-20 | Phase 3 rebar viz | `4a89dc9a` | Session 51 - Variable stirrups |
| 2026-01-25 | Fix AI page bugs | `fef3ae12`, `4d0a9c7c` | Session 49 - geometry/attribute errors |
| 2026-01-25 | Add GPT-4o-mini support | `fef3ae12` | Session 49 - configurable model |
| 2026-01-25 | Chat panel improvements | `37e0a21f` | Session 49 - welcome msg, clear btn |
| 2026-01-24 | 3D building view tab | `efe825d3` | Session 46 |

---

## Notes

- **Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history
- **8-week plan:** See [planning/8-week-development-plan.md](planning/8-week-development-plan.md)
- **Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
