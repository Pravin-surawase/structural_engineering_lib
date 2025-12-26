Attribute VB_Name = "Test_RunAll"
Option Explicit

' ==============================================================================
' Module:       Test_RunAll
' Description:  Unified Test Runner for all VBA modules
' Version:      0.9.4
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
'   Test results appear in the Immediate Window.
'   Each suite prints its own PASS/FAIL lines - review the output for failures.
'   A run log is written to the "TestLog" sheet if it exists.
'
' NOTE:
'   VBA test modules don't return counts, so this runner can't aggregate totals.
'   Review the Immediate Window output manually for any FAIL lines.
'
' ==============================================================================

Private m_SuiteErrors As Long
Private m_StartTime As Double

' ==============================================================================
' Main Entry Point
' ==============================================================================
Public Sub RunAllVBATests()
    m_SuiteErrors = 0
    m_StartTime = Timer
    
    Debug.Print ""
    Debug.Print "========================================"
    Debug.Print "  STRUCTURAL ENGINEERING LIB - VBA TESTS"
    Debug.Print "  Version: " & Get_Library_Version()
    Debug.Print "  Date: " & Format(Now, "yyyy-mm-dd hh:nn:ss")
    Debug.Print "========================================"
    Debug.Print ""
    Debug.Print "NOTE: Review each suite's output for PASS/FAIL."
    Debug.Print "      Totals are not aggregated - check for FAIL lines."
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
    
    ' --- v0.9+ Module Tests ---
    Call RunSuite_BBS
    Call RunSuite_Compliance
    
    ' --- Parity Tests (Python ↔ VBA) ---
    Call RunSuite_Parity
    
    ' --- Summary ---
    Dim elapsed As Double
    elapsed = Timer - m_StartTime
    
    Debug.Print ""
    Debug.Print "========================================"
    Debug.Print "  RUN COMPLETE"
    Debug.Print "========================================"
    Debug.Print "  Suites Run: 9"
    Debug.Print "  Suite Errors: " & m_SuiteErrors
    Debug.Print "  Time Elapsed: " & Format(elapsed, "0.00") & " seconds"
    Debug.Print "========================================"
    
    If m_SuiteErrors = 0 Then
        Debug.Print "  All suites executed without runtime errors."
        Debug.Print "  >> Review output above for FAIL lines <<"
    Else
        Debug.Print "  WARNING: " & m_SuiteErrors & " suite(s) had errors."
        Debug.Print "  Check for missing modules or runtime issues."
    End If
    Debug.Print "========================================"
    
    ' Log run to sheet
    Call LogResultsToSheet
End Sub

' ==============================================================================
' Suite Runners
' ==============================================================================
' NOTE: Each suite prints its own PASS/FAIL lines to the Immediate Window.
'       This runner can only detect if a suite fails to load/execute.
' ==============================================================================

Private Sub RunSuite_Structural()
    Debug.Print ">>> Suite: Structural (Flexure, Shear, Materials, Tables)"
    On Error GoTo ErrHandler
    Test_Structural.RunAllTests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_Flanged()
    Debug.Print ">>> Suite: Flanged Beams"
    On Error GoTo ErrHandler
    Test_Flanged.RunFlangedTests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_Ductile()
    Debug.Print ">>> Suite: Ductile Detailing (IS 13920)"
    On Error GoTo ErrHandler
    Test_Ductile.RunDuctileTests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_Detailing()
    Debug.Print ">>> Suite: Detailing (Ld, Lap, Spacing)"
    On Error GoTo ErrHandler
    Test_Detailing.Run_All_Detailing_Tests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_DXF()
    Debug.Print ">>> Suite: DXF Export"
    On Error GoTo ErrHandler
    Test_DXF.Run_All_DXF_Tests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_Serviceability()
    Debug.Print ">>> Suite: Serviceability (Deflection, Crack Width)"
    On Error GoTo ErrHandler
    Test_Serviceability.Run_All_Serviceability_Tests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_BBS()
    Debug.Print ">>> Suite: BBS (Bar Bending Schedule)"
    On Error GoTo ErrHandler
    Test_BBS.RunBBSTests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_Compliance()
    Debug.Print ">>> Suite: Compliance (Multi-check orchestration)"
    On Error GoTo ErrHandler
    Test_Compliance.RunComplianceTests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
    Debug.Print ""
End Sub

Private Sub RunSuite_Parity()
    Debug.Print ">>> Suite: Parity (Python <-> VBA verification)"
    On Error GoTo ErrHandler
    Test_Parity.Run_All_Parity_Tests
    Debug.Print ""
    Exit Sub
ErrHandler:
    Debug.Print "  [ERROR] Suite failed: " & Err.Description
    m_SuiteErrors = m_SuiteErrors + 1
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
    
    ' Log run timestamp and basic info
    ' Note: We can't aggregate pass/fail counts from individual suites
    ws.Cells(nextRow, 1).Value = Now
    ws.Cells(nextRow, 2).Value = Get_Library_Version()
    ws.Cells(nextRow, 3).Value = "7 suites"
    ws.Cells(nextRow, 4).Value = m_SuiteErrors & " suite errors"
    ws.Cells(nextRow, 5).Value = IIf(m_SuiteErrors = 0, "RUN OK", "ERRORS")
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
