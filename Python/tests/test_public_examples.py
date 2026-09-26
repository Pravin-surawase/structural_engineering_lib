"""Regression checks for repository examples advertised to external users."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


def test_canonical_workflows_use_public_types_and_complete_user_journeys(
    tmp_path: Path,
) -> None:
    script = Path(__file__).resolve().parents[1] / "examples" / "canonical_workflows.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["beam_bbs_weight_kg"] > 0
    assert result["column_status"] == result["slab_status"] == "PASS"
    assert result["column_check_passed"] is True
    assert result["review_required"] is True
    assert result["rejected_fields"] == ["geometry.b_mm"]
    assert not list(tmp_path.iterdir())


def test_synthetic_pipeline_uses_strict_cli_contract(tmp_path: Path) -> None:
    python_root = Path(__file__).resolve().parents[1]
    script = python_root / "examples" / "full_pipeline_synthetic.py"
    output_dir = tmp_path / "synthetic"

    completed = subprocess.run(
        [
            sys.executable,
            str(script),
            "--count",
            "3",
            "--skip-dxf",
            "--output-dir",
            str(output_dir),
        ],
        cwd=python_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert (output_dir / "results.json").is_file()
    assert (output_dir / "schedule.csv").is_file()

    with (output_dir / "beams_synthetic_3.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 3
    assert "eff_d" in rows[0]
    assert "Ast_req" not in rows[0]
    assert "Asc_req" not in rows[0]
