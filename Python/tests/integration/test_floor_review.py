# SPDX-License-Identifier: MIT
"""Verify local intake, review, traceability and held actions through the public entry."""

from __future__ import annotations

import csv
import json
import shutil
from hashlib import sha256
from pathlib import Path

import pytest

from structural_lib.__main__ import main
from structural_lib.services.floor_review import review_floor_v1

EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "floor_review"
SNAPSHOT = (
    Path(__file__).resolve().parents[1] / "fixtures" / "etabs" / "p5_trial_export"
)


def _paired_packet(tmp_path: Path) -> tuple[Path, dict]:
    folder = tmp_path / "paired"
    shutil.copytree(EXAMPLES / "etabs-paired", folder)
    path = folder / "packet.json"
    return path, json.loads(path.read_text())


def _write_packet(path: Path, packet: dict) -> None:
    path.write_text(json.dumps(packet), encoding="utf-8")


def _table_path(path: Path, packet: dict, role: str = "beam_table") -> Path:
    return path.parent / packet[role]["file"]


def _edit_table(path: Path, packet: dict, edit) -> None:
    target = _table_path(path, packet)
    rows = list(csv.reader(target.read_text().splitlines()))
    edit(rows)
    with target.open("w", newline="", encoding="utf-8") as stream:
        csv.writer(stream, lineterminator="\n").writerows(rows)
    packet["beam_table"]["sha256"] = sha256(target.read_bytes()).hexdigest()


def _read_paired(path: Path) -> dict:
    return review_floor_v1(path, profile="etabs-paired", evaluate=True)


def test_prepared_formats_return_equivalent_inputs_and_checks() -> None:
    pytest.importorskip("openpyxl")
    baseline, workbook, json_package = [
        review_floor_v1(
            EXAMPLES / f"prepared.{fmt}", profile=f"prepared-{fmt}", evaluate=True
        )
        for fmt in ("csv", "xlsx", "json")
    ]
    for package in (baseline, workbook, json_package):
        assert package["intake_status"] == "ACCEPTED"
        assert package["summary"]["engineering_statuses"] == {"PASS": 2}
    for same_beam in zip(
        baseline["members"], workbook["members"], json_package["members"], strict=True
    ):
        first, sheet, as_json = same_beam
        assert (
            first["canonical_input"]
            == sheet["canonical_input"]
            == as_json["canonical_input"]
        )
        assert (
            first["signed_actions"]
            == sheet["signed_actions"]
            == as_json["signed_actions"]
        )
        assert (
            first["evaluation"]["result"]["calculation"]
            == sheet["evaluation"]["result"]["calculation"]
            == as_json["evaluation"]["result"]["calculation"]
        )
        assert (
            len(
                {item["source_identity"]["input_artifact_sha256"] for item in same_beam}
            )
            == 3
        )
        assert (
            first["source_identity"]["source_row_number"]
            == sheet["source_identity"]["worksheet_row_number"]
        )
        assert (
            as_json["source_identity"]["source_row_number"] + 1
            == sheet["source_identity"]["worksheet_row_number"]
        )
    assert baseline["members"][0]["signed_actions"][0]["mu_knm"] < 0
    assert (
        baseline["members"][0]["evaluation"]["result"]["request"]["actions"][
            "primary_tension_face"
        ]
        == "TOP"
    )


def test_cli_writes_traceable_review_with_pass_fail_and_intake_only(
    tmp_path: Path,
) -> None:
    packet = EXAMPLES / "etabs-paired" / "packet.json"
    output = tmp_path / "floor.json"
    assert (
        main(
            [
                "floor-review",
                "review",
                str(packet),
                "--profile",
                "etabs-paired",
                "-o",
                str(output),
            ]
        )
        == 0
    )
    result = json.loads(output.read_text())
    assert result["schema_version"] == "local-floor-review/v1"
    assert result["review_status"] == "QUALIFIED_REVIEW_REQUIRED"
    assert result["engineering_approval"] == "UNREVIEWED"
    assert result["summary"]["engineering_statuses"] == {
        "PASS": 1,
        "FAIL": 1,
        "NOT_EVALUATED": 1,
    }
    beam, failed, column = result["members"]
    assert len(beam["signed_actions"]) == 9
    assert len(beam["evaluation"]["section_checks"]) == 3
    assert [row["evaluation_disposition"] for row in beam["signed_actions"]].count(
        "NON_ULTIMATE_PREVIEW"
    ) == 3
    assert failed["geometry"]["i_mm"]["x"] == 9000
    assert failed["geometry"]["j_mm"]["x"] == 5000
    assert failed["geometry"]["local_axes"]["e1"]["x"] == -1
    assert failed["source_identity"]["analysis_element_id"] == "1002"
    assert failed["evaluation"]["engineering_status"] == "FAIL"
    governing = failed["evaluation"]["governing"]["hogging"]
    assert (governing["combination"], governing["station_mm"]) == ("ULS-G1", 200)
    assert (governing["m3_nmm"], governing["v2_n"]) == (-238_000_000, 128_000)
    paired = result["provenance"]["paired_intake"]
    assert paired["engineering"] == "not_evaluated"
    rows = paired["outputs"]["source_rows"]
    physical = next(
        row for row in rows if row["source_row_id"] == governing["source_row_id"]
    )
    assert physical["cells"][12:15] == ["-238", "1002", "200"]
    assert physical["source_line"] == 13
    assert physical["table_sha256"] == result["artifacts"][1]["sha256"]
    assert failed["signed_actions"][0]["analysis_epoch_id"] == "L2-RUN-014"
    assert column["evaluation"]["reason"] == "COLUMN_INTAKE_ONLY"
    assert {
        key: column["signed_actions"][0][key]
        for key in ("p_n", "v2_n", "v3_n", "t_nmm", "m2_nmm", "m3_nmm")
    } == {
        "p_n": -500000,
        "v2_n": 32000,
        "v3_n": -18000,
        "t_nmm": 1250000,
        "m2_nmm": -23000000,
        "m3_nmm": 18750000,
    }
    assert (
        main(
            [
                "floor-review",
                "review",
                str(packet),
                "--profile",
                "etabs-paired",
                "-o",
                str(output),
            ]
        )
        == 2
    )


def test_snapshot_preserves_signed_rows_and_stays_preview_only() -> None:
    result = review_floor_v1(
        SNAPSHOT / "floor-packet.json", profile="etabs-snapshot", evaluate=True
    )
    assert result["intake_status"] == "ACCEPTED"
    assert result["summary"]["engineering_statuses"] == {"NOT_EVALUATED": 2}
    snapshot = result["provenance"]["snapshot"]["snapshot"]
    assert snapshot["row_accounting"]["approved_exclusion_rows"] == 1
    assert snapshot["snapshot_sha256"]
    beam = result["members"][0]
    assert beam["member_id"] == "etabs:P5-TRIAL-HALL:101"
    assert beam["geometry"]["point2"]["x"] == 5
    assert [(row["m3_knm"], row["v2_kn"]) for row in beam["signed_actions"]] == [
        (-120, 75),
        (150, -60),
    ]
    assert beam["evaluation"]["reason"] == "SNAPSHOT_ENVELOPE_PREVIEW_ONLY"


@pytest.mark.parametrize(
    "change,code",
    (
        ("units_missing", "REQUIRED_FIELD_MISSING"),
        ("units_conflict", "IMPORT.INVALID_TABLE_OR_BINDING"),
        ("axes_missing", "REQUIRED_FIELD_MISSING"),
        ("axes_conflict", "IMPORT.INVALID_TABLE_OR_BINDING"),
        ("duplicates", "IMPORT.INVALID_TABLE_OR_BINDING"),
        ("stale", "IMPORT.STALE_OR_UNMATCHED_CAPTURE"),
        ("mixed", "IMPORT.STALE_OR_UNMATCHED_CAPTURE"),
        ("incomplete", "IMPORT.REQUIRED_ROW_MISSING"),
        ("case_type", "IMPORT.COMBINATION_NOT_CONCURRENT"),
        ("axial", "IMPORT.ACTION_OUTSIDE_PROFILE"),
        ("changed_bytes", "FLOOR.ARTIFACT_HASH_MISMATCH"),
    ),
)
def test_unresolved_native_inputs_withhold_engineering(
    tmp_path: Path, change: str, code: str
) -> None:
    path, packet = _paired_packet(tmp_path)
    if change == "units_missing":
        del packet["units"]["force"]
    elif change == "units_conflict":
        packet["units"]["force"] = "N"
    elif change == "axes_missing":
        del packet["members"][0]["e2"]
    elif change == "axes_conflict":
        packet["members"][0]["e1"] = [-1, 0, 0]
    elif change == "duplicates":
        _edit_table(path, packet, lambda rows: rows.append(rows[3]))
    elif change == "stale":
        packet["current_basis"]["analysis_revision"] = "NEW-REVISION"
    elif change == "mixed":
        packet["column_table"]["capture_id"] = "OTHER-CAPTURE"
    elif change == "incomplete":
        _edit_table(path, packet, lambda rows: rows.pop(3))
    elif change == "case_type":
        _edit_table(path, packet, lambda rows: rows[3].__setitem__(4, "Linear Static"))
    elif change == "axial":
        _edit_table(path, packet, lambda rows: rows[3].__setitem__(7, "-26"))
    elif change == "changed_bytes":
        target = _table_path(path, packet)
        target.write_bytes(target.read_bytes() + b"\n")
    _write_packet(path, packet)

    result = _read_paired(path)
    assert result["intake_status"] in {"BLOCKED", "HOLD"}
    assert code in {entry["code"] for entry in result["issues"]}
    assert all(
        member["evaluation"]["engineering_status"] == "NOT_EVALUATED"
        for member in result["members"]
    )
    if change in ("stale", "mixed"):
        assert (
            result["provenance"]["paired_intake"]["outputs"]["normalized_snapshot"]
            is None
        )
        assert result["artifacts"][1]["table_text"].count("L2,") == 18


def test_ultimate_torque_is_retained_and_holds_only_affected_beam(
    tmp_path: Path,
) -> None:
    path, packet = _paired_packet(tmp_path)
    _edit_table(path, packet, lambda rows: rows[3].__setitem__(10, "-2.25"))
    _write_packet(path, packet)

    result = _read_paired(path)
    assert result["intake_status"] == "ACCEPTED"
    assert (
        result["members"][0]["evaluation"]["reason"]
        == "FLOOR.ACTION_OUTSIDE_SECTION_PROFILE"
    )
    assert result["members"][0]["signed_actions"][0]["t_nmm"] == -2_250_000
    assert result["members"][1]["evaluation"]["engineering_status"] == "FAIL"


def test_mismatched_reinforcement_revision_withholds_affected_section(
    tmp_path: Path,
) -> None:
    path, packet = _paired_packet(tmp_path)
    packet["members"][0]["section"]["analysis_revision"] = "EARLIER-ANALYSIS"
    _write_packet(path, packet)

    result = _read_paired(path)
    assert result["members"][0]["evaluation"]["reason"] == "FLOOR.STALE_SECTION"
    assert result["members"][1]["evaluation"]["engineering_status"] == "FAIL"


def test_hash_bound_xlsx_projection_matches_native_review(tmp_path: Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    path, packet = _paired_packet(tmp_path)
    baseline = _read_paired(path)
    for role in ("beam_table", "column_table"):
        target = _table_path(path, packet, role)
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "ETABS Table"
        for row in csv.reader(target.read_text().splitlines()):
            sheet.append(row)
        workbook_file = target.with_suffix(".xlsx")
        workbook.save(workbook_file)
        packet[role].update(
            file=workbook_file.name,
            sha256=sha256(workbook_file.read_bytes()).hexdigest(),
            worksheet="ETABS Table",
        )
    _write_packet(path, packet)

    result = _read_paired(path)
    assert result["intake_status"] == "ACCEPTED"
    assert result["members"] == baseline["members"]
    assert [artifact["projection_sha256"] for artifact in result["artifacts"][1:]] == [
        artifact["sha256"] for artifact in baseline["artifacts"][1:]
    ]


def test_preview_does_not_report_a_pass_and_edb_is_not_ingested(tmp_path: Path) -> None:
    path, _ = _paired_packet(tmp_path)
    preview = review_floor_v1(path, profile="etabs-paired")
    assert preview["summary"]["engineering_statuses"] == {"NOT_EVALUATED": 3}
    edb = tmp_path / "local.edb"
    edb.write_bytes(b"unread native placeholder")
    rejected = review_floor_v1(edb, profile="etabs-paired")
    assert rejected["intake_status"] == "BLOCKED"
    assert "licensed ETABS on Windows" in rejected["issues"][0]["message"]
