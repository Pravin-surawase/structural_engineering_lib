Attribute VB_Name = "DEBUG_Step1_CheckAnalysis"
Option Explicit

'==============================================================================
' STEP 1: Check if analysis results exist
'==============================================================================

Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub Step1_CheckAnalysisResults()
    On Error GoTo ErrorHandler
    
    ' Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    Debug.Print "========== STEP 1: CHECK ANALYSIS =========="
    Debug.Print "Model: " & mySapModel.GetModelFilename
    
    ' Check if results are available
    Dim ResultsAvailable As Boolean
    ret = mySapModel.Results.Setup.GetResultsAvailable(ResultsAvailable)
    Debug.Print "Results Available: " & ResultsAvailable & " (ret=" & ret & ")"
    
    If Not ResultsAvailable Then
        MsgBox "NO RESULTS AVAILABLE!" & vbCrLf & vbCrLf & _
               "You need to:" & vbCrLf & _
               "1. Run analysis in ETABS first" & vbCrLf & _
               "2. Or call mySapModel.Analyze.RunAnalysis()", _
               vbExclamation, "No Analysis Results"
        Exit Sub
    End If
    
    ' Get load cases that have results
    Dim NumberNames As Long
    Dim CaseName() As String
    
    ret = mySapModel.LoadCases.GetNameList(NumberNames, CaseName)
    Debug.Print "Load Cases: " & NumberNames
    
    If NumberNames > 0 Then
        Dim i As Long
        For i = 0 To NumberNames - 1
            Debug.Print "  - " & CaseName(i)
        Next i
    End If
    
    ' Get load combos
    ret = mySapModel.RespCombo.GetNameList(NumberNames, CaseName)
    Debug.Print "Load Combos: " & NumberNames
    
    If NumberNames > 0 Then
        For i = 0 To NumberNames - 1
            Debug.Print "  - " & CaseName(i)
        Next i
    End If
    
    MsgBox "Check Immediate Window for results!", vbInformation
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub
