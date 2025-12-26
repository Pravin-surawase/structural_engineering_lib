"""
Detailing Module — IS 456:2000 / SP 34:1987 Reinforcement Detailing

This module provides pure functions for calculating detailing parameters
required for shop drawings and fabrication.

References:
- IS 456:2000, Cl 26.2 (Development/Anchorage)
- IS 456:2000, Cl 26.3 (Spacing)
- IS 456:2000, Cl 26.5 (Stirrups)
- IS 13920:2016, Cl 6.2.6 (Splice locations for seismic)
- SP 34:1987 (Handbook on Detailing)
"""

from dataclasses import dataclass
from typing import Tuple, List
import math


# =============================================================================
# Constants
# =============================================================================

# Design bond stress (τbd) for deformed bars — IS 456 Table 5.3 (60% increase)
BOND_STRESS_DEFORMED = {
    15: 1.60,  # M15
    20: 1.92,  # M20
    25: 2.24,  # M25
    30: 2.40,  # M30
    35: 2.72,  # M35
    40: 3.04,  # M40
    45: 3.20,  # M45
    50: 3.36,  # M50
}

# Standard bar diameters (mm)
STANDARD_BAR_DIAMETERS = [8, 10, 12, 16, 20, 25, 32]

# Standard stirrup diameters (mm)
STANDARD_STIRRUP_DIAMETERS = [6, 8, 10, 12]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class BarArrangement:
    """Represents a reinforcement bar arrangement."""

    count: int
    diameter: float  # mm
    area_provided: float  # mm²
    spacing: float  # mm (center-to-center)
    layers: int

    def callout(self) -> str:
        """Return standard callout notation (e.g., '3-16φ')."""
        return f"{self.count}-{int(self.diameter)}φ"


@dataclass
class StirrupArrangement:
    """Represents a stirrup arrangement for a zone."""

    diameter: float  # mm
    legs: int
    spacing: float  # mm
    zone_length: float  # mm

    def callout(self) -> str:
        """Return standard callout notation (e.g., '2L-8φ@150')."""
        return f"{self.legs}L-{int(self.diameter)}φ@{int(self.spacing)}"


@dataclass
class BeamDetailingResult:
    """Complete detailing result for a beam section."""

    beam_id: str
    story: str
    b: float  # mm
    D: float  # mm
    span: float  # mm
    cover: float  # mm

    # Reinforcement
    top_bars: List[BarArrangement]  # [start, mid, end]
    bottom_bars: List[BarArrangement]  # [start, mid, end]
    stirrups: List[StirrupArrangement]  # [start, mid, end]

    # Detailing parameters
    ld_tension: float  # Development length for tension bars (mm)
    ld_compression: float  # Development length for compression bars (mm)
    lap_length: float  # Lap splice length (mm)

    # Validity
    is_valid: bool
    remarks: str


# =============================================================================
# Development Length (IS 456 Cl 26.2.1)
# =============================================================================


def get_bond_stress(fck: float, bar_type: str = "deformed") -> float:
    """
    Get design bond stress τbd.

    Args:
        fck: Characteristic compressive strength of concrete (N/mm²)
        bar_type: "plain" or "deformed"

    Returns:
        τbd in N/mm²
    """
    # Use nearest lower grade
    available_grades = sorted(BOND_STRESS_DEFORMED.keys())
    grade = available_grades[0]
    for g in available_grades:
        if g <= fck:
            grade = g
        else:
            break

    tau_bd = BOND_STRESS_DEFORMED[grade]

    if bar_type == "plain":
        tau_bd = tau_bd / 1.6  # Deformed bars have 60% increase

    return tau_bd


def calculate_development_length(
    bar_dia: float,
    fck: float,
    fy: float,
    bar_type: str = "deformed",
    stress_ratio: float = 0.87,
) -> float:
    """
    Calculate development length (Ld) per IS 456 Cl 26.2.1.

    Ld = (φ × σs) / (4 × τbd)

    Args:
        bar_dia: Bar diameter φ (mm)
        fck: Concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        bar_type: "plain" or "deformed"
        stress_ratio: σs/fy ratio (default 0.87 for limit state)

    Returns:
        Development length Ld (mm). Returns 0 if inputs are invalid.
    """
    if bar_dia <= 0 or fck <= 0 or fy <= 0:
        return 0.0

    sigma_s = stress_ratio * fy
    tau_bd = get_bond_stress(fck, bar_type)

    if tau_bd <= 0:
        return 0.0

    ld = (bar_dia * sigma_s) / (4 * tau_bd)

    return round(ld, 0)


def calculate_lap_length(
    bar_dia: float,
    fck: float,
    fy: float,
    bar_type: str = "deformed",
    splice_percent: float = 50.0,
    is_seismic: bool = False,
    in_tension: bool = True,
) -> float:
    """
    Calculate lap splice length per IS 456 Cl 26.2.5.

    Args:
        bar_dia: Bar diameter (mm)
        fck: Concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        bar_type: "plain" or "deformed"
        splice_percent: Percentage of bars spliced at section
        is_seismic: If True, use IS 13920 requirements (1.5×Ld)
        in_tension: If True, tension splice; else compression splice

    Returns:
        Lap length (mm)
    """
    ld = calculate_development_length(bar_dia, fck, fy, bar_type)

    if not in_tension:
        # Compression lap = Ld
        return round(ld, 0)

    # Tension lap with enhancement factor
    if is_seismic:
        alpha = 1.5  # IS 13920 requirement
    elif splice_percent > 50:
        alpha = 1.3  # More than 50% bars spliced
    else:
        alpha = 1.0  # 50% or less bars spliced

    lap = alpha * ld

    return round(lap, 0)


# =============================================================================
# Bar Spacing (IS 456 Cl 26.3)
# =============================================================================


def calculate_bar_spacing(
    b: float, cover: float, stirrup_dia: float, bar_dia: float, bar_count: int
) -> float:
    """
    Calculate center-to-center spacing of bars.

    Args:
        b: Beam width (mm)
        cover: Clear cover (mm)
        stirrup_dia: Stirrup diameter (mm)
        bar_dia: Main bar diameter (mm)
        bar_count: Number of bars in layer

    Returns:
        Center-to-center spacing (mm)
    """
    if bar_count <= 1:
        return 0.0

    # Available width = b - 2*(cover + stirrup_dia) - bar_dia
    # For n bars, we have (n-1) spaces
    available = b - 2 * (cover + stirrup_dia) - bar_dia
    spacing = available / (bar_count - 1)

    return round(spacing, 0)


def check_min_spacing(
    spacing: float, bar_dia: float, agg_size: float = 20.0
) -> Tuple[bool, str]:
    """
    Check if bar spacing meets IS 456 Cl 26.3.2 requirements.

    Minimum = max(bar_dia, agg_size + 5mm, 25mm)

    Args:
        spacing: Actual center-to-center spacing (mm)
        bar_dia: Bar diameter (mm)
        agg_size: Maximum aggregate size (mm)

    Returns:
        (is_valid, message)
    """
    min_spacing = max(bar_dia, agg_size + 5, 25)

    if spacing >= min_spacing:
        return True, f"OK (min {min_spacing} mm)"
    else:
        return False, f"FAIL: Spacing {spacing} mm < min {min_spacing} mm"


# =============================================================================
# Bar Arrangement
# =============================================================================


def select_bar_arrangement(
    ast_required: float,
    b: float,
    cover: float,
    stirrup_dia: float = 8.0,
    preferred_dia: float = None,
    max_layers: int = 2,
) -> BarArrangement:
    """
    Select a practical bar arrangement to provide required steel area.

    Args:
        ast_required: Required steel area (mm²)
        b: Beam width (mm)
        cover: Clear cover (mm)
        stirrup_dia: Stirrup diameter (mm)
        preferred_dia: Preferred bar diameter (mm), or None for auto-select
        max_layers: Maximum number of layers allowed

    Returns:
        BarArrangement with practical bar selection
    """
    if ast_required <= 0:
        return BarArrangement(
            count=2, diameter=12, area_provided=226, spacing=0, layers=1
        )

    if b <= 0 or cover < 0 or stirrup_dia <= 0:
        # Keep behavior deterministic; callers can mark invalid if needed.
        return BarArrangement(
            count=2, diameter=12, area_provided=226, spacing=0, layers=1
        )

    # Auto-select diameter based on area
    if preferred_dia is None:
        if ast_required < 400:
            preferred_dia = 12
        elif ast_required < 1000:
            preferred_dia = 16
        elif ast_required < 2000:
            preferred_dia = 20
        else:
            preferred_dia = 25

    # Try to satisfy min-spacing by increasing layers and/or increasing diameter.
    # Deterministic order: start from preferred_dia, then larger standard diameters.
    start_dia = float(preferred_dia)
    dia_candidates = [start_dia] + [
        float(d) for d in STANDARD_BAR_DIAMETERS if float(d) > start_dia
    ]

    last_count = 2
    last_dia = float(dia_candidates[-1])
    last_spacing = 0.0
    last_layers = 1

    for dia in dia_candidates:
        dia = float(dia)
        bar_area = math.pi * (dia / 2) ** 2
        count_float = ast_required / bar_area
        count = max(2, math.ceil(count_float))  # Minimum 2 bars

        for layers in range(1, max_layers + 1):
            bars_per_layer = math.ceil(count / layers)
            spacing = calculate_bar_spacing(b, cover, stirrup_dia, dia, bars_per_layer)
            is_valid, _ = check_min_spacing(spacing, dia)

            last_count = count
            last_dia = dia
            last_spacing = spacing
            last_layers = layers

            if is_valid:
                area_provided = count * bar_area
                return BarArrangement(
                    count=count,
                    diameter=dia,
                    area_provided=round(area_provided, 0),
                    spacing=round(spacing, 0),
                    layers=layers,
                )

    # If we cannot satisfy spacing, return the best-effort arrangement deterministically.
    area_provided = last_count * (math.pi * (last_dia / 2) ** 2)
    return BarArrangement(
        count=last_count,
        diameter=last_dia,
        area_provided=round(area_provided, 0),
        spacing=round(last_spacing, 0),
        layers=last_layers,
    )


# =============================================================================
# Stirrup Legs
# =============================================================================


def get_stirrup_legs(b: float) -> int:
    """
    Determine number of stirrup legs based on beam width.

    IS 456 Cl 26.5.1.5: If width > 450mm, use more legs.

    Args:
        b: Beam width (mm)

    Returns:
        Number of legs (2, 4, or 6)
    """
    if b <= 300:
        return 2
    elif b <= 450:
        return 2  # Can use 2 or 4
    elif b <= 600:
        return 4
    else:
        return 6


# =============================================================================
# Format Helpers
# =============================================================================


def format_bar_callout(count: int, diameter: float) -> str:
    """
    Format bar callout in standard notation.

    Examples: "3-16φ", "4-20φ + 2-16φ"

    Args:
        count: Number of bars
        diameter: Bar diameter (mm)

    Returns:
        Formatted string
    """
    return f"{count}-{int(diameter)}φ"


def format_stirrup_callout(legs: int, diameter: float, spacing: float) -> str:
    """
    Format stirrup callout.

    Example: "2L-8φ@150 c/c"

    Args:
        legs: Number of legs
        diameter: Stirrup diameter (mm)
        spacing: Spacing (mm)

    Returns:
        Formatted string
    """
    return f"{legs}L-{int(diameter)}φ@{int(spacing)} c/c"


# =============================================================================
# Main Detailing Function
# =============================================================================


def create_beam_detailing(
    beam_id: str,
    story: str,
    b: float,
    D: float,
    span: float,
    cover: float,
    fck: float,
    fy: float,
    ast_start: float,
    ast_mid: float,
    ast_end: float,
    asc_start: float = 0,
    asc_mid: float = 0,
    asc_end: float = 0,
    stirrup_dia: float = 8,
    stirrup_spacing_start: float = 150,
    stirrup_spacing_mid: float = 200,
    stirrup_spacing_end: float = 150,
    is_seismic: bool = False,
) -> BeamDetailingResult:
    """
    Create complete beam detailing from design output.

    Args:
        beam_id: Beam identifier
        story: Story identifier
        b: Beam width (mm)
        D: Beam depth (mm)
        span: Beam span length (mm)
        cover: Clear cover (mm)
        fck: Concrete strength (N/mm²)
        fy: Steel yield strength (N/mm²)
        ast_start, ast_mid, ast_end: Required tension steel at each section (mm²)
        asc_start, asc_mid, asc_end: Required compression steel (mm²)
        stirrup_dia: Stirrup diameter (mm)
        stirrup_spacing_start/mid/end: Stirrup spacing (mm)
        is_seismic: Apply IS 13920 requirements

    Returns:
        BeamDetailingResult with complete detailing information
    """
    assumption_notes: List[str] = []

    # Select bar arrangements
    # Note: At supports (start/end), tension is typically top; at mid, tension is bottom
    # This simplification assumes Ast is always the tension side

    # Note: If compression steel (Asc) is not provided, we use a heuristic 25% of Ast.
    # This is a drafting aid only; callers should provide explicit Asc when known.
    if asc_start <= 0 and ast_start > 0:
        assumption_notes.append(
            "Top steel at start defaulted to 0.25×Ast (Asc not provided)."
        )
    if asc_mid <= 0 and ast_mid > 0:
        assumption_notes.append(
            "Top steel at mid defaulted to 0.25×Ast (Asc not provided)."
        )
    if asc_end <= 0 and ast_end > 0:
        assumption_notes.append(
            "Top steel at end defaulted to 0.25×Ast (Asc not provided)."
        )

    top_start = select_bar_arrangement(
        asc_start if asc_start > 0 else ast_start * 0.25, b, cover, stirrup_dia
    )
    top_mid = select_bar_arrangement(
        asc_mid if asc_mid > 0 else ast_mid * 0.25, b, cover, stirrup_dia
    )
    top_end = select_bar_arrangement(
        asc_end if asc_end > 0 else ast_end * 0.25, b, cover, stirrup_dia
    )

    bot_start = select_bar_arrangement(ast_start, b, cover, stirrup_dia)
    bot_mid = select_bar_arrangement(ast_mid, b, cover, stirrup_dia)
    bot_end = select_bar_arrangement(ast_end, b, cover, stirrup_dia)

    # Use max diameter for Ld
    max_dia = max(
        top_start.diameter,
        top_mid.diameter,
        top_end.diameter,
        bot_start.diameter,
        bot_mid.diameter,
        bot_end.diameter,
    )

    # Calculate development/lap lengths
    ld_tension = calculate_development_length(max_dia, fck, fy)
    ld_compression = ld_tension  # Same for compression
    lap_length = calculate_lap_length(max_dia, fck, fy, is_seismic=is_seismic)

    # Stirrup arrangements
    legs = get_stirrup_legs(b)
    zone_length = span / 4  # Approximate zone lengths

    stirrups = [
        StirrupArrangement(stirrup_dia, legs, stirrup_spacing_start, zone_length),
        StirrupArrangement(stirrup_dia, legs, stirrup_spacing_mid, span / 2),
        StirrupArrangement(stirrup_dia, legs, stirrup_spacing_end, zone_length),
    ]

    # Spacing sanity-check (horizontal clear spacing). Vertical layer clearance is not modeled.
    spacing_violations: List[str] = []
    for label, arr in [
        ("top_start", top_start),
        ("top_mid", top_mid),
        ("top_end", top_end),
        ("bot_start", bot_start),
        ("bot_mid", bot_mid),
        ("bot_end", bot_end),
    ]:
        ok, msg = check_min_spacing(arr.spacing, arr.diameter)
        if not ok:
            spacing_violations.append(f"{label}: {msg}")

    is_valid = len(spacing_violations) == 0
    remarks_parts: List[str] = []
    if is_valid:
        remarks_parts.append("Detailing complete")
    else:
        remarks_parts.append("Detailing has spacing violations")
        remarks_parts.extend(spacing_violations)
    remarks_parts.extend(assumption_notes)

    return BeamDetailingResult(
        beam_id=beam_id,
        story=story,
        b=b,
        D=D,
        span=span,
        cover=cover,
        top_bars=[top_start, top_mid, top_end],
        bottom_bars=[bot_start, bot_mid, bot_end],
        stirrups=stirrups,
        ld_tension=ld_tension,
        ld_compression=ld_compression,
        lap_length=lap_length,
        is_valid=is_valid,
        remarks="; ".join(remarks_parts),
    )
