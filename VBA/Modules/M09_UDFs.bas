Attribute VB_Name = "M09_UDFs"
Option Explicit

' ==============================================================================
' Module:       M09_UDFs
' Description:  Excel User Defined Functions (Worksheet accessible)
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Wrapper for Mu_lim (Returns kN-m)
Public Function IS456_MuLim(ByVal b As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    IS456_MuLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    Exit Function
ErrHandler:
    IS456_MuLim = CVErr(xlErrValue)
End Function

' Wrapper for Ast Required (Returns mm^2 or String message)
Public Function IS456_AstRequired(ByVal b As Double, ByVal d As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As Double
    res = M06_Flexure.Calculate_Ast_Required(b, d, Mu_kNm, fck, fy)
    
    If res = -1 Then
        IS456_AstRequired = "Over-Reinforced"
    Else
        IS456_AstRequired = res
    End If
    Exit Function
ErrHandler:
    IS456_AstRequired = CVErr(xlErrValue)
End Function

' Wrapper for Shear Spacing (Returns mm or String message)
Public Function IS456_ShearSpacing(ByVal Vu_kN As Double, ByVal b As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double, ByVal Asv As Double, ByVal pt As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As ShearResult
    res = M07_Shear.Design_Shear(Vu_kN, b, d, fck, fy, Asv, pt)
    
    If Not res.IsSafe Then
        IS456_ShearSpacing = "Unsafe: " & res.Remarks
    Else
        IS456_ShearSpacing = res.Spacing
    End If
    Exit Function
ErrHandler:
    IS456_ShearSpacing = CVErr(xlErrValue)
End Function

' Wrapper for Flanged Mu_lim (Returns kN-m)
Public Function IS456_MuLim_Flanged(ByVal bw As Double, ByVal bf As Double, ByVal d As Double, ByVal Df As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    IS456_MuLim_Flanged = M06_Flexure.Calculate_Mu_Lim_Flanged(bw, bf, d, Df, fck, fy)
    Exit Function
ErrHandler:
    IS456_MuLim_Flanged = CVErr(xlErrValue)
End Function

' Wrapper for Rectangular Beam Design (Singly or Doubly)
' Returns 1x4 Array: [Ast_Req, Asc_Req, Xu, Status_String]
Public Function IS456_Design_Rectangular(ByVal b As Double, ByVal d As Double, ByVal d_dash As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    res = M06_Flexure.Design_Doubly_Reinforced(b, d, d_dash, D_total, Mu_kNm, fck, fy)
    
    Dim output(1 To 4) As Variant
    If res.IsSafe Then
        output(1) = res.Ast_Required
        output(2) = res.Asc_Required
        output(3) = res.Xu
        output(4) = "Safe"
    Else
        output(1) = 0
        output(2) = 0
        output(3) = res.Xu
        output(4) = res.ErrorMessage
    End If
    
    IS456_Design_Rectangular = output
    Exit Function
ErrHandler:
    IS456_Design_Rectangular = CVErr(xlErrValue)
End Function

' Wrapper for Flanged Beam Design
' Returns 1x4 Array: [Ast_Req, Asc_Req, Xu, Status_String]
Public Function IS456_Design_Flanged(ByVal bw As Double, ByVal bf As Double, ByVal d As Double, ByVal Df As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double, Optional ByVal d_dash As Double = 50) As Variant
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    res = M06_Flexure.Design_Flanged_Beam(bw, bf, d, Df, D_total, Mu_kNm, fck, fy, d_dash)
    
    Dim output(1 To 4) As Variant
    If res.IsSafe Then
        output(1) = res.Ast_Required
        output(2) = res.Asc_Required
        output(3) = res.Xu
        output(4) = "Safe"
    Else
        output(1) = 0
        output(2) = 0
        output(3) = res.Xu
        output(4) = res.ErrorMessage
    End If
    
    IS456_Design_Flanged = output
    Exit Function
ErrHandler:
    IS456_Design_Flanged = CVErr(xlErrValue)
End Function

' Wrapper for Tc (Table 19)
Public Function IS456_Tc(ByVal fck As Double, ByVal pt As Double) As Variant
    On Error GoTo ErrHandler
    IS456_Tc = M03_Tables.Get_Tc_Value(fck, pt)
    Exit Function
ErrHandler:
    IS456_Tc = CVErr(xlErrValue)
End Function

' Wrapper for Tc_max (Table 20)
Public Function IS456_TcMax(ByVal fck As Double) As Variant
    On Error GoTo ErrHandler
    IS456_TcMax = M03_Tables.Get_TcMax_Value(fck)
    Exit Function
ErrHandler:
    IS456_TcMax = CVErr(xlErrValue)
End Function

' Wrapper for Ductile Detailing Check (IS 13920)
' Returns String: "Compliant" or error message
Public Function IS456_Check_Ductility(ByVal b As Double, ByVal D_overall As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double, ByVal min_long_bar_dia As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As DuctileBeamResult
    res = M10_Ductile.Check_Beam_Ductility(b, D_overall, d, fck, fy, min_long_bar_dia)
    
    IS456_Check_Ductility = res.Remarks
    Exit Function
ErrHandler:
    IS456_Check_Ductility = CVErr(xlErrValue)
End Function


' ==============================================================================
' Detailing UDFs (v0.7+)
' ==============================================================================

' Wrapper for Development Length (Ld)
' Returns mm
Public Function IS456_Ld(ByVal bar_dia As Double, ByVal fck As Double, ByVal fy As Double, Optional ByVal bar_type As String = "deformed") As Variant
    On Error GoTo ErrHandler
    IS456_Ld = M15_Detailing.Calculate_Development_Length(bar_dia, fck, fy, bar_type)
    Exit Function
ErrHandler:
    IS456_Ld = CVErr(xlErrValue)
End Function

' Wrapper for Lap Length
' Returns mm
Public Function IS456_LapLength(ByVal bar_dia As Double, ByVal fck As Double, ByVal fy As Double, Optional ByVal is_seismic As Boolean = False, Optional ByVal in_tension As Boolean = True) As Variant
    On Error GoTo ErrHandler
    IS456_LapLength = M15_Detailing.Calculate_Lap_Length(bar_dia, fck, fy, "deformed", 50, is_seismic, in_tension)
    Exit Function
ErrHandler:
    IS456_LapLength = CVErr(xlErrValue)
End Function

' Wrapper for Bond Stress (τbd)
' Returns N/mm²
Public Function IS456_BondStress(ByVal fck As Double, Optional ByVal bar_type As String = "deformed") As Variant
    On Error GoTo ErrHandler
    IS456_BondStress = M15_Detailing.Get_Bond_Stress(fck, bar_type)
    Exit Function
ErrHandler:
    IS456_BondStress = CVErr(xlErrValue)
End Function

' Wrapper for Bar Spacing
' Returns mm
Public Function IS456_BarSpacing(ByVal b As Double, ByVal cover As Double, ByVal stirrup_dia As Double, ByVal bar_dia As Double, ByVal bar_count As Long) As Variant
    On Error GoTo ErrHandler
    IS456_BarSpacing = M15_Detailing.Calculate_Bar_Spacing(b, cover, stirrup_dia, bar_dia, bar_count)
    Exit Function
ErrHandler:
    IS456_BarSpacing = CVErr(xlErrValue)
End Function

' Wrapper for Minimum Spacing Check
' Returns TRUE if spacing is adequate
Public Function IS456_CheckSpacing(ByVal spacing As Double, ByVal bar_dia As Double, Optional ByVal agg_size As Double = 20) As Variant
    On Error GoTo ErrHandler
    IS456_CheckSpacing = M15_Detailing.Check_Min_Spacing(spacing, bar_dia, agg_size)
    Exit Function
ErrHandler:
    IS456_CheckSpacing = CVErr(xlErrValue)
End Function

' Wrapper for Bar Count calculation
' Returns number of bars needed
Public Function IS456_BarCount(ByVal ast_required As Double, ByVal bar_dia As Double) As Variant
    On Error GoTo ErrHandler
    IS456_BarCount = M15_Detailing.Calculate_Bar_Count(ast_required, bar_dia)
    Exit Function
ErrHandler:
    IS456_BarCount = CVErr(xlErrValue)
End Function

' Wrapper for Bar Callout formatting
' Returns string like "3-16φ"
Public Function IS456_BarCallout(ByVal count As Long, ByVal diameter As Double) As Variant
    On Error GoTo ErrHandler
    IS456_BarCallout = M15_Detailing.Format_Bar_Callout(count, diameter)
    Exit Function
ErrHandler:
    IS456_BarCallout = CVErr(xlErrValue)
End Function

' Wrapper for Stirrup Callout formatting
' Returns string like "2L-8φ@150 c/c"
Public Function IS456_StirrupCallout(ByVal legs As Long, ByVal diameter As Double, ByVal spacing As Double) As Variant
    On Error GoTo ErrHandler
    IS456_StirrupCallout = M15_Detailing.Format_Stirrup_Callout(legs, diameter, spacing)
    Exit Function
ErrHandler:
    IS456_StirrupCallout = CVErr(xlErrValue)
End Function


' ==============================================================================
' DXF Export UDFs (v0.7+)
' ==============================================================================

' Generate beam cross-section DXF drawing
' @Param filePath: Full path to save DXF file
' @Param B: Beam width (mm)
' @Param D: Beam depth (mm)
' @Param cover: Clear cover (mm)
' @Param topBars: Range with top bar diameters (e.g., A1:A3 with values 16,16,16)
' @Param bottomBars: Range with bottom bar diameters
' @Param stirrupDia: Stirrup diameter (mm)
' @Returns: TRUE if successful, error message otherwise
Public Function IS456_DrawSection(ByVal filePath As String, _
                                 ByVal B As Double, ByVal D As Double, _
                                 ByVal cover As Double, _
                                 ByVal topBarsRange As Range, _
                                 ByVal bottomBarsRange As Range, _
                                 ByVal stirrupDia As Double) As Variant
    On Error GoTo ErrHandler
    
    Dim topBars() As Double
    Dim bottomBars() As Double
    Dim i As Long, n As Long
    
    ' Convert top bars range to array
    n = topBarsRange.Cells.Count
    ReDim topBars(0 To n - 1)
    For i = 1 To n
        topBars(i - 1) = topBarsRange.Cells(i).Value
    Next i
    
    ' Convert bottom bars range to array
    n = bottomBarsRange.Cells.Count
    ReDim bottomBars(0 To n - 1)
    For i = 1 To n
        bottomBars(i - 1) = bottomBarsRange.Cells(i).Value
    Next i
    
    ' Generate DXF
    Dim success As Boolean
    success = M16_DXF.Draw_BeamSection(filePath, B, D, cover, topBars, bottomBars, stirrupDia)
    
    If success Then
        IS456_DrawSection = True
    Else
        IS456_DrawSection = "Error: Failed to generate DXF"
    End If
    Exit Function
    
ErrHandler:
    IS456_DrawSection = "Error: " & Err.Description
End Function

' Generate beam longitudinal section DXF drawing
' @Param filePath: Full path to save DXF file
' @Param length: Beam length (mm)
' @Param D: Beam depth (mm)
' @Param cover: Clear cover (mm)
' @Param topBarDia: Top bar diameter (mm)
' @Param bottomBarDia: Bottom bar diameter (mm)
' @Param stirrupDia: Stirrup diameter (mm)
' @Param stirrupSpacing: Stirrup spacing (mm)
' @Returns: TRUE if successful, error message otherwise
Public Function IS456_DrawLongitudinal(ByVal filePath As String, _
                                      ByVal length As Double, _
                                      ByVal D As Double, _
                                      ByVal cover As Double, _
                                      ByVal topBarDia As Double, _
                                      ByVal bottomBarDia As Double, _
                                      ByVal stirrupDia As Double, _
                                      ByVal stirrupSpacing As Double) As Variant
    On Error GoTo ErrHandler
    
    Dim success As Boolean
    success = M16_DXF.Draw_BeamLongitudinal(filePath, length, D, cover, _
                                           topBarDia, bottomBarDia, _
                                           stirrupDia, stirrupSpacing)
    
    If success Then
        IS456_DrawLongitudinal = True
    Else
        IS456_DrawLongitudinal = "Error: Failed to generate DXF"
    End If
    Exit Function
    
ErrHandler:
    IS456_DrawLongitudinal = "Error: " & Err.Description
End Function

' Generate complete beam detailing DXF from design result
' This is a macro (Sub) that reads from worksheet and generates DXF
' Call from a button or module, not as worksheet function
Public Sub IS456_ExportBeamDXF()
    On Error GoTo ErrHandler
    
    Dim ws As Worksheet
    Dim filePath As String
    Dim result As BeamDetailingResult
    
    ' Get active worksheet
    Set ws = ActiveSheet
    
    ' Prompt for save location
    filePath = Application.GetSaveAsFilename( _
        InitialFileName:="BeamDetailing.dxf", _
        FileFilter:="DXF Files (*.dxf), *.dxf", _
        Title:="Save Beam Drawing As")
    
    If filePath = "False" Then Exit Sub
    
    ' Read beam data from worksheet (expected cells)
    ' Assumes standard layout: B2=Width, B3=Depth, B4=Cover, B5=TopDia, B6=TopCount, etc.
    With result
        .B_mm = ws.Range("B2").Value
        .D_mm = ws.Range("B3").Value
        .Cover_mm = ws.Range("B4").Value
        .TopBars.Dia_mm = ws.Range("B5").Value
        .TopBars.Count_n = ws.Range("B6").Value
        .BottomBars.Dia_mm = ws.Range("B7").Value
        .BottomBars.Count_n = ws.Range("B8").Value
        .Stirrups.Dia_mm = ws.Range("B9").Value
        .Stirrups.Spacing_mm = ws.Range("B10").Value
        .Stirrups.Legs = ws.Range("B11").Value
    End With
    
    ' Generate DXF
    Dim success As Boolean
    success = M16_DXF.Draw_BeamDetailing(filePath, result)
    
    If success Then
        MsgBox "DXF exported successfully to:" & vbCrLf & filePath, vbInformation, "Export Complete"
    Else
        MsgBox "Failed to export DXF file.", vbExclamation, "Export Error"
    End If
    Exit Sub
    
ErrHandler:
    MsgBox "Error: " & Err.Description, vbCritical, "Export Error"
End Sub