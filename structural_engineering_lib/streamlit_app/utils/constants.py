"""Centralized constants for Streamlit UI pages.

This module consolidates commonly used constants across pages to:
1. Ensure consistency in defaults
2. Enable easy updates to IS 456 parameters
3. Reduce duplication across pages

TASK-602.5: Constants extraction from beam_design.py and cost_optimizer.py

Usage:
    from utils.constants import (
        CONCRETE_GRADE_MAP,
        STEEL_GRADE_MAP,
        EXPOSURE_COVER_MAP,
        DEFAULT_BEAM_INPUTS,
    )
"""

from __future__ import annotations

# =============================================================================
# MATERIAL GRADE MAPPINGS
# =============================================================================

CONCRETE_GRADE_MAP: dict[str, int] = {
    "M20": 20,
    "M25": 25,
    "M30": 30,
    "M35": 35,
    "M40": 40,
}
"""Maps concrete grade labels to characteristic strength fck (N/mm²)."""

STEEL_GRADE_MAP: dict[str, int] = {
    "Fe415": 415,
    "Fe500": 500,
    "Fe550": 550,
}
"""Maps steel grade labels to yield strength fy (N/mm²)."""

CONCRETE_GRADES: list[str] = list(CONCRETE_GRADE_MAP.keys())
"""Available concrete grade options for UI dropdowns."""

STEEL_GRADES: list[str] = list(STEEL_GRADE_MAP.keys())
"""Available steel grade options for UI dropdowns."""


# =============================================================================
# EXPOSURE & COVER (IS 456 Table 16)
# =============================================================================

EXPOSURE_COVER_MAP: dict[str, dict[str, int]] = {
    "Mild": {"cover": 20},
    "Moderate": {"cover": 30},
    "Severe": {"cover": 45},
    "Very Severe": {"cover": 50},
    "Extreme": {"cover": 75},
}
"""Minimum clear cover (mm) per exposure condition as per IS 456 Table 16."""

EXPOSURE_CONDITIONS: list[str] = list(EXPOSURE_COVER_MAP.keys())
"""Available exposure conditions for UI dropdowns."""


def get_cover_for_exposure(exposure: str, default: int = 30) -> int:
    """Get minimum cover for given exposure condition.

    Args:
        exposure: Exposure condition name
        default: Default cover if exposure not found

    Returns:
        Minimum cover in mm
    """
    return EXPOSURE_COVER_MAP.get(exposure, {"cover": default})["cover"]


# =============================================================================
# DEFAULT INPUT VALUES
# =============================================================================

DEFAULT_BEAM_INPUTS: dict = {
    "span_mm": 5000.0,
    "b_mm": 300.0,
    "D_mm": 500.0,
    "d_mm": 450.0,
    "concrete_grade": "M25",
    "steel_grade": "Fe500",
    "mu_knm": 120.0,
    "vu_kn": 80.0,
    "exposure": "Moderate",
    "support_condition": "Simply Supported",
    "design_computed": False,
    "design_result": None,
    "last_input_hash": None,
}
"""Default beam input values for session state initialization."""

DEFAULT_CONCRETE_GRADE: str = "M25"
DEFAULT_STEEL_GRADE: str = "Fe500"
DEFAULT_EXPOSURE: str = "Moderate"


# =============================================================================
# UI CONFIGURATION
# =============================================================================

CACHE_TTL_DESIGN: int = 300  # 5-min TTL for design calculations
CACHE_TTL_VIZ: int = 600  # 10-min TTL for visualizations
CACHE_SIZE_DESIGN_MB: int = 50
CACHE_SIZE_VIZ_MB: int = 30

# Auto-refresh intervals for fragments
FRAGMENT_REFRESH_CACHE_STATS: int = 10  # seconds


# =============================================================================
# DIMENSION LIMITS (IS 456 practical ranges)
# =============================================================================

BEAM_WIDTH_MIN: float = 200.0  # mm
BEAM_WIDTH_MAX: float = 600.0  # mm
BEAM_DEPTH_MIN: float = 300.0  # mm
BEAM_DEPTH_MAX: float = 1200.0  # mm
SPAN_MIN: float = 1000.0  # mm
SPAN_MAX: float = 15000.0  # mm

# Steel area limits
MIN_STEEL_PERCENTAGE: float = 0.12  # % for flexural members
MAX_STEEL_PERCENTAGE: float = 4.0  # % maximum

# Moment/shear limits for typical beams
MOMENT_MIN: float = 10.0  # kN·m
MOMENT_MAX: float = 1000.0  # kN·m
SHEAR_MIN: float = 5.0  # kN
SHEAR_MAX: float = 500.0  # kN
