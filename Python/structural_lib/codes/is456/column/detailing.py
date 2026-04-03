# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       detailing
Description:  Column detailing checks per IS 456:2000 Cl 26.5.3.
Traceability: Functions are decorated with @clause for IS 456 clause references.

Implements:
- Longitudinal reinforcement limits (Cl 26.5.3.1a)
- Minimum bar count and diameter (Cl 26.5.3.1b)
- Bar spacing checks (Cl 26.5.3.1c)
- Lateral tie diameter (Cl 26.5.3.2a)
- Lateral tie spacing (Cl 26.5.3.2b)
- Cross-tie requirements (Cl 26.5.3.2c)

References:
    IS 456:2000, Cl. 26.5.3
    SP:16:1980 Design Aids for Reinforced Concrete
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13
"""

from __future__ import annotations

import math

from structural_lib.codes.is456.common.constants import (
    COLUMN_MAX_STEEL_RATIO,
    COLUMN_MIN_STEEL_RATIO,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import ColumnDetailingResult
from structural_lib.core.errors import DimensionError

__all__ = [
    "calculate_tie_diameter",
    "calculate_tie_spacing",
    "check_bar_spacing",
    "check_longitudinal_limits",
    "check_min_bar_diameter",
    "create_column_detailing",
    "get_min_bar_count",
    "needs_cross_ties",
]

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.1(a): Steel ratio at lap sections
# ---------------------------------------------------------------------------
_MAX_STEEL_RATIO_LAP: float = 0.06  # 6% of Ag at lap sections

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.1(b): Minimum bar requirements
# ---------------------------------------------------------------------------
_MIN_BAR_DIA_MM: float = 12.0
_MIN_BARS_RECTANGULAR: int = 4
_MIN_BARS_CIRCULAR: int = 6

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.2(a): Minimum tie diameter
# ---------------------------------------------------------------------------
_MIN_TIE_DIA_MM: float = 6.0
_TIE_DIA_FRACTION: float = 4.0  # tie_dia >= max_long_bar_dia / 4

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.2(b): Maximum tie spacing
# ---------------------------------------------------------------------------
_MAX_TIE_SPACING_MM: float = 300.0
_TIE_SPACING_BAR_FACTOR: float = 16.0  # 16 × smallest longitudinal bar dia

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.2(c): Cross-tie threshold
# ---------------------------------------------------------------------------
_CROSS_TIE_THRESHOLD_MM: float = 150.0

# ---------------------------------------------------------------------------
# IS 456 Cl 26.5.3.1(c): Maximum clear spacing between bars
# ---------------------------------------------------------------------------
_MAX_BAR_SPACING_MM: float = 300.0

# ---------------------------------------------------------------------------
# Standard tie bar diameters available (mm)
# ---------------------------------------------------------------------------
_STANDARD_TIE_DIAMETERS: tuple[float, ...] = (6.0, 8.0, 10.0, 12.0, 16.0)


def check_longitudinal_limits(
    Ag_mm2: float,
    Asc_mm2: float,
    at_lap_section: bool = False,
) -> tuple[float, bool, bool, tuple[str, ...]]:
    """Check longitudinal steel ratio limits per IS 456 Cl 26.5.3.1(a).

    Args:
        Ag_mm2: Gross cross-sectional area (mm²). Must be > 0.
        Asc_mm2: Total area of longitudinal steel (mm²). Must be >= 0.
        at_lap_section: True if checking at a lap/splice section.

    Returns:
        Tuple of (ratio, is_min_ok, is_max_ok, warnings).

    Raises:
        DimensionError: If Ag_mm2 <= 0 or Asc_mm2 < 0.
    """
    if Ag_mm2 <= 0:
        raise DimensionError(
            f"Gross area Ag_mm2 must be > 0, got {Ag_mm2}",
            details={"Ag_mm2": Ag_mm2},
            clause_ref="Cl. 26.5.3.1",
        )
    if Asc_mm2 < 0:
        raise DimensionError(
            f"Steel area Asc_mm2 must be >= 0, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 26.5.3.1",
        )

    warnings: list[str] = []

    # IS 456 Cl 26.5.3.1(a): ratio = Asc / Ag
    ratio = Asc_mm2 / Ag_mm2

    # IS 456 Cl 26.5.3.1(a): min ratio = 0.8% = 0.008
    is_min_ok = ratio >= COLUMN_MIN_STEEL_RATIO
    if not is_min_ok:
        warnings.append(
            f"Steel ratio {ratio:.4f} is below minimum "
            f"{COLUMN_MIN_STEEL_RATIO} (0.8%) per Cl 26.5.3.1(a)"
        )

    # IS 456 Cl 26.5.3.1(a): max ratio depends on lap section
    max_ratio = _MAX_STEEL_RATIO_LAP if at_lap_section else COLUMN_MAX_STEEL_RATIO
    is_max_ok = ratio <= max_ratio

    if not is_max_ok:
        warnings.append(
            f"Steel ratio {ratio:.4f} exceeds maximum "
            f"{max_ratio} ({max_ratio * 100:.0f}%) per Cl 26.5.3.1(a)"
        )
    elif at_lap_section and ratio > COLUMN_MAX_STEEL_RATIO:
        # Between 4% and 6% at lap section — warn but allowed
        warnings.append(
            f"Steel ratio {ratio:.4f} exceeds general limit of "
            f"{COLUMN_MAX_STEEL_RATIO} (4%) but is within lap section "
            f"limit of {_MAX_STEEL_RATIO_LAP} (6%) per Cl 26.5.3.1(a)"
        )

    return (ratio, is_min_ok, is_max_ok, tuple(warnings))


def get_min_bar_count(is_circular: bool = False) -> int:
    """Return minimum number of longitudinal bars per IS 456 Cl 26.5.3.1(b).

    Args:
        is_circular: True for circular columns.

    Returns:
        Minimum bar count: 6 for circular, 4 for rectangular.
    """
    # IS 456 Cl 26.5.3.1(b): min 4 bars (rectangular), 6 bars (circular)
    return _MIN_BARS_CIRCULAR if is_circular else _MIN_BARS_RECTANGULAR


def check_min_bar_diameter(bar_dia_mm: float) -> bool:
    """Check if bar diameter meets minimum per IS 456 Cl 26.5.3.1(b).

    Args:
        bar_dia_mm: Longitudinal bar diameter (mm).

    Returns:
        True if bar_dia_mm >= 12mm.
    """
    # IS 456 Cl 26.5.3.1(b): minimum diameter = 12mm
    return bar_dia_mm >= _MIN_BAR_DIA_MM


def calculate_tie_diameter(max_long_bar_dia_mm: float) -> float:
    """Calculate required lateral tie diameter per IS 456 Cl 26.5.3.2(a).

    Tie diameter >= max(largest_longitudinal_bar / 4, 6mm),
    rounded up to the nearest standard bar size.

    Args:
        max_long_bar_dia_mm: Diameter of the largest longitudinal bar (mm).
            Must be > 0.

    Returns:
        Required tie diameter (mm), rounded up to standard size.

    Raises:
        DimensionError: If max_long_bar_dia_mm <= 0.
    """
    if max_long_bar_dia_mm <= 0:
        raise DimensionError(
            f"Longitudinal bar diameter must be > 0, got {max_long_bar_dia_mm}",
            details={"max_long_bar_dia_mm": max_long_bar_dia_mm},
            clause_ref="Cl. 26.5.3.2",
        )

    # IS 456 Cl 26.5.3.2(a): tie_dia >= max(bar_dia / 4, 6mm)
    min_tie_dia = max(max_long_bar_dia_mm / _TIE_DIA_FRACTION, _MIN_TIE_DIA_MM)

    # Round up to nearest standard tie diameter
    for std_dia in _STANDARD_TIE_DIAMETERS:
        if std_dia >= min_tie_dia:
            return std_dia

    # If larger than all standard sizes, return the computed value
    return math.ceil(min_tie_dia)


def calculate_tie_spacing(
    b_mm: float,
    D_mm: float,
    smallest_long_bar_dia_mm: float,
) -> float:
    """Calculate maximum lateral tie spacing per IS 456 Cl 26.5.3.2(b).

    Spacing <= min(least lateral dimension, 16 × smallest bar dia, 300mm).
    NOTE: Uses the SMALLEST longitudinal bar diameter, not the largest.

    Args:
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        smallest_long_bar_dia_mm: Diameter of the smallest longitudinal bar (mm).
            Must be > 0.

    Returns:
        Maximum permissible tie spacing (mm).

    Raises:
        DimensionError: If any dimension <= 0.
    """
    if b_mm <= 0:
        raise DimensionError(
            f"Column width b_mm must be > 0, got {b_mm}",
            details={"b_mm": b_mm},
            clause_ref="Cl. 26.5.3.2",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column depth D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 26.5.3.2",
        )
    if smallest_long_bar_dia_mm <= 0:
        raise DimensionError(
            f"Smallest bar diameter must be > 0, got {smallest_long_bar_dia_mm}",
            details={"smallest_long_bar_dia_mm": smallest_long_bar_dia_mm},
            clause_ref="Cl. 26.5.3.2",
        )

    # IS 456 Cl 26.5.3.2(b): least lateral dimension
    least_lateral_dim = min(b_mm, D_mm)

    # IS 456 Cl 26.5.3.2(b): 16 × smallest longitudinal bar diameter
    bar_spacing_limit = _TIE_SPACING_BAR_FACTOR * smallest_long_bar_dia_mm

    # IS 456 Cl 26.5.3.2(b): spacing <= min(least dim, 16 × dia, 300mm)
    return min(least_lateral_dim, bar_spacing_limit, _MAX_TIE_SPACING_MM)


def check_bar_spacing(
    b_mm: float,
    D_mm: float,
    cover_mm: float,
    bar_dia_mm: float,
    num_bars: int,
    is_circular: bool = False,
) -> tuple[float, bool, tuple[str, ...]]:
    """Check clear spacing between longitudinal bars per IS 456 Cl 26.5.3.1(c).

    For rectangular sections, distributes bars evenly around the perimeter.
    Maximum face-to-face spacing must not exceed 300mm.

    Args:
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        cover_mm: Clear cover (mm). Must be >= 0.
        bar_dia_mm: Longitudinal bar diameter (mm). Must be > 0.
        num_bars: Number of longitudinal bars. Must be >= 1.
        is_circular: True for circular columns.

    Returns:
        Tuple of (min_clear_spacing_mm, is_ok, warnings).

    Raises:
        DimensionError: If dimensions are invalid.
    """
    if b_mm <= 0 or D_mm <= 0:
        raise DimensionError(
            f"Column dimensions must be > 0, got b={b_mm}, D={D_mm}",
            details={"b_mm": b_mm, "D_mm": D_mm},
            clause_ref="Cl. 26.5.3.1",
        )
    if cover_mm < 0:
        raise DimensionError(
            f"Cover must be >= 0, got {cover_mm}",
            details={"cover_mm": cover_mm},
            clause_ref="Cl. 26.5.3.1",
        )
    if bar_dia_mm <= 0:
        raise DimensionError(
            f"Bar diameter must be > 0, got {bar_dia_mm}",
            details={"bar_dia_mm": bar_dia_mm},
            clause_ref="Cl. 26.5.3.1",
        )
    if num_bars < 1:
        raise DimensionError(
            f"Number of bars must be >= 1, got {num_bars}",
            details={"num_bars": num_bars},
            clause_ref="Cl. 26.5.3.1",
        )

    warnings: list[str] = []

    if is_circular:
        # Circular column: bars distributed uniformly around a circle
        # Effective perimeter diameter = D - 2 * cover - bar_dia
        effective_dia = D_mm - 2.0 * cover_mm - bar_dia_mm
        if effective_dia <= 0:
            return (0.0, False, ("Insufficient section size for bars and cover",))

        # IS 456 Cl 26.5.3.1(c): arc spacing between bars
        circumference = math.pi * effective_dia
        # Clear spacing = (circumference - num_bars * bar_dia) / num_bars
        clear_spacing = (circumference - num_bars * bar_dia_mm) / num_bars
    else:
        # Rectangular column: distribute bars around perimeter
        # Available perimeter = 2 * (b - 2*cover - bar_dia) + 2 * (D - 2*cover - bar_dia)
        avail_b = b_mm - 2.0 * cover_mm - bar_dia_mm
        avail_D = D_mm - 2.0 * cover_mm - bar_dia_mm
        if avail_b <= 0 or avail_D <= 0:
            return (0.0, False, ("Insufficient section size for bars and cover",))

        # Perimeter of bar centreline rectangle
        perimeter = 2.0 * (avail_b + avail_D)
        # Clear spacing between bars along the perimeter
        clear_spacing = (perimeter - num_bars * bar_dia_mm) / num_bars

    # NaN/Inf guard
    if math.isnan(clear_spacing) or math.isinf(clear_spacing):
        return (0.0, False, ("Numerical issue in bar spacing calculation",))

    min_clear_spacing = max(clear_spacing, 0.0)

    # IS 456 Cl 26.5.3.1(c): maximum face-to-face spacing <= 300mm
    # For rectangular, check each face: max face spacing ≈ (avail face - corner bars) / gaps
    is_ok = True
    if not is_circular:
        # Check the widest face
        max_face = max(avail_b, avail_D)
        # Conservative: if max face > 300mm, bars on that face must be spaced ≤ 300mm
        if max_face > _MAX_BAR_SPACING_MM:
            # With only corner bars on that face, the clear gap = max_face
            # More bars needed on that face to keep spacing ≤ 300mm
            if clear_spacing > _MAX_BAR_SPACING_MM:
                is_ok = False
                warnings.append(
                    f"Bar spacing {clear_spacing:.1f}mm exceeds maximum "
                    f"{_MAX_BAR_SPACING_MM:.0f}mm per Cl 26.5.3.1(c)"
                )
    else:
        if clear_spacing > _MAX_BAR_SPACING_MM:
            is_ok = False
            warnings.append(
                f"Bar spacing {clear_spacing:.1f}mm exceeds maximum "
                f"{_MAX_BAR_SPACING_MM:.0f}mm per Cl 26.5.3.1(c)"
            )

    if clear_spacing < bar_dia_mm:
        is_ok = False
        warnings.append(
            f"Clear spacing {clear_spacing:.1f}mm is less than bar diameter "
            f"{bar_dia_mm:.0f}mm — bars cannot be placed"
        )

    return (round(min_clear_spacing, 1), is_ok, tuple(warnings))


def needs_cross_ties(
    b_mm: float,
    D_mm: float,
    cover_mm: float,
    bar_dia_mm: float,
    num_bars: int,
) -> bool:
    """Check if cross-ties are needed per IS 456 Cl 26.5.3.2(c).

    Cross-ties are needed when any longitudinal bar is more than 150mm
    from a laterally restrained bar (a bar at a tie corner).

    For rectangular columns, corner bars are always restrained. If the
    spacing between corner bars along any face exceeds 2 × 150mm = 300mm,
    intermediate bars need cross-ties.

    Args:
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        cover_mm: Clear cover (mm). Must be >= 0.
        bar_dia_mm: Longitudinal bar diameter (mm). Must be > 0.
        num_bars: Total number of longitudinal bars. Must be >= 4.

    Returns:
        True if cross-ties are required.
    """
    if num_bars <= 4:
        # 4 corner bars — all restrained by default
        return False

    # Available distance between corner bar centres on each face
    face_b = b_mm - 2.0 * cover_mm - bar_dia_mm
    face_D = D_mm - 2.0 * cover_mm - bar_dia_mm

    # IS 456 Cl 26.5.3.2(c): cross-tie if any bar > 150mm from restrained bar
    # Corner-to-corner distance on each face — if > 2 × 150 = 300mm,
    # intermediate bars exist that are > 150mm from a restrained corner
    threshold = 2.0 * _CROSS_TIE_THRESHOLD_MM

    return face_b > threshold or face_D > threshold


@clause("26.5.3")
def create_column_detailing(
    b_mm: float,
    D_mm: float,
    cover_mm: float,
    fck: float,
    fy: float,
    num_bars: int,
    bar_dia_mm: float,
    tie_dia_mm: float | None = None,
    is_circular: bool = False,
    at_lap_section: bool = False,
) -> ColumnDetailingResult:
    """Assemble all column detailing checks per IS 456 Cl 26.5.3.

    Orchestrates all sub-checks: longitudinal steel limits, bar count,
    bar diameter, bar spacing, tie diameter, tie spacing, and cross-ties.

    Args:
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        cover_mm: Clear cover (mm). Must be >= 0.
        fck: Concrete compressive strength (N/mm²). Not used in detailing
            checks but included for consistency with other column functions.
        fy: Steel yield strength (N/mm²). Not used in detailing checks
            but included for consistency.
        num_bars: Number of longitudinal bars.
        bar_dia_mm: Longitudinal bar diameter (mm).
        tie_dia_mm: Lateral tie diameter (mm). None = auto-compute per Cl 26.5.3.2(a).
        is_circular: True for circular columns.
        at_lap_section: True if checking at a lap/splice section (allows up to 6%).

    Returns:
        ColumnDetailingResult with all check outcomes.

    Raises:
        DimensionError: If geometric dimensions are invalid.

    References:
        IS 456:2000, Cl. 26.5.3
    """
    # ===========================================================
    # 1. Input validation
    # ===========================================================
    if b_mm <= 0:
        raise DimensionError(
            f"Column width b_mm must be > 0, got {b_mm}",
            details={"b_mm": b_mm},
            clause_ref="Cl. 26.5.3",
        )
    if D_mm <= 0:
        raise DimensionError(
            f"Column depth D_mm must be > 0, got {D_mm}",
            details={"D_mm": D_mm},
            clause_ref="Cl. 26.5.3",
        )
    if cover_mm < 0:
        raise DimensionError(
            f"Clear cover must be >= 0, got {cover_mm}",
            details={"cover_mm": cover_mm},
            clause_ref="Cl. 26.5.3",
        )
    if bar_dia_mm <= 0:
        raise DimensionError(
            f"Bar diameter must be > 0, got {bar_dia_mm}",
            details={"bar_dia_mm": bar_dia_mm},
            clause_ref="Cl. 26.5.3",
        )
    if num_bars < 1:
        raise DimensionError(
            f"Number of bars must be >= 1, got {num_bars}",
            details={"num_bars": num_bars},
            clause_ref="Cl. 26.5.3",
        )

    all_warnings: list[str] = []

    # ===========================================================
    # 2. Section properties
    # ===========================================================
    if is_circular:
        # IS 456: Ag = π/4 × D² for circular columns
        Ag_mm2 = math.pi / 4.0 * D_mm * D_mm
    else:
        Ag_mm2 = b_mm * D_mm

    # IS 456: Asc = num_bars × π/4 × bar_dia²
    Asc_provided_mm2 = num_bars * math.pi / 4.0 * bar_dia_mm * bar_dia_mm

    # ===========================================================
    # 3. Longitudinal steel limits (Cl 26.5.3.1a)
    # ===========================================================
    steel_ratio, is_min_ok, is_max_ok, ratio_warnings = check_longitudinal_limits(
        Ag_mm2, Asc_provided_mm2, at_lap_section=at_lap_section
    )
    all_warnings.extend(ratio_warnings)

    # ===========================================================
    # 4. Minimum bar count (Cl 26.5.3.1b)
    # ===========================================================
    min_bars = get_min_bar_count(is_circular)
    min_bars_ok = num_bars >= min_bars
    if not min_bars_ok:
        all_warnings.append(
            f"Number of bars {num_bars} is below minimum "
            f"{min_bars} per Cl 26.5.3.1(b)"
        )

    # ===========================================================
    # 5. Minimum bar diameter (Cl 26.5.3.1b)
    # ===========================================================
    min_bar_dia_ok = check_min_bar_diameter(bar_dia_mm)
    if not min_bar_dia_ok:
        all_warnings.append(
            f"Bar diameter {bar_dia_mm:.0f}mm is below minimum "
            f"{_MIN_BAR_DIA_MM:.0f}mm per Cl 26.5.3.1(b)"
        )

    # ===========================================================
    # 6. Bar spacing (Cl 26.5.3.1c)
    # ===========================================================
    bar_spacing_mm, bar_spacing_ok, spacing_warnings = check_bar_spacing(
        b_mm, D_mm, cover_mm, bar_dia_mm, num_bars, is_circular
    )
    all_warnings.extend(spacing_warnings)

    # ===========================================================
    # 7. Tie diameter (Cl 26.5.3.2a)
    # ===========================================================
    tie_dia_required_mm = calculate_tie_diameter(bar_dia_mm)
    if tie_dia_mm is None:
        tie_dia_mm = tie_dia_required_mm
    tie_dia_ok = tie_dia_mm >= tie_dia_required_mm
    if not tie_dia_ok:
        all_warnings.append(
            f"Provided tie diameter {tie_dia_mm:.0f}mm is below required "
            f"{tie_dia_required_mm:.0f}mm per Cl 26.5.3.2(a)"
        )

    # ===========================================================
    # 8. Tie spacing (Cl 26.5.3.2b)
    # ===========================================================
    # NOTE: uses smallest longitudinal bar diameter (all bars same dia here)
    max_tie_spacing_mm = calculate_tie_spacing(b_mm, D_mm, bar_dia_mm)
    # Default provided spacing = max permissible (conservative)
    tie_spacing_mm = max_tie_spacing_mm
    tie_spacing_ok = tie_spacing_mm <= max_tie_spacing_mm

    # ===========================================================
    # 9. Cross-ties (Cl 26.5.3.2c)
    # ===========================================================
    cross_ties = False
    if not is_circular:
        cross_ties = needs_cross_ties(b_mm, D_mm, cover_mm, bar_dia_mm, num_bars)
        if cross_ties:
            all_warnings.append(
                "Cross-ties required — intermediate bars are > 150mm "
                "from a restrained bar per Cl 26.5.3.2(c)"
            )

    # ===========================================================
    # 10. Overall validity
    # ===========================================================
    is_valid = all(
        [
            is_min_ok,
            is_max_ok,
            min_bars_ok,
            min_bar_dia_ok,
            bar_spacing_ok,
            tie_dia_ok,
            tie_spacing_ok,
        ]
    )

    return ColumnDetailingResult(
        b_mm=b_mm,
        D_mm=D_mm,
        Ag_mm2=round(Ag_mm2, 1),
        num_bars=num_bars,
        bar_dia_mm=bar_dia_mm,
        Asc_provided_mm2=round(Asc_provided_mm2, 1),
        steel_ratio=round(steel_ratio, 6),
        min_steel_ok=is_min_ok,
        max_steel_ok=is_max_ok,
        min_bars_ok=min_bars_ok,
        min_bar_dia_ok=min_bar_dia_ok,
        bar_spacing_mm=bar_spacing_mm,
        bar_spacing_ok=bar_spacing_ok,
        tie_dia_mm=tie_dia_mm,
        tie_dia_required_mm=tie_dia_required_mm,
        tie_spacing_mm=tie_spacing_mm,
        max_tie_spacing_mm=max_tie_spacing_mm,
        tie_spacing_ok=tie_spacing_ok,
        cross_ties_needed=cross_ties,
        is_valid=is_valid,
        clause_ref="Cl. 26.5.3",
        warnings=tuple(all_warnings),
    )
