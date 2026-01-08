"""
Result Display Components
=========================

Production-ready reusable components for displaying design results.

Components:
- display_design_status() - Overall pass/fail banner
- display_reinforcement_summary() - Main/shear/compression steel summary
- display_flexure_result() - Flexure design details
- display_shear_result() - Shear design details
- display_summary_metrics() - Key metrics in columns
- display_utilization_meters() - Capacity utilization progress bars
- display_material_properties() - Concrete and steel grades
- display_compliance_checks() - IS 456 compliance checklist

Author: Agent 6 (Streamlit Specialist)
Task: IMPL-002
Status: Production
"""

from typing import List, Optional, Dict
import streamlit as st


def display_design_status(result: dict, show_icon: bool = True):
    """
    Display overall design status banner.

    Args:
        result: Design result dict with 'is_safe' key
        show_icon: Whether to show emoji icon (default: True)

    Example:
        >>> display_design_status(result)
        >>> display_design_status(result, show_icon=False)
    """
    is_safe = result.get("is_safe")

    if is_safe is None:
        st.info("ℹ️ Design status unknown - run analysis to see results")
        return

    if is_safe:
        icon = "✅ " if show_icon else ""
        st.success(f"{icon}**Design is SAFE** - Meets all IS 456 requirements")
    else:
        icon = "❌ " if show_icon else ""
        st.error(
            f"{icon}**Design is UNSAFE** - Does not meet IS 456 requirements. "
            "Modify dimensions or materials."
        )


def display_reinforcement_summary(result: dict, layout: str = "columns"):
    """
    Display reinforcement summary (main, shear, compression, side face steel).

    Args:
        result: Full design result dict
        layout: "columns" (default) or "rows"

    Example:
        >>> display_reinforcement_summary(result)
        >>> display_reinforcement_summary(result, layout="rows")
    """
    flexure = result.get("flexure", {})
    shear = result.get("shear", {})
    detailing = result.get("detailing", {})

    st.markdown("### 🔩 Reinforcement Details")

    # Row 1: Main steel, shear steel, compression steel
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Main Tension Steel**")
        num_bars = flexure.get("num_bars") or 0
        bar_dia = flexure.get("bar_dia") or 0
        ast_prov = flexure.get("ast_provided") or 0
        ast_req = flexure.get("ast_required") or 0

        if num_bars and bar_dia:
            st.markdown(f"📏 **{num_bars} - {bar_dia}mm** bars")
        st.caption(f"Ast = {ast_prov:.0f} mm² (req: {ast_req:.0f} mm²)")

        num_layers = flexure.get("num_layers", 1)
        if num_layers > 1:
            st.info(f"Arranged in {num_layers} layers")

    with col2:
        st.markdown("**Shear Reinforcement**")
        legs = shear.get("legs") or 0
        stirrup_dia = shear.get("stirrup_dia") or 0
        spacing = shear.get("spacing") or 0

        if legs and stirrup_dia and spacing:
            st.markdown(f"📏 **{legs}-legged {stirrup_dia}mm** @ **{spacing:.0f}mm** c/c")

        tau_v = shear.get("tau_v") or 0
        tau_c = shear.get("tau_c") or 0
        st.caption(f"τv = {tau_v:.2f} N/mm² (τc = {tau_c:.2f} N/mm²)")

    with col3:
        st.markdown("**Compression Steel**")
        if flexure.get("is_doubly_reinforced", False):
            asc_req = flexure.get("asc_required") or 0
            st.markdown(f"📏 **Required:** {asc_req:.0f} mm²")
            st.warning("⚠️ Doubly reinforced section")
        else:
            st.markdown("✅ **Not required**")
            st.caption("Singly reinforced section")

    st.markdown("---")

    # Row 2: Side face steel, cover, design status
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("**Side Face Steel**")
        if detailing.get("needs_side_face", False):
            side_area = detailing.get("side_face_area") or 0
            st.markdown(f"📏 **Required:** {side_area:.0f} mm²")
            st.caption("(D > 450mm, per IS 456 Cl. 26.5.1.3)")
        else:
            st.markdown("✅ **Not required**")
            st.caption("(D ≤ 450mm)")

    with col5:
        st.markdown("**Clear Cover**")
        cover = detailing.get("cover") or 0
        if cover:
            st.markdown(f"📏 **{cover} mm**")

    with col6:
        st.markdown("**Design Status**")
        if result.get("is_safe"):
            st.success("✅ **SAFE**")
        else:
            st.error("❌ **UNSAFE**")


def display_flexure_result(flexure: dict, compact: bool = False):
    """
    Display flexure design result details.

    Args:
        flexure: Flexure result dict
        compact: Use compact layout (default: False)

    Example:
        >>> display_flexure_result(result['flexure'])
        >>> display_flexure_result(result['flexure'], compact=True)
    """
    if compact:
        # Compact mode: single line
        ast_req = flexure.get("ast_required") or 0
        ast_prov = flexure.get("ast_provided") or 0
        st.markdown(f"**Ast:** {ast_prov:.0f} mm² (req: {ast_req:.0f} mm²)")
        return

    # Full mode: detailed display
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Steel Area**")
        ast_req = flexure.get("ast_required") or 0
        ast_prov = flexure.get("ast_provided") or 0
        st.markdown(f"Required: {ast_req:.0f} mm²")
        st.markdown(f"Provided: {ast_prov:.0f} mm²")

        if ast_prov >= ast_req:
            st.success("✅ Adequate")
        else:
            st.error("❌ Insufficient")

    with col2:
        st.markdown("**Bar Configuration**")
        num_bars = flexure.get("num_bars") or 0
        bar_dia = flexure.get("bar_dia") or 0
        st.markdown(f"{num_bars} × {bar_dia}mm bars")

        num_layers = flexure.get("num_layers") or 1
        if num_layers > 1:
            st.info(f"{num_layers} layers")

        if flexure.get("is_doubly_reinforced", False):
            st.warning("Doubly reinforced")


def display_shear_result(shear: dict, compact: bool = False):
    """
    Display shear design result details.

    Args:
        shear: Shear result dict
        compact: Use compact layout (default: False)

    Example:
        >>> display_shear_result(result['shear'])
        >>> display_shear_result(result['shear'], compact=True)
    """
    if compact:
        # Compact mode: single line
        spacing = shear.get("spacing") or 0
        st.markdown(f"**Spacing:** {spacing:.0f} mm c/c")
        return

    # Full mode: detailed display
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Stirrup Configuration**")
        legs = shear.get("legs") or 0
        stirrup_dia = shear.get("stirrup_dia") or 0
        spacing = shear.get("spacing") or 0
        st.markdown(f"{legs}-legged {stirrup_dia}mm")
        st.markdown(f"Spacing: {spacing:.0f} mm c/c")

    with col2:
        st.markdown("**Shear Stress**")
        tau_v = shear.get("tau_v") or 0
        tau_c = shear.get("tau_c") or 0
        st.markdown(f"τv = {tau_v:.2f} N/mm²")
        st.markdown(f"τc = {tau_c:.2f} N/mm²")

        if tau_v <= tau_c:
            st.success("✅ Safe")
        else:
            st.error("❌ Unsafe")


def display_summary_metrics(result: dict, metrics: Optional[List[str]] = None):
    """
    Display key metrics in column layout.

    Args:
        result: Full design result dict
        metrics: Optional list of metric keys to display (default: standard 3)

    Example:
        >>> display_summary_metrics(result)
        >>> display_summary_metrics(result, metrics=['ast_required', 'spacing'])
    """
    if metrics is None:
        # Default metrics: steel area, spacing, utilization
        flexure = result.get("flexure", {})
        shear = result.get("shear", {})

        ast_req = flexure.get("ast_required") or 0
        spacing = shear.get("spacing") or 0

        # Calculate utilization (simplified)
        flex_util = 0
        mu_limit = flexure.get("mu_limit_knm")
        if mu_limit and mu_limit > 0:
            flex_util = (ast_req / mu_limit) * 100

        col1, col2, col3 = st.columns(3)
        col1.metric("Steel Area Required", f"{ast_req:.0f} mm²")
        col2.metric("Stirrup Spacing", f"{spacing:.0f} mm c/c")
        col3.metric("Flexure Utilization", f"{flex_util:.1f}%")
    else:
        # Custom metrics
        cols = st.columns(len(metrics))
        for i, metric_key in enumerate(metrics):
            value = result.get("flexure", {}).get(metric_key) or result.get("shear", {}).get(metric_key) or 0
            cols[i].metric(metric_key.replace("_", " ").title(), f"{value:.0f}")


def display_utilization_meters(result: dict, thresholds: Optional[Dict[str, float]] = None):
    """
    Display capacity utilization progress bars.

    Args:
        result: Full design result dict
        thresholds: Optional dict with 'green', 'yellow', 'red' thresholds (default: 80, 95, 100)

    Example:
        >>> display_utilization_meters(result)
        >>> display_utilization_meters(result, thresholds={'green': 70, 'yellow': 90, 'red': 100})
    """
    if thresholds is None:
        thresholds = {"green": 80, "yellow": 95, "red": 100}

    st.markdown("### 📊 Capacity Utilization")

    flexure = result.get("flexure", {})
    shear = result.get("shear", {})

    # Flexure utilization (simplified - would need actual Mu/Mu_limit)
    ast_req = flexure.get("ast_required") or 0
    ast_prov = flexure.get("ast_provided") or 1
    if ast_prov > 0:
        flex_util = (ast_req / ast_prov) * 100
    else:
        flex_util = 0

    st.markdown("**Flexure Utilization**")
    flex_color = "🟢" if flex_util < thresholds["green"] else "🟡" if flex_util < thresholds["yellow"] else "🔴"
    st.markdown(f"{flex_color} {flex_util:.1f}%")
    st.progress(min(flex_util / 100, 1.0))

    # Shear utilization
    tau_v = shear.get("tau_v") or 0
    tau_c = shear.get("tau_c") or 1
    if tau_c > 0:
        shear_util = (tau_v / tau_c) * 100
    else:
        shear_util = 0

    st.markdown("**Shear Utilization**")
    shear_color = "🟢" if shear_util < thresholds["green"] else "🟡" if shear_util < thresholds["yellow"] else "🔴"
    st.markdown(f"{shear_color} {shear_util:.1f}%")
    st.progress(min(shear_util / 100, 1.0))


def display_material_properties(concrete: dict, steel: dict, compact: bool = False):
    """
    Display material properties (concrete and steel grades).

    Args:
        concrete: Concrete dict with 'grade' and 'fck'
        steel: Steel dict with 'grade' and 'fy'
        compact: Use compact layout (default: False)

    Example:
        >>> concrete = {"grade": "M25", "fck": 25}
        >>> steel = {"grade": "Fe415", "fy": 415}
        >>> display_material_properties(concrete, steel)
    """
    if compact:
        # Compact mode: single line
        st.markdown(f"**Materials:** {concrete.get('grade', 'M25')} / {steel.get('grade', 'Fe415')}")
        return

    # Full mode: detailed display
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Concrete**")
        grade = concrete.get("grade", "M25")
        fck = concrete.get("fck", 25)
        st.markdown(f"{grade} (fck = {fck} N/mm²)")

    with col2:
        st.markdown("**Steel**")
        grade = steel.get("grade", "Fe415")
        fy = steel.get("fy", 415)
        st.markdown(f"{grade} (fy = {fy} N/mm²)")


def display_compliance_checks(compliance: dict, show_details: bool = True):
    """
    Display IS 456 compliance checks.

    Args:
        compliance: Compliance dict with 'checks' list
        show_details: Show detailed check descriptions (default: True)

    Example:
        >>> display_compliance_checks(result['compliance'])
        >>> display_compliance_checks(result['compliance'], show_details=False)
    """
    checks = compliance.get("checks", [])

    if not checks:
        st.info("No compliance checks available")
        return

    st.markdown("### ✅ Compliance Checks")

    for check in checks:
        clause = check.get("clause", "")
        description = check.get("description", "")
        passed = check.get("passed", False)

        icon = "✅" if passed else "❌"
        status = "PASS" if passed else "FAIL"

        if show_details:
            st.markdown(f"{icon} **{status}** - {description} (Cl. {clause})")
        else:
            st.markdown(f"{icon} {clause}")
