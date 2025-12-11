Attribute VB_Name = "M14_Reporting"
Option Explicit

' ==========================================================================================
' Module:       M14_Reporting
' Description:  Generates the Beam Schedule and other reports.
'               Part of the "UI / DEV" Agent scope.
' Dependencies: M04_Utilities, M02_Types
' ==========================================================================================

' ------------------------------------------------------------------------------------------
' Public Macro: Generate Beam Schedule
' ------------------------------------------------------------------------------------------
Public Sub Generate_Beam_Schedule()
    Dim wsDesign As Worksheet
    Dim wsSchedule As Worksheet
    Dim tblDesign As ListObject
    Dim tblSchedule As ListObject
    
    ' 1. Initialize
    Set wsDesign = ThisWorkbook.Sheets("BEAM_DESIGN")
    Set wsSchedule = ThisWorkbook.Sheets("BEAM_SCHEDULE")
    Set tblDesign = wsDesign.ListObjects("tbl_BeamDesign")
    
    ' Ensure Schedule Table Exists (or clear it)
    On Error Resume Next
    Set tblSchedule = wsSchedule.ListObjects("tbl_BeamSchedule")
    On Error GoTo 0
    
    If tblSchedule Is Nothing Then
        MsgBox "Schedule table not found. Please run Setup.", vbCritical
        Exit Sub
    End If
    
    If Not tblSchedule.DataBodyRange Is Nothing Then
        tblSchedule.DataBodyRange.Delete
    End If
    
    Application.ScreenUpdating = False
    
    ' 2. Process Design Data
    Call Sort_Design_Table(tblDesign)
    Call Process_Design_To_Schedule(tblDesign, tblSchedule)
    
    Application.ScreenUpdating = True
    MsgBox "Beam Schedule Generated!", vbInformation
End Sub

' ------------------------------------------------------------------------------------------
' Core Logic: Pivot Design Data to Schedule
' ------------------------------------------------------------------------------------------
Private Sub Process_Design_To_Schedule(tblIn As ListObject, tblOut As ListObject)
    Dim i As Long
    Dim r As Range
    Dim currentID As String, lastID As String
    Dim currentStory As String, lastStory As String
    Dim b As Double, D As Double
    
    ' 0. Pre-Check
    If tblIn.ListRows.Count = 0 Then Exit Sub
    
    ' 1. Sort Input Table (Critical for Grouping)
    ' Sort by Story (Asc) then ID (Asc)
    With tblIn.Sort
        .SortFields.Clear
        .SortFields.Add Key:=tblIn.ListColumns("Story").Range, Order:=xlAscending
        .SortFields.Add Key:=tblIn.ListColumns("ID").Range, Order:=xlAscending
        .Header = xlYes
        .Apply
    End With
    
    ' Storage for one beam's sections
    Dim topSteel(1 To 3) As String ' Start, Mid, End
    Dim botSteel(1 To 3) As String
    Dim shearSteel(1 To 3) As String
    
    ' Initialize arrays with "-"
    Dim k As Integer
    For k = 1 To 3
        topSteel(k) = "-"
        botSteel(k) = "-"
        shearSteel(k) = "-"
    Next k
    
    ' 2. Dynamic Column Indices (Robustness)
    Dim idxID As Integer, idxStory As Integer, idxLoc As Integer
    Dim idxB As Integer, idxD As Integer, idxMu As Integer
    Dim idxAst As Integer, idxAsc As Integer, idxStirrup As Integer
    
    On Error Resume Next
    idxID = tblIn.ListColumns("ID").Index
    idxStory = tblIn.ListColumns("Story").Index
    idxLoc = tblIn.ListColumns("Span").Index ' Note: Header is "Span" in Design Sheet, but holds Loc
    idxB = tblIn.ListColumns("b").Index
    idxD = tblIn.ListColumns("D").Index
    idxMu = tblIn.ListColumns("Mu").Index
    idxAst = tblIn.ListColumns("Ast_Req").Index
    idxAsc = tblIn.ListColumns("Asc_Req").Index
    idxStirrup = tblIn.ListColumns("Stirrups").Index
    On Error GoTo 0
    
    If idxID = 0 Or idxStory = 0 Then
        MsgBox "Critical columns missing in Design Table.", vbCritical
        Exit Sub
    End If
    
    lastID = ""
    
    For i = 1 To tblIn.ListRows.Count
        Set r = tblIn.ListRows(i).Range
        currentID = r.Cells(1, idxID).Value
        currentStory = r.Cells(1, idxStory).Value
        
        ' New Beam Detected (Group by ID + Story)
        If (currentID <> lastID Or currentStory <> lastStory) And lastID <> "" Then
            Call Write_Schedule_Row(tblOut, lastID, lastStory, b, D, topSteel, botSteel, shearSteel)
            ' Reset
            For k = 1 To 3
                topSteel(k) = "-"
                botSteel(k) = "-"
                shearSteel(k) = "-"
            Next k
        End If
        
        ' Capture Geometry
        b = r.Cells(1, idxB).Value
        D = r.Cells(1, idxD).Value
        
        ' Capture Data based on Location
        Dim loc As String
        Dim idx As Integer
        loc = UCase(r.Cells(1, idxLoc).Value)
        
        Select Case loc
            Case "START": idx = 1
            Case "MID": idx = 2
            Case "END": idx = 3
            Case Else: idx = 0 ' Ignore unknown locations
        End Select
        
        If idx > 0 Then
            Dim ast As Double, asc As Double
            Dim stirrup As String
            ast = r.Cells(1, idxAst).Value
            asc = r.Cells(1, idxAsc).Value
            stirrup = r.Cells(1, idxStirrup).Value
            
            ' Logic:
            ' Mid Span: Bottom = Ast, Top = Asc (if any)
            ' Supports (Start/End): Top = Ast, Bottom = Asc (if any)
            ' Note: This is a simplification. Usually Ast at support is Top.
            ' Let's assume:
            ' - Start/End: Main tension is Top (Hogging). Compression is Bottom.
            ' - Mid: Main tension is Bottom (Sagging). Compression is Top.
            ' However, the library returns Ast_Required based on the input Mu.
            ' If Mu was negative (Hogging), Ast is for Top.
            ' If Mu was positive (Sagging), Ast is for Bottom.
            ' We need to know the sign of Mu to place steel correctly!
            ' Let's check Mu column (Col 9).
            
            Dim Mu As Double
            Mu = r.Cells(1, idxMu).Value
            
            Dim mainSteel As String, compSteel As String
            mainSteel = Get_Bar_Pattern(ast)
            compSteel = Get_Bar_Pattern(asc)
            
            If Mu < 0 Then ' Hogging -> Top Tension
                topSteel(idx) = mainSteel
                botSteel(idx) = compSteel
            Else ' Sagging -> Bottom Tension
                botSteel(idx) = mainSteel
                topSteel(idx) = compSteel
            End If
            
            If stirrup = "" Or stirrup = "0" Then stirrup = "-"
            shearSteel(idx) = stirrup
        End If
        
        lastID = currentID
        lastStory = currentStory
    Next i
    
    ' Write Final Beam
    If lastID <> "" Then
        Call Write_Schedule_Row(tblOut, lastID, lastStory, b, D, topSteel, botSteel, shearSteel)
    End If
    
End Sub

Private Sub Sort_Design_Table(tbl As ListObject)
    ' Sort by Story (col 2), then ID (col 1) to ensure grouping works even if BEAM_DESIGN is out of order.
    On Error GoTo Fail
    With tbl.Sort
        .SortFields.Clear
        .SortFields.Add Key:=tbl.ListColumns(2).Range, SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortTextAsNumbers
        .SortFields.Add Key:=tbl.ListColumns(1).Range, SortOn:=xlSortOnValues, Order:=xlAscending, DataOption:=xlSortTextAsNumbers
        .Header = xlYes
        .Apply
    End With
    Exit Sub
Fail:
    ' If sorting fails (e.g., protected sheet), continue without sorting.
End Sub

Private Sub Write_Schedule_Row(tbl As ListObject, ID As String, Story As String, b As Double, D As Double, top() As String, bot() As String, shear() As String)
    Dim newRow As ListRow
    Set newRow = tbl.ListRows.Add
    
    With newRow.Range
        .Cells(1, 1).Value = Story
        .Cells(1, 2).Value = ID
        .Cells(1, 3).Value = b & "x" & D
        
        ' Bottom (Start, Mid, End)
        .Cells(1, 4).Value = bot(1)
        .Cells(1, 5).Value = bot(2)
        .Cells(1, 6).Value = bot(3)
        
        ' Top (Start, Mid, End)
        .Cells(1, 7).Value = top(1)
        .Cells(1, 8).Value = top(2)
        .Cells(1, 9).Value = top(3)
        
        ' Stirrups (Start, Mid, End)
        .Cells(1, 10).Value = shear(1)
        .Cells(1, 11).Value = shear(2)
        .Cells(1, 12).Value = shear(3)
    End With
End Sub

' ------------------------------------------------------------------------------------------
' Helper: Convert Area to Pattern (Simple "N-Dia")
' ------------------------------------------------------------------------------------------
Private Function Get_Bar_Pattern(area As Double) As String
    If area <= 0 Then
        Get_Bar_Pattern = "-"
        Exit Function
    End If
    
    ' Default to 16mm for now (Area = 201)
    ' Ideally, pick 12, 16, 20, 25 based on magnitude
    Dim dia As Integer
    Dim barArea As Double
    
    If area < 300 Then
        dia = 12
    ElseIf area < 800 Then
        dia = 16
    ElseIf area < 1500 Then
        dia = 20
    Else
        dia = 25
    End If
    
    barArea = 3.14159 * (dia / 2) ^ 2
    
    Dim count As Integer
    ' Manual Ceiling
    count = Int(area / barArea)
    If (area / barArea) > count Then count = count + 1
    
    ' Min 2 bars usually
    If count < 2 Then count = 2
    
    Get_Bar_Pattern = count & "-" & dia & " (#" & Round(area, 0) & ")"
End Function
