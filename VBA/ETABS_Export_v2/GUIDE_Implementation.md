**Type:** Guide
**Audience:** All Agents, Developers
**Status:** Production Ready
**Importance:** Critical
**Created:** 2026-01-17
**Related Tasks:** ETABS Export, VBA Development

# ETABS VBA Export - Complete Implementation Guide

## Quick Reference Card

### Pre-Flight Checklist (Before ANY VBA Development)
```
□ ETABS API v1 reference added (Tools → References → ETABS.exe)
□ Model is open in ETABS
□ Analysis has been run (results available)
□ Output folder exists: %USERPROFILE%\Documents\ETABS_Export
```

### Essential Code Patterns (MUST USE)

**1. Connection Pattern:**
```vba
' ✅ CORRECT: Early binding with type library
Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI  
Dim mySapModel As ETABSv1.cSapModel

Sub Connect()
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
End Sub

' ❌ WRONG: Late binding (causes Error #430)
Dim sapModel As Object  ' This will fail on FrameObj methods!
```

**2. Case Selection Pattern:**
```vba
' ✅ CORRECT: Explicitly SELECT all cases
Dim NumberCases As Long, CaseName() As String
ret = mySapModel.LoadCases.GetNameList(NumberCases, CaseName)
For c = 0 To NumberCases - 1
    ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(c))
Next c

' ❌ WRONG: DeselectAll (returns error in current ETABS versions)
ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
' This returns ret=1 (error) and gives 0 results!
```

**3. Unit Setting Pattern:**
```vba
' ✅ CORRECT: Set units FIRST before any API calls
ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)  ' kN, meters, Celsius

' Then get results (will be in kN·m, kN, etc.)
```

**4. Error Handling Pattern:**
```vba
' ✅ CORRECT: Check return codes
ret = mySapModel.Results.FrameForce(...)
If ret <> 0 Then
    Debug.Print "ERROR: FrameForce failed with ret=" & ret
    Exit Sub
End If

' Also check array results
If NumberResults = 0 Then
    Debug.Print "WARNING: No results returned"
End If
```

---

## Common Errors & Solutions

### Error #430: "Class does not support Automation"

**Symptom:**
- `FrameObj.GetNameList()` fails
- `FrameObj.GetAllFrames()` fails  
- Any FrameObj method returns error

**Cause:** Late binding (declaring as `Object`) instead of early binding

**Solution:**
1. Open Excel VBA Editor
2. Tools → References
3. Browse to `C:\Program Files\Computers and Structures\ETABS XX\ETABS.exe`
4. Check "ETABS Object Library"
5. Change declarations from `As Object` to `As ETABSv1.cSapModel`

**Verification:**
```vba
Sub TestReference()
    Dim mySapModel As ETABSv1.cSapModel  ' If this compiles, reference is OK
    MsgBox "Reference is working!"
End Sub
```

---

### Empty Results (0 records returned)

**Symptom:**
- `Results.FrameForce()` returns `NumberResults = 0`
- CSV file is empty or header-only

**Cause:** No load cases/combos selected for output

**Solution:** Explicitly select ALL cases before calling Results methods:
```vba
' Select all load cases
Dim NumberCases As Long, CaseName() As String
ret = mySapModel.LoadCases.GetNameList(NumberCases, CaseName)
For c = 0 To NumberCases - 1
    ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(c))
Next c

' Select all combos
Dim NumberCombos As Long, ComboName() As String
ret = mySapModel.RespCombo.GetNameList(NumberCombos, ComboName)
For c = 0 To NumberCombos - 1
    ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ComboName(c))
Next c

' NOW call Results.FrameForce - it will return data
```

**Verification:**
```vba
Sub TestCaseSelection()
    ' After selecting cases, test one frame
    Dim NumberResults As Long
    ret = mySapModel.Results.FrameForce(frameName, eItemTypeElm_ObjectElm, ...)
    Debug.Print "Results: " & NumberResults  ' Should be > 0
End Sub
```

---

### Unknown Length Unit: 6

**Symptom:** Unit detection returns "Unknown length unit: 6"

**Cause:** GetPresentUnits_2 returns 6 for meters (not documented everywhere)

**Solution:** Handle all unit enums including 6:
```vba
Select Case lengthUnit
    Case 1: unitName = "in"
    Case 2: unitName = "ft"
    Case 3: unitName = "micron"
    Case 4: unitName = "mm"
    Case 5: unitName = "cm"
    Case 6: unitName = "m"    ' ← ADD THIS!
    Case Else: unitName = "unknown"
End Select
```

---

## API Reference Quick Cards

### Frame Object Methods
```vba
' Get all frame names
ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)

' Get section assigned to frame
ret = mySapModel.FrameObj.GetSection(frameName, sectName, SAuto)

' Get frame endpoints  
ret = mySapModel.FrameObj.GetPoints(frameName, Point1, Point2)
```

### Results Methods
```vba
' Get frame forces (M, V, P, T)
ret = mySapModel.Results.FrameForce( _
    Name,           ' Frame name or element
    ItemTypeElm,    ' 0=ObjectElm, 1=Element, 2=GroupElm, 3=SelectionElm
    NumberResults,  ' Output: count of results
    Obj, ObjSta, Elm, ElmSta,  ' Output: object/element stations
    LoadCase, StepType, StepNum,  ' Output: load case info
    P, V2, V3, T, M2, M3)  ' Output: forces and moments

' Set which cases to output
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName)
ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ComboName)
```

### Section Properties
```vba
' Get rectangular section dimensions
ret = mySapModel.PropFrame.GetRectangle(sectName, fileName, matProp, _
    t3, t2, color, notes, guid)  ' t3=depth, t2=width

' Get I-section dimensions
ret = mySapModel.PropFrame.GetISection(sectName, fileName, matProp, _
    d, bf, tf, tw, ...)  ' d=depth, bf=flange width, etc.
```

### Point/Coordinate Methods
```vba
' Get point coordinates
ret = mySapModel.PointObj.GetCoordCartesian(pointName, x, y, z)

' Get label and story from point
ret = mySapModel.PointObj.GetLabelFromName(pointName, label, story)
```

---

## Testing Checklist

Before committing any VBA export code, verify:

### 1. Connection Test
```vba
Sub Test_Connection()
    On Error GoTo Fail
    Call Connect
    Debug.Print "Model: " & mySapModel.GetModelFilename
    MsgBox "✓ Connection OK"
    Exit Sub
Fail:
    MsgBox "✗ Connection FAILED: " & Err.Description
End Sub
```

### 2. Case Selection Test
```vba
Sub Test_CaseSelection()
    Call Connect
    
    ' Select one case
    ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
    
    ' Test if it works
    Dim NumberResults As Long
    ret = mySapModel.Results.FrameForce("1", eItemTypeElm_ObjectElm, NumberResults, ...)
    
    If NumberResults > 0 Then
        MsgBox "✓ Case selection works: " & NumberResults & " results"
    Else
        MsgBox "✗ No results returned"
    End If
End Sub
```

### 3. Small Export Test (10 frames)
```vba
Sub Test_SmallExport()
    ' Export only first 10 frames to verify format
    ' Check: columns correct, units correct, data not empty
End Sub
```

### 4. Full Export Test
```vba
Sub Test_FullExport()
    ' Export all frames
    ' Check: row count reasonable, file size reasonable
End Sub
```

---

## Debugging Steps

When export fails, run these diagnostics in order:

**Step 1: Check connection**
```vba
Debug.Print mySapModel.GetModelFilename  ' Should print path
```

**Step 2: Check results available**
```vba
Dim available As Boolean
ret = mySapModel.Results.Setup.GetResultsAvailable(available)
Debug.Print "Results available: " & available  ' Should be True
```

**Step 3: Check frame count**
```vba
Dim NumberNames As Long, MyName() As String
ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
Debug.Print "Frames: " & NumberNames  ' Should be > 0
```

**Step 4: Check case selection**
```vba
' Select one case and test
ret = mySapModel.Results.Setup.SetCaseSelectedForOutput("DEAD")
Debug.Print "SetCase ret: " & ret  ' Should be 0

' Test frame force
ret = mySapModel.Results.FrameForce(MyName(0), 0, NumberResults, ...)
Debug.Print "FrameForce ret: " & ret  ' Should be 0
Debug.Print "NumberResults: " & NumberResults  ' Should be > 0
```

**Step 5: Check one result value**
```vba
If NumberResults > 0 Then
    Debug.Print "First M3: " & M3(0)  ' Should be a number
End If
```

---

## File Organization

### Production Files (VBA/ETABS_Export_v2/)
```
ETABS_Export_Production.bas    - Main export functions
ETABS_Export_Config.bas        - User-configurable settings
ETABS_Export_Properties.bas    - Section/material export
README.md                      - Usage guide
```

### Archive Files (VBA/ETABS_Export_v2/_archive/)
```
session31_trials/       - Failed attempts and iterations
session31_diagnostics/  - Debug modules (keep for future debugging)
session31_solutions/    - Intermediate solutions
README.md              - Archive documentation
```

---

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| v2.1 | 2026-01-17 | Initial with unit/case issues | Failed |
| v2.2 | 2026-01-17 | Added Case 6, SetPresentUnits | Connection error |
| v2.3 | 2026-01-17 | Fixed connection, removed case enum | Error #430 |
| v2.4 | 2026-01-17 | Added type library reference | Empty CSV |
| v2.5 | 2026-01-17 | Fixed case selection (SELECT all) | ✅ 364K rows |
| v3.0 | 2026-01-17 | Production with filtering | In progress |

---

## Quick Copy-Paste Templates

### Template: Basic Export Function
```vba
Sub ExportToCSV()
    On Error GoTo ErrorHandler
    
    ' 1. Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    ' 2. Set units
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    ' 3. Select all cases
    Dim NumberCases As Long, CaseName() As String
    ret = mySapModel.LoadCases.GetNameList(NumberCases, CaseName)
    For c = 0 To NumberCases - 1
        ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(c))
    Next c
    
    ' 4. Get frames
    Dim NumberNames As Long, MyName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    ' 5. Open file and write header
    Dim f As Integer: f = FreeFile
    Open outputPath For Output As #f
    Print #f, "Column1,Column2,Column3"
    
    ' 6. Loop and export
    For i = 0 To NumberNames - 1
        ' Get data and write...
    Next i
    
    ' 7. Close
    Close #f
    MsgBox "Done! " & outputPath
    Exit Sub

ErrorHandler:
    Close #f
    MsgBox "Error: " & Err.Description
End Sub
```

---

**Document Status:** Complete - Ready for use
**Last Updated:** 2026-01-17
**Validated By:** Successfully exported 364,365 rows
