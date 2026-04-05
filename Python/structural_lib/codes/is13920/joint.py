# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       codes.is13920.joint
Description:  IS 13920:2016 Beam-Column Joint checks.
Traceability: Functions are decorated with @clause for IS 13920 clause references.

Implements:
- Strong Column Weak Beam (SCWB) check (Cl 7.2.1)

The SCWB requirement ensures that plastic hinges form in beams rather than
columns during seismic events, preventing a storey-level collapse mechanism.

References:
    IS 13920:2016, Cl. 7.2.1
    Pillai & Menon, "Reinforced Concrete Design", 3rd Ed.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from structural_lib.codes.is456.traceability import clause
from structural_lib.core.errors import (
    E_SCWB_002,
    DesignError,
)

__all__ = [
    "SCWBResult",
    "check_scwb",
]

# IS 13920:2016 Cl 7.2.1: Default SCWB factor
_SCWB_FACTOR: float = 1.1


@dataclass(frozen=True)
class SCWBResult:
    """Result of IS 13920:2016 Cl 7.2.1 Strong Column Weak Beam check.

    Attributes:
        sum_column_capacity_knm: ΣMc — sum of column moment capacities at joint (kNm).
        sum_beam_capacity_knm: ΣMb — sum of beam moment capacities at joint (kNm).
        required_column_capacity_knm: factor × ΣMb — minimum required ΣMc (kNm).
        ratio: ΣMc / (factor × ΣMb) — values ≥ 1.0 satisfy the check.
        factor: SCWB factor used (default 1.1 per IS 13920).
        is_satisfied: True if ΣMc ≥ factor × ΣMb.
        clause: IS 13920 clause reference.
        errors: Accumulated design errors (empty tuple if check passes).
        warnings: Any warnings generated.
    """

    sum_column_capacity_knm: float
    sum_beam_capacity_knm: float
    required_column_capacity_knm: float
    ratio: float
    factor: float
    is_satisfied: bool
    clause: str
    errors: tuple[DesignError, ...] = ()
    warnings: tuple[str, ...] = ()

    def is_safe(self) -> bool:
        """Return True if the SCWB check is satisfied."""
        return self.is_satisfied

    def to_dict(self) -> dict:
        """Return a dict representation of the result."""
        return {
            "sum_column_capacity_knm": self.sum_column_capacity_knm,
            "sum_beam_capacity_knm": self.sum_beam_capacity_knm,
            "required_column_capacity_knm": self.required_column_capacity_knm,
            "ratio": self.ratio,
            "factor": self.factor,
            "is_satisfied": self.is_satisfied,
            "clause": self.clause,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return a human-readable summary."""
        status = "PASS" if self.is_satisfied else "FAIL"
        return (
            f"SCWB Check ({self.clause}): {status} — "
            f"ΣMc={self.sum_column_capacity_knm:.1f} kNm, "
            f"required={self.required_column_capacity_knm:.1f} kNm, "
            f"ratio={self.ratio:.3f}"
        )


@clause("7.2.1", standard="IS 13920")
def check_scwb(
    column_moments_top_knm: float,
    column_moments_bottom_knm: float,
    beam_moments_left_knm: float,
    beam_moments_right_knm: float,
    factor: float = _SCWB_FACTOR,
) -> SCWBResult:
    """IS 13920:2016 Cl 7.2.1 — Strong Column Weak Beam (SCWB) check.

    At every beam-column joint, the sum of the moment capacities of the
    columns framing into the joint must be at least ``factor`` times the
    sum of the moment capacities of the beams framing into the joint:

        ΣMc ≥ factor × ΣMb

    This ensures that plastic hinges develop in beams (ductile) rather
    than columns (brittle storey mechanism).

    Args:
        column_moments_top_knm: Moment capacity of column above joint (kNm).
        column_moments_bottom_knm: Moment capacity of column below joint (kNm).
        beam_moments_left_knm: Moment capacity of beam to left of joint (kNm).
        beam_moments_right_knm: Moment capacity of beam to right of joint (kNm).
        factor: SCWB factor (default 1.1 per IS 13920:2016 Cl 7.2.1).

    Returns:
        SCWBResult with check outcome, ratio, and any errors.

    Raises:
        ValueError: If any moment capacity is negative or zero, or factor ≤ 0.

    References:
        IS 13920:2016, Cl. 7.2.1
    """
    # ------------------------------------------------------------------
    # Input validation — all moment capacities must be positive
    # ------------------------------------------------------------------
    errors: list[DesignError] = []

    if column_moments_top_knm <= 0:
        raise ValueError(
            f"column_moments_top_knm must be > 0, got {column_moments_top_knm}"
        )
    if column_moments_bottom_knm <= 0:
        raise ValueError(
            f"column_moments_bottom_knm must be > 0, got {column_moments_bottom_knm}"
        )
    if beam_moments_left_knm <= 0:
        raise ValueError(
            f"beam_moments_left_knm must be > 0, got {beam_moments_left_knm}"
        )
    if beam_moments_right_knm <= 0:
        raise ValueError(
            f"beam_moments_right_knm must be > 0, got {beam_moments_right_knm}"
        )
    if factor <= 0:
        raise ValueError(f"factor must be > 0, got {factor}")

    # ------------------------------------------------------------------
    # IS 13920:2016 Cl 7.2.1: ΣMc ≥ factor × ΣMb
    # ------------------------------------------------------------------
    # IS 13920 Cl 7.2.1: ΣMc = Mc_top + Mc_bottom
    sum_mc = column_moments_top_knm + column_moments_bottom_knm

    # IS 13920 Cl 7.2.1: ΣMb = Mb_left + Mb_right
    sum_mb = beam_moments_left_knm + beam_moments_right_knm

    # IS 13920 Cl 7.2.1: required = factor × ΣMb
    required = factor * sum_mb

    # IS 13920 Cl 7.2.1: ratio = ΣMc / (factor × ΣMb)
    # required > 0 is guaranteed since all inputs are > 0 and factor > 0
    ratio = sum_mc / required

    # IS 13920 Cl 7.2.1: ΣMc ≥ factor × ΣMb
    is_satisfied = sum_mc >= required - 1e-9  # tolerance for floating point

    # Guard against NaN/Inf
    if math.isnan(ratio) or math.isinf(ratio):
        raise ValueError(
            f"Numerical error: ratio={ratio} (ΣMc={sum_mc}, required={required})"
        )

    if not is_satisfied:
        errors.append(E_SCWB_002)

    return SCWBResult(
        sum_column_capacity_knm=sum_mc,
        sum_beam_capacity_knm=sum_mb,
        required_column_capacity_knm=required,
        ratio=ratio,
        factor=factor,
        is_satisfied=is_satisfied,
        clause="IS 13920:2016 Cl 7.2.1",
        errors=tuple(errors),
    )
