Attribute VB_Name = "Test_Parity"
Option Explicit

' ==============================================================================
' Module:       Test_Parity
' Description:  Parity tests matching Python test vectors (parity_test_vectors.json)
' Version:      0.9.3
' License:      MIT
' ==============================================================================
'
' These tests verify VBA calculations match Python outputs exactly.
' Tolerance rules (matching Python):
'   - ast_mm2, asc_mm2: ±1.0
'   - mu_knm: ±0.01
'   - spacing_mm, length_mm: ±1.0
'   - stress_nmm2: ±0.01
'   - ratio: ±0.0001
'
' ==============================================================================

Private m_PassCount As Long
Private m_FailCount As Long
Private m_Results As String

Private Const TOL_AST As Double = 1#
Private Const TOL_MU As Double = 0.01
Private Const TOL_STRESS As Double = 0.01
Private Const TOL_LENGTH As Double = 1#
Private Const TOL_RATIO As Double = 0.0001

' ==============================================================================
' Main Entry Point
' ==============================================================================
Public Sub Run_All_Parity_Tests()
    m_PassCount = 0
    m_FailCount = 0
    m_Results = ""
    
    Debug.Print "========================================"
    Debug.Print "  PARITY TESTS: VBA vs Python Vectors"
    Debug.Print "========================================"
    Debug.Print ""
    
    ' Flexure Singly Reinforced
    Call Test_FSR_001
    Call Test_FSR_002
    Call Test_FSR_003
    
    ' Shear Tests
    Call Test_SHR_001
    Call Test_SHR_002
    Call Test_SHR_003
    
    ' Detailing Tests
    Call Test_DET_001
    Call Test_DET_002
    Call Test_DET_003
    Call Test_DET_004
    
    ' Serviceability Tests
    Call Test_SVC_001
    Call Test_SVC_002
    
    ' Summary
    Debug.Print ""
    Debug.Print "========================================"
    Debug.Print "  PARITY RESULTS"
    Debug.Print "========================================"
    Debug.Print "  Passed: " & m_PassCount
    Debug.Print "  Failed: " & m_FailCount
    Debug.Print "========================================"
    
    If m_FailCount > 0 Then
        Debug.Print ""
        Debug.Print "FAILURES:"
        Debug.Print m_Results
    Else
        Debug.Print "  STATUS: ALL PARITY TESTS PASSED"
    End If
    Debug.Print "========================================"
End Sub

' ==============================================================================
' Assertion Helpers
' ==============================================================================
Private Sub AssertAlmostEqual(ByVal actual As Double, ByVal expected As Double, _
                               ByVal tolerance As Double, ByVal testName As String)
    If Abs(actual - expected) <= tolerance Then
        m_PassCount = m_PassCount + 1
        Debug.Print "  [PASS] " & testName
    Else
        m_FailCount = m_FailCount + 1
        Debug.Print "  [FAIL] " & testName & " | Expected " & expected & ", Got " & actual
        m_Results = m_Results & testName & ": Expected " & expected & ", Got " & actual & vbCrLf
    End If
End Sub

Private Sub AssertTrue(ByVal condition As Boolean, ByVal testName As String)
    If condition Then
        m_PassCount = m_PassCount + 1
        Debug.Print "  [PASS] " & testName
    Else
        m_FailCount = m_FailCount + 1
        Debug.Print "  [FAIL] " & testName & " | Expected TRUE"
        m_Results = m_Results & testName & ": Expected TRUE" & vbCrLf
    End If
End Sub

' ==============================================================================
' FLEXURE SINGLY REINFORCED (FSR-001, FSR-002, FSR-003)
' ==============================================================================

Private Sub Test_FSR_001()
    ' FSR-001: Standard M20/Fe415 beam - under-reinforced
    Debug.Print ">>> FSR-001: Standard M20/Fe415 beam"
    
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim d_total As Double: d_total = 500#
    Dim mu As Double: mu = 100#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    ' Expected values from Python
    Dim exp_mu_lim As Double: exp_mu_lim = 128.513
    Dim exp_ast As Double: exp_ast = 719.62
    
    ' Calculate
    Dim mu_lim As Double
    mu_lim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    Dim ast As Double
    ast = M06_Flexure.Calculate_Ast_Required(b, d, mu, fck, fy)
    
    ' Assert
    AssertAlmostEqual mu_lim, exp_mu_lim, TOL_MU, "FSR-001_Mu_lim"
    AssertAlmostEqual ast, exp_ast, TOL_AST, "FSR-001_Ast"
End Sub

Private Sub Test_FSR_002()
    ' FSR-002: M25/Fe500 beam - under-reinforced
    Debug.Print ">>> FSR-002: M25/Fe500 beam"
    
    Dim b As Double: b = 300#
    Dim d As Double: d = 450#
    Dim mu As Double: mu = 150#
    Dim fck As Double: fck = 25#
    Dim fy As Double: fy = 500#
    
    Dim exp_mu_lim As Double: exp_mu_lim = 202.914
    Dim exp_ast As Double: exp_ast = 881.88
    
    Dim mu_lim As Double
    mu_lim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    Dim ast As Double
    ast = M06_Flexure.Calculate_Ast_Required(b, d, mu, fck, fy)
    
    AssertAlmostEqual mu_lim, exp_mu_lim, TOL_MU, "FSR-002_Mu_lim"
    AssertAlmostEqual ast, exp_ast, TOL_AST, "FSR-002_Ast"
End Sub

Private Sub Test_FSR_003()
    ' FSR-003: Small beam - low moment
    Debug.Print ">>> FSR-003: Small beam - low moment"
    
    Dim b As Double: b = 200#
    Dim d As Double: d = 350#
    Dim mu As Double: mu = 40#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    
    Dim exp_mu_lim As Double: exp_mu_lim = 67.60
    Dim exp_ast As Double: exp_ast = 353.80
    
    Dim mu_lim As Double
    mu_lim = M06_Flexure.Calculate_Mu_Lim(b, d, fck, fy)
    
    Dim ast As Double
    ast = M06_Flexure.Calculate_Ast_Required(b, d, mu, fck, fy)
    
    AssertAlmostEqual mu_lim, exp_mu_lim, TOL_MU, "FSR-003_Mu_lim"
    AssertAlmostEqual ast, exp_ast, TOL_AST, "FSR-003_Ast"
End Sub

' ==============================================================================
' SHEAR TESTS (SHR-001, SHR-002, SHR-003)
' ==============================================================================

Private Sub Test_SHR_001()
    ' SHR-001: Shear design with stirrups required
    Debug.Print ">>> SHR-001: Shear design with stirrups"
    
    Dim vu As Double: vu = 150#
    Dim b As Double: b = 230#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    Dim asv As Double: asv = 100#
    Dim pt As Double: pt = 1#
    
    Dim exp_tv As Double: exp_tv = 1.449
    Dim exp_tc As Double: exp_tc = 0.62
    
    ' Calculate
    Dim tv As Double
    tv = M07_Shear.Calculate_Tv(vu, b, d)
    
    Dim tc As Double
    tc = M03_Tables.Get_Tc(fck, pt)
    
    AssertAlmostEqual tv, exp_tv, TOL_STRESS, "SHR-001_tv"
    AssertAlmostEqual tc, exp_tc, TOL_STRESS, "SHR-001_tc"
End Sub

Private Sub Test_SHR_002()
    ' SHR-002: Low shear - minimum stirrups only
    Debug.Print ">>> SHR-002: Low shear - minimum stirrups"
    
    Dim vu As Double: vu = 50#
    Dim b As Double: b = 300#
    Dim d As Double: d = 450#
    Dim fck As Double: fck = 25#
    Dim pt As Double: pt = 0.5
    
    Dim exp_tv As Double: exp_tv = 0.370
    Dim exp_tc As Double: exp_tc = 0.49
    
    Dim tv As Double
    tv = M07_Shear.Calculate_Tv(vu, b, d)
    
    Dim tc As Double
    tc = M03_Tables.Get_Tc(fck, pt)
    
    AssertAlmostEqual tv, exp_tv, TOL_STRESS, "SHR-002_tv"
    AssertAlmostEqual tc, exp_tc, TOL_STRESS, "SHR-002_tc"
End Sub

Private Sub Test_SHR_003()
    ' SHR-003: High shear - close stirrup spacing
    Debug.Print ">>> SHR-003: High shear - close spacing"
    
    Dim vu As Double: vu = 300#
    Dim b As Double: b = 300#
    Dim d As Double: d = 550#
    Dim fck As Double: fck = 30#
    Dim pt As Double: pt = 1.5
    
    Dim exp_tv As Double: exp_tv = 1.818
    Dim exp_tc As Double: exp_tc = 0.76
    
    Dim tv As Double
    tv = M07_Shear.Calculate_Tv(vu, b, d)
    
    Dim tc As Double
    tc = M03_Tables.Get_Tc(fck, pt)
    
    AssertAlmostEqual tv, exp_tv, TOL_STRESS, "SHR-003_tv"
    AssertAlmostEqual tc, exp_tc, TOL_STRESS, "SHR-003_tc"
End Sub

' ==============================================================================
' DETAILING TESTS (DET-001 to DET-004)
' ==============================================================================

Private Sub Test_DET_001()
    ' DET-001: Development length - 16mm bar M25
    Debug.Print ">>> DET-001: Development length 16mm"
    
    Dim dia As Double: dia = 16#
    Dim fck As Double: fck = 25#
    Dim fy As Double: fy = 500#
    
    Dim exp_tau_bd As Double: exp_tau_bd = 2.24
    Dim exp_ld As Double: exp_ld = 777#
    
    Dim tau_bd As Double
    tau_bd = M15_Detailing.Get_Bond_Stress(fck, "deformed")
    
    Dim ld As Double
    ld = M15_Detailing.Calculate_Ld(dia, fck, fy, "deformed")
    
    AssertAlmostEqual tau_bd, exp_tau_bd, TOL_STRESS, "DET-001_tau_bd"
    AssertAlmostEqual ld, exp_ld, TOL_LENGTH, "DET-001_Ld"
End Sub

Private Sub Test_DET_002()
    ' DET-002: Development length - 20mm bar M30
    Debug.Print ">>> DET-002: Development length 20mm"
    
    Dim dia As Double: dia = 20#
    Dim fck As Double: fck = 30#
    Dim fy As Double: fy = 500#
    
    Dim exp_ld As Double: exp_ld = 906#
    
    Dim ld As Double
    ld = M15_Detailing.Calculate_Ld(dia, fck, fy, "deformed")
    
    AssertAlmostEqual ld, exp_ld, TOL_LENGTH, "DET-002_Ld"
End Sub

Private Sub Test_DET_003()
    ' DET-003: Lap length - tension splice
    Debug.Print ">>> DET-003: Lap length tension"
    
    Dim dia As Double: dia = 16#
    Dim fck As Double: fck = 25#
    Dim fy As Double: fy = 500#
    
    Dim exp_lap As Double: exp_lap = 1166#
    
    Dim lap As Double
    lap = M15_Detailing.Calculate_Lap_Length(dia, fck, fy, "deformed", 50#, True, True)
    
    AssertAlmostEqual lap, exp_lap, TOL_LENGTH, "DET-003_Lap"
End Sub

Private Sub Test_DET_004()
    ' DET-004: Bar spacing calculation
    Debug.Print ">>> DET-004: Bar spacing"
    
    Dim b As Double: b = 300#
    Dim cover As Double: cover = 25#
    Dim stirrup As Double: stirrup = 8#
    Dim bar_dia As Double: bar_dia = 16#
    Dim n_bars As Long: n_bars = 3
    
    Dim exp_spacing As Double: exp_spacing = 94#
    
    Dim spacing As Double
    spacing = M15_Detailing.Calculate_Bar_Spacing(b, cover, stirrup, bar_dia, n_bars)
    
    AssertAlmostEqual spacing, exp_spacing, TOL_LENGTH, "DET-004_Spacing"
End Sub

' ==============================================================================
' SERVICEABILITY TESTS (SVC-001, SVC-002)
' ==============================================================================

Private Sub Test_SVC_001()
    ' SVC-001: Deflection check - simply supported
    Debug.Print ">>> SVC-001: Deflection simply supported"
    
    Dim span As Double: span = 4000#
    Dim d As Double: d = 450#
    
    Dim exp_ld_ratio As Double: exp_ld_ratio = 8.8889
    Dim exp_allowable As Double: exp_allowable = 20#
    
    Dim ld_ratio As Double
    ld_ratio = span / d
    
    Dim allowable As Double
    allowable = M17_Serviceability.Get_Basic_Span_Depth("simply_supported")
    
    AssertAlmostEqual ld_ratio, exp_ld_ratio, TOL_RATIO, "SVC-001_ld_ratio"
    AssertAlmostEqual allowable, exp_allowable, TOL_RATIO, "SVC-001_allowable"
End Sub

Private Sub Test_SVC_002()
    ' SVC-002: Deflection check - continuous
    Debug.Print ">>> SVC-002: Deflection continuous"
    
    Dim span As Double: span = 6000#
    Dim d As Double: d = 500#
    
    Dim exp_ld_ratio As Double: exp_ld_ratio = 12#
    Dim exp_allowable As Double: exp_allowable = 26#
    
    Dim ld_ratio As Double
    ld_ratio = span / d
    
    Dim allowable As Double
    allowable = M17_Serviceability.Get_Basic_Span_Depth("continuous")
    
    AssertAlmostEqual ld_ratio, exp_ld_ratio, TOL_RATIO, "SVC-002_ld_ratio"
    AssertAlmostEqual allowable, exp_allowable, TOL_RATIO, "SVC-002_allowable"
End Sub
