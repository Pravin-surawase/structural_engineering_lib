# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for design_from_input API function.

This tests the integration between the inputs module and the API.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from structural_lib import api
from structural_lib.core.data_types import ComplianceReport
from structural_lib.core.inputs import (
    BeamGeometryInput,
    BeamInput,
    DetailingConfigInput,
    LoadCaseInput,
    LoadsInput,
    MaterialsInput,
)
from structural_lib.services.api_results import DesignAndDetailResult
from structural_lib.services.bbs import generate_bbs_from_detailing


class TestDesignFromInput:
    """Tests for design_from_input function."""

    def test_simple_single_case(self) -> None:
        """Test simple single-case design."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, bar_dia_mm=16),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60),
        )

        result = api.design_from_input(beam)

        assert isinstance(result, DesignAndDetailResult)
        assert result.beam_id == "B1"
        assert result.story == "GF"
        assert result.is_ok  # Should pass for these inputs
        assert result.design.case_id == "B1@GF"

    def test_single_case_id_reaches_design_and_compliance_report(self) -> None:
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, bar_dia_mm=16),
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60, case_id="ULS-A9-EXPLICIT"),
        )
        beam = BeamInput.from_json(beam.to_json())

        detailed = api.design_from_input(beam)
        report = api.design_from_input(beam, include_detailing=False)

        assert isinstance(detailed, DesignAndDetailResult)
        assert detailed.design.case_id == "ULS-A9-EXPLICIT"
        assert isinstance(report, ComplianceReport)
        assert report.to_dict()["governing_case_id"] == "ULS-A9-EXPLICIT"
        assert [case.case_id for case in report.cases] == ["ULS-A9-EXPLICIT"]

    @pytest.mark.parametrize("multiple_cases", [False, True])
    def test_explicit_end_spacing_reaches_the_schedule(
        self, multiple_cases: bool
    ) -> None:
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, bar_dia_mm=16),
            materials=MaterialsInput.m25_fe500(),
            loads=None if multiple_cases else LoadsInput(mu_knm=100, vu_kn=60),
            load_cases=(
                [
                    LoadCaseInput("DL+LL", mu_knm=80, vu_kn=50),
                    LoadCaseInput("DL+EQ", mu_knm=100, vu_kn=60),
                ]
                if multiple_cases
                else []
            ),
        )
        configured = replace(
            beam,
            detailing_config=replace(beam.detailing_config, stirrup_spacing_end_mm=125),
        )
        default = api.design_from_input(beam)
        detailed = api.design_from_input(BeamInput.from_json(configured.to_json()))

        assert isinstance(default, DesignAndDetailResult)
        assert isinstance(detailed, DesignAndDetailResult)
        assert [zone.spacing for zone in default.detailing.stirrups] == [150, 200, 150]
        assert [zone.spacing for zone in detailed.detailing.stirrups] == [150, 200, 125]
        counts = {
            item.zone: item.no_of_bars
            for item in generate_bbs_from_detailing(detailed.detailing)
            if item.location == "stirrup"
        }
        assert counts == {"start": 9, "mid": 13, "end": 11}

    def test_design_with_detailing(self) -> None:
        """Test that detailing is included by default."""
        beam = BeamInput(
            beam_id="B1",
            story="GF",
            geometry=BeamGeometryInput(b_mm=300, D_mm=500, span_mm=5000, bar_dia_mm=16),
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
            geometry=BeamGeometryInput(b_mm=300, D_mm=600, span_mm=6000, bar_dia_mm=16),
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
            geometry=BeamGeometryInput(
                b_mm=300, D_mm=500, span_mm=5000, bar_dia_mm=16, stirrup_dia_mm=10
            ),
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
            ),  # d = 500 - 50 - 8 - 20/2 = 432
            materials=MaterialsInput.m25_fe500(),
            loads=LoadsInput(mu_knm=100, vu_kn=60),
        )

        result = api.design_from_input(beam, include_detailing=False)

        assert beam.geometry.effective_depth == 432.0
        assert isinstance(result, ComplianceReport)
        assert len(result.cases) == 1
        assert result.cases[0].shear.tau_v == pytest.approx(60_000 / (300 * 432))

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
