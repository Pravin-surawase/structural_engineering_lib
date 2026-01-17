import json

import pytest

from structural_lib import api, detailing


@pytest.fixture
def sample_job_output_dir(tmp_path):
    inputs_dir = tmp_path / "inputs"
    design_dir = tmp_path / "design"
    inputs_dir.mkdir()
    design_dir.mkdir()

    job = {
        "schema_version": 1,
        "job_id": "TEST-001",
        "code": "IS456",
        "units": "IS456",
        "beam": {
            "b_mm": 300,
            "D_mm": 600,
            "d_mm": 550,
            "fck_nmm2": 25,
            "fy_nmm2": 500,
            "d_dash_mm": 50,
            "asv_mm2": 100,
        },
        "cases": [
            {"case_id": "C1", "mu_knm": 120, "vu_kn": 80},
            {"case_id": "C2", "mu_knm": 150, "vu_kn": 90},
        ],
    }
    results = {
        "is_ok": True,
        "governing_case_id": "C2",
        "governing_utilization": 0.85,
        "cases": [
            {
                "case_id": "C1",
                "mu_knm": 120.0,
                "vu_kn": 80.0,
                "is_ok": True,
                "governing_utilization": 0.65,
                "utilizations": {"flexure": 0.65, "shear": 0.4},
            },
            {
                "case_id": "C2",
                "mu_knm": 150.0,
                "vu_kn": 90.0,
                "is_ok": True,
                "governing_utilization": 0.85,
                "utilizations": {"flexure": 0.85, "shear": 0.5},
            },
        ],
        "summary": {"total_cases": 2, "passed": 2, "failed": 0},
    }

    (inputs_dir / "job.json").write_text(json.dumps(job, indent=2), encoding="utf-8")
    (design_dir / "design_results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )

    return tmp_path


@pytest.fixture
def sample_design_results(tmp_path):
    payload = {
        "schema_version": 1,
        "code": "IS456",
        "units": "IS456",
        "beams": [
            {
                "beam_id": "B1",
                "story": "G",
                "geometry": {
                    "b_mm": 300,
                    "D_mm": 600,
                    "d_mm": 550,
                    "span_mm": 4000,
                    "cover_mm": 40,
                },
                "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
                "loads": {"case_id": "G_B1", "mu_knm": 120, "vu_kn": 80},
                "flexure": {"ast_required_mm2": 900.0, "utilization": 0.7},
                "shear": {"is_safe": True, "utilization": 0.4},
                "serviceability": {
                    "deflection_utilization": 0.3,
                    "crack_width_utilization": 0.2,
                },
                "is_ok": True,
                "governing_utilization": 0.7,
            },
            {
                "beam_id": "B2",
                "story": "G",
                "geometry": {
                    "b_mm": 250,
                    "D_mm": 500,
                    "d_mm": 450,
                    "span_mm": 3500,
                    "cover_mm": 40,
                },
                "materials": {"fck_nmm2": 20, "fy_nmm2": 415},
                "loads": {"case_id": "G_B2", "mu_knm": 140, "vu_kn": 90},
                "flexure": {"ast_required_mm2": 1000.0, "utilization": 0.85},
                "shear": {"is_safe": True, "utilization": 0.6},
                "serviceability": {
                    "deflection_utilization": 0.4,
                    "crack_width_utilization": 0.3,
                },
                "is_ok": True,
                "governing_utilization": 0.85,
            },
        ],
        "summary": {"total_beams": 2, "passed": 2, "failed": 0},
    }

    path = tmp_path / "design_results.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload, path


@pytest.fixture
def sample_detailing_list():
    result = detailing.create_beam_detailing(
        beam_id="B1",
        story="S1",
        b=300,
        D=500,
        span=4000,
        cover=40,
        fck=25,
        fy=500,
        ast_start=900,
        ast_mid=900,
        ast_end=900,
    )
    return [result]


def test_compute_report_from_job_output(sample_job_output_dir):
    html = api.compute_report(sample_job_output_dir, format="html")
    assert "<html" in html


def test_compute_report_from_design_results_path(sample_design_results):
    _, path = sample_design_results
    output = api.compute_report(path, format="json")
    data = json.loads(output)
    assert "beams" in data


def test_compute_report_from_design_results_dict_writes_package(
    sample_design_results, tmp_path
):
    payload, _ = sample_design_results
    output = api.compute_report(payload, format="html", output_path=tmp_path / "report")
    assert isinstance(output, list)
    assert output
    assert output[0].exists()


def test_compute_critical_csv(sample_job_output_dir):
    output = api.compute_critical(sample_job_output_dir, top=1, format="csv")
    assert "case_id" in output.splitlines()[0]


def test_compute_critical_html_to_file(sample_job_output_dir, tmp_path):
    output_path = tmp_path / "critical.html"
    result = api.compute_critical(
        sample_job_output_dir,
        top=1,
        format="html",
        output_path=output_path,
    )
    assert result == output_path
    assert output_path.exists()


def test_compute_dxf_raises_when_ezdxf_missing(sample_detailing_list, monkeypatch):
    from structural_lib import dxf_export

    monkeypatch.setattr(dxf_export, "EZDXF_AVAILABLE", False)
    with pytest.raises(RuntimeError, match="ezdxf"):
        api.compute_dxf(sample_detailing_list, "out.dxf")
