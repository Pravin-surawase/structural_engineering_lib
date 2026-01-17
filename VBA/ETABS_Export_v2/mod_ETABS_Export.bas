Attribute VB_Name = "mod_ETABS_Export"
Option Explicit

'==============================================================================
' ETABS EXPORT - DATA EXPORT MODULE v2.2
'==============================================================================
' Purpose: Export all ETABS data to Excel worksheet first, then to CSV files
'
' Exports:
'   - Beam Forces (PRIMARY - required for Streamlit)
'   - Base Reactions
'   - Column Design Results
'   - Beam Design Results
'   - Sections
'   - Stories
'
' v2.2 Changes (fixes from legacy code analysis):
'   - Write to Excel worksheet first, then export to CSV
'   - Use SetCaseSelectedForOutput for load cases
'   - Use SetComboSelectedForOutput for load combinations (separate!)
'   - Better error handling for "No load cases" issue
'
' Based on:
'   - Legacy working code (2019-2021)
'   - ETABS API patterns from CSI documentation
'   - Efficient GetAllFrames pattern
'
' Author: Pravin Surawase
' License: MIT
' Version: 2.2.0
'==============================================================================

'------------------------------------------------------------------------------
' BEAM FORCES EXPORT (PRIMARY)
' This is the main export for Streamlit app
'------------------------------------------------------------------------------

' Export beam forces - tries DatabaseTables first, falls back to Direct API
Public Function ExportBeamForces(sapModel As Object, folder As String, units As UnitConversion) As Boolean
    On Error GoTo ExportError
    
    Dim csvPath As String
    csvPath = folder & "\beam_forces.csv"
    
    LogInfo "Exporting beam forces to: " & csvPath
    
    ' Method 1: Try DatabaseTables (fastest)
    Dim success As Boolean
    success = ExportForcesDatabaseTables(sapModel, csvPath)
    
    If success Then
        LogInfo "? Beam forces exported (DatabaseTables method)"
        ExportBeamForces = True
        Exit Function
    End If
    
    ' Method 2: Fallback to Direct API
    LogWarning "DatabaseTables failed, using Direct API..."
    success = ExportForcesDirectAPI(sapModel, csvPath, units)
    
    If success Then
        LogInfo "? Beam forces exported (Direct API method)"
        ExportBeamForces = True
    Else
        LogError "Both export methods failed"
        ExportBeamForces = False
    End If
    Exit Function

ExportError:
    LogError "ExportBeamForces error: " & Err.Description
    ExportBeamForces = False
End Function

' Method 1: DatabaseTables export (fastest)
Private Function ExportForcesDatabaseTables(sapModel As Object, csvPath As String) As Boolean
    On Error Resume Next
    
    ' Try multiple table name variants (ETABS versions differ)
    Dim tableNames() As Variant
    tableNames = Array( _
        "Element Forces - Frames", _
        "Element Forces-Frames", _
        "Frame Element Forces", _
        "Frame Forces")
    
    Dim ret As Long
    Dim tableName As Variant
    
    For Each tableName In tableNames
        Err.Clear
        LogDebug "Trying table: " & tableName
        
        ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
            CStr(tableName), csvPath, False, 0, "")
        
        If Err.Number = 0 And ret = 0 Then
            If FileExists(csvPath) Then
                Dim rows As Long
                rows = CountCSVRows(csvPath)
                If rows > 1 Then
                    LogInfo "  Table '" & tableName & "' exported: " & rows & " rows"
                    ExportForcesDatabaseTables = True
                    Exit Function
                End If
            End If
        End If
    Next
    
    ExportForcesDatabaseTables = False
End Function

' Method 2: Direct API export (more reliable, slower)
' Fixed v2.3: Don't enumerate cases - use ItemTypeElm=0 to get ALL results
Private Function ExportForcesDirectAPI(sapModel As Object, csvPath As String, units As UnitConversion) As Boolean
    On Error GoTo DirectError
    
    LogInfo "Using Direct API method..."
    
    ' *** FIX: Don't try to enumerate/select cases ***
    ' The legacy code doesn't do this! It just calls Results.FrameForce
    ' with ItemTypeElm=0 which returns ALL load cases automatically
    
    ' Get ALL frames efficiently (from legacy COLUMNS.bas pattern)
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String, StoryName() As String
    Dim PointName1() As String, PointName2() As String
    Dim Point1X() As Double, Point1Y() As Double, Point1Z() As Double
    Dim Point2X() As Double, Point2Y() As Double, Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double, Offset2X() As Double
    Dim Offset1Y() As Double, Offset2Y() As Double
    Dim Offset1Z() As Double, Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    LogDebug "Calling FrameObj.GetAllFrames..."
    
    Dim ret As Long
    On Error Resume Next
    ret = sapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
        PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
        Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
    
    If Err.Number <> 0 Then
        LogError "GetAllFrames error: " & Err.Description & " (#" & Err.Number & ")"
        ExportForcesDirectAPI = False
        Exit Function
    End If
    On Error GoTo DirectError
    
    If ret <> 0 Or NumberNames = 0 Then
        LogError "GetAllFrames failed: ret=" & ret & ", NumberNames=" & NumberNames
        ExportForcesDirectAPI = False
        Exit Function
    End If
    
    LogInfo "Found " & NumberNames & " frames"
    
    ' *** EXCEL-FIRST PATTERN: Write to Excel worksheet first ***
    Dim ws As Worksheet
    Set ws = GetExportWorksheet()
    If ws Is Nothing Then
        ' Fallback to direct CSV if no worksheet
        LogWarning "No Excel worksheet - writing directly to CSV"
        ExportForcesDirectAPI = ExportForcesDirectToCSV(sapModel, csvPath, units, MyName, PropName, StoryName, NumberNames)
        Exit Function
    End If
    
    ' Write header to Excel
    ws.Cells.Clear
    ws.Range("A1").Value = "Story"
    ws.Range("B1").Value = "Label"
    ws.Range("C1").Value = "Output Case"
    ws.Range("D1").Value = "Station"
    ws.Range("E1").Value = "M3"
    ws.Range("F1").Value = "V2"
    ws.Range("G1").Value = "P"
    
    Dim rowNum As Long
    rowNum = 2  ' Start after header
    
    Dim i As Long
    
    For i = LBound(MyName) To UBound(MyName)
        ' Get forces for this frame
        ' *** KEY FIX: Use ItemTypeElm=0 (Object element) to get ALL cases ***
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim t() As Double, M2() As Double, M3() As Double
        
        ' Log first frame attempt
        If i = LBound(MyName) Then
            LogDebug "Calling Results.FrameForce for first frame: " & MyName(i)
        End If
        
        On Error Resume Next
        ret = sapModel.Results.FrameForce( _
            MyName(i), 0, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, t, M2, M3)
        
        ' Check for errors on first frame
        If i = LBound(MyName) Then
            If Err.Number <> 0 Then
                LogError "Results.FrameForce error on first frame: " & Err.Description & " (#" & Err.Number & ")"
                LogError "This API call may not be supported in your ETABS version"
                ExportForcesDirectAPI = False
                Exit Function
            ElseIf ret <> 0 Then
                LogError "Results.FrameForce returned ret=" & ret & " on first frame"
                ExportForcesDirectAPI = False
                Exit Function
            Else
                LogDebug "Results.FrameForce succeeded: " & NumberResults & " results"
            End If
        End If
        
        If Err.Number = 0 And ret = 0 And NumberResults > 0 Then
            Dim j As Long
            For j = LBound(LoadCase) To UBound(LoadCase)
                ' Write to Excel (already in kN, m since we set units)
                ws.Cells(rowNum, 1).Value = StoryName(i)
                ws.Cells(rowNum, 2).Value = MyName(i)
                ws.Cells(rowNum, 3).Value = LoadCase(j)
                ws.Cells(rowNum, 4).Value = Round(ElmSta(j) * units.LengthToMM, 3)
                ws.Cells(rowNum, 5).Value = Round(M3(j) * units.MomentToKNM, 3)
                ws.Cells(rowNum, 6).Value = Round(V2(j) * units.ForceToKN, 3)
                ws.Cells(rowNum, 7).Value = Round(P(j) * units.ForceToKN, 3)
                rowNum = rowNum + 1
            Next j
        End If
        On Error GoTo DirectError
        
        ' Progress
        If i Mod 50 = 0 Then
            Application.StatusBar = "Exporting: " & i & "/" & NumberNames & " frames"
            DoEvents
        End If
    Next i
    
    Dim totalRows As Long
    totalRows = rowNum - 2  ' Subtract header and 1-based offset
    
    LogInfo "Written " & totalRows & " records to Excel"
    
    ' *** Now export Excel range to CSV ***
    If totalRows > 0 Then
        Call ExportRangeToCSV(ws, csvPath, 1, 7, rowNum - 1)
        LogInfo "? Exported to CSV: " & csvPath
        ExportForcesDirectAPI = True
    Else
        LogWarning "No force data retrieved"
        ExportForcesDirectAPI = False
    End If
    Exit Function

DirectError:
    LogError "Direct API error: " & Err.Description
    ExportForcesDirectAPI = False
End Function

' Export Excel range to CSV file
Private Sub ExportRangeToCSV(ws As Worksheet, csvPath As String, startRow As Long, numCols As Long, endRow As Long)
    On Error GoTo ExportError
    
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    Dim r As Long, c As Long
    Dim lineStr As String
    
    For r = startRow To endRow
        lineStr = ""
        For c = 1 To numCols
            If c > 1 Then lineStr = lineStr & ","
            lineStr = lineStr & CStr(ws.Cells(r, c).Value)
        Next c
        Print #f, lineStr
    Next r
    
    Close #f
    Exit Sub
    
ExportError:
    On Error Resume Next
    Close #f
    LogError "ExportRangeToCSV error: " & Err.Description
End Sub

' Fallback: Direct to CSV (if no Excel worksheet available)
Private Function ExportForcesDirectToCSV(sapModel As Object, csvPath As String, units As UnitConversion, _
    MyName() As String, PropName() As String, StoryName() As String, NumberNames As Long) As Boolean
    
    On Error GoTo WriteError
    
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    ' Header
    Print #f, "Story,Label,Output Case,Station,M3,V2,P"
    
    Dim i As Long, totalRows As Long
    totalRows = 0
    
    For i = LBound(MyName) To UBound(MyName)
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim t() As Double, M2() As Double, M3() As Double
        Dim ret As Long
        
        On Error Resume Next
        ret = sapModel.Results.FrameForce( _
            MyName(i), 0, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, t, M2, M3)
        
        If Err.Number = 0 And ret = 0 And NumberResults > 0 Then
            Dim j As Long
            For j = LBound(LoadCase) To UBound(LoadCase)
                Print #f, _
                    StoryName(i) & "," & _
                    MyName(i) & "," & _
                    LoadCase(j) & "," & _
                    Format(ElmSta(j) * units.LengthToMM, "0.000") & "," & _
                    Format(M3(j) * units.MomentToKNM, "0.000") & "," & _
                    Format(V2(j) * units.ForceToKN, "0.000") & "," & _
                    Format(P(j) * units.ForceToKN, "0.000")
                totalRows = totalRows + 1
            Next j
        End If
        On Error GoTo WriteError
    Next i
    
    Close #f
    
    LogInfo "Exported " & totalRows & " force records (direct CSV)"
    ExportForcesDirectToCSV = (totalRows > 0)
    Exit Function

WriteError:
    On Error Resume Next
    Close #f
    LogError "Direct CSV error: " & Err.Description
    ExportForcesDirectToCSV = False
End Function

'------------------------------------------------------------------------------
' BASE REACTIONS EXPORT
' From legacy BASE_REACTIONS.bas pattern - Simplified v2.3
'------------------------------------------------------------------------------

Public Function ExportBaseReactions(sapModel As Object, folder As String, units As UnitConversion) As Boolean
    On Error GoTo ReactionError
    
    Dim csvPath As String
    csvPath = folder & "\base_reactions.csv"
    
    LogInfo "Exporting base reactions..."
    
    ' *** FIX: Don't enumerate cases - just call BaseReact ***
    ' The legacy code gets case names from Excel, we'll get all results
    
    Dim ret As Long
    
    ' Get base reactions (returns all analyzed cases)
    Dim NumberResults As Long
    Dim LoadCase() As String, StepType() As String, StepNum() As Double
    Dim Fx() As Double, Fy() As Double, Fz() As Double
    Dim Mx() As Double, My() As Double, Mz() As Double
    Dim gx() As Double, gy() As Double, gz() As Double
    
    ret = sapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, _
        Fx, Fy, Fz, Mx, My, Mz, gx, gy, gz)
    
    If ret <> 0 Or NumberResults = 0 Then
        LogWarning "No base reactions available (ret=" & ret & ", n=" & NumberResults & ")"
        ExportBaseReactions = False
        Exit Function
    End If
    
    ' Write to Excel first
    Dim ws As Worksheet
    Set ws = GetExportWorksheet()
    
    If Not ws Is Nothing Then
        ' Find next available section in worksheet
        Dim startRow As Long
        startRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 3
        
        ws.Cells(startRow, 1).Value = "=== BASE REACTIONS ==="
        startRow = startRow + 1
        
        ws.Cells(startRow, 1).Value = "LoadCase"
        ws.Cells(startRow, 2).Value = "Fx_kN"
        ws.Cells(startRow, 3).Value = "Fy_kN"
        ws.Cells(startRow, 4).Value = "Fz_kN"
        ws.Cells(startRow, 5).Value = "Mx_kNm"
        ws.Cells(startRow, 6).Value = "My_kNm"
        ws.Cells(startRow, 7).Value = "Mz_kNm"
        
        Dim i As Long
        For i = LBound(LoadCase) To UBound(LoadCase)
            startRow = startRow + 1
            ws.Cells(startRow, 1).Value = LoadCase(i)
            ws.Cells(startRow, 2).Value = Round(Fx(i) * units.ForceToKN, 2)
            ws.Cells(startRow, 3).Value = Round(Fy(i) * units.ForceToKN, 2)
            ws.Cells(startRow, 4).Value = Round(Fz(i) * units.ForceToKN, 2)
            ws.Cells(startRow, 5).Value = Round(Mx(i) * units.MomentToKNM, 2)
            ws.Cells(startRow, 6).Value = Round(My(i) * units.MomentToKNM, 2)
            ws.Cells(startRow, 7).Value = Round(Mz(i) * units.MomentToKNM, 2)
        Next i
    End If
    
    ' Write CSV
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    Print #f, "LoadCase,Fx_kN,Fy_kN,Fz_kN,Mx_kNm,My_kNm,Mz_kNm"
    
    For i = LBound(LoadCase) To UBound(LoadCase)
        Print #f, _
            LoadCase(i) & "," & _
            Format(Fx(i) * units.ForceToKN, "0.00") & "," & _
            Format(Fy(i) * units.ForceToKN, "0.00") & "," & _
            Format(Fz(i) * units.ForceToKN, "0.00") & "," & _
            Format(Mx(i) * units.MomentToKNM, "0.00") & "," & _
            Format(My(i) * units.MomentToKNM, "0.00") & "," & _
            Format(Mz(i) * units.MomentToKNM, "0.00")
    Next i
    
    Close #f
    
    LogInfo "? Base reactions: " & NumberResults & " entries"
    ExportBaseReactions = True
    Exit Function

ReactionError:
    LogWarning "Base reactions error: " & Err.Description
    ExportBaseReactions = False
End Function

'------------------------------------------------------------------------------
' COLUMN DESIGN RESULTS
' From legacy COLUMNS.bas pattern
'------------------------------------------------------------------------------

Public Function ExportColumnDesignResults(sapModel As Object, folder As String) As Boolean
    On Error GoTo DesignError
    
    Dim csvPath As String
    csvPath = folder & "\column_design.csv"
    
    LogInfo "Exporting column design results..."
    
    ' Check if design results available
    Dim ResultsAvailable As Boolean
    On Error Resume Next
    ResultsAvailable = sapModel.DesignConcrete.GetResultsAvailable
    On Error GoTo DesignError
    
    If Not ResultsAvailable Then
        LogWarning "Column design not run - skipping"
        ExportColumnDesignResults = False
        Exit Function
    End If
    
    ' Get all frames
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String, StoryName() As String
    Dim PointName1() As String, PointName2() As String
    Dim Point1X() As Double, Point1Y() As Double, Point1Z() As Double
    Dim Point2X() As Double, Point2Y() As Double, Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double, Offset2X() As Double
    Dim Offset1Y() As Double, Offset2Y() As Double
    Dim Offset1Z() As Double, Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    Dim ret As Long
    ret = sapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
        PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
        Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
    
    If ret <> 0 Or NumberNames = 0 Then
        LogWarning "Cannot get frames"
        ExportColumnDesignResults = False
        Exit Function
    End If
    
    ' Create CSV
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    Print #f, "Story,Label,Section,Location,PMMCombo,PMMRatio,VmajorCombo,AVmajor,Error,Warning"
    
    Dim i As Long, colCount As Long
    colCount = 0
    
    For i = LBound(MyName) To UBound(MyName)
        ' Check if column (Frame_Type = 1)
        Dim Frame_Type As Long
        On Error Resume Next
        ret = sapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)
        If Err.Number <> 0 Then Frame_Type = 0
        On Error GoTo DesignError
        
        If Frame_Type = 1 Then
            ' Get column design results
            Dim NumberItems As Long
            Dim FrameName() As String, MyOption() As Long, Location() As Double
            Dim PMMCombo() As String, PMMArea() As Double, PMMRatio() As Double
            Dim VmajorCombo() As String, AVmajor() As Double
            Dim VminorCombo() As String, AVminor() As Double
            Dim ErrorSummary() As String, WarningSummary() As String
            
            On Error Resume Next
            ret = sapModel.DesignConcrete.GetSummaryResultsColumn( _
                MyName(i), NumberItems, FrameName, MyOption, Location, _
                PMMCombo, PMMArea, PMMRatio, _
                VmajorCombo, AVmajor, VminorCombo, AVminor, _
                ErrorSummary, WarningSummary, 0)
            
            If Err.Number = 0 And ret = 0 And NumberItems > 0 Then
                Dim j As Long
                For j = LBound(FrameName) To UBound(FrameName)
                    Print #f, _
                        StoryName(i) & "," & _
                        MyName(i) & "," & _
                        PropName(i) & "," & _
                        Format(Location(j), "0.00") & "," & _
                        PMMCombo(j) & "," & _
                        Format(PMMRatio(j), "0.000") & "," & _
                        VmajorCombo(j) & "," & _
                        Format(AVmajor(j), "0.00") & "," & _
                        ErrorSummary(j) & "," & _
                        WarningSummary(j)
                Next j
                colCount = colCount + 1
            End If
            On Error GoTo DesignError
        End If
    Next i
    
    Close #f
    
    LogInfo "? Column design: " & colCount & " columns"
    ExportColumnDesignResults = (colCount > 0)
    Exit Function

DesignError:
    On Error Resume Next
    Close #f
    LogWarning "Column design error: " & Err.Description
    ExportColumnDesignResults = False
End Function

'------------------------------------------------------------------------------
' BEAM DESIGN RESULTS
' From legacy BEAM_DESIGN.bas pattern
'------------------------------------------------------------------------------

Public Function ExportBeamDesignResults(sapModel As Object, folder As String) As Boolean
    On Error GoTo DesignError
    
    Dim csvPath As String
    csvPath = folder & "\beam_design.csv"
    
    LogInfo "Exporting beam design results..."
    
    ' Check if design results available
    Dim ResultsAvailable As Boolean
    On Error Resume Next
    ResultsAvailable = sapModel.DesignConcrete.GetResultsAvailable
    On Error GoTo DesignError
    
    If Not ResultsAvailable Then
        LogWarning "Beam design not run - skipping"
        ExportBeamDesignResults = False
        Exit Function
    End If
    
    ' Get all frames
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String, StoryName() As String
    Dim PointName1() As String, PointName2() As String
    Dim Point1X() As Double, Point1Y() As Double, Point1Z() As Double
    Dim Point2X() As Double, Point2Y() As Double, Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double, Offset2X() As Double
    Dim Offset1Y() As Double, Offset2Y() As Double
    Dim Offset1Z() As Double, Offset2Z() As Double
    Dim CardinalPoint() As Long
    
    Dim ret As Long
    ret = sapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, _
        PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, _
        Angle, Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
    
    If ret <> 0 Or NumberNames = 0 Then
        LogWarning "Cannot get frames"
        ExportBeamDesignResults = False
        Exit Function
    End If
    
    ' Create CSV
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    Print #f, "Story,Label,Section,Location,TopCombo,TopArea,BotCombo,BotArea,ShearCombo,ShearArea,Error,Warning"
    
    Dim i As Long, beamCount As Long
    beamCount = 0
    
    For i = LBound(MyName) To UBound(MyName)
        ' Check if beam (Frame_Type = 2)
        Dim Frame_Type As Long
        On Error Resume Next
        ret = sapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)
        If Err.Number <> 0 Then Frame_Type = 0
        On Error GoTo DesignError
        
        If Frame_Type = 2 Then
            ' Get beam design results
            Dim NumberItems As Long
            Dim FrameName() As String, Location() As Double
            Dim TopCombo() As String, TopArea() As Double
            Dim TopAreaReq() As Double, TopAreaMin() As Double, TopAreaProvided() As Double
            Dim BotCombo() As String, BotArea() As Double
            Dim BotAreaReq() As Double, BotAreaMin() As Double, BotAreaProvided() As Double
            Dim VmajorCombo() As String, VmajorArea() As Double
            Dim VmajorAreaReq() As Double, VmajorAreaMin() As Double, VmajorAreaProvided() As Double
            Dim TLCombo() As String, TLArea() As Double
            Dim TTCombo() As String, TTArea() As Double
            Dim ErrorSummary() As String, WarningSummary() As String
            
            On Error Resume Next
            ret = sapModel.DesignConcrete.GetSummaryResultsBeam_2( _
                MyName(i), NumberItems, FrameName, Location, _
                TopCombo, TopArea, TopAreaReq, TopAreaMin, TopAreaProvided, _
                BotCombo, BotArea, BotAreaReq, BotAreaMin, BotAreaProvided, _
                VmajorCombo, VmajorArea, VmajorAreaReq, VmajorAreaMin, VmajorAreaProvided, _
                TLCombo, TLArea, TTCombo, TTArea, _
                ErrorSummary, WarningSummary, 0)
            
            If Err.Number = 0 And ret = 0 And NumberItems > 0 Then
                Dim j As Long
                For j = LBound(FrameName) To UBound(FrameName)
                    Print #f, _
                        StoryName(i) & "," & _
                        MyName(i) & "," & _
                        PropName(i) & "," & _
                        Format(Location(j), "0.00") & "," & _
                        TopCombo(j) & "," & _
                        Format(TopArea(j), "0.00") & "," & _
                        BotCombo(j) & "," & _
                        Format(BotArea(j), "0.00") & "," & _
                        VmajorCombo(j) & "," & _
                        Format(VmajorArea(j), "0.00") & "," & _
                        ErrorSummary(j) & "," & _
                        WarningSummary(j)
                Next j
                beamCount = beamCount + 1
            End If
            On Error GoTo DesignError
        End If
    Next i
    
    Close #f
    
    LogInfo "? Beam design: " & beamCount & " beams"
    ExportBeamDesignResults = (beamCount > 0)
    Exit Function

DesignError:
    On Error Resume Next
    Close #f
    LogWarning "Beam design error: " & Err.Description
    ExportBeamDesignResults = False
End Function

'------------------------------------------------------------------------------
' SECTIONS EXPORT
'------------------------------------------------------------------------------

Public Function ExportSections(sapModel As Object, folder As String) As Boolean
    On Error GoTo SectionError
    
    Dim csvPath As String
    csvPath = folder & "\sections.csv"
    
    LogInfo "Exporting sections..."
    
    Dim ret As Long
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
        "Frame Section Assignments", csvPath, False, 0, "")
    
    If ret = 0 And FileExists(csvPath) Then
        LogInfo "? Sections exported"
        ExportSections = True
    Else
        LogWarning "Sections export failed: ret=" & ret
        ExportSections = False
    End If
    Exit Function

SectionError:
    LogWarning "Sections error: " & Err.Description
    ExportSections = False
End Function

'------------------------------------------------------------------------------
' STORIES EXPORT
'------------------------------------------------------------------------------

Public Function ExportStories(sapModel As Object, folder As String) As Boolean
    On Error GoTo StoryError
    
    Dim csvPath As String
    csvPath = folder & "\stories.csv"
    
    LogInfo "Exporting stories..."
    
    Dim ret As Long
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
        "Story Definitions", csvPath, False, 0, "")
    
    If ret = 0 And FileExists(csvPath) Then
        LogInfo "? Stories exported"
        ExportStories = True
    Else
        LogWarning "Stories export failed: ret=" & ret
        ExportStories = False
    End If
    Exit Function

StoryError:
    LogWarning "Stories error: " & Err.Description
    ExportStories = False
End Function

'------------------------------------------------------------------------------
' JOINT DISPLACEMENTS (Bonus - for drift checks)
' From legacy torsional_irregularity.bas pattern
'------------------------------------------------------------------------------

Public Function ExportJointDisplacements(sapModel As Object, folder As String, units As UnitConversion) As Boolean
    On Error GoTo DispError
    
    Dim csvPath As String
    csvPath = folder & "\joint_displacements.csv"
    
    LogInfo "Exporting joint displacements..."
    
    ' Get all joints
    Dim NumberNames As Long
    Dim MyName() As String
    Dim ret As Long
    
    ret = sapModel.PointObj.GetNameList(NumberNames, MyName)
    
    If ret <> 0 Or NumberNames = 0 Then
        LogWarning "No joints found"
        ExportJointDisplacements = False
        Exit Function
    End If
    
    ' Create CSV
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    Print #f, "Story,Joint,LoadCase,U1_mm,U2_mm,U3_mm,R1_rad,R2_rad,R3_rad"
    
    Dim i As Long, count As Long
    count = 0
    
    For i = LBound(MyName) To UBound(MyName)
        Dim NumberResults As Long
        Dim obj() As String, Elm() As String
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim U1() As Double, U2() As Double, U3() As Double
        Dim R1() As Double, R2() As Double, R3() As Double
        
        On Error Resume Next
        ret = sapModel.Results.JointDispl(MyName(i), 0, NumberResults, _
            obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
        
        If Err.Number = 0 And ret = 0 And NumberResults > 0 Then
            ' Get story
            Dim label As String, story As String
            sapModel.PointObj.GetLabelFromName MyName(i), label, story
            
            Dim j As Long
            For j = LBound(LoadCase) To UBound(LoadCase)
                Print #f, _
                    story & "," & _
                    label & "," & _
                    LoadCase(j) & "," & _
                    Format(U1(j) * units.LengthToMM, "0.0000") & "," & _
                    Format(U2(j) * units.LengthToMM, "0.0000") & "," & _
                    Format(U3(j) * units.LengthToMM, "0.0000") & "," & _
                    Format(R1(j), "0.000000") & "," & _
                    Format(R2(j), "0.000000") & "," & _
                    Format(R3(j), "0.000000")
                count = count + 1
            Next j
        End If
        On Error GoTo DispError
        
        ' Progress
        If i Mod 100 = 0 Then
            Application.StatusBar = "Exporting displacements: " & i & "/" & NumberNames
            DoEvents
        End If
    Next i
    
    Close #f
    
    LogInfo "? Joint displacements: " & count & " records"
    ExportJointDisplacements = (count > 0)
    Exit Function

DispError:
    On Error Resume Next
    Close #f
    LogWarning "Displacement error: " & Err.Description
    ExportJointDisplacements = False
End Function
