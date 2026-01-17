Attribute VB_Name = "M17_Serviceability"
Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

' ==============================================================================
' Module:       M17_Serviceability
' Description:  Serviceability checks (Deflection + Crack Width) — v0.8 Level A
' Version:      0.8.0
' ==============================================================================

' Design constraints:
' - Deterministic outputs.
' - Units explicit (mm, N/mm²).
' - No silent defaults: assumed values are recorded in Assumptions.

Private Const DEFAULT_ES_NMM2 As Double = 200000#

Private Function _AppendAssumption(ByVal current As String, ByVal note As String) As String
    If Len(current) = 0 Then
        _AppendAssumption = note
    Else
        _AppendAssumption = current & " | " & note
    End If
End Function

Private Function _NormalizeSupport(ByVal support_condition As String, ByRef assumptions As String) As SupportCondition
    Dim s As String
    s = LCase$(Trim$(support_condition))

    Select Case s
        Case "cantilever", "cant"
            _NormalizeSupport = SupportCondition.Cantilever
        Case "simply_supported", "simply", "ss"
            _NormalizeSupport = SupportCondition.SimplySupported
        Case "continuous", "cont"
            _NormalizeSupport = SupportCondition.Continuous
        Case Else
            _NormalizeSupport = SupportCondition.SimplySupported
            assumptions = _AppendAssumption(assumptions, "Unknown support condition '" & support_condition & "'. Defaulted to SimplySupported.")
    End Select
End Function

Private Function _DefaultBaseAllowableLD(ByVal support As SupportCondition) As Double
    Select Case support
        Case SupportCondition.Cantilever
            _DefaultBaseAllowableLD = 7#
        Case SupportCondition.SimplySupported
            _DefaultBaseAllowableLD = 20#
        Case SupportCondition.Continuous
            _DefaultBaseAllowableLD = 26#
        Case Else
            _DefaultBaseAllowableLD = 20#
    End Select
End Function

Public Function Check_Deflection_SpanDepth(
    ByVal span_mm As Double,
    ByVal d_mm As Double,
    Optional ByVal support_condition As String = "simply_supported",
    Optional ByVal base_allowable_ld As Variant,
    Optional ByVal mf_tension_steel As Variant,
    Optional ByVal mf_compression_steel As Variant,
    Optional ByVal mf_flanged As Variant
) As DeflectionResult

    Dim res As DeflectionResult
    Dim assumptions As String

    If span_mm <= 0# Or d_mm <= 0# Then
        res.IsOK = False
        res.Remarks = "Invalid input: span_mm and d_mm must be > 0."
        res.Assumptions = "Invalid inputs provided"
        Check_Deflection_SpanDepth = res
        Exit Function
    End If

    res.Support = _NormalizeSupport(support_condition, assumptions)

    If IsMissing(base_allowable_ld) Or IsEmpty(base_allowable_ld) Then
        res.BaseAllowable_LD = _DefaultBaseAllowableLD(res.Support)
        assumptions = _AppendAssumption(assumptions, "Used default base allowable L/d (" & CStr(res.BaseAllowable_LD) & ").")
    Else
        res.BaseAllowable_LD = CDbl(base_allowable_ld)
    End If

    If IsMissing(mf_tension_steel) Or IsEmpty(mf_tension_steel) Then
        res.MF_TensionSteel = 1#
        assumptions = _AppendAssumption(assumptions, "Assumed mf_tension_steel=1.0 (not provided).")
    Else
        res.MF_TensionSteel = CDbl(mf_tension_steel)
    End If

    If IsMissing(mf_compression_steel) Or IsEmpty(mf_compression_steel) Then
        res.MF_CompressionSteel = 1#
        assumptions = _AppendAssumption(assumptions, "Assumed mf_compression_steel=1.0 (not provided).")
    Else
        res.MF_CompressionSteel = CDbl(mf_compression_steel)
    End If

    If IsMissing(mf_flanged) Or IsEmpty(mf_flanged) Then
        res.MF_Flanged = 1#
        assumptions = _AppendAssumption(assumptions, "Assumed mf_flanged=1.0 (not provided).")
    Else
        res.MF_Flanged = CDbl(mf_flanged)
    End If

    res.LD_Ratio = span_mm / d_mm
    res.Allowable_LD = res.BaseAllowable_LD * res.MF_TensionSteel * res.MF_CompressionSteel * res.MF_Flanged

    res.IsOK = (res.LD_Ratio <= res.Allowable_LD)
    If res.IsOK Then
        res.Remarks = "OK: L/d=" & Format$(res.LD_Ratio, "0.000") & " ≤ allowable=" & Format$(res.Allowable_LD, "0.000")
    Else
        res.Remarks = "NOT OK: L/d=" & Format$(res.LD_Ratio, "0.000") & " > allowable=" & Format$(res.Allowable_LD, "0.000")
    End If

    res.Assumptions = assumptions
    Check_Deflection_SpanDepth = res
End Function

Private Function _NormalizeExposure(ByVal exposure_class As String, ByRef assumptions As String) As ExposureClass
    Dim s As String
    s = LCase$(Trim$(exposure_class))

    Select Case s
        Case "mild"
            _NormalizeExposure = ExposureClass.Mild
        Case "moderate", "mod"
            _NormalizeExposure = ExposureClass.Moderate
        Case "severe"
            _NormalizeExposure = ExposureClass.Severe
        Case "very severe", "very_severe", "very-severe", "vs"
            _NormalizeExposure = ExposureClass.VerySevere
        Case Else
            _NormalizeExposure = ExposureClass.Moderate
            assumptions = _AppendAssumption(assumptions, "Unknown exposure class '" & exposure_class & "'. Defaulted to Moderate.")
    End Select
End Function

Private Function _DefaultCrackLimit(ByVal exposure As ExposureClass) As Double
    Select Case exposure
        Case ExposureClass.Mild
            _DefaultCrackLimit = 0.3
        Case ExposureClass.Moderate
            _DefaultCrackLimit = 0.3
        Case ExposureClass.Severe
            _DefaultCrackLimit = 0.2
        Case ExposureClass.VerySevere
            _DefaultCrackLimit = 0.2
        Case Else
            _DefaultCrackLimit = 0.3
    End Select
End Function

Public Function Check_CrackWidth(
    Optional ByVal exposure_class As String = "moderate",
    Optional ByVal limit_mm As Variant,
    Optional ByVal acr_mm As Variant,
    Optional ByVal cmin_mm As Variant,
    Optional ByVal h_mm As Variant,
    Optional ByVal x_mm As Variant,
    Optional ByVal epsilon_m As Variant,
    Optional ByVal fs_service_nmm2 As Variant,
    Optional ByVal es_nmm2 As Double = DEFAULT_ES_NMM2
) As CrackWidthResult

    Dim res As CrackWidthResult
    Dim assumptions As String
    Dim denom As Double

    res.Exposure = _NormalizeExposure(exposure_class, assumptions)

    If IsMissing(limit_mm) Or IsEmpty(limit_mm) Then
        res.Limit_mm = _DefaultCrackLimit(res.Exposure)
        assumptions = _AppendAssumption(assumptions, "Used default crack width limit (" & CStr(res.Limit_mm) & " mm).")
    Else
        res.Limit_mm = CDbl(limit_mm)
    End If

    If IsMissing(epsilon_m) Or IsEmpty(epsilon_m) Then
        If IsMissing(fs_service_nmm2) Or IsEmpty(fs_service_nmm2) Then
            res.IsOK = False
            res.Remarks = "Missing epsilon_m or fs_service_nmm2 to estimate service steel strain."
            res.Assumptions = assumptions
            Check_CrackWidth = res
            Exit Function
        End If
        res.Epsilon_m = CDbl(fs_service_nmm2) / es_nmm2
        assumptions = _AppendAssumption(assumptions, "Estimated epsilon_m = fs_service_nmm2 / es_nmm2.")
    Else
        res.Epsilon_m = CDbl(epsilon_m)
    End If

    If IsMissing(acr_mm) Or IsEmpty(acr_mm) Then
        res.IsOK = False
        res.Remarks = "Missing required inputs for crack width calculation: acr_mm."
        res.Assumptions = assumptions
        Check_CrackWidth = res
        Exit Function
    End If
    If IsMissing(cmin_mm) Or IsEmpty(cmin_mm) Then
        res.IsOK = False
        res.Remarks = "Missing required inputs for crack width calculation: cmin_mm."
        res.Assumptions = assumptions
        Check_CrackWidth = res
        Exit Function
    End If
    If IsMissing(h_mm) Or IsEmpty(h_mm) Then
        res.IsOK = False
        res.Remarks = "Missing required inputs for crack width calculation: h_mm."
        res.Assumptions = assumptions
        Check_CrackWidth = res
        Exit Function
    End If
    If IsMissing(x_mm) Or IsEmpty(x_mm) Then
        res.IsOK = False
        res.Remarks = "Missing required inputs for crack width calculation: x_mm."
        res.Assumptions = assumptions
        Check_CrackWidth = res
        Exit Function
    End If

    res.Acr_mm = CDbl(acr_mm)
    res.Cmin_mm = CDbl(cmin_mm)
    res.h_mm = CDbl(h_mm)
    res.x_mm = CDbl(x_mm)

    If res.h_mm <= res.x_mm Then
        res.IsOK = False
        res.Remarks = "Invalid geometry: require h_mm > x_mm."
        res.Assumptions = assumptions
        Check_CrackWidth = res
        Exit Function
    End If

    denom = 1# + 2# * ((res.Acr_mm - res.Cmin_mm) / (res.h_mm - res.x_mm))
    res.Denom = denom

    If denom <= 0# Then
        res.IsOK = False
        res.Remarks = "Invalid computed denominator in crack width formula (<= 0)."
        res.Assumptions = assumptions
        Check_CrackWidth = res
        Exit Function
    End If

    res.Wcr_mm = 3# * res.Acr_mm * res.Epsilon_m / denom

    res.IsOK = (res.Wcr_mm <= res.Limit_mm)
    If res.IsOK Then
        res.Remarks = "OK: wcr=" & Format$(res.Wcr_mm, "0.0000") & " mm ≤ limit=" & Format$(res.Limit_mm, "0.0000") & " mm"
    Else
        res.Remarks = "NOT OK: wcr=" & Format$(res.Wcr_mm, "0.0000") & " mm > limit=" & Format$(res.Limit_mm, "0.0000") & " mm"
    End If

    res.Assumptions = assumptions
    Check_CrackWidth = res
End Function


' ==============================================================================
' Slenderness Check (IS 456 Cl 23.3) - v0.18+
' ==============================================================================

' Slenderness limits per beam type (IS 456 Cl 23.3)
Private Const SLENDERNESS_LIMIT_SIMPLY_SUPPORTED As Double = 60#
Private Const SLENDERNESS_LIMIT_CONTINUOUS As Double = 60#
Private Const SLENDERNESS_LIMIT_CANTILEVER As Double = 25#
Private Const DEPTH_WIDTH_WARNING As Double = 4#

' ------------------------------------------------------------------------------
' Function:     Get_Slenderness_Limit
' Description:  Returns slenderness limit (l_eff/b) for beam type
' Args:         support - SupportCondition enum
' Returns:      Slenderness limit per IS 456 Cl 23.3
' Reference:    IS 456:2000 Cl 23.3
' ------------------------------------------------------------------------------
Public Function Get_Slenderness_Limit(ByVal support As SupportCondition) As Double
    Select Case support
        Case SupportCondition.Cantilever
            Get_Slenderness_Limit = SLENDERNESS_LIMIT_CANTILEVER
        Case SupportCondition.SimplySupported
            Get_Slenderness_Limit = SLENDERNESS_LIMIT_SIMPLY_SUPPORTED
        Case SupportCondition.Continuous
            Get_Slenderness_Limit = SLENDERNESS_LIMIT_CONTINUOUS
        Case Else
            Get_Slenderness_Limit = SLENDERNESS_LIMIT_SIMPLY_SUPPORTED
    End Select
End Function


' ------------------------------------------------------------------------------
' Function:     Calculate_Slenderness_Ratio
' Description:  Calculates slenderness ratio l_eff/b
' Args:         l_eff_mm - Effective unsupported length (mm)
'               b_mm - Width of compression flange (mm)
' Returns:      Slenderness ratio (dimensionless)
' Reference:    IS 456:2000 Cl 23.3
' ------------------------------------------------------------------------------
Public Function Calculate_Slenderness_Ratio(ByVal l_eff_mm As Double, _
                                            ByVal b_mm As Double) As Double
    If l_eff_mm <= 0# Or b_mm <= 0# Then
        Calculate_Slenderness_Ratio = 0#
        Exit Function
    End If

    Calculate_Slenderness_Ratio = l_eff_mm / b_mm
End Function


' ------------------------------------------------------------------------------
' Function:     Check_Beam_Slenderness
' Description:  Comprehensive slenderness check per IS 456 Cl 23.3
' Args:         b_mm - Beam width (mm)
'               D_mm - Overall beam depth (mm)
'               l_eff_mm - Effective unsupported length (mm)
'               support_condition - "simply_supported", "continuous", "cantilever"
'               has_lateral_restraint - True if slab on top restrains laterally
' Returns:      SlendernessResult UDT
' Reference:    IS 456:2000 Cl 23.3
' ------------------------------------------------------------------------------
Public Function Check_Beam_Slenderness(ByVal b_mm As Double, _
                                       ByVal D_mm As Double, _
                                       ByVal l_eff_mm As Double, _
                                       Optional ByVal support_condition As String = "simply_supported", _
                                       Optional ByVal has_lateral_restraint As Boolean = False) As SlendernessResult

    Dim res As SlendernessResult
    Dim assumptions As String
    Dim support As SupportCondition

    ' Validate inputs
    If b_mm <= 0# Or D_mm <= 0# Or l_eff_mm <= 0# Then
        res.IsOK = False
        res.Remarks = "Invalid input: b_mm, D_mm, and l_eff_mm must be > 0."
        res.Assumptions = "Invalid inputs provided"
        Check_Beam_Slenderness = res
        Exit Function
    End If

    ' Normalize support condition
    support = _NormalizeSupport(support_condition, assumptions)

    ' Calculate ratios
    res.SlendernessRatio = l_eff_mm / b_mm
    res.SlendernessLimit = Get_Slenderness_Limit(support)
    res.DepthWidthRatio = D_mm / b_mm
    res.Utilization = res.SlendernessRatio / res.SlendernessLimit

    ' Check lateral restraint
    If has_lateral_restraint Then
        assumptions = _AppendAssumption(assumptions, "Beam has lateral restraint (slab on top).")
        res.IsOK = True
        res.IsSlender = False
        res.Remarks = "OK: Laterally restrained beam"
        res.Assumptions = assumptions
        Check_Beam_Slenderness = res
        Exit Function
    End If

    ' Check slenderness
    res.IsOK = (res.SlendernessRatio <= res.SlendernessLimit)
    res.IsSlender = (res.Utilization > 0.8)

    ' Build remarks
    If res.IsOK Then
        res.Remarks = "OK: L/b=" & Format$(res.SlendernessRatio, "0.00") & _
                      " <= limit=" & CStr(res.SlendernessLimit)
    Else
        res.Remarks = "NOT OK: L/b=" & Format$(res.SlendernessRatio, "0.00") & _
                      " > limit=" & CStr(res.SlendernessLimit)
    End If

    ' Add warning for deep beams
    If res.DepthWidthRatio > DEPTH_WIDTH_WARNING Then
        res.Remarks = res.Remarks & " | Warning: D/b=" & Format$(res.DepthWidthRatio, "0.00") & _
                      " > " & CStr(DEPTH_WIDTH_WARNING) & " - consider lateral buckling"
    End If

    res.Assumptions = assumptions
    Check_Beam_Slenderness = res
End Function
