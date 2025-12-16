Attribute VB_Name = "Installer_ImportAllModules"
Option Explicit

' Bulk import helper for this repo.
'
' Purpose:
' - Makes it easier for Excel users to set up the library during development
' - Imports all core modules from VBA/Modules (optionally tests from VBA/Tests)
'
' Requirements:
' - Enable "Trust access to the VBA project object model" in Excel Trust Center.
'
' Notes:
' - Import order matters: M02_Types must be imported first.
' - This macro removes existing library modules (matching patterns) to avoid duplicates.

Public Sub ImportAllModules()
    On Error GoTo Fail

    If Len(ThisWorkbook.Path) = 0 Then
        MsgBox "Save this workbook first, then re-run.", vbExclamation
        Exit Sub
    End If

    Const INCLUDE_TESTS As Boolean = False  ' Set True to also import VBA/Tests

    Dim repoRoot As String
    Dim modulesFolder As String
    Dim testsFolder As String

    repoRoot = EnsureTrailingSlash(ThisWorkbook.Path)
    modulesFolder = FindFolder(repoRoot, "VBA" & Application.PathSeparator & "Modules" & Application.PathSeparator)
    testsFolder = FindFolder(repoRoot, "VBA" & Application.PathSeparator & "Tests" & Application.PathSeparator)

    If modulesFolder = "" Then
        modulesFolder = PromptFolder("Enter full path to VBA/Modules (e.g., /path/to/structural_engineering_lib/VBA/Modules/):")
        If modulesFolder = "" Then Exit Sub
    End If

    If INCLUDE_TESTS And testsFolder = "" Then
        testsFolder = PromptFolder("Enter full path to VBA/Tests (or Cancel to skip tests):")
    End If

    ' Remove existing library modules (core patterns) and common tests to avoid duplicates
    RemoveIfExists "M0?_Constants"
    RemoveIfExists "M0?_Types"
    RemoveIfExists "M0?_Tables"
    RemoveIfExists "M0?_Utilities"
    RemoveIfExists "M0?_Materials"
    RemoveIfExists "M0?_Flexure"
    RemoveIfExists "M0?_Shear"
    RemoveIfExists "M0?_API"
    RemoveIfExists "M0?_UDFs"
    RemoveIfExists "M1?_Ductile"
    RemoveIfExists "M1?_Serviceability"

    RemoveIfExists "Test_*"

    ' IMPORTANT: Import M02_Types FIRST (other modules depend on UDT definitions)
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M02_Types.bas"

    ' Core modules (keep order stable)
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M01_Constants.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M03_Tables.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M04_Utilities.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M05_Materials.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M06_Flexure.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M07_Shear.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M08_API.bas"
    Application.VBE.ActiveVBProject.VBComponents.Import modulesFolder & "M09_UDFs.bas"

    ' Optional modules (import if present)
    ImportIfExists modulesFolder & "M10_Ductile.bas"
    ImportIfExists modulesFolder & "M13_Integration.bas"
    ImportIfExists modulesFolder & "M14_Reporting.bas"
    ImportIfExists modulesFolder & "M15_Detailing.bas"
    ImportIfExists modulesFolder & "M16_DXF.bas"
    ImportIfExists modulesFolder & "M17_Serviceability.bas"

    If INCLUDE_TESTS Then
        ImportIfExists testsFolder & "Test_Structural.bas"
        ImportIfExists testsFolder & "Test_Flanged.bas"
        ImportIfExists testsFolder & "Test_Ductile.bas"
        ImportIfExists testsFolder & "Test_DXF.bas"
    End If

    MsgBox "Modules imported from:" & vbCrLf & modulesFolder, vbInformation
    Exit Sub

Fail:
    MsgBox "Import failed: " & Err.Description, vbCritical
End Sub

Private Sub ImportIfExists(fullPath As String)
    On Error GoTo Skip
    If Len(fullPath) = 0 Then Exit Sub
    If Dir(fullPath) = "" Then Exit Sub
    Application.VBE.ActiveVBProject.VBComponents.Import fullPath
Skip:
    On Error GoTo 0
End Sub

Private Function EnsureTrailingSlash(pathStr As String) As String
    If Len(pathStr) = 0 Then Exit Function
    If Right(pathStr, 1) <> Application.PathSeparator Then
        EnsureTrailingSlash = pathStr & Application.PathSeparator
    Else
        EnsureTrailingSlash = pathStr
    End If
End Function

Private Function ParentFolder(pathStr As String) As String
    Dim p As String
    p = pathStr
    If Right(p, 1) = Application.PathSeparator Then p = Left(p, Len(p) - 1)
    Dim pos As Long
    pos = InStrRev(p, Application.PathSeparator)
    If pos > 0 Then ParentFolder = Left(p, pos)
End Function

Private Function FindFolder(repoRoot As String, subPath As String) As String
    Dim candidate As String
    candidate = EnsureTrailingSlash(repoRoot) & subPath
    If Dir(candidate, vbDirectory) <> "" Then
        FindFolder = candidate
        Exit Function
    End If

    Dim parent As String
    parent = ParentFolder(repoRoot)
    If Len(parent) > 0 Then
        candidate = EnsureTrailingSlash(parent) & subPath
        If Dir(candidate, vbDirectory) <> "" Then
            FindFolder = candidate
            Exit Function
        End If
    End If
End Function

Private Function PromptFolder(prompt As String) As String
    Dim pathStr As String
    pathStr = InputBox(prompt, "Locate folder")
    If Len(pathStr) = 0 Then Exit Function
    pathStr = EnsureTrailingSlash(pathStr)
    If Dir(pathStr, vbDirectory) = "" Then
        MsgBox "Folder not found: " & pathStr, vbCritical
        Exit Function
    End If
    PromptFolder = pathStr
End Function

Private Sub RemoveIfExists(pattern As String)
    On Error Resume Next
    Dim comp As Object
    For Each comp In Application.VBE.ActiveVBProject.VBComponents
        If comp.Name Like pattern Then
            Application.VBE.ActiveVBProject.VBComponents.Remove comp
        End If
    Next comp
    On Error GoTo 0
End Sub
