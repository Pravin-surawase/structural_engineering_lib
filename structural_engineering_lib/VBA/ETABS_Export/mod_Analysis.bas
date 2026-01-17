Attribute VB_Name = "mod_Analysis"
Option Explicit

'==============================================================================
' Analysis Module v2.0
' Manages ETABS analysis execution
'
' Based on official ETABS API example - simplified approach:
'   - Just call sapModel.Analyze.RunAnalysis
'   - Check return value (0 = success)
'   - If analysis already run, ETABS handles it gracefully
'
' NOTE: GetCaseStatus causes "Class does not support Automation" with late binding
'       so we avoid it entirely and use the simpler approach
'==============================================================================

' Ensure analysis is complete - simple approach from official ETABS example
Public Function EnsureAnalysisComplete(sapModel As Object) As Boolean
    On Error GoTo AnalysisError
    
    LogInfo "Checking/running analysis..."
    
    ' Ask user first before running
    Dim response As VbMsgBoxResult
    response = MsgBox( _
        "Export requires analysis results." & vbCrLf & vbCrLf & _
        "If you already ran analysis in ETABS, click YES to verify." & vbCrLf & _
        "If analysis has NOT been run, click YES to run it now." & vbCrLf & _
        "Click NO to skip and try export anyway." & vbCrLf & _
        "Click CANCEL to abort.", _
        vbYesNoCancel + vbQuestion, "Verify Analysis")
    
    Select Case response
        Case vbYes
            ' Run/verify analysis
            If RunAnalysis(sapModel) Then
                LogInfo "[OK] Analysis verified/completed"
                EnsureAnalysisComplete = True
            Else
                LogError "Analysis failed"
                EnsureAnalysisComplete = False
            End If
            
        Case vbNo
            LogWarning "User skipped analysis verification"
            LogWarning "Export may fail if analysis not run"
            EnsureAnalysisComplete = True
            
        Case vbCancel
            LogInfo "User cancelled export"
            EnsureAnalysisComplete = False
    End Select
    
    Exit Function

AnalysisError:
    LogError "Analysis error: " & Err.Description
    LogError "  Error #" & Err.Number
    
    Dim continueAnyway As VbMsgBoxResult
    continueAnyway = MsgBox( _
        "Error during analysis:" & vbCrLf & _
        Err.Description & vbCrLf & vbCrLf & _
        "Continue anyway?", _
        vbYesNo + vbExclamation, "Analysis Error")
    
    EnsureAnalysisComplete = (continueAnyway = vbYes)
End Function

' Run analysis - based on official ETABS API example
' If analysis already run, ETABS handles it gracefully (returns quickly)
Public Function RunAnalysis(sapModel As Object) As Boolean
    On Error GoTo RunError
    
    LogInfo "Calling sapModel.Analyze.RunAnalysis..."
    Application.StatusBar = "Running ETABS analysis..."
    
    Dim ret As Long
    
    ' This is the official way from ETABS API examples
    ' If already analyzed, ETABS returns quickly
    ret = sapModel.Analyze.RunAnalysis
    
    Application.StatusBar = ""
    
    If ret = 0 Then
        LogInfo "[OK] Analysis completed successfully (ret=0)"
        RunAnalysis = True
    Else
        LogError "RunAnalysis returned: " & ret
        LogError "Check ETABS for error messages"
        
        MsgBox "Analysis failed (return code: " & ret & ")" & vbCrLf & vbCrLf & _
               "Check ETABS window for error details.", _
               vbCritical, "Analysis Failed"
        
        RunAnalysis = False
    End If
    
    Exit Function

RunError:
    LogError "Error calling RunAnalysis: " & Err.Description
    LogError "  Error #" & Err.Number
    Application.StatusBar = ""
    
    MsgBox "Error running analysis:" & vbCrLf & _
           Err.Description, _
           vbCritical, "Analysis Error"
    
    RunAnalysis = False
End Function

' Quick check if model has frames (simple validation)
Public Function ModelHasFrames(sapModel As Object) As Boolean
    On Error Resume Next
    
    Dim frameCount As Long
    Dim frameNames() As String
    Dim ret As Long
    
    ret = sapModel.FrameObj.GetNameList(frameCount, frameNames)
    
    If Err.Number = 0 And ret = 0 And frameCount > 0 Then
        LogDebug "Model has " & frameCount & " frame objects"
        ModelHasFrames = True
    Else
        LogWarning "No frame objects found (count=" & frameCount & ")"
        ModelHasFrames = False
    End If
    
    Err.Clear
End Function

' Check if model file is saved (required before analysis)
Public Function ModelIsSaved(sapModel As Object) As Boolean
    On Error Resume Next
    
    Dim modelPath As String
    modelPath = sapModel.GetModelFilename
    
    If Err.Number = 0 And Len(modelPath) > 0 Then
        LogDebug "Model path: " & modelPath
        ModelIsSaved = True
    Else
        LogWarning "Model not saved or path empty"
        ModelIsSaved = False
    End If
    
    Err.Clear
End Function

