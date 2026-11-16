"""Verify the independently frozen Altair ETABS 21.0.0 intake."""

import csv
import hashlib
import io
import json
import runpy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from structural_lib.beam.semantics import canonical_json_bytes
from structural_lib.services.etabs_paired_forces import import_etabs_paired_forces

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/etabs_paired_forces.py"))
REFERENCE_PATH = EXAMPLE["ALTAIR_REFERENCE"]
REFERENCE_SHA256 = "9a7ddc091375e92215e6755f904fd6ddb8d25729d25e96c4968a58e25d0a9ddf"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CONTROLS = REFERENCE["controls"]
STATION_SIDES_PATH = REFERENCE_PATH.with_name(
    "library-030-flow04-altair-v21-station-sides.json"
)
STATION_SIDES_SHA256 = (
    "4b6ee3309f2fa43da883a3d800fdc4523002fc6ab543dfc42c4a60da1d1c3a69"
)
STATION_SIDES = json.loads(STATION_SIDES_PATH.read_text(encoding="utf-8"))


def _replace_table_rows(table, rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return replace(table, csv_bytes=stream.getvalue().encode("utf-8"))


@pytest.mark.parametrize(
    "path,digest,reference",
    (
        (REFERENCE_PATH, REFERENCE_SHA256, REFERENCE),
        (STATION_SIDES_PATH, STATION_SIDES_SHA256, STATION_SIDES),
    ),
    ids=("blank-location", "interior-sides"),
)
def test_altair_pair_preserves_concurrent_signed_rows(path, digest, reference) -> None:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    request = EXAMPLE["build_altair_request"](path)
    result = import_etabs_paired_forces(request).to_dict()
    expected = reference["controls"]["positive"]
    output = result["outputs"]
    snapshot = output["normalized_snapshot"]
    assert result["engineering"] == expected["engineering"]
    assert output["status"] == expected["status"]
    assert output["diagnostic_snapshot"] is None
    assert snapshot["analysis_epoch_id"] == reference["basis"]["analysis_revision"]
    assert snapshot["result_epoch_id"] == reference["capture_id"]
    assert len(snapshot["rows"]) == len(output["source_rows"]) == expected["rows"]
    assert len({row["row_id"] for row in snapshot["rows"]}) == expected["rows"]

    for row, source in zip(snapshot["rows"], output["source_rows"], strict=True):
        kind = source["member_kind"]
        member = reference["members"][kind]
        target = member["expected_rows"][source["source_line"] - 4]
        digest = member["table_sha256"]
        assert source["table_sha256"] == digest
        assert source["source_line"] == target["projected_csv_line"]
        assert row["source_row_id"] == f"{kind}:{digest}:{source['source_line']}"
        assert row["member_id"] == f"{member['story']}/{member['label']}"
        assert row["object_id"] == member["object_id"]
        assert row["analysis_element_id"] == member["analysis_element_id"]
        assert row["load_case_id"] == target["combination"]
        assert row["concurrency"] == "static_concurrent"
        assert row.get("station_side") == target.get("station_side")
        for station in ("object_station_mm", "element_station_mm"):
            assert row[station] == pytest.approx(target["station_mm"], abs=1e-8)
        for component, value in target["normalized_components"].items():
            assert row[component] == pytest.approx(value, rel=1e-12, abs=0)

    for axes in snapshot["local_axes"]:
        kind = axes["axis_id"].removesuffix("-axes")
        for name, expected_vector in zip(
            ("e1", "e2", "e3"), reference["members"][kind]["axis_vectors"], strict=True
        ):
            assert [axes[name][axis] for axis in "xyz"] == expected_vector

    for witness in reference.get("shear_jumps", ()):
        before, after = [
            row
            for row in snapshot["rows"]
            if row["object_id"] == witness["object"]
            and row["load_case_id"] == witness["combination"]
            and row.get("station_side") in ("before", "after")
        ]
        assert (before["station_side"], after["station_side"]) == ("before", "after")
        assert before["object_station_mm"] == after["object_station_mm"]
        assert after["v2_n"] - before["v2_n"] == pytest.approx(
            float(witness["expected_shear_jump_kn"]) * 1000,
            abs=1e-7,
        )
        assert before["m3_nmm"] == after["m3_nmm"]
        assert before["t_nmm"] == after["t_nmm"]


@pytest.mark.parametrize(
    "release,helper", (("22.7.0", "build_request"), ("21.0.0", "build_altair_request"))
)
def test_blank_location_result_identity_is_unchanged(release, helper) -> None:
    result = import_etabs_paired_forces(EXAMPLE[helper]()).to_dict()
    assert (
        hashlib.sha256(canonical_json_bytes(result)).hexdigest()
        == STATION_SIDES["legacy_intake_result_sha256"][release]
    )


@pytest.mark.parametrize(
    "name",
    (
        "missing_after",
        "missing_pair",
        "duplicate_before",
        "blank_at_pair",
        "undeclared_pair",
        "endpoint_pair",
        "different_coordinates",
    ),
)
def test_station_side_refusals_withhold_current_snapshot(name) -> None:
    request = EXAMPLE["build_altair_request"](STATION_SIDES_PATH)
    expected = STATION_SIDES["controls"][name]
    table = request.beam_table
    rows = list(csv.reader(io.StringIO(table.csv_bytes.decode("utf-8"))))
    before, after = [row for row in rows[3:] if row[3] == "SLS_Gravity" and row[-1]]
    if name == "undeclared_pair":
        request = replace(request, station_side_pairs=())
    elif name == "endpoint_pair":
        (pair,) = request.station_side_pairs
        request = replace(request, station_side_pairs=(replace(pair, station_mm=0.0),))
    else:
        if name in ("missing_after", "missing_pair"):
            rows.remove(after)
            if name == "missing_pair":
                rows.remove(before)
        elif name == "duplicate_before":
            rows.append(before)
        elif name == "blank_at_pair":
            after[-1] = ""
        elif name == "different_coordinates":
            offset_ft = Decimal(expected["difference_mm"]) / Decimal("304.8")
            for field in ("Station", "Elem Station"):
                index = rows[1].index(field)
                after[index] = str(Decimal(after[index]) + offset_ft)
        request = replace(request, beam_table=_replace_table_rows(table, rows))

    result = import_etabs_paired_forces(request).to_dict()
    assert result["outputs"].get("normalized_snapshot") is None
    diagnosed = [
        item for item in result["diagnostics"] if item["code"] == expected["diagnostic"]
    ]
    assert diagnosed
    if "execution" in expected:
        assert result["execution"] == expected["execution"]
    else:
        assert result["outputs"]["status"] == expected["status"]
        assert (
            len(result["outputs"]["diagnostic_snapshot"]["rows"])
            == expected["diagnostic_rows"]
        )
        missing = (
            [expected["missing_side"]]
            if name == "missing_after"
            else expected["missing_sides"]
        )
        assert (
            sorted(issue["field_or_location"].rsplit("/", 1)[1] for issue in diagnosed)
            == missing
        )


@pytest.mark.parametrize(
    "name",
    (
        "missing_row",
        "stale_capture",
        "envelope",
        "duplicate",
        "mixed_version",
        "wrong_location",
        "wrong_units",
        "wrong_axis",
    ),
)
def test_altair_refusals_withhold_current_snapshot(name) -> None:
    request = EXAMPLE["build_altair_request"]()
    table = request.beam_table
    rows = list(csv.reader(io.StringIO(table.csv_bytes.decode("utf-8"))))
    if name == "stale_capture":
        request = replace(
            request,
            column_table=replace(request.column_table, capture_id="older-capture"),
        )
    elif name == "mixed_version":
        request = replace(
            request, column_table=replace(request.column_table, etabs_release="22.7.0")
        )
    elif name == "envelope":
        service, ultimate = request.combinations
        request = replace(
            request, combinations=(service, replace(ultimate, source_type="Envelope"))
        )
    elif name == "wrong_axis":
        beam, column = request.members
        e1 = beam.local_axes.e1
        reverse = replace(e1, x=-e1.x, y=-e1.y, z=-e1.z)
        request = replace(
            request,
            members=(
                replace(beam, local_axes=replace(beam.local_axes, e1=reverse)),
                column,
            ),
        )
    else:
        if name == "missing_row":
            rows.pop()
        elif name == "duplicate":
            rows.append(rows[-1])
        elif name == "wrong_location":
            rows[-1][-1] = "After"
        elif name == "wrong_units":
            rows[2][5] = "m"
        request = replace(request, beam_table=_replace_table_rows(table, rows))

    result = import_etabs_paired_forces(request).to_dict()
    expected = CONTROLS[name]
    assert expected["diagnostic"] in {issue["code"] for issue in result["diagnostics"]}
    assert result["outputs"].get("normalized_snapshot") is None
    if "execution" in expected:
        assert result["execution"] == expected["execution"]
    else:
        assert result["outputs"]["status"] == expected["status"]
        if name == "stale_capture":
            assert result["outputs"]["diagnostic_snapshot"] is None
            assert len(result["outputs"]["source_rows"]) == 8


@pytest.mark.parametrize(
    "name",
    (
        "numerical_zero_boundary",
        "above_numerical_zero_boundary",
        "material_beam_component",
    ),
)
@pytest.mark.parametrize("column", (6, 8, 10), ids=("P", "V3", "M2"))
def test_altair_numerical_zero_limit_keeps_original_cells(name, column) -> None:
    request = EXAMPLE["build_altair_request"]()
    table = request.beam_table
    rows = list(csv.reader(io.StringIO(table.csv_bytes.decode("utf-8"))))
    expected = CONTROLS[name]
    value = str(expected["value"])
    rows[3][column] = value
    request = replace(request, beam_table=_replace_table_rows(table, rows))
    result = import_etabs_paired_forces(request).to_dict()
    output = result["outputs"]
    assert output["status"] == expected["status"]
    assert output["source_rows"][0]["cells"][column] == value
    if "diagnostic" in expected:
        assert expected["diagnostic"] in {
            issue["code"] for issue in result["diagnostics"]
        }
        assert output["normalized_snapshot"] is None
        assert output["diagnostic_snapshot"] is not None
    else:
        assert output["normalized_snapshot"] is not None


def test_22_7_requires_exact_zero_for_off_profile_beam_components() -> None:
    request = EXAMPLE["build_request"]()
    table = request.beam_table
    rows = list(csv.reader(io.StringIO(table.csv_bytes.decode("utf-8"))))
    column = rows[1].index("P")
    rows[3][column] = "1e-14"
    request = replace(request, beam_table=_replace_table_rows(table, rows))

    result = import_etabs_paired_forces(request).to_dict()
    assert result["outputs"]["status"] == "HOLD"
    assert result["outputs"]["normalized_snapshot"] is None
    assert "IMPORT.ACTION_OUTSIDE_PROFILE" in {
        issue["code"] for issue in result["diagnostics"]
    }
