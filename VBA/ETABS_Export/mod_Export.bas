Attribute VB_Name = "mod_Export"
Option Explicit

'==============================================================================
' Export Module
' Handles exporting data tables from ETABS
'==============================================================================

' Export frame forces using DatabaseTables (fastest method)
Public Function ExportFrameForces(sapModel As Object, outputFolder As String) As Boolean
    On Error GoTo ExportError

    Dim csvPath As String
    csvPath = outputFolder & "\frame_forces_raw.csv"

    LogInfo "Exporting frame forces to: " & csvPath
    LogInfo "Using DatabaseTables.GetTableForDisplayCSVFile (fastest method)"

    ' Try multiple table name variants (ETABS versions may differ)
    Dim tableNames() As Variant
    tableNames = Array( _
        "Element Forces - Frames", _
        "Element Forces-Frames", _
        "Frame Element Forces", _
        "Frame Forces" _
    )

    Dim ret As Long
    Dim success As Boolean
    success = False

    Dim tableName As Variant
    For Each tableName in tableNames
        On Error Resume Next
        Err.Clear

        LogDebug "Trying table name: " & tableName

        ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
            CStr(tableName), _
            csvPath, _
            False, _  ' Don't append
            0, _      ' All groups (eNamedSetType.All)
            "" _      ' Empty group name = all
        )

        If Err.Number = 0 And ret = 0 Then
            LogInfo "? Export successful using table: " & tableName
            success = True
            Exit For
        Else
            LogDebug "  Failed: ret=" & ret & ", err=" & Err.Number
        End If

        On Error GoTo ExportError
    Next

    If Not success Then
        LogError "All table name variants failed"
        LogWarning "Falling back to Direct API method..."

        ' Fallback: Direct API (slower but more compatible)
        success = ExportFrameForcesDirect(sapModel, csvPath)

        If Not success Then
            LogError "Both DatabaseTables and Direct API methods failed"
            ExportFrameForces = False
            Exit Function
        End If
    End If

    ' Verify file was created
    If Not FileExists(csvPath) Then
        LogError "CSV file was not created: " & csvPath
        ExportFrameForces = False
        Exit Function
    End If

    ' Count rows
    Dim rowCount As Long
    rowCount = CountCSVRows(csvPath)
    LogInfo "? Exported " & rowCount & " rows"

    If rowCount < 2 Then
        LogWarning "CSV has only " & rowCount & " rows (expected header + data)"
    End If

    ExportFrameForces = True
    Exit Function

ExportError:
    LogError "Export error: " & Err.Description
    ExportFrameForces = False
End Function

' Fallback: Export using Direct API
Private Function ExportFrameForcesDirect(sapModel As Object, csvPath As String) As Boolean
    On Error GoTo DirectError

    LogInfo "Using Direct API method (slower but compatible)"

    ' Get frame list
    Dim frameCount As Long
    Dim frameNames() As String

    Dim ret As Long
    ret = sapModel.FrameObj.GetNameList(frameCount, frameNames)

    If ret <> 0 Or frameCount = 0 Then
        LogError "Cannot get frame list: ret=" & ret & ", count=" & frameCount
        ExportFrameForcesDirect = False
        Exit Function
    End If

    LogInfo "Found " & frameCount & " frames, retrieving forces..."

    ' Create CSV file
    Dim fileNum As Integer
    fileNum = FreeFile
    Open csvPath For Output As #fileNum

    ' Write header
    Print #fileNum, "Story,Label,LoadCase,Station,M3,V2,P"

    ' Get forces for each frame
    Dim i As Long
    Dim totalRows As Long
    totalRows = 0

    For i = LBound(frameNames) To UBound(frameNames)
        Dim frameName As String
        frameName = frameNames(i)

        ' Get frame story
        Dim story As String
        story = GetFrameStory(sapModel, frameName)

        ' Get forces
        Dim NumberResults As Long
        Dim obj() As String
        Dim ObjSta() As Double
        Dim Elm() As String
        Dim ElmSta() As Double
        Dim LoadCase() As String
        Dim StepType() As String
        Dim StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double

        ret = sapModel.Results.FrameForce( _
            frameName, _
            0, _  ' eItemTypeElm.ObjectElm
            NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3 _
        )

        If ret = 0 And NumberResults > 0 Then
            ' Write results
            Dim j As Long
            For j = LBound(LoadCase) To UBound(LoadCase)
                Print #fileNum, _
                    story & "," & _
                    frameName & "," & _
                    LoadCase(j) & "," & _
                    Format(ElmSta(j), "0.000") & "," & _
                    Format(M3(j), "0.000") & "," & _
                    Format(V2(j), "0.000") & "," & _
                    Format(P(j), "0.000")

                totalRows = totalRows + 1
            Next j
        End If

        ' Progress update
        If i Mod 100 = 0 Then
            Application.StatusBar = "Exporting: " & i & "/" & frameCount & " frames"
            DoEvents
        End If
    Next i

    Close #fileNum

    LogInfo "? Direct API export complete: " & totalRows & " rows"
    ExportFrameForcesDirect = True
    Exit Function

DirectError:
    On Error Resume Next
    Close #fileNum
    LogError "Direct API export error: " & Err.Description
    ExportFrameForcesDirect = False
End Function

' Export sections
Public Function ExportSections(sapModel As Object, outputFolder As String) As Boolean
    On Error GoTo ExportError

    Dim csvPath As String
    csvPath = outputFolder & "\sections_raw.csv"

    LogInfo "Exporting sections to: " & csvPath

    Dim ret As Long
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
        "Frame Section Assignments", _
        csvPath, _
        False, 0, "" _
    )

    If ret <> 0 Then
        LogWarning "Sections export failed: ret=" & ret
        ExportSections = False
    Else
        LogInfo "? Sections exported"
        ExportSections = True
    End If

    Exit Function

ExportError:
    LogWarning "Sections export error: " & Err.Description
    ExportSections = False
End Function

' Export geometry
Public Function ExportGeometry(sapModel As Object, outputFolder As String) As Boolean
    On Error GoTo ExportError

    Dim csvPath As String
    csvPath = outputFolder & "\geometry_raw.csv"

    LogInfo "Exporting geometry to: " & csvPath

    Dim ret As Long
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
        "Connectivity - Frame", _
        csvPath, _
        False, 0, "" _
    )

    If ret <> 0 Then
        LogWarning "Geometry export failed: ret=" & ret
        ExportGeometry = False
    Else
        LogInfo "? Geometry exported"
        ExportGeometry = True
    End If

    Exit Function

ExportError:
    LogWarning "Geometry export error: " & Err.Description
    ExportGeometry = False
End Function

' Export stories
Public Function ExportStories(sapModel As Object, outputFolder As String) As Boolean
    On Error GoTo ExportError

    Dim csvPath As String
    csvPath = outputFolder & "\stories_raw.csv"

    LogInfo "Exporting stories to: " & csvPath

    Dim ret As Long
    ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
        "Story Definitions", _
        csvPath, _
        False, 0, "" _
    )

    If ret <> 0 Then
        LogWarning "Stories export failed: ret=" & ret
        ExportStories = False
    Else
        LogInfo "? Stories exported"
        ExportStories = True
    End If

    Exit Function

ExportError:
    LogWarning "Stories export error: " & Err.Description
    ExportStories = False
End Function

' Helper: Get frame story using PointObj parent
Private Function GetFrameStory(sapModel As Object, frameName As String) As String
    On Error Resume Next
    
    ' Try to get story from frame label (ETABS stores story in label)
    Dim label As String
    Dim story As String
    Dim ret As Long
    
    ret = sapModel.FrameObj.GetLabelFromName(frameName, label, story)
    
    If Err.Number = 0 And ret = 0 And Len(story) > 0 Then
        GetFrameStory = story
        Exit Function
    End If
    
    ' Fallback: Try to get from point object
    Dim point1 As String, point2 As String
    ret = sapModel.FrameObj.GetPoints(frameName, point1, point2)
    
    If Err.Number = 0 And ret = 0 Then
        ' Get story from point
        Dim pointLabel As String, pointStory As String
        ret = sapModel.PointObj.GetLabelFromName(point1, pointLabel, pointStory)
        
        If Err.Number = 0 And ret = 0 Then
            GetFrameStory = pointStory
            Exit Function
        End If
    End If
    
    ' Ultimate fallback
    GetFrameStory = "Unknown"
End Function
