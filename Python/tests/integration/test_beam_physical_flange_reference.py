"""Check the frozen physical T flange through the public detailing outputs."""

import csv
import hashlib
import json
import runpy
from collections import Counter
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import pytest

from structural_lib.design.is456 import beam

ROOT = Path(__file__).resolve().parents[3]
REFERENCE = ROOT / "docs/verification/library-030-beam05-physical-flange.json"
CASES = json.loads(REFERENCE.read_text(encoding="utf-8"))["cases"]
ISSUES = {
    "link_clash": "BEAM.FLANGE_LINK_CLASH_FAIL",
    "open_flange_link": "BEAM.FLANGE_CAP_CLOSURE_FAIL",
    "short_flange_development": "BEAM.FLANGE_DEVELOPMENT_FAIL",
    "missing_strip_actions": "BEAM.FLANGE_STRIP_ACTIONS_HELD",
    "stale_strip_geometry": "BEAM.FLANGE_STRIP_REVISION_HELD",
}


def test_physical_flange_reference_is_unchanged() -> None:
    assert hashlib.sha256(REFERENCE.read_bytes()).hexdigest() == (
        "2168766fbdd95d8657e8274172b2dd8c3318fb083fa35640f10cf2b69db7cf3e"
    )


@pytest.mark.parametrize("name", CASES)
def test_physical_flange_reference_and_outputs(name: str) -> None:
    convert = runpy.run_path(
        str(ROOT / "Python/examples/beam_continuous_detailing.py")
    )["physical_flange_fixture_input"]
    case = CASES[name]
    request = beam.load_continuous_detailing(convert(case["request"]))
    result = beam.check_continuous_detailing(request)
    report = beam.render_continuous_detailing_html(result, current=request)
    drawing = beam.render_continuous_detailing_svg(result, current=request)
    schedule = beam.render_continuous_detailing_bbs_csv(result, current=request)
    expected = case["expected"]
    assert result.engineering_status.value == expected["status"]
    stamp = result.envelope.result_identity
    assert stamp is not None and stamp.input_hash in report
    if name in ISSUES:
        assert ISSUES[name] in {issue.code for issue in result.issues}
        assert ISSUES[name] in report
        assert result.calculation["bbs"] is None and schedule is drawing is None
        assert "<svg" not in report and "Checked schedule withheld" in report
        return

    assert drawing is not None and schedule is not None
    assert drawing in report and stamp.input_hash in drawing
    strength = result.calculation["strength"]
    assembly = result.calculation["physical_flange"]
    checks = assembly["engineering"]
    assert checks["basis"]["effective_width_mm"] == expected["effective_width_mm"]
    assert (
        checks["basis"]["hogging_distribution_width_mm"]
        == expected["hogging_distribution_width_mm"]
    )
    assert strength["governing_rows"]["hogging"] == expected["governing_moment_row"]
    assert strength["governing_rows"]["shear"] == expected["governing_shear_row"]
    assert checks["strength"]["nominal_capacity_knm"]["top"] == pytest.approx(
        expected["hogging_strength"]["capacity_knm"]
    )
    assert checks["strength"]["web_only_hogging_capacity_knm"] == pytest.approx(
        expected["web_only_strength"]["top"]["capacity_knm"]
    )
    assert checks["strength"]["nominal_web_shear_capacity_kn"]["top"] == pytest.approx(
        expected["web_only_strength"]["top"]["shear_capacity_kn"]
    )
    assert checks["strength"]["adverse_capacity_knm"] == pytest.approx(
        expected["adverse_placement_capacity_knm"]
    )
    assert {row["action"]["row_id"]: row["action"] for row in strength["rows"]} == {
        row["row_id"]: row for row in case["request"]["actions"]
    }

    for actual, target in zip(
        checks["strip"]["strip_checks"], expected["strip_checks"], strict=True
    ):
        for key, value in target.items():
            assert actual[key] == (
                value if isinstance(value, str) else pytest.approx(value)
            )
    assert checks["strip"]["capacity_knm"]["nominal"]["top"] == pytest.approx(
        expected["strip_flexure_capacity_knm"]
    )
    assert checks["strip"]["available_main_development_mm"] == pytest.approx(
        expected["available_slab_main_development_mm"]
    )
    for bar in checks["anchorage"]["bars"]:
        assert (
            bar["available_at_support_mm"]
            == expected["minimum_flange_support_development_mm"]
        )
        assert bar["required_development_mm"] == pytest.approx(
            expected["required_flange_development_mm"]
        )
    placement = checks["geometry"]
    assert placement["flange_hook_plane_clearance_mm"] == pytest.approx(
        expected["flange_hook_plane_clearance_mm"]
    )
    assert placement["flange_hook_tails_mm"] == pytest.approx(
        expected["flange_hook_tails_mm"]
    )
    assert placement["nominal_cover_mm"] == pytest.approx(
        {
            "web": expected["nominal_cover_mm"]["web_mm"],
            "flange": expected["nominal_cover_mm"]["cap_mm"],
            "slab": expected["nominal_cover_mm"]["slab_mm"],
        }
    )
    assert placement["axial_access_mm"] == pytest.approx(
        expected["minimum_clearances_mm"]["cap_to_next_main_access_mm"]
    )
    assert placement["transverse_access_mm"] == pytest.approx(184 / 3 - 20)
    assert (
        placement["minimum_compaction_access_mm"]
        > case["request"]["minimum_compaction_access_mm"]
    )

    pieces = assembly["pieces"]
    physical_ids = {piece["bar_id"] for piece in pieces}
    assert len(pieces) == len(physical_ids) == expected["pieces"]
    assert Counter(piece["owner"] for piece in pieces) == {"BEAM": 118, "SLAB": 142}
    counts = Counter(piece["mark"] for piece in pieces)
    by_mark = {row["bar_mark"]: row for row in csv.DictReader(StringIO(schedule))}
    assert set(by_mark) == set(counts)
    for cut in expected["schedule"]:
        row = by_mark[cut["mark"]]
        assert row["owner"] == cut["owner"]
        assert int(row["quantity"]) == cut["quantity"] == counts[cut["mark"]]
        assert float(row["cut_mm"]) == pytest.approx(cut["cut_length_mm"])
        assert float(row["mass_kg"]) == pytest.approx(cut["mass_kg"])
        assert row["input_hash"] == stamp.input_hash
        assert row["path_result_id"] == result.calculation["paths"]["result_id"]
        assert report.count(f'data-mark="{cut["mark"]}"') == 1
    assert sum(float(row["mass_kg"]) for row in by_mark.values()) == pytest.approx(
        expected["mass_kg"]
    )
    sections = ElementTree.fromstring(drawing)
    elevation = next(el for el in sections if el.get("data-view") == "elevation")
    assert {piece.get("data-piece-id") for piece in elevation} - {None} == physical_ids
