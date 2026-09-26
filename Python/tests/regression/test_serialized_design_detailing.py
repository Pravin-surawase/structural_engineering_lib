"""A saved design must retain its strength basis through schedules and exports."""

import json
import math
from copy import deepcopy

import pytest

from structural_lib import __main__ as cli
from structural_lib import api
from structural_lib.core.errors import InputContractError
from structural_lib.services.beam_pipeline import design_single_beam


def _design(**overrides):
    return api.design_beam_is456(
        **{
            "units": "IS456",
            "case_id": "ULS-2",
            "mu_knm": 100,
            "vu_kn": 200,
            "b_mm": 300,
            "D_mm": 500,
            "d_mm": 444,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
            **overrides,
        }
    )


def _document(**overrides):
    result = _design(**overrides)
    return api.build_detailing_input(
        result, beam_id="B1", d_mm=result.design_inputs["d_mm"]
    )


def _codes(error):
    return {issue.code for issue in error.value.issues}


def test_round_trip_high_shear_design_uses_calculated_spacing_and_exports(tmp_path):
    document = json.loads(json.dumps(_document()))
    row = document["beams"][0]
    assert row["loads"]["case_id"] == "ULS-2"
    assert row["design_inputs"]["asv_mm2"] == 100
    assert row["result_envelope"]["engineering_status"] == "PASS"
    assert row["shear"]["spacing"] == 100

    details = api.compute_detailing(document)
    assert [s.spacing for s in details[0].stirrups] == [100, 100, 100]
    assert all(2 * math.pi * s.diameter**2 / 4 >= 100 for s in details[0].stirrups)
    schedule = api.compute_bbs(details)
    assert len(schedule.items) == 9
    low_shear = api.compute_bbs(api.compute_detailing(_document(vu_kn=80)))
    assert schedule.summary.total_weight_kg > low_shear.summary.total_weight_kg
    destination = api.export_bbs(schedule, tmp_path / "schedule.json", fmt="json")
    saved = json.loads(destination.read_text(encoding="utf-8"))
    assert len(saved["items"]) == 9
    assert saved["summary"]["total_weight_kg"] == schedule.summary.total_weight_kg


def test_adapter_copies_source_inputs_and_envelope():
    result = _design()
    document = api.build_detailing_input(result, d_mm=444)
    document["beams"][0]["design_inputs"]["asv_mm2"] = 1
    document["beams"][0]["result_envelope"]["result_identity"]["input_hash"] = "changed"
    assert result.design_inputs["asv_mm2"] == 100
    assert result.result_envelope["result_identity"]["input_hash"] != "changed"


@pytest.mark.parametrize("vu_kn", [300, 500])
def test_failed_shear_remains_reportable_but_cannot_generate_detailing(vu_kn):
    document = _document(vu_kn=vu_kn)
    assert not document["beams"][0]["is_ok"]
    assert api.compute_report(document, format="json")
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(document)
    assert _codes(error) == {"CONSUMER_RESULT_NOT_ACCEPTED"}


def test_failed_combined_design_cannot_generate_bbs():
    result = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="B1",
        story="GF",
        span_mm=4000,
        mu_knm=100,
        vu_kn=500,
        b_mm=300,
        D_mm=500,
        d_mm=444,
    )
    assert not result.is_ok and result.detailing.is_valid
    with pytest.raises(InputContractError) as error:
        api.compute_bbs(result)
    assert _codes(error) == {"CONSUMER_RESULT_NOT_ACCEPTED"}


def test_explicit_spacing_is_rejected_instead_of_silently_reduced():
    document = _document()
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(document, config={"stirrup_spacing_mid_mm": 200})
    assert _codes(error) == {"DETAILING_SHEAR_SPACING_EXCEEDED"}
    assert document["beams"][0]["shear"]["spacing"] == 100


def test_serialized_depth_cannot_change_the_original_strength_basis():
    document = _document()
    document["beams"][0]["geometry"]["d_mm"] = 460
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(document)
    assert _codes(error) == {"DETAILING_DESIGN_BASIS_MISMATCH"}


def test_adapter_rejects_changed_material_before_downstream_consumption():
    with pytest.raises(InputContractError) as error:
        api.build_detailing_input(_design(), d_mm=444, fck_nmm2=30)
    assert _codes(error) == {"DETAILING_DESIGN_BASIS_MISMATCH"}


def test_generated_depth_must_match_even_when_design_itself_passes():
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(_document(d_mm=460, vu_kn=80))
    assert _codes(error) == {"DETAILING_EFFECTIVE_DEPTH_MISMATCH"}


def test_smaller_links_cannot_replace_assumed_shear_area():
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(
            _document(d_mm=446),
            config={"stirrup_dia_mm": 6, "stirrup_spacing_mm": 75},
        )
    assert _codes(error) == {"DETAILING_SHEAR_AREA_MISMATCH"}


def test_legacy_design_without_original_inputs_requires_regeneration():
    document = _document()
    document["beams"][0].pop("design_inputs")
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(document)
    assert _codes(error) == {"DETAILING_DESIGN_BASIS_MISSING"}


def test_pipeline_serialization_carries_basis_for_later_detailing():
    result = design_single_beam(
        units="IS456",
        beam_id="B1",
        story="GF",
        span_mm=4000,
        mu_knm=100,
        vu_kn=200,
        b_mm=300,
        D_mm=500,
        d_mm=444,
        cover_mm=40,
        fck_nmm2=25,
        fy_nmm2=500,
        include_detailing=False,
    )
    document = json.loads(json.dumps({"beams": [result.to_dict()]}))
    details = api.compute_detailing(document)
    assert [s.spacing for s in details[0].stirrups] == [100, 100, 100]


def test_unmodified_span_depth_screen_retains_complete_workflow():
    params = {"span_mm": 4000, "d_mm": 444, "support_condition": "SIMPLY_SUPPORTED"}
    document = _document(deflection_params=params)
    assert api.compute_bbs(api.compute_detailing(document)).items


def test_span_depth_screen_cannot_certify_a_changed_drafting_span():
    document = _document(
        deflection_params={
            "span_mm": 4000,
            "d_mm": 444,
            "support_condition": "SIMPLY_SUPPORTED",
        }
    )
    document["beams"][0]["geometry"]["span_mm"] = 6000
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(document)
    assert _codes(error) == {"DETAILING_DESIGN_BASIS_MISMATCH"}


def test_supplied_steel_factor_is_not_promoted_to_generated_bar_acceptance():
    document = _document(
        deflection_params={
            "span_mm": 4000,
            "d_mm": 444,
            "support_condition": "SIMPLY_SUPPORTED",
            "mf_tension_steel": 1.5,
        }
    )
    with pytest.raises(InputContractError) as error:
        api.compute_detailing(document)
    assert _codes(error) == {"DETAILING_DESIGN_SCOPE_UNSUPPORTED"}


@pytest.mark.parametrize(
    "command,suffix", [("bbs", "csv"), ("detail", "json"), ("dxf", "dxf")]
)
def test_cli_mixed_project_does_not_write_partial_artifact(
    command, suffix, tmp_path, capsys
):
    if command == "dxf":
        pytest.importorskip("ezdxf")
    document = _document()
    document["beams"].extend(_document(vu_kn=500)["beams"])
    source = tmp_path / "design.json"
    source.write_text(json.dumps(document), encoding="utf-8")
    output = tmp_path / f"output.{suffix}"
    assert cli.main([command, str(source), "-o", str(output)]) != 0
    assert not output.exists()
    assert "CONSUMER_RESULT_NOT_ACCEPTED" in capsys.readouterr().err


def test_dxf_uses_same_high_shear_schedule_as_bbs(tmp_path, monkeypatch):
    pytest.importorskip("ezdxf")
    document = _document()
    source = tmp_path / "design.json"
    source.write_text(json.dumps(document), encoding="utf-8")
    observed = []
    original = api.compute_dxf

    def capture(details, *args, **kwargs):
        observed.extend(deepcopy(details[0].stirrups))
        return original(details, *args, **kwargs)

    monkeypatch.setattr(cli.api, "compute_dxf", capture)
    output = tmp_path / "beam.dxf"
    assert cli.main(["dxf", str(source), "-o", str(output)]) == 0
    assert output.stat().st_size > 0
    assert [s.spacing for s in observed] == [100, 100, 100]
