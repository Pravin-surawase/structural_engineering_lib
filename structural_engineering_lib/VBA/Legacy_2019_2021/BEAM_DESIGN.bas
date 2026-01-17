Attribute VB_Name = "BEAM_DESIGN"
' =============================================================================
' LEGACY CODE - ETABS Beam Design Results (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Extract beam reinforcement design results and export to Excel
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.DesignConcrete.StartDesign() - Start design
'   - mySapModel.DesignConcrete.GetSummaryResultsBeam() - Beam results
'   - mySapModel.DatabaseTables.GetAvailableTables() - Get table list
'   - mySapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay()
'   - mySapModel.DatabaseTables.ShowTablesInExcel() - Export to Excel
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

Sub ATTACH_TO_ETABS2()


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

Sub BEAM_REINF()
Call ATTACH_TO_ETABS2
'''''''''''''''''''''''''''''''
 
   Dim Name As String
   Dim NumberItems As Long
   Dim FrameName() As String
   Dim Location() As Double
   Dim TopCombo() As String
   Dim TopArea() As Double
   Dim BotCombo() As String
   Dim BotArea() As Double
   Dim VmajorCombo() As String
   Dim VmajorArea() As Double
   Dim TLCombo() As String
   Dim TLArea() As Double
   Dim TTCombo() As String
   Dim TTArea() As Double
   Dim ErrorSummary() As String
   Dim WarningSummary() As String

''''''''''''''''''''''''''''''''''
'start concrete design
   ret = mySapModel.DesignConcrete.StartDesign()

'get summary result data
   ret = mySapModel.DesignConcrete.GetSummaryResultsBeam("20", NumberItems, FrameName, Location, TopCombo, TopArea, BotCombo, BotArea, VmajorCombo, VmajorArea, TLCombo, TLArea, TTCombo, TTArea, ErrorSummary, WarningSummary)
  

End Sub

Sub beam_longRebarData()
Call ATTACH_TO_ETABS2
''''''''''''''''''''''''''''''''''''''''
    Dim Name As String
    Dim NumberRebarSets As Long
    Dim BarSizeName() As String
    Dim BarArea() As Double
    Dim NumberBars() As Long
    Dim Location() As String
    Dim ClearCover() As Double
    Dim StartCoord1() As Double
    Dim BarLength() As Double
    Dim BendingAngleStart() As Double
    Dim BendingAngleEnd() As Double
    Dim RebarSetGUID() As String
'''''''''''''''''''''''''''''''''''''''''
  '  ret = mySapModel.Detailing.GetBeamLongRebarData("20", NumberRebarSets, BarSizeName, BarArea, NumberBars, Location, ClearCover, StartCoord1, BarLength, BendingAngleStart, BendingAngleEnd, RebarSetGUID)
    
''''''''''''''''''''''''''''''''''''''''''
    Dim NumberTables As Long
    Dim TableKey() As String
    Dim TableName() As String
    Dim ImportType() As Long
  ret = mySapModel.DatabaseTables.GetAvailableTables(NumberTables, TableKey, TableName, ImportType)
    
    
    
    
    
 '''''''''''''''''''''''''''''''''''''''
    Dim TableKeyList(0) As String
    Dim WindowHandle As Integer
    TableKeyList(0) = TableKey(20)
  
   ' ret = mySapModel.DatabaseTables.ShowTablesInExcel(TableKeyList, WindowHandle)
'''''''''''''''''''''''''''''''''''''''
     Dim LoadCombinationList(1) As String
     Dim LoadCaseList(1) As String
    LoadCombinationList(0) = "Rx_scaled"
    LoadCombinationList(1) = "Ry_scaled"
    LoadCaseList(0) = "Ex"
    LoadCaseList(1) = "Ey"
   ret = mySapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(LoadCombinationList)
   ret = mySapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(LoadCaseList)
   ret = mySapModel.DatabaseTables.ShowTablesInExcel(TableKeyList, WindowHandle)

End Sub
