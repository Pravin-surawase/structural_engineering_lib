Attribute VB_Name = "DEBUG_Step3_AllFrames"
Option Explicit

'==============================================================================
' STEP 3: Loop through all frames and count which ones return results
'==============================================================================

Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub Step3_TestAllFrames()
    On Error GoTo ErrorHandler
    
    ' Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    
    ' Get all frames
    Dim NumberNames As Long
    Dim MyName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    Debug.Print "========== STEP 3: TEST ALL FRAMES =========="
    Debug.Print "Total frames: " & NumberNames
    Debug.Print ""
    
    Dim successCount As Long
    Dim failCount As Long
    Dim totalResults As Long
    
    Dim i As Long
    For i = 0 To NumberNames - 1
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        ' Try ItemTypeElm=0 (ObjectElm)
        ret = mySapModel.Results.FrameForce( _
            MyName(i), eItemTypeElm_ObjectElm, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        
        If ret = 0 And NumberResults > 0 Then
            successCount = successCount + 1
            totalResults = totalResults + NumberResults
            If i < 5 Then  ' Print first 5 successful frames
                Debug.Print "Frame " & (i + 1) & ": " & MyName(i) & " → " & NumberResults & " results"
            End If
        Else
            failCount = failCount + 1
            If i < 5 Then  ' Print first 5 failed frames
                Debug.Print "Frame " & (i + 1) & ": " & MyName(i) & " → FAILED (ret=" & ret & ")"
            End If
        End If
    Next i
    
    Debug.Print ""
    Debug.Print "========== SUMMARY =========="
    Debug.Print "Success: " & successCount & " frames"
    Debug.Print "Failed: " & failCount & " frames"
    Debug.Print "Total results: " & totalResults & " records"
    Debug.Print "Avg results per frame: " & Format(totalResults / successCount, "0.0")
    
    MsgBox "Success: " & successCount & " frames" & vbCrLf & _
           "Failed: " & failCount & " frames" & vbCrLf & _
           "Total results: " & totalResults & vbCrLf & vbCrLf & _
           "Check Immediate Window for details!", vbInformation
    Exit Sub
    
ErrorHandler:
    MsgBox "Error at frame " & i & ": " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub
