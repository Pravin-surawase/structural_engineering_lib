Attribute VB_Name = "mod_Main"
Option Explicit

'==============================================================================
' ETABS Export to Structural Lib - Main Module
' Version: 1.0.0
' Date: 2026-01-17
'
' Entry point for ETABS data export to structural_engineering_lib CSV format
'==============================================================================

' Global configuration
Public Const APP_VERSION As String = "1.0.0"
Public Const LOG_LEVEL As LogLevel = INFO_LEVEL
Public g_LogFile As String
Public g_OutputFolder As String
Public g_CancelRequested As Boolean

' Main entry point - Call this from Excel button or macro
Public Sub ExportETABSData()
    On Error GoTo ErrorHandler

    ' Reset cancellation flag
    g_CancelRequested = False

    ' Setup paths
    g_OutputFolder = GetOutputFolder()
    g_LogFile = g_OutputFolder & "\etabs_export_" & Format(Now, "yyyymmdd_hhnnss") & ".log"

    ' Clear previous status
    Application.StatusBar = False
    Application.ScreenUpdating = False

    ' Start logging
    Call OpenLogFile
    LogInfo "========================================"
    LogInfo "ETABS Export to Structural Lib v" & APP_VERSION
    LogInfo "Started: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    LogInfo "========================================"

    ' Phase 0: Validation
    StartCheckpoint "Environment Validation"
    If Not ValidateEnvironment() Then
        MsgBox "Environment validation failed." & vbCrLf & _
               "Please check the log file:" & vbCrLf & vbCrLf & _
               g_LogFile, vbCritical, "Validation Failed"
        GoTo Cleanup
    End If
    EndCheckpoint 1, True

    ' Connect to ETABS
    StartCheckpoint "Connect to ETABS"
    Dim etabs As Object
    Set etabs = ConnectToETABS()
    If etabs Is Nothing Then
        MsgBox "Cannot connect to ETABS." & vbCrLf & _
               "Please ensure ETABS is running or can be launched." & vbCrLf & vbCrLf & _
               "Log: " & g_LogFile, vbCritical, "Connection Failed"
        GoTo Cleanup
    End If

    Dim sapModel As Object
    Set sapModel = etabs.SapModel
    
    ' Validate model is ready
    If Not ValidateModelReady(sapModel) Then
        MsgBox "No model loaded in ETABS." & vbCrLf & _
               "Please open a model before running export." & vbCrLf & vbCrLf & _
               "Log: " & g_LogFile, vbExclamation, "No Model"
        GoTo Cleanup
    End If
    EndCheckpoint 1, True

    ' Phase 1: Ensure analysis is complete
    StartCheckpoint "Verify Analysis Status"
    If Not EnsureAnalysisComplete(sapModel) Then
        MsgBox "Analysis could not be completed." & vbCrLf & _
               "Export aborted." & vbCrLf & vbCrLf & _
               "Log: " & g_LogFile, vbExclamation, "Analysis Required"
        GoTo Cleanup
    End If
    EndCheckpoint 1, True

    ' Phase 2: Get and validate units
    StartCheckpoint "Detect Units"
    Dim units As UnitConversion
    units = GetAndValidateUnits(sapModel)
    If units.ForceToKN = 0 Then
        MsgBox "Unit detection failed." & vbCrLf & _
               "Cannot determine ETABS units." & vbCrLf & vbCrLf & _
               "Log: " & g_LogFile, vbCritical, "Unit Error"
        GoTo Cleanup
    End If
    EndCheckpoint 1, True

    ' Phase 3: Export tables
    Dim rawFolder As String
    rawFolder = g_OutputFolder & "\raw"
    If Not FolderExists(rawFolder) Then MkDir rawFolder

    ' Export frame forces (required)
    StartCheckpoint "Export Frame Forces"
    If Not ExportFrameForces(sapModel, rawFolder) Then
        MsgBox "Frame forces export failed." & vbCrLf & _
               "This is required for the export." & vbCrLf & vbCrLf & _
               "Log: " & g_LogFile, vbCritical, "Export Failed"
        GoTo Cleanup
    End If
    EndCheckpoint 1, True

    ' Export sections (optional but recommended)
    StartCheckpoint "Export Sections"
    If ExportSections(sapModel, rawFolder) Then
        EndCheckpoint 1, True
    Else
        LogWarning "Sections export failed - will use defaults"
        EndCheckpoint 0, False
    End If

    ' Export geometry (optional)
    StartCheckpoint "Export Geometry"
    If ExportGeometry(sapModel, rawFolder) Then
        EndCheckpoint 1, True
    Else
        LogWarning "Geometry export failed - 3D visualization may be limited"
        EndCheckpoint 0, False
    End If

    ' Export stories (optional)
    StartCheckpoint "Export Stories"
    If ExportStories(sapModel, rawFolder) Then
        EndCheckpoint 1, True
    Else
        LogWarning "Stories export failed - minor impact"
        EndCheckpoint 0, False
    End If

    ' Phase 4: Normalize CSVs to schema
    Dim normalizedFolder As String
    normalizedFolder = g_OutputFolder & "\normalized"
    If Not FolderExists(normalizedFolder) Then MkDir normalizedFolder

    StartCheckpoint "Normalize Data"
    If Not ValidateAndNormalizeCSV( _
        rawFolder & "\frame_forces_raw.csv", _
        normalizedFolder & "\beam_forces.csv", _
        units _
    ) Then
        MsgBox "Data normalization failed." & vbCrLf & _
               "Raw data is available but may not match schema." & vbCrLf & vbCrLf & _
               "Log: " & g_LogFile, vbExclamation, "Normalization Failed"
        GoTo Cleanup
    End If
    EndCheckpoint 1, True

    ' Phase 5: Create metadata
    StartCheckpoint "Create Metadata"
    Call CreateMetadataFile(sapModel, normalizedFolder, units)
    EndCheckpoint 1, True

    ' Success!
    Call WriteCheckpointSummary

    LogInfo "========================================"
    LogInfo "Export completed successfully!"
    LogInfo "Finished: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    LogInfo "========================================"
    LogInfo "Output folder: " & g_OutputFolder
    LogInfo "Normalized files: " & normalizedFolder

    MsgBox "Export completed successfully!" & vbCrLf & vbCrLf & _
           "Normalized files saved to:" & vbCrLf & _
           normalizedFolder & vbCrLf & vbCrLf & _
           "Log file: " & vbCrLf & _
           g_LogFile, vbInformation, "Export Complete"

    ' Open output folder
    If MsgBox("Open output folder?", vbYesNo + vbQuestion, "Export Complete") = vbYes Then
        Shell "explorer.exe """ & normalizedFolder & """", vbNormalFocus
    End If

Cleanup:
    Application.StatusBar = False
    Application.ScreenUpdating = True
    Call CloseLogFile
    Exit Sub

ErrorHandler:
    LogError "FATAL ERROR in ExportETABSData"
    LogError "Error #" & Err.Number & ": " & Err.Description
    LogError "Source: " & Err.Source

    MsgBox "Fatal error during export:" & vbCrLf & vbCrLf & _
           Err.Description & vbCrLf & vbCrLf & _
           "Check log: " & g_LogFile, vbCritical, "Fatal Error"

    GoTo Cleanup
End Sub

' Get output folder (configurable)
Private Function GetOutputFolder() As String
    Dim folder As String

    ' Default: My Documents\ETABS_Export
    folder = Environ("USERPROFILE") & "\Documents\ETABS_Export"

    ' Create if doesn't exist
    If Not FolderExists(folder) Then
        MkDir folder
    End If

    GetOutputFolder = folder
End Function

' Check if user wants to cancel (called during long operations)
Public Function UserWantsToCancelExport() As Boolean
    ' Allow user to press ESC to cancel
    DoEvents
    If g_CancelRequested Then
        UserWantsToCancelExport = True
    End If
End Function

' User-callable function to cancel export
Public Sub CancelExport()
    g_CancelRequested = True
    LogWarning "User requested cancellation"
End Sub
