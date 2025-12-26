Attribute VB_Name = "M02_Types"
Option Explicit

' ==============================================================================
' Module:       M02_Types
' Description:  Custom Data Types (UDTs) and Enums
' Version:      1.0.01
' License:      MIT
' ==============================================================================


' ------------------------------------------------------------------------------
' Enums
' ------------------------------------------------------------------------------

Public Enum BeamType
    Rectangular = 1
    Flanged_T = 2
    Flanged_L = 3
End Enum

Public Enum DesignSectionType
    UnderReinforced = 1
    Balanced = 2
    OverReinforced = 3
End Enum

' Serviceability (v0.8+)
Public Enum SupportCondition
    Cantilever = 1
    SimplySupported = 2
    Continuous = 3
End Enum

Public Enum ExposureClass
    Mild = 1
    Moderate = 2
    Severe = 3
    VerySevere = 4
End Enum

' ------------------------------------------------------------------------------
' User Defined Types (UDTs)
' ------------------------------------------------------------------------------

' Result type for Flexure Analysis
Public Type FlexureResult
    Mu_Lim As Double        ' Limiting Moment of Resistance (kN-m)
    Ast_Required As Double  ' Area of steel required (mm^2)
    Asc_Required As Double  ' Area of compression steel required (mm^2)
    Pt_Provided As Double   ' Percentage of steel provided
    SectionType As DesignSectionType
    Xu As Double            ' Depth of neutral axis (mm)
    Xu_max As Double        ' Max depth of neutral axis (mm)
    IsSafe As Boolean       ' True if design is valid
    ErrorMessage As String  ' Error description if any
End Type


' Result type for Shear Analysis
Public Type ShearResult
    Tv As Double            ' Nominal shear stress (N/mm^2)
    Tc As Double            ' Design shear strength of concrete (N/mm^2)
    Tc_max As Double        ' Max shear stress (N/mm^2)
    Vus As Double           ' Shear capacity of stirrups (kN)
    Spacing As Double       ' Calculated spacing (mm)
    IsSafe As Boolean       ' True if section is safe in shear (Tv < Tc_max)
    Remarks As String       ' Design remarks (e.g., "Min Shear Reinforcement")
End Type

'
' Serviceability result types (v0.8+)
'
Public Type DeflectionResult
    IsOK As Boolean
    Remarks As String
    Support As SupportCondition
    LD_Ratio As Double
    Allowable_LD As Double
    BaseAllowable_LD As Double
    MF_TensionSteel As Double
    MF_CompressionSteel As Double
    MF_Flanged As Double
    Assumptions As String
End Type

Public Type CrackWidthResult
    IsOK As Boolean
    Remarks As String
    Exposure As ExposureClass
    Wcr_mm As Double
    Limit_mm As Double
    Acr_mm As Double
    Cmin_mm As Double
    h_mm As Double
    x_mm As Double
    Epsilon_m As Double
    Denom As Double
    Assumptions As String
End Type


' ------------------------------------------------------------------------------
' Detailing Types (v0.7+)
' ------------------------------------------------------------------------------

' Bar arrangement for a single zone/location
Public Type BarArrangement
    count As Long           ' Number of bars
    diameter As Double      ' Bar diameter (mm)
    area_provided As Double ' Total area provided (mm^2)
    spacing As Double       ' Center-to-center spacing (mm)
    layers As Long          ' Number of layers (1 or 2)
End Type

' Stirrup arrangement for a zone
Public Type StirrupArrangement
    diameter As Double      ' Stirrup diameter (mm)
    legs As Long            ' Number of legs (2, 4, 6)
    spacing As Double       ' Spacing (mm)
    zone_length As Double   ' Length of zone (mm)
End Type

' Complete beam detailing result
Public Type BeamDetailingResult
    beam_id As String       ' Beam identifier
    story As String         ' Story identifier
    b As Double             ' Beam width (mm)
    D As Double             ' Beam depth (mm)
    span As Double          ' Span length (mm)
    cover As Double         ' Clear cover (mm)
    
    ' Bottom bars (tension at mid-span)
    bottom_start As BarArrangement
    bottom_mid As BarArrangement
    bottom_end As BarArrangement
    
    ' Top bars (tension at supports / compression at mid)
    top_start As BarArrangement
    top_mid As BarArrangement
    top_end As BarArrangement
    
    ' Stirrups
    stirrup_start As StirrupArrangement
    stirrup_mid As StirrupArrangement
    stirrup_end As StirrupArrangement
    
    ' Detailing parameters
    ld_tension As Double    ' Development length for tension bars (mm)
    ld_compression As Double ' Development length for compression bars (mm)
    lap_length As Double    ' Lap splice length (mm)
    
    ' Validity
    is_valid As Boolean
    remarks As String
End Type


' ------------------------------------------------------------------------------
' BBS Types (v0.9+)
' ------------------------------------------------------------------------------

' Single line item in a Bar Bending Schedule
Public Type BBSLineItem
    bar_mark As String      ' Unique identifier (e.g., "A1", "B1", "S1")
    member_id As String     ' Beam/element ID
    location As String      ' "bottom", "top", "stirrup"
    zone As String          ' "start", "mid", "end", or "full"
    shape_code As String    ' Shape per IS 2502 (A, B, C, D, E, etc.)
    diameter_mm As Double   ' Bar diameter
    no_of_bars As Long      ' Quantity
    cut_length_mm As Double ' Total length including hooks/bends
    total_length_mm As Double ' no_of_bars * cut_length
    unit_weight_kg As Double  ' Weight per bar
    total_weight_kg As Double ' Total weight
    remarks As String
End Type

' Summary of Bar Bending Schedule
Public Type BBSSummary
    member_id As String
    total_items As Long
    total_bars As Long
    total_length_m As Double  ' Total length in meters
    total_weight_kg As Double
End Type
