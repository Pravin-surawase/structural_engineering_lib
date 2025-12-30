Attribute VB_Name = "M06_Flexure"
Option Explicit

' ==============================================================================
' Module:       M06_Flexure
' Description:  Flexural design and analysis functions (Singly/Doubly reinforced)
' Version:      1.0.01
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
    ' Force Double arithmetic for safety
    Mu_lim_Nmm = k * CDbl(fck) * CDbl(b) * CDbl(d) * CDbl(d)
    
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
    term2 = (4.6 * Mu_Nmm) / (CDbl(fck) * CDbl(b) * CDbl(d) * CDbl(d))
    
    ' Safety clamp for precision issues when Mu ~= Mu_lim
    If term2 > 1# Then term2 = 1#
    
    Calculate_Ast_Required = term1 * (1# - Sqr(1# - term2)) * CDbl(b) * CDbl(d)
End Function

' Calculate Effective Flange Width (IS 456 Cl 23.1.2)
' beam_type: "T", "L", or "RECTANGULAR"
Public Function Calculate_Effective_Flange_Width(ByVal bw As Double, _
                                                 ByVal span As Double, _
                                                 ByVal df As Double, _
                                                 ByVal overhang_left As Double, _
                                                 ByVal overhang_right As Double, _
                                                 ByVal beam_type As String) As Double
    Dim bt As String
    bt = UCase(Trim(beam_type))
    
    If bw <= 0# Or span <= 0# Or df <= 0# Then
        Err.Raise vbObjectError + 513, "Calculate_Effective_Flange_Width", _
            "bw, span, and df must be > 0."
    End If
    If overhang_left < 0# Or overhang_right < 0# Then
        Err.Raise vbObjectError + 513, "Calculate_Effective_Flange_Width", _
            "Flange overhangs must be >= 0."
    End If
    
    Dim bf_geom As Double
    bf_geom = CDbl(bw) + CDbl(overhang_left) + CDbl(overhang_right)
    
    If bf_geom < bw Then
        Err.Raise vbObjectError + 513, "Calculate_Effective_Flange_Width", _
            "Geometric flange width must be >= bw."
    End If
    
    If bt = "RECTANGULAR" Or bt = "RECT" Or bt = "R" Then
        If overhang_left > 0# Or overhang_right > 0# Then
            Err.Raise vbObjectError + 513, "Calculate_Effective_Flange_Width", _
                "Rectangular beam cannot have flange overhangs."
        End If
        Calculate_Effective_Flange_Width = bw
        Exit Function
    End If
    
    Dim bf_limit As Double
    If bt = "T" Or bt = "FLANGED_T" Or bt = "T_BEAM" Then
        bf_limit = CDbl(bw) + (CDbl(span) / 6#) + (6# * CDbl(df))
    ElseIf bt = "L" Or bt = "FLANGED_L" Or bt = "L_BEAM" Then
        bf_limit = CDbl(bw) + (CDbl(span) / 12#) + (3# * CDbl(df))
    Else
        Err.Raise vbObjectError + 513, "Calculate_Effective_Flange_Width", _
            "beam_type must be T or L."
    End If
    
    If bf_geom < bf_limit Then
        Calculate_Effective_Flange_Width = bf_geom
    Else
        Calculate_Effective_Flange_Width = bf_limit
    End If
End Function

' Main Design Function for Singly Reinforced Beam
Public Function Design_Singly_Reinforced(ByVal b As Double, ByVal d As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As FlexureResult
    Dim res As FlexureResult
    
    ' 1. Calculate Mu_lim
    Dim Mu_lim As Double
    Mu_lim = Calculate_Mu_Lim(b, d, fck, fy)
    res.Mu_Lim = Mu_lim ' We return Mu_lim as the capacity limit
    
    res.Xu_max = M05_Materials.Get_XuMax_d(fy) * d
    
    ' 2. Check if Doubly Reinforced Needed
    If Abs(Mu_kNm) > Mu_lim Then
        res.SectionType = OverReinforced
        res.IsSafe = False
        res.ErrorMessage = "Mu exceeds Mu_lim. Doubly reinforced section required."
        res.Ast_Required = 0#
        res.Asc_Required = 0#
        res.Pt_Provided = 0#
        res.Xu = res.Xu_max ' Limiting depth
    Else
        res.SectionType = UnderReinforced
        res.IsSafe = True
        
        ' 3. Calculate Ast
        Dim Ast_calc As Double
        Ast_calc = Calculate_Ast_Required(b, d, Mu_kNm, fck, fy)
        
        ' 4. Check Minimum Steel (Cl. 26.5.1.1)
        Dim Ast_min As Double
        Ast_min = 0.85 * CDbl(b) * CDbl(d) / CDbl(fy)
        
        If Ast_calc < Ast_min Then
            res.Ast_Required = Ast_min
            res.ErrorMessage = "Minimum steel provided."
        Else
            res.Ast_Required = Ast_calc
        End If
        
        ' 5. Check Maximum Steel (Cl. 26.5.1.2)
        Dim Ast_max As Double
        Ast_max = 0.04 * CDbl(b) * CDbl(D_total)
        
        If res.Ast_Required > Ast_max Then
            res.IsSafe = False
            res.ErrorMessage = "Ast exceeds maximum limit (4% bD)."
        End If
        
        ' Calculate Pt
        res.Pt_Provided = (res.Ast_Required * 100#) / (CDbl(b) * CDbl(d))
        
        ' Calculate actual Xu
        res.Xu = (0.87 * CDbl(fy) * res.Ast_Required) / (0.36 * CDbl(fck) * CDbl(b))
        
        res.Asc_Required = 0 ' Explicitly set to 0
    End If
    
    Design_Singly_Reinforced = res
End Function

' Main Design Function for Doubly Reinforced Beam (or Singly if Mu <= Mu_lim)
Public Function Design_Doubly_Reinforced(ByVal b As Double, ByVal d As Double, ByVal d_dash As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double) As FlexureResult
    Dim res As FlexureResult
    Dim Mu_abs As Double
    Mu_abs = Abs(Mu_kNm)
    
    ' 1. Calculate Mu_lim
    Dim Mu_lim As Double
    Mu_lim = Calculate_Mu_Lim(b, d, fck, fy)
    res.Mu_Lim = Mu_lim
    res.Xu_max = M05_Materials.Get_XuMax_d(fy) * d
    
    ' Case 1: Singly Reinforced
    If Mu_abs <= Mu_lim Then
        ' Inline Singly Reinforced Logic to avoid nested UDT return stack issues on Mac
        res.SectionType = UnderReinforced
        res.IsSafe = True
        
        ' Calculate Ast (Inlined logic to avoid function call overhead)
        Dim Ast_calc As Double
        ' Ast = (0.5 * fck / fy) * (1 - Sqr(1 - (4.6 * Mu / (fck * b * d^2)))) * b * d
        Dim term1_inline As Double
        term1_inline = 0.5 * fck / fy
        
        Dim Mu_Nmm_inline As Double
        Mu_Nmm_inline = Abs(Mu_kNm) * 1000000#
        
        Dim term2_inline As Double
        term2_inline = (4.6 * Mu_Nmm_inline) / (CDbl(fck) * CDbl(b) * CDbl(d) * CDbl(d))
        
        If term2_inline > 1# Then term2_inline = 1#
        
        Ast_calc = term1_inline * (1# - Sqr(1# - term2_inline)) * CDbl(b) * CDbl(d)
        
        ' Check Minimum Steel
        Dim Ast_min As Double
        Ast_min = 0.85 * CDbl(b) * CDbl(d) / CDbl(fy)
        
        If Ast_calc < Ast_min Then
            res.Ast_Required = Ast_min
            res.ErrorMessage = "Minimum steel provided."
        Else
            res.Ast_Required = Ast_calc
        End If
        
        ' Check Maximum Steel
        Dim Ast_max As Double
        Ast_max = 0.04 * CDbl(b) * CDbl(D_total)
        
        If res.Ast_Required > Ast_max Then
            res.IsSafe = False
            res.ErrorMessage = "Ast exceeds maximum limit (4% bD)."
        End If
        
        ' Calculate Pt
        res.Pt_Provided = (res.Ast_Required * 100#) / (CDbl(b) * CDbl(d))
        
        ' Calculate actual Xu
        res.Xu = (0.87 * CDbl(fy) * res.Ast_Required) / (0.36 * CDbl(fck) * CDbl(b))
        
        res.Asc_Required = 0
        Design_Doubly_Reinforced = res
        Exit Function
    End If
    
    ' Case 2: Doubly Reinforced
    res.SectionType = OverReinforced ' Using OverReinforced enum to signify Doubly Reinforced need
    
    ' 1. Calculate Mu2
    Dim Mu2_kNm As Double
    Mu2_kNm = Mu_abs - Mu_lim
    
    Dim Mu2_Nmm As Double
    Mu2_Nmm = Mu2_kNm * 1000000#
    
    ' 2. Calculate Strain in Compression Steel
    ' strain_sc = 0.0035 * (1 - d'/xu_max)
    Dim strain_sc As Double
    strain_sc = 0.0035 * (1# - d_dash / res.Xu_max)
    
    ' 3. Calculate Stress in Compression Steel (fsc)
    Dim fsc As Double
    fsc = M05_Materials.Get_Steel_Stress(strain_sc, fy)
    
    ' 4. Calculate Stress in Concrete at level of compression steel (fcc)
    Dim fcc As Double
    fcc = 0.446 * CDbl(fck)
    
    ' 5. Calculate Asc
    ' Mu2 = Asc * (fsc - fcc) * (d - d')
    Dim denom As Double
    denom = (fsc - fcc) * (d - d_dash)
    
    If denom <= 0 Then
        res.IsSafe = False
        res.ErrorMessage = "Invalid section geometry for doubly reinforced design."
        Design_Doubly_Reinforced = res
        Exit Function
    End If
    
    res.Asc_Required = Mu2_Nmm / denom
    
    ' 6. Calculate Total Ast
    ' Ast1 (for Mu_lim)
    Dim Ast1 As Double
    Ast1 = Calculate_Ast_Required(b, d, Mu_lim, fck, fy)
    
    ' Ast2 (for Mu2)
    ' Ast2 * 0.87 * fy = Asc * (fsc - fcc)
    Dim Ast2 As Double
    Ast2 = (res.Asc_Required * (fsc - fcc)) / (0.87 * CDbl(fy))
    
    res.Ast_Required = Ast1 + Ast2
    
    ' 7. Check Max Steel (Cl. 26.5.1.2)
    Ast_max = 0.04 * CDbl(b) * CDbl(D_total)
    
    res.IsSafe = True
    
    If res.Ast_Required > Ast_max Then
        res.IsSafe = False
        res.ErrorMessage = "Total Ast exceeds maximum limit (4% bD)."
    End If
    
    If res.Asc_Required > Ast_max Then
        res.IsSafe = False
        res.ErrorMessage = res.ErrorMessage & " Asc exceeds maximum limit."
    End If
    
    ' Calculate Pt
    res.Pt_Provided = (res.Ast_Required * 100#) / (CDbl(b) * CDbl(d))
    res.Xu = res.Xu_max
    
    Design_Doubly_Reinforced = res
End Function

' Calculate Limiting Moment of Resistance for Flanged Beam (T-Beam)
Public Function Calculate_Mu_Lim_Flanged(ByVal bw As Double, ByVal bf As Double, ByVal d As Double, ByVal Df As Double, ByVal fck As Double, ByVal fy As Double) As Double
    Dim xu_max As Double
    xu_max = M05_Materials.Get_XuMax_d(fy) * d
    
    Dim yf As Double
    If (Df / d) <= 0.2 Then
        yf = Df
    Else
        yf = 0.15 * xu_max + 0.65 * Df
        If yf > Df Then yf = Df
    End If
    
    Dim Mu_web_kNm As Double
    Mu_web_kNm = Calculate_Mu_Lim(bw, d, fck, fy)
    
    Dim C_flange As Double
    C_flange = 0.45 * fck * (bf - bw) * yf
    
    Dim M_flange_Nmm As Double
    M_flange_Nmm = C_flange * (d - yf / 2#)
    
    Calculate_Mu_Lim_Flanged = Mu_web_kNm + (M_flange_Nmm / 1000000#)
End Function

' Design Flanged Beam (T-Beam)
Public Function Design_Flanged_Beam(ByVal bw As Double, ByVal bf As Double, ByVal d As Double, ByVal Df As Double, ByVal D_total As Double, ByVal Mu_kNm As Double, ByVal fck As Double, ByVal fy As Double, Optional ByVal d_dash As Double = 50#) As FlexureResult
    Dim res As FlexureResult
    Dim Mu_abs As Double
    Mu_abs = Abs(Mu_kNm)
    
    ' 1. Check if Neutral Axis is in Flange
    Dim Mu_capacity_at_Df_Nmm As Double
    Mu_capacity_at_Df_Nmm = 0.36 * fck * bf * Df * (d - 0.42 * Df)
    
    Dim Mu_capacity_at_Df As Double
    Mu_capacity_at_Df = Mu_capacity_at_Df_Nmm / 1000000#
    
    If Mu_abs <= Mu_capacity_at_Df Then
        Design_Flanged_Beam = Design_Singly_Reinforced(bf, d, D_total, Mu_kNm, fck, fy)
        Exit Function
    End If
    
    ' 2. Neutral Axis in Web
    Dim Mu_lim_T As Double
    Mu_lim_T = Calculate_Mu_Lim_Flanged(bw, bf, d, Df, fck, fy)
    
    Dim xu_max As Double
    xu_max = M05_Materials.Get_XuMax_d(fy) * d
    
    If Mu_abs > Mu_lim_T Then
        ' Doubly Reinforced T-Beam
        Dim yf As Double
        If (Df / d) <= 0.2 Then
            yf = Df
        Else
            yf = 0.15 * xu_max + 0.65 * Df
            If yf > Df Then yf = Df
        End If
        
        Dim C_flange As Double
        C_flange = 0.45 * fck * (bf - bw) * yf
        
        Dim M_flange_Nmm As Double
        M_flange_Nmm = C_flange * (d - yf / 2#)
        
        Dim Mu_web_target As Double
        Mu_web_target = Mu_abs - (M_flange_Nmm / 1000000#)
        
        Dim web_res As FlexureResult
        web_res = Design_Doubly_Reinforced(bw, d, d_dash, D_total, Mu_web_target, fck, fy)
        
        Dim Ast_flange As Double
        Ast_flange = C_flange / (0.87 * fy)
        
        res = web_res
        res.Mu_Lim = Mu_lim_T
        res.Ast_Required = web_res.Ast_Required + Ast_flange
        res.Pt_Provided = (res.Ast_Required * 100#) / (bw * d)
        res.SectionType = OverReinforced
        
        Design_Flanged_Beam = res
        Exit Function
    End If
    
    ' 3. Singly Reinforced T-Beam
    ' Solver for Xu
    Dim low As Double, high As Double, mid As Double
    low = Df
    high = xu_max
    
    Dim Mu_target_Nmm As Double
    Mu_target_Nmm = Mu_abs * 1000000#
    
    Dim xu_sol As Double
    xu_sol = high
    
    Dim i As Long
    Dim M_mid As Double
    Dim yf_mid As Double
    Dim C_web As Double, M_web As Double
    Dim C_flange_mid As Double, M_flange_mid As Double
    
    For i = 1 To 50
        mid = (low + high) / 2#
        
        ' Calculate Moment at mid
        If (Df / d) <= 0.2 Then
            yf_mid = Df
        Else
            yf_mid = 0.15 * mid + 0.65 * Df
            If yf_mid > Df Then yf_mid = Df
        End If
        
        C_web = 0.36 * fck * bw * mid
        M_web = C_web * (d - 0.42 * mid)
        
        C_flange_mid = 0.45 * fck * (bf - bw) * yf_mid
        M_flange_mid = C_flange_mid * (d - yf_mid / 2#)
        
        M_mid = M_web + M_flange_mid
        
        If Abs(M_mid - Mu_target_Nmm) < 1000# Then
            xu_sol = mid
            Exit For
        End If
        
        If M_mid < Mu_target_Nmm Then
            low = mid
        Else
            high = mid
        End If
    Next i
    
    If i > 50 Then xu_sol = (low + high) / 2#
    
    ' Calculate Ast
    Dim yf_sol As Double
    If (Df / d) <= 0.2 Then
        yf_sol = Df
    Else
        yf_sol = 0.15 * xu_sol + 0.65 * Df
        If yf_sol > Df Then yf_sol = Df
    End If
    
    Dim C_total As Double
    C_total = (0.36 * fck * bw * xu_sol) + (0.45 * fck * (bf - bw) * yf_sol)
    
    Dim Ast_req As Double
    Ast_req = C_total / (0.87 * CDbl(fy))
    
    res.SectionType = UnderReinforced
    res.IsSafe = True
    res.Mu_Lim = Mu_lim_T
    res.Xu = xu_sol
    res.Xu_max = xu_max
    
    ' Check Minimum Steel (based on web width bw)
    Dim Ast_min As Double
    Ast_min = 0.85 * CDbl(bw) * CDbl(d) / CDbl(fy)
    
    If Ast_req < Ast_min Then
        res.Ast_Required = Ast_min
        res.ErrorMessage = "Minimum steel provided."
    Else
        res.Ast_Required = Ast_req
    End If
    
    ' Check Maximum Steel (4% of gross web area usually, but code says bD)
    ' Using bw * D_total for T-beams is conservative/standard practice for web congestion
    Dim Ast_max As Double
    Ast_max = 0.04 * CDbl(bw) * CDbl(D_total)
    
    If res.Ast_Required > Ast_max Then
        res.IsSafe = False
        res.ErrorMessage = "Ast exceeds maximum limit (4% bwD)."
    End If
    
    res.Pt_Provided = (res.Ast_Required * 100#) / (CDbl(bw) * CDbl(d))
    res.Asc_Required = 0
    
    Design_Flanged_Beam = res
End Function
