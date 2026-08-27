"""Curated construction facade for the concentric isolated-footing service."""

from __future__ import annotations

from typing import Any

from structural_lib.core.data_types import FootingType
from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f3 import IsolatedFootingInputV1
from structural_lib.services.footing_api import (
    ConcentricIsolatedFootingInput,
    ConcentricIsolatedFootingResult,
    design_concentric_isolated_footing_is456,
)

__all__ = [
    "CanonicalFamilyResultV1",
    "ConcentricIsolatedFootingResult",
    "InputContractError",
    "InputIssueV1",
    "IsolatedFootingInputV1",
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
) -> IsolatedFootingInputV1:
    return model_validate_or_error(IsolatedFootingInputV1, locals())


def load(value: Any) -> IsolatedFootingInputV1:
    return model_validate_or_error(IsolatedFootingInputV1, value)


def design(request: IsolatedFootingInputV1) -> CanonicalFamilyResultV1:
    require_request_type(request, IsolatedFootingInputV1)
    i, g, a, m, e = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
        request.evidence_review,
    )
    values = {
        "case_id": i.identity.case_id,
        "service_axial_load_kN": a.service_axial_load_kn,
        "service_load_combination_id": i.service_load_combination_id,
        "service_load_basis": i.service_load_basis,
        "service_load_origin": i.service_load_origin,
        "factored_axial_load_kN": a.factored_axial_load_kn,
        "factored_load_combination_id": i.factored_load_combination_id,
        "allowable_soil_pressure_kPa": a.allowable_soil_pressure_kpa,
        "allowable_soil_pressure_source_reference": i.allowable_soil_pressure_source_reference,
        "allowable_soil_pressure_origin": i.allowable_soil_pressure_origin,
        "allowable_soil_pressure_is_externally_approved": e.allowable_soil_pressure_is_externally_approved,
        "footing_type": FootingType[g.footing_type],
        "column_L_mm": g.column_length_mm,
        "column_B_mm": g.column_width_mm,
        "minimum_overall_thickness_mm": g.minimum_overall_thickness_mm,
        "maximum_overall_thickness_mm": g.maximum_overall_thickness_mm,
        "thickness_increment_mm": g.thickness_increment_mm,
        "effective_depth_offset_L_mm": g.effective_depth_offset_length_mm,
        "effective_depth_offset_B_mm": g.effective_depth_offset_width_mm,
        "effective_supporting_area_A1_mm2": e.effective_supporting_area_mm2,
        "effective_supporting_area_basis": e.effective_supporting_area_basis,
        "effective_supporting_area_origin": e.effective_supporting_area_origin,
        "effective_supporting_area_is_approved": e.effective_supporting_area_is_approved,
        "cover_exposure_basis": e.cover_exposure_basis,
        "cover_exposure_basis_is_approved": e.cover_exposure_basis_is_approved,
        **m.model_dump(mode="python"),
    }
    values["permitted_bottom_bar_diameters_mm"] = tuple(
        values["permitted_bottom_bar_diameters_mm"]
    )
    try:
        calculation = design_concentric_isolated_footing_is456(
            ConcentricIsolatedFootingInput(**values)
        )
    except (ValidationError, TypeError, ValueError) as error:
        translate_owner_input_error(error)
    status = {
        "PASS": EngineeringStatus.PASS,
        "FAIL": EngineeringStatus.FAIL,
        "HOLD": EngineeringStatus.HOLD,
    }[calculation.status]
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.isolated-footing.concentric/v1",
        engineering_status=status,
        limitations=calculation.exclusions,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_ids,
    )
