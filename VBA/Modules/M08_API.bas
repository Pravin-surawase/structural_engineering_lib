Attribute VB_Name = "M08_API"
Option Explicit

' ==============================================================================
' Module:       M08_API
' Description:  Public facing API functions (Simplified wrappers)
' Version:      0.9.4
' License:      MIT
' ==============================================================================

Public Function Get_Library_Version() As String
    Get_Library_Version = "0.9.4"
End Function

'
' Serviceability (v0.8+) — public wrappers
'
Public Function Check_Deflection_SpanDepth(
    ByVal span_mm As Double,
    ByVal d_mm As Double,
    Optional ByVal support_condition As String = "simply_supported",
    Optional ByVal base_allowable_ld As Variant,
    Optional ByVal mf_tension_steel As Variant,
    Optional ByVal mf_compression_steel As Variant,
    Optional ByVal mf_flanged As Variant
) As DeflectionResult

    Check_Deflection_SpanDepth = M17_Serviceability.Check_Deflection_SpanDepth(
        span_mm:=span_mm,
        d_mm:=d_mm,
        support_condition:=support_condition,
        base_allowable_ld:=base_allowable_ld,
        mf_tension_steel:=mf_tension_steel,
        mf_compression_steel:=mf_compression_steel,
        mf_flanged:=mf_flanged
    )
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
    Optional ByVal es_nmm2 As Double = 200000#
) As CrackWidthResult

    Check_CrackWidth = M17_Serviceability.Check_CrackWidth(
        exposure_class:=exposure_class,
        limit_mm:=limit_mm,
        acr_mm:=acr_mm,
        cmin_mm:=cmin_mm,
        h_mm:=h_mm,
        x_mm:=x_mm,
        epsilon_m:=epsilon_m,
        fs_service_nmm2:=fs_service_nmm2,
        es_nmm2:=es_nmm2
    )
End Function

