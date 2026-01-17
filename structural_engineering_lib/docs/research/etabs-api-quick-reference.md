# ETABS API Quick Reference (From Legacy Code)

**Source:** Working VBA code from 2019-2021  
**Purpose:** Quick reference for ETABS API patterns

---

## Connection Pattern

```vb
' Early Binding (Recommended - requires ETABSv1 reference)
Dim myHelper As ETABSv1.cHelper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Set myHelper = New ETABSv1.Helper
Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
Set mySapModel = myETABSObject.SapModel
```

---

## Analysis & Design

### Run Analysis
```vb
ret = mySapModel.Analyze.CreateAnalysisModel
If ret = 0 Then ret = mySapModel.Analyze.RunAnalysis
```

### Check/Run Design
```vb
ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
```

---

## Frame Data

### Get ALL Frames (Efficient!)
```vb
ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
    PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
    Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
```

### Identify Beam vs Column
```vb
ret = mySapModel.PropFrame.GetTypeRebar(PropName, Frame_Type)
' Frame_Type: 1 = Column, 2 = Beam, Other = None
```

### Get Section Properties
```vb
ret = mySapModel.PropFrame.GetRectangle(PropName, FileName, MatProp, t3, t2, Color, Notes, GUID)
' t3 = depth, t2 = width (in model units)
```

### Label ↔ Name Conversion
```vb
ret = mySapModel.FrameObj.GetLabelFromName(InternalName, Label, Story)
ret = mySapModel.FrameObj.GetNameFromLabel(Label, Story, InternalName)
```

---

## Design Results

### Column Design Results
```vb
ret = mySapModel.DesignConcrete.GetSummaryResultsColumn(FrameName, NumberItems, _
    FrameName, MyOption, Location, _
    PMMCombo, PMMArea, PMMRatio, _      ' P-M-M interaction
    VmajorCombo, AVmajor, _              ' Major shear
    VminorCombo, AVminor, _              ' Minor shear
    ErrorSummary, WarningSummary, eItemType_Objects)
```

### Beam Design Results
```vb
ret = mySapModel.DesignConcrete.GetSummaryResultsBeam_2(Name, NumberItems, _
    FrameName, Location, _
    TopCombo, TopArea, TopAreaReq, TopAreaMin, TopAreaProvided, _
    BotCombo, BotArea, BotAreaReq, BotAreaMin, BotAreaProvided, _
    VmajorCombo, VmajorArea, VmajorAreaReq, VmajorAreaMin, VmajorAreaProvided, _
    TLCombo, TLArea, TTCombo, TTArea, _
    ErrorSummary, WarningSummary, eItemType_Objects)
```

### Pier/Wall Design Results
```vb
ret = mySapModel.DesignShearWall.GetPierSummaryResults(Story, PierLabel, Station, _
    DesignType, PierSecType, EdgeBar, EndBar, BarSpacing, ReinfPercent, CurrPercent, _
    DCRatio, PierLeg, LegX1, LegY1, LegX2, LegY2, EdgeLeft, EdgeRight, AsLeft, AsRight, _
    ShearAv, StressCompLeft, StressCompRight, StressLimitLeft, StressLimitRight, _
    CDepthLeft, CLimitLeft, CDepthRight, CLimitRight, InelasticRotDemand, _
    InelasticRotCapacity, NormCompStress, NormCompStressLimit, CDepth, _
    BZoneL, BZoneR, BZoneLength, WarnMsg, ErrMsg)
```

---

## Analysis Results

### Output Selection
```vb
' Always deselect all first
ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

' Then select specific case or combo
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("Ex")
ret = mySapModel.Results.Setup.SetComboSelectedForOutput("COMB1")
```

### Base Reactions
```vb
ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, _
    Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
' Returns arrays: Fx(), Fy(), Fz() - forces; Mx(), My(), Mz() - moments
' gx, gy, gz - center of rigidity
```

### Joint Displacements
```vb
ret = mySapModel.Results.JointDispl(PointName, eItemTypeElm_Element, NumberResults, _
    Obj, Elm, LoadCase, StepType, StepNum, _
    U1, U2, U3, R1, R2, R3)
' U1, U2, U3 - translations; R1, R2, R3 - rotations
```

---

## Load Combinations

### Get List
```vb
ret = mySapModel.RespCombo.GetNameList(NumberNames, MyName)
```

### Get Combo Contents
```vb
ret = mySapModel.RespCombo.GetCaseList(ComboName, NumberItems, CNameType, CName, SF)
' CNameType: 0 = LoadCase, 1 = LoadCombo
' SF() = Scale factors
```

### Get Combo Type
```vb
ret = mySapModel.RespCombo.GetTypeCombo(ComboName, ComboType)
' 0=Linear Additive, 1=Envelope, 2=Absolute Additive, 3=SRSS, 4=Range Additive
```

### Modify Combo
```vb
ret = mySapModel.RespCombo.Delete(ComboName)
ret = mySapModel.RespCombo.Add(ComboName, ComboType)
ret = mySapModel.RespCombo.SetCaseList(ComboName, eCNameType_LoadCase, CaseName, SF)
```

---

## Story & Model Info

### Get Stories
```vb
ret = mySapModel.Story.GetNameList(NumberNames, MyName)
ret = mySapModel.Story.GetHeight(StoryName, Height)
```

### Get Model Filename
```vb
ModelName = mySapModel.GetModelFilename(False)  ' False = without path
```

### Set Units
```vb
ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
ret = mySapModel.SetPresentUnits(eUnits_Ton_m_C)
ret = mySapModel.SetPresentUnits(eUnits_kN_cm_C)
```

---

## Model Modification

### Unlock Model
```vb
ret = mySapModel.SetModelIsLocked(False)
```

### Change Section
```vb
ret = mySapModel.FrameObj.SetSection(FrameName, SectionName)
```

### Select Objects
```vb
ret = mySapModel.SelectObj.ClearSelection
ret = mySapModel.FrameObj.SetSelected(FrameName, True)
```

### Refresh View
```vb
ret = mySapModel.View.RefreshView
```

---

## Database Tables (CSV Export)

### Get Available Tables
```vb
ret = mySapModel.DatabaseTables.GetAvailableTables(NumberTables, TableKey, TableName, ImportType)
```

### Export to CSV
```vb
ret = mySapModel.DatabaseTables.GetTableForDisplayCSVFile(TableKey, GroupName, FieldKeyList, _
    TableVersion, FieldKeysIncluded, NumberRecords, CSVFileName)
```

### Show in Excel
```vb
ret = mySapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(ComboList)
ret = mySapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(CaseList)
ret = mySapModel.DatabaseTables.ShowTablesInExcel(TableKeyList, WindowHandle)
```

---

## Common Return Value Check
```vb
' ret = 0 means success
If ret = 0 Then
    ' Success
Else
    ' Failed - check error
End If
```
