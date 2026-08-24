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

import math
from dataclasses import dataclass, field

from structural_lib.codes.is456.common.constants import (
    COLUMN_MAX_STEEL_RATIO,
    COLUMN_MIN_STEEL_RATIO,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.errors import (
    E_DUCTILE_COL_001,
    E_DUCTILE_COL_002,
    E_DUCTILE_COL_005,
    E_DUCTILE_COL_006,
    E_DUCTILE_COL_007,
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


_STANDARD = "IS 13920:2016"
_SOURCE_REFERENCE = (
    "IS 13920:2016 First Revision with Amendment 1 (2017) " "and Amendment 2 (2020)"
)
_CLAUSE_REFS = ("7.1.1", "7.1.2", "7.6.1", "7.6.1(c)(2)")
_COMPANION_STANDARD = "IS 456:2000"
_COMPANION_CLAUSE_REFS = ("26.5.3.1(a)",)
_RESULT_KIND = "BOUNDED_RECTANGULAR_SPECIAL_CONFINEMENT_CHECK"
_COMPLIANCE_SCOPE = "GEOMETRY_AND_PROVIDED_SPECIAL_CONFINEMENT"
_LONGITUDINAL_STATUS = "NOT_EVALUATED_NO_PROVIDED_LONGITUDINAL_STEEL"
_APPLICABILITY_STATUS = "CONFIRMED_BY_CALLER"


@dataclass
class DuctileColumnResult:
    """Bounded rectangular-column special-confinement result.

    ``is_compliant`` covers geometry and the explicitly provided confinement
    spacing, length, and area only. Longitudinal reinforcement is not provided
    to this contract and is therefore reported separately as not evaluated.
    """

    is_geometry_valid: bool
    min_pt: float  # IS 456 companion minimum longitudinal steel %
    max_pt: float  # IS 456 companion maximum longitudinal steel %
    confining_spacing_mm: float
    confining_length_mm: float
    ash_required_mm2: float
    ash_expression_1_mm2: float
    ash_expression_2_mm2: float
    governing_ash_expression: str
    provided_confining_spacing_mm: float
    provided_confining_length_mm: float
    provided_ash_mm2: float
    spacing_passed: bool
    length_passed: bool
    ash_passed: bool
    is_compliant: bool
    applicability_basis: str
    errors: list[DesignError] = field(default_factory=list)
    result_kind: str = _RESULT_KIND
    compliance_scope: str = _COMPLIANCE_SCOPE
    longitudinal_reinforcement_status: str = _LONGITUDINAL_STATUS
    applicability_status: str = _APPLICABILITY_STATUS
    standard: str = _STANDARD
    source_reference: str = _SOURCE_REFERENCE
    clause_refs: tuple[str, ...] = _CLAUSE_REFS
    companion_standard: str = _COMPANION_STANDARD
    companion_clause_refs: tuple[str, ...] = _COMPANION_CLAUSE_REFS


def _require_positive_finite(value: float, field: str) -> None:
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be a finite value > 0, got {value}")


def _require_bool(value: object, field: str) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be a bool")


@clause("7.1.1", "7.1.2", standard="IS 13920")
def check_column_geometry(
    b_mm: float, D_mm: float
) -> tuple[bool, str, list[DesignError]]:
    """
    Check the accepted IS 13920 rectangular-column geometry boundaries.

    Checks:
    1. Cl 7.1.1: Minimum dimension >= 300 mm
    2. Cl 7.1.2 with Amendment 1: shortest/longest dimension >= 0.4

    Args:
        b_mm: Column width — shorter dimension (mm).
        D_mm: Column depth — longer dimension (mm).

    Returns:
        Tuple of (is_valid, message, errors).
    """
    errors: list[DesignError] = []

    for field_name, value in (("b_mm", b_mm), ("D_mm", D_mm)):
        if isinstance(value, bool) or not math.isfinite(value):
            raise ValueError(f"{field_name} must be a finite real number")

    if b_mm <= 0 or D_mm <= 0:
        errors.append(E_DUCTILE_COL_001)
        return False, "Column dimensions must be positive", errors

    # Ensure b_mm is the shorter dimension
    short = min(b_mm, D_mm)
    long = max(b_mm, D_mm)

    # IS 13920 Cl 7.1.1: Minimum dimension >= 300 mm
    if short < 300.0:
        errors.append(E_DUCTILE_COL_001)
        return (
            False,
            f"Minimum dimension {short:.0f} mm < 300 mm (IS 13920 Cl 7.1.1)",
            errors,
        )

    # IS 13920 Cl 7.1.2 with Amendment 1: shorter/longer >= 0.4
    ratio = short / long
    if ratio < 0.4:
        errors.append(E_DUCTILE_COL_002)
        return (
            False,
            f"Aspect ratio {ratio:.2f} < 0.4 (IS 13920 Cl 7.1.2)",
            errors,
        )

    return True, "OK", errors


@clause("26.5.3.1(a)", standard="IS 456")
def get_min_longitudinal_steel() -> float:
    """Return the IS 456 companion minimum longitudinal-steel percentage."""
    return COLUMN_MIN_STEEL_RATIO * 100.0


@clause("26.5.3.1(a)", standard="IS 456")
def get_max_longitudinal_steel() -> float:
    """Return the IS 456 companion maximum longitudinal-steel percentage."""
    return COLUMN_MAX_STEEL_RATIO * 100.0


@clause("7.6.1", standard="IS 13920")
def calculate_special_confining_spacing(b_mm: float, bar_dia_mm: float) -> float:
    """
    Calculate the amended maximum special-confinement spacing.

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
    _require_positive_finite(b_mm, "b_mm")
    _require_positive_finite(bar_dia_mm, "bar_dia_mm")

    # IS 13920 Cl 7.6.1 with Amendments 1 and 2.
    s1 = b_mm / 4.0
    s2 = 6.0 * bar_dia_mm
    s3 = 100.0

    return min(s1, s2, s3)


@clause("7.6.1", standard="IS 13920")
def calculate_confining_length(D_mm: float, clear_height_mm: float) -> float:
    """
    Calculate the amended minimum special-confinement length.

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
    _require_positive_finite(D_mm, "D_mm")
    _require_positive_finite(clear_height_mm, "clear_height_mm")

    # IS 13920 Cl 7.6.1 with Amendments 1 and 2.
    lo1 = D_mm
    lo2 = clear_height_mm / 6.0
    lo3 = 450.0

    return max(lo1, lo2, lo3)


@clause("7.6.1(c)(2)", standard="IS 13920")
def calculate_ash_required(
    s_mm: float,
    h_mm: float,
    fck: float,
    fy: float,
    Ag_mm2: float,
    Ak_mm2: float,  # noqa: N803
) -> float:
    """
    Return the governing area from both accepted rectangular expressions.

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
    for field_name, value in (
        ("s_mm", s_mm),
        ("h_mm", h_mm),
        ("fck", fck),
        ("fy", fy),
        ("Ag_mm2", Ag_mm2),
        ("Ak_mm2", Ak_mm2),
    ):
        _require_positive_finite(value, field_name)
    if Ak_mm2 >= Ag_mm2:
        raise ValueError(
            f"Confined core area Ak_mm2 ({Ak_mm2}) must be < Ag_mm2 ({Ag_mm2})"
        )

    # The accepted expression limits the reinforcement yield strength to 500.
    fy_eff = min(fy, 500.0)

    ash_expression_1 = 0.18 * s_mm * h_mm * (fck / fy_eff) * (Ag_mm2 / Ak_mm2 - 1.0)
    ash_expression_2 = 0.05 * s_mm * h_mm * (fck / fy_eff)
    return max(ash_expression_1, ash_expression_2)


@clause("7.1.1", "7.1.2", "7.6.1", "7.6.1(c)(2)", standard="IS 13920")
def check_column_ductility(
    b_mm: float,
    D_mm: float,
    clear_height_mm: float,
    bar_dia_mm: float,
    fck: float,
    fy: float,
    *,
    Ag_mm2: float,
    Ak_mm2: float,  # noqa: N803
    h_mm: float,
    provided_confining_spacing_mm: float,
    provided_confining_length_mm: float,
    provided_ash_mm2: float,
    is_is13920_applicable: bool,
    applicability_basis: str,
    is_rectangular_section: bool,
) -> DuctileColumnResult:
    """Check one explicitly applicable rectangular special-confinement detail.

    The caller must establish IS 13920 applicability and provide the actual
    confined-core/hoop geometry plus provided spacing, length, and hoop area.
    No cover, core dimension, gross area, or reinforcement is inferred.
    """
    _require_bool(is_is13920_applicable, "is_is13920_applicable")
    _require_bool(is_rectangular_section, "is_rectangular_section")
    if not is_is13920_applicable:
        raise ValueError(
            "IS 13920 column applicability must be established before this check"
        )
    if not is_rectangular_section:
        raise ValueError("only rectangular column sections are supported")
    if not isinstance(applicability_basis, str) or not applicability_basis.strip():
        raise ValueError("applicability_basis must be a non-empty string")

    for field_name, value in (
        ("b_mm", b_mm),
        ("D_mm", D_mm),
        ("clear_height_mm", clear_height_mm),
        ("bar_dia_mm", bar_dia_mm),
        ("fck", fck),
        ("fy", fy),
        ("Ag_mm2", Ag_mm2),
        ("Ak_mm2", Ak_mm2),
        ("h_mm", h_mm),
        ("provided_confining_spacing_mm", provided_confining_spacing_mm),
        ("provided_confining_length_mm", provided_confining_length_mm),
        ("provided_ash_mm2", provided_ash_mm2),
    ):
        _require_positive_finite(value, field_name)

    rectangular_area = b_mm * D_mm
    if not math.isclose(Ag_mm2, rectangular_area, rel_tol=1e-9, abs_tol=1e-6):
        raise ValueError("Ag_mm2 must equal b_mm * D_mm for the rectangular section")
    if Ak_mm2 >= Ag_mm2:
        raise ValueError("Ak_mm2 must be less than Ag_mm2")
    long_dim = max(b_mm, D_mm)
    if h_mm > long_dim:
        raise ValueError("h_mm cannot exceed the larger column dimension")

    min_pt = get_min_longitudinal_steel()
    max_pt = get_max_longitudinal_steel()
    is_geo_valid, _geo_msg, geo_errors = check_column_geometry(b_mm, D_mm)
    if not is_geo_valid:
        return DuctileColumnResult(
            is_geometry_valid=False,
            min_pt=min_pt,
            max_pt=max_pt,
            confining_spacing_mm=0.0,
            confining_length_mm=0.0,
            ash_required_mm2=0.0,
            ash_expression_1_mm2=0.0,
            ash_expression_2_mm2=0.0,
            governing_ash_expression="NOT_EVALUATED_INVALID_GEOMETRY",
            provided_confining_spacing_mm=provided_confining_spacing_mm,
            provided_confining_length_mm=provided_confining_length_mm,
            provided_ash_mm2=provided_ash_mm2,
            spacing_passed=False,
            length_passed=False,
            ash_passed=False,
            is_compliant=False,
            applicability_basis=applicability_basis.strip(),
            errors=geo_errors,
        )

    short_dim = min(b_mm, D_mm)
    maximum_spacing = calculate_special_confining_spacing(short_dim, bar_dia_mm)
    minimum_length = calculate_confining_length(long_dim, clear_height_mm)

    fy_eff = min(fy, 500.0)
    ash_expression_1 = (
        0.18
        * provided_confining_spacing_mm
        * h_mm
        * (fck / fy_eff)
        * (Ag_mm2 / Ak_mm2 - 1.0)
    )
    ash_expression_2 = 0.05 * provided_confining_spacing_mm * h_mm * (fck / fy_eff)
    ash_required = calculate_ash_required(
        provided_confining_spacing_mm,
        h_mm,
        fck,
        fy,
        Ag_mm2,
        Ak_mm2,
    )
    governing_expression = (
        "0.18_CORE_RATIO" if ash_expression_1 >= ash_expression_2 else "0.05_MINIMUM"
    )

    spacing_passed = provided_confining_spacing_mm <= maximum_spacing + 1e-9
    length_passed = provided_confining_length_mm >= minimum_length - 1e-9
    ash_passed = provided_ash_mm2 >= ash_required - 1e-9
    errors: list[DesignError] = []
    if not spacing_passed:
        errors.append(E_DUCTILE_COL_006)
    if not length_passed:
        errors.append(E_DUCTILE_COL_007)
    if not ash_passed:
        errors.append(E_DUCTILE_COL_005)

    return DuctileColumnResult(
        is_geometry_valid=True,
        min_pt=min_pt,
        max_pt=max_pt,
        confining_spacing_mm=maximum_spacing,
        confining_length_mm=minimum_length,
        ash_required_mm2=ash_required,
        ash_expression_1_mm2=ash_expression_1,
        ash_expression_2_mm2=ash_expression_2,
        governing_ash_expression=governing_expression,
        provided_confining_spacing_mm=provided_confining_spacing_mm,
        provided_confining_length_mm=provided_confining_length_mm,
        provided_ash_mm2=provided_ash_mm2,
        spacing_passed=spacing_passed,
        length_passed=length_passed,
        ash_passed=ash_passed,
        is_compliant=(spacing_passed and length_passed and ash_passed),
        applicability_basis=applicability_basis.strip(),
        errors=errors,
    )
