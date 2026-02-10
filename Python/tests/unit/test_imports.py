# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for structural_lib.imports helpers."""

from __future__ import annotations

from pathlib import Path

from structural_lib.services.imports import parse_dual_csv, validate_import


def _write_csv(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def test_parse_dual_csv_generic(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"

    _write_csv(
        geometry_csv,
        """
BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm)
B1,300,500,5000,25,500,40
B2,300,450,4500,25,500,40
""",
    )

    _write_csv(
        forces_csv,
        """
BeamID,Mu (kN-m),Vu (kN),Load Case
B1,150,80,1.5(DL+LL)
B2,120,60,1.5(DL+LL)
""",
    )

    batch, warnings = parse_dual_csv(geometry_csv, forces_csv, format_hint="generic")

    assert len(batch.beams) == 2
    assert len(batch.forces) == 2
    assert warnings.warnings == []

    report = validate_import(batch)
    assert report.ok is True
    assert report.details.get("matched") == 2


def test_parse_dual_csv_unmatched_warns(tmp_path: Path) -> None:
    geometry_csv = tmp_path / "geometry.csv"
    forces_csv = tmp_path / "forces.csv"

    _write_csv(
        geometry_csv,
        """
BeamID,b (mm),D (mm),Span (mm),fck,fy,Cover (mm)
B1,300,500,5000,25,500,40
B2,300,450,4500,25,500,40
""",
    )

    _write_csv(
        forces_csv,
        """
BeamID,Mu (kN-m),Vu (kN)
B1,150,80
""",
    )

    batch, warnings = parse_dual_csv(geometry_csv, forces_csv, format_hint="generic")

    assert len(batch.beams) == 2
    assert len(batch.forces) == 1
    assert warnings.unmatched_beams == ["B2"]
    assert "beams have no matching forces" in " ".join(warnings.warnings)

    report = validate_import(batch)
    assert report.ok is True
    assert report.details.get("matched") == 1
    assert report.warnings
