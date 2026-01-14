"""
Tests for Enhanced Error Handler (IMPL-004)
===========================================

Tests the new error handling features:
- ErrorContext dataclass
- handle_library_error()
- handle_validation_error()
- handle_visualization_error()
- error_boundary context manager

Author: Agent 6 (Background Agent)
Task: IMPL-004
"""

import pytest
from unittest.mock import patch, MagicMock
from utils.error_handler import (
    ErrorSeverity,
    ErrorContext,
    handle_library_error,
    handle_validation_error,
    handle_visualization_error,
    error_boundary,
    display_error_with_recovery,
)


class TestErrorContext:
    """Test ErrorContext dataclass"""

    def test_error_context_creation(self):
        """Test creating ErrorContext with all fields"""
        ctx = ErrorContext(
            severity=ErrorSeverity.ERROR,
            message="Test error",
            technical_details="ValueError: invalid input",
            recovery_steps=["Step 1", "Step 2"],
            can_continue=True,
            fallback_value=None,
        )

        assert ctx.severity == ErrorSeverity.ERROR
        assert ctx.message == "Test error"
        assert ctx.technical_details == "ValueError: invalid input"
        assert len(ctx.recovery_steps) == 2
        assert ctx.can_continue is True
        assert ctx.fallback_value is None

    def test_error_context_defaults(self):
        """Test ErrorContext with default values"""
        ctx = ErrorContext(
            severity=ErrorSeverity.WARNING,
            message="Warning message",
            technical_details="debug info",
            recovery_steps=[],
        )

        assert ctx.can_continue is False  # Default
        assert ctx.fallback_value is None  # Default


class TestHandleLibraryError:
    """Test handle_library_error() function"""

    def test_convergence_error(self):
        """Test handling convergence failure"""
        e = RuntimeError("Design convergence failed after 100 iterations")
        ctx = handle_library_error(e, "beam design")

        assert ctx.severity == ErrorSeverity.ERROR
        assert "converge" in ctx.message.lower()  # "converge" not "convergence"
        assert "RuntimeError" in ctx.technical_details
        assert len(ctx.recovery_steps) > 0
        assert "Increase beam depth" in ctx.recovery_steps[0]
        assert ctx.can_continue is False

    def test_xu_max_error(self):
        """Test handling neutral axis error"""
        e = ValueError("xu_max exceeded for given section")
        ctx = handle_library_error(e, "flexure design")

        assert ctx.severity == ErrorSeverity.ERROR
        assert (
            "over-reinforced" in ctx.message.lower()
            or "neutral axis" in ctx.message.lower()
        )
        assert len(ctx.recovery_steps) > 0
        assert ctx.can_continue is False

    def test_value_error(self):
        """Test handling generic ValueError"""
        e = ValueError("Invalid dimension value: -100")
        ctx = handle_library_error(e, "input validation")

        assert ctx.severity == ErrorSeverity.WARNING
        assert "Invalid input" in ctx.message
        assert "ValueError" in ctx.technical_details
        assert len(ctx.recovery_steps) > 0
        assert ctx.can_continue is True

    def test_generic_error(self):
        """Test handling unknown library error"""
        e = RuntimeError("Unknown error in calculation")
        ctx = handle_library_error(e, "shear design")

        assert ctx.severity == ErrorSeverity.ERROR
        assert "shear design" in ctx.message
        assert "RuntimeError" in ctx.technical_details
        assert len(ctx.recovery_steps) > 0


class TestHandleValidationError:
    """Test handle_validation_error() function"""

    def test_field_validation_error(self):
        """Test handling field validation error"""
        e = ValueError("Value must be positive")
        ctx = handle_validation_error(e, "beam_width")

        assert ctx.severity == ErrorSeverity.WARNING
        assert "beam_width" in ctx.message
        assert "must be positive" in ctx.message.lower()
        assert len(ctx.recovery_steps) > 0
        assert ctx.can_continue is True

    def test_range_validation_error(self):
        """Test handling range validation error"""
        e = ValueError("Value 50 is below minimum 150")
        ctx = handle_validation_error(e, "width_mm")

        assert ctx.severity == ErrorSeverity.WARNING
        assert "width_mm" in ctx.message
        assert "ValidationError" in ctx.technical_details
        assert len(ctx.recovery_steps) > 0


class TestHandleVisualizationError:
    """Test handle_visualization_error() function"""

    def test_plotly_duration_error(self):
        """Test handling Plotly duration type error"""
        e = ValueError("Invalid value of type 'str' for 'duration'")
        ctx = handle_visualization_error(e, "beam diagram")

        assert ctx.severity == ErrorSeverity.ERROR
        assert "configuration error" in ctx.message.lower()
        assert "duration" in ctx.technical_details.lower()
        assert len(ctx.recovery_steps) > 0
        assert ctx.can_continue is True

    def test_none_type_error(self):
        """Test handling NoneType comparison error"""
        e = TypeError("'>' not supported between instances of 'NoneType' and 'int'")
        ctx = handle_visualization_error(e, "strain distribution")

        assert ctx.severity == ErrorSeverity.WARNING
        assert "data unavailable" in ctx.message.lower()
        assert "NoneType" in ctx.technical_details
        assert len(ctx.recovery_steps) > 0
        assert ctx.can_continue is True

    def test_generic_chart_error(self):
        """Test handling generic chart rendering error"""
        e = RuntimeError("Chart rendering failed")
        ctx = handle_visualization_error(e, "moment diagram")

        assert ctx.severity == ErrorSeverity.WARNING
        assert "Could not render" in ctx.message
        assert len(ctx.recovery_steps) > 0
        assert ctx.can_continue is True


class TestDisplayErrorWithRecovery:
    """Test display_error_with_recovery() function"""

    @patch("utils.error_handler.st.error")
    @patch("utils.error_handler.logger.error")
    def test_display_error_message(self, mock_logger, mock_st_error):
        """Test error is displayed to user"""
        e = ValueError("Test error message")
        display_error_with_recovery(e, ErrorSeverity.ERROR)

        assert mock_st_error.called
        assert mock_logger.called

        # Check message contains error type and message
        call_args = str(mock_st_error.call_args)
        assert "ValueError" in call_args
        assert "Test error message" in call_args

    @patch("utils.error_handler.st.warning")
    @patch("utils.error_handler.logger.error")
    def test_display_warning_message(self, mock_logger, mock_st_warning):
        """Test warning is displayed to user"""
        e = ValueError("Test warning")
        display_error_with_recovery(e, ErrorSeverity.WARNING)

        assert mock_st_warning.called
        assert mock_logger.called


class TestErrorBoundary:
    """Test error_boundary context manager"""

    @patch("utils.error_handler.display_error_with_recovery")
    def test_error_boundary_catches_exception(self, mock_display):
        """Test error_boundary catches and handles exception"""
        with error_boundary(fallback_value=None, context="test operation"):
            raise ValueError("Test error")

        # Should not raise, should display error
        assert mock_display.called

    @patch("utils.error_handler.display_error_with_recovery")
    def test_error_boundary_no_exception(self, mock_display):
        """Test error_boundary does nothing if no exception"""
        result = []
        with error_boundary(fallback_value=None, context="test operation"):
            result.append(1)

        assert len(result) == 1
        assert not mock_display.called

    @patch("utils.error_handler.display_error_with_recovery")
    def test_error_boundary_show_error_false(self, mock_display):
        """Test error_boundary with show_error=False"""
        with error_boundary(fallback_value=None, show_error=False, context="test"):
            raise ValueError("Silent error")

        # Should not display error
        assert not mock_display.called

    @patch("utils.error_handler.logger.exception")
    def test_error_boundary_logs_error(self, mock_logger):
        """Test error_boundary logs exceptions"""
        with error_boundary(fallback_value=None, context="test operation"):
            raise RuntimeError("Test runtime error")

        assert mock_logger.called
        call_args = str(mock_logger.call_args)
        assert "test operation" in call_args.lower()
        assert "RuntimeError" in call_args


# =============================================================================
# Integration Tests
# =============================================================================


class TestErrorHandlerIntegration:
    """Integration tests for complete error handling flow"""

    @patch("utils.error_handler.st.error")
    def test_library_error_end_to_end(self, mock_st_error):
        """Test complete flow: library error -> context -> display"""
        e = RuntimeError("Design convergence failed")
        ctx = handle_library_error(e, "beam design")

        # Verify context is correct
        assert ctx.severity == ErrorSeverity.ERROR
        assert len(ctx.recovery_steps) > 0

        # Verify would display correctly
        display_error_with_recovery(e, ctx.severity)
        assert mock_st_error.called

    @patch("utils.error_handler.st.warning")
    def test_validation_error_end_to_end(self, mock_st_warning):
        """Test complete flow: validation error -> context -> display"""
        e = ValueError("Invalid width value")
        ctx = handle_validation_error(e, "width_mm")

        # Verify context
        assert ctx.severity == ErrorSeverity.WARNING
        assert ctx.can_continue is True

        # Verify would display as warning
        display_error_with_recovery(e, ctx.severity)
        assert mock_st_warning.called

    @patch("utils.error_handler.st.error")  # Changed from st.warning to st.error
    @patch("utils.error_handler.logger.exception")
    def test_error_boundary_with_visualization(self, mock_logger, mock_st_error):
        """Test error_boundary handling visualization error"""
        with error_boundary(context="beam diagram rendering"):
            # Simulate Plotly error
            raise ValueError("Invalid value for 'duration'")

        # Should catch and log
        assert mock_logger.called
        assert mock_st_error.called  # Default severity is ERROR, not WARNING


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
