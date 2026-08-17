"""Focused safety and parity vectors for Excel Routine Workbench V1."""

from __future__ import annotations

import json

from structural_lib.__main__ import main
from structural_lib.core.excel_workbook import (
    ExcelFreshnessRequestV1,
    ExcelWorkbookPreviewRequestV1,
    ExcelWorkbookRunRequestV1,
    ExcelWorkbookSelectionV1,
)
from structural_lib.services.beam_api import design_beam_is456
from structural_lib.services.excel_workbench import (
    build_excel_mapping_preview_v1,
    check_excel_workbook_freshness_v1,
    get_excel_workbench_definition_v1,
    render_excel_review_bundle_markdown_v1,
    retain_excel_workbook_evidence_v1,
    run_excel_workbook_v1,
)
from structural_lib.services.project_beam import EffectiveDepthBasisV1
from structural_lib.services.serialization import to_transport_value

HEADERS = (
    "Row ID",
    "Beam ID",
    "Case ID",
    "Mu (kN·m)",
    "Vu (kN)",
    "b (mm)",
    "D (mm)",
    "Depth Basis",
    "d (mm)",
    "Clear Cover (mm)",
    "Stirrup Dia (mm)",
    "Tension Bar Dia (mm)",
    "d' (mm)",
    "Asv (mm²)",
    "fck (N/mm²)",
    "fy (N/mm²)",
    "Shear Basis",
)


def _selection() -> ExcelWorkbookSelectionV1:
    return ExcelWorkbookSelectionV1(
        workbook_instance_id="WORKBOOK-001",
        first_data_row_number=2,
        locale="en-IN",
        calculation_mode="AUTOMATIC",
    )


def _derived_row(
    *, row_id: str = "R1", beam_id: str = "B1", vu_kn: float = 100.0
) -> tuple[object, ...]:
    return (
        row_id,
        beam_id,
        "ULS-1",
        150.0,
        vu_kn,
        300.0,
        500.0,
        "DERIVED_FROM_BARS",
        None,
        40.0,
        8.0,
        18.0,
        None,
        100.0,
        25.0,
        500.0,
        "AUTO_FROM_FLEXURE",
    )


def _explicit_row(*, row_id: str = "R2", beam_id: str = "B2") -> tuple[object, ...]:
    return (
        row_id,
        beam_id,
        "ULS-2",
        150.0,
        420.0,
        300.0,
        500.0,
        "EXPLICIT_D",
        443.0,
        None,
        8.0,
        None,
        57.0,
        100.0,
        25.0,
        500.0,
        "AUTO_FROM_FLEXURE",
    )


def _preview_request(
    rows: tuple[tuple[object, ...], ...], headers: tuple[str, ...] = HEADERS
) -> ExcelWorkbookPreviewRequestV1:
    return ExcelWorkbookPreviewRequestV1(
        selection=_selection(),
        headers=headers,
        rows=rows,
    )


def _run_request(
    rows: tuple[tuple[object, ...], ...], headers: tuple[str, ...] = HEADERS
) -> ExcelWorkbookRunRequestV1:
    preview_request = _preview_request(rows, headers)
    preview = build_excel_mapping_preview_v1(preview_request)
    return ExcelWorkbookRunRequestV1(
        selection=preview_request.selection,
        headers=headers,
        rows=rows,
        confirmed_mapping_hash=preview.mapping_hash,
    )


def test_mapping_preview_is_explicit_and_hash_bound() -> None:
    request = _preview_request((_derived_row(),))
    preview = build_excel_mapping_preview_v1(request)

    assert preview.is_blocked is False
    assert len(preview.mapped_fields) == len(HEADERS)
    assert preview.excluded_headers == ()
    assert len(preview.mapping_hash) == 64
    assert {item.canonical_field for item in preview.mapped_fields} == {
        "row_id",
        "beam_id",
        "case_id",
        "mu_knm",
        "vu_kn",
        "b_mm",
        "D_mm",
        "depth_basis_mode",
        "d_mm",
        "clear_cover_mm",
        "stirrup_dia_mm",
        "tension_bar_dia_mm",
        "d_dash_mm",
        "asv_mm2",
        "fck_nmm2",
        "fy_nmm2",
        "shear_basis_mode",
    }


def test_mapping_preview_blocks_missing_and_duplicate_fields() -> None:
    headers = tuple(item for item in HEADERS if item != "Beam ID") + ("Row ID",)
    preview = build_excel_mapping_preview_v1(
        _preview_request((_derived_row(),), headers)
    )

    assert preview.is_blocked is True
    assert {item.code for item in preview.issues} >= {
        "E_EXCEL_HEADER_DUPLICATE",
        "E_EXCEL_MAPPING_DUPLICATE",
        "E_EXCEL_MAPPING_REQUIRED",
    }


def test_run_reconciles_every_source_row_without_defaults_or_drops() -> None:
    invalid = list(_derived_row(row_id="R3", beam_id="B3"))
    invalid[5] = "300"
    rows = (
        _derived_row(),
        _explicit_row(),
        tuple(invalid),
        tuple(None for _ in HEADERS),
    )
    result = run_excel_workbook_v1(_run_request(rows))

    assert result.counts.model_dump() == {
        "source_rows": 4,
        "accepted_rows": 2,
        "blocked_rows": 1,
        "excluded_rows": 1,
    }
    assert [item.disposition.value for item in result.row_ledger] == [
        "ACCEPTED",
        "ACCEPTED",
        "BLOCKED",
        "EXCLUDED",
    ]
    assert result.row_ledger[2].result_envelope["overall_status"] == "BLOCKED"
    assert result.row_ledger[3].issues[0].code == "I_EXCEL_BLANK_SOURCE_ROW"


def test_excel_result_matches_direct_canonical_beam_pass_and_fail() -> None:
    result = run_excel_workbook_v1(_run_request((_derived_row(), _explicit_row())))
    basis = EffectiveDepthBasisV1(
        clear_cover_mm=40.0,
        stirrup_diameter_mm=8.0,
        tension_bar_diameter_mm=18.0,
    )
    direct_pass = to_transport_value(
        design_beam_is456(
            units="IS456",
            case_id="ULS-1",
            mu_knm=150.0,
            vu_kn=100.0,
            b_mm=300.0,
            D_mm=500.0,
            d_mm=None,
            effective_depth_basis=basis,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
            asv_mm2=100.0,
            stirrup_dia_mm=8.0,
        )
    )
    direct_fail = to_transport_value(
        design_beam_is456(
            units="IS456",
            case_id="ULS-2",
            mu_knm=150.0,
            vu_kn=420.0,
            b_mm=300.0,
            D_mm=500.0,
            d_mm=443.0,
            d_dash_mm=57.0,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
            asv_mm2=100.0,
            stirrup_dia_mm=8.0,
        )
    )

    assert result.row_ledger[0].result == direct_pass
    assert result.row_ledger[1].result == direct_fail
    assert result.row_ledger[0].result_envelope["overall_status"] == "PASS"
    assert result.row_ledger[1].result_envelope["overall_status"] == "FAIL"


def test_mapping_must_be_reviewed_again_after_header_change() -> None:
    request = _run_request((_derived_row(),))
    changed = request.model_copy(
        update={"headers": HEADERS[:-1] + ("Shear Basis Renamed",)}
    )

    try:
        run_excel_workbook_v1(changed)
    except ValueError as exc:
        assert "mapping preview is blocked" in str(exc)
    else:  # pragma: no cover - assertion guard
        raise AssertionError("Changed mapping unexpectedly calculated")


def test_duplicate_row_ids_block_every_duplicate() -> None:
    result = run_excel_workbook_v1(
        _run_request((_derived_row(), _explicit_row(row_id="R1")))
    )

    assert result.counts.blocked_rows == 2
    assert all(
        "E_EXCEL_ROW_ID_DUPLICATE" in {issue.code for issue in item.issues}
        for item in result.row_ledger
    )


def test_populated_held_scope_column_is_visible_and_blocked() -> None:
    headers = HEADERS + ("Torsion",)
    result = run_excel_workbook_v1(_run_request((_derived_row() + (5.0,),), headers))

    assert result.counts.blocked_rows == 1
    assert result.mapping.excluded_headers == ("Torsion",)
    assert result.row_ledger[0].issues[0].code == "E_EXCEL_UNSUPPORTED_E1_SCOPE"
    assert result.row_ledger[0].result_envelope["overall_status"] == "HOLD"


def test_freshness_changes_immediately_after_input_edit() -> None:
    original_request = _preview_request((_derived_row(),))
    result = run_excel_workbook_v1(_run_request(original_request.rows))
    retained = retain_excel_workbook_evidence_v1(result)
    current = check_excel_workbook_freshness_v1(
        ExcelFreshnessRequestV1(
            previous_evidence=retained,
            current_request=original_request,
        )
    )
    edited = list(_derived_row())
    edited[3] = 151.0
    stale = check_excel_workbook_freshness_v1(
        ExcelFreshnessRequestV1(
            previous_evidence=retained,
            current_request=_preview_request((tuple(edited),)),
        )
    )

    assert current.freshness_status == "CURRENT"
    assert current.reasons == ()
    assert stale.freshness_status == "STALE"
    assert stale.reasons == ("SOURCE_TABLE_CHANGED",)


def test_run_and_review_bundle_are_deterministic() -> None:
    request = _run_request((_derived_row(), _explicit_row()))
    first = run_excel_workbook_v1(request)
    second = run_excel_workbook_v1(request)

    assert first == second
    assert first.bundle_hash == second.bundle_hash
    assert first.row_ledger[0].passport == second.row_ledger[0].passport
    assert first.bundle_hash in render_excel_review_bundle_markdown_v1(first)


def test_definition_does_not_claim_real_windows_excel_evidence() -> None:
    definition = get_excel_workbench_definition_v1()

    assert definition.software_capability == "AVAILABLE"
    assert definition.installed_windows_excel_evidence == "TO_VERIFY_WINDOWS"
    assert definition.workbook_artifact_name.endswith("-v1.xlsx")
    assert len(definition.workbook_artifact_sha256) == 64
    assert definition.workbook_artifact_size_bytes > 0
    assert definition.library_version
    assert len(definition.library_content_identity) == 64
    assert definition.canonical_function == "design_beam_is456"
    assert "ETABS acquisition or write-back" in definition.held_scopes


def test_cli_requires_preview_hash_and_matches_python_result(tmp_path) -> None:
    definition_path = tmp_path / "definition.json"
    assert main(["excel-v1", "definition", "-o", str(definition_path)]) == 0
    definition = json.loads(definition_path.read_text(encoding="utf-8"))
    assert definition["installed_windows_excel_evidence"] == "TO_VERIFY_WINDOWS"
    assert len(definition["workbook_artifact_sha256"]) == 64

    preview_request = _preview_request((_derived_row(),))
    input_path = tmp_path / "excel-request.json"
    preview_path = tmp_path / "preview.json"
    result_path = tmp_path / "result.json"
    input_path.write_text(preview_request.model_dump_json(indent=2), encoding="utf-8")

    assert main(["excel-v1", "preview", str(input_path), "-o", str(preview_path)]) == 0
    preview = json.loads(preview_path.read_text(encoding="utf-8"))
    assert preview["is_blocked"] is False
    assert (
        main(
            [
                "excel-v1",
                "run",
                str(input_path),
                "--mapping-hash",
                preview["mapping_hash"],
                "-o",
                str(result_path),
            ]
        )
        == 0
    )
    cli_result = json.loads(result_path.read_text(encoding="utf-8"))
    python_result = run_excel_workbook_v1(_run_request(preview_request.rows))
    assert cli_result == python_result.model_dump(mode="json")
