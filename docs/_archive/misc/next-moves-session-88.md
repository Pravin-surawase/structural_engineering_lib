# Next Moves — Post Session 88

**Date:** 2026-02-10
**Branch:** `refactor/folder-structure-v2` (PR #424 → main)
**Test suite:** 3194 passed, 5 skipped, 0 failures

---

## Session 88 Accomplishments

| # | Task | Commit | Impact |
|---|------|--------|--------|
| 1 | PR #424 created for folder refactor | — | 7 commits, 204 files changed |
| 2 | Script consolidation Phase 2: 4 groups merged | `51f1b8e` | 163→97 active scripts |
| 3 | materials.py → codes/is456/materials.py | `0cbbfc0` | Naming conflict resolved |
| 4 | Deep script audit: 5 broken imports fixed, shared utils, CLI upgrades | `4df60fb` | All scripts clean |

---

## Immediate Next (Priority Order)

### 1. Merge PR #424 → main
- **What:** 7 commits restructuring structural_lib into core/services subpackages
- **Risk:** Low — 3194 tests pass, 0 broken imports, full backward compat
- **Action:** Review CI, merge, delete `refactor/folder-structure-v2` branch

### 2. Phase 3 — Remaining root modules classification
11 non-stub modules remain at root level. Here's the plan for each:

| Module | Lines | Category | Proposed Location | Rationale |
|--------|-------|----------|-------------------|-----------|
| `bbs.py` | ~300 | Output/Report | `services/` | Bar bending schedule generation |
| `calculation_report.py` | ~600 | Output/Report | `services/` | HTML/Markdown report generation |
| `report.py` | ~200 | Output/Report | `services/` | PDF/text report utilities |
| `report_svg.py` | ~150 | Output/Report | `services/` | SVG diagram generation |
| `dxf_export.py` | ~400 | Output/Export | `services/` | DXF drawing export |
| `job_runner.py` | ~250 | Services | `services/` | Batch job orchestration |
| `job_cli.py` | ~100 | CLI | `services/` | CLI for job_runner |
| `excel_integration.py` | ~300 | IO/Bridge | `services/` | Excel ↔ Python bridge |
| `excel_bridge.py` | ~200 | IO/Bridge | `services/` | Excel VBA integration |
| `__init__.py` | — | Package | Keep at root | Package root |
| `__main__.py` | — | Entry | Keep at root | CLI entrypoint |

**Recommendation:** Move all 9 movable modules to `services/` in one Phase 3 batch. This completes the flat→structured migration.

### 3. Post-merge: Backward-compat stub cleanup plan
After PR #424 merges and has been stable for 1-2 releases:
- Add deprecation warnings to all 36+ stubs (DeprecationWarning with migration path)
- Plan removal for v1.0.0
- Update documentation to reference canonical paths

### 4. V3 Phase 5: Insights + Code Checks (from TASKS.md)
Per the V3 roadmap, the next feature work is:
- Wire dashboard insights into React Dashboard component
- Add live code check badges to DesignView
- Add rebar suggestion "Apply" buttons
- Create export panel (BBS/DXF/CSV)
- Add SSE batch progress UI
- Add REST fallback when WebSocket unavailable

### 5. Script consolidation Phase 4 (post-V3)
When V3 React migration is complete, archive ~10 Streamlit-specific scripts:
- `check_streamlit_issues.py`, `check_fragment_violations.py`
- `check_performance_issues.py`, `check_ui_duplication.py`
- `comprehensive_validator.py`, `profile_streamlit_page.py`
- `validate_session_state.py`, `validate_streamlit_page.py`
- `generate_streamlit_page.py`, `launch_streamlit.sh`

---

## Architecture State After Session 88

```
structural_lib/
├── __init__.py, __main__.py          # Package essentials
├── core/                             # 15 files: types, models, validation, errors
│   ├── base.py, geometry.py, materials.py, registry.py
│   ├── constants.py, types.py, data_types.py, models.py
│   ├── errors.py, error_messages.py, validation.py
│   ├── inputs.py, result_base.py, utilities.py
│   └── __init__.py
├── services/                         # 18 files: API, adapters, pipeline, optimization
│   ├── api.py, beam_pipeline.py, adapters.py
│   ├── batch.py, imports.py, etabs_import.py
│   ├── rebar.py, rebar_optimizer.py, optimization.py
│   ├── multi_objective_optimizer.py, audit.py
│   ├── intelligence.py, costing.py, serialization.py
│   ├── dashboard.py, testing_strategies.py, api_results.py
│   └── __init__.py
├── codes/is456/                      # 14 files: pure IS 456 math
│   ├── flexure.py, shear.py, detailing.py, materials.py (NEW)
│   ├── torsion.py, ductile.py, serviceability.py
│   ├── slenderness.py, tables.py, compliance.py
│   ├── load_analysis.py, traceability.py, clause_cli.py
│   └── __init__.py
├── insights/                         # Smart design, suggestions, sensitivity
├── geometry_3d.py                    # 3D visualization geometry
├── 36 backward-compat stubs          # Re-exports for existing code
└── 9 unmoved modules                 # Phase 3 candidates (bbs, reports, dxf, excel)
```

**Scripts:** 97 active + 70 archived + `_lib/utils.py` shared module

---

## Key Metrics

| Metric | Before Session 88 | After |
|--------|-------------------|-------|
| Active scripts | 113 | 97 |
| Archived scripts | 53 | 70 |
| Root modules (non-stub) | 12 | 11 (materials.py moved) |
| Broken script imports | 5 | 0 |
| Test count | 3194 | 3194 |
| Test failures | 0 | 0 |
