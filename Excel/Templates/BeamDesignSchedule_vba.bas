Attribute VB_Name = "BeamDesignSchedule_Exports"
Option Explicit

' ======================================================================
' Task 1.1 helper: build the workbook structure automatically
' ======================================================================

' Creates/overwrites the Task 1.1 template layout:
' - Sheets: Design, Instructions, Summary
' - Design headers A:Q, formulas J:Q, formatting and conditional rules
' - Sample data rows 2-11
' - Adds an "Export All Beams to DXF" button (best-effort)
Public Sub BeamDesignSchedule_SetupWorkbook()
    On Error GoTo ErrHandler

    Dim wb As Workbook
    Set wb = ThisWorkbook

    Application.ScreenUpdating = False

    Dim wsDesign As Worksheet
    Dim wsInstructions As Worksheet
    Dim wsSummary As Worksheet

    Set wsDesign = EnsureSheet(wb, "Design")
    Set wsInstructions = EnsureSheet(wb, "Instructions")
    Set wsSummary = EnsureSheet(wb, "Summary")

    Setup_Design_Sheet wsDesign
    Setup_Instructions_Sheet wsInstructions
    Setup_Summary_Sheet wsSummary

    wsDesign.Activate
    wsDesign.Range("A2").Select

    Application.ScreenUpdating = True

    MsgBox "BeamDesignSchedule template created (Task 1.1)." & vbCrLf & _
           "Next: confirm StructEngLib add-in is loaded (no #NAME?).", vbInformation, "Setup Complete"
    Exit Sub

ErrHandler:
    Application.ScreenUpdating = True
    MsgBox "Error: " & Err.Description, vbCritical, "Setup Failed"
End Sub

' Export all non-empty beams from sheet "Design" to DXF.
'
' This module is intended to be IMPORTED into the workbook:
'   Excel/Templates/BeamDesignSchedule.xlsm
'
' It calls StructEngLib add-in functions via Application.Run to avoid
' cross-project type dependencies.
'
' Expected headers (per Task 1.1 spec):
'   BeamID, D (mm), Cover (mm), Bar Callout, Stirrup Spacing (mm), Stirrup Callout
'
' If "Span (mm)" column is not present, the macro prompts once and uses that
' value for all beams.
Public Sub BeamDesignSchedule_ExportAllBeamsToDXF()
    On Error GoTo ErrHandler

    Dim ws As Worksheet
    Set ws = ThisWorkbook.Worksheets("Design")

    Dim colBeamId As Long
    Dim colD As Long
    Dim colCover As Long
    Dim colSpan As Long
    Dim colBarCallout As Long
    Dim colStirrupSpacing As Long
    Dim colStirrupCallout As Long

    colBeamId = FindHeaderColumn(ws, "BeamID")
    colD = FindHeaderColumn(ws, "D (mm)")
    colCover = FindHeaderColumn(ws, "Cover (mm)")

    ' Optional columns (macro will fall back safely)
    colSpan = FindHeaderColumn(ws, "Span (mm)")
    colBarCallout = FindHeaderColumn(ws, "Bar Callout")
    colStirrupSpacing = FindHeaderColumn(ws, "Stirrup Spacing (mm)")
    colStirrupCallout = FindHeaderColumn(ws, "Stirrup Callout")

    If colBeamId = 0 Or colD = 0 Or colCover = 0 Then
        MsgBox "Missing required headers in row 1. Need at least: BeamID, D (mm), Cover (mm).", vbExclamation, "Export All Beams to DXF"
        Exit Sub
    End If

    Dim outFolder As String
    outFolder = PickOutputFolder()
    If Len(outFolder) = 0 Then Exit Sub

    Dim defaultSpanMm As Double
    defaultSpanMm = 0

    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, colBeamId).End(xlUp).Row
    If lastRow < 2 Then
        MsgBox "No beam rows found (BeamID column is empty).", vbInformation, "Export All Beams to DXF"
        Exit Sub
    End If

    Dim total As Long, okCount As Long, failCount As Long
    Dim r As Long

    For r = 2 To lastRow
        Dim beamId As String
        beamId = Trim(CStr(ws.Cells(r, colBeamId).Value))
        If Len(beamId) = 0 Then
            ' Skip empty rows
            GoTo NextRow
        End If

        total = total + 1

        Dim Dmm As Double
        Dim coverMm As Double
        Dmm = CDbl(ws.Cells(r, colD).Value)
        coverMm = CDbl(ws.Cells(r, colCover).Value)

        Dim spanMm As Double
        spanMm = 0
        If colSpan > 0 Then
            If IsNumeric(ws.Cells(r, colSpan).Value) Then
                spanMm = CDbl(ws.Cells(r, colSpan).Value)
            End If
        End If

        If spanMm <= 0 Then
            If defaultSpanMm <= 0 Then
                defaultSpanMm = PromptForDefaultSpanMm()
                If defaultSpanMm <= 0 Then Exit Sub
            End If
            spanMm = defaultSpanMm
        End If

        Dim bottomDiaMm As Double
        bottomDiaMm = 0
        If colBarCallout > 0 Then
            bottomDiaMm = ParseDiameterMmFromPhiCallout(CStr(ws.Cells(r, colBarCallout).Value))
        End If
        If bottomDiaMm <= 0 Then bottomDiaMm = 16

        Dim topDiaMm As Double
        topDiaMm = bottomDiaMm

        Dim stirrupDiaMm As Double
        stirrupDiaMm = 0
        If colStirrupCallout > 0 Then
            stirrupDiaMm = ParseDiameterMmFromPhiCallout(CStr(ws.Cells(r, colStirrupCallout).Value))
        End If
        If stirrupDiaMm <= 0 Then stirrupDiaMm = 8

        Dim stirrupSpacingMm As Double
        stirrupSpacingMm = 0
        If colStirrupSpacing > 0 Then
            If IsNumeric(ws.Cells(r, colStirrupSpacing).Value) Then
                stirrupSpacingMm = CDbl(ws.Cells(r, colStirrupSpacing).Value)
            End If
        End If
        If stirrupSpacingMm <= 0 And colStirrupCallout > 0 Then
            stirrupSpacingMm = ParseSpacingMmFromStirrupCallout(CStr(ws.Cells(r, colStirrupCallout).Value))
        End If
        If stirrupSpacingMm <= 0 Then stirrupSpacingMm = 150

        Dim safeBeamId As String
        safeBeamId = SanitizeFileStem(beamId)

        Dim filePath As String
        filePath = JoinPath(outFolder, safeBeamId & ".dxf")

        Dim result As Variant
        result = Application.Run("IS456_DrawLongitudinal", filePath, spanMm, Dmm, coverMm, topDiaMm, bottomDiaMm, stirrupDiaMm, stirrupSpacingMm)

        If VarType(result) = vbBoolean Then
            If CBool(result) = True Then
                okCount = okCount + 1
            Else
                failCount = failCount + 1
                Debug.Print "DXF export failed (false): " & beamId & " -> " & filePath
            End If
        ElseIf VarType(result) = vbString Then
            failCount = failCount + 1
            Debug.Print "DXF export failed: " & beamId & " -> " & CStr(result)
        Else
            ' Unexpected return
            failCount = failCount + 1
            Debug.Print "DXF export returned unexpected type for beam " & beamId
        End If

        If (total Mod 10) = 0 Then
            Application.StatusBar = "Exported " & total & " beams..."
            DoEvents
        End If

NextRow:
    Next r

    Application.StatusBar = False

    MsgBox "DXF export complete." & vbCrLf & _
           "Total: " & total & vbCrLf & _
           "Success: " & okCount & vbCrLf & _
           "Failed: " & failCount & vbCrLf & vbCrLf & _
           "Output folder:" & vbCrLf & outFolder, vbInformation, "Export All Beams to DXF"

    Exit Sub

ErrHandler:
    Application.StatusBar = False
    MsgBox "Error: " & Err.Description, vbCritical, "Export All Beams to DXF"
End Sub


' --- Helpers ---

Private Function EnsureSheet(ByVal wb As Workbook, ByVal sheetName As String) As Worksheet
    On Error Resume Next
    Set EnsureSheet = wb.Worksheets(sheetName)
    On Error GoTo 0

    If EnsureSheet Is Nothing Then
        Set EnsureSheet = wb.Worksheets.Add(After:=wb.Worksheets(wb.Worksheets.Count))
        EnsureSheet.Name = sheetName
    End If
End Function

Private Sub Setup_Design_Sheet(ByVal ws As Worksheet)
    ws.Cells.Clear

    Dim headers As Variant
    headers = Array( _
        "BeamID", "b (mm)", "D (mm)", "d (mm)", "fck", "fy", "Mu (kN-m)", "Vu (kN)", "Cover (mm)", _
        "Mu_lim (kN-m)", "Ast (mm^2)", "Bar Count", "Bar Callout", "Stirrup Spacing (mm)", "Stirrup Callout", "Ld (mm)", "Status" _
    )

    ws.Range("A1").Resize(1, UBound(headers) + 1).Value = headers

    ' Header formatting
    With ws.Range("A1").Resize(1, UBound(headers) + 1)
        .Font.Name = "Calibri"
        .Font.Size = 11
        .Font.Bold = True
        .Font.Color = RGB(255, 255, 255)
        .Interior.Color = RGB(0, 32, 96)
        .HorizontalAlignment = xlCenter
        .VerticalAlignment = xlCenter
        .Borders.LineStyle = xlContinuous
    End With

    ws.Rows(1).RowHeight = 20

    ' Input region format
    With ws.Range("A2:I51")
        .Borders.LineStyle = xlContinuous
    End With

    ' Output region format
    With ws.Range("J2:Q51")
        .Interior.Color = RGB(242, 242, 242)
        .Font.Italic = True
        .Borders.LineStyle = xlContinuous
    End With
    ws.Range("Q2:Q51").Font.Italic = False

    ' Data validation for inputs B:I
    Apply_PositiveDecimalValidation ws.Range("B2:I51")

    ' Formulas (row 2)
    ws.Range("J2").Formula = "=IS456_MuLim(B2,D2,E2,F2)"
    ws.Range("K2").Formula = "=IS456_AstRequired(B2,D2,G2,E2,F2)"
    ws.Range("L2").Formula = "=IF(ISNUMBER(K2),CEILING(K2/201,1),\"\")"
    ws.Range("M2").Formula = "=IF(ISNUMBER(L2),IS456_BarCallout(L2,16),\"\")"
    ws.Range("N2").Formula = "=IS456_ShearSpacing(H2,B2,D2,E2,F2,100,K2*100/(B2*D2))"
    ws.Range("O2").Formula = "=IF(ISNUMBER(N2),IS456_StirrupCallout(2,8,FLOOR(N2/25,1)*25),\"\")"
    ws.Range("P2").Formula = "=IS456_Ld(16,E2,F2)"
    ws.Range("Q2").Formula = "=IF(AND(ISNUMBER(K2),G2<=J2),\"Safe\",\"Check\")"

    ws.Range("J2:Q2").AutoFill Destination:=ws.Range("J2:Q51")

    ' Conditional formatting
    Apply_StatusConditionalFormatting ws

    ' Freeze header row
    ws.Activate
    ws.Range("A2").Select
    ActiveWindow.FreezePanes = True

    ' Column widths (simple, readable defaults)
    ws.Columns("A").ColumnWidth = 10
    ws.Columns("B:I").ColumnWidth = 10
    ws.Columns("J:Q").ColumnWidth = 14

    ' Sample data rows 2-11
    Populate_SampleData ws

    ' Add export button (best-effort)
    Add_ExportButton ws
End Sub

Private Sub Apply_PositiveDecimalValidation(ByVal rng As Range)
    On Error Resume Next
    rng.Validation.Delete
    On Error GoTo 0

    rng.Validation.Add Type:=xlValidateDecimal, AlertStyle:=xlValidAlertStop, Operator:=xlGreater, Formula1:="0"
    rng.Validation.IgnoreBlank = True
    rng.Validation.InCellDropdown = True
    rng.Validation.ErrorTitle = "Invalid value"
    rng.Validation.ErrorMessage = "Value must be greater than 0"
End Sub

Private Sub Apply_StatusConditionalFormatting(ByVal ws As Worksheet)
    Dim rngStatus As Range
    Set rngStatus = ws.Range("Q2:Q51")

    rngStatus.FormatConditions.Delete
    ws.Range("A2:Q51").FormatConditions.Delete
    ws.Range("K2:K51").FormatConditions.Delete

    ' Red for Check
    With rngStatus.FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="=\"Check\"")
        .Interior.Color = RGB(255, 199, 206)
        .Font.Color = RGB(156, 0, 6)
    End With

    ' Green for Safe
    With rngStatus.FormatConditions.Add(Type:=xlCellValue, Operator:=xlEqual, Formula1:="=\"Safe\"")
        .Interior.Color = RGB(198, 239, 206)
        .Font.Color = RGB(0, 97, 0)
    End With

    ' Entire row highlight when Check
    With ws.Range("A2:Q51").FormatConditions.Add(Type:=xlExpression, Formula1:="=$Q2=\"Check\"")
        .Interior.Color = RGB(255, 242, 204)
    End With

    ' Over-reinforced indicator (text contains)
    With ws.Range("K2:K51").FormatConditions.Add(Type:=xlTextString, String:="Over-Reinforced", TextOperator:=xlContains)
        .Interior.Color = RGB(255, 229, 204)
        .Font.Bold = True
    End With
End Sub

Private Sub Populate_SampleData(ByVal ws As Worksheet)
    Dim data As Variant
    data = Array( _
        Array("B1", 300, 500, 450, 25, 500, 150, 100, 40), _
        Array("B2", 300, 450, 400, 25, 500, 120, 80, 40), _
        Array("B3", 350, 600, 550, 30, 500, 250, 150, 40), _
        Array("B4", 230, 450, 400, 25, 500, 100, 70, 40), _
        Array("B5", 300, 500, 450, 25, 500, 180, 120, 40), _
        Array("B6", 400, 600, 550, 30, 500, 280, 180, 50), _
        Array("B7", 300, 450, 400, 20, 500, 90, 60, 40), _
        Array("B8", 350, 550, 500, 25, 500, 200, 130, 40), _
        Array("B9", 230, 400, 350, 25, 500, 80, 50, 40), _
        Array("B10", 300, 500, 450, 25, 500, 160, 110, 40) _
    )

    Dim r As Long, c As Long
    For r = 0 To UBound(data)
        For c = 0 To 8
            ws.Cells(2 + r, 1 + c).Value = data(r)(c)
        Next c
    Next r
End Sub

Private Sub Add_ExportButton(ByVal ws As Worksheet)
    On Error GoTo Skip

    ' Remove existing buttons with same caption (best-effort)
    Dim shp As Shape
    For Each shp In ws.Shapes
        If shp.Type = msoFormControl Then
            If shp.FormControlType = xlButtonControl Then
                If InStr(1, shp.TextFrame.Characters.Text, "Export All", vbTextCompare) > 0 Then
                    shp.Delete
                End If
            End If
        End If
    Next shp

    Dim btn As Shape
    Set btn = ws.Shapes.AddFormControl(Type:=xlButtonControl, _
                                      Left:=ws.Range("S2").Left, _
                                      Top:=ws.Range("S2").Top, _
                                      Width:=180, Height:=28)
    btn.TextFrame.Characters.Text = "Export All Beams to DXF"
    btn.OnAction = "BeamDesignSchedule_ExportAllBeamsToDXF"
    Exit Sub

Skip:
    ' If button creation fails (some Mac builds), it's safe to ignore.
End Sub

Private Sub Setup_Instructions_Sheet(ByVal ws As Worksheet)
    ws.Cells.Clear
    ws.Columns("A").ColumnWidth = 2
    ws.Columns("B:H").ColumnWidth = 18

    With ws.Range("B2:H2")
        .Merge
        .Value = "Beam Design Schedule - User Guide"
        .Font.Size = 16
        .Font.Bold = True
        .HorizontalAlignment = xlCenter
    End With

    ws.Range("B4").Value = "How to Use"
    ws.Range("B4").Font.Bold = True

    ws.Range("B5").Value = "1. Input Data (Columns A-I): Beam ID, dimensions, materials, loads, cover (units in headers)."
    ws.Range("B6").Value = "2. Review Results (Columns J-Q): auto-calculated using IS 456:2000 UDFs."
    ws.Range("B7").Value = "   Safe = design is valid; Check = review required."
    ws.Range("B8").Value = "3. Export to DXF: click 'Export All Beams to DXF' and choose an output folder."

    ws.Range("B10").Value = "Troubleshooting"
    ws.Range("B10").Font.Bold = True
    ws.Range("B11").Value = "#NAME? : StructEngLib add-in not loaded (load StructEngLib.xlam)."
    ws.Range("B12").Value = "#VALUE! : Check input values (must be numeric, > 0)."
    ws.Range("B13").Value = "Over-Reinforced: beam requires a different design (e.g., doubly reinforced)."

    ws.Range("B5:B13").WrapText = True
End Sub

Private Sub Setup_Summary_Sheet(ByVal ws As Worksheet)
    ws.Cells.Clear
    ws.Columns("A").ColumnWidth = 22
    ws.Columns("B").ColumnWidth = 18

    ws.Range("A1").Value = "DESIGN SUMMARY"
    ws.Range("A1").Font.Size = 16
    ws.Range("A1").Font.Bold = True

    ws.Range("A3").Value = "Total Beams:"
    ws.Range("A4").Value = "Safe Beams:"
    ws.Range("A5").Value = "Check Required:"
    ws.Range("A6").Value = "Success Rate:"

    ws.Range("B3").Formula = "=COUNTA(Design!A2:A51)"
    ws.Range("B4").Formula = "=COUNTIF(Design!Q2:Q51,\"Safe\")"
    ws.Range("B5").Formula = "=COUNTIF(Design!Q2:Q51,\"Check\")"
    ws.Range("B6").Formula = "=IF(B3=0,\"\",B4/B3)"
    ws.Range("B6").NumberFormat = "0.0%"

    ws.Range("A8").Value = "MATERIAL SUMMARY"
    ws.Range("A8").Font.Bold = True
    ws.Range("A9").Value = "Total Steel (kg):"
    ws.Range("B9").Formula = "=SUM(Design!K2:K51)*7850/1000000*4"

    ws.Range("A11").Value = "CRITICAL BEAMS (Top 5 by Mu)"
    ws.Range("A11").Font.Bold = True
    ws.Range("A12").Value = "BeamID"
    ws.Range("B12").Value = "Mu"
    ws.Range("C12").Value = "Status"
    ws.Range("A12:C12").Font.Bold = True
    ws.Range("A12:C12").Borders.LineStyle = xlContinuous

    ' Keep this simple/manual for now; users can sort Design and paste top 5.
    ws.Range("A13").Value = "(Tip: sort Design sheet by Mu desc and copy top 5 here)"
    ws.Range("A13:C13").Merge
    ws.Range("A13").WrapText = True
End Sub

Private Function FindHeaderColumn(ByVal ws As Worksheet, ByVal headerText As String) As Long
    Dim lastCol As Long
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column

    Dim c As Long
    For c = 1 To lastCol
        If Trim(CStr(ws.Cells(1, c).Value)) = headerText Then
            FindHeaderColumn = c
            Exit Function
        End If
    Next c

    FindHeaderColumn = 0
End Function

Private Function PickOutputFolder() As String
    On Error GoTo Fallback

    Dim fd As FileDialog
    Set fd = Application.FileDialog(msoFileDialogFolderPicker)

    With fd
        .Title = "Select output folder for DXF files"
        .AllowMultiSelect = False
        If .Show <> -1 Then
            PickOutputFolder = ""
            Exit Function
        End If
        PickOutputFolder = .SelectedItems(1)
    End With

    Exit Function

Fallback:
    Dim folderPath As String
    folderPath = InputBox("Enter output folder full path for DXF files:", "DXF Output Folder")
    PickOutputFolder = Trim(folderPath)
End Function

Private Function PromptForDefaultSpanMm() As Double
    Dim s As String
    s = InputBox("Beam span is not provided in the table." & vbCrLf & _
                 "Enter default span in mm to use for ALL beams:", "Default Span (mm)")

    If Len(Trim(s)) = 0 Then
        PromptForDefaultSpanMm = 0
        Exit Function
    End If

    If IsNumeric(s) Then
        PromptForDefaultSpanMm = CDbl(s)
    Else
        MsgBox "Span must be numeric (mm).", vbExclamation, "Default Span (mm)"
        PromptForDefaultSpanMm = 0
    End If
End Function

Private Function ParseDiameterMmFromPhiCallout(ByVal callout As String) As Double
    ' Extracts diameter from strings like:
    '   "5-16φ"
    '   "2L-8φ@150"
    ' Strategy: find "φ" and scan left for the last numeric token.

    Dim s As String
    s = Replace(callout, " ", "")

    Dim phiPos As Long
    phiPos = InStr(1, s, "φ", vbTextCompare)
    If phiPos = 0 Then
        ParseDiameterMmFromPhiCallout = 0
        Exit Function
    End If

    Dim i As Long
    Dim digits As String
    digits = ""

    For i = phiPos - 1 To 1 Step -1
        Dim ch As String
        ch = Mid$(s, i, 1)
        If (ch >= "0" And ch <= "9") Or ch = "." Then
            digits = ch & digits
        Else
            If Len(digits) > 0 Then Exit For
        End If
    Next i

    If Len(digits) = 0 Then
        ParseDiameterMmFromPhiCallout = 0
    Else
        ParseDiameterMmFromPhiCallout = CDbl(digits)
    End If
End Function

Private Function ParseSpacingMmFromStirrupCallout(ByVal callout As String) As Double
    ' Extracts spacing from strings like "2L-8φ@150" (or "...@150c/c").

    Dim s As String
    s = Replace(callout, " ", "")

    Dim atPos As Long
    atPos = InStr(1, s, "@", vbTextCompare)
    If atPos = 0 Then
        ParseSpacingMmFromStirrupCallout = 0
        Exit Function
    End If

    Dim i As Long
    Dim digits As String
    digits = ""

    For i = atPos + 1 To Len(s)
        Dim ch As String
        ch = Mid$(s, i, 1)
        If (ch >= "0" And ch <= "9") Or ch = "." Then
            digits = digits & ch
        Else
            Exit For
        End If
    Next i

    If Len(digits) = 0 Then
        ParseSpacingMmFromStirrupCallout = 0
    Else
        ParseSpacingMmFromStirrupCallout = CDbl(digits)
    End If
End Function

Private Function SanitizeFileStem(ByVal fileStem As String) As String
    Dim s As String
    s = Trim(fileStem)

    s = Replace(s, "/", "-")
    s = Replace(s, "\\", "-")
    s = Replace(s, ":", "-")
    s = Replace(s, "*", "-")
    s = Replace(s, "?", "-")
    s = Replace(s, "\"", "-")
    s = Replace(s, "<", "-")
    s = Replace(s, ">", "-")
    s = Replace(s, "|", "-")

    If Len(s) = 0 Then s = "beam"

    SanitizeFileStem = s
End Function

Private Function JoinPath(ByVal folderPath As String, ByVal fileName As String) As String
    If Right$(folderPath, 1) = "/" Or Right$(folderPath, 1) = "\\" Then
        JoinPath = folderPath & fileName
    Else
        JoinPath = folderPath & Application.PathSeparator & fileName
    End If
End Function
