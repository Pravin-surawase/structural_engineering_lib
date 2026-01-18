Attribute VB_Name = "DEBUG_Step2_SingleFrame"
Option Explicit

'==============================================================================
' STEP 2: Test getting forces for a SINGLE frame with all ItemTypeElm values
'==============================================================================

Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub Step2_TestSingleFrame()
    On Error GoTo ErrorHandler
    
    ' Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    
    ' Get first frame name
    Dim NumberNames As Long
    Dim MyName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    If NumberNames = 0 Then
        MsgBox "No frames found!", vbCritical
        Exit Sub
    End If
    
    Dim testFrame As String
    testFrame = MyName(0)  ' First frame
    
    Debug.Print "========== STEP 2: TEST SINGLE FRAME =========="
    Debug.Print "Testing frame: " & testFrame
    Debug.Print ""
    
    ' Test with different ItemTypeElm values
    Dim itemTypes As Variant
    Dim itemNames As Variant
    itemTypes = Array(0, 1, 2, 3)
    itemNames = Array("ObjectElm", "Element", "GroupElm", "SelectionElm")
    
    Dim i As Long
    For i = 0 To 3
        Debug.Print "--- Testing ItemTypeElm=" & itemTypes(i) & " (" & itemNames(i) & ") ---"
        
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        ret = mySapModel.Results.FrameForce( _
            testFrame, itemTypes(i), NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        
        Debug.Print "  Return code: " & ret
        Debug.Print "  NumberResults: " & NumberResults
        
        If ret = 0 And NumberResults > 0 Then
            Debug.Print "  ✓ SUCCESS! Got " & NumberResults & " results"
            Debug.Print "  First result:"
            Debug.Print "    Load Case: " & LoadCase(0)
            Debug.Print "    Station: " & ElmSta(0)
            Debug.Print "    M3: " & M3(0) & " kN·m"
            Debug.Print "    V2: " & V2(0) & " kN"
            Debug.Print "    P: " & P(0) & " kN"
        Else
            Debug.Print "  ✗ FAILED or no results"
        End If
        Debug.Print ""
    Next i
    
    MsgBox "Check Immediate Window for detailed results!", vbInformation
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub
