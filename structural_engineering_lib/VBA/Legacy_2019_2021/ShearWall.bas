Attribute VB_Name = "ShearWall"
' =============================================================================
' LEGACY CODE - ETABS Shear Wall/Pier Design (2019-2021)
' =============================================================================
' Original Author: Pravin Surawase
' Period: 2019-2021 (Structural Engineering Firm)
' Purpose: Extract shear wall pier design results and calculate reinforcement
' Status: ARCHIVED - Working code from production use
' =============================================================================
'
' KEY APIs DEMONSTRATED:
'   - mySapModel.PierLabel.GetNameList() - Get pier names
'   - mySapModel.DesignShearWall.GetPierSummaryResults() - Pier design results
'   - mySapModel.PierLabel.GetSectionProperties() - Pier section dimensions
'   - mySapModel.Story.GetHeight() - Get story height
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
Dim i As Integer, j As Integer, k As Integer


''''''''''''''''''''''''''''''''''''''''''''''''''
'              Attach To ETABS                   '
''''''''''''''''''''''''''''''''''''''''''''''''''
Sub ATTACH_TO_ETABS_WALLS()
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
Call ATTACH_TO_ETABS_WALLS
Dim ResultsAvailable As Boolean, Run1 As Long
    Run1 = mySapModel.Analyze.CreateAnalysisModel
    If Run1 = 0 Then ret = mySapModel.Analyze.RunAnalysis
    
    ResultsAvailable = mySapModel.DesignConcrete.GetResultsAvailable
    'If ResultsAvailable = False Then ret = mySapModel.DesignConcrete.StartDesign()
   
    
End Sub
Function Rebar_Area(dia As Variant)
Rebar_Area = (22 / 7) * (1 / 4) * (dia) * (dia)
End Function

Sub Piers()
Call clear_ShearWall
Call ATTACH_TO_ETABS_WALLS
Dim WS_SW As Worksheet
Set WS_SW = Worksheets("SHEAR WALL")
ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
'get pier names
  Dim NumberNames As Long
  Dim MyName1() As String

 ret = mySapModel.PierLabel.GetNameList(NumberNames, MyName1)

    Dim Story() As String
    Dim PierLabel() As String
    Dim Station() As String
    Dim DesignType() As String
    Dim PierSecType() As String
    Dim EdgeBar() As String
    Dim EndBar() As String
    Dim BarSpacing() As Double
    Dim ReinfPercent() As Double
    Dim CurrPercent() As Double
    Dim DCRatio() As Double
    Dim PierLeg() As String
    Dim LegX1() As Double
    Dim LegY1() As Double
    Dim LegX2() As Double
    Dim LegY2() As Double
    Dim EdgeLeft() As Double
    Dim EdgeRight() As Double
    Dim AsLeft() As Double
    Dim AsRight() As Double
    Dim ShearAv() As Double
    Dim StressCompLeft() As Double
    Dim StressCompRight() As Double
    Dim StressLimitLeft() As Double
    Dim StressLimitRight() As Double
    Dim CDepthLeft() As Double
    Dim CLimitLeft() As Double
    Dim CDepthRight() As Double
    Dim CLimitRight() As Double
    Dim InelasticRotDemand() As Double
    Dim InelasticRotCapacity() As Double
    Dim NormCompStress() As Double
    Dim NormCompStressLimit() As Double
    Dim CDepth() As Double
    Dim BZoneL() As Double
    Dim BZoneR() As Double
    Dim BZoneLength() As Double
    Dim WarnMsg() As String
    Dim ErrMsg() As String
    
    
ret = mySapModel.DesignShearWall.GetPierSummaryResults(Story, PierLabel, Station, DesignType, PierSecType, EdgeBar, EndBar, BarSpacing, ReinfPercent, CurrPercent, DCRatio, PierLeg, LegX1, LegY1, LegX2, LegY2, EdgeLeft, EdgeRight, AsLeft, AsRight, ShearAv, StressCompLeft, StressCompRight, StressLimitLeft, StressLimitRight, CDepthLeft, CLimitLeft, CDepthRight, CLimitRight, InelasticRotDemand, InelasticRotCapacity, NormCompStress, NormCompStressLimit, CDepth, BZoneL, BZoneR, BZoneLength, WarnMsg, ErrMsg)
Dim story1 As Variant, story2 As Variant
Dim Pier1 As Variant, Pier2 As Variant

For i = 0 To UBound(Story)
    story1 = Story(i)
    Pier1 = PierLabel(i)
    
    If story2 = story1 And Pier2 = Pier1 Then GoTo NextRow
    Dim Reinf() As Variant
    Dim ShearReinf() As Variant
    Dim St As Variant
    k = 0
        For j = 0 To UBound(Story)
            If story1 = Story(j) And Pier1 = PierLabel(j) Then
               k = k + 1
               St = Station(j)
               ReDim Preserve Reinf(k)
               ReDim Preserve ShearReinf(k)
               Reinf(k) = ReinfPercent(j)
               ShearReinf(k) = ShearAv(j)
             End If
        Next j

    Dim max_reinf As Variant, max_shear As Variant
        max_reinf = WorksheetFunction.Max(Reinf)
        max_shear = WorksheetFunction.Max(ShearReinf)
   
    Dim k1 As Integer
        k1 = k1 + 1
    
        WS_SW.Range("B" & 4 + k1) = Pier1
        WS_SW.Range("C" & 4 + k1) = story1
       ' WS_SW.Range("D" & 4 + k1) = Length * 10
        WS_SW.Range("H" & 4 + k1) = max_reinf / 100
        WS_SW.Range("G" & 4 + k1) = max_shear * 10000
        
        If Pier2 = Pier1 Then
            GoTo END_BORDER
        Else
            With WS_SW.Range("A" & 4 + k1 & ":" & "Q" & 4 + k1).Borders(xlEdgeTop)
                 .LineStyle = xlContinuous
                 .ThemeColor = 5
                 .TintAndShade = 0.2
                 .Weight = xlThin
                 
            End With
       End If

END_BORDER:
        
        story2 = story1
        Pier2 = Pier1
                
NextRow:
       If i = UBound(Story) Then
            With WS_SW.Range("A" & 4 + k1 & ":" & "Q" & 4 + k1).Borders(xlEdgeBottom)
                 .LineStyle = xlContinuous
                 .ThemeColor = 5
                 .TintAndShade = 0.2
                 .Weight = xlThin
                 
            End With
        End If
    
'pier properties
    Dim Name As String
    Dim NumberStories As Long
    Dim StoryName() As String
    Dim AxisAngle() As Double
    Dim NumAreaObjs() As Long
    Dim NumLineObjs() As Long
    Dim WidthBot() As Double
    Dim ThicknessBot() As Double
    Dim WidthTop() As Double
    Dim ThicknessTop() As Double
    Dim MatProp() As String
    Dim CGBotX() As Double
    Dim CGBotY() As Double
    Dim CGBotZ() As Double
    Dim CGTopX() As Double
    Dim CGTopY() As Double
    Dim CGTopZ() As Double

    ret = mySapModel.PierLabel.GetSectionProperties(PierLabel(i), NumberStories, StoryName, AxisAngle, NumAreaObjs, NumLineObjs, WidthBot, ThicknessBot, WidthTop, ThicknessTop, MatProp, CGBotX, CGBotY, CGBotZ, CGTopX, CGTopY, CGTopZ)

    Dim storyNumber As Integer
    For storyNumber = 0 To NumberStories - 1
        If Story(i) = StoryName(storyNumber) Then
        
            WS_SW.Range("D" & 4 + k1) = WidthBot(storyNumber) * 1000
            WS_SW.Range("E" & 4 + k1) = ThicknessBot(storyNumber) * 1000
            WS_SW.Range("F" & 4 + k1) = ThicknessBot(storyNumber) * 1000
            Dim k4 As Integer
            For k4 = 0 To UBound(ErrMsg)
                If ErrMsg(k4) <> "No Message" And PierLabel(k4) = PierLabel(i) Then
                    WS_SW.Range("Q" & 4 + k1) = ErrMsg(k4)
                End If
            
            Next k4
            If WS_SW.Range("Q" & 4 + k1) = "" Then WS_SW.Range("Q" & 4 + k1) = "No Message"
            
        End If
    Next storyNumber
Next i


Call StoryHt
End Sub
Sub Pier_Length()
    Dim Name As String
    Dim NumberStories() As Integer
    Dim StoryName() As String
    Dim AxisAngle() As Double
    Dim NumAreaObjs() As Integer
    Dim NumLineObjs() As Integer
    Dim WidthBot() As Double
    Dim ThicknessBot() As Double
    Dim WidthTop() As Double
    Dim ThicknessTop() As Double
    Dim MatProp() As String
    Dim CGBotX() As Double
    Dim CGBotY() As Double
    Dim CGBotZ() As Double
    Dim CGTopX() As Double
    Dim CGTopY() As Double
    Dim CGTopZ() As Double


ret = GetSectionProperties(Name, NumberStories, StoryName, AxisAngle, NumAreaObjs, NumLineObjs, WidthBot, ThicknessBot, WidthTop, ThicknessTop, MatProp, CGBotX, CGBotY, CGBotZ, CGTopX, CGTopY, CGTopZ)
End Sub

Sub Wall_Reinf()
Call Shear_reinf
Dim WS_SW As Worksheet
Set WS_SW = Worksheets("SHEAR WALL")
Dim Count_rows As Integer
Count_rows = WorksheetFunction.CountA(WS_SW.Range("B5:B200"))
    Dim pi As Double
    Dim BAR_DIA_ALL(7) As Integer, Bar_DIA_Count As Integer
    Dim Spacing_All(4) As Integer
        pi = WorksheetFunction.pi
        BAR_DIA_ALL(1) = 12
        BAR_DIA_ALL(2) = 16
        BAR_DIA_ALL(3) = 20
        BAR_DIA_ALL(4) = 22
        BAR_DIA_ALL(5) = 25
        BAR_DIA_ALL(6) = 28
        BAR_DIA_ALL(7) = 32
       
        
        Spacing_All(1) = 200
        Spacing_All(2) = 150
        Spacing_All(3) = 125
        Spacing_All(4) = 100


        Dim Error1() As Variant
        Dim DATA_All1() As Variant
        Dim DATA_All2() As Variant
        Dim DATA_All3() As Variant
        Dim DATA_All4() As Variant
For i = 1 To Count_rows

    Dim WLength, Wwidth, WBoundary As Double
    Dim Req_Reinf_Percent, Req_Reinf_Shear As Double
    Dim Req_Reinf_Area As Double
    Dim BL_bars As Integer
    
 ''''''READ DATA FROM EXCEL'''''
    WLength = WS_SW.Range("A4").Offset(i, 3) 'in mm
    Wwidth = WS_SW.Range("A4").Offset(i, 4)
    WBoundary = WS_SW.Range("A4").Offset(i, 5)
    Req_Reinf_Shear = WS_SW.Range("A4").Offset(i, 6)
    Req_Reinf_Percent = WS_SW.Range("A4").Offset(i, 7)
    
'''''''Calculation''''''''''
    Req_Reinf_Area = ((WLength * Wwidth) / 100) * (Req_Reinf_Percent)
    BL_bars = (WorksheetFunction.RoundDown(WBoundary / 100, 0) + WorksheetFunction.RoundDown(Wwidth / 100, 0)) * 2 - 4
    
    Dim Bar_Dia, Spacing, BL_Dia(2), BL_Dia_Count, BL, k1 As Integer
    ReDim Error1(0) As Variant
    ReDim DATA_All1(0) As Variant
    ReDim DATA_All2(0) As Variant
    ReDim DATA_All3(0) As Variant
    ReDim DATA_All4(0) As Variant
    
    For Bar_Dia = 1 To UBound(BAR_DIA_ALL)
        If BAR_DIA_ALL(Bar_Dia) = 32 Then
            BL_Dia(1) = 32
            BL_Dia_Count = 1
        Else
            BL_Dia(1) = BAR_DIA_ALL(Bar_Dia)
            BL_Dia(2) = BAR_DIA_ALL(Bar_Dia + 1)
            BL_Dia_Count = 2
        End If
            
            For Spacing = 1 To UBound(Spacing_All)
                    For BL = 1 To BL_Dia_Count
                         Dim Provided_Wall_Reinf, Provided_BL_Reinf, Provided_Total_Reinf As Double
                         
                         Provided_Wall_Reinf = (2 * Rebar_Area(BAR_DIA_ALL(Bar_Dia)) / 100) * (WLength - (2 * WBoundary)) / (Spacing_All(Spacing))
                         Provided_BL_Reinf = (2 * BL_bars * Rebar_Area(BL_Dia(BL)) / 100)
                         Provided_Total_Reinf = Provided_Wall_Reinf + Provided_BL_Reinf
                            
                            If Provided_Total_Reinf > Req_Reinf_Area Then
                               k1 = k1 + 1
                               ReDim Preserve Error1(k1), DATA_All1(k1), DATA_All2(k1), DATA_All3(k1), DATA_All4(k1)
                                                              
                               Error1(k1) = (Provided_Total_Reinf - Req_Reinf_Area)
                               DATA_All1(k1) = BAR_DIA_ALL(Bar_Dia)
                               DATA_All2(k1) = Spacing_All(Spacing)
                               DATA_All3(k1) = BL_Dia(BL)
                               DATA_All4(k1) = BL_bars
                               
                            End If
                                        
                    Next BL
            Next Spacing
     Next Bar_Dia
    
    Dim Minimum_Error As Variant
    Minimum_Error = WorksheetFunction.Min(Error1)
        For j = 1 To UBound(Error1)
            If Error1(j) = Minimum_Error Then
                WS_SW.Range("A4").Offset(i, 8) = DATA_All1(j) '= BAR_DIA_ALL(Bar_dia)
                WS_SW.Range("A4").Offset(i, 9) = DATA_All2(j) ' = Spacing_All(Spacing)
                WS_SW.Range("A4").Offset(i, 10) = DATA_All3(j) ' = BL_Dia(BL)
                WS_SW.Range("A4").Offset(i, 11) = DATA_All4(j) ' = BL_bars
             End If
        Next j
     
Next i

End Sub

Sub Shear_reinf()
Dim WS_SW As Worksheet
Set WS_SW = Worksheets("SHEAR WALL")
Dim Count_rows As Integer
Count_rows = WorksheetFunction.CountA(WS_SW.Range("B5:B200"))
    Dim pi As Double
    Dim BAR_DIA_ALL(7) As Integer, Bar_DIA_Count As Integer
    Dim Spacing_All(4) As Integer
        pi = WorksheetFunction.pi
        BAR_DIA_ALL(1) = 12
        BAR_DIA_ALL(2) = 16
        BAR_DIA_ALL(3) = 20
        BAR_DIA_ALL(4) = 22
        BAR_DIA_ALL(5) = 25
        BAR_DIA_ALL(6) = 28
        BAR_DIA_ALL(7) = 32
       ''''''''''''''''''''''''''''
        Spacing_All(1) = 200
        Spacing_All(2) = 150
        Spacing_All(3) = 125
        Spacing_All(4) = 100
'''''''''''''''''''''''''''''''''''''''
        Dim Error1() As Variant
        Dim DATA_All1() As Variant
        Dim DATA_All2() As Variant
        Dim DATA_All3() As Variant
        Dim DATA_All4() As Variant

For i = 1 To Count_rows

    Dim WLength, Wwidth, WBoundary As Double
    Dim Req_Reinf_Shear As Double
    
 ''''''READ DATA FROM EXCEL'''''
    WLength = WS_SW.Range("A4").Offset(i, 3) 'in mm
    Wwidth = WS_SW.Range("A4").Offset(i, 4)
    WBoundary = WS_SW.Range("A4").Offset(i, 5)
    Req_Reinf_Shear = WS_SW.Range("A4").Offset(i, 6)

    Dim Bar_Dia, Spacing, k1 As Integer
    ReDim Error1(0) As Variant
    ReDim DATA_All1(0) As Variant
    ReDim DATA_All2(0) As Variant
    ReDim DATA_All3(0) As Variant
    ReDim DATA_All4(0) As Variant
    
    For Bar_Dia = 1 To UBound(BAR_DIA_ALL)
            For Spacing = 1 To UBound(Spacing_All)
                   
                         Dim Provided_Wall_Reinf, Provided_Total_Reinf As Double
                         
                         Provided_Wall_Reinf = (2 * Rebar_Area(BAR_DIA_ALL(Bar_Dia)) / 100) * (1000) / (Spacing_All(Spacing))
                         Provided_Total_Reinf = Provided_Wall_Reinf
                            
                            If Provided_Total_Reinf > Req_Reinf_Shear Then
                               k1 = k1 + 1
                               ReDim Preserve Error1(k1), DATA_All1(k1), DATA_All2(k1), DATA_All3(k1), DATA_All4(k1)
                                                              
                               Error1(k1) = (Provided_Total_Reinf - Req_Reinf_Shear)
                               DATA_All1(k1) = BAR_DIA_ALL(Bar_Dia)
                               DATA_All2(k1) = Spacing_All(Spacing)

                               
                            End If
                 
            Next Spacing
     Next Bar_Dia
    Dim Minimum_Error As Variant
    Minimum_Error = WorksheetFunction.Min(Error1)
        For j = 1 To UBound(Error1)
            If Error1(j) = Minimum_Error Then
                WS_SW.Range("A4").Offset(i, 13) = DATA_All1(j) '= BAR_DIA_ALL(Bar_dia)
                WS_SW.Range("A4").Offset(i, 14) = DATA_All2(j) ' = Spacing_All(Spacing)

             End If
        Next j

Next i

End Sub

Sub clear_ShearWall()
Dim WS_SW As Worksheet
Set WS_SW = Worksheets("SHEAR WALL")
Dim Count_rows As Integer
WS_SW.Range("A5:L200").ClearContents
WS_SW.Range("N5:O200").ClearContents
WS_SW.Range("Q5:Q200").ClearContents
Call Clear_Border
End Sub
Sub border1()
  For i = 1 To Total_Rows + 1
        If Sorting_Matrix(2, i) = "" Then GoTo END_BORDER
        If Sorting_Matrix(2, i) <> Sorting_Matrix(2, i + 1) Then
        
                With Range("A" & 2 + i & ":" & "Q" & 2 + i).Borders(xlEdgeBottom)
                    .LineStyle = xlContinuous
                    .Weight = xlThin
                End With
       End If
 END_BORDER
 Next i
 
End Sub
Sub Clear_Border()
Dim R As Range
    Set R = Range("A3:Q2000")
    R.Borders(xlDiagonalDown).LineStyle = xlNone
    R.Borders(xlDiagonalUp).LineStyle = xlNone
    R.Borders(xlEdgeLeft).LineStyle = xlNone
    R.Borders(xlEdgeTop).LineStyle = xlNone
    R.Borders(xlEdgeBottom).LineStyle = xlNone
    R.Borders(xlEdgeRight).LineStyle = xlNone
    R.Borders(xlInsideVertical).LineStyle = xlNone
    R.Borders(xlInsideHorizontal).LineStyle = xlNone
End Sub

Sub StoryHt()
Call ATTACH_TO_ETABS_WALLS
Dim Height As Double
Dim StoryName As String
Dim WS_SW As Worksheet
Set WS_SW = Worksheets("SHEAR WALL")

For i = 1 To 1000
    If WS_SW.Range("A4").Offset(i, 2) <> "" Then
       StoryName = WS_SW.Range("A4").Offset(i, 2)
        ret = mySapModel.Story.GetHeight(StoryName, Height)
        WS_SW.Range("A4").Offset(i, 0) = Height
    Else
    End If
Next i
End Sub
