# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Bounded IS 13920:2016 strong-column/weak-beam joint check."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum

from structural_lib.codes.is456.traceability import clause
from structural_lib.core.errors import E_SCWB_002, DesignError

__all__ = [
    "ColumnCapacityBasis",
    "JointTopology",
    "PrincipalPlane",
    "SCWBResult",
    "ShakingDirection",
    "check_scwb",
]

_SCWB_FACTOR_IS13920: float = 1.4
_SCWB_REFERENCE = (
    "IS 13920:2016 Cl. 7.2.1-7.2.1.3 with Amendment 1 column-capacity basis"
)
_SCWB_CASE_SCOPE = "ONE_PRINCIPAL_PLANE_ONE_SHAKING_DIRECTION"
_SCWB_APPLICABILITY = "APPLICABLE_NON_ROOF_BEAM_COLUMN_JOINT"


class JointTopology(StrEnum):
    """Supported beam framing topology in the checked principal plane."""

    INTERIOR = "INTERIOR"
    EXTERIOR_LEFT = "EXTERIOR_LEFT"
    EXTERIOR_RIGHT = "EXTERIOR_RIGHT"


class PrincipalPlane(StrEnum):
    """Principal plane for the directional capacity check."""

    X = "X"
    Y = "Y"


class ShakingDirection(StrEnum):
    """Direction of the beam actions used in one SCWB case."""

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"

    def opposite(self) -> ShakingDirection:
        """Return the direction required for the column capacities."""
        if self is ShakingDirection.POSITIVE:
            return ShakingDirection.NEGATIVE
        return ShakingDirection.POSITIVE


class ColumnCapacityBasis(StrEnum):
    """Supported basis for column moment capacities."""

    FACTORED_AXIAL_LOAD = "FACTORED_AXIAL_LOAD"


@dataclass(frozen=True)
class SCWBResult:
    """Result for one applicable principal-plane and shaking-direction case.

    A passing instance is not a complete whole-joint assessment. The caller
    must evaluate both shaking directions in every applicable principal plane.
    """

    topology: JointTopology
    principal_plane: PrincipalPlane
    shaking_direction: ShakingDirection
    beam_capacity_direction: ShakingDirection
    column_capacity_direction: ShakingDirection
    column_capacity_basis: ColumnCapacityBasis
    column_top_factored_axial_load_kn: float
    column_bottom_factored_axial_load_kn: float
    sum_column_capacity_knm: float
    sum_beam_capacity_knm: float
    required_column_capacity_knm: float
    ratio: float
    factor: float
    is_satisfied: bool
    standard: str
    source_reference: str
    applicability: str
    assessment_scope: str
    errors: tuple[DesignError, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def clause(self) -> str:
        """Backward-readable source reference for this bounded result."""
        return self.source_reference

    def is_safe(self) -> bool:
        """Return whether this directional case satisfies the SCWB ratio."""
        return self.is_satisfied

    def to_dict(self) -> dict:
        """Return a JSON-compatible representation of the result."""
        return {
            "topology": self.topology.value,
            "principal_plane": self.principal_plane.value,
            "shaking_direction": self.shaking_direction.value,
            "beam_capacity_direction": self.beam_capacity_direction.value,
            "column_capacity_direction": self.column_capacity_direction.value,
            "column_capacity_basis": self.column_capacity_basis.value,
            "column_top_factored_axial_load_kn": (
                self.column_top_factored_axial_load_kn
            ),
            "column_bottom_factored_axial_load_kn": (
                self.column_bottom_factored_axial_load_kn
            ),
            "sum_column_capacity_knm": self.sum_column_capacity_knm,
            "sum_beam_capacity_knm": self.sum_beam_capacity_knm,
            "required_column_capacity_knm": self.required_column_capacity_knm,
            "ratio": self.ratio,
            "factor": self.factor,
            "is_satisfied": self.is_satisfied,
            "standard": self.standard,
            "source_reference": self.source_reference,
            "clause": self.clause,
            "applicability": self.applicability,
            "assessment_scope": self.assessment_scope,
            "errors": [error.to_dict() for error in self.errors],
            "warnings": list(self.warnings),
        }

    def summary(self) -> str:
        """Return a human-readable directional-case summary."""
        status = "PASS" if self.is_satisfied else "FAIL"
        return (
            f"SCWB directional case ({self.principal_plane.value}, "
            f"{self.shaking_direction.value}, {self.topology.value}): {status} — "
            f"ΣMc={self.sum_column_capacity_knm:.1f} kNm, "
            f"required={self.required_column_capacity_knm:.1f} kNm, "
            f"ratio={self.ratio:.3f}"
        )


def _require_enum(value: object, enum_type: type[StrEnum], field: str) -> None:
    if not isinstance(value, enum_type):
        raise TypeError(f"{field} must be a {enum_type.__name__}")


def _require_bool(value: object, field: str) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{field} must be a bool")


def _require_positive_finite(value: float, field: str) -> None:
    if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{field} must be a finite value > 0, got {value}")


def _require_finite(value: float, field: str) -> None:
    if isinstance(value, bool) or not math.isfinite(value):
        raise ValueError(f"{field} must be finite, got {value}")


def _validate_topology(
    topology: JointTopology,
    beam_left_capacity_knm: float | None,
    beam_right_capacity_knm: float | None,
) -> tuple[float, ...]:
    capacities: tuple[float, ...]
    if topology is JointTopology.INTERIOR:
        if beam_left_capacity_knm is None or beam_right_capacity_knm is None:
            raise ValueError(
                "INTERIOR topology requires left and right beam capacities"
            )
        capacities = (beam_left_capacity_knm, beam_right_capacity_knm)
    elif topology is JointTopology.EXTERIOR_LEFT:
        if beam_left_capacity_knm is None or beam_right_capacity_knm is not None:
            raise ValueError(
                "EXTERIOR_LEFT topology requires only the left beam capacity"
            )
        capacities = (beam_left_capacity_knm,)
    else:
        if beam_left_capacity_knm is not None or beam_right_capacity_knm is None:
            raise ValueError(
                "EXTERIOR_RIGHT topology requires only the right beam capacity"
            )
        capacities = (beam_right_capacity_knm,)

    for index, capacity in enumerate(capacities):
        _require_positive_finite(capacity, f"beam_capacity_knm[{index}]")
    return capacities


@clause("7.2.1", standard="IS 13920")
def check_scwb(
    *,
    column_top_capacity_knm: float,
    column_bottom_capacity_knm: float,
    beam_left_capacity_knm: float | None,
    beam_right_capacity_knm: float | None,
    topology: JointTopology,
    principal_plane: PrincipalPlane,
    shaking_direction: ShakingDirection,
    column_capacity_direction: ShakingDirection,
    column_top_factored_axial_load_kn: float,
    column_bottom_factored_axial_load_kn: float,
    column_capacity_basis: ColumnCapacityBasis,
    is_roof_joint: bool,
    is_flat_slab_system: bool,
) -> SCWBResult:
    """Check one bounded IS 13920 SCWB directional case.

    Beam capacities must act in ``shaking_direction``. Column capacities must
    act in the opposite direction and be evaluated at the provided factored
    axial loads. The fixed IS 13920 requirement is ``ΣMc >= 1.4ΣMb``.

    Roof joints and flat-slab systems do not produce a passing or failing SCWB
    result from this function. Both shaking directions must be checked in every
    applicable principal plane before making a whole-joint assessment.
    """
    _require_enum(topology, JointTopology, "topology")
    _require_enum(principal_plane, PrincipalPlane, "principal_plane")
    _require_enum(shaking_direction, ShakingDirection, "shaking_direction")
    _require_enum(
        column_capacity_direction,
        ShakingDirection,
        "column_capacity_direction",
    )
    _require_enum(
        column_capacity_basis,
        ColumnCapacityBasis,
        "column_capacity_basis",
    )
    _require_bool(is_roof_joint, "is_roof_joint")
    _require_bool(is_flat_slab_system, "is_flat_slab_system")

    if is_flat_slab_system:
        raise ValueError("SCWB check is not supported for flat-slab systems")
    if is_roof_joint:
        raise ValueError("SCWB requirement is waived at roof joints")
    if column_capacity_basis is not ColumnCapacityBasis.FACTORED_AXIAL_LOAD:
        raise ValueError("column capacities must use the factored axial-load basis")

    required_column_direction = shaking_direction.opposite()
    if column_capacity_direction is not required_column_direction:
        raise ValueError(
            "column_capacity_direction must oppose the declared shaking_direction"
        )

    _require_positive_finite(column_top_capacity_knm, "column_top_capacity_knm")
    _require_positive_finite(
        column_bottom_capacity_knm,
        "column_bottom_capacity_knm",
    )
    _require_finite(
        column_top_factored_axial_load_kn,
        "column_top_factored_axial_load_kn",
    )
    _require_finite(
        column_bottom_factored_axial_load_kn,
        "column_bottom_factored_axial_load_kn",
    )
    beam_capacities = _validate_topology(
        topology,
        beam_left_capacity_knm,
        beam_right_capacity_knm,
    )

    sum_column_capacity = column_top_capacity_knm + column_bottom_capacity_knm
    sum_beam_capacity = sum(beam_capacities)
    required_column_capacity = _SCWB_FACTOR_IS13920 * sum_beam_capacity
    ratio = sum_column_capacity / required_column_capacity
    is_satisfied = sum_column_capacity >= required_column_capacity - 1e-9
    errors = () if is_satisfied else (E_SCWB_002,)

    return SCWBResult(
        topology=topology,
        principal_plane=principal_plane,
        shaking_direction=shaking_direction,
        beam_capacity_direction=shaking_direction,
        column_capacity_direction=column_capacity_direction,
        column_capacity_basis=column_capacity_basis,
        column_top_factored_axial_load_kn=column_top_factored_axial_load_kn,
        column_bottom_factored_axial_load_kn=column_bottom_factored_axial_load_kn,
        sum_column_capacity_knm=sum_column_capacity,
        sum_beam_capacity_knm=sum_beam_capacity,
        required_column_capacity_knm=required_column_capacity,
        ratio=ratio,
        factor=_SCWB_FACTOR_IS13920,
        is_satisfied=is_satisfied,
        standard="IS 13920:2016",
        source_reference=_SCWB_REFERENCE,
        applicability=_SCWB_APPLICABILITY,
        assessment_scope=_SCWB_CASE_SCOPE,
        errors=errors,
    )
