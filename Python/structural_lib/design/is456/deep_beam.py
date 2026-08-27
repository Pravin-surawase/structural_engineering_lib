"""Curated construction facade for the simply supported deep-beam service."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.deep_beam import (
    DeepBeamCheckStatus,
    DeepBeamContractError,
)
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f2 import DeepBeamInputV1
from structural_lib.services.deep_beam_api import (
    SimplySupportedDeepBeamDesignInput,
    SimplySupportedDeepBeamDesignResult,
    design_simply_supported_deep_beam_is456,
)

__all__ = [
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
    identity_source: Any,
    geometry_topology: Any,
    actions: Any,
    materials_reinforcement: Any,
    evidence_review: Any,
) -> DeepBeamInputV1:
    return model_validate_or_error(DeepBeamInputV1, locals())


def load(value: Any) -> DeepBeamInputV1:
    return model_validate_or_error(DeepBeamInputV1, value)


def design(request: DeepBeamInputV1) -> CanonicalFamilyResultV1:
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
