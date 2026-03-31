# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for the dashboard analytics module."""

import pytest

from structural_lib.services.dashboard import (
    CodeCheckResult,
    DashboardSummary,
    RebarSuggestion,
    RebarSuggestionsResult,
    code_checks_live,
    generate_dashboard,
    suggest_rebar_options,
)

# ---------------------------------------------------------------------------
# generate_dashboard tests
# ---------------------------------------------------------------------------


class TestGenerateDashboard:
    """Tests for generate_dashboard function."""

    def test_empty_results_returns_zeroed_summary(self):
        """Empty input produces zeroed dashboard."""
        summary = generate_dashboard([])
        assert isinstance(summary, DashboardSummary)
        assert summary.total_beams == 0
        assert summary.passed == 0
        assert summary.failed == 0
        assert summary.avg_utilization == 0.0

    def test_single_passing_beam(self):
        """Single passing beam updates pass count."""
        results = [
            {"beam_id": "B1", "is_valid": True, "utilization": 0.75, "story": "GF"}
        ]
        summary = generate_dashboard(results)

        assert summary.total_beams == 1
        assert summary.passed == 1
        assert summary.failed == 0

    def test_single_failing_beam(self):
        """Single failing beam updates fail count and critical list."""
        results = [
            {"beam_id": "B1", "is_valid": False, "utilization": 0.5, "story": "GF"}
        ]
        summary = generate_dashboard(results)

        assert summary.total_beams == 1
        assert summary.passed == 0
        assert summary.failed == 1
        assert "B1" in summary.critical_beams

    def test_pass_rate_calculation(self):
        """Pass rate computed correctly in to_dict."""
        results = [
            {"beam_id": "B1", "is_valid": True, "utilization": 0.5},
            {"beam_id": "B2", "is_valid": True, "utilization": 0.6},
            {"beam_id": "B3", "is_valid": False, "utilization": 0.9},
        ]
        summary = generate_dashboard(results)
        d = summary.to_dict()

        assert d["pass_rate"] == pytest.approx(66.7, abs=0.1)

    def test_utilization_stats(self):
        """Min/max/avg utilization computed correctly."""
        results = [
            {"beam_id": "B1", "utilization": 0.5},
            {"beam_id": "B2", "utilization": 0.8},
            {"beam_id": "B3", "utilization": 0.3},
        ]
        summary = generate_dashboard(results)

        assert summary.max_utilization == pytest.approx(0.8, abs=0.01)
        assert summary.min_utilization == pytest.approx(0.3, abs=0.01)
        assert summary.avg_utilization == pytest.approx(0.533, abs=0.01)

    def test_critical_beams_high_utilization(self):
        """Beams with utilization > 0.95 are flagged as critical."""
        results = [
            {"beam_id": "B1", "is_valid": True, "utilization": 0.98},
            {"beam_id": "B2", "is_valid": True, "utilization": 0.5},
        ]
        summary = generate_dashboard(results)

        assert "B1" in summary.critical_beams
        assert "B2" not in summary.critical_beams

    def test_story_grouping(self):
        """Beams are grouped by story in by_story dict."""
        results = [
            {"beam_id": "B1", "is_valid": True, "story": "GF"},
            {"beam_id": "B2", "is_valid": False, "story": "GF"},
            {"beam_id": "B3", "is_valid": True, "story": "1F"},
        ]
        summary = generate_dashboard(results)

        assert "GF" in summary.by_story
        assert summary.by_story["GF"]["total"] == 2
        assert summary.by_story["GF"]["passed"] == 1
        assert summary.by_story["GF"]["failed"] == 1
        assert summary.by_story["1F"]["total"] == 1

    def test_to_dict_format(self):
        """to_dict returns expected keys."""
        summary = generate_dashboard([])
        d = summary.to_dict()

        assert "total_beams" in d
        assert "pass_rate" in d
        assert "avg_utilization" in d
        assert "critical_beams" in d
        assert "by_story" in d

    def test_warnings_counted(self):
        """Warnings from results are counted."""
        results = [
            {"beam_id": "B1", "is_valid": True, "warnings": ["w1", "w2"]},
            {"beam_id": "B2", "is_valid": True, "warnings": ["w3"]},
        ]
        summary = generate_dashboard(results)
        assert summary.warnings_count == 3


# ---------------------------------------------------------------------------
# code_checks_live tests
# ---------------------------------------------------------------------------


class TestCodeChecksLive:
    """Tests for code_checks_live function."""

    def test_basic_passing_beam(self):
        """A well-designed beam should pass all checks."""
        beam = {
            "b_mm": 300,
            "D_mm": 500,
            "d_mm": 450,
            "span_mm": 5000,
            "fck": 25,
            "fy": 500,
        }
        config = {"ast_mm2": 800, "bar_count": 4, "bar_dia_mm": 16}
        result = code_checks_live(beam, config)

        assert isinstance(result, CodeCheckResult)
        assert len(result.checks) > 0

    def test_no_config_returns_result(self):
        """Calling without config still returns a valid result."""
        beam = {"b_mm": 300, "D_mm": 500, "span_mm": 5000}
        result = code_checks_live(beam)

        assert isinstance(result, CodeCheckResult)

    def test_narrow_beam_warning(self):
        """Width < 200mm triggers a warning."""
        beam = {"b_mm": 150, "D_mm": 400, "span_mm": 3000}
        result = code_checks_live(beam)

        assert any("200mm" in w for w in result.warnings)

    def test_to_dict_format(self):
        """to_dict returns expected structure."""
        beam = {"b_mm": 300, "D_mm": 500, "span_mm": 5000}
        result = code_checks_live(beam)
        d = result.to_dict()

        assert "passed" in d
        assert "checks" in d
        assert "utilization" in d


# ---------------------------------------------------------------------------
# suggest_rebar_options tests
# ---------------------------------------------------------------------------


class TestSuggestRebarOptions:
    """Tests for suggest_rebar_options function."""

    def test_basic_suggestion(self):
        """Beam with excess steel should get reduction suggestion."""
        beam = {
            "beam_id": "B1",
            "ast_required": 600,
            "ast_provided": 1200,
            "bar_count": 6,
            "bar_dia_mm": 16,
            "b_mm": 300,
        }
        result = suggest_rebar_options(beam)

        assert isinstance(result, RebarSuggestionsResult)
        assert result.beam_id == "B1"

    def test_empty_beam_returns_result(self):
        """Beam with no steel data returns empty suggestions."""
        beam = {"beam_id": "B2", "b_mm": 300}
        result = suggest_rebar_options(beam)

        assert isinstance(result, RebarSuggestionsResult)

    def test_to_dict_format(self):
        """to_dict returns expected keys."""
        beam = {"beam_id": "B3", "b_mm": 300}
        result = suggest_rebar_options(beam)
        d = result.to_dict()

        assert "beam_id" in d
        assert "suggestions" in d
        assert "suggestion_count" in d


# ---------------------------------------------------------------------------
# Dataclass tests
# ---------------------------------------------------------------------------


class TestDashboardDataclasses:
    """Tests for dashboard dataclass to_dict methods."""

    def test_dashboard_summary_default_values(self):
        """DashboardSummary has correct defaults."""
        s = DashboardSummary()
        assert s.total_beams == 0
        assert s.passed == 0
        assert s.failed == 0
        assert s.min_utilization == float("inf")

    def test_dashboard_summary_to_dict_inf_handling(self):
        """min_utilization=inf converts to 0.0 in to_dict."""
        s = DashboardSummary()
        d = s.to_dict()
        assert d["min_utilization"] == 0.0

    def test_code_check_result_to_dict(self):
        """CodeCheckResult to_dict rounds utilization."""
        r = CodeCheckResult(passed=True, utilization=0.8567)
        d = r.to_dict()
        assert d["utilization"] == 0.86

    def test_rebar_suggestion_to_dict(self):
        """RebarSuggestion to_dict includes all fields."""
        s = RebarSuggestion(
            id="S1",
            title="Reduce dia",
            description="Use 12mm",
            impact="MEDIUM",
            savings_percent=15.3,
        )
        d = s.to_dict()
        assert d["id"] == "S1"
        assert d["savings_percent"] == 15.3
