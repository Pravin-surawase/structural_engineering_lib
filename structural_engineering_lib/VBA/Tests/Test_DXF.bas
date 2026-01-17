Attribute VB_Name = "Test_DXF"
'@Module: Test_DXF
'@Description: Test Suite for M16_DXF - DXF Export Functions
'@Version: 0.8.0
'@Date: 2025-12-11

Option Explicit


' ==============================================================================
' SPDX-License-Identifier: MIT
' Copyright (c) 2024-2026 Pravin Surawase
' ==============================================================================

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
    ' Returns path in user's temp folder (cross-platform)
    GetTestFilePath = GetTempFolderPath() & fileName
End Function

Private Function GetTempFolderPath() As String
    Dim tmp As String
    tmp = Environ$("TMPDIR")
    If Len(tmp) = 0 Then tmp = Environ$("TEMP")
    If Len(tmp) = 0 Then tmp = Environ$("TMP")
    If Len(tmp) = 0 Then tmp = CurDir$

    ' Ensure trailing separator
    If Len(tmp) > 0 Then
        Dim sep As String
        If InStr(1, tmp, "/", vbBinaryCompare) > 0 Then
            sep = "/"
        Else
            sep = "\\"
        End If

        If Right$(tmp, 1) <> "/" And Right$(tmp, 1) <> "\\" Then
            tmp = tmp & sep
        End If
    End If

    GetTempFolderPath = tmp
End Function

Private Sub CleanupTestFile(ByVal filePath As String)
    On Error Resume Next
    Kill filePath
End Sub

Private Function ReadAllText(ByVal filePath As String) As String
    Dim fileNumber As Integer
    fileNumber = FreeFile

    Dim content As String
    Open filePath For Binary Access Read As #fileNumber
    content = String$(LOF(fileNumber), vbNullChar)
    Get #fileNumber, , content
    Close #fileNumber

    ReadAllText = content
End Function

Private Sub AssertContains(ByVal haystack As String, ByVal needle As String, ByVal testName As String)
    Call AssertTrue(InStr(1, haystack, needle, vbTextCompare) > 0, testName)
End Sub

Private Sub AssertDxfHasSection(ByVal dxfText As String, ByVal sectionName As String, ByVal testName As String)
    Call AssertContains(dxfText, vbCrLf & "2" & vbCrLf & sectionName & vbCrLf, testName)
End Sub

Private Sub AssertDxfHasLayer(ByVal dxfText As String, ByVal layerName As String, ByVal testName As String)
    Call AssertContains(dxfText, vbCrLf & "2" & vbCrLf & layerName & vbCrLf, testName)
End Sub

Private Sub AssertDxfHasEntity(ByVal dxfText As String, ByVal entityName As String, ByVal testName As String)
    Call AssertContains(dxfText, vbCrLf & "0" & vbCrLf & entityName & vbCrLf, testName)
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

    ' Test 4b: File contains basic DXF structure
    Dim dxfText As String
    dxfText = ReadAllText(testFile)
    Call AssertContains(dxfText, vbCrLf & "0" & vbCrLf & "SECTION" & vbCrLf, "DXF contains SECTION")
    Call AssertContains(dxfText, vbCrLf & "0" & vbCrLf & "EOF" & vbCrLf, "DXF contains EOF")

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

    ' Content-level validation (not just size)
    Dim dxfText As String
    dxfText = ReadAllText(testFile)

    Call AssertDxfHasSection(dxfText, "HEADER", "DXF has HEADER section")
    Call AssertDxfHasSection(dxfText, "TABLES", "DXF has TABLES section")
    Call AssertDxfHasSection(dxfText, "ENTITIES", "DXF has ENTITIES section")
    Call AssertContains(dxfText, vbCrLf & "0" & vbCrLf & "EOF" & vbCrLf, "DXF ends with EOF")

    Call AssertDxfHasLayer(dxfText, LAYER_BEAM_OUTLINE, "DXF defines layer: BEAM_OUTLINE")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_MAIN, "DXF defines layer: REBAR_MAIN")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_STIRRUP, "DXF defines layer: REBAR_STIRRUP")
    Call AssertDxfHasLayer(dxfText, LAYER_TEXT_CALLOUT, "DXF defines layer: TEXT_CALLOUT")

    Call AssertDxfHasEntity(dxfText, "LINE", "DXF contains LINE entity")
    Call AssertDxfHasEntity(dxfText, "CIRCLE", "DXF contains CIRCLE entity")
    Call AssertDxfHasEntity(dxfText, "ARC", "DXF contains ARC entity")
    Call AssertDxfHasEntity(dxfText, "TEXT", "DXF contains TEXT entity")

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

    ' Content-level validation
    Dim dxfText As String
    dxfText = ReadAllText(testFile)
    Call AssertDxfHasSection(dxfText, "ENTITIES", "Beam section DXF has ENTITIES section")
    Call AssertDxfHasLayer(dxfText, LAYER_BEAM_OUTLINE, "Beam section DXF defines BEAM_OUTLINE")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_MAIN, "Beam section DXF defines REBAR_MAIN")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_STIRRUP, "Beam section DXF defines REBAR_STIRRUP")
    Call AssertDxfHasLayer(dxfText, LAYER_COVER_LINE, "Beam section DXF defines COVER_LINE")
    Call AssertDxfHasEntity(dxfText, "CIRCLE", "Beam section DXF contains CIRCLE entities")

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

    ' Content-level validation
    Dim dxfText As String
    dxfText = ReadAllText(testFile)
    Call AssertDxfHasSection(dxfText, "ENTITIES", "Longitudinal DXF has ENTITIES section")
    Call AssertDxfHasLayer(dxfText, LAYER_BEAM_OUTLINE, "Longitudinal DXF defines BEAM_OUTLINE")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_MAIN, "Longitudinal DXF defines REBAR_MAIN")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_STIRRUP, "Longitudinal DXF defines REBAR_STIRRUP")
    Call AssertDxfHasLayer(dxfText, LAYER_CENTERLINE, "Longitudinal DXF defines CENTERLINE")
    Call AssertDxfHasEntity(dxfText, "LINE", "Longitudinal DXF contains LINE entities")

    ' Cleanup
    Call CleanupTestFile(testFile)
End Sub

Private Sub Test_DXF_FullDetailing()
    m_TestOutput = m_TestOutput & vbCrLf & "--- Full Beam Detailing Tests ---" & vbCrLf

    Dim testFile As String
    testFile = GetTestFilePath("test_beam_detail.dxf")

    ' Create BeamDetailingResult with correct field names
    Dim result As BeamDetailingResult
    result.beam_id = "B1"
    result.b = 300
    result.D = 450
    result.span = 4000
    result.cover = 40

    ' Bottom bars (mid-span tension)
    result.bottom_mid.count = 4
    result.bottom_mid.diameter = 20
    result.bottom_mid.spacing = 70
    result.bottom_start = result.bottom_mid
    result.bottom_end = result.bottom_mid

    ' Top bars (support tension)
    result.top_start.count = 3
    result.top_start.diameter = 16
    result.top_start.spacing = 90
    result.top_mid.count = 2
    result.top_mid.diameter = 16
    result.top_mid.spacing = 150
    result.top_end = result.top_start

    ' Stirrups
    result.stirrup_start.diameter = 8
    result.stirrup_start.spacing = 100
    result.stirrup_start.legs = 2
    result.stirrup_start.zone_length = 800

    result.stirrup_mid.diameter = 8
    result.stirrup_mid.spacing = 150
    result.stirrup_mid.legs = 2
    result.stirrup_mid.zone_length = 2400

    result.stirrup_end = result.stirrup_start

    ' Test 19: Generate full detailing drawing
    Dim success As Boolean
    success = M16_DXF.Draw_BeamDetailing(testFile, result)
    Call AssertTrue(success, "Draw_BeamDetailing returns True")

    ' Test 20: File exists
    Call AssertTrue(Dir(testFile) <> "", "Full detailing DXF file created")

    ' Test 21: File has substantial content (section + longitudinal + bar schedule)
    Call AssertTrue(FileLen(testFile) > 2000, "Full detailing DXF has comprehensive content")

    ' Content-level validation
    Dim dxfText As String
    dxfText = ReadAllText(testFile)
    Call AssertDxfHasSection(dxfText, "ENTITIES", "Full detailing DXF has ENTITIES section")
    Call AssertDxfHasLayer(dxfText, LAYER_BEAM_OUTLINE, "Full detailing DXF defines BEAM_OUTLINE")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_MAIN, "Full detailing DXF defines REBAR_MAIN")
    Call AssertDxfHasLayer(dxfText, LAYER_REBAR_STIRRUP, "Full detailing DXF defines REBAR_STIRRUP")
    Call AssertDxfHasLayer(dxfText, LAYER_DIMENSIONS, "Full detailing DXF defines DIMENSIONS")
    Call AssertDxfHasLayer(dxfText, LAYER_TEXT_CALLOUT, "Full detailing DXF defines TEXT_CALLOUT")
    Call AssertContains(dxfText, result.beam_id, "Full detailing DXF includes beam_id text")

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

    ' Create realistic beam detailing with correct field names
    Dim result As BeamDetailingResult
    result.beam_id = "B1-Sample"
    result.b = 300
    result.D = 450
    result.span = 4000
    result.cover = 40

    ' Bottom bars - mid-span (main tension)
    result.bottom_mid.count = 4
    result.bottom_mid.diameter = 20
    result.bottom_mid.area_provided = 1257  ' 4 x 314 mm²
    result.bottom_mid.spacing = 70
    result.bottom_start = result.bottom_mid
    result.bottom_end = result.bottom_mid

    ' Top bars - supports (hogging moment)
    result.top_start.count = 3
    result.top_start.diameter = 16
    result.top_start.area_provided = 603  ' 3 x 201 mm²
    result.top_start.spacing = 90
    result.top_mid.count = 2
    result.top_mid.diameter = 16
    result.top_mid.spacing = 150
    result.top_end = result.top_start

    ' Stirrups - zoned
    result.stirrup_start.diameter = 8
    result.stirrup_start.spacing = 100
    result.stirrup_start.legs = 2
    result.stirrup_start.zone_length = 800

    result.stirrup_mid.diameter = 8
    result.stirrup_mid.spacing = 150
    result.stirrup_mid.legs = 2
    result.stirrup_mid.zone_length = 2400

    result.stirrup_end = result.stirrup_start

    ' Generate
    Dim success As Boolean
    success = M16_DXF.Draw_BeamDetailing(filePath, result)

    If success Then
        MsgBox "Sample DXF generated successfully!" & vbCrLf & vbCrLf & _
               "File: " & filePath & vbCrLf & vbCrLf & _
               "Open in AutoCAD, DraftSight, or any DXF viewer to verify:" & vbCrLf & _
               "- Layer colors are correct" & vbCrLf & _
               "- Section shows 3T16 top, 4T20 bottom" & vbCrLf & _
               "- Longitudinal shows zoned stirrups" & vbCrLf & _
               "- Dimensions are accurate" & vbCrLf & _
               "- Bar schedule shows all zones", _
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
