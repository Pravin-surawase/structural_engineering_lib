Attribute VB_Name = "DEBUG_Step6_DatabaseTables"
Option Explicit

'==============================================================================
' STEP 6: Try DatabaseTables approach (alternative to Results API)
'==============================================================================

Dim myHelper As ETABSv1.Helper
Dim myETABSObject As ETABSv1.cOAPI
Dim mySapModel As ETABSv1.cSapModel

Sub Step6_TryDatabaseTables()
    On Error GoTo ErrorHandler
    
    ' Connect
    Set myHelper = New ETABSv1.Helper
    Set myETABSObject = GetObject(, "CSI.ETABS.API.ETABSObject")
    Set mySapModel = myETABSObject.SapModel
    
    Dim ret As Long
    ret = mySapModel.SetPresentUnits(eUnits_kN_m_C)
    
    Debug.Print "========== STEP 6: DATABASE TABLES =========="
    
    ' List all available tables
    Dim NumberTables As Long
    Dim TableKey() As String
    Dim TableName() As String
    Dim ImportType() As Long  ' Changed from eImportType to Long
    Dim IsEmpty() As Boolean
    
    ret = mySapModel.DatabaseTables.GetAllAvailableTables(NumberTables, TableKey, TableName, ImportType, IsEmpty)
    
    Debug.Print "Available tables: " & NumberTables
    Debug.Print ""
    
    ' Look for frame-related tables
    Dim i As Long
    For i = 0 To NumberTables - 1
        If InStr(1, LCase(TableKey(i)), "frame", vbTextCompare) > 0 Or _
           InStr(1, LCase(TableName(i)), "frame", vbTextCompare) > 0 Or _
           InStr(1, LCase(TableKey(i)), "element", vbTextCompare) > 0 Then
            Debug.Print "Found: " & TableKey(i) & " - " & TableName(i) & " (Empty: " & IsEmpty(i) & ")"
        End If
    Next i
    
    Debug.Print ""
    Debug.Print "--- Testing Frame Force Tables ---"
    
    ' Try common frame force table names
    Dim tableNames As Variant
    tableNames = Array( _
        "Frame Forces", _
        "Element Forces - Frames", _
        "Frame Element Forces", _
        "Element Forces", _
        "Frame Results", _
        "FRAME FORCES" _
    )
    
    For i = 0 To UBound(tableNames)
        Debug.Print "Trying: " & tableNames(i)
        
        Dim FieldKeyList() As String
        Dim NumberRecords As Long
        Dim TableData() As Variant  ' Changed from String to Variant
        
        ret = mySapModel.DatabaseTables.GetTableForDisplayArray( _
            tableNames(i), FieldKeyList, NumberRecords, TableData)
        
        If ret = 0 And NumberRecords > 0 Then
            Debug.Print "  ✓ SUCCESS! Got " & NumberRecords & " records"
            Debug.Print "  Fields: " & UBound(FieldKeyList) + 1
            
            ' Show first few field names
            Dim j As Long
            For j = 0 To Application.Min(9, UBound(FieldKeyList))
                Debug.Print "    Field " & j & ": " & FieldKeyList(j)
            Next j
            
            Exit For  ' Found it!
        Else
            Debug.Print "  ✗ Failed (ret=" & ret & ")"
        End If
    Next i
    
    MsgBox "Check Immediate Window for results!", vbInformation
    Exit Sub
    
ErrorHandler:
    MsgBox "Error: " & Err.Description & " (#" & Err.Number & ")", vbCritical
End Sub
