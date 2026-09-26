"""Run the advertised caller against real member/BBS/quantity operations."""

import json
import subprocess
import sys
from pathlib import Path


def test_candidate_example_excludes_failed_and_stale_evidence(tmp_path: Path) -> None:
    example = (
        Path(__file__).resolve().parents[2]
        / "examples"
        / "candidate_ranking_workflow.py"
    )
    result = subprocess.run(
        [sys.executable, str(example)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    output = json.loads(result.stdout)
    states = {item["diameter_mm"]: item["engineering"] for item in output["candidates"]}
    assert states == {12: "fail", 20: "pass", 25: "pass"}
    assert output["selected_diameter_mm"] == 20
    assert all(item["scheduled_links"] == 40 for item in output["candidates"])
    assert output["complete"] == "complete_enumeration"
    assert output["budget_limited"] == "budget_exhausted_incomplete"
    assert output["stale"] == "evidence_incomplete"
    assert output["partial_or_stale_optimum_claimed"] is False


def test_beam_checks_example_executes_its_declared_checks(tmp_path: Path) -> None:
    example = (
        Path(__file__).resolve().parents[2] / "examples" / "beam_checks_workflow.py"
    )
    result = subprocess.run(
        [sys.executable, str(example)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    output = json.loads(result.stdout)
    assert output["analysis"]["engineering"] == "not_evaluated"
    assert output["missing_history"]["diagnostics"] == ["EVIDENCE.REQUIRED"]
    assert output["continuity"]["engineering"] == "pass"


def test_snapshot_example_replays_and_rejects_modified_evidence(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[3]
    fixture = json.loads(
        (
            root / "contracts/structural-engineering/conformance/wp10-vectors.json"
        ).read_text(encoding="utf-8")
    )
    document = fixture["valid_snapshot"]
    source = tmp_path / "snapshot.json"
    source.write_text(json.dumps(document), encoding="utf-8")
    example = root / "Python/examples/analysis_snapshot_replay.py"
    valid = subprocess.run(
        [sys.executable, str(example), str(source)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    output = json.loads(valid.stdout)
    assert output["snapshot"]["canonical_round_trip"] is True
    assert output["engineering"] == "not_evaluated"
    document["snapshot_sha256"] = "0" * 64
    source.write_text(json.dumps(document), encoding="utf-8")
    invalid = subprocess.run(
        [sys.executable, str(example), str(source)],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )
    assert invalid.returncode == 2
    assert "snapshot" not in json.loads(invalid.stdout)
