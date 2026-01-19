# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-01-19 (Session 47)

---

## Rules
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items

---

## Current Focus

- **Version:** v0.17.6 (in progress)
- **Focus:** 3D Visualization Excellence + Smart Insights
- **8-Week Plan:** Phase 2.5 ✅ COMPLETE, Phase 3 (rebar) + Phase 3.5 (insights) planned
- **Next Milestone:** March 2026 (v0.18.0)
- **Key Insight:** We have SmartDesigner built — just need to expose it!
- **Vision:** [democratization-vision.md](planning/democratization-vision.md) — AI chat, automation, library evolution

---

## Active Tasks

### TASK-3D-008: Smart Insights Dashboard (Phase 3.5) 🚧 NEW

**Goal:** Expose existing AI-like intelligence in the UI

| Sub-task | Status | Notes |
|----------|--------|-------|
| SmartDesigner panel in beam design | 📋 TODO | 2h - Use existing `SmartDesigner.analyze()` |
| Cost optimization summary | 📋 TODO | 1h - Show current vs optimal cost |
| Design suggestions display | 📋 TODO | 1h - High/medium/low impact |
| Quick wins callout box | 📋 TODO | 1h - Actionable improvements |
| "Why is this unsafe?" explainer | 📋 TODO | 2h - Educational feedback |

**Why:** We built `SmartDesigner` in `structural_lib/insights/` but never exposed it in the UI!
This makes the tool feel intelligent without building full AI chat.

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
| 2026-01-24 | 3D building view tab | `efe825d3` | Session 46 |
| 2026-01-24 | Fix VBA import errors | `897da5dd` | Session 46 |
| 2026-01-24 | Docs cleanup | `67faaca6`, `2317a2b9` | Session 46 |
| 2026-01-18 | LOD threshold validation | PR #385 | Session 43 |
| 2026-01-17 | VBA ETABS export macro | PR #379 | Session 36 |
| 2026-01-16 | Multi-format adapter system | PR #381 | Session 42 |

---

## Notes

- **Session logs:** See [SESSION_LOG.md](SESSION_LOG.md) for detailed history
- **8-week plan:** See [planning/8-week-development-plan.md](planning/8-week-development-plan.md)
- **Task history:** See [_archive/tasks-history.md](_archive/tasks-history.md)
