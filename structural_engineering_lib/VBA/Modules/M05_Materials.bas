Attribute VB_Name = "M05_Materials"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       M05_Materials
' Description:  Material properties and derived constants (fck, fy related)
' Version:      1.0.01
' ==============================================================================

' Get Xu,max/d ratio based on steel grade (IS 456 Cl. 38.1)
' Returns 0 for invalid fy values (<= 0)
Public Function Get_XuMax_d(ByVal fy As Double) As Double
    If fy <= 0 Then
        Get_XuMax_d = 0#
        Exit Function
    End If
    Select Case fy
        Case 250: Get_XuMax_d = 0.53
        Case 415: Get_XuMax_d = 0.48
        Case 500: Get_XuMax_d = 0.46
        Case Else
            ' For other grades, use formula: 700 / (1100 + 0.87*fy)
            Get_XuMax_d = 700 / (1100 + (0.87 * fy))
    End Select
End Function

' Modulus of Elasticity of Concrete (IS 456 Cl. 6.2.3.1)
' Ec = 5000 * sqrt(fck)
Public Function Get_Ec(ByVal fck As Double) As Double
    If fck < 0 Then Get_Ec = 0 Else Get_Ec = 5000 * Sqr(fck)
End Function

' Flexural Strength of Concrete (IS 456 Cl. 6.2.2)
' fcr = 0.7 * sqrt(fck)
Public Function Get_Fcr(ByVal fck As Double) As Double
    If fck < 0 Then Get_Fcr = 0 Else Get_Fcr = 0.7 * Sqr(fck)
End Function

' Calculate stress in steel for a given strain and yield strength
' Uses IS 456 Figure 23 curve for HYSD bars (Fe415, Fe500)
' For Fe250, assumes elasto-plastic behavior
Public Function Get_Steel_Stress(ByVal strain As Double, ByVal fy As Double) As Double
    Dim Es As Double
    Es = 200000# ' N/mm^2

    If fy = 250 Then
        Dim yield_strain As Double
        yield_strain = 0.87 * fy / Es
        If strain >= yield_strain Then
            Get_Steel_Stress = 0.87 * fy
        Else
            Get_Steel_Stress = strain * Es
        End If
        Exit Function
    End If

    ' For HYSD bars (Fe415, Fe500)
    ' Data from SP:16 Table A
    Dim s(1 To 5) As Double
    Dim f(1 To 5) As Double
    Dim i As Long

    If fy = 415 Then
        s(1) = 0.00144: f(1) = 288.7
        s(2) = 0.00163: f(2) = 306.7
        s(3) = 0.00192: f(3) = 324.8
        s(4) = 0.00241: f(4) = 342.8
        s(5) = 0.0038:  f(5) = 360.9
    ElseIf fy = 500 Then
        s(1) = 0.00174: f(1) = 347.8
        s(2) = 0.00195: f(2) = 369.6
        s(3) = 0.00226: f(3) = 391.3
        s(4) = 0.00277: f(4) = 413#
        s(5) = 0.00417: f(5) = 434.8
    Else
        ' Fallback
        yield_strain = 0.87 * fy / Es + 0.002
        If strain >= yield_strain Then
            Get_Steel_Stress = 0.87 * fy
        Else
            If strain * Es > 0.87 * fy Then
                Get_Steel_Stress = 0.87 * fy
            Else
                Get_Steel_Stress = strain * Es
            End If
        End If
        Exit Function
    End If

    ' Interpolation Logic

    ' 1. Elastic region check
    If strain < s(1) Then
        Get_Steel_Stress = strain * Es
        Exit Function
    End If

    ' 2. Inelastic region interpolation
    For i = 1 To 4
        If strain >= s(i) And strain <= s(i + 1) Then
            Get_Steel_Stress = f(i) + (f(i + 1) - f(i)) * (strain - s(i)) / (s(i + 1) - s(i))
            Exit Function
        End If
    Next i

    ' 3. Yield plateau
    Get_Steel_Stress = f(5)
End Function
