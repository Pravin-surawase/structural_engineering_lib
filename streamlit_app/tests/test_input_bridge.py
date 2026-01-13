# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for input_bridge.py - Bridge between Streamlit UI and Library inputs.

These tests verify the conversion functions work correctly for TASK-276-279 integration.
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass
from datetime import datetime


# Mock BeamInputs for testing (mimics session_manager.BeamInputs)
@dataclass
class MockBeamInputs:
    """Mock of session_manager.BeamInputs for testing."""

    b_mm: float = 300.0
    D_mm: float = 500.0
    d_mm: float = 450.0
    span_mm: float = 4000.0
    cover_mm: float = 40.0
    fck_mpa: float = 25.0
    fy_mpa: float = 500.0
    mu_knm: float = 150.0
    vu_kn: float = 100.0
    timestamp: str = "2026-01-13T12:00:00"

    @classmethod
    def from_dict(cls, d: dict) -> "MockBeamInputs":
        """Create from dict."""
        return cls(**d)


# Mock DesignResult for testing
@dataclass
class MockDesignResult:
    """Mock of session_manager.DesignResult for testing."""

    ast_mm2: float = 1200.0
    ast_provided_mm2: float = 1357.0
    num_bars: int = 4
    bar_diameter_mm: int = 20
    stirrup_spacing_mm: float = 150.0
    utilization_pct: float = 88.5
    status: str = "PASS"


class TestInputBridge:
    """Tests for InputBridge class."""

    def test_to_library_input_basic(self) -> None:
        """Test basic conversion to library input format."""
        ui_inputs = MockBeamInputs()

        # Import the bridge
        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        result = InputBridge.to_library_input(ui_inputs)

        # Check structure
        assert "geometry" in result
        assert "materials" in result
        assert "loads" in result
        assert "beam_id" in result
        assert "story" in result

        # Check values
        assert result["geometry"]["b_mm"] == 300.0
        assert result["geometry"]["D_mm"] == 500.0
        assert result["geometry"]["d_mm"] == 450.0
        assert result["materials"]["fck_nmm2"] == 25.0
        assert result["materials"]["fy_nmm2"] == 500.0
        assert result["loads"]["mu_knm"] == 150.0
        assert result["loads"]["vu_kn"] == 100.0

    def test_to_api_kwargs(self) -> None:
        """Test conversion to API keyword arguments."""
        ui_inputs = MockBeamInputs()

        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        result = InputBridge.to_api_kwargs(ui_inputs)

        # Check required API arguments
        assert result["b_mm"] == 300.0
        assert result["D_mm"] == 500.0
        assert result["fck_nmm2"] == 25.0
        assert result["fy_nmm2"] == 500.0
        assert result["mu_knm"] == 150.0
        assert result["vu_kn"] == 100.0
        assert result["units"] == "IS456"

    def test_to_audit_log_inputs(self) -> None:
        """Test conversion for audit logging."""
        ui_inputs = MockBeamInputs()

        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        result = InputBridge.to_audit_log_inputs(ui_inputs)

        # Check audit fields
        assert result["source"] == "streamlit_ui"
        assert result["timestamp"] == "2026-01-13T12:00:00"
        assert result["b_mm"] == 300.0
        assert result["fck_nmm2"] == 25.0

    def test_result_to_audit_outputs(self) -> None:
        """Test conversion of results for audit."""
        result = MockDesignResult()

        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        audit_output = InputBridge.result_to_audit_outputs(result)

        assert audit_output["ast_mm2"] == 1200.0
        assert audit_output["ast_provided_mm2"] == 1357.0
        assert audit_output["status"] == "PASS"
        assert audit_output["is_ok"] is True

    def test_to_report_project_info(self) -> None:
        """Test project info generation for reports."""
        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        result = InputBridge.to_report_project_info(
            project_name="Test Project",
            engineer="John Engineer",
            client="Test Client",
        )

        assert result["project_name"] == "Test Project"
        assert result["engineer_name"] == "John Engineer"
        assert result["client_name"] == "Test Client"
        assert result["revision"] == "A"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_timestamp(self) -> None:
        """Test with empty timestamp."""
        ui_inputs = MockBeamInputs(timestamp="")

        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        result = InputBridge.to_library_input(ui_inputs)

        # Should still generate a beam_id
        assert result["beam_id"].startswith("B-")

    def test_zero_values(self) -> None:
        """Test with zero values (edge case)."""
        ui_inputs = MockBeamInputs(b_mm=0.0, D_mm=0.0, mu_knm=0.0)

        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        result = InputBridge.to_library_input(ui_inputs)

        # Should handle zeros without error
        assert result["geometry"]["b_mm"] == 0.0
        assert result["geometry"]["D_mm"] == 0.0

    def test_result_fail_status(self) -> None:
        """Test with FAIL status."""
        result = MockDesignResult(status="FAIL")

        import sys

        sys.path.insert(0, "streamlit_app")

        from utils.input_bridge import InputBridge

        audit_output = InputBridge.result_to_audit_outputs(result)

        assert audit_output["is_ok"] is False
