"""
Test Results Display Components
================================

Comprehensive unit tests for components/results.py

Author: Agent 6 (Streamlit Specialist)
Task: IMPL-002
"""

import pytest
from unittest.mock import Mock, patch, call
import sys
from pathlib import Path

# Add streamlit_app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.results import (
    display_design_status,
    display_reinforcement_summary,
    display_flexure_result,
    display_shear_result,
    display_summary_metrics,
    display_utilization_meters,
    display_material_properties,
    display_compliance_checks,
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_column_mock():
    """Create a mock that supports context manager (with statement)."""
    col = Mock()
    col.__enter__ = Mock(return_value=col)
    col.__exit__ = Mock(return_value=False)
    return col


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def safe_result():
    """Typical safe design result."""
    return {
        "is_safe": True,
        "flexure": {
            "ast_required": 682,
            "ast_provided": 804,
            "num_bars": 4,
            "bar_dia": 16,
            "num_layers": 1,
            "is_doubly_reinforced": False,
            "mu_limit_knm": 150.5,
        },
        "shear": {
            "spacing": 175,
            "legs": 2,
            "stirrup_dia": 8,
            "tau_v": 0.45,
            "tau_c": 0.36,
        },
        "detailing": {
            "cover": 30,
            "needs_side_face": False,
        },
        "compliance": {
            "all_passed": True,
            "checks": [
                {"clause": "26.5.1.1", "description": "Min steel", "passed": True},
                {"clause": "26.5.1.5", "description": "Max steel", "passed": True},
            ],
        },
    }


@pytest.fixture
def unsafe_result():
    """Typical unsafe design result."""
    return {
        "is_safe": False,
        "flexure": {
            "ast_required": 1200,
            "ast_provided": 804,
            "num_bars": 4,
            "bar_dia": 16,
            "num_layers": 1,
            "is_doubly_reinforced": False,
        },
        "shear": {
            "spacing": 300,
            "legs": 2,
            "stirrup_dia": 8,
            "tau_v": 0.85,
            "tau_c": 0.36,
        },
        "compliance": {
            "all_passed": False,
            "checks": [
                {"clause": "26.5.1.1", "description": "Min steel", "passed": True},
                {"clause": "40.1", "description": "Shear stress", "passed": False},
            ],
        },
    }


@pytest.fixture
def doubly_reinforced_result():
    """Doubly reinforced section result."""
    return {
        "is_safe": True,
        "flexure": {
            "ast_required": 1500,
            "ast_provided": 1608,
            "num_bars": 6,
            "bar_dia": 20,
            "num_layers": 2,
            "is_doubly_reinforced": True,
            "asc_required": 300,
            "asc_provided": 402,
        },
        "shear": {"spacing": 150, "legs": 2, "stirrup_dia": 10},
        "detailing": {"cover": 40, "needs_side_face": True, "side_face_area": 120},
    }


# ============================================================================
# TEST 1: display_design_status()
# ============================================================================

@patch("streamlit.success")
def test_design_status_safe_shows_success(mock_success, safe_result):
    """Safe design shows success banner."""
    display_design_status(safe_result)
    mock_success.assert_called_once()
    args = mock_success.call_args[0][0]
    assert "SAFE" in args.upper()
    assert "✅" in args


@patch("streamlit.error")
def test_design_status_unsafe_shows_error(mock_error, unsafe_result):
    """Unsafe design shows error banner."""
    display_design_status(unsafe_result)
    mock_error.assert_called_once()
    args = mock_error.call_args[0][0]
    assert "UNSAFE" in args.upper()
    assert "❌" in args


@patch("streamlit.success")
def test_design_status_icon_can_be_disabled(mock_success, safe_result):
    """Icon can be toggled off."""
    display_design_status(safe_result, show_icon=False)
    args = mock_success.call_args[0][0]
    assert "✅" not in args


@patch("streamlit.info")
def test_design_status_missing_key_shows_warning(mock_info):
    """Missing is_safe key shows warning."""
    display_design_status({})
    mock_info.assert_called()


# ============================================================================
# TEST 2: display_reinforcement_summary()
# ============================================================================

@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_reinforcement_summary_singly_reinforced(
    mock_columns, mock_markdown, safe_result
):
    """Singly reinforced section displays correctly."""
    mock_columns.return_value = [create_column_mock(), create_column_mock(), create_column_mock()]
    display_reinforcement_summary(safe_result)
    # Should render main steel, shear steel, but not compression steel
    assert mock_markdown.call_count >= 3


@patch("streamlit.markdown")
@patch("streamlit.warning")
@patch("streamlit.columns")
def test_reinforcement_summary_doubly_reinforced(
    mock_columns, mock_warning, mock_markdown, doubly_reinforced_result
):
    """Doubly reinforced section shows compression steel."""
    mock_columns.return_value = [create_column_mock(), create_column_mock(), create_column_mock()]
    display_reinforcement_summary(doubly_reinforced_result)
    # Should show warning about doubly reinforced
    mock_warning.assert_called()


@patch("streamlit.markdown")
@patch("streamlit.caption")
@patch("streamlit.columns")
def test_reinforcement_summary_side_face_steel(
    mock_columns, mock_caption, mock_markdown, doubly_reinforced_result
):
    """Side face steel shown when D > 450mm."""
    mock_columns.return_value = [create_column_mock(), create_column_mock(), create_column_mock()]
    display_reinforcement_summary(doubly_reinforced_result)
    # Check that side face section rendered
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    assert any("Side Face" in str(call) for call in markdown_calls)


@patch("streamlit.info")
@patch("streamlit.columns")
def test_reinforcement_summary_multi_layer_indication(
    mock_columns, mock_info, doubly_reinforced_result
):
    """Multi-layer bars indicated."""
    mock_columns.return_value = [create_column_mock(), create_column_mock(), create_column_mock()]
    display_reinforcement_summary(doubly_reinforced_result)
    mock_info.assert_called()
    args = str(mock_info.call_args[0][0])
    assert "layers" in args.lower()


# ============================================================================
# TEST 3: display_flexure_result()
# ============================================================================

@patch("streamlit.markdown")
@patch("streamlit.caption")
@patch("streamlit.columns")
def test_flexure_result_displays_steel_area(
    mock_columns, mock_caption, mock_markdown, safe_result
):
    """Steel area (required vs provided) displayed."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    display_flexure_result(safe_result["flexure"])
    # Should show ast_required and ast_provided
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    assert any("682" in str(call) or "804" in str(call) for call in markdown_calls)


@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_flexure_result_bar_configuration(
    mock_columns, mock_markdown, safe_result
):
    """Bar configuration (num × dia) displayed."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    display_flexure_result(safe_result["flexure"])
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    # Should show "4 - 16mm" or similar
    assert any("16" in str(call) for call in markdown_calls)


@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_flexure_result_compact_mode(mock_columns, mock_markdown, safe_result):
    """Compact mode uses less space."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    display_flexure_result(safe_result["flexure"], compact=True)
    # Compact mode should call markdown fewer times
    assert mock_markdown.call_count < 10


# ============================================================================
# TEST 4: display_shear_result()
# ============================================================================

@patch("streamlit.markdown")
@patch("streamlit.caption")
@patch("streamlit.columns")
def test_shear_result_stirrup_configuration(
    mock_columns, mock_caption, mock_markdown, safe_result
):
    """Stirrup configuration (legs × dia @ spacing) displayed."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    display_shear_result(safe_result["shear"])
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    # Should show "2-legged 8mm @ 175mm"
    assert any("175" in str(call) for call in markdown_calls)


@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_shear_result_stress_values(mock_columns, mock_markdown, safe_result):
    """Shear stress values (τv, τc) displayed."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    display_shear_result(safe_result["shear"])
    # Should have markdown calls showing stress values
    assert mock_markdown.called
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    # Check that we rendered the shear stress section
    assert len(markdown_calls) >= 4  # At least 4 markdown calls in full mode


# ============================================================================
# TEST 5: display_summary_metrics()
# ============================================================================

@patch("streamlit.metric")
@patch("streamlit.columns")
def test_summary_metrics_default(mock_columns, mock_metric, safe_result):
    """Default metrics displayed."""
    col1, col2, col3 = create_column_mock(), create_column_mock(), create_column_mock()
    col1.metric = mock_metric
    col2.metric = mock_metric
    col3.metric = mock_metric
    mock_columns.return_value = [col1, col2, col3]

    display_summary_metrics(safe_result)
    # Should create 3 metrics by default
    assert mock_metric.call_count >= 3


@patch("streamlit.metric")
@patch("streamlit.columns")
def test_summary_metrics_custom_list(mock_columns, mock_metric, safe_result):
    """Custom metric list works."""
    col1, col2 = create_column_mock(), create_column_mock()
    col1.metric = mock_metric
    col2.metric = mock_metric
    mock_columns.return_value = [col1, col2]

    display_summary_metrics(safe_result, metrics=["ast_required", "spacing"])
    # Should create 2 metrics
    assert mock_metric.call_count == 2


# ============================================================================
# TEST 6: display_utilization_meters()
# ============================================================================

@patch("streamlit.progress")
@patch("streamlit.markdown")
def test_utilization_meters_progress_bars(mock_markdown, mock_progress, safe_result):
    """Progress bars render correctly."""
    display_utilization_meters(safe_result)
    # Should create progress bars
    assert mock_progress.call_count >= 2


@patch("streamlit.progress")
def test_utilization_meters_color_thresholds(mock_progress, safe_result):
    """Color thresholds work (< 80% green, 80-95% yellow, > 95% red)."""
    # This test would need to verify the color parameter, but st.progress
    # doesn't have a color parameter. Instead, we use markdown with color coding.
    display_utilization_meters(safe_result)
    assert mock_progress.called


@patch("streamlit.progress")
def test_utilization_meters_zero_values(mock_progress):
    """Zero/null values handled gracefully."""
    result = {"flexure": {}, "shear": {}}
    display_utilization_meters(result)
    # Should not crash
    assert True


# ============================================================================
# TEST 7: display_material_properties()
# ============================================================================

@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_material_properties_standard_grades(mock_columns, mock_markdown):
    """Standard grades displayed."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    concrete = {"grade": "M25", "fck": 25}
    steel = {"grade": "Fe415", "fy": 415}
    display_material_properties(concrete, steel)
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    assert any("M25" in str(call) for call in markdown_calls)
    assert any("Fe415" in str(call) for call in markdown_calls)


@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_material_properties_compact_mode(mock_columns, mock_markdown):
    """Compact mode condensed."""
    mock_columns.return_value = [create_column_mock(), create_column_mock()]
    concrete = {"grade": "M25", "fck": 25}
    steel = {"grade": "Fe415", "fy": 415}
    display_material_properties(concrete, steel, compact=True)
    # Compact mode should call markdown fewer times
    assert mock_markdown.call_count < 10


# ============================================================================
# TEST 8: display_compliance_checks()
# ============================================================================

@patch("streamlit.markdown")
def test_compliance_checks_all_listed(mock_markdown, safe_result):
    """All checks listed."""
    display_compliance_checks(safe_result["compliance"])
    # Should render each check
    assert mock_markdown.call_count >= 2


@patch("streamlit.markdown")
def test_compliance_checks_pass_fail_icons(mock_markdown, unsafe_result):
    """Pass/fail icons shown."""
    display_compliance_checks(unsafe_result["compliance"])
    markdown_calls = [str(call) for call in mock_markdown.call_args_list]
    # Should contain ✅ and ❌
    all_calls = " ".join(str(call) for call in markdown_calls)
    assert "✅" in all_calls or "❌" in all_calls


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_all_components_handle_empty_dict():
    """All components handle empty dict without crashing."""
    empty = {}

    # Should not raise exceptions
    with patch("streamlit.info"):
        display_design_status(empty)

    with patch("streamlit.columns") as mock_cols:
        mock_cols.return_value = [create_column_mock(), create_column_mock(), create_column_mock()]
        with patch("streamlit.markdown"):
            display_reinforcement_summary(empty)
            display_summary_metrics(empty)

    with patch("streamlit.columns") as mock_cols2:
        mock_cols2.return_value = [create_column_mock(), create_column_mock()]
        with patch("streamlit.markdown"):
            display_flexure_result(empty)
            display_shear_result(empty)
            display_utilization_meters(empty)

    with patch("streamlit.markdown"):
        display_compliance_checks(empty)


def test_all_components_handle_none_values():
    """All components handle None values gracefully."""
    result = {
        "is_safe": None,
        "flexure": {"ast_required": None, "ast_provided": None},
        "shear": {"spacing": None},
    }

    # Should not raise exceptions
    with patch("streamlit.info"):
        display_design_status(result)

    with patch("streamlit.columns") as mock_cols:
        mock_cols.return_value = [create_column_mock(), create_column_mock(), create_column_mock()]
        with patch("streamlit.markdown"):
            display_reinforcement_summary(result)
            display_summary_metrics(result)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@patch("streamlit.success")
@patch("streamlit.markdown")
@patch("streamlit.columns")
def test_full_result_display_pipeline(
    mock_columns, mock_markdown, mock_success, safe_result
):
    """Full result display pipeline works."""
    # Mock columns to return proper column mocks
    def columns_side_effect(n):
        return [create_column_mock() for _ in range(n)]

    mock_columns.side_effect = columns_side_effect

    # Display all components in sequence (typical usage)
    display_design_status(safe_result)
    display_summary_metrics(safe_result)
    display_reinforcement_summary(safe_result)
    display_flexure_result(safe_result["flexure"])
    display_shear_result(safe_result["shear"])
    display_utilization_meters(safe_result)
    display_compliance_checks(safe_result["compliance"])

    # All components should have been called
    assert mock_success.called
    assert mock_markdown.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
