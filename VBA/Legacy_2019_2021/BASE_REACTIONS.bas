Attribute VB_Name = "BASE_REACTIONS"
' =============================================================================
' LEGACY CODE - ETABS Base Reactions Export (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Extract base reactions for seismic scaling verification
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.Results.BaseReact() - Get base reactions
'   - mySapModel.Results.Setup.SetCaseSelectedForOutput() - Select load case
'   - mySapModel.Results.Setup.SetComboSelectedForOutput() - Select combo
'   - mySapModel.RespCombo.GetCaseList() - Get combo composition
'   - mySapModel.RespCombo.SetCaseList() - Modify scale factors
'
' =============================================================================

Option Explicit

 Dim myHelper As ETABSv1.cHelper
 Dim myETABSObject As ETABSv1.cOAPI
 Dim mySapModel As ETABSv1.cSapModel
 Dim ModelName As String, ModelPath As String
   'use ret to check return values of API calls
  Dim ret As Long

Dim NumberItems As Long
Dim CNameType() As eCNameType
Dim CName() As String
Dim SF() As Double
Dim Rx_scaled As Double, Ry_scaled As Double
Dim Ex As Double, Ey As Double
'
   Dim NumberLoads As Integer
   Dim LoadType() As String
   Dim LoadName() As String
   
   
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'ATTACH TO ETABS

Sub ATTACH_TO_ETABS_3()

  Set myHelper = New ETABSv1.Helper
  Set myETABSObject = Nothing
  Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
  Set mySapModel = myETABSObject.SapModel

  If ret = 0 Then
    'MsgBox "API script completed successfully."
  Else
    MsgBox "API script FAILED to complete."
  End If

  Exit Sub

ErrHandler:
    MsgBox "Cannot run API script: " & Err.Description

End Sub

Sub check_for_run()
Call ATTACH_TO_ETABS_3
Dim ResultsAvailable As Boolean, Run1 As Long
    Run1 = mySapModel.Analyze.CreateAnalysisModel
    If Run1 = 0 Then ret = mySapModel.Analyze.RunAnalysis
End Sub

Sub Get_Base_Reactions()
' run analysis
Call check_for_run
Worksheets("BASE REACTIONS").Range("B1").ClearContents
Dim Rx_scaled As String, Ry_scaled As String
Dim Rx As String, Ry As String
Dim Ex As Variant, Ey As Variant
Dim j As Integer

Ex = Worksheets("BASE REACTIONS").Range("N4")
Ey = Worksheets("BASE REACTIONS").Range("N5")
Rx = Worksheets("BASE REACTIONS").Range("N6")
Ry = Worksheets("BASE REACTIONS").Range("N7")
Rx_scaled = Worksheets("BASE REACTIONS").Range("N8")
Ry_scaled = Worksheets("BASE REACTIONS").Range("N9")

Call Reset_SCALING_1

Call ATTACH_TO_ETABS_3
''''''''''''''''''''
''''''''SET UNITS'''''''''''''''''
If Worksheets("BASE REACTIONS").Range("G1") = "Ton_m_C" Then
    ret = mySapModel.SetPresentUnits(eUnits_Ton_m_C)
Else
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
End If
''''''''''''''''''''''''''''''''''

 
 'for Base reactions
    Dim NumberResults As Long
    Dim LoadCase() As String
    Dim StepType() As String
    Dim StepNum() As Double
    Dim Fx() As Double
    Dim Fy() As Double
    Dim Fz() As Double
    Dim Mx() As Double
    Dim ParamMy() As Double
    Dim Mz() As Double
    Dim gx As Double
    Dim gy As Double
    Dim gz As Double
 '3)Ex
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
       ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(Ex)
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    For j = 1 To 3
        Worksheets("BASE REACTIONS").Range("F4").Offset(j - 1, 0) = Fx(j - 1)
        Worksheets("BASE REACTIONS").Range("G4").Offset(j - 1, 0) = Fy(j - 1)
    Next j
 '4)EY
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
       ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(Ey)
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    For j = 1 To 3
        Worksheets("BASE REACTIONS").Range("F7").Offset(j - 1, 0) = Fx(j - 1)
        Worksheets("BASE REACTIONS").Range("G7").Offset(j - 1, 0) = Fy(j - 1)
    Next j
    
 '5)Rx_Scaled
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
       ret = mySapModel.Results.Setup.SetComboSelectedForOutput(Rx_scaled)
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    For j = 1 To UBound(Fx) + 1
        Worksheets("BASE REACTIONS").Range("F10").Offset(j - 1, 0) = Fx(j - 1)
        Worksheets("BASE REACTIONS").Range("G10").Offset(j - 1, 0) = Fy(j - 1)
    Next j
    
'6)Ry_Scaled
    ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
    ret = mySapModel.Results.Setup.SetComboSelectedForOutput(Ry_scaled)
    ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    For j = 1 To UBound(Fx) + 1
        Worksheets("BASE REACTIONS").Range("F12").Offset(j - 1, 0) = Fx(j - 1)
        Worksheets("BASE REACTIONS").Range("G12").Offset(j - 1, 0) = Fy(j - 1)
    Next j
Dim Model_Name As String
Model_Name = mySapModel.GetModelFilename(False)
Worksheets("BASE REACTIONS").Range("B1") = Model_Name
End Sub




Sub SCALING_1()
Application.Calculation = xlCalculationManual
Application.ScreenUpdating = False

' run analysis
Dim Rx_scaled As String, Ry_scaled As String
Dim Rx As String, Ry As String
Dim Ex As Variant, Ey As Variant
Dim j As Integer

Ex = Worksheets("BASE REACTIONS").Range("N4")
Ey = Worksheets("BASE REACTIONS").Range("N5")
Rx = Worksheets("BASE REACTIONS").Range("N6")
Ry = Worksheets("BASE REACTIONS").Range("N7")
Rx_scaled = Worksheets("BASE REACTIONS").Range("N8")
Ry_scaled = Worksheets("BASE REACTIONS").Range("N9")

Call Get_Base_Reactions
''''''''''''''''''''
' get scaling factor
Dim Old_SF_X As Double
Dim Old_SF_Y As Double
'1)Rx_scaled
 ret = mySapModel.RespCombo.GetCaseList(Rx_scaled, NumberItems, CNameType, CName, SF)
 'write in excel
    Old_SF_X = SF(0)
 
' '2)Ry_scaled
 ret = mySapModel.RespCombo.GetCaseList(Ry_scaled, NumberItems, CNameType, CName, SF)
 'write in excel
    Old_SF_Y = SF(0)
 
 
Dim SF_NEW_X As Double
Dim SF_NEW_Y As Double
'SCALING
'1)Scale Rx_scaled
    SF_NEW_X = (Old_SF_X * (Worksheets("BASE REACTIONS").Range("F4")) / (Worksheets("BASE REACTIONS").Range("F10")))
    SF_NEW_X = Abs(SF_NEW_X)
    If SF_NEW_X < 1 Then SF_NEW_X = 1
        ret = mySapModel.RespCombo.GetCaseList(Rx_scaled, NumberItems, CNameType, CName, SF)
        ret = mySapModel.RespCombo.SetCaseList(Rx_scaled, eCNameType_LoadCase, Rx, SF_NEW_X)

'2)scale Ry_scaled
    SF_NEW_Y = (Old_SF_Y * (Worksheets("BASE REACTIONS").Range("G7")) / (Worksheets("BASE REACTIONS").Range("G12")))
    SF_NEW_Y = Abs(SF_NEW_Y)
    If SF_NEW_Y < 1 Then SF_NEW_Y = 1
        ret = mySapModel.RespCombo.GetCaseList(Ry_scaled, NumberItems, CNameType, CName, SF)
        ret = mySapModel.RespCombo.SetCaseList(Ry_scaled, eCNameType_LoadCase, Ry, SF_NEW_Y)
        

        
'MsgBox ("DONE SCALING")

Call Get_Base_Reactions
Dim Model_Name As String
Model_Name = mySapModel.GetModelFilename(False)
Worksheets("BASE REACTIONS").Range("B1") = Model_Name
Application.Calculation = xlCalculationAutomatic
Application.ScreenUpdating = True

End Sub

Sub Reset_SCALING_1()
Worksheets("BASE REACTIONS").Range("F4:G13").ClearContents
'Range("F21:F25").ClearContents
End Sub

Sub Model_Name()
Call ATTACH_TO_ETABS_3
Dim Model_Name As String
Model_Name = mySapModel.GetModelFilename(False)
End Sub
