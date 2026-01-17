# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       validation
Description:  Reusable validation utilities for parameter checking.

This module provides common validation patterns to reduce code duplication
and ensure consistent error handling across the library.

See docs/research/cs-best-practices-audit.md for design rationale.
"""

from __future__ import annotations

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
) -> list[DesignError]:
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
    errors: list[DesignError] = []

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


def validate_materials(fck: float, fy: float) -> list[DesignError]:
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
    errors: list[DesignError] = []

    if fck <= 0:
        errors.append(E_INPUT_004)

    if fy <= 0:
        errors.append(E_INPUT_005)

    return errors


def validate_positive(
    value: float,
    field_name: str,
    error_map: dict[str, DesignError],
) -> list[DesignError]:
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
) -> list[DesignError]:
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
) -> list[DesignError]:
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
    errors: list[DesignError] = []

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
) -> list[DesignError]:
    """Validate stirrup parameters.

    Args:
        asv_mm2: Area of stirrup legs (mm²)
        spacing_mm: Stirrup spacing (mm)

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_stirrup_parameters(asv_mm2=100, spacing_mm=150)
    """
    errors: list[DesignError] = []

    if asv_mm2 <= 0:
        errors.append(E_INPUT_013)

    if spacing_mm <= 0:
        errors.append(E_INPUT_014)

    return errors


def validate_all_positive(
    **kwargs: float,
) -> list[DesignError]:
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
    errors: list[DesignError] = []

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


def validate_cover(
    cover: float,
    D: float,
    min_cover: float = 25.0,
) -> list[DesignError]:
    """Validate cover requirements.

    Args:
        cover: Clear cover (mm)
        D: Overall depth (mm)
        min_cover: Minimum cover per IS 456 (mm)

    Returns:
        List of validation errors (empty if valid)

    Checks:
        - cover > 0
        - cover >= min_cover
        - cover < D (physical constraint)

    Example:
        >>> errors = validate_cover(cover=30, D=500, min_cover=25)
        >>> if errors:
        ...     return FlexureResult(..., errors=errors)
    """
    errors: list[DesignError] = []

    if cover <= 0:
        errors.append(E_INPUT_015)

    if D > 0 and cover >= D:
        errors.append(
            DesignError(
                code="E_INPUT_COVER_TOO_LARGE",
                severity=Severity.ERROR,
                message=f"Clear cover {cover}mm >= overall depth {D}mm",
                field="cover",
                hint="Cover must be less than overall depth.",
            )
        )

    if cover > 0 and cover < min_cover:
        errors.append(
            DesignError(
                code="E_INPUT_COVER_MIN",
                severity=Severity.WARNING,
                message=f"Cover {cover}mm < minimum recommended {min_cover}mm",
                field="cover",
                hint=f"IS 456 recommends minimum {min_cover}mm cover.",
                clause="26.4",
            )
        )

    return errors


def validate_loads(
    mu: float,
    vu: float,
    *,
    allow_negative: bool = False,
) -> list[DesignError]:
    """Validate factored loads (moment, shear).

    Args:
        mu: Factored moment (kN-m)
        vu: Factored shear (kN)
        allow_negative: If True, allows negative values (hogging moment)

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_loads(mu=120, vu=80)
        >>> if errors:
        ...     return FlexureResult(..., errors=errors)
    """
    errors: list[DesignError] = []

    if not allow_negative:
        if mu < 0:
            errors.append(
                DesignError(
                    code="E_INPUT_MU_NEGATIVE",
                    severity=Severity.ERROR,
                    message="Factored moment Mu cannot be negative",
                    field="mu",
                    hint="Use positive value for sagging moment.",
                )
            )
        if vu < 0:
            errors.append(
                DesignError(
                    code="E_INPUT_VU_NEGATIVE",
                    severity=Severity.ERROR,
                    message="Factored shear Vu cannot be negative",
                    field="vu",
                    hint="Use positive value for shear force.",
                )
            )
    else:
        # If allowing negative, check for unreasonable magnitude
        if abs(mu) > 10000:
            errors.append(
                DesignError(
                    code="E_INPUT_MU_UNREASONABLE",
                    severity=Severity.WARNING,
                    message=f"Moment Mu = {mu} kN-m seems unreasonably large",
                    field="mu",
                    hint="Verify load calculations and units.",
                )
            )
        if abs(vu) > 5000:
            errors.append(
                DesignError(
                    code="E_INPUT_VU_UNREASONABLE",
                    severity=Severity.WARNING,
                    message=f"Shear Vu = {vu} kN seems unreasonably large",
                    field="vu",
                    hint="Verify load calculations and units.",
                )
            )

    return errors


def validate_material_grades(
    fck: float,
    fy: float,
) -> list[DesignError]:
    """Validate material grades per IS 456 allowed values.

    Args:
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)

    Returns:
        List of validation errors (empty if valid)

    Notes:
        IS 456 Table 2: fck = 15, 20, 25, 30, 35, 40, 45, 50
        IS 456 Annex C: fy = 250, 415, 500

    Example:
        >>> errors = validate_material_grades(fck=25, fy=415)
        >>> # Returns empty list (both are valid)
    """
    errors: list[DesignError] = []

    allowed_fck = [15, 20, 25, 30, 35, 40, 45, 50]
    allowed_fy = [250, 415, 500]

    if fck not in allowed_fck:
        errors.append(
            DesignError(
                code="E_INPUT_FCK_INVALID",
                severity=Severity.WARNING,
                message=f"fck = {fck} N/mm² not standard IS 456 grade",
                field="fck",
                hint=f"Standard grades: {allowed_fck}",
                clause="Table 2",
            )
        )

    if fy not in allowed_fy:
        errors.append(
            DesignError(
                code="E_INPUT_FY_INVALID",
                severity=Severity.WARNING,
                message=f"fy = {fy} N/mm² not standard IS 456 grade",
                field="fy",
                hint=f"Standard grades: {allowed_fy}",
                clause="Annex C",
            )
        )

    return errors


def validate_reinforcement(
    ast: float,
    ast_min: float,
    ast_max: float,
    *,
    field_name: str = "ast",
) -> list[DesignError]:
    """Validate reinforcement area against min/max limits.

    Args:
        ast: Provided steel area (mm²)
        ast_min: Minimum required area (mm²)
        ast_max: Maximum allowed area (mm²)
        field_name: Name for error messages

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_reinforcement(
        ...     ast=1200, ast_min=850, ast_max=3000
        ... )
        >>> # Returns empty (ast within limits)
    """
    errors: list[DesignError] = []

    if ast < 0:
        errors.append(
            DesignError(
                code="E_INPUT_AST_NEGATIVE",
                severity=Severity.ERROR,
                message=f"{field_name} cannot be negative",
                field=field_name,
            )
        )

    if ast > 0 and ast_min > 0 and ast < ast_min:
        errors.append(
            DesignError(
                code="E_INPUT_AST_BELOW_MIN",
                severity=Severity.ERROR,
                message=f"{field_name} = {ast:.0f} mm² < minimum {ast_min:.0f} mm²",
                field=field_name,
                hint="Increase reinforcement area.",
                clause="26.5.1.1",
            )
        )

    if ast > 0 and ast_max > 0 and ast > ast_max:
        errors.append(
            DesignError(
                code="E_INPUT_AST_ABOVE_MAX",
                severity=Severity.ERROR,
                message=f"{field_name} = {ast:.0f} mm² > maximum {ast_max:.0f} mm²",
                field=field_name,
                hint="Reduce reinforcement or increase section size.",
                clause="26.5.1.2",
            )
        )

    return errors


def validate_span(
    span: float,
    min_span: float = 1000.0,
    max_span: float = 30000.0,
) -> list[DesignError]:
    """Validate beam span.

    Args:
        span: Beam span (mm)
        min_span: Minimum reasonable span (mm)
        max_span: Maximum reasonable span (mm)

    Returns:
        List of validation errors (empty if valid)

    Example:
        >>> errors = validate_span(span=5000)
        >>> # Returns empty (5000mm is reasonable)
    """
    errors: list[DesignError] = []

    if span <= 0:
        errors.append(
            DesignError(
                code="E_INPUT_SPAN_POSITIVE",
                severity=Severity.ERROR,
                message="Span must be positive",
                field="span",
            )
        )
    elif span < min_span:
        errors.append(
            DesignError(
                code="E_INPUT_SPAN_TOO_SMALL",
                severity=Severity.WARNING,
                message=f"Span {span}mm < typical minimum {min_span}mm",
                field="span",
                hint="Verify span input is in mm, not m.",
            )
        )
    elif span > max_span:
        errors.append(
            DesignError(
                code="E_INPUT_SPAN_TOO_LARGE",
                severity=Severity.WARNING,
                message=f"Span {span}mm > typical maximum {max_span}mm",
                field="span",
                hint="Large spans may require special design considerations.",
            )
        )

    return errors


def validate_beam_inputs(
    b: float,
    d: float,
    D: float,
    cover: float,
    fck: float,
    fy: float,
    mu: float,
    vu: float,
    *,
    span: float | None = None,
    allow_negative_loads: bool = False,
) -> list[DesignError]:
    """Validate all common beam design inputs.

    Composite validator that runs all relevant validators for typical beam design.

    Args:
        b: Width (mm)
        d: Effective depth (mm)
        D: Overall depth (mm)
        cover: Clear cover (mm)
        fck: Concrete grade (N/mm²)
        fy: Steel grade (N/mm²)
        mu: Factored moment (kN-m)
        vu: Factored shear (kN)
        span: Beam span (mm), optional
        allow_negative_loads: If True, allows negative mu/vu

    Returns:
        Combined list of all validation errors

    Example:
        >>> errors = validate_beam_inputs(
        ...     b=300, d=450, D=500, cover=25,
        ...     fck=25, fy=415, mu=120, vu=80
        ... )
        >>> if errors:
        ...     return FlexureResult(..., errors=errors)
    """
    errors: list[DesignError] = []

    # Run all validators
    errors.extend(validate_dimensions(b, d, D))
    errors.extend(validate_cover(cover, D))
    errors.extend(validate_materials(fck, fy))
    errors.extend(validate_material_grades(fck, fy))
    errors.extend(validate_loads(mu, vu, allow_negative=allow_negative_loads))

    if span is not None:
        errors.extend(validate_span(span))

    return errors


__all__ = [
    "validate_dimensions",
    "validate_materials",
    "validate_positive",
    "validate_range",
    "validate_geometry_relationship",
    "validate_stirrup_parameters",
    "validate_all_positive",
    "validate_cover",
    "validate_loads",
    "validate_material_grades",
    "validate_reinforcement",
    "validate_span",
    "validate_beam_inputs",
]
