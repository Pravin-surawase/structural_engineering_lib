# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Owner-authorized normalized IS 456 slab coefficient lookup and interpolation."""

from __future__ import annotations

import bisect
import math
from enum import StrEnum

from structural_lib.codes.is456.slab.coefficients import (
    CoefficientMethod,
    OneWayContinuousCoefficientSet,
    TwoWayPanelCoefficientSet,
)
from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.slab.topology import (
    CornerLiftCondition,
    OrientedSlabPanelGeometry,
    SlabEdge,
    SlabEdgeContinuity,
    SlabSupportTopology,
)

__all__ = [
    "OneWayMomentLocation",
    "OneWayShearLocation",
    "resolve_builtin_one_way_continuous_coefficients",
    "resolve_builtin_two_way_panel_coefficients",
]


_OWNER_DECISION = "OWNER_DECISION_2026-08-10_BUILT_IN_SLAB_COEFFICIENTS"
_RATIOS_26 = (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2.0)
_RATIOS_27 = (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.75, 2.0, 2.5, 3.0)


class OneWayMomentLocation(StrEnum):
    END_SPAN_POSITIVE = "end_span_positive"
    INTERIOR_SPAN_POSITIVE = "interior_span_positive"
    NEXT_TO_END_SUPPORT_NEGATIVE = "next_to_end_support_negative"
    OTHER_INTERIOR_SUPPORT_NEGATIVE = "other_interior_support_negative"


class OneWayShearLocation(StrEnum):
    END_SUPPORT = "end_support"
    NEXT_TO_END_SUPPORT_OUTER = "next_to_end_support_outer"
    NEXT_TO_END_SUPPORT_INNER = "next_to_end_support_inner"
    OTHER_INTERIOR_SUPPORT = "other_interior_support"


_TABLE_12_FIXED = {
    OneWayMomentLocation.END_SPAN_POSITIVE: 1 / 12,
    OneWayMomentLocation.INTERIOR_SPAN_POSITIVE: 1 / 16,
    OneWayMomentLocation.NEXT_TO_END_SUPPORT_NEGATIVE: 1 / 10,
    OneWayMomentLocation.OTHER_INTERIOR_SUPPORT_NEGATIVE: 1 / 12,
}
_TABLE_12_NONFIXED = {
    OneWayMomentLocation.END_SPAN_POSITIVE: 1 / 10,
    OneWayMomentLocation.INTERIOR_SPAN_POSITIVE: 1 / 12,
    OneWayMomentLocation.NEXT_TO_END_SUPPORT_NEGATIVE: 1 / 9,
    OneWayMomentLocation.OTHER_INTERIOR_SUPPORT_NEGATIVE: 1 / 9,
}
_TABLE_13_FIXED = {
    OneWayShearLocation.END_SUPPORT: 0.4,
    OneWayShearLocation.NEXT_TO_END_SUPPORT_OUTER: 0.6,
    OneWayShearLocation.NEXT_TO_END_SUPPORT_INNER: 0.55,
    OneWayShearLocation.OTHER_INTERIOR_SUPPORT: 0.5,
}
_TABLE_13_NONFIXED = {
    OneWayShearLocation.END_SUPPORT: 0.45,
    OneWayShearLocation.NEXT_TO_END_SUPPORT_OUTER: 0.6,
    OneWayShearLocation.NEXT_TO_END_SUPPORT_INNER: 0.6,
    OneWayShearLocation.OTHER_INTERIOR_SUPPORT: 0.6,
}


# case -> (short-negative, short-positive, long-negative, long-positive)
_TABLE_26 = {
    1: (
        (0.032, 0.037, 0.043, 0.047, 0.051, 0.053, 0.060, 0.065),
        (0.024, 0.028, 0.032, 0.036, 0.039, 0.041, 0.045, 0.049),
        0.032,
        0.024,
    ),
    2: (
        (0.037, 0.043, 0.048, 0.051, 0.055, 0.057, 0.064, 0.068),
        (0.028, 0.032, 0.036, 0.039, 0.041, 0.044, 0.048, 0.052),
        0.037,
        0.028,
    ),
    3: (
        (0.037, 0.044, 0.052, 0.057, 0.063, 0.067, 0.077, 0.085),
        (0.028, 0.033, 0.039, 0.044, 0.047, 0.051, 0.059, 0.065),
        0.037,
        0.028,
    ),
    4: (
        (0.047, 0.053, 0.060, 0.065, 0.071, 0.075, 0.084, 0.091),
        (0.035, 0.040, 0.045, 0.049, 0.053, 0.056, 0.063, 0.069),
        0.047,
        0.035,
    ),
    5: (
        (0.045, 0.049, 0.052, 0.056, 0.059, 0.060, 0.065, 0.069),
        (0.035, 0.037, 0.040, 0.043, 0.044, 0.045, 0.049, 0.052),
        0.0,
        0.035,
    ),
    6: (
        (0.0,) * 8,
        (0.035, 0.043, 0.051, 0.057, 0.063, 0.068, 0.080, 0.088),
        0.045,
        0.035,
    ),
    7: (
        (0.057, 0.064, 0.071, 0.076, 0.080, 0.084, 0.091, 0.097),
        (0.043, 0.048, 0.053, 0.057, 0.060, 0.064, 0.069, 0.073),
        0.0,
        0.043,
    ),
    8: (
        (0.0,) * 8,
        (0.043, 0.051, 0.059, 0.065, 0.071, 0.076, 0.087, 0.096),
        0.057,
        0.043,
    ),
    9: (
        (0.0,) * 8,
        (0.056, 0.064, 0.072, 0.079, 0.085, 0.089, 0.100, 0.107),
        0.0,
        0.056,
    ),
}
_TABLE_27_X = (0.062, 0.074, 0.084, 0.093, 0.099, 0.104, 0.113, 0.118, 0.122, 0.124)
_TABLE_27_Y = (0.062, 0.061, 0.059, 0.055, 0.051, 0.046, 0.037, 0.029, 0.020, 0.014)


def _weighted_coefficient(
    fixed_load: float,
    nonfixed_load: float,
    fixed_coefficient: float,
    nonfixed_coefficient: float,
) -> float:
    total = fixed_load + nonfixed_load
    if total <= 0.0:
        raise SlabContractError("combined factored load components must be positive")
    return (
        fixed_load * fixed_coefficient + nonfixed_load * nonfixed_coefficient
    ) / total


def resolve_builtin_one_way_continuous_coefficients(
    *,
    factored_dead_and_fixed_imposed_load_kn_per_m2: float,
    factored_nonfixed_imposed_load_kn_per_m2: float,
    positive_location: OneWayMomentLocation | str,
    negative_location: OneWayMomentLocation | str,
    shear_location: OneWayShearLocation | str,
) -> OneWayContinuousCoefficientSet:
    """Resolve equivalent Table 12/13 coefficients for explicit load components."""
    fixed = float(factored_dead_and_fixed_imposed_load_kn_per_m2)
    nonfixed = float(factored_nonfixed_imposed_load_kn_per_m2)
    if (
        not math.isfinite(fixed)
        or fixed < 0.0
        or not math.isfinite(nonfixed)
        or nonfixed < 0.0
    ):
        raise SlabContractError(
            "factored load components must be finite and non-negative"
        )
    positive = OneWayMomentLocation(positive_location)
    negative = OneWayMomentLocation(negative_location)
    shear = OneWayShearLocation(shear_location)
    if positive not in (
        OneWayMomentLocation.END_SPAN_POSITIVE,
        OneWayMomentLocation.INTERIOR_SPAN_POSITIVE,
    ):
        raise SlabContractError("positive_location must select a positive span moment")
    if negative not in (
        OneWayMomentLocation.NEXT_TO_END_SUPPORT_NEGATIVE,
        OneWayMomentLocation.OTHER_INTERIOR_SUPPORT_NEGATIVE,
    ):
        raise SlabContractError(
            "negative_location must select a negative support moment"
        )
    return OneWayContinuousCoefficientSet(
        positive_midspan=_weighted_coefficient(
            fixed, nonfixed, _TABLE_12_FIXED[positive], _TABLE_12_NONFIXED[positive]
        ),
        negative_support=_weighted_coefficient(
            fixed, nonfixed, _TABLE_12_FIXED[negative], _TABLE_12_NONFIXED[negative]
        ),
        shear_support=_weighted_coefficient(
            fixed, nonfixed, _TABLE_13_FIXED[shear], _TABLE_13_NONFIXED[shear]
        ),
        source_reference="IS456_TABLE_12_13",
        source_is_approved=True,
        qualified_acceptance_reference=_OWNER_DECISION,
        qualified_acceptance_acknowledged=True,
        method=CoefficientMethod.BUILT_IN_EXACT,
        table_id="IS456_TABLE_12_13",
        case_id=f"{positive.value}|{negative.value}|{shear.value}",
    )


def _interpolate(
    ratio: float, ratios: tuple[float, ...], values: tuple[float, ...]
) -> tuple[float, tuple[float, float], bool]:
    if not math.isfinite(ratio) or ratio < ratios[0] or ratio > ratios[-1]:
        raise SlabContractError(
            f"aspect ratio must be within the coefficient table bounds {ratios[0]} to {ratios[-1]}"
        )
    if ratio in ratios:
        index = ratios.index(ratio)
        return values[index], (ratio, ratio), False
    upper_index = bisect.bisect_right(ratios, ratio)
    lower_index = upper_index - 1
    lower, upper = ratios[lower_index], ratios[upper_index]
    fraction = (ratio - lower) / (upper - lower)
    value = values[lower_index] + fraction * (values[upper_index] - values[lower_index])
    return value, (lower, upper), True


def _table_26_case(topology: SlabSupportTopology) -> int:
    discontinuous = {
        edge
        for edge, condition in topology.edge_conditions.items()
        if condition is SlabEdgeContinuity.DISCONTINUOUS
    }
    if not discontinuous:
        return 1
    if len(discontinuous) == 1:
        return 2 if next(iter(discontinuous)) in {SlabEdge.Y_MIN, SlabEdge.Y_MAX} else 3
    if len(discontinuous) == 2:
        if discontinuous == {SlabEdge.Y_MIN, SlabEdge.Y_MAX}:
            return 5
        if discontinuous == {SlabEdge.X_MIN, SlabEdge.X_MAX}:
            return 6
        return 4
    if len(discontinuous) == 3:
        continuous = set(SlabEdge) - discontinuous
        return 7 if next(iter(continuous)) in {SlabEdge.X_MIN, SlabEdge.X_MAX} else 8
    return 9


def resolve_builtin_two_way_panel_coefficients(
    *,
    geometry: OrientedSlabPanelGeometry,
    topology: SlabSupportTopology,
) -> TwoWayPanelCoefficientSet:
    """Resolve Table 26 or 27 with exact endpoints and bounded interpolation."""
    if not isinstance(geometry, OrientedSlabPanelGeometry):
        raise SlabContractError("geometry must be OrientedSlabPanelGeometry")
    if not isinstance(topology, SlabSupportTopology):
        raise SlabContractError("topology must be SlabSupportTopology")
    ratio = geometry.span_ratio_ly_lx
    if topology.corner_lift_condition is CornerLiftCondition.FREE_TO_LIFT:
        alpha_x, bounds, interpolated = _interpolate(ratio, _RATIOS_27, _TABLE_27_X)
        alpha_y, y_bounds, y_interpolated = _interpolate(ratio, _RATIOS_27, _TABLE_27_Y)
        if bounds != y_bounds or interpolated != y_interpolated:
            raise SlabContractError("Table 27 interpolation bounds are inconsistent")
        return TwoWayPanelCoefficientSet(
            support_topology_kind=topology.kind,
            alpha_x_negative=0.0,
            alpha_x_positive=alpha_x,
            alpha_y_negative=0.0,
            alpha_y_positive=alpha_y,
            source_reference="IS456_TABLE_27",
            source_is_approved=True,
            qualified_acceptance_reference=_OWNER_DECISION,
            qualified_acceptance_acknowledged=True,
            method=(
                CoefficientMethod.BUILT_IN_INTERPOLATED
                if interpolated
                else CoefficientMethod.BUILT_IN_EXACT
            ),
            table_id="IS456_TABLE_27",
            case_id="simply_supported_four_sides_corners_free",
            aspect_ratio_ly_lx=ratio,
            interpolation_bounds=bounds,
        )
    case = _table_26_case(topology)
    x_negative_values, x_positive_values, y_negative, y_positive = _TABLE_26[case]
    x_negative, bounds, interpolated = _interpolate(
        ratio, _RATIOS_26, x_negative_values
    )
    x_positive, positive_bounds, positive_interpolated = _interpolate(
        ratio, _RATIOS_26, x_positive_values
    )
    if bounds != positive_bounds or interpolated != positive_interpolated:
        raise SlabContractError("Table 26 interpolation bounds are inconsistent")
    return TwoWayPanelCoefficientSet(
        support_topology_kind=topology.kind,
        alpha_x_negative=x_negative,
        alpha_x_positive=x_positive,
        alpha_y_negative=y_negative,
        alpha_y_positive=y_positive,
        source_reference="IS456_TABLE_26",
        source_is_approved=True,
        qualified_acceptance_reference=_OWNER_DECISION,
        qualified_acceptance_acknowledged=True,
        method=(
            CoefficientMethod.BUILT_IN_INTERPOLATED
            if interpolated
            else CoefficientMethod.BUILT_IN_EXACT
        ),
        table_id="IS456_TABLE_26",
        case_id=f"table_26_case_{case}",
        aspect_ratio_ly_lx=ratio,
        interpolation_bounds=bounds,
    )
