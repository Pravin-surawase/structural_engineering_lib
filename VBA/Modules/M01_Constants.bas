Attribute VB_Name = "M01_Constants"
Option Explicit

' ==============================================================================
' Module:       M01_Constants
' Description:  Global constants for IS 456:2000 implementation
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Mathematical Constants
Public Const PI As Double = 3.14159265358979

' Material Safety Factors (IS 456:2000, Cl. 36.4.2)
Public Const GAMMA_C As Double = 1.5    ' Partial safety factor for concrete
Public Const GAMMA_S As Double = 1.15   ' Partial safety factor for steel

' Design Constants
Public Const MIN_ECCENTRICITY_RATIO As Double = 0.05 ' min e = L/500 + D/30, subject to min 20mm. Used in column design mostly.
Public Const MODULUS_ELASTICITY_STEEL As Double = 200000 ' N/mm^2 (Es)

' Error Handling Constants
Public Const ERR_INVALID_INPUT As Long = 1001
Public Const ERR_CALCULATION_FAILURE As Long = 1002
