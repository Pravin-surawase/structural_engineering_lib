Attribute VB_Name = "DEBUG_Step5_RawExport"
Option Explicit

'==============================================================================
' STEP 5: Export whatever we CAN get to Excel to see the actual data
'==============================================================================

Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub Step5_ExportRawData()
    On Error GoTo ErrorHandler
    
    ' Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    ' Select ALL cases (deselect doesn't work!)
    Dim NumberCases As Long
    Dim CaseName() As String
    ret = mySapModel.LoadCases.GetNameList(NumberCases, CaseName)
    
    Dim c As Long
    For c = 0 To NumberCases - 1
        ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(CaseName(c))
    Next c
    
    ' Also select combos
    Dim NumberCombos As Long
    Dim ComboName() As String
    ret = mySapModel.RespCombo.GetNameList(NumberCombos, ComboName)
    
    For c = 0 To NumberCombos - 1
        ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ComboName(c))
    Next c
    
    ' Get frames
    Dim NumberNames As Long
    Dim MyName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberNames, MyName)
    
    ' Create new worksheet
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("DEBUG_RawData")
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add
        ws.Name = "DEBUG_RawData"
    Else
        ws.Cells.Clear
    End If
    On Error GoTo ErrorHandler
    
    ' Write headers
    ws.Range("A1:J1").Value = Array("Frame", "LoadCase", "Station", "P", "V2", "V3", "T", "M2", "M3", "ObjSta")
    ws.Range("A1:J1").Font.Bold = True
    
    Dim row As Long
    row = 2
    
    Dim totalFrames As Long
    Dim framesWithResults As Long
    totalFrames = NumberNames
    
    ' Test first 10 frames
    Dim i As Long
    For i = 0 To Application.Min(9, NumberNames - 1)
        Dim NumberResults As Long
        Dim obj() As String, ObjSta() As Double
        Dim Elm() As String, ElmSta() As Double
        Dim LoadCase() As String, StepType() As String, StepNum() As Double
        Dim P() As Double, V2() As Double, V3() As Double
        Dim T() As Double, M2() As Double, M3() As Double
        
        ret = mySapModel.Results.FrameForce( _
            MyName(i), eItemTypeElm_ObjectElm, NumberResults, _
            obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
            P, V2, V3, T, M2, M3)
        
        If ret = 0 And NumberResults > 0 Then
            framesWithResults = framesWithResults + 1
            
            ' Write all results for this frame
            Dim j As Long
            For j = 0 To NumberResults - 1
                ws.Cells(row, 1).Value = MyName(i)
                ws.Cells(row, 2).Value = LoadCase(j)
                ws.Cells(row, 3).Value = ElmSta(j)
                ws.Cells(row, 4).Value = P(j)
                ws.Cells(row, 5).Value = V2(j)
                ws.Cells(row, 6).Value = V3(j)
                ws.Cells(row, 7).Value = T(j)
                ws.Cells(row, 8).Value = M2(j)
                ws.Cells(row, 9).Value = M3(j)
                ws.Cells(row, 10).Value = ObjSta(j)
                row = row + 1
            Next j
        End If
    Next i
    
    ' Auto-fit columns
    ws.Columns("A:J").AutoFit
    
    ' Summary
    ws.Range("L1").Value = "Summary:"
    ws.Range("L2").Value = "Total frames tested:"
    ws.Range("M2").Value = Application.Min(10, NumberNames)
    ws.Range("L3").Value = "Frames with results:"
    ws.Range("M3").Value = framesWithResults
    ws.Range("L4").Value = "Total data rows:"
    ws.Range("M4").Value = row - 2
    
    ws.Activate
    
    MsgBox "Exported " & (row - 2) & " data rows to DEBUG_RawData sheet!" & vbCrLf & vbCrLf & _
           "Frames with results: " & framesWithResults & " / " & Application.Min(10, NumberNames), _
           vbInformation, "Raw Data Export"
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub
