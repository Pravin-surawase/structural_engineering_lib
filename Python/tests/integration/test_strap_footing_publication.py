"""Public-contract proof for the bounded property-line strap-footing workflow."""

from __future__ import annotations

import dataclasses
import json
from dataclasses import FrozenInstanceError

import pytest

import structural_lib
import structural_lib.services as services
from structural_lib import api as compatibility_api
from structural_lib.codes.is456.strap_footing import (
    StrapFootingContractError,
    StrapFootingDesignDisposition,
)
from structural_lib.services import api as services_api
from structural_lib.services.strap_footing_api import (
    build_property_line_strap_footing_design_input,
)
from tests.codes.is456.strap_footing.test_analysis import _actions, _input
from tests.codes.is456.strap_footing.test_strength import _design_input


def _request(
    *,
    footing: object | None = None,
    case_id: str = "INDIA-2-STRAP-HAND-01",
    qualified_review_required: bool = True,
) -> services_api.PropertyLineStrapFootingDesignInput:
    return services_api.PropertyLineStrapFootingDesignInput(
        case_id=case_id,
        footing=footing or _design_input(),  # type: ignore[arg-type]
        qualified_review_required=qualified_review_required,
    )


def test_strap_footing_has_one_canonical_public_function_and_types() -> None:
    assert (
        structural_lib.design_property_line_strap_footing_is456
        is services_api.design_property_line_strap_footing_is456
        is services.design_property_line_strap_footing_is456
        is compatibility_api.design_property_line_strap_footing_is456
    )
    for name in (
        "design_property_line_strap_footing_is456",
        "PropertyLineStrapFootingDesignInput",
        "PropertyLineStrapFootingDesignProvenance",
        "PropertyLineStrapFootingDesignResult",
        "PropertyLineStrapFootingDesignStatus",
    ):
        assert name in services.__all__
        assert name in services_api.__all__
        assert name in compatibility_api.__all__
        assert name in structural_lib.__all__


def test_public_composition_matches_frozen_benchmark_and_is_serializable() -> None:
    result = structural_lib.design_property_line_strap_footing_is456(_request())

    assert result.status is services_api.PropertyLineStrapFootingDesignStatus.PASS
    assert result.strength.disposition is StrapFootingDesignDisposition.PASS
    assert result.strength.actions.service.exterior_reaction_kn == pytest.approx(1200.0)
    assert result.strength.actions.service.interior_reaction_kn == pytest.approx(1600.0)
    assert result.strength.flexure.exact_flexural_steel_required_mm2 == pytest.approx(
        2788.774499810215
    )
    assert result.strength.flexure.top_moment_capacity_kn_m == pytest.approx(
        961.337320139164
    )
    assert result.strength.shear.stirrup_carried_shear_required_kn == pytest.approx(
        19.6274979428445
    )
    assert result.is_safe_within_supported_scope is True
    assert result.qualified_review_required is True
    assert result.complete_engineering_design_approved is False
    json.dumps(dataclasses.asdict(result))


def test_public_workflow_preserves_every_caller_basis_and_source_boundary() -> None:
    result = structural_lib.design_property_line_strap_footing_is456(_request())
    provenance = result.provenance

    assert provenance.schema_version == "1.0"
    assert provenance.code_edition == "IS 456:2000 through Amendment 6"
    assert provenance.workflow == "design_property_line_strap_footing_is456"
    assert provenance.case_id == "INDIA-2-STRAP-HAND-01"
    assert provenance.benchmark_id == "INDIA-2-STRAP-HAND-01"
    assert provenance.geometry_basis_reference.endswith("-GEOMETRY")
    assert provenance.rigidity_basis_reference.endswith("-RIGIDITY")
    assert provenance.strap_isolation_basis_reference.endswith("-ISOLATION")
    assert provenance.load_basis_reference.endswith("-LOAD")
    assert provenance.bearing_settlement_basis_reference.endswith("-GEOTECH")
    assert provenance.footing_carrier_basis_reference.endswith("-CARRIER")
    assert provenance.strap_line_load_basis_reference.endswith("-LINE-LOAD")
    assert provenance.load_pattern_basis_reference.endswith("-PATTERN")
    assert provenance.exterior_footing_verification_reference == "EXT-FOOTING-01"
    assert provenance.interior_footing_verification_reference == "INT-FOOTING-01"
    assert provenance.transfer_verification_reference == "TRANSFER-01"
    assert provenance.construction_verification_reference == "CONSTRUCTION-01"
    assert provenance.material_basis_reference.endswith("-MATERIAL")
    assert provenance.detailing_basis_reference.endswith("-DETAILING")
    assert provenance.durability_basis_reference.endswith("-DURABILITY")
    assert provenance.clause_refs == result.strength.clause_refs
    assert "IS456-PUBLIC-DISTRIBUTION-001" in provenance.source_refs
    assert any(
        item.startswith("IS456-2000-A5:sha256:") for item in provenance.source_refs
    )
    assert any(
        item.startswith("IS456-AMD6-2024:sha256:") for item in provenance.source_refs
    )
    assert "no-soil-contact strap" in result.supported_case
    assert any("soil-structure interaction" in item for item in result.held_cases)
    assert any("professional approval" in item for item in result.held_cases)


def test_valid_inadequacy_returns_public_fail_result() -> None:
    failing = _design_input(
        analysis=_input(
            actions=_actions(allowable_gross_bearing_pressure_kn_per_m2=210.0)
        )
    )
    result = structural_lib.design_property_line_strap_footing_is456(
        _request(footing=failing)
    )

    assert result.status is services_api.PropertyLineStrapFootingDesignStatus.FAIL
    assert result.strength.disposition is StrapFootingDesignDisposition.FAIL
    assert result.strength.actions.gross_service_bearing_within_allowable is False


def test_invalid_public_contract_fails_closed() -> None:
    with pytest.raises(StrapFootingContractError, match="DesignInput"):
        services_api.design_property_line_strap_footing_is456(object())  # type: ignore[arg-type]
    with pytest.raises(StrapFootingContractError, match="case_id"):
        services_api.design_property_line_strap_footing_is456(_request(case_id=" "))
    with pytest.raises(StrapFootingContractError, match="footing"):
        services_api.design_property_line_strap_footing_is456(
            _request(footing=object())
        )
    with pytest.raises(StrapFootingContractError, match="qualified_review"):
        services_api.design_property_line_strap_footing_is456(
            _request(qualified_review_required=False)
        )


def test_mapping_builder_round_trips_and_fails_closed() -> None:
    request = _request()
    rebuilt = build_property_line_strap_footing_design_input(
        dataclasses.asdict(request)
    )
    assert rebuilt == request
    with pytest.raises(StrapFootingContractError, match="transport payload"):
        build_property_line_strap_footing_design_input({"case_id": "x"})


def test_public_result_is_frozen_and_deterministic() -> None:
    first = structural_lib.design_property_line_strap_footing_is456(_request())
    second = structural_lib.design_property_line_strap_footing_is456(_request())

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.status = services_api.PropertyLineStrapFootingDesignStatus.FAIL  # type: ignore[misc]


def test_capability_and_semantic_truth_publish_the_exact_workflow_in_d() -> None:
    capability = next(
        item
        for item in services_api.get_supported_is456_capabilities()
        if item.element == "strap_footing"
    )
    contract = next(
        item
        for item in services_api.get_supported_is456_semantic_contract().workflows
        if item.workflow == "design_property_line_strap_footing_is456"
    )

    assert capability.public_workflows == ("design_property_line_strap_footing_is456",)
    assert "no-soil-contact strap" in capability.supported_case
    assert contract.element == "strap_footing"
    assert {field.canonical_name for field in contract.fields} >= {
        "request.footing.analysis.geometry",
        "request.footing.analysis.actions",
        "request.footing.analysis.approvals",
        "strength.flexure",
        "strength.side_face",
        "strength.shear",
        "qualified_review_required",
    }
    assert contract.statuses[0].canonical_name == "status"
