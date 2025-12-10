Attribute VB_Name = "M02_Types"
Option Explicit

' ==============================================================================
' Module:       M02_Types
' Description:  Custom Data Types (UDTs) and Enums
' Version:      1.0.0
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

' ------------------------------------------------------------------------------
' User Defined Types (UDTs)
' ------------------------------------------------------------------------------

' Result type for Flexure Analysis
Public Type FlexureResult
    Mu_Lim As Double        ' Limiting Moment of Resistance (kN-m)
    Ast_Required As Double  ' Area of steel required (mm^2)
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
