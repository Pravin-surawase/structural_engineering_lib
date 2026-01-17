Attribute VB_Name = "mod_Types"
Option Explicit

'==============================================================================
' Type Definitions Module
' Common data structures used across modules
'==============================================================================

' Unit conversion factors
Public Type UnitConversion
    ForceUnit As String         ' "kN", "kip", "N", "lb"
    LengthUnit As String        ' "mm", "m", "in", "ft"
    ForceToKN As Double         ' Conversion factor to kN
    LengthToMM As Double        ' Conversion factor to mm
    MomentToKNM As Double       ' Conversion factor to kN.m
End Type

' ETABS unit enumerations (from OAPI)
' eForce enumeration
Public Enum eForce
    lb = 1
    Kip = 2
    N = 3
    kN = 4
    kgf = 5
    tonf = 6
End Enum

' eLength enumeration  
Public Enum eLength
    inch = 1
    ft = 2
    mm = 3
    m = 4
    cm = 5
    micron = 6  ' Micron (micrometer)
End Enum

' Export result summary
Public Type ExportResult
    ForcesExported As Boolean
    SectionsExported As Boolean
    GeometryExported As Boolean
    StoriesExported As Boolean
    
    TotalFrames As Long
    ExportedFrames As Long
    
    WarningCount As Integer
    ErrorCount As Integer
End Type
