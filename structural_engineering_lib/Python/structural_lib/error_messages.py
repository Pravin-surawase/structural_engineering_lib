# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       error_messages
Description:  Error message templates following the Three Questions Framework.

This module provides template functions for creating clear, actionable error messages
that answer:
1. What went wrong?
2. Why did it fail?
3. How to fix it?

Usage:
    from structural_lib.error_messages import dimension_too_small, capacity_exceeded

    if b_mm < 200:
        raise DimensionError(dimension_too_small("width", b_mm, 200, "Cl. 26.5.1.1"))

Related:
- TASK-213 (Implement error message templates)
- docs/guidelines/error-handling-standard.md
"""

from __future__ import annotations

from typing import Any

# =============================================================================
# Template Functions - Dimension Errors
# =============================================================================


def dimension_too_small(
    dim_name: str,
    actual: float,
    minimum: float,
    clause_ref: str | None = None,
    unit: str = "mm",
) -> str:
    """
    Template for dimension below minimum.

    Args:
        dim_name: Name of dimension (e.g., "width", "depth", "cover")
        actual: Actual value provided
        minimum: Minimum required value
        clause_ref: IS 456 clause reference
        unit: Unit of measurement

    Returns:
        Formatted error message

    Example:
        >>> dimension_too_small("width", 150, 200, "Cl. 26.5.1.1")
        'Width 150mm is below minimum 200mm (IS 456:2000 Cl. 26.5.1.1). Increase width to at least 200mm.'
    """
    parts = [f"{dim_name.capitalize()} {actual}{unit} is below minimum {minimum}{unit}"]
    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")
    parts.append(f"Increase {dim_name} to at least {minimum}{unit}.")
    return " ".join(parts)


def dimension_too_large(
    dim_name: str,
    actual: float,
    maximum: float,
    clause_ref: str | None = None,
    unit: str = "mm",
) -> str:
    """
    Template for dimension above maximum.

    Args:
        dim_name: Name of dimension
        actual: Actual value provided
        maximum: Maximum allowed value
        clause_ref: IS 456 clause reference
        unit: Unit of measurement

    Returns:
        Formatted error message
    """
    parts = [f"{dim_name.capitalize()} {actual}{unit} exceeds maximum {maximum}{unit}"]
    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")
    parts.append(f"Reduce {dim_name} to at most {maximum}{unit}.")
    return " ".join(parts)


def dimension_negative(dim_name: str, actual: float, unit: str = "mm") -> str:
    """
    Template for negative dimension.

    Args:
        dim_name: Name of dimension
        actual: Actual value provided (negative)
        unit: Unit of measurement

    Returns:
        Formatted error message

    Example:
        >>> dimension_negative("depth", -50)
        'Depth -50mm cannot be negative. Provide a positive value.'
    """
    return f"{dim_name.capitalize()} {actual}{unit} cannot be negative. Provide a positive value."


def dimension_relationship_invalid(
    dim1_name: str,
    dim1_value: float,
    dim2_name: str,
    dim2_value: float,
    relationship: str,
    unit: str = "mm",
) -> str:
    """
    Template for invalid dimension relationship.

    Args:
        dim1_name: Name of first dimension
        dim1_value: Value of first dimension
        dim2_name: Name of second dimension
        dim2_value: Value of second dimension
        relationship: Required relationship (e.g., "must be greater than", "must be less than")
        unit: Unit of measurement

    Returns:
        Formatted error message

    Example:
        >>> dimension_relationship_invalid("overall depth D", 400, "effective depth d", 450, "must be greater than")
        'Overall depth D 400mm must be greater than effective depth d 450mm. Adjust dimensions to satisfy the relationship.'
    """
    return (
        f"{dim1_name} {dim1_value}{unit} {relationship} "
        f"{dim2_name} {dim2_value}{unit}. "
        f"Adjust dimensions to satisfy the relationship."
    )


# =============================================================================
# Template Functions - Material Errors
# =============================================================================


def material_grade_invalid(
    material_name: str, actual: float, valid_grades: list[float], unit: str = "MPa"
) -> str:
    """
    Template for invalid material grade.

    Args:
        material_name: Name of material (e.g., "concrete", "steel")
        actual: Actual grade provided
        valid_grades: List of valid grades
        unit: Unit of material strength

    Returns:
        Formatted error message

    Example:
        >>> material_grade_invalid("concrete", 35, [20, 25, 30, 40, 45, 50])
        'Concrete grade 35MPa is not a standard grade. Use one of: [20, 25, 30, 40, 45, 50] MPa (IS 456:2000 Table 2).'
    """
    grades_str = ", ".join(str(g) for g in valid_grades)
    return (
        f"{material_name.capitalize()} grade {actual}{unit} is not a standard grade. "
        f"Use one of: [{grades_str}] {unit} (IS 456:2000 Table 2)."
    )


def material_property_out_of_range(
    property_name: str,
    actual: float,
    min_value: float | None = None,
    max_value: float | None = None,
    unit: str = "",
) -> str:
    """
    Template for material property out of valid range.

    Args:
        property_name: Name of property
        actual: Actual value provided
        min_value: Minimum valid value
        max_value: Maximum valid value
        unit: Unit of property

    Returns:
        Formatted error message
    """
    parts = [f"{property_name.capitalize()} {actual}{unit} is out of valid range"]

    if min_value is not None and max_value is not None:
        parts.append(f"({min_value}-{max_value}{unit})")
    elif min_value is not None:
        parts.append(f"(minimum {min_value}{unit})")
    elif max_value is not None:
        parts.append(f"(maximum {max_value}{unit})")

    parts.append("Provide a value within the valid range.")
    return " ".join(parts)


# =============================================================================
# Template Functions - Design Constraint Errors
# =============================================================================


def capacity_exceeded(
    load_name: str,
    load_value: float,
    capacity_name: str,
    capacity_value: float,
    suggestions: list[str],
    clause_ref: str | None = None,
    unit: str = "kN·m",
) -> str:
    """
    Template for load exceeding capacity.

    Args:
        load_name: Name of load (e.g., "Moment Mu", "Shear Vu")
        load_value: Applied load value
        capacity_name: Name of capacity (e.g., "Mu,lim", "Vu,max")
        capacity_value: Available capacity
        suggestions: List of suggestions to fix
        clause_ref: IS 456 clause reference
        unit: Unit of load/capacity

    Returns:
        Formatted error message

    Example:
        >>> capacity_exceeded("Moment Mu", 250, "Mu,lim", 200,
        ...     ["Increase section depth", "Use compression reinforcement", "Increase concrete grade"],
        ...     "Cl. 38.1")
        'Moment Mu 250kN·m exceeds section capacity Mu,lim 200kN·m (IS 456:2000 Cl. 38.1). Options: (1) Increase section depth, (2) Use compression reinforcement, (3) Increase concrete grade.'
    """
    parts = [
        f"{load_name} {load_value}{unit} exceeds section capacity "
        f"{capacity_name} {capacity_value}{unit}"
    ]

    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")

    if suggestions:
        options = ", ".join(f"({i+1}) {s}" for i, s in enumerate(suggestions))
        parts.append(f"Options: {options}.")

    return " ".join(parts)


def reinforcement_spacing_insufficient(
    available_space: float,
    required_space: float,
    bar_count: int,
    bar_diameter: float,
    clause_ref: str | None = None,
) -> str:
    """
    Template for insufficient spacing for reinforcement.

    Args:
        available_space: Available width
        required_space: Space required for bars
        bar_count: Number of bars trying to fit
        bar_diameter: Diameter of bars
        clause_ref: IS 456 clause reference

    Returns:
        Formatted error message

    Example:
        >>> reinforcement_spacing_insufficient(230, 280, 4, 20, "Cl. 26.3")
        'Cannot fit 4-#20mm bars in available width 230mm (requires 280mm) (IS 456:2000 Cl. 26.3). Options: (1) Reduce bar count, (2) Use smaller diameter, (3) Increase section width.'
    """
    parts = [
        f"Cannot fit {bar_count}-#{bar_diameter}mm bars in available width "
        f"{available_space}mm (requires {required_space}mm)"
    ]

    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")

    parts.append(
        "Options: (1) Reduce bar count, (2) Use smaller diameter, (3) Increase section width."
    )

    return " ".join(parts)


# =============================================================================
# Template Functions - Compliance Errors
# =============================================================================


def minimum_reinforcement_not_met(
    actual: float,
    minimum: float,
    parameter_name: str = "reinforcement",
    clause_ref: str | None = None,
    unit: str = "mm²",
) -> str:
    """
    Template for minimum reinforcement not satisfied.

    Args:
        actual: Actual reinforcement provided
        minimum: Minimum required
        parameter_name: Name of parameter (e.g., "tension steel", "stirrups")
        clause_ref: IS 456 clause reference
        unit: Unit of reinforcement

    Returns:
        Formatted error message

    Example:
        >>> minimum_reinforcement_not_met(950, 1100, "tension steel", "Cl. 26.5.1.1")
        'Tension steel 950mm² is below minimum 1100mm² (IS 456:2000 Cl. 26.5.1.1). Increase reinforcement to meet minimum requirement.'
    """
    parts = [
        f"{parameter_name.capitalize()} {actual}{unit} is below minimum {minimum}{unit}"
    ]

    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")

    parts.append("Increase reinforcement to meet minimum requirement.")

    return " ".join(parts)


def maximum_reinforcement_exceeded(
    actual: float,
    maximum: float,
    parameter_name: str = "reinforcement",
    clause_ref: str | None = None,
    unit: str = "mm²",
) -> str:
    """
    Template for maximum reinforcement exceeded.

    Args:
        actual: Actual reinforcement provided
        maximum: Maximum allowed
        parameter_name: Name of parameter
        clause_ref: IS 456 clause reference
        unit: Unit of reinforcement

    Returns:
        Formatted error message

    Example:
        >>> maximum_reinforcement_exceeded(5000, 4000, "tension steel", "Cl. 26.5.1.2")
        'Tension steel 5000mm² exceeds maximum 4000mm² (IS 456:2000 Cl. 26.5.1.2). Reduce reinforcement or increase section size.'
    """
    parts = [
        f"{parameter_name.capitalize()} {actual}{unit} exceeds maximum {maximum}{unit}"
    ]

    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")

    parts.append("Reduce reinforcement or increase section size.")

    return " ".join(parts)


def spacing_limit_exceeded(
    actual_spacing: float,
    maximum_spacing: float,
    spacing_type: str = "stirrup",
    clause_ref: str | None = None,
) -> str:
    """
    Template for spacing exceeding code limits.

    Args:
        actual_spacing: Actual spacing
        maximum_spacing: Maximum allowed spacing
        spacing_type: Type of spacing (e.g., "stirrup", "bar")
        clause_ref: IS 456 clause reference

    Returns:
        Formatted error message

    Example:
        >>> spacing_limit_exceeded(450, 300, "stirrup", "Cl. 26.5.1.6")
        'Stirrup spacing 450mm exceeds maximum 300mm (IS 456:2000 Cl. 26.5.1.6). Reduce spacing to meet code requirements.'
    """
    parts = [
        f"{spacing_type.capitalize()} spacing {actual_spacing}mm exceeds maximum {maximum_spacing}mm"
    ]

    if clause_ref:
        parts.append(f"(IS 456:2000 {clause_ref})")

    parts.append("Reduce spacing to meet code requirements.")

    return " ".join(parts)


# =============================================================================
# Template Functions - Calculation Errors
# =============================================================================


def convergence_failed(
    algorithm_name: str,
    iterations: int,
    tolerance: float,
    current_error: float | None = None,
) -> str:
    """
    Template for iterative calculation convergence failure.

    Args:
        algorithm_name: Name of algorithm
        iterations: Number of iterations attempted
        tolerance: Target tolerance
        current_error: Current error value if available

    Returns:
        Formatted error message

    Example:
        >>> convergence_failed("neutral axis iteration", 100, 0.001, 0.015)
        'Neutral axis iteration did not converge after 100 iterations (tolerance=0.001, current error=0.015). Check input values or increase iteration limit.'
    """
    parts = [
        f"{algorithm_name.capitalize()} did not converge after {iterations} iterations "
        f"(tolerance={tolerance}"
    ]

    if current_error is not None:
        parts.append(f", current error={current_error}")

    parts.append("). Check input values or increase iteration limit.")

    return "".join(parts)


def numerical_instability(operation: str, problematic_value: Any, reason: str) -> str:
    """
    Template for numerical instability.

    Args:
        operation: Operation being performed
        problematic_value: Value causing issues
        reason: Reason for instability

    Returns:
        Formatted error message

    Example:
        >>> numerical_instability("division", "xu", "denominator too close to zero")
        'Numerical instability in division: xu (denominator too close to zero). Check input values for validity.'
    """
    return (
        f"Numerical instability in {operation}: {problematic_value} ({reason}). "
        f"Check input values for validity."
    )


# =============================================================================
# Helper Functions
# =============================================================================


def format_value_with_unit(value: float, unit: str, precision: int = 2) -> str:
    """Format a value with its unit."""
    return f"{value:.{precision}f}{unit}"


def format_list(items: list[Any], conjunction: str = "or") -> str:
    """
    Format a list of items with proper grammar.

    Example:
        >>> format_list([20, 25, 30])
        '20, 25, or 30'
        >>> format_list(["increase depth", "add compression steel"], "or")
        'increase depth or add compression steel'
    """
    if not items:
        return ""
    if len(items) == 1:
        return str(items[0])
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    return f"{', '.join(str(i) for i in items[:-1])}, {conjunction} {items[-1]}"
