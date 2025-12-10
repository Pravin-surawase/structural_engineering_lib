Attribute VB_Name = "M06_Flexure"
Option Explicit

' ==============================================================================
' Module:       M06_Flexure
' Description:  Flexural design and analysis functions (Singly/Doubly reinforced)
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Calculate Limiting Moment of Resistance (Returns kN-m)
Public Function Calculate_Mu_Lim(ByVal b As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double) As Double
    Dim xu_max_d As Double
    xu_max_d = M05_Materials.Get_XuMax_d(fy)
    
    ' Mu_lim = 0.36 * (xu_max/d) * (1 - 0.42 * (xu_max/d)) * b * d^2 * fck
    Dim k As Double
    k = 0.36 * xu_max_d * (1 - 0.42 * xu_max_d)
    
    Dim Mu_lim_Nmm As Double
    Mu_lim_Nmm = k * fck * b * d * d
    
    Calculate_Mu_Lim = Mu_lim_Nmm / 1000000# ' Convert back to kN-m
End Function

' Calculate Ast Required for Singly Reinforced Section (Returns mm^2)
' Mu in kN-m
' Returns -1 if section is over-reinforced (Mu > Mu_lim)
Public Function Calculate_Ast_Required(ByVal b As Double, ByVal d As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As Double
    Dim Mu_Nmm As Double
    Mu_Nmm = Abs(Mu_kNm) * 1000000#
    
    Dim Mu_lim_kNm As Double
    Mu_lim_kNm = Calculate_Mu_Lim(b, d, fck, fy)
    
    If Abs(Mu_kNm) > Mu_lim_kNm Then
        Calculate_Ast_Required = -1
        Exit Function
    End If
    
    ' Ast = (0.5 * fck / fy) * (1 - Sqr(1 - (4.6 * Mu / (fck * b * d^2)))) * b * d
    Dim term1 As Double
    term1 = 0.5 * fck / fy
    
    Dim term2 As Double
    term2 = (4.6 * Mu_Nmm) / (fck * b * d * d)
    
    ' Safety clamp for precision issues when Mu ~= Mu_lim
    If term2 > 1# Then term2 = 1#
    
    Calculate_Ast_Required = term1 * (1# - Sqr(1# - term2)) * b * d
End Function

' Main Design Function for Singly Reinforced Beam
Public Function Design_Singly_Reinforced(ByVal b As Double, ByVal d As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As FlexureResult
    Dim res As FlexureResult
    
    ' 1. Calculate Mu_lim
    Dim Mu_lim As Double
    Mu_lim = Calculate_Mu_Lim(b, d, fck, fy)
    res.Mu = Mu_lim ' We return Mu_lim as the capacity limit
    
    res.Xu_max = M05_Materials.Get_XuMax_d(fy) * d
    
    ' 2. Check if Doubly Reinforced Needed
    If Abs(Mu_kNm) > Mu_lim Then
        res.SectionType = OverReinforced
        res.IsSafe = False
        res.ErrorMessage = "Mu exceeds Mu_lim. Doubly reinforced section required."
        res.Asc_Required = 0
        res.Pt_Provided = 0
        res.Xu = res.Xu_max ' Limiting depth
    Else
        res.SectionType = UnderReinforced
        res.IsSafe = True
        
        ' 3. Calculate Ast
        Dim Ast_calc As Double
        Ast_calc = Calculate_Ast_Required(b, d, Mu_kNm, fck, fy)
        
        ' 4. Check Minimum Steel (Cl. 26.5.1.1)
        Dim Ast_min As Double
        Ast_min = 0.85 * b * d / fy
        
        If Ast_calc < Ast_min Then
            res.Asc_Required = Ast_min
            res.ErrorMessage = "Minimum steel provided."
        Else
            res.Asc_Required = Ast_calc
        End If
        
        ' 5. Check Maximum Steel (Cl. 26.5.1.2)
        Dim Ast_max As Double
        Ast_max = 0.04 * b * D_total
        
        If res.Asc_Required > Ast_max Then
            res.IsSafe = False
            res.ErrorMessage = "Ast exceeds maximum limit (4% bD)."
        End If
        
        ' 6. Calculate Pt
        res.Pt_Provided = (res.Asc_Required * 100#) / (b * d)
        
        ' 7. Calculate actual Xu
        ' Xu = (0.87 * fy * Ast) / (0.36 * fck * b)
        res.Xu = (0.87 * fy * res.Asc_Required) / (0.36 * fck * b)
    End If
    
    Design_Singly_Reinforced = res
End Function

