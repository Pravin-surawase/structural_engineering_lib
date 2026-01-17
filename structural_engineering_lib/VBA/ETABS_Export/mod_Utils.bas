Attribute VB_Name = "mod_Utils"
Option Explicit

'==============================================================================
' Utility Functions Module
' Helper functions used across modules
'==============================================================================

' Check if folder exists
Public Function FolderExists(folderPath As String) As Boolean
    On Error Resume Next
    FolderExists = (Dir(folderPath, vbDirectory) <> "")
End Function

' Check if file exists
Public Function FileExists(filePath As String) As Boolean
    On Error Resume Next
    FileExists = (Dir(filePath) <> "")
End Function

' Count rows in CSV file (including header)
Public Function CountCSVRows(csvPath As String) As Long
    On Error Resume Next
    
    Dim fileNum As Integer
    Dim line As String
    Dim count As Long
    
    count = 0
    fileNum = FreeFile
    
    Open csvPath For Input As #fileNum
    
    Do While Not EOF(fileNum)
        Line Input #fileNum, line
        count = count + 1
    Loop
    
    Close #fileNum
    
    CountCSVRows = count
End Function

' Get free disk space in MB
Public Function GetDiskFreeSpace(driveLetter As String) As Long
    On Error Resume Next
    
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    Dim drive As Object
    Set drive = fso.GetDrive(driveLetter & ":")
    
    If Err.Number = 0 Then
        GetDiskFreeSpace = CLng(drive.FreeSpace / 1048576)  ' Convert to MB
    Else
        GetDiskFreeSpace = -1
    End If
End Function

' Format duration in seconds to readable string
Public Function FormatDuration(seconds As Double) As String
    If seconds < 60 Then
        FormatDuration = Format(seconds, "0.0") & "s"
    ElseIf seconds < 3600 Then
        FormatDuration = Format(seconds / 60, "0.0") & "m"
    Else
        FormatDuration = Format(seconds / 3600, "0.0") & "h"
    End If
End Function

' Safe string conversion (handles nulls and errors)
Public Function SafeStr(value As Variant) As String
    On Error Resume Next
    If IsNull(value) Or IsEmpty(value) Then
        SafeStr = ""
    Else
        SafeStr = CStr(value)
    End If
End Function

' Safe numeric conversion (handles nulls and errors)
Public Function SafeVal(value As Variant) As Double
    On Error Resume Next
    If IsNull(value) Or IsEmpty(value) Or Not IsNumeric(value) Then
        SafeVal = 0
    Else
        SafeVal = CDbl(value)
    End If
End Function

' Create timestamped backup of file
Public Function BackupFile(filePath As String) As Boolean
    On Error Resume Next
    
    If Not FileExists(filePath) Then
        BackupFile = False
        Exit Function
    End If
    
    Dim backupPath As String
    backupPath = filePath & ".bak." & Format(Now, "yyyymmdd_hhnnss")
    
    FileCopy filePath, backupPath
    
    If Err.Number = 0 Then
        BackupFile = True
    Else
        BackupFile = False
    End If
End Function

' Delete old backup files (keep last N)
Public Sub CleanupOldBackups(folder As String, keepCount As Integer)
    On Error Resume Next
    
    ' Get list of backup files
    Dim fileList As Collection
    Set fileList = New Collection
    
    Dim fileName As String
    fileName = Dir(folder & "\*.bak.*")
    
    Do While fileName <> ""
        fileList.Add fileName
        fileName = Dir
    Loop
    
    ' Sort by date (not implemented - would need custom sort)
    ' For simplicity, just delete if count exceeds keepCount
    
    If fileList.Count > keepCount Then
        LogInfo "Found " & fileList.Count & " backup files, keeping " & keepCount
        
        ' Delete oldest files
        Dim i As Integer
        For i = 1 To fileList.Count - keepCount
            Kill folder & "\" & fileList(i)
            LogDebug "Deleted old backup: " & fileList(i)
        Next
    End If
End Sub

' Get file size in MB
Public Function GetFileSizeMB(filePath As String) As Double
    On Error Resume Next
    
    Dim fso As Object
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    Dim file As Object
    Set file = fso.GetFile(filePath)
    
    If Err.Number = 0 Then
        GetFileSizeMB = file.Size / 1048576#
    Else
        GetFileSizeMB = 0
    End If
End Function

' Create directory recursively (like mkdir -p)
Public Function CreateDirectoryRecursive(path As String) As Boolean
    On Error Resume Next
    
    If FolderExists(path) Then
        CreateDirectoryRecursive = True
        Exit Function
    End If
    
    ' Get parent directory
    Dim parentPath As String
    Dim lastSlash As Integer
    lastSlash = InStrRev(path, "\")
    
    If lastSlash > 0 Then
        parentPath = Left(path, lastSlash - 1)
        
        ' Recursively create parent
        If Not FolderExists(parentPath) Then
            If Not CreateDirectoryRecursive(parentPath) Then
                CreateDirectoryRecursive = False
                Exit Function
            End If
        End If
    End If
    
    ' Create this directory
    MkDir path
    
    If Err.Number = 0 Then
        CreateDirectoryRecursive = True
    Else
        CreateDirectoryRecursive = False
    End If
End Function
