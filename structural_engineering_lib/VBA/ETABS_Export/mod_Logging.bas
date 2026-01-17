Attribute VB_Name = "mod_Logging"
Option Explicit

'==============================================================================
' Logging Module
' Multi-level logging with checkpoints
'==============================================================================

' Log levels (constants to avoid enum ambiguity)
Public Const DEBUG_LEVEL As Long = 0
Public Const INFO_LEVEL As Long = 1
Public Const WARNING_LEVEL As Long = 2
Public Const ERROR_LEVEL As Long = 3

' Checkpoint tracking
Public Type ExportCheckpoint
    Name As String
    StartTime As Date
    EndTime As Date
    ItemsProcessed As Long
    Success As Boolean
End Type

Public g_Checkpoints() As ExportCheckpoint  ' Dynamic array - will be ReDim'd in StartCheckpoint
Public g_CheckpointCount As Long

' File handle (module-level)
Private g_LogFileNum As Long

' Open log file
Public Sub OpenLogFile()
    On Error GoTo LogFileError

    ' Validate state
    If Len(g_OutputFolder) = 0 Or Len(g_LogFile) = 0 Then
        ' Don't use LogWarning here - logging not yet initialized
        Debug.Print "Warning: Output folder or log file path not initialized"
        g_LogFileNum = 0
        Exit Sub
    End If

    g_LogFileNum = FreeFile
    Open g_LogFile For Append As #g_LogFileNum

    If Err.Number <> 0 Then
        MsgBox "Warning: Cannot open log file" & vbCrLf & _
               g_LogFile & vbCrLf & vbCrLf & _
               Err.Description, vbExclamation, "Logging Disabled"
        g_LogFileNum = 0
    End If
    Exit Sub
    
LogFileError:
    MsgBox "Logging initialization error: " & Err.Description, vbExclamation
    g_LogFileNum = 0
End Sub

' Close log file
Public Sub CloseLogFile()
    On Error Resume Next
    If g_LogFileNum > 0 Then
        Close #g_LogFileNum
        g_LogFileNum = 0
    End If
End Sub

' Write log message
Private Sub WriteLog(level As String, message As String)
    On Error Resume Next

    If g_LogFileNum = 0 Then Exit Sub

    Dim timestamp As String
    timestamp = Format(Now, "yyyy-mm-dd hh:nn:ss")

    Print #g_LogFileNum, timestamp & " | " & level & " | " & message

    ' Also output to immediate window for debugging
    Debug.Print timestamp & " | " & level & " | " & message
End Sub

' Logging functions
Public Sub LogDebug(message As String)
    If LOG_LEVEL <= DEBUG_LEVEL Then WriteLog "DEBUG", message
End Sub

Public Sub LogInfo(message As String)
    If LOG_LEVEL <= INFO_LEVEL Then WriteLog "INFO ", message
End Sub

Public Sub LogWarning(message As String)
    If LOG_LEVEL <= WARNING_LEVEL Then WriteLog "WARN ", message
End Sub

Public Sub LogError(message As String)
    If LOG_LEVEL <= ERROR_LEVEL Then WriteLog "ERROR", message
End Sub

' Checkpoint management
Public Sub StartCheckpoint(checkpointName As String)
    On Error GoTo CheckpointError
    
    g_CheckpointCount = g_CheckpointCount + 1

    ' Initialize array if first checkpoint
    If g_CheckpointCount = 1 Then
        ReDim g_Checkpoints(1 To 20)
    ' Extend array if needed
    ElseIf g_CheckpointCount > UBound(g_Checkpoints) Then
        ReDim Preserve g_Checkpoints(1 To g_CheckpointCount + 10)
    End If
    
    ' Validate checkpoint index
    If g_CheckpointCount < 1 Or g_CheckpointCount > UBound(g_Checkpoints) Then
        LogError "Invalid checkpoint index: " & g_CheckpointCount
        Exit Sub
    End If

    With g_Checkpoints(g_CheckpointCount)
        .Name = checkpointName
        .StartTime = Now
        .ItemsProcessed = 0
        .Success = False
    End With

    LogInfo String(60, "=")
    LogInfo "CHECKPOINT START: " & checkpointName
    LogInfo String(60, "=")

    Application.StatusBar = "ETABS Export: " & checkpointName & "..."
    Exit Sub

CheckpointError:
    LogError "Error in StartCheckpoint: " & Err.Description
End Sub

Public Sub EndCheckpoint(itemsProcessed As Long, success As Boolean)
    If g_CheckpointCount = 0 Then Exit Sub

    With g_Checkpoints(g_CheckpointCount)
        .EndTime = Now
        .ItemsProcessed = itemsProcessed
        .Success = success

        Dim duration As Double
        duration = (.EndTime - .StartTime) * 86400  ' Convert to seconds

        Dim status As String
        status = IIf(success, "? OK", "? FAILED")

        LogInfo String(60, "=")
        LogInfo "CHECKPOINT END: " & .Name
        LogInfo "  Items: " & .ItemsProcessed
        LogInfo "  Duration: " & Format(duration, "0.00") & "s"
        LogInfo "  Status: " & status
        LogInfo String(60, "=")
    End With
End Sub

' Write checkpoint summary
Public Sub WriteCheckpointSummary()
    LogInfo ""
    LogInfo String(60, "=")
    LogInfo "CHECKPOINT SUMMARY"
    LogInfo String(60, "=")

    Dim i As Long
    Dim totalDuration As Double
    Dim successCount As Long

    For i = 1 To g_CheckpointCount
        With g_Checkpoints(i)
            Dim duration As Double
            duration = (.EndTime - .StartTime) * 86400
            totalDuration = totalDuration + duration

            If .Success Then successCount = successCount + 1

            Dim rate As String
            If duration > 0 And .ItemsProcessed > 0 Then
                rate = Format(.ItemsProcessed / duration, "0") & " items/s"
            Else
                rate = "N/A"
            End If

            Dim status As String
            status = IIf(.Success, "[?]", "[?]")

            LogInfo status & " " & .Name & ": " & _
                   .ItemsProcessed & " items in " & _
                   Format(duration, "0.00") & "s (" & rate & ")"
        End With
    Next

    LogInfo String(60, "-")
    LogInfo "Total: " & successCount & "/" & g_CheckpointCount & " checkpoints passed"
    LogInfo "Total Duration: " & Format(totalDuration, "0.00") & "s"
    LogInfo String(60, "=")
End Sub

' Save checkpoint state to file (for resume capability)
Public Sub SaveCheckpointState()
    On Error Resume Next

    Dim stateFile As String
    stateFile = g_OutputFolder & "\checkpoint_state.txt"

    Dim fileNum As Long
    fileNum = FreeFile

    Open stateFile For Output As #fileNum
    Print #fileNum, "LastCheckpoint=" & g_CheckpointCount
    Print #fileNum, "Timestamp=" & Format(Now, "yyyy-mm-dd hh:nn:ss")
    Close #fileNum
End Sub

' Load last checkpoint (for resume)
Public Function LoadLastCheckpoint() As Long
    On Error Resume Next

    Dim stateFile As String
    stateFile = g_OutputFolder & "\checkpoint_state.txt"

    If Not FileExists(stateFile) Then
        LoadLastCheckpoint = 1  ' Start from beginning
        Exit Function
    End If

    Dim fileNum As Long
    Dim line As String
    Dim lastCheckpoint As Long

    fileNum = FreeFile
    Open stateFile For Input As #fileNum

    Do While Not EOF(fileNum)
        Line Input #fileNum, line
        If InStr(line, "LastCheckpoint=") > 0 Then
            lastCheckpoint = Val(Mid(line, InStr(line, "=") + 1))
        End If
    Loop

    Close #fileNum

    If lastCheckpoint > 0 Then
        LoadLastCheckpoint = lastCheckpoint + 1  ' Resume from next checkpoint
        LogInfo "Resuming from checkpoint " & LoadLastCheckpoint
    Else
        LoadLastCheckpoint = 1
    End If
End Function
