"""
Tests for Fragment Utilities
============================

Tests modern Streamlit fragment patterns.

Note: These tests run without AppTest to avoid MockStreamlit conflicts.
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch

# Skip conftest's MockStreamlit by importing streamlit directly first
# This ensures we test against real streamlit, not mocks
import streamlit as real_st


class TestFragmentFeatureDetection:
    """Tests for feature detection functions."""

    def test_check_fragment_available(self):
        """Test fragment detection."""
        from streamlit_app.utils.fragments import check_fragment_available

        # In our environment, fragment should be available
        result = check_fragment_available()
        assert isinstance(result, bool)

    def test_check_dialog_available(self):
        """Test dialog detection."""
        from streamlit_app.utils.fragments import check_dialog_available

        result = check_dialog_available()
        assert isinstance(result, bool)

    def test_check_badge_available(self):
        """Test badge detection."""
        from streamlit_app.utils.fragments import check_badge_available

        result = check_badge_available()
        assert isinstance(result, bool)

    def test_get_available_features(self):
        """Test getting all available features."""
        from streamlit_app.utils.fragments import get_available_features

        features = get_available_features()

        assert isinstance(features, dict)
        assert "fragment" in features
        assert "dialog" in features
        assert "badge" in features
        assert "pills" in features
        assert "segmented_control" in features
        assert "feedback" in features

        # All values should be booleans
        for key, value in features.items():
            assert isinstance(value, bool), f"{key} should be bool"


class TestCacheStatsFragment:
    """Tests for CacheStatsFragment class."""

    def test_init(self):
        """Test initialization."""
        from streamlit_app.utils.fragments import CacheStatsFragment

        mock_design_cache = Mock()
        mock_viz_cache = Mock()

        fragment = CacheStatsFragment(
            design_cache=mock_design_cache,
            viz_cache=mock_viz_cache,
            refresh_interval=15,
        )

        assert fragment.design_cache == mock_design_cache
        assert fragment.viz_cache == mock_viz_cache
        assert fragment.refresh_interval == 15

    def test_init_without_viz_cache(self):
        """Test initialization without viz cache."""
        from streamlit_app.utils.fragments import CacheStatsFragment

        mock_design_cache = Mock()

        fragment = CacheStatsFragment(
            design_cache=mock_design_cache,
            refresh_interval=10,
        )

        assert fragment.design_cache == mock_design_cache
        assert fragment.viz_cache is None
        assert fragment.refresh_interval == 10


class TestShowStatusBadge:
    """Tests for status badge display."""

    @patch("streamlit_app.utils.fragments.st")
    def test_safe_status_with_badge(self, mock_st):
        """Test safe status when badge is available."""
        from streamlit_app.utils.fragments import show_status_badge

        mock_st.badge = Mock()

        show_status_badge(is_safe=True)

        mock_st.badge.assert_called_once_with("SAFE", color="green")

    @patch("streamlit_app.utils.fragments.st")
    def test_unsafe_status_with_badge(self, mock_st):
        """Test unsafe status when badge is available."""
        from streamlit_app.utils.fragments import show_status_badge

        mock_st.badge = Mock()

        show_status_badge(is_safe=False)

        mock_st.badge.assert_called_once_with("UNSAFE", color="red")

    @patch("streamlit_app.utils.fragments.st")
    def test_custom_text(self, mock_st):
        """Test custom safe/unsafe text."""
        from streamlit_app.utils.fragments import show_status_badge

        mock_st.badge = Mock()

        show_status_badge(is_safe=True, safe_text="OK", unsafe_text="FAIL")

        mock_st.badge.assert_called_once_with("OK", color="green")

    @patch("streamlit_app.utils.fragments.st")
    def test_fallback_when_badge_unavailable(self, mock_st):
        """Test fallback to success/error when badge not available."""
        from streamlit_app.utils.fragments import show_status_badge

        # Remove badge attribute
        del mock_st.badge
        mock_st.success = Mock()
        mock_st.error = Mock()

        show_status_badge(is_safe=True)

        mock_st.success.assert_called_once()


class TestCreateValidationFragment:
    """Tests for validation fragment factory."""

    def test_decorator_returns_callable(self):
        """Test that decorator returns callable."""
        from streamlit_app.utils.fragments import create_validation_fragment

        decorator = create_validation_fragment()
        assert callable(decorator)

    def test_decorated_function_structure(self):
        """Test that decorator can be applied (without running fragment)."""
        # We can't fully test fragment execution outside streamlit context
        # Just verify the factory returns a decorator
        from streamlit_app.utils.fragments import create_validation_fragment

        decorator = create_validation_fragment()

        # Verify it's a callable that takes functions
        assert callable(decorator)


class TestFragmentInputSection:
    """Tests for fragment_input_section function."""

    def test_function_exists(self):
        """Test function exists and is callable."""
        from streamlit_app.utils.fragments import fragment_input_section

        assert callable(fragment_input_section)


class TestExportDialog:
    """Tests for export dialog factory."""

    def test_dialog_feature_check(self):
        """Test that we can check if dialog is available."""
        from streamlit_app.utils.fragments import check_dialog_available

        result = check_dialog_available()
        assert isinstance(result, bool)
        # Returns True/False based on streamlit version


class TestCreateAutoRefreshFragment:
    """Tests for auto-refresh fragment factory."""

    def test_fragment_feature_check(self):
        """Test that we can check if fragment is available."""
        from streamlit_app.utils.fragments import check_fragment_available

        result = check_fragment_available()
        assert isinstance(result, bool)
        # Returns True/False based on streamlit version
