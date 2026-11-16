"""Verify the independently frozen Altair ETABS 21.0.0 intake."""

import csv
import hashlib
import io
import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest

from structural_lib.services.etabs_paired_forces import import_etabs_paired_forces

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/etabs_paired_forces.py"))
REFERENCE_PATH = EXAMPLE["ALTAIR_REFERENCE"]
REFERENCE_SHA256 = "9a7ddc091375e92215e6755f904fd6ddb8d25729d25e96c4968a58e25d0a9ddf"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
CONTROLS = REFERENCE["controls"]


def _replace_table_rows(table, rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return replace(table, csv_bytes=stream.getvalue().encode("utf-8"))


def test_altair_pair_preserves_eight_concurrent_signed_rows() -> None:
    assert hashlib.sha256(REFERENCE_PATH.read_bytes()).hexdigest() == REFERENCE_SHA256
    request = EXAMPLE["build_altair_request"]()
    result = import_etabs_paired_forces(request).to_dict()
    expected = CONTROLS["positive"]
    output = result["outputs"]
    snapshot = output["normalized_snapshot"]
    assert result["engineering"] == expected["engineering"]
    assert output["status"] == expected["status"]
    assert output["diagnostic_snapshot"] is None
    assert snapshot["analysis_epoch_id"] == REFERENCE["basis"]["analysis_revision"]
    assert snapshot["result_epoch_id"] == REFERENCE["capture_id"]
    assert len(snapshot["rows"]) == len(output["source_rows"]) == expected["rows"]

    for row, source in zip(snapshot["rows"], output["source_rows"], strict=True):
        kind = source["member_kind"]
        member = REFERENCE["members"][kind]
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
        for station in ("object_station_mm", "element_station_mm"):
            assert row[station] == pytest.approx(target["station_mm"], abs=1e-8)
        for component, value in target["normalized_components"].items():
            assert row[component] == pytest.approx(value, rel=1e-12, abs=0)

    for axes in snapshot["local_axes"]:
        kind = axes["axis_id"].removesuffix("-axes")
        for name, expected_vector in zip(
            ("e1", "e2", "e3"), REFERENCE["members"][kind]["axis_vectors"], strict=True
        ):
            assert [axes[name][axis] for axis in "xyz"] == expected_vector


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
