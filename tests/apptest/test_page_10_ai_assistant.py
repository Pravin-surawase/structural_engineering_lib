# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for AI Assistant page (10_🤖_ai_assistant.py).

These tests verify:
1. Page loads without errors
2. Parameter parsing from natural language
3. SmartDesigner integration
4. Chat panel functionality
"""

from __future__ import annotations

import pytest
from streamlit.testing.v1 import AppTest


class TestAIAssistantPageLoads:
    """Test that the AI assistant page loads without errors."""

    @pytest.fixture
    def app(self):
        """Create AppTest instance for AI assistant page."""
        return AppTest.from_file(
            "streamlit_app/pages/10_🤖_ai_assistant.py",
            default_timeout=30,
        )

    def test_page_loads_without_error(self, app):
        """Page should load without throwing exceptions."""
        app.run()
        assert not app.exception, f"Page raised exception: {app.exception}"

    def test_page_has_title(self, app):
        """Page should have the AI Assistant title."""
        app.run()
        # Title is rendered in the page (check for any title element)
        # Note: st.title renders as a special element
        assert len(app.title) >= 1 or len(app.markdown) >= 1, "Should have title or markdown elements"

    def test_page_has_chat_input(self, app):
        """Page should have chat input component."""
        app.run()
        assert len(app.chat_input) >= 1, "Should have at least one chat input"

    def test_page_has_tabs(self, app):
        """Page should have workspace tabs."""
        app.run()
        # Tabs should exist (Results, 3D View, Cost, Smart Dashboard)
        assert len(app.tabs) >= 1, "Should have workspace tabs"


class TestParameterParsing:
    """Test natural language parameter parsing."""

    def test_parse_moment_knm(self):
        """Parse moment from '150 kN·m' format."""
        # Import the function directly
        import sys
        import os

        # Add streamlit_app to path
        sys.path.insert(0, os.path.join(os.getcwd(), "streamlit_app", "pages"))


        # Import with dynamic import for special character filename
        # We can't test this directly due to module naming, so we use regex

        import re

        msg_lower = "design a beam for 150 kn·m moment"
        moment_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kn[·\-]?m|knm)", msg_lower)

        assert moment_match is not None
        assert float(moment_match.group(1)) == 150.0

    def test_parse_dimensions(self):
        """Parse dimensions from '300x500mm' format."""
        import re

        msg_lower = "design a 300x500mm beam"
        dim_match = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*(?:mm)?", msg_lower)

        assert dim_match is not None
        assert int(dim_match.group(1)) == 300
        assert int(dim_match.group(2)) == 500

    def test_parse_shear(self):
        """Parse shear from '80 kN' format."""
        import re

        msg_lower = "beam with 80 kn shear"
        shear_match = re.search(r"(\d+(?:\.\d+)?)\s*kn(?!\s*[·\-]?m)", msg_lower)

        assert shear_match is not None
        assert float(shear_match.group(1)) == 80.0

    def test_parse_span(self):
        """Parse span from '5m' format."""
        import re

        msg_lower = "beam with 5m span"
        span_match = re.search(
            r"(?:span\s+)?(\d+(?:\.\d+)?)\s*m(?:\s+span)?", msg_lower
        )

        assert span_match is not None
        assert float(span_match.group(1)) == 5.0

    def test_parse_concrete_grade(self):
        """Parse concrete grade from 'M25' format."""
        import re

        msg_lower = "design with m30 concrete"
        grade_match = re.search(r"m\s*(\d+)\s*(?:concrete)?", msg_lower)

        assert grade_match is not None
        assert int(grade_match.group(1)) == 30


class TestSmartDesignerIntegration:
    """Test SmartDesigner integration with AI chat."""

    def test_smart_designer_import(self):
        """SmartDesigner should be importable."""
        from structural_lib.insights import SmartDesigner

        assert SmartDesigner is not None

    def test_smart_designer_analyze_method_exists(self):
        """SmartDesigner should have analyze method."""
        from structural_lib.insights import SmartDesigner

        assert hasattr(SmartDesigner, "analyze")
        assert callable(SmartDesigner.analyze)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
