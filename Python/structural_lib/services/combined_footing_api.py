# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Stable orchestration for the bounded symmetric combined-footing workflow."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from structural_lib.codes.is456.combined_footing import (
    CombinedFootingActionInput,
    CombinedFootingAnalysisMethod,
    CombinedFootingContractError,
    CombinedFootingDesignDisposition,
    CombinedFootingDesignInput,
    CombinedFootingGeometryInput,
    CombinedFootingInput,
    CombinedFootingMaterialInput,
    CombinedFootingPressureModel,
    CombinedFootingReinforcementInput,
    CombinedFootingStrengthResult,
    CombinedFootingSupportingAreaBasis,
    CombinedFootingTransferInput,
    check_symmetric_combined_footing_strength,
)

__all__ = [
    "SymmetricCombinedFootingDesignInput",
    "SymmetricCombinedFootingDesignProvenance",
    "SymmetricCombinedFootingDesignResult",
    "SymmetricCombinedFootingDesignStatus",
    "build_symmetric_combined_footing_design_input",
    "design_symmetric_combined_footing_is456",
]


_SUPPORTED_CASE = (
    "Exactly two identical square columns with equal concentric axial loads on "
    "one symmetric rigid rectangular constant-depth footing on soil, using an "
    "externally approved uniform pressure model and caller-provided reinforcement, "
    "supporting-area, and dowel evidence."
)
_HELD_CASES = (
    "Unequal or eccentric loads, column moments, horizontal actions, uplift or load reversal, property-line layouts, trapezoidal or irregular plans, alternate columns, pedestals, openings, and variable-depth footings are excluded.",
    "Flexible, variable, nonlinear, or tensile soil pressure; bearing-capacity or settlement calculation; elastic-line, Winkler, plate, finite-element, and soil-structure-interaction analysis are excluded.",
    "Shear or punching reinforcement, coated, bundled, spliced or curtailed bars, automatic sizing or bar selection, durability selection, and construction approval are excluded.",
    "Strap footings, pile caps, raft foundations, React publication, release, professional approval, and complete engineering approval are excluded.",
)


class SymmetricCombinedFootingDesignStatus(StrEnum):
    """Aggregate disposition for the bounded public workflow."""

    PASS = "PASS"  # nosec B105 - engineering disposition, not a credential
    FAIL = "FAIL"


@dataclass(frozen=True)
class SymmetricCombinedFootingDesignInput:
    """Case identity, A/B typed design input, and review acknowledgement."""

    case_id: str
    footing: CombinedFootingDesignInput
    qualified_review_required: bool


@dataclass(frozen=True)
class SymmetricCombinedFootingDesignProvenance:
    """Stable workflow, benchmark, source, and caller-basis identity."""

    schema_version: str
    code_edition: str
    workflow: str
    case_id: str
    benchmark_id: str
    action_generation_status: str
    soil_verification_status: str
    geometry_basis_reference: str
    rigidity_basis_reference: str
    load_basis_reference: str
    bearing_settlement_basis_reference: str
    cancellation_basis_reference: str
    material_basis_reference: str
    detailing_basis_reference: str
    transfer_basis_reference: str
    clause_refs: tuple[str, ...]
    source_refs: tuple[str, ...]


@dataclass(frozen=True)
class SymmetricCombinedFootingDesignResult:
    """Composed A/B result with the supported case and retained holds."""

    case_id: str
    status: SymmetricCombinedFootingDesignStatus
    strength: CombinedFootingStrengthResult
    supported_case: str
    held_cases: tuple[str, ...]
    provenance: SymmetricCombinedFootingDesignProvenance
    qualified_review_required: bool = True
    complete_engineering_design_approved: bool = False

    @property
    def is_safe_within_supported_scope(self) -> bool:
        """Return whether every represented A/B comparison passes."""

        return self.status is SymmetricCombinedFootingDesignStatus.PASS


def _require_non_blank(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CombinedFootingContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _source_refs(*groups: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for group in groups for item in group))


def _mapping(value: object, field_name: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CombinedFootingContractError(f"{field_name} must be an object")
    return dict(value)


def build_symmetric_combined_footing_design_input(
    payload: Mapping[str, Any],
) -> SymmetricCombinedFootingDesignInput:
    """Build the service contract from an already transport-validated mapping."""
    values = dict(payload)
    try:
        footing_values = _mapping(values.pop("footing"), "footing")
        analysis_values = _mapping(footing_values.pop("analysis"), "footing.analysis")
        geometry_values = _mapping(
            analysis_values.pop("geometry"), "footing.analysis.geometry"
        )
        geometry_values["analysis_method"] = CombinedFootingAnalysisMethod(
            geometry_values["analysis_method"]
        )
        geometry_values["pressure_model"] = CombinedFootingPressureModel(
            geometry_values["pressure_model"]
        )
        transfer_values = _mapping(footing_values.pop("transfer"), "footing.transfer")
        transfer_values["effective_supporting_area_basis"] = (
            CombinedFootingSupportingAreaBasis(
                transfer_values["effective_supporting_area_basis"]
            )
        )
        return SymmetricCombinedFootingDesignInput(
            **values,
            footing=CombinedFootingDesignInput(
                analysis=CombinedFootingInput(
                    geometry=CombinedFootingGeometryInput(**geometry_values),
                    actions=CombinedFootingActionInput(
                        **_mapping(
                            analysis_values.pop("actions"),
                            "footing.analysis.actions",
                        )
                    ),
                    **analysis_values,
                ),
                material=CombinedFootingMaterialInput(
                    **_mapping(footing_values.pop("material"), "footing.material")
                ),
                reinforcement=CombinedFootingReinforcementInput(
                    **_mapping(
                        footing_values.pop("reinforcement"),
                        "footing.reinforcement",
                    )
                ),
                transfer=CombinedFootingTransferInput(**transfer_values),
                **footing_values,
            ),
        )
    except CombinedFootingContractError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise CombinedFootingContractError(
            "transport payload does not match the symmetric combined-footing input"
        ) from exc


def design_symmetric_combined_footing_is456(
    request: SymmetricCombinedFootingDesignInput,
) -> SymmetricCombinedFootingDesignResult:
    """Compose the sole G0-approved symmetric combined-footing workflow."""

    if not isinstance(request, SymmetricCombinedFootingDesignInput):
        raise CombinedFootingContractError(
            "request must be a SymmetricCombinedFootingDesignInput"
        )
    case_id = _require_non_blank(request.case_id, "case_id")
    if not isinstance(request.footing, CombinedFootingDesignInput):
        raise CombinedFootingContractError(
            "footing must be a CombinedFootingDesignInput"
        )
    if request.qualified_review_required is not True:
        raise CombinedFootingContractError(
            "qualified_review_required must be true for this workflow"
        )

    strength = check_symmetric_combined_footing_strength(request.footing)
    status = (
        SymmetricCombinedFootingDesignStatus.PASS
        if strength.disposition is CombinedFootingDesignDisposition.PASS
        else SymmetricCombinedFootingDesignStatus.FAIL
    )
    analysis = request.footing.analysis
    provenance = SymmetricCombinedFootingDesignProvenance(
        schema_version="1.0",
        code_edition="IS 456:2000 through Amendment 6",
        workflow="design_symmetric_combined_footing_is456",
        case_id=case_id,
        benchmark_id="INDIA-2-COMBINED-HAND-01",
        action_generation_status=(
            "recomputed_from_caller_supplied_approved_service_and_factored_actions"
        ),
        soil_verification_status=(
            "caller_approved_bearing_settlement_and_uniform_pressure_not_calculated"
        ),
        geometry_basis_reference=analysis.geometry.geometry_basis_reference,
        rigidity_basis_reference=analysis.geometry.rigidity_basis_reference,
        load_basis_reference=analysis.actions.load_basis_reference,
        bearing_settlement_basis_reference=(
            analysis.actions.bearing_settlement_basis_reference
        ),
        cancellation_basis_reference=analysis.actions.cancellation_basis_reference,
        material_basis_reference=request.footing.material.material_basis_reference,
        detailing_basis_reference=(
            request.footing.reinforcement.detailing_basis_reference
        ),
        transfer_basis_reference=request.footing.transfer.transfer_basis_reference,
        clause_refs=strength.clause_refs,
        source_refs=_source_refs(
            strength.source_refs,
            (
                "IS456-PUBLIC-DISTRIBUTION-001",
                "INDIA-2-COMBINED-HAND-01",
            ),
        ),
    )
    return SymmetricCombinedFootingDesignResult(
        case_id=case_id,
        status=status,
        strength=strength,
        supported_case=_SUPPORTED_CASE,
        held_cases=_HELD_CASES,
        provenance=provenance,
    )
