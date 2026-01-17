Attribute VB_Name = "M19_Compliance"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       M19_Compliance
' Description:  Compliance Checker — Orchestrates Flexure + Shear + Serviceability
' Version:      0.9.4
' ==============================================================================
'
' MVP Contract:
' - Accepts already-factored actions (Mu in kN·m, Vu in kN).
' - Produces per-case results + deterministic governing case.
'
' Design constraints:
' - Deterministic outputs (same inputs → same outputs).
' - Units explicit at API boundary.
' - No silent defaults: assumed values recorded in remarks.
' - Mac-safe: CDbl() for all multiplications.

' =============================================================================
' Types
' =============================================================================

Public Type ComplianceCaseResult
    case_id As String
    mu_knm As Double
    vu_kn As Double

    ' Sub-results
    flexure As FlexureResult
    shear As ShearResult
    deflection As DeflectionResult
    crack As CrackWidthResult

    ' Summary
    is_ok As Boolean
    governing_utilization As Double
    util_flexure As Double
    util_shear As Double
    util_deflection As Double
    util_crack As Double
    failed_checks As String  ' Comma-separated: "flexure,shear,deflection"
    remarks As String
End Type

Public Type ComplianceReport
    case_count As Long
    cases_ok As Long
    cases_failed As Long
    governing_case_id As String
    governing_utilization As Double
    overall_is_ok As Boolean
    remarks As String
End Type


' =============================================================================
' Utilization Helpers
' =============================================================================

Private Function UtilizationSafe(ByVal numer As Double, ByVal denom As Double) As Double
    ' Calculate utilization ratio safely (avoid divide by zero).
    If denom <= 0# Then
        If numer > 0# Then
            UtilizationSafe = 9999# ' Infinity substitute
        Else
            UtilizationSafe = 0#
        End If
    Else
        UtilizationSafe = CDbl(numer) / CDbl(denom)
    End If
End Function


Private Function ComputeFlexureUtilization(ByVal mu_knm As Double, ByRef flex As FlexureResult) As Double
    ' Compute flexure utilization as |Mu| / Mu_lim.
    Dim mu_abs As Double
    mu_abs = Abs(mu_knm)

    If mu_abs = 0# Then
        ComputeFlexureUtilization = 0#
        Exit Function
    End If

    If flex.Mu_Lim <= 0# Then
        ComputeFlexureUtilization = 9999#
        Exit Function
    End If

    ComputeFlexureUtilization = CDbl(mu_abs) / CDbl(flex.Mu_Lim)
End Function


Private Function ComputeShearUtilization(ByRef sh As ShearResult) As Double
    ' Compute shear utilization as Tv / Tc_max.
    If sh.Tc_max <= 0# Then
        If sh.Tv > 0# Then
            ComputeShearUtilization = 9999#
        Else
            ComputeShearUtilization = 0#
        End If
    Else
        ComputeShearUtilization = CDbl(sh.Tv) / CDbl(sh.Tc_max)
    End If
End Function


Private Function ComputeDeflectionUtilization(ByRef defl As DeflectionResult) As Double
    ' Compute deflection utilization as (L/d actual) / (L/d allowable).
    If defl.Allowable_LD <= 0# Then
        ComputeDeflectionUtilization = 0#
    Else
        ComputeDeflectionUtilization = CDbl(defl.LD_Ratio) / CDbl(defl.Allowable_LD)
    End If
End Function


Private Function ComputeCrackUtilization(ByRef cr As CrackWidthResult) As Double
    ' Compute crack width utilization as Wcr / limit.
    If cr.Limit_mm <= 0# Then
        ComputeCrackUtilization = 0#
    Else
        ComputeCrackUtilization = CDbl(cr.Wcr_mm) / CDbl(cr.Limit_mm)
    End If
End Function


Private Function MaxOf4(ByVal a As Double, ByVal b As Double, ByVal c As Double, ByVal d As Double) As Double
    Dim result As Double
    result = a
    If b > result Then result = b
    If c > result Then result = c
    If d > result Then result = d
    MaxOf4 = result
End Function


' =============================================================================
' Main Compliance Check Function
' =============================================================================

Public Function Compliance_CheckCase( _
    ByVal case_id As String, _
    ByVal mu_knm As Double, _
    ByVal vu_kn As Double, _
    ByVal b_mm As Double, _
    ByVal D_mm As Double, _
    ByVal d_mm As Double, _
    ByVal fck_nmm2 As Double, _
    ByVal fy_nmm2 As Double, _
    Optional ByVal d_dash_mm As Double = 50#, _
    Optional ByVal asv_mm2 As Double = 100#, _
    Optional ByVal pt_percent As Variant, _
    Optional ByVal check_deflection As Boolean = False, _
    Optional ByVal span_mm As Double = 0#, _
    Optional ByVal support_condition As String = "simply_supported", _
    Optional ByVal check_crack As Boolean = False, _
    Optional ByVal exposure_class As String = "moderate" _
) As ComplianceCaseResult
    ' Run a single compliance case.
    '
    ' Units:
    ' - Mu: kN·m (factored)
    ' - Vu: kN (factored)
    ' - All dimensions: mm
    ' - fck, fy: N/mm²
    '
    ' Returns:
    '     ComplianceCaseResult with all sub-checks and utilizations.

    Dim result As ComplianceCaseResult
    Dim failed As String
    Dim assumptions As String
    Dim pt_for_shear As Double

    result.case_id = case_id
    result.mu_knm = mu_knm
    result.vu_kn = vu_kn

    ' ----- Flexure Check -----
    result.flexure = M06_Flexure.DesignDoublyReinforced( _
        b_mm, d_mm, d_dash_mm, D_mm, mu_knm, fck_nmm2, fy_nmm2)

    ' ----- Determine pt for shear lookup -----
    If IsMissing(pt_percent) Or IsEmpty(pt_percent) Then
        ' Compute from flexure Ast
        If result.flexure.Ast_Required > 0# And CDbl(b_mm) * CDbl(d_mm) > 0# Then
            pt_for_shear = (result.flexure.Ast_Required * 100#) / (CDbl(b_mm) * CDbl(d_mm))
            assumptions = "pt computed from flexure Ast"
        Else
            pt_for_shear = 0#
            assumptions = "pt=0 (not provided)"
        End If
    Else
        pt_for_shear = CDbl(pt_percent)
    End If

    ' ----- Shear Check -----
    result.shear = M07_Shear.DesignShear( _
        vu_kn, b_mm, d_mm, fck_nmm2, fy_nmm2, asv_mm2, pt_for_shear)

    ' ----- Deflection Check (optional) -----
    If check_deflection And span_mm > 0# Then
        result.deflection = M17_Serviceability.Check_Deflection_SpanDepth( _
            span_mm, d_mm, support_condition)
    Else
        ' Initialize with OK defaults
        result.deflection.IsOK = True
        result.deflection.Remarks = "Not checked"
        result.deflection.LD_Ratio = 0#
        result.deflection.Allowable_LD = 999#
    End If

    ' ----- Crack Width Check (optional) -----
    If check_crack Then
        result.crack = M17_Serviceability.Check_CrackWidth( _
            b_mm, D_mm, d_mm, exposure_class)
    Else
        ' Initialize with OK defaults
        result.crack.IsOK = True
        result.crack.Remarks = "Not checked"
        result.crack.Wcr_mm = 0#
        result.crack.Limit_mm = 0.3
    End If

    ' ----- Compute Utilizations -----
    result.util_flexure = ComputeFlexureUtilization(mu_knm, result.flexure)
    result.util_shear = ComputeShearUtilization(result.shear)
    result.util_deflection = ComputeDeflectionUtilization(result.deflection)
    result.util_crack = ComputeCrackUtilization(result.crack)

    result.governing_utilization = MaxOf4( _
        result.util_flexure, result.util_shear, _
        result.util_deflection, result.util_crack)

    ' ----- Determine Pass/Fail -----
    failed = ""
    If Not result.flexure.IsSafe Then
        failed = AddToList(failed, "flexure")
    End If
    If Not result.shear.IsSafe Then
        failed = AddToList(failed, "shear")
    End If
    If check_deflection And Not result.deflection.IsOK Then
        failed = AddToList(failed, "deflection")
    End If
    If check_crack And Not result.crack.IsOK Then
        failed = AddToList(failed, "crack_width")
    End If

    result.failed_checks = failed
    result.is_ok = (Len(failed) = 0)

    If result.is_ok Then
        result.remarks = "OK"
    Else
        result.remarks = "FAIL: " & failed
    End If

    If Len(assumptions) > 0 Then
        result.remarks = result.remarks & " | " & assumptions
    End If

    Compliance_CheckCase = result
End Function


Private Function AddToList(ByVal current As String, ByVal item As String) As String
    If Len(current) = 0 Then
        AddToList = item
    Else
        AddToList = current & "," & item
    End If
End Function


' =============================================================================
' Multi-Case Report
' =============================================================================

Public Function Compliance_CheckMultipleCases( _
    ByRef cases() As ComplianceCaseResult _
) As ComplianceReport
    ' Aggregate multiple case results into a report.
    '
    ' Governing case is the one with highest utilization.
    ' Ties broken by case order (first wins).

    Dim report As ComplianceReport
    Dim i As Long
    Dim lowerBound As Long
    Dim upperBound As Long
    Dim maxUtil As Double

    ' Handle empty array
    On Error Resume Next
    lowerBound = LBound(cases)
    upperBound = UBound(cases)
    If Err.Number <> 0 Then
        On Error GoTo 0
        report.case_count = 0
        report.overall_is_ok = True
        report.remarks = "No cases provided"
        Compliance_CheckMultipleCases = report
        Exit Function
    End If
    On Error GoTo 0

    report.case_count = upperBound - lowerBound + 1
    report.cases_ok = 0
    report.cases_failed = 0
    maxUtil = -1#

    For i = lowerBound To upperBound
        If cases(i).is_ok Then
            report.cases_ok = report.cases_ok + 1
        Else
            report.cases_failed = report.cases_failed + 1
        End If

        ' Track governing case
        If cases(i).governing_utilization > maxUtil Then
            maxUtil = cases(i).governing_utilization
            report.governing_case_id = cases(i).case_id
            report.governing_utilization = maxUtil
        End If
    Next i

    report.overall_is_ok = (report.cases_failed = 0)

    If report.overall_is_ok Then
        report.remarks = "All " & CStr(report.cases_ok) & " cases OK"
    Else
        report.remarks = CStr(report.cases_failed) & " of " & CStr(report.case_count) & " cases failed"
    End If

    Compliance_CheckMultipleCases = report
End Function


' =============================================================================
' UDF Wrappers (for Excel)
' =============================================================================

Public Function IS456_ComplianceCheck( _
    ByVal mu_knm As Double, _
    ByVal vu_kn As Double, _
    ByVal b_mm As Double, _
    ByVal D_mm As Double, _
    ByVal d_mm As Double, _
    ByVal fck As Double, _
    ByVal fy As Double _
) As String
    ' Excel UDF: Quick compliance check.
    ' Returns "OK" or "FAIL: <reasons>"

    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("UDF", mu_knm, vu_kn, b_mm, D_mm, d_mm, fck, fy)
    IS456_ComplianceCheck = result.remarks
End Function


Public Function IS456_Utilization( _
    ByVal mu_knm As Double, _
    ByVal vu_kn As Double, _
    ByVal b_mm As Double, _
    ByVal D_mm As Double, _
    ByVal d_mm As Double, _
    ByVal fck As Double, _
    ByVal fy As Double _
) As Double
    ' Excel UDF: Get governing utilization ratio.
    ' Returns max of all check utilizations (< 1.0 means OK).

    Dim result As ComplianceCaseResult
    result = Compliance_CheckCase("UDF", mu_knm, vu_kn, b_mm, D_mm, d_mm, fck, fy)
    IS456_Utilization = result.governing_utilization
End Function
