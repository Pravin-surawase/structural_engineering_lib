"""Verify the public beam section example against the independent freeze."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path


def test_beam_example_matches_frozen_section_targets(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    example = root / "Python/examples/beam_comparator_reference.py"
    reference = json.loads(
        (root / "docs/verification/library-027-comparator-reference.json").read_text(
            encoding="utf-8"
        )
    )
    tolerances = reference["acceptance"]["absolute_tolerances"]
    expected = {
        case["id"]: case["expected"]["structlib"]
        for case in reference["cases"]
        if "structlib" in case["expected"]
    }
    completed = subprocess.run(
        [sys.executable, str(example)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    actual = json.loads(completed.stdout)
    assert actual.keys() == expected.keys()
    assert len(expected) == 3
    for case_id, targets in expected.items():
        row = actual[case_id]
        assert row.keys() == targets.keys() | {"method_revision_ids"}
        assert len(targets) == 7
        assert row["method_revision_ids"] == {
            "flexure": "is456-flexural-capacity-wp01-v3",
            "shear": "is456-shear-capacity-wp02-v1",
        }
        for name, target in targets.items():
            assert math.isclose(
                row[name], target, abs_tol=tolerances[name], rel_tol=0
            ), (case_id, name, row[name], target, tolerances[name])
