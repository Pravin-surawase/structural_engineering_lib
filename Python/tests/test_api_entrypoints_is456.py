import pytest

from structural_lib import api
from structural_lib.types import ComplianceCaseResult, ComplianceReport


def test_design_beam_is456_requires_units_param():
    with pytest.raises(TypeError):
        api.design_beam_is456(
            mu_knm=120.0,
            vu_kn=80.0,
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
        )


def test_design_beam_is456_rejects_unknown_units():
    with pytest.raises(ValueError, match="Invalid units"):
        api.design_beam_is456(
            units="kips-in",
            mu_knm=120.0,
            vu_kn=80.0,
            b_mm=300.0,
            D_mm=500.0,
            d_mm=450.0,
            fck_nmm2=25.0,
            fy_nmm2=500.0,
        )


def test_design_beam_is456_returns_case_result_and_records_pt_assumption():
    res = api.design_beam_is456(
        units="IS456",
        case_id="S1",
        mu_knm=120.0,
        vu_kn=80.0,
        b_mm=300.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        # pt_percent intentionally omitted
    )

    assert isinstance(res, ComplianceCaseResult)
    assert res.case_id == "S1"
    assert isinstance(res.utilizations, dict)

    # Deterministic behavior: if pt_percent is missing, it must be derived and recorded.
    assert "Computed pt_percent for shear" in res.remarks


def test_check_beam_is456_runs_multi_case_report():
    cases = [
        {"case_id": "C1", "mu_knm": 80.0, "vu_kn": 60.0},
        {"case_id": "C2", "mu_knm": 120.0, "vu_kn": 80.0},
    ]

    report = api.check_beam_is456(
        units="IS456",
        cases=cases,
        b_mm=300.0,
        D_mm=500.0,
        d_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    assert isinstance(report, ComplianceReport)
    assert report.governing_case_id in {"C1", "C2"}
    assert len(report.cases) == 2


def test_detail_beam_is456_wraps_detailing():
    res = api.detail_beam_is456(
        units="IS456",
        beam_id="B1",
        story="S1",
        b_mm=300.0,
        D_mm=500.0,
        span_mm=5000.0,
        cover_mm=25.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        ast_start_mm2=1200.0,
        ast_mid_mm2=900.0,
        ast_end_mm2=1200.0,
    )

    assert res.is_valid is True
    assert res.remarks
    assert len(res.top_bars) == 3
    assert len(res.bottom_bars) == 3
    assert len(res.stirrups) == 3
