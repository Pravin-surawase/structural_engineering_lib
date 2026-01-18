Attribute VB_Name = "APPROACH_3_MinimalAPI"
Option Explicit

'==============================================================================
' APPROACH 3: Minimal API Calls (Safest)
'==============================================================================
' Strategy: Use absolute minimum API calls
' - Only test which APIs work on your ETABS version
' - No complex iteration
' - Maximum error info
'==============================================================================

Sub Approach3_TestAPIs()
    On Error Resume Next
    
    ' Connect
    Dim helper As Object, etabs As Object, sapModel As Object
    Set helper = CreateObject("ETABSv1.Helper")
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    Set sapModel = etabs.SapModel
    
    Dim ret As Long
    Dim msg As String
    msg = "=== ETABS API TEST RESULTS ===" & vbCrLf & vbCrLf
    
    ' Test 1: SetPresentUnits
    Err.Clear
    ret = sapModel.SetPresentUnits(6)
    msg = msg & "SetPresentUnits: " & IIf(Err.Number = 0 And ret = 0, "✓ OK", "✗ FAIL - " & Err.Description) & vbCrLf
    
    ' Test 2: FrameObj.GetNameList
    Dim numFrames As Long, frameNames() As String
    Err.Clear
    ret = sapModel.FrameObj.GetNameList(numFrames, frameNames)
    msg = msg & "FrameObj.GetNameList: " & IIf(Err.Number = 0 And ret = 0, "✓ OK - " & numFrames & " frames", "✗ FAIL - " & Err.Description) & vbCrLf
    
    ' Test 3: FrameObj.GetAllFrames
    Dim NumberNames As Long, MyName() As String, PropName() As String, StoryName() As String
    Dim PointName1() As String, PointName2() As String
    Dim Point1X() As Double, Point1Y() As Double, Point1Z() As Double
    Dim Point2X() As Double, Point2Y() As Double, Point2Z() As Double
    Dim Angle() As Double, Offset1X() As Double, Offset2X() As Double
    Dim Offset1Y() As Double, Offset2Y() As Double, Offset1Z() As Double, Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    Err.Clear
    ret = sapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
        PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
        Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
    msg = msg & "FrameObj.GetAllFrames: " & IIf(Err.Number = 0 And ret = 0, "✓ OK - " & NumberNames & " frames", "✗ FAIL - " & Err.Description) & vbCrLf
    
    ' Test 4: Results.FrameForce (on first frame if we have names)
    If numFrames > 0 And Err.Number = 0 Then
        Dim NumberResults As Long, obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double, LoadCase() As String
        Dim StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        Err.Clear
        ret = sapModel.Results.FrameForce( _
            frameNames(LBound(frameNames)), 0, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        msg = msg & "Results.FrameForce: " & IIf(Err.Number = 0 And ret = 0, "✓ OK - " & NumberResults & " results", "✗ FAIL - " & Err.Description) & vbCrLf
    End If
    
    ' Test 5: DatabaseTables
    Dim csvPath As String
    csvPath = Environ("TEMP") & "\etabs_test.csv"
    Err.Clear
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile("Frame Element Forces", csvPath, False, 0, "")
    msg = msg & "DatabaseTables: " & IIf(Err.Number = 0 And ret = 0, "✓ OK", "✗ FAIL - " & Err.Description) & vbCrLf
    
    ' Test 6: Results.BaseReact
    Dim NumberResults2 As Long, LoadCase2() As String, StepType2() As String, StepNum2() As Double
    Dim Fx() As Double, Fy() As Double, Fz() As Double
    Dim Mx() As Double, My() As Double, Mz() As Double
    Dim gx() As Double, gy() As Double, gz() As Double
    
    Err.Clear
    ret = sapModel.Results.BaseReact(NumberResults2, LoadCase2, StepType2, StepNum2, _
        Fx, Fy, Fz, Mx, My, Mz, gx, gy, gz)
    msg = msg & "Results.BaseReact: " & IIf(Err.Number = 0 And ret = 0, "✓ OK - " & NumberResults2 & " results", "✗ FAIL - " & Err.Description) & vbCrLf
    
    MsgBox msg, vbInformation, "API Test Results"
End Sub

Sub Approach3_ExportUsingWorkingAPIs()
    ' After running Approach3_TestAPIs, implement export using ONLY the APIs that worked
    MsgBox "First run Approach3_TestAPIs to see which APIs work, then we'll implement export with those APIs."
End Sub
