# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Excel UDF Bridge - Exposes structural_lib functions to Excel via xlwings

This module acts as a bridge between Excel and the Python structural_lib.
Functions decorated with @xw.func become User-Defined Functions (UDFs) in Excel.

Usage in Excel:
    =IS456_MuLim(300, 450, 25, 500)  -> Returns limiting moment
    =IS456_AstRequired(300, 450, 120, 25, 500)  -> Returns required steel area

Setup:
    1. Install xlwings: pip install xlwings
    2. Install Excel add-in: xlwings addin install
    3. Open Excel, enable xlwings add-in
    4. Use functions in formulas
"""

from __future__ import annotations

import xlwings as xw

# Import existing Python modules (already tested!)
from structural_lib import detailing, flexure, shear

# ============================================================================
# FLEXURE UDFs (IS 456:2000)
# ============================================================================


@xw.func
@xw.arg("b", doc="Beam width (mm)")
@xw.arg("d", doc="Effective depth (mm)")
@xw.arg("fck", doc="Concrete grade (N/mm²)")
@xw.arg("fy", doc="Steel grade (N/mm²)")
@xw.ret(doc="Limiting moment of resistance (kN·m)")
def IS456_MuLim(b: float, d: float, fck: float, fy: float) -> float | str:
    """
    Calculate limiting moment of resistance for singly reinforced beam.

    This function reuses the tested Python implementation from
    structural_lib.calculations.is456.flexure.

    Example in Excel:
        =IS456_MuLim(300, 450, 25, 500)  -> Returns ~230.5 kN·m
    """
    try:
        # Use the actual function from flexure module
        result = flexure.calculate_mu_lim(b, d, fck, fy)
        return round(result, 2)
    except Exception as e:
        return f"Error: {str(e)}"


@xw.func
@xw.arg("b", doc="Beam width (mm)")
@xw.arg("d", doc="Effective depth (mm)")
@xw.arg("mu", doc="Factored moment (kN·m)")
@xw.arg("fck", doc="Concrete grade (N/mm²)")
@xw.arg("fy", doc="Steel grade (N/mm²)")
@xw.ret(doc="Required tension steel area (mm²) or error message")
def IS456_AstRequired(
    b: float, d: float, mu: float, fck: float, fy: float
) -> float | str:
    """
    Calculate required tension steel area for flexure.

    Returns:
        - Float: Required Ast in mm² if singly reinforced
        - String: "Over-Reinforced" if Mu > Mu_lim (needs compression steel)
        - String: "Error: ..." if invalid inputs

    Example in Excel:
        =IS456_AstRequired(300, 450, 120, 25, 500)  -> Returns ~850 mm²
        =IS456_AstRequired(300, 450, 300, 25, 500)  -> Returns "Over-Reinforced"
    """
    try:
        # Check if over-reinforced
        mu_lim = flexure.calculate_mu_lim(b, d, fck, fy)

        if mu > mu_lim:
            return "Over-Reinforced"

        # Calculate required steel
        ast = flexure.calculate_ast_required(b, d, mu, fck, fy)

        if ast < 0:  # Returns -1 if over-reinforced
            return "Over-Reinforced"

        return round(ast, 2)

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# SHEAR UDFs (IS 456:2000)
# ============================================================================


@xw.func
@xw.arg("vu", doc="Factored shear force (kN)")
@xw.arg("b", doc="Beam width (mm)")
@xw.arg("d", doc="Effective depth (mm)")
@xw.arg("fck", doc="Concrete grade (N/mm²)")
@xw.arg("fy", doc="Steel grade (N/mm²)")
@xw.arg("dia_stirrup", doc="Stirrup diameter (mm)")
@xw.arg("pt", doc="Tension steel percentage (%)")
@xw.ret(doc="Required stirrup spacing (mm)")
def IS456_ShearSpacing(
    vu: float, b: float, d: float, fck: float, fy: float, dia_stirrup: float, pt: float
) -> float | str:
    """
    Calculate required stirrup spacing for shear.

    Example in Excel:
        =IS456_ShearSpacing(120, 300, 450, 25, 500, 8, 0.5)  -> Returns spacing in mm
    """
    try:
        # Calculate Asv for given stirrup diameter (2 legs)
        import math

        asv = 2 * math.pi * (dia_stirrup / 2) ** 2

        result = shear.design_shear(vu, b, d, fck, fy, asv, pt)

        if not result.is_safe:
            return "Shear Failure"

        return round(result.spacing, 0)

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# DETAILING HELPERS
# ============================================================================


@xw.func
@xw.arg("num_bars", doc="Number of bars")
@xw.arg("dia", doc="Bar diameter (mm)")
@xw.ret(doc='Bar callout string (e.g., "5-16φ")')
def IS456_BarCallout(num_bars: int, dia: int) -> str:
    """
    Generate bar callout string.

    Example in Excel:
        =IS456_BarCallout(5, 16)  -> Returns "5-16φ"
    """
    return detailing.format_bar_callout(num_bars, dia)


@xw.func
@xw.arg("legs", doc="Number of stirrup legs (2 or 4)")
@xw.arg("dia", doc="Stirrup diameter (mm)")
@xw.arg("spacing", doc="Spacing (mm)")
@xw.ret(doc='Stirrup callout string (e.g., "2L-8φ@150")')
def IS456_StirrupCallout(legs: int, dia: int, spacing: int) -> str:
    """
    Generate stirrup callout string.

    Example in Excel:
        =IS456_StirrupCallout(2, 8, 150)  -> Returns "2L-8φ@150"
    """
    return detailing.format_stirrup_callout(legs, dia, spacing)


@xw.func
@xw.arg("dia", doc="Bar diameter (mm)")
@xw.arg("fck", doc="Concrete grade (N/mm²)")
@xw.arg("fy", doc="Steel grade (N/mm²)")
@xw.ret(doc="Development length (mm)")
def IS456_Ld(dia: float, fck: float, fy: float) -> float | str:
    """
    Calculate development length (IS 456:2000 Cl 26.2.1).

    Example in Excel:
        =IS456_Ld(16, 25, 500)  -> Returns development length in mm
    """
    try:
        result = detailing.calculate_development_length(dia, fck, fy)
        return round(result, 0)

    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# MACRO FUNCTIONS (called by Excel buttons, not formulas)
# ============================================================================


@xw.sub
def create_design_sheet() -> None:
    """
    Create a Design sheet with headers and formulas.

    Call this from a button macro in Excel:
        Sub CreateDesignSheet()
            RunPython "import structural_lib.excel_bridge; structural_lib.excel_bridge.create_design_sheet()"
        End Sub
    """
    wb = xw.Book.caller()

    # Check if sheet exists
    sheet_names = [s.name for s in wb.sheets]
    if "Design" in sheet_names:
        # Sheet exists - xlwings will auto-name as Design1, Design2, etc.
        pass

    # Create new sheet
    ws = wb.sheets.add("Design")

    # Headers (row 1)
    headers = [
        "BeamID",
        "b (mm)",
        "D (mm)",
        "d (mm)",
        "fck",
        "fy",
        "Mu (kN·m)",
        "Vu (kN)",
        "Cover (mm)",
        "Mu_lim (kN·m)",
        "Ast (mm²)",
        "Bar Count",
        "Bar Callout",
        "Stirrup Spacing (mm)",
        "Stirrup Callout",
        "Ld (mm)",
        "Status",
    ]

    ws.range("A1").value = headers

    # Format headers (dark blue background, white text)
    header_range = ws.range("A1:Q1")
    header_range.color = (0, 32, 96)
    header_range.api.Font.Color = 0xFFFFFF
    header_range.api.Font.Bold = True

    # Formulas (row 2) - These call the Python UDFs defined above!
    formulas = {
        "J2": "=IS456_MuLim(B2,D2,E2,F2)",
        "K2": "=IS456_AstRequired(B2,D2,G2,E2,F2)",
        "L2": '=IF(ISNUMBER(K2),CEILING(K2/201,1),"")',
        "M2": '=IF(ISNUMBER(L2),IS456_BarCallout(L2,16),"")',
        "N2": "=IS456_ShearSpacing(H2,B2,D2,E2,F2,8,K2*100/(B2*D2))",
        "O2": '=IF(ISNUMBER(N2),IS456_StirrupCallout(2,8,FLOOR(N2/25,1)*25),"")',
        "P2": "=IS456_Ld(16,E2,F2)",
        "Q2": '=IF(AND(ISNUMBER(K2),G2<=J2),"Safe","Check")',
    }

    for cell, formula in formulas.items():
        ws.range(cell).formula = formula

    # Copy formulas down to row 51
    ws.range("J2:Q2").api.Copy()
    ws.range("J3:Q51").api.PasteSpecial(-4163)  # xlPasteFormulas

    # Add sample data (first beam)
    sample_data = ["B1", 300, 500, 450, 25, 500, 120, 80, 40]
    ws.range("A2").value = sample_data

    print("✅ Design sheet created successfully!")


if __name__ == "__main__":
    # Test imports (ensures all dependencies are available)
    print("Testing excel_bridge imports...")
    print(f"✅ IS456_MuLim(300, 450, 25, 500) = {IS456_MuLim(300, 450, 25, 500)} kN·m")
    print(
        f"✅ IS456_AstRequired(300, 450, 120, 25, 500) = {IS456_AstRequired(300, 450, 120, 25, 500)} mm²"
    )
    print(f"✅ IS456_BarCallout(5, 16) = {IS456_BarCallout(5, 16)}")
    print("All functions imported successfully!")
