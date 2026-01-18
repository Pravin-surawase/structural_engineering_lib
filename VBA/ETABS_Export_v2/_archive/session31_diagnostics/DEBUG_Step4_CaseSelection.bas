Attribute VB_Name = "DEBUG_Step4_CaseSelection"
Option Explicit

'==============================================================================
' STEP 4: Test different case selection methods
'==============================================================================

Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub Step4_TestCaseSelection()
    On Error GoTo ErrorHandler
    
    ' Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    ' Get first frame
    Dim NumberNames As Long
    Dim MyName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    If NumberNames = 0 Then
        MsgBox "No frames found!", vbCritical
        Exit Sub
    End If
    
    Dim testFrame As String
    testFrame = MyName(0)
    
    Debug.Print "========== STEP 4: CASE SELECTION METHODS =========="
    Debug.Print "Testing frame: " & testFrame
    Debug.Print ""
    
    ' Test 1: Deselect all
    Debug.Print "--- Test 1: DeselectAllCasesAndCombosForOutput ---"
    ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    Call TestFrameForce(testFrame)
    
    ' Test 2: Get available cases and select first one
    Dim CaseName() As String
    ret = mySapModel.LoadCases.GetNameList(NumberNames, CaseName)
    
    If NumberNames > 0 Then
        Debug.Print "--- Test 2: Select specific case: " & CaseName(0) & " ---"
        ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(0))
        Call TestFrameForce(testFrame)
    End If
    
    ' Test 3: Select ALL cases
    If NumberNames > 0 Then
        Debug.Print "--- Test 3: Select ALL cases ---"
        ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
        
        Dim i As Long
        For i = 0 To NumberNames - 1
            ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(i))
        Next i
        
        Call TestFrameForce(testFrame)
    End If
    
    MsgBox "Check Immediate Window for results!", vbInformation
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub

Private Sub TestFrameForce(frameName As String)
    Dim ret As Long
    Dim NumberResults As Long
    Dim obj() As String, ObjSta() As Double
    Dim Elm() As String, ElmSta() As Double
    Dim LoadCase() As String, StepType() As String, StepNum() As Double
    Dim P() As Double, V2() As Double, V3() As Double
    Dim T() As Double, M2() As Double, M3() As Double
    
    ret = mySapModel.Results.FrameForce( _
        frameName, eItemTypeElm_ObjectElm, NumberResults, _
        obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
        P, V2, V3, T, M2, M3)
    
    Debug.Print "  Return: " & ret & ", Results: " & NumberResults
    
    If ret = 0 And NumberResults > 0 Then
        Debug.Print "  ✓ First result: Case=" & LoadCase(0) & ", M3=" & M3(0)
    End If
    Debug.Print ""
End Sub
