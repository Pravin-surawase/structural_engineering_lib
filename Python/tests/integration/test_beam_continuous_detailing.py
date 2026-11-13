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


CUTOFF_CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-beam05-cutoff.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("name", CUTOFF_CASES)
def test_bottom_cutoff_uses_the_actual_cut_and_reduced_section_rows(name):
    case = CUTOFF_CASES[name]
    result = beam.check_continuous_detailing(
        beam.load_continuous_detailing(case["request"])
    )
    expected = case["expected"]
    assert result.engineering_status == expected["status"]
    cutoff = result.calculation["cutoff"]
    svg = beam.render_continuous_detailing_svg(result)
    bbs = beam.render_continuous_detailing_bbs_csv(result)
    report = beam.render_continuous_detailing_html(result)
    if name == "missing_cutoff_rows":
        assert cutoff["missing_cutoff_rows"] == [
            ("U2", "CUT-END"),
            ("U2", "CUT-THEORETICAL"),
        ]
    else:
        assert "Bottom bar cutoff" in report and "B01:CUT-END" in report
        for field, key in (
            ("actual_extension_mm", "available_extension_mm"),
            ("required_extension_mm", "required_extension_mm"),
            ("continuing_bottom_mm2", "continuing_bottom_mm2"),
            ("continuing_shear_capacity_kn", "continuing_shear_capacity_kn"),
            ("termination_shear_limit_kn", "two_thirds_shear_kn"),
        ):
            assert cutoff[field] == pytest.approx(expected[key], abs=1e-8)
        anchor = cutoff["anchorage"]["outputs"]["checks"][0]
        assert anchor["required_development_length_mm"] == pytest.approx(
            expected["development_mm"]
        )
        assert len(cutoff["termination_rows"]) == 4
        if name == "short_development":
            assert anchor["deficit_mm"] == pytest.approx(100)
        if name == "cutoff_shear_over_two_thirds":
            assert cutoff["termination_rows"][0] == {
                "row_id": "B01:CUT-END",
                "shear_kn": -90,
                "passes_two_thirds": False,
            }
    if expected["status"] != "PASS":
        assert svg is None and bbs is None
        return
    assert svg is not None and bbs is not None
    path = ElementTree.fromstring(svg).find("{*}line[@data-bar-id='bottom-3']")
    assert path is not None and float(path.attrib["x2"]) == 3500
    rows = list(csv.DictReader(StringIO(bbs)))
    shortened = [row for row in rows if row["bar_mark"].endswith("-cutoff")]
    assert len(shortened) == 1
    assert shortened[0]["quantity"] == "1"
    assert float(shortened[0]["cut_mm"]) == pytest.approx(expected["cut_mm"])
    assert sum(float(row["mass_kg"]) for row in rows) == pytest.approx(
        expected["mass_kg"]
    )
    identity = result.envelope.result_identity
    assert (
        identity is not None
        and identity.input_hash in report
        and identity.input_hash in bbs
    )


FLOW03 = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-flow03-beam-edit.json"
    ).read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", FLOW03["states"])
def test_bar_edit_rechecks_current_physical_paths(case):
    request = beam.load_continuous_detailing(CUTOFF_CASES["cutoff"]["request"])
    previous = beam.check_continuous_detailing(request)
    current = request
    if case == "stale_base":
        current = beam.load_continuous_detailing(
            {
                **request.model_dump(mode="json"),
                "stock_length_mm": 10000,
            }
        )
    edit = beam.BeamBarEditV1(
        bar_id=FLOW03["bar_id"],
        diameter_mm=FLOW03["edited_diameter_mm"],
        x_from_left_mm=FLOW03["congested_centre_mm"] if case == "congested" else None,
    )
    result = beam.recheck_continuous_bar_edit(
        current,
        previous,
        edit,
        analysis_basis=(
            "reinforcement_dependent_stiffness"
            if case == "changed_stiffness"
            else "fixed_supplied_actions"
        ),
    )
    edited = beam.load_continuous_detailing(result.request.model_dump(mode="json"))
    assert edited.member.reinforcement_revision != request.member.reinforcement_revision
    assert result.engineering_status == FLOW03["states"][case]
    assert beam.render_continuous_detailing_bbs_csv(previous, current=edited) is None
    assert beam.render_continuous_detailing_svg(previous, current=edited) is None
    assert "HOLD · stale result" in beam.render_continuous_detailing_html(
        previous, current=edited
    )
    report = beam.render_continuous_detailing_html(result, current=edited)
    assert "20 → 16 mm" in report
    output = beam.render_continuous_detailing_bbs_csv(result, current=edited)
    if case == "edited":
        assert output is not None
        rows = list(csv.DictReader(StringIO(output)))
        bar = next(row for row in rows if row["bar_mark"].endswith("-cutoff"))
        assert float(bar["diameter_mm"]) == FLOW03["edited_diameter_mm"]
        assert float(bar["cut_mm"]) == pytest.approx(FLOW03["edited_cut_mm"])
        assert sum(float(row["mass_kg"]) for row in rows) == pytest.approx(
            FLOW03["edited_mass_kg"]
        )
        assert beam.render_continuous_detailing_bbs_csv(result, current=request) is None
        svg = beam.render_continuous_detailing_svg(result, current=edited)
        assert svg is not None and svg in report
    else:
        assert output is None
        assert beam.render_continuous_detailing_svg(result, current=edited) is None
        if case == "congested":
            assert "GEOMETRY.SPACING" in {issue.code for issue in result.issues}
        else:
            assert result.envelope.freshness_status == "STALE"


LAP_CASES = json.loads(
    (
        Path(__file__).resolve().parents[3]
        / "docs/verification/library-029-beam05-lap.json"
    ).read_text(encoding="utf-8")
)["cases"]


@pytest.mark.parametrize("case", LAP_CASES)
def test_separated_lap_replays_both_pieces_and_keeps_checked_evidence(case):
    item = LAP_CASES[case]
    expected = item["expected"]
    result = beam.check_continuous_detailing(
        beam.load_continuous_detailing(item["request"])
    )
    assert result.engineering_status == expected["status"]
    lap = result.calculation["lap"]
    report = beam.render_continuous_detailing_html(result)
    svg = beam.render_continuous_detailing_svg(result)
    bbs = beam.render_continuous_detailing_bbs_csv(result)
    if case in {"lap", "short_lap"}:
        checked_lap = lap["lap_result"]
        splice = checked_lap["outputs"]["splice_checks"][0]
        assert splice["required_length_mm"] == pytest.approx(
            expected["required_lap_mm"]
        )
        assert splice["actual_length_mm"] == expected["overlap_mm"]
        assert "Separated bottom lap" in report and "805.915 mm" in report
        assert len(lap["stress_rows"]) == 12
    if case == "missing_mid_lap_row":
        assert lap["missing_lap_rows"] == [("U2", "LAP-MID")]
    if expected["status"] != "PASS":
        assert svg is None and bbs is None
        return
    assert svg is not None and svg in report and bbs is not None
    drawing = ElementTree.fromstring(svg)
    original = drawing.find("{*}line[@data-bar-id='bottom-3']")
    partner = drawing.find("{*}line[@data-bar-id='bottom-3-partner']")
    assert original is not None and partner is not None
    assert (
        float(original.attrib["x2"]) - float(partner.attrib["x1"])
        == expected["overlap_mm"]
    )
    rows = list(csv.DictReader(StringIO(bbs)))
    cuts = {
        row["bar_mark"].rsplit("-", 1)[-1]: float(row["cut_mm"])
        for row in rows
        if "-lap-" in row["bar_mark"]
    }
    assert cuts == {"I": expected["cut_original_mm"], "J": expected["cut_partner_mm"]}
    assert sum(float(row["mass_kg"]) for row in rows) == pytest.approx(
        expected["mass_kg"]
    )
    arrangement = result.calculation["arrangement"]["outputs"]
    relevant = [
        row["actual_clear_mm"]
        for row in arrangement["horizontal_clearance_checks"]
        if "bottom-3-partner" in (row["first_bar_id"], row["second_bar_id"])
    ]
    assert min(relevant) == pytest.approx(expected["minimum_pair_clear_mm"])
