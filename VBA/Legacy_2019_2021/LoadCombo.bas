Attribute VB_Name = "LoadCombo"
' =============================================================================
' LEGACY CODE - ETABS Load Combination Management (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Read/write load combinations between Excel and ETABS
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.RespCombo.GetNameList() - Get all combo names
'   - mySapModel.RespCombo.GetCaseList() - Get cases in combo
'   - mySapModel.RespCombo.GetTypeCombo() - Get combo type
'   - mySapModel.RespCombo.Delete() - Delete combo
'   - mySapModel.RespCombo.Add() - Add new combo
'   - mySapModel.RespCombo.SetCaseList() - Add case to combo
'
' =============================================================================

Option Explicit



 Dim myHelper As ETABSv1.cHelper
 Dim myETABSObject As ETABSv1.cOAPI
 Dim mySapModel As ETABSv1.cSapModel
 Dim ModelName As String, ModelPath As String
   'use ret to check return values of API calls
  Dim ret As Long


Sub ATTACH_TO_ETABS1()

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





'  'clean up variables
'    Set mySapModel = Nothing
'    Set myETABSObject = Nothing
    'save mdoel

  'ret = mySapModel.File.Save(ModelPath)


    
  If ret = 0 Then
    'MsgBox "API script completed successfully."
  Else
    MsgBox "API script FAILED to complete."
  End If

  Exit Sub

ErrHandler:
    MsgBox "Cannot run API script: " & Err.Description

End Sub



Sub reset_LoadCases()

Worksheets("LOAD_COMBINATION").Range("B6:B200").ClearContents

End Sub

Sub Reset_LoadCombo()

Worksheets("LOAD COMBINATIONS").Range("A4:YZ2000").ClearContents

End Sub


Sub Load_Combination()

Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Call ATTACH_TO_ETABS1
Call Reset_LoadCombo

Dim i As Integer, j As Integer
'Define Variable to get Load combination names
Dim NumberNames As Long
Dim MyName() As String
'for type
Dim ComboType As Long
Dim type1 As String

'define variables to get cases in a conbo
Dim NumberItems As Long
Dim CNameType() As eCNameType
Dim CName() As String
Dim SF() As Double

'Get Names of each combo defined
 ret = mySapModel.RespCombo.GetNameList(NumberNames, MyName)
 For i = 1 To NumberNames
     Worksheets("LOAD COMBINATIONS").Range("A" & i + 3) = MyName(i - 1)
 Next i
'Get cases in each combo with SF
' ret = mySapModel.RespCombo.GetCaseList("COMB1", NumberItems, CNameType, CName, SF)
 For i = 1 To NumberNames
    ret = mySapModel.RespCombo.GetCaseList(MyName(i - 1), NumberItems, CNameType, CName, SF)
        For j = 1 To NumberItems
            Worksheets("LOAD COMBINATIONS").Range("C" & i + 3).Offset(0, (j - 1) * 3) = SF(j - 1)
            Worksheets("LOAD COMBINATIONS").Range("D" & i + 3).Offset(0, (j - 1) * 3) = CName(j - 1)
            Worksheets("LOAD COMBINATIONS").Range("E" & i + 3).Offset(0, (j - 1) * 3) = CNameType(j - 1)
        Next j
 
 Next i
  
    'get combo type
 For i = 1 To NumberNames
      ret = mySapModel.RespCombo.GetTypeCombo(MyName(i - 1), ComboType)
      If ComboType = 0 Then
         type1 = "Linear Additive"
      ElseIf ComboType = 1 Then
        type1 = "Envelope"
      ElseIf ComboType = 2 Then
        type1 = "Abosolute Additive"
      ElseIf ComboType = 3 Then
        type1 = "SRSS"
      ElseIf ComboType = 4 Then
        type1 = "Range Additive"
      Else
        type1 = "Unknown"
      End If

     Worksheets("LOAD COMBINATIONS").Range("B" & i + 3) = type1
 Next i
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
End Sub


Sub Update_Combo()
Dim i As Integer, j As Integer
Call ATTACH_TO_ETABS1


'Define Variable to get Load combination names
Dim NumberNames As Long
Dim MyName() As String


'Get Names of each combo defined
ret = mySapModel.RespCombo.GetNameList(NumberNames, MyName)
For i = 1 To NumberNames - 1
    Worksheets("LOAD COMBINATIONS").Range("A" & i + 3) = MyName(i - 1)
Next i


For i = 0 To NumberNames - 1
    ret = mySapModel.RespCombo.Delete(MyName(i))
Next i




End Sub

Sub update_in_etabs()
Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Call ATTACH_TO_ETABS1
Dim i As Integer, j As Integer, k As Integer
Dim cases_total As Integer
'Add Combo and type
Dim Name_From_Excel As String
Dim ComboType_From_Excel As String
Dim ComboType_In_etabs As Long, type1 As Integer


cases_total = WorksheetFunction.CountA(Worksheets("LOAD COMBINATIONS").Range("A4:A500"))

Dim combinations() As String
ReDim combinations(cases_total)
For k = 1 To cases_total
    combinations(k) = Worksheets("LOAD COMBINATIONS").Range("A3").Offset(k, 0)
Next k
''''''''''''''''''''''''''''''
'Delete previous Combo

'Define Variable to get Load combination names
Dim NumberNames As Long
Dim MyName() As String
ret = mySapModel.RespCombo.GetNameList(NumberNames, MyName)
For j = 0 To UBound(MyName)
    ret = mySapModel.RespCombo.Delete(MyName(j))
Next j
  
  
  
'Add COMBO and set case
For i = 1 To cases_total

    'Add Combo and type
    Name_From_Excel = Worksheets("LOAD COMBINATIONS").Range("A" & 3 + i)
    ComboType_From_Excel = Worksheets("LOAD COMBINATIONS").Range("B" & 3 + i)
          If ComboType_From_Excel = "Linear Additive" Then
            ComboType_In_etabs = 0
          ElseIf ComboType_From_Excel = "Envelope" Then
            ComboType_In_etabs = 1
          ElseIf ComboType_From_Excel = "Abosolute Additive" Then
            ComboType_In_etabs = 2
          ElseIf ComboType_From_Excel = "SRSS" Then
            ComboType_In_etabs = 3
          ElseIf ComboType_From_Excel = "Range Additive" Then
            ComboType_In_etabs = 4
          Else
            ComboType_In_etabs = 6
          End If
    
    ret = mySapModel.RespCombo.Add(Name_From_Excel, ComboType_In_etabs)


    'Calculate number of cases
    For j = 1 To 100
        ''''''''''''''''''''''''''''''''''''''''''
        'loadcase or combo
        Dim case_Type_1 As String
        Dim case_Name_1 As String
        Dim SF_1 As Double
        
       'Load case Name
        case_Name_1 = Worksheets("LOAD COMBINATIONS").Range("D" & i + 3).Offset(0, (j - 1) * 3)
        SF_1 = Worksheets("LOAD COMBINATIONS").Range("C" & i + 3).Offset(0, (j - 1) * 3)
'''''''''''''''''''''''''''''''''''''''
       'Load TYPE
       For k = 1 To UBound(combinations)
            If case_Name_1 = combinations(k) Then Worksheets("LOAD COMBINATIONS").Range("E" & i + 3).Offset(0, (j - 1) * 3) = 1
       Next k
'''''''''''''''''''''''''''''''''''''''
       
        If Worksheets("LOAD COMBINATIONS").Range("D" & i + 3).Offset(0, (j - 1) * 3) = "" Then
                GoTo next_Combo
        ElseIf Worksheets("LOAD COMBINATIONS").Range("E" & i + 3).Offset(0, (j - 1) * 3) = 0 Then
                case_Type_1 = "LoadCase"
        ElseIf Worksheets("LOAD COMBINATIONS").Range("E" & i + 3).Offset(0, (j - 1) * 3) = 1 Then
                case_Type_1 = "LoadCombo"
        End If
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        
        If case_Type_1 = "LoadCase" Then
           ' ret = mySapModel.RespCombo.SetCaseList_1(Name_From_Excel, eCNameType_LoadCase = 0, case_Name_1, 0, SF_1)
            ret = mySapModel.RespCombo.SetCaseList(Name_From_Excel, eCNameType_LoadCase, case_Name_1, SF_1)
        ElseIf case_Type_1 = "LoadCombo" Then
            'ret = mySapModel.RespCombo.SetCaseList_1(Name_From_Excel, eCNameType_LoadCombo = 1, case_Name_1, 0, SF_1)
            ret = mySapModel.RespCombo.SetCaseList(Name_From_Excel, eCNameType_LoadCombo, case_Name_1, SF_1)
           
        End If
    Next j
    
ret = mySapModel
next_Combo:
Next i
Call FORMAT1
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic

End Sub


Sub FORMAT1()

Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Dim k As Integer

For k = 4 To 300

   Range(k & ":" & k).Select
   
    With Selection.Interior
        .Pattern = xlNone
        .TintAndShade = 0
        .PatternTintAndShade = 0
    End With
    Rows("8:8").Select
    With Selection.Interior
        .Pattern = xlNone
        .TintAndShade = 0
        .PatternTintAndShade = 0
    End With
    Range("C10").Select
      k = k + 1
      
    Range(k & ":" & k).Select
    Selection.Style = "20% - Accent3"
  
Next k
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
End Sub
