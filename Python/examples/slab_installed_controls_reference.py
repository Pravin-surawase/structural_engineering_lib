#!/usr/bin/env python3
"""Replay the released regular-interior flat-slab controls from an installed package."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, replace

import structural_lib
from structural_lib.codes.is456.flat_slab import (
    FlatSlabAnalysisMethod,
    FlatSlabContractError,
    FlatSlabDirectionDetailingInput,
    FlatSlabGravityLoad,
    FlatSlabGridGeometry,
    FlatSlabMaterial,
    FlatSlabPanelInput,
    FlatSlabPanelLocation,
)
from structural_lib.codes.is456.slab.detailing import ProvidedSlabBars
from structural_lib.services import api as services_api

CASES = (
    "flat-regular-pass",
    "flat-reinforcement-fail",
    "flat-punching-fail",
    "flat-opening-refusal",
    "flat-exterior-refusal",
)


def _panel(
    *,
    dead_load: float = 9.0,
    live_load: float = 4.0,
    factored_load: float = 19.5,
    **geometry_overrides: object,
) -> FlatSlabPanelInput:
    geometry = {
        "centre_to_centre_span_x_mm": 6000.0,
        "centre_to_centre_span_y_mm": 6000.0,
        "continuous_span_count_x": 3,
        "continuous_span_count_y": 3,
        "column_width_x_mm": 500.0,
        "column_width_y_mm": 500.0,
        "overall_depth_mm": 300.0,
        "conservative_effective_depth_mm": 260.0,
        "analysis_method": FlatSlabAnalysisMethod.DIRECT_DESIGN,
        "panel_location": FlatSlabPanelLocation.INTERIOR,
        "all_spans_equal_x": True,
        "all_spans_equal_y": True,
        "columns_offset_from_grid": False,
        "solid_slab": True,
        "drop_present": False,
        "column_head_present": False,
        "marginal_beam_or_wall_present": False,
        "openings_present": False,
        "geometry_basis_reference": "INDIA-2-FLAT-HAND-01-GEOMETRY",
    }
    geometry.update(geometry_overrides)
    return FlatSlabPanelInput(
        geometry=FlatSlabGridGeometry(**geometry),
        material=FlatSlabMaterial(30.0, 500.0, True, "INDIA-2-FLAT-HAND-01-MATERIAL"),
        gravity_load=FlatSlabGravityLoad(
            dead_load,
            live_load,
            factored_load,
            True,
            True,
            False,
            False,
            True,
            "INDIA-2-FLAT-HAND-01-LOAD",
        ),
    )


def _direction() -> FlatSlabDirectionDetailingInput:
    return FlatSlabDirectionDetailingInput(
        ProvidedSlabBars(12.0, 160.0),
        ProvidedSlabBars(10.0, 200.0),
        ProvidedSlabBars(10.0, 200.0),
        ProvidedSlabBars(10.0, 200.0),
        1650.0,
    )


def _flat_request(*, panel: FlatSlabPanelInput | None = None, **overrides: object):
    selected = panel or _panel()
    values: dict[str, object] = {
        "case_id": "INDIA-2-FLAT-HAND-01",
        "panel": selected,
        "x": _direction(),
        "y": _direction(),
        "factored_support_reaction_kn": selected.gravity_load.factored_uniform_load_kn_per_m2
        * 36.0,
        "straight_bars_only": True,
        "all_bottom_bars_continuous": True,
        "splices_present": False,
        "serviceability_acceptance_acknowledged": True,
        "centred_concentric_reaction": True,
        "full_critical_perimeter_available": True,
        "no_punching_reinforcement_provided": True,
        "qualified_review_required": True,
        "detailing_basis_reference": "INDIA-2-FLAT-HAND-01-DETAILING",
        "serviceability_acceptance_reference": "INDIA-2-FLAT-G0-REVIEWED-SPAN-DEPTH",
        "support_reaction_basis_reference": "INDIA-2-FLAT-HAND-01-REACTION",
        "punching_basis_reference": "INDIA-2-FLAT-HAND-01-PUNCHING",
    }
    values.update(overrides)
    return services_api.RegularInteriorFlatSlabDesignInput(**values)


def run_case(case: str) -> dict:
    if case == "flat-regular-pass":
        result = structural_lib.design_regular_interior_flat_slab_is456(_flat_request())
        return {"case": case, "result": asdict(result)}
    if case == "flat-reinforcement-fail":
        direction = replace(
            _direction(), column_strip_negative_bars=ProvidedSlabBars(12.0, 200.0)
        )
        result = structural_lib.design_regular_interior_flat_slab_is456(
            _flat_request(x=direction)
        )
        return {"case": case, "result": asdict(result)}
    if case == "flat-punching-fail":
        result = structural_lib.design_regular_interior_flat_slab_is456(
            _flat_request(
                panel=_panel(dead_load=16.0, live_load=5.0, factored_load=31.5)
            )
        )
        return {"case": case, "result": asdict(result)}
    if case in {"flat-opening-refusal", "flat-exterior-refusal"}:
        field, value = (
            ("openings_present", True)
            if case.endswith("opening-refusal")
            else ("panel_location", "exterior")
        )
        try:
            _panel(**{field: value})
        except FlatSlabContractError as error:
            return {"case": case, "rejection": str(error)}
        raise AssertionError("flat-slab boundary was accepted")
    raise ValueError(case)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=CASES, default="flat-regular-pass")
    args = parser.parse_args()
    print(json.dumps(run_case(args.case), allow_nan=False, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
