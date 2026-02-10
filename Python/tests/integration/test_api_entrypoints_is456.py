import pytest

from structural_lib import api
from structural_lib.core.types import ComplianceCaseResult, ComplianceReport


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


def test_design_beam_is456_converts_vu_kn_to_tv_nmm2():
    res = api.design_beam_is456(
        units="IS456",
        case_id="C-TV",
        mu_knm=50.0,
        vu_kn=80.0,
        b_mm=200.0,
        D_mm=450.0,
        d_mm=400.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
        pt_percent=1.0,
        asv_mm2=100.0,
    )

    assert res.shear.tv == pytest.approx(1.0, rel=0.0, abs=1e-6)


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


# =============================================================================
# Tests for design_and_detail_beam_is456 (convenience function)
# =============================================================================


def test_design_and_detail_beam_is456_combines_design_and_detailing():
    """Test that the combined function produces both design and detailing."""
    result = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="B1",
        story="GF",
        span_mm=5000.0,
        mu_knm=150.0,
        vu_kn=80.0,
        b_mm=300.0,
        D_mm=500.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    # Check design result is present
    assert result.design is not None
    assert hasattr(result.design, "flexure")
    assert hasattr(result.design, "shear")
    assert result.design.flexure.ast_required > 0

    # Check detailing result is present
    assert result.detailing is not None
    assert len(result.detailing.top_bars) == 3
    assert len(result.detailing.bottom_bars) == 3
    assert len(result.detailing.stirrups) == 3

    # Check combined status
    assert result.is_ok is True
    assert result.beam_id == "B1"
    assert result.story == "GF"


def test_design_and_detail_beam_is456_summary():
    """Test that the summary method produces valid output."""
    result = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="FB-101",
        story="1F",
        span_mm=6000.0,
        mu_knm=200.0,
        vu_kn=100.0,
        b_mm=350.0,
        D_mm=600.0,
        fck_nmm2=30.0,
        fy_nmm2=500.0,
    )

    summary = result.summary()
    assert "FB-101@1F" in summary
    assert "350×600mm" in summary
    assert "Ast=" in summary


def test_design_and_detail_beam_is456_to_dict():
    """Test that to_dict produces serializable dictionary."""
    result = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="B2",
        story="GF",
        span_mm=4000.0,
        mu_knm=100.0,
        vu_kn=60.0,
        b_mm=250.0,
        D_mm=450.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    data = result.to_dict()
    assert isinstance(data, dict)
    assert data["beam_id"] == "B2"
    assert data["story"] == "GF"
    assert "design" in data
    assert "detailing" in data
    assert "geometry" in data
    assert data["geometry"]["b_mm"] == 250.0
    assert data["geometry"]["D_mm"] == 450.0


def test_design_and_detail_beam_is456_to_json():
    """Test that to_json produces valid JSON string."""
    import json

    result = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="B3",
        story="GF",
        span_mm=4000.0,
        mu_knm=80.0,
        vu_kn=50.0,
        b_mm=230.0,
        D_mm=400.0,
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    json_str = result.to_json()
    assert isinstance(json_str, str)

    # Should be valid JSON
    parsed = json.loads(json_str)
    assert parsed["beam_id"] == "B3"


def test_design_and_detail_beam_is456_auto_calculates_effective_depth():
    """Test that effective depth is auto-calculated when not provided."""
    result = api.design_and_detail_beam_is456(
        units="IS456",
        beam_id="B4",
        story="GF",
        span_mm=5000.0,
        mu_knm=120.0,
        vu_kn=70.0,
        b_mm=300.0,
        D_mm=500.0,
        cover_mm=40.0,  # d should be 500 - 40 = 460mm
        fck_nmm2=25.0,
        fy_nmm2=500.0,
    )

    assert result.geometry["d_mm"] == 460.0
    assert result.is_ok is True
