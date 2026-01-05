"""
Module:       validation
Description:  Reusable validation utilities for parameter checking.

This module provides common validation patterns to reduce code duplication
and ensure consistent error handling across the library.

See docs/research/cs-best-practices-audit.md for design rationale.
"""

from typing import List

from .errors import (
    E_INPUT_001,
    E_INPUT_002,
    E_INPUT_003,
    E_INPUT_004,
    E_INPUT_005,
    E_INPUT_013,
    E_INPUT_014,
    E_INPUT_015,
    DesignError,
    E_INPUT_003a,
    Severity,
)


def validate_dimensions(
    b: float,
    d: float,
    D: float,
    *,
    require_d_less_than_D: bool = True,
) -> List[DesignError]:
    """Validate beam dimensions (b, d, D).

    Args:
        b: Beam width (mm)
        d: Effective depth (mm)
        D: Overall depth (mm)
        require_d_less_than_D: If True, enforces d < D constraint

    Returns:
        List of validation errors (empty if all valid)

    Example:
        >>> errors = validate_dimensions(b=300, d=450, D=500)
        >>> if errors:
        ...     return FlexureResult(..., errors=errors)
    """
    errors: List[DesignError] = []

    if b <= 0:
        errors.append(E_INPUT_001)

    if d <= 0:
        errors.append(E_INPUT_002)

    if D <= 0:
        errors.append(E_INPUT_003a)

    # Only check d vs D if both are valid positive numbers
    if require_d_less_than_D and d > 0 and D > 0 and d >= D:
        errors.append(E_INPUT_003)

    return errors


def validate_materials(fck: float, fy: float) -> List[DesignError]:
    """Validate material properties (fck, fy).

    Args:
        fck: Concrete compressive strength (N/mm²)
        fy: Steel yield strength (N/mm²)

    Returns:
        List of validation errors (empty if all valid)

    Example:
        >>> errors = validate_materials(fck=25, fy=500)
        >>> if errors:
        ...     return FlexureResult(..., errors=errors)
    """
    errors: List[DesignError] = []

    if fck <= 0:
        errors.append(E_INPUT_004)

    if fy <= 0:
        errors.append(E_INPUT_005)

    return errors


def validate_positive(
    value: float,
    field_name: str,
    error_map: dict[str, DesignError],
) -> List[DesignError]:
    """Validate that a value is positive.

    Args:
        value: Value to check
        field_name: Name of the field (for error lookup)
        error_map: Dictionary mapping field names to DesignError objects

    Returns:
        List containing one error if invalid, empty otherwise

    Example:
        >>> error_map = {"mu_knm": E_INPUT_010}
        >>> errors = validate_positive(mu_knm, "mu_knm", error_map)
    """
    if value <= 0:
        error = error_map.get(field_name)
        if error:
            return [error]
        # Fallback: create a generic error if not in map
        return [
            DesignError(
                code="E_INPUT_GENERIC",
                severity=Severity.ERROR,
                message=f"{field_name} must be > 0",
                field=field_name,
            )
        ]
    return []


def validate_range(
    value: float,
    min_val: float,
    max_val: float,
    field_name: str,
    error: DesignError,
) -> List[DesignError]:
    """Validate that a value is within a specified range.

    Args:
        value: Value to check
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        field_name: Name of the field
        error: DesignError to return if validation fails

    Returns:
        List containing one error if out of range, empty otherwise

    Example:
        >>> errors = validate_range(pt, 0.0, 4.0, "pt", E_INPUT_012)
    """
    if not (min_val <= value <= max_val):
        return [error]
    return []


def validate_geometry_relationship(
    d: float,
    D: float,
    cover: float,
) -> List[DesignError]:
    """Validate beam geometry relationships.

    Checks that D = d + cover + bar diameter allowance.

    Args:
        d: Effective depth (mm)
        D: Overall depth (mm)
        cover: Clear cover (mm)

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_geometry_relationship(d=450, D=500, cover=40)
    """
    errors: List[DesignError] = []

    # Basic checks
    if d <= 0:
        errors.append(E_INPUT_002)

    if D <= 0:
        errors.append(E_INPUT_003a)

    if cover < 0:
        errors.append(E_INPUT_015)

    # Relationship check: D must be greater than d + cover (simplified)
    # This allows space for clear cover and rebar diameter
    # Only check if all values are valid
    if d > 0 and D > 0 and cover >= 0:
        if D < d + cover:
            errors.append(E_INPUT_003)

    return errors


def validate_stirrup_parameters(
    asv_mm2: float,
    spacing_mm: float,
) -> List[DesignError]:
    """Validate stirrup parameters.

    Args:
        asv_mm2: Area of stirrup legs (mm²)
        spacing_mm: Stirrup spacing (mm)

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_stirrup_parameters(asv_mm2=100, spacing_mm=150)
    """
    errors: List[DesignError] = []

    if asv_mm2 <= 0:
        errors.append(E_INPUT_013)

    if spacing_mm <= 0:
        errors.append(E_INPUT_014)

    return errors


def validate_all_positive(
    **kwargs: float,
) -> List[DesignError]:
    """Validate that all provided values are positive.

    Convenience function for validating multiple parameters at once.

    Args:
        **kwargs: Field name and value pairs to validate

    Returns:
        List of validation errors (empty if all valid)

    Example:
        >>> errors = validate_all_positive(
        ...     b=300, d=450, D=500, fck=25, fy=500
        ... )

    Note:
        This is a generic validator. For specific fields with dedicated
        error codes, use validate_dimensions() or validate_materials().
    """
    errors: List[DesignError] = []

    for field_name, value in kwargs.items():
        if value <= 0:
            errors.append(
                DesignError(
                    code="E_INPUT_GENERIC",
                    severity=Severity.ERROR,
                    message=f"{field_name} must be > 0",
                    field=field_name,
                    hint=f"Provided value: {value}",
                )
            )

    return errors


__all__ = [
    "validate_dimensions",
    "validate_materials",
    "validate_positive",
    "validate_range",
    "validate_geometry_relationship",
    "validate_stirrup_parameters",
    "validate_all_positive",
]
