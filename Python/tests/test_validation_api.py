import json

from structural_lib import api
from structural_lib import beam_pipeline


def _write_json(path, payload):
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_job_spec_ok(tmp_path):
    job = {
        "schema_version": 1,
        "job_id": "JOB-1",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 230,
            "D_mm": 500,
            "d_mm": 450,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
        },
        "cases": [
            {"case_id": "LC1", "mu_knm": 120, "vu_kn": 80},
        ],
    }
    path = tmp_path / "job.json"
    _write_json(path, job)

    report = api.validate_job_spec(path)
    assert report.ok
    assert report.details["cases_count"] == 1


def test_validate_job_spec_missing_schema(tmp_path):
    job = {
        "job_id": "JOB-2",
        "code": "IS456",
        "units": "IS456",
        "beam": {"b_mm": 230, "D_mm": 500, "d_mm": 450, "fck_nmm2": 25, "fy_nmm2": 500},
        "cases": [{"case_id": "LC1", "mu_knm": 120, "vu_kn": 80}],
    }
    path = tmp_path / "job.json"
    _write_json(path, job)

    report = api.validate_job_spec(path)
    assert not report.ok
    assert any("schema_version" in err for err in report.errors)


def test_validate_job_spec_missing_file(tmp_path):
    report = api.validate_job_spec(tmp_path / "missing.json")
    assert not report.ok
    assert report.errors


def test_validate_job_spec_invalid_units(tmp_path):
    job = {
        "schema_version": 1,
        "job_id": "JOB-3",
        "code": "IS456",
        "units": "BAD_UNITS",
        "beam": {
            "b_mm": 230,
            "D_mm": 500,
            "d_mm": 450,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
        },
        "cases": [{"case_id": "LC1", "mu_knm": 120, "vu_kn": 80}],
    }
    path = tmp_path / "job.json"
    _write_json(path, job)

    report = api.validate_job_spec(path)
    assert not report.ok
    assert any("units validation failed" in err for err in report.errors)


def test_validate_job_spec_unsupported_schema_version(tmp_path):
    job = {
        "schema_version": 2,
        "job_id": "JOB-4",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 230,
            "D_mm": 500,
            "d_mm": 450,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
        },
        "cases": [{"case_id": "LC1", "mu_knm": 120, "vu_kn": 80}],
    }
    path = tmp_path / "job.json"
    _write_json(path, job)

    report = api.validate_job_spec(path)
    assert not report.ok
    assert any("Unsupported schema_version" in err for err in report.errors)


def test_validate_design_results_ok(tmp_path):
    results = {
        "schema_version": beam_pipeline.SCHEMA_VERSION,
        "code": "IS456",
        "units": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "S1",
                "geometry": {"b_mm": 230, "D_mm": 500, "d_mm": 450},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"mu_knm": 120, "vu_kn": 80},
            }
        ],
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert report.ok
    assert report.details["beams_count"] == 1


def test_validate_design_results_missing_loads(tmp_path):
    results = {
        "schema_version": beam_pipeline.SCHEMA_VERSION,
        "code": "IS456",
        "units": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "S1",
                "geometry": {"b_mm": 230, "D_mm": 500, "d_mm": 450},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
            }
        ],
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert not report.ok
    assert any("missing load fields" in err for err in report.errors)


def test_validate_design_results_missing_units(tmp_path):
    results = {
        "schema_version": beam_pipeline.SCHEMA_VERSION,
        "code": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "S1",
                "geometry": {"b_mm": 230, "D_mm": 500, "d_mm": 450},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"mu_knm": 120, "vu_kn": 80},
            }
        ],
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert report.ok
    assert report.warnings


def test_validate_design_results_missing_beams_list(tmp_path):
    results = {
        "schema_version": beam_pipeline.SCHEMA_VERSION,
        "code": "IS456",
        "units": "IS456",
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert not report.ok
    assert any("beams" in err for err in report.errors)


def test_validate_design_results_invalid_schema_version(tmp_path):
    results = {
        "schema_version": "bad",
        "code": "IS456",
        "units": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "S1",
                "geometry": {"b_mm": 230, "D_mm": 500, "d_mm": 450},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"mu_knm": 120, "vu_kn": 80},
            }
        ],
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert not report.ok
    assert any("Invalid schema_version" in err for err in report.errors)


def test_validate_design_results_unsupported_schema_version(tmp_path):
    results = {
        "schema_version": 999,
        "code": "IS456",
        "units": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "S1",
                "geometry": {"b_mm": 230, "D_mm": 500, "d_mm": 450},
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"mu_knm": 120, "vu_kn": 80},
            }
        ],
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert not report.ok
    assert any("Unsupported schema_version" in err for err in report.errors)


def test_validate_design_results_non_dict_beam(tmp_path):
    results = {
        "schema_version": beam_pipeline.SCHEMA_VERSION,
        "code": "IS456",
        "units": "IS456",
        "beams": ["B1"],
    }
    path = tmp_path / "results.json"
    _write_json(path, results)

    report = api.validate_design_results(path)
    assert not report.ok
    assert any("expected object" in err for err in report.errors)
