#!/usr/bin/env python3
"""Run the bounded concentric isolated-footing reference fixture.

This is a worked software example, not a foundation design or an engineering
approval.  Its ``EXAMPLE-ONLY`` evidence identifiers are fictional fixture
labels.  The explicit approval booleans exercise the public input contract;
they do not establish soil, cover, frustum-geometry, material, or project
review evidence for a real structure.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
from typing import Any

import structural_lib
from structural_lib.core.data_types import FootingType

_CASES = ("baseline", "transfer-fail", "assumption-hold")


def request_for(case: str) -> dict[str, Any]:
    """Return one HTTP-shaped, flat reference request.

    ``footing_type`` is the transport enum-name string and the permitted bar
    diameters are a JSON list. ``run_case`` converts those two values to the
    public Python input types without changing the supplied evidence fields.
    """
    request: dict[str, Any] = {
        "case_id": "FOOT-INDIA-1C-SQ-001",
        "service_axial_load_kN": 800.0,
        "service_load_combination_id": "SLS-GRAVITY-01",
        "service_load_basis": "includes_footing_self_weight_and_overburden",
        "service_load_origin": "provided",
        "factored_axial_load_kN": 1_200.0,
        "factored_load_combination_id": "ULS-GRAVITY-01",
        "allowable_soil_pressure_kPa": 200.0,
        "allowable_soil_pressure_source_reference": (
            "EXAMPLE-ONLY-GEO-REPORT-001-NOT-REAL-APPROVAL"
        ),
        "allowable_soil_pressure_origin": "verified",
        "allowable_soil_pressure_is_externally_approved": True,
        "footing_type": "ISOLATED_SQUARE",
        "column_L_mm": 400.0,
        "column_B_mm": 400.0,
        "minimum_overall_thickness_mm": 500.0,
        "maximum_overall_thickness_mm": 500.0,
        "thickness_increment_mm": 50.0,
        "effective_depth_offset_L_mm": 100.0,
        "effective_depth_offset_B_mm": 100.0,
        "footing_concrete_fck_nmm2": 25.0,
        "column_concrete_fck_nmm2": 25.0,
        "steel_fy_nmm2": 415.0,
        "effective_supporting_area_A1_mm2": 640_000.0,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_origin": "provided",
        "effective_supporting_area_is_approved": True,
        "dowel_count": 4,
        "dowel_diameter_mm": 20.0,
        "column_longitudinal_bar_diameter_mm": 20.0,
        "available_dowel_development_length_into_footing_mm": 1_000.0,
        "available_dowel_development_length_into_column_mm": 1_000.0,
        "nominal_cover_mm": 50.0,
        "cover_exposure_basis": "EXAMPLE-ONLY-SEVERE-FOOTING-SCHEDULE",
        "cover_exposure_basis_is_approved": True,
        "nominal_max_aggregate_size_mm": 20.0,
        "lower_bottom_bar_direction": "L",
        "upper_bottom_bar_direction": "B",
        "permitted_bottom_bar_diameters_mm": [12, 16, 20, 25, 32],
        "footing_bottom_bar_type": "deformed",
    }
    if case == "transfer-fail":
        request["dowel_diameter_mm"] = 10.0
    elif case == "assumption-hold":
        request["allowable_soil_pressure_origin"] = "assumed"
    elif case != "baseline":
        raise ValueError(f"case must be one of {_CASES}, got {case!r}")
    return request


def _public_input(
    flat_request: dict[str, Any],
) -> structural_lib.ConcentricIsolatedFootingInput:
    values = dict(flat_request)
    values["footing_type"] = FootingType[values["footing_type"]]
    values["permitted_bottom_bar_diameters_mm"] = tuple(
        values["permitted_bottom_bar_diameters_mm"]
    )
    return structural_lib.ConcentricIsolatedFootingInput(**values)


def _require_finite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("example result contains a non-finite number")
    if isinstance(value, dict):
        for item in value.values():
            _require_finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _require_finite(item)


def run_case(case: str) -> dict[str, Any]:
    """Calculate one reference/control case through the public package API."""
    flat_request = request_for(case)
    result = structural_lib.design_concentric_isolated_footing_is456(
        _public_input(flat_request)
    )
    payload = {
        "case": case,
        "request": flat_request,
        "result": dataclasses.asdict(result),
    }
    _require_finite(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=_CASES, default="baseline")
    args = parser.parse_args()
    print(json.dumps(run_case(args.case), allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
