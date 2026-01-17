Attribute VB_Name = "BeamType"
' =============================================================================
' LEGACY CODE - ETABS Beam Classification & Design (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Classify beams (X/Y direction, continuous/discontinuous) and design
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.Story.GetNameList() - Get all story names
'   - mySapModel.FrameObj.GetPoints() - Get frame end points
'   - mySapModel.FrameObj.GetNameFromLabel() - Convert label to name
'   - mySapModel.DesignConcrete.GetSummaryResultsBeam_2() - Detailed beam results
'
' =============================================================================

Option Explicit

 Dim myHelper As ETABSv1.cHelper
 Dim myETABSObject As ETABSv1.cOAPI
 Dim mySapModel As ETABSv1.cSapModel
 Dim ModelName As String, ModelPath As String
 Dim ret As Long
 
 Dim List2() As Variant
 Dim NumberItems As Long
 Dim i, j, k, RowsCount As Integer
 Dim AllBEAMS() As Variant
 'Dim Rows1 As Integer
 

Sub ATTACH_TO_ETABS_BeamType()
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

Sub BEAMS_FROM_ETABS()
Call clear_Beams
Call ATTACH_TO_ETABS_BeamType
Call DropList
ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
j = 0
    
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
    'Get all frames
    ret = mySapModel.FrameObj.GetAllFrames(NumberNames, MyName, PropName, StoryName, PointName1, PointName2, Point1X, Point1Y, Point1Z, Point2X, Point2Y, Point2Z, Angle _
            , Offset1X, Offset2X, Offset1Y, Offset2Y, Offset1Z, Offset2Z, CardinalPoint)
            
            
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
    Dim B_depth As Double, B_width As Double
        
For i = 0 To NumberNames - 1
  '  ret = mySapModel.DesignConcrete.GetSummaryResultsBeam(MyName(i), NumberItems, FrameName, Location, TopCombo, TopArea, BotCombo, BotArea, VmajorCombo, VmajorArea, TLCombo, TLArea, TTCombo, TTArea, ErrorSummary, WarningSummary, eItemType_Objects)

   '''' Beam or column identify
   ret = mySapModel.PropFrame.GetTypeRebar(PropName(i), Frame_Type)

   If Frame_Type = 2 And (PropName(i) <> "DUMMY" And PropName(i) <> "Stiff Beam" And Worksheets("Beam Types").Range("B2") = StoryName(i)) Then         'BEAM
        'Get Section sizes'
        ret = mySapModel.PropFrame.GetRectangle(PropName(i), FileName, MatProp, t3, t2, Color, Notes, GUID)
        B_depth = t3
        B_width = t2
    
       j = j + 1 'counter
       ReDim Preserve AllBEAMS(12, j)
       AllBEAMS(1, j) = StoryName(i)
       ret = mySapModel.FrameObj.GetLabelFromName(MyName(i), Label, story_from_Label)
       AllBEAMS(2, j) = Label
      'AllBEAMS(3, j) = MyName(i)
       AllBEAMS(3, j) = PropName(i)
       AllBEAMS(4, j) = WorksheetFunction.Round(B_width * 1000, 0) ' to convert in mm
       AllBEAMS(5, j) = WorksheetFunction.Round(B_depth * 1000, 0)
        
       Dim Point1 As String
       Dim Point2 As String
       ret = mySapModel.FrameObj.GetPoints(MyName(i), Point1, Point2)
       AllBEAMS(6, j) = Point1
       AllBEAMS(7, j) = Point2
       AllBEAMS(8, j) = Point1X(i)
       AllBEAMS(9, j) = Point2X(i)
       AllBEAMS(10, j) = Point1Y(i)
       AllBEAMS(11, j) = Point2Y(i)
       
    End If
Next i
    
RowsCount = j
End Sub

Sub BeamType()
Call BEAMS_FROM_ETABS
Dim WS As Worksheet
Set WS = Worksheets("Beam Types")
Dim WB As Workbook
Set WB = ThisWorkbook
Dim RowNumber As Integer
'
'For i = 1 To RowsCount
'    For j = 1 To 11
'WS.Range("A5").Offset(i, j - 1) = AllBEAMS(j, i)
'
'    Next j
'Next i
Dim PointI(), PointJ() As Integer

'Get Type
If WS.Range("C2") = "X-Direction" Then
    For i = 1 To RowsCount
    
        For j = 1 To 11
            If AllBEAMS(10, i) = AllBEAMS(11, i) Then                     'X Direction Beams
    
                  WS.Range("A5").Offset(RowNumber, j - 1) = AllBEAMS(j, i)
                  'search for point i in all beams
                  ReDim Preserve PointI(RowNumber), PointJ(RowNumber)
    
                  PointI(RowNumber) = AllBEAMS(6, i)
                  PointJ(RowNumber) = AllBEAMS(7, i)
    
            End If
        Next j
        If AllBEAMS(10, i) = AllBEAMS(11, i) Then RowNumber = RowNumber + 1
    Next i

Else
    ' Y direction Beams
    For i = 1 To RowsCount
        
        
        For j = 1 To 11
            If AllBEAMS(8, i) = AllBEAMS(9, i) Then                     'Y Direction Beams
                                
                  WS.Range("A5").Offset(RowNumber, j - 1) = AllBEAMS(j, i)
                  'search for point i in all beams
                  ReDim Preserve PointI(RowNumber), PointJ(RowNumber)
                  
                  PointI(RowNumber) = AllBEAMS(6, i)
                  PointJ(RowNumber) = AllBEAMS(7, i)
                                
            End If
        Next j
        If AllBEAMS(8, i) = AllBEAMS(9, i) Then RowNumber = RowNumber + 1
    Next i

End If

'END 1 CONDITION
Dim End1_Condition() As String
ReDim End1_Condition(RowNumber)
'Compare Points i & j for x direction
For i = 0 To RowNumber - 1
    For j = 0 To RowNumber - 1
        If PointI(i) = PointJ(j) Then
        WS.Range("A5").Offset(i, 11) = "END 1 Continuous"
        End1_Condition(i) = "END 1 Continuous"
        GoTo NextLine
        End If
         
    Next j
    End1_Condition(i) = "END 1 Discontinuous"
    WS.Range("A5").Offset(i, 11) = "END 1 Discontinuous"
NextLine:
Next i

'END 1 CONDITION

Dim End2_Condition() As String
ReDim End2_Condition(RowNumber)
'Compare Points i & j for x direction
For i = 0 To RowNumber - 1
    For j = 0 To RowNumber - 1
        If PointJ(i) = PointI(j) Then
        WS.Range("A5").Offset(i, 12) = "END 2 Continuous"
        End2_Condition(i) = "END 2 Continuous"
        GoTo NextLine1
        End If
         
    Next j
    End2_Condition(i) = "END 2 Discontinuous"
    WS.Range("A5").Offset(i, 12) = "END 2 Discontinuous"
    
    
NextLine1:
Next i

'Both Ends Continuous
Dim End_Condition() As String
ReDim End_Condition(RowNumber)

'For i = 1 To RowNumber
'    If End1_Condition(i) = "END 1 Discontinuous" And End2_Condition(i) = "END 2 Continuous" Then
'       End_Condition(i) = "BOTH END CONTINUOUS"
'    elseif
'
'    End If
'
'Next i
If WS.Range("C2") = "X-Direction" Then
    Call SortX
Else
    Call SortY
End If

End Sub

Sub BeamReinf()
Call ATTACH_TO_ETABS_BeamType
Call check_for_run
Dim WS As Worksheet
Set WS = Worksheets("Beam Types")
Dim Rows1 As Integer
'Get Label and Story From Excel
Dim Label() As String
Dim Story() As String
Dim Name As String

For i = 1 To 5000
    If WS.Range("B" & 4 + i) = "" Then
        GoTo NextRow
    Else: Rows1 = Rows1 + 1
    End If
    
NextRow:
Next i
    'Beam reinf req
    Dim NumberItems As Long
    Dim FrameName() As String
    Dim Location() As Double
    Dim TopCombo() As String
    Dim TopArea() As Double
    Dim TopAreaReq() As Double
    Dim TopAreaMin() As Double
    Dim TopAreaProvided() As Double
    Dim BotCombo() As String
    Dim BotArea() As Double
    Dim BotAreaReq() As Double
    Dim BotAreaMin() As Double
    Dim BotAreaProvided() As Double
    Dim VmajorCombo() As String
    Dim VmajorArea() As Double
    Dim VmajorAreaReq() As Double
    Dim VmajorAreaMin() As Double
    Dim VmajorAreaProvided() As Double
    Dim TLCombo() As String
    Dim TLArea() As Double
    Dim TTCombo() As String
    Dim TTArea() As Double
    Dim ErrorSummary() As String
    Dim WarningSummary() As String
    Dim ItemType As eItemType

ret = mySapModel.SetPresentUnits(eUnits_kN_cm_C)
ReDim Label(Rows1), Story(Rows1)

For i = 1 To Rows1
    Story(i) = WS.Range("A" & 4 + i)
    Label(i) = WS.Range("B" & 4 + i)
    
    ret = mySapModel.FrameObj.GetNameFromLabel(Label(i), Story(i), Name)
    ret = mySapModel.DesignConcrete.GetSummaryResultsBeam_2(Name, NumberItems, FrameName, Location, TopCombo, TopArea, TopAreaReq, TopAreaMin, TopAreaProvided, BotCombo, BotArea, BotAreaReq, BotAreaMin, BotAreaProvided, VmajorCombo, VmajorArea, VmajorAreaReq, VmajorAreaMin, VmajorAreaProvided, TLCombo, TLArea, TTCombo, TTArea, ErrorSummary, WarningSummary, eItemType_Objects)
    Dim Length As Double
    Dim TopEnd1(), TopEnd2(), TopMid() As Double
    ReDim TopEnd1(UBound(Location)), TopEnd2(UBound(Location)), TopMid(UBound(Location))
    Length = Abs(WorksheetFunction.Min(Location) - WorksheetFunction.Max(Location))
    For j = 0 To UBound(Location)
        If Location(j) < Length / 3 Then
           TopEnd1(j) = TopArea(j)
        ElseIf Location(j) > Length * 2 / 3 Then
           TopEnd2(j) = TopArea(j)
        Else
           TopMid(j) = TopArea(j)
        End If

    Next j
        WS.Range("O5").Offset(i - 1, 0) = Format(WorksheetFunction.Max(TopEnd1), "0.00")
        WS.Range("O5").Offset(i - 1, 1) = Format(WorksheetFunction.Max(TopMid), "0.00")
        WS.Range("O5").Offset(i - 1, 2) = Format(WorksheetFunction.Max(TopEnd2), "0.00")
        WS.Range("O5").Offset(i - 1, 3) = Format(WorksheetFunction.Max(BotArea), "0.00")
        'Shear
        
        WS.Range("AA5").Offset(i - 1, 0) = Format(WorksheetFunction.Max(VmajorArea), "0.0000") * 100
        WS.Range("AA5").Offset(i - 1, 2) = Format(WorksheetFunction.Max(TLArea), "0.0000")
        WS.Range("AA5").Offset(i - 1, 4) = Format(WorksheetFunction.Max(TTArea), "0.0000") * 100
        'TTArea
Next i

End Sub

Sub ProvideBeamReinf()
'Call RebarAreaList
Call clear_reinf
Dim pi As Variant
Dim M, k2, k3 As Integer

Dim BAR_DIA_ALL(7) As Variant, Bar_DIA_Count As Variant
pi = WorksheetFunction.pi
BAR_DIA_ALL(1) = 12
BAR_DIA_ALL(2) = 16
BAR_DIA_ALL(3) = 20
BAR_DIA_ALL(4) = 22
BAR_DIA_ALL(5) = 25
BAR_DIA_ALL(6) = 28
BAR_DIA_ALL(7) = 32

'Read From EXCEL
Dim WS As Worksheet
Set WS = Worksheets("Beam Types")
Dim Rows1 As Integer

For i = 1 To 5000
    If WS.Range("B" & 4 + i) = "" Then
        GoTo NextRow
    Else: Rows1 = Rows1 + 1
    End If
NextRow:
Next i


Dim NO_of_Bars, Width, Depth As Integer
Dim Min_BARS, Max_BARS As Integer
Dim End1C, End2C As String
Dim TopE1, TOPM, TOPE2, Bottom As Double

For j = 0 To 3
    For i = 1 To Rows1
    
    Width = WS.Range("A4").Offset(i, 3)
    Depth = WS.Range("A4").Offset(i, 4)
    
    TopE1 = WS.Range("O4").Offset(i, 0)
    TOPM = WS.Range("O4").Offset(i, 1)
    TOPE2 = WS.Range("O4").Offset(i, 2)
    Bottom = WS.Range("O4").Offset(i, 3)
    Dim BEAM_REQ_REINF As Double
    
    BEAM_REQ_REINF = WS.Range("O4").Offset(i, j)
    
    Min_BARS = WorksheetFunction.RoundDown(Width / 100, 0)
    Max_BARS = Min_BARS * 2
    
    'If Width = 400 Then Min_BARS = 3  ' change min bars as per project
    'NO_of_Bars=
    'Min bars
    ' Min_BARS = (WorksheetFunction.RoundUp(Column_Data(5, i) / 150, 0) + WorksheetFunction.RoundUp(Column_Data(6, i) / 150 + 1, 0)) * 2 - 4
    ' Max_bars = (WorksheetFunction.RoundUp(Column_Data(5, i) / 100, 0) + WorksheetFunction.RoundUp(Column_Data(6, i) / 100, 0)) * 2 - 4
        Dim Differene() As Variant
        Dim Reinf() As Double
        Dim Bar_dia_of_Reinf() As Integer
        Dim No_of_Bars_Reinf() As Integer
        Dim reinf_Prov As Double
        
        ReDim Differene(UBound(BAR_DIA_ALL), 2)
        ReDim Reinf(M)
        ReDim Bar_dia_of_Reinf(M)
        ReDim No_of_Bars_Reinf(M)
'''''''''''''''''        ''''''''''
For Bar_DIA_Count = 1 To UBound(BAR_DIA_ALL)     '1 st layer bars
    For k = 1 To UBound(BAR_DIA_ALL)             '2nd layer
       For k3 = 0 To 1                           'NO of Bars in 2nd layer
        'Rebar_AreaBeam
        k2 = k2 + 1
        ReDim Preserve List2(4, k2)
        ReDim Preserve Reinf(k2)
       
        List2(1, k2) = Min_BARS & " T " & BAR_DIA_ALL(Bar_DIA_Count)
        If k <= Bar_DIA_Count And Depth > WS.Range("T1") Then ''''''''''' change for double layers minimum depth
        
            List2(2, k2) = (Min_BARS - k3) & " T " & BAR_DIA_ALL(k)
        Else
            List2(2, k2) = ""
        End If
        
        List2(3, k2) = Rebar_AreaBeam(List2(1, k2)) + Rebar_AreaBeam(List2(2, k2))
        List2(4, k2) = BEAM_REQ_REINF - List2(3, k2)
        If List2(4, k2) > 0 Then List2(4, k2) = -500
        Reinf(k2) = List2(4, k2)
        Next k3
    Next k
Next Bar_DIA_Count '

Dim Minimum_Found As Double
Reinf(0) = -500
Minimum_Found = WorksheetFunction.Max(Reinf)
       For k = 1 To UBound(Reinf)
          If Reinf(k) = Minimum_Found Then
                If List2(2, k) = "" Then
                    WS.Range("T4").Offset(i, j) = List2(1, k)
                ElseIf j = 3 Then
                    WS.Range("T4").Offset(i, j) = List2(2, k) & " + " & List2(1, k)
                Else
                    WS.Range("T4").Offset(i, j) = List2(1, k) & " + " & List2(2, k)
                End If
                GoTo NEXT_BEAM
          End If
       Next k
        WS.Range("T4").Offset(i, j) = " Check"
        
NEXT_BEAM:
k2 = 0
    Next i
Next j




''''''''''''''''''''''''''''''''''''''''''        ''''''''''
'         For Bar_DIA_Count = 1 To UBound(BAR_DIA_ALL)
'             For k = 1 To 2
'
'                    reinf_Prov = ((pi) * (1 / 4) * (BAR_DIA_ALL(Bar_DIA_Count)) ^ 2 * (Min_BARS * k))
'                    Differene(Bar_DIA_Count, k) = BEAM_REQ_REINF - reinf_Prov / 100
'
'                    ' add total matrix
'
'                    M = M + 1
'                    ReDim Preserve Reinf(M)
'                    ReDim Preserve Bar_dia_of_Reinf(M)
'                    ReDim Preserve No_of_Bars_Reinf(M)
'
'                    No_of_Bars_Reinf(M) = Min_BARS * k ' No of Bars
'                    Bar_dia_of_Reinf(M) = BAR_DIA_ALL(Bar_DIA_Count) ' Bar Dia
'                    Reinf(M) = Differene(Bar_DIA_Count, k)  ' Reinf Diff
'
'
'             Next k
'
'         Next Bar_DIA_Count
'    '
'       For k = 1 To M + 1
'         If Reinf(k - 1) >= 0 Then Reinf(k - 1) = -200
'       Next k
'       Dim Minimum_Found As Double
'       Minimum_Found = WorksheetFunction.Max(Reinf)
'       For k = 1 To M + 1
'          If Reinf(k - 1) = Minimum_Found Then
'
'                WS.Range("T4").Offset(i, j) = No_of_Bars_Reinf(k - 1) & " T " & Bar_dia_of_Reinf(k - 1)
'
'                GoTo NEXT_BEAM
'           End If
'
'
'        Next k
'        WS.Range("T4").Offset(i, j) = " Check"
'
'NEXT_BEAM:
'M = 0
'    Next i
'Next j

Call checkForContiousBeams
End Sub

Sub checkForContiousBeams()

Dim Data1() As Variant
'Read From EXCEL
Dim WS As Worksheet
Set WS = Worksheets("Beam Types")
Dim Rows1 As Integer

For i = 1 To 5000
    If WS.Range("B" & 4 + i) = "" Then
        GoTo NextRow
    Else: Rows1 = Rows1 + 1
    End If
NextRow:
Next i
ReDim Data1(Rows1, 10)
For i = 1 To Rows1
    
    Data1(i, 1) = WS.Range("A4").Offset(i, 1) 'Beam Label
    Data1(i, 2) = WS.Range("A4").Offset(i, 5) 'PT I
    Data1(i, 3) = WS.Range("A4").Offset(i, 6) 'PT J
    Data1(i, 4) = WS.Range("L4").Offset(i, 0) 'END1 Cond
    Data1(i, 5) = WS.Range("L4").Offset(i, 1) 'END2 Cond
    Data1(i, 6) = WS.Range("L4").Offset(i, 3) 'End 1 req
    Data1(i, 7) = WS.Range("L4").Offset(i, 5) 'End 2 req
    Data1(i, 8) = WS.Range("T4").Offset(i, 0) 'End 1 req
    Data1(i, 9) = WS.Range("T4").Offset(i, 2) 'End 2 req
Next i
Dim Pt2, RowOfContBeam As Integer
For i = 1 To Rows1
    If Data1(i, 5) = "END 2 Discontinuous" Then GoTo Next_Beam1
    Pt2 = Data1(i, 3)
    For j = 1 To Rows1
        If Data1(j, 2) = Pt2 Then GoTo Found_NextBeam

    Next j
Found_NextBeam:
RowOfContBeam = j
'check for max reinf
Dim max_reinf_of_Two As Double
max_reinf_of_Two = WorksheetFunction.Max(Data1(i, 7), Data1(RowOfContBeam, 6))


'provide max of two
If Data1(RowOfContBeam, 6) >= Data1(i, 7) Then
   'WS.Range("T4").Offset(i, 2).Select
    WS.Range("T4").Offset(i, 2) = Data1(RowOfContBeam, 8)
Else
   ' WS.Range("T4").Offset(RowOfContBeam, 0).Select
    WS.Range("T4").Offset(RowOfContBeam, 0) = Data1(i, 9)
    
End If


Next_Beam1:
Next i


End Sub



Sub clear_reinf()
Worksheets("Beam Types").Range("S5:W5000").ClearContents
End Sub





Sub check_for_run()
Call ATTACH_TO_ETABS_BeamType
Dim ResultsAvailable As Boolean, Run1 As Long
'Run1 = mySapModel.Analyze.CreateAnalysisModel
ret = mySapModel.Analyze.RunAnalysis

ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
End Sub


Sub clear_Beams()
Worksheets("Beam Types").Range("A5:X5000").ClearContents
End Sub


Sub DropList()
Call ATTACH_TO_ETABS_BeamType
Dim NumberNames As Long
Dim MyName() As String
ret = mySapModel.Story.GetNameList(NumberNames, MyName)



    With Range("B2").Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, Operator:= _
        xlBetween, Formula1:=Join(MyName, ",")
        .IgnoreBlank = True
        .InCellDropdown = True
        .InputTitle = ""
        .ErrorTitle = ""
        .InputMessage = ""
        .ErrorMessage = ""
        .ShowInput = False
        .ShowError = False
    End With


End Sub

Sub SortX()

'Sort By X Coodinate
    Range("H5").Select
    Range(Selection, Selection.End(xlDown)).Select
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.clear
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.Add2 Key:=Range("H5"), _
        SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
    With ActiveWorkbook.Worksheets("Beam Types").Sort
        .SetRange Range("A5:O1000")
        .Header = xlNo
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With


'Sort By Y Coodinate
    Range("J5").Select
    Range(Selection, Selection.End(xlDown)).Select
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.clear
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.Add2 Key:=Range("J5"), _
        SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
    With ActiveWorkbook.Worksheets("Beam Types").Sort
        .SetRange Range("A5:O1000")
        .Header = xlNo
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With
End Sub

Sub SortY()

'Sort By Y Coodinate
    Range("J5").Select
    Range(Selection, Selection.End(xlDown)).Select
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.clear
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.Add2 Key:=Range("J5"), _
        SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
    With ActiveWorkbook.Worksheets("Beam Types").Sort
        .SetRange Range("A5:O1000")
        .Header = xlNo
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With
    
'Sort By X Coodinate
    Range("H5").Select
    Range(Selection, Selection.End(xlDown)).Select
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.clear
    ActiveWorkbook.Worksheets("Beam Types").Sort.SortFields.Add2 Key:=Range("H5"), _
        SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortNormal
    With ActiveWorkbook.Worksheets("Beam Types").Sort
        .SetRange Range("A5:O1000")
        .Header = xlNo
        .MatchCase = False
        .Orientation = xlTopToBottom
        .SortMethod = xlPinYin
        .Apply
    End With

End Sub


Sub BeamNumbers()

Dim Data1() As Variant
'Read From EXCEL
Dim WS As Worksheet
Set WS = Worksheets("Beam Types")
Dim Rows1 As Integer

    For i = 1 To 5000
    If WS.Range("B" & 4 + i) = "" Then
        GoTo NextRow
    Else: Rows1 = Rows1 + 1
    End If
NextRow:
Next i

WS.Range("S4" & ":" & "S" & Rows1 + 5).ClearContents
' get data from excel

ReDim Data1(Rows1, 9)
For i = 1 To Rows1
    
    Data1(i, 1) = WS.Range("A4").Offset(i, 1) 'Beam Label
    Data1(i, 2) = WS.Range("A4").Offset(i, 2) 'Section
    Data1(i, 3) = WS.Range("A4").Offset(i, 6) 'PT J
    Data1(i, 4) = WS.Range("L4").Offset(i, 0) 'END1 Cond
    Data1(i, 5) = WS.Range("L4").Offset(i, 1) 'END2 Cond
    Data1(i, 6) = WS.Range("T4").Offset(i, 0) 'Top END1 reinf provided
    Data1(i, 7) = WS.Range("T4").Offset(i, 1) 'Top mid reinf provided
    Data1(i, 8) = WS.Range("T4").Offset(i, 2) 'Top END2 reinf provided
    Data1(i, 9) = WS.Range("T4").Offset(i, 3) 'Bottom reinf provided
Next i


'Dim Pt2, RowOfContBeam As Integer
'For i = 1 To Rows1
'    If Data1(i, 5) = "END 2 Discontinuous" Then GoTo Next_Beam1
'    Pt2 = Data1(i, 3)
'    For j = 1 To Rows1
'        If Data1(j, 2) = Pt2 Then GoTo Found_NextBeam
'
'    Next j
'Found_NextBeam:
'RowOfContBeam = j



''''''''''''''


Dim End1C, End2C, BeamName, BeamSection As String
Dim UniqueBeam As Integer
Dim TopEnd1Reinf, TopMidReinf, TopEnd2Reinf, BottomReinf As Variant
Dim Diff, Diff1, Diff2, Diff3 As Double

For i = 1 To Rows1

    If WS.Range("S4").Offset(i, 0) = "" Then
       UniqueBeam = UniqueBeam + 1
       WS.Range("S4").Offset(i, 0) = "B" & UniqueBeam
       BeamSection = Data1(i, 2)
       End1C = Data1(i, 4)
       End2C = Data1(i, 5)
       BeamName = "B" & UniqueBeam
       TopEnd1Reinf = Data1(i, 6)
       TopMidReinf = Data1(i, 7)
       TopEnd2Reinf = Data1(i, 8)
       BottomReinf = Data1(i, 9)
       
       
       For j = 1 To Rows1
            If Data1(j, 2) = BeamSection Then
                    If Data1(j, 4) = End1C And Data1(j, 5) = End2C Then
                       Diff1 = Abs(Rebar_AreaBeam(TopEnd1Reinf) - Rebar_AreaBeam(Data1(j, 6)))
                       Diff2 = Abs(Rebar_AreaBeam(TopEnd2Reinf) - Rebar_AreaBeam(Data1(j, 8)))
                       Diff3 = Abs(Rebar_AreaBeam(BottomReinf) - Rebar_AreaBeam(Data1(j, 9)))
                       Diff = WorksheetFunction.Max(Diff1, Diff2, Diff3)
                       If Diff < WS.Range("S3") Then
                            WS.Range("S4").Offset(j, 0) = "B" & UniqueBeam
                            'END 1
                            If Rebar_AreaBeam(TopEnd1Reinf) > Rebar_AreaBeam(Data1(j, 6)) Then
                               WS.Range("S4").Offset(j, 1) = TopEnd1Reinf
                            Else
                               WS.Range("S4").Offset(i, 1) = Data1(j, 6)
                            End If
                            'Mid
                            If Rebar_AreaBeam(TopMidReinf) > Rebar_AreaBeam(Data1(j, 7)) Then
                               WS.Range("S4").Offset(j, 2) = TopMidReinf
                            Else
                               WS.Range("S4").Offset(i, 2) = Data1(j, 7)
                            End If
                            'END 2
                            If Rebar_AreaBeam(TopEnd2Reinf) > Rebar_AreaBeam(Data1(j, 8)) Then
                               WS.Range("S4").Offset(j, 3) = TopEnd2Reinf
                            Else
                               WS.Range("S4").Offset(i, 3) = Data1(j, 8)
                            End If
                            'Bottom
                            If Rebar_AreaBeam(BottomReinf) > Rebar_AreaBeam(Data1(j, 9)) Then
                               WS.Range("S4").Offset(j, 4) = BottomReinf
                            Else
                               WS.Range("S4").Offset(i, 4) = Data1(j, 9)
                            End If
                       End If
                    End If
            End If
       Next j
       
'       For j = 1 To Rows1
'        If Data1(j, 2) = BeamSection Then
'                If Data1(j, 4) = End1C And Data1(j, 5) = End2C Then
'                    If Data1(j, 6) = TopEnd1Reinf Then 'And Data1(j, 7) = TopMidReinf Then
'                        If Data1(j, 6) = TopEnd2Reinf And Data1(j, 6) = BottomReinf Then
'
'                            WS.Range("S4").Offset(j, 0) = "B" & UniqueBeam
'                        End If
'                    End If
'                End If
'        End If
'       Next j
'
    End If

Next i

Call checkForContiousBeams
End Sub


Sub ChangeReinfasType()


End Sub
Function Rebar_AreaBeam(Reinf As Variant) As Double
Dim NO_of_Bars, Bar_Dia As Integer
Dim pi As Double

If Reinf = "" Then
    Rebar_AreaBeam = 0
    GoTo NEXT1
End If
NO_of_Bars = Left(Reinf, 1)
Bar_Dia = Right(Reinf, 2)
pi = WorksheetFunction.pi()

Rebar_AreaBeam = NO_of_Bars * pi * 0.25 * Bar_Dia * Bar_Dia / 100
'3 T 28
NEXT1:
End Function

Sub RebarAreaList()

Dim MinBars, MaxBars As Integer
Dim BAR_DIA_ALL(7) As Integer
Dim NO_of_Bars, k2 As Integer
'Dim List2() As Variant
'ReDim List2(1, 2)
MinBars = 3
MaxBars = MinBars * 2


BAR_DIA_ALL(1) = 12
BAR_DIA_ALL(2) = 16
BAR_DIA_ALL(3) = 20
BAR_DIA_ALL(4) = 22
BAR_DIA_ALL(5) = 25
BAR_DIA_ALL(6) = 28
BAR_DIA_ALL(7) = 32


For i = 1 To 7  '1 st layer bars
    For k = 1 To 7  '2nd layer
       For k3 = 0 To 1   'NO of Bars in 2nd layer
        'Rebar_AreaBeam
        k2 = k2 + 1
        ReDim Preserve List2(3, k2)
       
        List2(1, k2) = MinBars & " T " & BAR_DIA_ALL(i)
        If k <= i Then
            List2(2, k2) = (MinBars - k3) & " T " & BAR_DIA_ALL(k)
        Else
            List2(2, k2) = ""
        End If
        
        List2(3, k2) = Rebar_AreaBeam(List2(1, k2)) + Rebar_AreaBeam(List2(2, k2))
        
        Next k3
    Next k
Next i

End Sub


Sub ShearReinf()
'Call clear_Shear_reinf
Dim pi As Variant
Dim M, k2, k3 As Integer

Dim BAR_DIA_ALL(2) As Variant, Bar_DIA_Count As Variant
pi = WorksheetFunction.pi
BAR_DIA_ALL(1) = 12
BAR_DIA_ALL(2) = 16

Dim SpacingAll(4) As Integer
SpacingAll(1) = 200
SpacingAll(2) = 150
SpacingAll(3) = 125
SpacingAll(4) = 100


'Read From EXCEL
Dim WS As Worksheet
Set WS = Worksheets("Beam Types")
Dim Rows1 As Integer

For i = 1 To 5000
    If WS.Range("B" & 4 + i) = "" Then
        GoTo NextRow
    Else: Rows1 = Rows1 + 1
    End If
NextRow:
Next i


Dim NO_of_Bars, Width, Depth As Integer
Dim Min_BARS, Max_BARS As Integer
Dim End1C, End2C As String
Dim TopE1, TOPM, TOPE2, Bottom As Double

Dim No_Of_Legs, Spacing, bardia As Integer
'For j = 0 To 1
    For i = 1 To Rows1
    
    Width = WS.Range("A4").Offset(i, 3)
    Depth = WS.Range("A4").Offset(i, 4)
    

    No_Of_Legs = Switch(Width < 400, 2, Width < 600, 4, Width < 800, 6, Width < 1000, 8)
    
    WS.Range("AA4").Offset(i, 1) = No_Of_Legs
    
    Dim BarDiaCount, SpacingCount, k2 As Integer
    Dim BarDiaUsed(), SpacingUsed(), ReabarAreaUsed() As Integer
    
    For BarDiaCount = 1 To UBound(BAR_DIA_ALL)
        For SpacingCount = 1 To UBound(SpacingAll)
        k2 = k2 + 1
        
        ReDim BarDiaUsed(k2), SpacingUsed(k2), ReabarAreaUsed(k2)
        BarDiaUsed(k2) = BAR_DIA_ALL(BarDiaCount)
        SpacingUsed(k2) = SpacingAll(SpacingCount)
        ReabarAreaUsed(k2) = Rebar_Area(BAR_DIA_ALL(BarDiaCount))
    
        Next SpacingCount
    Next BarDiaCount
    Next i
'Next j

End Sub

Function Rebar_Area_cm2(dia As Variant)
Rebar_Area = (22 / 7) * (1 / 4) * (dia) * (dia) / 100
End Function
