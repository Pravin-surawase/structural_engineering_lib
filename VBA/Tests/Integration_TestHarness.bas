Attribute VB_Name = "Integration_TestHarness"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' Populates BEAM_INPUT with a small battery of cases and optionally runs the design.
' Use this from the test workbook to sanity check end-to-end flow.

Public Sub Populate_BeamInput_TestCases()
    Dim ws As Worksheet
    Dim tbl As ListObject
    Dim i As Long

    On Error GoTo Fail
    Set ws = ThisWorkbook.Sheets("BEAM_INPUT")
    Set tbl = ws.ListObjects("tbl_BeamInput")

    ' Clear existing rows
    If Not tbl.DataBodyRange Is Nothing Then
        tbl.DataBodyRange.Delete
    End If

    ' Test cases: ID, Story, Span, b, D, Cover, fck, fy, Mu, Vu, Flanged?, Df, bf
    Dim cases As Variant
    cases = Array( _
        Array("Singly_OK", "S1", "Mid", 230, 450, 25, 25, 500, 150, 100, "No", 0, 0), _
        Array("Flanged_OK", "S2", "Mid", 300, 550, 30, 25, 500, 200, 120, "Yes", 120, 800), _
        Array("High_Mu_Doubly", "S3", "Mid", 250, 500, 25, 30, 415, 260, 110, "No", 0, 0), _
        Array("High_Vu_Shear", "S4", "Support", 230, 450, 25, 20, 500, 120, 250, "No", 0, 0), _
        Array("Shear_Over_Tcmax", "S5", "Support", 200, 450, 25, 20, 500, 80, 400, "No", 0, 0) _
    )

    For i = LBound(cases) To UBound(cases)
        Dim row As ListRow
        Set row = tbl.ListRows.Add
        row.Range.Cells(1, 1).Resize(1, 13).Value = cases(i)
    Next i

    MsgBox "Populated " & (UBound(cases) - LBound(cases) + 1) & " test rows into BEAM_INPUT.", vbInformation
    Exit Sub
Fail:
    MsgBox "Populate failed: " & Err.Description, vbCritical
End Sub

Public Sub Run_Integration_TestSuite()
    On Error GoTo Fail
    Populate_BeamInput_TestCases
    M11_AppLayer.Run_BeamDesign
    MsgBox "Integration test run complete. Review BEAM_DESIGN for results.", vbInformation
    Exit Sub
Fail:
    MsgBox "Integration test run failed: " & Err.Description, vbCritical
End Sub

Public Sub Export_BEAM_DESIGN_ToCSV()
    ' Exports BEAM_DESIGN table to CSV for quick regression snapshots.
    Dim ws As Worksheet
    Dim tbl As ListObject
    Dim filePath As Variant
    Dim fnum As Integer
    Dim r As Long, c As Long

    On Error GoTo Fail
    Set ws = ThisWorkbook.Sheets("BEAM_DESIGN")
    Set tbl = ws.ListObjects("tbl_BeamDesign")

    If tbl.DataBodyRange Is Nothing Then
        MsgBox "No data in BEAM_DESIGN to export.", vbExclamation
        Exit Sub
    End If

    filePath = Application.GetSaveAsFilename( _
        InitialFileName:="BEAM_DESIGN_snapshot.csv", _
        FileFilter:="CSV Files (*.csv), *.csv")
    If filePath = False Then Exit Sub

    fnum = FreeFile
    Open CStr(filePath) For Output As #fnum

    ' Write headers
    For c = 1 To tbl.HeaderRowRange.Columns.Count
        Print #fnum, CleanCsv(tbl.HeaderRowRange.Cells(1, c).Value, c = tbl.HeaderRowRange.Columns.Count);
    Next c
    Print #fnum, ""

    ' Write rows
    For r = 1 To tbl.DataBodyRange.Rows.Count
        For c = 1 To tbl.DataBodyRange.Columns.Count
            Print #fnum, CleanCsv(tbl.DataBodyRange.Cells(r, c).Value, c = tbl.DataBodyRange.Columns.Count);
        Next c
        Print #fnum, ""
    Next r

    Close #fnum
    MsgBox "Exported BEAM_DESIGN to: " & filePath, vbInformation
    Exit Sub
Fail:
    On Error Resume Next
    Close #fnum
    MsgBox "Export failed: " & Err.Description, vbCritical
End Sub

Public Sub Run_And_Export_Integration_Snapshot()
    On Error GoTo Fail
    Run_Integration_TestSuite
    Export_BEAM_DESIGN_ToCSV
    Exit Sub
Fail:
    MsgBox "Run/Export failed: " & Err.Description, vbCritical
End Sub

Private Function CleanCsv(val As Variant, isLast As Boolean) As String
    Dim s As String
    s = CStr(val)
    If InStr(1, s, ",") > 0 Or InStr(1, s, """") > 0 Then
        s = """" & Replace(s, """", """""") & """"
    End If
    If isLast Then
        CleanCsv = s
    Else
        CleanCsv = s & ","
    End If
End Function
