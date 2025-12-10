Attribute VB_Name = "M05_Materials"
Option Explicit

' ==============================================================================
' Module:       M05_Materials
' Description:  Material properties and derived constants (fck, fy related)
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Get Xu,max/d ratio based on steel grade (IS 456 Cl. 38.1)
Public Function Get_XuMax_d(ByVal fy As Double) As Double
    Select Case fy
        Case 250: Get_XuMax_d = 0.53
        Case 415: Get_XuMax_d = 0.48
        Case 500: Get_XuMax_d = 0.46
        Case Else
            ' For other grades, use formula: 700 / (1100 + 0.87*fy)
            Get_XuMax_d = 700 / (1100 + (0.87 * fy))
    End Select
End Function

' Modulus of Elasticity of Concrete (IS 456 Cl. 6.2.3.1)
' Ec = 5000 * sqrt(fck)
Public Function Get_Ec(ByVal fck As Double) As Double
    If fck < 0 Then Get_Ec = 0 Else Get_Ec = 5000 * Sqr(fck)
End Function

' Flexural Strength of Concrete (IS 456 Cl. 6.2.2)
' fcr = 0.7 * sqrt(fck)
Public Function Get_Fcr(ByVal fck As Double) As Double
    If fck < 0 Then Get_Fcr = 0 Else Get_Fcr = 0.7 * Sqr(fck)
End Function

