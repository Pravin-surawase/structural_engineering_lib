"""Versioned, host-free beam project and design-profile contracts."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .semantics import (
    ApplicabilityState,
    Diagnostic,
    EngineeringState,
    OperationResult,
    Provenance,
    completed_result,
    effective_inputs,
    rejected_result,
    semantic_hash,
)

CREATE_BEAM_PROJECT_OPERATION = "structural.beam_project.create/v1"
PROJECT_METHOD_REVISION = "structural-beam-project-wp06-v1"


class CheckScope(StrEnum):
    MEMBER = "member"
    SPAN = "span"
    STATION = "station"
    FACE = "face"
    AXIS = "axis"
    BAR_END = "bar_end"
    ARRANGEMENT = "arrangement"


class SeismicDesignProfile(StrEnum):
    ORDINARY_IS456 = "ordinary_is456"
    IS13920_2016 = "is13920_2016"


@dataclass(frozen=True)
class StructuralUnitBasis:
    length_unit: str
    force_unit: str
    moment_unit: str
    stress_unit: str


@dataclass(frozen=True)
class RevisionBinding:
    binding_id: str
    revision_id: str
    source_reference: str


@dataclass(frozen=True)
class DesignCriterion:
    criterion_id: str
    value: float
    unit: str
    source_reference: str


@dataclass(frozen=True)
class DesignCheckRule:
    rule_id: str
    operation_semantic_id: str
    scope: CheckScope
    expected_applicability: ApplicabilityState
    source_reference: str
    code_data_binding_id: str | None = None


@dataclass(frozen=True)
class BeamProjectDefinition:
    project_id: str
    name: str
    revision_id: str


@dataclass(frozen=True)
class BeamDesignProfile:
    profile_id: str
    revision_id: str
    design_code: str
    seismic_design_profile: SeismicDesignProfile
    check_rules: tuple[DesignCheckRule, ...]
    criteria: tuple[DesignCriterion, ...]


@dataclass(frozen=True)
class BeamProjectRequest:
    project: BeamProjectDefinition
    unit_basis: StructuralUnitBasis
    code_data_revisions: tuple[RevisionBinding, ...]
    profile: BeamDesignProfile
    catalogue_revisions: tuple[RevisionBinding, ...] = ()


@dataclass(frozen=True)
class BeamProject:
    project_basis_id: str
    project: BeamProjectDefinition
    unit_basis: StructuralUnitBasis
    code_data_revisions: tuple[RevisionBinding, ...]
    catalogue_revisions: tuple[RevisionBinding, ...]
    profile: BeamDesignProfile


def _diagnostic(code: str, message: str, field: str, remediation: str) -> Diagnostic:
    return Diagnostic(
        code,
        "error",
        message,
        CREATE_BEAM_PROJECT_OPERATION,
        field,
        "beam-project",
        remediation,
    )


def _text(value: str | None) -> bool:
    return bool(value and value.strip())


def _leaf_identifier(value: str | None) -> bool:
    return _text(value) and "@" not in value


def _unique_text(items: tuple[Any, ...], attribute: str) -> bool:
    values = [getattr(item, attribute, None) for item in items]
    return all(_text(value) for value in values) and len(values) == len(set(values))


def _provenance() -> Provenance:
    return Provenance(
        "project-basis-wp06-v1",
        PROJECT_METHOD_REVISION,
        (
            "PF4 semantic identity and effective-input rules",
            "PF5 AO14 versioned beam project contract",
        ),
    )


def create_beam_project(request: BeamProjectRequest) -> OperationResult:
    """Validate and return an immutable beam project/profile basis."""

    inputs = effective_inputs(request=request)
    provenance = _provenance()
    project = request.project
    profile = request.profile

    if not all(
        _text(value)
        for value in (
            project.project_id,
            project.name,
            project.revision_id,
            profile.profile_id,
            profile.revision_id,
            profile.design_code,
        )
    ):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROJECT.IDENTITY",
                    "Project and profile identities, names, revisions, and design code are required.",
                    "project,profile",
                    "Supply immutable project and profile revision identities.",
                ),
            ),
            provenance=provenance,
        )

    if request.unit_basis != StructuralUnitBasis("mm", "N", "Nmm", "N/mm2"):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "UNITS.UNSUPPORTED",
                    "WP06 requires the canonical mm, N, Nmm, and N/mm2 unit basis.",
                    "unit_basis",
                    "Normalize values at the adapter boundary before creating the project.",
                ),
            ),
            provenance=provenance,
        )

    if not isinstance(profile.seismic_design_profile, SeismicDesignProfile):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.SEISMIC",
                    "The design profile requires an explicit supported seismic applicability.",
                    "profile.seismic_design_profile",
                    "Select ordinary_is456 or is13920_2016.",
                ),
            ),
            provenance=provenance,
        )

    if not request.code_data_revisions or not _unique_text(
        request.code_data_revisions, "binding_id"
    ):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "REVISION.CODE_DATA",
                    "Code-data bindings are required and their binding ids must be unique.",
                    "code_data_revisions",
                    "Supply one identified current revision per code-data family.",
                ),
            ),
            provenance=provenance,
        )
    all_revisions = (*request.code_data_revisions, *request.catalogue_revisions)
    if any(
        not _text(binding.revision_id) or not _text(binding.source_reference)
        for binding in all_revisions
    ) or not _unique_text(all_revisions, "binding_id"):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "REVISION.INVALID",
                    "Every code-data and catalogue binding requires a revision and source reference.",
                    "code_data_revisions,catalogue_revisions",
                    "Correct duplicate or incomplete revision bindings.",
                ),
            ),
            provenance=provenance,
        )

    if not profile.check_rules or not _unique_text(profile.check_rules, "rule_id"):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.CHECK_RULES",
                    "At least one uniquely identified required-check rule is needed.",
                    "profile.check_rules",
                    "Declare each required operation and scope once.",
                ),
            ),
            provenance=provenance,
        )
    if any(not _leaf_identifier(rule.rule_id) for rule in profile.check_rules):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.RULE_ID_INVALID",
                    "Check-rule ids must be nonempty and cannot contain the leaf-id separator '@'.",
                    "profile.check_rules",
                    "Use stable rule ids without '@'.",
                ),
            ),
            provenance=provenance,
        )
    code_binding_ids = {
        binding.binding_id for binding in request.code_data_revisions
    }
    if any(
        not _text(rule.operation_semantic_id)
        or not _text(rule.source_reference)
        or not isinstance(rule.scope, CheckScope)
        or rule.expected_applicability
        not in (ApplicabilityState.APPLICABLE, ApplicabilityState.NOT_APPLICABLE)
        or rule.code_data_binding_id is not None
        and rule.code_data_binding_id not in code_binding_ids
        for rule in profile.check_rules
    ):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.CHECK_RULE_INVALID",
                    "Each check rule needs an operation, scope, expected applicability, source, and valid code-data binding.",
                    "profile.check_rules",
                    "Correct the check-rule operation and revision references.",
                ),
            ),
            provenance=provenance,
        )
    rule_keys = [
        (rule.operation_semantic_id, rule.scope) for rule in profile.check_rules
    ]
    if len(rule_keys) != len(set(rule_keys)):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.CHECK_RULE_CONFLICT",
                    "Two rules define the same operation and scope.",
                    "profile.check_rules",
                    "Remove the conflicting project default.",
                ),
            ),
            provenance=provenance,
        )

    seismic_rules = [
        rule
        for rule in profile.check_rules
        if rule.operation_semantic_id
        == "is456.beam.seismic_detailing.check/v1"
    ]
    expected_seismic = (
        ApplicabilityState.NOT_APPLICABLE
        if profile.seismic_design_profile is SeismicDesignProfile.ORDINARY_IS456
        else ApplicabilityState.APPLICABLE
    )
    if len(seismic_rules) != 1 or seismic_rules[0].expected_applicability is not expected_seismic:
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.SEISMIC_CONFLICT",
                    "The seismic check rule must match the selected seismic design profile.",
                    "profile.check_rules",
                    "Declare one seismic rule with the profile-resolved applicability.",
                ),
            ),
            provenance=provenance,
        )

    if not profile.criteria or not _unique_text(profile.criteria, "criterion_id") or any(
        not math.isfinite(criterion.value)
        or not _text(criterion.unit)
        or not _text(criterion.source_reference)
        for criterion in profile.criteria
    ):
        return rejected_result(
            CREATE_BEAM_PROJECT_OPERATION,
            inputs,
            (
                _diagnostic(
                    "PROFILE.CRITERIA",
                    "Design criteria require unique ids, finite values, units, and sources.",
                    "profile.criteria",
                    "Resolve conflicting or incomplete design criteria.",
                ),
            ),
            provenance=provenance,
        )

    output = BeamProject(
        semantic_hash("beam_project_basis_id", request),
        project,
        request.unit_basis,
        request.code_data_revisions,
        request.catalogue_revisions,
        profile,
    )
    return completed_result(
        CREATE_BEAM_PROJECT_OPERATION,
        inputs,
        {"project": output},
        engineering=EngineeringState.PASS,
        provenance=provenance,
    )


__all__ = [
    "BeamDesignProfile",
    "BeamProject",
    "BeamProjectDefinition",
    "BeamProjectRequest",
    "CheckScope",
    "DesignCheckRule",
    "DesignCriterion",
    "RevisionBinding",
    "SeismicDesignProfile",
    "StructuralUnitBasis",
    "create_beam_project",
]
