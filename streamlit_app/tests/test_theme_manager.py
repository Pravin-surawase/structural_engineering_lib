"""
Tests for Theme Manager (UI-004)

Tests dark mode toggle, theme persistence, and CSS injection.
"""

import pytest
import streamlit as st
from utils.theme_manager import (
    initialize_theme,
    get_current_theme,
    set_theme,
    toggle_theme,
    get_theme_colors,
    ThemeMode
)


class TestThemeInitialization:
    """Test theme initialization."""

    def test_initialize_theme_creates_session_state(self, clean_session_state):
        """Test that initialize_theme creates required session state keys."""
        initialize_theme()

        assert "theme_mode" in st.session_state
        assert "use_dark_mode" in st.session_state
        assert st.session_state.theme_mode == "light"
        assert st.session_state.use_dark_mode is False

    def test_initialize_theme_preserves_existing(self, clean_session_state):
        """Test that initialize_theme doesn't override existing values."""
        st.session_state.theme_mode = "dark"
        st.session_state.use_dark_mode = True

        initialize_theme()

        assert st.session_state.theme_mode == "dark"
        assert st.session_state.use_dark_mode is True


class TestThemeGetters:
    """Test theme getter functions."""

    def test_get_current_theme_default(self, clean_session_state):
        """Test get_current_theme returns default."""
        theme = get_current_theme()
        assert theme == "light"

    def test_get_current_theme_dark(self, clean_session_state):
        """Test get_current_theme with dark mode."""
        st.session_state.theme_mode = "dark"
        st.session_state.use_dark_mode = True

        theme = get_current_theme()
        assert theme == "dark"


class TestThemeSetters:
    """Test theme setter functions."""

    def test_set_theme_light(self, clean_session_state):
        """Test setting light theme."""
        set_theme("light")

        assert st.session_state.theme_mode == "light"
        assert st.session_state.use_dark_mode is False

    def test_set_theme_dark(self, clean_session_state):
        """Test setting dark theme."""
        set_theme("dark")

        assert st.session_state.theme_mode == "dark"
        assert st.session_state.use_dark_mode is True

    def test_set_theme_auto(self, clean_session_state):
        """Test setting auto theme."""
        set_theme("auto")

        assert st.session_state.theme_mode == "auto"
        # auto mode doesn't set use_dark_mode to True


class TestThemeToggle:
    """Test theme toggle functionality."""

    def test_toggle_from_light_to_dark(self, clean_session_state):
        """Test toggling from light to dark."""
        st.session_state.use_dark_mode = False
        st.session_state.theme_mode = "light"

        toggle_theme()

        assert st.session_state.use_dark_mode is True
        assert st.session_state.theme_mode == "dark"

    def test_toggle_from_dark_to_light(self, clean_session_state):
        """Test toggling from dark to light."""
        st.session_state.use_dark_mode = True
        st.session_state.theme_mode = "dark"

        toggle_theme()

        assert st.session_state.use_dark_mode is False
        assert st.session_state.theme_mode == "light"

    def test_toggle_multiple_times(self, clean_session_state):
        """Test toggling multiple times."""
        initial_state = False
        st.session_state.use_dark_mode = initial_state

        toggle_theme()
        assert st.session_state.use_dark_mode is not initial_state

        toggle_theme()
        assert st.session_state.use_dark_mode is initial_state


class TestThemeColors:
    """Test theme color retrieval."""

    def test_get_theme_colors_light_mode(self, clean_session_state):
        """Test getting colors in light mode."""
        st.session_state.use_dark_mode = False

        colors = get_theme_colors()

        assert "bg_primary" in colors
        assert "text_primary" in colors
        assert "primary" in colors
        assert "accent" in colors

        # Check that colors are valid hex codes
        assert colors["primary"].startswith("#")
        assert len(colors["primary"]) == 7

    def test_get_theme_colors_dark_mode(self, clean_session_state):
        """Test getting colors in dark mode."""
        st.session_state.use_dark_mode = True

        colors = get_theme_colors()

        assert "bg_primary" in colors
        assert "text_primary" in colors
        assert "primary" in colors
        assert "accent" in colors

        # Dark mode should have different colors
        assert colors["bg_primary"] != "#FAFAFA"  # Not light mode gray

    def test_get_theme_colors_all_keys(self, clean_session_state):
        """Test that all required color keys are present."""
        colors = get_theme_colors()

        required_keys = [
            "bg_primary",
            "bg_secondary",
            "bg_tertiary",
            "text_primary",
            "text_secondary",
            "text_tertiary",
            "border_primary",
            "border_secondary",
            "primary",
            "primary_hover",
            "accent",
            "accent_hover",
        ]

        for key in required_keys:
            assert key in colors, f"Missing color key: {key}"


class TestThemePersistence:
    """Test theme persistence across function calls."""

    def test_theme_persists_after_toggle(self, clean_session_state):
        """Test that theme persists after toggling."""
        initialize_theme()

        # Toggle to dark
        toggle_theme()
        dark_theme = get_current_theme()

        # Initialize again (simulates page reload)
        initialize_theme()

        # Theme should persist
        assert get_current_theme() == dark_theme

    def test_theme_colors_consistent_for_mode(self, clean_session_state):
        """Test that theme colors are consistent for the same mode."""
        st.session_state.use_dark_mode = True

        colors1 = get_theme_colors()
        colors2 = get_theme_colors()

        assert colors1 == colors2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_initialize_with_invalid_state(self, clean_session_state):
        """Test initialize handles invalid existing state."""
        st.session_state.theme_mode = "invalid"

        initialize_theme()

        # Should preserve the value (doesn't validate)
        assert st.session_state.theme_mode == "invalid"

    def test_get_colors_without_initialization(self, clean_session_state):
        """Test get_theme_colors works without explicit initialization."""
        # Don't call initialize_theme
        colors = get_theme_colors()

        # Should initialize automatically
        assert colors is not None
        assert "primary" in colors


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestThemeIntegration:
    """Integration tests for theme system."""

    def test_full_theme_workflow(self, clean_session_state):
        """Test complete theme workflow."""
        # 1. Initialize
        initialize_theme()
        assert get_current_theme() == "light"

        # 2. Set to dark
        set_theme("dark")
        assert get_current_theme() == "dark"

        # 3. Get colors
        colors = get_theme_colors()
        assert colors["bg_primary"] == "#0F1419"  # Dark mode bg

        # 4. Toggle back
        toggle_theme()
        assert get_current_theme() == "light"

        # 5. Get colors again
        colors = get_theme_colors()
        assert colors["bg_primary"] != "#0F1419"  # Not dark mode anymore

    def test_theme_switching_performance(self, clean_session_state):
        """Test that theme switching is fast."""
        import time

        initialize_theme()

        start = time.time()
        for _ in range(100):
            toggle_theme()
        elapsed = time.time() - start

        # Should complete 100 toggles in under 1 second
        assert elapsed < 1.0

    def test_concurrent_color_requests(self, clean_session_state):
        """Test that multiple color requests return consistent results."""
        st.session_state.use_dark_mode = True

        colors_list = [get_theme_colors() for _ in range(10)]

        # All should be identical
        for colors in colors_list[1:]:
            assert colors == colors_list[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
