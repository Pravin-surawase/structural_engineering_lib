# Legacy VBA Code Archive (2019-2021)

**Origin:** Pravin Surawase's structural engineering automation work  
**Period:** 2019-2021  
**Status:** Archived for reference - **PROVEN WORKING CODE**

---

## 📁 Files in this Archive

| File | Purpose | Key APIs |
|------|---------|----------|
| `BASE_REACTIONS.bas` | Extract base reactions for seismic scaling | `Results.BaseReact`, `RespCombo.SetCaseList` |
| `BEAM_DESIGN.bas` | Beam reinforcement design results | `DesignConcrete.GetSummaryResultsBeam` |
| `BeamType.bas` | Beam classification (X/Y, continuous/discontinuous) | `GetAllFrames`, `GetSummaryResultsBeam_2` |
| `COLUMNS.bas` | **Complete column design workflow** | `GetAllFrames`, `GetSummaryResultsColumn` |
| `LoadCombo.bas` | Load combination management | `RespCombo.GetNameList`, `Add`, `Delete` |
| `SCALING.bas` | Response spectrum scaling automation | `RespCombo.GetCaseList`, `SetCaseList` |
| `ShearWall.bas` | Pier/shear wall design results | `DesignShearWall.GetPierSummaryResults` |
| `torsional_irregularity.bas` | Joint displacement extraction | `Results.JointDispl` |

---

## 🔑 Why This Code is Valuable

### 1. Uses Early Binding (More Reliable)
```vb
' This code uses explicit types - works better with ETABS API
Dim mySapModel As ETABSv1.cSapModel
```

### 2. Proven Production Patterns
All this code was used on real projects in a structural engineering firm.

### 3. Complete Workflows
- Analysis → Design → Results extraction → Excel output
- Includes error handling and user prompts

### 4. Efficient Bulk Operations
```vb
' Get ALL frames at once (efficient)
ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, ...)

' NOT one by one (slow and error-prone)
```

---

## 🎯 Key Features We Need

### Frame Forces & Design Results
From `COLUMNS.bas`:
```vb
' Get column design results (required steel area)
ret = mySapModel.DesignConcrete.GetSummaryResultsColumn(MyName(i), NumberItems, _
    FrameName, MyOption, Location, PMMCombo, PMMArea, PMMRatio, _
    VmajorCombo, AVmajor, VminorCombo, AVminor, _
    ErrorSummary, WarningSummary, eItemType_Objects)
```

### Base Reactions
From `BASE_REACTIONS.bas`:
```vb
' Get base reactions (Fx, Fy, Fz, Mx, My, Mz)
ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, _
    Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
```

### Joint Displacements
From `torsional_irregularity.bas`:
```vb
' Get joint displacements
ret = mySapModel.Results.JointDispl(Name, ItemTypeElm, NumberResults, _
    Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
```

---

## ⚠️ Notes for Modern ETABS

1. **API Reference Requirement**
   - In VBA Editor: Tools → References → Check "ETABSv1"
   - This enables early binding with IntelliSense

2. **Connection Pattern**
   ```vb
   Set myHelper = New ETABSv1.Helper
   Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
   Set mySapModel = myETABSObject.SapModel
   ```

3. **Analysis Check Pattern**
   ```vb
   Run1 = mySapModel.Analyze.CreateAnalysisModel
   If Run1 = 0 Then ret = mySapModel.Analyze.RunAnalysis
   
   ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
   If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
   ```

---

## 📚 Related Documentation

- [Legacy VBA Code Analysis](../../docs/research/legacy-vba-code-analysis-2019-2021.md) - Comprehensive analysis
- [ETABS API Patterns](../../docs/research/etabs-api-patterns.md) - API reference

---

## 🔄 Integration with Current Work

These patterns should be integrated into:
- `mod_Export.bas` - Frame forces extraction
- `mod_Analysis.bas` - Analysis verification
- `mod_Design.bas` - Design results

See the analysis document for specific recommendations.
