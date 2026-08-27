"""Curated construction facade for the straight-flight staircase service."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.staircase import (
    StaircaseContractError,
    StaircaseDesignStatus,
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
from structural_lib.services.contracts.family_f2 import StaircaseInputV1
from structural_lib.services.staircase_api import (
    StraightFlightStaircaseInput,
    StraightFlightStaircaseResult,
    design_straight_flight_staircase_is456,
)

__all__ = [
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
    identity_source: Any,
    geometry_topology: Any,
    actions: Any,
    materials_reinforcement: Any,
    evidence_review: Any,
) -> StaircaseInputV1:
    return model_validate_or_error(StaircaseInputV1, locals())


def load(value: Any) -> StaircaseInputV1:
    return model_validate_or_error(StaircaseInputV1, value)


def design(request: StaircaseInputV1) -> CanonicalFamilyResultV1:
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
