# GitHub Fix Plan — Post-Cleanup Issues

**Type:** Reference
**Audience:** All Agents
**Status:** Approved
**Importance:** Critical
**Created:** 2026-03-27
**Last Updated:** 2026-03-27

## Summary

After the 6-phase repo cleanup (Streamlit removal, VBA/Excel gitignore, research archive, config consolidation), the Mac Mini fresh clone could not import CSVs, load sample building, or build React. This document tracks what was fixed and how.

## What Was Done (TASK-102 PR)

### Phase 1: Merged TASK-101 (Mac Mini bug fixes)
TASK-101 had 4 commits with legitimate fixes that were never merged to main:

| Fix | File(s) | What |
|-----|---------|------|
| Sample building 404 | `fastapi_app/routers/imports.py` + `Etabs_CSV/` (5 new files) | New tracked sample data dir with fallback paths |
| CSV import crash | `fastapi_app/routers/imports.py` | Adapter auto-detection with cascading fallback |
| xlwings crash | `Python/structural_lib/services/excel_bridge.py` | try/except with no-op stubs |
| Docker build fail | `Dockerfile.fastapi` | Removed deleted `setup.cfg` from COPY, added `Etabs_CSV` |
| Vite IPv6 | `react_app/vite.config.ts` | `host: '0.0.0.0'` for Colima compatibility |
| CSV API contract | `useCSVImport.ts` + `ImportView.tsx` + `imports.py` | Frontend-backend contract aligned |
| Doc links | 20+ docs | ~30 broken links to deleted files fixed |
| Bootstrap | `docs/getting-started/agent-bootstrap.md` | Major update for post-cleanup paths |

### Phase 2: Streamlit Remnant Cleanup (21 files)
Removed all dead Streamlit references from scripts that survived the initial cleanup:

| File | What was removed |
|------|-----------------|
| `run.sh` | Streamlit check category from help, options, completions |
| `scripts/check_all.py` | Streamlit Category block + `streamlit_app/` path mapping |
| `scripts/agent_start.sh` | Streamlit dep check + agent-6 Streamlit guidance |
| `scripts/safe_push.sh` | `check-streamlit` hook check |
| `scripts/watch_tests.sh` | `check_streamlit.py` invocation |
| `scripts/should_use_pr.sh` | `STREAMLIT_MINOR_THRESHOLD`, `HAS_STREAMLIT_CODE`, `STREAMLIT_ONLY`, entire Streamlit PR logic block |
| `scripts/check_architecture_boundaries.py` | `streamlit` from forbidden imports, `streamlit_app` from UI paths, fix hints |
| `scripts/check_circular_imports.py` | `streamlit_app` from scan paths and descriptions |
| `scripts/check_instruction_drift.py` | `streamlit` instruction pair |
| `scripts/check_type_annotations.py` | `streamlit_app/` scan directories |
| `scripts/validate_imports.py` | `streamlit_app` scope + `streamlit` known package |
| `scripts/check_governance.py` | `streamlit_app/docs` from allowed dated_files locations |
| `scripts/check_fastapi_issues.py` | Docstring reference to `check_streamlit.py` |
| `scripts/check_api.py` | Default `pages_dir` changed from `streamlit_app/pages` to `react_app/src` |
| `scripts/audit_readiness_report.py` | Streamlit journey tests, scanner, and fragment validator blocks |
| `scripts/create_test_scaffold.py` | Entire `streamlit_page` test type + `generate_streamlit_page_test()` function (207 lines removed) |
| `scripts/migrate_python_module.py` | `streamlit_app` from search dirs |
| `scripts/safe_file_delete.py` | `streamlit_app` from search dirs |
| `scripts/safe_file_move.py` | `streamlit_app` from search dirs (2 locations) |
| `scripts/test_import_3d_pipeline.py` | `streamlit_dir` path setup + `streamlit_app` sys.path |
| `Python/structural_lib/services/dxf_export.py` | Streamlit docstring example replaced with file-based example |

### Phase 3: Deleted Orphaned Test Files (4 files, 1627 lines)
These test files imported from the deleted `streamlit_app` module and could never pass:

| File | Lines | streamlit_app refs |
|------|-------|--------------------|
| `tests/test_lod_manager.py` | 564 | 19 |
| `tests/test_lod_performance.py` | 293 | 2 |
| `tests/test_report_export_component.py` | 225 | 4 |
| `tests/test_visualizations_3d.py` | 545 | 3 |

## Verification Results

After all changes:
- **Python tests:** 3181 passed, 3 skipped ✅
- **React build:** ✓ built in 4.89s ✅
- **FastAPI:** 43 routes loaded ✅
- **Streamlit refs remaining:** 0 (in active code) ✅
  - Only `scripts/fix_broken_links.py` contains Streamlit entries — intentional (it's a tool that detects broken links to deleted files)

## Backup

Git tag `backup-working-local-2026-03-27` at commit `bc06893` preserves the pre-fix state.

---

## Mac Mini Agent Instructions

After this PR is merged to `main`, the Mac Mini agent needs to do the following:

```bash
# 1. Pull the updated code
cd ~/VS_code_project/structural_engineering_lib
git checkout main
git pull origin main

# 2. Reinstall structural_lib (picks up any dependency changes)
.venv/bin/pip install -e "Python[dev,dxf]"

# 3. Verify everything works
cd Python && ../.venv/bin/pytest tests/ -x -p no:benchmark --ignore=tests/performance --tb=line
cd ../react_app && npm run build
.venv/bin/python -c "from fastapi_app.main import app; print(f'{len(app.routes)} routes')"

# 4. Test the import + sample building
# Start FastAPI:
.venv/bin/uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000
# In another terminal:
curl http://localhost:8000/api/v1/import/sample-building | head -c 200

# 5. Clean up ghost packages (optional but recommended)
.venv/bin/pip uninstall -y streamlit plotly xlwings watchdog altair 2>/dev/null
```

### What Mac Mini Will Get From This PR
- `Etabs_CSV/` directory with sample building data (no more 404)
- Fixed CSV import that doesn't crash on auto-detection
- `excel_bridge.py` that works without xlwings installed
- All Streamlit dead code removed from scripts
- Updated `agent-bootstrap.md` with correct post-cleanup instructions
- Fixed broken doc links

### What Mac Mini Does NOT Need To Do
- No manual file edits — everything is in the PR
- No branch management — just `git pull` on main after PR merge
- No script fixes — all already done
