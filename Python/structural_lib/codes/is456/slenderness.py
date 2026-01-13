# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Slenderness Check Module — IS 456:2000 Beam Lateral Stability

This module provides functions for checking lateral stability and
slenderness effects in beams per IS 456:2000 Clause 23.3.

References:
- IS 456:2000, Cl 23.3 (Slenderness limits for beams)
- IS 456:2000, Cl 25.1.1, 25.1.2, 25.1.3 (Requirements for columns - reference)

Note: This module focuses on BEAM slenderness (lateral stability).
Column slenderness checks are a separate future module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

__all__ = [
    "SlendernessResult",
    "BeamType",
    "check_beam_slenderness",
    "calculate_slenderness_ratio",
    "get_slenderness_limit",
]


class BeamType(Enum):
    """Classification of beam for slenderness limits."""

    SIMPLY_SUPPORTED = "simply_supported"
    CONTINUOUS = "continuous"
    CANTILEVER = "cantilever"


@dataclass
class SlendernessResult:
    """Result of beam slenderness (lateral stability) check.

    Attributes:
        is_ok: True if beam passes all slenderness checks.
        is_slender: True if beam is classified as slender (requires extra checks).
        slenderness_ratio: l_eff / b (effective length / flange width).
        slenderness_limit: Maximum allowable slenderness ratio.
        utilization: slenderness_ratio / slenderness_limit (>1.0 is fail).
        depth_to_width_ratio: D / b (overall depth / width).
        remarks: Human-readable summary.
        assumptions: List of assumptions made during calculation.
        inputs: Input values used.
        computed: Intermediate computed values.
        errors: List of compliance errors (if any).
        warnings: List of warnings (if any).
    """

    is_ok: bool
    is_slender: bool
    slenderness_ratio: float
    slenderness_limit: float
    utilization: float
    depth_to_width_ratio: float
    remarks: str
    assumptions: list[str] = field(default_factory=list)
    inputs: dict[str, Any] = field(default_factory=dict)
    computed: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# Constants from IS 456:2000
# =============================================================================

# IS 456 Cl 23.3 - Slenderness limits for lateral stability
# l_u / b_f <= 60 for simply supported and continuous beams
# l_u / b_f <= 25 for cantilevers
# where l_u = unsupported length, b_f = width of compression flange
_SLENDERNESS_LIMITS: dict[BeamType, float] = {
    BeamType.SIMPLY_SUPPORTED: 60.0,
    BeamType.CONTINUOUS: 60.0,
    BeamType.CANTILEVER: 25.0,
}

# IS 456 Cl 23.3 - Additional depth/width limit
# 100 * b / D >= 40 (i.e., D/b <= 2.5 for some conditions)
# More general guidance: D/b <= 4 for lateral stability without restraint
_DEPTH_WIDTH_LIMIT_WARNING = 4.0  # D/b above this triggers warning


# =============================================================================
# Public Functions
# =============================================================================


def get_slenderness_limit(beam_type: BeamType | str) -> float:
    """Get the slenderness limit for a given beam type.

    Args:
        beam_type: BeamType enum or string ('simply_supported', 'continuous',
            'cantilever', 'ss', 'cont', 'cant').

    Returns:
        Slenderness limit (l_eff / b) per IS 456 Cl 23.3.

    Raises:
        ValueError: If beam type is not recognized.

    Example:
        >>> get_slenderness_limit(BeamType.CANTILEVER)
        25.0
        >>> get_slenderness_limit("simply_supported")
        60.0
    """
    normalized = _normalize_beam_type(beam_type)
    return _SLENDERNESS_LIMITS[normalized]


def calculate_slenderness_ratio(
    l_eff_mm: float,
    b_mm: float,
) -> float:
    """Calculate the slenderness ratio for a beam.

    Args:
        l_eff_mm: Effective unsupported length in mm.
        b_mm: Width of compression flange (typically beam width) in mm.

    Returns:
        Slenderness ratio (l_eff / b), dimensionless.

    Raises:
        ValueError: If l_eff_mm or b_mm are not positive.

    Example:
        >>> calculate_slenderness_ratio(6000, 250)
        24.0
    """
    if l_eff_mm <= 0:
        raise ValueError(f"Effective length must be positive, got {l_eff_mm} mm")
    if b_mm <= 0:
        raise ValueError(f"Beam width must be positive, got {b_mm} mm")

    return l_eff_mm / b_mm


def check_beam_slenderness(
    b_mm: float,
    d_mm: float,
    l_eff_mm: float,
    beam_type: BeamType | str = BeamType.SIMPLY_SUPPORTED,
    has_lateral_restraint: bool = False,
) -> SlendernessResult:
    """Check beam slenderness for lateral stability per IS 456 Cl 23.3.

    This function checks whether a beam section satisfies the lateral
    stability requirements of IS 456:2000. It considers:
    1. Slenderness ratio (l_eff / b) limit
    2. Depth-to-width ratio (D / b) for lateral buckling potential

    Args:
        b_mm: Width of compression flange in mm (typically beam width).
        d_mm: Overall depth of beam in mm.
        l_eff_mm: Effective unsupported length in mm.
            For simply supported: distance between lateral restraints.
            For cantilever: 2× projecting length.
        beam_type: Type of beam ('simply_supported', 'continuous', 'cantilever').
        has_lateral_restraint: If True, beam is laterally restrained (slab on top).
            Laterally restrained beams are generally OK for slenderness.

    Returns:
        SlendernessResult with check status and details.

    Raises:
        ValueError: If inputs are invalid (non-positive dimensions).

    Example:
        >>> result = check_beam_slenderness(
        ...     b_mm=300,
        ...     d_mm=600,
        ...     l_eff_mm=8000,
        ...     beam_type="simply_supported"
        ... )
        >>> result.is_ok
        True
        >>> result.slenderness_ratio
        26.67

    References:
        IS 456:2000 Cl 23.3: Slenderness limits for beams
    """
    # Validate inputs
    errors: list[str] = []
    warnings: list[str] = []
    assumptions: list[str] = []

    if b_mm <= 0:
        errors.append(f"Beam width must be positive, got {b_mm} mm")
    if d_mm <= 0:
        errors.append(f"Beam depth must be positive, got {d_mm} mm")
    if l_eff_mm <= 0:
        errors.append(f"Effective length must be positive, got {l_eff_mm} mm")

    if errors:
        return SlendernessResult(
            is_ok=False,
            is_slender=False,
            slenderness_ratio=0.0,
            slenderness_limit=0.0,
            utilization=0.0,
            depth_to_width_ratio=0.0,
            remarks="Invalid inputs: " + "; ".join(errors),
            assumptions=assumptions,
            inputs={"b_mm": b_mm, "d_mm": d_mm, "l_eff_mm": l_eff_mm},
            computed={},
            errors=errors,
            warnings=warnings,
        )

    # Normalize beam type
    try:
        beam_type_enum = _normalize_beam_type(beam_type)
    except ValueError as e:
        errors.append(str(e))
        beam_type_enum = BeamType.SIMPLY_SUPPORTED
        assumptions.append("Assumed simply_supported beam type due to invalid input")

    # Calculate ratios
    slenderness_ratio = l_eff_mm / b_mm
    slenderness_limit = _SLENDERNESS_LIMITS[beam_type_enum]
    depth_width_ratio = d_mm / b_mm
    utilization = slenderness_ratio / slenderness_limit if slenderness_limit > 0 else 0

    # Store inputs and computed
    inputs = {
        "b_mm": b_mm,
        "d_mm": d_mm,
        "l_eff_mm": l_eff_mm,
        "beam_type": beam_type_enum.value,
        "has_lateral_restraint": has_lateral_restraint,
    }
    computed = {
        "slenderness_ratio": round(slenderness_ratio, 2),
        "slenderness_limit": slenderness_limit,
        "depth_width_ratio": round(depth_width_ratio, 2),
        "utilization": round(utilization, 3),
    }

    # Check lateral restraint assumption
    if has_lateral_restraint:
        assumptions.append(
            "Beam is laterally restrained (e.g., slab provides compression flange restraint)"
        )

    # Determine slenderness status
    is_slender = (
        slenderness_ratio > slenderness_limit * 0.8
    )  # 80% threshold for "slender"
    slenderness_ok = slenderness_ratio <= slenderness_limit

    # Check depth/width ratio
    depth_width_ok = True
    if depth_width_ratio > _DEPTH_WIDTH_LIMIT_WARNING and not has_lateral_restraint:
        warnings.append(
            f"D/b ratio ({depth_width_ratio:.1f}) exceeds {_DEPTH_WIDTH_LIMIT_WARNING}. "
            "Deep narrow beams may have lateral stability issues. "
            "Consider lateral restraint or wider section."
        )
        if depth_width_ratio > 6.0:
            depth_width_ok = False
            errors.append(
                f"D/b ratio ({depth_width_ratio:.1f}) is too high (>6). "
                "Section is prone to lateral-torsional buckling."
            )

    # Overall status
    is_ok = slenderness_ok and depth_width_ok and (len(errors) == 0)

    # Generate remarks
    if is_ok:
        if has_lateral_restraint:
            remarks = (
                f"OK: Beam is laterally restrained. "
                f"Slenderness ratio {slenderness_ratio:.1f} ≤ {slenderness_limit} limit."
            )
        else:
            remarks = (
                f"OK: Slenderness ratio {slenderness_ratio:.1f} ≤ {slenderness_limit} limit "
                f"(IS 456 Cl 23.3). D/b = {depth_width_ratio:.1f}."
            )
    else:
        if not slenderness_ok:
            remarks = (
                f"FAIL: Slenderness ratio {slenderness_ratio:.1f} > {slenderness_limit} limit "
                f"(IS 456 Cl 23.3). Beam may buckle laterally."
            )
        else:
            remarks = (
                f"FAIL: D/b ratio {depth_width_ratio:.1f} is excessive. "
                "Increase width or add lateral restraint."
            )

    return SlendernessResult(
        is_ok=is_ok,
        is_slender=is_slender,
        slenderness_ratio=round(slenderness_ratio, 2),
        slenderness_limit=slenderness_limit,
        utilization=round(utilization, 3),
        depth_to_width_ratio=round(depth_width_ratio, 2),
        remarks=remarks,
        assumptions=assumptions,
        inputs=inputs,
        computed=computed,
        errors=errors,
        warnings=warnings,
    )


# =============================================================================
# Private Helpers
# =============================================================================


def _normalize_beam_type(value: BeamType | str) -> BeamType:
    """Normalize beam type input to enum.

    Args:
        value: BeamType enum or string alias.

    Returns:
        Normalized BeamType enum.

    Raises:
        ValueError: If beam type is not recognized.
    """
    if isinstance(value, BeamType):
        return value

    if not isinstance(value, str):
        raise ValueError(f"Invalid beam type: {value}. Expected BeamType or string.")

    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")

    # Map aliases
    alias_map = {
        "simply_supported": BeamType.SIMPLY_SUPPORTED,
        "ss": BeamType.SIMPLY_SUPPORTED,
        "simple": BeamType.SIMPLY_SUPPORTED,
        "continuous": BeamType.CONTINUOUS,
        "cont": BeamType.CONTINUOUS,
        "fixed": BeamType.CONTINUOUS,
        "cantilever": BeamType.CANTILEVER,
        "cant": BeamType.CANTILEVER,
        "cantilevered": BeamType.CANTILEVER,
    }

    if normalized in alias_map:
        return alias_map[normalized]

    valid_options = list(alias_map.keys())
    raise ValueError(f"Unknown beam type '{value}'. Valid options: {valid_options}")
