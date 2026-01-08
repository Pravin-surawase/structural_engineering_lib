"""
Input Components
================

Reusable input widgets with validation and consistent styling.

Components:
- dimension_input() - Number input with real-time validation
- material_selector() - Dropdown for concrete/steel grades
- load_input() - Moment and shear inputs
- support_condition_selector() - Simply supported, cantilever, etc.

All components return (value, is_valid) tuples for validation tracking.

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: Stub - To be implemented in STREAMLIT-IMPL-002
"""

import streamlit as st
from typing import Tuple


def dimension_input(
    label: str,
    min_value: float,
    max_value: float,
    default_value: float,
    unit: str = "mm",
    help_text: str = None,
    key: str = None
) -> Tuple[float, bool]:
    """
    Dimension input with real-time validation.

    Args:
        label: Display label (e.g., "Span")
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default_value: Default value
        unit: Unit string (e.g., "mm", "kN")
        help_text: Tooltip text
        key: Unique key for Streamlit

    Returns:
        (value, is_valid) tuple

    Example:
        >>> span, is_valid = dimension_input("Span", 1000, 12000, 5000, "mm")
        >>> if is_valid:
        ...     # Use span value
    """
    # TODO: Implement in STREAMLIT-IMPL-002
    value = st.number_input(
        f"{label} ({unit})",
        min_value=min_value,
        max_value=max_value,
        value=default_value,
        help=help_text,
        key=key
    )
    is_valid = min_value <= value <= max_value
    return value, is_valid


def material_selector(
    material_type: str,
    key: str = None
) -> dict:
    """
    Material grade selector.

    Args:
        material_type: "concrete" or "steel"
        key: Unique key for Streamlit

    Returns:
        dict with grade, strength, cost_factor

    Example:
        >>> concrete = material_selector("concrete")
        >>> print(concrete)
        {'grade': 'M25', 'fck': 25, 'cost_factor': 1.15}
    """
    # TODO: Implement in STREAMLIT-IMPL-002
    if material_type == "concrete":
        grades = {"M20": 20, "M25": 25, "M30": 30}
        selected = st.selectbox("Concrete Grade", list(grades.keys()), index=1, key=key)
        return {"grade": selected, "fck": grades[selected]}
    else:
        grades = {"Fe415": 415, "Fe500": 500}
        selected = st.selectbox("Steel Grade", list(grades.keys()), index=1, key=key)
        return {"grade": selected, "fy": grades[selected]}
