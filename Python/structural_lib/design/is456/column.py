"""Curated supplied-steel column-check facade."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.column_api import ColumnDesignResult, design_column_is456
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f1 import (
    ColumnActionsV1,
    ColumnDesignInputV1,
    ColumnGeometryV1,
    ColumnMaterialsV1,
    ColumnReinforcementV1,
)

__all__ = [
    "ColumnDesignResult",
    "FamilyIdentityV1",
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
    *,
    identity: FamilyIdentityV1 | Mapping[str, object],
    geometry: ColumnGeometryV1 | Mapping[str, object],
    actions: ColumnActionsV1 | Mapping[str, object],
    materials: ColumnMaterialsV1 | Mapping[str, object],
    reinforcement: ColumnReinforcementV1 | Mapping[str, object],
) -> ColumnDesignInputV1:
    """Build a validated column request from explicit groups.

    Parameters
    ----------
    identity : FamilyIdentityV1 or Mapping[str, object]
        Member, case and caller-owned source identity. Mapping inputs use the same strict validation.
    geometry : ColumnGeometryV1 or Mapping[str, object]
        Dimensions in mm and the explicit support/topology choices. Mapping inputs use the same strict validation.
    actions : ColumnActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials : ColumnMaterialsV1 or Mapping[str, object]
        Concrete and reinforcement strengths in N/mm². Mapping inputs use the same strict validation.
    reinforcement : ColumnReinforcementV1 or Mapping[str, object]
        Supplied bar areas, positions or dimensions in mm and mm². Mapping inputs use the same strict validation.

    Returns
    -------
    ColumnDesignInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

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


def load(value: Mapping[str, object] | ColumnDesignInputV1) -> ColumnDesignInputV1:
    """Validate a Python mapping or an existing ColumnDesignInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or ColumnDesignInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    ColumnDesignInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(ColumnDesignInputV1, value)


def design(request: ColumnDesignInputV1) -> CanonicalFamilyResultV1[ColumnDesignResult]:
    """Check supplied reinforcement for a solid rectangular column.

    Parameters
    ----------
    request : ColumnDesignInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[ColumnDesignResult]
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
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

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


def check(request: ColumnDesignInputV1) -> CanonicalFamilyResultV1[ColumnDesignResult]:
    """Check supplied reinforcement for a solid rectangular column.

    Parameters
    ----------
    request : ColumnDesignInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[ColumnDesignResult]
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
    Automatic steel selection, circular sections and arbitrary bar layouts are not supported.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable column recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return design(request)
