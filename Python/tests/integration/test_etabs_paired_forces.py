"""Exercise native table fidelity and incomplete import evidence."""

import json
import runpy
from dataclasses import replace
from pathlib import Path

import pytest

from structural_lib.beam.analysis import ForceUnit, Vector3
from structural_lib.beam.semantics import (
    EngineeringState,
    ExecutionState,
    FreshnessState,
)
from structural_lib.services.etabs_paired_forces import import_etabs_paired_forces

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = runpy.run_path(str(ROOT / "Python/examples/etabs_paired_forces.py"))
REFERENCE = json.loads(EXAMPLE["REFERENCE"].read_text())
COMPONENTS = ("p_n", "v2_n", "v3_n", "t_nmm", "m2_nmm", "m3_nmm")


def _change_beam(request, change):
    table = request.beam_table
    return replace(
        request, beam_table=replace(table, csv_bytes=change(table.csv_bytes))
    )


@pytest.mark.parametrize("alternate_units", (False, True))
def test_reconcile_eight_rows_with_frozen_signs_and_stations(alternate_units):
    request = EXAMPLE["build_request"](alternate_units=alternate_units)
    result = import_etabs_paired_forces(request)
    output = result.to_dict()["outputs"]
    assert result.engineering == EngineeringState.NOT_EVALUATED
    assert output["status"] == REFERENCE["controls"]["complete"]
    assert output["diagnostic_snapshot"] is None
    rows = output["normalized_snapshot"]["rows"]
    sources = output["source_rows"]
    assert len(rows) == len(sources) == 8
    assert len({row["row_id"] for row in rows}) == 8
    for row, source in zip(rows, sources, strict=True):
        assert row["source_row_id"] == source["source_row_id"]
        assert row["axis_id"] == f"{source['member_kind']}-axes"
        assert row["concurrency"] == "static_concurrent"
        assert row["load_case_id"] in REFERENCE["combinations"]
        assert (
            source["combination_design_use"]
            == REFERENCE["combinations"][row["load_case_id"]]
        )
        member = REFERENCE["members"][source["member_kind"]]
        assert row["member_id"] == f"{member['story']}/{member['label']}"
        assert row["object_id"] == row["analysis_element_id"] == member["object_id"]
        assert (
            row["object_station_mm"]
            == row["element_station_mm"]
            == member["station_mm"]
        )
        assert [row[key] for key in COMPONENTS] == member["expected_n_nmm"]


@pytest.mark.parametrize(
    ("case", "code"),
    (
        ("missing_combination", "IMPORT.REQUIRED_ROW_MISSING"),
        ("unclassified_combination", "IMPORT.ROW_OUTSIDE_INVENTORY"),
        ("envelope_combination", "IMPORT.COMBINATION_NOT_CONCURRENT"),
        ("stale_geometry", "IMPORT.STALE_OR_UNMATCHED_CAPTURE"),
        ("different_capture", "IMPORT.STALE_OR_UNMATCHED_CAPTURE"),
        ("unsupported_actions", "IMPORT.ACTION_OUTSIDE_PROFILE"),
    ),
)
def test_partial_intake_withholds_current_snapshot(case, code):
    request = EXAMPLE["build_request"]()
    if case == "missing_combination":
        request = _change_beam(
            request,
            lambda data: b"\n".join(
                line for line in data.splitlines() if b",U2," not in line
            ),
        )
    elif case == "unclassified_combination":
        request = _change_beam(
            request, lambda data: data + data.splitlines()[-1].replace(b",S2,", b",U3,")
        )
    elif case == "envelope_combination":
        definitions = request.combinations
        request = replace(
            request,
            combinations=(
                replace(definitions[0], source_type="Envelope"),
                *definitions[1:],
            ),
        )
    elif case == "stale_geometry":
        basis = replace(
            request.current_basis, section_stiffness_connectivity_revision="stiffness-2"
        )
        request = replace(request, current_basis=basis)
    elif case == "different_capture":
        request = replace(
            request, column_table=replace(request.column_table, capture_id="capture-2")
        )
    elif case == "unsupported_actions":
        request = _change_beam(
            request, lambda data: data.replace(b",1250,0,-32.5,0,", b",1250,1,-32.5,2,")
        )
        table = request.column_table
        request = replace(
            request,
            column_table=replace(
                table, csv_bytes=table.csv_bytes.replace(b",-412.5,", b",412.5,")
            ),
        )
    result = import_etabs_paired_forces(request)
    assert result.engineering == EngineeringState.NOT_EVALUATED
    assert result.outputs["status"] == REFERENCE["controls"][case]
    assert result.outputs["normalized_snapshot"] is None
    assert result.outputs["source_rows"]
    assert code in {diagnostic.code for diagnostic in result.diagnostics}
    if case in {"stale_geometry", "different_capture"}:
        assert result.freshness == FreshnessState.STALE
        assert result.outputs["diagnostic_snapshot"] is None
    else:
        rows = result.outputs["diagnostic_snapshot"]["rows"]
        assert len(rows) == len(result.outputs["source_rows"])
        if case == "unsupported_actions":
            assert rows[0]["p_n"] == 1000
            assert rows[0]["v3_n"] == 2000
            assert rows[-1]["p_n"] == 412500


@pytest.mark.parametrize(
    "case",
    (
        "conflicting_units",
        "duplicate_station",
        "reversed_ij",
        "invalid_axes",
        "wrong_table",
    ),
)
def test_invalid_input_is_rejected(case):
    request = EXAMPLE["build_request"]()
    beam, column = request.members
    if case == "conflicting_units":
        request = replace(
            request,
            configured_units=replace(request.configured_units, force=ForceUnit.N),
        )
    elif case == "duplicate_station":
        request = _change_beam(
            request,
            lambda data: data + data.splitlines()[-1].replace(b"18.75", b"19.75"),
        )
    elif case == "reversed_ij":
        request = replace(
            request, members=(replace(beam, i_mm=beam.j_mm, j_mm=beam.i_mm), column)
        )
    elif case == "invalid_axes":
        request = replace(
            request,
            members=(
                replace(beam, local_axes=replace(beam.local_axes, e3=Vector3(0, 1, 0))),
                column,
            ),
        )
    elif case == "wrong_table":
        request = _change_beam(
            request, lambda data: data.replace(b"Element Forces", b"Design Forces")
        )
    result = import_etabs_paired_forces(request)
    assert REFERENCE["controls"][case] == "REJECTED"
    assert result.execution == ExecutionState.REJECTED_INPUT
    assert result.engineering == EngineeringState.NOT_EVALUATED
    assert result.outputs == {}
    assert result.diagnostics
