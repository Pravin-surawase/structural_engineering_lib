Attribute VB_Name = "mod_Validation"
Option Explicit

'==============================================================================
' Validation Module
' Unit conversion, CSV normalization, and schema validation
'==============================================================================

' Get ETABS units and build conversion factors
Public Function GetAndValidateUnits(sapModel As Object) As UnitConversion
    On Error GoTo UnitError
    
    Dim units As UnitConversion
    
    ' Get current ETABS units
    Dim forceUnits As Long
    Dim lengthUnits As Long
    Dim tempUnits As Long
    
    Dim ret As Long
    ret = sapModel.GetPresentUnits_2(forceUnits, lengthUnits, tempUnits)
    
    If ret <> 0 Then
        LogError "Cannot get ETABS units: ret=" & ret
        units.ForceToKN = 0  ' Signal error
        GetAndValidateUnits = units
        Exit Function
    End If
    
    ' Map force units (eForce enum values)
    Select Case forceUnits
        Case 1  ' lb
            units.ForceUnit = "lb"
            units.ForceToKN = 0.00444822
        Case 2  ' kip
            units.ForceUnit = "kip"
            units.ForceToKN = 4.44822
        Case 3  ' N
            units.ForceUnit = "N"
            units.ForceToKN = 0.001
        Case 4  ' kN
            units.ForceUnit = "kN"
            units.ForceToKN = 1#
        Case 5  ' kgf
            units.ForceUnit = "kgf"
            units.ForceToKN = 0.00980665
        Case 6  ' tonf
            units.ForceUnit = "tonf"
            units.ForceToKN = 9.80665
        Case Else
            LogError "Unknown force unit: " & forceUnits
            units.ForceToKN = 0
            GetAndValidateUnits = units
            Exit Function
    End Select
    
    ' Map length units (eLength enum values)
    Select Case lengthUnits
        Case 1  ' inch
            units.LengthUnit = "in"
            units.LengthToMM = 25.4
        Case 2  ' ft
            units.LengthUnit = "ft"
            units.LengthToMM = 304.8
        Case 3  ' mm
            units.LengthUnit = "mm"
            units.LengthToMM = 1#
        Case 4  ' m
            units.LengthUnit = "m"
            units.LengthToMM = 1000#
        Case 5  ' cm
            units.LengthUnit = "cm"
            units.LengthToMM = 10#
        Case Else
            LogError "Unknown length unit: " & lengthUnits
            units.ForceToKN = 0
            GetAndValidateUnits = units
            Exit Function
    End Select
    
    ' Calculate moment conversion
    ' Moment in ETABS = Force × Length
    ' Target: kN·m
    ' kN·m = (ETABS_Force × ForceToKN) × (ETABS_Length × LengthToMM / 1000)
    units.MomentToKNM = units.ForceToKN * (units.LengthToMM / 1000#)
    
    LogInfo "? ETABS Units: Force=" & units.ForceUnit & ", Length=" & units.LengthUnit
    LogInfo "  Conversions: F?kN=" & Format(units.ForceToKN, "0.000000") & _
            ", L?mm=" & Format(units.LengthToMM, "0.000") & _
            ", M?kN·m=" & Format(units.MomentToKNM, "0.000000")
    
    GetAndValidateUnits = units
    Exit Function
    
UnitError:
    LogError "Unit detection error: " & Err.Description
    units.ForceToKN = 0
    GetAndValidateUnits = units
End Function

' Normalize CSV to schema format
Public Function ValidateAndNormalizeCSV(rawCSVPath As String, _
                                        outputPath As String, _
                                        units As UnitConversion) As Boolean
    On Error GoTo ValidationError
    
    LogInfo "Normalizing CSV..."
    LogInfo "  Input: " & rawCSVPath
    LogInfo "  Output: " & outputPath
    
    ' Open raw CSV
    Dim wb As Workbook
    Set wb = Workbooks.Open(rawCSVPath, ReadOnly:=True)
    
    Dim ws As Worksheet
    Set ws = wb.Sheets(1)
    
    ' Find column indices
    Dim colMap As Object
    Set colMap = CreateObject("Scripting.Dictionary")
    
    Dim col As Long
    For col = 1 To ws.UsedRange.Columns.Count
        Dim header As String
        header = Trim(CStr(ws.Cells(1, col).Value))
        If Len(header) > 0 Then
            colMap(header) = col
        End If
    Next
    
    ' Validate required columns exist (with alternate names)
    ' ETABS exports may use variations like "OutputCase" vs "Output Case"
    Dim requiredCols() As Variant
    requiredCols = Array("Story", "Label", "OutputCase|Output Case|LoadCase|Load Case", "M3", "V2")
    
    Dim missing As String
    missing = ""
    
    Dim colName As Variant
    For Each colName In requiredCols
        ' Support alternate column names with pipe separator
        Dim colVariants() As String
        colVariants = Split(CStr(colName), "|")
        
        Dim found As Boolean
        found = False
        
        Dim variant As Variant
        For Each variant In colVariants
            If colMap.Exists(Trim(CStr(variant))) Then
                ' Normalize to first name
                If CStr(variant) <> CStr(colVariants(0)) Then
                    colMap(CStr(colVariants(0))) = colMap(Trim(CStr(variant)))
                End If
                found = True
                Exit For
            End If
        Next
        
        If Not found Then
            missing = missing & CStr(colVariants(0)) & ", "
        End If
    Next
    
    If Len(missing) > 0 Then
        missing = Left(missing, Len(missing) - 2)
        LogError "Missing required columns: " & missing
        wb.Close SaveChanges:=False
        ValidateAndNormalizeCSV = False
        Exit Function
    End If
    
    LogInfo "? All required columns found"
    
    ' Create output workbook
    Dim wbOut As Workbook
    Set wbOut = Workbooks.Add
    
    Dim wsOut As Worksheet
    Set wsOut = wbOut.Sheets(1)
    
    ' Write schema headers
    wsOut.Cells(1, 1).Value = "Story"
    wsOut.Cells(1, 2).Value = "Label"
    wsOut.Cells(1, 3).Value = "Output Case"
    wsOut.Cells(1, 4).Value = "Station"
    wsOut.Cells(1, 5).Value = "M3"
    wsOut.Cells(1, 6).Value = "V2"
    wsOut.Cells(1, 7).Value = "P"
    
    ' Copy and convert data
    Dim lastRow As Long
    lastRow = ws.UsedRange.Rows.Count
    
    Dim outRow As Long
    outRow = 2
    
    Dim row As Long
    For row = 2 To lastRow
        ' Basic columns
        wsOut.Cells(outRow, 1).Value = ws.Cells(row, colMap("Story")).Value
        wsOut.Cells(outRow, 2).Value = ws.Cells(row, colMap("Label")).Value
        wsOut.Cells(outRow, 3).Value = ws.Cells(row, colMap("OutputCase")).Value
        
        ' Station (with multiple possible column names)
        Dim stationCol As Long
        stationCol = 0
        If colMap.Exists("Station") Then stationCol = colMap("Station")
        If stationCol = 0 And colMap.Exists("ObjSta") Then stationCol = colMap("ObjSta")
        If stationCol = 0 And colMap.Exists("Object Station") Then stationCol = colMap("Object Station")
        
        If stationCol > 0 Then
            Dim station As Double
            station = Val(ws.Cells(row, stationCol).Value)
            wsOut.Cells(outRow, 4).Value = station * units.LengthToMM
        Else
            wsOut.Cells(outRow, 4).Value = 0
        End If
        
        ' Forces (convert to kN and kN·m)
        Dim m3 As Double, v2 As Double, p As Double
        
        m3 = Val(ws.Cells(row, colMap("M3")).Value)
        v2 = Val(ws.Cells(row, colMap("V2")).Value)
        
        If colMap.Exists("P") Then
            p = Val(ws.Cells(row, colMap("P")).Value)
        Else
            p = 0
        End If
        
        ' Apply conversions
        wsOut.Cells(outRow, 5).Value = m3 * units.MomentToKNM
        wsOut.Cells(outRow, 6).Value = v2 * units.ForceToKN
        wsOut.Cells(outRow, 7).Value = p * units.ForceToKN
        
        outRow = outRow + 1
        
        ' Progress
        If row Mod 1000 = 0 Then
            Application.StatusBar = "Normalizing: " & row & "/" & lastRow
            DoEvents
        End If
    Next
    
    ' Save as CSV
    wbOut.SaveAs outputPath, xlCSV
    wbOut.Close SaveChanges:=False
    wb.Close SaveChanges:=False
    
    LogInfo "? Normalized " & (outRow - 2) & " data rows"
    
    ValidateAndNormalizeCSV = True
    Exit Function
    
ValidationError:
    On Error Resume Next
    If Not wb Is Nothing Then wb.Close SaveChanges:=False
    If Not wbOut Is Nothing Then wbOut.Close SaveChanges:=False
    LogError "Validation error: " & Err.Description
    ValidateAndNormalizeCSV = False
End Function

' Validate environment before export
Public Function ValidateEnvironment() As Boolean
    On Error GoTo ValidationError
    
    LogInfo "Validating environment..."
    
    ' Check 1: ETABS API registered
    On Error Resume Next
    Dim helper As Object
    Set helper = CreateObject("ETABSv1.Helper")
    
    If Err.Number <> 0 Or helper Is Nothing Then
        LogError "ETABS API not registered"
        LogError "Please install ETABS or register the API"
        ValidateEnvironment = False
        Exit Function
    End If
    On Error GoTo ValidationError
    
    LogInfo "? ETABS API registered"
    
    ' Check 2: Output folder writable
    If Not FolderExists(g_OutputFolder) Then
        On Error Resume Next
        MkDir g_OutputFolder
        If Err.Number <> 0 Then
            LogError "Cannot create output folder: " & g_OutputFolder
            ValidateEnvironment = False
            Exit Function
        End If
        On Error GoTo ValidationError
        LogInfo "Created output folder: " & g_OutputFolder
    End If
    
    LogInfo "? Output folder ready: " & g_OutputFolder
    
    ' Check 3: Disk space (at least 100MB free)
    Dim freeSpace As Variant
    freeSpace = GetDiskFreeSpace(Left(g_OutputFolder, 1))
    
    If freeSpace < 100 Then
        LogWarning "Low disk space: " & freeSpace & " MB"
    Else
        LogInfo "? Disk space: " & freeSpace & " MB available"
    End If
    
    ValidateEnvironment = True
    Exit Function
    
ValidationError:
    LogError "Validation error: " & Err.Description
    ValidateEnvironment = False
End Function

' Create metadata JSON file
Public Sub CreateMetadataFile(sapModel As Object, outputFolder As String, units As UnitConversion)
    On Error Resume Next
    
    Dim metaPath As String
    metaPath = outputFolder & "\metadata.json"
    
    Dim fileNum As Integer
    fileNum = FreeFile
    
    Open metaPath For Output As #fileNum
    
    ' Get model info
    Dim modelPath As String
    modelPath = sapModel.GetModelFilename
    
    Dim modelName As String
    If Len(modelPath) > 0 Then
        modelName = Right(modelPath, Len(modelPath) - InStrRev(modelPath, "\"))
    Else
        modelName = "Unknown"
    End If
    
    ' Write JSON
    Print #fileNum, "{"
    Print #fileNum, "  ""export_version"": """ & APP_VERSION & ""","
    Print #fileNum, "  ""export_timestamp"": """ & Format(Now, "yyyy-mm-dd hh:nn:ss") & ""","
    Print #fileNum, "  ""model_name"": """ & modelName & ""","
    Print #fileNum, "  ""model_path"": """ & Replace(modelPath, "\", "\\") & ""","
    Print #fileNum, "  ""etabs_units"": {"
    Print #fileNum, "    ""force"": """ & units.ForceUnit & ""","
    Print #fileNum, "    ""length"": """ & units.LengthUnit & """"
    Print #fileNum, "  },"
    Print #fileNum, "  ""output_units"": {"
    Print #fileNum, "    ""force"": ""kN"","
    Print #fileNum, "    ""length"": ""mm"","
    Print #fileNum, "    ""moment"": ""kN·m"""
    Print #fileNum, "  }"
    Print #fileNum, "}"
    
    Close #fileNum
    
    If Err.Number = 0 Then
        LogInfo "? Metadata file created: " & metaPath
    Else
        LogWarning "Could not create metadata file: " & Err.Description
    End If
End Sub
