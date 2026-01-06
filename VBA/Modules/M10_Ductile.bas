Attribute VB_Name = "M10_Ductile"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       M10_Ductile
' Description:  IS 13920:2016 Ductile Detailing checks for Beams
' Version:      1.0.0
' ==============================================================================

Public Type DuctileBeamResult
    IsGeometryValid As Boolean
    MinPt As Double
    MaxPt As Double
    ConfinementSpacing As Double
    Remarks As String
End Type

' Clause 6.1: Geometry requirements
' Returns True if valid, False otherwise. Populates ErrorMsg.
Public Function Check_Geometry(ByVal b As Double, ByVal D As Double, ByRef ErrorMsg As String) As Boolean
    If b < 200 Then
        Check_Geometry = False
        ErrorMsg = "Width " & b & " mm < 200 mm (IS 13920 Cl 6.1.1)"
        Exit Function
    End If

    If D <= 0 Then
        Check_Geometry = False
        ErrorMsg = "Invalid depth"
        Exit Function
    End If

    Dim ratio As Double
    ratio = b / D

    If ratio < 0.3 Then
        Check_Geometry = False
        ErrorMsg = "Width/Depth ratio " & Format(ratio, "0.00") & " < 0.3 (IS 13920 Cl 6.1.2)"
        Exit Function
    End If

    Check_Geometry = True
    ErrorMsg = "OK"
End Function

' Clause 6.2.1 (b): Min tension steel percentage
Public Function Get_Min_Tension_Steel_Percentage(ByVal fck As Double, ByVal fy As Double) As Double
    ' rho_min = 0.24 * sqrt(fck) / fy
    ' Returns 0 if inputs are invalid
    If fck <= 0 Or fy <= 0 Then
        Get_Min_Tension_Steel_Percentage = 0#
        Exit Function
    End If
    Dim rho As Double
    rho = 0.24 * Sqr(fck) / fy
    Get_Min_Tension_Steel_Percentage = rho * 100#
End Function

' Clause 6.2.2: Max tension steel percentage
Public Function Get_Max_Tension_Steel_Percentage() As Double
    Get_Max_Tension_Steel_Percentage = 2.5
End Function

' Clause 6.3.5: Hoop spacing in confinement zone
Public Function Calculate_Confinement_Spacing(ByVal d As Double, ByVal min_long_bar_dia As Double) As Double
    ' Spacing shall not exceed:
    ' 1. d/4
    ' 2. 8 * db_min
    ' 3. 100 mm

    Dim s1 As Double, s2 As Double, s3 As Double
    s1 = d / 4#
    s2 = 8# * min_long_bar_dia
    s3 = 100#

    Dim s_final As Double
    s_final = s1
    If s2 < s_final Then s_final = s2
    If s3 < s_final Then s_final = s3

    Calculate_Confinement_Spacing = s_final
End Function

' Main check function
Public Function Check_Beam_Ductility(ByVal b As Double, ByVal D_overall As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double, ByVal min_long_bar_dia As Double) As DuctileBeamResult
    Dim res As DuctileBeamResult
    Dim msg As String

    res.IsGeometryValid = Check_Geometry(b, D_overall, msg)
    res.MinPt = Get_Min_Tension_Steel_Percentage(fck, fy)
    res.MaxPt = Get_Max_Tension_Steel_Percentage()
    res.ConfinementSpacing = Calculate_Confinement_Spacing(d, min_long_bar_dia)

    If Not res.IsGeometryValid Then
        res.Remarks = msg
    Else
        res.Remarks = "Compliant"
    End If

    Check_Beam_Ductility = res
End Function
