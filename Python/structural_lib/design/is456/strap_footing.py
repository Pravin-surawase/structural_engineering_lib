"""Curated construction facade for the property-line strap-footing service."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.strap_footing import StrapFootingContractError
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f3 import StrapFootingInputV1
from structural_lib.services.strap_footing_api import (
    PropertyLineStrapFootingDesignResult,
    PropertyLineStrapFootingDesignStatus,
    build_property_line_strap_footing_design_input,
    design_property_line_strap_footing_is456,
)

__all__ = [
    "CanonicalFamilyResultV1",
    "InputContractError",
    "InputIssueV1",
    "PropertyLineStrapFootingDesignResult",
    "StrapFootingInputV1",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *,
    identity_source: Any,
    geometry_topology: Any,
    actions: Any,
    materials_reinforcement: Any,
    evidence_review: Any,
) -> StrapFootingInputV1:
    return model_validate_or_error(StrapFootingInputV1, locals())


def load(value: Any) -> StrapFootingInputV1:
    return model_validate_or_error(StrapFootingInputV1, value)


def design(request: StrapFootingInputV1) -> CanonicalFamilyResultV1:
    require_request_type(request, StrapFootingInputV1)
    i, g, a, m, e = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
        request.evidence_review,
    )
    material_values = m.model_dump(mode="python")
    material_keys = {
        "strap_concrete_grade_nmm2",
        "steel_grade_nmm2",
        "uncoated_deformed_bars",
    }
    approval_keys = {
        "exterior_footing_design_verified",
        "interior_footing_design_verified",
        "column_and_strap_transfer_verified",
        "footing_reinforcement_and_anchorage_verified",
        "supporting_areas_verified",
        "construction_clearances_verified",
        "exterior_footing_verification_reference",
        "interior_footing_verification_reference",
        "transfer_verification_reference",
        "construction_verification_reference",
    }
    evidence_values = e.model_dump(mode="python")
    payload = {
        "case_id": i.identity.case_id,
        "qualified_review_required": e.qualified_review_required,
        "footing": {
            "analysis": {
                "geometry": {
                    **g.model_dump(mode="python"),
                    "geometry_basis_reference": i.geometry_basis_reference,
                    "rigidity_basis_reference": i.rigidity_basis_reference,
                    "strap_isolation_basis_reference": i.strap_isolation_basis_reference,
                },
                "actions": {
                    **a.model_dump(mode="python"),
                    "load_basis_reference": i.load_basis_reference,
                    "bearing_settlement_basis_reference": i.bearing_settlement_basis_reference,
                    "footing_carrier_basis_reference": i.footing_carrier_basis_reference,
                    "strap_line_load_basis_reference": i.strap_line_load_basis_reference,
                    "load_pattern_basis_reference": i.load_pattern_basis_reference,
                },
                "approvals": {key: evidence_values[key] for key in approval_keys},
            },
            "material": {
                **{key: material_values[key] for key in material_keys},
                "material_basis_reference": i.material_basis_reference,
            },
            "reinforcement": {
                **{
                    key: value
                    for key, value in material_values.items()
                    if key not in material_keys
                },
                "detailing_basis_reference": e.detailing_basis_reference,
                "durability_basis_reference": e.durability_basis_reference,
            },
        },
    }
    try:
        calculation = design_property_line_strap_footing_is456(
            build_property_line_strap_footing_design_input(payload)
        )
    except StrapFootingContractError as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.strap-footing.property-line/v1",
        engineering_status=(
            EngineeringStatus.PASS
            if calculation.status is PropertyLineStrapFootingDesignStatus.PASS
            else EngineeringStatus.FAIL
        ),
        limitations=calculation.held_cases,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_refs,
    )
