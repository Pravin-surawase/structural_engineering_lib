Attribute VB_Name = "torsional_irregularity"
' =============================================================================
' LEGACY CODE - ETABS Torsional Irregularity Check (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Extract joint displacements for torsional irregularity verification
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.Analyze.RunAnalysis() - Run analysis
'   - mySapModel.PointObj.GetNameFromLabel() - Convert label to internal name
'   - mySapModel.Results.JointDispl() - Get joint displacements
'   - mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
'   - mySapModel.Results.Setup.SetCaseSelectedForOutput()
'
' =============================================================================

Option Explicit

 Dim myHelper As ETABSv1.cHelper
 Dim myETABSObject As ETABSv1.cOAPI
 Dim mySapModel As ETABSv1.cSapModel
 Dim ModelName As String, ModelPath As String
   'use ret to check return values of API calls
  Dim ret As Long


Sub ATTACH_TO_ETABS3()
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

Sub Jt_Disp()
Call ATTACH_TO_ETABS3
Dim i As Integer, j As Integer
Dim Jtno As String, Story As Variant, StepNumber As Variant
Dim LoadCase1 As String
LoadCase1 = Worksheets("TORSIONAL IRREGULARITY").Range("B1")
StepNumber = Worksheets("TORSIONAL IRREGULARITY").Range("D2")
ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    Dim Name As String
    Dim ItemTypeElm As eItemTypeElm
    Dim NumberResults As Long
    Dim Obj() As String
    Dim Elm() As String
    Dim LoadCase() As String
    Dim StepType() As String
    Dim StepNum() As Double
    Dim U1() As Double
    Dim U2() As Double
    Dim U3() As Double
    Dim R1() As Double
    Dim R2() As Double
    Dim R3() As Double
 'Run model
    ret = mySapModel.Analyze.RunAnalysis()
'deselect all cases and combos
    ret = mySapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

'set case selected for output
    ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(LoadCase1)
    For i = 1 To 8
       Story = Worksheets("TORSIONAL IRREGULARITY").Range("C" & i + 5)
'''''''''''''''''''''''''''''''' JOINT 1'''''''''''''''''''
        Jtno = Worksheets("TORSIONAL IRREGULARITY").Range("D" & i + 5)
        ret = mySapModel.PointObj.GetNameFromLabel(Jtno, Story, Name)
        ret = mySapModel.Results.JointDispl(Name, ItemTypeElm = eItemTypeElm_Element, NumberResults, Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
        If LoadCase1 = "EY" Then
            Worksheets("TORSIONAL IRREGULARITY").Range("E" & i + 5) = U2(StepNumber - 1)
        Else
             Worksheets("TORSIONAL IRREGULARITY").Range("E" & i + 5) = U1(StepNumber - 1)
        End If
''''''''''''''''''''''''''''''''' JOINT 2'''''''''''''''''''
        Jtno = Worksheets("TORSIONAL IRREGULARITY").Range("F" & i + 5)
    'get area object data
        ret = mySapModel.PointObj.GetNameFromLabel(Jtno, Story, Name)
    'get joint displacements
        ret = mySapModel.Results.JointDispl(Name, ItemTypeElm = eItemTypeElm_Element, NumberResults, Obj, Elm, LoadCase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
    'diplacement
        If LoadCase1 = "EY" Then
           Worksheets("TORSIONAL IRREGULARITY").Range("G" & i + 5) = U2(StepNumber - 1)
        Else
           Worksheets("TORSIONAL IRREGULARITY").Range("G" & i + 5) = U1(StepNumber - 1)
        End If
    Next i
End Sub
