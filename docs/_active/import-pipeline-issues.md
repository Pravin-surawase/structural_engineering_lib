# Import Pipeline — Issues & Solutions

**Type:** Reference
**Audience:** Developers
**Status:** Draft
**Importance:** Critical
**Created:** 2025-03-26
**Last Updated:** 2025-07-16

## Summary

After Mac Mini migration, the CSV import pipeline has several frontend issues.
Backend (FastAPI) endpoints all work correctly — verified via curl.
All issues are TypeScript interface mismatches and a missing UI state transition.

---

## Issue 1: CRITICAL — Dual CSV Import UI Gets "Stuck"

**Symptom**: User uploads geometry + forces CSVs, clicks "Import & Merge", beams are imported (stored in Zustand), but UI stays on the Upload step. Never transitions to Preview step.

**Root Cause**: Missing step transition callback for dual CSV import.

- **Single CSV path** (works): `FileDropZone` has a `useEffect` watching `data?.success && data.beam_count > 0` → calls `onSuccess(count)` → `handleFileImported(count)` → `setStep("preview")`.
- **Dual CSV path** (broken): `handleDualImport()` calls `importFiles()`. The `useDualCSVImport` hook's `onSuccess` stores beams via `setBeams()` but has no callback to signal completion to `UploadStep`. No `useEffect` watches the dual import result.

**Files**: `react_app/src/components/import/ImportView.tsx`, `react_app/src/hooks/useCSVImport.ts`

**Fix**: Add a `useEffect` in `UploadStep` that watches `useDualCSVImport`'s `data` result and calls `onFileImported(data.beam_count)` when successful.

---

## Issue 2: MODERATE — CSVImportResponse TS Type Mismatch

**Symptom**: No runtime error, but TypeScript type doesn't match actual API response.

**Details**:
- TS interface declares `column_mapping: Record<string, string>` — field does NOT exist in API response
- TS interface missing `format_detected: string` — field DOES exist in API response

**Actual API response keys**: `success, message, beam_count, beams, format_detected, warnings`

**File**: `react_app/src/hooks/useCSVImport.ts` (line ~73)

**Fix**: Remove `column_mapping`, add `format_detected`.

---

## Issue 3: MODERATE — BatchDesignResponse TS Type Mismatches

**Symptom**: If the simple batch design hook from `useCSVImport.ts` is used, result data would be incorrectly typed.

**Details**:
| Field | TS Interface | Actual API |
|-------|-------------|------------|
| Count field | `successful: number` | `passed: number` |
| Results type | `DesignedBeam[]` | `BatchDesignResult[]` |
| Result shape | Nested `design?: {...}` | Flat: `beam_id, ast_required, asc_required, stirrup_spacing, is_safe, utilization_ratio, error` |
| Extra field | `warnings: string[]` | Not present |

**File**: `react_app/src/hooks/useCSVImport.ts` (lines ~84-92)

**Fix**: Align TS `BatchDesignResponse` and result type with actual API response.

---

## Issue 4: LOW — Duplicate useBatchDesign Hooks

**Details**: Two different `useBatchDesign` hooks exist:
1. `useCSVImport.ts` — Simple POST to `/import/batch-design` (exported from barrel `hooks/index.ts`)
2. `useBatchDesign.ts` — SSE streaming to `/stream/batch-design` (imported directly by `BatchDesignPage.tsx`)

**Impact**: Confusing but not a runtime bug since consumers import the right one.

**Fix**: No action needed now. Could rename or consolidate later.

---

## Verification

All backend endpoints verified working via curl:

```
POST /api/v1/import/csv          → 200, 153 beams (from beam_forces.csv)
POST /api/v1/import/dual-csv     → 200, 153 beams (geometry + forces)
GET  /api/v1/import/sample       → 200, 153 beams (with 3D positions)
POST /api/v1/import/batch-design → 200, design results with correct shape
```

Field mappings in `useCSVImport.ts` `onSuccess` callbacks are correct (fixed in previous session):
- `b.id` → `id`, `b.width_mm` → `b`, `b.depth_mm` → `D`, `b.span_mm` → `span`
- `b.mu_knm` → `Mu_mid`, `b.vu_kn` → `Vu_start`/`Vu_end`, `b.cover_mm` → `cover`

Sample data mapping in `sampleData.ts` is correct.
CORS is properly configured for `localhost:5173`.

---

## Issue 5: CRITICAL — Single CSV Import Crashes (BeamGeometry.length_mm)

**Symptom**: Single CSV import via `/api/v1/import/csv` returns 500 Internal Server Error when using generic CSV format. Error: `'BeamGeometry' object has no attribute 'length_mm'`.

**Root Cause**: `fastapi_app/routers/imports.py` line 236 used `geom.length_mm`, but `BeamGeometry` (from `structural_lib.core.models`) only has `length_m` (computed field, in meters).

**Fix**: Changed `span_mm=geom.length_mm` → `span_mm=geom.length_m * 1000` to convert meters to millimeters.

**Status**: ✅ Fixed

---

## Issue 6: MODERATE — Auto-Detection Picks Wrong Adapter

**Symptom**: Generic CSV files with a "Story" column are incorrectly matched by the ETABS adapter's `can_handle()`. Since ETABS is tried first in auto-detection, it gets selected but then fails on `load_geometry()` (requires `label`, `point1_x`, etc.), causing a 422 error instead of falling through to the Generic adapter.

**Root Cause**: ETABS `can_handle()` checks for `{"Story", "Label", "XI", "XJ", "JointI", "JointJ"}` intersection — a CSV with just "Story" matches. The endpoint then committed to this adapter without fallback.

**Fix**: Rewrote the auto-detection loop to try all candidate adapters sequentially. If one adapter fails both `load_geometry()` and `load_forces()`, the next candidate is tried. Only raises 422 if ALL adapters fail.

**Status**: ✅ Fixed

---

## Issue 7: NO ISSUE — Sample Building Path Verified Working

**Investigation**: Traced the sample building flow end-to-end:
- `ImportView.tsx` → `loadSampleData()` → `GET /api/v1/import/sample` → 153 beams with 3D positions
- `mapSampleBeamsToRows()` maps fields correctly: `width_mm→b`, `depth_mm→D`, `span_mm→span`, etc.
- `applyMaterialOverrides()` applies `fck`, `fy`, `cover` overrides correctly
- `setBeams()` stores in Zustand → `setStep("preview")` transitions UI

All `SampleBeam`, `SampleDataResponse`, `Point3D` TypeScript interfaces match the actual API response exactly. **No issues found.**

**Status**: ✅ Verified working — no fix needed

---

## Test Coverage

### pytest (47/47 pass)
- `fastapi_app/tests/test_endpoints.py` — 47 tests including 11 new import tests:
  - `test_single_csv_import` — 2 beams imported via generic CSV
  - `test_single_csv_response_shape` — validates response keys match TypeScript interface
  - `test_single_csv_beam_fields` — validates all required beam fields present
  - `test_sample_data_endpoint` — sample building with 3D positions
  - `test_sample_beam_has_3d` — validates `point1`/`point2` in sample beams
  - `test_sample_beam_fields` — validates all sample beam fields
  - `test_batch_design_endpoint` — batch design returns results
  - `test_batch_design_response_shape` — validates batch response keys
  - `test_batch_design_result_fields` — validates individual result fields

### Standalone E2E tests (18/18 pass)
- `scripts/test_import_pipeline.py` — comprehensive test against live server covering health, sample (6), single CSV (3), dual CSV (4), batch design (4)
