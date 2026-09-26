# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Keep source effective depth intact through accepted CSV design workflows."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from structural_lib.core.models import SectionProperties
from structural_lib.services import api
from structural_lib.services.adapters import GenericCSVAdapter
from structural_lib.services.cli_design import load_cli_design_input_v1
from structural_lib.services.imports import (
    parse_dual_csv_lossless,
    parse_single_csv_lossless,
)


def _schedule(
    path: Path, *, overall: str = "D_mm", effective: str = "d_mm", depth: str = "470"
) -> Path:
    path.write_text(
        f"beam_id,story,b_mm,{overall},{effective},span_mm,fck,fy,cover_mm,mu_knm,vu_kn,"
        "stirrup_diameter_mm,stirrup_spacing_mm\n"
        f"B1,GF,300,500,{depth},6000,25,500,40,100,70,8,100\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.parametrize(
    "overall,effective",
    [
        ("D_mm", "d_mm"),
        ("D (mm)", "d (mm)"),
        ("D", "d"),
        ("D_mm", "eff_d"),
        ("Depth", "effective_depth_mm"),
    ],
)
def test_source_depth_survives_import_and_matches_direct_design(
    tmp_path, overall, effective
):
    path = _schedule(tmp_path / "beams.csv", overall=overall, effective=effective)
    imported = parse_single_csv_lossless(path, format_hint="generic")
    assert imported.batch is not None, imported.issues
    assert not imported.issues
    section = imported.batch.beams[0].section
    assert section.depth_mm == 500
    assert section.d_mm == section.effective_depth_mm == 470
    ledger_depth = next(
        field
        for field in imported.ledger.rows[0].fields
        if field.canonical_field == "eff_depth_mm"
    )
    assert ledger_depth.parsed_value == section.d_mm
    force = imported.batch.forces[0]
    actual = api.design_beam_is456(
        units="IS456",
        b_mm=section.width_mm,
        D_mm=section.depth_mm,
        d_mm=section.effective_depth_mm,
        fck_nmm2=section.fck_mpa,
        fy_nmm2=section.fy_mpa,
        mu_knm=force.mu_knm,
        vu_kn=force.vu_kn,
    )
    expected = api.design_beam_is456(
        units="IS456",
        b_mm=300,
        D_mm=500,
        d_mm=470,
        fck_nmm2=25,
        fy_nmm2=500,
        mu_knm=100,
        vu_kn=70,
    )
    assert actual.is_ok == expected.is_ok
    assert actual.flexure.Ast_required == pytest.approx(expected.flexure.Ast_required)
    assert actual.shear.spacing == expected.shear.spacing
    intake = load_cli_design_input_v1(path)
    assert intake.records[0].d == intake.records[0].project_payload["d_mm"] == 470


def test_dual_csv_and_section_json_preserve_explicit_depth(tmp_path):
    geometry = tmp_path / "geometry.csv"
    geometry.write_text(
        "beam_id,b_mm,D_mm,d_mm,fck,fy,cover_mm\nB1,300,500,470,25,500,40\n",
        encoding="utf-8",
    )
    forces = tmp_path / "forces.csv"
    forces.write_text("beam_id,mu_knm,vu_kn\nB1,100,70\n", encoding="utf-8")
    result = parse_dual_csv_lossless(geometry, forces, format_hint="generic")
    assert result.batch is not None, result.issues
    section = result.batch.beams[0].section
    restored = SectionProperties.model_validate_json(
        section.model_dump_json(exclude={"effective_depth_mm"})
    )
    assert restored.d_mm == restored.effective_depth_mm == 470


def test_absent_explicit_depth_keeps_existing_derived_basis(tmp_path):
    path = tmp_path / "geometry.csv"
    path.write_text("beam_id,b_mm,D_mm\nB1,300,500\n", encoding="utf-8")
    section = GenericCSVAdapter().load_geometry(path)[0].section
    assert section.d_mm is None
    assert section.effective_depth_mm == 442


@pytest.mark.parametrize("depth", ["0", "-1", "500", "600", "nan", "inf", "bad-depth"])
def test_invalid_depth_blocks_whole_import_with_row_context(tmp_path, depth):
    path = _schedule(tmp_path / "beams.csv")
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"B2,GF,300,500,{depth},6000,25,500,40,100,70,8,100\n")
    with pytest.raises(ValueError, match="CSV row 3"):
        GenericCSVAdapter().load_geometry(path)
    result = parse_single_csv_lossless(path, format_hint="generic")
    assert result.batch is None
    assert result.status.value == "BLOCKED"
    assert result.issues


@pytest.mark.parametrize("depth", [0, -1, 500, float("nan"), float("inf")])
def test_explicit_section_depth_contract(depth):
    with pytest.raises(ValidationError):
        SectionProperties(width_mm=300, depth_mm=500, d_mm=depth)


@pytest.mark.parametrize("duplicate", ["d_mm", "effective_depth_mm", "D_MM"])
def test_duplicate_or_conflicting_depth_headers_still_block(tmp_path, duplicate):
    path = _schedule(tmp_path / "beams.csv")
    header, values = path.read_text(encoding="utf-8").splitlines()
    path.write_text(f"{header},{duplicate}\n{values},470\n", encoding="utf-8")
    result = parse_single_csv_lossless(path, format_hint="generic")
    assert result.batch is None
    assert any("header" in issue.code.value for issue in result.issues)
