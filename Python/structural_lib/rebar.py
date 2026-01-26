# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Rebar Configuration Module — Validation and Application of Rebar Layouts.

This module provides functions for validating and applying rebar configurations
to beam designs. It enforces IS 456:2000 and IS 13920 constraints for spacing,
cover, bar diameters, and arrangement rules.

Key Functions:
    - validate_rebar_config(): Validate rebar configuration against code rules
    - apply_rebar_config(): Apply rebar config and return updated geometry
    - suggest_rebar_layout(): Suggest optimal rebar arrangement

Architecture:
    This module is UI-agnostic and provides canonical validation for:
    - React rebar editor
    - FastAPI validation endpoints
    - CLI input validation
    - Streamlit design tools

Example:
    >>> from structural_lib.rebar import validate_rebar_config, RebarConfig
    >>>
    >>> config = RebarConfig(
    ...     bottom_bars=[(4, 16)],  # 4-16mm bars
    ...     top_bars=[(2, 12)],     # 2-12mm bars
    ...     stirrup_dia=8,
    ...     stirrup_spacing=150,
    ... )
    >>> result = validate_rebar_config(300, 500, 40, config)
    >>> if not result.is_valid:
    ...     print(f"Errors: {result.errors}")

References:
    - IS 456:2000, Clause 26 (Development, Anchorage, and Splicing)
    - IS 456:2000, Clause 26.3 (Spacing of Reinforcement)
    - IS 13920:2016 (Ductile Detailing for Seismic)

Author: Session 46 Agent
Task: TASK-V3-FOUNDATION
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    # Core functions
    "validate_rebar_config",
    "apply_rebar_config",
    "suggest_rebar_layout",
    "check_bar_spacing",
    "check_cover",
    # Result types
    "RebarConfig",
    "RebarValidationResult",
    "RebarWarning",
    "RebarSuggestion",
]


# =============================================================================
# Configuration Types
# =============================================================================


@dataclass
class RebarConfig:
    """Rebar configuration for a beam section.

    Attributes:
        bottom_bars: List of (count, diameter_mm) tuples for bottom layers
        top_bars: List of (count, diameter_mm) tuples for top layers
        stirrup_dia: Stirrup diameter in mm
        stirrup_spacing: Stirrup spacing in mm (uniform or start zone)
        stirrup_spacing_mid: Optional mid-zone spacing (defaults to stirrup_spacing)
        stirrup_legs: Number of stirrup legs (2 or 4)
        is_seismic: Apply seismic detailing rules (IS 13920)
        cover_mm: Clear cover in mm (default 40)
    """

    bottom_bars: list[tuple[int, float]] = field(default_factory=list)
    top_bars: list[tuple[int, float]] = field(default_factory=list)
    stirrup_dia: float = 8.0
    stirrup_spacing: float = 150.0
    stirrup_spacing_mid: float | None = None
    stirrup_legs: int = 2
    is_seismic: bool = False
    cover_mm: float = 40.0

    @property
    def total_bottom_area(self) -> float:
        """Calculate total area of bottom reinforcement (mm²)."""
        return sum(
            count * math.pi * (dia / 2) ** 2
            for count, dia in self.bottom_bars
        )

    @property
    def total_top_area(self) -> float:
        """Calculate total area of top reinforcement (mm²)."""
        return sum(
            count * math.pi * (dia / 2) ** 2
            for count, dia in self.top_bars
        )

    @property
    def total_bottom_bars(self) -> int:
        """Total count of bottom bars."""
        return sum(count for count, _ in self.bottom_bars)

    @property
    def total_top_bars(self) -> int:
        """Total count of top bars."""
        return sum(count for count, _ in self.top_bars)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bottom_bars": self.bottom_bars,
            "top_bars": self.top_bars,
            "stirrup_dia": self.stirrup_dia,
            "stirrup_spacing": self.stirrup_spacing,
            "stirrup_spacing_mid": self.stirrup_spacing_mid,
            "stirrup_legs": self.stirrup_legs,
            "is_seismic": self.is_seismic,
            "cover_mm": self.cover_mm,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RebarConfig:
        """Create from dictionary."""
        return cls(
            bottom_bars=[(int(c), float(d)) for c, d in data.get("bottom_bars", [])],
            top_bars=[(int(c), float(d)) for c, d in data.get("top_bars", [])],
            stirrup_dia=float(data.get("stirrup_dia", 8.0)),
            stirrup_spacing=float(data.get("stirrup_spacing", 150.0)),
            stirrup_spacing_mid=data.get("stirrup_spacing_mid"),
            stirrup_legs=int(data.get("stirrup_legs", 2)),
            is_seismic=bool(data.get("is_seismic", False)),
            cover_mm=float(data.get("cover_mm", 40.0)),
        )


@dataclass
class RebarWarning:
    """Warning from rebar validation.

    Attributes:
        code: Warning code (e.g., "SPACING_TIGHT", "COVER_LOW")
        message: Human-readable warning message
        severity: "error" (blocks), "warning" (caution), "info" (advisory)
        clause: IS code clause reference (e.g., "IS 456, Cl 26.3")
        value: Actual value that triggered warning
        limit: Code limit that was exceeded
    """

    code: str
    message: str
    severity: str = "warning"  # "error", "warning", "info"
    clause: str | None = None
    value: float | None = None
    limit: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "clause": self.clause,
            "value": self.value,
            "limit": self.limit,
        }


@dataclass
class RebarValidationResult:
    """Result from rebar configuration validation.

    Attributes:
        is_valid: True if configuration passes all critical checks
        errors: List of critical errors that block the configuration
        warnings: List of warnings (non-blocking)
        computed: Computed values from validation (spacing, areas, etc.)
    """

    is_valid: bool = True
    errors: list[RebarWarning] = field(default_factory=list)
    warnings: list[RebarWarning] = field(default_factory=list)
    computed: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "computed": self.computed,
        }


@dataclass
class RebarSuggestion:
    """Suggested rebar configuration.

    Attributes:
        config: Suggested RebarConfig
        area_provided: Total steel area provided (mm²)
        utilization: Steel utilization ratio (Ast_required / Ast_provided)
        reason: Reason for this suggestion
    """

    config: RebarConfig
    area_provided: float
    utilization: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "config": self.config.to_dict(),
            "area_provided": self.area_provided,
            "utilization": self.utilization,
            "reason": self.reason,
        }


# =============================================================================
# IS 456 Constants
# =============================================================================

# Minimum clear spacing (IS 456, Cl 26.3.2)
MIN_CLEAR_SPACING_MM = 25.0  # or bar diameter, whichever is greater

# Standard bar diameters (mm)
STANDARD_BAR_DIAS = [8, 10, 12, 16, 20, 25, 28, 32]

# Maximum bar diameter ratio (larger to smaller)
MAX_BAR_DIA_RATIO = 2.0

# Minimum cover by exposure (IS 456, Table 16)
MIN_COVER_MILD = 20.0
MIN_COVER_MODERATE = 30.0
MIN_COVER_SEVERE = 45.0
MIN_COVER_VERY_SEVERE = 50.0
MIN_COVER_EXTREME = 75.0

# Seismic requirements (IS 13920)
SEISMIC_MIN_STIRRUP_DIA = 8.0
SEISMIC_MAX_STIRRUP_SPACING = 150.0


# =============================================================================
# Validation Functions
# =============================================================================


def check_bar_spacing(
    beam_width: float,
    cover: float,
    stirrup_dia: float,
    bars: list[tuple[int, float]],
    *,
    is_seismic: bool = False,
) -> list[RebarWarning]:
    """Check bar spacing against IS 456 requirements.

    Args:
        beam_width: Beam width in mm
        cover: Clear cover in mm
        stirrup_dia: Stirrup diameter in mm
        bars: List of (count, diameter) tuples
        is_seismic: Apply IS 13920 requirements

    Returns:
        List of warnings/errors for spacing issues
    """
    warnings: list[RebarWarning] = []

    if not bars:
        return warnings

    # Calculate available width for bars
    available = beam_width - 2 * cover - 2 * stirrup_dia

    # Calculate total bar width and required spacing
    for count, dia in bars:
        if count < 2:
            continue

        total_bar_width = count * dia
        total_spacing = available - total_bar_width
        clear_spacing = total_spacing / (count - 1) if count > 1 else 0

        # Minimum spacing rule (IS 456, Cl 26.3.2)
        min_required = max(MIN_CLEAR_SPACING_MM, dia, 1.0 * dia)  # or aggregate + 5mm

        if clear_spacing < min_required:
            warnings.append(
                RebarWarning(
                    code="SPACING_TOO_TIGHT",
                    message=f"Clear spacing {clear_spacing:.1f}mm < {min_required:.1f}mm required",
                    severity="error",
                    clause="IS 456, Cl 26.3.2",
                    value=clear_spacing,
                    limit=min_required,
                )
            )
        elif clear_spacing < min_required * 1.2:
            warnings.append(
                RebarWarning(
                    code="SPACING_MARGINAL",
                    message=f"Clear spacing {clear_spacing:.1f}mm is close to minimum",
                    severity="warning",
                    clause="IS 456, Cl 26.3.2",
                    value=clear_spacing,
                    limit=min_required,
                )
            )

    return warnings


def check_cover(
    cover: float,
    *,
    exposure: str = "moderate",
    is_seismic: bool = False,
) -> list[RebarWarning]:
    """Check cover against IS 456 requirements.

    Args:
        cover: Clear cover in mm
        exposure: Exposure condition ("mild", "moderate", "severe", etc.)
        is_seismic: Apply IS 13920 requirements

    Returns:
        List of warnings/errors for cover issues
    """
    warnings: list[RebarWarning] = []

    # Get minimum cover for exposure
    exposure_limits = {
        "mild": MIN_COVER_MILD,
        "moderate": MIN_COVER_MODERATE,
        "severe": MIN_COVER_SEVERE,
        "very_severe": MIN_COVER_VERY_SEVERE,
        "extreme": MIN_COVER_EXTREME,
    }
    min_cover = exposure_limits.get(exposure.lower(), MIN_COVER_MODERATE)

    if cover < min_cover:
        warnings.append(
            RebarWarning(
                code="COVER_INSUFFICIENT",
                message=f"Cover {cover}mm < {min_cover}mm required for {exposure} exposure",
                severity="error",
                clause="IS 456, Table 16",
                value=cover,
                limit=min_cover,
            )
        )

    return warnings


def validate_rebar_config(
    beam_width: float,
    beam_depth: float,
    cover: float,
    config: RebarConfig,
    *,
    ast_required: float | None = None,
    exposure: str = "moderate",
) -> RebarValidationResult:
    """Validate rebar configuration against IS 456 requirements.

    Checks:
    - Bar spacing (horizontal and vertical clearance)
    - Cover requirements
    - Bar diameter consistency
    - Stirrup requirements
    - Optional: steel area vs required

    Args:
        beam_width: Beam width in mm
        beam_depth: Beam overall depth in mm
        cover: Clear cover in mm
        config: Rebar configuration to validate
        ast_required: Optional required steel area for check
        exposure: Exposure condition for cover check

    Returns:
        RebarValidationResult with errors, warnings, and computed values

    Example:
        >>> result = validate_rebar_config(300, 500, 40, config)
        >>> if not result.is_valid:
        ...     for error in result.errors:
        ...         print(f"{error.code}: {error.message}")
    """
    errors: list[RebarWarning] = []
    warnings: list[RebarWarning] = []
    computed: dict[str, Any] = {}

    # Check cover
    cover_issues = check_cover(cover, exposure=exposure, is_seismic=config.is_seismic)
    for issue in cover_issues:
        if issue.severity == "error":
            errors.append(issue)
        else:
            warnings.append(issue)

    # Check bottom bar spacing
    bottom_spacing = check_bar_spacing(
        beam_width=beam_width,
        cover=cover,
        stirrup_dia=config.stirrup_dia,
        bars=config.bottom_bars,
        is_seismic=config.is_seismic,
    )
    for issue in bottom_spacing:
        if issue.severity == "error":
            errors.append(issue)
        else:
            warnings.append(issue)

    # Check top bar spacing
    top_spacing = check_bar_spacing(
        beam_width=beam_width,
        cover=cover,
        stirrup_dia=config.stirrup_dia,
        bars=config.top_bars,
        is_seismic=config.is_seismic,
    )
    for issue in top_spacing:
        if issue.severity == "error":
            errors.append(issue)
        else:
            warnings.append(issue)

    # Check stirrup requirements
    if config.is_seismic:
        if config.stirrup_dia < SEISMIC_MIN_STIRRUP_DIA:
            errors.append(
                RebarWarning(
                    code="STIRRUP_DIA_SEISMIC",
                    message=f"Stirrup dia {config.stirrup_dia}mm < {SEISMIC_MIN_STIRRUP_DIA}mm for seismic",
                    severity="error",
                    clause="IS 13920, Cl 6.3",
                    value=config.stirrup_dia,
                    limit=SEISMIC_MIN_STIRRUP_DIA,
                )
            )
        if config.stirrup_spacing > SEISMIC_MAX_STIRRUP_SPACING:
            errors.append(
                RebarWarning(
                    code="STIRRUP_SPACING_SEISMIC",
                    message=f"Stirrup spacing {config.stirrup_spacing}mm > {SEISMIC_MAX_STIRRUP_SPACING}mm for seismic",
                    severity="error",
                    clause="IS 13920, Cl 6.3",
                    value=config.stirrup_spacing,
                    limit=SEISMIC_MAX_STIRRUP_SPACING,
                )
            )

    # Check bar diameter consistency
    all_dias = [d for _, d in config.bottom_bars] + [d for _, d in config.top_bars]
    if all_dias:
        max_dia = max(all_dias)
        min_dia = min(all_dias)
        if max_dia / min_dia > MAX_BAR_DIA_RATIO:
            warnings.append(
                RebarWarning(
                    code="BAR_DIA_RATIO",
                    message=f"Large diameter ratio {max_dia}/{min_dia} = {max_dia/min_dia:.1f} (limit {MAX_BAR_DIA_RATIO})",
                    severity="warning",
                    clause="Good practice",
                    value=max_dia / min_dia,
                    limit=MAX_BAR_DIA_RATIO,
                )
            )

    # Check steel area if required
    if ast_required is not None:
        ast_provided = config.total_bottom_area
        computed["ast_required"] = ast_required
        computed["ast_provided"] = ast_provided
        computed["utilization"] = ast_required / ast_provided if ast_provided > 0 else 0

        if ast_provided < ast_required:
            errors.append(
                RebarWarning(
                    code="STEEL_INSUFFICIENT",
                    message=f"Steel area {ast_provided:.0f}mm² < {ast_required:.0f}mm² required",
                    severity="error",
                    clause="IS 456, Cl 26.5.1",
                    value=ast_provided,
                    limit=ast_required,
                )
            )
        elif ast_provided > ast_required * 1.5:
            warnings.append(
                RebarWarning(
                    code="STEEL_EXCESSIVE",
                    message=f"Steel area {ast_provided:.0f}mm² is {(ast_provided/ast_required-1)*100:.0f}% more than required",
                    severity="info",
                    clause="Economics",
                    value=ast_provided,
                    limit=ast_required * 1.5,
                )
            )

    # Compute additional metrics
    computed["total_bottom_bars"] = config.total_bottom_bars
    computed["total_top_bars"] = config.total_top_bars
    computed["total_bottom_area"] = config.total_bottom_area
    computed["total_top_area"] = config.total_top_area

    return RebarValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        computed=computed,
    )


def apply_rebar_config(
    beam_width: float,
    beam_depth: float,
    cover: float,
    config: RebarConfig,
) -> dict[str, Any]:
    """Apply rebar configuration and return 3D geometry data.

    Validates configuration and generates geometry data for visualization.

    Args:
        beam_width: Beam width in mm
        beam_depth: Beam overall depth in mm
        cover: Clear cover in mm
        config: Rebar configuration to apply

    Returns:
        Dictionary with:
        - validation: Validation result
        - geometry: 3D geometry data for rebars

    Example:
        >>> result = apply_rebar_config(300, 500, 40, config)
        >>> if result["validation"]["is_valid"]:
        ...     geometry = result["geometry"]
    """
    # Validate first
    validation = validate_rebar_config(beam_width, beam_depth, cover, config)

    # Generate geometry even if invalid (for preview)
    from .visualization.geometry_3d import cross_section_geometry

    geometry = cross_section_geometry(
        width=beam_width,
        depth=beam_depth,
        cover=cover,
        bottom_bars=config.bottom_bars,
        top_bars=config.top_bars,
        stirrup_dia=config.stirrup_dia,
    )

    return {
        "validation": validation.to_dict(),
        "geometry": geometry.to_dict(),
    }


def suggest_rebar_layout(
    beam_width: float,
    beam_depth: float,
    cover: float,
    ast_required: float,
    *,
    preferred_dias: list[float] | None = None,
    is_seismic: bool = False,
    max_layers: int = 2,
) -> list[RebarSuggestion]:
    """Suggest optimal rebar arrangements for required steel area.

    Generates multiple layout options sorted by efficiency.

    Args:
        beam_width: Beam width in mm
        beam_depth: Beam overall depth in mm
        cover: Clear cover in mm
        ast_required: Required steel area in mm²
        preferred_dias: Preferred bar diameters (default: standard sizes)
        is_seismic: Apply IS 13920 requirements
        max_layers: Maximum bar layers allowed

    Returns:
        List of RebarSuggestion sorted by utilization (best first)

    Example:
        >>> suggestions = suggest_rebar_layout(300, 500, 40, ast_required=800)
        >>> for s in suggestions[:3]:
        ...     print(f"{s.config.bottom_bars}: {s.utilization:.1%} utilization")
    """
    suggestions: list[RebarSuggestion] = []
    preferred_dias = preferred_dias or [12, 16, 20, 25]

    # Available width for bars (single layer)
    stirrup_dia = 10.0 if is_seismic else 8.0
    available = beam_width - 2 * cover - 2 * stirrup_dia

    for dia in preferred_dias:
        # Calculate max bars that fit
        min_spacing = max(MIN_CLEAR_SPACING_MM, dia)
        max_bars = int((available + min_spacing) / (dia + min_spacing))
        max_bars = max(2, min(max_bars, 8))  # Limit range

        # Find optimal count
        area_per_bar = math.pi * (dia / 2) ** 2

        for count in range(2, max_bars + 1):
            area_provided = count * area_per_bar

            if area_provided >= ast_required * 0.95:  # Within 5%
                config = RebarConfig(
                    bottom_bars=[(count, dia)],
                    top_bars=[(2, min(dia, 12))],  # Nominal top
                    stirrup_dia=stirrup_dia,
                    stirrup_spacing=150 if is_seismic else 200,
                    is_seismic=is_seismic,
                    cover_mm=cover,
                )

                # Validate
                result = validate_rebar_config(
                    beam_width, beam_depth, cover, config,
                    ast_required=ast_required,
                )

                if result.is_valid:
                    utilization = ast_required / area_provided
                    suggestions.append(
                        RebarSuggestion(
                            config=config,
                            area_provided=area_provided,
                            utilization=utilization,
                            reason=f"{count}-{int(dia)}mm bars, {utilization:.0%} utilization",
                        )
                    )
                    break  # Move to next diameter

    # Sort by utilization (higher is better, closer to 100%)
    suggestions.sort(key=lambda s: abs(1.0 - s.utilization))

    return suggestions
