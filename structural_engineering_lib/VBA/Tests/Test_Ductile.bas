Attribute VB_Name = "Test_Ductile"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       Test_Ductile
' Description:  Unit tests for IS 13920 Ductile Detailing
' Version:      1.0.0
' Dependencies: M10_Ductile
' ==============================================================================

Private Sub AssertTrue(ByVal Condition As Boolean, Optional ByVal TestName As String = "")
    If Not Condition Then
        Debug.Print "FAIL: " & TestName & " | Expected True"
    Else
        Debug.Print "PASS: " & TestName
    End If
End Sub

Private Sub AssertFalse(ByVal Condition As Boolean, Optional ByVal TestName As String = "")
    If Condition Then
        Debug.Print "FAIL: " & TestName & " | Expected False"
    Else
        Debug.Print "PASS: " & TestName
    End If
End Sub

Private Sub AssertAlmostEqual(ByVal Actual As Double, ByVal Expected As Double, Optional ByVal Tolerance As Double = 0.001, Optional ByVal TestName As String = "")
    If Abs(Actual - Expected) > Tolerance Then
        Debug.Print "FAIL: " & TestName & " | Expected " & Expected & ", Got " & Actual
    Else
        Debug.Print "PASS: " & TestName
    End If
End Sub

Public Sub RunDuctileTests()
    Debug.Print "--- Starting Ductile Detailing Tests ---"
    Test_Geometry_Checks
    Test_Min_Steel
    Test_Confinement_Spacing
    Test_Full_Check
    Debug.Print "--- Ductile Tests Completed ---"
End Sub

Private Sub Test_Geometry_Checks()
    Dim valid As Boolean
    Dim msg As String

    ' Valid case: 230x450
    valid = M10_Ductile.Check_Geometry(230#, 450#, msg)
    AssertTrue valid, "Geometry_Valid_230x450"
    AssertTrue (msg = "OK"), "Geometry_Msg_OK"

    ' Invalid Width: 150x450
    valid = M10_Ductile.Check_Geometry(150#, 450#, msg)
    AssertFalse valid, "Geometry_Invalid_Width"

    ' Invalid Ratio: 200x700 (ratio 0.285 < 0.3)
    valid = M10_Ductile.Check_Geometry(200#, 700#, msg)
    AssertFalse valid, "Geometry_Invalid_Ratio"
End Sub

Private Sub Test_Min_Steel()
    Dim pt As Double

    ' fck=25, fy=500 -> 0.24%
    pt = M10_Ductile.Get_Min_Tension_Steel_Percentage(25#, 500#)
    AssertAlmostEqual pt, 0.24, 0.0001, "MinSteel_M25_Fe500"

    ' fck=30, fy=415 -> 0.3168%
    pt = M10_Ductile.Get_Min_Tension_Steel_Percentage(30#, 415#)
    AssertAlmostEqual pt, 0.3168, 0.001, "MinSteel_M30_Fe415"
End Sub

Private Sub Test_Confinement_Spacing()
    Dim s As Double

    ' d=450, min_bar=12
    ' 1. d/4 = 112.5
    ' 2. 8*12 = 96
    ' 3. 100
    ' Min should be 96
    s = M10_Ductile.Calculate_Confinement_Spacing(450#, 12#)
    AssertAlmostEqual s, 96#, 0.1, "Spacing_Case1"

    ' d=600, min_bar=20
    ' 1. 150
    ' 2. 160
    ' 3. 100
    ' Min should be 100
    s = M10_Ductile.Calculate_Confinement_Spacing(600#, 20#)
    AssertAlmostEqual s, 100#, 0.1, "Spacing_Case2"
End Sub

Private Sub Test_Full_Check()
    Dim res As DuctileBeamResult

    ' Valid Beam
    res = M10_Ductile.Check_Beam_Ductility(230#, 450#, 410#, 25#, 500#, 12#)
    AssertTrue res.IsGeometryValid, "FullCheck_Valid_Geo"

    ' d=410. d/4 = 102.5. 8*12=96. 100. Min is 96.
    AssertAlmostEqual res.ConfinementSpacing, 96#, 0.1, "FullCheck_Spacing"

    AssertTrue (res.Remarks = "Compliant"), "FullCheck_Remarks"
End Sub
