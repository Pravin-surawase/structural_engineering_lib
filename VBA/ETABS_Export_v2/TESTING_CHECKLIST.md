# ETABS Comprehensive Export - Testing Checklist

**Date:** 2025-01-27
**Version:** v1.0
**Status:** Ready for Testing

---

## ✅ Pre-Testing Setup

### 1. ETABS Model Requirements
- [ ] ETABS is running with model open
- [ ] Model contains beams and columns
- [ ] Analysis has been run (F5)
- [ ] Model has multiple stories (for story export test)
- [ ] Load cases and combos exist

### 2. Excel VBA Setup
- [ ] Open Excel
- [ ] Press `Alt+F11` (VBA Editor)
- [ ] **Tools → References → Browse**
- [ ] Navigate to: `C:\Program Files\Computers and Structures\ETABS XX\ETABS.exe`
- [ ] Check "ETABS Object Library" → OK
- [ ] **File → Import File → ETABS_ComprehensiveExport.bas**

---

## 🧪 Test Cases

### Test 1: Quick Geometry Export (No Forces)
**Function:** `ExportGeometryOnly`
**Expected Time:** 2-5 seconds
**Purpose:** Test API calls without slow force calculations

**Steps:**
1. In VBA Editor: Press `Alt+F8`
2. Select: `ExportGeometryOnly`
3. Click **Run**

**Expected Result:**
- Success message with counts
- Output folder: `Documents\ETABS_Export\<timestamp>\`
- 3 CSV files created:
  - `stories.csv` ✓
  - `frames_geometry.csv` ✓
  - `frames_properties.csv` ✓

**Validation:**
```csv
# stories.csv should have:
StoryName,Elevation_m
Ground,0.000
Story1,3.000

# frames_geometry.csv should have:
UniqueName,Label,Story,FrameType,SectionName,Point1Name,Point2Name,...
1,82,Ground,Beam,230x450,1,2,0.000,0.000,0.000,2.750,0.000,0.000,...

# frames_properties.csv should have:
SectionName,Width_mm,Depth_mm,Material,FrameType
230x450,230,450,C25,Beam
300x300,300,300,C25,Column
```

---

### Test 2: Full Export (With Forces)
**Function:** `ExportAllForVisualization`
**Expected Time:** 10-30 seconds (depends on model size)
**Purpose:** Complete data export including envelope forces

**Steps:**
1. In VBA Editor: Press `Alt+F8`
2. Select: `ExportAllForVisualization`
3. Click **Run**

**Expected Result:**
- Success message with counts and time
- Output folder: `Documents\ETABS_Export\<timestamp>\`
- 4 CSV files created:
  - `stories.csv` ✓
  - `frames_geometry.csv` ✓
  - `frames_properties.csv` ✓
  - `beam_forces.csv` ✓ (NEW - only beams)

**Validation:**
```csv
# beam_forces.csv should have:
UniqueName,Label,Story,SectionName,Width_mm,Depth_mm,Span_m,Mu_max_kNm,Mu_min_kNm,Vu_max_kN
1,82,Ground,230x450,230,450,2.750,7.526,0.000,13.088
```

---

### Test 3: Error Handling
**Purpose:** Verify graceful failure when ETABS not running

**Steps:**
1. **Close ETABS** (important!)
2. Run either export function
3. Observe error message

**Expected Result:**
- Error message: "Failed to connect to ETABS. Make sure ETABS is running."
- No crash, clean exit

---

## 🔍 Common Issues & Fixes

### Issue 1: "User-defined type not defined"
**Cause:** ETABS reference not added
**Fix:** Add ETABS reference (see Pre-Testing Setup #2)

### Issue 2: "Method or data member not found"
**Cause:** ETABS API version mismatch
**Fix:** Check ETABS version, API should be v1 (ETABSv1.xxx)

### Issue 3: "Wrong number of arguments"
**Cause:** API signature mismatch
**Fix:** This should NOT happen - code uses verified legacy patterns

### Issue 4: Empty CSV files (0 records)
**Possible Causes:**
- Model has no frames → Expected behavior
- Analysis not run → Run analysis in ETABS (F5)
- All frames are "DUMMY" or "Stiff Beam" → Expected filtering

### Issue 5: Slow export (>60 seconds)
**Cause:** Large model (1000+ beams) with many load combos
**Fix:** Use `ExportGeometryOnly` instead, or set `EXPORT_BEAM_FORCES = False`

---

## 📊 Output Verification

### Check 1: File Sizes
**Typical values for small model (100 frames):**
- `stories.csv`: 1-2 KB (5-10 stories)
- `frames_geometry.csv`: 10-50 KB (100 frames)
- `frames_properties.csv`: 1-2 KB (5-10 unique sections)
- `beam_forces.csv`: 5-20 KB (50 beams)

### Check 2: Data Consistency
**Cross-check between files:**
- Every `SectionName` in `frames_geometry.csv` should exist in `frames_properties.csv`
- Every `Story` in `frames_geometry.csv` should exist in `stories.csv`
- Every `UniqueName` in `beam_forces.csv` should exist in `frames_geometry.csv`

### Check 3: Coordinate Sanity
**frames_geometry.csv:**
- Point1X, Point1Y, Point1Z should be ≠ Point2X, Point2Y, Point2Z (unless vertical column)
- Coordinates should match model extents (e.g., if model is 20m x 30m)
- Elevations (Point1Z, Point2Z) should match story elevations

### Check 4: Forces Sanity
**beam_forces.csv:**
- `Mu_max_kNm` should be ≥ 0 (sagging moment)
- `Mu_min_kNm` should be ≤ 0 (hogging moment)
- `Vu_max_kN` should be > 0
- Values should be reasonable (e.g., 5m beam: Mu ~ 50-200 kN·m)

---

## ✅ Success Criteria

**Export is successful if:**
- [x] All expected CSV files created
- [x] No VBA errors during execution
- [x] File sizes > 0 bytes
- [x] CSV headers match documentation
- [x] Data rows exist (if model has frames)
- [x] Coordinates are reasonable
- [x] No missing/null values in critical columns

---

## 🐛 Bug Report Template

If you encounter issues, report with:

```
**Issue:** [Brief description]
**Function:** [ExportAllForVisualization | ExportGeometryOnly]
**ETABS Version:** [e.g., ETABS 2020]
**Model Size:** [Number of beams/columns]
**Error Message:** [Exact VBA error or message box text]
**Output:** [What files were created, if any]
**VBA Line:** [Line number where error occurred, if shown]
```

---

## 📝 Post-Testing

After successful testing:
- [ ] Verify CSV files open correctly in Excel
- [ ] Check if data matches ETABS model visually
- [ ] Note any performance issues (time > 60s)
- [ ] Ready for Streamlit import

**Next Step:** Import CSVs into Streamlit 3D visualization

---

**Status:** 🟢 Ready for User Testing
**Last Updated:** 2025-01-27
