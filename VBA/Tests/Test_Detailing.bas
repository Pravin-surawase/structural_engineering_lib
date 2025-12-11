Attribute VB_Name = "Test_Detailing"
Option Explicit

' ==============================================================================
' Module:       Test_Detailing
' Description:  Unit Tests for M15_Detailing module
' Version:      0.7.0
' License:      MIT
' ==============================================================================

Private m_PassCount As Long
Private m_FailCount As Long
Private m_Results As String

' ------------------------------------------------------------------------------
' Main Test Runner
' ------------------------------------------------------------------------------
Public Sub Run_All_Detailing_Tests()
    m_PassCount = 0
    m_FailCount = 0
    m_Results = ""
    
    Debug.Print "========================================"
    Debug.Print "TEST SUITE: M15_Detailing"
    Debug.Print "========================================"
    
    ' Bond Stress Tests
    Call Test_BondStress_M20
    Call Test_BondStress_M25
    Call Test_BondStress_M30
    Call Test_BondStress_Plain
    
    ' Development Length Tests
    Call Test_Ld_Standard
    Call Test_Ld_Fe415
    Call Test_Ld_Fe500
    
    ' Lap Length Tests
    Call Test_LapLength_Tension
    Call Test_LapLength_Compression
    Call Test_LapLength_Seismic
    
    ' Bar Spacing Tests
    Call Test_BarSpacing_Basic
    Call Test_BarSpacing_SingleBar
    Call Test_MinSpacing_Check
    
    ' Stirrup Legs Tests
    Call Test_StirrupLegs_Narrow
    Call Test_StirrupLegs_Medium
    Call Test_StirrupLegs_Wide
    
    ' Bar Selection Tests
    Call Test_SelectBarDia_Small
    Call Test_SelectBarDia_Medium
    Call Test_SelectBarDia_Large
    Call Test_BarCount
    
    ' Format Tests
    Call Test_BarCallout
    Call Test_StirrupCallout
    
    Debug.Print "========================================"
    Debug.Print "RESULTS: " & m_PassCount & " Passed, " & m_FailCount & " Failed"
    Debug.Print "========================================"
    
    If m_FailCount > 0 Then
        Debug.Print "FAILURES:"
        Debug.Print m_Results
    End If
End Sub


' ------------------------------------------------------------------------------
' Test Helpers
' ------------------------------------------------------------------------------
Private Sub AssertEqual(ByVal actual As Variant, ByVal expected As Variant, ByVal testName As String, Optional ByVal tolerance As Double = 0.01)
    Dim passed As Boolean
    
    If IsNumeric(actual) And IsNumeric(expected) Then
        passed = (Abs(CDbl(actual) - CDbl(expected)) <= tolerance * Abs(CDbl(expected) + 0.001))
    Else
        passed = (actual = expected)
    End If
    
    If passed Then
        m_PassCount = m_PassCount + 1
        Debug.Print "  [PASS] " & testName
    Else
        m_FailCount = m_FailCount + 1
        Debug.Print "  [FAIL] " & testName & " - Expected: " & expected & ", Got: " & actual
        m_Results = m_Results & testName & ": Expected " & expected & ", Got " & actual & vbCrLf
    End If
End Sub

Private Sub AssertTrue(ByVal condition As Boolean, ByVal testName As String)
    If condition Then
        m_PassCount = m_PassCount + 1
        Debug.Print "  [PASS] " & testName
    Else
        m_FailCount = m_FailCount + 1
        Debug.Print "  [FAIL] " & testName & " - Expected TRUE"
        m_Results = m_Results & testName & ": Expected TRUE" & vbCrLf
    End If
End Sub

Private Sub AssertFalse(ByVal condition As Boolean, ByVal testName As String)
    If Not condition Then
        m_PassCount = m_PassCount + 1
        Debug.Print "  [PASS] " & testName
    Else
        m_FailCount = m_FailCount + 1
        Debug.Print "  [FAIL] " & testName & " - Expected FALSE"
        m_Results = m_Results & testName & ": Expected FALSE" & vbCrLf
    End If
End Sub


' ==============================================================================
' Bond Stress Tests
' ==============================================================================

Private Sub Test_BondStress_M20()
    Dim result As Double
    result = M15_Detailing.Get_Bond_Stress(20, "deformed")
    Call AssertEqual(result, 1.92, "BondStress_M20_Deformed")
End Sub

Private Sub Test_BondStress_M25()
    Dim result As Double
    result = M15_Detailing.Get_Bond_Stress(25, "deformed")
    Call AssertEqual(result, 2.24, "BondStress_M25_Deformed")
End Sub

Private Sub Test_BondStress_M30()
    Dim result As Double
    result = M15_Detailing.Get_Bond_Stress(30, "deformed")
    Call AssertEqual(result, 2.4, "BondStress_M30_Deformed")
End Sub

Private Sub Test_BondStress_Plain()
    Dim result As Double
    result = M15_Detailing.Get_Bond_Stress(25, "plain")
    Call AssertEqual(result, 1.4, "BondStress_M25_Plain")  ' 2.24/1.6 = 1.4
End Sub


' ==============================================================================
' Development Length Tests
' ==============================================================================

Private Sub Test_Ld_Standard()
    ' 16mm bar, M25, Fe500: Ld = (16 * 0.87 * 500) / (4 * 2.24) = 776.8
    Dim result As Double
    result = M15_Detailing.Calculate_Development_Length(16, 25, 500, "deformed")
    Call AssertEqual(result, 777, "Ld_16mm_M25_Fe500", 0.02)
End Sub

Private Sub Test_Ld_Fe415()
    ' 16mm bar, M25, Fe415: Ld = (16 * 0.87 * 415) / (4 * 2.24) = 644.8
    Dim result As Double
    result = M15_Detailing.Calculate_Development_Length(16, 25, 415, "deformed")
    Call AssertEqual(result, 645, "Ld_16mm_M25_Fe415", 0.02)
End Sub

Private Sub Test_Ld_Fe500()
    ' 20mm bar, M25, Fe500: Ld = (20 * 0.87 * 500) / (4 * 2.24) = 971
    Dim result As Double
    result = M15_Detailing.Calculate_Development_Length(20, 25, 500, "deformed")
    Call AssertEqual(result, 971, "Ld_20mm_M25_Fe500", 0.02)
End Sub


' ==============================================================================
' Lap Length Tests
' ==============================================================================

Private Sub Test_LapLength_Tension()
    ' 16mm bar, M25, Fe500, tension: Ld * 1.0 = 777
    Dim result As Double
    result = M15_Detailing.Calculate_Lap_Length(16, 25, 500, "deformed", 50, False, True)
    Call AssertEqual(result, 777, "LapLength_Tension_Standard", 0.02)
End Sub

Private Sub Test_LapLength_Compression()
    ' 16mm bar, M25, Fe500, compression: Ld = 777
    Dim result As Double
    result = M15_Detailing.Calculate_Lap_Length(16, 25, 500, "deformed", 50, False, False)
    Call AssertEqual(result, 777, "LapLength_Compression", 0.02)
End Sub

Private Sub Test_LapLength_Seismic()
    ' 16mm bar, M25, Fe500, seismic: Ld * 1.5 = 1166
    Dim result As Double
    result = M15_Detailing.Calculate_Lap_Length(16, 25, 500, "deformed", 50, True, True)
    Call AssertEqual(result, 1166, "LapLength_Seismic", 0.02)
End Sub


' ==============================================================================
' Bar Spacing Tests
' ==============================================================================

Private Sub Test_BarSpacing_Basic()
    ' b=300, cover=40, stirrup=8, bar=16, 3 bars
    ' Available = 300 - 2*(40+8) - 16 = 188, Spacing = 188/2 = 94
    Dim result As Double
    result = M15_Detailing.Calculate_Bar_Spacing(300, 40, 8, 16, 3)
    Call AssertEqual(result, 94, "BarSpacing_3bars_300w")
End Sub

Private Sub Test_BarSpacing_SingleBar()
    ' Single bar should return 0
    Dim result As Double
    result = M15_Detailing.Calculate_Bar_Spacing(300, 40, 8, 16, 1)
    Call AssertEqual(result, 0, "BarSpacing_SingleBar")
End Sub

Private Sub Test_MinSpacing_Check()
    ' min_spacing = max(16, 20+5, 25) = 25
    ' spacing=94 >= 25, should pass
    Dim result As Boolean
    result = M15_Detailing.Check_Min_Spacing(94, 16, 20)
    Call AssertTrue(result, "MinSpacing_94mm_OK")
    
    ' spacing=20 < 25, should fail
    result = M15_Detailing.Check_Min_Spacing(20, 16, 20)
    Call AssertFalse(result, "MinSpacing_20mm_Fail")
End Sub


' ==============================================================================
' Stirrup Legs Tests
' ==============================================================================

Private Sub Test_StirrupLegs_Narrow()
    Dim result As Long
    result = M15_Detailing.Get_Stirrup_Legs(250)
    Call AssertEqual(result, 2, "StirrupLegs_250mm")
End Sub

Private Sub Test_StirrupLegs_Medium()
    Dim result As Long
    result = M15_Detailing.Get_Stirrup_Legs(500)
    Call AssertEqual(result, 4, "StirrupLegs_500mm")
End Sub

Private Sub Test_StirrupLegs_Wide()
    Dim result As Long
    result = M15_Detailing.Get_Stirrup_Legs(700)
    Call AssertEqual(result, 6, "StirrupLegs_700mm")
End Sub


' ==============================================================================
' Bar Selection Tests
' ==============================================================================

Private Sub Test_SelectBarDia_Small()
    Dim result As Double
    result = M15_Detailing.Select_Bar_Diameter(300)
    Call AssertEqual(result, 12, "SelectBarDia_300mm2")
End Sub

Private Sub Test_SelectBarDia_Medium()
    Dim result As Double
    result = M15_Detailing.Select_Bar_Diameter(800)
    Call AssertEqual(result, 16, "SelectBarDia_800mm2")
End Sub

Private Sub Test_SelectBarDia_Large()
    Dim result As Double
    result = M15_Detailing.Select_Bar_Diameter(1500)
    Call AssertEqual(result, 20, "SelectBarDia_1500mm2")
End Sub

Private Sub Test_BarCount()
    ' 942 mm² with 20mm bars (area=314.16): 942/314.16 = 2.99 → 3 bars
    Dim result As Long
    result = M15_Detailing.Calculate_Bar_Count(942, 20)
    Call AssertEqual(result, 3, "BarCount_942mm2_20dia")
End Sub


' ==============================================================================
' Format Tests
' ==============================================================================

Private Sub Test_BarCallout()
    Dim result As String
    result = M15_Detailing.Format_Bar_Callout(3, 16)
    Call AssertEqual(result, "3-16" & ChrW(966), "BarCallout_3-16")
End Sub

Private Sub Test_StirrupCallout()
    Dim result As String
    result = M15_Detailing.Format_Stirrup_Callout(2, 8, 150)
    Call AssertEqual(result, "2L-8" & ChrW(966) & "@150 c/c", "StirrupCallout_2L-8@150")
End Sub
