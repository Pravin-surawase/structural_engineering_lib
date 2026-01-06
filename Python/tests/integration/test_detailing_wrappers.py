import json

import pytest

from structural_lib import api


@pytest.fixture
def design_results_dict():
    return {
        "schema_version": 1,
        "code": "IS456",
        "units": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "Story1",
                "geometry": {
                    "b": 300,
                    "D": 500,
                    "d": 460,
                    "span": 4000,
                    "cover": 40,
                },
                "materials": {
                    "fck": 25,
                    "fy": 500,
                },
                "flexure": {
                    "ast_req": 942.5,
                    "asc_req": 0,
                },
            }
        ],
    }


def test_compute_detailing_from_results(design_results_dict):
    detailing_list = api.compute_detailing(design_results_dict)

    assert len(detailing_list) == 1
    result = detailing_list[0]
    assert result.beam_id == "B1"
    assert len(result.top_bars) == 3
    assert len(result.bottom_bars) == 3
    assert len(result.stirrups) == 3


def test_compute_detailing_respects_config(design_results_dict):
    detailing_list = api.compute_detailing(
        design_results_dict,
        config={
            "stirrup_dia_mm": 10,
            "stirrup_spacing_start_mm": 125,
            "stirrup_spacing_mid_mm": 150,
            "stirrup_spacing_end_mm": 125,
            "is_seismic": True,
        },
    )

    result = detailing_list[0]
    assert result.stirrups[0].diameter == 10
    assert result.stirrups[1].spacing == 150
    assert result.stirrups[2].spacing == 125


def test_compute_bbs_and_export(tmp_path, design_results_dict):
    detailing_list = api.compute_detailing(design_results_dict)
    bbs_doc = api.compute_bbs(detailing_list, project_name="Test BBS")

    csv_path = tmp_path / "schedule.csv"
    json_path = tmp_path / "schedule.json"

    assert api.export_bbs(bbs_doc, csv_path).exists()
    assert api.export_bbs(bbs_doc, json_path, fmt="json").exists()

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["project_name"] == "Test BBS"
    assert data["items"]
