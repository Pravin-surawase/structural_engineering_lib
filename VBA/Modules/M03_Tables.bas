Attribute VB_Name = "M03_Tables"
Option Explicit

' ==============================================================================
' Module:       M03_Tables
' Description:  Data tables from IS 456:2000 (Table 19, Table 20, etc.)
' Version:      1.0.01
' License:      MIT
' ==============================================================================

' ------------------------------------------------------------------------------
' Table 19: Design Shear Strength of Concrete (Tc)
' ------------------------------------------------------------------------------

Private Function Get_Pt_Rows() As Variant
    Get_Pt_Rows = Array(0.15, 0.25, 0.5, 0.75, 1#, 1.25, 1.5, 1.75, 2#, 2.25, 2.5, 2.75, 3#)
End Function

Private Function Get_Tc_Column_M15() As Variant
    Get_Tc_Column_M15 = Array(0.28, 0.35, 0.46, 0.54, 0.6, 0.64, 0.68, 0.71, 0.71, 0.71, 0.71, 0.71, 0.71)
End Function

Private Function Get_Tc_Column_M20() As Variant
    Get_Tc_Column_M20 = Array(0.28, 0.36, 0.48, 0.56, 0.62, 0.67, 0.72, 0.75, 0.79, 0.81, 0.82, 0.82, 0.82)
End Function

Private Function Get_Tc_Column_M25() As Variant
    Get_Tc_Column_M25 = Array(0.29, 0.36, 0.49, 0.57, 0.64, 0.7, 0.74, 0.78, 0.82, 0.85, 0.88, 0.9, 0.92)
End Function

Private Function Get_Tc_Column_M30() As Variant
    Get_Tc_Column_M30 = Array(0.29, 0.37, 0.5, 0.59, 0.66, 0.71, 0.76, 0.8, 0.84, 0.88, 0.91, 0.94, 0.96)
End Function

Private Function Get_Tc_Column_M35() As Variant
    Get_Tc_Column_M35 = Array(0.29, 0.37, 0.5, 0.59, 0.67, 0.73, 0.78, 0.82, 0.86, 0.9, 0.93, 0.96, 0.99)
End Function

Private Function Get_Tc_Column_M40() As Variant
    Get_Tc_Column_M40 = Array(0.3, 0.38, 0.51, 0.6, 0.68, 0.74, 0.79, 0.84, 0.88, 0.92, 0.95, 0.98, 1.01)
End Function

' Helper to get Tc for a specific grade (interpolating Pt)
Private Function Get_Tc_For_Grade(ByVal Grade As Long, ByVal pt As Double) As Double
    Dim arrTc As Variant
    
    Select Case Grade
        Case 15: arrTc = Get_Tc_Column_M15()
        Case 20: arrTc = Get_Tc_Column_M20()
        Case 25: arrTc = Get_Tc_Column_M25()
        Case 30: arrTc = Get_Tc_Column_M30()
        Case 35: arrTc = Get_Tc_Column_M35()
        Case Else: arrTc = Get_Tc_Column_M40() ' M40 and above
    End Select
    
    Dim arrPt As Variant
    arrPt = Get_Pt_Rows()
    
    ' Clamp Pt
    If pt < 0.15 Then pt = 0.15
    If pt > 3# Then pt = 3#
    
    ' Find interval
    Dim i As Long
    For i = LBound(arrPt) To UBound(arrPt) - 1
        If pt >= arrPt(i) And pt <= arrPt(i + 1) Then
            Get_Tc_For_Grade = M04_Utilities.LinearInterp(pt, CDbl(arrPt(i)), CDbl(arrTc(i)), CDbl(arrPt(i + 1)), CDbl(arrTc(i + 1)))
            Exit Function
        End If
    Next i
    
    ' Fallback (should not reach here due to clamp)
    Get_Tc_For_Grade = arrTc(UBound(arrTc))
End Function

' Public Function to get Tc (Table 19)
' Interpolates for Pt only. Uses nearest lower grade for Fck (conservative).
Public Function Get_Tc_Value(ByVal fck As Double, ByVal pt As Double) As Double
    ' 1. Handle Fck (No interpolation, use nearest lower grade)
    ' Available columns: 15, 20, 25, 30, 35, 40
    
    Dim gradeToUse As Long
    
    If fck >= 40 Then
        gradeToUse = 40
    ElseIf fck >= 35 Then
        gradeToUse = 35
    ElseIf fck >= 30 Then
        gradeToUse = 30
    ElseIf fck >= 25 Then
        gradeToUse = 25
    ElseIf fck >= 20 Then
        gradeToUse = 20
    Else
        gradeToUse = 15 ' Minimum or fallback
    End If
    
    Get_Tc_Value = Get_Tc_For_Grade(gradeToUse, pt)
End Function


' ------------------------------------------------------------------------------
' Table 20: Maximum Shear Stress (Tc_max)
' ------------------------------------------------------------------------------

Public Function Get_TcMax_Value(ByVal fck As Double) As Double
    ' Table 20 Data
    ' M15: 2.5, M20: 2.8, M25: 3.1, M30: 3.5, M35: 3.7, M40+: 4.0
    
    If fck >= 40 Then
        Get_TcMax_Value = 4#
    ElseIf fck <= 15 Then
        Get_TcMax_Value = 2.5
    Else
        ' Interpolate
        Dim x1 As Double, y1 As Double, x2 As Double, y2 As Double
        
        If fck < 20 Then
            x1 = 15: y1 = 2.5: x2 = 20: y2 = 2.8
        ElseIf fck < 25 Then
            x1 = 20: y1 = 2.8: x2 = 25: y2 = 3.1
        ElseIf fck < 30 Then
            x1 = 25: y1 = 3.1: x2 = 30: y2 = 3.5
        ElseIf fck < 35 Then
            x1 = 30: y1 = 3.5: x2 = 35: y2 = 3.7
        Else
            x1 = 35: y1 = 3.7: x2 = 40: y2 = 4#
        End If
        
        Get_TcMax_Value = M04_Utilities.LinearInterp(fck, x1, y1, x2, y2)
    End If
End Function
