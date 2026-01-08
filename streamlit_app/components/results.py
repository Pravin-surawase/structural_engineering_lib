"""
Result Display Components
=========================

Reusable components for displaying design results.

Components:
- display_flexure_result() - Flexure design summary
- display_shear_result() - Shear design summary
- display_summary_metrics() - Key metrics in columns
- display_design_status() - Overall pass/fail status

Author: STREAMLIT UI SPECIALIST (Agent 6)
Status: Stub - To be implemented in STREAMLIT-IMPL-004
"""

import streamlit as st


def display_flexure_result(flexure_result: dict):
    """
    Display flexure design result in formatted layout.

    Args:
        flexure_result: FlexureResult dataclass or dict

    Example:
        >>> display_flexure_result(result.flexure)
    """
    # TODO: Implement in STREAMLIT-IMPL-004
    st.info("Flexure result display (placeholder)")


def display_shear_result(shear_result: dict):
    """
    Display shear design result in formatted layout.

    Args:
        shear_result: ShearResult dataclass or dict

    Example:
        >>> display_shear_result(result.shear)
    """
    # TODO: Implement in STREAMLIT-IMPL-004
    st.info("Shear result display (placeholder)")


def display_summary_metrics(result: dict):
    """
    Display key metrics in column layout.

    Args:
        result: BeamDesignOutput dataclass or dict

    Example:
        >>> display_summary_metrics(result)
    """
    # TODO: Implement in STREAMLIT-IMPL-004
    col1, col2, col3 = st.columns(3)
    col1.metric("Steel Area", "— mm²")
    col2.metric("Stirrup Spacing", "— mm")
    col3.metric("Utilization", "—%")


def display_design_status(result: dict):
    """
    Display overall design status.

    Args:
        result: BeamDesignOutput dataclass or dict

    Example:
        >>> display_design_status(result)
    """
    # TODO: Implement in STREAMLIT-IMPL-004
    is_safe = result.get("is_safe", False)
    if is_safe:
        st.success("✅ Design is safe")
    else:
        st.error("❌ Design is not safe")
