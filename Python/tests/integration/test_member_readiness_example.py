"""Exercise the public example through source and clean installed-package runs."""

import gzip
import json
import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "contracts/structural-engineering/conformance/beam-readiness-v1.gz"
EXAMPLE = ROOT / "Python/examples/member_readiness_workflow.py"


def test_stored_ready_members_are_inspected_without_currentness(capsys) -> None:
    main = runpy.run_path(str(EXAMPLE))["main"]
    assert main([str(FIXTURE)]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["requested_member_count"] == len(report["members"]) == 3
    assert all(x["recorded_ready_for_selected_profile"] for x in report["members"])
    assert report["freshness"] == "unbound"
    assert (report["engineering"], report["approval"]) == (
        "not_evaluated",
        "unreviewed",
    )
    assert "HOLD" in report["source_qualification"]


def test_explicit_current_bindings_and_changed_ledger(tmp_path, capsys) -> None:
    main = runpy.run_path(str(EXAMPLE))["main"]
    raw = json.loads(gzip.decompress(FIXTURE.read_bytes()))
    snapshot = tmp_path / "current-snapshot.json"
    snapshot.write_text(json.dumps(raw["request"]["snapshot"]), encoding="utf-8")
    arguments = [
        str(FIXTURE),
        "--current-snapshot",
        str(snapshot),
        "--current-request-id",
        raw["request_id"],
        "--current-engine-identity",
        raw["engine_identity"],
        "--current-ledger-revision",
        raw["ledger"]["revision"],
    ]
    assert main(arguments) == 0
    assert json.loads(capsys.readouterr().out)["freshness"] == "current"
    arguments[-1] = "changed-ledger"
    assert main(arguments) == 2
    assert json.loads(capsys.readouterr().out)["freshness"] == "stale"


def test_altered_evidence_and_partial_bindings_block_the_example(
    tmp_path, capsys
) -> None:
    main = runpy.run_path(str(EXAMPLE))["main"]
    raw = json.loads(gzip.decompress(FIXTURE.read_bytes()))
    raw["approval"] = "approved"
    altered = tmp_path / "altered.json"
    altered.write_text(json.dumps(raw), encoding="utf-8")
    assert main([str(altered)]) == 1
    output = capsys.readouterr()
    assert output.out == ""
    assert "Readiness input rejected" in output.err
    with pytest.raises(SystemExit) as failure:
        main([str(FIXTURE), "--current-ledger-revision", "one-field-only"])
    assert failure.value.code == 2
