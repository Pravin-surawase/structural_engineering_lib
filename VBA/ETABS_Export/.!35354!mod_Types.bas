Attribute VB_Name = "mod_Types"
Option Explicit

'==============================================================================
' Type Definitions Module
' Common data structures used across modules
'==============================================================================

' Unit conversion factors
Public Type UnitConversion
    ForceUnit As String         ' "kN", "kip", "N", "lb"
    LengthUnit As String        ' "mm", "m", "in", "ft"
    ForceToKN As Double         ' Conversion factor to kN
    LengthToMM As Double        ' Conversion factor to mm
