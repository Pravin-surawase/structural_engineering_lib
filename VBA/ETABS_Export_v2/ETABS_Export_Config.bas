Attribute VB_Name = "ETABS_Export_Config"
Option Explicit

'==============================================================================
' ETABS EXPORT CONFIGURATION
'==============================================================================
' Edit these settings to customize your export
' Created: 2026-01-17 | Version: 1.0
'==============================================================================

' ============================================
' 1. OUTPUT SETTINGS
' ============================================

' Output folder (use %USERPROFILE% for Documents folder)
Public Const OUTPUT_FOLDER As String = "%USERPROFILE%\Documents\ETABS_Export"

' File names
Public Const FORCES_FILENAME As String = "beam_forces.csv"
Public Const PROPERTIES_FILENAME As String = "beam_properties.csv"
Public Const SPANS_FILENAME As String = "beam_spans.csv"

' Export options
Public Const EXPORT_TO_EXCEL As Boolean = True    ' Also write to Excel sheet
Public Const EXPORT_TO_CSV As Boolean = True      ' Write to CSV file
Public Const OPEN_FOLDER_AFTER As Boolean = True  ' Open folder when done

' ============================================
' 2. LOAD COMBINATION FILTER
' ============================================

' Set to True to export only specific combinations
Public Const FILTER_COMBOS As Boolean = True

' List of design combinations to export (comma-separated)
' Set these to match YOUR model's combo names
' Example: "COMB1,COMB2,1.5(DL+LL),1.2(DL+LL+EQX)"
Public Const DESIGN_COMBOS As String = "COMB1,COMB2,COMB3,COMB4,COMB5,COMB6,COMB7,COMB8"

' If True, also include individual load cases (Modal, DEAD, LIVE, etc.)
Public Const INCLUDE_LOAD_CASES As Boolean = False

' ============================================
' 3. STATION/LOCATION FILTER
' ============================================

' Station filtering method:
'   1 = Envelope Only (max/min M3, max V2 per combo) - SMALLEST output
'   2 = Critical Stations (supports + midspan + quarter) - MEDIUM output
'   3 = All Stations - LARGEST output (no filtering)
Public Const STATION_FILTER_METHOD As Integer = 1

' Minimum moment threshold (skip locations where |M3| < this value in kN·m)
Public Const MIN_MOMENT_THRESHOLD As Double = 1#

' ============================================
' 4. MATERIAL DEFAULTS
' ============================================

' Used when material not found in model
Public Const DEFAULT_FCK As Double = 25    ' N/mm² (M25 concrete)
Public Const DEFAULT_FY As Double = 500    ' N/mm² (Fe500 steel)
Public Const DEFAULT_COVER As Double = 25  ' mm clear cover

' ============================================
' 5. FRAME TYPE FILTER
' ============================================

' Filter by section type prefix (leave blank to export all)
' Example: "B" for beams only, "C" for columns only
Public Const SECTION_PREFIX_FILTER As String = ""

' Filter by story (leave blank to export all)
' Example: "Story1,Story2,Story3"
Public Const STORY_FILTER As String = ""

' ============================================
' HELPER FUNCTIONS
' ============================================

' Get resolved output folder path
Public Function GetOutputFolder() As String
    Dim path As String
    path = Replace(OUTPUT_FOLDER, "%USERPROFILE%", Environ("USERPROFILE"))
    
    ' Create if doesn't exist
    If Dir(path, vbDirectory) = "" Then
        MkDir path
    End If
    
    GetOutputFolder = path
End Function

' Get design combo list as array
Public Function GetDesignCombos() As Variant
    GetDesignCombos = Split(DESIGN_COMBOS, ",")
End Function

' Check if a combo should be exported
Public Function ShouldExportCombo(comboName As String) As Boolean
    If Not FILTER_COMBOS Then
        ShouldExportCombo = True
        Exit Function
    End If
    
    Dim combos As Variant
    combos = GetDesignCombos()
    
    Dim i As Long
    For i = LBound(combos) To UBound(combos)
        If Trim(combos(i)) = comboName Then
            ShouldExportCombo = True
            Exit Function
        End If
    Next i
    
    ShouldExportCombo = False
End Function

' Check if a story should be exported
Public Function ShouldExportStory(storyName As String) As Boolean
    If STORY_FILTER = "" Then
        ShouldExportStory = True
        Exit Function
    End If
    
    Dim stories As Variant
    stories = Split(STORY_FILTER, ",")
    
    Dim i As Long
    For i = LBound(stories) To UBound(stories)
        If Trim(stories(i)) = storyName Then
            ShouldExportStory = True
            Exit Function
        End If
    Next i
    
    ShouldExportStory = False
End Function

' Print current configuration
Public Sub PrintConfig()
    Debug.Print "========== EXPORT CONFIGURATION =========="
    Debug.Print "Output folder: " & GetOutputFolder()
    Debug.Print "Filter combos: " & FILTER_COMBOS
    Debug.Print "Design combos: " & DESIGN_COMBOS
    Debug.Print "Station filter: " & STATION_FILTER_METHOD & " (1=Envelope, 2=Critical, 3=All)"
    Debug.Print "Min moment: " & MIN_MOMENT_THRESHOLD & " kN·m"
    Debug.Print "=========================================="
End Sub
