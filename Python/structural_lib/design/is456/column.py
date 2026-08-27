"""Curated supplied-steel column-check facade."""

from __future__ import annotations

from typing import Any

from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.column_api import design_column_is456
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f1 import (
    ColumnActionsV1,
    ColumnDesignInputV1,
    ColumnGeometryV1,
    ColumnMaterialsV1,
    ColumnReinforcementV1,
)

__all__ = [
    "CanonicalFamilyResultV1",
    "ColumnActionsV1",
    "ColumnDesignInputV1",
    "ColumnGeometryV1",
    "ColumnMaterialsV1",
    "ColumnReinforcementV1",
    "InputContractError",
    "InputIssueV1",
    "check",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *, identity: Any, geometry: Any, actions: Any, materials: Any, reinforcement: Any
) -> ColumnDesignInputV1:
    return model_validate_or_error(
        ColumnDesignInputV1,
        {
            "identity": identity,
            "geometry": geometry,
            "actions": actions,
            "materials": materials,
            "reinforcement": reinforcement,
        },
    )


def load(value: Any) -> ColumnDesignInputV1:
    return model_validate_or_error(ColumnDesignInputV1, value)


def design(request: ColumnDesignInputV1) -> CanonicalFamilyResultV1:
    require_request_type(request, ColumnDesignInputV1)
    geometry = request.geometry
    actions = request.actions
    materials = request.materials
    reinforcement = request.reinforcement
    try:
        calculation = design_column_is456(
            Pu_kN=actions.pu_kn,
            Mux_kNm=actions.mux_knm,
            Muy_kNm=actions.muy_knm,
            b_mm=geometry.b_mm,
            D_mm=geometry.D_mm,
            l_mm=geometry.unsupported_length_mm,
            end_condition=geometry.end_condition,
            fck_nmm2=materials.fck_nmm2,
            fy_nmm2=materials.fy_nmm2,
            Asc_mm2=reinforcement.supplied_steel_area_mm2,
            d_prime_mm=reinforcement.reinforcement_centroid_depth_mm,
            l_unsupported_mm=geometry.minimum_eccentricity_length_mm,
            braced=geometry.braced,
            M1x_kNm=actions.m1x_signed_knm,
            M2x_kNm=actions.m2x_signed_knm,
            M1y_kNm=actions.m1y_signed_knm,
            M2y_kNm=actions.m2y_signed_knm,
        )
    except (ValidationError, TypeError, ValueError) as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.column.supplied-steel-check/v1",
        engineering_status=(
            EngineeringStatus.PASS if calculation["is_safe"] else EngineeringStatus.FAIL
        ),
        limitations=(
            "Checks one supplied equal-opposite-face steel area for a solid rectangular column.",
            "Automatic steel selection, arbitrary multilayer layouts, circular sections, and professional approval are held.",
        ),
        assumptions=(
            "All end moments and restraint choices are explicit caller inputs.",
        ),
        provenance=("structural_lib.services.column_api.design_column_is456",),
    )


def check(request: ColumnDesignInputV1) -> CanonicalFamilyResultV1:
    """Delegate the explicit supplied-steel check to the canonical operation."""

    return design(request)
