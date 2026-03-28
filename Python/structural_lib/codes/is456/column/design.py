# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       column
Description:  Column design per IS 456:2000 Cl 39.1-39.5

This module provides functions for RC column design including:
- Axial capacity (Cl 39.3)
- Uniaxial bending capacity (Cl 39.5)
- Reinforcement limits (Cl 26.5.3.1)
- P-M interaction check

Note: Requires check_column_slenderness() from slenderness.py for
classification before design. This module handles SHORT columns only.
Long column additional moments (Cl 39.7.1) are a future extension.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from structural_lib.codes.is456.materials import get_xu_max_d

__all__ = [
    "ColumnDesignResult",
    "design_short_column",
    "calculate_axial_capacity",
    "calculate_pm_interaction_point",
    "check_reinforcement_limits",
]


# =============================================================================
# Constants — IS 456 Column Limits
# =============================================================================

_MIN_COLUMN_DIM_MM = 200.0          # Cl 26.5.3.1 recommended minimum
_MIN_AST_PERCENT = 0.8              # Cl 26.5.3.1 — 0.8% of gross area
_MAX_AST_PERCENT = 6.0              # Cl 26.5.3.1 — 6% of gross area (4% at laps)
_MIN_BARS = 4                       # Cl 26.5.3.1(b) — min 4 bars in rectangular
_MIN_ECCENTRICITY_FACTOR = 0.05     # Cl 25.4 — e_min = max(l/500 + D/30, 20mm), simplified


@dataclass
class ColumnDesignResult:
    """Result of column design per IS 456:2000.

    Attributes:
        is_safe: True if column can resist applied loads.
        Pu_capacity_kn: Pure axial capacity (kN) — Cl 39.3.
        Mu_capacity_knm: Moment capacity at given axial load (kN·m).
        ast_required_mm2: Required total longitudinal steel area (mm²).
        ast_min_mm2: Minimum steel per Cl 26.5.3.1 (0.8% Ag).
        ast_max_mm2: Maximum steel per Cl 26.5.3.1 (6% Ag).
        p_percent: Steel percentage provided/required.
        utilization: Interaction ratio (≤1.0 is safe).
        e_min_mm: Minimum eccentricity per Cl 25.4.
        remarks: Human-readable summary.
        inputs: Input values used.
        computed: Intermediate computed values.
        errors: List of errors.
        warnings: List of warnings.
    """
    is_safe: bool
    Pu_capacity_kn: float
    Mu_capacity_knm: float
    ast_required_mm2: float
    ast_min_mm2: float
    ast_max_mm2: float
    p_percent: float
    utilization: float
    e_min_mm: float
    remarks: str
    inputs: dict[str, Any] = field(default_factory=dict)
    computed: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# =============================================================================
# Public Functions
# =============================================================================


def calculate_axial_capacity(
    b_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
    ast_mm2: float,
) -> float:
    """Calculate pure axial capacity of short column per IS 456 Cl 39.3.

    Pu = 0.4 × fck × Ac + 0.67 × fy × Asc
    where Ac = Ag - Asc (net concrete area)

    Args:
        b_mm: Column width (mm).
        D_mm: Column depth (mm).
        fck: Characteristic concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        ast_mm2: Total longitudinal steel area (mm²).

    Returns:
        Pure axial capacity Pu in kN.

    Raises:
        ValueError: If inputs are invalid.
    """
    if b_mm <= 0 or D_mm <= 0:
        raise ValueError(f"Column dimensions must be positive: b={b_mm}, D={D_mm}")
    if fck <= 0 or fy <= 0:
        raise ValueError(f"Material strengths must be positive: fck={fck}, fy={fy}")
    if ast_mm2 < 0:
        raise ValueError(f"Steel area must be non-negative: ast={ast_mm2}")

    Ag = b_mm * D_mm
    Ac = Ag - ast_mm2
    if Ac < 0:
        raise ValueError(f"Steel area ({ast_mm2}) exceeds gross area ({Ag})")

    # IS 456 Cl 39.3: Pu = 0.4*fck*Ac + 0.67*fy*Asc
    Pu_N = 0.4 * fck * Ac + 0.67 * fy * ast_mm2
    return Pu_N / 1000.0  # Convert to kN


def calculate_pm_interaction_point(
    b_mm: float,
    D_mm: float,
    fck: float,
    fy: float,
    ast_mm2: float,
    cover_mm: float = 40.0,
    xu_d_ratio: float | None = None,
) -> tuple[float, float]:
    """Calculate one P-M interaction point for given xu/d ratio.

    For a rectangular section with equal steel on both faces, calculates
    the (Pu, Mu) point at balanced failure per IS 456 Cl 38.1 + 39.1.

    Args:
        b_mm: Column width (mm).
        D_mm: Column depth (mm).
        fck: Concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        ast_mm2: Total steel area (mm²) — assumed equally split top+bottom.
        cover_mm: Clear cover (mm).
        xu_d_ratio: Neutral axis depth ratio (xu/d). If None, uses xu_max/d.

    Returns:
        Tuple of (Pu_kn, Mu_knm) — axial load and moment at this point.
    """
    if b_mm <= 0 or D_mm <= 0:
        raise ValueError(f"Dimensions must be positive: b={b_mm}, D={D_mm}")
    if fck <= 0 or fy <= 0:
        raise ValueError(f"Material strengths must be positive: fck={fck}, fy={fy}")

    d_mm = D_mm - cover_mm - 12  # Effective depth (assuming 12mm bar radius)
    d_prime = cover_mm + 12       # Compression steel depth

    if xu_d_ratio is None:
        xu_d_ratio = get_xu_max_d(fy)

    xu = xu_d_ratio * d_mm

    # Concrete compression force: Cu = 0.36 × fck × b × xu
    Cu_N = 0.36 * fck * b_mm * xu

    # Steel on each face (assume equal distribution)
    ast_each = ast_mm2 / 2.0

    # Compression steel strain and stress
    if xu > 0:
        strain_sc = 0.0035 * (xu - d_prime) / xu
        stress_sc = min(abs(strain_sc) * 200000, 0.87 * fy)
        if strain_sc < 0:
            stress_sc = -stress_sc  # Tension in "compression" steel

        # Tension steel strain and stress
        strain_st = 0.0035 * (d_mm - xu) / xu
        stress_st = min(abs(strain_st) * 200000, 0.87 * fy)
        if strain_st < 0:
            stress_st = -stress_st
    else:
        stress_sc = 0.0
        stress_st = 0.87 * fy

    # Forces
    Csc_N = stress_sc * ast_each       # Compression steel force
    Tst_N = stress_st * ast_each       # Tension steel force

    # Axial capacity: Pu = Cu + Csc - Tst
    Pu_N = Cu_N + Csc_N - Tst_N
    Pu_kn = Pu_N / 1000.0

    # Moment about centroid (D/2):
    # Mu = Cu × (D/2 - 0.42×xu) + Csc × (D/2 - d') + Tst × (d - D/2)
    Mu_Nmm = (
        Cu_N * (D_mm / 2 - 0.42 * xu)
        + Csc_N * (D_mm / 2 - d_prime)
        + Tst_N * (d_mm - D_mm / 2)
    )
    Mu_knm = Mu_Nmm / 1e6

    return (round(Pu_kn, 2), round(Mu_knm, 2))


def check_reinforcement_limits(
    b_mm: float,
    D_mm: float,
    ast_mm2: float,
) -> dict[str, Any]:
    """Check column reinforcement against IS 456 limits (Cl 26.5.3.1).

    Args:
        b_mm: Column width (mm).
        D_mm: Column depth (mm).
        ast_mm2: Total longitudinal steel area (mm²).

    Returns:
        Dict with: p_percent, ast_min, ast_max, is_ok, errors, warnings.
    """
    Ag = b_mm * D_mm
    p_percent = (ast_mm2 / Ag) * 100 if Ag > 0 else 0
    ast_min = _MIN_AST_PERCENT * Ag / 100
    ast_max = _MAX_AST_PERCENT * Ag / 100

    errors = []
    warnings = []
    is_ok = True

    if ast_mm2 < ast_min:
        errors.append(
            f"Steel area {ast_mm2:.0f} mm² < minimum {ast_min:.0f} mm² "
            f"({_MIN_AST_PERCENT}% of Ag, IS 456 Cl 26.5.3.1)"
        )
        is_ok = False

    if ast_mm2 > ast_max:
        errors.append(
            f"Steel area {ast_mm2:.0f} mm² > maximum {ast_max:.0f} mm² "
            f"({_MAX_AST_PERCENT}% of Ag, IS 456 Cl 26.5.3.1)"
        )
        is_ok = False

    if 4.0 < p_percent <= _MAX_AST_PERCENT:
        warnings.append(
            f"Steel percentage {p_percent:.1f}% > 4.0%. "
            "IS 456 Cl 26.5.3.1 recommends max 4% except at laps."
        )

    min_dim = min(b_mm, D_mm)
    if min_dim < _MIN_COLUMN_DIM_MM:
        warnings.append(
            f"Minimum dimension {min_dim:.0f} mm < {_MIN_COLUMN_DIM_MM:.0f} mm "
            "(IS 456 Cl 26.5.3.1 recommendation)"
        )

    return {
        "p_percent": round(p_percent, 2),
        "ast_min_mm2": round(ast_min, 1),
        "ast_max_mm2": round(ast_max, 1),
        "is_ok": is_ok,
        "errors": errors,
        "warnings": warnings,
    }


def design_short_column(
    b_mm: float,
    D_mm: float,
    Pu_kn: float,
    Mu_knm: float,
    fck: float,
    fy: float,
    cover_mm: float = 40.0,
    unsupported_length_mm: float | None = None,
) -> ColumnDesignResult:
    """Design a short RC column for axial load + uniaxial bending.

    Determines required longitudinal steel for a short rectangular column
    subjected to factored axial load Pu and factored moment Mu per
    IS 456 Cl 39.1-39.5.

    Design approach:
    1. Check minimum eccentricity (Cl 25.4)
    2. Calculate pure axial capacity at various steel percentages
    3. Find steel percentage that satisfies P-M interaction
    4. Check reinforcement limits (Cl 26.5.3.1)

    Args:
        b_mm: Column width (mm).
        D_mm: Column depth (mm).
        Pu_kn: Factored axial load (kN).
        Mu_knm: Factored bending moment (kN·m). Min eccentricity applied if too small.
        fck: Characteristic concrete strength (N/mm²).
        fy: Steel yield strength (N/mm²).
        cover_mm: Clear cover (mm), default 40.
        unsupported_length_mm: If provided, used to compute e_min. Otherwise D/30+20 used.

    Returns:
        ColumnDesignResult with capacity, steel requirement, and checks.

    Example:
        >>> result = design_short_column(300, 300, 1500, 50, 25, 500)
        >>> result.is_safe
        True
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Input validation
    if b_mm <= 0:
        errors.append(f"Column width must be positive, got {b_mm} mm")
    if D_mm <= 0:
        errors.append(f"Column depth must be positive, got {D_mm} mm")
    if Pu_kn <= 0:
        errors.append(f"Axial load must be positive, got {Pu_kn} kN")
    if fck <= 0 or fy <= 0:
        errors.append(f"Material strengths must be positive: fck={fck}, fy={fy}")

    if errors:
        return ColumnDesignResult(
            is_safe=False,
            Pu_capacity_kn=0.0,
            Mu_capacity_knm=0.0,
            ast_required_mm2=0.0,
            ast_min_mm2=0.0,
            ast_max_mm2=0.0,
            p_percent=0.0,
            utilization=0.0,
            e_min_mm=0.0,
            remarks="Invalid inputs: " + "; ".join(errors),
            errors=errors,
            warnings=warnings,
        )

    Ag = b_mm * D_mm
    d_mm = D_mm - cover_mm - 12  # effective depth

    # Minimum eccentricity — IS 456 Cl 25.4
    if unsupported_length_mm is not None:
        e_min = max(unsupported_length_mm / 500.0 + D_mm / 30.0, 20.0)
    else:
        e_min = max(D_mm / 30.0, 20.0)

    # Apply minimum eccentricity
    e_actual = (Mu_knm * 1e6) / (Pu_kn * 1000) if Pu_kn > 0 else float('inf')
    if e_actual < e_min:
        Mu_knm = Pu_kn * e_min / 1000.0  # kN × mm / 1000 = kN·m
        warnings.append(
            f"Applied eccentricity {e_actual:.1f} mm < minimum {e_min:.1f} mm (Cl 25.4). "
            f"Design moment increased to {Mu_knm:.2f} kN·m."
        )

    # Reinforcement limits
    ast_min = _MIN_AST_PERCENT * Ag / 100
    ast_max = _MAX_AST_PERCENT * Ag / 100

    # Iterative design: find steel area that satisfies P-M interaction
    # Start from minimum, increase until capacity >= demand
    ast_trial = ast_min
    step = max(50.0, ast_min * 0.1)  # Increment step
    max_iterations = 200
    found = False

    for _ in range(max_iterations):
        if ast_trial > ast_max:
            break

        # Calculate capacity at this steel level
        Pu_cap = calculate_axial_capacity(b_mm, D_mm, fck, fy, ast_trial)
        Pu_cap_Mu, Mu_cap = calculate_pm_interaction_point(
            b_mm, D_mm, fck, fy, ast_trial, cover_mm
        )

        # Simple interaction check: (Pu/Pu_cap) + (Mu/Mu_cap) <= 1.0
        # This is conservative — proper P-M curve would be more efficient
        if Pu_cap > 0 and Mu_cap > 0:
            interaction = (Pu_kn / Pu_cap) + (Mu_knm / Mu_cap)
        else:
            interaction = 2.0  # Unsafe

        if interaction <= 1.0:
            found = True
            break

        ast_trial += step

    if not found:
        ast_trial = ast_max
        Pu_cap = calculate_axial_capacity(b_mm, D_mm, fck, fy, ast_trial)
        _, Mu_cap = calculate_pm_interaction_point(
            b_mm, D_mm, fck, fy, ast_trial, cover_mm
        )
        interaction = (Pu_kn / Pu_cap + Mu_knm / Mu_cap) if (Pu_cap > 0 and Mu_cap > 0) else 2.0
        errors.append(
            f"Cannot design column within reinforcement limits. "
            f"Interaction ratio = {interaction:.2f} > 1.0 at max steel {ast_max:.0f} mm². "
            "Increase section size."
        )

    # Check reinforcement limits
    rebar_check = check_reinforcement_limits(b_mm, D_mm, ast_trial)
    warnings.extend(rebar_check["warnings"])

    p_percent = (ast_trial / Ag) * 100

    # Dimension warnings
    min_dim = min(b_mm, D_mm)
    if min_dim < _MIN_COLUMN_DIM_MM:
        warnings.append(
            f"Min dimension {min_dim:.0f} mm < {_MIN_COLUMN_DIM_MM:.0f} mm (Cl 26.5.3.1)"
        )

    is_safe = found and len(errors) == 0

    if is_safe:
        remarks = (
            f"Column design OK: Ast = {ast_trial:.0f} mm² ({p_percent:.1f}%), "
            f"Pu_cap = {Pu_cap:.0f} kN, Mu_cap = {Mu_cap:.1f} kN·m. "
            f"Interaction ratio = {interaction:.2f} ≤ 1.0."
        )
    else:
        remarks = (
            f"Column UNSAFE: interaction ratio = {interaction:.2f} > 1.0. "
            "Increase section size or steel."
        )

    inputs = {
        "b_mm": b_mm,
        "D_mm": D_mm,
        "Pu_kn": Pu_kn,
        "Mu_knm": Mu_knm,
        "fck": fck,
        "fy": fy,
        "cover_mm": cover_mm,
    }
    computed = {
        "Ag_mm2": Ag,
        "d_mm": d_mm,
        "e_min_mm": round(e_min, 1),
        "e_actual_mm": round(e_actual, 1),
        "Pu_capacity_kn": round(Pu_cap, 1),
        "Mu_capacity_knm": round(Mu_cap, 1),
        "interaction_ratio": round(interaction, 3),
    }

    return ColumnDesignResult(
        is_safe=is_safe,
        Pu_capacity_kn=round(Pu_cap, 1),
        Mu_capacity_knm=round(Mu_cap, 1),
        ast_required_mm2=round(ast_trial, 0),
        ast_min_mm2=round(ast_min, 0),
        ast_max_mm2=round(ast_max, 0),
        p_percent=round(p_percent, 2),
        utilization=round(interaction, 3),
        e_min_mm=round(e_min, 1),
        remarks=remarks,
        inputs=inputs,
        computed=computed,
        errors=errors,
        warnings=warnings,
    )
