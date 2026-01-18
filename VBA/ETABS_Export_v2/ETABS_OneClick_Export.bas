Attribute VB_Name = "ETABS_OneClick_Export"
Option Explicit

'==============================================================================
' ETABS ONE-CLICK EXPORT - Simplest Possible Export for Streamlit
'==============================================================================
'
' PHILOSOPHY:
'   - User clicks ONE button
'   - No configuration needed
'   - Export envelope values (worst case) for design
'   - Ready for IS456 beam design in Streamlit
'
' OUTPUT: Single CSV with one row per beam containing:
'   - Max positive moment (for sagging reinforcement)
'   - Max negative moment (for hogging reinforcement)
'   - Max shear force (for stirrup design)
'   - Section dimensions (width, depth)
'   - Span length
'
' REQUIREMENTS:
'   1. ETABS model open with analysis completed
'   2. Add ETABS API reference (Tools → References → ETABS.exe)
'
' Created: 2026-01-17 | Version: 1.0
'==============================================================================

' Module-level ETABS objects
Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

' ============================================
' MAIN FUNCTION - ONE CLICK EXPORT
' ============================================

Sub ExportForStreamlit()
    '
    ' THIS IS THE ONLY FUNCTION USER NEEDS TO RUN
    ' Just press F5 or Alt+F8 → ExportForStreamlit → Run
    '
    On Error GoTo ErrorHandler
    
    Application.StatusBar = "Connecting to ETABS..."
    DoEvents
    
    ' 1. Connect to ETABS
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)  ' kN, meters
    
    Debug.Print "=========================================="
    Debug.Print "ETABS Export for Streamlit"
    Debug.Print "Model: " & mySapModel.GetModelFilename(False)
    Debug.Print "=========================================="
    
    ' 2. Select ALL cases and combos (no filtering)
    Application.StatusBar = "Selecting all load cases..."
    DoEvents
    Call SelectAllCasesAndCombos
    
    ' 3. Get all frames
    Application.StatusBar = "Getting frame list..."
    DoEvents
    
    Dim NumberFrames As Long
    Dim FrameName() As String
    ret = mySapModel.FrameObj.GetNameList(NumberFrames, FrameName)
    
    Debug.Print "Total frames: " & NumberFrames
    
    ' 4. Create output file
    Dim outputFolder As String
    outputFolder = Environ("USERPROFILE") & "\Documents\ETABS_Export"
    If Dir(outputFolder, vbDirectory) = "" Then MkDir outputFolder
    
    Dim csvPath As String
    csvPath = outputFolder & "\beam_design_data.csv"
    
    Dim f As Integer
    f = FreeFile
    Open csvPath For Output As #f
    
    ' Write header - exactly what Streamlit needs
    Print #f, "Label,Story,Width_mm,Depth_mm,Span_m,Mu_max_kNm,Mu_min_kNm,Vu_max_kN,fck,fy"
    
    ' 5. Process each frame
    Dim exported As Long
    exported = 0
    
    Dim i As Long
    For i = 0 To NumberFrames - 1
        Application.StatusBar = "Processing: " & (i + 1) & "/" & NumberFrames & " frames"
        If i Mod 10 = 0 Then DoEvents
        
        ' Get frame data
        Dim beamData As BeamExportData
        beamData = GetBeamData(FrameName(i))
        
        ' Skip if no valid data (e.g., columns, braces)
        If beamData.IsValid Then
            ' Write CSV row
            Print #f, _
                beamData.Label & "," & _
                beamData.Story & "," & _
                Format(beamData.Width_mm, "0") & "," & _
                Format(beamData.Depth_mm, "0") & "," & _
                Format(beamData.Span_m, "0.000") & "," & _
                Format(beamData.Mu_max, "0.000") & "," & _
                Format(beamData.Mu_min, "0.000") & "," & _
                Format(beamData.Vu_max, "0.000") & "," & _
                Format(beamData.fck, "0") & "," & _
                Format(beamData.fy, "0")
            
            exported = exported + 1
        End If
    Next i
    
    Close #f
    Application.StatusBar = False
    
    Debug.Print ""
    Debug.Print "=========================================="
    Debug.Print "EXPORT COMPLETE!"
    Debug.Print "Beams exported: " & exported
    Debug.Print "Output file: " & csvPath
    Debug.Print "=========================================="
    
    ' 6. Show success message
    MsgBox "✅ Export Complete!" & vbCrLf & vbCrLf & _
           "Beams exported: " & exported & vbCrLf & _
           "File: beam_design_data.csv" & vbCrLf & vbCrLf & _
           "Upload this file to Streamlit for IS456 design.", _
           vbInformation, "ETABS Export"
    
    ' Open output folder
    Shell "explorer.exe /select,""" & csvPath & """", vbNormalFocus
    
    Exit Sub

ErrorHandler:
    Application.StatusBar = False
    Close #f
    MsgBox "❌ Export Failed!" & vbCrLf & vbCrLf & _
           "Error: " & Err.Description & vbCrLf & _
           "Error #" & Err.Number & vbCrLf & vbCrLf & _
           "Make sure:" & vbCrLf & _
           "1. ETABS is open with a model" & vbCrLf & _
           "2. Analysis has been run" & vbCrLf & _
           "3. ETABS reference is added (Tools → References)", _
           vbCritical, "Export Error"
End Sub

' ============================================
' DATA STRUCTURE
' ============================================

Private Type BeamExportData
    IsValid As Boolean
    Label As String
    Story As String
    Width_mm As Double
    Depth_mm As Double
    Span_m As Double
    Mu_max As Double      ' Max positive moment (sagging)
    Mu_min As Double      ' Max negative moment (hogging, stored as negative)
    Vu_max As Double      ' Max absolute shear
    fck As Double         ' Concrete grade (default 25 MPa)
    fy As Double          ' Steel grade (default 500 MPa)
End Type

' ============================================
' GET ALL DATA FOR ONE BEAM
' ============================================

Private Function GetBeamData(frameName As String) As BeamExportData
    Dim ret As Long
    Dim result As BeamExportData
    result.IsValid = False
    
    ' --- Get Story ---
    Dim point1 As String, point2 As String
    ret = mySapModel.FrameObj.GetPoints(frameName, point1, point2)
    
    If ret <> 0 Then Exit Function
    
    Dim label As String, story As String
    ret = mySapModel.PointObj.GetLabelFromName(point1, label, story)
    result.Story = IIf(ret = 0, story, "Unknown")
    result.Label = frameName
    
    ' --- Get Span Length ---
    Dim x1 As Double, y1 As Double, z1 As Double
    Dim x2 As Double, y2 As Double, z2 As Double
    
    ret = mySapModel.PointObj.GetCoordCartesian(point1, x1, y1, z1)
    ret = mySapModel.PointObj.GetCoordCartesian(point2, x2, y2, z2)
    
    result.Span_m = Sqr((x2 - x1) ^ 2 + (y2 - y1) ^ 2 + (z2 - z1) ^ 2)
    
    ' Skip if vertical (likely a column, not beam)
    If Abs(z2 - z1) > 0.1 And result.Span_m > 0.1 Then
        Dim horizontalSpan As Double
        horizontalSpan = Sqr((x2 - x1) ^ 2 + (y2 - y1) ^ 2)
        If horizontalSpan < Abs(z2 - z1) * 0.5 Then
            ' More vertical than horizontal = column
            Exit Function
        End If
    End If
    
    ' --- Get Section Dimensions ---
    Dim sectName As String, sAuto As String
    ret = mySapModel.FrameObj.GetSection(frameName, sectName, sAuto)
    
    If ret <> 0 Then Exit Function
    
    ' Try rectangular section
    Dim fileName As String, matProp As String
    Dim t3 As Double, t2 As Double  ' t3=depth, t2=width
    Dim color As Long, notes As String, guid As String
    
    ret = mySapModel.PropFrame.GetRectangle(sectName, fileName, matProp, _
        t3, t2, color, notes, guid)
    
    If ret = 0 And t2 > 0 And t3 > 0 Then
        ' Convert to mm (if in meters, values will be < 1)
        If t2 < 1 And t3 < 1 Then
            result.Width_mm = t2 * 1000
            result.Depth_mm = t3 * 1000
        Else
            result.Width_mm = t2
            result.Depth_mm = t3
        End If
    Else
        ' Use defaults if section not found
        result.Width_mm = 230
        result.Depth_mm = 450
    End If
    
    ' --- Get Forces (Envelope) ---
    Dim NumberResults As Long
    Dim obj() As String, ObjSta() As Double
    Dim Elm() As String, ElmSta() As Double
    Dim LoadCase() As String, StepType() As String, StepNum() As Double
    Dim P() As Double, V2() As Double, V3() As Double
    Dim T() As Double, M2() As Double, M3() As Double
    
    ret = mySapModel.Results.FrameForce( _
        frameName, eItemTypeElm_ObjectElm, NumberResults, _
        obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, _
        P, V2, V3, T, M2, M3)
    
    If ret <> 0 Or NumberResults = 0 Then
        ' No results - use zeros
        result.Mu_max = 0
        result.Mu_min = 0
        result.Vu_max = 0
    Else
        ' Find envelope values (worst case across all combos and stations)
        result.Mu_max = -1E+30  ' Will find max positive
        result.Mu_min = 1E+30   ' Will find max negative
        result.Vu_max = 0       ' Will find max absolute
        
        Dim j As Long
        For j = 0 To NumberResults - 1
            ' Max positive moment
            If M3(j) > result.Mu_max Then result.Mu_max = M3(j)
            
            ' Max negative moment
            If M3(j) < result.Mu_min Then result.Mu_min = M3(j)
            
            ' Max absolute shear
            If Abs(V2(j)) > result.Vu_max Then result.Vu_max = Abs(V2(j))
        Next j
        
        ' Handle case where no positive or negative moments found
        If result.Mu_max < -1E+29 Then result.Mu_max = 0
        If result.Mu_min > 1E+29 Then result.Mu_min = 0
    End If
    
    ' --- Material Properties (Defaults) ---
    ' TODO: Could parse from material name if needed
    result.fck = 25   ' M25 concrete
    result.fy = 500   ' Fe500 steel
    
    result.IsValid = True
    GetBeamData = result
End Function

' ============================================
' SELECT ALL CASES AND COMBOS
' ============================================

Private Sub SelectAllCasesAndCombos()
    Dim ret As Long
    Dim NumberItems As Long
    Dim ItemName() As String
    Dim c As Long
    
    ' Select all load cases
    ret = mySapModel.LoadCases.GetNameList(NumberItems, ItemName)
    Debug.Print "Load cases: " & NumberItems
    
    For c = 0 To NumberItems - 1
        ret = mySapModel.Results.Setup.SetCaseSelectedForOutput(ItemName(c))
    Next c
    
    ' Select all load combos
    ret = mySapModel.RespCombo.GetNameList(NumberItems, ItemName)
    Debug.Print "Load combos: " & NumberItems
    
    For c = 0 To NumberItems - 1
        ret = mySapModel.Results.Setup.SetComboSelectedForOutput(ItemName(c))
    Next c
End Sub
