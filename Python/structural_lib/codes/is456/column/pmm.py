# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Experimental strain-compatibility analysis for rectangular columns.

This module adds a discrete longitudinal-bar representation and a fiber-based
P-M-M surface without changing the supported Bresler check in :mod:`biaxial`.
Compression is positive. The gross-section centroid is the coordinate origin;
``Mx`` is positive for compression toward ``+y`` and ``My`` follows the
right-handed convention ``My = -sum(F * x)``.

The implementation is an experimental development aid. It is not a substitute
for the prescribed IS 456 Cl. 39.6 biaxial check or professional design review.
"""

from __future__ import annotations

import math

import numpy as np

from structural_lib.codes.is456.common.constants import (
    COLUMN_CONCRETE_COEFF,
    COLUMN_MAX_STEEL_RATIO,
    COLUMN_MIN_STEEL_RATIO,
    COLUMN_STEEL_COEFF,
    EPSILON_C0,
    EPSILON_CU,
    ES_STEEL_MPA,
    STRESS_BLOCK_PEAK,
)
from structural_lib.codes.is456.common.stress_blocks import (
    steel_stress_from_strain_5point,
)
from structural_lib.codes.is456.traceability import clause
from structural_lib.core.data_types import (
    ColumnReinforcementBar,
    ColumnReinforcementLayout,
    PMMInteractionPoint,
    PMMInteractionSlice,
    PMMInteractionSurface,
)
from structural_lib.core.errors import DimensionError, MaterialError
from structural_lib.core.materials import Steel

__all__ = [
    "create_symmetric_two_face_layout",
    "experimental_pmm_interaction_surface",
    "pm_interaction_slice_for_layout",
]

_MIN_FIBERS_PER_AXIS = 8
_MIN_DEPTH_POINTS = 12
_MIN_ANGLES = 4
_AXIAL_TOLERANCE_KN = 1e-6


def create_symmetric_two_face_layout(
    *,
    b_mm: float,
    D_mm: float,
    Asc_mm2: float,
    d_prime_mm: float,
    material: Steel,
    layout_id: str = "SYMMETRIC-TWO-FACE",
) -> ColumnReinforcementLayout:
    """Adapt the legacy symmetric two-face inputs to four corner bars.

    Each face retains ``Asc_mm2 / 2`` at the legacy ``d_prime_mm`` depth.
    Dividing each face into two equal corner bars also provides a defined
    coordinate in the orthogonal direction for experimental P-M-M sampling.
    """
    values = {
        "b_mm": b_mm,
        "D_mm": D_mm,
        "Asc_mm2": Asc_mm2,
        "d_prime_mm": d_prime_mm,
    }
    for name, value in values.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite, got {value}")
    if b_mm <= 0 or D_mm <= 0:
        raise DimensionError(
            f"Column dimensions must be positive, got b_mm={b_mm}, D_mm={D_mm}",
            details={"b_mm": b_mm, "D_mm": D_mm},
            clause_ref="Cl. 39.5",
        )
    if Asc_mm2 <= 0:
        raise DimensionError(
            f"Asc_mm2 must be positive, got {Asc_mm2}",
            details={"Asc_mm2": Asc_mm2},
            clause_ref="Cl. 26.5.3.1",
        )
    if d_prime_mm <= 0 or d_prime_mm >= min(b_mm, D_mm) / 2.0:
        raise DimensionError(
            "d_prime_mm must be positive and inside both section faces",
            details={
                "d_prime_mm": d_prime_mm,
                "b_mm": b_mm,
                "D_mm": D_mm,
            },
            clause_ref="Cl. 26.4",
        )

    x = b_mm / 2.0 - d_prime_mm
    y = D_mm / 2.0 - d_prime_mm
    area = Asc_mm2 / 4.0
    bars = tuple(
        ColumnReinforcementBar(
            x_mm=x_sign * x,
            y_mm=y_sign * y,
            area_mm2=area,
            material=material,
        )
        for y_sign in (-1.0, 1.0)
        for x_sign in (-1.0, 1.0)
    )
    return ColumnReinforcementLayout(bars=bars, layout_id=layout_id)


def _validate_section_and_layout(
    *,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    reinforcement: ColumnReinforcementLayout,
    n_fibers_x: int,
    n_fibers_y: int,
    n_depths: int,
) -> tuple[str, ...]:
    """Validate one rectangular section-analysis contract."""
    if not all(math.isfinite(value) for value in (b_mm, D_mm, fck_nmm2)):
        raise ValueError("b_mm, D_mm, and fck_nmm2 must be finite")
    if b_mm <= 0 or D_mm <= 0:
        raise DimensionError(
            f"Column dimensions must be positive, got b_mm={b_mm}, D_mm={D_mm}",
            details={"b_mm": b_mm, "D_mm": D_mm},
            clause_ref="Cl. 39.5",
        )
    if not 15 <= fck_nmm2 <= 80:
        raise MaterialError(
            f"fck_nmm2 must be within 15-80 N/mm², got {fck_nmm2}",
            details={"fck_nmm2": fck_nmm2},
            clause_ref="Cl. 5.2.1",
        )
    if n_fibers_x < _MIN_FIBERS_PER_AXIS or n_fibers_y < _MIN_FIBERS_PER_AXIS:
        raise ValueError(
            f"n_fibers_x and n_fibers_y must each be >= {_MIN_FIBERS_PER_AXIS}"
        )
    if n_depths < _MIN_DEPTH_POINTS:
        raise ValueError(f"n_depths must be >= {_MIN_DEPTH_POINTS}")

    half_b = b_mm / 2.0
    half_d = D_mm / 2.0
    for index, bar in enumerate(reinforcement.bars):
        if not (-half_b < bar.x_mm < half_b):
            raise DimensionError(
                f"Bar {index} x_mm={bar.x_mm} lies outside the section",
                details={"bar_index": index, "x_mm": bar.x_mm, "b_mm": b_mm},
                clause_ref="Cl. 26.4",
            )
        if not (-half_d < bar.y_mm < half_d):
            raise DimensionError(
                f"Bar {index} y_mm={bar.y_mm} lies outside the section",
                details={"bar_index": index, "y_mm": bar.y_mm, "D_mm": D_mm},
                clause_ref="Cl. 26.4",
            )
        if not 250 <= bar.material.fy <= 550:
            raise MaterialError(
                f"Bar {index} fy={bar.material.fy} must be within 250-550 N/mm²",
                details={"bar_index": index, "fy_nmm2": bar.material.fy},
                clause_ref="Cl. 5.6",
            )
        if not math.isclose(bar.material.Es, ES_STEEL_MPA, rel_tol=0.0, abs_tol=1e-9):
            raise MaterialError(
                "Experimental IS 456 P-M-M analysis currently requires "
                f"Es={ES_STEEL_MPA:.0f} N/mm²; bar {index} has {bar.material.Es}",
                details={"bar_index": index, "es_nmm2": bar.material.Es},
                clause_ref="Cl. 5.6.3",
            )

    gross_area_mm2 = b_mm * D_mm
    steel_ratio = reinforcement.total_area_mm2 / gross_area_mm2
    warnings: list[str] = []
    if steel_ratio < COLUMN_MIN_STEEL_RATIO:
        warnings.append(f"Steel ratio {steel_ratio:.4f} is below 0.8% per Cl. 26.5.3.1")
    if steel_ratio > COLUMN_MAX_STEEL_RATIO:
        warnings.append(f"Steel ratio {steel_ratio:.4f} exceeds the 4% analysis limit")
    return tuple(warnings)


def _concrete_stress_nmm2(strain: np.ndarray, fck_nmm2: float) -> np.ndarray:
    """Return IS 456 design concrete stress for compression-positive strain."""
    positive = np.maximum(strain, 0.0)
    ratio = np.minimum(positive / EPSILON_C0, 1.0)
    parabolic = STRESS_BLOCK_PEAK * fck_nmm2 * (2.0 * ratio - ratio**2)
    return np.where(positive > 0.0, parabolic, 0.0)


def _concrete_stress_scalar(strain: float, fck_nmm2: float) -> float:
    """Scalar counterpart of :func:`_concrete_stress_nmm2`."""
    if strain <= 0.0:
        return 0.0
    ratio = min(strain / EPSILON_C0, 1.0)
    return STRESS_BLOCK_PEAK * fck_nmm2 * (2.0 * ratio - ratio**2)


def _fiber_grid(
    b_mm: float,
    D_mm: float,
    n_fibers_x: int,
    n_fibers_y: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Return cell-center coordinates and equal concrete-fiber area."""
    dx = b_mm / n_fibers_x
    dy = D_mm / n_fibers_y
    x = np.linspace(-b_mm / 2.0 + dx / 2.0, b_mm / 2.0 - dx / 2.0, n_fibers_x)
    y = np.linspace(-D_mm / 2.0 + dy / 2.0, D_mm / 2.0 - dy / 2.0, n_fibers_y)
    x_grid, y_grid = np.meshgrid(x, y, indexing="xy")
    return x_grid.ravel(), y_grid.ravel(), dx * dy


def _section_response(
    *,
    theta_deg: float,
    neutral_axis_depth_mm: float,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    reinforcement: ColumnReinforcementLayout,
    fiber_x_mm: np.ndarray,
    fiber_y_mm: np.ndarray,
    fiber_area_mm2: float,
) -> PMMInteractionPoint:
    """Integrate one linear strain plane over concrete fibers and steel bars."""
    theta_rad = math.radians(theta_deg)
    sin_t = math.sin(theta_rad)
    cos_t = math.cos(theta_rad)
    projected_depth_mm = abs(b_mm * sin_t) + abs(D_mm * cos_t)
    q_max_mm = projected_depth_mm / 2.0
    q_min_mm = q_max_mm - projected_depth_mm

    fiber_q_mm = fiber_x_mm * sin_t + fiber_y_mm * cos_t
    if neutral_axis_depth_mm <= projected_depth_mm:
        q_na_mm = q_max_mm - neutral_axis_depth_mm
        concrete_strain = EPSILON_CU * ((fiber_q_mm - q_na_mm) / neutral_axis_depth_mm)

        def strain_at(q_mm: float) -> float:
            return EPSILON_CU * ((q_mm - q_na_mm) / neutral_axis_depth_mm)

    else:
        # IS 456 Cl. 38.1: modified strain profile when the whole section
        # is in compression and the neutral axis lies beyond the far face.
        far_strain = EPSILON_CU * (
            (neutral_axis_depth_mm - projected_depth_mm) / neutral_axis_depth_mm
        )
        maximum_strain = EPSILON_CU - 0.75 * far_strain
        strain_gradient = (maximum_strain - far_strain) / projected_depth_mm
        concrete_strain = far_strain + strain_gradient * (fiber_q_mm - q_min_mm)

        def strain_at(q_mm: float) -> float:
            return far_strain + strain_gradient * (q_mm - q_min_mm)

    concrete_stress = _concrete_stress_nmm2(concrete_strain, fck_nmm2)
    concrete_force_n = concrete_stress * fiber_area_mm2

    axial_force_n = float(np.sum(concrete_force_n))
    mx_nmm = float(np.sum(concrete_force_n * fiber_y_mm))
    my_nmm = float(-np.sum(concrete_force_n * fiber_x_mm))

    steel_strains: list[float] = []
    for bar in reinforcement.bars:
        bar_q_mm = bar.x_mm * sin_t + bar.y_mm * cos_t
        bar_strain = strain_at(bar_q_mm)
        steel_strains.append(bar_strain)
        steel_stress = steel_stress_from_strain_5point(bar_strain, bar.material.fy)
        displaced_concrete_stress = _concrete_stress_scalar(bar_strain, fck_nmm2)
        net_bar_force_n = (steel_stress - displaced_concrete_stress) * bar.area_mm2
        axial_force_n += net_bar_force_n
        mx_nmm += net_bar_force_n * bar.y_mm
        my_nmm -= net_bar_force_n * bar.x_mm

    return PMMInteractionPoint(
        theta_deg=theta_deg % 360.0,
        neutral_axis_depth_mm=neutral_axis_depth_mm,
        Pu_kN=axial_force_n / 1000.0,
        Mx_kNm=mx_nmm / 1e6,
        My_kNm=my_nmm / 1e6,
        max_concrete_strain=max(float(np.max(concrete_strain)), 0.0),
        min_steel_strain=min(steel_strains),
        max_steel_strain=max(steel_strains),
    )


def _nominal_axial_point(
    *,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    reinforcement: ColumnReinforcementLayout,
) -> PMMInteractionPoint:
    """Return the empirical Cl. 39.3 axial cap with layout eccentricity."""
    concrete_force_n = COLUMN_CONCRETE_COEFF * fck_nmm2 * b_mm * D_mm
    axial_force_n = concrete_force_n
    mx_nmm = 0.0
    my_nmm = 0.0
    for bar in reinforcement.bars:
        net_bar_stress = (
            COLUMN_STEEL_COEFF * bar.material.fy - COLUMN_CONCRETE_COEFF * fck_nmm2
        )
        net_bar_force_n = net_bar_stress * bar.area_mm2
        axial_force_n += net_bar_force_n
        mx_nmm += net_bar_force_n * bar.y_mm
        my_nmm -= net_bar_force_n * bar.x_mm

    return PMMInteractionPoint(
        theta_deg=0.0,
        neutral_axis_depth_mm=None,
        Pu_kN=axial_force_n / 1000.0,
        Mx_kNm=mx_nmm / 1e6,
        My_kNm=my_nmm / 1e6,
        max_concrete_strain=0.0,
        min_steel_strain=0.0,
        max_steel_strain=0.0,
    )


def _zero_axial_intersection(
    first: PMMInteractionPoint,
    second: PMMInteractionPoint,
) -> PMMInteractionPoint | None:
    """Linearly interpolate a Pu=0 point when two samples bracket zero."""
    if first.Pu_kN == 0.0:
        return first
    if second.Pu_kN == 0.0:
        return second
    if first.Pu_kN * second.Pu_kN > 0.0:
        return None
    denominator = second.Pu_kN - first.Pu_kN
    if abs(denominator) <= _AXIAL_TOLERANCE_KN:
        return None
    factor = -first.Pu_kN / denominator

    def interpolate(a: float, b: float) -> float:
        return a + factor * (b - a)

    first_depth = first.neutral_axis_depth_mm or 0.0
    second_depth = second.neutral_axis_depth_mm or 0.0
    return PMMInteractionPoint(
        theta_deg=first.theta_deg,
        neutral_axis_depth_mm=interpolate(first_depth, second_depth),
        Pu_kN=0.0,
        Mx_kNm=interpolate(first.Mx_kNm, second.Mx_kNm),
        My_kNm=interpolate(first.My_kNm, second.My_kNm),
        max_concrete_strain=interpolate(
            first.max_concrete_strain, second.max_concrete_strain
        ),
        min_steel_strain=interpolate(first.min_steel_strain, second.min_steel_strain),
        max_steel_strain=interpolate(first.max_steel_strain, second.max_steel_strain),
    )


@clause("38.1", "39.3", "39.5")
def pm_interaction_slice_for_layout(
    *,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    reinforcement: ColumnReinforcementLayout,
    theta_deg: float = 0.0,
    n_fibers_x: int = 24,
    n_fibers_y: int = 32,
    n_depths: int = 64,
) -> PMMInteractionSlice:
    """Generate one experimental strain-compatibility P-M-M slice.

    Neutral-axis depth is sampled geometrically from ``0.01`` to ``20``
    projected section depths. Points outside the Cl. 39.3 nominal compression
    cap are excluded. The separate nominal axial point is returned by
    :func:`experimental_pmm_interaction_surface`.
    """
    # IS 456 Cl. 38.1/39.5: integrate equilibrium for a linear strain plane.
    _validate_section_and_layout(
        b_mm=b_mm,
        D_mm=D_mm,
        fck_nmm2=fck_nmm2,
        reinforcement=reinforcement,
        n_fibers_x=n_fibers_x,
        n_fibers_y=n_fibers_y,
        n_depths=n_depths,
    )
    if not math.isfinite(theta_deg):
        raise ValueError(f"theta_deg must be finite, got {theta_deg}")

    normalized_theta = theta_deg % 360.0
    theta_rad = math.radians(normalized_theta)
    projected_depth_mm = abs(b_mm * math.sin(theta_rad)) + abs(
        D_mm * math.cos(theta_rad)
    )
    depths_mm = np.geomspace(
        0.01 * projected_depth_mm,
        20.0 * projected_depth_mm,
        n_depths,
    )
    fiber_x_mm, fiber_y_mm, fiber_area_mm2 = _fiber_grid(
        b_mm, D_mm, n_fibers_x, n_fibers_y
    )
    raw_points = [
        _section_response(
            theta_deg=normalized_theta,
            neutral_axis_depth_mm=float(depth_mm),
            b_mm=b_mm,
            D_mm=D_mm,
            fck_nmm2=fck_nmm2,
            reinforcement=reinforcement,
            fiber_x_mm=fiber_x_mm,
            fiber_y_mm=fiber_y_mm,
            fiber_area_mm2=fiber_area_mm2,
        )
        for depth_mm in depths_mm
    ]

    axial_limit_kN = _nominal_axial_point(
        b_mm=b_mm,
        D_mm=D_mm,
        fck_nmm2=fck_nmm2,
        reinforcement=reinforcement,
    ).Pu_kN
    accepted: list[PMMInteractionPoint] = []
    for first, second in zip(raw_points, raw_points[1:], strict=False):
        zero_point = _zero_axial_intersection(first, second)
        if zero_point is not None and not accepted:
            accepted.append(zero_point)
        if -_AXIAL_TOLERANCE_KN <= second.Pu_kN <= axial_limit_kN:
            accepted.append(second)

    if not accepted:
        raise ValueError("No compression-domain interaction points were generated")
    return PMMInteractionSlice(theta_deg=normalized_theta, points=tuple(accepted))


@clause("38.1", "39.3", "39.5")
def experimental_pmm_interaction_surface(
    *,
    b_mm: float,
    D_mm: float,
    fck_nmm2: float,
    reinforcement: ColumnReinforcementLayout,
    n_angles: int = 24,
    n_fibers_x: int = 24,
    n_fibers_y: int = 32,
    n_depths: int = 64,
) -> PMMInteractionSurface:
    """Generate a full 360° experimental P-M-M interaction surface."""
    # IS 456 Cl. 39.3: retain the empirical axial cap for every sampled slice.
    warnings = list(
        _validate_section_and_layout(
            b_mm=b_mm,
            D_mm=D_mm,
            fck_nmm2=fck_nmm2,
            reinforcement=reinforcement,
            n_fibers_x=n_fibers_x,
            n_fibers_y=n_fibers_y,
            n_depths=n_depths,
        )
    )
    if n_angles < _MIN_ANGLES:
        raise ValueError(f"n_angles must be >= {_MIN_ANGLES}")

    angles_deg = np.linspace(0.0, 360.0, n_angles, endpoint=False)
    slices = tuple(
        pm_interaction_slice_for_layout(
            b_mm=b_mm,
            D_mm=D_mm,
            fck_nmm2=fck_nmm2,
            reinforcement=reinforcement,
            theta_deg=float(theta_deg),
            n_fibers_x=n_fibers_x,
            n_fibers_y=n_fibers_y,
            n_depths=n_depths,
        )
        for theta_deg in angles_deg
    )
    warnings.extend(
        (
            "Experimental strain-compatibility surface; retain the supported "
            "Bresler Cl. 39.6 route for production checks.",
            "Rectangular short-column section only; slenderness, confinement, "
            "second-order effects, and detailing are excluded.",
            "The Cl. 39.3 nominal axial point is an empirical cap, not a sampled "
            "fiber strain state.",
        )
    )
    return PMMInteractionSurface(
        b_mm=b_mm,
        D_mm=D_mm,
        fck_nmm2=fck_nmm2,
        reinforcement=reinforcement,
        slices=slices,
        nominal_axial_point=_nominal_axial_point(
            b_mm=b_mm,
            D_mm=D_mm,
            fck_nmm2=fck_nmm2,
            reinforcement=reinforcement,
        ),
        n_fibers_x=n_fibers_x,
        n_fibers_y=n_fibers_y,
        n_depths=n_depths,
        warnings=tuple(warnings),
    )
