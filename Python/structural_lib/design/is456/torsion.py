"""Curated construction facade for the existing IS 456 torsion owner."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.beam.torsion import TorsionResult, design_torsion
from structural_lib.core.errors import InputContractError, InputIssueV1, ValidationError
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    FamilyIdentityV1,
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
    "FamilyIdentityV1",
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
    identity: FamilyIdentityV1 | Mapping[str, object],
    geometry: TorsionGeometryV1 | Mapping[str, object],
    actions: TorsionActionsV1 | Mapping[str, object],
    materials: TorsionMaterialsV1 | Mapping[str, object],
    reinforcement: TorsionReinforcementV1 | Mapping[str, object],
) -> TorsionDesignInputV1:
    """Build a validated torsion request from explicit groups.

    Parameters
    ----------
    identity : FamilyIdentityV1 or Mapping[str, object]
        Member, case and caller-owned source identity. Mapping inputs use the same strict validation.
    geometry : TorsionGeometryV1 or Mapping[str, object]
        Dimensions in mm and the explicit support/topology choices. Mapping inputs use the same strict validation.
    actions : TorsionActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials : TorsionMaterialsV1 or Mapping[str, object]
        Concrete and reinforcement strengths in N/mm². Mapping inputs use the same strict validation.
    reinforcement : TorsionReinforcementV1 or Mapping[str, object]
        Supplied bar areas, positions or dimensions in mm and mm². Mapping inputs use the same strict validation.

    Returns
    -------
    TorsionDesignInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Actions are factored magnitudes; redistribution and axial interaction are not included.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable torsion recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

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


def load(value: Mapping[str, object] | TorsionDesignInputV1) -> TorsionDesignInputV1:
    """Validate a Python mapping or an existing TorsionDesignInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or TorsionDesignInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    TorsionDesignInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Actions are factored magnitudes; redistribution and axial interaction are not included.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable torsion recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(TorsionDesignInputV1, value)


def design(request: TorsionDesignInputV1) -> CanonicalFamilyResultV1[TorsionResult]:
    """Design a rectangular beam for combined torsion, shear and bending.

    Parameters
    ----------
    request : TorsionDesignInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[TorsionResult]
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
    Actions are factored magnitudes; redistribution and axial interaction are not included.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable torsion recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

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
            corner_bar_centres_mm=(
                geometry.corner_bar_centres_b1_mm,
                geometry.corner_bar_centres_d1_mm,
            ),
            d_opposite_mm=geometry.d_opposite_mm,
            fy_transverse_nmm2=materials.fy_transverse_nmm2,
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
