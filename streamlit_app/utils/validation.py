"""
Validation Utilities
====================

Input validation functions.

Functions:
- validate_dimension() - Check dimension range
- validate_materials() - Check material compatibility
- validate_loads() - Check load values
- format_error_message() - Create user-friendly error messages

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: Stub - To be implemented in STREAMLIT-IMPL-002
"""


def validate_dimension(
    value: float,
    min_val: float,
    max_val: float,
    name: str
) -> tuple[bool, str]:
    """
    Validate dimension value.

    Args:
        value: Input value
        min_val: Minimum allowed
        max_val: Maximum allowed
        name: Parameter name (for error message)

    Returns:
        (is_valid, error_message) tuple

    Example:
        >>> is_valid, msg = validate_dimension(5000, 1000, 12000, "Span")
        >>> print(is_valid, msg)
        True, ""
    """
    if value < min_val:
        return False, f"❌ {name} must be ≥ {min_val}"
    if value > max_val:
        return False, f"❌ {name} must be ≤ {max_val}"
    return True, ""


def validate_materials(fck: float, fy: float) -> tuple[bool, str]:
    """
    Validate material combination.

    Args:
        fck: Concrete strength (N/mm²)
        fy: Steel strength (N/mm²)

    Returns:
        (is_valid, error_message) tuple

    Example:
        >>> is_valid, msg = validate_materials(25, 500)
        >>> print(is_valid, msg)
        True, ""
    """
    # TODO: Add material compatibility checks
    return True, ""


def format_error_message(error_type: str, details: str) -> str:
    """
    Format user-friendly error message.

    Args:
        error_type: Error category
        details: Specific details

    Returns:
        Formatted error message

    Example:
        >>> msg = format_error_message("DIMENSION", "Span exceeds 12m")
        >>> print(msg)
        ❌ Dimension Error: Span exceeds 12m
    """
    icons = {
        "DIMENSION": "❌",
        "MATERIAL": "⚠️",
        "LOAD": "❌",
        "DESIGN": "❌"
    }
    icon = icons.get(error_type, "❌")
    return f"{icon} {error_type.title()} Error: {details}"
