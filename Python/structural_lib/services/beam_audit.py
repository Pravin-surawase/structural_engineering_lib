"""W3E: strict, same-row beam-strength audit; no application or file I/O.

An accepted evaluation is software evidence, not approval of installed steel,
serviceability, a global model, or a professional design. Every retained row is
checked: independent component extrema are never assembled into a load state.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal, Self

from pydantic import Field, ValidationError, model_validator

from structural_lib.core.analysis_contracts import (
    BeamActionRowV1,
    BeamDemandPurposeV1,
    BeamDemandSnapshotV1,
    EvidenceStateV1,
    EvidenceValueV1,
)
from structural_lib.core.errors import StructuralLibError
from structural_lib.services import canonical_beam
from structural_lib.services.contracts.beam import (
    BeamActionsV1,
    BeamCalculationBasisV1,
    BeamDesignInputV1,
    BeamDetailingOptionsV1,
    IS456MaterialsV1,
    IS456ReinforcementMaterialsV1,
    MemberIdentityV1,
    RectangularBeamSectionV1,
)
from structural_lib.services.contracts.common import StrictPublicModel
from structural_lib.services.contracts.etabs_w3 import (
    BeamDemandDerivationRequestV1,
    W3BuildIssueV1,
    W3BuildStatusV1,
    _project_action_rows,
    derive_beam_demand_snapshot_v1,
)

__all__ = [
    "BeamAuditApplicabilityBasisV1",
    "BeamAuditMemberBasisV1",
    "BeamAuditInputBuildRequestV1",
    "BeamAuditInputBuildResultV1",
    "BeamAuditInputsV1",
    "BeamAuditRowInputV1",
    "BeamAuditCheckV1",
    "BeamAuditRowResultV1",
    "BeamAuditEvaluationRequestV1",
    "BeamAuditEvaluationResultV1",
    "build_beam_audit_inputs_v1",
    "evaluate_beam_audit_v1",
]

_SHA = r"^[0-9a-f]{64}$"


class BeamAuditApplicabilityBasisV1(StrictPublicModel):
    """Caller-owned engineering applicability, never inferred from labels.

    The excluded-action bounds are caller criteria, NOT library recommendations.
    M3 sign-to-tension-face mapping is explicit even though the canonical strength
    route uses magnitudes. This route designs required steel, not installed rebar.
    """

    scope: Literal["RECTANGULAR_MAJOR_AXIS_STRENGTH"]
    factored_action_basis: str = Field(min_length=1)
    max_abs_axial_kn: float = Field(ge=0)
    max_abs_minor_shear_kn: float = Field(ge=0)
    max_abs_minor_moment_knm: float = Field(ge=0)
    positive_m3_tension_face: Literal["TOP", "BOTTOM"]
    negative_m3_tension_face: Literal["TOP", "BOTTOM"]

    @model_validator(mode="after")
    def _opposite_faces(self) -> Self:
        if self.positive_m3_tension_face == self.negative_m3_tension_face:
            raise ValueError("opposite M3 signs require opposite tension faces")
        return self


class BeamAuditMemberBasisV1(StrictPublicModel):
    member_id: str = Field(min_length=1)
    section: EvidenceValueV1[RectangularBeamSectionV1]
    materials: EvidenceValueV1[IS456MaterialsV1 | IS456ReinforcementMaterialsV1]
    calculation_basis: EvidenceValueV1[BeamCalculationBasisV1]
    detailing: EvidenceValueV1[BeamDetailingOptionsV1]
    applicability: EvidenceValueV1[BeamAuditApplicabilityBasisV1]
    # Required serviceability blocks until the canonical typed route exists.
    serviceability_basis: EvidenceValueV1[str]
    assumptions: tuple[str, ...] = Field(min_length=1)


class BeamAuditInputBuildRequestV1(StrictPublicModel):
    demand: BeamDemandDerivationRequestV1
    accepted_snapshot: BeamDemandSnapshotV1
    member_bases: tuple[BeamAuditMemberBasisV1, ...] = Field(min_length=1)
    require_serviceability: bool
    max_action_rows: int = Field(ge=1, le=10000)


class BeamAuditRowInputV1(StrictPublicModel):
    action: BeamActionRowV1
    canonical_request: BeamDesignInputV1
    tension_face: Literal["TOP", "BOTTOM", "ZERO_MOMENT"]
    demand_governing_reference_ids: tuple[str, ...]
    basis_source_references: tuple[str, ...]
    assumptions: tuple[str, ...]
    serviceability_basis: EvidenceValueV1[str]


class BeamAuditInputsV1(StrictPublicModel):
    schema_version: Literal["beam-audit-inputs/v1"] = "beam-audit-inputs/v1"
    source_request: BeamAuditInputBuildRequestV1
    rows: tuple[BeamAuditRowInputV1, ...] = Field(min_length=1)
    inputs_sha256: str = Field(pattern=_SHA)


class BeamAuditInputBuildResultV1(StrictPublicModel):
    status: W3BuildStatusV1
    issues: tuple[W3BuildIssueV1, ...]
    inputs: BeamAuditInputsV1 | None

    @model_validator(mode="after")
    def _complete_or_blocked(self) -> Self:
        if self.status is W3BuildStatusV1.ACCEPTED:
            if self.inputs is None or self.issues:
                raise ValueError(
                    "accepted build requires complete inputs and no issues"
                )
        elif self.inputs is not None or not self.issues:
            raise ValueError("blocked build requires issues and no partial inputs")
        return self


class BeamAuditCheckV1(StrictPublicModel):
    check: Literal["flexure", "shear", "torsion", "serviceability"]
    scenario_id: str
    action_row_id: str
    outcome: EvidenceValueV1[Literal["PASS", "FAIL"]]
    utilization: EvidenceValueV1[float]
    clause_references: tuple[str, ...] = Field(min_length=1)


class BeamAuditRowResultV1(StrictPublicModel):
    input: BeamAuditRowInputV1
    checks: tuple[BeamAuditCheckV1, ...]
    canonical_result_json: str
    canonical_result_sha256: str = Field(pattern=_SHA)


class BeamAuditEvaluationRequestV1(StrictPublicModel):
    inputs: BeamAuditInputsV1


class BeamAuditEvaluationResultV1(StrictPublicModel):
    schema_version: Literal["beam-audit-evaluation/v1"] = "beam-audit-evaluation/v1"
    status: W3BuildStatusV1
    verdict: Literal["PASS", "FAIL", "HELD", "BLOCKED"]
    issues: tuple[W3BuildIssueV1, ...]
    inputs_sha256: str = Field(pattern=_SHA)
    rows: tuple[BeamAuditRowResultV1, ...]
    # Actual check governors, not an artificial concurrent action vector.
    governing_checks: tuple[BeamAuditCheckV1, ...]
    evaluation_sha256: str = Field(pattern=_SHA)
    limitations: tuple[str, ...] = (
        "Software strength-design checks only; required steel is not installed-steel acceptance.",
        "Canonical serviceability remains held; no global analysis or professional approval.",
        "Independent extrema remain references only; every evaluation uses one signed source row.",
    )

    @model_validator(mode="after")
    def _complete_or_blocked(self) -> Self:
        if self.status is W3BuildStatusV1.BLOCKED:
            if (
                not self.issues
                or self.rows
                or self.governing_checks
                or self.verdict != "BLOCKED"
            ):
                raise ValueError(
                    "blocked evaluation exposes issues and no partial results"
                )
        elif self.issues or not self.rows or self.verdict == "BLOCKED":
            raise ValueError(
                "accepted evaluation requires complete results and no issues"
            )
        return self


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _issue(code: str, path: str, message: str) -> W3BuildIssueV1:
    return W3BuildIssueV1(code=code, path=path, message=message)


def build_beam_audit_inputs_v1(
    request: BeamAuditInputBuildRequestV1, /
) -> BeamAuditInputBuildResultV1:
    """Re-derive accepted demand, bind explicit bases, and project every row."""
    derived = derive_beam_demand_snapshot_v1(request.demand)
    issues = list(derived.issues)
    if derived.snapshot != request.accepted_snapshot:
        issues.append(
            _issue(
                "BEAM_AUDIT_DEMAND_MISMATCH",
                "accepted_snapshot",
                "snapshot must equal canonical re-derivation",
            )
        )
    if request.demand.scenario.purpose is not BeamDemandPurposeV1.STRENGTH:
        issues.append(
            _issue(
                "BEAM_AUDIT_PURPOSE_HELD",
                "demand.scenario",
                "canonical strength requires an explicit STRENGTH scenario",
            )
        )
    if any(
        check.state is EvidenceStateV1.BLOCKED
        for check in request.demand.scenario.held_checks
    ):
        issues.append(
            _issue(
                "BEAM_AUDIT_SCENARIO_CHECK_BLOCKED",
                "demand.scenario.held_checks",
                "BLOCKED scenario evidence cannot produce an accepted parent audit",
            )
        )
    if issues:
        return BeamAuditInputBuildResultV1(
            status=W3BuildStatusV1.BLOCKED, issues=tuple(issues), inputs=None
        )
    actions = _project_action_rows(
        request.demand.baseline, request.demand.catalogue, request.demand.scenario
    )
    if len(actions) > request.max_action_rows:
        issues.append(
            _issue(
                "BEAM_AUDIT_CAPACITY_EXCEEDED",
                "max_action_rows",
                "complete row domain exceeds explicit bound; no truncation",
            )
        )
    bases = {basis.member_id: basis for basis in request.member_bases}
    if len(bases) != len(request.member_bases) or set(bases) != {
        row.member_id for row in actions
    }:
        issues.append(
            _issue(
                "BEAM_AUDIT_MEMBER_BASIS_MISMATCH",
                "member_bases",
                "exactly one explicit basis is required per retained member",
            )
        )
    frames = {frame.member_id: frame for frame in request.demand.baseline.frames}
    rows: list[BeamAuditRowInputV1] = []
    for action in actions:
        basis = bases.get(action.member_id)
        frame = frames.get(action.member_id)
        if basis is None or frame is None:
            issues.append(
                _issue(
                    "BEAM_AUDIT_MEMBER_MISSING",
                    action.row_id,
                    "retained member requires both frame identity and explicit basis",
                )
            )
            continue
        service = basis.serviceability_basis
        if service.state is EvidenceStateV1.BLOCKED or (
            request.require_serviceability
            and service.state is not EvidenceStateV1.NOT_APPLICABLE
        ):
            issues.append(
                _issue(
                    "BEAM_AUDIT_REQUIRED_SERVICEABILITY_BLOCKED",
                    f"member_bases:{action.member_id}.serviceability_basis",
                    "Required serviceability cannot be evaluated by the current canonical route; "
                    f"scenario={request.demand.scenario.scenario_id}, row={action.row_id}, "
                    f"source_state={service.state.value}. No partial accepted audit is returned.",
                )
            )
            continue
        fields = (
            basis.section,
            basis.materials,
            basis.calculation_basis,
            basis.detailing,
            basis.applicability,
        )
        if any(field.state is not EvidenceStateV1.PRESENT for field in fields):
            issues.append(
                _issue(
                    "BEAM_AUDIT_REQUIRED_BASIS_HELD",
                    action.row_id,
                    "section/material/calculation/detailing/applicability evidence must all be PRESENT",
                )
            )
            continue
        section, materials, calculation, detailing, applicability = (
            field.value for field in fields
        )
        assert isinstance(section, RectangularBeamSectionV1)
        assert isinstance(materials, IS456MaterialsV1)
        assert isinstance(calculation, BeamCalculationBasisV1)
        assert isinstance(detailing, BeamDetailingOptionsV1)
        assert isinstance(applicability, BeamAuditApplicabilityBasisV1)
        if (section.b_mm, section.D_mm, section.span_mm) != (
            frame.section.width_t2_mm,
            frame.section.depth_t3_mm,
            frame.local_axis.length_mm,
        ):
            issues.append(
                _issue(
                    "BEAM_AUDIT_GEOMETRY_MISMATCH",
                    action.row_id,
                    "section and span must equal the accepted baseline; candidates require a new identity",
                )
            )
            continue
        if (
            abs(action.p_kn) > applicability.max_abs_axial_kn
            or abs(action.v3_kn) > applicability.max_abs_minor_shear_kn
            or abs(action.m2_knm) > applicability.max_abs_minor_moment_knm
        ):
            issues.append(
                _issue(
                    "BEAM_AUDIT_APPLICABILITY_EXCEEDED",
                    action.row_id,
                    "excluded signed action exceeds the explicit caller-owned applicability bound",
                )
            )
            continue
        try:
            canonical = BeamDesignInputV1(
                identity=MemberIdentityV1(
                    member_id=action.member_id,
                    story=frame.story,
                    case_id=action.selection_id,
                ),
                section=section,
                materials=materials,
                actions=BeamActionsV1(
                    mu_knm=abs(action.m3_knm),
                    vu_kn=abs(action.v2_kn),
                    tu_knm=abs(action.t_knm),
                ),
                calculation_basis=calculation,
                detailing=detailing,
                source_provenance=f"beam-audit:{request.accepted_snapshot.snapshot_sha256}:{action.row_sha256}",
            )
        except ValidationError as exc:
            issues.append(
                _issue("BEAM_AUDIT_CANONICAL_INPUT_BLOCKED", action.row_id, str(exc))
            )
            continue
        face: Literal["TOP", "BOTTOM", "ZERO_MOMENT"] = "ZERO_MOMENT"
        if action.m3_knm > 0:
            face = applicability.positive_m3_tension_face
        elif action.m3_knm < 0:
            face = applicability.negative_m3_tension_face
        rows.append(
            BeamAuditRowInputV1(
                action=action,
                canonical_request=canonical,
                tension_face=face,
                demand_governing_reference_ids=tuple(
                    ref.reference_id
                    for ref in request.accepted_snapshot.governing_references
                    if action.row_id in ref.action_row_ids
                ),
                basis_source_references=tuple(
                    dict.fromkeys(
                        ref for field in fields for ref in field.source_references
                    )
                ),
                assumptions=basis.assumptions
                + (
                    applicability.factored_action_basis,
                    "Canonical Mu/Vu/Tu are magnitudes projected together from this one retained signed row.",
                ),
                serviceability_basis=basis.serviceability_basis,
            )
        )
    if issues:
        return BeamAuditInputBuildResultV1(
            status=W3BuildStatusV1.BLOCKED, issues=tuple(issues), inputs=None
        )
    provisional = BeamAuditInputsV1(
        source_request=request, rows=tuple(rows), inputs_sha256="0" * 64
    )
    payload = provisional.model_dump(mode="json", exclude={"inputs_sha256"})
    inputs = provisional.model_copy(update={"inputs_sha256": _sha(_json(payload))})
    return BeamAuditInputBuildResultV1(
        status=W3BuildStatusV1.ACCEPTED, issues=(), inputs=inputs
    )


def _not_evaluated(
    state: EvidenceStateV1, code: str, message: str, refs: tuple[str, ...]
) -> dict[str, object]:
    return {
        "state": state,
        "value": None,
        "reason_code": code,
        "message": message,
        "source_references": refs,
    }


def _evaluation_result(**values: object) -> BeamAuditEvaluationResultV1:
    result = BeamAuditEvaluationResultV1.model_validate(
        {**values, "evaluation_sha256": "0" * 64}
    )
    payload = result.model_dump(mode="json", exclude={"evaluation_sha256"})
    return result.model_copy(update={"evaluation_sha256": _sha(_json(payload))})


def evaluate_beam_audit_v1(
    request: BeamAuditEvaluationRequestV1, /
) -> BeamAuditEvaluationResultV1:
    """Run canonical strength per row with exact clause/result provenance."""
    inputs = request.inputs
    rebuilt = build_beam_audit_inputs_v1(inputs.source_request)
    if rebuilt.inputs != inputs:
        return _evaluation_result(
            status=W3BuildStatusV1.BLOCKED,
            verdict="BLOCKED",
            issues=(
                _issue(
                    "BEAM_AUDIT_INPUT_IDENTITY_INVALID",
                    "inputs",
                    "inputs must equal complete canonical rebuild",
                ),
            ),
            inputs_sha256=inputs.inputs_sha256,
            rows=(),
            governing_checks=(),
        )
    rows: list[BeamAuditRowResultV1] = []
    issues: list[W3BuildIssueV1] = []
    scenario_id = inputs.source_request.demand.scenario.scenario_id
    for row in inputs.rows:
        refs = (
            f"scenario:{scenario_id}",
            f"action:{row.action.row_sha256}",
            f"inputs:{inputs.inputs_sha256}",
        )
        try:
            result = canonical_beam.check(row.canonical_request)
            serialized = _json(result.to_dict())
        except (StructuralLibError, ValueError, ArithmeticError) as exc:
            issues.append(
                _issue(
                    "BEAM_AUDIT_CALCULATION_BLOCKED",
                    row.action.row_id,
                    f"{type(exc).__name__}: {exc}",
                )
            )
            continue
        calculation = result.calculation
        checks: list[BeamAuditCheckV1] = []
        for name in ("flexure", "shear", "torsion"):
            item = getattr(calculation, name)
            if item is None:
                missing = _not_evaluated(
                    EvidenceStateV1.NOT_APPLICABLE,
                    "ZERO_TORSION_DEMAND",
                    "The retained row has exactly zero torsion.",
                    refs,
                )
                outcome = EvidenceValueV1[Literal["PASS", "FAIL"]].model_validate(
                    missing
                )
                utilization = EvidenceValueV1[float].model_validate(missing)
            else:
                outcome = EvidenceValueV1[Literal["PASS", "FAIL"]](
                    state=EvidenceStateV1.PRESENT,
                    value="PASS" if item.is_safe else "FAIL",
                    source_references=refs,
                )
                utilization = EvidenceValueV1[float](
                    state=EvidenceStateV1.PRESENT,
                    value=calculation.utilizations[name],
                    source_references=refs,
                )
            checks.append(
                BeamAuditCheckV1(
                    check=name,
                    scenario_id=scenario_id,
                    action_row_id=row.action.row_id,
                    outcome=outcome,
                    utilization=utilization,
                    clause_references=(
                        calculation.clause_refs.get(
                            name, "IS 456 Cl 41; zero torsion scope"
                        ),
                    ),
                )
            )
        service = row.serviceability_basis
        state = (
            service.state
            if service.state is not EvidenceStateV1.PRESENT
            else EvidenceStateV1.UNAVAILABLE
        )
        missing = _not_evaluated(
            state,
            service.reason_code or "CANONICAL_SERVICEABILITY_SCOPE_HOLD",
            service.message
            or "Strict canonical serviceability is not implemented; supplied basis retained without a pass claim.",
            refs + service.source_references,
        )
        checks.append(
            BeamAuditCheckV1(
                check="serviceability",
                scenario_id=scenario_id,
                action_row_id=row.action.row_id,
                outcome=EvidenceValueV1[Literal["PASS", "FAIL"]].model_validate(
                    missing
                ),
                utilization=EvidenceValueV1[float].model_validate(missing),
                clause_references=(
                    calculation.clause_refs["deflection"],
                    calculation.clause_refs["crack_width"],
                ),
            )
        )
        rows.append(
            BeamAuditRowResultV1(
                input=row,
                checks=tuple(checks),
                canonical_result_json=serialized,
                canonical_result_sha256=_sha(serialized),
            )
        )
    if issues:
        return _evaluation_result(
            status=W3BuildStatusV1.BLOCKED,
            verdict="BLOCKED",
            issues=tuple(issues),
            inputs_sha256=inputs.inputs_sha256,
            rows=(),
            governing_checks=(),
        )
    governors: list[BeamAuditCheckV1] = []
    for member_id in sorted({row.input.action.member_id for row in rows}):
        for name in ("flexure", "shear", "torsion"):
            candidates = [
                (row, check)
                for row in rows
                if row.input.action.member_id == member_id
                for check in row.checks
                if check.check == name and check.utilization.value is not None
            ]
            if candidates:
                _, governor = min(
                    candidates,
                    key=lambda pair: (
                        pair[1].outcome.value != "FAIL",
                        -float(pair[1].utilization.value or 0),
                        pair[0].input.action.source_row_index,
                        pair[0].input.action.row_id,
                    ),
                )
                governors.append(governor)
    failed = any(check.outcome.value == "FAIL" for row in rows for check in row.checks)
    held = bool(inputs.source_request.demand.scenario.held_checks) or (
        inputs.source_request.require_serviceability
        and any(
            row.input.serviceability_basis.state is not EvidenceStateV1.NOT_APPLICABLE
            for row in rows
        )
    )
    return _evaluation_result(
        status=W3BuildStatusV1.ACCEPTED,
        verdict="FAIL" if failed else "HELD" if held else "PASS",
        issues=(),
        inputs_sha256=inputs.inputs_sha256,
        rows=tuple(rows),
        governing_checks=tuple(governors),
    )
