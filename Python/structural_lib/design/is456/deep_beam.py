"""Curated construction facade for the simply supported deep-beam service."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.deep_beam import (
    DeepBeamCheckStatus,
    DeepBeamContractError,
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
    DeepActionsV1,
    DeepBeamInputV1,
    DeepEvidenceReviewV1,
    DeepGeometryTopologyV1,
    DeepIdentitySourceV1,
    DeepMaterialsReinforcementV1,
)
from structural_lib.services.deep_beam_api import (
    SimplySupportedDeepBeamDesignInput,
    SimplySupportedDeepBeamDesignResult,
    design_simply_supported_deep_beam_is456,
)

__all__ = [
    "DeepActionsV1",
    "DeepEvidenceReviewV1",
    "DeepGeometryTopologyV1",
    "DeepIdentitySourceV1",
    "DeepMaterialsReinforcementV1",
    "FamilyIdentityV1",
    "CanonicalFamilyResultV1",
    "DeepBeamInputV1",
    "InputContractError",
    "InputIssueV1",
    "SimplySupportedDeepBeamDesignResult",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *,
    identity_source: DeepIdentitySourceV1 | Mapping[str, object],
    geometry_topology: DeepGeometryTopologyV1 | Mapping[str, object],
    actions: DeepActionsV1 | Mapping[str, object],
    materials_reinforcement: DeepMaterialsReinforcementV1 | Mapping[str, object],
    evidence_review: DeepEvidenceReviewV1 | Mapping[str, object],
) -> DeepBeamInputV1:
    """Build a validated deep beam request from explicit groups.

    Parameters
    ----------
    identity_source : DeepIdentitySourceV1 or Mapping[str, object]
        Member/case identity and source references for the design basis. Mapping inputs use the same strict validation.
    geometry_topology : DeepGeometryTopologyV1 or Mapping[str, object]
        Dimensions in mm and the supported arrangement and restraints. Mapping inputs use the same strict validation.
    actions : DeepActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials_reinforcement : DeepMaterialsReinforcementV1 or Mapping[str, object]
        Material strengths and explicit supplied/permitted reinforcement. Mapping inputs use the same strict validation.
    evidence_review : DeepEvidenceReviewV1 or Mapping[str, object]
        Caller-supplied basis, review references and acknowledgements. Mapping inputs use the same strict validation.

    Returns
    -------
    DeepBeamInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Continuous, opening-bearing and other unsupported deep-beam arrangements are excluded.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable deep-beam recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(DeepBeamInputV1, locals())


def load(value: Mapping[str, object] | DeepBeamInputV1) -> DeepBeamInputV1:
    """Validate a Python mapping or an existing DeepBeamInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or DeepBeamInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    DeepBeamInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Continuous, opening-bearing and other unsupported deep-beam arrangements are excluded.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable deep-beam recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(DeepBeamInputV1, value)


def design(
    request: DeepBeamInputV1,
) -> CanonicalFamilyResultV1[SimplySupportedDeepBeamDesignResult]:
    """Design the supported simply supported deep beam.

    Parameters
    ----------
    request : DeepBeamInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[SimplySupportedDeepBeamDesignResult]
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
    Continuous, opening-bearing and other unsupported deep-beam arrangements are excluded.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable deep-beam recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, DeepBeamInputV1)
    i, g, a, m, e = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
        request.evidence_review,
    )
    values = {
        "case_id": i.identity.case_id,
        "geometry_basis_reference": i.geometry_basis_reference,
        **g.model_dump(mode="python"),
        **a.model_dump(mode="python"),
        **m.model_dump(mode="python"),
        "bearing_nodal_zone_verified": e.bearing_nodal_zone_verified,
        "bearing_nodal_zone_reference": e.bearing_nodal_zone_reference,
        "reinforcement_basis_reference": e.reinforcement_basis_reference,
    }
    try:
        calculation = design_simply_supported_deep_beam_is456(
            SimplySupportedDeepBeamDesignInput(**values)
        )
    except DeepBeamContractError as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.deep-beam.simply-supported/v1",
        engineering_status=(
            EngineeringStatus.PASS
            if calculation.status is DeepBeamCheckStatus.PASS
            else EngineeringStatus.FAIL
        ),
        limitations=calculation.held_cases,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_refs,
    )
