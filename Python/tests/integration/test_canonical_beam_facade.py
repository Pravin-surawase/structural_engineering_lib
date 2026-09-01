"""LIB-PRO-013 B0 canonical beam contract and consumer evidence."""

from __future__ import annotations

import json
import math

import pytest

from structural_lib.__main__ import main as cli_main
from structural_lib.core.errors import CalculationError, InputContractError
from structural_lib.design.is456 import beam
from structural_lib.services.api import (
    compute_bbs,
    compute_report,
    design_beam_is456,
    export_bbs,
)


def _detailing() -> beam.BeamDetailingOptionsV1:
    return beam.BeamDetailingOptionsV1(
        standard=beam.DetailingStandard.IS456,
        clear_cover_mm=40,
        tension_bar_diameter_mm=20,
        compression_bar_diameter_mm=16,
        nominal_top_steel_ratio=0.25,
        stirrup_diameter_mm=8,
        stirrup_legs=2,
        stirrup_spacing_support_mm=150,
        stirrup_spacing_mid_mm=200,
    )


def _request(*, with_detailing: bool = False) -> beam.BeamDesignInputV1:
    detailing = _detailing() if with_detailing else None
    return beam.input(
        member_id="B1",
        story="GF",
        case_id="ULS-1",
        span_mm=5000,
        b_mm=300,
        D_mm=550,
        d_mm=500,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=150,
        vu_kn=80,
        d_dash_mm=50,
        asv_mm2=detailing.asv_mm2 if detailing is not None else 100,
        detailing=detailing,
    )


@pytest.mark.parametrize(
    ("path", "value", "code"),
    [
        ("actions.mu_knm", "150", "INPUT_TYPE_INVALID"),
        ("actions.vu_kn", True, "INPUT_TYPE_INVALID"),
        ("actions.mu_knm", math.inf, "INPUT_NOT_FINITE"),
        ("actions.mu_knm", -1, "INPUT_OUT_OF_RANGE"),
        ("identity.member_id", "", "IDENTITY_INVALID"),
    ],
)
def test_strict_nested_request_raises_only_library_input_errors(path, value, code):
    payload = _request().model_dump(mode="python")
    owner, field = path.split(".")
    payload[owner][field] = value

    with pytest.raises(InputContractError) as exc_info:
        beam.load(payload)

    assert exc_info.value.issues[0].path == path
    assert exc_info.value.issues[0].code == code


def test_extra_fields_and_invalid_enum_do_not_expose_pydantic_errors():
    payload = _request(with_detailing=True).model_dump(mode="python")
    payload["unexpected"] = 1
    payload["detailing"]["standard"] = "DEFAULT"

    with pytest.raises(InputContractError) as exc_info:
        beam.load(payload)

    assert {issue.code for issue in exc_info.value.issues} == {
        "ENUM_VALUE_INVALID",
        "EXTRA_FIELD_FORBIDDEN",
    }


def test_advertised_beam_fields_have_machine_readable_validation_dimensions():
    contracts = {item.path: item for item in beam.BEAM_FIELD_CONTRACTS}

    assert "identity.member_id" in contracts
    assert "actions.mu_knm" in contracts
    assert "detailing.stirrup_spacing_support_mm" in contracts
    assert "detailing.side_face_bar_diameter_mm" in contracts
    assert (
        "side_face_bar_diameter_mm"
        not in _request(with_detailing=True).model_dump()["detailing"]
    )
    assert all(item.dimensions for item in contracts.values())
    assert len(contracts) == len(beam.BEAM_FIELD_CONTRACTS)


def test_canonical_and_compatibility_strength_results_are_numerically_identical():
    canonical = beam.design(_request())
    compatibility = design_beam_is456(
        units="IS456",
        case_id="ULS-1",
        mu_knm=150,
        vu_kn=80,
        b_mm=300,
        D_mm=550,
        d_mm=500,
        fck_nmm2=25,
        fy_nmm2=500,
        d_dash_mm=50,
        asv_mm2=100,
    )

    assert canonical.calculation.flexure.Ast_required == pytest.approx(
        compatibility.flexure.Ast_required
    )
    assert canonical.calculation.shear.spacing == pytest.approx(
        compatibility.shear.spacing
    )
    assert canonical.engineering_status.value == "PASS"
    assert canonical.to_dict()["envelope"]["overall_status"] == "PASS"


def test_explicit_detailing_and_combined_result_have_identical_bbs_accounting():
    request = _request(with_detailing=True)
    combined = beam.design_and_detail(
        request, detailing_standard=beam.DetailingStandard.IS456
    )

    from_combined = beam.bbs(combined)
    from_detailing = beam.bbs(combined.detailing)

    assert len(from_combined.items) == 9
    assert from_combined.items == from_detailing.items
    assert from_combined.summary == from_detailing.summary
    assert from_combined.total_weight_kg > 0


def test_bbs_rejects_unaccepted_result_type_before_generating_items():
    design_result = beam.design(_request())

    with pytest.raises(InputContractError) as exc_info:
        beam.bbs(design_result)  # type: ignore[arg-type]

    assert exc_info.value.issues[0].code == "CONSUMER_TYPE_INVALID"


def test_engineering_fail_remains_a_result_and_cannot_generate_bbs():
    detailing = _detailing()
    request = beam.input(
        member_id="B-FAIL",
        story="GF",
        case_id="ULS-FAIL",
        span_mm=5000,
        b_mm=300,
        D_mm=550,
        d_mm=500,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=2000,
        vu_kn=80,
        d_dash_mm=50,
        asv_mm2=detailing.asv_mm2,
        detailing=detailing,
    )
    result = beam.design_and_detail(
        request, detailing_standard=beam.DetailingStandard.IS456
    )

    assert result.engineering_status.value == "FAIL"
    with pytest.raises(InputContractError) as exc_info:
        beam.bbs(result)
    assert exc_info.value.issues[0].code == "CONSUMER_RESULT_NOT_ACCEPTED"


def test_unsupported_serviceability_is_a_distinct_hold_issue():
    payload = _request().model_dump(mode="python")
    payload["serviceability"] = {
        "deflection_params": {"span_mm": 5000},
        "crack_width_params": None,
    }

    with pytest.raises(InputContractError) as exc_info:
        beam.load(payload)

    assert exc_info.value.issues[0].path == "serviceability"
    assert exc_info.value.issues[0].code == "SERVICEABILITY_SCOPE_HOLD"


def test_internal_calculation_errors_are_not_converted_to_intake_or_pass(
    monkeypatch,
):
    import structural_lib.services.beam_api as beam_api

    def fail_calculation(**_):
        raise CalculationError("controlled internal failure")

    monkeypatch.setattr(beam_api, "_design_beam_is456_calculation", fail_calculation)
    with pytest.raises(CalculationError, match="controlled internal failure"):
        beam.design(_request())


def test_detailing_requires_explicit_options_and_matching_standard():
    design_result = beam.design(_request())
    with pytest.raises(InputContractError) as exc_info:
        beam.detail(design_result, detailing_standard=beam.DetailingStandard.IS456)
    assert exc_info.value.issues[0].path == "request.detailing"

    request = _request(with_detailing=True)
    with pytest.raises(InputContractError) as conflict:
        beam.design_and_detail(
            request, detailing_standard=beam.DetailingStandard.IS13920
        )
    assert conflict.value.issues[0].code == "DETAILING_STANDARD_CONFLICT"


def test_cross_field_design_and_detailing_choices_must_reconcile():
    payload = _request(with_detailing=True).model_dump(mode="python")
    payload["calculation_basis"]["asv_mm2"] = 100

    with pytest.raises(InputContractError) as stirrup_conflict:
        beam.load(payload)
    assert stirrup_conflict.value.issues[0].path == "detailing"
    assert stirrup_conflict.value.issues[0].code == "CROSS_FIELD_CONTRACT_INVALID"

    payload = _request(with_detailing=True).model_dump(mode="python")
    payload["section"]["d_mm"] = None
    payload["section"]["effective_depth_basis"] = {
        "clear_cover_mm": 35,
        "stirrup_diameter_mm": 8,
        "tension_bar_diameter_mm": 20,
    }
    with pytest.raises(InputContractError) as depth_conflict:
        beam.load(payload)
    assert depth_conflict.value.issues[0].path == "detailing"
    assert depth_conflict.value.issues[0].code == "CROSS_FIELD_CONTRACT_INVALID"


def test_canonical_cli_preserves_result_and_problem_contracts(tmp_path, capsys):
    request_path = tmp_path / "beam.json"
    request_path.write_text(
        json.dumps(_request(with_detailing=True).model_dump(mode="json")),
        encoding="utf-8",
    )

    assert cli_main(["beam-v1", str(request_path), "--mode", "bbs"]) == 0
    accepted = json.loads(capsys.readouterr().out)
    assert accepted["schema_version"] == "beam-bbs-result/v1"
    assert accepted["summary"]["total_items"] == 9

    invalid = _request().model_dump(mode="json")
    invalid["actions"]["mu_knm"] = "150"
    request_path.write_text(json.dumps(invalid), encoding="utf-8")
    assert cli_main(["beam-v1", str(request_path)]) == 2
    problem = json.loads(capsys.readouterr().err)
    assert problem["schema_version"] == "structural-problem/v1"
    assert problem["details"]["issues"][0]["path"] == "actions.mu_knm"


def test_report_and_export_adapters_accept_named_canonical_results(tmp_path):
    request = _request(with_detailing=True)
    combined = beam.design_and_detail(
        request, detailing_standard=beam.DetailingStandard.IS456
    )
    canonical_bbs = beam.bbs(combined)

    compatibility_document = compute_bbs(combined)
    assert compatibility_document.items == list(canonical_bbs.items)
    assert (
        compatibility_document.summary.total_weight_kg
        == canonical_bbs.summary.total_weight_kg
    )
    assert compatibility_document.summary.total_bars == canonical_bbs.summary.total_bars

    report_payload = json.loads(compute_report(combined, format="json"))
    assert report_payload["schema_version"] == "beam-design-and-detail-result/v1"
    assert report_payload["envelope"]["overall_status"] == "PASS"

    export_path = tmp_path / "canonical-bbs.json"
    assert export_bbs(canonical_bbs, export_path, fmt="json") == export_path
    exported = json.loads(export_path.read_text(encoding="utf-8"))
    assert exported["schema_version"] == "beam-bbs-result/v1"
    assert exported["summary"]["total_items"] == 9

    with pytest.raises(InputContractError):
        compute_report(combined, format="html")
    with pytest.raises(InputContractError):
        export_bbs(canonical_bbs, tmp_path / "bad.bin", fmt="binary")
    with pytest.raises(InputContractError):
        export_bbs(canonical_bbs, tmp_path / "bad.json", fmt="binary")


def test_compatibility_bbs_rejects_empty_and_mixed_consumer_inputs():
    with pytest.raises(InputContractError) as empty:
        compute_bbs([])
    assert empty.value.issues[0].code == "COLLECTION_EMPTY"

    with pytest.raises(InputContractError) as mixed:
        compute_bbs([object()])
    assert mixed.value.issues[0].code == "CONSUMER_TYPE_INVALID"
