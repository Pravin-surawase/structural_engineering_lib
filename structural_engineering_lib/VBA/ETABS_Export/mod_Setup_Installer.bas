Attribute VB_Name = "mod_Setup_Installer"
Option Explicit

'==============================================================================
' ETABS Export - Simplified Installer v2.0
' Date: 2026-01-17
'
' USAGE: In Excel VBA Immediate Window (Ctrl+G), type:
'   Call StartInstallation()
'
' This installer:
'   1. Removes old mod_* modules (except itself)
'   2. Imports 8 core modules
'   3. Stays installed for future updates
'==============================================================================

' *** UPDATE THIS PATH FOR YOUR MACHINE ***
Public Const SOURCE_FOLDER As String = "C:\Users\P\Pravin2025\Projects\structural_lib_repo\structural_engineering_lib\VBA\ETABS_Export\"

' Number of expected modules (9 core + 1 installer = 10)
Private Const EXPECTED_MODULES As Long = 10

'==============================================================================
' MAIN ENTRY POINT
'==============================================================================

Public Sub StartInstallation()
    On Error GoTo ErrHandler
    
    ' Confirm
    If MsgBox("Install ETABS Export modules?" & vbCrLf & vbCrLf & _
              "This will import 9 core modules.", _
              vbYesNo + vbQuestion, "ETABS Export Installer") = vbNo Then
        Exit Sub
    End If
    
    Application.ScreenUpdating = False
    
    ' Step 1: Remove old modules (except this installer)
    Debug.Print "=== STEP 1: Removing old modules ==="
    RemoveOldModules
    
    ' Step 2: Import modules
    Debug.Print ""
    Debug.Print "=== STEP 2: Importing modules ==="
    ImportModules
    
    ' Step 3: Verify
    Debug.Print ""
    Debug.Print "=== STEP 3: Verifying ==="
    Dim n As Long
    n = CountModules()
    
    Application.ScreenUpdating = True
    
    ' Done
    Debug.Print ""
    Debug.Print "=== INSTALLATION COMPLETE ==="
    Debug.Print "Modules: " & n & " (expected " & EXPECTED_MODULES & ")"
    Debug.Print ""
    Debug.Print "NEXT STEPS:"
    Debug.Print "1. Open ETABS with your model"
    Debug.Print "2. Run analysis (F5 in ETABS)"
    Debug.Print "3. Call ExportETABSData()"
    
    MsgBox "Installation complete!" & vbCrLf & _
           "Modules: " & n & vbCrLf & vbCrLf & _
           "Next: Call ExportETABSData()", vbInformation
    Exit Sub

ErrHandler:
    Application.ScreenUpdating = True
    Debug.Print "ERROR: " & Err.Description
    MsgBox "Error: " & Err.Description, vbCritical
End Sub

'==============================================================================
' REMOVE OLD MODULES (except this installer)
'==============================================================================

Private Sub RemoveOldModules()
    On Error Resume Next
    Dim comp As Object
    For Each comp In Application.VBE.ActiveVBProject.VBComponents
        If comp.Name Like "mod_*" And comp.Name <> "mod_Setup_Installer" Then
            Debug.Print "  Removing: " & comp.Name
            Application.VBE.ActiveVBProject.VBComponents.Remove comp
        End If
    Next comp
End Sub

'==============================================================================
' IMPORT MODULES
'==============================================================================

Private Sub ImportModules()
    On Error Resume Next
    Dim f As String
    f = SOURCE_FOLDER
    
    Debug.Print "  Importing mod_Logging..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Logging.bas"
    
    Debug.Print "  Importing mod_Types..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Types.bas"
    
    Debug.Print "  Importing mod_Utils..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Utils.bas"
    
    Debug.Print "  Importing mod_Connection..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Connection.bas"
    
    Debug.Print "  Importing mod_Analysis..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Analysis.bas"
    
    Debug.Print "  Importing mod_Design..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Design.bas"
    
    Debug.Print "  Importing mod_Export..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Export.bas"
    
    Debug.Print "  Importing mod_Validation..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Validation.bas"
    
    Debug.Print "  Importing mod_Main..."
    Application.VBE.ActiveVBProject.VBComponents.Import f & "mod_Main.bas"
    
    Debug.Print "  [OK] All modules imported"
End Sub

'==============================================================================
' COUNT MODULES
'==============================================================================

Private Function CountModules() As Long
    Dim n As Long
    Dim comp As Object
    For Each comp In Application.VBE.ActiveVBProject.VBComponents
        If comp.Name Like "mod_*" Then
            Debug.Print "  Found: " & comp.Name
            n = n + 1
        End If
    Next comp
    CountModules = n
End Function

'==============================================================================
' QUICK REINSTALL (no prompts)
'==============================================================================

Public Sub QuickReinstall()
    Application.ScreenUpdating = False
    RemoveOldModules
    ImportModules
    Application.ScreenUpdating = True
    Debug.Print "Reinstalled " & CountModules() & " modules"
End Sub
