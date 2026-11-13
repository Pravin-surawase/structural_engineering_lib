"""Replay physical ring and spiral schedules and their eligibility controls."""

import csv
import json
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
