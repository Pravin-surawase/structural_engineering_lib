**Type:** Plan
**Audience:** All Agents  
**Status:** Draft
**Importance:** High
**Created:** 2026-01-17
**Related Tasks:** ETABS Export Production, Streamlit Integration

# ETABS Export Production Plan

## Current State
- ✅ VBA export working: 364,365 rows
- ✅ Columns: Story, Label, Output Case, Station, M3, V2, P
- ✅ All frames (225), all cases/combos (36), multiple stations

## Problem
- **Too much data:** 364K rows exceeds Streamlit needs
- **Unfiltered:** Includes load cases (not just combinations)
- **Raw values:** No envelopes, no design-specific filtering
- **Missing data:** Need section properties, material properties

---

## Phase 1: Data Requirements Analysis

### A. IS456 Beam Design Inputs Required

**From flexure.py analysis:**
```python
def calculate_ast_required(
    moment: float,      # kN·m - HAVE from ETABS
    width: float,       # mm - NEED section property
    depth: float,       # mm - NEED section property  
    fck: float,         # N/mm² - NEED material property
    fy: float,          # N/mm² - NEED material property
    ...
)
```

**Required Data Layers:**

**Layer 1: Forces (HAVE - Current Export)**
- Bending moments (M3) in kN·m
- Shear forces (V2) in kN
- Axial forces (P) in kN
- Per frame, per load combination

**Layer 2: Section Properties (NEED - Next Export)**
- Section name (e.g., "C450x230")
- Width (b) in mm
- Depth (D) in mm
- Clear cover in mm
- Bar diameter assumption for effective depth

**Layer 3: Material Properties (NEED - Next Export)**
- Concrete grade (fck) in N/mm²
- Steel grade (fy) in N/mm²
- Per frame or global default

**Layer 4: Structural Info (NEED - Next Export)**
- Span length (for development length, deflection)
- Support conditions (simply supported, continuous)
- Story level (for grouping)

---

## Phase 2: Data Filtering Strategy

### Current: 364,365 rows
**Breakdown:**
- 225 frames
- 36 load cases/combos
- ~143 stations per frame average (364365 / 225 / 36)

### Target: ~2,000-5,000 rows

**Filtering Logic:**

**1. Remove Load Cases (keep only Load Combinations)**
- Load cases: Modal, DEAD, LIVE, EQX, EQY, etc.
- Load combinations: COMB1, COMB2, 1.5(DL+LL), 1.2(DL+LL+EQX), etc.
- Reduction: ~40-60% (if ~20 cases, ~16 combos)

**2. Critical Stations Only**
- Option A: Max/min moments only (envelope per combo)
- Option B: Specific stations (supports, midspan, quarter points)
- Option C: Filter by |M3| > threshold (skip negligible moments)
- Reduction: 90-95% (from ~143 stations to 1-5 critical per frame)

**3. Design Load Combinations Only**
- Filter to specific combos: 1.5(DL+LL), 1.2(DL+LL±EQ), 1.5(DL+WL)
- Skip: Service combinations, rare combinations if not needed
- Reduction: 50-70% (from ~16 combos to 3-5 design combos)

**Final Estimate:**
```
225 frames × 5 design combos × 2 critical stations = 2,250 rows
```

---

## Phase 3: VBA Implementation Plan

### File Structure
```
VBA/ETABS_Export_v2/
├── ETABS_Export_Production.bas       (Main export - filtered forces)
├── ETABS_Export_Properties.bas       (Section + material properties)
├── ETABS_Export_Config.bas          (User-configurable filters)
└── README.md                         (Usage guide)
```

### Export 1: Filtered Forces (High Priority)

**Function:** `ExportBeamForces_Filtered()`

**Filters to implement:**
```vba
' 1. Combo filtering
Dim designCombos As Variant
designCombos = Array("COMB1", "COMB2", "COMB3")  ' User-configurable

' 2. Station filtering - Get envelope per combo
For each frame:
    For each combo:
        Find max positive M3 and its station
        Find max negative M3 and its station  
        Find max |V2| and its station
        Write 2-3 rows per combo per frame
```

**Calculations to add:**
```vba
' A. Station in meters (convert from model units)
stationMeters = ElmSta(j) * unitConversionFactor

' B. Absolute max shear (for design)
maxAbsShear = Abs(V2(j))

' C. Support moment adjustment flag
If stationMeters < 0.1 Then
    isSupportLocation = True
End If
```

**Output Columns:**
```
Story, Label, LoadCombo, Station_m, M3_kNm, V2_kN, P_kN, LocationType
```

Where LocationType: "Support", "Span", "Max+M", "Max-M", "MaxShear"

### Export 2: Frame Properties

**Function:** `ExportBeamProperties()`

**ETABS API calls:**
```vba
' Get section for frame
Dim sectName As String
ret = mySapModel.FrameObj.GetSection(frameName, sectName, ...)

' Get section dimensions (if standard)
Dim depth As Double, width As Double
ret = mySapModel.PropFrame.GetRectangle(sectName, fileName, matProp, _
    depth, width, ...)

' Get material
Dim matName As String
ret = mySapModel.PropFrame.GetMaterial(sectName, matName, ...)

' Get material properties
Dim fck As Double
' Parse from material name or property
```

**Output CSV:**
```
Label, Section, Width_mm, Depth_mm, Material, fck_MPa, fy_MPa, Cover_mm
```

### Export 3: Span Information

**Function:** `ExportBeamSpans()`

**ETABS API calls:**
```vba
' Get frame points
Dim point1 As String, point2 As String
ret = mySapModel.FrameObj.GetPoints(frameName, point1, point2)

' Get point coordinates
Dim x1, y1, z1, x2, y2, z2 As Double
ret = mySapModel.PointObj.GetCoordCartesian(point1, x1, y1, z1)
ret = mySapModel.PointObj.GetCoordCartesian(point2, x2, y2, z2)

' Calculate span
Dim spanLength As Double
spanLength = Sqr((x2-x1)^2 + (y2-y1)^2 + (z2-z1)^2)
```

**Output CSV:**
```
Label, Story, Point1, Point2, Span_m, Orientation
```

---

## Phase 4: Configuration Module

### User-Editable Settings

**File:** `ETABS_Export_Config.bas`

```vba
' ============================================
' USER CONFIGURATION - Edit these values
' ============================================

' 1. Load combinations to export (comma-separated)
Public Const DESIGN_COMBOS As String = "COMB1,COMB2,COMB3,COMB4,COMB5"

' 2. Station filtering method
Public Enum StationFilterMethod
    EnvelopeOnly = 1        ' Max/min per combo only (smallest output)
    CriticalStations = 2    ' Supports + midspan + quarter points
    AllStations = 3         ' No filtering (largest output)
End Enum
Public Const STATION_FILTER As StationFilterMethod = EnvelopeOnly

' 3. Material defaults (if not found in model)
Public Const DEFAULT_FCK As Double = 25    ' N/mm²
Public Const DEFAULT_FY As Double = 500    ' N/mm²
Public Const DEFAULT_COVER As Double = 25  ' mm

' 4. Output folder
Public Const OUTPUT_FOLDER As String = "%USERPROFILE%\Documents\ETABS_Export"

' 5. Minimum moment threshold (skip if |M| < this)
Public Const MIN_MOMENT_KNM As Double = 1.0

' 6. Export options
Public Const EXPORT_TO_EXCEL As Boolean = True
Public Const EXPORT_TO_CSV As Boolean = True
Public Const OPEN_FOLDER_AFTER_EXPORT As Boolean = True
```

---

## Phase 5: Archive Strategy

### Move to Archive Folder

**Create:** `VBA/ETABS_Export_v2/_archive/`

**Archive Structure:**
```
_archive/
├── session31_trials/
│   ├── mod_ETABS_Core_v2.1.bas
│   ├── mod_ETABS_Core_v2.2.bas
│   ├── mod_ETABS_Core_v2.3.bas
│   ├── mod_ETABS_Export_v2.1.bas
│   ├── mod_ETABS_Export_v2.2.bas
│   ├── mod_ETABS_Export_v2.3.bas
│   ├── APPROACH_1_DatabaseTablesOnly.bas
│   ├── APPROACH_2_LegacyPattern.bas
│   └── APPROACH_3_MinimalAPI.bas
├── session31_diagnostics/
│   ├── DIAGNOSTIC_Simple.bas
│   ├── DEBUG_Step1_CheckAnalysis.bas
│   ├── DEBUG_Step2_SingleFrame.bas
│   ├── DEBUG_Step3_AllFrames.bas
│   ├── DEBUG_Step4_CaseSelection.bas
│   ├── DEBUG_Step5_RawExport.bas
│   └── DEBUG_Step6_DatabaseTables.bas
├── session31_solutions/
│   ├── SOLUTION_DatabaseTablesAll.bas
│   └── INSTRUCTIONS_AddReference.bas
└── README.md  (explains archive contents)
```

---

## Phase 6: Implementation Order

### Step 1: Create Archive (5 min)
- Create `_archive/` folder structure
- Move 20 trial/diagnostic files
- Create archive README

### Step 2: Rename Current Working File (1 min)
- `FINAL_WithReference.bas` → `ETABS_Export_Production_v1.bas`
- Keep as baseline

### Step 3: Implement Config Module (10 min)
- Create `ETABS_Export_Config.bas`
- Define all user-configurable settings
- Document each option

### Step 4: Implement Filtered Forces Export (30 min)
- Copy `ETABS_Export_Production_v1.bas` → `ETABS_Export_Production_v2.bas`
- Add combo filtering logic
- Add envelope calculation logic
- Add output format with LocationType column
- Test with 10 frames first

### Step 5: Implement Properties Export (20 min)
- Create `ETABS_Export_Properties.bas`
- Get section dimensions from ETABS
- Get material properties
- Export to separate CSV

### Step 6: Implement Span Export (15 min)
- Create `ETABS_Export_Spans.bas`
- Calculate span lengths
- Export to separate CSV

### Step 7: Integration & Testing (20 min)
- Create master export function
- Test all 3 exports together
- Verify file outputs
- Document usage

### Step 8: Update Documentation (10 min)
- Create production README
- Update session log
- Update next session brief

**Total Estimated Time:** ~2 hours

---

## Phase 7: Streamlit Integration Plan

### CSV Files to Upload

**1. beam_forces_filtered.csv** (~2-5K rows)
```
Story,Label,LoadCombo,Station_m,M3_kNm,V2_kN,P_kN,LocationType
Story1,B1,COMB1,0.000,45.2,32.1,-15.0,Support
Story1,B1,COMB1,3.500,85.6,0.5,-15.0,Max+M
```

**2. beam_properties.csv** (~225 rows)
```
Label,Section,Width_mm,Depth_mm,Material,fck_MPa,fy_MPa,Cover_mm
B1,C450x230,230,450,M25,25,500,25
```

**3. beam_spans.csv** (~225 rows)
```
Label,Story,Point1,Point2,Span_m,Orientation
B1,Story1,P101,P102,7.0,Major
```

### Streamlit Page Updates

**File:** `streamlit_app/pages/beam_design.py` (or similar)

**Add CSV Upload:**
```python
col1, col2, col3 = st.columns(3)

with col1:
    forces_file = st.file_uploader("Beam Forces (CSV)", type="csv")
    
with col2:
    props_file = st.file_uploader("Beam Properties (CSV)", type="csv")
    
with col3:
    spans_file = st.file_uploader("Beam Spans (CSV)", type="csv")

if forces_file and props_file:
    df_forces = pd.read_csv(forces_file)
    df_props = pd.read_csv(props_file)
    
    # Merge data
    df = df_forces.merge(df_props, on="Label", how="left")
    
    # Call design API for each row
    for idx, row in df.iterrows():
        result = calculate_ast_required(
            moment=row['M3_kNm'],
            width=row['Width_mm'],
            depth=row['Depth_mm'],
            fck=row['fck_MPa'],
            fy=row['fy_MPa']
        )
```

---

## Success Metrics

**Data Size:**
- ✅ Forces CSV < 1 MB (from 364K rows to 2-5K)
- ✅ Properties CSV < 50 KB
- ✅ Spans CSV < 50 KB

**Data Quality:**
- ✅ Only design load combinations
- ✅ Only critical stations (envelope + supports)
- ✅ Complete section/material properties
- ✅ No missing data for design calculations

**Usability:**
- ✅ Export time < 60 seconds for all 3 files
- ✅ Config file is clear and well-documented
- ✅ Output files ready for direct Streamlit upload
- ✅ No post-processing needed

**Code Quality:**
- ✅ All trial files archived
- ✅ Only production code in main folder
- ✅ Comprehensive README
- ✅ Error handling for all API calls

---

## Next Session Priorities

1. **Immediate:** Archive trial files (cleans up repository)
2. **High:** Implement filtered forces export (reduces data 100x)
3. **High:** Implement properties export (enables design calculations)
4. **Medium:** Implement spans export (enables span-dependent checks)
5. **Medium:** Create master export function (one-click export)
6. **Low:** Streamlit integration (after VBA exports proven)

---

**Document Status:** Draft - Ready for implementation
**Estimated Effort:** 2-3 hours for complete implementation
**Dependencies:** None (current export works, this is enhancement)
