"""Check two-span quantity and artifact identity against independent values."""

import csv
import json
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import beam

CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-beam05-member-detailing.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("name", CASES)
def test_continuous_detailing_report_drawing_bbs(name):
    case = CASES[name]
    request = beam.load_continuous_detailing(case["request"])
    result = beam.check_continuous_detailing(request)
    expected = case["expected"]
    assert result.engineering_status.value == expected["status"]
    report = beam.render_continuous_detailing_html(result)
    identity = result.to_dict()["envelope"]["result_identity"]["input_hash"]
    assert identity in report and "Qualified review required" in report
    drawing = beam.render_continuous_detailing_svg(result)
    bbs = beam.render_continuous_detailing_bbs_csv(result)
    if expected["status"] != "PASS":
        assert drawing is None and bbs is None
        assert result.calculation["bbs"] is None
        return
    assert drawing is not None and bbs is not None
    paths = result.calculation["paths"]
    assert drawing in report and identity in drawing and paths["result_id"] in drawing
    assert len(ElementTree.fromstring(drawing).findall("{*}line")) == 34
    rows = list(csv.DictReader(StringIO(bbs)))
    links = [row for row in rows if row["role"] == "transverse_link"]
    longitudinal = [row for row in rows if row not in links]
    assert sum(int(row["quantity"]) for row in links) == expected["link_count"]
    assert (
        sum(int(row["quantity"]) for row in longitudinal)
        == expected["longitudinal_count"]
    )
    assert float(links[0]["cut_mm"]) == pytest.approx(expected["link_cut_mm"], abs=1e-8)
    assert all(
        float(row["cut_mm"]) == expected["longitudinal_cut_mm"] for row in longitudinal
    )
    assert sum(float(row["mass_kg"]) for row in rows) == pytest.approx(
        expected["mass_kg"], abs=1e-8
    )
    assert all(
        row["input_hash"] == identity and row["path_result_id"] == paths["result_id"]
        for row in rows
    )
