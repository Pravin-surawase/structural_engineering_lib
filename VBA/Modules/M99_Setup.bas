Attribute VB_Name = "M99_Setup"
Option Explicit

' ==============================================================================
' Module:       M99_Setup
' Description:  Scaffolding script to generate the v0.5 Workbook Structure
' Author:       UI Agent
' Usage:        Run 'Setup_Workbook' in a blank Excel file
' ==============================================================================

Public Sub Setup_Workbook()
    Dim wb As Workbook
    Set wb = ActiveWorkbook
    
    Application.ScreenUpdating = False
    
    ' 1. Create Sheets
    EnsureSheet wb, "HOME"
    EnsureSheet wb, "BEAM_INPUT"
    EnsureSheet wb, "BEAM_DESIGN"
    EnsureSheet wb, "BEAM_SCHEDULE"
    EnsureSheet wb, "LOG"
    
    ' 2. Setup HOME Sheet
    Setup_Home_Sheet wb.Sheets("HOME")
    
    ' 3. Setup BEAM_INPUT Table
    Setup_Input_Sheet wb.Sheets("BEAM_INPUT")
    
    ' 4. Setup BEAM_DESIGN Table
    Setup_Design_Sheet wb.Sheets("BEAM_DESIGN")
    
    ' 5. Setup LOG Sheet
    Setup_Log_Sheet wb.Sheets("LOG")
    
    ' Cleanup
    wb.Sheets("HOME").Activate
    Application.ScreenUpdating = True
    MsgBox "Workbook Structure Created Successfully (v0.5)", vbInformation
End Sub

Private Sub EnsureSheet(wb As Workbook, sheetName As String)
    On Error Resume Next
    Dim ws As Worksheet
    Set ws = wb.Sheets(sheetName)
    On Error GoTo 0
    
    If ws Is Nothing Then
        Set ws = wb.Sheets.Add(After:=wb.Sheets(wb.Sheets.Count))
        ws.Name = sheetName
    End If
End Sub

Private Sub Setup_Home_Sheet(ws As Worksheet)
    ws.Cells.Clear
    
    ' Title
    With ws.Range("B2")
        .Value = "IS 456 RC Beam Design Engine"
        .Font.Size = 24
        .Font.Bold = True
        .Font.Color = RGB(0, 51, 102)
    End With
    
    With ws.Range("B3")
        .Value = "Version 0.5.0 | Status: Beta"
        .Font.Size = 12
        .Font.Italic = True
    End With
    
    ' Dashboard Placeholder
    ws.Range("B6").Value = "Total Beams"
    ws.Range("C6").Value = "Passed"
    ws.Range("D6").Value = "Failed"
    
    ws.Range("B7").Value = 0
    ws.Range("C7").Value = 0
    ws.Range("D7").Value = 0
    
    Format_Dashboard_Card ws.Range("B6:B7")
    Format_Dashboard_Card ws.Range("C6:C7")
    Format_Dashboard_Card ws.Range("D6:D7")
    
    ' Instructions
    ws.Range("B10").Value = "Instructions:"
    ws.Range("B11").Value = "1. Go to BEAM_INPUT sheet and enter beam geometry/loads."
    ws.Range("B12").Value = "2. Click 'Run Design' (Macro: Main_RunDesign)."
    ws.Range("B13").Value = "3. Check BEAM_DESIGN for detailed results."
    
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B:E").ColumnWidth = 20
End Sub

Private Sub Format_Dashboard_Card(rng As Range)
    With rng
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .Borders.LineStyle = xlContinuous
        .Interior.Color = RGB(240, 240, 240)
    End With
    rng.Cells(1, 1).Font.Bold = True
    rng.Cells(2, 1).Font.Size = 14
End Sub

Private Sub Setup_Input_Sheet(ws As Worksheet)
    ws.Cells.Clear
    ws.Range("A1").Value = "Beam Input Data"
    ws.Range("A1").Font.Size = 16
    ws.Range("A1").Font.Bold = True
    
    ' Headers
    Dim headers As Variant
    headers = Array("ID", "Story", "Span", "b (mm)", "D (mm)", "Cover (mm)", "fck", "fy", "Mu (kNm)", "Vu (kN)", "Flanged?", "Df (mm)", "bf (mm)")
    
    ws.Range("A3").Resize(1, UBound(headers) + 1).Value = headers
    
    ' Create Table
    Dim tbl As ListObject
    On Error Resume Next
    Set tbl = ws.ListObjects("tbl_BeamInput")
    On Error GoTo 0
    
    If tbl Is Nothing Then
        Set tbl = ws.ListObjects.Add(xlSrcRange, ws.Range("A3").Resize(2, UBound(headers) + 1), , xlYes)
        tbl.Name = "tbl_BeamInput"
    End If
    
    ' Formatting
    tbl.TableStyle = "TableStyleMedium2"
    tbl.DataBodyRange.Interior.Color = RGB(255, 255, 204) ' Input Color
    
    ws.Columns.AutoFit
End Sub

Private Sub Setup_Design_Sheet(ws As Worksheet)
    ws.Cells.Clear
    ws.Range("A1").Value = "Design Results"
    ws.Range("A1").Font.Size = 16
    ws.Range("A1").Font.Bold = True
    
    ' Headers (Full Input Mirror + Results)
    Dim headers As Variant
    headers = Array("ID", "Story", "Span", "b", "D", "Cover", "fck", "fy", "Mu", "Vu", "Flanged?", "Df", "bf", _
                    "d_eff", "Mu_Lim", "Status", "Ast_Req", "Pt_Prov", "Asc_Req", "Tv", "Tc", "Shear_Sts", "Stirrups", "Remarks")
    
    ws.Range("A3").Resize(1, UBound(headers) + 1).Value = headers
    
    ' Create Table
    Dim tbl As ListObject
    On Error Resume Next
    Set tbl = ws.ListObjects("tbl_BeamDesign")
    On Error GoTo 0
    
    If tbl Is Nothing Then
        Set tbl = ws.ListObjects.Add(xlSrcRange, ws.Range("A3").Resize(2, UBound(headers) + 1), , xlYes)
        tbl.Name = "tbl_BeamDesign"
    End If
    
    ' Formatting
    tbl.TableStyle = "TableStyleLight9"
    tbl.DataBodyRange.Interior.Color = RGB(242, 242, 242) ' Output Color
    
    ws.Columns.AutoFit
End Sub

Private Sub Setup_Log_Sheet(ws As Worksheet)
    ws.Cells.Clear
    ws.Range("A1").Value = "Execution Log"
    ws.Range("A3").Value = "Timestamp"
    ws.Range("B3").Value = "Level"
    ws.Range("C3").Value = "Message"
    
    ws.Columns("A").ColumnWidth = 20
    ws.Columns("B").ColumnWidth = 10
    ws.Columns("C").ColumnWidth = 80
End Sub
