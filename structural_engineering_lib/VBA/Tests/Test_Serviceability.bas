Attribute VB_Name = "Test_Serviceability"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       Test_Serviceability
' Description:  Unit Tests for M17_Serviceability module
' Version:      0.8.0
' ==============================================================================

Private m_PassCount As Long
Private m_FailCount As Long
Private m_Results As String

Public Sub Run_All_Serviceability_Tests()
    m_PassCount = 0
    m_FailCount = 0
    m_Results = ""

    Debug.Print "========================================"
    Debug.Print "TEST SUITE: M17_Serviceability"
    Debug.Print "========================================"

    Call Test_Deflection_OK_Defaults
    Call Test_Deflection_Fails_When_Too_Slender
    Call Test_CrackWidth_Fails_When_Missing_Params
    Call Test_CrackWidth_OK_With_Explicit_Params

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

Private Sub AssertApprox(ByVal actual As Double, ByVal expected As Double, ByVal testName As String, Optional ByVal tolerance As Double = 0.000001)
    If Abs(actual - expected) <= tolerance Then
        m_PassCount = m_PassCount + 1
        Debug.Print "  [PASS] " & testName
    Else
        m_FailCount = m_FailCount + 1
        Debug.Print "  [FAIL] " & testName & " - Expected: " & expected & ", Got: " & actual
        m_Results = m_Results & testName & ": Expected " & expected & ", Got " & actual & vbCrLf
    End If
End Sub

' ------------------------------------------------------------------------------
' Tests
' ------------------------------------------------------------------------------
Private Sub Test_Deflection_OK_Defaults()
    Dim res As DeflectionResult
    res = M17_Serviceability.Check_Deflection_SpanDepth(span_mm:=4000, d_mm:=500, support_condition:="simply_supported")
    Call AssertTrue(res.IsOK, "Deflection OK with defaults")
    Call AssertApprox(res.LD_Ratio, 8#, "Deflection L/d computed")
End Sub

Private Sub Test_Deflection_Fails_When_Too_Slender()
    Dim res As DeflectionResult
    res = M17_Serviceability.Check_Deflection_SpanDepth(
        span_mm:=4000,
        d_mm:=100,
        support_condition:="simply_supported",
        base_allowable_ld:=20#,
        mf_tension_steel:=1#,
        mf_compression_steel:=1#,
        mf_flanged:=1#
    )
    Call AssertFalse(res.IsOK, "Deflection fails when L/d exceeds allowable")
    Call AssertApprox(res.LD_Ratio, 40#, "Deflection L/d ratio")
    Call AssertApprox(res.Allowable_LD, 20#, "Deflection allowable")
End Sub

Private Sub Test_CrackWidth_Fails_When_Missing_Params()
    Dim res As CrackWidthResult
    res = M17_Serviceability.Check_CrackWidth(exposure_class:="moderate", limit_mm:=0.3)
    Call AssertFalse(res.IsOK, "Crack width fails when missing required parameters")
End Sub

Private Sub Test_CrackWidth_OK_With_Explicit_Params()
    Dim res As CrackWidthResult
    res = M17_Serviceability.Check_CrackWidth(
        exposure_class:="moderate",
        limit_mm:=0.3,
        acr_mm:=50#,
        cmin_mm:=25#,
        h_mm:=500#,
        x_mm:=200#,
        epsilon_m:=0.001
    )
    Call AssertTrue(res.Denom > 0#, "Crack width denom positive")
    Call AssertTrue(res.IsOK, "Crack width OK under limit")
End Sub
