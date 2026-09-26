"""Curated construction facade for the concentric isolated-footing service."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.core.data_types import FootingType
from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f3 import (
    IsolatedActionsV1,
    IsolatedEvidenceReviewV1,
    IsolatedFootingInputV1,
    IsolatedGeometryTopologyV1,
    IsolatedIdentitySourceV1,
    IsolatedMaterialsReinforcementV1,
)
from structural_lib.services.footing_api import (
    ConcentricIsolatedFootingInput,
    ConcentricIsolatedFootingResult,
    design_concentric_isolated_footing_is456,
)

__all__ = [
    "FamilyIdentityV1",
    "IsolatedActionsV1",
    "IsolatedEvidenceReviewV1",
    "IsolatedGeometryTopologyV1",
    "IsolatedIdentitySourceV1",
    "IsolatedMaterialsReinforcementV1",
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
    identity_source: IsolatedIdentitySourceV1 | Mapping[str, object],
    geometry_topology: IsolatedGeometryTopologyV1 | Mapping[str, object],
    actions: IsolatedActionsV1 | Mapping[str, object],
    materials_reinforcement: IsolatedMaterialsReinforcementV1 | Mapping[str, object],
    evidence_review: IsolatedEvidenceReviewV1 | Mapping[str, object],
) -> IsolatedFootingInputV1:
    """Build a validated isolated footing request from explicit groups.

    Parameters
    ----------
    identity_source : IsolatedIdentitySourceV1 or Mapping[str, object]
        Member/case identity and source references for the design basis. Mapping inputs use the same strict validation.
    geometry_topology : IsolatedGeometryTopologyV1 or Mapping[str, object]
        Dimensions in mm and the supported arrangement and restraints. Mapping inputs use the same strict validation.
    actions : IsolatedActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials_reinforcement : IsolatedMaterialsReinforcementV1 or Mapping[str, object]
        Material strengths and explicit supplied/permitted reinforcement. Mapping inputs use the same strict validation.
    evidence_review : IsolatedEvidenceReviewV1 or Mapping[str, object]
        Caller-supplied basis, review references and acknowledgements. Mapping inputs use the same strict validation.

    Returns
    -------
    IsolatedFootingInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Service loads govern bearing; factored loads govern strength. Soil approval is caller evidence.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable isolated-footing recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(IsolatedFootingInputV1, locals())


def load(
    value: Mapping[str, object] | IsolatedFootingInputV1,
) -> IsolatedFootingInputV1:
    """Validate a Python mapping or an existing IsolatedFootingInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or IsolatedFootingInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    IsolatedFootingInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Service loads govern bearing; factored loads govern strength. Soil approval is caller evidence.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable isolated-footing recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(IsolatedFootingInputV1, value)


def design(
    request: IsolatedFootingInputV1,
) -> CanonicalFamilyResultV1[ConcentricIsolatedFootingResult]:
    """Design a concentric isolated footing using explicit soil and load bases.

    Parameters
    ----------
    request : IsolatedFootingInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[ConcentricIsolatedFootingResult]
        ``calculation`` holds the maintained owner result. Read
        ``engineering_status`` for PASS/FAIL/HOLD, ``limitations`` for scope,
        and ``to_dict()`` for finite JSON. Completion is not engineering approval.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Service loads govern bearing; factored loads govern strength. Soil approval is caller evidence.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable isolated-footing recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

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
