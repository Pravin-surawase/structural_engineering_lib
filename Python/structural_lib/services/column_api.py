# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       column_api
Description:  Column design API functions (IS 456:2000 Clause 39).

Split from services/api.py (ARCH-NEW-12).
"""

from __future__ import annotations

import warnings
from typing import Any, TypeVar

from structural_lib.codes.is456.column.axial import (
    classify_column,
    effective_length,
    min_eccentricity,
    short_axial_capacity,
)
from structural_lib.codes.is456.column.biaxial import biaxial_bending_check
from structural_lib.codes.is456.column.detailing import create_column_detailing
from structural_lib.codes.is456.column.uniaxial import (
    design_short_column_uniaxial,
    pm_interaction_curve,
)
from structural_lib.codes.is13920.column import check_column_ductility
from structural_lib.core.data_types import (
    AdditionalMomentResult,
    ColumnAxialResult,
    ColumnBiaxialResult,
    ColumnDetailingResult,
    ColumnUniaxialResult,
    EndCondition,
    HelicalReinforcementResult,
    LongColumnResult,
    PMInteractionResult,
)

# ============================================================================
# Deprecated-parameter resolution helper
# ============================================================================

_T = TypeVar("_T")


def _resolve_deprecated_param(
    new_val: _T | None,
    old_val: _T | None,
    new_name: str,
    old_name: str,
    func_name: str,
) -> _T:
    """Resolve new vs deprecated param, warn if old is used."""
    if old_val is not None and new_val is not None:
        raise ValueError(
            f"{func_name}(): specify '{new_name}' or '{old_name}', not both"
        )
    if old_val is not None:
        warnings.warn(
            f"{func_name}(): '{old_name}' is deprecated, use '{new_name}' instead. "
            f"'{old_name}' will be removed in v0.24.",
            DeprecationWarning,
            stacklevel=3,
        )
        return old_val
    if new_val is not None:
        return new_val
    raise TypeError(f"{func_name}() requires '{new_name}'")


# ============================================================================
# Column Design Functions (IS 456:2000 Clause 39)
# ============================================================================


def calculate_effective_length_is456(
    l_mm: float,
    end_condition: str,
    use_theoretical: bool = False,
) -> dict[str, Any]:
    """Calculate effective length per IS 456 Cl 25.2, Table 28.

    Computes the effective length le = ratio × l for a column based on
    end restraint conditions. IS 456 Table 28 provides both theoretical
    (Euler) and recommended design values for seven standard cases.

    Args:
        l_mm: Unsupported length of column (mm). Must be between 100 and 50000 mm.
        end_condition: End condition string — one of:
            'FIXED_FIXED'      - Both ends fixed, no lateral translation
            'FIXED_HINGED'     - One end fixed, one hinged
            'FIXED_FIXED_SWAY' - Both ends fixed, lateral translation allowed
            'FIXED_FREE'       - One end fixed, one free (cantilever)
            'HINGED_HINGED'    - Both ends hinged
            'FIXED_PARTIAL'    - One fixed, partial restraint at other
            'HINGED_PARTIAL'   - One hinged, partial restraint at other
        use_theoretical: If True, use theoretical values (default: recommended).
            Note: Cases 6 and 7 have no theoretical values; recommended is used.

    Returns:
        dict with keys:
            - le_mm (float): Effective length (mm)
            - ratio (float): Effective length ratio (le/l)
            - end_condition (str): End condition used
            - method (str): 'theoretical' or 'recommended'

    Raises:
        ValueError: If l_mm is out of range or end_condition is invalid.

    References:
        IS 456:2000, Cl. 25.2, Table 28

    Examples:
        >>> calculate_effective_length_is456(3000, 'FIXED_FIXED')
        {'le_mm': 1950.0, 'ratio': 0.65, 'end_condition': 'FIXED_FIXED', 'method': 'recommended'}
        >>> calculate_effective_length_is456(4000, 'HINGED_HINGED', use_theoretical=True)
        {'le_mm': 4000.0, 'ratio': 1.0, 'end_condition': 'HINGED_HINGED', 'method': 'theoretical'}
    """
    # Plausibility guard: reasonable column lengths (100mm to 50m)
    if not (100 <= l_mm <= 50000):
        raise ValueError(
            f"Unsupported length l_mm must be between 100 and 50000 mm, got {l_mm}"
        )

    # Convert string to EndCondition enum
    try:
        end_cond_enum = EndCondition[end_condition]
    except KeyError as err:
        valid_conditions = ", ".join([ec.name for ec in EndCondition])
        raise ValueError(
            f"Invalid end_condition '{end_condition}'. "
            f"Valid options: {valid_conditions}"
        ) from err

    # Call the underlying IS 456 function
    le_mm = effective_length(
        l_mm=l_mm,
        end_condition=end_cond_enum,
        use_theoretical=use_theoretical,
    )

    # Calculate the ratio for reference
    ratio = le_mm / l_mm

    return {
        "le_mm": le_mm,
        "ratio": ratio,
        "end_condition": end_condition,
        "method": "theoretical" if use_theoretical else "recommended",
    }


def classify_column_is456(
    le_mm: float,
    D_mm: float,
) -> str:
    """Classify column as SHORT or SLENDER based on slenderness ratio (IS 456 Cl 25.1.2).

    A column is considered SHORT if both:
    - le/D < 12 for a rectangular column
    - le/d < 12 for a circular column (d = diameter)

    where le = effective length based on end restraints.

    Args:
        le_mm: Effective length (mm). Must be > 0.
        D_mm: Least lateral dimension (mm). For rectangular: smaller of b or D.
              For circular: diameter. Must be > 0.

    Returns:
        "SHORT" if slenderness ratio < 12, "SLENDER" otherwise.

    Raises:
        E_COLUMN_001: If le_mm ≤ 0 or D_mm ≤ 0.

    References:
        IS 456:2000, Cl. 25.1.2, Table 28

    Examples:
        >>> classify_column_is456(le_mm=3000, D_mm=300)
        'SHORT'
        >>> classify_column_is456(le_mm=4800, D_mm=300)
        'SLENDER'
    """

    result = classify_column(le_mm=le_mm, D_mm=D_mm)
    return result.name  # Return "SHORT" or "SLENDER" string


def min_eccentricity_is456(
    l_unsupported_mm: float,
    D_mm: float,
) -> float:
    """Calculate minimum design eccentricity for a column (IS 456 Cl 25.4).

    Per IS 456:2000 Cl 25.4, all columns must be designed for minimum eccentricity:
        e_min = greater of (l_unsupported/500 + D/30) or 20mm

    where:
    - l_unsupported = unsupported length of the column
    - D = lateral dimension in the plane of bending

    Args:
        l_unsupported_mm: Unsupported length of column (mm). Must be > 0.
        D_mm: Lateral dimension in the plane of bending (mm). Must be > 0.

    Returns:
        Minimum eccentricity e_min (mm). Always ≥ 20mm.

    Raises:
        E_COLUMN_002: If l_unsupported_mm ≤ 0 or D_mm ≤ 0.

    References:
        IS 456:2000, Cl. 25.4

    Examples:
        >>> min_eccentricity_is456(l_unsupported_mm=3000, D_mm=300)
        26.0
        >>> min_eccentricity_is456(l_unsupported_mm=2000, D_mm=200)
        20.67
    """
    return min_eccentricity(l_unsupported_mm=l_unsupported_mm, D_mm=D_mm)


def design_column_axial_is456(
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Ag_mm2: float = 0.0,
    Asc_mm2: float = 0.0,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> ColumnAxialResult:
    """Calculate axial load capacity for a short column (IS 456 Cl 39.3).

    For a short column under pure axial load (or minimum eccentricity),
    the design strength is:

        Pu = 0.4·fck·Ac + 0.67·fy·Asc

    where:
    - Ac = Ag - Asc (net concrete area)
    - Asc = area of longitudinal steel (must be 0.8% to 6% of Ag)

    NOTE: This applies ONLY to SHORT columns with minimum eccentricity.
    For slender columns or significant eccentricity, use interaction diagrams.

    Args:
        fck_nmm2: Characteristic concrete strength (N/mm²). Must be > 0.
        fy_nmm2: Yield strength of steel (N/mm²). Must be > 0.
        Ag_mm2: Gross cross-sectional area (mm²). Must be > 0.
        Asc_mm2: Area of longitudinal reinforcement (mm²). Must be ≥ 0.

    Returns:
        Dictionary with:
            - Pu_kN: Axial load capacity (kN)
            - steel_ratio: Asc/Ag (percentage)
            - warnings: List of warnings (e.g., steel ratio out of code limits)

    Raises:
        E_COLUMN_003: If fck ≤ 0, fy ≤ 0, or Ag_mm2 ≤ 0.
        E_COLUMN_004: If Asc_mm2 < 0.
        E_COLUMN_005: If Asc_mm2 > Ag_mm2.

    References:
        IS 456:2000, Cl. 39.3
        IS 456:2000, Cl. 26.5.3.1 (steel ratio limits)

    Examples:
        >>> result = design_column_axial_is456(
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Ag_mm2=90000.0,
        ...     Asc_mm2=1800.0
        ... )
        >>> result['Pu_kN']
        1380.62
        >>> result['steel_ratio']
        0.02
    """
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "design_column_axial_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "design_column_axial_is456"
    )

    result: ColumnAxialResult = short_axial_capacity(
        fck=fck_nmm2,
        fy=fy_nmm2,
        Ag_mm2=Ag_mm2,
        Asc_mm2=Asc_mm2,
    )

    return result


def design_short_column_uniaxial_is456(
    Pu_kN: float,  # noqa: N803
    Mu_kNm: float,  # noqa: N803
    b_mm: float,
    D_mm: float,
    le_mm: float,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Asc_mm2: float = 0.0,
    d_prime_mm: float = 0.0,
    l_unsupported_mm: float | None = None,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> ColumnUniaxialResult:
    """Design short column for uniaxial bending per IS 456 Cl 39.5.

    Generates the P-M interaction envelope for the given section and
    determines whether the applied (Pu, Mu) lies within it. Uses radial
    intersection to find capacity: a ray from origin through (Pu, Mu)
    intersects the envelope at (Pu_cap, Mu_cap).

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face, placed
    at d_prime_mm from the nearest face.

    Args:
        Pu_kN: Applied factored axial load (kN). Must be >= 0.
        Mu_kNm: Applied factored moment about bending axis (kNm). Must be >= 0.
        b_mm: Column width perpendicular to bending axis (mm). Typical: 100-2000.
        D_mm: Column depth in direction of bending (mm). Typical: 100-2000.
        le_mm: Effective length of column (mm). Must be > 0.
        fck_nmm2: Characteristic concrete strength (N/mm²). IS 456 range: 15-80.
        fy_nmm2: Yield strength of steel (N/mm²). IS 456 range: 250-550.
        Asc_mm2: Total longitudinal reinforcement area (mm²), symmetrically placed.
        d_prime_mm: Distance from face to steel centroid (mm). Must be > 0 and < D_mm/2.
        l_unsupported_mm: Unsupported length (mm) for min eccentricity per Cl 25.4.
            If None, minimum eccentricity check is skipped.

    Returns:
        Dictionary with:
            - ok: True if (Pu, Mu) is within capacity envelope
            - utilization: Radial utilization ratio (applied / capacity)
            - Pu_cap_kN: Capacity axial load at same Pu/Mu slope
            - Mu_cap_kNm: Capacity moment at same Pu/Mu slope
            - classification: "SHORT" or "SLENDER"
            - eccentricity_mm: Actual eccentricity e = M/P
            - e_min_mm: Minimum eccentricity (if l_unsupported_mm provided)
            - warnings: List of code compliance warnings

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.5 (P-M interaction)
        IS 456:2000, Cl. 25.4 (minimum eccentricity)
        IS 456:2000, Cl. 25.1.2 (column classification)
        SP:16:1980 Design Aids, Charts 27-62, Table I

    Examples:
        >>> result = design_short_column_uniaxial_is456(
        ...     Pu_kN=1200.0,
        ...     Mu_kNm=150.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     le_mm=3000.0,
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ...     l_unsupported_mm=3000.0,
        ... )
        >>> print(f"Safe: {result['ok']}")
        >>> print(f"Utilization: {result['utilization']:.1%}")

    See Also:
        - classify_column_is456: Check if column is short or slender
        - min_eccentricity_is456: Calculate minimum eccentricity
        - design_column_axial_is456: Pure axial capacity (no moment)
        - codes.is456.column.uniaxial.design_short_column_uniaxial: Core implementation
    """

    # Plausibility guards (aligned with existing api.py patterns)
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0, got {Pu_kN}")
    if Mu_kNm < 0:
        raise ValueError(f"Moment Mu_kNm must be >= 0, got {Mu_kNm}")

    # Resolve deprecated parameter aliases
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "design_short_column_uniaxial_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "design_short_column_uniaxial_is456"
    )

    # Dimension checks
    if not (100 <= b_mm <= 2000):
        raise ValueError(
            f"Column width b_mm should be 100-2000mm (got {b_mm}). "
            "If intentional, adjust validation."
        )
    if not (100 <= D_mm <= 2000):
        raise ValueError(
            f"Column depth D_mm should be 100-2000mm (got {D_mm}). "
            "If intentional, adjust validation."
        )

    # Material checks
    if not (15 <= fck_nmm2 <= 80):
        raise ValueError(
            f"fck_nmm2 should be 15-80 N/mm² per IS 456 (got {fck_nmm2}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy_nmm2 <= 550):
        raise ValueError(
            f"fy_nmm2 should be 250-550 N/mm² per IS 456 (got {fy_nmm2}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: ColumnUniaxialResult = design_short_column_uniaxial(
        Pu_kN=Pu_kN,
        Mu_kNm=Mu_kNm,
        b_mm=b_mm,
        D_mm=D_mm,
        le_mm=le_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        l_unsupported_mm=l_unsupported_mm,
    )

    # Return dataclass (DictCompatMixin provides result["key"] access)
    return result


def pm_interaction_curve_is456(
    b_mm: float,
    D_mm: float,  # noqa: N803
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Asc_mm2: float = 0.0,  # noqa: N803
    d_prime_mm: float = 0.0,
    n_points: int = 50,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> PMInteractionResult:
    """Produces the complete P-M interaction diagram for a rectangular column
    section with symmetrically placed reinforcement. Returns key points
    (pure axial, balanced, pure bending) and the full curve data.

    Args:
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth in bending direction (mm). Must be > 0.
        fck_nmm2: Characteristic compressive strength of concrete (N/mm²).
        fy_nmm2: Characteristic yield strength of steel (N/mm²).
        Asc_mm2: Total area of longitudinal reinforcement (mm²).
        d_prime_mm: Cover to steel centroid from nearest face (mm).
        n_points: Number of points on the curve (default 50, min 10).

    Returns:
        dict with keys:
            points: list of {"Pu_kN": float, "Mu_kNm": float} dicts
            Pu_0_kN: Pure axial capacity (kN)
            Mu_0_kNm: Pure bending capacity (kN·m)
            Pu_bal_kN: Balanced point axial load (kN)
            Mu_bal_kNm: Balanced point moment (kN·m)
            fck, fy, b_mm, D_mm, Asc_mm2, d_prime_mm: echoed inputs
            clause_ref: "Cl. 39.5"
            warnings: list of warning strings

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        ValueError: If n_points < 10.

    Example:
        >>> result = pm_interaction_curve_is456(
        ...     b_mm=300, D_mm=500, fck_nmm2=25, fy_nmm2=415,
        ...     Asc_mm2=3000, d_prime_mm=50,
        ... )
        >>> result["Pu_0_kN"]  # Pure axial capacity
        2304.15

    See Also:
        - codes.is456.column.uniaxial.pm_interaction_curve: Core implementation
    """
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "pm_interaction_curve_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "pm_interaction_curve_is456"
    )

    result: PMInteractionResult = pm_interaction_curve(
        b_mm=b_mm,
        D_mm=D_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        n_points=n_points,
    )
    return result


def biaxial_bending_check_is456(
    Pu_kN: float,
    Mux_kNm: float,
    Muy_kNm: float,
    b_mm: float,
    D_mm: float,
    le_mm: float,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Asc_mm2: float = 0.0,
    d_prime_mm: float = 0.0,
    l_unsupported_mm: float | None = None,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> ColumnBiaxialResult:
    """Check column under biaxial bending per IS 456 Cl 39.6.

    Implements the Bresler load contour formula to check if a column section
    with symmetrical reinforcement can safely resist combined axial load and
    biaxial bending moments.

    The Bresler formula is:
        (Mux / Mux1)^alpha_n + (Muy / Muy1)^alpha_n <= 1.0

    where Mux1, Muy1 are the uniaxial moment capacities at the applied
    axial load Pu, obtained from P-M interaction curves. The exponent
    alpha_n varies from 1.0 to 2.0 based on the Pu/Puz ratio.

    Reinforcement is assumed symmetrical: Asc_mm2 / 2 on each face,
    placed at d_prime_mm from the nearest face.

    Args:
        Pu_kN: Applied factored axial load (kN). Must be >= 0.
        Mux_kNm: Applied factored moment about x-axis (kNm). Must be >= 0.
        Muy_kNm: Applied factored moment about y-axis (kNm). Must be >= 0.
        b_mm: Column width perpendicular to x-axis bending (mm).
            Typical: 100-2000.
        D_mm: Column depth in x-axis bending direction (mm).
            Typical: 100-2000.
        le_mm: Effective length of column (mm). Must be > 0.
        fck_nmm2: Characteristic concrete strength (N/mm²). IS 456 range: 15-80.
        fy_nmm2: Yield strength of steel (N/mm²). IS 456 range: 250-550.
        Asc_mm2: Total longitudinal reinforcement area (mm²),
            symmetrically placed.
        d_prime_mm: Distance from face to steel centroid (mm).
            Must be > 0 and < min(b_mm, D_mm)/2.
        l_unsupported_mm: Unsupported length (mm) for slenderness warning.
            If None, slenderness is checked using le_mm only.

    Returns:
        Dictionary with:
            - Pu_kN: Applied axial load (kN)
            - Mux_kNm: Applied moment about x-axis (kN·m)
            - Muy_kNm: Applied moment about y-axis (kN·m)
            - Mux1_kNm: Uniaxial moment capacity about x at Pu (kN·m)
            - Muy1_kNm: Uniaxial moment capacity about y at Pu (kN·m)
            - Puz_kN: Pure axial crush capacity (kN) per Cl 39.6a
            - alpha_n: Bresler exponent (1.0–2.0)
            - interaction_ratio: (Mux/Mux1)^αn + (Muy/Muy1)^αn
            - is_safe: True if interaction_ratio ≤ 1.0
            - classification: "SHORT" or "SLENDER"
            - clause_ref: "Cl. 39.6"
            - warnings: List of warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.6 (biaxial bending, Bresler formula)
        IS 456:2000, Cl. 39.6a (Puz formula)
        IS 456:2000, Cl. 39.5 (P-M interaction envelope)
        IS 456:2000, Cl. 25.1.2 (column classification)
        SP:16:1980 Design Aids, Charts 63-64
        Pillai & Menon, "Reinforced Concrete Design", 3rd Ed., Ch. 13

    Examples:
        >>> result = biaxial_bending_check_is456(
        ...     Pu_kN=1200.0,
        ...     Mux_kNm=80.0,
        ...     Muy_kNm=60.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     le_mm=3000.0,
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Interaction Ratio: {result['interaction_ratio']:.3f}")

    See Also:
        - design_short_column_uniaxial_is456: Uniaxial bending check
        - pm_interaction_curve_is456: Generate P-M interaction curve
        - classify_column_is456: Check if column is short or slender
        - codes.is456.column.biaxial.biaxial_bending_check: Core implementation
    """

    # Plausibility guards (aligned with existing api.py patterns)
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0, got {Pu_kN}")
    if Mux_kNm < 0:
        raise ValueError(f"Moment Mux_kNm must be >= 0, got {Mux_kNm}")
    if Muy_kNm < 0:
        raise ValueError(f"Moment Muy_kNm must be >= 0, got {Muy_kNm}")

    # Resolve deprecated parameter aliases
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "biaxial_bending_check_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "biaxial_bending_check_is456"
    )

    # Dimension checks
    if not (100 <= b_mm <= 2000):
        raise ValueError(
            f"Column width b_mm should be 100-2000mm (got {b_mm}). "
            "If intentional, adjust validation."
        )
    if not (100 <= D_mm <= 2000):
        raise ValueError(
            f"Column depth D_mm should be 100-2000mm (got {D_mm}). "
            "If intentional, adjust validation."
        )

    # Material checks
    if not (15 <= fck_nmm2 <= 80):
        raise ValueError(
            f"fck_nmm2 should be 15-80 N/mm² per IS 456 (got {fck_nmm2}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy_nmm2 <= 550):
        raise ValueError(
            f"fy_nmm2 should be 250-550 N/mm² per IS 456 (got {fy_nmm2}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: ColumnBiaxialResult = biaxial_bending_check(
        Pu_kN=Pu_kN,
        Mux_kNm=Mux_kNm,
        Muy_kNm=Muy_kNm,
        b_mm=b_mm,
        D_mm=D_mm,
        le_mm=le_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        l_unsupported_mm=l_unsupported_mm,
    )

    # Return dataclass (DictCompatMixin provides result["key"] access)
    return result


def calculate_additional_moment_is456(
    Pu_kN: float,
    b_mm: float,
    D_mm: float,
    lex_mm: float,
    ley_mm: float,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Asc_mm2: float = 0.0,
    d_prime_mm: float = 0.0,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> AdditionalMomentResult:
    """Calculate additional moment for slender columns per IS 456 Cl 39.7.1.

    For slender columns (le/D >= 12), IS 456 requires an additional moment
    Ma = Pu × eadd to account for P-delta effects.

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        b_mm: Column width (mm). Must be > 0.
        D_mm: Column depth (mm). Must be > 0.
        lex_mm: Effective length about x-axis (mm). Must be > 0.
        ley_mm: Effective length about y-axis (mm). Must be > 0.
        fck_nmm2: Concrete characteristic strength (N/mm²).
        fy_nmm2: Steel yield strength (N/mm²).
        Asc_mm2: Total longitudinal steel area (mm²).
        d_prime_mm: Cover to centroid of reinforcement (mm).

    Returns:
        Dictionary with additional moments, eccentricities, k-factor,
        and slenderness classification for both axes.

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.7.1, 39.7.1.1

    Examples:
        >>> result = calculate_additional_moment_is456(
        ...     Pu_kN=1200.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     lex_mm=5400.0,
        ...     ley_mm=3600.0,
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ... )
        >>> print(f"Ma_x: {result['Ma_x_kNm']:.2f} kN·m")
        >>> print(f"Ma_y: {result['Ma_y_kNm']:.2f} kN·m")

    See Also:
        - classify_column_is456: Check if column is short or slender
        - biaxial_bending_check_is456: Biaxial bending check
        - codes.is456.column.slenderness.calculate_additional_moment: Core implementation
    """
    from structural_lib.codes.is456.column.slenderness import (
        calculate_additional_moment,
    )

    # Resolve deprecated parameter aliases
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "calculate_additional_moment_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "calculate_additional_moment_is456"
    )

    # Plausibility guards (unit confusion detection)
    if b_mm > 5000:
        raise ValueError("b_mm > 5000 — did you pass meters instead of mm?")
    if D_mm > 5000:
        raise ValueError("D_mm > 5000 — did you pass meters instead of mm?")
    if lex_mm > 100000:
        raise ValueError("lex_mm > 100000 — did you pass meters instead of mm?")
    if ley_mm > 100000:
        raise ValueError("ley_mm > 100000 — did you pass meters instead of mm?")

    # Call core implementation (already has full validation)
    result = calculate_additional_moment(
        Pu_kN=Pu_kN,
        b_mm=b_mm,
        D_mm=D_mm,
        lex_mm=lex_mm,
        ley_mm=ley_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
    )

    return result


def design_long_column_is456(
    Pu_kN: float,
    M1x_kNm: float,
    M2x_kNm: float,
    M1y_kNm: float,
    M2y_kNm: float,
    b_mm: float,
    D_mm: float,
    lex_mm: float,
    ley_mm: float,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Asc_mm2: float = 0.0,
    d_prime_mm: float = 0.0,
    braced: bool = True,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> LongColumnResult:
    """For slender columns (le/D >= 12), the design must account for additional
    moments due to P-delta effects. This function:
    1. Calculates additional moment Ma per Cl 39.7.1
    2. Augments applied moments: Mx_design = Mx + Ma_x
    3. Checks biaxial capacity with augmented moments

    The column must satisfy both:
    - Uniaxial checks with augmented moments
    - Biaxial interaction check (Bresler formula)

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        M1x_kNm: End moment 1 about x-axis (kNm). For equal end moments,
            M1x = M2x. Sign convention: +ve causes tension on same face.
        M2x_kNm: End moment 2 about x-axis (kNm).
        M1y_kNm: End moment 1 about y-axis (kNm).
        M2y_kNm: End moment 2 about y-axis (kNm).
        b_mm: Column width perpendicular to x-axis (mm). Typical: 100-2000.
        D_mm: Column depth in x-direction (mm). Typical: 100-2000.
        lex_mm: Effective length about x-axis (mm). Must be > 0.
        ley_mm: Effective length about y-axis (mm). Must be > 0.
        fck_nmm2: Concrete characteristic strength (N/mm²). IS 456 range: 15-80.
        fy_nmm2: Steel yield strength (N/mm²). IS 456 range: 250-550.
        Asc_mm2: Total longitudinal steel area (mm²), symmetrically placed.
        d_prime_mm: Cover to centroid of reinforcement (mm). Must be > 0.
        braced: If True, assumes braced frame (sway prevented). Default: True.

    Returns:
        Dictionary with:
            - is_safe (bool): True if column is adequate
            - classification (str): "SLENDER"
            - Pu_kN (float): Applied axial load (kN)
            - M1x_kNm, M2x_kNm, M1y_kNm, M2y_kNm (float): Applied end moments
            - Ma_x_kNm, Ma_y_kNm (float): Additional moments from P-delta (kNm)
            - Mx_design_kNm, My_design_kNm (float): Total design moments (kNm)
            - biaxial_check (dict): Result from biaxial_bending_check_is456
            - clause_ref (str): "Cl. 39.7"
            - warnings (list): Warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.7 (slender column design)
        IS 456:2000, Cl. 39.7.1 (additional moment Ma)
        IS 456:2000, Cl. 39.6 (biaxial bending check)

    Examples:
        >>> result = design_long_column_is456(
        ...     Pu_kN=1200.0,
        ...     M1x_kNm=60.0,
        ...     M2x_kNm=80.0,
        ...     M1y_kNm=40.0,
        ...     M2y_kNm=50.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     lex_mm=5400.0,
        ...     ley_mm=3600.0,
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Asc_mm2=2700.0,
        ...     d_prime_mm=50.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Design Moment X: {result['Mx_design_kNm']:.2f} kN·m")

    See Also:
        - calculate_additional_moment_is456: Calculate Ma per Cl 39.7.1
        - biaxial_bending_check_is456: Biaxial capacity check
        - classify_column_is456: Classify as SHORT or SLENDER
        - codes.is456.column.long_column.design_long_column: Core implementation
    """
    from structural_lib.codes.is456.column.long_column import design_long_column

    # Resolve deprecated parameter aliases
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "design_long_column_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "design_long_column_is456"
    )

    # Plausibility guards (unit confusion detection)
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0, got {Pu_kN}")
    if not (100 <= b_mm <= 2000):
        raise ValueError(
            f"Column width b_mm should be 100-2000mm (got {b_mm}). "
            "If intentional, adjust validation."
        )
    if not (100 <= D_mm <= 2000):
        raise ValueError(
            f"Column depth D_mm should be 100-2000mm (got {D_mm}). "
            "If intentional, adjust validation."
        )
    if not (15 <= fck_nmm2 <= 80):
        raise ValueError(
            f"fck_nmm2 should be 15-80 N/mm² per IS 456 (got {fck_nmm2}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy_nmm2 <= 550):
        raise ValueError(
            f"fy_nmm2 should be 250-550 N/mm² per IS 456 (got {fy_nmm2}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: LongColumnResult = design_long_column(
        Pu_kN=Pu_kN,
        M1x_kNm=M1x_kNm,
        M2x_kNm=M2x_kNm,
        M1y_kNm=M1y_kNm,
        M2y_kNm=M2y_kNm,
        b_mm=b_mm,
        D_mm=D_mm,
        lex_mm=lex_mm,
        ley_mm=ley_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        Asc_mm2=Asc_mm2,
        d_prime_mm=d_prime_mm,
        braced=braced,
    )

    # Return dataclass (DictCompatMixin provides result["key"] access)
    return result


def check_helical_reinforcement_is456(
    D_mm: float,
    D_core_mm: float,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    d_helix_mm: float = 0.0,
    pitch_mm: float = 0.0,
    Pu_axial_kN: float = 0.0,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> HelicalReinforcementResult:
    """For circular columns with helical (spiral) reinforcement, IS 456 Cl 39.4
    provides an alternative design approach where the helically reinforced
    core can carry significantly higher loads than a tied column.

    The pure axial capacity is given by:
        Pu = 1.05 × (0.4·fck·Ac + 0.67·fy·Asc + ρh·fck·Ak)

    where:
    - Ac = core area within helix
    - Asc = longitudinal steel area
    - Ak = core area measured to outside of helix
    - ρh = volumetric ratio of helical steel

    The helix must satisfy minimum pitch and bar diameter requirements
    per Cl 26.5.3.2(c).

    Args:
        D_mm: Overall column diameter (mm). Must be > 200 (typical: 200-2000).
        D_core_mm: Core diameter to centerline of helix (mm). Must be < D_mm.
        fck_nmm2: Concrete characteristic strength (N/mm²). IS 456 range: 15-80.
        fy_nmm2: Steel yield strength (N/mm²). IS 456 range: 250-550.
        d_helix_mm: Diameter of helical bar (mm). Typical: 8-20.
        pitch_mm: Pitch of helix (mm). Must satisfy: 25mm ≤ pitch ≤ 75mm
            or pitch ≤ D_core/6 per Cl 26.5.3.2(c).
        Pu_axial_kN: Applied factored axial load (kN). Must be >= 0.

    Returns:
        Dictionary with:
            - is_safe (bool): True if helix satisfies IS 456 requirements
            - Pu_capacity_kN (float): Axial capacity with helical reinforcement (kN)
            - rho_h (float): Volumetric ratio of helical steel (dimensionless)
            - Ah_mm2 (float): Cross-sectional area of one helix turn (mm²)
            - pitch_ok (bool): True if pitch meets Cl 26.5.3.2(c)
            - d_helix_ok (bool): True if bar diameter adequate
            - utilization (float): Pu_axial / Pu_capacity (0.0-1.0)
            - clause_ref (str): "Cl. 39.4"
            - warnings (list): Warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        ValueError: If plausibility checks fail.

    References:
        IS 456:2000, Cl. 39.4 (helically reinforced columns)
        IS 456:2000, Cl. 26.5.3.2(c) (helix pitch and bar diameter)

    Examples:
        >>> result = check_helical_reinforcement_is456(
        ...     D_mm=500.0,
        ...     D_core_mm=440.0,
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     d_helix_mm=10.0,
        ...     pitch_mm=50.0,
        ...     Pu_axial_kN=2000.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Capacity: {result['Pu_capacity_kN']:.2f} kN")

    See Also:
        - design_column_axial_is456: Pure axial capacity check
        - codes.is456.column.helical.check_helical_reinforcement: Core implementation
    """
    from structural_lib.codes.is456.column.helical import check_helical_reinforcement

    # Resolve deprecated parameter aliases
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "check_helical_reinforcement_is456"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "check_helical_reinforcement_is456"
    )

    # Plausibility guards (unit confusion detection)
    if D_mm > 5000:
        raise ValueError("D_mm > 5000 — did you pass meters instead of mm?")
    if D_core_mm >= D_mm:
        raise ValueError(
            f"Core diameter D_core_mm ({D_core_mm}) must be < overall diameter D_mm ({D_mm})"
        )
    if not (15 <= fck_nmm2 <= 80):
        raise ValueError(
            f"fck_nmm2 should be 15-80 N/mm² per IS 456 (got {fck_nmm2}). "
            "If intentional, adjust validation."
        )
    if not (250 <= fy_nmm2 <= 550):
        raise ValueError(
            f"fy_nmm2 should be 250-550 N/mm² per IS 456 (got {fy_nmm2}). "
            "If intentional, adjust validation."
        )

    # Call core implementation (already has full validation)
    result: HelicalReinforcementResult = check_helical_reinforcement(
        D_mm=D_mm,
        D_core_mm=D_core_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        d_helix_mm=d_helix_mm,
        pitch_mm=pitch_mm,
        Pu_axial_kN=Pu_axial_kN,
    )

    # Return dataclass (DictCompatMixin provides result["key"] access)
    return result


def design_column_is456(
    Pu_kN: float,
    Mux_kNm: float = 0.0,
    Muy_kNm: float = 0.0,
    b_mm: float = 0.0,
    D_mm: float = 0.0,
    l_mm: float = 0.0,
    end_condition: str = "FIXED_FIXED",
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Asc_mm2: float = 0.0,
    d_prime_mm: float = 50.0,
    l_unsupported_mm: float | None = None,
    braced: bool = True,
    M1x_kNm: float | None = None,
    M2x_kNm: float | None = None,
    M1y_kNm: float | None = None,
    M2y_kNm: float | None = None,
    *,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> dict[str, Any]:
    """Design column per IS 456:2000 — unified orchestrator.

    Master entry point for column design that automatically routes to the
    appropriate design checks based on column classification. Handles:
    1. Effective length calculation from end conditions (Cl 25.2, Table 28)
    2. Column classification as SHORT or SLENDER (Cl 25.1.2)
    3. Minimum eccentricity enforcement (Cl 25.4)
    4. Short column checks: uniaxial or biaxial (Cl 39.5, 39.6)
    5. Slender column checks with additional moments (Cl 39.7)

    This function provides a single, consistent interface for all column
    design scenarios, automatically selecting the appropriate IS 456 clauses.

    Args:
        Pu_kN: Factored axial load (kN). Must be >= 0.
        Mux_kNm: Applied factored moment about x-axis (kNm). Default: 0.0.
        Muy_kNm: Applied factored moment about y-axis (kNm). Default: 0.0.
        b_mm: Column width perpendicular to x-axis (mm). Default: 0.0.
            Typical: 100-2000.
        D_mm: Column depth in x-direction (mm). Default: 0.0.
            Typical: 100-2000.
        l_mm: Unsupported length of column (mm). Default: 0.0.
        end_condition: End restraint condition. Default: 'FIXED_FIXED'.
            Options: 'FIXED_FIXED', 'FIXED_HINGED', 'FIXED_FIXED_SWAY',
            'FIXED_FREE', 'HINGED_HINGED', 'FIXED_PARTIAL', 'HINGED_PARTIAL'.
        fck_nmm2: Concrete characteristic strength (N/mm²). Default: 25.0.
            IS 456 range: 15-80.
        fy_nmm2: Steel yield strength (N/mm²). Default: 415.0.
            IS 456 range: 250-550.
        Asc_mm2: Total longitudinal steel area (mm²). Default: 0.0.
            For initial sizing, use 0.8-6% of gross area.
        d_prime_mm: Cover to centroid of reinforcement (mm). Default: 50.0.
        l_unsupported_mm: Unsupported length for min eccentricity (mm).
            If None, uses l_mm. Used for Cl 25.4 minimum eccentricity.
        braced: If True, assumes braced frame (sway prevented). Default: True.
            Affects slender column moment magnification.
        M1x_kNm: End moment 1 about x-axis (kNm) for slender columns.
            If None and column is slender, assumes M1x = M2x = Mux.
        M2x_kNm: End moment 2 about x-axis (kNm) for slender columns.
            If None and column is slender, assumes M2x = Mux.
        M1y_kNm: End moment 1 about y-axis (kNm) for slender columns.
            If None and column is slender, assumes M1y = M2y = Muy.
        M2y_kNm: End moment 2 about y-axis (kNm) for slender columns.
            If None and column is slender, assumes M2y = Muy.

    Returns:
        Dictionary with:
            - is_safe (bool): Overall adequacy indicator
            - classification (str): "SHORT" or "SLENDER"
            - le_x_mm, le_y_mm (float): Effective lengths (mm)
            - slenderness_x, slenderness_y (float): Slenderness ratios
            - emin_x_mm, emin_y_mm (float): Minimum eccentricities (mm)
            - Mux_design_kNm, Muy_design_kNm (float): Design moments with
                minimum eccentricity and (for slender) additional moments (kNm)
            - governing_check (str): "uniaxial_x", "uniaxial_y", "biaxial",
                or "long_column"
            - checks (dict): Results from all applicable sub-checks
            - clause_refs (list): List of applicable IS 456 clause references
            - warnings (list): Warning messages

    Raises:
        DimensionError: If geometric dimensions are invalid.
        MaterialError: If material properties are out of range.
        CalculationError: If numerical issues are encountered.
        ValueError: If plausibility checks fail or required inputs missing.

    References:
        IS 456:2000, Cl. 25.2 (effective length)
        IS 456:2000, Cl. 25.1.2 (column classification)
        IS 456:2000, Cl. 25.4 (minimum eccentricity)
        IS 456:2000, Cl. 39.5 (short column uniaxial)
        IS 456:2000, Cl. 39.6 (short column biaxial)
        IS 456:2000, Cl. 39.7 (slender column design)

    Examples:
        >>> # Short column, uniaxial
        >>> result = design_column_is456(
        ...     Pu_kN=800.0,
        ...     Mux_kNm=120.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     l_mm=3000.0,
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Asc_mm2=2400.0,
        ... )
        >>> print(f"Safe: {result['is_safe']}")
        >>> print(f"Classification: {result['classification']}")
        >>> print(f"Governing: {result['governing_check']}")

        >>> # Slender column, biaxial
        >>> result = design_column_is456(
        ...     Pu_kN=1200.0,
        ...     Mux_kNm=80.0,
        ...     Muy_kNm=60.0,
        ...     b_mm=300.0,
        ...     D_mm=450.0,
        ...     l_mm=6000.0,
        ...     end_condition='HINGED_HINGED',
        ...     fck_nmm2=25.0,
        ...     fy_nmm2=415.0,
        ...     Asc_mm2=2700.0,
        ... )
        >>> print(f"Classification: {result['classification']}")  # SLENDER
        >>> print(f"Additional Moment X: {result.get('Ma_x_kNm', 0):.2f} kN·m")

    See Also:
        - calculate_effective_length_is456: Effective length per Table 28
        - classify_column_is456: SHORT vs SLENDER classification
        - min_eccentricity_is456: Minimum eccentricity per Cl 25.4
        - design_short_column_uniaxial_is456: Short column uniaxial check
        - biaxial_bending_check_is456: Short column biaxial check
        - design_long_column_is456: Slender column design with Ma
    """
    # Validate required inputs
    if b_mm <= 0 or D_mm <= 0:
        raise ValueError(f"Column dimensions must be > 0 (got b={b_mm}, D={D_mm})")
    if l_mm <= 0:
        raise ValueError(f"Column length l_mm must be > 0 (got {l_mm})")
    if Pu_kN < 0:
        raise ValueError(f"Axial load Pu_kN must be >= 0 (got {Pu_kN})")

    # Resolve deprecated parameter aliases (with defaults)
    if fck_nmm2 is None and fck is None:
        fck_nmm2 = 25.0
    else:
        fck_nmm2 = _resolve_deprecated_param(
            fck_nmm2, fck, "fck_nmm2", "fck", "design_column_is456"
        )
    if fy_nmm2 is None and fy is None:
        fy_nmm2 = 415.0
    else:
        fy_nmm2 = _resolve_deprecated_param(
            fy_nmm2, fy, "fy_nmm2", "fy", "design_column_is456"
        )

    # Step 1: Calculate effective lengths in both directions
    le_result = calculate_effective_length_is456(l_mm, end_condition)
    le_mm = le_result["le_mm"]

    # Use same effective length for both axes unless different unsupported lengths
    le_x_mm = le_mm
    le_y_mm = le_mm

    # Step 2: Classify column based on slenderness in both directions
    classification_x = classify_column_is456(le_x_mm, D_mm)
    classification_y = classify_column_is456(le_y_mm, b_mm)

    # Overall classification: SLENDER if slender in either direction
    is_slender = (classification_x == "SLENDER") or (classification_y == "SLENDER")
    classification = "SLENDER" if is_slender else "SHORT"

    # Step 3: Calculate minimum eccentricities per Cl 25.4
    l_unsup = l_unsupported_mm if l_unsupported_mm is not None else l_mm
    emin_x_mm = min_eccentricity_is456(l_unsup, D_mm)
    emin_y_mm = min_eccentricity_is456(l_unsup, b_mm)

    # Minimum moments from eccentricity
    Mux_min_kNm = Pu_kN * emin_x_mm / 1000.0  # Convert mm to m
    Muy_min_kNm = Pu_kN * emin_y_mm / 1000.0

    # Enforce minimum eccentricity
    Mux_design = max(Mux_kNm, Mux_min_kNm)
    Muy_design = max(Muy_kNm, Muy_min_kNm)

    # Initialize result dictionary
    result: dict[str, Any] = {
        "Pu_kN": Pu_kN,
        "Mux_applied_kNm": Mux_kNm,
        "Muy_applied_kNm": Muy_kNm,
        "classification": classification,
        "le_x_mm": le_x_mm,
        "le_y_mm": le_y_mm,
        "slenderness_x": le_x_mm / D_mm,
        "slenderness_y": le_y_mm / b_mm,
        "emin_x_mm": emin_x_mm,
        "emin_y_mm": emin_y_mm,
        "Mux_min_kNm": Mux_min_kNm,
        "Muy_min_kNm": Muy_min_kNm,
        "checks": {},
        "warnings": [],
        "clause_refs": ["Cl. 25.2", "Cl. 25.1.2", "Cl. 25.4"],
    }

    # Step 4 & 5: Design path depends on classification
    if classification == "SHORT":
        # SHORT column checks
        result["Mux_design_kNm"] = Mux_design
        result["Muy_design_kNm"] = Muy_design

        # Determine if uniaxial or biaxial
        is_biaxial = (Mux_design > 0.001) and (Muy_design > 0.001)

        if is_biaxial:
            # Biaxial check
            biaxial_result = biaxial_bending_check_is456(
                Pu_kN=Pu_kN,
                Mux_kNm=Mux_design,
                Muy_kNm=Muy_design,
                b_mm=b_mm,
                D_mm=D_mm,
                le_mm=le_mm,
                fck_nmm2=fck_nmm2,
                fy_nmm2=fy_nmm2,
                Asc_mm2=Asc_mm2,
                d_prime_mm=d_prime_mm,
                l_unsupported_mm=l_unsup,
            )
            result["checks"]["biaxial"] = biaxial_result
            result["is_safe"] = biaxial_result["is_safe"]
            result["governing_check"] = "biaxial"
            result["clause_refs"].append("Cl. 39.6")
        else:
            # Uniaxial check (x-axis or y-axis dominant)
            if Mux_design >= Muy_design:
                # X-axis bending dominant
                uniaxial_result = design_short_column_uniaxial_is456(
                    Pu_kN=Pu_kN,
                    Mu_kNm=Mux_design,
                    b_mm=b_mm,
                    D_mm=D_mm,
                    le_mm=le_mm,
                    fck_nmm2=fck_nmm2,
                    fy_nmm2=fy_nmm2,
                    Asc_mm2=Asc_mm2,
                    d_prime_mm=d_prime_mm,
                )
                result["checks"]["uniaxial_x"] = uniaxial_result
                result["is_safe"] = uniaxial_result["ok"]
                result["governing_check"] = "uniaxial_x"
            else:
                # Y-axis bending dominant (swap dimensions)
                uniaxial_result = design_short_column_uniaxial_is456(
                    Pu_kN=Pu_kN,
                    Mu_kNm=Muy_design,
                    b_mm=D_mm,  # Swap for y-axis bending
                    D_mm=b_mm,
                    le_mm=le_mm,
                    fck_nmm2=fck_nmm2,
                    fy_nmm2=fy_nmm2,
                    Asc_mm2=Asc_mm2,
                    d_prime_mm=d_prime_mm,
                )
                result["checks"]["uniaxial_y"] = uniaxial_result
                result["is_safe"] = uniaxial_result["ok"]
                result["governing_check"] = "uniaxial_y"

            result["clause_refs"].append("Cl. 39.5")

    else:
        # SLENDER column — must account for additional moments
        result["clause_refs"].append("Cl. 39.7")

        # If end moments not provided, assume equal end moments
        M1x = M1x_kNm if M1x_kNm is not None else Mux_design
        M2x = M2x_kNm if M2x_kNm is not None else Mux_design
        M1y = M1y_kNm if M1y_kNm is not None else Muy_design
        M2y = M2y_kNm if M2y_kNm is not None else Muy_design

        # Call slender column design
        long_result = design_long_column_is456(
            Pu_kN=Pu_kN,
            M1x_kNm=M1x,
            M2x_kNm=M2x,
            M1y_kNm=M1y,
            M2y_kNm=M2y,
            b_mm=b_mm,
            D_mm=D_mm,
            lex_mm=le_x_mm,
            ley_mm=le_y_mm,
            fck_nmm2=fck_nmm2,
            fy_nmm2=fy_nmm2,
            Asc_mm2=Asc_mm2,
            d_prime_mm=d_prime_mm,
            braced=braced,
        )

        result["checks"]["long_column"] = long_result
        result["is_safe"] = long_result["is_safe"]
        result["governing_check"] = "long_column"

        # Include additional moments in top-level result
        result["Ma_x_kNm"] = long_result.get("Max_kNm", 0.0)
        result["Ma_y_kNm"] = long_result.get("May_kNm", 0.0)
        result["Mux_design_kNm"] = long_result.get("Mux_design_kNm", 0.0)
        result["Muy_design_kNm"] = long_result.get("Muy_design_kNm", 0.0)

        # Aggregate warnings
        if long_result.get("warnings"):
            result["warnings"].extend(long_result["warnings"])

    return result


def detail_column_is456(
    *,
    b_mm: float,
    D_mm: float,
    cover_mm: float = 40.0,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    num_bars: int,
    bar_dia_mm: float,
    tie_dia_mm: float | None = None,
    is_circular: bool = False,
    at_lap_section: bool = False,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> ColumnDetailingResult:
    """Validates longitudinal reinforcement limits, bar spacing, tie diameter,
    tie spacing, and cross-tie requirements for a column section.

    Args:
        b_mm: Column width (mm). Range: 100–5000.
        D_mm: Column depth (mm). Range: 100–5000.
        cover_mm: Clear cover (mm). Range: 15–100. Default: 40.0.
        fck_nmm2: Characteristic concrete strength (N/mm²). Range: 15–80. Default: 25.0.
        fy_nmm2: Yield strength of steel (N/mm²). Range: 250–600. Default: 415.0.
        num_bars: Number of longitudinal bars. Range: 3–60.
        bar_dia_mm: Longitudinal bar diameter (mm). Range: 8–50.
        tie_dia_mm: Tie bar diameter (mm). If None, auto-selected per code.
        is_circular: True for circular columns. Default: False.
        at_lap_section: True if checking at lap splice location. Default: False.

    Returns:
        Dictionary with all detailing check results (see ColumnDetailingResult).

    Raises:
        ValueError: If parameters are outside plausible ranges.

    References:
        IS 456:2000, Cl. 26.5.3

    Examples:
        >>> result = detail_column_is456(
        ...     b_mm=300, D_mm=450, num_bars=6, bar_dia_mm=16
        ... )
        >>> result['is_valid']
        True
    """
    # Resolve deprecated aliases (defaults: fck=25.0, fy=415.0)
    if fck_nmm2 is None and fck is None:
        fck_nmm2 = 25.0
    else:
        fck_nmm2 = _resolve_deprecated_param(
            fck_nmm2, fck, "fck_nmm2", "fck", "detail_column_is456"
        )
    if fy_nmm2 is None and fy is None:
        fy_nmm2 = 415.0
    else:
        fy_nmm2 = _resolve_deprecated_param(
            fy_nmm2, fy, "fy_nmm2", "fy", "detail_column_is456"
        )

    # Boundary validation
    if not (100 <= b_mm <= 5000):
        raise ValueError(f"Column width b_mm should be 100–5000mm (got {b_mm}).")
    if not (100 <= D_mm <= 5000):
        raise ValueError(f"Column depth D_mm should be 100–5000mm (got {D_mm}).")
    if not (15 <= cover_mm <= 100):
        raise ValueError(f"Cover cover_mm should be 15–100mm (got {cover_mm}).")
    if not (15 <= fck_nmm2 <= 80):
        raise ValueError(f"fck_nmm2 should be 15–80 N/mm² per IS 456 (got {fck_nmm2}).")
    if not (250 <= fy_nmm2 <= 600):
        raise ValueError(f"fy_nmm2 should be 250–600 N/mm² per IS 456 (got {fy_nmm2}).")
    if not (3 <= num_bars <= 60):
        raise ValueError(f"num_bars should be 3–60 (got {num_bars}).")
    if not (8 <= bar_dia_mm <= 50):
        raise ValueError(f"bar_dia_mm should be 8–50mm (got {bar_dia_mm}).")

    result = create_column_detailing(
        b_mm=b_mm,
        D_mm=D_mm,
        cover_mm=cover_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        num_bars=num_bars,
        bar_dia_mm=bar_dia_mm,
        tie_dia_mm=tie_dia_mm,
        is_circular=is_circular,
        at_lap_section=at_lap_section,
    )

    return result


def check_column_ductility_is13920(
    *,
    b_mm: float,
    D_mm: float,
    clear_height_mm: float,
    bar_dia_mm: float,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    Ag_mm2: float | None = None,
    Ak_mm2: float | None = None,
    fck: float | None = None,  # Deprecated alias
    fy: float | None = None,  # Deprecated alias
) -> dict:
    """Check column ductile detailing per IS 13920:2016 Cl 7.

    Validates geometry, longitudinal steel limits, special confining
    reinforcement spacing, confinement zone length, and confining bar area.

    Args:
        b_mm: Column width — shorter dimension (mm). Range: 200–5000.
        D_mm: Column depth — longer dimension (mm). Range: 200–5000.
        clear_height_mm: Clear height of column between floors (mm).
        bar_dia_mm: Smallest longitudinal bar diameter (mm). Range: 8–50.
        fck_nmm2: Concrete compressive strength (N/mm²). Range: 15–80.
        fy_nmm2: Steel yield strength (N/mm²). Range: 250–600.
        Ag_mm2: Gross area of column (mm²). If None, computed as b_mm × D_mm.
        Ak_mm2: Confined core area to hoop centerline (mm²). If None,
            estimated as (b_mm - 80) × (D_mm - 80) assuming 40 mm cover.

    Returns:
        Dictionary with ductile detailing check results.

    Raises:
        ValueError: If parameters are outside plausible ranges.

    References:
        IS 13920:2016, Cl. 7

    Examples:
        >>> result = check_column_ductility_is13920(
        ...     b_mm=400, D_mm=500, clear_height_mm=3000,
        ...     bar_dia_mm=16, fck=25, fy=415,
        ... )
        >>> result['is_compliant']
        True
    """
    fck_nmm2 = _resolve_deprecated_param(
        fck_nmm2, fck, "fck_nmm2", "fck", "check_column_ductility_is13920"
    )
    fy_nmm2 = _resolve_deprecated_param(
        fy_nmm2, fy, "fy_nmm2", "fy", "check_column_ductility_is13920"
    )

    # Boundary validation
    if not (200 <= b_mm <= 5000):
        raise ValueError(f"Column width b_mm should be 200–5000mm (got {b_mm}).")
    if not (200 <= D_mm <= 5000):
        raise ValueError(f"Column depth D_mm should be 200–5000mm (got {D_mm}).")
    if clear_height_mm <= 0:
        raise ValueError(f"clear_height_mm must be positive (got {clear_height_mm}).")
    if not (8 <= bar_dia_mm <= 50):
        raise ValueError(f"bar_dia_mm should be 8–50mm (got {bar_dia_mm}).")
    if not (15 <= fck_nmm2 <= 80):
        raise ValueError(f"fck_nmm2 should be 15–80 N/mm² (got {fck_nmm2}).")
    if not (250 <= fy_nmm2 <= 600):
        raise ValueError(f"fy_nmm2 should be 250–600 N/mm² (got {fy_nmm2}).")

    # Default areas for rectangular section
    if Ag_mm2 is None:
        Ag_mm2 = b_mm * D_mm
    if Ak_mm2 is None:
        Ak_mm2 = (b_mm - 2 * 40) * (D_mm - 2 * 40)

    result = check_column_ductility(
        b_mm=b_mm,
        D_mm=D_mm,
        clear_height_mm=clear_height_mm,
        bar_dia_mm=bar_dia_mm,
        fck=fck_nmm2,
        fy=fy_nmm2,
        Ag_mm2=Ag_mm2,
        Ak_mm2=Ak_mm2,
    )

    from dataclasses import asdict

    return asdict(result)
