Attribute VB_Name = "M13_Integration"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

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

' ------------------------------------------------------------------------------------------
' Public Macro: Import ETABS CSV
' ------------------------------------------------------------------------------------------
Public Sub Import_ETABS_Data()
    Dim filePath As String
    Dim wsInput As Worksheet
    Dim tblInput As ListObject

    ' 1. Select File (mac-friendly with fallback) or load sample if unavailable
    #If Mac Then
        On Error Resume Next
        filePath = MacScript("choose file of type {""public.comma-separated-values-text"", ""TEXT""} with prompt ""Select ETABS CSV Export""")
        On Error GoTo 0
        If filePath = "" Then
            filePath = InputBox("Enter full path to CSV file (or leave blank to load sample):", "File Selection")
        End If
    #Else
        filePath = Application.GetOpenFilename("CSV Files (*.csv), *.csv")
        If filePath = "False" Then filePath = ""
    #End If

    ' 2. Setup Target
    Set wsInput = ThisWorkbook.Sheets("BEAM_INPUT")
    On Error Resume Next
    Set tblInput = wsInput.ListObjects("tbl_BeamInput")
    On Error GoTo 0

    If tblInput Is Nothing Then
        MsgBox "Error: tbl_BeamInput not found. Please run Setup first.", vbCritical
        Exit Sub
    End If

    ' 3. If no file or invalid path, load sample data
    If Len(Trim$(filePath)) = 0 Or Dir(filePath) = "" Then
        Populate_Sample_Input tblInput
        MsgBox "Sample data loaded into BEAM_INPUT.", vbInformation
        Exit Sub
    End If

    ' 4. Read & Parse CSV
    Application.ScreenUpdating = False
    Call Process_ETABS_CSV(filePath, tblInput)
    Application.ScreenUpdating = True

    MsgBox "Import Complete!", vbInformation
End Sub

' ------------------------------------------------------------------------------------------
' Public Macro: Generate Sample ETABS CSV
' ------------------------------------------------------------------------------------------
Public Sub Generate_Sample_ETABS_CSV()
    Dim filePath As String
    Dim fileNum As Integer
    Dim i As Long

    ' Default path: Desktop or Documents
    #If Mac Then
        filePath = MacScript("return POSIX path of (path to desktop folder)") & "ETABS_Sample_Export.csv"
    #Else
        filePath = Environ("USERPROFILE") & "\Desktop\ETABS_Sample_Export.csv"
    #End If

    fileNum = FreeFile
    Open filePath For Output As #fileNum

    ' Write Header
    Print #fileNum, "Story,Label,Unique Name,Output Case,Station,P,V2,M3"

    ' Write Sample Data (B1, B2, B3)
    ' B1: Story1, 4m span
    Print #fileNum, "Story1,B1,1,Combo1,0,0,100,-50"
    Print #fileNum, "Story1,B1,1,Combo1,2000,0,0,150"
    Print #fileNum, "Story1,B1,1,Combo1,4000,0,-100,-50"

    ' B2: Story1, 3m span
    Print #fileNum, "Story1,B2,2,Combo1,0,0,80,-40"
    Print #fileNum, "Story1,B2,2,Combo1,1500,0,0,100"
    Print #fileNum, "Story1,B2,2,Combo1,3000,0,-80,-40"

    ' B3: Story2, 5m span
    Print #fileNum, "Story2,B3,3,Combo1,0,0,120,-60"
    Print #fileNum, "Story2,B3,3,Combo1,2500,0,0,200"
    Print #fileNum, "Story2,B3,3,Combo1,5000,0,-120,-60"

    Close #fileNum

    MsgBox "Sample CSV generated at: " & vbNewLine & filePath, vbInformation
End Sub

' ------------------------------------------------------------------------------------------
' Helper: Populate sample data (for environments without ETABS/CSV)
' ------------------------------------------------------------------------------------------
Private Sub Populate_Sample_Input(tbl As ListObject)
    ' Columns: ID, Story, Span, b, D, Cover, fck, fy, Mu, Vu, Flanged?, Df, bf
    Dim samples As Variant
    samples = Array( _
        Array("B1", "Story1", "Start", 230, 450, 25, 25, 500, -50, 100, "No", 0, 0), _
        Array("B1", "Story1", "Mid", 230, 450, 25, 25, 500, 150, 0, "No", 0, 0), _
        Array("B1", "Story1", "End", 230, 450, 25, 25, 500, -50, 100, "No", 0, 0), _
        Array("B2", "Story1", "Start", 300, 600, 30, 30, 500, -40, 80, "Yes", 120, 800), _
        Array("B2", "Story1", "Mid", 300, 600, 30, 30, 500, 100, 0, "Yes", 120, 800), _
        Array("B2", "Story1", "End", 300, 600, 30, 30, 500, -40, 80, "Yes", 120, 800), _
        Array("B3", "Story2", "Start", 230, 500, 25, 25, 500, -60, 120, "No", 0, 0), _
        Array("B3", "Story2", "Mid", 230, 500, 25, 25, 500, 200, 0, "No", 0, 0), _
        Array("B3", "Story2", "End", 230, 500, 25, 25, 500, -60, 120, "No", 0, 0) _
    )

    ' Clear existing rows
    If Not tbl.DataBodyRange Is Nothing Then
        tbl.DataBodyRange.Delete
    End If

    Dim i As Long
    For i = LBound(samples) To UBound(samples)
        Dim lr As ListRow
        Set lr = tbl.ListRows.Add
        lr.Range.Cells(1, 1).Resize(1, 13).Value = samples(i)
    Next i
End Sub

' ------------------------------------------------------------------------------------------
' Helper: Process one beam group (multiple stations/load cases)
' ------------------------------------------------------------------------------------------
Private Sub Process_Beam_Group(key As String, rows As Collection, tbl As ListObject, idxStation As Long, idxM3 As Long, idxV2 As Long)
    Dim i As Long
    Dim rowData As Variant
    Dim sVal As Double, mVal As Double, vVal As Double
    Dim maxStation As Double

    ' 1. Find Length (Max Station)
    maxStation = 0
    For i = 1 To rows.Count
        rowData = rows(i)
        sVal = CDbl(Val(rowData(idxStation))) ' Val handles strings safely
        If sVal > maxStation Then maxStation = sVal
    Next i

    If maxStation <= 0 Then Exit Sub

    ' 2. Buckets (Store Max Magnitude with Sign)
    Dim mStart As Double, vStart As Double
    Dim mMid As Double, vMid As Double
    Dim mEnd As Double, vEnd As Double

    ' Initialize
    mStart = 0: vStart = 0
    mMid = 0: vMid = 0
    mEnd = 0: vEnd = 0

    ' 3. Aggregate
    For i = 1 To rows.Count
        rowData = rows(i)
        sVal = CDbl(Val(rowData(idxStation)))
        mVal = CDbl(Val(rowData(idxM3))) ' Keep Sign!
        vVal = CDbl(Val(rowData(idxV2))) ' Keep Sign!

        ' Bucket Logic (0-20%, 20-80%, 80-100%)
        If sVal <= 0.2 * maxStation Then
            If Abs(mVal) > Abs(mStart) Then mStart = mVal
            If Abs(vVal) > Abs(vStart) Then vStart = vVal
        ElseIf sVal >= 0.8 * maxStation Then
            If Abs(mVal) > Abs(mEnd) Then mEnd = mVal
            If Abs(vVal) > Abs(vEnd) Then vEnd = vVal
        Else
            If Abs(mVal) > Abs(mMid) Then mMid = mVal
            If Abs(vVal) > Abs(vMid) Then vMid = vVal
        End If
    Next i

    ' 4. Write to Table
    Dim parts() As String
    parts = Split(key, "|")
    Dim story As String: story = parts(0)
    Dim label As String: label = parts(1)

    AddRow tbl, label, story, "Start", mStart, vStart
    AddRow tbl, label, story, "Mid", mMid, vMid
    AddRow tbl, label, story, "End", mEnd, vEnd
End Sub

Private Sub AddRow(tbl As ListObject, ID As String, story As String, loc As String, Mu As Double, Vu As Double)
    Dim newRow As ListRow
    Set newRow = tbl.ListRows.Add

    ' Dynamic Column Mapping
    Dim idxID As Integer, idxStory As Integer, idxLoc As Integer
    Dim idxB As Integer, idxD As Integer, idxCover As Integer
    Dim idxFck As Integer, idxFy As Integer
    Dim idxMu As Integer, idxVu As Integer, idxFlanged As Integer

    On Error Resume Next
    idxID = tbl.ListColumns("ID").Index
    idxStory = tbl.ListColumns("Story").Index
    idxLoc = tbl.ListColumns("Span").Index
    idxB = tbl.ListColumns("b").Index
    idxD = tbl.ListColumns("D").Index
    idxCover = tbl.ListColumns("Cover").Index
    idxFck = tbl.ListColumns("fck").Index
    idxFy = tbl.ListColumns("fy").Index
    idxMu = tbl.ListColumns("Mu").Index
    idxVu = tbl.ListColumns("Vu").Index
    idxFlanged = tbl.ListColumns("Flanged").Index
    On Error GoTo 0

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
' Utilities: Robust CSV Parsing & Header Mapping
' ------------------------------------------------------------------------------------------
Private Function MapHeaders(headers() As String) As Collection
    Dim c As New Collection
    Dim i As Long
    Dim h As String

    For i = LBound(headers) To UBound(headers)
        h = NormalizeHeader(headers(i))
        If h <> "" Then
            On Error Resume Next
            c.Add i, h ' Key is normalized name, Item is index
            On Error GoTo 0
        End If
    Next i
    Set MapHeaders = c
End Function

Private Function NormalizeHeader(raw As String) As String
    Dim s As String
    s = UCase(Trim(Replace(raw, """", "")))

    ' Aliases
    If InStr(s, "STORY") > 0 Then NormalizeHeader = COL_STORY: Exit Function
    If InStr(s, "LABEL") > 0 Or InStr(s, "BEAM") > 0 Then NormalizeHeader = COL_LABEL: Exit Function
    If InStr(s, "STATION") > 0 Or InStr(s, "DIST") > 0 Then NormalizeHeader = COL_STATION: Exit Function
    If InStr(s, "M3") > 0 Or InStr(s, "MOMENT") > 0 Then NormalizeHeader = COL_M3: Exit Function
    If InStr(s, "V2") > 0 Or InStr(s, "SHEAR") > 0 Then NormalizeHeader = COL_V2: Exit Function
    If InStr(s, "CASE") > 0 Or InStr(s, "COMBO") > 0 Then NormalizeHeader = COL_CASE: Exit Function

    NormalizeHeader = ""
End Function

Private Function ValidateColumns(map As Collection, ByRef iStory As Long, ByRef iLabel As Long, ByRef iStation As Long, ByRef iM3 As Long, ByRef iV2 As Long) As Boolean
    On Error Resume Next
    iStory = map(COL_STORY)
    iLabel = map(COL_LABEL)
    iStation = map(COL_STATION)
    iM3 = map(COL_M3)
    iV2 = map(COL_V2)
    On Error GoTo 0

    ' Check if all required indices are > 0 (Collection returns Empty/Error if missing? No, Error)
    If iStory < 0 Or iLabel < 0 Or iStation < 0 Or iM3 < 0 Or iV2 < 0 Then
        ValidateColumns = False
    Else
        ValidateColumns = True
    End If
End Function

Private Function ParseCSVLine(line As String) As String()
    ' Robust CSV Parser handling quoted commas
    Dim result() As String
    Dim char As String
    Dim currentField As String
    Dim inQuotes As Boolean
    Dim i As Long
    Dim count As Long

    ReDim result(0 To Len(line)) ' Max possible fields
    count = 0
    inQuotes = False
    currentField = ""

    For i = 1 To Len(line)
        char = Mid(line, i, 1)
        If char = """" Then
            inQuotes = Not inQuotes
        ElseIf char = "," And Not inQuotes Then
            result(count) = currentField
            count = count + 1
            currentField = ""
        Else
            currentField = currentField & char
        End If
    Next i

    result(count) = currentField
    ReDim Preserve result(0 To count)
    ParseCSVLine = result
End Function

Private Function PromptForPath(prompt As String) As String
    Dim p As String
    p = InputBox(prompt, "Locate CSV")
    If Len(p) = 0 Then
        PromptForPath = ""
        Exit Function
    End If
    PromptForPath = p
End Function

' ------------------------------------------------------------------------------------------
' Helper: Populate sample data (for environments without ETABS/CSV)
' ------------------------------------------------------------------------------------------
Private Sub Populate_Sample_Input(tbl As ListObject)
    ' Columns: ID, Story, Span, b, D, Cover, fck, fy, Mu, Vu, Flanged?, Df, bf
    Dim samples As Variant
    samples = Array( _
        Array("B1", "S1", "Start", 230, 450, 25, 25, 500, -50, 90, "No", 0, 0), _
        Array("B1", "S1", "Mid", 230, 450, 25, 25, 500, 150, 120, "No", 0, 0), _
        Array("B1", "S1", "End", 230, 450, 25, 25, 500, -50, 90, "No", 0, 0), _
        Array("B2", "S2", "Start", 300, 550, 30, 30, 500, -60, 100, "Yes", 120, 800), _
        Array("B2", "S2", "Mid", 300, 550, 30, 30, 500, 180, 140, "Yes", 120, 800), _
        Array("B2", "S2", "End", 300, 550, 30, 30, 500, -60, 100, "Yes", 120, 800), _
        Array("B3", "S3", "Start", 250, 600, 30, 25, 415, -80, 150, "No", 0, 0), _
        Array("B3", "S3", "Mid", 250, 600, 30, 25, 415, 200, 180, "No", 0, 0), _
        Array("B3", "S3", "End", 250, 600, 30, 25, 415, -70, 140, "No", 0, 0) _
    )

    ' Clear existing rows
    If Not tbl.DataBodyRange Is Nothing Then
        tbl.DataBodyRange.Delete
    End If

    Dim i As Long
    For i = LBound(samples) To UBound(samples)
        Dim lr As ListRow
        Set lr = tbl.ListRows.Add
        lr.Range.Cells(1, 1).Resize(1, 13).Value = samples(i)
    Next i
End Sub

' ------------------------------------------------------------------------------------------
' Helper: Generate a sample ETABS-style CSV (optional)
' ------------------------------------------------------------------------------------------
Public Sub Generate_Sample_ETABS_CSV()
    Dim filePath As Variant
    Dim fnum As Integer
    Dim rows As Variant
    Dim i As Long

    rows = Array( _
        Array("S1", "B1", 0, -50, 90, "COMBO1"), _
        Array("S1", "B1", 5, 150, 120, "COMBO1"), _
        Array("S1", "B1", 10, -50, 90, "COMBO1"), _
        Array("S2", "B2", 0, -60, 100, "COMBO1"), _
        Array("S2", "B2", 6, 180, 140, "COMBO1"), _
        Array("S2", "B2", 12, -60, 100, "COMBO1"), _
        Array("S3", "B3", 0, -80, 150, "COMBO1"), _
        Array("S3", "B3", 7, 200, 180, "COMBO1"), _
        Array("S3", "B3", 14, -70, 140, "COMBO1") _
    )

    filePath = Application.GetSaveAsFilename("ETABS_Sample_Export.csv", "CSV Files (*.csv), *.csv", , "Save sample ETABS CSV")
    If filePath = False Then Exit Sub

    fnum = FreeFile
    Open CStr(filePath) For Output As #fnum
    Print #fnum, "Story,Label,Station,M3,V2,Output Case"

    For i = LBound(rows) To UBound(rows)
        Print #fnum, rows(i)(0) & "," & rows(i)(1) & "," & rows(i)(2) & "," & rows(i)(3) & "," & rows(i)(4) & "," & rows(i)(5)
    Next i

    Close #fnum
    MsgBox "Sample ETABS CSV saved to: " & filePath, vbInformation
End Sub
