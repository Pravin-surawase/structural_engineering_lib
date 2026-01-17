"""
Input Components
================

Reusable input widgets with validation and consistent styling.

Components:
- dimension_input() - Number input with real-time validation
- material_selector() - Dropdown for concrete/steel grades
- load_input() - Moment and shear inputs
- exposure_selector() - Exposure condition selector
- support_condition_selector() - Simply supported, cantilever, etc.

All components follow IS 456 theme and WCAG 2.1 Level AA accessibility.

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: ✅ IMPLEMENTED (STREAMLIT-IMPL-002)
"""

import streamlit as st
from typing import Tuple, Dict, Optional


# Material property databases (IS 456:2000)
CONCRETE_GRADES = {
    "M20": {
        "fck": 20,
        "ec": 22360,
        "cost_factor": 1.0,
        "description": "General construction",
    },
    "M25": {
        "fck": 25,
        "ec": 25000,
        "cost_factor": 1.15,
        "description": "Standard beams/columns",
    },
    "M30": {"fck": 30, "ec": 27386, "cost_factor": 1.30, "description": "Heavy loads"},
    "M35": {
        "fck": 35,
        "ec": 29580,
        "cost_factor": 1.45,
        "description": "High-rise structures",
    },
    "M40": {
        "fck": 40,
        "ec": 31623,
        "cost_factor": 1.60,
        "description": "Prestressed concrete",
    },
}

STEEL_GRADES = {
    "Fe415": {
        "fy": 415,
        "es": 200000,
        "cost_factor": 1.0,
        "description": "Standard reinforcement",
    },
    "Fe500": {
        "fy": 500,
        "es": 200000,
        "cost_factor": 1.12,
        "description": "High-strength (common)",
    },
    "Fe550": {
        "fy": 550,
        "es": 200000,
        "cost_factor": 1.25,
        "description": "High-strength (special)",
    },
}

EXPOSURE_CONDITIONS = {
    "Mild": {
        "cover": 20,
        "max_crack_width": 0.3,
        "description": "Protected from weather",
    },
    "Moderate": {"cover": 30, "max_crack_width": 0.3, "description": "Normal exposure"},
    "Severe": {
        "cover": 45,
        "max_crack_width": 0.2,
        "description": "Coastal, industrial",
    },
    "Very Severe": {
        "cover": 50,
        "max_crack_width": 0.2,
        "description": "Marine, chemical",
    },
    "Extreme": {"cover": 75, "max_crack_width": 0.1, "description": "Severe marine"},
}

SUPPORT_CONDITIONS = {
    "Simply Supported": {"end_condition": "pinned-pinned", "moment_factor": 1.0},
    "Continuous": {"end_condition": "continuous", "moment_factor": 0.8},
    "Cantilever": {"end_condition": "fixed-free", "moment_factor": 2.0},
    "Fixed Both Ends": {"end_condition": "fixed-fixed", "moment_factor": 0.67},
}


def dimension_input(
    label: str,
    min_value: float,
    max_value: float,
    default_value: float,
    unit: str = "mm",
    help_text: Optional[str] = None,
    key: Optional[str] = None,
    step: float = 1.0,
    show_validation: bool = True,
) -> Tuple[float, bool]:
    """
    Dimension input with real-time validation and visual feedback.

    Features:
    - Real-time validation with colored feedback
    - Warning for borderline values
    - Typical range hints
    - WCAG 2.1 AA accessible (icons + colors)

    Args:
        label: Display label (e.g., "Span")
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default_value: Default value
        unit: Unit string (e.g., "mm", "kN", "kNm")
        help_text: Tooltip text
        key: Unique key for Streamlit
        step: Increment step
        show_validation: Show validation feedback

    Returns:
        (value, is_valid) tuple

    Example:
        >>> span, is_valid = dimension_input("Span", 1000, 12000, 5000, "mm")
        >>> if is_valid:
        ...     st.success("Valid span!")
    """
    # Build help text with typical range
    full_help = help_text or f"Typical range: {min_value}-{max_value} {unit}"

    # Input widget
    value = st.number_input(
        f"{label} ({unit})",
        min_value=min_value,
        max_value=max_value,
        value=default_value,
        step=step,
        help=full_help,
        key=key,
    )

    # Validation
    is_valid = min_value <= value <= max_value

    # Visual feedback (if enabled)
    if show_validation:
        range_size = max_value - min_value
        warn_low = min_value + 0.1 * range_size
        warn_high = max_value - 0.1 * range_size

        if not is_valid:
            st.error(f"❌ {label} must be between {min_value} and {max_value} {unit}")
        elif value < warn_low:
            st.warning(
                f"⚠️ {label} is very small. Typical minimum: {warn_low:.0f} {unit}"
            )
        elif value > warn_high:
            st.warning(
                f"⚠️ {label} is very large. Typical maximum: {warn_high:.0f} {unit}"
            )
        else:
            st.success(f"✅ {label} is within typical range")

    return value, is_valid


def material_selector(
    material_type: str,
    default_grade: Optional[str] = None,
    key: Optional[str] = None,
    show_properties: bool = True,
) -> Dict[str, any]:
    """
    Material grade selector with properties per IS 456:2000.

    Features:
    - Grade selection with descriptions
    - Material properties (fck/fy, Ec/Es, cost factors)
    - Visual property display
    - IS 456 clause references

    Args:
        material_type: "concrete" or "steel"
        default_grade: Default grade (e.g., "M25", "Fe500")
        key: Unique key for Streamlit
        show_properties: Show property information

    Returns:
        dict with grade, strength, modulus, cost_factor, etc.

    Example:
        >>> concrete = material_selector("concrete", default_grade="M25")
        >>> print(concrete['fck'])  # 25
        >>> print(concrete['cost_factor'])  # 1.15
    """
    material_type = material_type.lower()

    if material_type == "concrete":
        grades_db = CONCRETE_GRADES
        default_idx = (
            list(grades_db.keys()).index(default_grade) if default_grade else 1
        )

        # Selectbox - show grade code only (description shown as caption)
        grades = list(grades_db.keys())
        selected_grade = st.selectbox(
            "Concrete Grade",
            options=grades,
            index=default_idx,
            key=key,
            help="IS 456 Table 2 - Characteristic strength",
        )

        props = grades_db[selected_grade]

        # Show description below dropdown
        st.caption(f"📋 {props['description']}")

        # Build result
        result = {
            "grade": selected_grade,
            "fck": props["fck"],  # N/mm²
            "ec": props["ec"],  # N/mm² (Modulus)
            "cost_factor": props["cost_factor"],
            "description": props["description"],
            "material_type": "concrete",
        }

        # Show properties
        if show_properties:
            col1, col2, col3 = st.columns(3)
            col1.metric("fck", f"{props['fck']} N/mm²", help="Characteristic strength")
            col2.metric("Ec", f"{props['ec']:.0f} N/mm²", help="Modulus of elasticity")
            col3.metric(
                "Cost Factor", f"{props['cost_factor']:.2f}x", help="Relative to M20"
            )

    else:  # steel
        grades_db = STEEL_GRADES
        default_idx = (
            list(grades_db.keys()).index(default_grade) if default_grade else 1
        )

        # Selectbox - show grade code only (description shown as caption)
        grades = list(grades_db.keys())
        selected_grade = st.selectbox(
            "Steel Grade",
            options=grades,
            index=default_idx,
            key=key,
            help="IS 456 Cl. 5.6 - Yield strength",
        )

        props = grades_db[selected_grade]

        # Show description below dropdown
        st.caption(f"📋 {props['description']}")

        # Build result
        result = {
            "grade": selected_grade,
            "fy": props["fy"],  # N/mm²
            "es": props["es"],  # N/mm²
            "cost_factor": props["cost_factor"],
            "description": props["description"],
            "material_type": "steel",
        }

        # Show properties
        if show_properties:
            col1, col2, col3 = st.columns(3)
            col1.metric("fy", f"{props['fy']} N/mm²", help="Yield strength")
            col2.metric("Es", f"{props['es']:.0f} N/mm²", help="Modulus of elasticity")
            col3.metric(
                "Cost Factor", f"{props['cost_factor']:.2f}x", help="Relative to Fe415"
            )

    return result


def load_input(
    default_moment: float = 100.0,
    default_shear: float = 50.0,
    key_prefix: Optional[str] = None,
) -> Dict[str, float]:
    """
    Load input for moment and shear forces.

    Features:
    - Moment and shear inputs side-by-side
    - Typical range hints
    - Warning for unusual ratios

    Args:
        default_moment: Default moment (kNm)
        default_shear: Default shear (kN)
        key_prefix: Prefix for widget keys

    Returns:
        dict with mu_knm, vu_kn

    Example:
        >>> loads = load_input(default_moment=120, default_shear=80)
        >>> print(loads['mu_knm'])  # 120
    """
    col1, col2 = st.columns(2)

    with col1:
        mu_knm, mu_valid = dimension_input(
            label="Moment",
            min_value=1.0,
            max_value=1000.0,
            default_value=default_moment,
            unit="kNm",
            help_text="Factored design moment (1.5 × service load)",
            key=f"{key_prefix}_moment" if key_prefix else None,
            show_validation=False,
        )

    with col2:
        vu_kn, vu_valid = dimension_input(
            label="Shear",
            min_value=1.0,
            max_value=500.0,
            default_value=default_shear,
            unit="kN",
            help_text="Factored design shear (1.5 × service load)",
            key=f"{key_prefix}_shear" if key_prefix else None,
            show_validation=False,
        )

    # Check moment-shear ratio (typical M/V = span/2 for simply supported)
    if mu_valid and vu_valid and vu_kn > 0:
        ratio = mu_knm / vu_kn
        if ratio < 1.0:
            st.warning("⚠️ Moment/Shear ratio is low (<1m). Verify loads are correct.")
        elif ratio > 15.0:
            st.warning("⚠️ Moment/Shear ratio is high (>15m). Verify loads are correct.")

    return {"mu_knm": mu_knm, "vu_kn": vu_kn}


def exposure_selector(
    default: str = "Moderate", key: Optional[str] = None, show_requirements: bool = True
) -> Dict[str, any]:
    """
    Exposure condition selector (IS 456 Table 16).

    Features:
    - Exposure categories with descriptions
    - Cover and crack width requirements
    - Visual requirement display

    Args:
        default: Default exposure ("Mild", "Moderate", etc.)
        key: Unique key for Streamlit
        show_requirements: Show cover and crack width

    Returns:
        dict with exposure, cover, max_crack_width, description

    Example:
        >>> exposure = exposure_selector(default="Moderate")
        >>> print(exposure['cover'])  # 30
    """
    # Selectbox - show exposure name only (description as caption)
    exposures = list(EXPOSURE_CONDITIONS.keys())
    default_idx = exposures.index(default)

    selected_exposure = st.selectbox(
        "Exposure",
        options=exposures,
        index=default_idx,
        key=key,
        help="IS 456 Table 16 - Environmental classification",
    )

    props = EXPOSURE_CONDITIONS[selected_exposure]

    # Show description below dropdown
    st.caption(f"📋 {props['description']}")

    # Build result
    result = {
        "exposure": selected_exposure,
        "cover": props["cover"],  # mm
        "max_crack_width": props["max_crack_width"],  # mm
        "description": props["description"],
    }

    # Show requirements
    if show_requirements:
        col1, col2 = st.columns(2)
        col1.metric("Min Cover", f"{props['cover']} mm", help="IS 456 Cl. 26.4")
        col2.metric(
            "Max Crack Width",
            f"{props['max_crack_width']} mm",
            help="IS 456 Cl. 35.3.2",
        )

    return result


def support_condition_selector(
    default: str = "Simply Supported", key: Optional[str] = None
) -> Dict[str, any]:
    """
    Support condition selector for structural analysis.

    Features:
    - Standard support types
    - Moment adjustment factors

    Args:
        default: Default condition
        key: Unique key for Streamlit

    Returns:
        dict with condition, end_condition, moment_factor

    Example:
        >>> support = support_condition_selector()
        >>> print(support['moment_factor'])  # 1.0 for simply supported
    """
    # Selectbox - compact label
    selected = st.selectbox(
        "Support",
        list(SUPPORT_CONDITIONS.keys()),
        index=list(SUPPORT_CONDITIONS.keys()).index(default),
        key=key,
        help="Structural support configuration",
    )

    props = SUPPORT_CONDITIONS[selected]

    return {
        "condition": selected,
        "end_condition": props["end_condition"],
        "moment_factor": props["moment_factor"],
    }
