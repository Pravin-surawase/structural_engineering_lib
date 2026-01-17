Attribute VB_Name = "Test_BBS"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       Test_BBS
' Description:  Unit tests for M18_BBS module
' Version:      0.9.4
' ==============================================================================

Private g_PassCount As Long
Private g_FailCount As Long

Public Sub RunBBSTests()
    ' Main test runner for BBS module.
    '
    ' Run from Immediate Window: RunBBSTests

    g_PassCount = 0
    g_FailCount = 0

    Debug.Print "========================================"
    Debug.Print "BBS Module Tests"
    Debug.Print "========================================"

    ' Weight calculation tests
    Test_BarWeight_16mm_1m
    Test_BarWeight_20mm_2m
    Test_BarWeight_Zero_Diameter
    Test_BarWeight_Zero_Length

    ' Unit weight tests
    Test_UnitWeight_Standard_Diameters
    Test_UnitWeight_Calculated

    ' Hook length tests
    Test_HookLength_90deg
    Test_HookLength_135deg
    Test_HookLength_180deg

    ' Bend deduction tests
    Test_BendDeduction_90deg
    Test_BendDeduction_135deg
    Test_BendDeduction_180deg

    ' Stirrup cut length tests
    Test_StirrupCutLength_300x500
    Test_StirrupCutLength_250x450

    ' Line item creation tests
    Test_CreateLineItem_Basic
    Test_CreateLineItem_Stirrup

    ' Summary tests
    Test_Summary_SingleItem
    Test_Summary_MultipleItems

    Debug.Print "========================================"
    Debug.Print "RESULTS: " & g_PassCount & " passed, " & g_FailCount & " failed"
    Debug.Print "========================================"
End Sub


' =============================================================================
' Assertion Helpers
' =============================================================================

Private Sub AssertEqual(ByVal actual As Variant, ByVal expected As Variant, ByVal testName As String)
    If actual = expected Then
        g_PassCount = g_PassCount + 1
        Debug.Print "[PASS] " & testName
    Else
        g_FailCount = g_FailCount + 1
        Debug.Print "[FAIL] " & testName & " - Expected: " & expected & ", Got: " & actual
    End If
End Sub

Private Sub AssertNear(ByVal actual As Double, ByVal expected As Double, ByVal tolerance As Double, ByVal testName As String)
    If Abs(actual - expected) <= tolerance Then
        g_PassCount = g_PassCount + 1
        Debug.Print "[PASS] " & testName
    Else
        g_FailCount = g_FailCount + 1
        Debug.Print "[FAIL] " & testName & " - Expected: " & expected & " +/- " & tolerance & ", Got: " & actual
    End If
End Sub

Private Sub AssertTrue(ByVal condition As Boolean, ByVal testName As String)
    If condition Then
        g_PassCount = g_PassCount + 1
        Debug.Print "[PASS] " & testName
    Else
        g_FailCount = g_FailCount + 1
        Debug.Print "[FAIL] " & testName & " - Expected True"
    End If
End Sub


' =============================================================================
' Weight Calculation Tests
' =============================================================================

Private Sub Test_BarWeight_16mm_1m()
    ' 16mm bar, 1m length should be approximately 1.58 kg
    ' π × (8/1000)² × 1 × 7850 ≈ 1.579 kg
    Dim weight As Double
    weight = BBS_CalculateBarWeight(16, 1000)
    AssertNear weight, 1.58, 0.01, "BarWeight_16mm_1m"
End Sub

Private Sub Test_BarWeight_20mm_2m()
    ' 20mm bar, 2m length
    ' π × (10/1000)² × 2 × 7850 ≈ 4.93 kg
    Dim weight As Double
    weight = BBS_CalculateBarWeight(20, 2000)
    AssertNear weight, 4.93, 0.05, "BarWeight_20mm_2m"
End Sub

Private Sub Test_BarWeight_Zero_Diameter()
    ' Zero diameter should return 0
    Dim weight As Double
    weight = BBS_CalculateBarWeight(0, 1000)
    AssertEqual weight, 0#, "BarWeight_Zero_Diameter"
End Sub

Private Sub Test_BarWeight_Zero_Length()
    ' Zero length should return 0
    Dim weight As Double
    weight = BBS_CalculateBarWeight(16, 0)
    AssertEqual weight, 0#, "BarWeight_Zero_Length"
End Sub


' =============================================================================
' Unit Weight Tests
' =============================================================================

Private Sub Test_UnitWeight_Standard_Diameters()
    ' Standard diameters should match pre-calculated values
    AssertNear BBS_GetStandardUnitWeight(8), 0.395, 0.001, "UnitWeight_8mm"
    AssertNear BBS_GetStandardUnitWeight(12), 0.888, 0.001, "UnitWeight_12mm"
    AssertNear BBS_GetStandardUnitWeight(16), 1.579, 0.001, "UnitWeight_16mm"
    AssertNear BBS_GetStandardUnitWeight(20), 2.466, 0.001, "UnitWeight_20mm"
    AssertNear BBS_GetStandardUnitWeight(25), 3.853, 0.001, "UnitWeight_25mm"
End Sub

Private Sub Test_UnitWeight_Calculated()
    ' Non-standard diameter should be calculated
    Dim weight As Double
    weight = BBS_GetStandardUnitWeight(14)
    AssertTrue weight > 1#, "UnitWeight_14mm_Calculated"
End Sub


' =============================================================================
' Hook Length Tests
' =============================================================================

Private Sub Test_HookLength_90deg()
    ' 90° hook = 8d
    Dim hookLen As Double
    hookLen = BBS_CalculateHookLength(12, 90)
    AssertEqual hookLen, 96#, "HookLength_90deg_12mm"
End Sub

Private Sub Test_HookLength_135deg()
    ' 135° hook = 6d
    Dim hookLen As Double
    hookLen = BBS_CalculateHookLength(12, 135)
    AssertEqual hookLen, 72#, "HookLength_135deg_12mm"
End Sub

Private Sub Test_HookLength_180deg()
    ' 180° hook = 8d
    Dim hookLen As Double
    hookLen = BBS_CalculateHookLength(12, 180)
    AssertEqual hookLen, 96#, "HookLength_180deg_12mm"
End Sub


' =============================================================================
' Bend Deduction Tests
' =============================================================================

Private Sub Test_BendDeduction_90deg()
    ' 90° bend = 2d
    Dim deduction As Double
    deduction = BBS_CalculateBendDeduction(12, 90)
    AssertEqual deduction, 24#, "BendDeduction_90deg_12mm"
End Sub

Private Sub Test_BendDeduction_135deg()
    ' 135° bend = 3d
    Dim deduction As Double
    deduction = BBS_CalculateBendDeduction(12, 135)
    AssertEqual deduction, 36#, "BendDeduction_135deg_12mm"
End Sub

Private Sub Test_BendDeduction_180deg()
    ' 180° bend = 4d
    Dim deduction As Double
    deduction = BBS_CalculateBendDeduction(12, 180)
    AssertEqual deduction, 48#, "BendDeduction_180deg_12mm"
End Sub


' =============================================================================
' Stirrup Cut Length Tests
' =============================================================================

Private Sub Test_StirrupCutLength_300x500()
    ' 300x500mm beam, 25mm cover, 8mm stirrup
    ' Inner: 250 × 450
    ' Perimeter: 2×250 + 2×450 = 1400mm
    ' Hooks: 2 × 6 × 8 = 96mm (135° hooks)
    ' Bend deductions: 4 × 2 × 8 = 64mm
    ' Total ≈ 1400 + 96 - 64 = 1432mm → rounded to 1430mm
    Dim cutLen As Double
    cutLen = BBS_CalculateStirrupCutLength(300, 500, 25, 8, 135)
    AssertTrue cutLen > 1400 And cutLen < 1500, "StirrupCutLength_300x500"
End Sub

Private Sub Test_StirrupCutLength_250x450()
    ' 250x450mm beam, 25mm cover, 8mm stirrup
    Dim cutLen As Double
    cutLen = BBS_CalculateStirrupCutLength(250, 450, 25, 8, 135)
    AssertTrue cutLen > 1100 And cutLen < 1300, "StirrupCutLength_250x450"
End Sub


' =============================================================================
' Line Item Creation Tests
' =============================================================================

Private Sub Test_CreateLineItem_Basic()
    ' Create a basic straight bar line item
    Dim item As BBSLineItem
    item = BBS_CreateLineItem("A1", "B1", "bottom", "full", "A", 16, 4, 5500)

    AssertEqual item.bar_mark, "A1", "LineItem_BarMark"
    AssertEqual item.member_id, "B1", "LineItem_MemberId"
    AssertEqual item.no_of_bars, 4, "LineItem_Count"
    AssertEqual item.cut_length_mm, 5500#, "LineItem_CutLength"
    AssertEqual item.total_length_mm, 22000#, "LineItem_TotalLength"
    AssertTrue item.unit_weight_kg > 0, "LineItem_UnitWeight"
    AssertTrue item.total_weight_kg > 0, "LineItem_TotalWeight"
End Sub

Private Sub Test_CreateLineItem_Stirrup()
    ' Create a stirrup line item
    Dim item As BBSLineItem
    item = BBS_CreateLineItem("S1", "B1", "stirrup", "start", "E", 8, 20, 1400)

    AssertEqual item.bar_mark, "S1", "StirrupItem_BarMark"
    AssertEqual item.location, "stirrup", "StirrupItem_Location"
    AssertEqual item.shape_code, "E", "StirrupItem_Shape"
    AssertEqual item.no_of_bars, 20, "StirrupItem_Count"
End Sub


' =============================================================================
' Summary Tests
' =============================================================================

Private Sub Test_Summary_SingleItem()
    ' Summary with single item
    Dim items(0) As BBSLineItem
    Dim summary As BBSSummary

    items(0) = BBS_CreateLineItem("A1", "B1", "bottom", "full", "A", 16, 4, 5500)
    summary = BBS_CalculateSummary(items, "B1")

    AssertEqual summary.member_id, "B1", "Summary_MemberId"
    AssertEqual summary.total_items, 1, "Summary_TotalItems"
    AssertEqual summary.total_bars, 4, "Summary_TotalBars"
    AssertNear summary.total_length_m, 22#, 0.1, "Summary_TotalLength"
    AssertTrue summary.total_weight_kg > 0, "Summary_TotalWeight"
End Sub

Private Sub Test_Summary_MultipleItems()
    ' Summary with multiple items
    Dim items(1) As BBSLineItem
    Dim summary As BBSSummary

    items(0) = BBS_CreateLineItem("A1", "B1", "bottom", "full", "A", 16, 4, 5500)
    items(1) = BBS_CreateLineItem("S1", "B1", "stirrup", "full", "E", 8, 30, 1400)
    summary = BBS_CalculateSummary(items, "B1")

    AssertEqual summary.total_items, 2, "MultiSummary_TotalItems"
    AssertEqual summary.total_bars, 34, "MultiSummary_TotalBars"
    AssertTrue summary.total_weight_kg > 30, "MultiSummary_TotalWeight"
End Sub
