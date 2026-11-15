"""Replay physical ring and spiral schedules and their eligibility controls."""

import csv
import json
from copy import deepcopy
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import column

CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-col07-circular-member.json"
    ).read_text()
)["cases"]


@pytest.mark.parametrize("name", CASES)
def test_circular_detailing_quantities_and_artifacts(name):
    case = CASES[name]
    request = column.load_circular_column_detailing(case["request"])
    result = column.check_circular_column_detailing(request)
    expected = case["expected"]
    assert result.engineering_status.value == expected["status"]
    wire = result.to_dict()
    identity = wire["envelope"]["result_identity"]["input_hash"]
    assert [row["combination_id"] for row in wire["calculation"]["sections"]] == [
        "U1",
        "U2",
    ]
    report = column.render_circular_detailing_html(result)
    drawing = column.render_circular_detailing_svg(result)
    schedule = column.render_circular_detailing_bbs_csv(result)
    assert identity in report and "Qualified review required" in report
    if expected["status"] != "PASS":
        assert drawing is None and schedule is None
        return
    assert drawing is not None and schedule is not None
    assert identity in drawing and identity in schedule
    assert drawing in report
    xml = ElementTree.fromstring(drawing)
    tag = "line" if name == "tied" else "polyline"
    assert (
        len(xml.findall(f".//{{*}}{tag}[@data-mark]")) == expected["transverse_count"]
    )
    rows = list(csv.DictReader(StringIO(schedule)))
    assert sum(float(row["total_weight_kg"]) for row in rows) == pytest.approx(
        expected["mass_kg"]
    )
    transverse = [row for row in rows if row["role"] != "longitudinal"]
    assert len(transverse) == 1
    assert int(transverse[0]["quantity"]) == expected["transverse_count"]
    assert float(transverse[0]["cut_length_mm"]) == pytest.approx(expected["cut_mm"])
    main = [row for row in rows if row["role"] == "longitudinal"]
    assert len(main) == expected["longitudinal_count"]
    assert all(
        float(row["cut_length_mm"]) == expected["longitudinal_cut_mm"] for row in main
    )


@pytest.mark.parametrize(
    "name,limit,status",
    [
        ("tied", 70, "PASS"),
        ("tied", 75, "FAIL"),
        ("spiral", 55, "PASS"),
        ("spiral", 56, "FAIL"),
    ],
)
def test_circular_end_faces_obey_stricter_detail_clearance(name, limit, status):
    request = deepcopy(CASES[name]["request"])
    if name == "tied":
        request["placement"].update(first_station_mm=75, last_station_mm=2925)
        request["end_detail"]["max_end_hoop_offset_mm"] = 90
        start_actual = end_actual = 70
    else:
        request["placement"]["end_anchor_pitch_mm"] = 20
        start_actual, end_actual = 62.5, 55
    request["end_detail"]["end_face_clearance_mm"] = limit
    result = column.check_circular_column_detailing(
        column.load_circular_column_detailing(request)
    )
    assert result.engineering_status.value == status
    report = column.render_circular_detailing_html(result)
    assert "end_detail.end_face_clearance_mm" in report
    assert f"{start_actual:g} mm at the start" in report
    assert f"{end_actual:g} mm at the end" in report
    assert (column.render_circular_detailing_svg(result) is not None) == (
        status == "PASS"
    )
    assert (column.render_circular_detailing_bbs_csv(result) is not None) == (
        status == "PASS"
    )
    if status == "FAIL":
        assert result.calculation["transverse"] is None
        assert any(
            issue.code == "COLUMN.CIRCULAR_END_PLACEMENT"
            and issue.path == "end_detail.end_face_clearance_mm"
            for issue in result.issues
        )
