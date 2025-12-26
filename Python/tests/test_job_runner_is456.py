import json
from pathlib import Path

import pytest

from structural_lib import api
from structural_lib import job_runner


def _write_job(path: Path, job: dict) -> None:
    path.write_text(json.dumps(job, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_job_runner_writes_expected_outputs(tmp_path: Path):
    job = {
        "schema_version": 1,
        "job_id": "job_test_001",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "d_dash_mm": 50.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "asv_mm2": 100.0,
            "pt_percent": None,
        },
        "cases": [
            {"case_id": "C1", "mu_knm": 80.0, "vu_kn": 60.0},
            {"case_id": "C2", "mu_knm": 120.0, "vu_kn": 200.0},
        ],
    }

    job_path = tmp_path / "job.json"
    out_dir = tmp_path / "out"
    _write_job(job_path, job)

    summary = job_runner.run_job(job_path=job_path, out_dir=out_dir)
    assert summary["job_id"] == "job_test_001"
    assert summary["num_cases"] == 2

    # Folder layout
    assert (out_dir / "inputs" / "job.json").exists()
    assert (out_dir / "parsed" / "beam.json").exists()
    assert (out_dir / "parsed" / "cases.json").exists()
    assert (out_dir / "design" / "design_results.json").exists()
    assert (out_dir / "design" / "compliance_summary.csv").exists()
    assert (out_dir / "deliverables").is_dir()
    assert (out_dir / "logs").is_dir()

    # design_results.json should match the engine output (core truth)
    expected_report = api.check_beam_is456(
        units="IS456",
        cases=job["cases"],
        b_mm=job["beam"]["b_mm"],
        D_mm=job["beam"]["D_mm"],
        d_mm=job["beam"]["d_mm"],
        fck_nmm2=job["beam"]["fck_nmm2"],
        fy_nmm2=job["beam"]["fy_nmm2"],
        d_dash_mm=job["beam"]["d_dash_mm"],
        asv_mm2=job["beam"]["asv_mm2"],
    )

    payload = json.loads(
        (out_dir / "design" / "design_results.json").read_text(encoding="utf-8")
    )
    assert payload["summary"] == expected_report.summary
    assert payload["job"]["job_id"] == "job_test_001"


def test_job_runner_is_deterministic_for_same_inputs(tmp_path: Path):
    job = {
        "schema_version": 1,
        "job_id": "job_test_002",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "d_mm": 450.0,
            "d_dash_mm": 50.0,
            "fck_nmm2": 25.0,
            "fy_nmm2": 500.0,
            "asv_mm2": 100.0,
            "pt_percent": None,
        },
        "cases": [
            {"case_id": "C1", "mu_knm": 80.0, "vu_kn": 60.0},
            {"case_id": "C2", "mu_knm": 120.0, "vu_kn": 200.0},
        ],
    }

    job_path = tmp_path / "job.json"
    _write_job(job_path, job)

    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"

    job_runner.run_job(job_path=job_path, out_dir=out1)
    job_runner.run_job(job_path=job_path, out_dir=out2)

    p1 = (out1 / "design" / "design_results.json").read_text(encoding="utf-8")
    p2 = (out2 / "design" / "design_results.json").read_text(encoding="utf-8")
    assert p1 == p2

    c1 = (out1 / "design" / "compliance_summary.csv").read_text(encoding="utf-8")
    c2 = (out2 / "design" / "compliance_summary.csv").read_text(encoding="utf-8")
    assert c1 == c2


def test_job_runner_rejects_unknown_code(tmp_path: Path):
    job = {
        "schema_version": 1,
        "job_id": "job_test_003",
        "code": "ACI318",
        "units": "ACI",
        "beam": {},
        "cases": [],
    }
    job_path = tmp_path / "job.json"
    _write_job(job_path, job)

    with pytest.raises(ValueError, match="Unsupported code"):
        job_runner.run_job(job_path=job_path, out_dir=tmp_path / "out")


# ============================================================================
# Q-013: Edge cases for malformed JSON
# ============================================================================


def test_job_runner_rejects_missing_job_id(tmp_path: Path):
    """Q-013: Missing job_id should raise ValueError."""
    job = {
        "schema_version": 1,
        "code": "IS456",
        "units": "IS456",
        # job_id missing
        "beam": {"b_mm": 230},
        "cases": [],
    }
    job_path = tmp_path / "job.json"
    _write_job(job_path, job)

    with pytest.raises(ValueError, match="job_id"):
        job_runner.run_job(job_path=job_path, out_dir=tmp_path / "out")


def test_job_runner_rejects_beam_not_dict(tmp_path: Path):
    """Q-013: beam must be a dict."""
    job = {
        "schema_version": 1,
        "code": "IS456",
        "units": "IS456",
        "job_id": "test",
        "beam": "not_a_dict",
        "cases": [],
    }
    job_path = tmp_path / "job.json"
    _write_job(job_path, job)

    with pytest.raises(ValueError, match="beam must be an object"):
        job_runner.run_job(job_path=job_path, out_dir=tmp_path / "out")


def test_job_runner_rejects_cases_not_list(tmp_path: Path):
    """Q-013: cases must be a list."""
    job = {
        "schema_version": 1,
        "code": "IS456",
        "units": "IS456",
        "job_id": "test",
        "beam": {"b_mm": 230},
        "cases": "not_a_list",
    }
    job_path = tmp_path / "job.json"
    _write_job(job_path, job)

    with pytest.raises(ValueError, match="cases must be an array"):
        job_runner.run_job(job_path=job_path, out_dir=tmp_path / "out")
