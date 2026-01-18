Attribute VB_Name = "DIAGNOSTIC_Simple"
Option Explicit

'==============================================================================
' SIMPLE DIAGNOSTIC - Check basic connection
'==============================================================================

Sub Test_Connection()
    On Error Resume Next
    
    Dim helper As Object
    Dim etabs As Object
    Dim sapModel As Object
    
    ' Step 1: Create Helper
    Set helper = CreateObject("ETABSv1.Helper")
    If helper Is Nothing Then
        MsgBox "FAIL: Cannot create ETABSv1.Helper" & vbCrLf & _
               "ETABS may not be installed properly.", vbCritical
        Exit Sub
    End If
    MsgBox "✓ ETABSv1.Helper created", vbInformation
    
    ' Step 2: Get ETABS Object
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    If etabs Is Nothing Then
        MsgBox "FAIL: GetObject returned Nothing" & vbCrLf & _
               "Is ETABS running with a model loaded?", vbCritical
        Exit Sub
    End If
    MsgBox "✓ ETABS Object obtained", vbInformation
    
    ' Step 3: Get SapModel
    Set sapModel = etabs.SapModel
    If sapModel Is Nothing Then
        MsgBox "FAIL: SapModel is Nothing", vbCritical
        Exit Sub
    End If
    MsgBox "✓ SapModel obtained", vbInformation
    
    ' Step 4: Try GetModelFilename
    Dim modelPath As String
    Err.Clear
    modelPath = sapModel.GetModelFilename()
    
    If Err.Number <> 0 Then
        MsgBox "FAIL: GetModelFilename error" & vbCrLf & _
               Err.Description & " (#" & Err.Number & ")", vbCritical
        Exit Sub
    End If
    
    MsgBox "✓ Model: " & modelPath, vbInformation
    
    ' Step 5: Try SetPresentUnits
    Dim ret As Long
    Err.Clear
    ret = sapModel.SetPresentUnits(6)
    
    If Err.Number <> 0 Then
        MsgBox "FAIL: SetPresentUnits error" & vbCrLf & _
               Err.Description & " (#" & Err.Number & ")" & vbCrLf & _
               "Error #430 = 'Class does not support Automation'", vbCritical
        Exit Sub
    End If
    
    MsgBox "✓ SetPresentUnits OK (ret=" & ret & ")", vbInformation
    
    ' Final message
    MsgBox "=== ALL BASIC TESTS PASSED ===" & vbCrLf & vbCrLf & _
           "Connection works. The issue is with specific API calls." & vbCrLf & _
           "Please run Test_SpecificAPIs next.", vbInformation
End Sub

Sub Test_SpecificAPIs()
    On Error Resume Next
    
    ' Connect first
    Dim helper As Object, etabs As Object, sapModel As Object
    Set helper = CreateObject("ETABSv1.Helper")
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    Set sapModel = etabs.SapModel
    sapModel.SetPresentUnits 6
    
    Dim msg As String, ret As Long
    msg = "API Test Results:" & vbCrLf & vbCrLf
    
    ' Test GetNameList
    Dim n As Long, names() As String
    Err.Clear
    ret = sapModel.FrameObj.GetNameList(n, names)
    msg = msg & "FrameObj.GetNameList: "
    If Err.Number = 0 Then
        msg = msg & "✓ OK (" & n & " frames)" & vbCrLf
    Else
        msg = msg & "✗ FAIL - Error #" & Err.Number & ": " & Err.Description & vbCrLf
    End If
    
    ' Test GetAllFrames
    Dim nn As Long, MyName() As String, PropName() As String, StoryName() As String
    Dim PointName1() As String, PointName2() As String
    Dim Point1X() As Double, Point1Y() As Double, Point1Z() As Double
    Dim Point2X() As Double, Point2Y() As Double, Point2Z() As Double
    Dim Angle() As Double, Offset1X() As Double, Offset2X() As Double
    Dim Offset1Y() As Double, Offset2Y() As Double, Offset1Z() As Double, Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    Err.Clear
    ret = sapModel.FrameObj.GetAllFrames(nn, MyName, PropName, StoryName, _
        PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
        Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
    msg = msg & "FrameObj.GetAllFrames: "
    If Err.Number = 0 Then
        msg = msg & "✓ OK (" & nn & " frames)" & vbCrLf
    Else
        msg = msg & "✗ FAIL - Error #" & Err.Number & ": " & Err.Description & vbCrLf
    End If
    
    ' If GetNameList worked, test Results.FrameForce
    If n > 0 And Err.Number = 0 Then
        Dim NumberResults As Long, obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double, LoadCase() As String
        Dim StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        Err.Clear
        ret = sapModel.Results.FrameForce( _
            names(LBound(names)), 0, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        msg = msg & "Results.FrameForce: "
        If Err.Number = 0 Then
            msg = msg & "✓ OK (" & NumberResults & " results)" & vbCrLf
        Else
            msg = msg & "✗ FAIL - Error #" & Err.Number & ": " & Err.Description & vbCrLf
        End If
    Else
        msg = msg & "Results.FrameForce: SKIPPED (no frame names)" & vbCrLf
    End If
    
    MsgBox msg, vbInformation, "Detailed API Test"
End Sub
