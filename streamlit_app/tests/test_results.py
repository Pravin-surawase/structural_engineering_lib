"""
Unit Tests for Result Display Components
=========================================

Tests for components/results.py module.

Test Coverage:
- display_flexure_result() - Result formatting
- display_shear_result() - Result formatting
- display_summary_metrics() - Metrics display
- display_design_status() - Status display

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-FIX-001 Enhancement
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.results import (
    display_flexure_result,
    display_shear_result,
    display_summary_metrics,
    display_design_status,
)


class TestDisplayFunctions:
    """Test display functions handle various input formats"""

    def test_flexure_result_with_dict(self):
        """Test flexure display with dict input"""
        result = {"Ast_mm2": 804.0, "bars": "3-16mm", "is_safe": True, "xu_mm": 124.5}
        # Should not raise exception
        display_flexure_result(result)

    def test_shear_result_with_dict(self):
        """Test shear display with dict input"""
        result = {
            "spacing_mm": 150,
            "stirrup_config": "2L-8mm",
            "is_safe": True,
            "tau_v": 1.25,
        }
        # Should not raise exception
        display_shear_result(result)

    def test_summary_metrics_with_complete_result(self):
        """Test summary metrics with complete result"""
        result = {
            "flexure": {"Ast_mm2": 804.0, "is_safe": True},
            "shear": {"spacing_mm": 150, "is_safe": True},
            "is_safe": True,
        }
        # Should not raise exception
        display_summary_metrics(result)

    def test_design_status_safe(self):
        """Test design status display for safe design"""
        result = {"is_safe": True}
        # Should not raise exception
        display_design_status(result)

    def test_design_status_unsafe(self):
        """Test design status display for unsafe design"""
        result = {"is_safe": False}
        # Should not raise exception
        display_design_status(result)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_dict_handling(self):
        """Test functions handle empty dicts gracefully"""
        empty = {}
        # Should not raise exception
        display_flexure_result(empty)
        display_shear_result(empty)
        display_summary_metrics(empty)
        display_design_status(empty)

    def test_none_values_handling(self):
        """Test functions handle None values gracefully"""
        result_with_none = {"Ast_mm2": None, "bars": None, "is_safe": None}
        # Should not raise exception
        display_flexure_result(result_with_none)

    def test_missing_keys_handling(self):
        """Test functions handle missing keys gracefully"""
        partial = {"Ast_mm2": 804.0}
        # Should not raise exception
        display_flexure_result(partial)
        display_summary_metrics(partial)


class TestInputVariations:
    """Test various input formats"""

    def test_flexure_with_extra_keys(self):
        """Test flexure display ignores extra keys"""
        result = {
            "Ast_mm2": 804.0,
            "bars": "3-16mm",
            "is_safe": True,
            "extra_key": "ignored",
            "another_key": 123,
        }
        # Should not raise exception
        display_flexure_result(result)

    def test_shear_with_minimal_data(self):
        """Test shear display with minimal data"""
        result = {"spacing_mm": 150}
        # Should not raise exception
        display_shear_result(result)

    def test_summary_with_string_values(self):
        """Test summary handles string conversions"""
        result = {
            "flexure": {"Ast_mm2": "804", "is_safe": "True"},
            "shear": {"spacing_mm": "150", "is_safe": "True"},
        }
        # Should not raise exception (may need conversion logic)
        display_summary_metrics(result)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
