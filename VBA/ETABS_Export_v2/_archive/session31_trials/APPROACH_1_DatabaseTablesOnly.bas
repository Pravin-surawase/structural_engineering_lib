Attribute VB_Name = "APPROACH_1_DatabaseTablesOnly"
Option Explicit

'==============================================================================
' APPROACH 1: DatabaseTables Only (Simplest)
'==============================================================================
' Strategy: Only use DatabaseTables.GetTableForDisplayCSVFile
' No Direct API calls at all
' Fastest if it works for your ETABS version
'==============================================================================

Sub Approach1_ExportBeamForces()
    On Error GoTo ErrorHandler
    
    ' Connect
    Dim helper As Object, etabs As Object, sapModel As Object
    Set helper = CreateObject("ETABSv1.Helper")
    Set etabs = helper.GetObject("CSI.ETABS.API.ETABSObject")
    Set sapModel = etabs.SapModel
    
    ' Set units
    sapModel.SetPresentUnits 6  ' kN, m, C
    
    ' Output path
    Dim csvPath As String
    csvPath = Environ("USERPROFILE") & "\Documents\ETABS_Export\beam_forces_approach1.csv"
    
    ' Try different table names
    Dim tableNames As Variant
    tableNames = Array( _
        "Element Forces - Frames", _
        "Element Forces-Frames", _
        "Frame Element Forces", _
        "Frame Forces", _
        "Frame Results", _
        "Analysis Results - Frame Forces", _
        "Object Element Forces - Frames")
    
    Dim i As Long, ret As Long
    For i = LBound(tableNames) To UBound(tableNames)
        Debug.Print "Trying: " & tableNames(i)
        
        ret = sapModel.DatabaseTables.GetTableForDisplayCSVFile( _
            CStr(tableNames(i)), csvPath, False, 0, "")
        
        If ret = 0 Then
            If Dir(csvPath) <> "" Then
                MsgBox "SUCCESS! Exported via table: " & tableNames(i) & vbCrLf & csvPath
                Exit Sub
            End If
        End If
    Next i
    
    MsgBox "All table names failed. Your ETABS version may use different table names."
    Exit Sub

ErrorHandler:
    MsgBox "Error: " & Err.Description
End Sub
