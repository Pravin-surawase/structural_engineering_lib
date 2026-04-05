"""EA-7: End-to-end pipeline test — design → detailing → BBS → report.

Tests the complete user workflow that the external audit identified as having
zero integration coverage. Each step feeds into the next.

Pipeline: design_beam_is456 → build_detailing_input → compute_detailing
          → compute_bbs → compute_report
          → compute_dxf (optional, requires ezdxf)
"""

import pytest

from structural_lib import api

# ---------------------------------------------------------------------------
# Shared constants — single reference beam used across all pipeline steps
# ---------------------------------------------------------------------------
_B_MM = 300.0
_D_MM = 500.0
_D_EFF_MM = 450.0
_FCK = 25.0
_FY = 500.0
_MU_KNM = 150.0
_VU_KN = 80.0
_COVER_MM = 30.0
_SPAN_MM = 6000.0


@pytest.mark.integration
class TestFullPipelineE2E:
    """Full pipeline: design → detailing → BBS → report."""

    @pytest.fixture
    def beam_design_result(self):
        """Design a reference beam for pipeline tests."""
        result = api.design_beam_is456(
            units="IS456",
            b_mm=_B_MM,
            d_mm=_D_EFF_MM,
            D_mm=_D_MM,
            fck_nmm2=_FCK,
            fy_nmm2=_FY,
            mu_knm=_MU_KNM,
            vu_kn=_VU_KN,
        )
        return result

    @pytest.fixture
    def detailing_input(self, beam_design_result):
        """Build detailing input dict from the design result."""
        return api.build_detailing_input(
            beam_design_result,
            beam_id="B1-E2E",
            b_mm=_B_MM,
            D_mm=_D_MM,
            d_mm=_D_EFF_MM,
            span_mm=_SPAN_MM,
            cover_mm=_COVER_MM,
            fck_nmm2=_FCK,
            fy_nmm2=_FY,
        )

    @pytest.fixture
    def detailing_list(self, detailing_input):
        """Compute detailing from the input dict."""
        return api.compute_detailing(detailing_input)

    # ------------------------------------------------------------------
    # Step 1: Design
    # ------------------------------------------------------------------
    def test_step1_design(self, beam_design_result):
        """Step 1: Beam design produces valid result with flexure and shear."""
        result = beam_design_result
        assert result is not None
        # Flexure checks
        assert hasattr(result, "flexure")
        assert result.flexure.Ast_required > 0
        assert result.flexure.Mu_lim > 0
        assert result.flexure.is_safe
        # Shear checks
        assert hasattr(result, "shear")
        assert result.shear.tau_v >= 0
        assert result.shear.tau_c > 0

    # ------------------------------------------------------------------
    # Step 2: Build detailing input
    # ------------------------------------------------------------------
    def test_step2_build_detailing_input(self, detailing_input):
        """Step 2: build_detailing_input produces well-formed dict."""
        assert isinstance(detailing_input, dict)
        assert "beams" in detailing_input
        beams = detailing_input["beams"]
        assert len(beams) == 1
        beam = beams[0]
        assert beam["beam_id"] == "B1-E2E"
        assert beam["geometry"]["b_mm"] == _B_MM
        assert beam["materials"]["fck_nmm2"] == _FCK
        # Flexure data should flow through from design result
        assert "flexure" in beam
        assert beam["flexure"]["ast_required_mm2"] > 0

    # ------------------------------------------------------------------
    # Step 3: Detailing
    # ------------------------------------------------------------------
    def test_step3_detailing(self, detailing_list):
        """Step 3: compute_detailing returns non-empty list."""
        assert isinstance(detailing_list, list)
        assert len(detailing_list) > 0
        det = detailing_list[0]
        assert hasattr(det, "beam_id")
        assert det.beam_id == "B1-E2E"

    # ------------------------------------------------------------------
    # Step 4: BBS
    # ------------------------------------------------------------------
    def test_step4_bbs(self, detailing_list):
        """Step 4: compute_bbs produces a BBSDocument."""
        bbs = api.compute_bbs(detailing_list, project_name="E2E-Test")
        assert bbs is not None
        # BBSDocument should have entries
        assert hasattr(bbs, "entries") or hasattr(bbs, "items") or hasattr(bbs, "rows")

    # ------------------------------------------------------------------
    # Step 5: Report (HTML string)
    # ------------------------------------------------------------------
    def test_step5_report_html(self, detailing_input):
        """Step 5: compute_report generates HTML string from dict."""
        report_str = api.compute_report(detailing_input, format="html")
        assert isinstance(report_str, str)
        assert len(report_str) > 100
        # Should contain some HTML content
        assert "<" in report_str

    # ------------------------------------------------------------------
    # Step 5b: Report (JSON string)
    # ------------------------------------------------------------------
    def test_step5b_report_json(self, detailing_input):
        """Step 5b: compute_report generates JSON string from dict."""
        report_str = api.compute_report(detailing_input, format="json")
        assert isinstance(report_str, str)
        assert len(report_str) > 10

    # ------------------------------------------------------------------
    # Step 6: DXF export (optional — requires ezdxf)
    # ------------------------------------------------------------------
    def test_step6_dxf_export(self, detailing_list, tmp_path):
        """Step 6: compute_dxf exports a DXF file (skipped if ezdxf missing)."""
        pytest.importorskip("ezdxf")
        output_file = tmp_path / "e2e_test.dxf"
        result_path = api.compute_dxf(detailing_list, output=output_file)
        assert result_path.exists()
        assert result_path.stat().st_size > 0

    # ------------------------------------------------------------------
    # Full chain — canonical workflow in one test
    # ------------------------------------------------------------------
    def test_full_chain(self, tmp_path):
        """Complete chain in one test — the canonical end-to-end workflow."""
        # 1. Design
        result = api.design_beam_is456(
            units="IS456",
            b_mm=_B_MM,
            d_mm=_D_EFF_MM,
            D_mm=_D_MM,
            fck_nmm2=_FCK,
            fy_nmm2=_FY,
            mu_knm=_MU_KNM,
            vu_kn=_VU_KN,
        )
        assert result is not None
        assert result.flexure.is_safe

        # 2. Build detailing input
        det_input = api.build_detailing_input(
            result,
            beam_id="B1-CHAIN",
            b_mm=_B_MM,
            D_mm=_D_MM,
            d_mm=_D_EFF_MM,
            span_mm=_SPAN_MM,
            cover_mm=_COVER_MM,
            fck_nmm2=_FCK,
            fy_nmm2=_FY,
        )
        assert "beams" in det_input

        # 3. Detailing
        detailed = api.compute_detailing(det_input)
        assert len(detailed) > 0
        assert detailed[0].beam_id == "B1-CHAIN"

        # 4. BBS
        bbs = api.compute_bbs(detailed, project_name="Chain-Test")
        assert bbs is not None

        # 5. Report (HTML as string — no output_path)
        report = api.compute_report(det_input, format="html")
        assert isinstance(report, str)
        assert len(report) > 100

        # 6. Report saved to file
        report_dir = tmp_path / "chain_report"
        saved = api.compute_report(det_input, format="html", output_path=report_dir)
        # compute_report may return Path or list[Path] depending on beam count
        if isinstance(saved, list):
            assert len(saved) > 0
            assert all(p.exists() for p in saved)
        else:
            assert saved.exists()
            assert saved.stat().st_size > 100
