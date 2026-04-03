# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       codes.is13920.column
Description:  IS 13920:2016 Ductile Detailing checks for Columns (Cl 7)

IS 13920:2016 is the Indian Standard for ductile detailing of reinforced
concrete structures subjected to seismic forces. Clause 7 specifies
special confining reinforcement requirements for columns.

Location: structural_lib.codes.is13920.column (canonical)

References:
    IS 13920:2016, Cl. 7 — Special Confining Reinforcement
    IS 456:2000, Cl. 26.5.3 — Column detailing (non-seismic)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from structural_lib.core.errors import (
    E_DUCTILE_COL_001,
    E_DUCTILE_COL_002,
    E_INPUT_004,
    E_INPUT_005,
    DesignError,
)

__all__ = [
    "DuctileColumnResult",
    "check_column_geometry",
    "get_min_longitudinal_steel",
    "get_max_longitudinal_steel",
    "calculate_special_confining_spacing",
    "calculate_confining_length",
    "calculate_ash_required",
    "check_column_ductility",
]


@dataclass
class DuctileColumnResult:
    """Result of IS 13920:2016 Cl 7 ductile column detailing check."""

    is_geometry_valid: bool
    min_pt: float  # min longitudinal steel %
    max_pt: float  # max longitudinal steel %
    confining_spacing_mm: float
    confining_length_mm: float
    ash_required_mm2: float
    is_compliant: bool
    errors: list[DesignError] = field(default_factory=list)


def check_column_geometry(
    b_mm: float, D_mm: float
) -> tuple[bool, str, list[DesignError]]:
    """
    IS 13920:2016 Cl 7.1: Column geometry requirements for seismic zones.

    Checks:
    1. Cl 7.1.2: Minimum dimension >= 300 mm
    2. Cl 7.1.3: Ratio of shortest to longest dimension >= 0.4

    Args:
        b_mm: Column width — shorter dimension (mm).
        D_mm: Column depth — longer dimension (mm).

    Returns:
        Tuple of (is_valid, message, errors).
    """
    errors: list[DesignError] = []

    if b_mm <= 0 or D_mm <= 0:
        errors.append(E_DUCTILE_COL_001)
        return False, "Column dimensions must be positive", errors

    # Ensure b_mm is the shorter dimension
    short = min(b_mm, D_mm)
    long = max(b_mm, D_mm)

    # IS 13920 Cl 7.1.2: Minimum dimension >= 300 mm
    if short < 300.0:
        errors.append(E_DUCTILE_COL_001)
        return (
            False,
            f"Minimum dimension {short:.0f} mm < 300 mm (IS 13920 Cl 7.1.2)",
            errors,
        )

    # IS 13920 Cl 7.1.3: Aspect ratio (shorter/longer) >= 0.4
    ratio = short / long
    if ratio < 0.4 - 1e-9:
        errors.append(E_DUCTILE_COL_002)
        return (
            False,
            f"Aspect ratio {ratio:.2f} < 0.4 (IS 13920 Cl 7.1.3)",
            errors,
        )

    return True, "OK", errors


def get_min_longitudinal_steel() -> float:
    """
    IS 13920:2016 Cl 7.2.1: Minimum longitudinal steel for seismic columns.

    Returns:
        Minimum longitudinal steel percentage (0.8%).
    """
    return 0.8


def get_max_longitudinal_steel() -> float:
    """
    IS 13920:2016 Cl 7.2.1: Maximum longitudinal steel for seismic columns.

    Returns:
        Maximum longitudinal steel percentage (4.0%).
    """
    return 4.0


def calculate_special_confining_spacing(b_mm: float, bar_dia_mm: float) -> float:
    """
    IS 13920:2016 Cl 7.4.6: Spacing of special confining reinforcement.

    Spacing shall not exceed:
    1. b/4 (short dimension of column)
    2. 6 × smallest longitudinal bar diameter
    3. 100 mm

    Args:
        b_mm: Shorter dimension of column cross-section (mm).
        bar_dia_mm: Smallest longitudinal bar diameter (mm).

    Returns:
        Maximum permissible spacing of confining reinforcement (mm).

    Raises:
        ValueError: If b_mm or bar_dia_mm are not positive.
    """
    if b_mm <= 0:
        raise ValueError(f"Column dimension b_mm must be positive, got {b_mm}")
    if bar_dia_mm <= 0:
        raise ValueError(f"Bar diameter bar_dia_mm must be positive, got {bar_dia_mm}")

    # IS 13920 Cl 7.4.6: s <= min(b/4, 6*db, 100 mm)
    s1 = b_mm / 4.0
    s2 = 6.0 * bar_dia_mm
    s3 = 100.0

    return min(s1, s2, s3)


def calculate_confining_length(D_mm: float, clear_height_mm: float) -> float:
    """
    IS 13920:2016 Cl 7.4.1: Length of special confinement zone (lo).

    The special confinement zone extends from each joint face for a length lo:
    1. lo >= D (larger lateral dimension of member)
    2. lo >= clear_height / 6
    3. lo >= 450 mm

    Args:
        D_mm: Larger lateral dimension of column (mm).
        clear_height_mm: Clear height of column between floors (mm).

    Returns:
        Minimum required confinement length lo (mm).

    Raises:
        ValueError: If D_mm or clear_height_mm are not positive.
    """
    if D_mm <= 0:
        raise ValueError(f"Column dimension D_mm must be positive, got {D_mm}")
    if clear_height_mm <= 0:
        raise ValueError(f"Clear height must be positive, got {clear_height_mm}")

    # IS 13920 Cl 7.4.1: lo >= max(D, clear_height/6, 450 mm)
    lo1 = D_mm
    lo2 = clear_height_mm / 6.0
    lo3 = 450.0

    return max(lo1, lo2, lo3)


def calculate_ash_required(
    s_mm: float,
    h_mm: float,
    fck: float,
    fy: float,
    Ag_mm2: float,
    Ak_mm2: float,
) -> float:
    """
    IS 13920:2016 Cl 7.4.7/7.4.8: Area of special confining reinforcement.

    IS 13920 Cl 7.4.8: Ash = 0.18 * s * h * (fck / fy) * (Ag / Ak - 1.0)

    Args:
        s_mm: Spacing of confining reinforcement (mm).
        h_mm: Longer dimension of rectangular confining hoop,
              measured to its outer face (mm).
        fck: Characteristic compressive strength of concrete (N/mm²).
        fy: Yield strength of confining reinforcement (N/mm²).
              Not to be taken greater than 500 N/mm².
        Ag_mm2: Gross area of column cross-section (mm²).
        Ak_mm2: Area of confined concrete core, measured to
                centerline of confining hoop (mm²).

    Returns:
        Required area of confining bar Ash (mm²).

    Raises:
        ValueError: If any input is not positive or Ak >= Ag.
    """
    if s_mm <= 0:
        raise ValueError(f"Spacing s_mm must be positive, got {s_mm}")
    if h_mm <= 0:
        raise ValueError(f"Hoop dimension h_mm must be positive, got {h_mm}")
    if fck <= 0:
        raise ValueError(f"Concrete strength fck must be positive, got {fck}")
    if fy <= 0:
        raise ValueError(f"Steel strength fy must be positive, got {fy}")
    if Ag_mm2 <= 0:
        raise ValueError(f"Gross area Ag_mm2 must be positive, got {Ag_mm2}")
    if Ak_mm2 <= 0:
        raise ValueError(f"Confined core area Ak_mm2 must be positive, got {Ak_mm2}")
    if Ak_mm2 >= Ag_mm2:
        raise ValueError(
            f"Confined core area Ak_mm2 ({Ak_mm2}) must be < Ag_mm2 ({Ag_mm2})"
        )

    # IS 13920 Cl 7.4.8: fy capped at 500 N/mm²
    fy_eff = min(fy, 500.0)

    # IS 13920 Cl 7.4.8: Ash = 0.18 × s × h × (fck/fy) × (Ag/Ak - 1.0)
    Ash = 0.18 * s_mm * h_mm * (fck / fy_eff) * (Ag_mm2 / Ak_mm2 - 1.0)

    return Ash


def check_column_ductility(
    b_mm: float,
    D_mm: float,
    clear_height_mm: float,
    bar_dia_mm: float,
    fck: float,
    fy: float,
    Ag_mm2: float | None = None,
    Ak_mm2: float | None = None,
) -> DuctileColumnResult:
    """
    IS 13920:2016 Cl 7: Comprehensive ductile detailing check for columns.

    Performs all seismic detailing checks for column:
    - Geometry (Cl 7.1)
    - Longitudinal steel limits (Cl 7.2.1)
    - Special confining spacing (Cl 7.4.6)
    - Confinement zone length (Cl 7.4.1)
    - Confining reinforcement area (Cl 7.4.7/7.4.8) — only if Ag and Ak provided

    Args:
        b_mm: Column width — shorter dimension (mm).
        D_mm: Column depth — longer dimension (mm).
        clear_height_mm: Clear height of column (mm).
        bar_dia_mm: Smallest longitudinal bar diameter (mm).
        fck: Concrete compressive strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        Ag_mm2: Gross area of column (mm²). If None, computed as b_mm × D_mm.
        Ak_mm2: Area of confined core to centerline of hoop (mm²). Optional.

    Returns:
        DuctileColumnResult with all check outcomes.
    """
    # --- Geometry check (Cl 7.1) ---
    is_geo_valid, geo_msg, geo_errors = check_column_geometry(b_mm, D_mm)
    if not is_geo_valid:
        return DuctileColumnResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confining_spacing_mm=0.0,
            confining_length_mm=0.0,
            ash_required_mm2=0.0,
            is_compliant=False,
            errors=geo_errors,
        )

    # --- Input validation ---
    input_errors: list[DesignError] = []
    if clear_height_mm <= 0:
        input_errors.append(
            DesignError(
                code="E_DUCTILE_COL_INPUT",
                severity=E_INPUT_004.severity,
                message="clear_height_mm must be > 0",
                field="clear_height_mm",
            )
        )
    if bar_dia_mm <= 0:
        input_errors.append(
            DesignError(
                code="E_DUCTILE_COL_INPUT",
                severity=E_INPUT_004.severity,
                message="bar_dia_mm must be > 0",
                field="bar_dia_mm",
            )
        )
    if fck <= 0:
        input_errors.append(E_INPUT_004)
    if fy <= 0:
        input_errors.append(E_INPUT_005)

    if input_errors:
        return DuctileColumnResult(
            is_geometry_valid=True,
            min_pt=0.0,
            max_pt=0.0,
            confining_spacing_mm=0.0,
            confining_length_mm=0.0,
            ash_required_mm2=0.0,
            is_compliant=False,
            errors=input_errors,
        )

    # --- Longitudinal steel limits (Cl 7.2.1) ---
    min_pt = get_min_longitudinal_steel()
    max_pt = get_max_longitudinal_steel()

    # --- Special confining spacing (Cl 7.4.6) ---
    short_dim = min(b_mm, D_mm)
    spacing = calculate_special_confining_spacing(short_dim, bar_dia_mm)

    # --- Confinement zone length (Cl 7.4.1) ---
    long_dim = max(b_mm, D_mm)
    lo = calculate_confining_length(long_dim, clear_height_mm)

    # --- Confining reinforcement area (Cl 7.4.7/7.4.8) ---
    ash = 0.0
    if Ag_mm2 is None:
        Ag_mm2 = b_mm * D_mm
    if Ak_mm2 is not None and Ak_mm2 > 0 and Ak_mm2 < Ag_mm2:
        # h = longer dimension of rectangular confining hoop
        # Approximation: h ≈ D_mm - 2 * cover, but since Ak is provided,
        # use the longer core dimension. For the formula, h is the longer
        # dimension of the hoop measured to outer face.
        # We use D_mm side as the longer hoop dimension approximation.
        h_mm = long_dim - 2 * 40.0  # assuming 40 mm cover
        if h_mm > 0:
            ash = calculate_ash_required(spacing, h_mm, fck, fy, Ag_mm2, Ak_mm2)

    return DuctileColumnResult(
        is_geometry_valid=True,
        min_pt=min_pt,
        max_pt=max_pt,
        confining_spacing_mm=spacing,
        confining_length_mm=lo,
        ash_required_mm2=ash,
        is_compliant=True,
        errors=[],
    )
