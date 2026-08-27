"""Curated construction facade for the regular interior flat-slab service."""

from __future__ import annotations

from typing import Any

from structural_lib.codes.is456.flat_slab import FlatSlabContractError
from structural_lib.core.errors import InputContractError, InputIssueV1
from structural_lib.core.result_contract import EngineeringStatus
from structural_lib.services.canonical_family import (
    CanonicalFamilyResultV1,
    canonical_family_result,
    require_request_type,
    translate_owner_input_error,
)
from structural_lib.services.contracts.common import model_validate_or_error
from structural_lib.services.contracts.family_f2 import FlatSlabInputV1
from structural_lib.services.flat_slab_api import (
    RegularInteriorFlatSlabDesignResult,
    RegularInteriorFlatSlabDesignStatus,
    build_regular_interior_flat_slab_design_input,
    design_regular_interior_flat_slab_is456,
)

__all__ = [
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
    identity_source: Any,
    geometry_topology: Any,
    actions: Any,
    materials_reinforcement: Any,
    evidence_review: Any,
) -> FlatSlabInputV1:
    return model_validate_or_error(FlatSlabInputV1, locals())


def load(value: Any) -> FlatSlabInputV1:
    return model_validate_or_error(FlatSlabInputV1, value)


def design(request: FlatSlabInputV1) -> CanonicalFamilyResultV1:
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
