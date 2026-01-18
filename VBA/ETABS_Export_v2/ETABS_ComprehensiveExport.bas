' =============================================================================
' ETABS Comprehensive Export for 3D Visualization (v1.0)
' =============================================================================
' Author: Pravin Surawase
' Date: 2025-01-27
' Purpose: Export all data needed for Streamlit 3D visualization
' =============================================================================
'
' EXPORTS:
'   1. frames_geometry.csv    - Frame coordinates, connectivity, type
'   2. frames_properties.csv  - Section dimensions (unique sections only)
'   3. beam_forces.csv        - Envelope M3, V2 for beams
'   4. stories.csv            - Story names, heights, elevations
'
' REQUIREMENTS:
'   1. ETABS model must be open with analysis complete
'   2. Design must be run (or will be started automatically)
'   3. Add reference: Tools > References > ETABS.exe
'
' USAGE:
'   1. Open ETABS model
'   2. Run analysis
'   3. Alt+F11 > Insert > Module > Paste this code
'   4. Add ETABS reference
'   5. Run: ExportAllForVisualization
'
' =============================================================================

Option Explicit

' Module-level ETABS objects
Private myHelper As ETABSv1.cHelper
Private myETABSObject As ETABSv1.cOAPI
Private mySapModel As ETABSv1.cSapModel

' Configuration
Private Const OUTPUT_FOLDER As String = "ETABS_Export"  ' In Documents folder
Private Const EXPORT_BEAM_FORCES As Boolean = True       ' Set False to skip forces

' =============================================================================
' MAIN EXPORT FUNCTION
' =============================================================================

Public Sub ExportAllForVisualization()
    ' Main entry point - exports all data for 3D visualization
    
    Dim startTime As Double
    startTime = Timer
    
    ' Connect to ETABS
    If Not ConnectToETABS() Then
        MsgBox "Failed to connect to ETABS. Make sure ETABS is running.", vbCritical
        Exit Sub
    End If
    
    ' Set units to kN, m, C
    mySapModel.SetPresentUnits eUnits_kN_m_C
    
    ' Create output folder
    Dim outputPath As String
    outputPath = CreateOutputFolder()
    If outputPath = "" Then
        MsgBox "Failed to create output folder.", vbCritical
        Exit Sub
    End If
    
    ' Export each data type
    Dim framesCount As Long
    Dim propsCount As Long
    Dim storiesCount As Long
    Dim beamsCount As Long
    
    ' 1. Export stories first (needed for context)
    storiesCount = ExportStories(outputPath)
    Debug.Print "Exported " & storiesCount & " stories"
    
    ' 2. Export frame geometry (main export)
    framesCount = ExportFrameGeometry(outputPath)
    Debug.Print "Exported " & framesCount & " frames"
    
    ' 3. Export section properties (unique sections)
    propsCount = ExportSectionProperties(outputPath)
    Debug.Print "Exported " & propsCount & " section properties"
    
    ' 4. Export beam forces (optional, slowest operation)
    If EXPORT_BEAM_FORCES Then
        beamsCount = ExportBeamForces(outputPath)
        Debug.Print "Exported " & beamsCount & " beam force records"
    End If
    
    ' Summary
    Dim elapsed As Double
    elapsed = Timer - startTime
    
    MsgBox "Export Complete!" & vbCrLf & vbCrLf & _
           "Frames: " & framesCount & vbCrLf & _
           "Sections: " & propsCount & vbCrLf & _
           "Stories: " & storiesCount & vbCrLf & _
           IIf(EXPORT_BEAM_FORCES, "Beam Forces: " & beamsCount & vbCrLf, "") & _
           vbCrLf & _
           "Time: " & Format(elapsed, "0.0") & " seconds" & vbCrLf & _
           "Path: " & outputPath, _
           vbInformation, "ETABS Export"
End Sub

' =============================================================================
' CONNECT TO ETABS
' =============================================================================

Private Function ConnectToETABS() As Boolean
    ' Connect to running ETABS instance
    On Error GoTo ErrHandler
    
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = Nothing
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    ConnectToETABS = True
    Exit Function
    
ErrHandler:
    Debug.Print "ConnectToETABS Error: " & Err.Description
    ConnectToETABS = False
End Function

' =============================================================================
' CREATE OUTPUT FOLDER
' =============================================================================

Private Function CreateOutputFolder() As String
    ' Create output folder in Documents
    On Error Resume Next
    
    Dim basePath As String
    basePath = Environ("USERPROFILE") & "\Documents\" & OUTPUT_FOLDER
    
    ' Create folder if not exists
    If Dir(basePath, vbDirectory) = "" Then
        MkDir basePath
    End If
    
    ' Create timestamp subfolder
    Dim timestamp As String
    timestamp = Format(Now, "yyyy-mm-dd_HHmmss")
    Dim fullPath As String
    fullPath = basePath & "\" & timestamp
    MkDir fullPath
    
    If Dir(fullPath, vbDirectory) <> "" Then
        CreateOutputFolder = fullPath
    Else
        CreateOutputFolder = ""
    End If
End Function

' =============================================================================
' EXPORT STORIES
' =============================================================================

Private Function ExportStories(ByVal outputPath As String) As Long
    ' Export story names and elevations
    ' Pattern from legacy BeamType.bas and ShearWall.bas
    Dim ret As Long
    Dim i As Long
    
    ' Get story names
    Dim NumberStories As Long
    Dim StoryNames() As String
    ret = mySapModel.Story.GetNameList(NumberStories, StoryNames)
    
    If ret <> 0 Or NumberStories = 0 Then
        ExportStories = 0
        Exit Function
    End If
    
    ' Write CSV
    Dim fileNum As Integer
    fileNum = FreeFile
    Open outputPath & "\stories.csv" For Output As #fileNum
    
    ' Header
    Print #fileNum, "StoryName,Elevation_m"
    
    ' Get elevation for each story
    Dim StoryElev As Double
    For i = 0 To NumberStories - 1
        ret = mySapModel.Story.GetElevation(StoryNames(i), StoryElev)
        If ret = 0 Then
            Print #fileNum, StoryNames(i) & "," & Format(StoryElev, "0.000")
        End If
    Next i
    
    Close #fileNum
    ExportStories = NumberStories
End Function

' =============================================================================
' EXPORT FRAME GEOMETRY
' =============================================================================

Private Function ExportFrameGeometry(ByVal outputPath As String) As Long
    ' Export frame coordinates, connectivity, type using GetAllFrames
    Dim ret As Long
    Dim i As Long
    
    ' GetAllFrames - efficient single API call
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String
    Dim StoryName() As String
    Dim PointName1() As String
    Dim PointName2() As String
    Dim Point1X() As Double
    Dim Point1Y() As Double
    Dim Point1Z() As Double
    Dim Point2X() As Double
    Dim Point2Y() As Double
    Dim Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double
    Dim Offset2X() As Double
    Dim Offset1Y() As Double
    Dim Offset2Y() As Double
    Dim Offset1Z() As Double
    Dim Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, _
            StoryName, PointName1, PointName2, _
            Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
            Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, _
            CardinalPoint)
    
    If ret <> 0 Or NumberNames = 0 Then
        ExportFrameGeometry = 0
        Exit Function
    End If
    
    ' Open CSV
    Dim fileNum As Integer
    fileNum = FreeFile
    Open outputPath & "\frames_geometry.csv" For Output As #fileNum
    
    ' Header
    Print #fileNum, "UniqueName,Label,Story,FrameType,SectionName," & _
                    "Point1Name,Point2Name," & _
                    "Point1X,Point1Y,Point1Z,Point2X,Point2Y,Point2Z," & _
                    "Angle,CardinalPoint"
    
    ' Variables for frame type detection
    Dim Frame_Type As Long
    Dim FrameTypeName As String
    Dim Label As String
    Dim StoryFromLabel As String
    
    For i = 0 To NumberNames - 1
        ' Skip dummy sections
        If PropName(i) = "DUMMY" Or PropName(i) = "Stiff Beam" Then
            GoTo NextFrame
        End If
        
        ' Get frame type (1=Column, 2=Beam)
        ret = mySapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)
        Select Case Frame_Type
            Case 1
                FrameTypeName = "Column"
            Case 2
                FrameTypeName = "Beam"
            Case Else
                FrameTypeName = "Other"
        End Select
        
        ' Get user-friendly label
        ret = mySapModel.FrameObj.GetLabelFromName(MyName(i), Label, StoryFromLabel)
        If ret <> 0 Then Label = MyName(i)
        
        ' Write row
        Print #fileNum, MyName(i) & "," & _
                        Label & "," & _
                        StoryName(i) & "," & _
                        FrameTypeName & "," & _
                        PropName(i) & "," & _
                        PointName1(i) & "," & _
                        PointName2(i) & "," & _
                        Format(Point1X(i), "0.000") & "," & _
                        Format(Point1Y(i), "0.000") & "," & _
                        Format(Point1Z(i), "0.000") & "," & _
                        Format(Point2X(i), "0.000") & "," & _
                        Format(Point2Y(i), "0.000") & "," & _
                        Format(Point2Z(i), "0.000") & "," & _
                        Format(Angle(i), "0.00") & "," & _
                        CardinalPoint(i)
NextFrame:
    Next i
    
    Close #fileNum
    ExportFrameGeometry = NumberNames
End Function

' =============================================================================
' EXPORT SECTION PROPERTIES
' =============================================================================

Private Function ExportSectionProperties(ByVal outputPath As String) As Long
    ' Export unique section dimensions (from GetAllFrames PropNames)
    Dim ret As Long
    Dim i As Long
    
    ' First get all frames to find unique sections
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String
    Dim StoryName() As String
    Dim PointName1() As String
    Dim PointName2() As String
    Dim Point1X() As Double
    Dim Point1Y() As Double
    Dim Point1Z() As Double
    Dim Point2X() As Double
    Dim Point2Y() As Double
    Dim Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double
    Dim Offset2X() As Double
    Dim Offset1Y() As Double
    Dim Offset2Y() As Double
    Dim Offset1Z() As Double
    Dim Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, _
            StoryName, PointName1, PointName2, _
            Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
            Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, _
            CardinalPoint)
    
    If ret <> 0 Or NumberNames = 0 Then
        ExportSectionProperties = 0
        Exit Function
    End If
    
    ' Build unique sections list using Collection (VBA's simple way to avoid duplicates)
    Dim uniqueSections As Collection
    Set uniqueSections = New Collection
    
    On Error Resume Next  ' Ignore duplicate key errors
    For i = 0 To NumberNames - 1
        If PropName(i) <> "DUMMY" And PropName(i) <> "Stiff Beam" Then
            uniqueSections.Add PropName(i), PropName(i)  ' Key = section name
        End If
    Next i
    On Error GoTo 0
    
    ' Open CSV
    Dim fileNum As Integer
    fileNum = FreeFile
    Open outputPath & "\frames_properties.csv" For Output As #fileNum
    
    ' Header
    Print #fileNum, "SectionName,Width_mm,Depth_mm,Material,FrameType"
    
    ' Get dimensions for each unique section
    Dim sectionName As Variant
    Dim FileName As String
    Dim MatProp As String
    Dim t3 As Double  ' Depth
    Dim t2 As Double  ' Width
    Dim Color As Long
    Dim Notes As String
    Dim GUID As String
    Dim Frame_Type As Long
    Dim FrameTypeName As String
    Dim propCount As Long
    
    For Each sectionName In uniqueSections
        ' Get section dimensions
        ret = mySapModel.PropFrame.GetRectangle(CStr(sectionName), FileName, MatProp, _
                                                 t3, t2, Color, Notes, GUID)
        
        ' Get frame type
        ret = mySapModel.PropFrame.GetTypeRebar(CStr(sectionName), Frame_Type)
        Select Case Frame_Type
            Case 1
                FrameTypeName = "Column"
            Case 2
                FrameTypeName = "Beam"
            Case Else
                FrameTypeName = "Other"
        End Select
        
        ' Write row (convert m to mm)
        Print #fileNum, sectionName & "," & _
                        Format(t2 * 1000, "0") & "," & _
                        Format(t3 * 1000, "0") & "," & _
                        MatProp & "," & _
                        FrameTypeName
        
        propCount = propCount + 1
    Next sectionName
    
    Close #fileNum
    ExportSectionProperties = propCount
End Function

' =============================================================================
' EXPORT BEAM FORCES (Envelope M3, V2)
' =============================================================================

Private Function ExportBeamForces(ByVal outputPath As String) As Long
    ' Export envelope forces for beams (same logic as SimpleExport)
    Dim ret As Long
    Dim i As Long, j As Long
    
    ' Get all frames
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String
    Dim StoryName() As String
    Dim PointName1() As String
    Dim PointName2() As String
    Dim Point1X() As Double
    Dim Point1Y() As Double
    Dim Point1Z() As Double
    Dim Point2X() As Double
    Dim Point2Y() As Double
    Dim Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double
    Dim Offset2X() As Double
    Dim Offset1Y() As Double
    Dim Offset2Y() As Double
    Dim Offset1Z() As Double
    Dim Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, _
            StoryName, PointName1, PointName2, _
            Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
            Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, _
            CardinalPoint)
    
    If ret <> 0 Or NumberNames = 0 Then
        ExportBeamForces = 0
        Exit Function
    End If
    
    ' Setup analysis results
    ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput
    
    ' Select all load cases
    Dim numCases As Long
    Dim caseNames() As String
    ret = mySapModel.LoadCases.GetNameList(numCases, caseNames)
    If ret = 0 And numCases > 0 Then
        For i = 0 To numCases - 1
            mySapModel.Results.Setup.SetCaseSelectedForOutput caseNames(i)
        Next i
    End If
    
    ' Select all combos
    Dim numCombos As Long
    Dim comboNames() As String
    ret = mySapModel.RespCombo.GetNameList(numCombos, comboNames)
    If ret = 0 And numCombos > 0 Then
        For i = 0 To numCombos - 1
            mySapModel.Results.Setup.SetComboSelectedForOutput comboNames(i)
        Next i
    End If
    
    ' Open CSV
    Dim fileNum As Integer
    fileNum = FreeFile
    Open outputPath & "\beam_forces.csv" For Output As #fileNum
    
    ' Header
    Print #fileNum, "UniqueName,Label,Story,SectionName,Width_mm,Depth_mm,Span_m," & _
                    "Mu_max_kNm,Mu_min_kNm,Vu_max_kN"
    
    ' Process each frame
    Dim Frame_Type As Long
    Dim Label As String
    Dim StoryFromLabel As String
    Dim beamCount As Long
    
    ' Section dimensions
    Dim FileName As String
    Dim MatProp As String
    Dim t3 As Double, t2 As Double
    Dim Color As Long
    Dim Notes As String
    Dim GUID As String
    
    ' Force results
    Dim NumberResults As Long
    Dim Obj() As String
    Dim ObjSta() As Double
    Dim Elm() As String
    Dim ElmSta() As Double
    Dim LoadCase() As String
    Dim StepType() As String
    Dim StepNum() As Double
    Dim P() As Double
    Dim V2() As Double
    Dim V3() As Double
    Dim T() As Double
    Dim M2() As Double
    Dim M3() As Double
    
    For i = 0 To NumberNames - 1
        ' Skip non-beams
        If PropName(i) = "DUMMY" Or PropName(i) = "Stiff Beam" Then
            GoTo NextBeam
        End If
        
        ret = mySapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)
        If Frame_Type <> 2 Then GoTo NextBeam  ' Only beams
        
        ' Get label
        ret = mySapModel.FrameObj.GetLabelFromName(MyName(i), Label, StoryFromLabel)
        If ret <> 0 Then Label = MyName(i)
        
        ' Get section dimensions
        ret = mySapModel.PropFrame.GetRectangle(PropName(i), FileName, MatProp, _
                                                 t3, t2, Color, Notes, GUID)
        
        ' Calculate span
        Dim span As Double
        span = Sqr((Point2X(i) - Point1X(i)) ^ 2 + _
                   (Point2Y(i) - Point1Y(i)) ^ 2 + _
                   (Point2Z(i) - Point1Z(i)) ^ 2)
        
        ' Get forces
        ret = mySapModel.Results.FrameForce(MyName(i), eItemTypeElm_ObjectElm, _
                NumberResults, Obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
                P, V2, V3, T, M2, M3)
        
        If ret <> 0 Or NumberResults = 0 Then GoTo NextBeam
        
        ' Calculate envelope values
        Dim M3_max As Double, M3_min As Double, V2_max As Double
        M3_max = M3(0)
        M3_min = M3(0)
        V2_max = Abs(V2(0))
        
        For j = 1 To NumberResults - 1
            If M3(j) > M3_max Then M3_max = M3(j)
            If M3(j) < M3_min Then M3_min = M3(j)
            If Abs(V2(j)) > V2_max Then V2_max = Abs(V2(j))
        Next j
        
        ' Write row
        Print #fileNum, MyName(i) & "," & _
                        Label & "," & _
                        StoryName(i) & "," & _
                        PropName(i) & "," & _
                        Format(t2 * 1000, "0") & "," & _
                        Format(t3 * 1000, "0") & "," & _
                        Format(span, "0.000") & "," & _
                        Format(M3_max, "0.000") & "," & _
                        Format(M3_min, "0.000") & "," & _
                        Format(V2_max, "0.000")
        
        beamCount = beamCount + 1
        
NextBeam:
    Next i
    
    Close #fileNum
    ExportBeamForces = beamCount
End Function

' =============================================================================
' QUICK EXPORT (Without Forces - Faster)
' =============================================================================

Public Sub ExportGeometryOnly()
    ' Export only geometry (faster, no forces)
    ' Use this for quick 3D visualization without design data
    
    Dim startTime As Double
    startTime = Timer
    
    ' Connect to ETABS
    If Not ConnectToETABS() Then
        MsgBox "Failed to connect to ETABS. Make sure ETABS is running.", vbCritical
        Exit Sub
    End If
    
    mySapModel.SetPresentUnits eUnits_kN_m_C
    
    ' Create output folder
    Dim outputPath As String
    outputPath = CreateOutputFolder()
    If outputPath = "" Then
        MsgBox "Failed to create output folder.", vbCritical
        Exit Sub
    End If
    
    ' Export geometry only
    Dim storiesCount As Long
    Dim framesCount As Long
    Dim propsCount As Long
    
    storiesCount = ExportStories(outputPath)
    framesCount = ExportFrameGeometry(outputPath)
    propsCount = ExportSectionProperties(outputPath)
    
    Dim elapsed As Double
    elapsed = Timer - startTime
    
    MsgBox "Geometry Export Complete!" & vbCrLf & vbCrLf & _
           "Frames: " & framesCount & vbCrLf & _
           "Sections: " & propsCount & vbCrLf & _
           "Stories: " & storiesCount & vbCrLf & _
           vbCrLf & _
           "Time: " & Format(elapsed, "0.0") & " seconds" & vbCrLf & _
           "Path: " & outputPath, _
           vbInformation, "ETABS Export"
End Sub
