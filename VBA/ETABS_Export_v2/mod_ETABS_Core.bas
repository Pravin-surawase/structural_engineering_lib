Attribute VB_Name = "mod_ETABS_Core"
Option Explicit

'==============================================================================
' ETABS EXPORT - CORE MODULE v2.2
'==============================================================================
' Purpose: Export ETABS data to Excel/CSV for Streamlit structural engineering app
' Target:  structural_engineering_lib/streamlit_app
'
' Features:
'   - Connect to running ETABS instance (GetObject pattern)
'   - Run/verify analysis
'   - Export beam forces, sections, geometry
'   - Base reactions and design results
'   - Excel-first pattern: Write to Excel worksheet, then export to CSV
'   - Unit conversion (set to kN, m, then convert)
'
' Usage:
'   1. Open ETABS with your model
'   2. Run analysis (F5) if not done
'   3. In Excel, run ExportETABSData macro
'   4. Upload CSV to Streamlit app
'
' CSV Output Format (for Streamlit):
'   Story,Label,Output Case,Station,M3,V2,P
'   Story1,B1,1.5DL+LL,0.000,125.500,85.200,0.000
'
' v2.2 Changes (fixes from legacy code analysis):
'   - Use GetObject() for connection (more reliable)
'   - SetPresentUnits() BEFORE any results retrieval
'   - Write to Excel worksheet first, then export to CSV
'   - Separate handling for LoadCases vs Combos
'
' Author: Pravin Surawase
' License: MIT
' Version: 2.2.0
' Date: 2026-01-17
'==============================================================================

'------------------------------------------------------------------------------
' CONFIGURATION
'------------------------------------------------------------------------------
Public Const APP_VERSION As String = "2.2.0"
Public Const LOG_LEVEL As Long = 0     ' 0=DEBUG, 1=INFO, 2=WARN, 3=ERROR

' Global state
Public g_LogFile As String
Public g_OutputFolder As String
Public g_LogFileNum As Long

' Global ETABS objects (like legacy code pattern)
Public g_ETABSObject As Object
Public g_SapModel As Object

' Excel worksheet for intermediate storage
Public Const WS_EXPORT_NAME As String = "ETABS_Export"

'------------------------------------------------------------------------------
' TYPE DEFINITIONS
'------------------------------------------------------------------------------

' Unit conversion factors
Public Type UnitConversion
    ForceUnit As String         ' "kN", "kip", "N", "lb"
    LengthUnit As String        ' "mm", "m", "in", "ft"
    ForceToKN As Double         ' Conversion factor to kN
    LengthToMM As Double        ' Conversion factor to mm
    MomentToKNM As Double       ' Conversion factor to kN.m
End Type

'------------------------------------------------------------------------------
' MAIN ENTRY POINT - Call this from Excel button or macro
'------------------------------------------------------------------------------
Public Sub ExportETABSData()
    On Error GoTo ErrorHandler
    
    ' Setup paths
    g_OutputFolder = Environ("USERPROFILE") & "\Documents\ETABS_Export"
    If Not FolderExists(g_OutputFolder) Then MkDir g_OutputFolder
    
    g_LogFile = g_OutputFolder & "\export_" & Format(Now, "yyyymmdd_hhnnss") & ".log"
    
    ' Start logging
    OpenLogFile
    LogInfo "========================================"
    LogInfo "ETABS Export v" & APP_VERSION
    LogInfo "Started: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    LogInfo "========================================"
    
    Application.ScreenUpdating = False
    Application.StatusBar = "Connecting to ETABS..."
    
    ' Connect to ETABS (using GetObject - legacy pattern)
    If Not ConnectToETABS() Then
        MsgBox "Cannot connect to ETABS." & vbCrLf & _
               "Please ensure ETABS is running with a model loaded.", _
               vbCritical, "Connection Failed"
        GoTo Cleanup
    End If
    
    ' Validate model is ready
    Dim modelPath As String
    modelPath = g_SapModel.GetModelFilename
    If Len(modelPath) = 0 Then
        MsgBox "No model loaded in ETABS." & vbCrLf & _
               "Please open a model before running export.", _
               vbExclamation, "No Model"
        GoTo Cleanup
    End If
    LogInfo "Model: " & modelPath
    
    ' *** CRITICAL FIX: Set standard units FIRST (from legacy code) ***
    LogInfo "Setting units to kN, m, C..."
    Dim ret As Long
    ret = g_SapModel.SetPresentUnits(6)  ' eUnits_kN_m_C = 6
    If ret <> 0 Then
        LogWarning "Could not set units: ret=" & ret
    Else
        LogInfo "? Units set to kN, m, C"
    End If
    
    ' Check/Run analysis
    Application.StatusBar = "Verifying analysis..."
    If Not EnsureAnalysisComplete(g_SapModel) Then
        GoTo Cleanup
    End If
    
    ' Get units (should now be kN, m, C)
    Application.StatusBar = "Detecting units..."
    Dim units As UnitConversion
    units = GetETABSUnits(g_SapModel)
    If units.ForceToKN = 0 Then
        MsgBox "Cannot determine ETABS units.", vbCritical, "Unit Error"
        GoTo Cleanup
    End If
    
    ' Setup Excel worksheet for intermediate data
    Call SetupExportWorksheet
    
    ' Create output folders
    Dim rawFolder As String, normFolder As String
    rawFolder = g_OutputFolder & "\raw"
    normFolder = g_OutputFolder & "\normalized"
    If Not FolderExists(rawFolder) Then MkDir rawFolder
    If Not FolderExists(normFolder) Then MkDir normFolder
    
    ' Export all data (write to Excel first, then CSV)
    Application.StatusBar = "Exporting frame forces..."
    LogInfo ""
    LogInfo "=== EXPORTING DATA ==="
    
    Dim success As Boolean
    success = ExportBeamForces(g_SapModel, rawFolder, units)
    
    If Not success Then
        MsgBox "Frame forces export failed." & vbCrLf & _
               "Check log: " & g_LogFile, vbCritical, "Export Failed"
        GoTo Cleanup
    End If
    
    ' Export additional data (optional - continue on failure)
    Application.StatusBar = "Exporting base reactions..."
    Call ExportBaseReactions(g_SapModel, rawFolder, units)
    
    Application.StatusBar = "Exporting column design..."
    Call ExportColumnDesignResults(g_SapModel, rawFolder)
    
    Application.StatusBar = "Exporting beam design..."
    Call ExportBeamDesignResults(g_SapModel, rawFolder)
    
    Application.StatusBar = "Exporting sections..."
    Call ExportSections(g_SapModel, rawFolder)
    
    Application.StatusBar = "Exporting stories..."
    Call ExportStories(g_SapModel, rawFolder)
    
    ' Create metadata
    Call CreateMetadata(g_SapModel, normFolder, units)
    
    ' Success!
    LogInfo ""
    LogInfo "========================================"
    LogInfo "Export completed successfully!"
    LogInfo "Output: " & g_OutputFolder
    LogInfo "========================================"
    
    MsgBox "Export completed!" & vbCrLf & vbCrLf & _
           "Files saved to:" & vbCrLf & _
           g_OutputFolder & vbCrLf & vbCrLf & _
           "Upload beam_forces.csv to Streamlit app.", _
           vbInformation, "Success"
    
    ' Open folder
    If MsgBox("Open output folder?", vbYesNo + vbQuestion) = vbYes Then
        Shell "explorer.exe """ & g_OutputFolder & """", vbNormalFocus
    End If

Cleanup:
    Application.StatusBar = False
    Application.ScreenUpdating = True
    CloseLogFile
    Exit Sub

ErrorHandler:
    LogError "FATAL: " & Err.Description & " (#" & Err.Number & ")"
    MsgBox "Fatal error: " & Err.Description, vbCritical, "Error"
    GoTo Cleanup
End Sub

'------------------------------------------------------------------------------
' EXCEL WORKSHEET SETUP (for Excel-first pattern)
'------------------------------------------------------------------------------

' Create or clear the export worksheet
Private Sub SetupExportWorksheet()
    On Error Resume Next
    Dim ws As Worksheet
    
    ' Try to get existing worksheet
    Set ws = ThisWorkbook.Worksheets(WS_EXPORT_NAME)
    
    If ws Is Nothing Then
        ' Create new worksheet
        Set ws = ThisWorkbook.Worksheets.Add
        ws.Name = WS_EXPORT_NAME
        LogInfo "Created worksheet: " & WS_EXPORT_NAME
    Else
        ' Clear existing data
        ws.Cells.Clear
        LogInfo "Cleared worksheet: " & WS_EXPORT_NAME
    End If
End Sub

' Get export worksheet
Public Function GetExportWorksheet() As Worksheet
    On Error Resume Next
    Set GetExportWorksheet = ThisWorkbook.Worksheets(WS_EXPORT_NAME)
End Function

'------------------------------------------------------------------------------
' CONNECTION (Fixed: Using GetObject like legacy code)
'------------------------------------------------------------------------------

' Connect to running ETABS instance using GetObject (legacy pattern)
Public Function ConnectToETABS() As Boolean
    On Error GoTo ConnectionError
    
    LogInfo "Connecting to running ETABS..."
    
    ' Method 1: Direct GetObject (most reliable - from legacy code)
    On Error Resume Next
    Set g_ETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    On Error GoTo ConnectionError
    
    If Not g_ETABSObject Is Nothing Then
        Set g_SapModel = g_ETABSObject.SapModel
        LogInfo "? Connected to ETABS (GetObject)"
        ConnectToETABS = True
        Exit Function
    End If
    
    ' Method 2: Try ETABSv1.Helper as fallback
    On Error Resume Next
    Dim helper As Object
    Set helper = CreateObject("ETABSv1.Helper")
    
    If Not helper Is Nothing Then
        Set g_ETABSObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
        If Not g_ETABSObject Is Nothing Then
            Set g_SapModel = g_ETABSObject.SapModel
            LogInfo "? Connected to ETABS (Helper)"
            ConnectToETABS = True
            Exit Function
        End If
    End If
    On Error GoTo ConnectionError
    
    ' No running instance - ask user
    Dim response As VbMsgBoxResult
    response = MsgBox("ETABS is not running." & vbCrLf & vbCrLf & _
                     "Please start ETABS and open your model first.", _
                     vbOKOnly + vbExclamation, "ETABS Not Running")
    
    ConnectToETABS = False
    Exit Function

ConnectionError:
    LogError "Connection error: " & Err.Description
    ConnectToETABS = False
End Function

'------------------------------------------------------------------------------
' ANALYSIS
'------------------------------------------------------------------------------

' Ensure analysis is run
Public Function EnsureAnalysisComplete(sapModel As Object) As Boolean
    On Error GoTo AnalysisError
    
    LogInfo "Checking analysis status..."
    
    ' Ask user
    Dim response As VbMsgBoxResult
    response = MsgBox("Has analysis been run in ETABS?" & vbCrLf & vbCrLf & _
                     "YES - Verify and continue" & vbCrLf & _
                     "NO - Run analysis now" & vbCrLf & _
                     "CANCEL - Abort export", _
                     vbYesNoCancel + vbQuestion, "Analysis Check")
    
    Select Case response
        Case vbYes, vbNo
            ' Run analysis (ETABS handles if already run)
            LogInfo "Running analysis..."
            Dim ret As Long
            ret = sapModel.Analyze.RunAnalysis
            
            If ret = 0 Then
                LogInfo "? Analysis OK (ret=0)"
                EnsureAnalysisComplete = True
            Else
                LogError "Analysis failed: ret=" & ret
                MsgBox "Analysis failed. Check ETABS for errors.", vbCritical
                EnsureAnalysisComplete = False
            End If
            
        Case vbCancel
            LogInfo "User cancelled"
            EnsureAnalysisComplete = False
    End Select
    Exit Function

AnalysisError:
    LogError "Analysis error: " & Err.Description
    EnsureAnalysisComplete = False
End Function

'------------------------------------------------------------------------------
' UNIT DETECTION (Fixed: Read units after SetPresentUnits)
'------------------------------------------------------------------------------

' Get ETABS units and build conversion factors
' Note: We call SetPresentUnits(kN,m,C) before this, so conversion should be 1.0
Public Function GetETABSUnits(sapModel As Object) As UnitConversion
    On Error GoTo UnitError
    
    Dim units As UnitConversion
    
    ' Since we set to kN, m, C before calling this, conversion factors are 1.0
    ' But let's verify by reading current units
    Dim forceUnits As Long, lengthUnits As Long, tempUnits As Long
    
    Dim ret As Long
    ret = sapModel.GetPresentUnits_2(forceUnits, lengthUnits, tempUnits)
    
    LogDebug "GetPresentUnits_2: force=" & forceUnits & ", length=" & lengthUnits & ", temp=" & tempUnits
    
    If ret <> 0 Then
        LogError "Cannot get units: ret=" & ret
        ' Default to kN, m since we set it
        units.ForceUnit = "kN"
        units.LengthUnit = "m"
        units.ForceToKN = 1#
        units.LengthToMM = 1000#
        units.MomentToKNM = 1#
        GetETABSUnits = units
        Exit Function
    End If
    
    ' Force units (should be 4 = kN after SetPresentUnits)
    Select Case forceUnits
        Case 1: units.ForceUnit = "lb": units.ForceToKN = 0.00444822
        Case 2: units.ForceUnit = "kip": units.ForceToKN = 4.44822
        Case 3: units.ForceUnit = "N": units.ForceToKN = 0.001
        Case 4: units.ForceUnit = "kN": units.ForceToKN = 1#
        Case 5: units.ForceUnit = "kgf": units.ForceToKN = 0.00980665
        Case 6: units.ForceUnit = "tonf": units.ForceToKN = 9.80665
        Case Else
            LogWarning "Unknown force unit: " & forceUnits & " - assuming kN"
            units.ForceUnit = "kN"
            units.ForceToKN = 1#
    End Select
    
    ' Length units (should be 4 = m after SetPresentUnits)
    Select Case lengthUnits
        Case 1: units.LengthUnit = "in": units.LengthToMM = 25.4
        Case 2: units.LengthUnit = "ft": units.LengthToMM = 304.8
        Case 3: units.LengthUnit = "mm": units.LengthToMM = 1#
        Case 4: units.LengthUnit = "m": units.LengthToMM = 1000#
        Case 5: units.LengthUnit = "cm": units.LengthToMM = 10#
        Case Else
            LogWarning "Unknown length unit: " & lengthUnits & " - assuming m"
            units.LengthUnit = "m"
            units.LengthToMM = 1000#
    End Select
    
    ' Moment = Force * Length -> kN.m
    units.MomentToKNM = units.ForceToKN * (units.LengthToMM / 1000#)
    
    LogInfo "? Units: " & units.ForceUnit & ", " & units.LengthUnit
    LogInfo "  Conversions: F->kN=" & Format(units.ForceToKN, "0.0000") & _
            ", L->mm=" & Format(units.LengthToMM, "0.00") & _
            ", M->kN.m=" & Format(units.MomentToKNM, "0.0000")
    
    GetETABSUnits = units
    Exit Function

UnitError:
    LogError "Unit detection error: " & Err.Description
    ' Default to kN, m since we set it
    units.ForceUnit = "kN"
    units.LengthUnit = "m"
    units.ForceToKN = 1#
    units.LengthToMM = 1000#
    units.MomentToKNM = 1#
    GetETABSUnits = units
End Function

'------------------------------------------------------------------------------
' LOGGING (Simplified)
'------------------------------------------------------------------------------

Public Sub OpenLogFile()
    On Error Resume Next
    g_LogFileNum = FreeFile
    Open g_LogFile For Append As #g_LogFileNum
End Sub

Public Sub CloseLogFile()
    On Error Resume Next
    If g_LogFileNum > 0 Then Close #g_LogFileNum
    g_LogFileNum = 0
End Sub

Private Sub WriteLog(level As String, msg As String)
    On Error Resume Next
    Dim ts As String
    ts = Format(Now, "hh:nn:ss")
    If g_LogFileNum > 0 Then Print #g_LogFileNum, ts & " | " & level & " | " & msg
    Debug.Print ts & " | " & level & " | " & msg
End Sub

Public Sub LogDebug(msg As String)
    If LOG_LEVEL <= 0 Then WriteLog "DEBUG", msg
End Sub

Public Sub LogInfo(msg As String)
    If LOG_LEVEL <= 1 Then WriteLog "INFO ", msg
End Sub

Public Sub LogWarning(msg As String)
    If LOG_LEVEL <= 2 Then WriteLog "WARN ", msg
End Sub

Public Sub LogError(msg As String)
    If LOG_LEVEL <= 3 Then WriteLog "ERROR", msg
End Sub

'------------------------------------------------------------------------------
' UTILITIES
'------------------------------------------------------------------------------

Public Function FolderExists(path As String) As Boolean
    On Error Resume Next
    FolderExists = (Dir(path, vbDirectory) <> "")
End Function

Public Function FileExists(path As String) As Boolean
    On Error Resume Next
    FileExists = (Dir(path) <> "")
End Function

' Count CSV rows
Public Function CountCSVRows(csvPath As String) As Long
    On Error Resume Next
    Dim f As Integer, line As String, count As Long
    f = FreeFile
    Open csvPath For Input As #f
    Do While Not EOF(f)
        Line Input #f, line
        count = count + 1
    Loop
    Close #f
    CountCSVRows = count
End Function

'------------------------------------------------------------------------------
' METADATA
'------------------------------------------------------------------------------

Public Sub CreateMetadata(sapModel As Object, folder As String, units As UnitConversion)
    On Error Resume Next
    
    Dim path As String
    path = folder & "\metadata.json"
    
    Dim f As Integer
    f = FreeFile
    Open path For Output As #f
    
    Dim modelName As String
    modelName = sapModel.GetModelFilename
    
    Print #f, "{"
    Print #f, "  ""export_version"": """ & APP_VERSION & ""","
    Print #f, "  ""export_time"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & ""","
    Print #f, "  ""model"": """ & Replace(modelName, "\", "\\") & ""","
    Print #f, "  ""etabs_units"": {""force"": """ & units.ForceUnit & """, ""length"": """ & units.LengthUnit & """},"
    Print #f, "  ""output_units"": {""force"": ""kN"", ""length"": ""mm"", ""moment"": ""kN.m""}"
    Print #f, "}"
    
    Close #f
    LogInfo "? Metadata created"
End Sub
