Attribute VB_Name = "M18_BBS"
Option Explicit

' ==============================================================================
' Module:       M18_BBS
' Description:  Bar Bending Schedule (BBS) Generation — IS 2502:1999 / SP 34:1987
' Version:      0.9.4
' License:      MIT
' ==============================================================================
'
' References:
' - IS 2502:1999 (Steel for Reinforcement)
' - SP 34:1987 (Handbook on Concrete Reinforcement and Detailing)
' - IS 1786:2008 (High Strength Deformed Steel Bars)
'
' Design constraints:
' - Deterministic outputs (same inputs → same outputs).
' - Units explicit: mm, kg, N/mm².
' - Mac-safe: CDbl() for all multiplications, no Debug.Print in calcs.

' =============================================================================
' Constants
' =============================================================================

Private Const STEEL_DENSITY_KG_M3 As Double = 7850#

' Rounding rules per SP 34 / site practice
Private Const LENGTH_ROUND_MM As Double = 10#
Private Const WEIGHT_ROUND_DECIMALS As Long = 2

' Standard stock lengths (mm)
Public Const STOCK_6M As Double = 6000#
Public Const STOCK_7P5M As Double = 7500#
Public Const STOCK_9M As Double = 9000#
Public Const STOCK_12M As Double = 12000#


' =============================================================================
' Weight Calculations
' =============================================================================

Public Function BBS_CalculateBarWeight( _
    ByVal diameter_mm As Double, _
    ByVal length_mm As Double _
) As Double
    ' Calculate weight of a single bar.
    '
    ' Weight = (π × d² / 4) × length × density
    '
    ' Args:
    '     diameter_mm: Bar diameter (mm)
    '     length_mm: Bar length (mm)
    '
    ' Returns:
    '     Weight in kg (rounded to 2 decimal places)
    
    Dim d_m As Double
    Dim l_m As Double
    Dim area_m2 As Double
    Dim weight As Double
    Const PI As Double = 3.14159265358979
    
    ' Validate inputs
    If diameter_mm <= 0# Or length_mm <= 0# Then
        BBS_CalculateBarWeight = 0#
        Exit Function
    End If
    
    ' Convert to meters (Mac-safe: use CDbl)
    d_m = CDbl(diameter_mm) / 1000#
    l_m = CDbl(length_mm) / 1000#
    
    ' Cross-sectional area (m²)
    area_m2 = PI * CDbl(d_m / 2#) * CDbl(d_m / 2#)
    
    ' Weight (kg)
    weight = CDbl(area_m2) * CDbl(l_m) * STEEL_DENSITY_KG_M3
    
    BBS_CalculateBarWeight = Round(weight, WEIGHT_ROUND_DECIMALS)
End Function


Public Function BBS_UnitWeightPerMeter(ByVal diameter_mm As Double) As Double
    ' Calculate unit weight per meter for a bar diameter.
    '
    ' Args:
    '     diameter_mm: Bar diameter (mm)
    '
    ' Returns:
    '     Weight in kg/m
    
    BBS_UnitWeightPerMeter = BBS_CalculateBarWeight(diameter_mm, 1000#)
End Function


Public Function BBS_GetStandardUnitWeight(ByVal diameter_mm As Long) As Double
    ' Get pre-calculated standard unit weight (kg/m) for common diameters.
    '
    ' Args:
    '     diameter_mm: Bar diameter (mm) — integer values only
    '
    ' Returns:
    '     Weight in kg/m, or 0 if not a standard diameter
    
    Select Case diameter_mm
        Case 6: BBS_GetStandardUnitWeight = 0.222
        Case 8: BBS_GetStandardUnitWeight = 0.395
        Case 10: BBS_GetStandardUnitWeight = 0.617
        Case 12: BBS_GetStandardUnitWeight = 0.888
        Case 16: BBS_GetStandardUnitWeight = 1.579
        Case 20: BBS_GetStandardUnitWeight = 2.466
        Case 25: BBS_GetStandardUnitWeight = 3.853
        Case 32: BBS_GetStandardUnitWeight = 6.313
        Case Else: BBS_GetStandardUnitWeight = BBS_UnitWeightPerMeter(CDbl(diameter_mm))
    End Select
End Function


' =============================================================================
' Cut Length Calculations
' =============================================================================

Public Function BBS_CalculateHookLength( _
    ByVal diameter_mm As Double, _
    Optional ByVal hook_angle As Double = 90# _
) As Double
    ' Calculate hook length per IS 456 Cl 26.2.2.1.
    '
    ' Standard hooks:
    ' - 90° hook: 8d minimum
    ' - 180° hook: 4d beyond bend + 4d radius = 8d equivalent
    ' - 135° hook: 6d
    '
    ' Args:
    '     diameter_mm: Bar diameter (mm)
    '     hook_angle: Hook angle in degrees (default 90)
    '
    ' Returns:
    '     Hook length (mm)
    
    If diameter_mm <= 0# Then
        BBS_CalculateHookLength = 0#
        Exit Function
    End If
    
    Select Case hook_angle
        Case 180#
            BBS_CalculateHookLength = CDbl(8#) * CDbl(diameter_mm)
        Case 90#
            BBS_CalculateHookLength = CDbl(8#) * CDbl(diameter_mm)
        Case 135#
            BBS_CalculateHookLength = CDbl(6#) * CDbl(diameter_mm)
        Case Else
            BBS_CalculateHookLength = CDbl(8#) * CDbl(diameter_mm)
    End Select
End Function


Public Function BBS_CalculateBendDeduction( _
    ByVal diameter_mm As Double, _
    Optional ByVal bend_angle As Double = 90# _
) As Double
    ' Calculate bend deduction per SP 34.
    '
    ' Bend deductions (approximate):
    ' - 90° bend: 2d
    ' - 135° bend: 3d
    ' - 180° bend: 4d
    '
    ' Args:
    '     diameter_mm: Bar diameter (mm)
    '     bend_angle: Bend angle in degrees (default 90)
    '
    ' Returns:
    '     Bend deduction (mm)
    
    If diameter_mm <= 0# Then
        BBS_CalculateBendDeduction = 0#
        Exit Function
    End If
    
    Select Case bend_angle
        Case 180#
            BBS_CalculateBendDeduction = CDbl(4#) * CDbl(diameter_mm)
        Case 135#
            BBS_CalculateBendDeduction = CDbl(3#) * CDbl(diameter_mm)
        Case 90#
            BBS_CalculateBendDeduction = CDbl(2#) * CDbl(diameter_mm)
        Case 45#
            BBS_CalculateBendDeduction = CDbl(1#) * CDbl(diameter_mm)
        Case Else
            BBS_CalculateBendDeduction = CDbl(2#) * CDbl(diameter_mm)
    End Select
End Function


Public Function BBS_CalculateStraightBarLength( _
    ByVal span_mm As Double, _
    ByVal cover_mm As Double, _
    Optional ByVal hooks As Long = 0, _
    Optional ByVal hook_angle As Double = 90# _
) As Double
    ' Calculate cut length for a straight bar (Shape A).
    '
    ' Args:
    '     span_mm: Span length (mm)
    '     cover_mm: Clear cover (mm)
    '     hooks: Number of hooks (0, 1, or 2)
    '     hook_angle: Hook angle in degrees
    '
    ' Returns:
    '     Cut length (mm), rounded to LENGTH_ROUND_MM
    
    Dim base_length As Double
    Dim hook_length As Double
    Dim total As Double
    
    If span_mm <= 0# Then
        BBS_CalculateStraightBarLength = 0#
        Exit Function
    End If
    
    ' Bar extends from cover to cover (inside faces)
    base_length = CDbl(span_mm) - CDbl(2#) * CDbl(cover_mm)
    
    ' Add hook lengths
    hook_length = CDbl(hooks) * BBS_CalculateHookLength(12#, hook_angle) ' Assume 12mm for hook calc
    
    total = base_length + hook_length
    
    ' Round to nearest LENGTH_ROUND_MM
    BBS_CalculateStraightBarLength = RoundToNearest(total, LENGTH_ROUND_MM)
End Function


Public Function BBS_CalculateStirrupCutLength( _
    ByVal b_mm As Double, _
    ByVal D_mm As Double, _
    ByVal cover_mm As Double, _
    ByVal stirrup_dia_mm As Double, _
    Optional ByVal hook_angle As Double = 135# _
) As Double
    ' Calculate cut length for a closed stirrup (Shape E).
    '
    ' Perimeter = 2 × (b - 2c) + 2 × (D - 2c) + hook + bend deductions
    '
    ' Args:
    '     b_mm: Beam width (mm)
    '     D_mm: Beam depth (mm)
    '     cover_mm: Clear cover to stirrup (mm)
    '     stirrup_dia_mm: Stirrup diameter (mm)
    '     hook_angle: Hook angle in degrees (default 135°)
    '
    ' Returns:
    '     Cut length (mm), rounded to LENGTH_ROUND_MM
    
    Dim inner_width As Double
    Dim inner_depth As Double
    Dim perimeter As Double
    Dim hooks As Double
    Dim bends As Double
    Dim total As Double
    
    If b_mm <= 0# Or D_mm <= 0# Then
        BBS_CalculateStirrupCutLength = 0#
        Exit Function
    End If
    
    ' Inner dimensions (to centerline of stirrup)
    inner_width = CDbl(b_mm) - CDbl(2#) * CDbl(cover_mm)
    inner_depth = CDbl(D_mm) - CDbl(2#) * CDbl(cover_mm)
    
    ' Perimeter (2 widths + 2 depths)
    perimeter = CDbl(2#) * inner_width + CDbl(2#) * inner_depth
    
    ' Add hooks (2 hooks for closed stirrup)
    hooks = CDbl(2#) * BBS_CalculateHookLength(stirrup_dia_mm, hook_angle)
    
    ' Subtract bend deductions (4 corners × 90°)
    bends = CDbl(4#) * BBS_CalculateBendDeduction(stirrup_dia_mm, 90#)
    
    total = perimeter + hooks - bends
    
    ' Round to nearest LENGTH_ROUND_MM
    BBS_CalculateStirrupCutLength = RoundToNearest(total, LENGTH_ROUND_MM)
End Function


' =============================================================================
' Helper Functions
' =============================================================================

Private Function RoundToNearest(ByVal value As Double, ByVal nearest As Double) As Double
    ' Round to nearest multiple.
    If nearest <= 0# Then
        RoundToNearest = value
        Exit Function
    End If
    RoundToNearest = Round(CDbl(value) / CDbl(nearest), 0) * nearest
End Function


' =============================================================================
' BBS Line Item Creation
' =============================================================================

Public Function BBS_CreateLineItem( _
    ByVal bar_mark As String, _
    ByVal member_id As String, _
    ByVal location As String, _
    ByVal zone As String, _
    ByVal shape_code As String, _
    ByVal diameter_mm As Double, _
    ByVal no_of_bars As Long, _
    ByVal cut_length_mm As Double, _
    Optional ByVal remarks As String = "" _
) As BBSLineItem
    ' Create a BBS line item with calculated weights.
    '
    ' Args:
    '     bar_mark: Unique identifier (e.g., "A1")
    '     member_id: Beam/element ID
    '     location: "bottom", "top", "stirrup"
    '     zone: "start", "mid", "end", "full"
    '     shape_code: Shape per IS 2502
    '     diameter_mm: Bar diameter (mm)
    '     no_of_bars: Quantity
    '     cut_length_mm: Cut length per bar (mm)
    '     remarks: Optional remarks
    '
    ' Returns:
    '     BBSLineItem with all fields populated
    
    Dim item As BBSLineItem
    
    item.bar_mark = bar_mark
    item.member_id = member_id
    item.location = location
    item.zone = zone
    item.shape_code = shape_code
    item.diameter_mm = diameter_mm
    item.no_of_bars = no_of_bars
    item.cut_length_mm = RoundToNearest(cut_length_mm, LENGTH_ROUND_MM)
    item.total_length_mm = CDbl(no_of_bars) * item.cut_length_mm
    item.unit_weight_kg = BBS_CalculateBarWeight(diameter_mm, item.cut_length_mm)
    item.total_weight_kg = CDbl(no_of_bars) * item.unit_weight_kg
    item.remarks = remarks
    
    BBS_CreateLineItem = item
End Function


' =============================================================================
' BBS Summary Calculation
' =============================================================================

Public Function BBS_CalculateSummary( _
    ByRef items() As BBSLineItem, _
    ByVal member_id As String _
) As BBSSummary
    ' Calculate summary totals for a set of BBS line items.
    '
    ' Args:
    '     items: Array of BBSLineItem
    '     member_id: Member identifier for summary
    '
    ' Returns:
    '     BBSSummary with totals
    
    Dim summary As BBSSummary
    Dim i As Long
    Dim lowerBound As Long
    Dim upperBound As Long
    
    summary.member_id = member_id
    summary.total_items = 0
    summary.total_bars = 0
    summary.total_length_m = 0#
    summary.total_weight_kg = 0#
    
    ' Handle empty array
    On Error Resume Next
    lowerBound = LBound(items)
    upperBound = UBound(items)
    If Err.Number <> 0 Then
        On Error GoTo 0
        BBS_CalculateSummary = summary
        Exit Function
    End If
    On Error GoTo 0
    
    summary.total_items = upperBound - lowerBound + 1
    
    For i = lowerBound To upperBound
        summary.total_bars = summary.total_bars + items(i).no_of_bars
        summary.total_length_m = summary.total_length_m + CDbl(items(i).total_length_mm) / 1000#
        summary.total_weight_kg = summary.total_weight_kg + items(i).total_weight_kg
    Next i
    
    ' Round totals
    summary.total_length_m = Round(summary.total_length_m, 2)
    summary.total_weight_kg = Round(summary.total_weight_kg, 2)
    
    BBS_CalculateSummary = summary
End Function


' =============================================================================
' UDF Wrappers (for Excel)
' =============================================================================

Public Function IS456_BarWeight( _
    ByVal diameter_mm As Double, _
    ByVal length_mm As Double _
) As Double
    ' Excel UDF: Calculate bar weight.
    ' Returns weight in kg.
    IS456_BarWeight = BBS_CalculateBarWeight(diameter_mm, length_mm)
End Function


Public Function IS456_UnitWeight(ByVal diameter_mm As Double) As Double
    ' Excel UDF: Get unit weight per meter.
    ' Returns weight in kg/m.
    IS456_UnitWeight = BBS_UnitWeightPerMeter(diameter_mm)
End Function


Public Function IS456_StirrupCutLength( _
    ByVal b_mm As Double, _
    ByVal D_mm As Double, _
    ByVal cover_mm As Double, _
    ByVal stirrup_dia_mm As Double _
) As Double
    ' Excel UDF: Calculate stirrup cut length.
    ' Returns length in mm.
    IS456_StirrupCutLength = BBS_CalculateStirrupCutLength(b_mm, D_mm, cover_mm, stirrup_dia_mm)
End Function


Public Function IS456_HookLength( _
    ByVal diameter_mm As Double, _
    Optional ByVal hook_angle As Double = 90# _
) As Double
    ' Excel UDF: Calculate hook length.
    ' Returns length in mm.
    IS456_HookLength = BBS_CalculateHookLength(diameter_mm, hook_angle)
End Function
