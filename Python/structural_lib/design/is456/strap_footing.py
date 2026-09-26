"""Curated construction facade for the property-line strap-footing service."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.strap_footing import StrapFootingContractError
from structural_lib.core.errors import InputContractError, InputIssueV1
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
    StrapActionsV1,
    StrapEvidenceReviewV1,
    StrapFootingInputV1,
    StrapGeometryTopologyV1,
    StrapIdentitySourceV1,
    StrapMaterialsReinforcementV1,
)
from structural_lib.services.strap_footing_api import (
    PropertyLineStrapFootingDesignResult,
    PropertyLineStrapFootingDesignStatus,
    build_property_line_strap_footing_design_input,
    design_property_line_strap_footing_is456,
)

__all__ = [
    "FamilyIdentityV1",
    "StrapActionsV1",
    "StrapEvidenceReviewV1",
    "StrapGeometryTopologyV1",
    "StrapIdentitySourceV1",
    "StrapMaterialsReinforcementV1",
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
    identity_source: StrapIdentitySourceV1 | Mapping[str, object],
    geometry_topology: StrapGeometryTopologyV1 | Mapping[str, object],
    actions: StrapActionsV1 | Mapping[str, object],
    materials_reinforcement: StrapMaterialsReinforcementV1 | Mapping[str, object],
    evidence_review: StrapEvidenceReviewV1 | Mapping[str, object],
) -> StrapFootingInputV1:
    """Build a validated strap footing request from explicit groups.

    Parameters
    ----------
    identity_source : StrapIdentitySourceV1 or Mapping[str, object]
        Member/case identity and source references for the design basis. Mapping inputs use the same strict validation.
    geometry_topology : StrapGeometryTopologyV1 or Mapping[str, object]
        Dimensions in mm and the supported arrangement and restraints. Mapping inputs use the same strict validation.
    actions : StrapActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials_reinforcement : StrapMaterialsReinforcementV1 or Mapping[str, object]
        Material strengths and explicit supplied/permitted reinforcement. Mapping inputs use the same strict validation.
    evidence_review : StrapEvidenceReviewV1 or Mapping[str, object]
        Caller-supplied basis, review references and acknowledgements. Mapping inputs use the same strict validation.

    Returns
    -------
    StrapFootingInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    The strap and both pads must satisfy the declared topology and load-basis contract.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable strap-footing recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(StrapFootingInputV1, locals())


def load(value: Mapping[str, object] | StrapFootingInputV1) -> StrapFootingInputV1:
    """Validate a Python mapping or an existing StrapFootingInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or StrapFootingInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    StrapFootingInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    The strap and both pads must satisfy the declared topology and load-basis contract.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable strap-footing recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(StrapFootingInputV1, value)


def design(
    request: StrapFootingInputV1,
) -> CanonicalFamilyResultV1[PropertyLineStrapFootingDesignResult]:
    """Design the supported property-line strap footing.

    Parameters
    ----------
    request : StrapFootingInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[PropertyLineStrapFootingDesignResult]
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
    The strap and both pads must satisfy the declared topology and load-basis contract.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable strap-footing recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

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
