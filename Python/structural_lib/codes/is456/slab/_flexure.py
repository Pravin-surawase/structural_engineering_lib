# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Shared rectangular stress-block arithmetic for bounded slab flexure slices."""

from __future__ import annotations

import math

from structural_lib.codes.is456.slab.models import SlabContractError


def calculate_ast_from_rectangular_stress_block(
    *,
    b_mm: float,
    d_mm: float,
    factored_moment_knm: float,
    fck_n_per_mm2: float,
    fy_n_per_mm2: float,
) -> tuple[float, float]:
    """Solve the canonical P7 rectangular stress-block quadratic.

    All terms use N and mm after the input moment is converted from kN m to
    N mm.  The smaller physical root is returned as ``(Ast_mm2, xu_mm)``.
    Capacity against the applicable limiting neutral-axis ratio remains the
    responsibility of each caller because it is directional for two-way slabs.
    """
    moment_nmm = factored_moment_knm * 1_000_000.0
    normalized_moment = moment_nmm / (fck_n_per_mm2 * b_mm * d_mm * d_mm)
    discriminant = 1.0 - (4.0 * 0.42 / 0.36) * normalized_moment
    if discriminant < 0.0:
        raise SlabContractError(
            "factored moment is outside the P7 rectangular stress-block domain"
        )

    xu_over_d = (1.0 - math.sqrt(discriminant)) / (2.0 * 0.42)
    neutral_axis_depth_mm = xu_over_d * d_mm
    ast_required_mm2 = (0.36 * fck_n_per_mm2 * b_mm * neutral_axis_depth_mm) / (
        0.87 * fy_n_per_mm2
    )
    return ast_required_mm2, neutral_axis_depth_mm
