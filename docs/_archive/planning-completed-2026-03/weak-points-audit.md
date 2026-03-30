# Weak Points Audit — Deep Analysis

**Type:** Plan
**Audience:** All Agents
**Status:** In Progress
**Importance:** High
**Created:** 2026-03-25
**Last Updated:** 2026-03-25
**Related Tasks:** TASK-506, TASK-507, TASK-508, TASK-509, TASK-510

---

## Summary

Deep audit of structural, architectural, and quality weak points across the V3 stack.
Six issues identified across React, Streamlit, and Python layers — ranging from critical
(zero test coverage) to low (type annotation gaps). Each issue has exact file references,
root causes, and a linked task for resolution.

---

## WP-1: React Has Zero Tests (CRITICAL)

**Task:** TASK-506 | **Impact:** No regression detection, WebSocket resilience unknown

### What was found

- **0 test files** in `react_app/src/` — no `.test.ts`, `.test.tsx`, `.spec.ts` files
- **No test framework** — `package.json` has no `test` script, no `vitest`, no `@testing-library/*`
- **No `vitest.config.ts`** or `jest.config.js` exists

### Critical untested paths

| Hook / Component | File | Risk |
|-----------------|------|------|
| `useLiveDesign` | `react_app/src/hooks/useLiveDesign.ts` (208 lines) | WebSocket connection failure, reconnection, debounce — entirely untested |
| `useAutoDesign` | `react_app/src/hooks/useAutoDesign.ts` | AbortController, debounce timing, REST fallback path — untested |
| `DesignView` | `react_app/src/components/design/DesignView.tsx` (435 lines) | Core user flow: live design → code checks → rebar suggestions — untested |
| `useCSVFileImport` / `useDualCSVImport` / `useBatchDesign` | `react_app/src/hooks/useCSVImport.ts` | Batch design pipeline — untested |
| `useBeamGeometry` | `react_app/src/hooks/useBeamGeometry.ts` | 3D geometry computation — untested |
| `useExportBBS` / `useExportDXF` / `useExportReport` | `react_app/src/hooks/useExport.ts` | File download triggers — untested |
| `Viewport3D` | `react_app/src/components/viewport/Viewport3D.tsx` | Three.js + R3F rendering — untested |

### Root cause

The React app was bootstrapped as a migration-in-progress from Streamlit. Tests were always
"next sprint" — now 1071 TypeScript files exist with zero coverage.

### Fix (see TASK-506)

1. Add `vitest` + `@testing-library/react` + `jsdom` to `react_app/package.json`
2. Create `react_app/vitest.config.ts`
3. Write smoke tests for 5 critical components/hooks: `DesignView`, `useLiveDesign`,
   `useAutoDesign`, `useCSVFileImport`, `useBeamGeometry`
4. Add `"test": "vitest"` and `"test:coverage": "vitest --coverage"` to `package.json` scripts

---

## WP-2: DesignView Has No HTTP Fallback (HIGH)

**Task:** TASK-503 (existing) | **Impact:** WebSocket down → red error text, no recovery

### What was found

- `DesignView.tsx` lines 34-46: uses `useLiveDesign({ enabled: true })` — WebSocket always on
- Lines 179-184: error state renders `<p className="text-xs text-red-400/60">{state.error}</p>` — display only, no recovery
- `useLiveDesign.ts` line 31: `connectionStatus` types include `'error'` and `'disconnected'` but DesignView does not branch on these
- `useAutoDesign.ts` line 9: imports `designBeam` from `../api/client` (HTTP) — REST path exists but is **not wired into DesignView**
- `useAutoDesign.ts` line 3 (docstring): "Provides debounced auto-design on input changes **with WebSocket fallback**" — but DesignView uses `useLiveDesign`, not `useAutoDesign`

### Root cause

Two hooks exist for the same purpose:
- `useLiveDesign` — WebSocket-first, no fallback
- `useAutoDesign` — REST-first with debounce (the fallback)

`DesignView` wires only `useLiveDesign`. The fallback hook exists but is not connected.

### Fix (see TASK-503)

In `DesignView.tsx`: when `connectionStatus === 'error' || connectionStatus === 'disconnected'`,
swap to `useAutoDesign` for REST-based design. Add an indicator showing degraded mode.

---

## WP-3: Architecture Violations in Streamlit (293 flagged) (MODERATE)

**Task:** TASK-507 | **Impact:** CI check fails, UI imports Services directly

### What was found

The `validate_imports.py` script passes (0 broken syntax imports). The 293 violations
are **architectural boundary violations** flagged by `check_all.py`:

**Direct service imports from UI layer (the real violations):**

| File | Line | Violation |
|------|------|-----------|
| `streamlit_app/pages/02_💰_cost_optimizer.py` | 42 | `from structural_lib.services.multi_objective_optimizer import ...` |
| `streamlit_app/utils/api_wrapper.py` | 47 | `from structural_lib.services.rebar_optimizer import optimize_bar_arrangement` |

**Correct stubs exist** — `Python/structural_lib/rebar_optimizer.py` and
`Python/structural_lib/multi_objective_optimizer.py` are backward-compat stubs that
re-export from services. These files just need to use the stub path instead.

**Test files with broken paths (legacy):**

| File | Line | Issue |
|------|------|-------|
| `tests/test_validation_system.py` | 16-17 | `from comprehensive_validator`, `from autonomous_fixer` — scripts no longer exist |
| `tests/test_visualizations_3d.py` | 21 | `from components.visualizations_3d` — Streamlit-era component path |

### Root cause

Streamlit layer grew organically. When services were refactored into `services/`, some pages
were not updated to use stubs. The ~293 count is inflated by legacy test detection logic
scanning non-test `.py` files in streamlit_app/.

### Fix (see TASK-507)

1. `02_💰_cost_optimizer.py:42` → change to `from structural_lib.multi_objective_optimizer import ...`
2. `utils/api_wrapper.py:47` → change to `from structural_lib.rebar_optimizer import optimize_bar_arrangement`
3. Either fix or skip `tests/test_validation_system.py` and `tests/test_visualizations_3d.py`
4. Verify `check_all.py` import check drops from 293 to near-zero

---

## WP-4: `ai_workspace.py` is 5,103 Lines (HIGH)

**Task:** TASK-508 | **Impact:** Untestable monolith, circular deps, high maintenance burden

### What was found

**File:** `streamlit_app/components/ai_workspace.py`
**Size:** 5,103 lines, 1 enum class, 37 module-level functions

**Function groups that should be separate modules:**

| Proposed Module | Functions | Lines (approx) |
|----------------|-----------|----------------|
| `workspace_state.py` | `WorkspaceState`, `init_workspace_state`, `set_workspace_state`, `get_workspace_state` | ~80 |
| `import_handler.py` | `auto_map_columns`, `standardize_dataframe`, `load_sample_data`, `detect_format_from_content`, `process_with_adapters`, `beams_to_dataframe`, `process_uploaded_file`, `process_multi_files` | ~800 |
| `design_handler.py` | `design_beam_row` (line 678), `design_all_beams_ws` (line 751) | ~300 |
| `rebar_handler.py` | `calculate_rebar_layout` (line 606), `calculate_rebar_checks`, `suggest_optimal_rebar` (line 2059), `optimize_beam_line` (line 2222), `render_rebar_editor` | ~600 |
| `export_handler.py` | `_generate_and_download_report`, `_generate_and_download_pdf_report`, `_generate_and_download_dxf`, `calculate_material_takeoff` | ~400 |
| `ui_renderers.py` | All `render_*` and `create_*` functions (~18 functions) | ~2900 |

**Import issues:**
- Lines 56-75: Direct try-import of `structural_lib.services.adapters` (architecture violation in Streamlit layer)
- Imported by: `streamlit_app/ai/handlers.py`, `streamlit_app/utils/batch_design.py`, `streamlit_app/utils/rebar_optimization.py`

### Root cause

Single-file Streamlit app grew session-by-session without refactoring gates. No module
size limits were enforced (governance only covers folder structure, not file size).

### Fix (see TASK-508)

Split into 6 modules using `safe_file_move.py` + `migrate_python_module.py`. Keep
`ai_workspace.py` as a thin re-export shim during transition. Requires a dedicated PR
(Streamlit changes are production-adjacent for the legacy layer).

---

## WP-5: React Bundle — No Lazy Loading (LOW)

**Task:** TASK-502 (existing) | **Impact:** Larger initial load, all routes loaded upfront

### What was found

**`react_app/vite.config.ts` lines 11-23:** Three.js IS manually chunked:
```typescript
manualChunks: {
  three: ['three'],
  'react-three': ['@react-three/fiber', '@react-three/drei'],
  react: ['react', 'react-dom'],
  dockview: ['dockview'],
}
```

**However, zero `React.lazy()` or dynamic `import()` calls** exist in `react_app/src/`.
Manual chunks split the vendor libs but all app routes/components load at startup.

**Heavy deps with no lazy loading:**
- `@ag-grid-community/*@^32.3.9` — AG Grid (no manual chunk, always loaded)
- `framer-motion@^12.29.2` — Animation (always loaded)
- `dockview@^4.13.1` — Layout (chunked but always requested)
- `Viewport3D` — Three.js 3D view (chunked vendor, but component is statically imported)

### Fix (see TASK-502)

Wrap route-level components with `React.lazy()`:
- `Viewport3D` — lazy-load entire 3D viewport
- `BuildingEditorPage` — lazy-load AG Grid
- `DashboardPage` — lazy-load insights
Add `@ag-grid-community` to `manualChunks` in `vite.config.ts`.

---

## WP-6: Type Annotation Gaps in Streamlit (LOW)

**Task:** TASK-509 | **Impact:** mypy on core passes; Streamlit pages untyped

### What was found

`check_all.py` type annotation check reports:
- **49 missing return types** — almost entirely in `streamlit_app/pages/`
- **15 missing param types** — in Streamlit pages and hidden pages
- **4 missing `__all__`** — in Python core modules

**mypy on `Python/structural_lib/services/api.py`:** ✅ `Success: no issues found`

The core library is typed correctly. All 64 issues are in the Streamlit legacy layer.

**Worst offenders:**
- `streamlit_app/pages/06_📥_multi_format_import.py` lines 162, 585
- `streamlit_app/pages/_hidden/_06_📤_etabs_import.py` lines 123, 262
- Multiple `render_*()` and `main()` functions with no return type annotation

### Fix (see TASK-509)

Add `-> None` to all `render_*()`, `main()`, `init_*()` functions in Streamlit pages.
Add param types to `progress_bar: st.delta_generator.DeltaGenerator` pattern functions.
Add `__all__` to 4 Python core modules flagged.

---

## Priority Matrix

| ID | Weak Point | Severity | Effort | Do When |
|----|-----------|----------|--------|---------|
| WP-1 | Zero React tests | 🔴 Critical | 2d | Before TASK-502/503 refactors |
| WP-2 | DesignView no HTTP fallback | 🟠 High | 0.5d | With TASK-503 |
| WP-3 | 293 arch violations (Streamlit) | 🟡 Moderate | 0.5d | Standalone, anytime |
| WP-4 | ai_workspace.py monolith | 🟠 High | 2d | Dedicated PR, after test coverage |
| WP-5 | No lazy loading | 🟡 Moderate | 1d | With TASK-502 |
| WP-6 | Type annotations | 🟢 Low | 1d | Batch, low priority |

---

## Next Steps

1. Start with **TASK-506** (React tests) — must exist before refactoring TASK-502/503
2. **TASK-507** (fix 293 arch violations) — fast win, 2 line changes + test file fixes
3. **TASK-503** (REST fallback) — wire `useAutoDesign` into DesignView on WS failure
4. **TASK-508** (split ai_workspace.py) — needs dedicated PR after tests are in place

---

*Run `./run.sh check --quick` to see current pass/fail state.*
