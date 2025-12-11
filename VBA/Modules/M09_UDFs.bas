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

' Wrapper for Flanged Mu_lim (Returns kN-m)
Public Function IS456_MuLim_Flanged(ByVal bw As Double, ByVal bf As Double, ByVal d As Double, ByVal Df As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    IS456_MuLim_Flanged = M06_Flexure.Calculate_Mu_Lim_Flanged(bw, bf, d, Df, fck, fy)
    Exit Function
ErrHandler:
    IS456_MuLim_Flanged = CVErr(xlErrValue)
End Function

' Wrapper for Rectangular Beam Design (Singly or Doubly)
' Returns 1x4 Array: [Ast_Req, Asc_Req, Xu, Status_String]
Public Function IS456_Design_Rectangular(ByVal b As Double, ByVal d As Double, ByVal d_dash As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    res = M06_Flexure.Design_Doubly_Reinforced(b, d, d_dash, D_total, Mu_kNm, fck, fy)
    
    Dim output(1 To 4) As Variant
    If res.IsSafe Then
        output(1) = res.Ast_Required
        output(2) = res.Asc_Required
        output(3) = res.Xu
        output(4) = "Safe"
    Else
        output(1) = 0
        output(2) = 0
        output(3) = res.Xu
        output(4) = res.ErrorMessage
    End If
    
    IS456_Design_Rectangular = output
    Exit Function
ErrHandler:
    IS456_Design_Rectangular = CVErr(xlErrValue)
End Function

' Wrapper for Flanged Beam Design
' Returns 1x4 Array: [Ast_Req, Asc_Req, Xu, Status_String]
Public Function IS456_Design_Flanged(ByVal bw As Double, ByVal bf As Double, ByVal d As Double, ByVal Df As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double, Optional ByVal d_dash As Double = 50) As Variant
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    res = M06_Flexure.Design_Flanged_Beam(bw, bf, d, Df, D_total, Mu_kNm, fck, fy, d_dash)
    
    Dim output(1 To 4) As Variant
    If res.IsSafe Then
        output(1) = res.Ast_Required
        output(2) = res.Asc_Required
        output(3) = res.Xu
        output(4) = "Safe"
    Else
        output(1) = 0
        output(2) = 0
        output(3) = res.Xu
        output(4) = res.ErrorMessage
    End If
    
    IS456_Design_Flanged = output
    Exit Function
ErrHandler:
    IS456_Design_Flanged = CVErr(xlErrValue)
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

' Wrapper for Ductile Detailing Check (IS 13920)
' Returns String: "Compliant" or error message
Public Function IS456_Check_Ductility(ByVal b As Double, ByVal D_overall As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double, ByVal min_long_bar_dia As Double) As Variant
    On Error GoTo ErrHandler
    Dim res As DuctileBeamResult
    res = M10_Ductile.Check_Beam_Ductility(b, D_overall, d, fck, fy, min_long_bar_dia)
    
    IS456_Check_Ductility = res.Remarks
    Exit Function
ErrHandler:
    IS456_Check_Ductility = CVErr(xlErrValue)
End Function

