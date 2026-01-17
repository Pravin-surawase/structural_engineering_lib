Attribute VB_Name = "mod_Analysis"
Option Explicit

'==============================================================================
' Analysis Module
' Manages ETABS analysis status and execution
'==============================================================================

' Ensure all load cases are solved
Public Function EnsureAnalysisComplete(sapModel As Object) As Boolean
    On Error GoTo AnalysisError

    ' Get all load cases
    Dim caseCount As Long
    Dim caseNames() As String
    Dim caseTypes() As Long

    Dim ret As Long
    ret = sapModel.LoadCases.GetNameList(caseCount, caseNames, caseTypes)

    If ret <> 0 Or caseCount = 0 Then
        LogError "Cannot retrieve load case list (ret=" & ret & ", count=" & caseCount & ")"
        EnsureAnalysisComplete = False
        Exit Function
    End If

    LogInfo "Found " & caseCount & " load cases"

    ' Check status of each case
    Dim i As Long
    Dim needsRun As Boolean
    needsRun = False

    Dim unsolvedCases As String
    unsolvedCases = ""

    For i = LBound(caseNames) To UBound(caseNames)
        Dim status As Long
        ret = sapModel.Analyze.GetCaseStatus(caseNames(i), status)

        ' Status codes:
        ' 0 = Not run
        ' 1 = Could not start
        ' 2 = Not finished
        ' 3 = Finished successfully

        If status <> 3 Then
            needsRun = True
            unsolvedCases = unsolvedCases & caseNames(i) & ", "
            LogWarning "Case not solved: " & caseNames(i) & " (status=" & status & ")"
        Else
            LogDebug "Case solved: " & caseNames(i)
        End If
    Next i

    If needsRun Then
        ' Remove trailing comma and space
        If Len(unsolvedCases) > 2 Then
            unsolvedCases = Left(unsolvedCases, Len(unsolvedCases) - 2)
        End If

        LogWarning "Analysis incomplete. Unsolved cases: " & unsolvedCases

        ' Prompt user
        Dim response As VbMsgBoxResult
        response = MsgBox( _
            "Model analysis is incomplete or stale." & vbCrLf & vbCrLf & _
            "Unsolved cases: " & vbCrLf & _
            unsolvedCases & vbCrLf & vbCrLf & _
            "Run analysis now?" & vbCrLf & _
            "(This may take several minutes depending on model size)", _
            vbYesNo + vbQuestion, "Analysis Required")

        If response = vbNo Then
            LogInfo "User declined to run analysis"
            EnsureAnalysisComplete = False
            Exit Function
        End If

        ' Run analysis
        LogInfo "User approved analysis run"
        LogInfo "Starting analysis..."

        Application.StatusBar = "Running ETABS analysis..."

        ret = sapModel.Analyze.RunAnalysis()

        If ret <> 0 Then
            LogError "Analysis failed with return code: " & ret
            MsgBox "Analysis failed!" & vbCrLf & _
                   "Return code: " & ret & vbCrLf & vbCrLf & _
                   "Check ETABS analysis log for details.", _
                   vbCritical, "Analysis Failed"
            EnsureAnalysisComplete = False
            Exit Function
        End If

        ' Wait for completion
        LogInfo "Waiting for analysis to complete..."
        If Not WaitForAnalysisComplete(sapModel, caseNames) Then
            LogError "Analysis did not complete in time"
            EnsureAnalysisComplete = False
            Exit Function
        End If

        LogInfo "? Analysis completed successfully"
    Else
        LogInfo "? All cases already solved"
    End If

    EnsureAnalysisComplete = True
    Exit Function

AnalysisError:
    LogError "Analysis check error: " & Err.Description
    EnsureAnalysisComplete = False
End Function

' Wait for analysis to complete
Private Function WaitForAnalysisComplete(sapModel As Object, _
                                         caseNames() As String, _
                                         Optional maxWaitMinutes As Integer = 30) As Boolean
    On Error GoTo WaitError

    Dim startTime As Date
    startTime = Now

    Dim totalCases As Long
    totalCases = UBound(caseNames) - LBound(caseNames) + 1

    LogInfo "Waiting for " & totalCases & " cases (max " & maxWaitMinutes & " minutes)"

    Do While DateDiff("n", startTime, Now) < maxWaitMinutes
        Dim allComplete As Boolean
        allComplete = True

        Dim solvedCount As Long
        solvedCount = 0

        Dim i As Long
        For i = LBound(caseNames) To UBound(caseNames)
            Dim status As Long
            sapModel.Analyze.GetCaseStatus caseNames(i), status

            If status = 3 Then
                solvedCount = solvedCount + 1
            ElseIf status = 1 Then
                ' Could not start - fatal error
                LogError "Case '" & caseNames(i) & "' could not start"
                WaitForAnalysisComplete = False
                Exit Function
            Else
                allComplete = False
            End If
        Next

        If allComplete Then
            LogInfo "? All " & totalCases & " cases completed"
            WaitForAnalysisComplete = True
            Exit Function
        End If

        ' Update progress
        Dim pct As Integer
        pct = CInt((solvedCount / totalCases) * 100)

        Application.StatusBar = "Analysis: " & solvedCount & "/" & totalCases & " cases (" & pct & "%)"
        LogDebug "Analysis progress: " & solvedCount & "/" & totalCases & " (" & pct & "%)"

        ' Check every 5 seconds
        Application.Wait Now + TimeValue("00:00:05")
        DoEvents

        ' Check for user cancellation
        If UserWantsToCancelExport() Then
            LogWarning "Analysis cancelled by user"
            WaitForAnalysisComplete = False
            Exit Function
        End If
    Loop

    ' Timeout
    LogError "Analysis timeout after " & maxWaitMinutes & " minutes"
    MsgBox "Analysis did not complete within " & maxWaitMinutes & " minutes." & vbCrLf & _
           "The export cannot continue with incomplete analysis.", _
           vbExclamation, "Analysis Timeout"

    WaitForAnalysisComplete = False
    Exit Function

WaitError:
    LogError "Error waiting for analysis: " & Err.Description
    WaitForAnalysisComplete = False
End Function
