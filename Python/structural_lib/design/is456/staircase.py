"""Curated construction facade for the straight-flight staircase service."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.staircase import (
    StaircaseContractError,
    StaircaseDesignStatus,
)
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
from structural_lib.services.contracts.family_f2 import (
    StairActionsV1,
    StaircaseInputV1,
    StairEvidenceReviewV1,
    StairGeometryTopologyV1,
    StairIdentitySourceV1,
    StairMaterialsReinforcementV1,
)
from structural_lib.services.staircase_api import (
    StraightFlightStaircaseInput,
    StraightFlightStaircaseResult,
    design_straight_flight_staircase_is456,
)

__all__ = [
    "FamilyIdentityV1",
    "StairActionsV1",
    "StairEvidenceReviewV1",
    "StairGeometryTopologyV1",
    "StairIdentitySourceV1",
    "StairMaterialsReinforcementV1",
    "CanonicalFamilyResultV1",
    "InputContractError",
    "InputIssueV1",
    "StaircaseInputV1",
    "StraightFlightStaircaseResult",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *,
    identity_source: StairIdentitySourceV1 | Mapping[str, object],
    geometry_topology: StairGeometryTopologyV1 | Mapping[str, object],
    actions: StairActionsV1 | Mapping[str, object],
    materials_reinforcement: StairMaterialsReinforcementV1 | Mapping[str, object],
    evidence_review: StairEvidenceReviewV1 | Mapping[str, object],
) -> StaircaseInputV1:
    """Build a validated staircase request from explicit groups.

    Parameters
    ----------
    identity_source : StairIdentitySourceV1 or Mapping[str, object]
        Member/case identity and source references for the design basis. Mapping inputs use the same strict validation.
    geometry_topology : StairGeometryTopologyV1 or Mapping[str, object]
        Dimensions in mm and the supported arrangement and restraints. Mapping inputs use the same strict validation.
    actions : StairActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials_reinforcement : StairMaterialsReinforcementV1 or Mapping[str, object]
        Material strengths and explicit supplied/permitted reinforcement. Mapping inputs use the same strict validation.
    evidence_review : StairEvidenceReviewV1 or Mapping[str, object]
        Caller-supplied basis, review references and acknowledgements. Mapping inputs use the same strict validation.

    Returns
    -------
    StaircaseInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    A completed calculation can remain HOLD when the supplied review evidence is insufficient.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable staircase recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(StaircaseInputV1, locals())


def load(value: Mapping[str, object] | StaircaseInputV1) -> StaircaseInputV1:
    """Validate a Python mapping or an existing StaircaseInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or StaircaseInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    StaircaseInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    A completed calculation can remain HOLD when the supplied review evidence is insufficient.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable staircase recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(StaircaseInputV1, value)


def design(
    request: StaircaseInputV1,
) -> CanonicalFamilyResultV1[StraightFlightStaircaseResult]:
    """Design a straight stair flight with collinear spanning landings.

    Parameters
    ----------
    request : StaircaseInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[StraightFlightStaircaseResult]
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
    A completed calculation can remain HOLD when the supplied review evidence is insufficient.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable staircase recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, StaircaseInputV1)
    i, g, a, m = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
    )
    values = {
        "case_id": i.identity.case_id,
        "load_basis_reference": i.load_basis_reference,
        **g.model_dump(mode="python"),
        **a.model_dump(mode="python"),
        **m.model_dump(mode="python"),
        "fck_n_per_mm2": m.fck_nmm2,
        "fy_n_per_mm2": m.fy_nmm2,
    }
    values.pop("fck_nmm2")
    values.pop("fy_nmm2")
    try:
        calculation = design_straight_flight_staircase_is456(
            StraightFlightStaircaseInput(**values)
        )
    except StaircaseContractError as error:
        translate_owner_input_error(error)
    disposition = {
        StaircaseDesignStatus.PASS: EngineeringStatus.PASS,
        StaircaseDesignStatus.FAIL: EngineeringStatus.FAIL,
        StaircaseDesignStatus.REVIEW_REQUIRED: EngineeringStatus.HOLD,
    }[calculation.status]
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.staircase.straight-flight/v1",
        engineering_status=disposition,
        limitations=calculation.held_cases,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_refs,
    )
