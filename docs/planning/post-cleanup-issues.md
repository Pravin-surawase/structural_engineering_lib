# Post-Cleanup Issues & Fixes

**Type:** Reference
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-03-27
**Last Updated:** 2026-03-27

After removing Streamlit, VBA/Excel from git tracking, and archiving research docs,
several issues remain. This document catalogs every known issue, its root cause,
severity, and fix.

---

## Summary

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | React build fails — `useExport.ts` TypeScript error | **Critical** | Open |
| 2 | Sample building endpoint returns 404 on fresh clone | **Critical** | Open |
| 3 | Ghost packages still installed (streamlit, plotly, xlwings) | **High** | Open |
| 4 | `excel_bridge.py` hard-imports xlwings (crashes if uninstalled) | **High** | Open |
| 5 | 46 broken Python imports in test/script files | **High** | Open |
| 6 | 66 broken documentation links | **Medium** | Open |
| 7 | `run.sh` / `check_all.py` still reference Streamlit | **Medium** | Open |
| 8 | 15+ scripts still reference `streamlit_app/` | **Medium** | Open |
| 9 | `dxf_export.py` docstring references Streamlit | **Low** | Open |
| 10 | Version mismatch: pyproject.toml 0.19.1 vs pip 0.19.0 | **Low** | Open |
| 11 | Deprecation test fails (test_deprecation_warnings_silenced_by_default) | **Low** | Open |

---

## Issue 1: React Build Fails

### Error

```
src/hooks/useExport.ts:176:9 - error TS2345:
  Argument of type 'BuildingExportParams' is not assignable to
  parameter of type 'ExportBeamParams | ExportReportParams'.
  Type 'BuildingExportParams' is missing: width, depth, fck, fy
```

### Root Cause

`fetchExport()` function signature only accepts `ExportBeamParams | ExportReportParams`,
but `useExportBuildingSummary()` passes a `BuildingExportParams` (which has `beams[]`
instead of individual beam fields). This is a pre-existing type mismatch that was
masked by `tsc -b` (project mode) vs `tsc --noEmit` (standalone mode).

### Fix

Widen `fetchExport` parameter type to include `BuildingExportParams`:

```typescript
// react_app/src/hooks/useExport.ts line 67
async function fetchExport(
  endpoint: string,
  body: ExportBeamParams | ExportReportParams | BuildingExportParams,  // ADD
  filename: string
): Promise<string> {
```

### Severity: Critical — `npm run build` fails, React app cannot be deployed.

---

## Issue 2: Sample Building 404 on Fresh Clone

### Error

`GET /api/v1/import/sample` returns HTTP 404 on Mac Mini or any fresh clone.

### Root Cause

The sample data endpoint in `fastapi_app/routers/imports.py` (line 652) hardcodes
a path to VBA sample CSVs:

```python
sample_dir = base_path / "VBA" / "ETABS_Export_v2" / "Etabs_output" / "2026-01-17_222801"
```

VBA/ is gitignored, so the files don't exist after a fresh `git clone`.
The data (4 CSV files, ~30KB total) only exists locally on this MacBook.

### Fix Options

**Option A (Recommended):** Move sample data into the tracked repo:

```bash
mkdir -p Python/structural_lib/data/sample_building
cp VBA/ETABS_Export_v2/Etabs_output/2026-01-17_222801/*.csv \
   Python/structural_lib/data/sample_building/
```

Then update `imports.py` line 652:

```python
sample_dir = base_path / "Python" / "structural_lib" / "data" / "sample_building"
```

**Option B:** Bundle as package data in pyproject.toml and access via `importlib.resources`.

### Severity: Critical — "Load sample building" button in React UI is broken for any new clone.

---

## Issue 3: Ghost Python Packages Still Installed

### Problem

The old `.venv` still has packages that were removed from `requirements.txt`:

| Package | Version | Status |
|---------|---------|--------|
| streamlit | 1.53.1 | Removed from requirements, still installed |
| plotly | 6.5.2 | Removed from requirements, still installed |
| xlwings | 0.33.20 | Removed from requirements, still installed |

Streamlit alone brings ~50 transitive dependencies (altair, tornado, pyarrow, etc.).

### Root Cause

`pip install -r requirements.txt` only installs — it never uninstalls. The old venv
carries forward all packages from before the cleanup.

### Fix

On this MacBook (old venv):

```bash
.venv/bin/pip uninstall streamlit plotly xlwings -y
```

On Mac Mini: Not an issue — fresh venv will be clean.

### Why This Matters

- Wastes ~200MB disk space
- `excel_bridge.py` silently works because xlwings is still present (see Issue 4)
- Tests may pass locally but fail in CI with a clean install

### Severity: High — hides real import failures.

---

## Issue 4: excel_bridge.py Hard-Imports xlwings

### Error (when xlwings is uninstalled)

```
ImportError: No module named 'xlwings'
```

### Root Cause

`Python/structural_lib/services/excel_bridge.py` line 22:

```python
import xlwings as xw
```

This is a top-level unconditional import. Since xlwings was removed from
`requirements.txt`, this file will crash on any fresh install.

### Fix

Make it a lazy/conditional import:

```python
try:
    import xlwings as xw
except ImportError:
    xw = None  # Excel bridge unavailable without xlwings

# Guard all @xw.func decorators:
if xw is not None:
    @xw.func
    def IS456_MuLim(...): ...
```

Or move `excel_bridge.py` out of the main package since VBA/Excel is gitignored.

### Severity: High — importing `structural_lib.services` may fail on clean install.

---

## Issue 5: 46 Broken Python Imports (Test/Script Files)

### Affected Files

| File | Broken Imports | Root Cause |
|------|---------------|------------|
| `tests/test_lod_manager.py` | 15 × `from streamlit_app.utils.lod_manager` | Streamlit removed |
| `tests/test_lod_performance.py` | 19 × `from utils.lod_manager`, `from components.visualizations_3d` | Streamlit removed |
| `tests/test_report_export_component.py` | 6 × `from components.report_export` | Streamlit removed |
| `tests/test_visualizations_3d.py` | 4 × `from components.visualizations_3d` | Streamlit removed |
| `scripts/test_import_3d_pipeline.py` | 2 × `from utils.api_wrapper`, `from components.visualizations_3d` | Streamlit removed |

### Fix

Delete these orphaned test files (they test deleted Streamlit components):

```bash
rm tests/test_lod_manager.py
rm tests/test_lod_performance.py
rm tests/test_report_export_component.py
rm tests/test_visualizations_3d.py
rm scripts/test_import_3d_pipeline.py
```

Or use the safe delete script:

```bash
.venv/bin/python scripts/safe_file_delete.py tests/test_lod_manager.py
# repeat for each file
```

### Severity: High — `validate_imports.py` check fails.

---

## Issue 6: 66 Broken Documentation Links

### Breakdown by File

| File | Broken Links | Cause |
|------|-------------|-------|
| `docs/_internal/copilot-tasks/README.md` | 8 | Links to deleted Streamlit/VBA docs |
| `docs/contributing/index.md` | 7 | Links to deleted guides |
| `docs/SESSION_LOG.md` | 6 | Historical links to deleted files |
| `docs/guides/react-ui-user-flow.md` | 4 | Links to deleted UI docs |
| `docs/agents/guides/agent-6-*.md` | 7 | Links to deleted Streamlit agent guides |
| `docs/README.md` | 4 | Links to deleted reference/contributing docs |
| `docs/reference/*.md` | 8 | Links to VBA/Streamlit reference pages |
| `docs/planning/*.md` | 5 | Links to deleted planning docs |
| Other | 17 | Various |

### Fix

```bash
.venv/bin/python scripts/check_links.py --fix   # Auto-fix where possible
```

Then manually review remaining broken links. Most should be removed (link to deleted
content) rather than redirected.

### Severity: Medium — doesn't break runtime, but `check --quick` fails.

---

## Issue 7: run.sh / check_all.py Still Reference Streamlit

### In `run.sh`

- Line 80: Help text lists `streamlit` as a check category
- Line 94: Describes "Streamlit issues"
- Line 580: `categories` array includes `'streamlit'`

### In `scripts/check_all.py`

- Line 162: `name="streamlit"` check category
- Line 166: `Check("Streamlit scanner", ...)` runs deleted `check_streamlit.py`
- Line 188: Maps `streamlit_app/` directory to streamlit checks

### Fix

Remove the `streamlit` category from both files. In `check_all.py`, delete the
streamlit check group. In `run.sh`, remove it from the categories array and help text.

### Severity: Medium — `./run.sh check` will error trying to run deleted `check_streamlit.py`.

---

## Issue 8: 15+ Scripts Reference streamlit_app/

### Affected Scripts (non-archive)

| Script | References |
|--------|-----------|
| `scripts/check_architecture_boundaries.py` | UI layer defined as `streamlit_app` |
| `scripts/check_circular_imports.py` | Scans `streamlit_app/pages`, `streamlit_app/utils` |
| `scripts/create_test_scaffold.py` | Generates tests for `streamlit_app` modules |
| `scripts/test_import_3d_pipeline.py` | Imports from `streamlit_app` |
| `scripts/check_all.py` | Streamlit check category |
| `scripts/agent_start.sh` | References streamlit |
| `scripts/safe_push.sh` | References streamlit |
| `scripts/check_api.py` | References streamlit |
| `scripts/should_use_pr.sh` | References streamlit |
| `scripts/check_governance.py` | References streamlit |
| `scripts/check_instruction_drift.py` | References streamlit |
| `scripts/audit_readiness_report.py` | References streamlit |
| `scripts/validate_imports.py` | References streamlit |
| `scripts/check_type_annotations.py` | References streamlit |

Additionally, `scripts/_archive/` has 15+ archived Streamlit scripts — these are
harmless but add dead weight.

### Fix

Update each active script to remove `streamlit_app` references. Most are just
removing entries from directory lists or check arrays. The archived scripts can stay.

### Severity: Medium — scripts may scan non-existent directory (usually just warnings).

---

## Issue 9: dxf_export.py Docstring References Streamlit

### Location

`Python/structural_lib/services/dxf_export.py` line 1746:

```python
>>> import streamlit as st
```

### Fix

Remove or replace the Streamlit example in the docstring.

### Severity: Low — cosmetic only, no runtime impact.

---

## Issue 10: Version Mismatch

### Problem

- `Python/pyproject.toml`: version = "0.19.1"
- Installed package (pip): Version: 0.19.0
- `structural_lib.__version__` reports: 0.19.0

### Root Cause

The editable install was done before the version bump. Running
`pip install -e ".[dev]"` again will pick up the new version.

### Fix

```bash
cd Python && ../.venv/bin/pip install -e ".[dev]" && cd ..
```

### Severity: Low — only affects version reporting.

---

## Issue 11: Deprecation Test Failure

### Error

```
FAILED tests/integration/test_deprecation.py::TestDeprecationWarningsBehavior::test_deprecation_warnings_silenced_by_default
assert len(w) == 1  # assert 0 == 1
```

### Root Cause

The test expects a deprecation warning to be raised, but the warning filter
configuration has changed. The test uses `-W ignore` which now suppresses the
warning it's trying to catch.

### Fix

Investigate the test's warning filter setup. Likely needs `simplefilter("always")`
before the assertion.

### Severity: Low — 1 test out of 3181.

---

## Issues on Mac Mini (Fresh Clone)

When cloning to Mac Mini, you will hit these **additional** problems:

### A. No sample data files

VBA/ is gitignored → sample building button returns 404.
Fix: Issue 2 above (move sample CSVs into tracked location).

### B. Clean venv — excel_bridge crashes

No xlwings installed → `import structural_lib.services.excel_bridge` crashes.
Fix: Issue 4 above (lazy import).

### C. React build fails on first attempt

TypeScript error in useExport.ts.
Fix: Issue 1 above (widen type).

### D. `./run.sh check` will error

The streamlit check category runs a deleted script.
Fix: Issue 7 above.

### E. node_modules won't exist

Run `cd react_app && npm install` first.
Guide already covers this.

---

## Recommended Fix Order

1. **Issue 1** — Fix React TS error (unblocks build)
2. **Issue 2** — Move sample data into tracked repo (unblocks UI demo)
3. **Issue 4** — Lazy-import xlwings in excel_bridge (unblocks clean install)
4. **Issue 3** — Uninstall ghost packages from old venv
5. **Issue 5** — Delete orphaned Streamlit test files
6. **Issue 7** — Clean run.sh and check_all.py
7. **Issue 8** — Clean Streamlit refs from active scripts
8. **Issue 6** — Fix broken doc links
9. **Issue 10** — Reinstall editable package
10. **Issue 9** — Clean docstring
11. **Issue 11** — Fix deprecation test

---

## Quick Fix Commands (Copy-Paste)

```bash
# Issue 1: React TS fix — edit react_app/src/hooks/useExport.ts line 67
# Change: body: ExportBeamParams | ExportReportParams,
# To:     body: ExportBeamParams | ExportReportParams | BuildingExportParams,

# Issue 2: Move sample data
mkdir -p Python/structural_lib/data/sample_building
cp VBA/ETABS_Export_v2/Etabs_output/2026-01-17_222801/*.csv \
   Python/structural_lib/data/sample_building/

# Issue 3: Remove ghost packages
.venv/bin/pip uninstall streamlit plotly xlwings -y

# Issue 5: Delete orphaned test files
rm tests/test_lod_manager.py tests/test_lod_performance.py \
   tests/test_report_export_component.py tests/test_visualizations_3d.py \
   scripts/test_import_3d_pipeline.py

# Issue 6: Auto-fix doc links
.venv/bin/python scripts/check_links.py --fix

# Issue 10: Reinstall to pick up version
cd Python && ../.venv/bin/pip install -e ".[dev]" && cd ..
```
