Attribute VB_Name = "Test_Structural"
Option Explicit

' ==============================================================================
' Module:       Test_Structural
' Description:  Unit tests for Structural Library (Flexure, Shear, Tables)
'               Requires Rubberduck or manual execution of subs.
' Version:      1.0.0
' License:      MIT
' ==============================================================================

' Simple assertion helper
Private Sub AssertAlmostEqual(ByVal Actual As Double, ByVal Expected As Double, Optional ByVal Tolerance As Double = 0.001, Optional ByVal TestName As String = "")
    If Abs(Actual - Expected) > Tolerance Then
        Debug.Print "FAIL: " & TestName & " | Expected " & Expected & ", Got " & Actual
    Else
        Debug.Print "PASS: " & TestName
    End If
End Sub

Private Sub AssertTrue(ByVal Condition As Boolean, Optional ByVal TestName As String = "")
    If Not Condition Then
        Debug.Print "FAIL: " & TestName & " | Expected True"
    Else
        Debug.Print "PASS: " & TestName
    End If
End Sub

Private Sub AssertFalse(ByVal Condition As Boolean, Optional ByVal TestName As String = "")
    If Condition Then
        Debug.Print "FAIL: " & TestName & " | Expected False"
    Else
        Debug.Print "PASS: " & TestName
    End If
End Sub

' ==============================================================================
' Test Runner
' ==============================================================================
Public Sub RunAllTests()
    Debug.Print "--- Starting Tests ---"
    Test_Materials
    Test_Tables_Tc
    Test_Flexure_MuLim
    Test_Flexure_Design
    Test_Flexure_MinSteel
    Test_Flexure_OverReinforced
    Test_Shear_Design
    Test_Shear_Unsafe
    Test_Shear_MinReinf
    Debug.Print "--- Tests Completed ---"
End Sub

' ==============================================================================
' Test Cases
' ==============================================================================

Public Sub Test_Materials()
    AssertAlmostEqual M05_Materials.Get_XuMax_d(250), 0.53, , "Materials_XuMax_250"
    AssertAlmostEqual M05_Materials.Get_XuMax_d(415), 0.48, , "Materials_XuMax_415"
    AssertAlmostEqual M05_Materials.Get_XuMax_d(500), 0.46, , "Materials_XuMax_500"
    
    AssertAlmostEqual M05_Materials.Get_Ec(25), 25000#, , "Materials_Ec_25"
End Sub

Public Sub Test_Tables_Tc()
    ' M20, pt=0.5 -> 0.48
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20, 0.5), 0.48, , "Tables_Tc_M20_0.5"
    
    ' Interpolation: M20, pt=0.625 -> 0.52
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20, 0.625), 0.52, , "Tables_Tc_M20_Interp"
    
    ' No Fck Interpolation: M22.5 -> Uses M20 -> 0.48
    AssertAlmostEqual M03_Tables.Get_Tc_Value(22.5, 0.5), 0.48, , "Tables_Tc_NoFckInterp"
    
    ' Pt Clamping
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20, 0.05), 0.28, , "Tables_Tc_ClampLow"
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20, 4#), 0.82, , "Tables_Tc_ClampHigh"
End Sub

Public Sub Test_Flexure_MuLim()
    ' M20, Fe415, b=230, d=450
    Dim Mu_lim As Double
    Mu_lim = M06_Flexure.Calculate_Mu_Lim(230, 450, 20, 415)
    
    ' Expected ~128.5
    AssertTrue (Mu_lim > 128 And Mu_lim < 129), "Flexure_MuLim_Range"
End Sub

Public Sub Test_Flexure_Design()
    Dim res As FlexureResult
    res = M06_Flexure.Design_Singly_Reinforced(230, 450, 500, 100, 20, 415)
    
    AssertTrue res.IsSafe, "Flexure_Design_Safe"
    AssertTrue (res.SectionType = UnderReinforced), "Flexure_Design_UnderReinforced"
    AssertTrue (res.Ast_Required > 650 And res.Ast_Required < 750), "Flexure_Design_Ast_Range"
End Sub

Public Sub Test_Flexure_MinSteel()
    Dim res As FlexureResult
    ' Very small moment
    res = M06_Flexure.Design_Singly_Reinforced(230, 450, 500, 5, 20, 415)
    
    Dim Ast_min As Double
    Ast_min = 0.85 * 230 * 450 / 415 ' ~212.0
    
    AssertTrue res.IsSafe, "Flexure_MinSteel_Safe"
    AssertAlmostEqual res.Ast_Required, Ast_min, 0.1, "Flexure_MinSteel_Value"
End Sub

Public Sub Test_Flexure_OverReinforced()
    Dim res As FlexureResult
    ' Large moment > 128
    res = M06_Flexure.Design_Singly_Reinforced(230, 450, 500, 150, 20, 415)
    
    AssertFalse res.IsSafe, "Flexure_Over_Safe"
    AssertTrue (res.SectionType = OverReinforced), "Flexure_Over_Type"
    AssertAlmostEqual res.Ast_Required, 0, , "Flexure_Over_AstZero"
End Sub

Public Sub Test_Shear_Design()
    Dim res As ShearResult
    ' M20, Fe415, Vu=100, Asv=100.5 (8mm 2L), pt=1.0
    res = M07_Shear.Design_Shear(100, 230, 450, 20, 415, 100.5, 1#)
    
    AssertTrue res.IsSafe, "Shear_Design_Safe"
    AssertAlmostEqual res.Spacing, 300#, , "Shear_Design_Spacing"
    AssertTrue (res.Vus > 0), "Shear_Design_Vus"
End Sub

Public Sub Test_Shear_Unsafe()
    Dim res As ShearResult
    ' Vu=300 -> Tv > Tc_max (2.8)
    res = M07_Shear.Design_Shear(300, 230, 450, 20, 415, 100.5, 1#)
    
    AssertFalse res.IsSafe, "Shear_Unsafe_Check"
End Sub

Public Sub Test_Shear_MinReinf()
    Dim res As ShearResult
    ' Vu=50 -> Tv < Tc (0.62)
    res = M07_Shear.Design_Shear(50, 230, 450, 20, 415, 100.5, 1#)
    
    AssertTrue res.IsSafe, "Shear_MinReinf_Safe"
    AssertAlmostEqual res.Vus, 0, , "Shear_MinReinf_VusZero"
    AssertAlmostEqual res.Spacing, 300#, , "Shear_MinReinf_Spacing"
End Sub
