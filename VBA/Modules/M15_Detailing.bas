Attribute VB_Name = "M15_Detailing"
Option Explicit

' ==============================================================================
' Module:       M15_Detailing
' Description:  IS 456:2000 / SP 34:1987 Reinforcement Detailing
' Version:      0.7.0
' License:      MIT
' References:   IS 456:2000 Cl 26.2-26.5, IS 13920:2016, SP 34:1987
' ==============================================================================

' ------------------------------------------------------------------------------
' Bond Stress Table (IS 456 Table 5.3) - Deformed Bars (60% increase applied)
' Key: fck grade, Value: τbd (N/mm²)
' ------------------------------------------------------------------------------
Private Const TAU_BD_M15 As Double = 1.6
Private Const TAU_BD_M20 As Double = 1.92
Private Const TAU_BD_M25 As Double = 2.24
Private Const TAU_BD_M30 As Double = 2.4
Private Const TAU_BD_M35 As Double = 2.72
Private Const TAU_BD_M40 As Double = 3.04
Private Const TAU_BD_M45 As Double = 3.2
Private Const TAU_BD_M50 As Double = 3.36

' Standard bar diameters (mm)
Private Const STANDARD_BARS As String = "8,10,12,16,20,25,32"

' Standard stirrup diameters (mm)
Private Const STANDARD_STIRRUPS As String = "6,8,10,12"


' ==============================================================================
' Bond Stress Lookup
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Get_Bond_Stress
' Description:  Returns design bond stress τbd for given concrete grade
' Args:         fck - Characteristic compressive strength (N/mm²)
'               bar_type - "deformed" (default) or "plain"
' Returns:      τbd in N/mm²
' Reference:    IS 456 Table 5.3
' ------------------------------------------------------------------------------
Public Function Get_Bond_Stress(ByVal fck As Double, _
                                Optional ByVal bar_type As String = "deformed") As Double
    Dim tau_bd As Double
    
    ' Select based on nearest lower grade
    Select Case True
        Case fck >= 50: tau_bd = TAU_BD_M50
        Case fck >= 45: tau_bd = TAU_BD_M45
        Case fck >= 40: tau_bd = TAU_BD_M40
        Case fck >= 35: tau_bd = TAU_BD_M35
        Case fck >= 30: tau_bd = TAU_BD_M30
        Case fck >= 25: tau_bd = TAU_BD_M25
        Case fck >= 20: tau_bd = TAU_BD_M20
        Case Else: tau_bd = TAU_BD_M15
    End Select
    
    ' Plain bars have 60% less bond stress
    If LCase(bar_type) = "plain" Then
        tau_bd = tau_bd / 1.6
    End If
    
    Get_Bond_Stress = tau_bd
End Function


' ==============================================================================
' Development Length (IS 456 Cl 26.2.1)
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Calculate_Development_Length
' Description:  Calculates development length Ld per IS 456 Cl 26.2.1
' Formula:      Ld = (φ × σs) / (4 × τbd)
' Args:         bar_dia - Bar diameter φ (mm)
'               fck - Concrete strength (N/mm²)
'               fy - Steel yield strength (N/mm²)
'               bar_type - "deformed" or "plain"
'               stress_ratio - σs/fy ratio (default 0.87 for limit state)
' Returns:      Development length Ld (mm)
' ------------------------------------------------------------------------------
Public Function Calculate_Development_Length(ByVal bar_dia As Double, _
                                             ByVal fck As Double, _
                                             ByVal fy As Double, _
                                             Optional ByVal bar_type As String = "deformed", _
                                             Optional ByVal stress_ratio As Double = 0.87) As Double
    Dim sigma_s As Double
    Dim tau_bd As Double
    Dim Ld As Double
    
    sigma_s = stress_ratio * fy
    tau_bd = Get_Bond_Stress(fck, bar_type)
    
    Ld = (bar_dia * sigma_s) / (4# * tau_bd)
    
    Calculate_Development_Length = Round(Ld, 0)
End Function


' ==============================================================================
' Lap Length (IS 456 Cl 26.2.5)
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Calculate_Lap_Length
' Description:  Calculates lap splice length per IS 456 Cl 26.2.5
' Args:         bar_dia - Bar diameter (mm)
'               fck - Concrete strength (N/mm²)
'               fy - Steel yield strength (N/mm²)
'               bar_type - "deformed" or "plain"
'               splice_percent - Percentage of bars spliced at section
'               is_seismic - Apply IS 13920 requirements (1.5×Ld)
'               in_tension - True for tension zone, False for compression
' Returns:      Lap length (mm)
' ------------------------------------------------------------------------------
Public Function Calculate_Lap_Length(ByVal bar_dia As Double, _
                                     ByVal fck As Double, _
                                     ByVal fy As Double, _
                                     Optional ByVal bar_type As String = "deformed", _
                                     Optional ByVal splice_percent As Double = 50#, _
                                     Optional ByVal is_seismic As Boolean = False, _
                                     Optional ByVal in_tension As Boolean = True) As Double
    Dim Ld As Double
    Dim alpha As Double
    Dim lap As Double
    
    Ld = Calculate_Development_Length(bar_dia, fck, fy, bar_type)
    
    ' Compression lap = Ld (no enhancement)
    If Not in_tension Then
        Calculate_Lap_Length = Round(Ld, 0)
        Exit Function
    End If
    
    ' Tension lap with enhancement factor
    If is_seismic Then
        alpha = 1.5  ' IS 13920 requirement
    ElseIf splice_percent > 50 Then
        alpha = 1.3  ' More than 50% bars spliced
    Else
        alpha = 1#   ' 50% or less bars spliced
    End If
    
    lap = alpha * Ld
    
    Calculate_Lap_Length = Round(lap, 0)
End Function


' ==============================================================================
' Bar Spacing (IS 456 Cl 26.3)
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Calculate_Bar_Spacing
' Description:  Calculates center-to-center spacing of main bars
' Args:         b - Beam width (mm)
'               cover - Clear cover (mm)
'               stirrup_dia - Stirrup diameter (mm)
'               bar_dia - Main bar diameter (mm)
'               bar_count - Number of bars in one layer
' Returns:      Center-to-center spacing (mm)
' ------------------------------------------------------------------------------
Public Function Calculate_Bar_Spacing(ByVal b As Double, _
                                      ByVal cover As Double, _
                                      ByVal stirrup_dia As Double, _
                                      ByVal bar_dia As Double, _
                                      ByVal bar_count As Long) As Double
    Dim available As Double
    Dim spacing As Double
    
    If bar_count <= 1 Then
        Calculate_Bar_Spacing = 0#
        Exit Function
    End If
    
    ' Available width = b - 2*(cover + stirrup_dia) - bar_dia
    ' For n bars, we have (n-1) spaces
    available = CDbl(b) - 2# * (CDbl(cover) + CDbl(stirrup_dia)) - CDbl(bar_dia)
    spacing = available / CDbl(bar_count - 1)
    
    Calculate_Bar_Spacing = Round(spacing, 0)
End Function


' ------------------------------------------------------------------------------
' Function:     Get_Min_Spacing
' Description:  Returns minimum required spacing per IS 456 Cl 26.3.2
' Args:         bar_dia - Bar diameter (mm)
'               agg_size - Maximum aggregate size (mm), default 20
' Returns:      Minimum spacing (mm) = max(bar_dia, agg_size+5, 25)
' ------------------------------------------------------------------------------
Public Function Get_Min_Spacing(ByVal bar_dia As Double, _
                                Optional ByVal agg_size As Double = 20#) As Double
    Dim min_sp As Double
    
    min_sp = bar_dia
    If agg_size + 5# > min_sp Then min_sp = agg_size + 5#
    If 25# > min_sp Then min_sp = 25#
    
    Get_Min_Spacing = min_sp
End Function


' ------------------------------------------------------------------------------
' Function:     Check_Min_Spacing
' Description:  Validates bar spacing against IS 456 Cl 26.3.2
' Args:         spacing - Actual center-to-center spacing (mm)
'               bar_dia - Bar diameter (mm)
'               agg_size - Maximum aggregate size (mm)
' Returns:      True if spacing is adequate
' ------------------------------------------------------------------------------
Public Function Check_Min_Spacing(ByVal spacing As Double, _
                                  ByVal bar_dia As Double, _
                                  Optional ByVal agg_size As Double = 20#) As Boolean
    Check_Min_Spacing = (spacing >= Get_Min_Spacing(bar_dia, agg_size))
End Function


' ==============================================================================
' Stirrup Legs
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Get_Stirrup_Legs
' Description:  Determines number of stirrup legs based on beam width
' Reference:    IS 456 Cl 26.5.1.5
' Args:         b - Beam width (mm)
' Returns:      Number of legs (2, 4, or 6)
' ------------------------------------------------------------------------------
Public Function Get_Stirrup_Legs(ByVal b As Double) As Long
    If b <= 300 Then
        Get_Stirrup_Legs = 2
    ElseIf b <= 450 Then
        Get_Stirrup_Legs = 2  ' Can use 2 or 4
    ElseIf b <= 600 Then
        Get_Stirrup_Legs = 4
    Else
        Get_Stirrup_Legs = 6
    End If
End Function


' ==============================================================================
' Bar Selection
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Select_Bar_Diameter
' Description:  Auto-selects appropriate bar diameter based on required area
' Args:         ast_required - Required steel area (mm²)
' Returns:      Recommended bar diameter (mm)
' ------------------------------------------------------------------------------
Public Function Select_Bar_Diameter(ByVal ast_required As Double) As Double
    If ast_required < 400 Then
        Select_Bar_Diameter = 12
    ElseIf ast_required < 1000 Then
        Select_Bar_Diameter = 16
    ElseIf ast_required < 2000 Then
        Select_Bar_Diameter = 20
    Else
        Select_Bar_Diameter = 25
    End If
End Function


' ------------------------------------------------------------------------------
' Function:     Calculate_Bar_Count
' Description:  Calculates number of bars needed for required area
' Args:         ast_required - Required steel area (mm²)
'               bar_dia - Bar diameter (mm)
' Returns:      Number of bars (minimum 2)
' ------------------------------------------------------------------------------
Public Function Calculate_Bar_Count(ByVal ast_required As Double, _
                                    ByVal bar_dia As Double) As Long
    Dim bar_area As Double
    Dim count As Long
    
    bar_area = PI * (bar_dia / 2#) ^ 2
    count = Application.WorksheetFunction.Ceiling(ast_required / bar_area, 1)
    
    If count < 2 Then count = 2  ' Minimum 2 bars
    
    Calculate_Bar_Count = count
End Function


' ------------------------------------------------------------------------------
' Function:     Calculate_Bar_Area
' Description:  Calculates area of a single bar
' Args:         bar_dia - Bar diameter (mm)
' Returns:      Bar area (mm²)
' ------------------------------------------------------------------------------
Public Function Calculate_Bar_Area(ByVal bar_dia As Double) As Double
    Calculate_Bar_Area = PI * (bar_dia / 2#) ^ 2
End Function


' ------------------------------------------------------------------------------
' Sub:          Select_Bar_Arrangement
' Description:  Selects practical bar arrangement for required steel area
' Args:         ast_required - Required steel area (mm²)
'               b - Beam width (mm)
'               cover - Clear cover (mm)
'               stirrup_dia - Stirrup diameter (mm)
'               result - BarArrangement UDT to populate (ByRef)
' ------------------------------------------------------------------------------
Public Sub Select_Bar_Arrangement(ByVal ast_required As Double, _
                                  ByVal b As Double, _
                                  ByVal cover As Double, _
                                  ByVal stirrup_dia As Double, _
                                  ByRef result As BarArrangement)
    Dim bar_dia As Double
    Dim bar_count As Long
    Dim bar_area As Double
    Dim spacing As Double
    Dim is_valid As Boolean
    
    ' Handle zero or negative area
    If ast_required <= 0 Then
        result.count = 2
        result.diameter = 12
        result.area_provided = 226  ' 2 × π × 6²
        result.spacing = 0
        result.layers = 1
        Exit Sub
    End If
    
    ' Auto-select diameter
    bar_dia = Select_Bar_Diameter(ast_required)
    bar_area = Calculate_Bar_Area(bar_dia)
    bar_count = Calculate_Bar_Count(ast_required, bar_dia)
    
    ' Calculate spacing
    spacing = Calculate_Bar_Spacing(b, cover, stirrup_dia, bar_dia, bar_count)
    is_valid = Check_Min_Spacing(spacing, bar_dia)
    
    ' If single layer doesn't fit, try 2 layers
    result.layers = 1
    If Not is_valid Then
        result.layers = 2
        Dim bars_per_layer As Long
        bars_per_layer = Application.WorksheetFunction.Ceiling(CDbl(bar_count) / 2#, 1)
        spacing = Calculate_Bar_Spacing(b, cover, stirrup_dia, bar_dia, bars_per_layer)
    End If
    
    ' Populate result
    result.count = bar_count
    result.diameter = bar_dia
    result.area_provided = Round(CDbl(bar_count) * bar_area, 0)
    result.spacing = Round(spacing, 0)
End Sub


' ==============================================================================
' Callout Formatting
' ==============================================================================

' ------------------------------------------------------------------------------
' Function:     Format_Bar_Callout
' Description:  Formats bar callout in standard notation (e.g., "3-16φ")
' Args:         count - Number of bars
'               diameter - Bar diameter (mm)
' Returns:      Formatted string
' ------------------------------------------------------------------------------
Public Function Format_Bar_Callout(ByVal count As Long, _
                                   ByVal diameter As Double) As String
    Format_Bar_Callout = CStr(count) & "-" & CStr(CLng(diameter)) & ChrW(966)  ' φ = ChrW(966)
End Function


' ------------------------------------------------------------------------------
' Function:     Format_Stirrup_Callout
' Description:  Formats stirrup callout (e.g., "2L-8φ@150 c/c")
' Args:         legs - Number of legs
'               diameter - Stirrup diameter (mm)
'               spacing - Spacing (mm)
' Returns:      Formatted string
' ------------------------------------------------------------------------------
Public Function Format_Stirrup_Callout(ByVal legs As Long, _
                                       ByVal diameter As Double, _
                                       ByVal spacing As Double) As String
    Format_Stirrup_Callout = CStr(legs) & "L-" & CStr(CLng(diameter)) & ChrW(966) & _
                             "@" & CStr(CLng(spacing)) & " c/c"
End Function


' ==============================================================================
' Complete Detailing Function
' ==============================================================================

' ------------------------------------------------------------------------------
' Sub:          Create_Beam_Detailing
' Description:  Creates complete beam detailing from design output
' Args:         beam_id, story - Identifiers
'               b, D, span, cover - Geometry (mm)
'               fck, fy - Material grades (N/mm²)
'               ast_start, ast_mid, ast_end - Required tension steel (mm²)
'               asc_start, asc_mid, asc_end - Required compression steel (mm²)
'               stirrup_dia - Stirrup diameter (mm)
'               sv_start, sv_mid, sv_end - Stirrup spacing (mm)
'               is_seismic - Apply IS 13920 requirements
'               result - BeamDetailingResult UDT (ByRef)
' ------------------------------------------------------------------------------
Public Sub Create_Beam_Detailing(ByVal beam_id As String, _
                                 ByVal story As String, _
                                 ByVal b As Double, _
                                 ByVal D As Double, _
                                 ByVal span As Double, _
                                 ByVal cover As Double, _
                                 ByVal fck As Double, _
                                 ByVal fy As Double, _
                                 ByVal ast_start As Double, _
                                 ByVal ast_mid As Double, _
                                 ByVal ast_end As Double, _
                                 Optional ByVal asc_start As Double = 0, _
                                 Optional ByVal asc_mid As Double = 0, _
                                 Optional ByVal asc_end As Double = 0, _
                                 Optional ByVal stirrup_dia As Double = 8, _
                                 Optional ByVal sv_start As Double = 150, _
                                 Optional ByVal sv_mid As Double = 200, _
                                 Optional ByVal sv_end As Double = 150, _
                                 Optional ByVal is_seismic As Boolean = False, _
                                 ByRef result As BeamDetailingResult)
    
    Dim max_dia As Double
    Dim legs As Long
    
    ' Populate geometry
    result.beam_id = beam_id
    result.story = story
    result.b = b
    result.D = D
    result.span = span
    result.cover = cover
    
    ' Select bar arrangements for bottom (tension at mid) and top (tension at supports)
    ' Bottom bars
    Call Select_Bar_Arrangement(ast_start, b, cover, stirrup_dia, result.bottom_start)
    Call Select_Bar_Arrangement(ast_mid, b, cover, stirrup_dia, result.bottom_mid)
    Call Select_Bar_Arrangement(ast_end, b, cover, stirrup_dia, result.bottom_end)
    
    ' Top bars (use compression steel or 25% of tension as hanger bars)
    Dim top_ast_start As Double, top_ast_mid As Double, top_ast_end As Double
    top_ast_start = IIf(asc_start > 0, asc_start, ast_start * 0.25)
    top_ast_mid = IIf(asc_mid > 0, asc_mid, ast_mid * 0.25)
    top_ast_end = IIf(asc_end > 0, asc_end, ast_end * 0.25)
    
    Call Select_Bar_Arrangement(top_ast_start, b, cover, stirrup_dia, result.top_start)
    Call Select_Bar_Arrangement(top_ast_mid, b, cover, stirrup_dia, result.top_mid)
    Call Select_Bar_Arrangement(top_ast_end, b, cover, stirrup_dia, result.top_end)
    
    ' Stirrups
    legs = Get_Stirrup_Legs(b)
    
    result.stirrup_start.diameter = stirrup_dia
    result.stirrup_start.legs = legs
    result.stirrup_start.spacing = sv_start
    result.stirrup_start.zone_length = span * 0.2  ' 20% at start
    
    result.stirrup_mid.diameter = stirrup_dia
    result.stirrup_mid.legs = legs
    result.stirrup_mid.spacing = sv_mid
    result.stirrup_mid.zone_length = span * 0.6  ' 60% at mid
    
    result.stirrup_end.diameter = stirrup_dia
    result.stirrup_end.legs = legs
    result.stirrup_end.spacing = sv_end
    result.stirrup_end.zone_length = span * 0.2  ' 20% at end
    
    ' Calculate development and lap lengths using maximum bar diameter
    max_dia = result.bottom_mid.diameter
    If result.top_start.diameter > max_dia Then max_dia = result.top_start.diameter
    
    result.ld_tension = Calculate_Development_Length(max_dia, fck, fy, "deformed", 0.87)
    result.ld_compression = Calculate_Development_Length(max_dia, fck, fy, "deformed", 0.67)
    result.lap_length = Calculate_Lap_Length(max_dia, fck, fy, "deformed", 50, is_seismic, True)
    
    ' Validate
    result.is_valid = True
    result.remarks = "OK"
    
    ' Check spacing validity
    If Not Check_Min_Spacing(result.bottom_mid.spacing, result.bottom_mid.diameter) Then
        result.remarks = "Warning: Bar spacing tight"
    End If
End Sub
