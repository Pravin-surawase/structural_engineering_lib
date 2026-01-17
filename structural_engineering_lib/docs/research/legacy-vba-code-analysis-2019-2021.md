# Legacy VBA Code Analysis (2019-2021)

**Created:** 2026-01-17  
**Purpose:** Document and analyze Pravin's working ETABS VBA automation from structural engineering firm  
**Source:** 8 VBA modules from production use

---

## Executive Summary

This legacy code is **extremely valuable** because:
1. **It worked in production** - proven patterns from real projects
2. **Uses early binding** - more reliable than our late binding approach
3. **Has complete workflows** - analysis → design → results extraction
4. **Covers features we need** - beam/column design, base reactions, load combos

### Key Discovery: Early Binding vs Late Binding

**Our current approach (problematic):**
```vb
Dim sapModel As Object  ' Late binding - causes "Class does not support Automation"
Set sapModel = etabs.SapModel
```

**Legacy approach (reliable):**
```vb
Dim mySapModel As ETABSv1.cSapModel  ' Early binding - full IntelliSense, reliable
Set mySapModel = myETABSObject.SapModel
```

---

## Module Analysis

### 1. BASE_REACTIONS.bas
**Purpose:** Extract base reactions for seismic scaling verification

**Key APIs Used:**
```vb
' Attach to ETABS (early binding)
Set myHelper = New ETABSv1.Helper
Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
Set mySapModel = myETABSObject.SapModel

' Set units
ret = mySapModel.SetPresentUnits(eUnits_Ton_m_C)
' or
ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)

' Deselect all output cases
ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

' Select specific load case
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("Ex")

' Get base reactions
ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, _
                                    Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)

' Select combo for output
ret = mySapModel.Results.Setup.SetComboSelectedForOutput("Rx_scaled")

' Get model filename
Model_Name = mySapModel.GetModelFilename(False)
```

**Workflow:**
1. Attach to ETABS
2. Run analysis if needed (`CreateAnalysisModel` + `RunAnalysis`)
3. Set output units
4. Select load cases for output
5. Extract base reactions (Fx, Fy, Fz, Mx, My, Mz)
6. Write to Excel worksheet

**Useful For Us:** ✅ Base reaction export for Streamlit app

---

### 2. BEAM_DESIGN.bas
**Purpose:** Get beam reinforcement design results

**Key APIs Used:**
```vb
' Start concrete design
ret = mySapModel.DesignConcrete.StartDesign()

' Get beam summary results
ret = mySapModel.DesignConcrete.GetSummaryResultsBeam("20", NumberItems, _
    FrameName, Location, TopCombo, TopArea, BotCombo, BotArea, _
    VmajorCombo, VmajorArea, TLCombo, TLArea, TTCombo, TTArea, _
    ErrorSummary, WarningSummary)

' Get available database tables
ret = mySapModel.DatabaseTables.GetAvailableTables(NumberTables, TableKey, TableName, ImportType)

' Set load cases/combos for display
ret = mySapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(LoadCombinationList)
ret = mySapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(LoadCaseList)

' Show tables in Excel
ret = mySapModel.DatabaseTables.ShowTablesInExcel(TableKeyList, WindowHandle)
```

**Key Insight:** `GetSummaryResultsBeam` returns:
- `TopArea()` - Top reinforcement area at each location
- `BotArea()` - Bottom reinforcement area
- `VmajorArea()` - Shear reinforcement
- `TLArea()` - Torsion longitudinal
- `TTArea()` - Torsion transverse
- `Location()` - Station along beam

**Useful For Us:** ✅ Beam design results for Streamlit visualization

---

### 3. torsional_irregularity.bas
**Purpose:** Check torsional irregularity per code requirements

**Key APIs Used:**
```vb
' Run analysis
ret = mySapModel.Analyze.RunAnalysis()

' Deselect all, select specific case
ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(LoadCase1)

' Get point name from label
ret = mySapModel.PointObj.GetNameFromLabel(Jtno, Story, Name)

' Get joint displacements
ret = mySapModel.Results.JointDispl(Name, ItemTypeElm, NumberResults, _
    Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
```

**Workflow:**
1. Read joint labels and story from Excel
2. Convert label to internal name
3. Get joint displacements (U1, U2, U3 translations; R1, R2, R3 rotations)
4. Calculate torsional irregularity ratios

**Useful For Us:** ✅ Joint displacement export, story drift analysis

---

### 4. SCALING.bas
**Purpose:** Automate response spectrum scaling to match base shear

**Key APIs Used:**
```vb
' Get combo case list with scale factors
ret = mySapModel.RespCombo.GetCaseList(Rx_scaled, NumberItems, CNameType, CName, SF)

' Set combo case list (update scale factor)
ret = mySapModel.RespCombo.SetCaseList(Rx_scaled, eCNameType_LoadCase, "RX", SF_NEW_X)

' Initialize new model
ret = mySapModel.InitializeNewModel(eUnits_Ton_m_C)

' Create new grid-only model
ret = mySapModel.File.newgridonly(4, 4, 4, 4, 4, 4, 4)

' Add load pattern
ret = mySapModel.LoadPatterns.Add("Ex", eLoadPatternType_Quake, 0, True)
```

**Key Insight:** This automates the tedious manual process of:
1. Get Ex/Ey base reactions
2. Get Rx_scaled/Ry_scaled base reactions
3. Calculate scale factor = Static/Dynamic
4. Update combo scale factors
5. Re-run and verify

**Useful For Us:** ✅ Automated seismic scaling workflow

---

### 5. COLUMNS.bas (Most Comprehensive!)
**Purpose:** Complete column design workflow with reinforcement selection

**Key APIs Used:**
```vb
' Get ALL frames at once
ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
    PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
    Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)

' Check if design results available
ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()

' Get column summary results
ret = mySapModel.DesignConcrete.GetSummaryResultsColumn(MyName(i), NumberItems, _
    FrameName, MyOption, Location, PMMCombo, PMMArea, PMMRatio, _
    VmajorCombo, AVmajor, VminorCombo, AVminor, ErrorSummary, WarningSummary, eItemType_Objects)

' Get frame type (column vs beam)
ret = mySapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)
' Frame_Type: 1 = Column, 2 = Beam

' Get rectangular section properties
ret = mySapModel.PropFrame.GetRectangle(PropName(i), FileName, MatProp, t3, t2, Color, Notes, GUID)

' Get label from internal name
ret = mySapModel.FrameObj.GetLabelFromName(MyName(i), Label, story_from_Label)

' Get all frame properties
ret = mySapModel.PropFrame.GetAllFrameProperties_2(NumberNames, MyName, PropType, _
    t3, t2, tf, tw, t2b, tfb, Area)

' Set frame section
ret = mySapModel.FrameObj.SetSection(UName, Updated_Section)

' Get diaphragm info
ret = mySapModel.Diaphragm.GetNameList(NumberNames, MyName1)
ret = mySapModel.Diaphragm.GetDiaphragm(MyName1(i), SemiRigid)

' Select/deselect objects
ret = mySapModel.SelectObj.ClearSelection
ret = mySapModel.FrameObj.SetSelected(selected_columns(k), True)

' Unlock model for modifications
ret = mySapModel.SetModelIsLocked(False)

' Refresh view
ret = mySapModel.View.RefreshView
```

**Complete Column Workflow:**
1. Get all frames with geometry
2. Filter columns only (Frame_Type = 1)
3. Get design results (PMMArea = required steel area)
4. Calculate required bars based on section size
5. Provide reinforcement matching required area
6. Group similar columns
7. Allow section updates back to ETABS

**Key Data Extracted:**
- Story, Label, Internal Name, Section
- Width, Depth, Required Steel Area, Steel Ratio
- X, Y, Z coordinates
- Column length
- Warning messages

**Useful For Us:** ✅ This is EXACTLY what we need for column design export!

---

### 6. LoadCombo.bas
**Purpose:** Read/write load combinations between Excel and ETABS

**Key APIs Used:**
```vb
' Get list of all combos
ret = mySapModel.RespCombo.GetNameList(NumberNames, MyName)

' Get cases in a combo
ret = mySapModel.RespCombo.GetCaseList(MyName(i - 1), NumberItems, CNameType, CName, SF)

' Get combo type
ret = mySapModel.RespCombo.GetTypeCombo(MyName(i - 1), ComboType)
' ComboType: 0=Linear Additive, 1=Envelope, 2=Absolute Additive, 3=SRSS, 4=Range Additive

' Delete combo
ret = mySapModel.RespCombo.Delete(MyName(i))

' Add new combo
ret = mySapModel.RespCombo.Add(Name_From_Excel, ComboType_In_etabs)

' Add case to combo
ret = mySapModel.RespCombo.SetCaseList(Name_From_Excel, eCNameType_LoadCase, case_Name_1, SF_1)
' or for load combo:
ret = mySapModel.RespCombo.SetCaseList(Name_From_Excel, eCNameType_LoadCombo, case_Name_1, SF_1)
```

**Workflow:**
1. Export all combos from ETABS to Excel
2. User modifies in Excel
3. Delete all combos in ETABS
4. Create new combos from Excel data

**Useful For Us:** ✅ Load combination management for Streamlit

---

### 7. BeamType.bas
**Purpose:** Classify beams and calculate reinforcement

**Key APIs Used:**
```vb
' Get story list
ret = mySapModel.Story.GetNameList(NumberNames, MyName)

' Get frame points
ret = mySapModel.FrameObj.GetPoints(MyName(i), Point1, Point2)

' Get name from label
ret = mySapModel.FrameObj.GetNameFromLabel(Label(i), Story(i), Name)

' Get beam summary results v2 (more detailed)
ret = mySapModel.DesignConcrete.GetSummaryResultsBeam_2(Name, NumberItems, _
    FrameName, Location, _
    TopCombo, TopArea, TopAreaReq, TopAreaMin, TopAreaProvided, _
    BotCombo, BotArea, BotAreaReq, BotAreaMin, BotAreaProvided, _
    VmajorCombo, VmajorArea, VmajorAreaReq, VmajorAreaMin, VmajorAreaProvided, _
    TLCombo, TLArea, TTCombo, TTArea, _
    ErrorSummary, WarningSummary, eItemType_Objects)
```

**Beam Classification Logic:**
- X-Direction beams: Point1Y = Point2Y
- Y-Direction beams: Point1X = Point2X
- End conditions: Check if beam shares points with adjacent beams
- Continuous vs Discontinuous ends

**Reinforcement Selection:**
- Top End 1, Top Mid, Top End 2, Bottom
- Calculates bars needed for each zone
- Handles double-layer reinforcement for deep beams

**Useful For Us:** ✅ Beam classification and design summary

---

### 8. ShearWall.bas
**Purpose:** Shear wall/pier design results and reinforcement

**Key APIs Used:**
```vb
' Get pier names
ret = mySapModel.PierLabel.GetNameList(NumberNames, MyName1)

' Get pier design summary
ret = mySapModel.DesignShearWall.GetPierSummaryResults(Story, PierLabel, Station, _
    DesignType, PierSecType, EdgeBar, EndBar, BarSpacing, ReinfPercent, CurrPercent, _
    DCRatio, PierLeg, LegX1, LegY1, LegX2, LegY2, EdgeLeft, EdgeRight, AsLeft, AsRight, _
    ShearAv, StressCompLeft, StressCompRight, StressLimitLeft, StressLimitRight, _
    CDepthLeft, CLimitLeft, CDepthRight, CLimitRight, InelasticRotDemand, _
    InelasticRotCapacity, NormCompStress, NormCompStressLimit, CDepth, _
    BZoneL, BZoneR, BZoneLength, WarnMsg, ErrMsg)

' Get pier section properties
ret = mySapModel.PierLabel.GetSectionProperties(PierLabel(i), NumberStories, StoryName, _
    AxisAngle, NumAreaObjs, NumLineObjs, WidthBot, ThicknessBot, WidthTop, ThicknessTop, _
    MatProp, CGBotX, CGBotY, CGBotZ, CGTopX, CGTopY, CGTopZ)

' Get story height
ret = mySapModel.Story.GetHeight(StoryName, Height)
```

**Useful For Us:** ✅ Shear wall design export

---

## Critical Learnings for Our Current Work

### 1. Use Early Binding (Add Reference)
The legacy code uses early binding which is more reliable:
```vb
' In VBA Editor: Tools → References → Check "ETABSv1"
Dim myHelper As ETABSv1.cHelper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel
```

### 2. Proper Attach Pattern
```vb
Set myHelper = New ETABSv1.Helper
Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
Set mySapModel = myETABSObject.SapModel
```

### 3. Analysis Check Before Design
```vb
' Check if analysis is up to date
Run1 = mySapModel.Analyze.CreateAnalysisModel
If Run1 = 0 Then ret = mySapModel.Analyze.RunAnalysis

' Check if design results available
ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
```

### 4. Output Selection Pattern
```vb
' Always deselect all first, then select specific cases
ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("Ex")
' OR for combo:
ret = mySapModel.Results.Setup.SetComboSelectedForOutput("COMB1")
```

### 5. Get ALL Frames Efficiently
```vb
' Don't loop and call API for each frame
' Instead, get all at once:
ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, ...)
```

---

## Opportunities for Our Repository

### Immediate Integration Opportunities

| Feature | Legacy Module | Current Gap | Priority |
|---------|--------------|-------------|----------|
| **Frame Forces Export** | COLUMNS.bas, BeamType.bas | Our current export failing | HIGH |
| **Base Reactions** | BASE_REACTIONS.bas | Not implemented | HIGH |
| **Joint Displacements** | torsional_irregularity.bas | Not implemented | MEDIUM |
| **Design Results** | BEAM_DESIGN.bas, COLUMNS.bas | Not implemented | HIGH |
| **Load Combos** | LoadCombo.bas | Not implemented | MEDIUM |
| **Shear Walls** | ShearWall.bas | Not implemented | LOW |

### Recommended Actions

1. **Switch to Early Binding** - Add ETABSv1 reference instead of late binding
2. **Use GetAllFrames** - More efficient than iterating
3. **Add Design Results Export** - Use GetSummaryResultsBeam/Column
4. **Add Base Reactions** - Critical for seismic analysis
5. **Add Load Combo Management** - Useful for automation

---

## Differences from Current ETABS API

The legacy code is for ETABS 2019-2021. Modern changes:

| Legacy API | Current API | Status |
|------------|-------------|--------|
| `ETABSv1.cHelper` | Same | ✅ Compatible |
| `GetObject(, "CSI.ETABS.API.ETABSObject")` | Same | ✅ Compatible |
| `GetSummaryResultsBeam` | `GetSummaryResultsBeam_2` available | ✅ Updated |
| `GetSummaryResultsColumn` | Same | ✅ Compatible |
| `GetAllFrames` | Same | ✅ Compatible |
| `BaseReact` | Same | ✅ Compatible |
| `DatabaseTables.GetTableForDisplayCSVFile` | Same | ✅ Compatible |

**Key Finding:** Most APIs are still valid! The core methods haven't changed.

---

## File Preservation Plan

These legacy files should be preserved at:
```
structural_engineering_lib/
├── VBA/
│   ├── ETABS_Export/           # Our new modules
│   └── Legacy_2019_2021/       # Archive of working code
│       ├── BASE_REACTIONS.bas
│       ├── BEAM_DESIGN.bas
│       ├── BeamType.bas
│       ├── COLUMNS.bas
│       ├── LoadCombo.bas
│       ├── SCALING.bas
│       ├── ShearWall.bas
│       ├── torsional_irregularity.bas
│       └── README.md
```

---

## Next Steps

1. ✅ Document legacy code (this file)
2. 🔲 Archive legacy files in repo
3. 🔲 Update mod_Export.bas to use early binding pattern
4. 🔲 Add GetAllFrames method instead of iteration
5. 🔲 Add design results export (beam/column)
6. 🔲 Add base reactions export
7. 🔲 Test with current ETABS version

---

## Conclusion

**This legacy code is gold.** It provides:
- Proven patterns that worked in production
- Complete workflows we're missing
- Early binding approach that avoids our "Automation" errors
- Efficient bulk data retrieval methods

The fact that Pravin already solved these problems 5 years ago but we've been struggling suggests we need to adopt the **early binding approach** and use these **proven API patterns**.

