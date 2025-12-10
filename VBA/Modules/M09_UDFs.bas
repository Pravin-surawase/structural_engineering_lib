Attribute VB_Name = "M09_UDFs"
Option Explicit

' ==============================================================================
' Module:       M09_UDFs
' Description:  Excel User Defined Functions (Worksheet accessible)
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Wrapper for Mu_lim (Returns kN-m)
Public Function IS456_MuLim(ByVal b As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    IS456_MuLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    Exit Function
ErrHandler:
    IS456_MuLim = CVErr(xlErrValue)
End Function

' Wrapper for Ast Required (Returns mm^2 or String message)
Public Function IS456_AstRequired(ByVal b As Double, ByVal d As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As Double
    res = M06_Flexure.Calculate_Ast_Required(b, d, Mu_kNm, fck, fy)
    
    If res = -1 Then
        IS456_AstRequired = "Over-Reinforced"
    Else
        IS456_AstRequired = res
    End If
    Exit Function
ErrHandler:
    IS456_AstRequired = CVErr(xlErrValue)
End Function

' Wrapper for Shear Spacing (Returns mm or String message)
Public Function IS456_ShearSpacing(ByVal Vu_kN As Double, ByVal b As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double, ByVal Asv As Double, ByVal pt As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As ShearResult
    res = M07_Shear.Design_Shear(Vu_kN, b, d, fck, fy, Asv, pt)
    
    If Not res.IsSafe Then
        IS456_ShearSpacing = "Unsafe: " & res.Remarks
    Else
        IS456_ShearSpacing = res.Spacing
    End If
    Exit Function
ErrHandler:
    IS456_ShearSpacing = CVErr(xlErrValue)
End Function

' Wrapper for Tc (Table 19)
Public Function IS456_Tc(ByVal fck As Double, ByVal pt As Double) As Variant
    On Error GoTo ErrHandler
    IS456_Tc = M03_Tables.Get_Tc_Value(fck, pt)
    Exit Function
ErrHandler:
    IS456_Tc = CVErr(xlErrValue)
End Function

' Wrapper for Tc_max (Table 20)
Public Function IS456_TcMax(ByVal fck As Double) As Variant
    On Error GoTo ErrHandler
    IS456_TcMax = M03_Tables.Get_TcMax_Value(fck)
    Exit Function
ErrHandler:
    IS456_TcMax = CVErr(xlErrValue)
End Function

