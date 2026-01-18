Attribute VB_Name = "ETABS_SimpleExport"
Option Explicit

'==============================================================================
' ETABS SIMPLE EXPORT - No Complex VBA Features
'==============================================================================
' Uses only basic VBA: variables, arrays, loops
' No Type definitions, no classes, no complex features
'
' USER: Just run ExportBeamsSimple()
'
' Created: 2026-01-17
'==============================================================================

' Module-level ETABS objects
Private myHelper As ETABSv1.Helper
Private myETABSObject As ETABSv1.cOAPI
Private mySapModel As ETABSv1.cSapModel

Sub ExportBeamsSimple()
    '
    ' MAIN FUNCTION - RUN THIS
    '
    On Error GoTo ErrorHandler
    
    ' Connect to ETABS
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    Debug.Print "Connected: " & mySapModel.GetModelFilename(False)
    
    ' Select all cases for output
    Call SelectAllCases
    
    ' Get frame list
    Dim NumberFrames As Long
    Dim FrameName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberFrames, FrameName)
    Debug.Print "Frames found: " & NumberFrames
    
    ' Create output folder
    Dim outputFolder As String
    outputFolder = Environ("USERPROFILE") & "\Documents\ETABS_Export"
    If Dir(outputFolder, vbDirectory) = "" Then MkDir outputFolder
    
    ' Open CSV file
    Dim csvPath As String
    csvPath = outputFolder & "\beam_design_data.csv"
    
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    ' Header
    Print #f, "Label,Story,Width_mm,Depth_mm,Span_m,Mu_max_kNm,Mu_min_kNm,Vu_max_kN,fck,fy"
    
    ' Process each frame
    Dim i As Long
    Dim exported As Long
    exported = 0
    
    For i = 0 To NumberFrames - 1
        
        ' Variables for this beam
        Dim beamLabel As String
        Dim beamStory As String
        Dim beamWidth As Double
        Dim beamDepth As Double
        Dim beamSpan As Double
        Dim beamMuMax As Double
        Dim beamMuMin As Double
        Dim beamVuMax As Double
        Dim isBeam As Boolean
        
        ' Get beam data
        isBeam = GetBeamInfo(FrameName(i), beamLabel, beamStory, _
                             beamWidth, beamDepth, beamSpan, _
                             beamMuMax, beamMuMin, beamVuMax)
        
        If isBeam Then
            ' Write CSV row
            Print #f, beamLabel & "," & _
                      beamStory & "," & _
                      Format(beamWidth, "0") & "," & _
                      Format(beamDepth, "0") & "," & _
                      Format(beamSpan, "0.000") & "," & _
                      Format(beamMuMax, "0.000") & "," & _
                      Format(beamMuMin, "0.000") & "," & _
                      Format(beamVuMax, "0.000") & "," & _
                      "25,500"
            
            exported = exported + 1
        End If
        
        ' Progress
        If i Mod 50 = 0 Then
            Application.StatusBar = "Processing: " & i & "/" & NumberFrames
            DoEvents
        End If
    Next i
    
    Close #f
    Application.StatusBar = False
    
    Debug.Print "Exported: " & exported & " beams"
    Debug.Print "File: " & csvPath
    
    MsgBox "Export Complete!" & vbCrLf & vbCrLf & _
           "Beams: " & exported & vbCrLf & _
           "File: " & csvPath, vbInformation
    
    Shell "explorer.exe /select,""" & csvPath & """", vbNormalFocus
    Exit Sub

ErrorHandler:
    Close #f
    Application.StatusBar = False
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub

Private Function GetBeamInfo(frameName As String, _
    ByRef outLabel As String, ByRef outStory As String, _
    ByRef outWidth As Double, ByRef outDepth As Double, _
    ByRef outSpan As Double, ByRef outMuMax As Double, _
    ByRef outMuMin As Double, ByRef outVuMax As Double) As Boolean
    
    ' Returns True if this is a valid beam, False if column or invalid
    
    On Error Resume Next
    Dim ret As Long
    
    GetBeamInfo = False
    outLabel = frameName
    
    ' --- Get Points ---
    Dim point1 As String, point2 As String
    ret = mySapModel.FrameObj.GetPoints(frameName, point1, point2)
    If ret <> 0 Then Exit Function
    
    ' --- Get Story ---
    Dim tempLabel As String, tempStory As String
    ret = mySapModel.PointObj.GetLabelFromName(point1, tempLabel, tempStory)
    If ret = 0 Then
        outStory = tempStory
    Else
        outStory = "Unknown"
    End If
    
    ' --- Get Coordinates ---
    Dim x1 As Double, y1 As Double, z1 As Double
    Dim x2 As Double, y2 As Double, z2 As Double
    
    ret = mySapModel.PointObj.GetCoordCartesian(point1, x1, y1, z1)
    ret = mySapModel.PointObj.GetCoordCartesian(point2, x2, y2, z2)
    
    ' Calculate span
    outSpan = Sqr((x2 - x1) ^ 2 + (y2 - y1) ^ 2 + (z2 - z1) ^ 2)
    
    ' Check if column (mostly vertical)
    Dim dz As Double, dxy As Double
    dz = Abs(z2 - z1)
    dxy = Sqr((x2 - x1) ^ 2 + (y2 - y1) ^ 2)
    
    If dz > dxy Then
        ' More vertical than horizontal = column, skip
        Exit Function
    End If
    
    ' --- Get Section ---
    Dim sectName As String, sAuto As String
    ret = mySapModel.FrameObj.GetSection(frameName, sectName, sAuto)
    If ret <> 0 Then Exit Function
    
    ' Get dimensions (rectangular)
    Dim fileName As String, matProp As String
    Dim t3 As Double, t2 As Double
    Dim color As Long, notes As String, guid As String
    
    ret = mySapModel.PropFrame.GetRectangle(sectName, fileName, matProp, _
        t3, t2, color, notes, guid)
    
    If ret = 0 And t2 > 0 And t3 > 0 Then
        If t2 < 1 Then
            outWidth = t2 * 1000  ' m to mm
            outDepth = t3 * 1000
        Else
            outWidth = t2
            outDepth = t3
        End If
    Else
        outWidth = 230  ' Default
        outDepth = 450
    End If
    
    ' --- Get Forces ---
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
    
    If ret <> 0 Or NumberResults = 0 Then
        outMuMax = 0
        outMuMin = 0
        outVuMax = 0
    Else
        ' Find envelope
        outMuMax = M3(0)
        outMuMin = M3(0)
        outVuMax = Abs(V2(0))
        
        Dim j As Long
        For j = 1 To NumberResults - 1
            If M3(j) > outMuMax Then outMuMax = M3(j)
            If M3(j) < outMuMin Then outMuMin = M3(j)
            If Abs(V2(j)) > outVuMax Then outVuMax = Abs(V2(j))
        Next j
    End If
    
    GetBeamInfo = True
End Function

Private Sub SelectAllCases()
    Dim ret As Long
    Dim NumberItems As Long
    Dim ItemName() As String
    Dim c As Long
    
    ' Load cases
    ret = mySapModel.LoadCases.GetNameList(NumberItems, ItemName)
    For c = 0 To NumberItems - 1
        ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(ItemName(c))
    Next c
    Debug.Print "Selected " & NumberItems & " load cases"
    
    ' Load combos
    ret = mySapModel.RespCombo.GetNameList(NumberItems, ItemName)
    For c = 0 To NumberItems - 1
        ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ItemName(c))
    Next c
    Debug.Print "Selected " & NumberItems & " load combos"
End Sub
