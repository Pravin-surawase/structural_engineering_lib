Attribute VB_Name = "mod_Design"
Option Explicit

'==============================================================================
' ETABS Design Module v2.0
' Handles design execution - simplified approach
'
' Based on official ETABS API pattern:
'   - Just call sapModel.DesignConcrete.StartDesign or DesignSteel.StartDesign
'   - Check return value (0 = success)
'   - If design already run, ETABS handles it gracefully
'
' NOTE: GetResultsAvailable may not work with late binding, so we use
'       the simpler approach of just running design if user wants it
'==============================================================================

' Check if design is needed and run if requested
Public Function EnsureDesignComplete(sapModel As Object) As Boolean
    On Error GoTo DesignError
    
    LogInfo "=== Design Check ==="
    
    ' Design is optional - ask user
    Dim response As VbMsgBoxResult
    response = MsgBox( _
        "Do you want to run/verify design?" & vbCrLf & vbCrLf & _
        "YES = Run concrete and steel design" & vbCrLf & _
        "NO = Skip design (export analysis results only)" & vbCrLf & _
        "CANCEL = Abort export", _
        vbYesNoCancel + vbQuestion, "Design Check")
    
    Select Case response
        Case vbYes
            If RunDesign(sapModel) Then
                LogInfo "[OK] Design completed"
                EnsureDesignComplete = True
            Else
                ' Design failed but analysis might still be valid
                Dim continueWithout As VbMsgBoxResult
                continueWithout = MsgBox( _
                    "Design failed. Continue with export anyway?", _
                    vbYesNo + vbQuestion, "Design Failed")
                EnsureDesignComplete = (continueWithout = vbYes)
            End If
            
        Case vbNo
            LogInfo "User skipped design"
            EnsureDesignComplete = True
            
        Case vbCancel
            LogInfo "User cancelled export"
            EnsureDesignComplete = False
    End Select
    
    Exit Function
    
DesignError:
    LogError "Error in design check: " & Err.Description
    EnsureDesignComplete = True  ' Continue anyway
End Function

' Run design (both concrete and steel) - simple approach
Public Function RunDesign(sapModel As Object) As Boolean
    On Error GoTo DesignError
    
    LogInfo "Running design..."
    Application.StatusBar = "Running ETABS design..."
    
    Dim retConcrete As Long
    Dim retSteel As Long
    Dim concreteOK As Boolean
    Dim steelOK As Boolean
    
    ' Run concrete design
    LogInfo "Starting concrete design..."
    On Error Resume Next
    retConcrete = sapModel.DesignConcrete.StartDesign
    
    If Err.Number <> 0 Then
        LogWarning "Concrete design not available: " & Err.Description
        Err.Clear
        concreteOK = False
    ElseIf retConcrete <> 0 Then
        LogWarning "Concrete design returned: " & retConcrete
        concreteOK = False
    Else
        LogInfo "[OK] Concrete design completed (ret=0)"
        concreteOK = True
    End If
    
    ' Run steel design
    LogInfo "Starting steel design..."
    retSteel = sapModel.DesignSteel.StartDesign
    
    If Err.Number <> 0 Then
        LogWarning "Steel design not available: " & Err.Description
        Err.Clear
        steelOK = False
    ElseIf retSteel <> 0 Then
        LogWarning "Steel design returned: " & retSteel
        steelOK = False
    Else
        LogInfo "[OK] Steel design completed (ret=0)"
        steelOK = True
    End If
    
    On Error GoTo DesignError
    Application.StatusBar = ""
    
    ' Success if at least one design worked
    RunDesign = concreteOK Or steelOK
    
    If Not RunDesign Then
        LogError "Both concrete and steel design failed"
    End If
    
    Exit Function
    
DesignError:
    LogError "Error running design: " & Err.Description
    Application.StatusBar = ""
    RunDesign = False
End Function

' Get design code being used for concrete
Public Function GetConcreteDesignCode(sapModel As Object) As String
    On Error Resume Next
    
    Dim code As String
    Dim ret As Long
    
    ret = sapModel.DesignConcrete.GetCode(code)
    
    If Err.Number <> 0 Or ret <> 0 Then
        GetConcreteDesignCode = "Unknown"
        Err.Clear
    Else
        GetConcreteDesignCode = code
        LogDebug "Concrete design code: " & code
    End If
End Function

' Get design code being used for steel
Public Function GetSteelDesignCode(sapModel As Object) As String
    On Error Resume Next
    
    Dim code As String
    Dim ret As Long
    
    ret = sapModel.DesignSteel.GetCode(code)
    
    If Err.Number <> 0 Or ret <> 0 Then
        GetSteelDesignCode = "Unknown"
        Err.Clear
    Else
        GetSteelDesignCode = code
        LogDebug "Steel design code: " & code
    End If
End Function