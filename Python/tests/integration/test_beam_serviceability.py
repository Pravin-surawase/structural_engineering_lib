"""Independent bounded service benchmarks and real canonical/W3 consumers."""

import copy
import json

import pytest
from pydantic import ValidationError

from structural_lib.codes.is456.beam.serviceability import check_crack_width
from structural_lib.core.analysis_contracts import EvidenceStateV1
from structural_lib.core.errors import InputContractError
from structural_lib.design.is456 import beam
from structural_lib.services import beam_audit as audit
from structural_lib.services.contracts.etabs_w3 import W3BuildStatusV1
from tests.integration.test_canonical_beam_facade import _request
from tests.unit.test_beam_audit import _evaluate
from tests.unit.test_beam_audit import _request as audit_request
from tests.unit.test_etabs_w3_contracts import _present


def service_payload():
    return {
        "schema_version": "beam-serviceability-checks/v1",
        "basis": {
            "member_id": "B1",
            "service_case_id": "SLS-1",
            "station_mm": 1500.0,
            "tension_face": "BOTTOM",
            "b_mm": 300.0,
            "h_mm": 550.0,
            "d_mm": 500.0,
            "reinforcement_reference": "synthetic:bars-r1",
            "service_load_reference": "synthetic:unfactored-service-analysis",
            "source_reference": "synthetic:strain-and-factor-calculation",
            "source_sha256": "a" * 64,
        },
        "deflection": {
            "method": "IS456_SPAN_DEPTH",
            "effective_span_mm": 5000.0,
            "support_condition": "SIMPLY_SUPPORTED",
            "mf_tension_steel": 1.2,
            "mf_compression_steel": 1.1,
            "span_support_reference": "synthetic:effective-span-support",
            "modification_factors_reference": "synthetic:figures-4-5",
        },
        "crack_width": {
            "method": "IS456_ANNEX_F_TENSION_SURFACE",
            "exposure_class": "MODERATE",
            "cracking_harmful": True,
            "limit_mm": 0.2,
            "limit_reference": "synthetic:weather-exposure-criterion",
            "acr_mm": 60.0,
            "cmin_mm": 40.0,
            "x_mm": 150.0,
            "epsilon_m": 0.001,
            "fs_service_nmm2": 200.0,
            "es_nmm2": 200000.0,
            "strain_geometry_reference": "synthetic:service-section-analysis",
        },
    }


def canonical_payload():
    data = _request().model_dump(mode="json")
    data["serviceability"] = service_payload()
    return data


def test_independent_annex_f_and_span_depth_benchmarks():
    result = beam.check(beam.load(canonical_payload()))
    assert result.is_ok
    assert result.calculation.deflection.computed["allowable_ld"] == pytest.approx(26.4)
    assert result.calculation.deflection.computed["ld_ratio"] == 10.0
    # Independent hand vector: 0.180 / 1.100 = 0.163636... mm.
    assert result.calculation.crack_width.computed["wcr_mm"] == pytest.approx(
        0.16363636363636364
    )
    assert result.calculation.crack_width.assumptions == []
    assert not any("Assumed" in a for a in result.calculation.deflection.assumptions)
    assert (
        result.envelope.result_identity.calculation_identity
        == "is456-rectangular-beam-serviceability/v1"
    )
    assert result.request.serviceability.basis.service_case_id == "SLS-1"
    assert "ETABS-W3E-SERVICEABILITY-CLAUSES-23-35-ANNEX-F" in json.dumps(
        result.to_dict()
    )
    assert (
        beam.check(beam.load(result.request.model_dump(mode="json"))).to_dict()
        == result.to_dict()
    )


@pytest.mark.parametrize("check", ["deflection", "crack_width"])
def test_service_failure_changes_canonical_verdict(check):
    payload = canonical_payload()
    service = payload["serviceability"]
    if check == "deflection":
        service[check].update(
            effective_span_mm=10000.0, mf_tension_steel=0.5, mf_compression_steel=1.0
        )
    else:
        service[check]["limit_mm"] = 0.1
    result = beam.check(beam.load(payload))
    assert not result.is_ok
    assert check in result.calculation.failed_checks
    assert result.calculation.utilizations[check] > 1


@pytest.mark.parametrize(
    "group,field,value",
    [
        ("basis", "member_id", "other"),
        ("basis", "service_case_id", "ULS-1"),
        ("basis", "station_mm", 6000.0),
        ("basis", "h_mm", 600.0),
        ("basis", "d_mm", 450.0),
        ("basis", "source_sha256", "unknown"),
        ("basis", "reinforcement_reference", ""),
        ("deflection", "support_condition", "unknown"),
        ("deflection", "effective_span_mm", 10000.01),
        ("deflection", "method", "LEVEL_C"),
        ("deflection", "mf_tension_steel", 2.1),
        ("deflection", "mf_compression_steel", 1.6),
        ("crack_width", "epsilon_m", -0.001),
        ("crack_width", "epsilon_m", 0.002),
        ("crack_width", "fs_service_nmm2", 400.01),
        ("crack_width", "cmin_mm", 60.0),
        ("crack_width", "x_mm", 500.0),
        ("crack_width", "acr_mm", 30.0),
        ("crack_width", "limit_mm", 0.3),
        ("crack_width", "es_nmm2", 0.0),
        ("crack_width", "epsilon_m", float("nan")),
        ("crack_width", "epsilon_m", True),
        ("crack_width", "epsilon_m", "0.001"),
    ],
)
def test_invalid_or_untraceable_service_basis_is_rejected(group, field, value):
    payload = canonical_payload()
    payload["serviceability"][group][field] = value
    with pytest.raises(InputContractError):
        beam.load(payload)


@pytest.mark.parametrize("group", ["basis", "deflection", "crack_width"])
def test_no_partial_serviceability_pass(group):
    payload = canonical_payload()
    del payload["serviceability"][group]
    with pytest.raises(InputContractError):
        beam.load(payload)


@pytest.mark.parametrize("exposure", ["VERY_SEVERE", "EXTREME"])
def test_amendment_four_limit_and_reinforcement_strain_boundary(exposure):
    payload = canonical_payload()
    crack = payload["serviceability"]["crack_width"]
    crack.update(exposure_class=exposure)
    with pytest.raises(InputContractError):
        beam.load(payload)
    crack.update(limit_mm=0.1, fs_service_nmm2=400.0, epsilon_m=0.0021)
    result = beam.check(beam.load(payload))
    # Surface mean strain can exceed 0.8 fy/Es; the prerequisite applies to steel.
    assert not result.is_ok
    assert result.calculation.crack_width.exposure_class.name == exposure


def test_service_results_do_not_use_factored_mu_and_provenance_changes_identity():
    payload = canonical_payload()
    first = beam.check(beam.load(payload))
    payload["actions"]["mu_knm"] = 75.0
    second = beam.check(beam.load(payload))
    assert second.calculation.crack_width == first.calculation.crack_width
    payload["serviceability"]["basis"]["source_sha256"] = "b" * 64
    third = beam.check(beam.load(payload))
    assert (
        third.envelope.result_identity.input_hash
        != second.envelope.result_identity.input_hash
    )


@pytest.mark.parametrize("exposure", ["VERY_SEVERE", "EXTREME"])
def test_shared_owner_aggressive_default_is_not_an_obsolete_pass(exposure):
    result = check_crack_width(
        exposure_class=exposure,
        acr_mm=60.0,
        cmin_mm=40.0,
        h_mm=550.0,
        x_mm=150.0,
        epsilon_m=0.001,
    )
    assert result.computed["limit_mm"] == 0.1
    assert not result.is_ok
    assert result.exposure_class.name == exposure


def typed_audit_request():
    request = audit_request()
    built = audit.build_beam_audit_inputs_v1(request)
    rows = []
    for row in built.inputs.rows:
        payload = service_payload()
        payload["basis"].update(
            member_id=row.action.member_id,
            h_mm=500.0,
            d_mm=442.0,
            station_mm=row.action.object_station_mm,
            tension_face=row.tension_face,
        )
        payload["deflection"]["effective_span_mm"] = 3000.0
        rows.append(
            audit.BeamAuditServiceabilityRowV1(
                action_row_id=row.action.row_id,
                action_row_sha256=row.action.row_sha256,
                checks=beam.BeamServiceabilityChecksV1.model_validate(payload),
            )
        )
    basis = request.member_bases[0].model_copy(
        update={
            "serviceability_basis": _present(
                audit.BeamAuditServiceabilityV1(rows=tuple(rows))
            )
        }
    )
    return request.model_copy(
        update={"member_bases": (basis,), "require_serviceability": True}
    )


def test_w3_complete_service_checks_govern_and_replay():
    request = typed_audit_request()
    result = _evaluate(request)
    assert result.verdict == "PASS"
    assert "serviceability" in {c.check for c in result.governing_checks}
    for row in result.rows:
        check = row.checks[-1]
        assert (
            check.outcome.state is EvidenceStateV1.PRESENT
            and check.outcome.value == "PASS"
        )
        assert check.scenario_id == "SLS-1"
        assert (
            row.input.canonical_request.serviceability.basis.source_sha256 == "a" * 64
        )
    assert (
        audit.BeamAuditEvaluationResultV1.model_validate_json(
            result.model_dump_json(), strict=False
        )
        == result
    )
    assert _evaluate(request) == result
    data = request.model_dump(mode="json")
    data["member_bases"][0]["serviceability_basis"]["value"]["rows"][1]["checks"][
        "crack_width"
    ]["limit_mm"] = 0.1
    failed = _evaluate(
        audit.BeamAuditInputBuildRequestV1.model_validate_json(
            json.dumps(data), strict=False
        )
    )
    assert failed.verdict == "FAIL"
    governor = next(c for c in failed.governing_checks if c.check == "serviceability")
    assert governor.action_row_id == result.rows[1].input.action.row_id
    assert governor.outcome.value == "FAIL"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "extra",
        "duplicate",
        "digest",
        "station",
        "face",
        "member",
        "geometry",
    ],
)
def test_w3_service_domain_and_binding_mismatch_blocks_all(mutation):
    data = typed_audit_request().model_dump(mode="json")
    rows = data["member_bases"][0]["serviceability_basis"]["value"]["rows"]
    if mutation == "missing":
        rows.pop()
    elif mutation in ("extra", "duplicate"):
        rows.append(copy.deepcopy(rows[0]))
        if mutation == "extra":
            rows[-1]["action_row_id"] = "other"
    elif mutation == "digest":
        rows[0]["action_row_sha256"] = "b" * 64
    else:
        field, value = {
            "station": ("station_mm", 777.0),
            "face": ("tension_face", "TOP"),
            "member": ("member_id", "other"),
            "geometry": ("d_mm", 430.0),
        }[mutation]
        rows[0]["checks"]["basis"][field] = value
    request = audit.BeamAuditInputBuildRequestV1.model_validate_json(
        json.dumps(data), strict=False
    )
    built = audit.build_beam_audit_inputs_v1(request)
    assert built.status is W3BuildStatusV1.BLOCKED and built.inputs is None


def test_invalid_nested_service_type_is_not_accepted_as_legacy_text():
    data = typed_audit_request().model_dump(mode="json")
    data["member_bases"][0]["serviceability_basis"]["value"]["rows"][0]["checks"][
        "crack_width"
    ].pop("epsilon_m")
    with pytest.raises(ValidationError):
        audit.BeamAuditInputBuildRequestV1.model_validate_json(
            json.dumps(data), strict=False
        )
