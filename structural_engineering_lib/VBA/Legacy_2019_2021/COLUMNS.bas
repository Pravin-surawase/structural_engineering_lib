Attribute VB_Name = "COLUMNS"
' =============================================================================
' LEGACY CODE - ETABS Column Design & Detailing (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Complete column design workflow with automatic reinforcement selection
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.FrameObj.GetAllFrames() - Get all frames at once (efficient!)
'   - mySapModel.DesignConcrete.GetResultsAvailable - Check design status
'   - mySapModel.DesignConcrete.StartDesign() - Run concrete design
'   - mySapModel.DesignConcrete.GetSummaryResultsColumn() - Column design results
'   - mySapModel.PropFrame.GetTypeRebar() - Identify beam vs column
'   - mySapModel.PropFrame.GetRectangle() - Get section dimensions
'   - mySapModel.FrameObj.GetLabelFromName() - Get user label
'   - mySapModel.FrameObj.SetSection() - Update section
'   - mySapModel.Diaphragm.GetNameList() - Get diaphragm info
'
' =============================================================================

Option Explicit
Dim myHelper As ETABSv1.cHelper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel
Dim ModelName As String, ModelPath As String
Dim ret As Long

Dim Column_Data() As Variant, warning() As Variant
Dim rows_count As Integer
Dim Colum_XYZ() As Variant
Dim col_length() As Variant

''''''''''''''''''''''''''''''''''''''''''''''''''
'              Attach To ETABS                   '
''''''''''''''''''''''''''''''''''''''''''''''''''
Sub ATTACH_TO_ETABS_COLUMNS()
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
Call ATTACH_TO_ETABS_COLUMNS
Dim ResultsAvailable As Boolean, Run1 As Long
    Run1 = mySapModel.Analyze.CreateAnalysisModel
    If Run1 = 0 Then ret = mySapModel.Analyze.RunAnalysis
    
    ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
    If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
End Sub

Sub Column_Detailing()
Call check_for_run

ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
Dim i As Integer, j As Integer
    
'Get All Frames
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropName() As String
    Dim StoryName() As String
    Dim PointName1() As String
    Dim PointName2() As String
    Dim Point1X() As Double
    Dim Point1Y() As Double
    Dim Point1Z() As Double
    Dim Point2X() As Double
    Dim Point2Y() As Double
    Dim Point2Z() As Double
    Dim Angle() As Double
    Dim Offset1X() As Double
    Dim Offset2X() As Double
    Dim Offset1Y() As Double
    Dim Offset2Y() As Double
    Dim Offset1Z() As Double
    Dim Offset2Z() As Double
    Dim CardinalPoint() As Long

      ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, Angle _
            , Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'
    
   Dim Name As String
   Dim NumberItems As Long
   Dim FrameName() As String
   Dim MyOption() As Long
   Dim Location() As Double
   Dim PMMCombo() As String
   Dim PMMArea() As Double
   Dim PMMRatio() As Double
   Dim VmajorCombo() As String
   Dim AVmajor() As Double
   Dim VminorCombo() As String
   Dim AVminor() As Double
   Dim ErrorSummary() As String
   Dim WarningSummary() As String

   Dim Frame_Type As Long
   Dim Frame_1 As String
   
   Dim Label As String
   Dim story_from_Label As String
   ''''' Get Section sizes''''
    Dim FileName As String
    Dim MatProp As String
    Dim t3 As Double
    Dim t2 As Double
    Dim Color As Long
    Dim Notes As String
    Dim GUID As String
    Dim Col_depth As Double, Col_width As Double
    
       
    
        '' run model check
        ' ret = mySapModel.Analyze.CreateAnalysisModel
    Dim ResultsAvailable As Boolean
       'check if design results are available
        ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
        If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
        
For i = 0 To NumberNames - 1
   ret = mySapModel.DesignConcrete.GetSummaryResultsColumn(MyName(i), NumberItems, FrameName, MyOption, Location, PMMCombo, PMMArea, PMMRatio, VmajorCombo, AVmajor, VminorCombo, AVminor, ErrorSummary, WarningSummary, eItemType_Objects)

'''' Beam or column identify
   ret = mySapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)
   If Frame_Type = 1 Then
      Frame_1 = "Column"
   ElseIf Frame_Type = 2 Then
      Frame_1 = "Beam"
   Else
      Frame_1 = "None"
   End If
''''' Get Section sizes''''
    ret = mySapModel.PropFrame.GetRectangle(PropName(i), FileName, MatProp, t3, t2, Color, Notes, GUID)
    Col_depth = t3
    Col_width = t2
    
    If Frame_1 = "Column" Then
       j = j + 1
       ReDim Preserve Column_Data(9, j)
       Column_Data(1, j) = StoryName(i)
       ret = mySapModel.FrameObj.GetLabelFromName(MyName(i), Label, story_from_Label)
       Column_Data(2, j) = Label
       Column_Data(3, j) = MyName(i)
       Column_Data(4, j) = PropName(i)
       Column_Data(5, j) = Col_width * 1000 ' to convert in mm
       Column_Data(6, j) = Col_depth * 1000
       Column_Data(7, j) = (WorksheetFunction.Max(PMMArea)) * 10000 ' to convert in cm2
       Column_Data(8, j) = (WorksheetFunction.Max(PMMArea) / (Col_depth * Col_width))
'      Column_Data(9, j) = Point1X(i)
'      Column_Data(10, j) = Point1Y(i)
'      Column_Data(11, j) = Point1Z(i)
   
      ReDim Preserve Colum_XYZ(3, j)
        Colum_XYZ(1, j) = Point1X(i)
        Colum_XYZ(2, j) = Point1Y(i)
        Colum_XYZ(3, j) = Point1Z(i)
    ReDim Preserve col_length(j)
        col_length(j) = Point2Z(i) - Point1Z(i)
      ReDim Preserve warning(1, j)
        warning(1, j) = WarningSummary
    End If
Next i
    

rows_count = j - 1
End Sub


Sub Provide_Reinforcement()
Application.ScreenUpdating = False
Application.Calculation = xlCalculationManual
Dim i As Integer, j As Integer
Dim k As Integer, M As Integer
Dim tw As Workbook
Dim CWS As Worksheet
Dim Min_BARS As Integer, Max_BARS As Integer
Dim Differene() As Variant, reinf_Prov As Variant

 'length of column

' to get minimum diff
Dim Reinf() As Variant
Dim Bar_dia_of_Reinf() As Variant
Dim No_of_Bars_Reinf() As Variant
''temp
Dim Minimum_Found As Variant

Set tw = ThisWorkbook
Set CWS = tw.Worksheets("Columns")
''''''''''''''''''''
Call RESET_BEFORE_Run
Call Column_Detailing
'Call SORT_1
Dim pi As Variant
Dim BAR_DIA_ALL(7) As Variant, Bar_DIA_Count As Variant
pi = WorksheetFunction.pi
BAR_DIA_ALL(1) = 12
BAR_DIA_ALL(2) = 16
BAR_DIA_ALL(3) = 20
BAR_DIA_ALL(4) = 25
BAR_DIA_ALL(5) = 32
BAR_DIA_ALL(6) = 22
BAR_DIA_ALL(7) = 28

''''''''''''''''''''
'Application.ScreenUpdating = True
'Application.Calculation = xlCalculationAutomatic

tw.Activate

For i = 1 To rows_count + 1
    For j = 1 To UBound(Column_Data) - 1
        CWS.Range("A3").Offset(i - 1, j - 1) = Column_Data(j, i)
        CWS.Range("P3").Offset(i - 1, 0) = Colum_XYZ(3, i)
        CWS.Range("T3").Offset(i - 1, 0) = warning(1, i)
        CWS.Range("Y3").Offset(i - 1, 0) = col_length(i)
    Next j
    

    Min_BARS = (WorksheetFunction.RoundUp(Column_Data(5, i) / 150, 0) + WorksheetFunction.RoundUp(Column_Data(6, i) / 150 + 1, 0)) * 2 - 4
    Max_BARS = (WorksheetFunction.RoundUp(Column_Data(5, i) / 100, 0) + WorksheetFunction.RoundUp(Column_Data(6, i) / 100, 0)) * 2 - 4
'''''''''''''''''''''''''''''''''''''''''''''
    ReDim Differene(UBound(BAR_DIA_ALL), (Max_BARS - Min_BARS) / 2 + 1)
    ReDim Reinf(M)
    ReDim Bar_dia_of_Reinf(M)
    ReDim No_of_Bars_Reinf(M)
    
     For Bar_DIA_Count = 1 To UBound(BAR_DIA_ALL)
         For k = 1 To (Max_BARS - Min_BARS) / 2 + 1
                reinf_Prov = ((pi) * (1 / 4) * (BAR_DIA_ALL(Bar_DIA_Count)) ^ 2 * (Min_BARS + (k - 1) * 2))
                Differene(Bar_DIA_Count, k) = Column_Data(7, i) - reinf_Prov / 100
                
                ' add total matrix

                M = M + 1
                ReDim Preserve Reinf(M - 1)
                ReDim Preserve Bar_dia_of_Reinf(M - 1)
                ReDim Preserve No_of_Bars_Reinf(M - 1)
                No_of_Bars_Reinf(M - 1) = Min_BARS + (k - 1) * 2  ' No of Bars
                Bar_dia_of_Reinf(M - 1) = BAR_DIA_ALL(Bar_DIA_Count) ' Bar Dia
                Reinf(M - 1) = Differene(Bar_DIA_Count, k)  ' Reinf Diff
               
         Next k
    
     Next Bar_DIA_Count
      
   For k = 1 To M
     If Reinf(k - 1) >= 0 Then Reinf(k - 1) = -200
    ' Minimum_Found = WorksheetFunction.Max(TMat)
     
     
   Next k
     Minimum_Found = WorksheetFunction.Max(Reinf)
    For k = 1 To M
        If Reinf(k - 1) = Minimum_Found Then
        
            CWS.Range("A3").Offset(i - 1, j) = No_of_Bars_Reinf(k - 1)
            CWS.Range("A3").Offset(i - 1, j + 1) = Bar_dia_of_Reinf(k - 1)
            GoTo NEXT_COLUMN
        End If
    Next k
            CWS.Range("A3").Offset(i - 1, j) = " Check"
            CWS.Range("A3").Offset(i - 1, j + 1) = " Check"
        
     
NEXT_COLUMN:
M = 0
Next i
''''''
'Call Column_Graph
Call Total_Steel
Call SORT_1
Call Drop_list
Call sections_available
Call GROUPING
Call diaphragm1
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
End Sub

''''''''''''''''''''
Sub Column_Graph()
Dim i As Integer, j As Integer
Dim tw As Workbook
Dim CWS As Worksheet
Set tw = ThisWorkbook
Set CWS = tw.Worksheets("Columns")
Call clear_xyz
Call Column_Detailing

    For j = 1 To rows_count + 1
      
        CWS.Range("AG3").Offset(j - 1, 0) = Column_Data(2, j)
        CWS.Range("AH3").Offset(j - 1, 0) = Colum_XYZ(1, j)
        CWS.Range("AI3").Offset(j - 1, 0) = Colum_XYZ(2, j)
        CWS.Range("AJ3").Offset(j - 1, 0) = Colum_XYZ(3, j)
        CWS.Range("AK3").Offset(j - 1, 0) = Colum_XYZ(UBound(Colum_XYZ), j)
    Next j
    

End Sub

Sub clear_xyz()
Dim i As Integer, j As Integer
Dim tw As Workbook
Dim CWS As Worksheet
Set tw = ThisWorkbook
Set CWS = tw.Worksheets("Columns")
CWS.Range("AG3:AK1000").ClearContents
End Sub
Sub Total_Steel()
Dim i As Integer, j As Integer
Dim tw As Workbook
Dim CWS As Worksheet
Set tw = ThisWorkbook
Set CWS = tw.Worksheets("Columns")
Dim Bar_Dia, NO_of_Bars As Integer
Dim Length As Double, Steel As Double
  For i = 1 To rows_count + 1
        Bar_Dia = CWS.Range("K" & i + 2)
        NO_of_Bars = CWS.Range("J" & i + 2)
        Length = CWS.Range("Y" & i + 2)
        Steel = ((Bar_Dia) ^ 2) * NO_of_Bars * Length / 162
        CWS.Range("Z" & i + 2) = Steel
Next i
End Sub


'SORT
Sub SORT_1()
Call clear
 Dim WS As Worksheet
 Dim i As Integer, j As Integer
 Dim Total_Rows As Integer
 
 Dim Sorting_Matrix() As Variant
 Set WS = Worksheets("COLUMNS")
 Total_Rows = WorksheetFunction.CountA(WS.Range("A3:A1000"))
 ReDim Sorting_Matrix(2, Total_Rows + 1)
 For i = 1 To Total_Rows
    Sorting_Matrix(1, i) = WS.Range("B" & i + 2)
    Sorting_Matrix(2, i) = Right(Sorting_Matrix(1, i), Len(Sorting_Matrix(1, i)) - 1)
    WS.Range("B" & i + 2) = j
    j = Sorting_Matrix(2, i)
    WS.Range("B" & i + 2) = j
 Next i
'''''''''''''''''SORT by story
Range("P3").Select
    Range(Selection, Selection.End(xlDown)).Select
    ActiveWorkbook.Worksheets("COLUMNS").Sort.SortFields.clear
    ActiveWorkbook.Worksheets("COLUMNS").Sort.SortFields.Add2 Key:=Range("P3"), _
        SortOn:=xlSortOnValues, Order:=xlDescending, DataOption:=xlSortNormal
    With ActiveWorkbook.Worksheets("COLUMNS").Sort
        .SetRange Range("A2:Z1000")
        .Header = xlYes
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With

'SORT by number
     Range("B3").Select
    Range(Selection, Selection.End(xlDown)).Select
    ActiveWorkbook.Worksheets("COLUMNS").Sort.SortFields.clear
    ActiveWorkbook.Worksheets("COLUMNS").Sort.SortFields.Add2 Key:=Range("B3"), _
        SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
    With ActiveWorkbook.Worksheets("COLUMNS").Sort
        .SetRange Range("A2:Z1000")
        .Header = xlYes
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With
 
  For i = 1 To Total_Rows
    Sorting_Matrix(1, i) = WS.Range("B" & i + 2)
    Sorting_Matrix(2, i) = "C" & WS.Range("B" & i + 2)
    WS.Range("B" & i + 2) = Sorting_Matrix(2, i)
'    j = Sorting_Matrix(2, i)
'    WS.Range("B" & i + 2) = j
 Next i
  Range("B3").Select

  For i = 1 To Total_Rows + 1
        If Sorting_Matrix(2, i) = "" Then GoTo END_BORDER
        If Sorting_Matrix(2, i) <> Sorting_Matrix(2, i + 1) Then
        
                With Range("A" & 2 + i & ":" & "Z" & 2 + i).Borders(xlEdgeBottom)
                            .ThemeColor = 5
                            .TintAndShade = 0.399975585192419
                            .Weight = xlThin
                End With
       End If
 Next i
 
END_BORDER:

End Sub

Sub clear()
Dim R As Range
    Set R = Range("A3:Z2000")
    R.Borders(xlDiagonalDown).LineStyle = xlNone
    R.Borders(xlDiagonalUp).LineStyle = xlNone
    R.Borders(xlEdgeLeft).LineStyle = xlNone
    R.Borders(xlEdgeTop).LineStyle = xlNone
    R.Borders(xlEdgeBottom).LineStyle = xlNone
    R.Borders(xlEdgeRight).LineStyle = xlNone
    R.Borders(xlInsideVertical).LineStyle = xlNone
    R.Borders(xlInsideHorizontal).LineStyle = xlNone
End Sub


Sub Clear_All_Filters_Range()

  'To Clear All Fitlers use the ShowAllData method for
  'for the sheet.  Add error handling to bypass error if
  'no filters are applied.  Does not work for Tables.
  On Error Resume Next
    Worksheets("COLUMNS").ShowAllData
  On Error GoTo 0
  
End Sub
Sub RESET_BEFORE_Run()
Call Clear_All_Filters_Range
Call clear

Worksheets("COLUMNS").Range("A3:H2000").ClearContents
Worksheets("COLUMNS").Range("J3:K2000").ClearContents
Worksheets("COLUMNS").Range("O3:U2000").ClearContents
Worksheets("COLUMNS").Range("W3:AE2000").ClearContents
If WorksheetFunction.CountA(Worksheets("COLUMNS").Range("V3:V2000")) > 0 Then Worksheets("COLUMNS").Range("V3:V2000").ClearContents
    
End Sub


Sub Drop_list()
Dim i As Integer, j As Integer
Dim WS As Worksheet
Set WS = Worksheets("COLUMNS")
Dim Total_Rows As Integer
Dim R As Range, R2 As Range
Dim no_of_Bar_List() As String
Dim Min_BARS As Integer
Dim Max_BARS As Integer
Dim Width As Integer, Depth As Integer
Total_Rows = WorksheetFunction.CountA(Range("A3:A1000"))

For i = 1 To Total_Rows

    Width = WS.Range("E" & 2 + i)
    Depth = WS.Range("F" & 2 + i)
    Min_BARS = (WorksheetFunction.RoundUp((Width / 150), 0) * 2 + WorksheetFunction.RoundUp((Depth / 150) + 1, 0) * 2) - 4
    Max_BARS = (WorksheetFunction.RoundDown((Width / 100), 0) * 2 + WorksheetFunction.RoundDown((Depth / 100), 0) * 2) - 4
    ReDim no_of_Bar_List((Max_BARS - Min_BARS) / 2 + 1)
        For j = 1 To UBound(no_of_Bar_List)
            no_of_Bar_List(j) = Min_BARS + (j - 1) * 2
        Next j
        no_of_Bar_List(0) = ""
    Set R = WS.Range("J" & 2 + i)
    With R.Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertInformation, _
        Operator:=xlBetween, Formula1:=Join(no_of_Bar_List, ",")
        .IgnoreBlank = True
        .InCellDropdown = True
        .InputTitle = ""
        .ErrorTitle = ""
        .InputMessage = ""
        .ErrorMessage = ""
        .ShowInput = True
        .ShowError = False
    End With


'''''BAR DIA''''''''''''''''''''''
   Set R2 = Range("K" & 2 + i)
    With R2.Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertInformation, _
        Operator:=xlBetween, Formula1:="12,16,20,22,25,28,32"
        .IgnoreBlank = True
        .InCellDropdown = True
        .InputTitle = ""
        .ErrorTitle = ""
        .InputMessage = ""
        .ErrorMessage = ""
        .ShowInput = True
        .ShowError = False
    End With

Next i
End Sub


Sub GROUPING()
Dim i As Integer, j As Integer
Dim rows_count As Integer
Dim WS_Col As Worksheet, Unique_columns() As Variant
Set WS_Col = Worksheets("COLUMNS")
rows_count = WorksheetFunction.CountA(WS_Col.Range("B3:B500"))
'remove duplicates
For i = 1 To rows_count
    WS_Col.Range("AE" & i + 2) = WS_Col.Range("B" & i + 2)
Next i
WS_Col.Range("AE3" & ":" & "AE" & 500).RemoveDuplicates COLUMNS:=1, Header:=xlNo

Dim ROWS_COUNT1 As Integer
ROWS_COUNT1 = WorksheetFunction.CountA(WS_Col.Range("AE3:AE500"))
ReDim Unique_columns(ROWS_COUNT1)
For i = 1 To ROWS_COUNT1
   Unique_columns(i) = WS_Col.Range("AE" & i + 2)
Next i

Dim Story() As Variant, section() As Variant
Dim k As Integer, Group_String As String
For j = 1 To UBound(Unique_columns)
    For i = 1 To rows_count
        If WS_Col.Range("B" & i + 2) = Unique_columns(j) Then
            k = k + 1
            ReDim Preserve Story(k)
            ReDim Preserve section(k)
             Story(k) = WS_Col.Range("A" & i + 2)
             Group_String = Group_String & Story(k) & "-"
             section(k) = WS_Col.Range("D" & i + 2)
             Group_String = Group_String & section(k) & " "
        End If
    Next i
    
    For i = 1 To rows_count
        If WS_Col.Range("B" & i + 2) = Unique_columns(j) Then
            WS_Col.Range("Q" & i + 2) = Group_String
        End If
    Next i
    
Group_String = ""
Next j
Dim uString() As Variant
ReDim uString(0)
'uString(1) = WS_Col.Range("Q" & i + 2)

    For i = 1 To rows_count
        For j = 1 To UBound(uString)
            If WS_Col.Range("Q" & i + 2) = uString(j) Or WS_Col.Range("Q" & i + 2) = "" Then GoTo next_row
        Next j
         ReDim Preserve uString(UBound(uString) + 1)
         uString(UBound(uString)) = WS_Col.Range("Q" & i + 2)
next_row:
    Next i
    
'name the groups
For j = 1 To UBound(uString)
    For i = 1 To rows_count
        If WS_Col.Range("Q" & i + 2) = uString(j) Then
           WS_Col.Range("O" & i + 2) = "G-" & j
        End If
    Next i
Next j
End Sub

Sub Select_Columns()
Call ATTACH_TO_ETABS_COLUMNS
Dim i As Integer, j As Integer, k As Integer
Dim selected_columns() As String
Dim rows_count As Integer
Dim WS_C As Worksheet
Set WS_C = Worksheets("COLUMNS")
rows_count = WorksheetFunction.CountA(WS_C.Range("B3:B1000"))
ret = mySapModel.SelectObj.ClearSelection
'ret = mySapModel.FrameObj.SetSelected("66", True, eItemType_SelectedObjects)
For i = 1 To rows_count
    If WS_C.Range("U" & i + 2) = "YES" Then
        k = k + 1
        ReDim Preserve selected_columns(k)
        selected_columns(k) = WS_C.Range("C" & i + 2)
        ret = mySapModel.FrameObj.SetSelected(selected_columns(k), True)
    End If

Next i
End Sub




Sub Clear_Selection()
Call ATTACH_TO_ETABS_COLUMNS
Dim i As Integer, j As Integer, k As Integer
Dim selected_columns() As String
Dim rows_count As Integer
Dim WS_C As Worksheet
Set WS_C = Worksheets("COLUMNS")
rows_count = WorksheetFunction.CountA(WS_C.Range("B3:B1000"))
ret = mySapModel.SelectObj.ClearSelection
For i = 1 To rows_count
    If WS_C.Range("U" & i + 2) = "YES" Then
       WS_C.Range("U" & i + 2) = "NO"
        k = k + 1
'        ReDim Preserve selected_columns(k)
'        selected_columns(k) = WS_C.Range("C" & i + 2)
'        ret = mySapModel.FrameObj.SetSelected(selected_columns(k), True)
    End If
     If WS_C.Range("V" & i + 2) <> "" Then
        WS_C.Range("V" & i + 2) = ""
     
     
     End If
Next i
End Sub

Sub sections_available()
'Call ATTACH_TO_ETABS_COLUMNS
Dim i As Integer, j As Integer
Dim Col_Sect() As Variant
    Dim NumberNames As Long
    Dim MyName() As String
    Dim PropType() As eFramePropType
    Dim t3() As Double
    Dim t2() As Double
    Dim tf() As Double
    Dim tw() As Double
    Dim t2b() As Double
    Dim tfb() As Double
    Dim Area() As Double

    Dim Frame_Type As Long
    Dim Frame_1 As Variant

ret = mySapModel.PropFrame.GetAllFrameProperties_2(NumberNames, MyName, PropType, t3, t2, tf, tw, t2b, tfb, Area)

For i = 0 To NumberNames - 1
   ret = mySapModel.PropFrame.GetTypeRebar(MyName(i), Frame_Type)
   If Frame_Type = 1 Then
      Frame_1 = "Column"
   ElseIf Frame_Type = 2 Then
      Frame_1 = "Beam"
   Else
      Frame_1 = "None"
   End If
''''' Get Section sizes''''
'    ret = mySapModel.PropFrame.GetRectangle(PropName(i), FileName, MatProp, t3, t2, Color, Notes, GUID)
'    Col_depth = t3
'    Col_width = t2
    
    If Frame_1 = "Column" Then
       j = j + 1
       ReDim Preserve Col_Sect(j)
       Col_Sect(j) = MyName(i)
    End If
Next i

''''''''''''''''
Dim R As Range
Dim rows_count As Integer
Dim WS_C As Worksheet
Set WS_C = Worksheets("COLUMNS")

rows_count = WorksheetFunction.CountA(WS_C.Range("B3:B1000"))
For i = 1 To rows_count
        Col_Sect(0) = ""
    Set R = WS_C.Range("V" & 2 + i)
    With R.Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertInformation, _
        Operator:=xlBetween, Formula1:=Join(Col_Sect, ",")
        .IgnoreBlank = True
        .InCellDropdown = True
        .InputTitle = ""
        .ErrorTitle = ""
        .InputMessage = ""
        .ErrorMessage = ""
        .ShowInput = True
        .ShowError = False
    End With
Next i
End Sub

Sub Section_update()

Call ATTACH_TO_ETABS_COLUMNS
 ret = mySapModel.SetModelIsLocked(False)
Dim i As Integer, j As Integer, k As Integer
Dim selected_columns() As String
Dim rows_count As Integer
Dim WS_C As Worksheet
Dim UName As String
Dim Updated_Section As String
Set WS_C = Worksheets("COLUMNS")
rows_count = WorksheetFunction.CountA(WS_C.Range("B3:B1000"))

ret = mySapModel.SelectObj.ClearSelection

For i = 1 To rows_count
    If WS_C.Range("V" & i + 2) <> "" Then
        UName = WS_C.Range("C" & i + 2)
        Updated_Section = WS_C.Range("V" & i + 2)
        ret = mySapModel.FrameObj.SetSection(UName, Updated_Section)
    End If
    
Next i
ret = mySapModel.View.RefreshView
End Sub

Sub diaphragm1()
    ' DIAPHRAGM
    Dim DiaphragmOption As eDiaphragmOption
    Dim DiaphragmName As String
    Dim NumberNames As Long
    Dim MyName1() As String
    Dim SemiRigid As Boolean
    Dim i As Integer
    
    ret = mySapModel.Diaphragm.GetNameList(NumberNames, MyName1)
    For i = 0 To NumberNames - 1
        ret = mySapModel.Diaphragm.GetDiaphragm(MyName1(i), SemiRigid)
        Worksheets("COLUMNS").Range("AB" & i + 3) = MyName1(i)
        If SemiRigid = False Then
            Worksheets("COLUMNS").Range("AC" & i + 3) = "RIGID"
        Else
            Worksheets("COLUMNS").Range("AC" & i + 3) = "SEMI-RIGID"
        End If

    Next i
End Sub
Sub Run_and_Check()
Call ATTACH_TO_ETABS_COLUMNS
Call Provide_Reinforcement

ret = mySapModel.Analyze.CreateAnalysisModel

End Sub
Sub cal()
Application.ScreenUpdating = True
Application.Calculation = xlCalculationAutomatic
End Sub
