Attribute VB_Name = "M13_Integration"
Option Explicit

' ==========================================================================================
' Module:       M13_Integration
' Description:  Handles data import/export from external sources (ETABS, CSV).
'               Part of the "Integration" Agent scope.
' Dependencies: M04_Utilities
' ==========================================================================================

' ------------------------------------------------------------------------------------------
' Constants for CSV Parsing
' ------------------------------------------------------------------------------------------
Private Const COL_STORY As String = "Story"
Private Const COL_LABEL As String = "Label"
Private Const COL_STATION As String = "Station"
Private Const COL_M3 As String = "M3"
Private Const COL_V2 As String = "V2"
Private Const COL_CASE As String = "Output Case"
' Optional Geometry
Private Const COL_SECTION As String = "Analysis Section" ' Or just "Section"

' ------------------------------------------------------------------------------------------
' Public Macro: Import ETABS CSV
' ------------------------------------------------------------------------------------------
Public Sub Import_ETABS_Data()
    Dim filePath As String
    Dim wsInput As Worksheet
    Dim tblInput As ListObject
    
    ' 1. Select File
    #If Mac Then
        ' Mac specific file picker (simplified for now, or use AppleScript)
        ' For v0.6, we might just ask for a path or assume a file in the same folder
        ' Let's try a simple InputBox for the path as a fallback, or standard GetOpenFilename if it works
        On Error Resume Next
        filePath = Application.GetOpenFilename("CSV Files (*.csv), *.csv")
        On Error GoTo 0
    #Else
        filePath = Application.GetOpenFilename("CSV Files (*.csv), *.csv")
    #End If
    
    If filePath = "False" Or filePath = "" Then Exit Sub
    
    ' 2. Setup Target
    Set wsInput = ThisWorkbook.Sheets("BEAM_INPUT")
    Set tblInput = wsInput.ListObjects("tbl_BeamInput")
    
    ' 3. Read & Parse
    Application.ScreenUpdating = False
    Call Process_ETABS_CSV(filePath, tblInput)
    Application.ScreenUpdating = True
    
    MsgBox "Import Complete!", vbInformation
End Sub

' ------------------------------------------------------------------------------------------
' Core Logic: Read CSV, Group by Beam, Aggregate Forces
' ------------------------------------------------------------------------------------------
Private Sub Process_ETABS_CSV(filePath As String, tbl As ListObject)
    Dim fileNum As Integer
    Dim lineData As String
    Dim headers() As String
    Dim rowData() As String
    Dim colMap As Collection
    Dim i As Long
    
    ' Column Indices
    Dim idxStory As Long, idxLabel As Long, idxStation As Long
    Dim idxM3 As Long, idxV2 As Long, idxCase As Long
    
    fileNum = FreeFile
    Open filePath For Input As #fileNum
    
    ' --- Read Headers ---
    If Not EOF(fileNum) Then
        Line Input #fileNum, lineData
        headers = Split(lineData, ",")
        Set colMap = MapHeaders(headers)
        
        ' Validate Required Columns
        If Not ValidateColumns(colMap, idxStory, idxLabel, idxStation, idxM3, idxV2) Then
            MsgBox "Missing required columns (Story, Label, Station, M3, V2).", vbCritical
            Close #fileNum
            Exit Sub
        End If
    End If
    
    ' --- Process Data (Stream Processing) ---
    ' We assume data is sorted by Story -> Label -> Station.
    ' If not, this simple logic fails. But ETABS exports are usually sorted.
    
    Dim currKey As String, lastKey As String
    Dim beamRows As Collection
    Set beamRows = New Collection
    
    Do Until EOF(fileNum)
        Line Input #fileNum, lineData
        rowData = ParseCSVLine(lineData) ' Handle quotes if needed
        
        If UBound(rowData) >= UBound(headers) Then ' Basic validity check
            Dim sStory As String: sStory = rowData(idxStory)
            Dim sLabel As String: sLabel = rowData(idxLabel)
            currKey = sStory & "|" & sLabel
            
            If currKey <> lastKey And lastKey <> "" Then
                ' Process the accumulated beam
                Call Write_Beam_To_Table(lastKey, beamRows, tbl, idxStation, idxM3, idxV2)
                Set beamRows = New Collection
            End If
            
            ' Add current row data to collection
            beamRows.Add rowData
            lastKey = currKey
        End If
    Loop
    
    ' Process final beam
    If beamRows.Count > 0 Then
        Call Write_Beam_To_Table(lastKey, beamRows, tbl, idxStation, idxM3, idxV2)
    End If
    
    Close #fileNum
End Sub

' ------------------------------------------------------------------------------------------
' Helper: Write 3 Rows (Start, Mid, End) for one Beam
' ------------------------------------------------------------------------------------------
Private Sub Write_Beam_To_Table(key As String, dataRows As Collection, tbl As ListObject, idxStation As Long, idxM3 As Long, idxV2 As Long)
    Dim i As Long
    Dim rowData As Variant
    Dim sVal As Double, mVal As Double, vVal As Double
    Dim maxStation As Double
    
    ' 1. Find Length (Max Station)
    maxStation = 0
    For i = 1 To dataRows.Count
        rowData = dataRows(i)
        sVal = CDbl(rowData(idxStation))
        If sVal > maxStation Then maxStation = sVal
    Next i
    
    If maxStation <= 0 Then Exit Sub ' Invalid beam
    
    ' 2. Buckets
    Dim mStart As Double, vStart As Double
    Dim mMid As Double, vMid As Double
    Dim mEnd As Double, vEnd As Double
    
    ' Initialize with 0
    mStart = 0: vStart = 0
    mMid = 0: vMid = 0
    mEnd = 0: vEnd = 0
    
    ' 3. Aggregate
    For i = 1 To dataRows.Count
        rowData = dataRows(i)
        sVal = CDbl(rowData(idxStation))
        mVal = Abs(CDbl(rowData(idxM3))) ' Take magnitude
        vVal = Abs(CDbl(rowData(idxV2))) ' Take magnitude
        
        ' Bucket Logic (0-20%, 20-80%, 80-100%)
        If sVal <= 0.2 * maxStation Then
            If mVal > mStart Then mStart = mVal
            If vVal > vStart Then vStart = vVal
        ElseIf sVal >= 0.8 * maxStation Then
            If mVal > mEnd Then mEnd = mVal
            If vVal > vEnd Then vEnd = vVal
        Else
            If mVal > mMid Then mMid = mVal
            If vVal > vMid Then vMid = vVal
        End If
    Next i
    
    ' 4. Write to Table
    Dim parts() As String
    parts = Split(key, "|")
    Dim story As String: story = parts(0)
    Dim label As String: label = parts(1)
    
    ' Add 3 Rows
    AddRow tbl, label, story, "Start", mStart, vStart
    AddRow tbl, label, story, "Mid", mMid, vMid
    AddRow tbl, label, story, "End", mEnd, vEnd
    
End Sub

Private Sub AddRow(tbl As ListObject, ID As String, story As String, loc As String, Mu As Double, Vu As Double)
    Dim newRow As ListRow
    Set newRow = tbl.ListRows.Add
    
    ' Dynamic Column Mapping for Robustness
    Dim idxID As Integer, idxStory As Integer, idxLoc As Integer
    Dim idxB As Integer, idxD As Integer, idxCover As Integer
    Dim idxFck As Integer, idxFy As Integer
    Dim idxMu As Integer, idxVu As Integer, idxFlanged As Integer
    
    On Error Resume Next
    idxID = tbl.ListColumns("ID").Index
    idxStory = tbl.ListColumns("Story").Index
    idxLoc = tbl.ListColumns("Span").Index ' Header is "Span" (Location)
    idxB = tbl.ListColumns("b").Index
    idxD = tbl.ListColumns("D").Index
    idxCover = tbl.ListColumns("Cover").Index
    idxFck = tbl.ListColumns("fck").Index
    idxFy = tbl.ListColumns("fy").Index
    idxMu = tbl.ListColumns("Mu").Index
    idxVu = tbl.ListColumns("Vu").Index
    idxFlanged = tbl.ListColumns("Flanged").Index
    On Error GoTo 0
    
    ' Fallback if columns not found (though they should exist)
    If idxID = 0 Then idxID = 1
    
    With newRow.Range
        If idxID > 0 Then .Cells(1, idxID).Value = ID
        If idxStory > 0 Then .Cells(1, idxStory).Value = story
        If idxLoc > 0 Then .Cells(1, idxLoc).Value = loc
        
        ' Default Geometry (User must fill)
        If idxB > 0 Then .Cells(1, idxB).Value = 230
        If idxD > 0 Then .Cells(1, idxD).Value = 450
        If idxCover > 0 Then .Cells(1, idxCover).Value = 25
        If idxFck > 0 Then .Cells(1, idxFck).Value = 25
        If idxFy > 0 Then .Cells(1, idxFy).Value = 500
        
        ' Forces
        If idxMu > 0 Then .Cells(1, idxMu).Value = Mu
        If idxVu > 0 Then .Cells(1, idxVu).Value = Vu
        
        ' Defaults
        If idxFlanged > 0 Then .Cells(1, idxFlanged).Value = "No"
    End With
End Sub

' ------------------------------------------------------------------------------------------
' Utilities
' ------------------------------------------------------------------------------------------
Private Function MapHeaders(headers() As String) As Collection
    Dim c As New Collection
    Dim i As Long
    For i = LBound(headers) To UBound(headers)
        ' Clean quotes
        Dim h As String
        h = Replace(headers(i), """", "")
        h = Trim(h)
        On Error Resume Next
        c.Add i, h
        On Error GoTo 0
    Next i
    Set MapHeaders = c
End Function

Private Function ValidateColumns(map As Collection, ByRef iStory As Long, ByRef iLabel As Long, ByRef iStation As Long, ByRef iM3 As Long, ByRef iV2 As Long) As Boolean
    On Error Resume Next
    iStory = map(COL_STORY)
    iLabel = map(COL_LABEL)
    iStation = map(COL_STATION)
    iM3 = map(COL_M3)
    iV2 = map(COL_V2)
    
    If Err.Number <> 0 Then
        ValidateColumns = False
    Else
        ValidateColumns = True
    End If
    On Error GoTo 0
End Function

Private Function ParseCSVLine(line As String) As String()
    ' Simple split for now. Complex CSV (commas in quotes) needs a real parser.
    ParseCSVLine = Split(line, ",")
End Function
