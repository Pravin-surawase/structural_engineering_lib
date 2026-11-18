# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Strict Generic geometry needs a supplied span with consistent units."""

from pathlib import Path

import pytest

from structural_lib.imports import parse_dual_csv_lossless, parse_single_csv_lossless
from structural_lib.services.adapters import GenericCSVAdapter
from structural_lib.services.import_ledger import ImportStatus


def _inputs(tmp_path: Path, header: str | None, value: str):
    geometry, forces, combined = (
        tmp_path / name for name in ("geometry.csv", "forces.csv", "combined.csv")
    )
    headers = "BeamID,b (mm),D (mm),fck,fy,Cover (mm)" + (
        "," + header if header else ""
    )
    values = "B1,300,500,25,500,40" + ("," + value if header else "")
    geometry.write_text(headers + "\n" + values + "\n", encoding="utf-8")
    forces.write_text(
        "BeamID,Mu (kN-m),Vu (kN),Load Case\nB1,120,75,ULS-1\n", encoding="utf-8"
    )
    combined.write_text(
        headers + ",Mu (kN-m),Vu (kN),Load Case\n" + values + ",120,75,ULS-1\n",
        encoding="utf-8",
    )
    return geometry, forces, combined


@pytest.mark.parametrize("single", [False, True], ids=["paired", "single"])
@pytest.mark.parametrize(
    ("header", "value"),
    [
        (None, ""),
        ("Span (mm)", ""),
        ("Span (mm)", "bad"),
        ("Span (mm)", "NaN"),
        ("Span (mm)", "0"),
    ],
)
def test_strict_generic_refuses_missing_or_invalid_span(
    tmp_path: Path, single: bool, header, value
):
    geometry, forces, combined = _inputs(tmp_path, header, value)
    result = (
        parse_single_csv_lossless(combined, format_hint="generic")
        if single
        else parse_dual_csv_lossless(geometry, forces, format_hint="generic")
    )
    assert result.status is ImportStatus.BLOCKED and result.batch is None
    assert result.issues
    if header:
        field = next(
            field
            for row in result.ledger.rows
            for field in row.fields
            if field.canonical_field == "span_mm"
        )
        assert field.raw_value == value


@pytest.mark.parametrize("single", [False, True], ids=["paired", "single"])
@pytest.mark.parametrize(
    ("header", "value"), [("Span (mm)", "4200"), ("Span_m", "4.2")]
)
def test_generic_span_units_agree_in_ledger_and_geometry(
    tmp_path: Path, single: bool, header: str, value: str
):
    geometry, forces, combined = _inputs(tmp_path, header, value)
    result = (
        parse_single_csv_lossless(combined, format_hint="generic")
        if single
        else parse_dual_csv_lossless(geometry, forces, format_hint="generic")
    )
    assert result.status is ImportStatus.ACCEPTED and result.batch is not None
    assert result.batch.beams[0].length_m == pytest.approx(4.2)
    field = next(
        field
        for row in result.ledger.rows
        for field in row.fields
        if field.canonical_field == "span_mm"
    )
    assert field.raw_value == value
    assert field.parsed_value == pytest.approx(4200)
    assert field.units == "mm"


@pytest.mark.parametrize("value", ["", "bad", "NaN", "0"])
def test_direct_generic_rejects_invalid_supplied_span(tmp_path: Path, value: str):
    geometry, _, _ = _inputs(tmp_path, "Span (mm)", value)
    with pytest.raises(ValueError, match="CSV row 2"):
        GenericCSVAdapter().load_geometry(geometry)


def test_direct_generic_legacy_placeholder_is_explicitly_bounded(tmp_path: Path):
    geometry, _, _ = _inputs(tmp_path, None, "")
    assert GenericCSVAdapter().load_geometry(geometry)[0].length_m == 5
