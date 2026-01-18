Attribute VB_Name = "FINAL_WithReference"
Option Explicit

'==============================================================================
' FINAL SOLUTION: Using Early Binding with ETABS Type Library
'==============================================================================
' REQUIRES: ETABS API v1 reference added (Tools → References)
' Uses same pattern as legacy COLUMNS.bas and BASE_REACTIONS.bas
'==============================================================================

' Module-level variables (like legacy code)
Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub ConnectToETABS()
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = Nothing
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
End Sub

Sub ExportBeamForces_Final()
    On Error GoTo ErrorHandler
    
    ' Connect using legacy pattern
    Call ConnectToETABS
    
    ' Set units (CRITICAL - do this first)
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    Debug.Print "Connected: " & mySapModel.GetModelFilename
    
    ' CRITICAL: SELECT ALL CASES (deselect doesn't work in this ETABS version!)
    ' Get all load cases
    Dim NumberCases As Long
    Dim CaseName() As String
    ret = mySapModel.LoadCases.GetNameList(NumberCases, CaseName)
    
    Debug.Print "Found " & NumberCases & " load cases"
    
    ' Select all cases for output
    Dim c As Long
    For c = 0 To NumberCases - 1
        ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(c))
    Next c
    
    ' Also get and select load combos
    Dim NumberCombos As Long
    Dim ComboName() As String
    ret = mySapModel.RespCombo.GetNameList(NumberCombos, ComboName)
    
    Debug.Print "Found " & NumberCombos & " load combos"
    
    For c = 0 To NumberCombos - 1
        ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ComboName(c))
    Next c
    
    ' Get frame names (not GetAllFrames - that failed in diagnostic)
    Dim NumberNames As Long
    Dim MyName() As String
    
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    If ret <> 0 Or NumberNames = 0 Then
        MsgBox "GetNameList failed: ret=" & ret & ", Error: " & Err.Description, vbCritical
        Exit Sub
    End If
    
    Debug.Print "Found " & NumberNames & " frames"
    
    ' Create output folder
    Dim outputFolder As String
    outputFolder = Environ("USERPROFILE") & "\Documents\ETABS_Export"
    If Dir(outputFolder, vbDirectory) = "" Then MkDir outputFolder
    
    Dim csvPath As String
    csvPath = outputFolder & "\beam_forces_final.csv"
    
    ' Open CSV file
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    ' Write header
    Print #f, "Story,Label,Output Case,Station,M3,V2,P"
    
    ' Export each frame
    Dim i As Long, totalRows As Long
    totalRows = 0
    
    For i = LBound(MyName) To UBound(MyName)
        ' Get story name for this frame
        Dim storyName As String
        storyName = GetFrameStory(MyName(i))
        
        ' Get forces using Results.FrameForce with ItemTypeElm=0
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        ret = mySapModel.Results.FrameForce( _
            MyName(i), eItemTypeElm_ObjectElm, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        
        If ret = 0 And NumberResults > 0 Then
            Dim j As Long
            For j = 0 To NumberResults - 1
                ' Write to CSV (units already kN, m from SetPresentUnits)
                Print #f, _
                    storyName & "," & _
                    MyName(i) & "," & _
                    LoadCase(j) & "," & _
                    Format(ElmSta(j) * 1000, "0.000") & "," & _
                    Format(M3(j), "0.000") & "," & _
                    Format(V2(j), "0.000") & "," & _
                    Format(P(j), "0.000")
                totalRows = totalRows + 1
            Next j
        End If
        
        ' Progress
        If i Mod 100 = 0 Then
            Application.StatusBar = "Exporting: " & i & "/" & NumberNames & " frames"
            DoEvents
        End If
    Next i
    
    Close #f
    Application.StatusBar = False
    
    ' Success!
    MsgBox "SUCCESS!" & vbCrLf & vbCrLf & _
           "Exported " & totalRows & " force records" & vbCrLf & _
           NumberNames & " frames processed" & vbCrLf & vbCrLf & _
           "Output: " & csvPath, _
           vbInformation, "Export Complete"
    
    ' Open folder
    Shell "explorer.exe /select,""" & csvPath & """", vbNormalFocus
    Exit Sub

ErrorHandler:
    On Error Resume Next
    Close #f
    Application.StatusBar = False
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")" & vbCrLf & vbCrLf & _
           "At line: " & Erl, vbCritical, "Export Failed"
End Sub

' Helper: Get story name for a frame
Private Function GetFrameStory(frameName As String) As String
    On Error Resume Next
    
    Dim NumberPoints As Long
    Dim PointName() As String, ret As Long
    
    ' Get points for this frame
    ret = mySapModel.FrameObj.GetPoints(frameName, PointName(0), PointName(1))
    
    If ret = 0 Then
        ' Get story from first point
        Dim label As String, story As String
        ret = mySapModel.PointObj.GetLabelFromName(PointName(0), label, story)
        If ret = 0 Then
            GetFrameStory = story
            Exit Function
        End If
    End If
    
    ' Fallback
    GetFrameStory = "Unknown"
End Function

Sub TestWithReference()
    On Error GoTo TestError
    
    ' Test that reference is working
    Call ConnectToETABS
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    Dim NumberNames As Long
    Dim MyName() As String
    
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    If ret = 0 And NumberNames > 0 Then
        MsgBox "✓ Reference is working!" & vbCrLf & vbCrLf & _
               "Found " & NumberNames & " frames" & vbCrLf & vbCrLf & _
               "You can now run: ExportBeamForces_Final", _
               vbInformation, "Test Passed"
    Else
        MsgBox "GetNameList returned ret=" & ret & vbCrLf & _
               "NumberNames=" & NumberNames, vbExclamation
    End If
    Exit Sub
    
TestError:
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")" & vbCrLf & vbCrLf & _
           "Make sure ETABS API v1 is checked in Tools → References", _
           vbCritical, "Test Failed"
End Sub
