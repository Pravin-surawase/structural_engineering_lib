Attribute VB_Name = "Test_Compliance"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       Test_Compliance
' Description:  Unit tests for M19_Compliance module
' Version:      0.9.4
' ==============================================================================

Private g_PassCount As Long
Private g_FailCount As Long

Public Sub RunComplianceTests()
    ' Main test runner for Compliance module.
    '
    ' Run from Immediate Window: RunComplianceTests

    g_PassCount = 0
    g_FailCount = 0

    Debug.Print "========================================"
    Debug.Print "Compliance Module Tests"
    Debug.Print "========================================"

    ' Basic compliance checks
    Test_SingleCase_OK
    Test_SingleCase_FlexureFail
    Test_SingleCase_ShearFail
    Test_SingleCase_BothFail

    ' Utilization tests
    Test_Utilization_SafeSection
    Test_Utilization_HighlyUtilized

    ' Multi-case tests
    Test_MultipleCases_AllOK
    Test_MultipleCases_OneFail
    Test_MultipleCases_GoverningCase

    ' UDF tests
    Test_UDF_ComplianceCheck
    Test_UDF_Utilization

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

Private Sub AssertTrue(ByVal condition As Boolean, ByVal testName As String)
    If condition Then
        g_PassCount = g_PassCount + 1
        Debug.Print "[PASS] " & testName
    Else
        g_FailCount = g_FailCount + 1
        Debug.Print "[FAIL] " & testName & " - Expected True"
    End If
End Sub

Private Sub AssertFalse(ByVal condition As Boolean, ByVal testName As String)
    If Not condition Then
        g_PassCount = g_PassCount + 1
        Debug.Print "[PASS] " & testName
    Else
        g_FailCount = g_FailCount + 1
        Debug.Print "[FAIL] " & testName & " - Expected False"
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

Private Sub AssertContains(ByVal text As String, ByVal substring As String, ByVal testName As String)
    If InStr(1, text, substring, vbTextCompare) > 0 Then
        g_PassCount = g_PassCount + 1
        Debug.Print "[PASS] " & testName
    Else
        g_FailCount = g_FailCount + 1
        Debug.Print "[FAIL] " & testName & " - Expected '" & text & "' to contain '" & substring & "'"
    End If
End Sub


' =============================================================================
' Basic Compliance Check Tests
' =============================================================================

Private Sub Test_SingleCase_OK()
    ' Test a case that should pass all checks
    ' Low Mu and Vu on a generous section
    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("C1", 50, 30, 300, 500, 450, 25, 415)

    AssertTrue result.is_ok, "SingleCase_OK_IsOK"
    AssertTrue result.flexure.IsSafe, "SingleCase_OK_FlexureSafe"
    AssertTrue result.shear.IsSafe, "SingleCase_OK_ShearSafe"
    AssertContains result.remarks, "OK", "SingleCase_OK_Remarks"
End Sub

Private Sub Test_SingleCase_FlexureFail()
    ' Test a case with very high Mu that should fail flexure
    ' 500 kN·m on a 200x400 section is way too much
    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("C2", 500, 30, 200, 400, 350, 20, 415)

    AssertFalse result.is_ok, "FlexureFail_IsNotOK"
    AssertFalse result.flexure.IsSafe, "FlexureFail_FlexureNotSafe"
    AssertContains result.failed_checks, "flexure", "FlexureFail_FailedChecks"
End Sub

Private Sub Test_SingleCase_ShearFail()
    ' Test a case with very high Vu that should fail shear
    ' 500 kN on a small section exceeds tc_max
    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("C3", 50, 500, 200, 400, 350, 20, 415)

    AssertFalse result.is_ok, "ShearFail_IsNotOK"
    AssertContains result.failed_checks, "shear", "ShearFail_FailedChecks"
End Sub

Private Sub Test_SingleCase_BothFail()
    ' Test a case that fails both flexure and shear
    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("C4", 500, 500, 200, 400, 350, 20, 415)

    AssertFalse result.is_ok, "BothFail_IsNotOK"
    AssertContains result.failed_checks, "flexure", "BothFail_HasFlexure"
    AssertContains result.failed_checks, "shear", "BothFail_HasShear"
End Sub


' =============================================================================
' Utilization Tests
' =============================================================================

Private Sub Test_Utilization_SafeSection()
    ' A safe section should have utilization < 1.0
    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("U1", 50, 30, 300, 500, 450, 25, 415)

    AssertTrue result.governing_utilization < 1#, "SafeSection_UtilLT1"
    AssertTrue result.governing_utilization > 0#, "SafeSection_UtilGT0"
End Sub

Private Sub Test_Utilization_HighlyUtilized()
    ' A section near its limit should have utilization close to 1.0
    ' 150 kN·m on 250x500 with M25/Fe415
    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("U2", 150, 50, 250, 500, 450, 25, 415)

    AssertTrue result.governing_utilization > 0.3, "HighUtil_Reasonable"
End Sub


' =============================================================================
' Multi-Case Tests
' =============================================================================

Private Sub Test_MultipleCases_AllOK()
    ' Test multiple cases where all pass
    Dim cases(1) As ComplianceCaseResult
    Dim report As ComplianceReport

    cases(0) = Compliance_CheckCase("C1", 50, 30, 300, 500, 450, 25, 415)
    cases(1) = Compliance_CheckCase("C2", 80, 40, 300, 500, 450, 25, 415)

    report = Compliance_CheckMultipleCases(cases)

    AssertEqual report.case_count, 2, "MultiAllOK_CaseCount"
    AssertEqual report.cases_ok, 2, "MultiAllOK_CasesOK"
    AssertEqual report.cases_failed, 0, "MultiAllOK_CasesFailed"
    AssertTrue report.overall_is_ok, "MultiAllOK_OverallOK"
End Sub

Private Sub Test_MultipleCases_OneFail()
    ' Test multiple cases where one fails
    Dim cases(1) As ComplianceCaseResult
    Dim report As ComplianceReport

    cases(0) = Compliance_CheckCase("C1", 50, 30, 300, 500, 450, 25, 415)
    cases(1) = Compliance_CheckCase("C2", 500, 30, 200, 400, 350, 20, 415) ' Will fail

    report = Compliance_CheckMultipleCases(cases)

    AssertEqual report.case_count, 2, "MultiOneFail_CaseCount"
    AssertEqual report.cases_ok, 1, "MultiOneFail_CasesOK"
    AssertEqual report.cases_failed, 1, "MultiOneFail_CasesFailed"
    AssertFalse report.overall_is_ok, "MultiOneFail_OverallNotOK"
End Sub

Private Sub Test_MultipleCases_GoverningCase()
    ' The governing case should be the one with highest utilization
    Dim cases(2) As ComplianceCaseResult
    Dim report As ComplianceReport

    cases(0) = Compliance_CheckCase("Low", 30, 20, 300, 500, 450, 25, 415)
    cases(1) = Compliance_CheckCase("High", 180, 80, 300, 500, 450, 25, 415) ' Higher util
    cases(2) = Compliance_CheckCase("Mid", 100, 50, 300, 500, 450, 25, 415)

    report = Compliance_CheckMultipleCases(cases)

    AssertEqual report.governing_case_id, "High", "GoverningCase_IsHigh"
    AssertTrue report.governing_utilization > cases(0).governing_utilization, "GoverningCase_HigherThanLow"
End Sub


' =============================================================================
' UDF Tests
' =============================================================================

Private Sub Test_UDF_ComplianceCheck()
    ' Test the UDF wrapper
    Dim result As String
    result = IS456_ComplianceCheck(50, 30, 300, 500, 450, 25, 415)
    AssertContains result, "OK", "UDF_ComplianceCheck_OK"
End Sub

Private Sub Test_UDF_Utilization()
    ' Test the utilization UDF
    Dim util As Double
    util = IS456_Utilization(50, 30, 300, 500, 450, 25, 415)
    AssertTrue util > 0#, "UDF_Utilization_GT0"
    AssertTrue util < 1#, "UDF_Utilization_LT1"
End Sub
