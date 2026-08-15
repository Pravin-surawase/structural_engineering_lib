# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Self-weight and three-segment actions for the INDIA-2 staircase case."""

from __future__ import annotations

from dataclasses import dataclass

from structural_lib.codes.is456.staircase.geometry import (
    StraightFlightGeometryResult,
    resolve_straight_flight_geometry,
)
from structural_lib.codes.is456.staircase.models import (
    StaircaseContractError,
    StraightFlightActionInput,
)
from structural_lib.codes.is456.traceability import clause

__all__ = ["StraightFlightActionResult", "analyze_straight_flight_actions"]


_SOURCE_REFS = (
    "IS 456:2000 Cl. 33.1-33.3",
    "NPTEL-M9L20-EX9.1",
    "ACTIONS: caller-supplied superimposed loads and load factor; no IS 875 generation",
)


@dataclass(frozen=True)
class StraightFlightActionResult:
    """Self-weight, piecewise loads, reactions, shear, and sagging moment."""

    input: StraightFlightActionInput
    geometry: StraightFlightGeometryResult
    waist_self_weight_kn_per_m2: float
    step_self_weight_kn_per_m2: float
    landing_self_weight_kn_per_m2: float
    flight_service_load_kn_per_m2: float
    lower_landing_factored_load_kn_per_m2: float
    flight_factored_load_kn_per_m2: float
    upper_landing_factored_load_kn_per_m2: float
    total_factored_load_kn: float
    lower_support_reaction_kn: float
    upper_support_reaction_kn: float
    maximum_factored_shear_kn: float
    maximum_factored_shear_kn_per_m: float
    maximum_moment_location_mm: float
    maximum_factored_moment_knm: float
    maximum_factored_moment_knm_per_m: float
    segment_boundary_moments_knm: tuple[float, float]
    equilibrium_residual_kn: float
    source_refs: tuple[str, ...]
    load_generation_status: str = "not_generated_caller_supplied_actions"


def _moment_at_m(
    x_m: float,
    lower_reaction_kn: float,
    segment_lengths_m: tuple[float, float, float],
    segment_line_loads_kn_per_m: tuple[float, float, float],
) -> float:
    """Return sagging moment at horizontal coordinate ``x_m`` in kNm."""
    moment_knm = lower_reaction_kn * x_m
    segment_start_m = 0.0
    for length_m, line_load_kn_per_m in zip(
        segment_lengths_m, segment_line_loads_kn_per_m, strict=True
    ):
        loaded_length_m = min(max(x_m - segment_start_m, 0.0), length_m)
        if loaded_length_m > 0.0:
            resultant_kn = line_load_kn_per_m * loaded_length_m
            centroid_m = segment_start_m + loaded_length_m / 2.0
            moment_knm -= resultant_kn * (x_m - centroid_m)
        segment_start_m += length_m
    return moment_knm


@clause("33.1", "33.2", "33.3")
def analyze_straight_flight_actions(
    design_input: StraightFlightActionInput,
) -> StraightFlightActionResult:
    """Analyze three contiguous UDL segments over one simply supported span.

    Concrete self-weight is calculated explicitly. Superimposed actions,
    landing shares, and the ultimate factor remain caller-supplied provenance.
    """
    if not isinstance(design_input, StraightFlightActionInput):
        raise StaircaseContractError("design_input must be a StraightFlightActionInput")
    geometry = resolve_straight_flight_geometry(design_input.geometry)
    raw_geometry = design_input.geometry
    loads = design_input.loads
    concrete_unit_weight = loads.concrete_unit_weight_kn_per_m3

    waist_self_weight = (
        concrete_unit_weight
        * raw_geometry.waist_thickness_mm
        / 1000.0
        * geometry.slope_factor
    )
    step_self_weight = concrete_unit_weight * raw_geometry.riser_mm / 2000.0
    landing_self_weight = (
        concrete_unit_weight * raw_geometry.landing_thickness_mm / 1000.0
    )
    flight_service_load = (
        waist_self_weight
        + step_self_weight
        + loads.flight_superimposed_service_load_kn_per_m2
    )
    lower_factored_load = (
        (landing_self_weight + loads.lower_landing_superimposed_service_load_kn_per_m2)
        * loads.lower_landing_load_share
        * loads.ultimate_load_factor
    )
    flight_factored_load = flight_service_load * loads.ultimate_load_factor
    upper_factored_load = (
        (landing_self_weight + loads.upper_landing_superimposed_service_load_kn_per_m2)
        * loads.upper_landing_load_share
        * loads.ultimate_load_factor
    )

    segment_lengths_m = (
        raw_geometry.lower_landing_effective_length_mm / 1000.0,
        raw_geometry.going_mm / 1000.0,
        raw_geometry.upper_landing_effective_length_mm / 1000.0,
    )
    width_m = raw_geometry.flight_width_mm / 1000.0
    segment_line_loads: tuple[float, float, float] = (
        lower_factored_load * width_m,
        flight_factored_load * width_m,
        upper_factored_load * width_m,
    )
    segment_resultants = tuple(
        line_load * length
        for line_load, length in zip(segment_line_loads, segment_lengths_m, strict=True)
    )
    total_span_m = geometry.effective_span_mm / 1000.0
    total_factored_load = sum(segment_resultants)
    moment_about_lower_knm = 0.0
    segment_start_m = 0.0
    for resultant_kn, length_m in zip(
        segment_resultants, segment_lengths_m, strict=True
    ):
        moment_about_lower_knm += resultant_kn * (segment_start_m + length_m / 2.0)
        segment_start_m += length_m
    upper_reaction = moment_about_lower_knm / total_span_m
    lower_reaction = total_factored_load - upper_reaction

    cumulative_load_kn = 0.0
    segment_start_m = 0.0
    maximum_moment_location_m: float | None = None
    for length_m, line_load_kn_per_m, resultant_kn in zip(
        segment_lengths_m,
        segment_line_loads,
        segment_resultants,
        strict=True,
    ):
        if cumulative_load_kn + resultant_kn >= lower_reaction:
            maximum_moment_location_m = (
                segment_start_m
                + (lower_reaction - cumulative_load_kn) / line_load_kn_per_m
            )
            break
        cumulative_load_kn += resultant_kn
        segment_start_m += length_m
    if maximum_moment_location_m is None:
        raise StaircaseContractError(
            "factored segment loads did not produce an internal zero-shear point"
        )

    maximum_moment = _moment_at_m(
        maximum_moment_location_m,
        lower_reaction,
        segment_lengths_m,
        segment_line_loads,
    )
    first_boundary_m = segment_lengths_m[0]
    second_boundary_m = segment_lengths_m[0] + segment_lengths_m[1]
    boundary_moments = (
        _moment_at_m(
            first_boundary_m,
            lower_reaction,
            segment_lengths_m,
            segment_line_loads,
        ),
        _moment_at_m(
            second_boundary_m,
            lower_reaction,
            segment_lengths_m,
            segment_line_loads,
        ),
    )
    maximum_shear = max(lower_reaction, upper_reaction)
    equilibrium_residual = lower_reaction + upper_reaction - total_factored_load

    return StraightFlightActionResult(
        input=design_input,
        geometry=geometry,
        waist_self_weight_kn_per_m2=waist_self_weight,
        step_self_weight_kn_per_m2=step_self_weight,
        landing_self_weight_kn_per_m2=landing_self_weight,
        flight_service_load_kn_per_m2=flight_service_load,
        lower_landing_factored_load_kn_per_m2=lower_factored_load,
        flight_factored_load_kn_per_m2=flight_factored_load,
        upper_landing_factored_load_kn_per_m2=upper_factored_load,
        total_factored_load_kn=total_factored_load,
        lower_support_reaction_kn=lower_reaction,
        upper_support_reaction_kn=upper_reaction,
        maximum_factored_shear_kn=maximum_shear,
        maximum_factored_shear_kn_per_m=maximum_shear / width_m,
        maximum_moment_location_mm=maximum_moment_location_m * 1000.0,
        maximum_factored_moment_knm=maximum_moment,
        maximum_factored_moment_knm_per_m=maximum_moment / width_m,
        segment_boundary_moments_knm=boundary_moments,
        equilibrium_residual_kn=equilibrium_residual,
        source_refs=_SOURCE_REFS + (loads.load_basis_reference,),
    )
