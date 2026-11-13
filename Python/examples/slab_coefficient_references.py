"""Replay the frozen B02 continuous strip and B04 restrained panel cases."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any

from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.services.api import (
    design_continuous_one_way_slab_builtin_is456,
    design_continuous_one_way_slab_is456,
    design_two_way_slab_panel_builtin_is456,
    design_two_way_slab_panel_is456,
)

CASES = (
    "b02-external",
    "b02-builtin",
    "b02-redistribution",
    "b04-external",
    "b04-builtin",
    "b04-topology-conflict",
    "b04-capacity-fail",
)


def reviewed_serviceability(
    case_id: str, base_limit: float, modification: float
) -> dict[str, Any]:
    return {
        "reviewed_base_span_depth_limit": base_limit,
        "reviewed_aggregate_modification_factor": modification,
        "serviceability_limit_source_reference": f"NPTEL-{case_id}-SLS",
        "serviceability_limit_source_is_approved": True,
        "qualified_serviceability_acceptance_reference": f"example-review:{case_id}-SLS",
        "qualified_serviceability_acceptance_acknowledged": True,
    }


def reviewed_coefficients(case_id: str) -> dict[str, Any]:
    return {
        "coefficient_source_reference": f"NPTEL-{case_id}",
        "coefficient_source_is_approved": True,
        "qualified_coefficient_acceptance_reference": f"example-review:{case_id}",
        "qualified_coefficient_acceptance_acknowledged": True,
    }


def b02_request(case: str) -> dict[str, Any]:
    request = {
        "short_effective_span_mm": 3000,
        "long_effective_span_mm": 7500,
        "thickness_mm": 140,
        "d_mm": 115,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
        "number_of_spans": 3,
        "maximum_span_variation_percent": 0,
        "uniform_cross_section_acknowledged": True,
        "substantially_uniform_load_acknowledged": True,
        "redistribution_applied": case == "b02-redistribution",
        "positive_bar_diameter_mm": 8,
        "positive_bar_spacing_mm": 180,
        "negative_bar_diameter_mm": 10,
        "negative_bar_spacing_mm": 230,
        "distribution_bar_diameter_mm": 8,
        "distribution_bar_spacing_mm": 250,
        **reviewed_serviceability("L18-B02", 23, 1.18),
    }
    if case == "b02-builtin":
        request.update(
            factored_dead_and_fixed_imposed_load_kn_per_m2=14.25,
            factored_nonfixed_imposed_load_kn_per_m2=0,
            positive_location="end_span_positive",
            negative_location="next_to_end_support_negative",
            shear_location="end_support",
        )
    else:
        request.update(
            factored_area_load_kn_per_m2=14.25,
            positive_moment_coefficient=1 / 12,
            negative_moment_coefficient=1 / 10,
            shear_coefficient=0.4,
            **reviewed_coefficients("L18-B02"),
        )
    return request


def b04_request(case: str) -> dict[str, Any]:
    request = {
        "x_effective_span_mm": 4000,
        "y_effective_span_mm": 6000,
        "thickness_mm": 160,
        "x_min_edge": "discontinuous",
        "x_max_edge": "continuous",
        "y_min_edge": "discontinuous",
        "y_max_edge": "continuous",
        "corner_lift_condition": "restrained",
        "factored_area_load_kn_per_m2": 100 if case == "b04-capacity-fail" else 15.5,
        "d_x_mm": 135,
        "d_y_mm": 125,
        "fck_n_per_mm2": 20,
        "fy_n_per_mm2": 415,
        "x_positive_bar_diameter_mm": 10,
        "x_positive_bar_spacing_mm": 200,
        "x_negative_bar_diameter_mm": 10,
        "x_negative_bar_spacing_mm": 200,
        "y_positive_bar_diameter_mm": 8,
        "y_positive_bar_spacing_mm": 200,
        "y_negative_bar_diameter_mm": 8,
        "y_negative_bar_spacing_mm": 200,
        "edge_strip_bar_diameter_mm": 8,
        "edge_strip_bar_spacing_mm": 250,
        "torsion_bar_diameter_mm": 8,
        "torsion_bar_spacing_mm": 200,
        **reviewed_serviceability("L19-B04", 30, 1),
    }
    if case != "b04-builtin":
        request.update(
            support_topology_kind=(
                "four_edges_continuous"
                if case == "b04-topology-conflict"
                else "two_adjacent_edges_discontinuous"
            ),
            alpha_x_negative=0.075,
            alpha_x_positive=0.056,
            alpha_y_negative=0.047,
            alpha_y_positive=0.035,
            **reviewed_coefficients("L19-B04"),
        )
    return request


def run_case(case: str) -> dict[str, Any]:
    if case.startswith("b02-"):
        request = b02_request(case)
        design = (
            design_continuous_one_way_slab_builtin_is456
            if case == "b02-builtin"
            else design_continuous_one_way_slab_is456
        )
    else:
        request = b04_request(case)
        design = (
            design_two_way_slab_panel_builtin_is456
            if case == "b04-builtin"
            else design_two_way_slab_panel_is456
        )

    try:
        result = design(**request)
    except SlabContractError as error:
        if case not in {"b02-redistribution", "b04-topology-conflict"}:
            raise
        return {"case": case, "request": request, "rejection": str(error)}
    return {"case": case, "request": request, "result": asdict(result)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, default="b02-builtin")
    args = parser.parse_args()
    print(json.dumps(run_case(args.case), allow_nan=False, sort_keys=True))


if __name__ == "__main__":
    main()
