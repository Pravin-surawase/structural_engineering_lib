"""W3E deterministic software evidence; synthetic basis, no ETABS/Excel calls."""

from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any

import pytest
from pydantic import ValidationError

import structural_lib
from structural_lib.core.analysis_contracts import EvidenceStateV1, EvidenceValueV1
from structural_lib.services import beam_audit as audit
from structural_lib.services import canonical_beam
from structural_lib.services.contracts.beam import (
    BeamCalculationBasisV1,
    BeamDetailingOptionsV1,
    DetailingStandard,
    IS456MaterialsV1,
    RectangularBeamSectionV1,
)
from structural_lib.services.contracts.etabs_w3 import (
    BeamDemandDerivationRequestV1,
    W3BuildStatusV1,
    derive_beam_demand_snapshot_v1,
)
from tests.unit.test_etabs_w3_contracts import (
    _accepted_catalogue,
    _baseline,
    _present,
    _scenario_and_rules,
)


def _absent(state: EvidenceStateV1) -> EvidenceValueV1[Any]:
    return EvidenceValueV1(
        state=state,
        value=None,
        reason_code="SYNTHETIC_EXPLICIT_HOLD",
        message="Synthetic caller basis is explicitly absent.",
        source_references=("synthetic:owner-basis",),
    )


def _request() -> audit.BeamAuditInputBuildRequestV1:
    baseline, catalogue = _baseline(), _accepted_catalogue()
    scenario, rules = _scenario_and_rules(catalogue, baseline)
    demand = BeamDemandDerivationRequestV1(
        baseline=baseline, catalogue=catalogue, scenario=scenario, envelope_rules=rules
    )
    snapshot = derive_beam_demand_snapshot_v1(demand).snapshot
    assert snapshot is not None
    detailing = BeamDetailingOptionsV1(
        standard=DetailingStandard.IS456,
        clear_cover_mm=40.0,
        tension_bar_diameter_mm=20.0,
        compression_bar_diameter_mm=16.0,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=8.0,
        stirrup_legs=2,
        stirrup_spacing_support_mm=150.0,
        stirrup_spacing_mid_mm=200.0,
    )
    basis = audit.BeamAuditMemberBasisV1(
        member_id="member:1",
        section=_present(
            RectangularBeamSectionV1(b_mm=300.0, D_mm=500.0, d_mm=442.0, span_mm=3000.0)
        ),
        materials=_present(IS456MaterialsV1(fck_nmm2=25.0, fy_nmm2=500.0)),
        calculation_basis=_present(
            BeamCalculationBasisV1(
                d_dash_mm=56.0, asv_mm2=detailing.asv_mm2, pt_percent=1.0
            )
        ),
        detailing=_present(detailing),
        applicability=_present(
            audit.BeamAuditApplicabilityBasisV1(
                scope="RECTANGULAR_MAJOR_AXIS_STRENGTH",
                factored_action_basis="Synthetic factored fixture, not an engineering criterion.",
                max_abs_axial_kn=2.0,
                max_abs_minor_shear_kn=3.0,
                max_abs_minor_moment_knm=5.0,
                positive_m3_tension_face="BOTTOM",
                negative_m3_tension_face="TOP",
            )
        ),
        serviceability_basis=_absent(EvidenceStateV1.NOT_REQUESTED),
        assumptions=("Synthetic excluded-component limits are not recommendations.",),
    )
    return audit.BeamAuditInputBuildRequestV1(
        demand=demand,
        accepted_snapshot=snapshot,
        member_bases=(basis,),
        require_serviceability=False,
        max_action_rows=3,
    )


def _evaluate(
    request: audit.BeamAuditInputBuildRequestV1,
) -> audit.BeamAuditEvaluationResultV1:
    built = audit.build_beam_audit_inputs_v1(request)
    assert built.inputs is not None, built.issues
    return audit.evaluate_beam_audit_v1(
        audit.BeamAuditEvaluationRequestV1(inputs=built.inputs)
    )


def test_every_signed_row_matches_canonical_owner_and_governor_provenance() -> None:
    result = _evaluate(_request())
    assert result.status is W3BuildStatusV1.ACCEPTED
    assert len(result.rows) == 3
    assert [row.input.action.m3_knm for row in result.rows] == [100.0, 50.0, -100.0]
    assert [row.input.tension_face for row in result.rows] == [
        "BOTTOM",
        "BOTTOM",
        "TOP",
    ]
    assert result.rows[0].input.canonical_request.actions.vu_kn == 20.0
    assert result.rows[1].input.canonical_request.actions.mu_knm == 50.0
    for row in result.rows:
        expected = canonical_beam.check(row.input.canonical_request).to_dict()
        assert json.loads(row.canonical_result_json) == expected
        assert (
            hashlib.sha256(row.canonical_result_json.encode()).hexdigest()
            == row.canonical_result_sha256
        )
        assert len(row.checks) == 4
        for check in row.checks:
            assert check.action_row_id == row.input.action.row_id
            assert check.scenario_id == "scenario:strength"
            assert check.clause_references and check.outcome.source_references
    assert {check.check for check in result.governing_checks} == {
        "flexure",
        "shear",
        "torsion",
    }
    assert all(
        check.action_row_id in {row.input.action.row_id for row in result.rows}
        for check in result.governing_checks
    )
    assert (
        audit.BeamAuditEvaluationResultV1.model_validate_json(
            result.model_dump_json(), strict=False
        )
        == result
    )
    assert _evaluate(_request()) == result


@pytest.mark.parametrize(
    "field", ["section", "materials", "calculation_basis", "detailing", "applicability"]
)
@pytest.mark.parametrize(
    "state",
    [
        EvidenceStateV1.UNAVAILABLE,
        EvidenceStateV1.NOT_REQUESTED,
        EvidenceStateV1.NOT_APPLICABLE,
        EvidenceStateV1.BLOCKED,
    ],
)
def test_missing_design_basis_blocks_without_defaults(
    field: str, state: EvidenceStateV1
) -> None:
    request = _request()
    basis = request.member_bases[0].model_copy(update={field: _absent(state)})
    built = audit.build_beam_audit_inputs_v1(
        request.model_copy(update={"member_bases": (basis,)})
    )
    assert built.status is W3BuildStatusV1.BLOCKED and built.inputs is None
    assert "BEAM_AUDIT_REQUIRED_BASIS_HELD" in {issue.code for issue in built.issues}


@pytest.mark.parametrize("state", list(EvidenceStateV1))
def test_serviceability_five_states_retained_and_never_faked(
    state: EvidenceStateV1,
) -> None:
    request = _request()
    service = (
        _present("Explicit service criteria awaiting strict canonical support.")
        if state is EvidenceStateV1.PRESENT
        else _absent(state)
    )
    basis = request.member_bases[0].model_copy(update={"serviceability_basis": service})
    required = request.model_copy(
        update={"member_bases": (basis,), "require_serviceability": True}
    )
    built = audit.build_beam_audit_inputs_v1(required)
    if state is not EvidenceStateV1.NOT_APPLICABLE:
        assert built.status is W3BuildStatusV1.BLOCKED and built.inputs is None
        assert all(
            issue.code == "BEAM_AUDIT_REQUIRED_SERVICEABILITY_BLOCKED"
            for issue in built.issues
        )
    else:
        assert built.status is W3BuildStatusV1.ACCEPTED
    optional = required.model_copy(update={"require_serviceability": False})
    if state is EvidenceStateV1.BLOCKED:
        blocked = audit.build_beam_audit_inputs_v1(optional)
        assert blocked.status is W3BuildStatusV1.BLOCKED and blocked.inputs is None
        return
    result = _evaluate(optional)
    for row in result.rows:
        check = next(item for item in row.checks if item.check == "serviceability")
        assert check.outcome.value is None
        assert check.outcome.state is (
            EvidenceStateV1.UNAVAILABLE if state is EvidenceStateV1.PRESENT else state
        )
        assert row.input.serviceability_basis == service


def test_hash_geometry_capacity_member_and_applicability_guards() -> None:
    request = _request()
    basis = request.member_bases[0]
    assert basis.section.value is not None and basis.applicability.value is not None
    variants = (
        request.model_copy(
            update={
                "accepted_snapshot": request.accepted_snapshot.model_copy(
                    update={"member_count": 2}
                )
            }
        ),
        request.model_copy(update={"max_action_rows": 2}),
        request.model_copy(update={"member_bases": (basis, basis)}),
        request.model_copy(
            update={
                "member_bases": (
                    basis.model_copy(
                        update={
                            "section": _present(
                                basis.section.value.model_copy(update={"b_mm": 400.0})
                            )
                        }
                    ),
                )
            }
        ),
        request.model_copy(
            update={
                "member_bases": (
                    basis.model_copy(
                        update={
                            "applicability": _present(
                                basis.applicability.value.model_copy(
                                    update={"max_abs_axial_kn": 0.0}
                                )
                            )
                        }
                    ),
                )
            }
        ),
    )
    for variant in variants:
        built = audit.build_beam_audit_inputs_v1(variant)
        assert built.status is W3BuildStatusV1.BLOCKED and built.inputs is None
    built = audit.build_beam_audit_inputs_v1(request)
    assert built.inputs is not None
    changed = built.inputs.rows[0].model_copy(update={"tension_face": "TOP"})
    tampered = built.inputs.model_copy(
        update={"rows": (changed,) + built.inputs.rows[1:]}
    )
    result = audit.evaluate_beam_audit_v1(
        audit.BeamAuditEvaluationRequestV1(inputs=tampered)
    )
    assert result.verdict == "BLOCKED" and not result.rows


def test_canonical_failure_has_no_partial_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(_: object) -> object:
        raise ValueError("synthetic main-process failure")

    monkeypatch.setattr(canonical_beam, "check", fail)
    result = _evaluate(_request())
    assert result.status is W3BuildStatusV1.BLOCKED and not result.rows
    assert len(result.issues) == 3
    assert all(
        issue.code == "BEAM_AUDIT_CALCULATION_BLOCKED" for issue in result.issues
    )


def test_exact_public_signatures_strictness_and_hash_basis() -> None:
    for name in ("build_beam_audit_inputs_v1", "evaluate_beam_audit_v1"):
        function = getattr(structural_lib, name)
        assert function is getattr(audit, name)
        parameter = next(iter(inspect.signature(function).parameters.values()))
        assert parameter.kind is inspect.Parameter.POSITIONAL_ONLY
    request = _request()
    with pytest.raises(ValidationError):
        audit.BeamAuditInputBuildRequestV1.model_validate(
            {**request.model_dump(), "unknown": 1}
        )
    result = _evaluate(request)
    payload = result.model_dump(mode="json", exclude={"evaluation_sha256"})
    assert (
        hashlib.sha256(
            json.dumps(
                payload, sort_keys=True, separators=(",", ":"), allow_nan=False
            ).encode()
        ).hexdigest()
        == result.evaluation_sha256
    )
