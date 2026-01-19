# Task Board

> **Single source of truth for active work.** Keep it short and current.

**Updated:** 2026-01-19 (Session 46+)

---

## Rules
- **WIP = 2** (max 2 active tasks at once)
- **Done = tests pass + docs updated + scanner passes**
- **Archive rule:** Move completed items to [tasks-history.md](_archive/tasks-history.md) after 20+ items

---

## Current Focus

- **Version:** v0.17.6 (in progress)
- **Focus:** 3D Visualization Excellence & Library Improvements
- **8-Week Plan:** Phase 2 at 90%, Phase 3 starting
- **Next Milestone:** March 2026 (v0.18.0)

---

## Active Tasks

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

### TASK-LIB-001: Library Utility Functions 🚧 IN PROGRESS

| Sub-task | Status | Notes |
|----------|--------|-------|
| BuildingStatistics model | ✅ Done | `907684b5` - 4 tests added |
| Concrete volume calculation | ✅ Done | Included in BuildingStatistics |
| Story breakdown metrics | ✅ Done | beams_per_story dict |

---

## Backlog (Prioritized)

### High Priority

| ID | Task | Est | Notes |
|----|------|-----|-------|
| TASK-PERF-001 | LOD optimization for 1000+ beams | 2h | Use lod_manager.py |
| TASK-3D-006 | Camera presets (front/top/iso) | 1h | Quick navigation |
| TASK-DATA-003 | Column/slab support | 4h | Extend adapter system |

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
