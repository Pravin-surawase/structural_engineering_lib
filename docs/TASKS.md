# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-01-20 (Session 52)

---

## Rules
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items

---

## Current Focus

- **Version:** v0.18.0 → v0.18.2 (AI v2 + Rebar Visualization)
- **Focus:** AI Assistant v2 with dynamic workspace
- **8-Week Plan:** Phase AI COMPLETE ✅, AI v2 IN PROGRESS
- **Next Milestone:** v0.18.2 - AI v2 with Dynamic Workspace
- **Key Insight:** Single dynamic panel > 5 tabs
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution

---

## Active Tasks

### TASK-AI-V2: AI Assistant v2 with Dynamic Workspace 🚧 IN PROGRESS

**Goal:** Redesign AI chat with single dynamic workspace panel (35% chat / 65% workspace)

| Sub-task | Status | Notes |
|----------|--------|-------|
| AI workspace component | ✅ Done | Session 52 - `ai_workspace.py` |
| State machine (6 states) | ✅ Done | Session 52 - WELCOME → DASHBOARD |
| Auto-column-mapping | ✅ Done | Session 52 - Detect ETABS columns |
| Sample data (10 beams) | ✅ Done | Session 52 - Built-in demo |
| AI v2 page | ✅ Done | Session 52 - `11_⚡_ai_assistant_v2.py` |
| Chat commands | ✅ Done | Session 52 - load/design/view/dashboard |
| Page 07 beam detail 3D | ✅ Done | Session 52 - `e1189937` |
| Test and polish | 📋 Next | Verify all states work |

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
| 2026-01-25 | Add GPT-5-mini support | `fef3ae12` | Session 49 - configurable model |
| 2026-01-25 | Chat panel improvements | `37e0a21f` | Session 49 - welcome msg, clear btn |
| 2026-01-24 | 3D building view tab | `efe825d3` | Session 46 |

---

## Notes

- **Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history
- **8-week plan:** See [planning/8-week-development-plan.md](planning/8-week-development-plan.md)
- **Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
