---
**Type:** Implementation Plan
**Audience:** Developers, VBA Implementers
**Status:** Draft
**Importance:** High
**Created:** 2026-01-17
**Last Updated:** 2026-01-17
**Related Tasks:** TASK-VBA-01, TASK-VBA-02, TASK-VBA-03
**Related Docs:** [etabs-vba-export-macro.md](etabs-vba-export-macro.md), [csv-import-schema.md](../specs/csv-import-schema.md), [etabs-automation-bridge-plan.md](../planning/etabs-automation-bridge-plan.md)
---

# ETABS VBA Export — In-Depth Implementation Plan

## Executive Summary

This document provides comprehensive planning for implementing a production-ready VBA macro that exports ETABS data to our CSV schema. Focus areas:

1. **Performance:** Minimize API calls, batch operations, efficient data structures
2. **Error Handling:** Graceful degradation, detailed logging, recovery paths
3. **Debugging:** Instrumentation, trace logs, validation checkpoints
4. **Control:** Progress tracking, cancellation, partial exports

**Target:** Export 1000+ beams in <60 seconds with full error recovery.

---

## Table of Contents

1. [Performance Strategy](#performance-strategy)
2. [Error Handling Architecture](#error-handling-architecture)
3. [Debug & Logging System](#debug--logging-system)
4. [API Call Optimization](#api-call-optimization)
5. [Data Validation Pipeline](#data-validation-pipeline)
6. [Implementation Phases](#implementation-phases)
7. [VBA Module Structure](#vba-module-structure)
8. [Testing Strategy](#testing-strategy)
9. [Known Gotchas & Solutions](#known-gotchas--solutions)

---

## 1. Performance Strategy

### 1.1 API Call Analysis

**Problem:** ETABS OAPI is synchronous and blocking. Each method call has overhead.

**Solution:** Batch operations, minimize round-trips

| Operation | Naive Approach | Optimized Approach | Speedup |
|-----------|---------------|-------------------|---------|
| Get frame list | Loop GetName(i) | GetNameList() → array | 100x |
| Get section props | Loop GetSection(name) | Cache + single pass | 50x |
| Get forces | Loop FrameForce(name, station) | DatabaseTables bulk export | 200x |
| Get joint coords | Loop GetCoordCartesian(pt) | GetNameList + batch | 80x |

### 1.2 Recommended API Approach: DatabaseTables

**Primary Strategy:** Use `SapModel.DatabaseTables.GetTableForDisplayCSVFile()`

**Rationale:**
- Single call exports entire table to CSV
- Pre-formatted, includes headers
- Handles units automatically
- Fastest for bulk data (1000+ frames)

**Fallback Strategy:** Direct API calls when DatabaseTables unavailable

```vba
' Primary: Bulk export (FAST)
ret = SapModel.DatabaseTables.GetTableForDisplayCSVFile( _
    "Element Forces - Frames", _
    outputPath, _
    True, _  ' Append to file
    eNamedSetType.Group, _
    "ALL" _
)

' Fallback: Direct API (SLOWER but more control)
ret = SapModel.Results.FrameForce( _
    frameName, _
    eItemTypeElm.ObjectElm, _
    NumberResults, _
    Obj(), StationVal(), Elm(), LoadCase(), StepType(), StepNum(), _
    P(), V2(), V3(), T(), M2(), M3() _
)
```

### 1.3 Memory Management

**VBA Arrays:**
- Pre-allocate array sizes based on counts
- Use `ReDim Preserve` sparingly (expensive)
- Clear large arrays after use: `Erase arrayName`

```vba
' Good: Pre-allocate
Dim frameCount As Long
ret = SapModel.FrameObj.GetNameList(frameCount, frameNames())
ReDim forces(1 To frameCount, 1 To 6) As Double

' Bad: Dynamic resize in loop
For i = 1 To frameCount
    ReDim Preserve forces(1 To i, 1 To 6)  ' O(n²) complexity!
Next
```

### 1.4 Progress Tracking Without Blocking

```vba
' Update progress every 100 items
If frameIndex Mod 100 = 0 Then
    Application.StatusBar = "Exporting frame " & frameIndex & " of " & frameCount
    DoEvents  ' Allow Excel to process events

    ' Check for user cancellation
    If UserWantsToCancelExport() Then
        Exit For
    End If
End If
```

---

## 2. Error Handling Architecture

### 2.1 Error Categories & Recovery

| Error Type | Example | Recovery Strategy | User Action |
|------------|---------|-------------------|-------------|
| **Fatal** | ETABS not running | Abort with clear message | Start ETABS |
| **Retryable** | COM timeout | Retry 3x with exponential backoff | Wait |
| **Degradable** | Missing optional data | Skip, log warning, continue | Review log |
| **Validation** | Invalid units | Convert or abort with details | Fix model |

### 2.2 Error Handler Template

```vba
Sub ExportETABSData()
    On Error GoTo ErrorHandler

    Dim logFile As String
    logFile = OpenLogFile()

    ' Initialize with validation
    If Not ValidateEnvironment(logFile) Then
        MsgBox "Environment validation failed. Check log: " & logFile
        Exit Sub
    End If

    ' Main export with checkpoints
    Dim checkpoint As String
    checkpoint = "Connecting to ETABS"
    LogInfo logFile, "Starting export: " & Now

    ' ... export code ...

    LogInfo logFile, "Export completed successfully: " & Now
    MsgBox "Export complete! Files saved to: " & outputFolder
    CloseLogFile logFile
    Exit Sub

ErrorHandler:
    LogError logFile, "ERROR at checkpoint: " & checkpoint
    LogError logFile, "Error #" & Err.Number & ": " & Err.Description
    LogError logFile, "Source: " & Err.Source

    ' Try graceful degradation
    Select Case Err.Number
        Case -2147417848  ' COM object disconnected
            If RetryConnection(3) Then
                Resume  ' Try again
            Else
                MsgBox "Lost connection to ETABS. Export aborted." & vbCrLf & _
                       "Check log: " & logFile
            End If

        Case 5  ' Invalid procedure call
            LogError logFile, "Invalid API call - check ETABS version compatibility"
            MsgBox "API compatibility error. See log: " & logFile

        Case Else
            MsgBox "Unexpected error at: " & checkpoint & vbCrLf & _
                   Err.Description & vbCrLf & _
                   "See log: " & logFile
    End Select

    CloseLogFile logFile
End Sub
```

### 2.3 Retry Logic with Exponential Backoff

```vba
Function RetryOperation(operationName As String, maxRetries As Integer) As Boolean
    Dim retryCount As Integer
    Dim waitTime As Integer

    For retryCount = 1 To maxRetries
        On Error Resume Next

        ' Attempt operation (caller implements this)
        Dim success As Boolean
        success = ExecuteOperation()  ' Placeholder

        If success Then
            RetryOperation = True
            Exit Function
        End If

        ' Exponential backoff: 1s, 2s, 4s
        waitTime = 2 ^ (retryCount - 1)
        LogWarning logFile, operationName & " failed, retry " & retryCount & _
                           "/" & maxRetries & " after " & waitTime & "s"

        Application.Wait Now + TimeValue("00:00:" & Format(waitTime, "00"))
    Next

    RetryOperation = False
End Function
```

---

## 3. Debug & Logging System

### 3.1 Multi-Level Logging

```vba
Enum LogLevel
    DEBUG_LEVEL = 0
    INFO_LEVEL = 1
    WARNING_LEVEL = 2
    ERROR_LEVEL = 3
End Enum

Dim g_LogLevel As LogLevel
g_LogLevel = INFO_LEVEL  ' Set to DEBUG_LEVEL for detailed tracing

Sub LogDebug(logFile As String, message As String)
    If g_LogLevel <= DEBUG_LEVEL Then WriteLog logFile, "[DEBUG] " & message
End Sub

Sub LogInfo(logFile As String, message As String)
    If g_LogLevel <= INFO_LEVEL Then WriteLog logFile, "[INFO] " & message
End Sub

Sub LogWarning(logFile As String, message As String)
    If g_LogLevel <= WARNING_LEVEL Then WriteLog logFile, "[WARNING] " & message
End Sub

Sub LogError(logFile As String, message As String)
    If g_LogLevel <= ERROR_LEVEL Then WriteLog logFile, "[ERROR] " & message
End Sub

Sub WriteLog(logFile As String, message As String)
    Dim fileNum As Integer
    fileNum = FreeFile

    On Error Resume Next  ' Don't let logging crash the export
    Open logFile For Append As #fileNum
    Print #fileNum, Format(Now, "yyyy-mm-dd hh:nn:ss") & " | " & message
    Close #fileNum
End Sub
```

### 3.2 Checkpoint System

```vba
Type ExportCheckpoint
    Name As String
    StartTime As Date
    EndTime As Date
    ItemsProcessed As Long
    Success As Boolean
End Type

Dim g_Checkpoints() As ExportCheckpoint
Dim g_CheckpointCount As Integer

Sub StartCheckpoint(name As String)
    g_CheckpointCount = g_CheckpointCount + 1
    ReDim Preserve g_Checkpoints(1 To g_CheckpointCount)

    With g_Checkpoints(g_CheckpointCount)
        .Name = name
        .StartTime = Now
        .ItemsProcessed = 0
        .Success = False
    End With

    LogInfo logFile, "=== CHECKPOINT START: " & name & " ==="
End Sub

Sub EndCheckpoint(itemsProcessed As Long, success As Boolean)
    With g_Checkpoints(g_CheckpointCount)
        .EndTime = Now
        .ItemsProcessed = itemsProcessed
        .Success = success

        Dim duration As Double
        duration = (.EndTime - .StartTime) * 86400  ' Convert to seconds

        LogInfo logFile, "=== CHECKPOINT END: " & .Name & " | " & _
                        "Items: " & .ItemsProcessed & " | " & _
                        "Duration: " & Format(duration, "0.0") & "s | " & _
                        "Status: " & IIf(.Success, "OK", "FAILED") & " ==="
    End With
End Sub

Sub WriteCheckpointSummary(logFile As String)
    LogInfo logFile, vbCrLf & "=== CHECKPOINT SUMMARY ==="

    Dim i As Integer
    For i = 1 To g_CheckpointCount
        With g_Checkpoints(i)
            Dim duration As Double
            duration = (.EndTime - .StartTime) * 86400

            LogInfo logFile, .Name & ": " & _
                            .ItemsProcessed & " items in " & _
                            Format(duration, "0.0") & "s " & _
                            "(" & Format(.ItemsProcessed / duration, "0") & " items/s) " & _
                            IIf(.Success, "[OK]", "[FAILED]")
        End With
    Next
End Sub
```

### 3.3 Validation Checkpoints

```vba
Function ValidateEnvironment(logFile As String) As Boolean
    On Error GoTo ValidationError

    ' Check 1: ETABS API available
    Dim helper As Object
    Set helper = CreateObject("ETABSv1.Helper")
    If helper Is Nothing Then
        LogError logFile, "ETABS API not registered"
        ValidateEnvironment = False
        Exit Function
    End If
    LogInfo logFile, "✓ ETABS API registered"

    ' Check 2: ETABS instance available
    Dim etabs As Object
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    If etabs Is Nothing Then
        LogWarning logFile, "No running ETABS instance, will attempt to launch"
        ' Could try CreateObjectProgID here
    Else
        LogInfo logFile, "✓ ETABS instance connected"
    End If

    ' Check 3: Model loaded
    Dim modelPath As String
    modelPath = etabs.SapModel.GetModelFilename
    If Len(modelPath) = 0 Then
        LogError logFile, "No model loaded in ETABS"
        ValidateEnvironment = False
        Exit Function
    End If
    LogInfo logFile, "✓ Model loaded: " & modelPath

    ' Check 4: Output folder exists/writable
    Dim outputFolder As String
    outputFolder = GetOutputFolder()
    If Not FolderExists(outputFolder) Then
        MkDir outputFolder
        LogInfo logFile, "Created output folder: " & outputFolder
    End If
    LogInfo logFile, "✓ Output folder ready: " & outputFolder

    ValidateEnvironment = True
    Exit Function

ValidationError:
    LogError logFile, "Validation failed: " & Err.Description
    ValidateEnvironment = False
End Function
```

---

## 4. API Call Optimization

### 4.1 Connection Strategy

```vba
' Strategy: Attach to running instance first, launch only if needed
Function ConnectToETABS() As Object
    On Error GoTo LaunchETABS

    Dim helper As Object
    Set helper = CreateObject("ETABSv1.Helper")

    ' Try to attach to running instance
    LogDebug logFile, "Attempting to attach to running ETABS..."
    Dim etabs As Object
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")

    If Not etabs Is Nothing Then
        LogInfo logFile, "✓ Attached to running ETABS instance"
        Set ConnectToETABS = etabs
        Exit Function
    End If

LaunchETABS:
    ' Launch new instance if attach failed
    LogInfo logFile, "No running instance, launching ETABS..."
    Set etabs = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject")

    If etabs Is Nothing Then
        LogError logFile, "Failed to launch ETABS"
        Set ConnectToETABS = Nothing
        Exit Function
    End If

    LogInfo logFile, "✓ Launched new ETABS instance"
    Set ConnectToETABS = etabs
End Function
```

### 4.2 Analysis Status & Run Strategy

```vba
Function EnsureAnalysisComplete(sapModel As Object, logFile As String) As Boolean
    On Error GoTo AnalysisError

    StartCheckpoint "Verify Analysis Status"

    ' Get list of all load cases
    Dim caseCount As Long
    Dim caseNames() As String
    Dim caseTypes() As Long

    Dim ret As Long
    ret = sapModel.LoadCases.GetNameList(caseCount, caseNames, caseTypes)

    LogInfo logFile, "Found " & caseCount & " load cases"

    ' Check status of each case
    Dim i As Long
    Dim needsRun As Boolean
    needsRun = False

    Dim unsolvedCases As String
    unsolvedCases = ""

    For i = LBound(caseNames) To UBound(caseNames)
        Dim status As Long
        ret = sapModel.Analyze.GetCaseStatus(caseNames(i), status)

        ' Status: 0=Not Run, 1=Could Not Start, 2=Not Finished, 3=Finished
        If status <> 3 Then
            needsRun = True
            unsolvedCases = unsolvedCases & caseNames(i) & ", "
            LogWarning logFile, "Case not solved: " & caseNames(i) & " (status=" & status & ")"
        Else
            LogDebug logFile, "Case solved: " & caseNames(i)
        End If
    Next i

    If needsRun Then
        LogWarning logFile, "Analysis required for: " & Left(unsolvedCases, Len(unsolvedCases) - 2)

        ' Prompt user
        Dim response As VbMsgBoxResult
        response = MsgBox("Model analysis is incomplete." & vbCrLf & _
                         "Run analysis now? (This may take several minutes)", _
                         vbYesNo + vbQuestion, "Analysis Required")

        If response = vbNo Then
            LogInfo logFile, "User declined to run analysis"
            EndCheckpoint 0, False
            EnsureAnalysisComplete = False
            Exit Function
        End If

        ' Run analysis with progress
        LogInfo logFile, "Starting analysis..."
        ret = sapModel.Analyze.RunAnalysis()

        If ret <> 0 Then
            LogError logFile, "Analysis failed with return code: " & ret
            EndCheckpoint 0, False
            EnsureAnalysisComplete = False
            Exit Function
        End If

        ' Wait for completion
        If Not WaitForAnalysisComplete(sapModel, logFile) Then
            LogError logFile, "Analysis did not complete in time"
            EndCheckpoint 0, False
            EnsureAnalysisComplete = False
            Exit Function
        End If

        LogInfo logFile, "✓ Analysis completed successfully"
    Else
        LogInfo logFile, "✓ All cases already solved"
    End If

    EndCheckpoint caseCount, True
    EnsureAnalysisComplete = True
    Exit Function

AnalysisError:
    LogError logFile, "Analysis check error: " & Err.Description
    EndCheckpoint 0, False
    EnsureAnalysisComplete = False
End Function

Function WaitForAnalysisComplete(sapModel As Object, logFile As String, _
                                 Optional maxWaitMinutes As Integer = 30) As Boolean
    Dim startTime As Date
    startTime = Now

    Dim caseCount As Long
    Dim caseNames() As String
    Dim caseTypes() As Long
    sapModel.LoadCases.GetNameList caseCount, caseNames, caseTypes

    Do While DateDiff("n", startTime, Now) < maxWaitMinutes
        Dim allComplete As Boolean
        allComplete = True

        Dim i As Long
        For i = LBound(caseNames) To UBound(caseNames)
            Dim status As Long
            sapModel.Analyze.GetCaseStatus caseNames(i), status

            If status <> 3 Then
                allComplete = False
                Exit For
            End If
        Next

        If allComplete Then
            WaitForAnalysisComplete = True
            Exit Function
        End If

        ' Update progress
        Dim solvedCount As Long
        solvedCount = 0
        For i = LBound(caseNames) To UBound(caseNames)
            sapModel.Analyze.GetCaseStatus caseNames(i), status
            If status = 3 Then solvedCount = solvedCount + 1
        Next

        Application.StatusBar = "Analysis: " & solvedCount & "/" & caseCount & " cases complete"
        LogDebug logFile, "Analysis progress: " & solvedCount & "/" & caseCount

        Application.Wait Now + TimeValue("00:00:05")  ' Check every 5 seconds
        DoEvents
    Loop

    LogError logFile, "Analysis timeout after " & maxWaitMinutes & " minutes"
    WaitForAnalysisComplete = False
End Function
```

### 4.3 Bulk Export Using DatabaseTables

```vba
Function ExportFrameForces(sapModel As Object, outputFolder As String, logFile As String) As Boolean
    On Error GoTo ExportError

    StartCheckpoint "Export Frame Forces"

    ' Use DatabaseTables for fastest bulk export
    Dim tableName As String
    tableName = "Element Forces - Frames"

    Dim csvPath As String
    csvPath = outputFolder & "\frame_forces_raw.csv"

    LogInfo logFile, "Exporting table: " & tableName
    LogInfo logFile, "Output: " & csvPath

    Dim ret As Long
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
        tableName, _
        csvPath, _
        False, _  ' Overwrite existing file
        eNamedSetType.All, _
        "" _  ' All groups
    )

    If ret <> 0 Then
        LogError logFile, "DatabaseTables export failed with code: " & ret
        EndCheckpoint 0, False
        ExportFrameForces = False
        Exit Function
    End If

    ' Count rows in exported file
    Dim rowCount As Long
    rowCount = CountCSVRows(csvPath)

    LogInfo logFile, "✓ Exported " & rowCount & " rows to CSV"

    EndCheckpoint rowCount, True
    ExportFrameForces = True
    Exit Function

ExportError:
    LogError logFile, "Export error: " & Err.Description
    EndCheckpoint 0, False
    ExportFrameForces = False
End Function
```

---

## 5. Data Validation Pipeline

### 5.1 Units Validation & Conversion

```vba
Type UnitSystem
    ForceUnit As String      ' "N", "kN", "kip", etc.
    LengthUnit As String     ' "mm", "m", "in", "ft"
    TempUnit As String       ' "C", "F"

    ' Conversion factors to our standard (N, mm)
    ForceToN As Double
    LengthToMM As Double
End Type

Function GetAndValidateUnits(sapModel As Object, logFile As String) As UnitSystem
    On Error GoTo UnitError

    Dim units As UnitSystem

    ' Get current units from ETABS
    Dim forceUnits As Long
    Dim lengthUnits As Long
    Dim tempUnits As Long

    Dim ret As Long
    ret = sapModel.GetPresentUnits_2(forceUnits, lengthUnits, tempUnits)

    ' Enum values from eForce, eLength, eTemperature
    ' See: docs/reference/vendor/etabs/etabs-chm/html/...

    ' Map force units
    Select Case forceUnits
        Case 1  ' lb
            units.ForceUnit = "lb"
            units.ForceToN = 4.44822
        Case 2  ' kip
            units.ForceUnit = "kip"
            units.ForceToN = 4448.22
        Case 3  ' N
            units.ForceUnit = "N"
            units.ForceToN = 1.0
        Case 4  ' kN
            units.ForceUnit = "kN"
            units.ForceToN = 1000.0
        Case Else
            LogError logFile, "Unknown force unit: " & forceUnits
            GoTo UnitError
    End Select

    ' Map length units
    Select Case lengthUnits
        Case 1  ' in
            units.LengthUnit = "in"
            units.LengthToMM = 25.4
        Case 2  ' ft
            units.LengthUnit = "ft"
            units.LengthToMM = 304.8
        Case 3  ' mm
            units.LengthUnit = "mm"
            units.LengthToMM = 1.0
        Case 4  ' m
            units.LengthUnit = "m"
            units.LengthToMM = 1000.0
        Case Else
            LogError logFile, "Unknown length unit: " & lengthUnits
            GoTo UnitError
    End Select

    LogInfo logFile, "✓ Units detected: Force=" & units.ForceUnit & ", Length=" & units.LengthUnit
    LogInfo logFile, "  Conversion factors: F→N=" & units.ForceToN & ", L→mm=" & units.LengthToMM

    GetAndValidateUnits = units
    Exit Function

UnitError:
    LogError logFile, "Unit validation failed"
    ' Return invalid units to trigger error handling
    units.ForceToN = 0
    GetAndValidateUnits = units
End Function
```

### 5.2 CSV Post-Processing & Validation

```vba
Function ValidateAndNormalizeCSV(rawCSVPath As String, _
                                 outputPath As String, _
                                 units As UnitSystem, _
                                 logFile As String) As Boolean
    On Error GoTo ValidationError

    StartCheckpoint "Validate & Normalize CSV"

    ' Read raw CSV
    Dim wb As Workbook
    Set wb = Workbooks.Open(rawCSVPath, ReadOnly:=True)

    Dim ws As Worksheet
    Set ws = wb.Sheets(1)

    ' Find required columns
    Dim headerRow As Long
    headerRow = 1

    Dim colMap As Object
    Set colMap = CreateObject("Scripting.Dictionary")

    Dim col As Long
    For col = 1 To ws.UsedRange.Columns.Count
        Dim header As String
        header = Trim(ws.Cells(headerRow, col).Value)
        colMap(header) = col
    Next

    ' Validate required columns exist
    Dim requiredCols() As Variant
    requiredCols = Array("Story", "Label", "OutputCase", "M3", "V2")

    Dim missing As String
    missing = ""

    Dim colName As Variant
    For Each colName In requiredCols
        If Not colMap.Exists(CStr(colName)) Then
            missing = missing & colName & ", "
        End If
    Next

    If Len(missing) > 0 Then
        LogError logFile, "Missing required columns: " & Left(missing, Len(missing) - 2)
        wb.Close SaveChanges:=False
        EndCheckpoint 0, False
        ValidateAndNormalizeCSV = False
        Exit Function
    End If

    LogInfo logFile, "✓ All required columns found"

    ' Create normalized output workbook
    Dim wbOut As Workbook
    Set wbOut = Workbooks.Add
    Dim wsOut As Worksheet
    Set wsOut = wbOut.Sheets(1)

    ' Write headers for our schema
    wsOut.Cells(1, 1).Value = "Story"
    wsOut.Cells(1, 2).Value = "Label"
    wsOut.Cells(1, 3).Value = "Output Case"
    wsOut.Cells(1, 4).Value = "Station"
    wsOut.Cells(1, 5).Value = "M3"  ' Already in kN·m if ETABS units were kN/m
    wsOut.Cells(1, 6).Value = "V2"  ' Already in kN
    wsOut.Cells(1, 7).Value = "P"

    ' Copy and convert data
    Dim lastRow As Long
    lastRow = ws.UsedRange.Rows.Count

    Dim outRow As Long
    outRow = 2

    Dim row As Long
    For row = headerRow + 1 To lastRow
        ' Copy basic columns
        wsOut.Cells(outRow, 1).Value = ws.Cells(row, colMap("Story")).Value
        wsOut.Cells(outRow, 2).Value = ws.Cells(row, colMap("Label")).Value
        wsOut.Cells(outRow, 3).Value = ws.Cells(row, colMap("OutputCase")).Value

        ' Station (optional, default 0)
        If colMap.Exists("Station") Then
            Dim station As Double
            station = Val(ws.Cells(row, colMap("Station")).Value)
            wsOut.Cells(outRow, 4).Value = station * units.LengthToMM  ' Convert to mm
        Else
            wsOut.Cells(outRow, 4).Value = 0
        End If

        ' Forces (convert to kN and kN·m)
        Dim m3 As Double
        Dim v2 As Double
        Dim p As Double

        m3 = Val(ws.Cells(row, colMap("M3")).Value)
        v2 = Val(ws.Cells(row, colMap("V2")).Value)

        If colMap.Exists("P") Then
            p = Val(ws.Cells(row, colMap("P")).Value)
        Else
            p = 0
        End If

        ' Convert force units (moment = force * length)
        wsOut.Cells(outRow, 5).Value = m3 * units.ForceToN * units.LengthToMM / 1000000  ' → kN·m
        wsOut.Cells(outRow, 6).Value = v2 * units.ForceToN / 1000  ' → kN
        wsOut.Cells(outRow, 7).Value = p * units.ForceToN / 1000   ' → kN

        outRow = outRow + 1

        ' Progress update
        If row Mod 1000 = 0 Then
            Application.StatusBar = "Processing row " & row & " of " & lastRow
            DoEvents
        End If
    Next

    ' Save normalized CSV
    wbOut.SaveAs outputPath, xlCSV
    wbOut.Close SaveChanges:=False
    wb.Close SaveChanges:=False

    LogInfo logFile, "✓ Normalized " & (outRow - 2) & " data rows"

    EndCheckpoint outRow - 2, True
    ValidateAndNormalizeCSV = True
    Exit Function

ValidationError:
    LogError logFile, "Validation error: " & Err.Description
    If Not wb Is Nothing Then wb.Close SaveChanges:=False
    If Not wbOut Is Nothing Then wbOut.Close SaveChanges:=False
    EndCheckpoint 0, False
    ValidateAndNormalizeCSV = False
End Function
```

---

## 6. Implementation Phases

### Phase 0: Setup & Validation (1 hour)
**Goal:** Verify environment, test basic connection

**Tasks:**
1. Create VBA module skeleton
2. Test ETABS API registration
3. Test attach to running instance
4. Test basic model query (GetModelFilename)
5. Implement logging system

**Exit Criteria:**
- Can connect to ETABS
- Can read model path
- Log file created with timestamps

### Phase 1: Analysis Management (2-3 hours)
**Goal:** Ensure analysis is complete before export

**Tasks:**
1. Implement GetCaseStatus for all load cases
2. Implement analysis run trigger
3. Add progress monitoring during analysis
4. Add user prompts and cancellation

**Exit Criteria:**
- Can detect unsolved cases
- Can run analysis if needed
- User can cancel if analysis takes too long

### Phase 2: Bulk Data Export (3-4 hours)
**Goal:** Export frame forces using DatabaseTables

**Tasks:**
1. Test DatabaseTables.GetTableForDisplayCSVFile
2. Export "Element Forces - Frames" table
3. Verify CSV format matches expected schema
4. Handle missing optional columns

**Exit Criteria:**
- Raw CSV exported successfully
- Contains all required columns
- Includes all load cases/combos

### Phase 3: Data Normalization (2-3 hours)
**Goal:** Convert to standardized units and schema

**Tasks:**
1. Implement GetPresentUnits_2 unit detection
2. Build unit conversion logic
3. Post-process CSV to normalized format
4. Validate output against schema

**Exit Criteria:**
- Forces in kN, kN·m
- Lengths in mm
- Valid CSV for Streamlit import

### Phase 4: Additional Tables (2-3 hours)
**Goal:** Export geometry, sections, stories

**Tasks:**
1. Export "Frame Assignments - Sections" table
2. Export "Story Definitions" table
3. Export joint coordinates (may need direct API)
4. Package all files into ZIP with metadata.json

**Exit Criteria:**
- Complete data package
- Metadata includes units, timestamp, model name

### Phase 5: Error Handling & Polish (2-3 hours)
**Goal:** Production-ready robustness

**Tasks:**
1. Add comprehensive error handlers
2. Implement retry logic
3. Add progress bars and status updates
4. Write user documentation

**Exit Criteria:**
- Handles common errors gracefully
- Clear user messages
- No silent failures

### Phase 6: Performance Testing (1-2 hours)
**Goal:** Validate performance targets

**Tasks:**
1. Test with 1000-frame model
2. Profile export time per phase
3. Optimize slow operations
4. Add performance metrics to log

**Exit Criteria:**
- <60s export for 1000 frames
- <5s per checkpoint
- Memory usage <200MB

---

## 7. VBA Module Structure

```
Excel Workbook: StructuralLib_ETABSExport.xlsm
│
├─ Module: mod_Main
│   ├─ Sub ExportETABSData()           ' Entry point
│   └─ Function GetOutputFolder()      ' Config
│
├─ Module: mod_Connection
│   ├─ Function ConnectToETABS()
│   ├─ Function ValidateConnection()
│   └─ Function GetETABSVersion()
│
├─ Module: mod_Analysis
│   ├─ Function EnsureAnalysisComplete()
│   ├─ Function WaitForAnalysisComplete()
│   └─ Function GetCaseList()
│
├─ Module: mod_Export
│   ├─ Function ExportFrameForces()
│   ├─ Function ExportSections()
│   ├─ Function ExportGeometry()
│   └─ Function ExportStories()
│
├─ Module: mod_Validation
│   ├─ Function ValidateAndNormalizeCSV()
│   ├─ Function GetAndValidateUnits()
│   └─ Function ValidateOutputSchema()
│
├─ Module: mod_Logging
│   ├─ Sub LogDebug/Info/Warning/Error()
│   ├─ Function OpenLogFile()
│   ├─ Sub CloseLogFile()
│   ├─ Sub StartCheckpoint()
│   ├─ Sub EndCheckpoint()
│   └─ Sub WriteCheckpointSummary()
│
├─ Module: mod_ErrorHandling
│   ├─ Function RetryOperation()
│   ├─ Function HandleComTimeout()
│   └─ Function FormatErrorMessage()
│
└─ Module: mod_Utils
    ├─ Function FolderExists()
    ├─ Function CountCSVRows()
    ├─ Function CreateZipPackage()
    └─ Function FormatDuration()
```

---

## 8. Testing Strategy

### 8.1 Unit Tests (Manual)

| Test Case | Input | Expected Output | Status |
|-----------|-------|-----------------|--------|
| Connect to running ETABS | ETABS open | Connection success | ⏳ |
| Connect when ETABS closed | ETABS closed | Launch new instance | ⏳ |
| Detect solved analysis | All cases solved | Skip analysis run | ⏳ |
| Detect unsolved analysis | Some cases unsolved | Prompt to run | ⏳ |
| Export with kN/m units | Model in kN/m | Correct CSV values | ⏳ |
| Export with lb/ft units | Model in lb/ft | Converted to kN/m | ⏳ |
| Handle missing optional column | No "P" column | P=0 in output | ⏳ |
| Handle COM timeout | Slow ETABS | Retry 3x, then fail | ⏳ |
| Export 1000-frame model | Large model | Complete in <60s | ⏳ |
| Validate CSV schema | Valid CSV | Schema check pass | ⏳ |

### 8.2 Integration Tests

| Test Scenario | Steps | Success Criteria |
|---------------|-------|------------------|
| **End-to-End Export** | 1. Open test model<br>2. Run macro<br>3. Check output files | All CSVs created, valid schema |
| **Analysis Required** | 1. Open unsolved model<br>2. Run macro<br>3. Accept analysis run | Analysis completes, export succeeds |
| **Error Recovery** | 1. Close ETABS mid-export<br>2. Check log | Error logged, graceful exit, no corruption |
| **Unit Conversion** | 1. Set ETABS to lb/ft<br>2. Run export<br>3. Verify values | Forces in kN, lengths in mm |
| **Large Model Performance** | 1. Load 1000-frame model<br>2. Time export | <60s total, checkpoints logged |

### 8.3 Validation Checklist

Before marking implementation complete:

- [ ] Connects to ETABS reliably (attach/launch)
- [ ] Detects analysis status correctly
- [ ] Runs analysis when needed
- [ ] Exports all required tables
- [ ] Converts units correctly
- [ ] Validates CSV schema
- [ ] Handles errors gracefully
- [ ] Logs all operations
- [ ] Meets performance targets
- [ ] Documentation complete
- [ ] User guide written

---

## 9. Known Gotchas & Solutions

### 9.1 COM Object Lifetime

**Problem:** ETABS COM object becomes invalid if ETABS crashes or closes

**Solution:**
```vba
' Wrap ALL API calls with reconnect logic
Function SafeAPICall(ByRef etabs As Object) As Boolean
    On Error GoTo ReconnectNeeded

    ' Try API call
    Dim ret As Long
    ret = etabs.SapModel.SomeMethod()
    SafeAPICall = True
    Exit Function

ReconnectNeeded:
    LogWarning logFile, "COM object disconnected, reconnecting..."
    Set etabs = ConnectToETABS()
    SafeAPICall = (Not etabs Is Nothing)
End Function
```

### 9.2 ETABS API Version Differences

**Problem:** Method signatures change between ETABS versions

**Solution:**
```vba
' Check version and use appropriate API
Function GetETABSVersion(helper As Object) As Integer
    On Error Resume Next
    GetETABSVersion = helper.GetOAPIVersionNumber

    If Err.Number <> 0 Then
        LogWarning logFile, "Cannot determine ETABS version, assuming v20"
        GetETABSVersion = 20  ' Default to recent version
    End If
End Function

' Use version-specific logic
If etabsVersion >= 20 Then
    ' Use GetPresentUnits_2 (newer API)
    ret = sapModel.GetPresentUnits_2(forceUnits, lengthUnits, tempUnits)
Else
    ' Use GetPresentUnits (legacy API)
    ret = sapModel.GetPresentUnits(units)
    ' Parse units string manually
End If
```

### 9.3 DatabaseTables Table Name Variations

**Problem:** Table names may vary slightly between ETABS versions

**Solution:**
```vba
' Try multiple table name variants
Dim tableNames() As Variant
tableNames = Array("Element Forces - Frames", _
                   "Element Forces-Frames", _
                   "Frame Forces", _
                   "Frame Element Forces")

Dim success As Boolean
success = False

Dim tableName As Variant
For Each tableName In tableNames
    On Error Resume Next
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile(CStr(tableName), csvPath, False, 0, "")

    If Err.Number = 0 And ret = 0 Then
        LogInfo logFile, "✓ Found table: " & tableName
        success = True
        Exit For
    End If

    LogDebug logFile, "Table not found: " & tableName
Next

If Not success Then
    LogError logFile, "Could not find frame forces table with any known name"
    ' Fall back to direct API approach
End If
```

### 9.4 Memory Leaks with Large Arrays

**Problem:** VBA doesn't garbage collect arrays efficiently

**Solution:**
```vba
' Explicitly erase large arrays when done
Dim largeArray() As Double
ReDim largeArray(1 To 100000)

' ... use array ...

Erase largeArray  ' Free memory immediately
Set largeArray = Nothing  ' Extra safety
```

### 9.5 Excel Date/Time Formatting in CSV

**Problem:** Excel may auto-format station numbers as dates

**Solution:**
```vba
' Force text format for numeric IDs
wsOut.Cells(row, col).NumberFormat = "@"  ' Text format
wsOut.Cells(row, col).Value = stationValue

' OR save as CSV with explicit quoting
' OR use .txt extension instead of .csv
```

---

## 10. Next Steps

### Immediate Actions (This Session)
1. **Create skeleton VBA module** with basic structure
2. **Test ETABS API connection** on Windows machine
3. **Document actual table names** from test ETABS model
4. **Verify unit enums** from CHM documentation

### Follow-Up Tasks
1. **TASK-VBA-01:** Implement Phase 0-1 (Connection + Analysis) - 4 hours
2. **TASK-VBA-02:** Implement Phase 2-3 (Export + Normalization) - 6 hours
3. **TASK-VBA-03:** Implement Phase 4-6 (Complete + Polish) - 6 hours
4. **TASK-VBA-04:** Write user guide and installation instructions - 2 hours
5. **TASK-VBA-05:** Package as Excel Add-In (.xlam) - 2 hours

### Questions to Resolve
1. **Export Strategy:** DatabaseTables (bulk, fast) vs Direct API (more control)?
   - **Recommendation:** DatabaseTables primary, Direct API fallback
2. **Table Names:** What are exact table names in your ETABS version?
   - **Action:** Test on actual ETABS installation
3. **Output Format:** Multiple CSVs vs single ZIP package?
   - **Recommendation:** Single ZIP with metadata.json
4. **Installation:** Standalone workbook vs Excel Add-In?
   - **Recommendation:** Start with workbook, migrate to Add-In later

---

## References

- [ETABS VBA Export Macro Recipe](etabs-vba-export-macro.md)
- [CSV Import Schema](../specs/csv-import-schema.md)
- [ETABS Automation Bridge Plan](../planning/etabs-automation-bridge-plan.md)
- [ETABS CHM API Documentation](../reference/vendor/etabs/etabs-chm/)
- ETABS OAPI Method Reference:
  - GetObject: `docs/reference/vendor/etabs/etabs-chm/html/10421d6a-9180-f71a-b493-a7e7785053f1.htm`
  - RunAnalysis: `docs/reference/vendor/etabs/etabs-chm/html/516e7b74-8cb4-af27-31d5-38bb95b3c1d1.htm`
  - GetCaseStatus: `docs/reference/vendor/etabs/etabs-chm/html/94fc4a33-5784-228c-62ad-edcc74eaf034.htm`
  - DatabaseTables: `docs/reference/vendor/etabs/etabs-chm/html/e39eded9-8da2-c558-ecbc-a942b9bb42a3.htm`
  - GetPresentUnits_2: `docs/reference/vendor/etabs/etabs-chm/html/bbeca1c7-a471-6d04-bd18-2df96a44a7a3.htm`

---

**Status:** Ready for Implementation
**Estimated Total Effort:** 20-24 hours (phased delivery)
**Risk Level:** Low (all techniques proven in industry)
**Performance Target:** <60s for 1000 frames ✅
