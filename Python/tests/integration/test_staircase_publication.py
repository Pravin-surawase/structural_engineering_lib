"""Public-contract proof for the composed straight-flight staircase route."""

from __future__ import annotations

import dataclasses
import json

import pytest

import structural_lib
from structural_lib.codes.is456.staircase import StaircaseDesignStatus
from structural_lib.design.is456 import staircase as staircase_facade
from structural_lib.services import api as services_api


def _benchmark_request(
    **overrides: object,
) -> services_api.StraightFlightStaircaseInput:
    values: dict[str, object] = {
        "case_id": "STAIR-INDIA-2-NPTEL-EX9.1",
        "lower_landing_effective_length_mm": 750.0,
        "going_mm": 2700.0,
        "upper_landing_effective_length_mm": 1650.0,
        "flight_width_mm": 1500.0,
        "riser_mm": 160.0,
        "tread_mm": 270.0,
        "waist_thickness_mm": 250.0,
        "landing_thickness_mm": 200.0,
        "lower_landing_superimposed_service_load_kn_per_m2": 6.0,
        "flight_superimposed_service_load_kn_per_m2": 6.0,
        "upper_landing_superimposed_service_load_kn_per_m2": 6.0,
        "lower_landing_load_share": 0.5,
        "upper_landing_load_share": 1.0,
        "concrete_unit_weight_kn_per_m3": 25.0,
        "ultimate_load_factor": 1.5,
        "load_basis_reference": "NPTEL-M9L20-EX9.1",
        "effective_depth_mm": 224.0,
        "fck_n_per_mm2": 20.0,
        "fy_n_per_mm2": 415.0,
        "main_bar_diameter_mm": 12.0,
        "main_bar_spacing_mm": 120.0,
        "distribution_bar_diameter_mm": 8.0,
        "distribution_bar_spacing_mm": 160.0,
    }
    values.update(overrides)
    return services_api.StraightFlightStaircaseInput(**values)  # type: ignore[arg-type]


def test_staircase_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_straight_flight_staircase_is456
        is services_api.design_straight_flight_staircase_is456
    )
    for name in (
        "design_straight_flight_staircase_is456",
        "StraightFlightStaircaseInput",
        "StraightFlightStaircaseProvenance",
        "StraightFlightStaircaseResult",
    ):
        assert name in services_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_nptel_example_and_retains_review() -> None:
    result = structural_lib.design_straight_flight_staircase_is456(_benchmark_request())

    assert result.status is StaircaseDesignStatus.REVIEW_REQUIRED
    assert result.geometry.effective_span_mm == 5100.0
    assert result.actions.maximum_factored_moment_knm_per_m == pytest.approx(
        68.048997, abs=1e-6
    )
    assert result.design.ast_required_mm2_per_m == pytest.approx(920.64, abs=2.0)
    assert result.design.shear.is_safe_without_shear_reinforcement
    assert result.design.actual_span_to_depth_ratio == pytest.approx(5100.0 / 224.0)
    assert result.provenance.load_generation_status == (
        "not_generated_caller_supplied_actions"
    )
    assert result.qualified_review_required
    assert not result.complete_engineering_design_approved
    json.dumps(dataclasses.asdict(result))


def test_short_public_case_passes_and_insufficient_steel_fails() -> None:
    passing = structural_lib.design_straight_flight_staircase_is456(
        _benchmark_request(upper_landing_effective_length_mm=550.0)
    )
    failing = structural_lib.design_straight_flight_staircase_is456(
        _benchmark_request(main_bar_spacing_mm=300.0)
    )

    assert passing.status is StaircaseDesignStatus.PASS
    assert failing.status is StaircaseDesignStatus.FAIL


def _canonical_request(
    request: services_api.StraightFlightStaircaseInput,
) -> staircase_facade.StaircaseInputV1:
    """Share explicit physical inputs between the two maintained stair callers."""
    values = dataclasses.asdict(request)
    return staircase_facade.input(
        identity_source={
            "identity": {
                "family_id": "stair",
                "case_id": request.case_id,
                "member_id": request.case_id,
                "story": "AMD3",
                "source_reference": "AMD3-STAIR-ALTERED-FIXTURE",
            },
            "load_basis_reference": request.load_basis_reference,
        },
        geometry_topology={
            key: values[key]
            for key in (
                "lower_landing_effective_length_mm",
                "going_mm",
                "upper_landing_effective_length_mm",
                "flight_width_mm",
                "riser_mm",
                "tread_mm",
                "waist_thickness_mm",
                "landing_thickness_mm",
                "support_case",
                "span_direction",
                "landings_collinear",
                "has_stringer_beams",
                "is_cast_in_situ_solid",
            )
        },
        actions={
            key: values[key]
            for key in (
                "lower_landing_superimposed_service_load_kn_per_m2",
                "flight_superimposed_service_load_kn_per_m2",
                "upper_landing_superimposed_service_load_kn_per_m2",
                "lower_landing_load_share",
                "upper_landing_load_share",
                "concrete_unit_weight_kn_per_m3",
                "ultimate_load_factor",
            )
        },
        materials_reinforcement={
            "fck_nmm2": request.fck_n_per_mm2,
            "fy_nmm2": request.fy_n_per_mm2,
            **{
                key: values[key]
                for key in (
                    "effective_depth_mm",
                    "main_bar_diameter_mm",
                    "main_bar_spacing_mm",
                    "distribution_bar_diameter_mm",
                    "distribution_bar_spacing_mm",
                )
            },
        },
        evidence_review={"qualified_review_required": True},
    )


@pytest.mark.parametrize(
    ("spacing_mm", "status"), [(300.0, "PASS"), (400.0, "FAIL"), (451.0, "FAIL")]
)
def test_amended_spacing_disposition_reaches_public_and_serialized_facade(
    spacing_mm: float, status: str
) -> None:
    # This shortened/altered diagnostic is distinct from the published example.
    request = _benchmark_request(
        case_id="AMD3-STAIR-ALTERED-4000MM-FIXTURE",
        load_basis_reference="AMD3-STAIR-ALTERED-4000MM-FIXTURE",
        upper_landing_effective_length_mm=550.0,
        distribution_bar_diameter_mm=14.0,
        distribution_bar_spacing_mm=spacing_mm,
    )
    public = structural_lib.design_straight_flight_staircase_is456(request)
    canonical_request = _canonical_request(request)
    serialized_request = staircase_facade.load_json(canonical_request.model_dump_json())
    canonical = staircase_facade.design(serialized_request)
    payload = canonical.to_dict()

    assert public.design.maximum_distribution_bar_spacing_mm == 300.0
    assert public.status.value == canonical.engineering_status.value == status
    assert canonical.calculation == public
    assert payload["envelope"]["calculation_status"] == "COMPLETED"
    assert payload["envelope"]["engineering_status"] == status
    assert payload["envelope"]["qualified_review_required"] is True
    assert payload["calculation"]["complete_engineering_design_approved"] is False
    assert public.qualified_review_required and canonical.qualified_review_required
    assert any("physical horizontal/soffit" in item for item in public.held_cases)
    assert any("physical horizontal/soffit" in item for item in payload["limitations"])
    assert "IS 456:2000 Cl. 26.3.3(b)(2), Amendment 3 (August 2007)" in (
        public.provenance.source_refs
    )
    json.dumps(payload, allow_nan=False)


def test_stair_capability_names_only_the_bounded_public_workflow() -> None:
    stair = next(
        item
        for item in services_api.get_supported_is456_capabilities()
        if item.element == "stair"
    )

    assert stair.public_workflows == ("design_straight_flight_staircase_is456",)
    assert "straight waist-slab flight" in stair.supported_case
    assert any("Dog-legged" in item for item in stair.held_cases)
    assert any("IS 875" in item for item in stair.held_cases)
    assert stair.qualified_review_required
