"""
Validation helpers for cost optimizer.

Provides type-safe validation of beam inputs and design results.
"""

from typing import TypedDict, Any
from dataclasses import dataclass
import math


class BeamInputs(TypedDict):
    """Type-safe beam design inputs."""

    mu_knm: float
    vu_kn: float
    b_mm: float
    D_mm: float
    d_mm: float
    span_mm: float
    fck_nmm2: float
    fy_nmm2: float


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


@dataclass
class ValidationResult:
    """Result of validation check."""

    is_valid: bool
    errors: list[str]

    def __bool__(self):
        return self.is_valid


def validate_beam_inputs(inputs: dict) -> ValidationResult:
    """
    Validate beam design inputs with comprehensive checks.

    Args:
        inputs: Dictionary of beam parameters

    Returns:
        ValidationResult with is_valid flag and error list

    Example:
        >>> result = validate_beam_inputs({"mu_knm": 120, ...})
        >>> if not result:
        ...     for error in result.errors:
        ...         print(f"Error: {error}")
    """
    errors = []

    # Required keys
    required = [
        "mu_knm",
        "vu_kn",
        "b_mm",
        "D_mm",
        "d_mm",
        "span_mm",
        "fck_nmm2",
        "fy_nmm2",
    ]
    for key in required:
        if key not in inputs:
            errors.append(f"Missing required parameter: {key}")

    if errors:
        return ValidationResult(False, errors)

    # Type checks
    for key in required:
        value = inputs[key]
        if not isinstance(value, (int, float)):
            errors.append(f"{key} must be numeric, got {type(value).__name__}")
        elif math.isnan(value) or math.isinf(value):
            errors.append(f"{key} is NaN or Inf")

    if errors:
        return ValidationResult(False, errors)

    # Range checks
    mu_knm = inputs["mu_knm"]
    vu_kn = inputs["vu_kn"]
    b_mm = inputs["b_mm"]
    D_mm = inputs["D_mm"]
    d_mm = inputs["d_mm"]
    span_mm = inputs["span_mm"]
    fck_nmm2 = inputs["fck_nmm2"]
    fy_nmm2 = inputs["fy_nmm2"]

    if mu_knm <= 0:
        errors.append(f"Moment must be positive, got {mu_knm} kN·m")
    if mu_knm > 10000:
        errors.append(f"Moment {mu_knm} kN·m is unrealistically large (>10000)")

    if vu_kn < 0:
        errors.append(f"Shear force cannot be negative, got {vu_kn} kN")
    if vu_kn > 5000:
        errors.append(f"Shear force {vu_kn} kN is unrealistically large (>5000)")

    if b_mm < 100:
        errors.append(f"Width {b_mm} mm is too small (minimum 100 mm)")
    if b_mm > 1000:
        errors.append(f"Width {b_mm} mm is too large (maximum 1000 mm)")

    if D_mm < 150:
        errors.append(f"Total depth {D_mm} mm is too small (minimum 150 mm)")
    if D_mm > 2000:
        errors.append(f"Total depth {D_mm} mm is too large (maximum 2000 mm)")

    if d_mm < 100:
        errors.append(f"Effective depth {d_mm} mm is too small (minimum 100 mm)")
    if d_mm >= D_mm:
        errors.append(
            f"Effective depth {d_mm} mm must be less than total depth {D_mm} mm"
        )

    cover = D_mm - d_mm
    if cover < 20:
        errors.append(f"Cover {cover:.0f} mm is too small (minimum 20 mm)")
    if cover > 100:
        errors.append(f"Cover {cover:.0f} mm is too large (maximum 100 mm)")

    if span_mm < 1000:
        errors.append(f"Span {span_mm} mm is too small (minimum 1000 mm)")
    if span_mm > 50000:
        errors.append(f"Span {span_mm} mm is too large (maximum 50000 mm)")

    # Span to depth ratio
    span_to_depth = span_mm / D_mm
    if span_to_depth < 5:
        errors.append(f"Span/depth ratio {span_to_depth:.1f} is too small (minimum 5)")
    if span_to_depth > 30:
        errors.append(f"Span/depth ratio {span_to_depth:.1f} is too large (maximum 30)")

    if fck_nmm2 < 20:
        errors.append(
            f"Concrete strength {fck_nmm2} N/mm² is below IS 456 minimum (M20)"
        )
    if fck_nmm2 > 100:
        errors.append(f"Concrete strength {fck_nmm2} N/mm² is too high (maximum 100)")

    if fy_nmm2 < 250:
        errors.append(
            f"Steel yield strength {fy_nmm2} N/mm² is below IS 456 minimum (Fe250)"
        )
    if fy_nmm2 > 600:
        errors.append(
            f"Steel yield strength {fy_nmm2} N/mm² is above IS 456 maximum (Fe600)"
        )

    return ValidationResult(len(errors) == 0, errors)


def validate_design_result(result: Any) -> ValidationResult:
    """
    Validate design result structure.

    Args:
        result: Design result dictionary from cached_smart_analysis

    Returns:
        ValidationResult with validation status
    """
    errors = []

    if not isinstance(result, dict):
        errors.append(f"Design result must be dict, got {type(result).__name__}")
        return ValidationResult(False, errors)

    if "design" not in result:
        errors.append("Design result missing 'design' key")
        return ValidationResult(False, errors)

    design = result["design"]
    if not isinstance(design, dict):
        errors.append(f"design must be dict, got {type(design).__name__}")
        return ValidationResult(False, errors)

    if "flexure" not in design:
        errors.append("Design missing 'flexure' analysis")
        return ValidationResult(False, errors)

    flexure = design["flexure"]
    if not isinstance(flexure, dict):
        errors.append(f"flexure must be dict, got {type(flexure).__name__}")
        return ValidationResult(False, errors)

    # Check for required flexure keys
    if "tension_steel" not in flexure:
        errors.append("Flexure result missing 'tension_steel'")
    if "_bar_alternatives" not in flexure:
        errors.append("Flexure result missing '_bar_alternatives'")

    # Validate tension_steel structure
    if "tension_steel" in flexure:
        steel = flexure["tension_steel"]
        if not isinstance(steel, dict):
            errors.append(f"tension_steel must be dict, got {type(steel).__name__}")
        else:
            for key in ["num", "dia", "area"]:
                if key not in steel:
                    errors.append(f"tension_steel missing '{key}' key")
                elif not isinstance(steel[key], (int, float)):
                    errors.append(f"tension_steel['{key}'] must be numeric")

    # Validate alternatives structure
    if "_bar_alternatives" in flexure:
        alts = flexure["_bar_alternatives"]
        if not isinstance(alts, list):
            errors.append(f"_bar_alternatives must be list, got {type(alts).__name__}")
        elif len(alts) == 0:
            errors.append("_bar_alternatives is empty list")
        else:
            # Check first alternative structure
            alt = alts[0]
            if not isinstance(alt, dict):
                errors.append(f"Alternative must be dict, got {type(alt).__name__}")
            else:
                for key in ["num", "dia", "area"]:
                    if key not in alt:
                        errors.append(f"Alternative missing '{key}' key")

    return ValidationResult(len(errors) == 0, errors)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safe division with zero check.

    Args:
        numerator: Top value
        denominator: Bottom value
        default: Value to return if denominator is zero

    Returns:
        numerator / denominator, or default if denominator is zero

    Example:
        >>> safe_divide(10, 2)  # Returns 5.0
        >>> safe_divide(10, 0)  # Returns 0.0
        >>> safe_divide(10, 0, float('nan'))  # Returns nan
    """
    if denominator == 0 or math.isnan(denominator) or math.isinf(denominator):
        return default

    result = numerator / denominator

    # Check result validity
    if math.isnan(result) or math.isinf(result):
        return default

    return result


def safe_format_currency(value: Any) -> str:
    """
    Format currency value safely.

    Args:
        value: Numeric value to format

    Returns:
        Formatted string like "₹1,234" or "Invalid" if not a number
    """
    if not isinstance(value, (int, float)):
        return "Invalid"

    if math.isnan(value) or math.isinf(value):
        return "N/A"

    if value < 0:
        return f"-₹{abs(value):,.0f}"

    return f"₹{value:,.0f}"


def safe_format_percent(value: Any) -> str:
    """
    Format percentage value safely.

    Args:
        value: Numeric value (0-1 range for percentage)

    Returns:
        Formatted string like "45.23%" or "Invalid" if not a number
    """
    if not isinstance(value, (int, float)):
        return "Invalid"

    if math.isnan(value) or math.isinf(value):
        return "N/A"

    return f"{value:.2%}"
