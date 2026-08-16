# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Shared rectangular stress-block arithmetic for bounded slab flexure slices."""

from __future__ import annotations

from structural_lib.codes.is456.common.stress_blocks import (
    calculate_ast_from_rectangular_stress_block as _calculate_ast_from_rectangular_stress_block,
)
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
    try:
        return _calculate_ast_from_rectangular_stress_block(
            b_mm=b_mm,
            d_mm=d_mm,
            factored_moment_knm=factored_moment_knm,
            fck_n_per_mm2=fck_n_per_mm2,
            fy_n_per_mm2=fy_n_per_mm2,
        )
    except ValueError as exc:
        raise SlabContractError(
            "factored moment is outside the P7 rectangular stress-block domain"
        ) from exc
