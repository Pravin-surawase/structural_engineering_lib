# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       codes.is13920.beam
Description:  IS 13920:2016 Ductile Detailing checks for Beams

IS 13920:2016 is the Indian Standard for ductile detailing of reinforced
concrete structures subjected to seismic forces. It is a companion code
to IS 456:2000 and provides additional requirements for seismic zones.

Location: structural_lib.codes.is13920.beam (canonical)
Migration: Phase 0 restructure (TASK-709) — moved from codes.is456.ductile
"""

import math
from dataclasses import dataclass, field

from structural_lib.codes.is456.traceability import clause
from structural_lib.core.errors import (
    E_DUCTILE_001,
    E_DUCTILE_002,
    E_DUCTILE_003,
    E_INPUT_002,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_011,
    DesignError,
)
from structural_lib.core.validation import validate_finite_reals

__all__ = [
    "DuctileBeamResult",
    "check_geometry",
    "get_min_tension_steel_percentage",
    "get_max_tension_steel_percentage",
    "calculate_confinement_spacing",
    "check_beam_ductility",
]

_STANDARD = "IS 13920:2016"
_SOURCE_REFERENCE = (
    "IS 13920:2016 First Revision with Amendment 1 (2017) " "and Amendment 2 (2020)"
)
_CLAUSE_REFS = ("6.1.1", "6.1.2", "6.2.1(b)", "6.2.2", "6.3.5")
_RESULT_KIND = "REQUIREMENTS_WITH_GEOMETRY_CHECK"
_COMPLIANCE_STATUS = "NOT_EVALUATED_NO_PROVIDED_REINFORCEMENT"


@dataclass
class DuctileBeamResult:
    """Geometry result plus required beam reinforcement limits.

    This contract does not accept provided longitudinal reinforcement or link
    spacing, so it cannot report reinforcement compliance.
    """

    is_geometry_valid: bool
    min_pt: float
    max_pt: float
    confinement_spacing: float
    remarks: str = ""  # Deprecated: Use errors list instead
    errors: list[DesignError] = field(default_factory=list)  # Structured errors
    result_kind: str = _RESULT_KIND
    compliance_status: str = _COMPLIANCE_STATUS
    standard: str = _STANDARD
    source_reference: str = _SOURCE_REFERENCE
    clause_refs: tuple[str, ...] = _CLAUSE_REFS


@clause("6.1.1", "6.1.2", standard="IS 13920")
def check_geometry(b: float, D: float) -> tuple[bool, str, list[DesignError]]:
    """
    Clause 6.1: Geometry requirements
    1. b/D > 0.3 (6.1.1)
    2. b >= 200 mm (6.1.2)

    .. deprecated:: 0.10.5
        Return signature changed from (bool, str) to (bool, str, List[DesignError]).
        This is a breaking change for direct callers. Use check_beam_ductility()
        for the stable public API.
    """
    errors = validate_finite_reals(b=b, D=D)
    if errors:
        return False, "Invalid input: b and D must be finite real numbers.", errors

    if b < 200:
        errors.append(E_DUCTILE_001)
        return False, f"Width {b} mm < 200 mm (IS 13920 Cl 6.1.2)", errors

    if D <= 0:
        errors.append(E_DUCTILE_003)
        return False, "Invalid depth", errors

    ratio = b / D
    if ratio <= 0.3:
        errors.append(E_DUCTILE_002)
        return (
            False,
            f"Width/Depth ratio {ratio:.3f} must be > 0.3 (IS 13920 Cl 6.1.1)",
            errors,
        )

    return True, "OK", errors


@clause("6.2.1(b)", standard="IS 13920")
def get_min_tension_steel_percentage(fck: float, fy: float) -> float:
    """
    Clause 6.2.1 (b): Min tension steel ratio
    rho_min = 0.24 * sqrt(fck) / fy
    Returns percentage (0-100)

    Raises:
        ValueError: If fck or fy are non-positive.
    """
    if not math.isfinite(fck) or fck <= 0:
        raise ValueError(f"Concrete strength fck must be positive, got {fck}")
    if not math.isfinite(fy) or fy <= 0:
        raise ValueError(f"Steel yield strength fy must be positive, got {fy}")
    rho = 0.24 * math.sqrt(fck) / fy
    return rho * 100.0


@clause("6.2.2", standard="IS 13920")
def get_max_tension_steel_percentage() -> float:
    """
    Clause 6.2.2: Max tension steel ratio = 2.5%
    """
    return 2.5


@clause("6.3.5", standard="IS 13920")
def calculate_confinement_spacing(d: float, min_long_bar_dia: float) -> float:
    """
    Clause 6.3.5 with Amendment 1: close-link spacing within 2d of joint face.
    Spacing shall not exceed:
    1. d/4
    2. 6 * db_min (smallest longitudinal bar diameter)
    3. 100 mm
    """
    if not math.isfinite(d) or d <= 0:
        raise ValueError(f"Effective depth d must be positive and finite, got {d}")
    if not math.isfinite(min_long_bar_dia) or min_long_bar_dia <= 0:
        raise ValueError(
            "Minimum longitudinal bar diameter must be positive and finite, "
            f"got {min_long_bar_dia}"
        )

    s1 = d / 4.0
    s2 = 6.0 * min_long_bar_dia
    s3 = 100.0

    return min(s1, s2, s3)


@clause("6.1.1", "6.1.2", "6.2.1(b)", "6.2.2", "6.3.5", standard="IS 13920")
def check_beam_ductility(
    b: float, D: float, d: float, fck: float, fy: float, min_long_bar_dia: float
) -> DuctileBeamResult:
    """
    Check beam geometry and calculate bounded IS 13920 requirements.

    Provided longitudinal reinforcement and link spacing are not inputs. The
    returned result therefore never labels the reinforcement as compliant.
    """
    finite_errors = validate_finite_reals(
        b=b,
        D=D,
        d=d,
        fck=fck,
        fy=fy,
        min_long_bar_dia=min_long_bar_dia,
    )
    if finite_errors:
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks="Invalid input: all values must be finite real numbers.",
            errors=finite_errors,
        )

    is_geo_valid, geo_msg, geo_errors = check_geometry(b, D)
    if not is_geo_valid:
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks=geo_msg,
            errors=geo_errors,
        )

    input_errors = []
    if d <= 0:
        input_errors.append(E_INPUT_002)
    if min_long_bar_dia <= 0:
        input_errors.append(E_INPUT_011)
    if input_errors:
        failed_fields = [e.field for e in input_errors if e.field]
        error_message = f"Invalid input: {', '.join(failed_fields)} must be > 0."
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks=error_message,
            errors=input_errors,
        )

    material_errors = []
    if fck <= 0:
        material_errors.append(E_INPUT_004)
    if fy <= 0:
        material_errors.append(E_INPUT_005)
    if material_errors:
        return DuctileBeamResult(
            is_geometry_valid=False,
            min_pt=0.0,
            max_pt=0.0,
            confinement_spacing=0.0,
            remarks="Invalid input: fck and fy must be > 0.",
            errors=material_errors,
        )

    min_pt = get_min_tension_steel_percentage(fck, fy)
    max_pt = get_max_tension_steel_percentage()
    spacing = calculate_confinement_spacing(d, min_long_bar_dia)

    return DuctileBeamResult(
        is_geometry_valid=True,
        min_pt=min_pt,
        max_pt=max_pt,
        confinement_spacing=spacing,
        remarks=(
            "Requirements calculated; provided reinforcement compliance "
            "was not evaluated."
        ),
        errors=[],
    )
