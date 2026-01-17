Attribute VB_Name = "M11_AppLayer"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==========================================================================================
' Module:       M11_AppLayer
' Description:  Application Layer for Beam Design. Orchestrates data flow between
'               Excel Tables and the Core Structural Library.
' Dependencies: M06_Flexure, M07_Shear, M02_Types
' ==========================================================================================

Public Sub Run_BeamDesign()
    Dim wsInput As Worksheet
    Dim wsDesign As Worksheet
    Dim tblInput As ListObject
    Dim tblDesign As ListObject
    Dim i As Long
    Dim rowInput As ListRow
    Dim newRow As ListRow

    ' --- 1. Initialize ---
    On Error GoTo ErrorHandler
    Set wsInput = ThisWorkbook.Sheets("BEAM_INPUT")
    Set wsDesign = ThisWorkbook.Sheets("BEAM_DESIGN")
    Set tblInput = wsInput.ListObjects("tbl_BeamInput")
    Set tblDesign = wsDesign.ListObjects("tbl_BeamDesign")

    Application.ScreenUpdating = False
    Application.Calculation = xlCalculationManual

    ' --- 2. Clear Previous Results ---
    If Not tblDesign.DataBodyRange Is Nothing Then
        tblDesign.DataBodyRange.Delete
    End If

    ' --- 3. Process Each Beam ---
    For i = 1 To tblInput.ListRows.Count
        Set rowInput = tblInput.ListRows(i)
        Set newRow = tblDesign.ListRows.Add

        ' Process Single Row
        Call Process_Beam_Row(rowInput, newRow)
    Next i

    MsgBox "Design Completed Successfully!", vbInformation, "Structural Engineering Lib"

ExitHandler:
    Application.ScreenUpdating = True
    Application.Calculation = xlCalculationAutomatic
    Exit Sub

ErrorHandler:
    MsgBox "Error " & Err.Number & ": " & Err.Description, vbCritical, "Run_BeamDesign"
    Resume ExitHandler
End Sub

Private Sub Process_Beam_Row(rowIn As ListRow, rowOut As ListRow)
    ' Inputs
    Dim ID As String, Story As String, SpanLoc As String
    Dim b As Double, D As Double, Cover As Double
    Dim fck As Double, fy As Double
    Dim Mu As Double, Vu As Double
    Dim isFlanged As Boolean, Df As Double, bf As Double

    ' Outputs
    Dim d_eff As Double
    Dim flexRes As FlexureResult
    Dim shearRes As ShearResult
    Dim status As String
    Dim remarks As String
    Dim calcNotes As String

    On Error GoTo RowError

    ' --- Read Inputs ---
    With rowIn.Range
        ID = .Cells(1, 1).Value
        Story = .Cells(1, 2).Value
        SpanLoc = .Cells(1, 3).Value
        b = .Cells(1, 4).Value
        D = .Cells(1, 5).Value
        Cover = .Cells(1, 6).Value
        fck = .Cells(1, 7).Value
        fy = .Cells(1, 8).Value
        Mu = .Cells(1, 9).Value
        Vu = .Cells(1, 10).Value
        isFlanged = (UCase(.Cells(1, 11).Value) = "YES")
        Df = .Cells(1, 12).Value
        bf = .Cells(1, 13).Value
    End With

    ' --- Calculations ---
    ' Treat Cover as clear cover; add stirrup/main bar allowances to reach effective covers.
    Dim stirrupDia As Double
    Dim barDiaTension As Double
    Dim barDiaCompression As Double
    stirrupDia = GetOptionalValue(rowIn.Range, 14, 8#)         ' mm, defaults to 8mm stirrup
    barDiaTension = GetOptionalValue(rowIn.Range, 15, 16#)     ' mm, defaults to 16mm main bar
    barDiaCompression = GetOptionalValue(rowIn.Range, 16, barDiaTension) ' mm, default mirror tension bar

    Dim tensionCoverEff As Double
    Dim compressionCoverEff As Double
    tensionCoverEff = Cover + stirrupDia + (barDiaTension / 2#)
    compressionCoverEff = Cover + stirrupDia + (barDiaCompression / 2#)

    d_eff = D - tensionCoverEff

    ' 1. Flexure Design
    ' Note: Library expects Mu in kN-m (based on M06_Flexure signatures)
    ' Design_Doubly_Reinforced(b, d, d_dash, D_total, Mu_kNm, fck, fy)
    ' Design_Flanged_Beam(bw, bf, d, Df, D_total, Mu_kNm, fck, fy, d_dash)

    Dim d_dash As Double
    d_dash = compressionCoverEff

    ' Guards for bad geometry inputs
    calcNotes = ""
    If d_eff <= 0 Then
        d_eff = D - Cover   ' fallback to legacy effective cover assumption
        calcNotes = calcNotes & "Adjusted d using input cover only; clear cover + bars exceeded depth. "
    End If
    If d_dash >= D Then
        d_dash = Cover
        calcNotes = calcNotes & "Compression cover capped at input cover. "
    End If

    If isFlanged Then
        flexRes = M06_Flexure.Design_Flanged_Beam(b, bf, d_eff, Df, D, Mu, fck, fy, d_dash)
    Else
        flexRes = M06_Flexure.Design_Doubly_Reinforced(b, d_eff, d_dash, D, Mu, fck, fy)
    End If

    ' 2. Shear Design
    ' Design_Shear(Vu_kN, b, d, fck, fy, Asv, pt)
    ' Assuming 2-legged 8mm stirrups (Area = 100.53 mm2)
    Dim Asv_Default As Double
    Asv_Default = 100.53

    shearRes = M07_Shear.Design_Shear(Vu, b, d_eff, fck, fy, Asv_Default, flexRes.Pt_Provided)

    ' --- Write Inputs to Output Table (Mirroring) ---
    With rowOut.Range
        .Cells(1, 1).Value = ID
        .Cells(1, 2).Value = Story
        .Cells(1, 3).Value = SpanLoc
        .Cells(1, 4).Value = b
        .Cells(1, 5).Value = D
        .Cells(1, 6).Value = Cover
        .Cells(1, 7).Value = fck
        .Cells(1, 8).Value = fy
        .Cells(1, 9).Value = Mu
        .Cells(1, 10).Value = Vu
        .Cells(1, 11).Value = IIf(isFlanged, "Yes", "No")
        .Cells(1, 12).Value = Df
        .Cells(1, 13).Value = bf

        ' --- Write Results ---
        .Cells(1, 14).Value = d_eff
        .Cells(1, 15).Value = flexRes.Mu_Lim

        ' Status Logic
        If flexRes.IsSafe = False Or shearRes.IsSafe = False Then
            status = "FAIL"
        Else
            status = "OK"
        End If
        .Cells(1, 16).Value = status

        .Cells(1, 17).Value = flexRes.Ast_Required
        .Cells(1, 18).Value = flexRes.Pt_Provided
        .Cells(1, 19).Value = flexRes.Asc_Required

        .Cells(1, 20).Value = shearRes.Tv
        .Cells(1, 21).Value = shearRes.Tc

        ' Shear Status
        If shearRes.IsSafe Then
            If shearRes.Tv <= shearRes.Tc Then
                .Cells(1, 22).Value = "Safe"
            Else
                .Cells(1, 22).Value = "Shear Reinf"
            End If
        Else
            .Cells(1, 22).Value = "Unsafe"
        End If

        ' Stirrups
        If shearRes.IsSafe Then
            If shearRes.Tv <= shearRes.Tc Then
                .Cells(1, 23).Value = "Nominal (2L-8mm)"
            Else
                ' Format spacing
                .Cells(1, 23).Value = "2L-8mm @ " & Format(shearRes.Spacing, "0") & " mm"
            End If
        Else
            .Cells(1, 23).Value = "Redesign"
        End If

        ' Remarks
        remarks = calcNotes
        If flexRes.SectionType = OverReinforced Then remarks = remarks & "Doubly Reinforced. "
        If Not flexRes.IsSafe Then remarks = remarks & "Flexure: " & flexRes.ErrorMessage & " "
        If Not shearRes.IsSafe Then remarks = remarks & "Shear: " & shearRes.Remarks & " "
        .Cells(1, 24).Value = remarks
    End With

    Exit Sub

RowError:
    rowOut.Range.Cells(1, 16).Value = "ERROR"
    rowOut.Range.Cells(1, 24).Value = "Error: " & Err.Description
    Resume Next
End Sub

Public Sub Clear_Results()
    Dim wsDesign As Worksheet
    Dim tblDesign As ListObject

    On Error Resume Next
    Set wsDesign = ThisWorkbook.Sheets("BEAM_DESIGN")
    Set tblDesign = wsDesign.ListObjects("tbl_BeamDesign")

    If Not tblDesign.DataBodyRange Is Nothing Then
        tblDesign.DataBodyRange.Delete
    End If
    MsgBox "Results Cleared.", vbInformation
End Sub

Private Function GetOptionalValue(rowRange As Range, colIndex As Long, defaultValue As Double) As Double
    ' Safely read an optional column from the table; returns defaultValue if missing/blank.
    If colIndex <= rowRange.Columns.Count Then
        If Len(Trim(CStr(rowRange.Cells(1, colIndex).Value))) > 0 Then
            GetOptionalValue = rowRange.Cells(1, colIndex).Value
            Exit Function
        End If
    End If
    GetOptionalValue = defaultValue
End Function
