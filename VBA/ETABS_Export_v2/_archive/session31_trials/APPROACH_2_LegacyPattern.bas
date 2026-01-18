Attribute VB_Name = "APPROACH_2_LegacyPattern"
Option Explicit

'==============================================================================
' APPROACH 2: Exact Legacy Pattern (Most Compatible)
'==============================================================================
' Strategy: Replicate BASE_REACTIONS.bas pattern exactly
' - Direct GetObject connection
' - SetPresentUnits before operations  
' - No GetAllFrames, no case enumeration
' - Direct Results calls on specific objects
'==============================================================================

Sub Approach2_ExportBeamForces()
    On Error GoTo ErrorHandler
    
    ' *** EXACT LEGACY CONNECTION PATTERN ***
    Dim myHelper As Object
    Dim myETABSObject As Object
    Dim mySapModel As Object
    
    Set myHelper = CreateObject("ETABSv1.Helper")  
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    ' *** SET UNITS FIRST (legacy pattern) ***
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(6)  ' eUnits_kN_m_C
    
    Debug.Print "Connected. Model: " & mySapModel.GetModelFilename
    
    ' *** Get list of ALL frame NAMES (not GetAllFrames) ***
    Dim NumberNames As Long
    Dim MyName() As String
    
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    If ret <> 0 Or NumberNames = 0 Then
        MsgBox "GetNameList failed: ret=" & ret & ", count=" & NumberNames
        Exit Sub
    End If
    
    Debug.Print "Found " & NumberNames & " frames"
    
    ' *** Create output file ***
    Dim csvPath As String
    csvPath = Environ("USERPROFILE") & "\Documents\ETABS_Export\beam_forces_approach2.csv"
    
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    Print #f, "Story,Label,Output Case,Station,M3,V2,P"
    
    ' *** Iterate frames and get forces ***
    Dim i As Long, totalRows As Long
    totalRows = 0
    
    For i = LBound(MyName) To UBound(MyName)
        ' Get story for this frame
        Dim storyName As String, pointName As String
        ret = mySapModel.PointObj.GetCommonTo(MyName(i), 1, pointName)
        ret = mySapModel.PointObj.GetLabelFromName(pointName, MyName(i), storyName)
        
        ' *** Get forces using ItemTypeElm=0 (all cases) ***
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        On Error Resume Next
        ret = mySapModel.Results.FrameForce( _
            MyName(i), 0, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        
        If Err.Number = 0 And ret = 0 And NumberResults > 0 Then
            Dim j As Long
            For j = LBound(LoadCase) To UBound(LoadCase)
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
        
        On Error GoTo ErrorHandler
        
        ' Progress
        If i Mod 100 = 0 Then
            Debug.Print "Progress: " & i & "/" & NumberNames
        End If
    Next i
    
    Close #f
    
    MsgBox "SUCCESS! Exported " & totalRows & " records" & vbCrLf & csvPath
    Exit Sub

ErrorHandler:
    On Error Resume Next
    Close #f
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")"
End Sub
