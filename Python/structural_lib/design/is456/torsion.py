"""Curated construction facade for the existing IS 456 torsion owner."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.beam.torsion import TorsionResult, design_torsion
from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f1 import (
    TorsionActionsV1,
    TorsionDesignInputV1,
    TorsionGeometryV1,
    TorsionMaterialsV1,
    TorsionReinforcementV1,
)

__all__ = [
    "CanonicalFamilyResultV1",
    "InputContractError",
    "InputIssueV1",
    "TorsionActionsV1",
    "TorsionDesignInputV1",
    "TorsionGeometryV1",
    "TorsionMaterialsV1",
    "TorsionReinforcementV1",
    "TorsionResult",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *,
    identity: Any,
    geometry: Any,
    actions: Any,
    materials: Any,
    reinforcement: Any,
) -> TorsionDesignInputV1:
    return model_validate_or_error(
        TorsionDesignInputV1,
        {
            "identity": identity,
            "geometry": geometry,
            "actions": actions,
            "materials": materials,
            "reinforcement": reinforcement,
        },
    )


def load(value: Any) -> TorsionDesignInputV1:
    return model_validate_or_error(TorsionDesignInputV1, value)


def design(request: TorsionDesignInputV1) -> CanonicalFamilyResultV1:
    require_request_type(request, TorsionDesignInputV1)
    geometry = request.geometry
    actions = request.actions
    materials = request.materials
    reinforcement = request.reinforcement
    try:
        calculation = design_torsion(
            tu_knm=actions.tu_knm,
            vu_kn=actions.vu_kn,
            mu_knm=actions.mu_knm,
            b=geometry.b_mm,
            D=geometry.D_mm,
            d=geometry.d_mm,
            fck=materials.fck_nmm2,
            fy=materials.fy_nmm2,
            cover=geometry.clear_cover_mm,
            stirrup_dia=reinforcement.stirrup_diameter_mm,
            pt=reinforcement.tension_steel_percent,
        )
    except (ValidationError, ValueError) as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.torsion.design/v1",
        engineering_status=(
            EngineeringStatus.PASS if calculation.is_safe else EngineeringStatus.FAIL
        ),
        limitations=(
            "Rectangular solid sections and the maintained IS 456 equivalent-action method only.",
            "Applied torsion redistribution and axial interaction remain caller-owned or held.",
        ),
        assumptions=(
            "Caller supplied factored action magnitudes and a closed-stirrup basis.",
        ),
        provenance=("structural_lib.codes.is456.beam.torsion.design_torsion",),
    )
