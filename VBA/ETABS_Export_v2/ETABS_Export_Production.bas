Attribute VB_Name = "ETABS_Export_Production"
Option Explicit

'==============================================================================
' ETABS EXPORT PRODUCTION v2.0
'==============================================================================
' Exports filtered beam forces, properties, and spans to CSV
'
' REQUIREMENTS:
'   1. Add ETABS API v1 reference (Tools → References → ETABS.exe)
'   2. ETABS model must be open with analysis results
'   3. Configure settings in ETABS_Export_Config.bas
'
' USAGE:
'   1. Import both this file and ETABS_Export_Config.bas
'   2. Edit config settings for your model's combo names
'   3. Run ExportAll() for complete export
'   4. Or run individual exports: ExportForces, ExportProperties, ExportSpans
'
' Created: 2026-01-17 | Version: 2.0
'==============================================================================

' Module-level ETABS objects (early binding - requires type library)
Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

' ============================================
' MAIN EXPORT FUNCTIONS
' ============================================

' Export everything in one click
Sub ExportAll()
    On Error GoTo ErrorHandler
    
    Debug.Print "========== ETABS EXPORT STARTED =========="
    Debug.Print "Time: " & Now
    
    ' Print config
    Call PrintConfig
    
    ' Export forces (filtered)
    Call ExportForces_Filtered
    
    ' Export properties
    Call ExportProperties
    
    ' Export spans
    Call ExportSpans
    
    Debug.Print "========== EXPORT COMPLETE =========="
    
    ' Open output folder
    If OPEN_FOLDER_AFTER Then
        Shell "explorer.exe """ & GetOutputFolder() & """", vbNormalFocus
    End If
    
    Exit Sub
    
ErrorHandler:
    MsgBox "Export failed: " & Err.Description & vbCrLf & _
           "Error #" & Err.Number, vbCritical, "Export Error"
End Sub

' ============================================
' FORCES EXPORT (FILTERED)
' ============================================

Sub ExportForces_Filtered()
    On Error GoTo ErrorHandler
    
    Debug.Print ""
    Debug.Print "--- Exporting Forces (Filtered) ---"
    
    ' Connect to ETABS
    Call ConnectToETABS
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    ' Get load combos and select filtered ones
    Dim NumberCombos As Long
    Dim ComboName() As String
    ret = mySapModel.RespCombo.GetNameList(NumberCombos, ComboName)
    
    Debug.Print "Total combos in model: " & NumberCombos
    
    ' Select only design combos for output
    Dim selectedCount As Long
    selectedCount = 0
    
    Dim c As Long
    For c = 0 To NumberCombos - 1
        If ShouldExportCombo(ComboName(c)) Then
            ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ComboName(c))
            selectedCount = selectedCount + 1
            Debug.Print "  Selected: " & ComboName(c)
        End If
    Next c
    
    ' Also include load cases if configured
    If INCLUDE_LOAD_CASES Then
        Dim NumberCases As Long
        Dim CaseName() As String
        ret = mySapModel.LoadCases.GetNameList(NumberCases, CaseName)
        
        For c = 0 To NumberCases - 1
            ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(c))
            selectedCount = selectedCount + 1
        Next c
    End If
    
    Debug.Print "Selected for export: " & selectedCount & " cases/combos"
    
    If selectedCount = 0 Then
        MsgBox "No combos selected for export!" & vbCrLf & _
               "Check DESIGN_COMBOS in Config matches your model.", _
               vbExclamation, "No Combos"
        Exit Sub
    End If
    
    ' Get all frames
    Dim NumberFrames As Long
    Dim FrameName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberFrames, FrameName)
    
    Debug.Print "Total frames: " & NumberFrames
    
    ' Open output file
    Dim outputPath As String
    outputPath = GetOutputFolder() & "\" & FORCES_FILENAME
    
    Dim f As Integer
    f = FreeFile
    Open outputPath For Output As #f
    
    ' Write header
    Print #f, "Story,Label,LoadCombo,Station_m,M3_kNm,V2_kN,P_kN,LocationType"
    
    ' Track statistics
    Dim totalRows As Long, framesExported As Long
    totalRows = 0
    framesExported = 0
    
    ' Process each frame
    Dim i As Long
    For i = 0 To NumberFrames - 1
        ' Get story for this frame
        Dim storyName As String
        storyName = GetFrameStory(FrameName(i))
        
        ' Check story filter
        If Not ShouldExportStory(storyName) Then
            GoTo NextFrame
        End If
        
        ' Get frame forces
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        ret = mySapModel.Results.FrameForce( _
            FrameName(i), eItemTypeElm_ObjectElm, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        
        If ret <> 0 Or NumberResults = 0 Then
            GoTo NextFrame
        End If
        
        framesExported = framesExported + 1
        
        ' Apply station filtering
        Select Case STATION_FILTER_METHOD
            Case 1  ' Envelope only
                Call WriteEnvelopeResults(f, FrameName(i), storyName, _
                    NumberResults, LoadCase, ElmSta, P, V2, M3, totalRows)
            
            Case 2  ' Critical stations
                Call WriteCriticalStations(f, FrameName(i), storyName, _
                    NumberResults, LoadCase, ElmSta, P, V2, M3, totalRows)
            
            Case Else  ' All stations
                Call WriteAllResults(f, FrameName(i), storyName, _
                    NumberResults, LoadCase, ElmSta, P, V2, M3, totalRows)
        End Select
        
NextFrame:
        ' Progress
        If i Mod 50 = 0 Then
            Application.StatusBar = "Exporting forces: " & i & "/" & NumberFrames
            DoEvents
        End If
    Next i
    
    Close #f
    Application.StatusBar = False
    
    Debug.Print "Forces export complete:"
    Debug.Print "  Frames exported: " & framesExported
    Debug.Print "  Total rows: " & totalRows
    Debug.Print "  Output: " & outputPath
    
    MsgBox "Forces Export Complete!" & vbCrLf & vbCrLf & _
           "Frames: " & framesExported & vbCrLf & _
           "Rows: " & totalRows & vbCrLf & _
           "File: " & outputPath, _
           vbInformation, "Export Success"
    
    Exit Sub
    
ErrorHandler:
    On Error Resume Next
    Close #f
    Application.StatusBar = False
    MsgBox "Forces export failed: " & Err.Description, vbCritical
End Sub

' ============================================
' ENVELOPE FILTER (Station Filter Method 1)
' ============================================

Private Sub WriteEnvelopeResults(f As Integer, frameName As String, storyName As String, _
    NumberResults As Long, LoadCase() As String, ElmSta() As Double, _
    P() As Double, V2() As Double, M3() As Double, ByRef totalRows As Long)
    
    ' Find envelope values per load combo
    ' Structure: Dictionary of combo -> (maxM3, minM3, maxV2, their stations and values)
    
    ' Since VBA doesn't have good dictionaries, we'll use a simpler approach:
    ' Track max positive M3, max negative M3, max |V2| for each combo
    
    Dim lastCombo As String
    Dim maxPosM3 As Double, maxNegM3 As Double, maxAbsV2 As Double
    Dim maxPosM3_Sta As Double, maxNegM3_Sta As Double, maxV2_Sta As Double
    Dim maxPosM3_P As Double, maxNegM3_P As Double, maxV2_P As Double
    Dim maxPosM3_V2 As Double, maxNegM3_V2 As Double, maxV2_M3 As Double
    Dim hasData As Boolean
    
    lastCombo = ""
    hasData = False
    
    Dim j As Long
    For j = 0 To NumberResults - 1
        ' Skip if below threshold
        If Abs(M3(j)) < MIN_MOMENT_THRESHOLD Then GoTo NextResult
        
        ' Check if new combo (results are grouped by combo)
        If LoadCase(j) <> lastCombo Then
            ' Write previous combo's envelope if exists
            If hasData Then
                Call WriteEnvelopeRow(f, storyName, frameName, lastCombo, _
                    maxPosM3_Sta, maxPosM3, maxPosM3_V2, maxPosM3_P, "Max+M", totalRows)
                    
                If maxNegM3 < 0 Then
                    Call WriteEnvelopeRow(f, storyName, frameName, lastCombo, _
                        maxNegM3_Sta, maxNegM3, maxNegM3_V2, maxNegM3_P, "Max-M", totalRows)
                End If
                
                If maxAbsV2 > 0 Then
                    Call WriteEnvelopeRow(f, storyName, frameName, lastCombo, _
                        maxV2_Sta, maxV2_M3, maxAbsV2, maxV2_P, "MaxV", totalRows)
                End If
            End If
            
            ' Reset for new combo
            lastCombo = LoadCase(j)
            maxPosM3 = -1E+30: maxNegM3 = 1E+30: maxAbsV2 = 0
            hasData = True
        End If
        
        ' Track max positive M3
        If M3(j) > maxPosM3 Then
            maxPosM3 = M3(j)
            maxPosM3_Sta = ElmSta(j)
            maxPosM3_V2 = V2(j)
            maxPosM3_P = P(j)
        End If
        
        ' Track max negative M3
        If M3(j) < maxNegM3 Then
            maxNegM3 = M3(j)
            maxNegM3_Sta = ElmSta(j)
            maxNegM3_V2 = V2(j)
            maxNegM3_P = P(j)
        End If
        
        ' Track max |V2|
        If Abs(V2(j)) > maxAbsV2 Then
            maxAbsV2 = Abs(V2(j))
            maxV2_Sta = ElmSta(j)
            maxV2_M3 = M3(j)
            maxV2_P = P(j)
        End If
        
NextResult:
    Next j
    
    ' Write last combo's envelope
    If hasData Then
        Call WriteEnvelopeRow(f, storyName, frameName, lastCombo, _
            maxPosM3_Sta, maxPosM3, maxPosM3_V2, maxPosM3_P, "Max+M", totalRows)
            
        If maxNegM3 < 0 Then
            Call WriteEnvelopeRow(f, storyName, frameName, lastCombo, _
                maxNegM3_Sta, maxNegM3, maxNegM3_V2, maxNegM3_P, "Max-M", totalRows)
        End If
        
        If maxAbsV2 > 0 Then
            Call WriteEnvelopeRow(f, storyName, frameName, lastCombo, _
                maxV2_Sta, maxV2_M3, maxAbsV2, maxV2_P, "MaxV", totalRows)
        End If
    End If
End Sub

Private Sub WriteEnvelopeRow(f As Integer, storyName As String, frameName As String, _
    comboName As String, station As Double, M3 As Double, V2 As Double, P As Double, _
    locType As String, ByRef totalRows As Long)
    
    Print #f, storyName & "," & frameName & "," & comboName & "," & _
              Format(station, "0.000") & "," & _
              Format(M3, "0.000") & "," & _
              Format(V2, "0.000") & "," & _
              Format(P, "0.000") & "," & locType
    
    totalRows = totalRows + 1
End Sub

' ============================================
' CRITICAL STATIONS (Station Filter Method 2)
' ============================================

Private Sub WriteCriticalStations(f As Integer, frameName As String, storyName As String, _
    NumberResults As Long, LoadCase() As String, ElmSta() As Double, _
    P() As Double, V2() As Double, M3() As Double, ByRef totalRows As Long)
    
    ' Write results at critical stations:
    ' - Start (station ~0)
    ' - End (max station)
    ' - Midspan (station ~0.5 * max)
    
    ' First find max station
    Dim maxStation As Double
    maxStation = 0
    
    Dim j As Long
    For j = 0 To NumberResults - 1
        If ElmSta(j) > maxStation Then maxStation = ElmSta(j)
    Next j
    
    ' Define critical station ranges
    Dim startRange As Double, midRange As Double, endRange As Double
    startRange = maxStation * 0.1  ' 0-10% of span = start
    midRange = maxStation * 0.1     ' ±10% of midpoint
    endRange = maxStation * 0.9     ' 90-100% of span = end
    
    ' Write filtered results
    For j = 0 To NumberResults - 1
        Dim locType As String
        locType = ""
        
        If ElmSta(j) <= startRange Then
            locType = "Start"
        ElseIf ElmSta(j) >= endRange Then
            locType = "End"
        ElseIf Abs(ElmSta(j) - maxStation / 2) <= midRange Then
            locType = "Mid"
        End If
        
        If locType <> "" And Abs(M3(j)) >= MIN_MOMENT_THRESHOLD Then
            Print #f, storyName & "," & frameName & "," & LoadCase(j) & "," & _
                      Format(ElmSta(j), "0.000") & "," & _
                      Format(M3(j), "0.000") & "," & _
                      Format(V2(j), "0.000") & "," & _
                      Format(P(j), "0.000") & "," & locType
            totalRows = totalRows + 1
        End If
    Next j
End Sub

' ============================================
' ALL STATIONS (Station Filter Method 3)
' ============================================

Private Sub WriteAllResults(f As Integer, frameName As String, storyName As String, _
    NumberResults As Long, LoadCase() As String, ElmSta() As Double, _
    P() As Double, V2() As Double, M3() As Double, ByRef totalRows As Long)
    
    Dim j As Long
    For j = 0 To NumberResults - 1
        If Abs(M3(j)) >= MIN_MOMENT_THRESHOLD Then
            Print #f, storyName & "," & frameName & "," & LoadCase(j) & "," & _
                      Format(ElmSta(j), "0.000") & "," & _
                      Format(M3(j), "0.000") & "," & _
                      Format(V2(j), "0.000") & "," & _
                      Format(P(j), "0.000") & ",All"
            totalRows = totalRows + 1
        End If
    Next j
End Sub

' ============================================
' PROPERTIES EXPORT
' ============================================

Sub ExportProperties()
    On Error GoTo ErrorHandler
    
    Debug.Print ""
    Debug.Print "--- Exporting Properties ---"
    
    ' Connect
    Call ConnectToETABS
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    ' Get all frames
    Dim NumberFrames As Long
    Dim FrameName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberFrames, FrameName)
    
    ' Open output file
    Dim outputPath As String
    outputPath = GetOutputFolder() & "\" & PROPERTIES_FILENAME
    
    Dim f As Integer
    f = FreeFile
    Open outputPath For Output As #f
    
    ' Write header
    Print #f, "Label,Story,Section,Width_mm,Depth_mm,fck_MPa,fy_MPa"
    
    Dim exported As Long
    exported = 0
    
    Dim i As Long
    For i = 0 To NumberFrames - 1
        Dim storyName As String
        storyName = GetFrameStory(FrameName(i))
        
        If Not ShouldExportStory(storyName) Then GoTo NextProp
        
        ' Get section name
        Dim sectName As String, sAuto As String
        ret = mySapModel.FrameObj.GetSection(FrameName(i), sectName, sAuto)
        
        If ret <> 0 Then GoTo NextProp
        
        ' Get section dimensions (try rectangular first)
        Dim fileName As String, matProp As String
        Dim t3 As Double, t2 As Double  ' t3=depth, t2=width
        Dim color As Long, notes As String, guid As String
        
        ret = mySapModel.PropFrame.GetRectangle(sectName, fileName, matProp, _
            t3, t2, color, notes, guid)
        
        ' Convert from m to mm (if in meters)
        Dim width_mm As Double, depth_mm As Double
        If t2 < 1 Then  ' Likely in meters
            width_mm = t2 * 1000
            depth_mm = t3 * 1000
        Else
            width_mm = t2
            depth_mm = t3
        End If
        
        ' Get material properties
        Dim fck As Double, fy As Double
        fck = DEFAULT_FCK
        fy = DEFAULT_FY
        
        ' Write row
        Print #f, FrameName(i) & "," & storyName & "," & sectName & "," & _
                  Format(width_mm, "0") & "," & Format(depth_mm, "0") & "," & _
                  Format(fck, "0") & "," & Format(fy, "0")
        exported = exported + 1
        
NextProp:
    Next i
    
    Close #f
    
    Debug.Print "Properties export complete:"
    Debug.Print "  Frames: " & exported
    Debug.Print "  Output: " & outputPath
    
    Exit Sub
    
ErrorHandler:
    On Error Resume Next
    Close #f
    MsgBox "Properties export failed: " & Err.Description, vbCritical
End Sub

' ============================================
' SPANS EXPORT
' ============================================

Sub ExportSpans()
    On Error GoTo ErrorHandler
    
    Debug.Print ""
    Debug.Print "--- Exporting Spans ---"
    
    ' Connect
    Call ConnectToETABS
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    ' Get all frames
    Dim NumberFrames As Long
    Dim FrameName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberFrames, FrameName)
    
    ' Open output file
    Dim outputPath As String
    outputPath = GetOutputFolder() & "\" & SPANS_FILENAME
    
    Dim f As Integer
    f = FreeFile
    Open outputPath For Output As #f
    
    ' Write header
    Print #f, "Label,Story,Point1,Point2,Span_m"
    
    Dim exported As Long
    exported = 0
    
    Dim i As Long
    For i = 0 To NumberFrames - 1
        Dim storyName As String
        storyName = GetFrameStory(FrameName(i))
        
        If Not ShouldExportStory(storyName) Then GoTo NextSpan
        
        ' Get frame endpoints
        Dim point1 As String, point2 As String
        ret = mySapModel.FrameObj.GetPoints(FrameName(i), point1, point2)
        
        If ret <> 0 Then GoTo NextSpan
        
        ' Get coordinates
        Dim x1 As Double, y1 As Double, z1 As Double
        Dim x2 As Double, y2 As Double, z2 As Double
        
        ret = mySapModel.PointObj.GetCoordCartesian(point1, x1, y1, z1)
        ret = mySapModel.PointObj.GetCoordCartesian(point2, x2, y2, z2)
        
        ' Calculate span
        Dim spanLength As Double
        spanLength = Sqr((x2 - x1) ^ 2 + (y2 - y1) ^ 2 + (z2 - z1) ^ 2)
        
        ' Write row
        Print #f, FrameName(i) & "," & storyName & "," & point1 & "," & point2 & "," & _
                  Format(spanLength, "0.000")
        exported = exported + 1
        
NextSpan:
    Next i
    
    Close #f
    
    Debug.Print "Spans export complete:"
    Debug.Print "  Frames: " & exported
    Debug.Print "  Output: " & outputPath
    
    Exit Sub
    
ErrorHandler:
    On Error Resume Next
    Close #f
    MsgBox "Spans export failed: " & Err.Description, vbCritical
End Sub

' ============================================
' HELPER FUNCTIONS
' ============================================

Private Sub ConnectToETABS()
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
End Sub

Private Function GetFrameStory(frameName As String) As String
    On Error Resume Next
    
    Dim point1 As String, point2 As String
    Dim ret As Long
    
    ret = mySapModel.FrameObj.GetPoints(frameName, point1, point2)
    
    If ret = 0 Then
        Dim label As String, story As String
        ret = mySapModel.PointObj.GetLabelFromName(point1, label, story)
        If ret = 0 Then
            GetFrameStory = story
            Exit Function
        End If
    End If
    
    GetFrameStory = "Unknown"
End Function
