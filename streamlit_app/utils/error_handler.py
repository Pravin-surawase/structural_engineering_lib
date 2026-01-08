"""
Error Handler for Streamlit UI
================================

Comprehensive error handling and user-friendly error messages.

Features:
- Catches all library exceptions
- Converts technical errors to user-friendly messages
- Provides actionable fix suggestions
- Logs errors for debugging
- Handles validation errors
- Graceful degradation

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: STREAMLIT-IMPL-009
"""

import streamlit as st
import logging
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Error Severity Levels
# =============================================================================

class ErrorSeverity(Enum):
    """Error severity classification"""
    INFO = "info"        # Informational, no action needed
    WARNING = "warning"  # Warning, but can proceed
    ERROR = "error"      # Error, cannot proceed
    CRITICAL = "critical"  # Critical system error


@dataclass
class ErrorMessage:
    """
    Structured error message.

    Attributes:
        severity: Error severity level
        title: Short error title
        message: Detailed error message
        fix_suggestions: List of actionable fixes
        technical_details: Technical details (for logging)
        clause_reference: IS 456 clause reference (if applicable)
    """
    severity: ErrorSeverity
    title: str
    message: str
    fix_suggestions: list[str]
    technical_details: Optional[str] = None
    clause_reference: Optional[str] = None


# =============================================================================
# Error Message Templates
# =============================================================================

def create_dimension_error(
    dim_name: str,
    actual: float,
    minimum: float,
    maximum: float,
    unit: str = "mm"
) -> ErrorMessage:
    """
    Create error for dimension out of range.

    Args:
        dim_name: Dimension name (e.g., "Span", "Width", "Depth")
        actual: Actual value provided
        minimum: Minimum allowed value
        maximum: Maximum allowed value
        unit: Unit of measurement

    Returns:
        ErrorMessage object
    """
    if actual < minimum:
        return ErrorMessage(
            severity=ErrorSeverity.ERROR,
            title=f"{dim_name} Too Small",
            message=f"{dim_name} of {actual:,.0f}{unit} is below minimum allowed value of {minimum:,.0f}{unit}.",
            fix_suggestions=[
                f"Increase {dim_name.lower()} to at least {minimum:,.0f}{unit}",
                f"Check if you entered the value in correct units ({unit})",
                "Refer to IS 456:2000 for minimum dimension requirements"
            ],
            technical_details=f"Dimension validation failed: {actual} < {minimum}"
        )
    else:  # actual > maximum
        return ErrorMessage(
            severity=ErrorSeverity.ERROR,
            title=f"{dim_name} Too Large",
            message=f"{dim_name} of {actual:,.0f}{unit} exceeds maximum allowed value of {maximum:,.0f}{unit}.",
            fix_suggestions=[
                f"Reduce {dim_name.lower()} to at most {maximum:,.0f}{unit}",
                "Consider using multiple beams or different structural system",
                "Consult a structural engineer for large spans"
            ],
            technical_details=f"Dimension validation failed: {actual} > {maximum}"
        )


def create_material_error(
    fck: float,
    fy: float
) -> ErrorMessage:
    """
    Create error for invalid material combination.

    Args:
        fck: Concrete strength (MPa)
        fy: Steel yield strength (MPa)

    Returns:
        ErrorMessage object
    """
    valid_fck = [15, 20, 25, 30, 35, 40, 45, 50]
    valid_fy = [250, 415, 500, 550]

    errors = []
    if fck not in valid_fck:
        errors.append(f"Concrete grade M{int(fck)} is not standard")
    if fy not in valid_fy:
        errors.append(f"Steel grade Fe{int(fy)} is not standard")

    return ErrorMessage(
        severity=ErrorSeverity.ERROR,
        title="Invalid Material Grade",
        message=f"Material combination fck={fck} MPa, fy={fy} MPa is not valid. " + " ".join(errors),
        fix_suggestions=[
            f"Use standard concrete grades: {', '.join(f'M{int(g)}' for g in valid_fck)}",
            f"Use standard steel grades: {', '.join(f'Fe{int(g)}' for g in valid_fy)}",
            "Most common: M25 concrete with Fe500 steel"
        ],
        technical_details=f"Invalid material: fck={fck}, fy={fy}",
        clause_reference="IS 456:2000 Table 2 & Annex C"
    )


def create_load_error(
    load_type: str,
    actual: float,
    limit: float,
    unit: str = "kN"
) -> ErrorMessage:
    """
    Create error for invalid load value.

    Args:
        load_type: Type of load ("Moment", "Shear", etc.)
        actual: Actual load value
        limit: Limit value
        unit: Unit of measurement

    Returns:
        ErrorMessage object
    """
    return ErrorMessage(
        severity=ErrorSeverity.ERROR,
        title=f"Invalid {load_type}",
        message=f"{load_type} value of {actual:,.1f}{unit} is invalid or exceeds practical limits.",
        fix_suggestions=[
            f"Check if {load_type.lower()} calculation is correct",
            f"Verify units are correct ({unit}, not N or kgf)",
            "Recalculate loads using IS 875 (Loads code)",
            "For very large loads, consider larger section or prestressed concrete"
        ],
        technical_details=f"Load validation failed: {load_type}={actual}{unit}, limit={limit}{unit}"
    )


def create_design_failure_error(
    reason: str,
    capacity: Optional[float] = None,
    demand: Optional[float] = None,
    clause: Optional[str] = None
) -> ErrorMessage:
    """
    Create error for design failure.

    Args:
        reason: Reason for failure
        capacity: Capacity value (if applicable)
        demand: Demand value (if applicable)
        clause: IS 456 clause reference

    Returns:
        ErrorMessage object
    """
    message = f"Design failed: {reason}."
    if capacity and demand:
        message += f" Capacity={capacity:.2f}, Demand={demand:.2f}."

    return ErrorMessage(
        severity=ErrorSeverity.ERROR,
        title="Design Does Not Meet Requirements",
        message=message,
        fix_suggestions=[
            "Increase beam section size (width or depth)",
            "Use higher grade concrete (e.g., M30 instead of M25)",
            "Use higher grade steel (e.g., Fe500 instead of Fe415)",
            "Reduce applied loads if possible",
            "Add compression reinforcement (if moment failure)"
        ],
        technical_details=f"Design failure: {reason}",
        clause_reference=clause
    )


def create_compliance_error(
    clause: str,
    requirement: str,
    provided: float,
    required: float,
    unit: str = "mm"
) -> ErrorMessage:
    """
    Create error for IS 456 compliance violation.

    Args:
        clause: IS 456 clause number
        requirement: Description of requirement
        provided: Value provided
        required: Value required
        unit: Unit of measurement

    Returns:
        ErrorMessage object
    """
    margin = provided - required
    margin_pct = (margin / required) * 100 if required > 0 else 0

    return ErrorMessage(
        severity=ErrorSeverity.ERROR,
        title=f"IS 456 Compliance Failure - {clause}",
        message=f"{requirement}: Provided {provided:,.1f}{unit}, Required {required:,.1f}{unit}. "
                f"Deficit: {-margin:,.1f}{unit} ({-margin_pct:.1f}%).",
        fix_suggestions=[
            f"Increase provided value to at least {required:,.1f}{unit}",
            "Review IS 456 clause requirements carefully",
            "Consider alternative design approach",
            "Consult structural design manual (SP:16)"
        ],
        technical_details=f"Compliance check failed: {clause}",
        clause_reference=f"IS 456:2000 {clause}"
    )


def create_convergence_error(
    iterations: int,
    tolerance: float
) -> ErrorMessage:
    """
    Create error for convergence failure.

    Args:
        iterations: Number of iterations attempted
        tolerance: Target tolerance

    Returns:
        ErrorMessage object
    """
    return ErrorMessage(
        severity=ErrorSeverity.ERROR,
        title="Design Algorithm Did Not Converge",
        message=f"Design calculations did not converge after {iterations} iterations (tolerance={tolerance}).",
        fix_suggestions=[
            "Increase beam depth significantly (+100mm or more)",
            "Try different initial section size",
            "Use higher concrete grade (M30 or M35)",
            "Check if loads are realistic for the span",
            "This may indicate an over-reinforced section - increase section size"
        ],
        technical_details=f"Convergence failure: {iterations} iterations, tolerance={tolerance}"
    )


def create_input_validation_error(
    field_name: str,
    error_details: str
) -> ErrorMessage:
    """
    Create error for input validation failure.

    Args:
        field_name: Name of input field
        error_details: Details of what's wrong

    Returns:
        ErrorMessage object
    """
    return ErrorMessage(
        severity=ErrorSeverity.WARNING,
        title=f"Invalid Input - {field_name}",
        message=f"The value entered for '{field_name}' is invalid: {error_details}",
        fix_suggestions=[
            "Check if the value is in the correct range",
            "Verify units are correct (mm, kN, kNm, MPa)",
            "Ensure numeric values only (no letters or special characters)",
            "Try using example values first to verify app works"
        ],
        technical_details=f"Input validation: {field_name} - {error_details}"
    )


def create_generic_error(
    error: Exception
) -> ErrorMessage:
    """
    Create generic error message from exception.

    Args:
        error: Exception object

    Returns:
        ErrorMessage object
    """
    return ErrorMessage(
        severity=ErrorSeverity.CRITICAL,
        title="Unexpected Error",
        message="An unexpected error occurred while processing your request. "
                "This has been logged and will be investigated.",
        fix_suggestions=[
            "Try refreshing the page and entering values again",
            "Check if all inputs are filled correctly",
            "Try using example values to verify app works",
            "If problem persists, please contact support with error details below"
        ],
        technical_details=f"{type(error).__name__}: {str(error)}"
    )


# =============================================================================
# Display Functions
# =============================================================================

def display_error_message(error_msg: ErrorMessage):
    """
    Display error message in Streamlit UI.

    Args:
        error_msg: ErrorMessage object to display
    """
    # Icon mapping
    icons = {
        ErrorSeverity.INFO: "ℹ️",
        ErrorSeverity.WARNING: "⚠️",
        ErrorSeverity.ERROR: "❌",
        ErrorSeverity.CRITICAL: "🚨"
    }

    # Display function mapping
    display_funcs = {
        ErrorSeverity.INFO: st.info,
        ErrorSeverity.WARNING: st.warning,
        ErrorSeverity.ERROR: st.error,
        ErrorSeverity.CRITICAL: st.error
    }

    icon = icons.get(error_msg.severity, "❌")
    display_func = display_funcs.get(error_msg.severity, st.error)

    # Build message
    message_parts = [f"{icon} **{error_msg.title}**", "", error_msg.message]

    # Add fix suggestions
    if error_msg.fix_suggestions:
        message_parts.append("")
        message_parts.append("**How to fix:**")
        for i, suggestion in enumerate(error_msg.fix_suggestions, 1):
            message_parts.append(f"{i}. {suggestion}")

    # Add clause reference
    if error_msg.clause_reference:
        message_parts.append("")
        message_parts.append(f"📖 *Reference: {error_msg.clause_reference}*")

    # Display
    display_func("\n".join(message_parts))

    # Log technical details
    if error_msg.technical_details:
        logger.error(f"[{error_msg.severity.value.upper()}] {error_msg.title}: {error_msg.technical_details}")

        # Show technical details in expander (for debugging)
        with st.expander("🔍 Technical Details (for debugging)"):
            st.code(error_msg.technical_details)


# =============================================================================
# Error Handler Decorator
# =============================================================================

def handle_errors(
    default_message: str = "An error occurred during processing",
    show_traceback: bool = False
):
    """
    Decorator for handling errors in Streamlit functions.

    Args:
        default_message: Default message if error type unknown
        show_traceback: Whether to show full traceback

    Example:
        @handle_errors(default_message="Failed to analyze beam design")
        def analyze_beam():
            # ... code that might raise exceptions ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                # Input validation errors
                error_msg = create_input_validation_error(
                    field_name=func.__name__,
                    error_details=str(e)
                )
                display_error_message(error_msg)
                return None
            except KeyError as e:
                # Missing data errors
                error_msg = ErrorMessage(
                    severity=ErrorSeverity.ERROR,
                    title="Missing Data",
                    message=f"Required data not found: {str(e)}",
                    fix_suggestions=[
                        "Ensure all input fields are filled",
                        "Try refreshing the page",
                        "Check if you navigated from another page (data may not be passed)"
                    ],
                    technical_details=f"KeyError: {str(e)}"
                )
                display_error_message(error_msg)
                return None
            except Exception as e:
                # Generic error
                error_msg = create_generic_error(e)
                display_error_message(error_msg)

                # Log full exception
                logger.exception(f"Unhandled exception in {func.__name__}")

                # Show traceback if requested
                if show_traceback:
                    st.exception(e)

                return None
        return wrapper
    return decorator


# =============================================================================
# Validation Helper Functions
# =============================================================================

def validate_dimension_range(
    value: float,
    min_val: float,
    max_val: float,
    name: str,
    unit: str = "mm"
) -> Optional[ErrorMessage]:
    """
    Validate dimension is within range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Dimension name
        unit: Unit of measurement

    Returns:
        ErrorMessage if validation fails, None if valid
    """
    if value < min_val or value > max_val:
        return create_dimension_error(name, value, min_val, max_val, unit)
    return None


def validate_material_grades(
    fck: float,
    fy: float
) -> Optional[ErrorMessage]:
    """
    Validate material grades are standard.

    Args:
        fck: Concrete strength (MPa)
        fy: Steel yield strength (MPa)

    Returns:
        ErrorMessage if validation fails, None if valid
    """
    valid_fck = [15, 20, 25, 30, 35, 40, 45, 50]
    valid_fy = [250, 415, 500, 550]

    if fck not in valid_fck or fy not in valid_fy:
        return create_material_error(fck, fy)
    return None


def validate_load_value(
    value: float,
    load_type: str,
    min_val: float = 0.0,
    max_val: float = 10000.0,
    unit: str = "kN"
) -> Optional[ErrorMessage]:
    """
    Validate load value is reasonable.

    Args:
        value: Load value
        load_type: Type of load ("Moment", "Shear")
        min_val: Minimum reasonable value
        max_val: Maximum reasonable value
        unit: Unit of measurement

    Returns:
        ErrorMessage if validation fails, None if valid
    """
    if value < min_val or value > max_val:
        return create_load_error(load_type, value, max_val, unit)
    return None


# =============================================================================
# Batch Validation
# =============================================================================

def validate_beam_inputs(
    span_mm: float,
    b_mm: float,
    d_mm: float,
    D_mm: float,
    fck_mpa: float,
    fy_mpa: float,
    mu_knm: float,
    vu_kn: float
) -> list[ErrorMessage]:
    """
    Validate all beam design inputs.

    Args:
        span_mm: Span length (mm)
        b_mm: Width (mm)
        d_mm: Effective depth (mm)
        D_mm: Overall depth (mm)
        fck_mpa: Concrete strength (MPa)
        fy_mpa: Steel yield strength (MPa)
        mu_knm: Factored moment (kNm)
        vu_kn: Factored shear (kN)

    Returns:
        List of ErrorMessage objects (empty if all valid)
    """
    errors = []

    # Geometry validation
    error = validate_dimension_range(span_mm, 1000, 15000, "Span", "mm")
    if error:
        errors.append(error)

    error = validate_dimension_range(b_mm, 150, 1000, "Width", "mm")
    if error:
        errors.append(error)

    error = validate_dimension_range(d_mm, 200, 2000, "Effective Depth", "mm")
    if error:
        errors.append(error)

    error = validate_dimension_range(D_mm, 250, 2500, "Overall Depth", "mm")
    if error:
        errors.append(error)

    # Check d < D
    if d_mm >= D_mm:
        errors.append(ErrorMessage(
            severity=ErrorSeverity.ERROR,
            title="Invalid Depth Values",
            message=f"Effective depth ({d_mm}mm) must be less than overall depth ({D_mm}mm).",
            fix_suggestions=[
                "Effective depth = Overall depth - Cover - Bar diameter/2",
                "Typical: d = D - 30-50mm (for cover and bars)",
                "Check if you swapped the values"
            ],
            technical_details=f"d={d_mm} >= D={D_mm}"
        ))

    # Material validation
    error = validate_material_grades(fck_mpa, fy_mpa)
    if error:
        errors.append(error)

    # Load validation
    error = validate_load_value(mu_knm, "Moment", 1.0, 5000.0, "kNm")
    if error:
        errors.append(error)

    error = validate_load_value(vu_kn, "Shear", 0.5, 3000.0, "kN")
    if error:
        errors.append(error)

    return errors


# =============================================================================
# Success Message
# =============================================================================

def display_success_message(message: str, details: Optional[str] = None):
    """
    Display success message.

    Args:
        message: Success message
        details: Optional additional details
    """
    if details:
        st.success(f"✅ **{message}**\n\n{details}")
    else:
        st.success(f"✅ {message}")


def display_warning_message(message: str, suggestions: Optional[list[str]] = None):
    """
    Display warning message.

    Args:
        message: Warning message
        suggestions: Optional list of suggestions
    """
    message_parts = [f"⚠️ {message}"]

    if suggestions:
        message_parts.append("")
        message_parts.append("**Suggestions:**")
        for i, suggestion in enumerate(suggestions, 1):
            message_parts.append(f"{i}. {suggestion}")

    st.warning("\n".join(message_parts))


def display_info_message(message: str):
    """
    Display informational message.

    Args:
        message: Info message
    """
    st.info(f"ℹ️ {message}")
