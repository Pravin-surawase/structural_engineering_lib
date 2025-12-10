Attribute VB_Name = "M04_Utilities"
Option Explicit

' ==============================================================================
' Module:       M04_Utilities
' Description:  Helper functions (Interpolation, Rounding, Validation)
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Linear Interpolation
Public Function LinearInterp(ByVal X As Double, ByVal x1 As Double, ByVal y1 As Double, ByVal x2 As Double, ByVal y2 As Double) As Double
    ' y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    If (x2 - x1) = 0 Then
        LinearInterp = y1
    Else
        LinearInterp = y1 + (X - x1) * (y2 - y1) / (x2 - x1)
    End If
End Function

' Rounding function (Standard arithmetic rounding)
Public Function RoundTo(ByVal Value As Double, ByVal Digits As Integer) As Double
    RoundTo = Round(Value, Digits)
End Function
