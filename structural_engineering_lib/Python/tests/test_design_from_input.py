# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for design_from_input API function.

This tests the integration between the inputs module and the API.
"""

from __future__ import annotations

from structural_lib import api
from structural_lib.api_results import DesignAndDetailResult
from structural_lib.data_types import ComplianceReport
from structural_lib.inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)


class TestDesignFromInput:
    """Tests for design_from_input function."""

    def test_simple_single_case(self) -> None:
        """Test simple single-case design."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60),
        )

        result = api.design_from_input(beam)

        assert isinstance(result, DesignAndDetailResult)
        assert result.beam_id == "B1"
        assert result.story == "GF"
        assert result.is_ok  # Should pass for these inputs

    def test_design_with_detailing(self) -> None:
        """Test that detailing is included by default."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60),
        )

        result = api.design_from_input(beam, include_detailing=True)

        assert isinstance(result, DesignAndDetailResult)
        assert result.detailing is not None
        assert len(result.detailing.bottom_bars) > 0

    def test_multi_case_with_detailing(self) -> None:
        """Test multi-case design returns DesignAndDetailResult with envelope."""
        beam = BeamInput(
            beam_id="B2",
            story="1F",
            geometry=BeamGeometryInput(b_mm=300, D_mm=600, span_mm=6000),
            materials=MaterialsInput.m30_fe500(),
            load_cases=[
                LoadCaseInput("DL+LL", mu_knm=150, vu_kn=90),
                LoadCaseInput("DL+EQ", mu_knm=180, vu_kn=110),
            ],
        )

        result = api.design_from_input(beam, include_detailing=True)

        assert isinstance(result, DesignAndDetailResult)
        # Should use governing moment (180 kN·m from DL+EQ)
        assert result.design.mu_knm == 180

    def test_multi_case_without_detailing(self) -> None:
        """Test multi-case design without detailing returns ComplianceReport."""
        beam = BeamInput(
            beam_id="B2",
            story="1F",
            geometry=BeamGeometryInput(b_mm=300, D_mm=600, span_mm=6000),
            materials=MaterialsInput.m30_fe500(),
            load_cases=[
                LoadCaseInput("DL+LL", mu_knm=150, vu_kn=90),
                LoadCaseInput("DL+EQ", mu_knm=180, vu_kn=110),
            ],
        )

        result = api.design_from_input(beam, include_detailing=False)

        assert isinstance(result, ComplianceReport)
        assert len(result.cases) == 2
        # Governing should be DL+EQ (higher utilization)

    def test_with_seismic_detailing(self) -> None:
        """Test design with seismic detailing configuration."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60),
            detailing_config=DetailingConfigInput.seismic(zone=4),
        )

        result = api.design_from_input(beam)

        assert isinstance(result, DesignAndDetailResult)
        # Detailing should reflect seismic requirements
        assert result.detailing is not None

    def test_effective_depth_calculation(self) -> None:
        """Test that effective depth is correctly calculated."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(
                b_mm=300, D_mm=500, span_mm=5000, cover_mm=50
            ),  # d = 500 - 50 = 450
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60),
        )

        result = api.design_from_input(beam)

        assert isinstance(result, DesignAndDetailResult)
        assert result.geometry["d_mm"] == 450.0

    def test_api_exports_input_classes(self) -> None:
        """Test that input classes are exported from api module."""
        # These should all be accessible from api module
        assert hasattr(api, "BeamInput")
        assert hasattr(api, "BeamGeometryInput")
        assert hasattr(api, "MaterialsInput")
        assert hasattr(api, "LoadsInput")
        assert hasattr(api, "LoadCaseInput")
        assert hasattr(api, "DetailingConfigInput")
        assert hasattr(api, "design_from_input")
