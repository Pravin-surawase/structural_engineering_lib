"""Source-free exact-wheel UAT for the pre-release input-safety contract."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import sys
import sysconfig
import tempfile
from collections.abc import Callable
from importlib.resources import files
from pathlib import Path
from typing import Any

import structural_lib
from structural_lib import __main__ as cli_main
from structural_lib.core.data_types import FootingType
from structural_lib.core.models import BeamForces
from structural_lib.services import api
from structural_lib.services.batch import design_project_beams_v1
from structural_lib.services.footing_api import (
    ConcentricIsolatedFootingInput,
    design_concentric_isolated_footing_is456,
)
from structural_lib.services.import_ledger import ImportIssueCode, ImportStatus
from structural_lib.services.imports import (
    parse_dual_csv_lossless,
    parse_single_csv_lossless,
)

_MATRIX_RESOURCE = files("structural_lib").joinpath("data/release_negative_uat_v1.json")
_ENTRYPOINT_RESOURCE = files("structural_lib").joinpath(
    "data/advertised_entry_points_v1.json"
)


def _beam(**updates: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": "project-beam-design/v1",
        "member_id": "B1",
        "b_mm": 300,
        "D_mm": 500,
        "d_mm": 442,
        "mu_knm": 150,
        "vu_kn": 80,
        "fck_nmm2": 25,
        "fy_nmm2": 500,
    }
    value.update(updates)
    return value


def _assert_blocked(payload: dict[str, Any]) -> dict[str, Any]:
    result = design_project_beams_v1([payload]).to_dict()
    member = result["members"][0]
    assert member["intake_status"] == "BLOCKED"
    assert member["calculation_status"] == "NOT_EVALUATED"
    assert member["overall_status"] == "BLOCKED"
    assert member["calculation"] is None
    return {"issue_codes": [issue["code"] for issue in member["issues"]]}


def _write(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


_CLI_HEADER = (
    "BeamID,Story,b,D,eff_d,Span,Cover,fck,fy,Mu,Vu," "Stirrup_Dia,Stirrup_Spacing"
)
_CLI_VALID_ROW = "B1,S1,300,500,450,4000,40,25,500,150,80,8,150"


def _capture_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        return cli_main.main(argv), stdout.getvalue(), stderr.getvalue()


def _assert_cli_blocked(
    text: str, *, suffix: str = ".csv", extra: list[str] | None = None
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / f"input{suffix}"
        _write(path, text)
        rc, stdout, stderr = _capture_cli(["design", str(path), *(extra or [])])
    assert rc != 0
    assert stdout == ""
    assert "Design complete" not in stderr
    return {"return_code": rc, "stderr": stderr.splitlines()[-1]}


def _case_cli_design_valid() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "input.csv"
        _write(path, f"{_CLI_HEADER}\n{_CLI_VALID_ROW}")
        rc, stdout, stderr = _capture_cli(["design", str(path)])
    payload = json.loads(stdout)
    assert rc == 0 and payload["schema_version"] == 1
    assert payload["summary"]["total_beams"] == 1
    assert "Warning: Skipping row" not in stdout
    return {
        "beams": 1,
        "diagnostics_stream": "stderr",
        "stderr_lines": len(stderr.splitlines()),
    }


def _case_cli_design_malformed_only() -> dict[str, Any]:
    return _assert_cli_blocked(
        f"{_CLI_HEADER}\nB1,S1,BAD,500,450,4000,40,25,500,150,80,8,150"
    )


def _case_cli_design_mixed_validity() -> dict[str, Any]:
    return _assert_cli_blocked(
        f"{_CLI_HEADER}\n{_CLI_VALID_ROW}\n"
        "B2,S1,BAD,500,450,4000,40,25,500,150,80,8,150"
    )


def _case_cli_design_empty() -> dict[str, Any]:
    return _assert_cli_blocked(_CLI_HEADER)


def _case_cli_design_missing_depth_basis() -> dict[str, Any]:
    header = _CLI_HEADER.replace(",eff_d", "")
    row = _CLI_VALID_ROW.replace(",450", "", 1)
    return _assert_cli_blocked(f"{header}\n{row}")


def _case_cli_design_non_finite() -> dict[str, Any]:
    return _assert_cli_blocked(
        '{"schema_version":"cli-beam-design-input/v1","beams":['
        '{"beam_id":"B1","story":"S1","b":300,"D":500,"d":NaN,'
        '"span":4000,"cover":40,"fck":25,"fy":500,"Mu":150,"Vu":80,'
        '"stirrup_dia":8,"stirrup_spacing":150}]}',
        suffix=".json",
    )


def _case_cli_design_unknown_field() -> dict[str, Any]:
    return _assert_cli_blocked(f"{_CLI_HEADER},mystery\n{_CLI_VALID_ROW},value")


def _case_cli_design_duplicate_identity() -> dict[str, Any]:
    return _assert_cli_blocked(f"{_CLI_HEADER}\n{_CLI_VALID_ROW}\n{_CLI_VALID_ROW}")


def _case_cli_design_ambiguous_format() -> dict[str, Any]:
    return _assert_cli_blocked(
        "Story,Label,b,D,eff_d,Span,Cover,fck,fy,Mu,Vu,"
        "Stirrup_Dia,Stirrup_Spacing\n"
        "S1,B1,300,500,450,4000,40,25,500,150,80,8,150",
        extra=["--input-format", "auto"],
    )


def _case_cli_design_downstream_consumers() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        input_path = root / "input.csv"
        design_path = root / "design.json"
        bbs_path = root / "bbs.json"
        detail_path = root / "detail.json"
        _write(input_path, f"{_CLI_HEADER}\n{_CLI_VALID_ROW}")
        commands = [
            ["design", str(input_path), "-o", str(design_path)],
            ["bbs", str(design_path), "-o", str(bbs_path)],
            ["detail", str(design_path), "-o", str(detail_path)],
        ]
        for command in commands:
            rc, _stdout, _stderr = _capture_cli(command)
            assert rc == 0
        from structural_lib.services import dxf_export

        dxf_exercised = dxf_export.EZDXF_AVAILABLE
        if dxf_exercised:
            rc, _stdout, _stderr = _capture_cli(
                ["dxf", str(design_path), "-o", str(root / "drawing.dxf")]
            )
            assert rc == 0
        assert json.loads(design_path.read_text(encoding="utf-8"))["beams"]
        assert json.loads(bbs_path.read_text(encoding="utf-8"))["items"]
        assert json.loads(detail_path.read_text(encoding="utf-8"))["beams"]
    return {"bbs": True, "detail": True, "dxf_exercised": dxf_exercised}


def _case_complete_canonical_row() -> dict[str, Any]:
    result = design_project_beams_v1([_beam()]).to_dict()
    member = result["members"][0]
    assert member["intake_status"] == "VALID"
    assert member["calculation_status"] == "COMPLETED"
    assert member["overall_status"] in {"PASS", "FAIL"}
    return {"overall_status": member["overall_status"]}


def _case_named_adapter_alias() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "combined.csv"
        _write(
            path,
            "BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm),"
            "Mu (kN-m),Vu (kN)\nB1,300,500,5000,25,500,40,150,80",
        )
        result = parse_single_csv_lossless(path, format_hint="generic")
    assert result.status is ImportStatus.ACCEPTED and result.batch is not None
    assert all(row.status is ImportStatus.ACCEPTED for row in result.ledger.rows)
    return {"rows": result.ledger.totals.source_rows}


def _case_unknown_calculation_header() -> dict[str, Any]:
    return _assert_blocked(_beam(mystery_load_kn=10))


def _case_missing_required_value() -> dict[str, Any]:
    payload = _beam()
    payload.pop("fck_nmm2")
    return _assert_blocked(payload)


def _case_empty_required_value() -> dict[str, Any]:
    return _assert_blocked(_beam(member_id="   "))


def _case_malformed_numeric_value() -> dict[str, Any]:
    return _assert_blocked(_beam(mu_knm="not-a-number"))


def _case_non_finite_value() -> dict[str, Any]:
    return _assert_blocked(_beam(mu_knm=math.inf))


def _case_conflicting_depth_basis() -> dict[str, Any]:
    return _assert_blocked(
        _beam(
            effective_depth_basis={
                "clear_cover_mm": 40,
                "stirrup_diameter_mm": 8,
                "tension_bar_diameter_mm": 20,
            }
        )
    )


def _case_duplicate_member_identity() -> dict[str, Any]:
    result = design_project_beams_v1([_beam(), _beam()]).to_dict()
    assert result["summary"]["blocked"] == 2
    assert result["summary"]["evaluated"] == 0
    assert all(member["overall_status"] == "BLOCKED" for member in result["members"])
    return {"blocked": 2}


def _case_explicit_valid_zero() -> dict[str, Any]:
    result = design_project_beams_v1([_beam(vu_kn=0)]).to_dict()
    member = result["members"][0]
    assert member["intake_status"] == "VALID"
    assert member["calculation_status"] == "COMPLETED"
    return {"vu_kn": member["input"]["vu_kn"]}


def _case_empty_batch() -> dict[str, Any]:
    result = design_project_beams_v1([]).to_dict()
    assert result["summary"]["overall_status"] == "BLOCKED"
    assert result["summary"]["calculation_status"] == "NOT_EVALUATED"
    assert result["summary"]["passed"] == 0
    return {"overall_status": "BLOCKED"}


def _case_ambiguous_adapter() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "combined.csv"
        _write(
            path,
            "Story,Label,b (mm),D (mm),Mu (kN-m),Vu (kN)\n" "L1,B1,300,500,150,80",
        )
        result = parse_single_csv_lossless(path, format_hint="auto")
    assert result.status is ImportStatus.BLOCKED
    assert len(result.ledger.adapter_selection.candidates) > 1
    assert ImportIssueCode.AMBIGUOUS_FORMAT in {issue.code for issue in result.issues}
    return {"candidates": list(result.ledger.adapter_selection.candidates)}


def _case_invalid_import_row() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "combined.csv"
        _write(
            path,
            "BeamID,b (mm),D (mm),fck,fy,Cover (mm),Mu (kN-m),Vu (kN)\n"
            "B1,300,500,25,500,40,bad,80",
        )
        result = parse_single_csv_lossless(path, format_hint="generic")
    assert result.status is ImportStatus.BLOCKED and result.batch is None
    assert result.ledger.totals.source_rows == 1
    assert result.ledger.totals.blocked_rows == 1
    return {"blocked_rows": 1}


def _case_adapter_row_loss_guard() -> dict[str, Any]:
    from structural_lib.services import imports as import_service
    from structural_lib.services.adapters import GenericCSVAdapter

    class DroppingAdapter(GenericCSVAdapter):
        def load_forces(self, path: Path | str) -> list[BeamForces]:
            return []

    original = import_service._ADAPTER_FACTORIES["generic"]
    import_service._ADAPTER_FACTORIES["generic"] = DroppingAdapter
    try:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "combined.csv"
            _write(
                path,
                "BeamID,b (mm),D (mm),fck,fy,Cover (mm),Mu (kN-m),Vu (kN)\n"
                "B1,300,500,25,500,40,150,80",
            )
            result = parse_single_csv_lossless(path, format_hint="generic")
    finally:
        import_service._ADAPTER_FACTORIES["generic"] = original
    assert result.status is ImportStatus.BLOCKED
    assert ImportIssueCode.ADAPTER_ROW_LOSS in {issue.code for issue in result.issues}
    return {"issue": ImportIssueCode.ADAPTER_ROW_LOSS.value}


def _case_unmatched_geometry_force() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        geometry = Path(directory) / "geometry.csv"
        forces = Path(directory) / "forces.csv"
        _write(
            geometry,
            "BeamID,b (mm),D (mm),fck,fy,Cover (mm)\nB1,300,500,25,500,40",
        )
        _write(forces, "BeamID,Mu (kN-m),Vu (kN)\nB2,150,80")
        result = parse_dual_csv_lossless(
            geometry,
            forces,
            format_hint="generic",
        )
    assert result.status is ImportStatus.BLOCKED
    codes = {issue.code for issue in result.issues}
    assert ImportIssueCode.UNMATCHED_GEOMETRY in codes
    assert ImportIssueCode.UNMATCHED_FORCE in codes
    return {"unmatched": 2}


def _case_column_missing_materials() -> dict[str, Any]:
    try:
        api.design_column_is456(
            Pu_kN=1000,
            Mux_kNm=80,
            Muy_kNm=40,
            b_mm=400,
            D_mm=400,
            l_mm=3000,
            Asc_mm2=2412,
        )
    except TypeError as exc:
        assert "fck_nmm2" in str(exc)
        return {"blocked": True}
    raise AssertionError("column calculation ran without explicit materials")


def _footing_input(**updates: Any) -> ConcentricIsolatedFootingInput:
    values: dict[str, Any] = {
        "case_id": "UAT-FOOT-001",
        "service_axial_load_kN": 1000.0,
        "service_load_combination_id": "SLS-GRAVITY-01",
        "service_load_basis": "includes_footing_self_weight_and_overburden",
        "service_load_origin": "provided",
        "factored_axial_load_kN": 1500.0,
        "factored_load_combination_id": "ULS-GRAVITY-01",
        "allowable_soil_pressure_kPa": 200.0,
        "allowable_soil_pressure_source_reference": "GEO-REPORT-001",
        "allowable_soil_pressure_origin": "verified",
        "allowable_soil_pressure_is_externally_approved": True,
        "footing_type": FootingType.ISOLATED_RECTANGULAR,
        "column_L_mm": 400.0,
        "column_B_mm": 300.0,
        "minimum_overall_thickness_mm": 600.0,
        "maximum_overall_thickness_mm": 700.0,
        "thickness_increment_mm": 50.0,
        "effective_depth_offset_L_mm": 80.0,
        "effective_depth_offset_B_mm": 80.0,
        "footing_concrete_fck_nmm2": 25.0,
        "column_concrete_fck_nmm2": 25.0,
        "steel_fy_nmm2": 415.0,
        "effective_supporting_area_A1_mm2": 480000.0,
        "effective_supporting_area_basis": "largest_frustum_1v_2h",
        "effective_supporting_area_origin": "provided",
        "effective_supporting_area_is_approved": True,
        "dowel_count": 8,
        "dowel_diameter_mm": 25.0,
        "column_longitudinal_bar_diameter_mm": 25.0,
        "available_dowel_development_length_into_footing_mm": 1400.0,
        "available_dowel_development_length_into_column_mm": 1400.0,
    }
    values.update(updates)
    return ConcentricIsolatedFootingInput(**values)


def _case_assumed_footing_basis() -> dict[str, Any]:
    result = design_concentric_isolated_footing_is456(
        _footing_input(allowable_soil_pressure_origin="assumed")
    )
    assert result.status == "HOLD"
    assert (
        "ASSUMED_BASIS_REQUIRES_VERIFICATION:allowable_soil_pressure_origin"
        in result.hold_reasons
    )
    return {"status": result.status}


def _case_insufficient_footing_dowels() -> dict[str, Any]:
    result = design_concentric_isolated_footing_is456(
        _footing_input(
            available_dowel_development_length_into_footing_mm=100.0,
            available_dowel_development_length_into_column_mm=100.0,
        )
    )
    assert result.status == "FAIL"
    assert result.load_transfer.is_safe is False
    return {"status": result.status}


def _case_safe_result_review_boundary() -> dict[str, Any]:
    result = design_project_beams_v1([_beam(mu_knm=100, vu_kn=50)]).to_dict()
    member = result["members"][0]
    assert member["overall_status"] == "PASS"
    assert member["qualified_review_required"] is True
    slab = api.design_one_way_slab_is456(
        short_effective_span_mm=2500,
        long_effective_span_mm=7500,
        thickness_mm=150,
        d_mm=125,
        factored_area_load_kn_per_m2=10,
        fck_n_per_mm2=20,
        fy_n_per_mm2=415,
        main_bar_diameter_mm=10,
        main_bar_spacing_mm=250,
        distribution_bar_diameter_mm=8,
        distribution_bar_spacing_mm=250,
    )
    assert slab.detailing.qualified_review_required is True
    serialized = repr(slab.detailing).lower()
    assert "no_qualified_review_required" not in serialized
    return {"beam": "PASS", "slab_review_required": True}


_HANDLERS: dict[str, Callable[[], dict[str, Any]]] = {
    name.removeprefix("_case_"): value
    for name, value in list(globals().items())
    if name.startswith("_case_") and callable(value)
}


def _advertised_entry_points(matrix_case_ids: set[str]) -> dict[str, Any]:
    inventory_bytes = _ENTRYPOINT_RESOURCE.read_bytes()
    inventory = json.loads(inventory_bytes)
    entries = inventory["entry_points"]
    commands = [entry["command"] for entry in entries]
    assert len(commands) == len(set(commands))

    parser = cli_main._build_parser()
    command_action = next(
        action for action in parser._actions if action.dest == "command"
    )
    choices = command_action.choices
    assert isinstance(choices, dict)
    live_commands = set(choices)
    assert set(commands) == live_commands, {
        "missing_inventory_entries": sorted(live_commands - set(commands)),
        "stale_inventory_entries": sorted(set(commands) - live_commands),
    }
    allowed_classifications = {
        "calculation_entry",
        "result_consumer",
        "inspection",
        "compatibility",
        "deprecated",
        "held",
    }
    for entry in entries:
        assert entry["classification"] in allowed_classifications
        assert entry["acceptance"]
        if entry["id"] == "cli.design":
            assert set(entry["acceptance"]).issubset(matrix_case_ids)
    return {
        "schema_version": inventory["schema_version"],
        "sha256": hashlib.sha256(inventory_bytes).hexdigest(),
        "entry_count": len(entries),
        "entries": entries,
    }


def _public_examples() -> dict[str, Any]:
    beam = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="B1",
        story="GF",
        span_mm=5000,
        mu_knm=150,
        vu_kn=80,
        b_mm=300,
        D_mm=500,
        d_mm=442,
        cover_mm=40,
        fck_nmm2=25,
        fy_nmm2=500,
        d_dash_mm=58,
        asv_mm2=100,
        stirrup_dia_mm=8,
        stirrup_spacing_support_mm=150,
        stirrup_spacing_mid_mm=200,
        is_seismic=False,
    )
    batch = design_project_beams_v1([_beam()])
    assert beam.summary() and batch.summary.evaluated == 1
    return {"readme_beam": True, "python_readme_batch": True}


def run(*, require_installed_wheel: bool = False) -> dict[str, Any]:
    matrix_bytes = _MATRIX_RESOURCE.read_bytes()
    matrix = json.loads(matrix_bytes)
    matrix_cases = matrix["cases"]
    ids = [case["id"] for case in matrix_cases]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(_HANDLERS), {
        "missing_handlers": sorted(set(ids) - set(_HANDLERS)),
        "undeclared_handlers": sorted(set(_HANDLERS) - set(ids)),
    }

    package_origin = Path(structural_lib.__file__).resolve()
    if require_installed_wheel:
        purelib = Path(sysconfig.get_paths()["purelib"]).resolve()
        assert package_origin.is_relative_to(purelib), (package_origin, purelib)

    results = []
    for case in matrix_cases:
        detail = _HANDLERS[case["id"]]()
        results.append(
            {
                "id": case["id"],
                "expected": case["expected"],
                "status": "PASS",
                "detail": detail,
            }
        )

    from structural_lib.services.evidence import get_library_content_identity

    entry_points = _advertised_entry_points(set(ids))

    return {
        "schema_version": "exact-wheel-uat-receipt/v1",
        "status": "PASS",
        "package_version": structural_lib.__version__,
        "package_origin": str(package_origin),
        "library_content_identity": get_library_content_identity(),
        "matrix_schema_version": matrix["schema_version"],
        "matrix_sha256": hashlib.sha256(matrix_bytes).hexdigest(),
        "case_count": len(results),
        "cases": results,
        "advertised_entry_points": entry_points,
        "public_examples": _public_examples(),
        "qualified_review_required": True,
        "professional_approval": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-installed-wheel", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    receipt = run(require_installed_wheel=args.require_installed_wheel)
    serialized = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
