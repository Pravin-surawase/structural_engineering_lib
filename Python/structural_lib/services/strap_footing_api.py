# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration for the bounded property-line strap-footing workflow."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from structural_lib.codes.is456.strap_footing import (
    StrapFootingActionInput,
    StrapFootingAnalysisInput,
    StrapFootingAnalysisMethod,
    StrapFootingApprovalInput,
    StrapFootingContractError,
    StrapFootingDesignDisposition,
    StrapFootingDesignInput,
    StrapFootingGeometryInput,
    StrapFootingMaterialInput,
    StrapFootingPressureModel,
    StrapFootingReinforcementInput,
    StrapFootingStrengthResult,
    check_property_line_strap_footing_strength,
)

__all__ = [
    "PropertyLineStrapFootingDesignInput",
    "PropertyLineStrapFootingDesignProvenance",
    "PropertyLineStrapFootingDesignResult",
    "PropertyLineStrapFootingDesignStatus",
    "build_property_line_strap_footing_design_input",
    "design_property_line_strap_footing_is456",
]


_SUPPORTED_CASE = (
    "Exactly two separate rectangular constant-depth footings on soil with one "
    "exterior square column eccentric toward the property line, one centred "
    "interior square column, and one straight prismatic no-soil-contact strap; "
    "equal uniform net pressure, common-factor vertical actions, and caller-"
    "verified footing slabs, transfer, soil, settlement, and detailing only."
)
_HELD_CASES = (
    "Automatic footing sizing or slab/transfer/connection design, unequal or nonuniform pressure, strap soil bearing, and alternate footing or column arrangements are excluded.",
    "Column moments, lateral or seismic actions, uplift, reversal, patterned or independently factored actions, settlement and bearing-capacity calculation, and soil-structure interaction are excluded.",
    "Deep, haunched, skewed, offset, crossed or multiple straps; torsion, prestress, openings, coated, bundled, spliced or curtailed bars, and automatic reinforcement are excluded.",
    "React publication, release, professional approval, and complete engineering approval are excluded.",
)


class PropertyLineStrapFootingDesignStatus(StrEnum):
    """Aggregate disposition for the bounded public Python workflow."""

    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"


@dataclass(frozen=True)
class PropertyLineStrapFootingDesignInput:
    """Case identity, A/B design input, and review acknowledgement."""

    case_id: str
    footing: StrapFootingDesignInput
    qualified_review_required: bool


@dataclass(frozen=True)
class PropertyLineStrapFootingDesignProvenance:
    """Stable workflow, source, benchmark, and caller-basis identity."""

    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    soil_verification_status: str
    geometry_basis_reference: str
    rigidity_basis_reference: str
    strap_isolation_basis_reference: str
    load_basis_reference: str
    bearing_settlement_basis_reference: str
    footing_carrier_basis_reference: str
    strap_line_load_basis_reference: str
    load_pattern_basis_reference: str
    exterior_footing_verification_reference: str
    interior_footing_verification_reference: str
    transfer_verification_reference: str
    construction_verification_reference: str
    material_basis_reference: str
    detailing_basis_reference: str
    durability_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class PropertyLineStrapFootingDesignResult:
    """Composed A/B result with supported and held case truth."""

    case_id: str
    status: PropertyLineStrapFootingDesignStatus
    strength: StrapFootingStrengthResult
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: PropertyLineStrapFootingDesignProvenance
    qualified_review_required: bool = True
    complete_engineering_design_approved: bool = False

    @property
    def is_safe_within_supported_scope(self) -> bool:
        """Return whether every represented A/B comparison passes."""

        return self.status is PropertyLineStrapFootingDesignStatus.PASS


def _require_non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StrapFootingContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _source_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise StrapFootingContractError(f"{field_name} must be an object")
    return dict(value)


def build_property_line_strap_footing_design_input(
    payload: Mapping[str, Any],
) -> PropertyLineStrapFootingDesignInput:
    """Build the service contract from an already transport-validated mapping."""

    values = dict(payload)
    try:
        footing_values = _mapping(values.pop("footing"), "footing")
        analysis_values = _mapping(footing_values.pop("analysis"), "footing.analysis")
        geometry_values = _mapping(
            analysis_values.pop("geometry"), "footing.analysis.geometry"
        )
        geometry_values["analysis_method"] = StrapFootingAnalysisMethod(
            geometry_values["analysis_method"]
        )
        geometry_values["pressure_model"] = StrapFootingPressureModel(
            geometry_values["pressure_model"]
        )
        return PropertyLineStrapFootingDesignInput(
            **values,
            footing=StrapFootingDesignInput(
                analysis=StrapFootingAnalysisInput(
                    geometry=StrapFootingGeometryInput(**geometry_values),
                    actions=StrapFootingActionInput(
                        **_mapping(
                            analysis_values.pop("actions"),
                            "footing.analysis.actions",
                        )
                    ),
                    approvals=StrapFootingApprovalInput(
                        **_mapping(
                            analysis_values.pop("approvals"),
                            "footing.analysis.approvals",
                        )
                    ),
                    **analysis_values,
                ),
                material=StrapFootingMaterialInput(
                    **_mapping(footing_values.pop("material"), "footing.material")
                ),
                reinforcement=StrapFootingReinforcementInput(
                    **_mapping(
                        footing_values.pop("reinforcement"),
                        "footing.reinforcement",
                    )
                ),
                **footing_values,
            ),
        )
    except StrapFootingContractError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise StrapFootingContractError(
            "transport payload does not match the property-line strap-footing input"
        ) from exc


def design_property_line_strap_footing_is456(
    request: PropertyLineStrapFootingDesignInput,
) -> PropertyLineStrapFootingDesignResult:
    """Compose the sole G0-approved property-line strap-footing workflow."""

    if not isinstance(request, PropertyLineStrapFootingDesignInput):
        raise StrapFootingContractError(
            "request must be a PropertyLineStrapFootingDesignInput"
        )
    case_id = _require_non_blank(request.case_id, "case_id")
    if not isinstance(request.footing, StrapFootingDesignInput):
        raise StrapFootingContractError("footing must be a StrapFootingDesignInput")
    if request.qualified_review_required is not True:
        raise StrapFootingContractError(
            "qualified_review_required must be true for this workflow"
        )

    strength = check_property_line_strap_footing_strength(request.footing)
    status = (
        PropertyLineStrapFootingDesignStatus.PASS
        if strength.disposition is StrapFootingDesignDisposition.PASS
        else PropertyLineStrapFootingDesignStatus.FAIL
    )
    analysis = request.footing.analysis
    provenance = PropertyLineStrapFootingDesignProvenance(
        schema_version="1.0",
        code_edition="IS 456:2000 through Amendment 6",
        workflow="design_property_line_strap_footing_is456",
        case_id=case_id,
        benchmark_id="INDIA-2-STRAP-HAND-01",
        action_generation_status=(
            "recomputed_from_caller_supplied_approved_service_and_factored_actions"
        ),
        soil_verification_status=(
            "caller_approved_bearing_settlement_and_equal_pressure_not_calculated"
        ),
        geometry_basis_reference=analysis.geometry.geometry_basis_reference,
        rigidity_basis_reference=analysis.geometry.rigidity_basis_reference,
        strap_isolation_basis_reference=(
            analysis.geometry.strap_isolation_basis_reference
        ),
        load_basis_reference=analysis.actions.load_basis_reference,
        bearing_settlement_basis_reference=(
            analysis.actions.bearing_settlement_basis_reference
        ),
        footing_carrier_basis_reference=(
            analysis.actions.footing_carrier_basis_reference
        ),
        strap_line_load_basis_reference=(
            analysis.actions.strap_line_load_basis_reference
        ),
        load_pattern_basis_reference=analysis.actions.load_pattern_basis_reference,
        exterior_footing_verification_reference=(
            analysis.approvals.exterior_footing_verification_reference
        ),
        interior_footing_verification_reference=(
            analysis.approvals.interior_footing_verification_reference
        ),
        transfer_verification_reference=(
            analysis.approvals.transfer_verification_reference
        ),
        construction_verification_reference=(
            analysis.approvals.construction_verification_reference
        ),
        material_basis_reference=request.footing.material.material_basis_reference,
        detailing_basis_reference=(
            request.footing.reinforcement.detailing_basis_reference
        ),
        durability_basis_reference=(
            request.footing.reinforcement.durability_basis_reference
        ),
        clause_refs=strength.clause_refs,
        source_refs=_source_refs(
            strength.source_refs,
            (
                "IS456-PUBLIC-DISTRIBUTION-001",
                "INDIA-2-STRAP-HAND-01",
            ),
        ),
    )
    return PropertyLineStrapFootingDesignResult(
        case_id=case_id,
        status=status,
        strength=strength,
        supported_case=_SUPPORTED_CASE,
        held_cases=_HELD_CASES,
        provenance=provenance,
    )
