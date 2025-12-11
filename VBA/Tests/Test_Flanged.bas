Attribute VB_Name = "Test_Flanged"
Option Explicit

' ==============================================================================
' Module:       Test_Flanged
' Description:  Unit tests for Flanged Beam (T/L) Design
'               Strictly follows Mac VBA "Safe Assertion Pattern"
' ==============================================================================

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

Public Sub RunFlangedTests()
    Debug.Print "--- Starting Flanged Beam Tests ---"
    Test_Flanged_NA_In_Flange
    Test_Flanged_NA_In_Web_Singly
    Test_Flanged_NA_In_Web_Doubly
    Debug.Print "--- Flanged Beam Tests Completed ---"
End Sub

' Case 1: Neutral Axis in Flange (Xu < Df)
' Behaves exactly like a rectangular beam of width bf
Public Sub Test_Flanged_NA_In_Flange()
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    
    ' Geometry: Large flange, small moment
    Dim bw As Double: bw = 230#
    Dim bf As Double: bf = 1000#
    Dim d As Double: d = 450#
    Dim Df As Double: Df = 120#
    Dim D_total As Double: D_total = 500#
    Dim fck As Double: fck = 20#
    Dim fy As Double: fy = 415#
    Dim Mu As Double: Mu = 150# ' kNm
    
    ' Expected:
    ' Mu_lim for rect(1000, 450) ~ 558 kNm
    ' 150 < 558 -> Under Reinforced
    ' Xu for 150 kNm with b=1000 is small (< Df)
    
    res = M06_Flexure.Design_Flanged_Beam(bw, bf, d, Df, D_total, Mu, fck, fy)
    
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim isUnder As Boolean: isUnder = (res.SectionType = UnderReinforced)
    Dim xu As Double: xu = res.Xu
    Dim isInFlange As Boolean: isInFlange = (xu < Df)
    
    AssertTrue isSafe, "Flanged_Case1_Safe"
    AssertTrue isUnder, "Flanged_Case1_UnderReinforced"
    AssertTrue isInFlange, "Flanged_Case1_NA_In_Flange"
    
    ' Check Ast against rectangular formula: Ast ~ 960 mm2
    AssertAlmostEqual res.Ast_Required, 960#, 20#, "Flanged_Case1_Ast"
    
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Flanged_Case1 [Error " & Err.Number & "]"
End Sub

' Case 2: Neutral Axis in Web (Xu > Df), Singly Reinforced
Public Sub Test_Flanged_NA_In_Web_Singly()
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    
    ' Geometry
    Dim bw As Double: bw = 300#
    Dim bf As Double: bf = 1500#
    Dim d As Double: d = 600#
    Dim Df As Double: Df = 100#
    Dim D_total As Double: D_total = 650#
    Dim fck As Double: fck = 25#
    Dim fy As Double: fy = 500#
    
    ' Mu needs to be large enough to push NA into web, but < Mu_lim_T
    ' Mu_lim_T approx 1200 kNm
    Dim Mu As Double: Mu = 900#
    
    res = M06_Flexure.Design_Flanged_Beam(bw, bf, d, Df, D_total, Mu, fck, fy)
    
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim xu As Double: xu = res.Xu
    Dim isInWeb As Boolean: isInWeb = (xu > Df)
    
    AssertTrue isSafe, "Flanged_Case2_Safe"
    AssertTrue isInWeb, "Flanged_Case2_NA_In_Web"
    
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Flanged_Case2 [Error " & Err.Number & "]"
End Sub

' Case 3: Neutral Axis in Web, Doubly Reinforced
Public Sub Test_Flanged_NA_In_Web_Doubly()
    On Error GoTo ErrHandler
    Dim res As FlexureResult
    
    ' Geometry
    Dim bw As Double: bw = 300#
    Dim bf As Double: bf = 1500#
    Dim d As Double: d = 600#
    Dim Df As Double: Df = 100#
    Dim D_total As Double: D_total = 650#
    Dim fck As Double: fck = 25#
    Dim fy As Double: fy = 500#
    
    ' Mu > Mu_lim_T
    Dim Mu As Double: Mu = 1500#
    
    res = M06_Flexure.Design_Flanged_Beam(bw, bf, d, Df, D_total, Mu, fck, fy)
    
    Dim isSafe As Boolean: isSafe = res.IsSafe
    Dim isOver As Boolean: isOver = (res.SectionType = OverReinforced)
    Dim asc As Double: asc = res.Asc_Required
    Dim hasCompSteel As Boolean: hasCompSteel = (asc > 0#)
    
    AssertTrue isSafe, "Flanged_Case3_Safe"
    AssertTrue isOver, "Flanged_Case3_Doubly"
    AssertTrue hasCompSteel, "Flanged_Case3_HasAsc"
    
    Exit Sub
ErrHandler:
    Debug.Print "FAIL: Flanged_Case3 [Error " & Err.Number & "]"
End Sub
