"""
Input Validators
=================

Comprehensive input validation for beam design parameters.

This module provides validation functions that:
- Check engineering constraints (IS 456 compliance)
- Provide detailed error messages
- Suggest corrections
- Sanitize inputs safely

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ IMPL-004 Part 2
Created: 2026-01-09
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ValidationResult:
    """Result of input validation with detailed feedback"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_value: Any
    suggestion: Optional[str] = None


def validate_beam_inputs(
    span_mm: float,
    width_mm: float,
    depth_mm: float,
    cover_mm: float = 25.0,
) -> ValidationResult:
    """
    Validate beam geometry with IS 456 constraints.

    Args:
        span_mm: Beam span in mm
        width_mm: Beam width in mm
        depth_mm: Beam total depth in mm
        cover_mm: Clear cover in mm

    Returns:
        ValidationResult with validation status and feedback

    IS 456 Constraints:
        - Minimum width: 150mm (Cl. 26.5.1.1)
        - Minimum depth: 200mm (practical minimum)
        - Width-depth ratio: 1.5 to 3.5 (typical)
        - Span-depth ratio: 10 to 25 (Cl. 23.2.1)
        - Minimum cover: 20mm (Cl. 26.4.2)
    """
    errors = []
    warnings = []
    sanitized = {
        "span_mm": span_mm,
        "width_mm": width_mm,
        "depth_mm": depth_mm,
        "cover_mm": cover_mm,
    }
    suggestion = None

    # Validate span
    if span_mm <= 0:
        errors.append("Span must be greater than 0")
    elif span_mm < 1000:
        warnings.append("Very short span (<1m) - check if mm units are correct")
    elif span_mm > 20000:
        warnings.append(
            "Very long span (>20m) - may need special design considerations"
        )

    # Validate width
    if width_mm <= 0:
        errors.append("Width must be greater than 0")
    elif width_mm < 150:
        errors.append("Width must be ≥150mm per IS 456:2000 Cl. 26.5.1.1")
        suggestion = "Increase width to 230mm or 300mm (standard sizes)"
    elif width_mm > 1000:
        warnings.append("Very wide beam (>1m) - check design assumptions")

    # Validate depth
    if depth_mm <= 0:
        errors.append("Depth must be greater than 0")
    elif depth_mm < 200:
        errors.append("Depth should be ≥200mm (practical minimum)")
        suggestion = "Increase depth to 300mm or 450mm (standard sizes)"
    elif depth_mm > 2000:
        warnings.append("Very deep beam (>2m) - check if special beam design needed")

    # Check width-depth ratio
    if width_mm > 0 and depth_mm > 0:
        d_b_ratio = depth_mm / width_mm
        if d_b_ratio < 1.0:
            warnings.append(
                f"Depth/Width ratio = {d_b_ratio:.2f} is low. "
                "Typical range is 1.5 to 3.5"
            )
        elif d_b_ratio > 4.0:
            warnings.append(
                f"Depth/Width ratio = {d_b_ratio:.2f} is high. "
                "Consider increasing width for better stability"
            )

    # Check span-depth ratio
    if span_mm > 0 and depth_mm > 0:
        span_d_ratio = span_mm / depth_mm
        if span_d_ratio < 7:
            warnings.append(
                f"Span/Depth ratio = {span_d_ratio:.1f} is very low. "
                "Beam may be over-designed"
            )
        elif span_d_ratio > 30:
            errors.append(
                f"Span/Depth ratio = {span_d_ratio:.1f} exceeds typical limit. "
                "Check IS 456:2000 Cl. 23.2.1 deflection criteria"
            )
            suggestion = f"Increase depth to ≥{span_mm / 25:.0f}mm"

    # Validate cover
    if cover_mm < 20:
        errors.append("Cover must be ≥20mm per IS 456:2000 Cl. 26.4.2")
        suggestion = "Use 25mm for mild exposure, 30-40mm for moderate/severe"
    elif cover_mm > 75:
        warnings.append("Very large cover (>75mm) - check exposure condition")

    # Calculate effective depth
    d_eff = depth_mm - cover_mm - 8  # Assuming 16mm bar (8mm to centroid)
    if d_eff < 150:
        errors.append(f"Effective depth = {d_eff:.0f}mm is too low (minimum ~150mm)")

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        sanitized_value=sanitized,
        suggestion=suggestion,
    )


def validate_material_inputs(fck: float, fy: float) -> ValidationResult:
    """
    Validate material properties per IS 456.

    Args:
        fck: Concrete characteristic strength in N/mm²
        fy: Steel yield strength in N/mm²

    Returns:
        ValidationResult with validation status

    IS 456 Standard Grades:
        Concrete: M15, M20, M25, M30, M35, M40, M45, M50
        Steel: Fe 250, Fe 415, Fe 500, Fe 550
    """
    errors = []
    warnings = []
    sanitized = {"fck": fck, "fy": fy}
    suggestion = None

    # Standard concrete grades per IS 456
    standard_fck = [15, 20, 25, 30, 35, 40, 45, 50]

    # Validate concrete grade
    if fck <= 0:
        errors.append("Concrete grade must be positive")
    elif fck < 15:
        errors.append("Minimum concrete grade is M15 per IS 456")
        suggestion = "Use M20 or M25 for structural members"
    elif fck > 50:
        errors.append("Concrete grade >M50 requires special design considerations")
        suggestion = "Consult IS 456:2000 Annex F for high-strength concrete"
    elif fck not in standard_fck:
        warnings.append(
            f"fck = {fck} N/mm² is not a standard grade. "
            f"Standard grades: {standard_fck}"
        )

    # Standard steel grades per IS 456
    standard_fy = [250, 415, 500, 550]

    # Validate steel grade
    if fy <= 0:
        errors.append("Steel grade must be positive")
    elif fy < 250:
        errors.append("Minimum steel grade is Fe 250 per IS 456")
        suggestion = "Use Fe 415 (most common) or Fe 500"
    elif fy > 550:
        errors.append("Steel grade >Fe 550 is not covered by IS 456")
        suggestion = "Use Fe 415 or Fe 500"
    elif fy not in standard_fy:
        warnings.append(
            f"fy = {fy} N/mm² is not a standard grade. "
            f"Standard grades: {standard_fy}"
        )

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        sanitized_value=sanitized,
        suggestion=suggestion,
    )


def validate_loading_inputs(
    dead_load_kn_m: float,
    live_load_kn_m: float,
) -> ValidationResult:
    """
    Validate loading with engineering checks.

    Args:
        dead_load_kn_m: Dead load in kN/m
        live_load_kn_m: Live load in kN/m

    Returns:
        ValidationResult with validation status

    Typical Ranges:
        - Residential: DL = 10-25 kN/m, LL = 8-15 kN/m
        - Commercial: DL = 15-40 kN/m, LL = 15-30 kN/m
        - DL/LL ratio: 0.5 to 4.0 (typical)
    """
    errors = []
    warnings = []
    sanitized = {"dead_load_kn_m": dead_load_kn_m, "live_load_kn_m": live_load_kn_m}
    suggestion = None

    # Validate dead load
    if dead_load_kn_m < 0:
        errors.append("Dead load cannot be negative")
    elif dead_load_kn_m == 0:
        warnings.append("Zero dead load - beam self-weight will be added")
    elif dead_load_kn_m > 500:
        warnings.append("Very high dead load (>500 kN/m) - verify load calculations")

    # Validate live load
    if live_load_kn_m < 0:
        errors.append("Live load cannot be negative")
    elif live_load_kn_m == 0:
        warnings.append("Zero live load - is this intentional?")
    elif live_load_kn_m > 200:
        warnings.append("Very high live load (>200 kN/m) - verify load calculations")

    # Check total load
    total_load = dead_load_kn_m + live_load_kn_m
    if total_load > 1000:
        warnings.append(
            f"Total load = {total_load:.1f} kN/m is very high. "
            "Verify load calculations and consider multiple beams"
        )

    # Check DL/LL ratio
    if live_load_kn_m > 0:
        dl_ll_ratio = dead_load_kn_m / live_load_kn_m
        if dl_ll_ratio < 0.3:
            warnings.append(
                f"DL/LL ratio = {dl_ll_ratio:.2f} is low. " "Typical range: 0.5 to 4.0"
            )
        elif dl_ll_ratio > 5.0:
            warnings.append(
                f"DL/LL ratio = {dl_ll_ratio:.2f} is high. "
                "Check if dead load includes partitions/finishes correctly"
            )

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        sanitized_value=sanitized,
        suggestion=suggestion,
    )


def sanitize_numeric_input(
    value: Any,
    min_val: float,
    max_val: float,
    default: float,
    field_name: str = "value",
) -> tuple[float, Optional[str]]:
    """
    Safely convert and bound numeric input.

    Args:
        value: Input value (any type)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        default: Default value if conversion fails
        field_name: Name of field for error messages

    Returns:
        Tuple of (sanitized_value, error_message)
        error_message is None if successful

    Examples:
        >>> sanitize_numeric_input("5000", 0, 10000, 3000, "span")
        (5000.0, None)

        >>> sanitize_numeric_input("invalid", 0, 10000, 3000, "span")
        (3000.0, "Invalid span: using default 3000.0")

        >>> sanitize_numeric_input(-500, 0, 10000, 3000, "span")
        (0.0, "span = -500.0 is below minimum 0.0, clamped to 0.0")
    """
    try:
        num_val = float(value)
    except (ValueError, TypeError):
        return default, f"Invalid {field_name}: using default {default}"

    # Check bounds
    if num_val < min_val:
        return min_val, (
            f"{field_name} = {num_val} is below minimum {min_val}, "
            f"clamped to {min_val}"
        )
    elif num_val > max_val:
        return max_val, (
            f"{field_name} = {num_val} exceeds maximum {max_val}, "
            f"clamped to {max_val}"
        )

    return num_val, None


def validate_reinforcement_inputs(
    main_bar_dia: int,
    num_bars: int,
    stirrup_dia: int,
    stirrup_spacing: float,
) -> ValidationResult:
    """
    Validate reinforcement details.

    Args:
        main_bar_dia: Main bar diameter in mm
        num_bars: Number of main bars
        stirrup_dia: Stirrup diameter in mm
        stirrup_spacing: Stirrup spacing in mm

    Returns:
        ValidationResult with validation status
    """
    errors = []
    warnings = []
    sanitized = {
        "main_bar_dia": main_bar_dia,
        "num_bars": num_bars,
        "stirrup_dia": stirrup_dia,
        "stirrup_spacing": stirrup_spacing,
    }
    suggestion = None

    # Standard bar sizes per IS 1786
    standard_bar_sizes = [6, 8, 10, 12, 16, 20, 25, 32, 36, 40]

    # Validate main bar diameter
    if main_bar_dia not in standard_bar_sizes:
        errors.append(
            f"Main bar diameter {main_bar_dia}mm is not standard. "
            f"Use: {standard_bar_sizes}"
        )
    elif main_bar_dia < 12:
        warnings.append("Main bars <12mm not recommended for structural beams")
        suggestion = "Use 12mm, 16mm, or 20mm bars"

    # Validate number of bars
    if num_bars < 2:
        errors.append("Minimum 2 bars required per IS 456:2000 Cl. 26.5.1.1")
    elif num_bars > 10:
        warnings.append("Very large number of bars - consider larger bar size")

    # Validate stirrup diameter
    if stirrup_dia not in [6, 8, 10, 12]:
        errors.append("Stirrup diameter should be 6, 8, 10, or 12mm")
    elif stirrup_dia > main_bar_dia / 4:
        warnings.append(
            f"Stirrup diameter ({stirrup_dia}mm) seems large "
            f"relative to main bars ({main_bar_dia}mm)"
        )

    # Validate stirrup spacing
    if stirrup_spacing <= 0:
        errors.append("Stirrup spacing must be positive")
    elif stirrup_spacing < 75:
        errors.append("Minimum stirrup spacing is 75mm (practical limit)")
    elif stirrup_spacing > 300:
        warnings.append(
            "Stirrup spacing >300mm exceeds typical maximum per IS 456:2000 Cl. 26.5.1.5"
        )

    is_valid = len(errors) == 0
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        sanitized_value=sanitized,
        suggestion=suggestion,
    )
