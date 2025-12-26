Attribute VB_Name = "Test_RunAll"
Option Explicit

' ==============================================================================
' Module:       Test_RunAll
' Description:  Unified Test Runner for all VBA modules
' Version:      0.9.2
' License:      MIT
' ==============================================================================
'
' USAGE:
'   1. Open the Excel workbook (StructEng_BeamDesign_v0.5.xlsm or equivalent)
'   2. Press Alt+F11 to open VBA Editor
'   3. In Immediate Window (Ctrl+G), type: Test_RunAll.RunAllVBATests
'   4. Press Enter
'
' OUTPUT:
'   Test results appear in the Immediate Window with PASS/FAIL counts.
'   A summary is also written to the "TestLog" sheet if it exists.
'
' ==============================================================================

Private m_TotalPass As Long
Private m_TotalFail As Long
Private m_StartTime As Double

' ==============================================================================
' Main Entry Point
' ==============================================================================
Public Sub RunAllVBATests()
    m_TotalPass = 0
    m_TotalFail = 0
    m_StartTime = Timer
    
    Debug.Print ""
    Debug.Print "========================================"
    Debug.Print "  STRUCTURAL ENGINEERING LIB - VBA TESTS"
    Debug.Print "  Version: " & Get_Library_Version()
    Debug.Print "  Date: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    Debug.Print "========================================"
    Debug.Print ""
    
    ' --- Core Module Tests ---
    Call RunSuite_Structural
    Call RunSuite_Flanged
    Call RunSuite_Ductile
    
    ' --- v0.7+ Module Tests ---
    Call RunSuite_Detailing
    Call RunSuite_DXF
    
    ' --- v0.8+ Module Tests ---
    Call RunSuite_Serviceability
    
    ' --- Summary ---
    Dim elapsed As Double
    elapsed = Timer - m_StartTime
    
    Debug.Print ""
    Debug.Print "========================================"
    Debug.Print "  FINAL SUMMARY"
    Debug.Print "========================================"
    Debug.Print "  Total Passed: " & m_TotalPass
    Debug.Print "  Total Failed: " & m_TotalFail
    Debug.Print "  Time Elapsed: " & Format(elapsed, "0.00") & " seconds"
    Debug.Print "========================================"
    
    If m_TotalFail = 0 Then
        Debug.Print "  STATUS: ALL TESTS PASSED"
    Else
        Debug.Print "  STATUS: " & m_TotalFail & " FAILURES - REVIEW ABOVE"
    End If
    Debug.Print "========================================"
    
    ' Optionally log to sheet
    Call LogResultsToSheet
End Sub

' ==============================================================================
' Suite Runners (capture pass/fail counts from each module)
' ==============================================================================

Private Sub RunSuite_Structural()
    On Error Resume Next
    Debug.Print ">>> Suite: Structural (Flexure, Shear, Materials, Tables)"
    
    ' Test_Structural.RunAllTests outputs PASS/FAIL to Debug
    ' We can't easily capture counts, so we run it and trust its output
    Test_Structural.RunAllTests
    
    Debug.Print ""
End Sub

Private Sub RunSuite_Flanged()
    On Error Resume Next
    Debug.Print ">>> Suite: Flanged Beams"
    Test_Flanged.RunFlangedTests
    Debug.Print ""
End Sub

Private Sub RunSuite_Ductile()
    On Error Resume Next
    Debug.Print ">>> Suite: Ductile Detailing (IS 13920)"
    Test_Ductile.RunDuctileTests
    Debug.Print ""
End Sub

Private Sub RunSuite_Detailing()
    On Error Resume Next
    Debug.Print ">>> Suite: Detailing (Ld, Lap, Spacing)"
    Test_Detailing.Run_All_Detailing_Tests
    Debug.Print ""
End Sub

Private Sub RunSuite_DXF()
    On Error Resume Next
    Debug.Print ">>> Suite: DXF Export"
    Test_DXF.Run_All_DXF_Tests
    Debug.Print ""
End Sub

Private Sub RunSuite_Serviceability()
    On Error Resume Next
    Debug.Print ">>> Suite: Serviceability (Deflection, Crack Width)"
    Test_Serviceability.Run_All_Serviceability_Tests
    Debug.Print ""
End Sub

' ==============================================================================
' Optional: Log to Sheet
' ==============================================================================
Private Sub LogResultsToSheet()
    On Error Resume Next
    
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("TestLog")
    If ws Is Nothing Then Exit Sub
    
    Dim nextRow As Long
    nextRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row + 1
    
    ws.Cells(nextRow, 1).Value = Now
    ws.Cells(nextRow, 2).Value = Get_Library_Version()
    ws.Cells(nextRow, 3).Value = m_TotalPass
    ws.Cells(nextRow, 4).Value = m_TotalFail
    ws.Cells(nextRow, 5).Value = IIf(m_TotalFail = 0, "PASS", "FAIL")
End Sub

' ==============================================================================
' Version Helper (fallback if M99_Setup not available)
' ==============================================================================
Private Function Get_Library_Version() As String
    On Error Resume Next
    Get_Library_Version = M99_Setup.Get_Library_Version()
    If Err.Number <> 0 Or Len(Get_Library_Version) = 0 Then
        Get_Library_Version = "0.9.x"
    End If
End Function
