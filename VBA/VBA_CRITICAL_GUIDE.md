# VBA ETABS Export - Critical Reference Guide

**Purpose:** Single consolidated document for ETABS VBA development  
**Priority:** HIGH - Essential patterns for production code  
**Last Updated:** From legacy code analysis + current development

---

## 📁 Recommended Module Structure

**Current:** 10 .bas files (too fragmented)  
**Recommended:** 2-3 .bas files

| Module | Purpose | Content |
|--------|---------|---------|
| **mod_ETABS_Core.bas** | Main + Connection + Essential Functions | Entry point, connect, export, utils |
| **mod_ETABS_Results.bas** | All result extraction | Frame forces, design results, reactions |
| **(Optional) mod_ETABS_Config.bas** | Configuration only | Types, constants (if needed) |

**Why fewer modules:**
- Easier to import/maintain in Excel VBA
- Less file management
- Your legacy code worked with single-purpose files - simpler is better

---

## 🔌 Connection Pattern (CRITICAL)

### ✅ Recommended (from your legacy code)
```vb
' Early binding - requires ETABS reference but MORE RELIABLE
Dim myHelper As ETABSv1.cHelper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Set myHelper = New ETABSv1.Helper
Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
Set mySapModel = myETABSObject.SapModel
```

### Alternative (current approach - works but less IntelliSense)
```vb
' Late binding - no reference needed but error-prone
Dim helper As Object
Dim etabs As Object
Dim sapModel As Object

Set helper = CreateObject("ETABSv1.Helper")
Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
Set sapModel = etabs.SapModel
```

---

## 📊 Data Handling Strategy (FROM YOUR LEGACY - SMART!)

### Your Pattern: Keep data in VBA, write only what's needed

```vb
' ✅ GOOD - Your approach: Store in arrays, process in VBA
Dim AllFrameData() As Variant  ' Store all frame data
Dim FilteredResults() As Variant  ' Only what we need

' Get all data once
ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, ...)

' Process in VBA - fast, no Excel overhead
For i = LBound(MyName) To UBound(MyName)
    ' Filter, calculate, transform in VBA
    If Frame_Type = 1 Then  ' Only columns
        ' Add to FilteredResults
    End If
Next

' Write ONLY filtered results to Excel - fast, light
Range("A2").Resize(ResultCount, ColCount).Value = FilteredResults
```

```vb
' ❌ SLOW - Writing each row to Excel
For i = 1 To 10000
    Cells(i, 1).Value = data(i)  ' 10,000 Excel calls = SLOW
Next

' ✅ FAST - Array to range (one call)
Cells(1, 1).Resize(10000, 1).Value = data  ' 1 Excel call = FAST
```

---

## 🚀 Efficient API Patterns

### Get ALL Frames at Once (Your COLUMNS.bas pattern)
```vb
' ✅ EFFICIENT - One API call, all data
ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
    PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
    Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)

' Already have: name, section, story, coordinates
' No need for separate GetFrameStory() calls!
```

### Before Getting Results - ALWAYS
```vb
' ✅ REQUIRED - Deselect all first, then select what you need
ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("Dead")
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("Live")
```

### Check Design Before Getting Results
```vb
' ✅ CHECK - Avoid errors
If Not mySapModel.DesignConcrete.GetResultsAvailable Then
    ret = mySapModel.DesignConcrete.StartDesign()
End If
```

---

## 📋 Essential API Calls

### Frame Forces
```vb
ret = sapModel.Results.FrameForce(FrameName, 0, NumberResults, _
    Obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
    P, V2, V3, T, M2, M3)
' P=axial, V2/V3=shear, T=torsion, M2/M3=moment
```

### Base Reactions
```vb
ret = sapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, _
    Fx, Fy, Fz, Mx, My, Mz, gx, gy, gz)
```

### Column Design Results
```vb
ret = sapModel.DesignConcrete.GetSummaryResultsColumn(FrameName, NumberItems, _
    FrameName, MyOption, Location, _
    PMMCombo, PMMArea, PMMRatio, _
    VmajorCombo, AVmajor, VminorCombo, AVminor, _
    ErrorSummary, WarningSummary, 0)
```

### Beam Design Results
```vb
ret = sapModel.DesignConcrete.GetSummaryResultsBeam_2(Name, NumberItems, _
    FrameName, Location, _
    TopCombo, TopArea, TopAreaReq, TopAreaMin, TopAreaProvided, _
    BotCombo, BotArea, BotAreaReq, BotAreaMin, BotAreaProvided, _
    VmajorCombo, VmajorArea, VmajorAreaReq, VmajorAreaMin, VmajorAreaProvided, _
    TLCombo, TLArea, TTCombo, TTArea, _
    ErrorSummary, WarningSummary, 0)
```

### Joint Displacements
```vb
ret = sapModel.Results.JointDispl(PointName, 0, NumberResults, _
    Obj, Elm, LoadCase, StepType, StepNum, _
    U1, U2, U3, R1, R2, R3)
```

### Identify Frame Type
```vb
ret = sapModel.PropFrame.GetTypeRebar(PropName, Frame_Type)
' 1 = Column, 2 = Beam, Other = None
```

---

## ⚡ Performance Tips (From Your Experience)

### 1. Screen Updates OFF
```vb
Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
' ... do work ...
Application.Calculation = xlCalculationAutomatic
Application.ScreenUpdating = True
```

### 2. Status Bar for Long Operations
```vb
If i Mod 100 = 0 Then
    Application.StatusBar = "Processing: " & i & "/" & total
    DoEvents  ' Allow Excel to respond
End If
```

### 3. Error Handling Pattern
```vb
On Error GoTo ErrorHandler
' ... code ...
Exit Sub

ErrorHandler:
    MsgBox "Error: " & Err.Description
    ' Cleanup
End Sub
```

### 4. Avoid Repeated Sheet Access
```vb
' ❌ SLOW
For i = 1 To 1000
    Worksheets("Data").Cells(i, 1).Value = x
Next

' ✅ FAST - Get reference once
Dim ws As Worksheet
Set ws = Worksheets("Data")
For i = 1 To 1000
    ws.Cells(i, 1).Value = x  ' Still slow - use array instead
Next
```

---

## 🔧 Common Fixes

### "Automation Error"
- **Cause:** ETABS not running or model not loaded
- **Fix:** Ensure ETABS is open with a model before running

### "Object Required" 
- **Cause:** Connection failed silently
- **Fix:** Always check `If sapModel Is Nothing Then Exit`

### "Subscript Out of Range"
- **Cause:** Array not populated (API returned 0 items)
- **Fix:** Check `NumberResults > 0` before accessing arrays

### "No Results Available"
- **Cause:** Analysis not run or design not run
- **Fix:** 
```vb
' Check if analysis complete
ret = sapModel.Analyze.GetCaseStatus(caseName, status)
If status <> 4 Then  ' 4 = Complete
    ret = sapModel.Analyze.RunAnalysis()
End If
```

---

## 📝 Code Template

### Minimal Working Export
```vb
Option Explicit

Public Sub ExportToCSV()
    On Error GoTo ErrorHandler
    
    ' Connect
    Dim helper As Object, etabs As Object, sapModel As Object
    Set helper = CreateObject("ETABSv1.Helper")
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    
    If etabs Is Nothing Then
        MsgBox "Start ETABS first!"
        Exit Sub
    End If
    
    Set sapModel = etabs.SapModel
    
    ' Verify model
    If Len(sapModel.GetModelFilename) = 0 Then
        MsgBox "Open a model in ETABS first!"
        Exit Sub
    End If
    
    ' Get frames
    Dim NumberNames As Long
    Dim MyName() As String, PropName() As String, StoryName() As String
    ' ... other arrays for GetAllFrames
    
    Dim ret As Long
    ret = sapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
        PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
        Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
    
    If ret <> 0 Or NumberNames = 0 Then
        MsgBox "No frames found"
        Exit Sub
    End If
    
    ' Build results array (only what we need)
    Dim results() As Variant
    ReDim results(1 To NumberNames, 1 To 3)  ' Story, Name, Section
    
    Dim i As Long
    For i = LBound(MyName) To UBound(MyName)
        results(i + 1, 1) = StoryName(i)
        results(i + 1, 2) = MyName(i)
        results(i + 1, 3) = PropName(i)
    Next
    
    ' Write to sheet in ONE call
    Application.ScreenUpdating = False
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Data")
    ws.Range("A1").Resize(1, 3).Value = Array("Story", "Name", "Section")
    ws.Range("A2").Resize(NumberNames, 3).Value = results
    Application.ScreenUpdating = True
    
    MsgBox "Exported " & NumberNames & " frames!"
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description
End Sub
```

---

## 📚 Reference Files

| File | Location | Use For |
|------|----------|---------|
| Legacy COLUMNS.bas | VBA/Legacy_2019_2021/ | Complete column workflow |
| Legacy BASE_REACTIONS.bas | VBA/Legacy_2019_2021/ | Base reactions pattern |
| Legacy BeamType.bas | VBA/Legacy_2019_2021/ | Beam classification |
| API Quick Reference | docs/research/etabs-api-quick-reference.md | API syntax |
| Integration Guide | docs/research/integration-recommendations.md | What to add next |

---

## ✅ Quick Checklist Before Running

- [ ] ETABS is open
- [ ] Model is loaded (not blank screen)
- [ ] Analysis has been run (F5 in ETABS)
- [ ] For design results: Design has been run
- [ ] Excel VBA is ready (enable macros)
