# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Hypothesis strategies for structural engineering property-based tests.

This module provides reusable strategies for generating valid inputs
to IS 456 structural design functions. Strategies are designed to:
1. Respect physical constraints (positive dimensions, valid material grades)
2. Cover realistic engineering ranges (not just extreme edge cases)
3. Generate dependent values correctly (e.g., d < D for effective depth)

Usage:
    from tests.property.strategies import beam_section, concrete_grade, steel_grade

    @given(section=beam_section(), fck=concrete_grade(), fy=steel_grade())
    def test_design_property(section, fck, fy):
        ...
"""

from hypothesis import strategies as st

# =============================================================================
# MATERIAL STRATEGIES
# =============================================================================

# Standard IS 456 concrete grades (N/mm²)
# Table 2: M15 to M80 (M15/M20 common, M25-M40 typical, M50+ high-strength)
CONCRETE_GRADES = [15, 20, 25, 30, 35, 40, 50, 60, 70, 80]

# Standard IS 456 steel grades (N/mm²)
# Fe250 (mild steel), Fe415/Fe500/Fe550 (HYSD bars)
STEEL_GRADES = [250, 415, 500, 550]

# Common bar diameters (mm) per IS 1786
BAR_DIAMETERS = [6, 8, 10, 12, 16, 20, 25, 32, 40]


def concrete_grade() -> st.SearchStrategy[int]:
    """Strategy for valid IS 456 concrete grades (fck in N/mm²)."""
    return st.sampled_from(CONCRETE_GRADES)


def steel_grade() -> st.SearchStrategy[int]:
    """Strategy for valid IS 456 steel grades (fy in N/mm²)."""
    return st.sampled_from(STEEL_GRADES)


def bar_diameter() -> st.SearchStrategy[int]:
    """Strategy for standard reinforcement bar diameters (mm)."""
    return st.sampled_from(BAR_DIAMETERS)


def concrete_grade_float() -> st.SearchStrategy[float]:
    """
    Strategy for concrete grade as float, including interpolation values.
    Useful for testing table interpolation logic.
    """
    return st.floats(
        min_value=15.0, max_value=80.0, allow_nan=False, allow_infinity=False
    )


def steel_grade_float() -> st.SearchStrategy[float]:
    """
    Strategy for steel grade as float.
    Useful for testing formula-based calculations.
    """
    return st.floats(
        min_value=250.0, max_value=600.0, allow_nan=False, allow_infinity=False
    )


# =============================================================================
# DIMENSION STRATEGIES
# =============================================================================


def beam_width() -> st.SearchStrategy[float]:
    """
    Strategy for beam width (b) in mm.
    Range: 150-1000mm (typical RC beams)
    """
    return st.floats(
        min_value=150.0, max_value=1000.0, allow_nan=False, allow_infinity=False
    )


def beam_width_narrow() -> st.SearchStrategy[float]:
    """
    Strategy for narrow beam width (b < 200mm) for testing ductile failures.
    IS 13920 Cl 6.1.1 requires b >= 200mm, so this generates invalid widths.
    """
    return st.floats(
        min_value=100.0, max_value=199.9, allow_nan=False, allow_infinity=False
    )


def beam_width_ductile() -> st.SearchStrategy[float]:
    """
    Strategy for ductile beam width (b) in mm.
    IS 13920 Cl 6.1.1: b >= 200mm
    """
    return st.floats(
        min_value=200.0, max_value=1000.0, allow_nan=False, allow_infinity=False
    )


def total_depth() -> st.SearchStrategy[float]:
    """
    Strategy for total beam depth (D) in mm.
    Range: 300-1800mm (typical RC beams)
    """
    return st.floats(
        min_value=300.0, max_value=1800.0, allow_nan=False, allow_infinity=False
    )


def effective_depth() -> st.SearchStrategy[float]:
    """
    Strategy for effective depth (d) in mm.
    Range: 200-1700mm (d < D always)
    """
    return st.floats(
        min_value=200.0, max_value=1700.0, allow_nan=False, allow_infinity=False
    )


def cover() -> st.SearchStrategy[float]:
    """
    Strategy for concrete cover in mm.
    Range: 25-75mm (IS 456 Table 16)
    """
    return st.floats(
        min_value=25.0, max_value=75.0, allow_nan=False, allow_infinity=False
    )


# =============================================================================
# COMPOSITE STRATEGIES (Dependent Values)
# =============================================================================


@st.composite
def beam_section(draw: st.DrawFn) -> dict[str, float]:
    """
    Generate a valid beam section with consistent dimensions.

    Ensures: d < D (effective depth < total depth)
    Returns: {"b": width, "D": total_depth, "d": effective_depth}
    """
    b = draw(beam_width())
    D = draw(
        st.floats(
            min_value=300.0, max_value=1800.0, allow_nan=False, allow_infinity=False
        )
    )
    # Effective depth is typically D - cover - bar_dia/2
    # Use 85-95% of D as realistic range
    d = draw(
        st.floats(
            min_value=D * 0.80,
            max_value=D * 0.95,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    return {"b": b, "D": D, "d": d}


@st.composite
def ductile_beam_section(draw: st.DrawFn) -> dict[str, float]:
    """
    Generate a beam section valid for IS 13920 ductile detailing.

    Ensures:
    - b >= 200mm (Cl 6.1.1)
    - b/D >= 0.3 (Cl 6.1.2)
    - d < D
    """
    b = draw(beam_width_ductile())
    # D must satisfy b/D >= 0.3, so D <= b/0.3
    depth_max = min(b / 0.3, 1800.0)
    depth_min = max(300.0, b * 0.3)  # Ensure reasonable minimum
    if depth_max < depth_min:
        depth_max = depth_min + 100  # Fallback for edge cases
    depth_total = draw(
        st.floats(
            min_value=depth_min,
            max_value=depth_max,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    d = draw(
        st.floats(
            min_value=depth_total * 0.80,
            max_value=depth_total * 0.95,
            allow_nan=False,
            allow_infinity=False,
        )
    )
    return {"b": b, "D": depth_total, "d": d}


@st.composite
def flexure_inputs(draw: st.DrawFn) -> dict[str, float]:
    """
    Generate complete inputs for flexure design.

    Returns: {"b", "d", "D", "fck", "fy", "mu_ratio"}
    mu_ratio is 0.1-0.9 of Mu_lim (for under-reinforced design)
    """
    section = draw(beam_section())
    fck = float(draw(concrete_grade()))
    fy = float(draw(steel_grade()))
    # Moment as ratio of Mu_lim (to ensure under-reinforced for most tests)
    mu_ratio = draw(
        st.floats(min_value=0.1, max_value=0.9, allow_nan=False, allow_infinity=False)
    )
    return {
        "b": section["b"],
        "d": section["d"],
        "D": section["D"],
        "fck": fck,
        "fy": fy,
        "mu_ratio": mu_ratio,
    }


@st.composite
def shear_inputs(draw: st.DrawFn) -> dict[str, float]:
    """
    Generate complete inputs for shear design.

    Returns: {"b", "d", "fck", "fy", "vu_kn", "asv", "pt"}
    """
    section = draw(beam_section())
    fck = float(draw(concrete_grade()))
    fy = float(draw(steel_grade()))
    # Shear force: 10-500 kN typical range
    vu_kn = draw(
        st.floats(
            min_value=10.0, max_value=500.0, allow_nan=False, allow_infinity=False
        )
    )
    # Stirrup area: 2-legged 8mm to 4-legged 12mm
    asv = draw(
        st.floats(
            min_value=50.0, max_value=500.0, allow_nan=False, allow_infinity=False
        )
    )
    # Tension steel percentage: 0.15% to 3%
    pt = draw(
        st.floats(min_value=0.15, max_value=3.0, allow_nan=False, allow_infinity=False)
    )
    return {
        "b": section["b"],
        "d": section["d"],
        "fck": fck,
        "fy": fy,
        "vu_kn": vu_kn,
        "asv": asv,
        "pt": pt,
    }


@st.composite
def ductile_inputs(draw: st.DrawFn) -> dict[str, float]:
    """
    Generate complete inputs for ductile detailing checks.

    Returns: {"b", "D", "d", "fck", "fy", "min_bar_dia"}
    """
    section = draw(ductile_beam_section())
    fck = float(draw(concrete_grade()))
    fy = float(draw(steel_grade()))
    min_bar_dia = float(draw(bar_diameter()))
    return {
        "b": section["b"],
        "D": section["D"],
        "d": section["d"],
        "fck": fck,
        "fy": fy,
        "min_bar_dia": min_bar_dia,
    }


# =============================================================================
# FORCE/MOMENT STRATEGIES
# =============================================================================


def moment_knm() -> st.SearchStrategy[float]:
    """
    Strategy for bending moment in kN·m.
    Range: 1-2000 kN·m (typical beam moments)
    """
    return st.floats(
        min_value=1.0, max_value=2000.0, allow_nan=False, allow_infinity=False
    )


def shear_kn() -> st.SearchStrategy[float]:
    """
    Strategy for shear force in kN.
    Range: 1-1000 kN (typical beam shears)
    """
    return st.floats(
        min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False
    )


# =============================================================================
# PERCENTAGE STRATEGIES
# =============================================================================


def steel_percentage() -> st.SearchStrategy[float]:
    """
    Strategy for steel percentage (pt).
    Range: 0.15% to 4% (IS 456 limits)
    """
    return st.floats(
        min_value=0.15, max_value=4.0, allow_nan=False, allow_infinity=False
    )


def steel_percentage_table() -> st.SearchStrategy[float]:
    """
    Strategy for steel percentage for Table 19 lookup.
    Range: 0.15% to 3% (table range)
    """
    return st.floats(
        min_value=0.15, max_value=3.0, allow_nan=False, allow_infinity=False
    )
