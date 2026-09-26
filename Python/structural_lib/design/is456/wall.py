"""Curated construction facade for the bounded braced-wall service."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.wall import WallAxialStatus, WallContractError
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
    BracedWallInputV1,
    WallActionsV1,
    WallEvidenceReviewV1,
    WallGeometryTopologyV1,
    WallIdentitySourceV1,
    WallMaterialsReinforcementV1,
)
from structural_lib.services.wall_api import (
    BracedWallDesignInput,
    BracedWallDesignResult,
    design_braced_wall_is456,
)

__all__ = [
    "FamilyIdentityV1",
    "WallActionsV1",
    "WallEvidenceReviewV1",
    "WallGeometryTopologyV1",
    "WallIdentitySourceV1",
    "WallMaterialsReinforcementV1",
    "BracedWallDesignResult",
    "BracedWallInputV1",
    "CanonicalFamilyResultV1",
    "InputContractError",
    "InputIssueV1",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *,
    identity_source: WallIdentitySourceV1 | Mapping[str, object],
    geometry_topology: WallGeometryTopologyV1 | Mapping[str, object],
    actions: WallActionsV1 | Mapping[str, object],
    materials_reinforcement: WallMaterialsReinforcementV1 | Mapping[str, object],
    evidence_review: WallEvidenceReviewV1 | Mapping[str, object],
) -> BracedWallInputV1:
    """Build a validated wall request from explicit groups.

    Parameters
    ----------
    identity_source : WallIdentitySourceV1 or Mapping[str, object]
        Member/case identity and source references for the design basis. Mapping inputs use the same strict validation.
    geometry_topology : WallGeometryTopologyV1 or Mapping[str, object]
        Dimensions in mm and the supported arrangement and restraints. Mapping inputs use the same strict validation.
    actions : WallActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials_reinforcement : WallMaterialsReinforcementV1 or Mapping[str, object]
        Material strengths and explicit supplied/permitted reinforcement. Mapping inputs use the same strict validation.
    evidence_review : WallEvidenceReviewV1 or Mapping[str, object]
        Caller-supplied basis, review references and acknowledgements. Mapping inputs use the same strict validation.

    Returns
    -------
    BracedWallInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    The request must establish the supported bracing and reinforcement conditions.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable wall recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(BracedWallInputV1, locals())


def load(value: Mapping[str, object] | BracedWallInputV1) -> BracedWallInputV1:
    """Validate a Python mapping or an existing BracedWallInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or BracedWallInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    BracedWallInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    The request must establish the supported bracing and reinforcement conditions.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable wall recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(BracedWallInputV1, value)


def design(
    request: BracedWallInputV1,
) -> CanonicalFamilyResultV1[BracedWallDesignResult]:
    """Check the bounded braced wall under axial load and eccentricity.

    Parameters
    ----------
    request : BracedWallInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[BracedWallDesignResult]
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
    The request must establish the supported bracing and reinforcement conditions.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable wall recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, BracedWallInputV1)
    i, g, a, m, e = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
        request.evidence_review,
    )
    values = {
        "case_id": i.identity.case_id,
        "bracing_basis_reference": i.bracing_basis_reference,
        **g.model_dump(mode="python"),
        **a.model_dump(mode="python"),
        **m.model_dump(mode="python"),
        "reinforcement_basis_reference": e.reinforcement_basis_reference,
    }
    try:
        calculation = design_braced_wall_is456(BracedWallDesignInput(**values))
    except WallContractError as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.wall.braced-axial/v1",
        engineering_status=(
            EngineeringStatus.PASS
            if calculation.status is WallAxialStatus.PASS
            else EngineeringStatus.FAIL
        ),
        limitations=calculation.held_cases,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_refs,
    )
