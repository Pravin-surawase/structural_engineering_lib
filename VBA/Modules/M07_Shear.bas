Attribute VB_Name = "M07_Shear"
Option Explicit

' ==============================================================================
' Module:       M07_Shear
' Description:  Shear design and analysis functions
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Calculate Nominal Shear Stress (N/mm^2)
Public Function Calculate_Tv(ByVal Vu_kN As Double, ByVal b As Double, ByVal d As Double) As Double
    If b * d = 0 Then
        Calculate_Tv = 0
    Else
        Calculate_Tv = (Abs(Vu_kN) * 1000#) / (b * d)
    End If
End Function

' Main Shear Design Function
' Vu_kN: Shear force in kN
' b, d: Dimensions in mm
' fck: Concrete grade
' fy: Stirrup steel grade
' Asv: Area of stirrup legs (e.g. 2 * 50 = 100 for 2-legged 8mm)
' pt: Percentage of tension steel provided (100 * Ast / bd)
Public Function Design_Shear(ByVal Vu_kN As Double, ByVal b As Double, ByVal d As Double, ByVal fck As Double, ByVal fy As Double, ByVal Asv As Double, ByVal pt As Double) As ShearResult
    Dim res As ShearResult
    
    ' 1. Calculate Tv
    res.Tv = Calculate_Tv(Vu_kN, b, d)
    
    ' 2. Get Tc_max
    res.Tc_max = M03_Tables.Get_TcMax_Value(fck)
    
    ' Check Safety
    If res.Tv > res.Tc_max Then
        res.IsSafe = False
        res.Remarks = "Shear stress exceeds Tc_max. Redesign section."
        res.Tc = 0
        res.Vus = 0
        res.Spacing = 0
        Design_Shear = res
        Exit Function
    End If
    
    res.IsSafe = True
    
    ' 3. Get Tc
    res.Tc = M03_Tables.Get_Tc_Value(fck, pt)
    
    ' 4. Calculate Vus and Spacing
    Dim Vu_N As Double
    Vu_N = Abs(Vu_kN) * 1000#
    
    Dim Vc_N As Double
    Vc_N = res.Tc * b * d
    
    Dim Spacing_Calc As Double
    
    If res.Tv <= res.Tc Then
        ' Nominal shear < Design strength
        ' Provide minimum shear reinforcement
        res.Vus = 0
        res.Remarks = "Nominal shear < Tc. Provide minimum shear reinforcement."
        
        ' Spacing for min reinforcement (Cl. 26.5.1.6)
        ' sv <= (0.87 * fy * Asv) / (0.4 * b)
        Spacing_Calc = (0.87 * fy * Asv) / (0.4 * b)
    Else
        ' Design for shear
        res.Vus = (Vu_N - Vc_N) / 1000# ' kN
        res.Remarks = "Shear reinforcement required."
        
        ' sv = (0.87 * fy * Asv * d) / Vus_N
        Spacing_Calc = (0.87 * fy * Asv * d) / (res.Vus * 1000#)
    End If
    
    ' 5. Apply Max Spacing Limits (Cl. 26.5.1.5)
    Dim Max_Spacing_1 As Double
    Max_Spacing_1 = 0.75 * d
    
    Dim Max_Spacing_2 As Double
    Max_Spacing_2 = 300#
    
    ' Also check Min Reinforcement Spacing Limit again (as a cap)
    ' The min reinforcement formula gives a max spacing allowed to satisfy min reinf.
    Dim Max_Spacing_MinReinf As Double
    Max_Spacing_MinReinf = (0.87 * fy * Asv) / (0.4 * b)
    
    ' Final Spacing is Min of all
    res.Spacing = Spacing_Calc
    If res.Spacing > Max_Spacing_1 Then res.Spacing = Max_Spacing_1
    If res.Spacing > Max_Spacing_2 Then res.Spacing = Max_Spacing_2
    If res.Spacing > Max_Spacing_MinReinf Then res.Spacing = Max_Spacing_MinReinf
    
    ' Round spacing down to nearest 5mm or 10mm?
    ' Engineering practice: Round down to nearest 5 or 10.
    ' Let's round down to nearest integer for now, or leave as double.
    ' The user can round in the UI.
    ' But "Pure Engineering Functions" usually return exact calc.
    ' I'll leave it exact.
    
    Design_Shear = res
End Function

