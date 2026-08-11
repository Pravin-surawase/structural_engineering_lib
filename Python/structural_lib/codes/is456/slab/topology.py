# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Physical edge and corner topology for oriented solid rectangular slabs."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real

from structural_lib.codes.is456.slab.models import SlabContractError

__all__ = [
    "CornerLiftCondition",
    "CornerTorsionClass",
    "OrientedSlabPanelGeometry",
    "SlabCorner",
    "SlabEdge",
    "SlabEdgeContinuity",
    "SlabSupportTopology",
    "SlabSupportTopologyKind",
]


def _positive_finite_mm(value: float, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{field_name} must be a real value in mm")
    normalized = float(value)
    if not math.isfinite(normalized) or normalized <= 0.0:
        raise SlabContractError(f"{field_name} must be finite and positive in mm")
    return normalized


class SlabEdge(StrEnum):
    X_MIN = "x_min"
    X_MAX = "x_max"
    Y_MIN = "y_min"
    Y_MAX = "y_max"


class SlabCorner(StrEnum):
    X_MIN_Y_MIN = "x_min_y_min"
    X_MIN_Y_MAX = "x_min_y_max"
    X_MAX_Y_MIN = "x_max_y_min"
    X_MAX_Y_MAX = "x_max_y_max"


class SlabEdgeContinuity(StrEnum):
    CONTINUOUS = "continuous"
    DISCONTINUOUS = "discontinuous"


class CornerLiftCondition(StrEnum):
    RESTRAINED = "restrained"
    FREE_TO_LIFT = "free_to_lift"


class CornerTorsionClass(StrEnum):
    FULL = "full"
    HALF = "half"
    NONE = "none"
    NOT_APPLICABLE_FREE_TO_LIFT = "not_applicable_free_to_lift"


class SlabSupportTopologyKind(StrEnum):
    FOUR_EDGES_CONTINUOUS = "four_edges_continuous"
    ONE_EDGE_DISCONTINUOUS = "one_edge_discontinuous"
    TWO_ADJACENT_EDGES_DISCONTINUOUS = "two_adjacent_edges_discontinuous"
    TWO_OPPOSITE_EDGES_DISCONTINUOUS = "two_opposite_edges_discontinuous"
    THREE_EDGES_DISCONTINUOUS = "three_edges_discontinuous"
    FOUR_EDGES_DISCONTINUOUS_RESTRAINED = "four_edges_discontinuous_restrained"
    SIMPLY_SUPPORTED_CORNERS_FREE = "simply_supported_corners_free"


@dataclass(frozen=True)
class OrientedSlabPanelGeometry:
    """Panel with physical x/y axes; x is explicitly the short-span direction."""

    x_effective_span_mm: float
    y_effective_span_mm: float
    thickness_mm: float

    def __post_init__(self) -> None:
        for name in ("x_effective_span_mm", "y_effective_span_mm", "thickness_mm"):
            object.__setattr__(
                self, name, _positive_finite_mm(getattr(self, name), name)
            )
        if self.x_effective_span_mm > self.y_effective_span_mm:
            raise SlabContractError(
                "x_effective_span_mm must be the explicit short span and cannot exceed y_effective_span_mm"
            )

    @property
    def span_ratio_ly_lx(self) -> float:
        return self.y_effective_span_mm / self.x_effective_span_mm


_CORNER_EDGES = {
    SlabCorner.X_MIN_Y_MIN: (SlabEdge.X_MIN, SlabEdge.Y_MIN),
    SlabCorner.X_MIN_Y_MAX: (SlabEdge.X_MIN, SlabEdge.Y_MAX),
    SlabCorner.X_MAX_Y_MIN: (SlabEdge.X_MAX, SlabEdge.Y_MIN),
    SlabCorner.X_MAX_Y_MAX: (SlabEdge.X_MAX, SlabEdge.Y_MAX),
}


@dataclass(frozen=True)
class SlabSupportTopology:
    """Explicit physical edge continuity and one common corner-lift policy."""

    x_min: SlabEdgeContinuity
    x_max: SlabEdgeContinuity
    y_min: SlabEdgeContinuity
    y_max: SlabEdgeContinuity
    corner_lift_condition: CornerLiftCondition

    def __post_init__(self) -> None:
        for name in ("x_min", "x_max", "y_min", "y_max"):
            value = getattr(self, name)
            if not isinstance(value, SlabEdgeContinuity):
                try:
                    object.__setattr__(self, name, SlabEdgeContinuity(value))
                except (TypeError, ValueError) as exc:
                    raise SlabContractError(
                        f"{name} must declare edge continuity"
                    ) from exc
        if not isinstance(self.corner_lift_condition, CornerLiftCondition):
            try:
                object.__setattr__(
                    self,
                    "corner_lift_condition",
                    CornerLiftCondition(self.corner_lift_condition),
                )
            except (TypeError, ValueError) as exc:
                raise SlabContractError(
                    "corner_lift_condition must be restrained or free_to_lift"
                ) from exc
        if self.corner_lift_condition is CornerLiftCondition.FREE_TO_LIFT and any(
            value is SlabEdgeContinuity.CONTINUOUS
            for value in self.edge_conditions.values()
        ):
            raise SlabContractError(
                "free_to_lift is supported only for the explicit four-edge simply supported topology"
            )

    @property
    def edge_conditions(self) -> dict[SlabEdge, SlabEdgeContinuity]:
        return {
            SlabEdge.X_MIN: self.x_min,
            SlabEdge.X_MAX: self.x_max,
            SlabEdge.Y_MIN: self.y_min,
            SlabEdge.Y_MAX: self.y_max,
        }

    @property
    def kind(self) -> SlabSupportTopologyKind:
        discontinuous = {
            edge
            for edge, condition in self.edge_conditions.items()
            if condition is SlabEdgeContinuity.DISCONTINUOUS
        }
        count = len(discontinuous)
        if count == 0:
            return SlabSupportTopologyKind.FOUR_EDGES_CONTINUOUS
        if count == 1:
            return SlabSupportTopologyKind.ONE_EDGE_DISCONTINUOUS
        if count == 2:
            opposite = discontinuous in (
                {SlabEdge.X_MIN, SlabEdge.X_MAX},
                {SlabEdge.Y_MIN, SlabEdge.Y_MAX},
            )
            return (
                SlabSupportTopologyKind.TWO_OPPOSITE_EDGES_DISCONTINUOUS
                if opposite
                else SlabSupportTopologyKind.TWO_ADJACENT_EDGES_DISCONTINUOUS
            )
        if count == 3:
            return SlabSupportTopologyKind.THREE_EDGES_DISCONTINUOUS
        if self.corner_lift_condition is CornerLiftCondition.FREE_TO_LIFT:
            return SlabSupportTopologyKind.SIMPLY_SUPPORTED_CORNERS_FREE
        return SlabSupportTopologyKind.FOUR_EDGES_DISCONTINUOUS_RESTRAINED

    def corner_torsion_class(self, corner: SlabCorner) -> CornerTorsionClass:
        if not isinstance(corner, SlabCorner):
            corner = SlabCorner(corner)
        if self.corner_lift_condition is CornerLiftCondition.FREE_TO_LIFT:
            return CornerTorsionClass.NOT_APPLICABLE_FREE_TO_LIFT
        adjacent = [self.edge_conditions[edge] for edge in _CORNER_EDGES[corner]]
        discontinuous_count = sum(
            condition is SlabEdgeContinuity.DISCONTINUOUS for condition in adjacent
        )
        if discontinuous_count == 2:
            return CornerTorsionClass.FULL
        if discontinuous_count == 1:
            return CornerTorsionClass.HALF
        return CornerTorsionClass.NONE
