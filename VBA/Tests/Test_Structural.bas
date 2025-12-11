Attribute VB_Name = "Test_Structural"
Option Explicit

' ==============================================================================
' Module:       Test_Structural
' Description:  Unit tests for Structural Library (Flexure, Shear, Tables)
'               Requires Rubberduck or manual execution of subs.
' Version:      1.0.2
' Dependencies: M06_Flexure v1.0.0, M07_Shear v1.0.0, M05_Materials v1.0.0
' License:      MIT
' ==============================================================================
' Note: All numeric literals use # suffix to prevent Integer overflow
'       UDT members captured immediately after function returns (Mac VBA workaround)
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
    Test_Flexure_CalcOnly
    Test_Shear_ScalarCalcs
    Test_Materials
    Test_Tables_Tc
    Test_Flexure_MuLim
    Test_Flexure_Design
    Test_Flexure_MinSteel
    Test_Flexure_OverReinforced
    Test_Shear_Design
    Test_Shear_Unsafe
    Test_Shear_MinReinf
    Test_Doubly_Reinforced
    
    ' Run Flanged Beam Tests (New in v0.3)
    Test_Flanged.RunFlangedTests
    
    ' Run Ductile Detailing Tests (New in v1.0)
    Test_Ductile.RunDuctileTests
    
    Debug.Print "--- Tests Completed ---"
End Sub

' ==============================================================================
' Test Cases
' ==============================================================================

' Quick scalar checks to isolate overflow sources in flexure
Public Sub Test_Flexure_CalcOnly()
    Dim stepTag As String
    On Error GoTo ErrHandler
    
    ' Use Variant to avoid any implicit type coercion issues on Mac
    Dim muLim As Variant
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    stepTag = "Calc_Mu_Lim"
    ' Assign to Variant first
    muLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    ' Explicitly cast to Double for local use
    Dim muLimD As Double
    muLimD = CDbl(muLim)
    
    stepTag = "Bounds_Lower"
    Dim okLower As Boolean
    If muLimD > 120# Then okLower = True Else okLower = False
    
    stepTag = "Bounds_Upper"
    Dim okUpper As Boolean
    If muLimD < 170# Then okUpper = True Else okUpper = False
    
    ' Over-reinforced request should return -1 without overflow
    stepTag = "Calc_Ast_Over"
    Dim astOver As Variant
    Dim Mu_over As Double: Mu_over = 1.2 * muLimD
    astOver = M06_Flexure.Calculate_Ast_Required(b, d, Mu_over, fck, fy)
    
    Dim astOverD As Double
    astOverD = CDbl(astOver)
    
    Dim isOver As Boolean
    isOver = (astOverD = -1#)
    
    AssertTrue okLower, "Flexure_CalcOnly_MuLim_Lower"
    AssertTrue okUpper, "Flexure_CalcOnly_MuLim_Upper"
    AssertTrue isOver, "Flexure_CalcOnly_OverFlag"
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Flexure_CalcOnly [" & stepTag & "]: "; Err.Number; " - "; Err.Description
End Sub

' ==============================================================================
' EXPERIMENTAL TESTS (Mac Stability Brute Force)
' ==============================================================================

' Exp 1: Inline Assertion (No Sub Call)
Public Sub Test_Exp_InlineAssert()
    On Error GoTo ErrHandler
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    Dim muLim As Variant
    muLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    Dim muLimD As Double: muLimD = CDbl(muLim)
    
    Dim Mu_over As Double: Mu_over = 1.2 * muLimD
    Dim astOver As Variant
    astOver = M06_Flexure.Calculate_Ast_Required(b, d, Mu_over, fck, fy)
    Dim astOverD As Double: astOverD = CDbl(astOver)
    
    ' Avoid calling AssertTrue
    If astOverD = -1# Then
        Debug.Print "PASS: Exp_InlineAssert"
    Else
        Debug.Print "FAIL: Exp_InlineAssert (Got " & astOverD & ")"
    End If
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Exp_InlineAssert [Error " & Err.Number & "]"
End Sub

' Exp 2: Pure Double (No Variant, No Print until end)
Public Sub Test_Exp_PureDouble()
    On Error GoTo ErrHandler
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    Dim muLim As Double
    muLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    Dim Mu_over As Double: Mu_over = 1.2 * muLim
    Dim astOver As Double
    astOver = M06_Flexure.Calculate_Ast_Required(b, d, Mu_over, fck, fy)
    
    If astOver = -1# Then
        Debug.Print "PASS: Exp_PureDouble"
    Else
        Debug.Print "FAIL: Exp_PureDouble (Got " & astOver & ")"
    End If
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Exp_PureDouble [Error " & Err.Number & "]"
End Sub

' Exp 3: ByRef Helper Wrapper
' This forces the return value to be passed via a parameter, avoiding the function return stack mechanism
Private Sub Helper_CalcAst(ByVal b As Double, ByVal d As Double, ByVal Mu As Double, ByVal fck As Double, ByVal fy As Double, ByRef result As Double)
    result = M06_Flexure.Calculate_Ast_Required(b, d, Mu, fck, fy)
End Sub

Public Sub Test_Exp_ByRefHelper()
    On Error GoTo ErrHandler
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    Dim muLim As Double
    muLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    Dim Mu_over As Double: Mu_over = 1.2 * muLim
    Dim astOver As Double
    
    ' Call wrapper
    Helper_CalcAst b, d, Mu_over, fck, fy, astOver
    
    If astOver = -1# Then
        Debug.Print "PASS: Exp_ByRefHelper"
    Else
        Debug.Print "FAIL: Exp_ByRefHelper (Got " & astOver & ")"
    End If
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Exp_ByRefHelper [Error " & Err.Number & "]"
End Sub

' Exp 4: Split Comparison
' Break the comparison into simplest possible steps
Public Sub Test_Exp_SplitComp()
    On Error GoTo ErrHandler
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    Dim muLim As Variant
    muLim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    Dim muLimD As Double: muLimD = CDbl(muLim)
    
    Dim Mu_over As Double: Mu_over = 1.2 * muLimD
    Dim astOver As Variant
    astOver = M06_Flexure.Calculate_Ast_Required(b, d, Mu_over, fck, fy)
    Dim astOverD As Double: astOverD = CDbl(astOver)
    
    Dim target As Double: target = -1#
    Dim isMatch As Boolean
    
    ' The comparison itself might be overflowing if types are weird
    If astOverD = target Then isMatch = True Else isMatch = False
    
    If isMatch Then
        Debug.Print "PASS: Exp_SplitComp"
    Else
        Debug.Print "FAIL: Exp_SplitComp"
    End If
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Exp_SplitComp [Error " & Err.Number & "]"
End Sub

' Quick scalar checks to isolate overflow sources in shear
Public Sub Test_Shear_ScalarCalcs()
    On Error GoTo ErrHandler
    Dim tv As Double
    tv = M07_Shear.Calculate_Tv(100#, 230#, 450#)
    Debug.Print "  [ShearCalc] Tv = "; tv
    AssertAlmostEqual tv, 0.966183575, 0.0001, "Shear_Tv_Calc"
    
    Dim tc As Double
    tc = M03_Tables.Get_Tc_Value(20#, 1#)
    Debug.Print "  [ShearCalc] Tc = "; tc
    AssertAlmostEqual tc, 0.62, 0.0001, "Shear_Tc_Calc"
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Shear_ScalarCalcs: "; Err.Number; " - "; Err.Description; " | tv="; tv; " | tc="; tc
End Sub

Public Sub Test_Doubly_Reinforced()
    Dim stepTag As String
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    Dim b As Double, d As Double, d_dash As Double, D_total As Double
    Dim fck As Double, fy As Double
    
    b = 230#: d = 450#: d_dash = 40#: D_total = 500#
    fck = 25#: fy = 415#
    
    ' Avoid calling Calculate_Mu_Lim here to keep stack clean
    ' Mu_lim for M25/Fe415/230/450 is approx 160.6 kNm
    Dim Mu_lim_Est As Double
    Mu_lim_Est = 160.6
    
    ' Case 1: Singly Reinforced Fallback (Mu < Mu_lim)
    Dim Mu_case1 As Double
    Mu_case1 = 120# ' Safe value well below 160
    
    stepTag = "Design_Doubly_Case1"
    res = M06_Flexure.Design_Doubly_Reinforced(b, d, d_dash, D_total, Mu_case1, fck, fy)
    
    ' Immediately capture values
    Dim isSafe1 As Boolean: isSafe1 = res.IsSafe
    Dim asc1 As Double: asc1 = res.Asc_Required
    
    AssertTrue isSafe1, "Doubly_Fallback_Safe"
    AssertAlmostEqual asc1, 0#, , "Doubly_Fallback_AscZero"
    
    ' Case 2: Doubly Reinforced Needed (Mu > Mu_lim)
    Dim Mu_case2 As Double
    Mu_case2 = 240# ' Safe value well above 160
    
    stepTag = "Design_Doubly_Case2"
    res = M06_Flexure.Design_Doubly_Reinforced(b, d, d_dash, D_total, Mu_case2, fck, fy)
    
    ' Immediately capture values
    Dim isSafe2 As Boolean: isSafe2 = res.IsSafe
    Dim asc2 As Double: asc2 = res.Asc_Required
    Dim ast2 As Double: ast2 = res.Ast_Required
    Dim secType2 As DesignSectionType: secType2 = res.SectionType
    
    Dim isAscPos As Boolean: isAscPos = (CDbl(asc2) > 0#)
    Dim isAstPos As Boolean: isAstPos = (CDbl(ast2) > 0#)
    Dim isOver As Boolean: isOver = (secType2 = OverReinforced)
    
    AssertTrue isSafe2, "Doubly_Needed_Safe"
    AssertTrue isAscPos, "Doubly_Needed_AscPositive"
    AssertTrue isAstPos, "Doubly_Needed_AstPositive"
    AssertTrue isOver, "Doubly_Needed_Type"
    
    ' Case 3: Steel Stress Check (Fe415)
    AssertAlmostEqual M05_Materials.Get_Steel_Stress(0.00144, 415#), 288.7, , "SteelStress_Fe415_Point1"
    AssertAlmostEqual M05_Materials.Get_Steel_Stress(0.005, 415#), 360.9, , "SteelStress_Fe415_Yield"
    
    Debug.Print "  [Debug] Case 1 returned. IsSafe=" & isSafe1 & ", Asc=" & asc1
    Debug.Print "  [Debug] Case 2 returned. IsSafe=" & isSafe2 & ", Asc=" & asc2 & ", Ast=" & ast2
    Exit Sub
    
ErrHandler:
    Debug.Print "  [ERROR] Test_Doubly_Reinforced [" & stepTag & "]: " & Err.Number & " - " & Err.Description
End Sub

Public Sub Test_Materials()
    AssertAlmostEqual M05_Materials.Get_XuMax_d(250#), 0.53, , "Materials_XuMax_250"
    AssertAlmostEqual M05_Materials.Get_XuMax_d(415#), 0.48, , "Materials_XuMax_415"
    AssertAlmostEqual M05_Materials.Get_XuMax_d(500#), 0.46, , "Materials_XuMax_500"
    
    AssertAlmostEqual M05_Materials.Get_Ec(25#), 25000#, , "Materials_Ec_25"
End Sub

Public Sub Test_Tables_Tc()
    ' M20, pt=0.5 -> 0.48
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20#, 0.5), 0.48, , "Tables_Tc_M20_0.5"
    
    ' Interpolation: M20, pt=0.625 -> 0.52
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20#, 0.625), 0.52, , "Tables_Tc_M20_Interp"
    
    ' No Fck Interpolation: M22.5 -> Uses M20 -> 0.48
    AssertAlmostEqual M03_Tables.Get_Tc_Value(22.5, 0.5), 0.48, , "Tables_Tc_NoFckInterp"
    
    ' Pt Clamping
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20#, 0.05), 0.28, , "Tables_Tc_ClampLow"
    AssertAlmostEqual M03_Tables.Get_Tc_Value(20#, 4#), 0.82, , "Tables_Tc_ClampHigh"
End Sub

Public Sub Test_Flexure_MuLim()
    ' M20, Fe415, b=230, d=450
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    Dim Mu_lim As Variant
    Mu_lim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    Dim Mu_limD As Double
    Mu_limD = CDbl(Mu_lim)
    
    ' Expected ~128.5
    Dim checkLower As Boolean: checkLower = (Mu_limD > 128#)
    Dim checkUpper As Boolean: checkUpper = (Mu_limD < 129#)
    
    Debug.Print "  [Flexure_MuLim] Mu_lim = "; Mu_limD
    AssertTrue checkLower, "Flexure_MuLim_Lower"
    AssertTrue checkUpper, "Flexure_MuLim_Upper"
End Sub

Public Sub Test_Flexure_Design()
    Dim res As FlexureResult
    res = M06_Flexure.Design_Singly_Reinforced(230#, 450#, 500#, 100#, 20#, 415#)
    
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim isUnder As Boolean: isUnder = (res.SectionType = UnderReinforced)
    Dim astReq As Double: astReq = res.Ast_Required
    
    AssertTrue isSafe, "Flexure_Design_Safe"
    AssertTrue isUnder, "Flexure_Design_UnderReinforced"
    ' Expect Ast ~700 mm^2 for 230x450, Mu=100 kN·m, M20/Fe415
    AssertAlmostEqual astReq, 700#, 100#, "Flexure_Design_Ast_Range"
End Sub

Public Sub Test_Flexure_MinSteel()
    Dim res As FlexureResult
    ' Very small moment
    res = M06_Flexure.Design_Singly_Reinforced(230#, 450#, 500#, 5#, 20#, 415#)
    
    Dim Ast_min As Double
    ' Force Double arithmetic to avoid Integer overflow (230*450 > 32767)
    Ast_min = 0.85 * 230# * 450# / 415# ' ~212.0
    
    AssertTrue res.IsSafe, "Flexure_MinSteel_Safe"
    AssertAlmostEqual res.Ast_Required, Ast_min, 0.1, "Flexure_MinSteel_Value"
End Sub

Public Sub Test_Flexure_OverReinforced()
    Dim stepTag As String
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    
    Debug.Print "  [Debug] Calling Design_Singly_Reinforced..."
    
    ' Large moment > 128
    stepTag = "Call_Design_Singly_Over"
    res = M06_Flexure.Design_Singly_Reinforced(230#, 450#, 500#, 150#, 20#, 415#)
    
    ' Immediately capture all values we need
    stepTag = "Capture_Result"
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim secType As DesignSectionType: secType = res.SectionType
    Dim astReq As Double: astReq = res.Ast_Required
    
    stepTag = "Assert_Result"
    Dim isOver As Boolean: isOver = (secType = OverReinforced)
    Dim isAstZero As Boolean: isAstZero = (CDbl(astReq) < 0.001)
    
    AssertFalse isSafe, "Flexure_Over_Safe"
    AssertTrue isOver, "Flexure_Over_Type"
    AssertTrue isAstZero, "Flexure_Over_AstZero"
    Exit Sub
    
ErrHandler:
    Debug.Print "  [ERROR] Test_Flexure_OverReinforced [" & stepTag & "]: " & Err.Number & " - " & Err.Description
End Sub

Public Sub Test_Shear_Design()
    Dim stepTag As String
    On Error GoTo ErrHandler
    Dim res As ShearResult
    
    Debug.Print "  [Debug] Calling Design_Shear..."
    
    ' M20, Fe415, Vu=100, Asv=100.5 (8mm 2L), pt=1.0
    stepTag = "Call_Design_Shear"
    res = M07_Shear.Design_Shear(100#, 230#, 450#, 20#, 415#, 100.5, 1#)
    
    ' Immediately capture all values we need
    stepTag = "Capture_Result"
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim tv As Double: tv = res.Tv
    Dim tc As Double: tc = res.Tc
    Dim vus As Double: vus = res.Vus
    Dim spacing As Double: spacing = res.Spacing
    
    stepTag = "Assert_Result"
    Dim isVusPos As Boolean: isVusPos = (CDbl(vus) > 0#)
    
    AssertTrue isSafe, "Shear_Design_Safe"
    AssertAlmostEqual tv, 0.966183575, 0.0001, "Shear_Design_Tv"
    AssertAlmostEqual tc, 0.62, 0.0001, "Shear_Design_Tc"
    AssertAlmostEqual spacing, 300#, , "Shear_Design_Spacing"
    AssertTrue isVusPos, "Shear_Design_Vus_Positive"
    Exit Sub
    
ErrHandler:
    Debug.Print "  [ERROR] Test_Shear_Design [" & stepTag & "]: " & Err.Number & " - " & Err.Description & _
                " | Tv=" & tv & " Tc=" & tc & " Vus=" & vus & " Spacing=" & spacing
End Sub

Public Sub Test_Shear_Unsafe()
    Dim res As ShearResult
    ' Vu=300 -> Tv > Tc_max (2.8)
    res = M07_Shear.Design_Shear(300#, 230#, 450#, 20#, 415#, 100.5, 1#)
    
    Dim isSafe As Boolean: isSafe = res.IsSafe
    AssertFalse isSafe, "Shear_Unsafe_Check"
End Sub

Public Sub Test_Shear_MinReinf()
    Dim res As ShearResult
    ' Vu=50 -> Tv < Tc (0.62)
    res = M07_Shear.Design_Shear(50#, 230#, 450#, 20#, 415#, 100.5, 1#)
    
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim vus As Double: vus = res.Vus
    Dim spacing As Double: spacing = res.Spacing
    
    AssertTrue isSafe, "Shear_MinReinf_Safe"
    AssertAlmostEqual vus, 0#, , "Shear_MinReinf_VusZero"
    AssertAlmostEqual spacing, 300#, , "Shear_MinReinf_Spacing"
End Sub
