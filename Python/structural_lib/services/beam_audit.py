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
from structural_lib.services.contracts.beam_serviceability import (
    BeamServiceabilityChecksV1,
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
    "BeamAuditServiceabilityRowV1",
    "BeamAuditServiceabilityV1",
    "BeamAuditInputBuildRequestV1",
    "BeamAuditInputBuildResultV1",
    "BeamAuditInputsV1",
    "BeamAuditRowInputV1",
    "BeamAuditRowEvaluationRequestV1",
    "BeamAuditRowEvaluationResultV1",
    "BeamAuditCheckV1",
    "BeamAuditRowResultV1",
    "BeamAuditEvaluationRequestV1",
    "BeamAuditEvaluationResultV1",
    "build_beam_audit_inputs_v1",
    "canonical_beam_action_row_sha256_v1",
    "evaluate_beam_audit_v1",
    "evaluate_beam_audit_row_v1",
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


class BeamAuditServiceabilityRowV1(StrictPublicModel):
    """Explicit association, not a conversion from ULS to SLS demand."""

    action_row_id: str = Field(min_length=1)
    action_row_sha256: str = Field(pattern=_SHA)
    checks: BeamServiceabilityChecksV1


class BeamAuditServiceabilityV1(StrictPublicModel):
    rows: tuple[BeamAuditServiceabilityRowV1, ...] = Field(min_length=1)


class BeamAuditMemberBasisV1(StrictPublicModel):
    member_id: str = Field(min_length=1)
    section: EvidenceValueV1[RectangularBeamSectionV1]
    materials: EvidenceValueV1[IS456MaterialsV1 | IS456ReinforcementMaterialsV1]
    calculation_basis: EvidenceValueV1[BeamCalculationBasisV1]
    detailing: EvidenceValueV1[BeamDetailingOptionsV1]
    applicability: EvidenceValueV1[BeamAuditApplicabilityBasisV1]
    serviceability_basis: EvidenceValueV1[str | BeamAuditServiceabilityV1]
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
    serviceability_basis: EvidenceValueV1[str | BeamServiceabilityChecksV1]


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
        "Only explicit bounded service inputs are evaluated; no global analysis or professional approval.",
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


class BeamAuditRowEvaluationRequestV1(StrictPublicModel):
    """Bounded compatibility entry into the canonical signed-row audit owner."""

    schema_version: Literal["beam-audit-row-evaluation-request/v1"] = (
        "beam-audit-row-evaluation-request/v1"
    )
    row: BeamAuditRowInputV1
    scenario_id: str = Field(min_length=1, max_length=160)
    context_sha256: str = Field(pattern=_SHA)
    require_serviceability: bool


class BeamAuditRowEvaluationResultV1(StrictPublicModel):
    schema_version: Literal["beam-audit-row-evaluation/v1"] = (
        "beam-audit-row-evaluation/v1"
    )
    status: W3BuildStatusV1
    verdict: Literal["PASS", "FAIL", "HELD", "BLOCKED"]
    issues: tuple[W3BuildIssueV1, ...]
    context_sha256: str = Field(pattern=_SHA)
    row: BeamAuditRowResultV1 | None
    evaluation_sha256: str = Field(pattern=_SHA)
    limitations: tuple[str, ...] = (
        "Compatibility row evaluation does not replace a complete demand-domain audit.",
        "The caller must retain the accepted baseline/catalogue identities behind the row.",
    )

    @model_validator(mode="after")
    def _complete_or_blocked(self) -> Self:
        if self.status is W3BuildStatusV1.BLOCKED:
            if not self.issues or self.row is not None or self.verdict != "BLOCKED":
                raise ValueError("blocked row evaluation exposes issues only")
        elif self.issues or self.row is None or self.verdict == "BLOCKED":
            raise ValueError("accepted row evaluation requires one complete row")
        return self


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_beam_action_row_sha256_v1(row: BeamActionRowV1, /) -> str:
    """Return the canonical digest used by retained signed beam-action rows."""

    return _sha(_json(row.model_dump(mode="json", exclude={"row_sha256"})))


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
    service_index: dict[tuple[str, str, str], BeamServiceabilityChecksV1] = {}
    for member_id, member_basis in bases.items():
        service_set = member_basis.serviceability_basis.value
        if isinstance(service_set, BeamAuditServiceabilityV1):
            expected = {
                (a.row_id, a.row_sha256) for a in actions if a.member_id == member_id
            }
            supplied = {
                (s.action_row_id, s.action_row_sha256) for s in service_set.rows
            }
            service_index.update(
                ((member_id, s.action_row_id, s.action_row_sha256), s.checks)
                for s in service_set.rows
            )
            if supplied != expected or len(supplied) != len(service_set.rows):
                issues.append(
                    _issue(
                        "BEAM_AUDIT_SERVICE_ROW_MISMATCH",
                        member_id,
                        "service evidence must bind every retained row exactly once by id and digest",
                    )
                )
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
        typed_service = isinstance(service.value, BeamAuditServiceabilityV1)
        if service.state is EvidenceStateV1.BLOCKED or (
            request.require_serviceability
            and service.state is not EvidenceStateV1.NOT_APPLICABLE
            and not typed_service
        ):
            issues.append(
                _issue(
                    "BEAM_AUDIT_REQUIRED_SERVICEABILITY_BLOCKED",
                    f"member_bases:{action.member_id}.serviceability_basis",
                    "Required serviceability needs complete typed service checks; "
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
        face: Literal["TOP", "BOTTOM", "ZERO_MOMENT"] = "ZERO_MOMENT"
        if action.m3_knm > 0:
            face = applicability.positive_m3_tension_face
        elif action.m3_knm < 0:
            face = applicability.negative_m3_tension_face
        service_checks = None
        if isinstance(service.value, BeamAuditServiceabilityV1):
            service_checks = service_index.get(
                (action.member_id, action.row_id, action.row_sha256)
            )
            if service_checks is None:
                continue  # Complete-domain issue above prevents any partial acceptance.
            if (
                service_checks.basis.station_mm != action.object_station_mm
                or service_checks.basis.tension_face != face
            ):
                issues.append(
                    _issue(
                        "BEAM_AUDIT_SERVICE_LOCATION_MISMATCH",
                        action.row_id,
                        "service evidence must match the retained station and explicit tension face; zero-moment association is unsupported",
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
                    primary_tension_face=(face if face != "ZERO_MOMENT" else None),
                ),
                calculation_basis=calculation,
                detailing=detailing,
                serviceability=service_checks,
                source_provenance=f"beam-audit:{request.accepted_snapshot.snapshot_sha256}:{action.row_sha256}",
            )
        except ValidationError as exc:
            issues.append(
                _issue("BEAM_AUDIT_CANONICAL_INPUT_BLOCKED", action.row_id, str(exc))
            )
            continue
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
                serviceability_basis=EvidenceValueV1[str | BeamServiceabilityChecksV1](
                    state=service.state,
                    value=(
                        service_checks
                        if service_checks is not None
                        else service.value if isinstance(service.value, str) else None
                    ),
                    reason_code=service.reason_code,
                    message=service.message,
                    source_references=service.source_references,
                ),
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


def _row_evaluation_result(**values: object) -> BeamAuditRowEvaluationResultV1:
    provisional = BeamAuditRowEvaluationResultV1.model_validate(
        {**values, "evaluation_sha256": "0" * 64}
    )
    payload = provisional.model_dump(mode="json", exclude={"evaluation_sha256"})
    return provisional.model_copy(update={"evaluation_sha256": _sha(_json(payload))})


def evaluate_beam_audit_row_v1(
    request: BeamAuditRowEvaluationRequestV1, /
) -> BeamAuditRowEvaluationResultV1:
    """Evaluate one exact signed action row through the canonical audit owner."""

    row = request.row
    action = row.action
    canonical = row.canonical_request
    issues: list[W3BuildIssueV1] = []
    if action.row_sha256 != canonical_beam_action_row_sha256_v1(action):
        issues.append(
            _issue(
                "BEAM_AUDIT_ACTION_ROW_IDENTITY_INVALID",
                action.row_id,
                "signed action row digest does not match its canonical fields",
            )
        )
    expected_face: Literal["TOP", "BOTTOM", "ZERO_MOMENT"] = row.tension_face
    if action.m3_knm == 0:
        expected_face = "ZERO_MOMENT"
    expected_primary = expected_face if expected_face != "ZERO_MOMENT" else None
    expected_actions = (
        abs(action.m3_knm),
        abs(action.v2_kn),
        abs(action.t_knm),
        expected_primary,
    )
    actual_actions = (
        canonical.actions.mu_knm,
        canonical.actions.vu_kn,
        canonical.actions.tu_knm,
        canonical.actions.primary_tension_face,
    )
    if expected_actions != actual_actions:
        issues.append(
            _issue(
                "BEAM_AUDIT_SAME_ROW_OR_FACE_MISMATCH",
                action.row_id,
                "canonical actions must be same-row magnitudes with the explicit physical face",
            )
        )
    if (
        canonical.identity.member_id != action.member_id
        or canonical.identity.case_id != action.selection_id
        or canonical.source_provenance is None
        or action.row_sha256 not in canonical.source_provenance
    ):
        issues.append(
            _issue(
                "BEAM_AUDIT_ROW_PROVENANCE_MISMATCH",
                action.row_id,
                "canonical member/case/source provenance must bind the exact signed row",
            )
        )
    if issues:
        return _row_evaluation_result(
            status=W3BuildStatusV1.BLOCKED,
            verdict="BLOCKED",
            issues=tuple(issues),
            context_sha256=request.context_sha256,
            row=None,
        )
    refs = (
        f"scenario:{request.scenario_id}",
        f"action:{action.row_sha256}",
        f"context:{request.context_sha256}",
    )
    try:
        result = canonical_beam.check(canonical)
        serialized = _json(result.to_dict())
    except (StructuralLibError, ValueError, ArithmeticError) as exc:
        return _row_evaluation_result(
            status=W3BuildStatusV1.BLOCKED,
            verdict="BLOCKED",
            issues=(
                _issue(
                    "BEAM_AUDIT_CALCULATION_BLOCKED",
                    action.row_id,
                    f"{type(exc).__name__}: {exc}",
                ),
            ),
            context_sha256=request.context_sha256,
            row=None,
        )
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
            outcome = EvidenceValueV1[Literal["PASS", "FAIL"]].model_validate(missing)
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
                scenario_id=request.scenario_id,
                action_row_id=action.row_id,
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
    service_checks = canonical.serviceability
    service_scenario = request.scenario_id
    if isinstance(service_checks, BeamServiceabilityChecksV1):
        assert (
            calculation.deflection is not None and calculation.crack_width is not None
        )
        service_scenario = service_checks.basis.service_case_id
        service_refs = refs + service.source_references
        outcome = EvidenceValueV1[Literal["PASS", "FAIL"]](
            state=EvidenceStateV1.PRESENT,
            value=(
                "PASS"
                if calculation.deflection.is_ok and calculation.crack_width.is_ok
                else "FAIL"
            ),
            source_references=service_refs,
        )
        utilization = EvidenceValueV1[float](
            state=EvidenceStateV1.PRESENT,
            value=max(
                calculation.utilizations["deflection"],
                calculation.utilizations["crack_width"],
            ),
            source_references=service_refs,
        )
    else:
        state = (
            service.state
            if service.state is not EvidenceStateV1.PRESENT
            else EvidenceStateV1.UNAVAILABLE
        )
        missing = _not_evaluated(
            state,
            service.reason_code or "CANONICAL_SERVICEABILITY_SCOPE_HOLD",
            service.message or "Complete typed service checks are absent.",
            refs + service.source_references,
        )
        outcome = EvidenceValueV1[Literal["PASS", "FAIL"]].model_validate(missing)
        utilization = EvidenceValueV1[float].model_validate(missing)
    checks.append(
        BeamAuditCheckV1(
            check="serviceability",
            scenario_id=service_scenario,
            action_row_id=action.row_id,
            outcome=outcome,
            utilization=utilization,
            clause_references=(
                calculation.clause_refs["deflection"],
                calculation.clause_refs["crack_width"],
            ),
        )
    )
    row_result = BeamAuditRowResultV1(
        input=row,
        checks=tuple(checks),
        canonical_result_json=serialized,
        canonical_result_sha256=_sha(serialized),
    )
    failed = any(check.outcome.value == "FAIL" for check in checks)
    service_hold = request.require_serviceability and any(
        check.outcome.state
        not in (EvidenceStateV1.PRESENT, EvidenceStateV1.NOT_APPLICABLE)
        for check in checks
        if check.check == "serviceability"
    )
    return _row_evaluation_result(
        status=W3BuildStatusV1.ACCEPTED,
        verdict="FAIL" if failed else "HELD" if service_hold else "PASS",
        issues=(),
        context_sha256=request.context_sha256,
        row=row_result,
    )


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
        service_checks = row.canonical_request.serviceability
        service_scenario = scenario_id
        if isinstance(service_checks, BeamServiceabilityChecksV1):
            assert (
                calculation.deflection is not None
                and calculation.crack_width is not None
            )
            service_scenario = service_checks.basis.service_case_id
            service_refs = (
                refs
                + service.source_references
                + (
                    f"service-source:{service_checks.basis.source_sha256}",
                    service_checks.basis.source_reference,
                    service_checks.basis.service_load_reference,
                    service_checks.basis.reinforcement_reference,
                )
            )
            outcome = EvidenceValueV1[Literal["PASS", "FAIL"]](
                state=EvidenceStateV1.PRESENT,
                value=(
                    "PASS"
                    if calculation.deflection.is_ok and calculation.crack_width.is_ok
                    else "FAIL"
                ),
                source_references=service_refs,
            )
            utilization = EvidenceValueV1[float](
                state=EvidenceStateV1.PRESENT,
                value=max(
                    calculation.utilizations["deflection"],
                    calculation.utilizations["crack_width"],
                ),
                source_references=service_refs,
            )
        else:
            state = (
                service.state
                if service.state is not EvidenceStateV1.PRESENT
                else EvidenceStateV1.UNAVAILABLE
            )
            missing = _not_evaluated(
                state,
                service.reason_code or "CANONICAL_SERVICEABILITY_SCOPE_HOLD",
                service.message
                or "Complete typed service checks are absent; supplied text retained without a pass claim.",
                refs + service.source_references,
            )
            outcome = EvidenceValueV1[Literal["PASS", "FAIL"]].model_validate(missing)
            utilization = EvidenceValueV1[float].model_validate(missing)
        checks.append(
            BeamAuditCheckV1(
                check="serviceability",
                scenario_id=service_scenario,
                action_row_id=row.action.row_id,
                outcome=outcome,
                utilization=utilization,
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
        for name in ("flexure", "shear", "torsion", "serviceability"):
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
            check.outcome.state
            not in (EvidenceStateV1.PRESENT, EvidenceStateV1.NOT_APPLICABLE)
            for row in rows
            for check in row.checks
            if check.check == "serviceability"
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
