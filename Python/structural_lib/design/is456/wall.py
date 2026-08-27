"""Curated construction facade for the bounded braced-wall service."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.wall import WallAxialStatus, WallContractError
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f2 import BracedWallInputV1
from structural_lib.services.wall_api import (
    BracedWallDesignInput,
    BracedWallDesignResult,
    design_braced_wall_is456,
)

__all__ = [
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
    identity_source: Any,
    geometry_topology: Any,
    actions: Any,
    materials_reinforcement: Any,
    evidence_review: Any,
) -> BracedWallInputV1:
    return model_validate_or_error(BracedWallInputV1, locals())


def load(value: Any) -> BracedWallInputV1:
    return model_validate_or_error(BracedWallInputV1, value)


def design(request: BracedWallInputV1) -> CanonicalFamilyResultV1:
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
