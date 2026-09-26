"""Curated construction facade for the regular interior flat-slab service."""

from __future__ import annotations

from collections.abc import Mapping

from structural_lib.codes.is456.flat_slab import FlatSlabContractError
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
    FlatActionsV1,
    FlatDirectionReinforcementV1,
    FlatEvidenceReviewV1,
    FlatGeometryTopologyV1,
    FlatIdentitySourceV1,
    FlatMaterialsReinforcementV1,
    FlatProvidedBarsV1,
    FlatSlabInputV1,
)
from structural_lib.services.flat_slab_api import (
    RegularInteriorFlatSlabDesignResult,
    RegularInteriorFlatSlabDesignStatus,
    build_regular_interior_flat_slab_design_input,
    design_regular_interior_flat_slab_is456,
)

__all__ = [
    "FamilyIdentityV1",
    "FlatActionsV1",
    "FlatDirectionReinforcementV1",
    "FlatEvidenceReviewV1",
    "FlatGeometryTopologyV1",
    "FlatIdentitySourceV1",
    "FlatMaterialsReinforcementV1",
    "FlatProvidedBarsV1",
    "CanonicalFamilyResultV1",
    "FlatSlabInputV1",
    "InputContractError",
    "InputIssueV1",
    "RegularInteriorFlatSlabDesignResult",
    "design",
    "input",
    "load",
]


def input(  # noqa: A001
    *,
    identity_source: FlatIdentitySourceV1 | Mapping[str, object],
    geometry_topology: FlatGeometryTopologyV1 | Mapping[str, object],
    actions: FlatActionsV1 | Mapping[str, object],
    materials_reinforcement: FlatMaterialsReinforcementV1 | Mapping[str, object],
    evidence_review: FlatEvidenceReviewV1 | Mapping[str, object],
) -> FlatSlabInputV1:
    """Build a validated flat slab request from explicit groups.

    Parameters
    ----------
    identity_source : FlatIdentitySourceV1 or Mapping[str, object]
        Member/case identity and source references for the design basis. Mapping inputs use the same strict validation.
    geometry_topology : FlatGeometryTopologyV1 or Mapping[str, object]
        Dimensions in mm and the supported arrangement and restraints. Mapping inputs use the same strict validation.
    actions : FlatActionsV1 or Mapping[str, object]
        Factored design actions in the units named by each field. Mapping inputs use the same strict validation.
    materials_reinforcement : FlatMaterialsReinforcementV1 or Mapping[str, object]
        Material strengths and explicit supplied/permitted reinforcement. Mapping inputs use the same strict validation.
    evidence_review : FlatEvidenceReviewV1 or Mapping[str, object]
        Caller-supplied basis, review references and acknowledgements. Mapping inputs use the same strict validation.

    Returns
    -------
    FlatSlabInputV1
        Immutable typed request, ready for ``design``.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Edge, corner and irregular panels are outside this route.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable flat-slab recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(FlatSlabInputV1, locals())


def load(value: Mapping[str, object] | FlatSlabInputV1) -> FlatSlabInputV1:
    """Validate a Python mapping or an existing FlatSlabInputV1.

    Parameters
    ----------
    value : Mapping[str, object] or FlatSlabInputV1
        Decoded JSON/Python fields or a typed request. Parse JSON text with
        ``json.loads`` first; values are not silently coerced.

    Returns
    -------
    FlatSlabInputV1
        Validated immutable request with field-level issue paths on rejection.

    Raises
    ------
    InputContractError
        Invalid fields, inconsistent inputs, or an unsupported request type.
        Inspect ``error.issues`` for stable codes, paths and constraints.

    Limitations
    -----------
    Edge, corner and irregular panels are outside this route.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable flat-slab recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    return model_validate_or_error(FlatSlabInputV1, value)


def design(
    request: FlatSlabInputV1,
) -> CanonicalFamilyResultV1[RegularInteriorFlatSlabDesignResult]:
    """Design the regular interior flat-slab panel.

    Parameters
    ----------
    request : FlatSlabInputV1
        Validated input from ``input`` or ``load``; all engineering bases are explicit.

    Returns
    -------
    CanonicalFamilyResultV1[RegularInteriorFlatSlabDesignResult]
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
    Edge, corner and irregular panels are outside this route.
    Existing mapping-based callers remain supported; no engineering defaults are inferred.

    Examples
    --------
    See the executable flat-slab recipe in the family facade cookbook:
    ``docs/cookbook/python/family-facades.md``.

    Provenance
    ----------
    Request fields are validated by the named canonical request model.
    The operation delegates to the maintained family service/code owner;
    returned ``provenance`` identifies that owner and its source references.
    """

    require_request_type(request, FlatSlabInputV1)
    i, g, a, m, e = (
        request.identity_source,
        request.geometry_topology,
        request.actions,
        request.materials_reinforcement,
        request.evidence_review,
    )
    payload = {
        "case_id": i.identity.case_id,
        "geometry": {
            **g.model_dump(mode="python"),
            "geometry_basis_reference": i.geometry_basis_reference,
        },
        "material": {
            "concrete_grade_nmm2": m.concrete_grade_nmm2,
            "steel_grade_nmm2": m.steel_grade_nmm2,
            "uncoated_deformed_bars": m.uncoated_deformed_bars,
            "material_basis_reference": i.material_basis_reference,
        },
        "gravity_load": {
            "service_dead_load_kn_per_m2": a.service_dead_load_kn_per_m2,
            "service_live_load_kn_per_m2": a.service_live_load_kn_per_m2,
            "factored_uniform_load_kn_per_m2": a.factored_uniform_load_kn_per_m2,
            "self_weight_included": a.self_weight_included,
            "identical_full_loading_on_represented_panels": a.identical_full_loading_on_represented_panels,
            "patterned_loading_required": a.patterned_loading_required,
            "unbalanced_or_lateral_moment_transfer_present": a.unbalanced_or_lateral_moment_transfer_present,
            "load_combination_approved": a.load_combination_approved,
            "load_basis_reference": i.load_basis_reference,
        },
        "x": m.x.model_dump(mode="python"),
        "y": m.y.model_dump(mode="python"),
        "factored_support_reaction_kn": a.factored_support_reaction_kn,
        **e.model_dump(mode="python"),
    }
    try:
        calculation = design_regular_interior_flat_slab_is456(
            build_regular_interior_flat_slab_design_input(payload)
        )
    except FlatSlabContractError as error:
        translate_owner_input_error(error)
    return canonical_family_result(
        request,
        calculation,
        workflow_id="is456.flat-slab.regular-interior/v1",
        engineering_status=(
            EngineeringStatus.PASS
            if calculation.status is RegularInteriorFlatSlabDesignStatus.PASS
            else EngineeringStatus.FAIL
        ),
        limitations=calculation.held_cases,
        assumptions=(calculation.supported_case,),
        provenance=calculation.provenance.source_refs,
    )
