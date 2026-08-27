"""Curated construction facade for the symmetric combined-footing service."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.combined_footing import CombinedFootingContractError
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.combined_footing_api import (
    SymmetricCombinedFootingDesignResult,
    SymmetricCombinedFootingDesignStatus,
    build_symmetric_combined_footing_design_input,
    design_symmetric_combined_footing_is456,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f3 import CombinedFootingInputV1

__all__ = [
    "CanonicalFamilyResultV1",
    "CombinedFootingInputV1",
    "InputContractError",
    "InputIssueV1",
    "SymmetricCombinedFootingDesignResult",
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
) -> CombinedFootingInputV1:
    return model_validate_or_error(CombinedFootingInputV1, locals())


def load(value: Any) -> CombinedFootingInputV1:
    return model_validate_or_error(CombinedFootingInputV1, value)


def design(request: CombinedFootingInputV1) -> CanonicalFamilyResultV1:
    require_request_type(request, CombinedFootingInputV1)
    i, g, a, m, e = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
        request.evidence_review,
    )
    material_keys = {
        "footing_concrete_grade_nmm2",
        "column_concrete_grade_nmm2",
        "steel_grade_nmm2",
        "uncoated_deformed_bars",
    }
    transfer_keys = {
        "effective_supporting_area_each_mm2",
        "effective_supporting_area_basis",
        "effective_supporting_area_approved",
        "dowel_count_each",
        "dowel_diameter_mm",
        "column_longitudinal_bar_diameter_mm",
        "available_dowel_development_into_footing_mm",
        "available_dowel_development_into_column_mm",
        "uncoated_deformed_dowels",
    }
    material_reinforcement = m.model_dump(mode="python")
    payload = {
        "case_id": i.identity.case_id,
        "qualified_review_required": e.qualified_review_required,
        "footing": {
            "analysis": {
                "geometry": {
                    **g.model_dump(mode="python"),
                    "geometry_basis_reference": i.geometry_basis_reference,
                    "rigidity_basis_reference": i.rigidity_basis_reference,
                },
                "actions": {
                    **a.model_dump(mode="python"),
                    "load_basis_reference": i.load_basis_reference,
                    "bearing_settlement_basis_reference": i.bearing_settlement_basis_reference,
                    "cancellation_basis_reference": i.cancellation_basis_reference,
                },
            },
            "material": {
                **{key: material_reinforcement[key] for key in material_keys},
                "material_basis_reference": i.material_basis_reference,
            },
            "reinforcement": {
                **{
                    key: value
                    for key, value in material_reinforcement.items()
                    if key not in material_keys | transfer_keys
                },
                "detailing_basis_reference": e.detailing_basis_reference,
            },
            "transfer": {
                **{key: material_reinforcement[key] for key in transfer_keys},
                "transfer_basis_reference": e.transfer_basis_reference,
            },
        },
    }
    try:
        calculation = design_symmetric_combined_footing_is456(
            build_symmetric_combined_footing_design_input(payload)
        )
    except CombinedFootingContractError as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.combined-footing.symmetric/v1",
        engineering_status=(
            EngineeringStatus.PASS
            if calculation.status is SymmetricCombinedFootingDesignStatus.PASS
            else EngineeringStatus.FAIL
        ),
        limitations=calculation.held_cases,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_refs,
    )
