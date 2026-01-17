Attribute VB_Name = "SCALING"
' =============================================================================
' LEGACY CODE - ETABS Response Spectrum Scaling (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Automate response spectrum scaling to match static base shear
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.RespCombo.GetCaseList() - Get combo contents and scale factors
'   - mySapModel.RespCombo.SetCaseList() - Set scale factors
'   - mySapModel.Results.BaseReact() - Get base reactions
'   - mySapModel.InitializeNewModel() - Create new model
'   - mySapModel.File.newgridonly() - New grid-only model
'   - mySapModel.LoadPatterns.Add() - Add load pattern
'
' =============================================================================

Option Explicit

 Dim myHelper As ETABSv1.cHelper
 Dim myETABSObject As ETABSv1.cOAPI
 Dim mySapModel As ETABSv1.cSapModel
 Dim ModelName As String, ModelPath As String
   'use ret to check return values of API calls
  Dim ret As Long
  Dim NewGrid As Integer, LoadPattern As Integer, RunAnalysis As Integer
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
Sub ATTACH_TO_ETABS()

  'full path to the model
  'set it to the desired path of your model
'  Dim ModelDirectory As String
'  ModelDirectory = "C:\Users\psurawase\Desktop\Pravin Training\Study\Excel for study\ETABS API\Etabs Models"
'  If Len(Dir(ModelDirectory, vbDirectory)) = 0 Then
'    MkDir ModelDirectory
'  End If
'
'  ModelName = "SCALING_1.1.edb"
'
'  ModelPath = ModelDirectory & Application.PathSeparator & ModelName

  'create API helper object
'  Dim myHelper As ETABSv1.cHelper
  Set myHelper = New ETABSv1.Helper

  'dimension the ETABS Object as cOAPI type
'  Dim myETABSObject As ETABSv1.cOAPI
  Set myETABSObject = Nothing

    'attach to a running instance of ETABS
    'get the active ETABS object
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")


  'get a reference to cSapModel to access all API classes and functions
'  Dim mySapModel As ETABSv1.cSapModel
  Set mySapModel = myETABSObject.SapModel

If NewGrid = 2 Then
    ret = mySapModel.InitializeNewModel(eUnits_Ton_m_C)
    ret = mySapModel.File.newgridonly(4, 4, 4, 4, 4, 4, 4)
Else
End If

If LoadPattern = 2 Then
    ret = mySapModel.LoadPatterns.Add("Ex", eLoadPatternType_Quake, 0, True)
Else
End If

If RunAnalysis = 2 Then
    ret = mySapModel.Analyze.RunAnalysis
Else
End If




'  'clean up variables
'    Set mySapModel = Nothing
'    Set myETABSObject = Nothing
    'save mdoel
If RunAnalysis = 0 Then
  ret = mySapModel.File.Save(ModelPath)
Else
End If

    
  If ret = 0 Then
    'MsgBox "API script completed successfully."
  Else
    MsgBox "API script FAILED to complete."
  End If

  Exit Sub

ErrHandler:
    MsgBox "Cannot run API script: " & Err.Description

End Sub

Sub newgridonly()
NewGrid = 2
Call ATTACH_TO_ETABS
  'initialize model
'ret = mySapModel.InitializeNewModel(eUnits_Ton_m_C)
'ret = mySapModel.File.newgridonly(4, 4, 4, 4, 4, 4, 4)

End Sub
Sub load_pattern()
LoadPattern = 2
Call ATTACH_TO_ETABS
'ret = mySapModel.LoadPatterns.Add("Ex", eLoadPatternType_Quake, 0, True)
ret = mySapModel.LoadPatterns.AutoSeismic


End Sub
Sub Load_cases()



End Sub
'define variable for scaling
'
'Dim NumberItems As Integer
'Dim CNameType() As eCNameType
'Dim CName() As String
'Dim SF() As Double
'Dim Rx_scaled As Double, Ry_scaled As Double
'Dim Ex As Double, Ey As Double
' for Load cases
'   Dim NumberLoads As Integer
'   Dim LoadType() As String
'   Dim LoadName() As String
  
  


Sub SCALING()
' run analysis
Dim Rx_scaled As String, Ry_scaled As String
Dim Ex1 As Variant, Ey1 As Variant
Rx_scaled = Sheet1.Range("B22")
Ry_scaled = Sheet1.Range("B25")
Ex1 = Sheet1.Range("B21")
Ey1 = Sheet1.Range("B24")
Call reset_SCALING
RunAnalysis = 2
Call ATTACH_TO_ETABS

ret = mySapModel.SetPresentUnits(eUnits_Ton_m_C)
' get scaling factor
'1)Rx_scaled
 ret = mySapModel.RespCombo.GetCaseList(Rx_scaled, NumberItems, CNameType, CName, SF)
 'write in excel
 Worksheets("sheet1").Range("F22") = SF
 
' '2)Ry_scaled
 ret = mySapModel.RespCombo.GetCaseList(Ry_scaled, NumberItems, CNameType, CName, SF)
 'write in excel
 Worksheets("sheet1").Range("F25") = SF
 
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
   'deselect all cases and combos
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

   'set case selected for output
       ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(Ex1)

   'get base reactions
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    'write in excel
    Worksheets("sheet1").Range("C21") = Fx(1)
 '4)EY
   'deselect all cases and combos
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

   'set case selected for output
       ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(Ey1)

   'get base reactions
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    'write in excel
    Worksheets("sheet1").Range("C24") = Fy(1)
    
     '5)Rx_Scaled
   'deselect all cases and combos
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

   'set case selected for output
       ret = mySapModel.Results.Setup.SetComboSelectedForOutput(Rx_scaled)

   'get base reactions
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    'write in excel
    Worksheets("sheet1").Range("C22") = Fx(0)
   ' 6)Ry_Scaled
   'deselect all cases and combos
       ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

   'set case selected for output
       ret = mySapModel.Results.Setup.SetComboSelectedForOutput(Ry_scaled)

   'get base reactions
       ret = mySapModel.Results.BaseReact(NumberResults, LoadCase, StepType, StepNum, Fx, Fy, Fz, Mx, ParamMy, Mz, gx, gy, gz)
    'write in excel
    Worksheets("sheet1").Range("C25") = Fy(0)
  Dim SF_1 As Double
  
'SCALING
'2)ScaleRy_scaled
SF_1 = Worksheets("Sheet1").Range("G25")
        ret = mySapModel.RespCombo.GetCaseList(Ry_scaled, NumberItems, CNameType, CName, SF)
        ret = mySapModel.RespCombo.SetCaseList(Ry_scaled, eCNameType_LoadCase, "RY", SF_1)

'1)scale Rx_scaled
SF_1 = Worksheets("Sheet1").Range("G22")
        ret = mySapModel.RespCombo.GetCaseList(Rx_scaled, NumberItems, CNameType, CName, SF)
        ret = mySapModel.RespCombo.SetCaseList(Rx_scaled, eCNameType_LoadCase, "RX", SF_1)
        

        
MsgBox ("DONE SCALING")

 ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
 ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(Ex1)
 ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(Ey1)
 ret = mySapModel.Results.Setup.SetComboSelectedForOutput(Ry_scaled, True)
 ret = mySapModel.Results.Setup.SetComboSelectedForOutput(Rx_scaled, True)
End Sub

Sub reset_SCALING()
Range("C21:C25").ClearContents
Range("F21:F25").ClearContents
End Sub
