Attribute VB_Name = "Test_DXF"
'@Module: Test_DXF
'@Description: Test Suite for M16_DXF - DXF Export Functions
'@Version: 0.7.0
'@Date: 2025-12-11

Option Explicit

Private m_PassCount As Long
Private m_FailCount As Long
Private m_TestOutput As String

' ============================================================================
' TEST RUNNER
' ============================================================================

Public Sub Run_All_DXF_Tests()
    m_PassCount = 0
    m_FailCount = 0
    m_TestOutput = "=== DXF Export Test Suite ===" & vbCrLf & vbCrLf
    
    ' Run test groups
    Call Test_DXF_Initialize
    Call Test_DXF_Primitives
    Call Test_DXF_Structural_Components
    Call Test_DXF_BeamSection
    Call Test_DXF_BeamLongitudinal
    Call Test_DXF_FullDetailing
    
    ' Summary
    m_TestOutput = m_TestOutput & vbCrLf & "=== SUMMARY ===" & vbCrLf
    m_TestOutput = m_TestOutput & "Passed: " & m_PassCount & vbCrLf
    m_TestOutput = m_TestOutput & "Failed: " & m_FailCount & vbCrLf
    m_TestOutput = m_TestOutput & "Total:  " & (m_PassCount + m_FailCount) & vbCrLf
    
    Debug.Print m_TestOutput
    
    ' Show summary in message box
    If m_FailCount = 0 Then
        MsgBox "All " & m_PassCount & " DXF tests passed!", vbInformation, "Test Results"
    Else
        MsgBox m_FailCount & " of " & (m_PassCount + m_FailCount) & " tests failed." & vbCrLf & _
               "Check Immediate window for details.", vbExclamation, "Test Results"
    End If
End Sub

' ============================================================================
' HELPER FUNCTIONS
' ============================================================================

Private Sub AssertTrue(ByVal condition As Boolean, ByVal testName As String)
    If condition Then
        m_PassCount = m_PassCount + 1
        m_TestOutput = m_TestOutput & "[PASS] " & testName & vbCrLf
    Else
        m_FailCount = m_FailCount + 1
        m_TestOutput = m_TestOutput & "[FAIL] " & testName & vbCrLf
    End If
End Sub

Private Sub AssertEqual(ByVal actual As Variant, ByVal expected As Variant, ByVal testName As String)
    If actual = expected Then
        m_PassCount = m_PassCount + 1
        m_TestOutput = m_TestOutput & "[PASS] " & testName & vbCrLf
    Else
        m_FailCount = m_FailCount + 1
        m_TestOutput = m_TestOutput & "[FAIL] " & testName & " (Expected: " & expected & ", Got: " & actual & ")" & vbCrLf
    End If
End Sub

Private Function GetTestFilePath(ByVal fileName As String) As String
    ' Returns path in user's temp folder
    GetTestFilePath = Environ("TEMP") & "\" & fileName
End Function

Private Sub CleanupTestFile(ByVal filePath As String)
    On Error Resume Next
    Kill filePath
End Sub

' ============================================================================
' TEST GROUPS
' ============================================================================

Private Sub Test_DXF_Initialize()
    m_TestOutput = m_TestOutput & vbCrLf & "--- DXF Initialize Tests ---" & vbCrLf
    
    Dim testFile As String
    testFile = GetTestFilePath("test_init.dxf")
    
    ' Test 1: Initialize creates file
    Dim success As Boolean
    success = M16_DXF.DXF_Initialize(testFile)
    Call AssertTrue(success, "DXF_Initialize returns True")
    
    ' Test 2: IsOpen returns True
    Call AssertTrue(M16_DXF.DXF_IsOpen(), "DXF_IsOpen returns True after init")
    
    ' Test 3: Close works
    Call M16_DXF.DXF_Close
    Call AssertTrue(Not M16_DXF.DXF_IsOpen(), "DXF_IsOpen returns False after close")
    
    ' Test 4: File exists
    Call AssertTrue(Dir(testFile) <> "", "DXF file was created")
    
    ' Cleanup
    Call CleanupTestFile(testFile)
End Sub

Private Sub Test_DXF_Primitives()
    m_TestOutput = m_TestOutput & vbCrLf & "--- DXF Primitives Tests ---" & vbCrLf
    
    Dim testFile As String
    testFile = GetTestFilePath("test_primitives.dxf")
    
    ' Initialize
    Call M16_DXF.DXF_Initialize(testFile)
    
    ' Test 5: Line entity
    Call M16_DXF.DXF_Line(0, 0, 100, 100, LAYER_BEAM_OUTLINE)
    Call AssertEqual(M16_DXF.DXF_GetEntityCount(), 1, "Line increases entity count")
    
    ' Test 6: Circle entity
    Call M16_DXF.DXF_Circle(50, 50, 25, LAYER_REBAR_MAIN)
    Call AssertEqual(M16_DXF.DXF_GetEntityCount(), 2, "Circle increases entity count")
    
    ' Test 7: Arc entity
    Call M16_DXF.DXF_Arc(50, 50, 30, 0, 90, LAYER_REBAR_STIRRUP)
    Call AssertEqual(M16_DXF.DXF_GetEntityCount(), 3, "Arc increases entity count")
    
    ' Test 8: Text entity
    Call M16_DXF.DXF_Text(0, 0, 10, "Test Label", LAYER_TEXT_CALLOUT)
    Call AssertEqual(M16_DXF.DXF_GetEntityCount(), 4, "Text increases entity count")
    
    ' Test 9: Rectangle (4 lines)
    Dim countBefore As Long
    countBefore = M16_DXF.DXF_GetEntityCount()
    Call M16_DXF.DXF_Rectangle(0, 0, 100, 50, LAYER_BEAM_OUTLINE)
    Call AssertEqual(M16_DXF.DXF_GetEntityCount(), countBefore + 4, "Rectangle adds 4 lines")
    
    ' Close and verify file
    Call M16_DXF.DXF_Close
    Call AssertTrue(FileLen(testFile) > 0, "DXF file has content")
    
    ' Cleanup
    Call CleanupTestFile(testFile)
End Sub

Private Sub Test_DXF_Structural_Components()
    m_TestOutput = m_TestOutput & vbCrLf & "--- Structural Component Tests ---" & vbCrLf
    
    Dim testFile As String
    testFile = GetTestFilePath("test_structural.dxf")
    
    ' Initialize
    Call M16_DXF.DXF_Initialize(testFile)
    
    ' Test 10: Stirrup drawing
    Dim countBefore As Long
    countBefore = M16_DXF.DXF_GetEntityCount()
    Call M16_DXF.DXF_Stirrup(150, 200, 200, 300, 8, 80)
    Call AssertTrue(M16_DXF.DXF_GetEntityCount() > countBefore, "Stirrup adds entities")
    
    ' Test 11: Rebar section (filled)
    countBefore = M16_DXF.DXF_GetEntityCount()
    Call M16_DXF.DXF_RebarSection(50, 50, 16, True)
    Call AssertTrue(M16_DXF.DXF_GetEntityCount() > countBefore, "RebarSection adds entities")
    
    ' Test 12: Dimension line
    countBefore = M16_DXF.DXF_GetEntityCount()
    Call M16_DXF.DXF_Dimension(0, 0, 300, 0, 50, 20)
    Call AssertTrue(M16_DXF.DXF_GetEntityCount() > countBefore, "Dimension adds entities")
    
    ' Close
    Call M16_DXF.DXF_Close
    
    ' Cleanup
    Call CleanupTestFile(testFile)
End Sub

Private Sub Test_DXF_BeamSection()
    m_TestOutput = m_TestOutput & vbCrLf & "--- Beam Section Drawing Tests ---" & vbCrLf
    
    Dim testFile As String
    testFile = GetTestFilePath("test_beam_section.dxf")
    
    ' Prepare test data
    Dim topBars(0 To 2) As Double
    Dim bottomBars(0 To 2) As Double
    topBars(0) = 16: topBars(1) = 16: topBars(2) = 16
    bottomBars(0) = 20: bottomBars(1) = 20: bottomBars(2) = 20
    
    ' Test 13: Generate beam section
    Dim success As Boolean
    success = M16_DXF.Draw_BeamSection(testFile, 300, 450, 40, topBars, bottomBars, 8)
    Call AssertTrue(success, "Draw_BeamSection returns True")
    
    ' Test 14: File exists
    Call AssertTrue(Dir(testFile) <> "", "Beam section DXF file created")
    
    ' Test 15: File has content
    Call AssertTrue(FileLen(testFile) > 500, "Beam section DXF has substantial content")
    
    ' Cleanup
    Call CleanupTestFile(testFile)
End Sub

Private Sub Test_DXF_BeamLongitudinal()
    m_TestOutput = m_TestOutput & vbCrLf & "--- Beam Longitudinal Drawing Tests ---" & vbCrLf
    
    Dim testFile As String
    testFile = GetTestFilePath("test_beam_long.dxf")
    
    ' Test 16: Generate longitudinal section
    Dim success As Boolean
    success = M16_DXF.Draw_BeamLongitudinal(testFile, 4000, 450, 40, 16, 20, 8, 150)
    Call AssertTrue(success, "Draw_BeamLongitudinal returns True")
    
    ' Test 17: File exists
    Call AssertTrue(Dir(testFile) <> "", "Longitudinal DXF file created")
    
    ' Test 18: File has content
    Call AssertTrue(FileLen(testFile) > 500, "Longitudinal DXF has substantial content")
    
    ' Cleanup
    Call CleanupTestFile(testFile)
End Sub

Private Sub Test_DXF_FullDetailing()
    m_TestOutput = m_TestOutput & vbCrLf & "--- Full Beam Detailing Tests ---" & vbCrLf
    
    Dim testFile As String
    testFile = GetTestFilePath("test_beam_detail.dxf")
    
    ' Create BeamDetailingResult
    Dim result As BeamDetailingResult
    result.B_mm = 300
    result.D_mm = 450
    result.Cover_mm = 40
    result.TopBars.Dia_mm = 16
    result.TopBars.Count_n = 3
    result.BottomBars.Dia_mm = 20
    result.BottomBars.Count_n = 4
    result.Stirrups.Dia_mm = 8
    result.Stirrups.Spacing_mm = 150
    result.Stirrups.Legs = 2
    
    ' Test 19: Generate full detailing drawing
    Dim success As Boolean
    success = M16_DXF.Draw_BeamDetailing(testFile, result)
    Call AssertTrue(success, "Draw_BeamDetailing returns True")
    
    ' Test 20: File exists
    Call AssertTrue(Dir(testFile) <> "", "Full detailing DXF file created")
    
    ' Test 21: File has substantial content (section + longitudinal + bar schedule)
    Call AssertTrue(FileLen(testFile) > 2000, "Full detailing DXF has comprehensive content")
    
    ' Don't cleanup - keep for visual verification
    m_TestOutput = m_TestOutput & "  [INFO] Test file kept at: " & testFile & vbCrLf
End Sub

' ============================================================================
' VISUAL VERIFICATION TEST
' ============================================================================

' Run this to generate a sample DXF for manual verification in AutoCAD/viewer
Public Sub Generate_Sample_DXF()
    Dim filePath As String
    filePath = Application.GetSaveAsFilename( _
        InitialFileName:="SampleBeam_300x450.dxf", _
        FileFilter:="DXF Files (*.dxf), *.dxf", _
        Title:="Save Sample DXF")
    
    If filePath = "False" Then Exit Sub
    
    ' Create realistic beam detailing
    Dim result As BeamDetailingResult
    result.B_mm = 300
    result.D_mm = 450
    result.Cover_mm = 40
    result.TopBars.Dia_mm = 16
    result.TopBars.Count_n = 3
    result.TopBars.Ast_mm2 = 603   ' 3 x 201 mm²
    result.BottomBars.Dia_mm = 20
    result.BottomBars.Count_n = 4
    result.BottomBars.Ast_mm2 = 1257  ' 4 x 314 mm²
    result.Stirrups.Dia_mm = 8
    result.Stirrups.Spacing_mm = 150
    result.Stirrups.Legs = 2
    
    ' Generate
    Dim success As Boolean
    success = M16_DXF.Draw_BeamDetailing(filePath, result)
    
    If success Then
        MsgBox "Sample DXF generated successfully!" & vbCrLf & vbCrLf & _
               "File: " & filePath & vbCrLf & vbCrLf & _
               "Open in AutoCAD, DraftSight, or any DXF viewer to verify:" & vbCrLf & _
               "- Layer colors are correct" & vbCrLf & _
               "- Section shows 3T16 top, 4T20 bottom" & vbCrLf & _
               "- Longitudinal shows 8T@150 c/c stirrups" & vbCrLf & _
               "- Dimensions are accurate" & vbCrLf & _
               "- Bar schedule is present", _
               vbInformation, "DXF Generated"
    Else
        MsgBox "Failed to generate DXF.", vbExclamation, "Error"
    End If
End Sub

' ============================================================================
' LAYER VERIFICATION TEST
' ============================================================================

Public Sub Test_Layer_Colors()
    ' Quick visual test to verify layer setup
    m_TestOutput = "=== Layer Configuration ===" & vbCrLf
    m_TestOutput = m_TestOutput & "Layer Name        | Color Code" & vbCrLf
    m_TestOutput = m_TestOutput & "------------------|------------" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_BEAM_OUTLINE & " | " & ACI_CYAN & " (Cyan)" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_REBAR_MAIN & "   | " & ACI_RED & " (Red)" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_REBAR_STIRRUP & " | " & ACI_GREEN & " (Green)" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_DIMENSIONS & "   | " & ACI_YELLOW & " (Yellow)" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_TEXT_CALLOUT & " | " & ACI_WHITE & " (White)" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_CENTERLINE & "   | " & ACI_MAGENTA & " (Magenta)" & vbCrLf
    m_TestOutput = m_TestOutput & LAYER_COVER_LINE & "   | " & ACI_BLUE & " (Blue)" & vbCrLf
    
    Debug.Print m_TestOutput
    MsgBox m_TestOutput, vbInformation, "DXF Layer Setup"
End Sub
