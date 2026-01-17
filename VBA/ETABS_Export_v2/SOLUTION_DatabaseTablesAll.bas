Attribute VB_Name = "SOLUTION_DatabaseTablesAll"
Option Explicit

'==============================================================================
' SOLUTION: Try ALL possible DatabaseTables export names
'==============================================================================
' Since FrameObj methods fail, use DatabaseTables with exhaustive table list
' This works without type library reference
'==============================================================================

Sub Export_TryAllTableNames()
    On Error Resume Next
    
    ' Connect
    Dim helper As Object, etabs As Object, sapModel As Object
    Set helper = CreateObject("ETABSv1.Helper")
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    Set sapModel = etabs.SapModel
    
    sapModel.SetPresentUnits 6  ' kN, m, C
    
    ' Output folder
    Dim outputFolder As String
    outputFolder = Environ("USERPROFILE") & "\Documents\ETABS_Export"
    If Dir(outputFolder, vbDirectory) = "" Then MkDir outputFolder
    
    Dim csvPath As String
    csvPath = outputFolder & "\beam_forces_final.csv"
    
    ' Comprehensive list of possible table names across ETABS versions
    Dim tableNames As Variant
    tableNames = Array( _
        "Element Forces - Frames", _
        "Element Forces-Frames", _
        "Frame Element Forces", _
        "Frame Forces", _
        "Frame Results", _
        "Analysis Results - Frame Forces", _
        "Object Element Forces - Frames", _
        "Element Forces", _
        "Frame Element Forces - Frames", _
        "Results - Frame Forces", _
        "Frame Object Forces", _
        "Connectivity - Frame", _
        "Frame Section Assignments" _
    )
    
    Dim i As Long, ret As Long
    Dim successTable As String
    
    For i = LBound(tableNames) To UBound(tableNames)
        Debug.Print "Trying table: " & tableNames(i)
        
        Err.Clear
        ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
            CStr(tableNames(i)), csvPath, False, 0, "")
        
        If Err.Number = 0 And ret = 0 Then
            ' Check if file created and has content
            If Dir(csvPath) <> "" Then
                Dim fso As Object
                Set fso = CreateObject("Scripting.FileSystemObject")
                
                If fso.GetFile(csvPath).Size > 100 Then
                    successTable = tableNames(i)
                    Exit For
                End If
            End If
        End If
    Next i
    
    If successTable <> "" Then
        MsgBox "SUCCESS!" & vbCrLf & vbCrLf & _
               "Table: " & successTable & vbCrLf & _
               "Output: " & csvPath & vbCrLf & vbCrLf & _
               "File size: " & fso.GetFile(csvPath).Size & " bytes", _
               vbInformation, "Export Complete"
        
        ' Open folder
        Shell "explorer.exe /select,""" & csvPath & """", vbNormalFocus
    Else
        MsgBox "All table names failed." & vbCrLf & vbCrLf & _
               "Your ETABS version may not support DatabaseTables export." & vbCrLf & _
               "Please add ETABS type library reference:" & vbCrLf & _
               "Tools → References → Browse for ETABS.exe", _
               vbExclamation, "Export Failed"
    End If
End Sub

Sub ListAllAvailableTables()
    ' Try to list all available table names
    On Error Resume Next
    
    Dim helper As Object, etabs As Object, sapModel As Object
    Set helper = CreateObject("ETABSv1.Helper")
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    Set sapModel = etabs.SapModel
    
    Dim tableKey() As String, tableName() As String
    Dim importType() As Long, isEmptyAfterTabularInputAll() As Boolean
    Dim NumberTables As Long
    
    Err.Clear
    Dim ret As Long
    ret = sapModel.DatabaseTables.GetAvailableTables( _
        NumberTables, tableKey, tableName, importType, isEmptyAfterTabularInputAll)
    
    If Err.Number = 0 And ret = 0 Then
        Dim msg As String
        msg = "Available Tables (" & NumberTables & "):" & vbCrLf & vbCrLf
        
        Dim i As Long
        For i = LBound(tableName) To UBound(tableName)
            msg = msg & tableName(i) & vbCrLf
            If i > 50 Then
                msg = msg & "... (truncated)"
                Exit For
            End If
        Next i
        
        MsgBox msg, vbInformation, "Available Tables"
    Else
        MsgBox "GetAvailableTables failed: " & Err.Description, vbCritical
    End If
End Sub
