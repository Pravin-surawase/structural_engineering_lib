# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Edge case tests for report generation modules (TASK-520).

Coverage targets:
- ReportContext: date auto-fill, to_dict edge cases
- generate_html_report: object with to_dict(), object with __dict__,
  non-dict/non-object input
- _generate_fallback_html: fallback rendering path
- Template filters: _format_number, _format_mm, _format_percent edge cases
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from structural_lib.reports.generator import (
    JINJA2_AVAILABLE,
    ReportContext,
    _format_mm,
    _format_number,
    _format_percent,
    _generate_fallback_html,
    generate_html_report,
)

requires_jinja2 = pytest.mark.skipif(
    not JINJA2_AVAILABLE, reason="Jinja2 not installed"
)


# =============================================================================
# ReportContext edge cases
# =============================================================================


class TestReportContextEdgeCases:
    """Edge case tests for ReportContext dataclass."""

    def test_date_auto_filled_when_empty(self) -> None:
        """ReportContext.__post_init__ should set today's date if empty."""
        ctx = ReportContext(beam_id="B1", inputs={}, results={})
        assert ctx.date != ""
        parts = ctx.date.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4

    def test_date_preserved_when_provided(self) -> None:
        """Explicit date should not be overwritten."""
        ctx = ReportContext(beam_id="B1", date="2025-01-15", inputs={}, results={})
        assert ctx.date == "2025-01-15"

    def test_to_dict_fail_status(self) -> None:
        """to_dict should set status_class='status-fail' when is_ok=False."""
        ctx = ReportContext(beam_id="B1", inputs={}, results={}, is_ok=False)
        d = ctx.to_dict()
        assert d["status_class"] == "status-fail"
        assert d["status_text"] == "FAIL"

    def test_to_dict_pass_status(self) -> None:
        """to_dict should set status_class='status-pass' when is_ok=True."""
        ctx = ReportContext(beam_id="B1", inputs={}, results={}, is_ok=True)
        d = ctx.to_dict()
        assert d["status_class"] == "status-pass"
        assert d["status_text"] == "PASS"

    def test_to_dict_contains_all_fields(self) -> None:
        """to_dict should contain all fields from the context."""
        ctx = ReportContext(
            beam_id="B99",
            project_name="Edge Test",
            project_number="PRJ-999",
            client_name="Client X",
            engineer_name="Eng Y",
            checker_name="Check Z",
            revision="C",
            inputs={"b_mm": 200},
            results={"test": True},
            is_ok=True,
            code_reference="IS 456:2000",
            software_version="0.22.0",
        )
        d = ctx.to_dict()
        assert d["beam_id"] == "B99"
        assert d["project_number"] == "PRJ-999"
        assert d["software_version"] == "0.22.0"
        assert d["code_reference"] == "IS 456:2000"

    def test_empty_inputs_and_results(self) -> None:
        """Context with empty dicts should serialize cleanly."""
        ctx = ReportContext(beam_id="B1", inputs={}, results={})
        d = ctx.to_dict()
        assert d["inputs"] == {}
        assert d["results"] == {}


# =============================================================================
# Fallback HTML generation (no Jinja2)
# =============================================================================


class TestFallbackHtml:
    """Tests for _generate_fallback_html (when Jinja2 not installed)."""

    def test_fallback_produces_valid_html(self) -> None:
        """Fallback HTML should contain proper structure."""
        context = {
            "beam_id": "B1",
            "project_name": "Test Project",
            "is_ok": True,
            "results": {"flexure": {"ast_mm2": 1000}},
        }
        html = _generate_fallback_html(context)
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "B1" in html
        assert "Test Project" in html
        assert "PASS" in html

    def test_fallback_fail_status(self) -> None:
        """Fallback HTML should show FAIL for is_ok=False."""
        context = {"beam_id": "B2", "is_ok": False, "results": {}}
        html = _generate_fallback_html(context)
        assert "FAIL" in html
        assert "#dc3545" in html

    def test_fallback_escapes_html(self) -> None:
        """Fallback should escape HTML entities in user input."""
        context = {
            "beam_id": "<script>alert('xss')</script>",
            "project_name": "A & B <Corp>",
            "is_ok": True,
            "results": {},
        }
        html = _generate_fallback_html(context)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "&amp;" in html

    def test_fallback_missing_keys(self) -> None:
        """Fallback should handle missing keys gracefully."""
        context: dict = {}
        html = _generate_fallback_html(context)
        assert "<!DOCTYPE html>" in html
        assert "B1" in html

    def test_fallback_includes_results(self) -> None:
        """Fallback should include results in pre block."""
        context = {
            "beam_id": "B1",
            "is_ok": True,
            "results": {"shear": {"vu_kn": 100}},
        }
        html = _generate_fallback_html(context)
        assert "vu_kn" in html


# =============================================================================
# Template filter edge cases
# =============================================================================


class TestTemplateFilters:
    """Tests for template filter functions."""

    def test_format_number_none(self) -> None:
        assert _format_number(None) == "-"

    def test_format_number_invalid_string(self) -> None:
        assert _format_number("abc") == "abc"

    def test_format_number_zero(self) -> None:
        assert _format_number(0) == "0.00"

    def test_format_number_large(self) -> None:
        assert _format_number(1234567.89) == "1,234,567.89"

    def test_format_number_custom_decimals(self) -> None:
        assert _format_number(3.14159, 4) == "3.1416"

    def test_format_mm_none(self) -> None:
        assert _format_mm(None) == "-"

    def test_format_mm_valid(self) -> None:
        assert _format_mm(300) == "300 mm"

    def test_format_mm_with_decimals(self) -> None:
        assert _format_mm(300.5, 1) == "300.5 mm"

    def test_format_mm_invalid(self) -> None:
        assert _format_mm("abc") == "abc"

    def test_format_percent_none(self) -> None:
        assert _format_percent(None) == "-"

    def test_format_percent_valid(self) -> None:
        assert _format_percent(0.85) == "0.85%"

    def test_format_percent_custom_decimals(self) -> None:
        assert _format_percent(1.23456, 1) == "1.2%"

    def test_format_percent_invalid(self) -> None:
        assert _format_percent("abc") == "abc"


# =============================================================================
# generate_html_report with different input types
# =============================================================================


@requires_jinja2
class TestGenerateReportInputTypes:
    """Tests for generate_html_report with various input types."""

    def test_input_with_to_dict_method(self) -> None:
        """generate_html_report should call to_dict() on objects that have it."""

        @dataclass
        class FakeResult:
            inputs: dict
            results: dict
            is_ok: bool

            def to_dict(self) -> dict:
                return {
                    "inputs": self.inputs,
                    "results": self.results,
                    "is_ok": self.is_ok,
                }

        obj = FakeResult(
            inputs={"b_mm": 300, "D_mm": 500},
            results={"flexure": {"ast_mm2": 1000}},
            is_ok=True,
        )
        html = generate_html_report(obj, beam_id="B1")
        assert isinstance(html, str)
        assert "B1" in html

    def test_input_with_dunder_dict(self) -> None:
        """generate_html_report should use vars() for objects with __dict__."""

        class SimpleObj:
            def __init__(self) -> None:
                self.inputs = {"b_mm": 250}
                self.results = {"shear": {"sv_mm": 150}}
                self.is_ok = False

        obj = SimpleObj()
        html = generate_html_report(obj, beam_id="B2")
        assert isinstance(html, str)
        assert "B2" in html

    def test_input_with_non_dict_non_object(self) -> None:
        """Non-dict, non-object input should be wrapped."""
        html = generate_html_report("raw string data", beam_id="B3")
        assert isinstance(html, str)
        assert "B3" in html

    def test_is_ok_from_nested_results(self) -> None:
        """is_ok should be extracted from results dict if not at top level."""
        result = {
            "inputs": {"b_mm": 300},
            "results": {"is_ok": True, "flexure": {}},
        }
        html = generate_html_report(result, beam_id="B4")
        assert "PASS" in html or "status-pass" in html

    def test_full_project_info_fields(self) -> None:
        """All project_info fields should propagate to context."""
        result = {"inputs": {}, "results": {}, "is_ok": True}
        html = generate_html_report(
            result,
            beam_id="B5",
            project_info={
                "project_name": "Edge Project",
                "project_number": "PRJ-EDGE-001",
                "client_name": "Edge Client",
                "engineer_name": "Edge Engineer",
                "checker_name": "Edge Checker",
                "revision": "Rev X",
                "date": "2025-12-31",
                "software_version": "0.99.0",
            },
        )
        assert "Edge Project" in html
        assert "B5" in html
