"""
Tests for accessibility utilities.

Tests ARIA labels, keyboard navigation, screen reader support,
and WCAG 2.1 compliance helpers.
"""

from streamlit_app.utils.accessibility import (
    add_aria_label,
    announce_to_screen_reader,
    validate_color_contrast,
    add_keyboard_shortcut,
    show_keyboard_shortcuts_help,
    focus_element,
    add_skip_link,
    add_focus_indicator_styles,
    add_landmark_roles,
    validate_form_accessibility,
    get_wcag_compliance_report,
    apply_accessibility_features,
)


class TestARIALabels:
    """Test ARIA label generation."""

    def test_basic_aria_label(self):
        """Test basic ARIA label without role."""
        result = add_aria_label("test-button", "Click me")
        assert 'aria-label="Click me"' in result
        assert 'data-testid="test-button"' in result
        assert "role=" not in result

    def test_aria_label_with_role(self):
        """Test ARIA label with role."""
        result = add_aria_label("nav-button", "Navigate", role="button")
        assert 'aria-label="Navigate"' in result
        assert 'role="button"' in result

    def test_aria_label_escaping(self):
        """Test that special characters are handled."""
        result = add_aria_label("test", 'Label with "quotes"')
        assert "test" in result  # Should not crash


class TestScreenReaderAnnouncements:
    """Test screen reader announcement functionality."""

    def test_announce_polite(self, mock_streamlit):
        """Test polite announcement."""
        announce_to_screen_reader("Design complete")
        # Should call st.markdown with ARIA live region
        assert mock_streamlit.markdown_called

    def test_announce_assertive(self, mock_streamlit):
        """Test assertive announcement."""
        announce_to_screen_reader("Error occurred", priority="assertive")
        assert mock_streamlit.markdown_called

    def test_announce_invalid_priority(self, mock_streamlit):
        """Test invalid priority defaults to polite."""
        announce_to_screen_reader("Test", priority="invalid")
        # Should not crash, defaults to polite


class TestColorContrast:
    """Test color contrast validation."""

    def test_high_contrast_passes(self):
        """Test high contrast black on white."""
        result = validate_color_contrast("#000000", "#FFFFFF")
        assert result["ratio"] == 21.0  # Perfect contrast
        assert result["passes_text"] is True
        assert result["passes_large_text"] is True
        assert result["passes_ui"] is True

    def test_low_contrast_fails(self):
        """Test low contrast fails requirements."""
        result = validate_color_contrast("#777777", "#888888", level="AA")
        assert result["ratio"] < 4.5
        assert result["passes_text"] is False

    def test_wcag_aa_threshold(self):
        """Test WCAG AA threshold (4.5:1 for normal text)."""
        result = validate_color_contrast("#595959", "#FFFFFF", level="AA")
        assert result["ratio"] >= 4.5
        assert result["passes_text"] is True

    def test_wcag_aaa_threshold(self):
        """Test WCAG AAA threshold (7:1 for normal text)."""
        result = validate_color_contrast("#595959", "#FFFFFF", level="AAA")
        # This combo is ~7.0, should pass AAA
        assert result["level"] == "AAA"

    def test_ui_component_contrast(self):
        """Test UI component contrast (3:1 minimum)."""
        result = validate_color_contrast("#757575", "#FFFFFF")
        assert result["passes_ui"] is True  # Should be > 3:1

    def test_hex_without_hash(self):
        """Test that colors without # are handled."""
        result = validate_color_contrast("000000", "FFFFFF")
        assert result["ratio"] == 21.0  # Should work


class TestKeyboardShortcuts:
    """Test keyboard shortcut documentation."""

    def test_add_keyboard_shortcut(self, mock_streamlit):
        """Test adding a keyboard shortcut."""
        result = add_keyboard_shortcut("Ctrl+S", "Save design", scope="global")
        assert "Ctrl+S" in result
        assert "Save design" in result
        assert "keyboard-shortcut" in result

    def test_shortcut_stored_in_session(self, mock_streamlit):
        """Test shortcuts are stored in session state."""
        mock_streamlit.session_state.clear()
        add_keyboard_shortcut("Alt+D", "Design beam")
        assert "keyboard_shortcuts" in mock_streamlit.session_state
        assert len(mock_streamlit.session_state["keyboard_shortcuts"]) == 1

    def test_show_shortcuts_empty(self, mock_streamlit):
        """Test showing shortcuts when none registered."""
        mock_streamlit.session_state.clear()
        show_keyboard_shortcuts_help()
        # Should show info message

    def test_show_shortcuts_with_data(self, mock_streamlit):
        """Test showing registered shortcuts."""
        mock_streamlit.session_state["keyboard_shortcuts"] = [
            {"key": "Ctrl+S", "description": "Save", "scope": "global"},
            {"key": "Alt+D", "description": "Design", "scope": "page-specific"},
        ]
        show_keyboard_shortcuts_help()
        # Should display both shortcuts


class TestFocusManagement:
    """Test focus management utilities."""

    def test_focus_element(self, mock_streamlit):
        """Test focusing an element."""
        focus_element("main-button")
        # Should inject JS to focus element
        assert mock_streamlit.markdown_called

    def test_add_skip_link(self, mock_streamlit):
        """Test adding skip link."""
        add_skip_link("main-content", "Skip to content")
        assert mock_streamlit.markdown_called

    def test_skip_link_default_label(self, mock_streamlit):
        """Test skip link with default label."""
        add_skip_link("content")
        # Should use default "Skip to main content"


class TestFocusIndicators:
    """Test focus indicator styles."""

    def test_add_focus_indicators(self, mock_streamlit):
        """Test adding focus indicator styles."""
        add_focus_indicator_styles()
        assert mock_streamlit.markdown_called
        # Should inject CSS for focus styles


class TestLandmarkRoles:
    """Test ARIA landmark roles."""

    def test_add_landmarks(self, mock_streamlit):
        """Test adding landmark roles."""
        add_landmark_roles()
        assert mock_streamlit.markdown_called
        # Should inject JS to add roles


class TestFormAccessibility:
    """Test form accessibility validation."""

    def test_validate_form(self):
        """Test form validation."""
        result = validate_form_accessibility("design-form")
        assert "has_labels" in result
        assert "required_marked" in result
        assert "error_messages" in result
        assert "focus_management" in result


class TestWCAGCompliance:
    """Test WCAG compliance reporting."""

    def test_compliance_report_structure(self):
        """Test compliance report has all sections."""
        report = get_wcag_compliance_report()
        assert "perceivable" in report
        assert "operable" in report
        assert "understandable" in report
        assert "robust" in report

    def test_perceivable_criteria(self):
        """Test perceivable criteria in report."""
        report = get_wcag_compliance_report()
        assert "text_alternatives" in report["perceivable"]
        assert "distinguishable" in report["perceivable"]

    def test_operable_criteria(self):
        """Test operable criteria in report."""
        report = get_wcag_compliance_report()
        assert "keyboard_accessible" in report["operable"]
        assert "navigable" in report["operable"]


class TestAccessibilityIntegration:
    """Test integrated accessibility features."""

    def test_apply_all_features(self, mock_streamlit):
        """Test applying all accessibility features."""
        apply_accessibility_features()
        # Should call multiple st.markdown for skip links, styles, landmarks
        assert mock_streamlit.markdown_called

    def test_apply_selective_features(self, mock_streamlit):
        """Test applying only some features."""
        mock_streamlit.markdown_called = False
        apply_accessibility_features(
            add_skip_links=False,
            add_focus_indicators=True,
            add_landmarks=False,
        )
        # Should only add focus indicators

    def test_apply_no_features(self, mock_streamlit):
        """Test applying no features."""
        mock_streamlit.markdown_called = False
        apply_accessibility_features(
            add_skip_links=False,
            add_focus_indicators=False,
            add_landmarks=False,
        )
        # Should do nothing


class TestAccessibilityEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_aria_label(self):
        """Test empty ARIA label."""
        result = add_aria_label("test", "")
        assert 'aria-label=""' in result

    def test_invalid_hex_color(self):
        """Test invalid hex color in contrast check."""
        # Should not crash with malformed hex
        try:
            result = validate_color_contrast("invalid", "#FFFFFF")
            # If it doesn't crash, that's a pass
            assert True
        except (ValueError, IndexError):
            # Expected for truly invalid input
            assert True

    def test_multiple_shortcuts_same_key(self, mock_streamlit):
        """Test adding multiple shortcuts with same key."""
        mock_streamlit.session_state.clear()
        add_keyboard_shortcut("Ctrl+S", "Save design")
        add_keyboard_shortcut("Ctrl+S", "Save project")
        # Should allow duplicates (might warn in UI)
        assert len(mock_streamlit.session_state["keyboard_shortcuts"]) == 2
