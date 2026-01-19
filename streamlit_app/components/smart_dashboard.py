# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
SmartDesigner Dashboard Component.

Provides visual components for displaying SmartDesigner analysis results
including overall scores, key issues, quick wins, and detailed metrics.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_score_gauge(score: float, label: str = "Score") -> None:
    """Render a visual gauge for a score (0-1 scale)."""
    percentage = int(score * 100)

    # Color based on score
    if percentage >= 80:
        color = "#28a745"  # Green
        emoji = "🟢"
    elif percentage >= 60:
        color = "#ffc107"  # Yellow
        emoji = "🟡"
    else:
        color = "#dc3545"  # Red
        emoji = "🔴"

    # Custom CSS for gauge
    st.markdown(
        f"""
        <div style="text-align: center;">
            <div style="font-size: 2.5em; font-weight: bold; color: {color};">
                {emoji} {percentage}%
            </div>
            <div style="font-size: 0.9em; color: #666;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_breakdown(
    safety: float,
    cost: float,
    constructability: float,
    robustness: float,
) -> None:
    """Render a breakdown of individual scores."""
    cols = st.columns(4)

    scores = [
        ("🛡️ Safety", safety),
        ("💰 Cost", cost),
        ("🏗️ Build", constructability),
        ("🔧 Robust", robustness),
    ]

    for col, (label, score) in zip(cols, scores):
        with col:
            percentage = int(score * 100)
            color = (
                "#28a745"
                if percentage >= 80
                else ("#ffc107" if percentage >= 60 else "#dc3545")
            )
            st.markdown(
                f"""
                <div style="text-align: center; padding: 10px;
                            background-color: rgba(0,0,0,0.05); border-radius: 8px;">
                    <div style="font-size: 1.5em; font-weight: bold; color: {color};">
                        {percentage}%
                    </div>
                    <div style="font-size: 0.8em; color: #666;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_status_badge(status: str) -> None:
    """Render a status badge (PASS/WARNING/FAIL)."""
    status_config = {
        "PASS": ("✅", "#28a745", "All checks passed"),
        "WARNING": ("⚠️", "#ffc107", "Some issues need attention"),
        "FAIL": ("❌", "#dc3545", "Critical issues found"),
    }

    emoji, color, description = status_config.get(
        status, ("❓", "#6c757d", "Unknown status")
    )

    st.markdown(
        f"""
        <div style="display: inline-block; padding: 8px 16px;
                    background-color: {color}20; border: 2px solid {color};
                    border-radius: 20px; margin: 10px 0;">
            <span style="font-size: 1.2em;">{emoji}</span>
            <span style="color: {color}; font-weight: bold; margin-left: 8px;">
                {status}
            </span>
        </div>
        <div style="color: #666; font-size: 0.9em; margin-top: 5px;">
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_issues_list(issues: list[str], title: str = "Key Issues") -> None:
    """Render a list of issues with warning styling."""
    if not issues:
        st.info("No issues found! 🎉")
        return

    st.markdown(f"### ⚠️ {title}")

    for issue in issues:
        st.warning(issue)


def render_quick_wins(wins: list[str], title: str = "Quick Wins") -> None:
    """Render a list of quick wins with success styling."""
    if not wins:
        return

    st.markdown(f"### 💡 {title}")

    for win in wins:
        st.success(win)


def render_suggestions_table(suggestions: list[dict[str, Any]]) -> None:
    """Render suggestions in a structured format."""
    if not suggestions:
        st.info("No suggestions available.")
        return

    st.markdown("### 📋 Improvement Suggestions")

    for i, sug in enumerate(suggestions, 1):
        impact = sug.get("impact", "MEDIUM").upper()
        impact_badge = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(impact, "⚪")

        category = sug.get("category", "General")
        description = sug.get("description", "No description")
        savings = sug.get("savings_percent", 0)

        with st.expander(f"{impact_badge} [{impact}] {category}", expanded=i <= 3):
            st.write(description)
            if savings > 0:
                st.markdown(f"**Potential Savings:** {savings:.1f}%")


def render_cost_comparison(
    current_cost: float,
    optimal_cost: float,
    savings_percent: float,
    currency: str = "₹",
) -> None:
    """Render cost comparison with visual indicators."""
    st.markdown("### 💰 Cost Analysis")

    cols = st.columns(3)

    with cols[0]:
        st.metric(
            "Current Cost",
            f"{currency}{current_cost:,.0f}/m",
            help="Cost per meter of beam",
        )

    with cols[1]:
        st.metric(
            "Optimal Cost",
            f"{currency}{optimal_cost:,.0f}/m",
            help="Cost with optimizations",
        )

    with cols[2]:
        savings_amount = current_cost - optimal_cost
        st.metric(
            "Potential Savings",
            f"{savings_percent:.1f}%",
            delta=f"-{currency}{savings_amount:,.0f}",
            delta_color="normal",
            help="Savings achievable with recommendations",
        )


def render_constructability_details(
    score: float,
    level: str,
    bar_complexity: str,
    congestion_risk: str,
    issues: list[str] | None = None,
) -> None:
    """Render constructability analysis details."""
    st.markdown("### 🏗️ Constructability")

    # Main score
    percentage = int(score * 100)
    color = (
        "#28a745"
        if percentage >= 80
        else ("#ffc107" if percentage >= 60 else "#dc3545")
    )

    st.markdown(
        f"""
        <div style="padding: 15px; background-color: {color}10;
                    border-left: 4px solid {color}; border-radius: 4px;">
            <span style="font-size: 1.5em; font-weight: bold; color: {color};">
                {percentage}%
            </span>
            <span style="margin-left: 10px; color: #666;">
                ({level.title()})
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Details
    st.write("")
    cols = st.columns(2)

    with cols[0]:
        st.markdown(f"**Bar Complexity:** {bar_complexity}")

    with cols[1]:
        st.markdown(f"**Congestion Risk:** {congestion_risk}")

    # Issues
    if issues:
        st.markdown("**Construction Challenges:**")
        for issue in issues:
            st.markdown(f"- ⚠️ {issue}")


def render_smart_dashboard_full(dashboard: Any) -> None:
    """
    Render the complete SmartDesigner dashboard.

    Args:
        dashboard: DashboardReport from SmartDesigner.analyze()
    """
    if not dashboard:
        st.info("Run smart analysis to see the dashboard.")
        return

    # Get summary
    s = dashboard.summary

    # Overall Score
    st.markdown("## 🎯 SmartDesigner Analysis")

    render_score_gauge(s.overall_score, "Overall Design Score")

    st.divider()

    # Score Breakdown
    render_score_breakdown(
        safety=s.safety_score,
        cost=s.cost_efficiency,
        constructability=s.constructability,
        robustness=s.robustness,
    )

    st.divider()

    # Status
    render_status_badge(s.design_status)

    st.divider()

    # Key Issues and Quick Wins side by side
    col1, col2 = st.columns(2)

    with col1:
        render_issues_list(s.key_issues)

    with col2:
        render_quick_wins(s.quick_wins)

    st.divider()

    # Cost Analysis
    if dashboard.cost:
        render_cost_comparison(
            current_cost=dashboard.cost.current_cost,
            optimal_cost=dashboard.cost.optimal_cost,
            savings_percent=dashboard.cost.savings_percent,
        )

        st.divider()

    # Suggestions
    if dashboard.suggestions and dashboard.suggestions.suggestions:
        render_suggestions_table(dashboard.suggestions.suggestions[:5])

        st.divider()

    # Constructability
    if dashboard.constructability:
        cons = dashboard.constructability
        render_constructability_details(
            score=cons.score,
            level=cons.level,
            bar_complexity=cons.bar_complexity,
            congestion_risk=cons.congestion_risk,
            issues=cons.issues,
        )


def render_smart_dashboard_compact(dashboard: Any) -> None:
    """
    Render a compact version of the SmartDesigner dashboard.

    Suitable for sidebar or smaller spaces.

    Args:
        dashboard: DashboardReport from SmartDesigner.analyze()
    """
    if not dashboard:
        st.info("No analysis available.")
        return

    s = dashboard.summary

    # Compact score display
    percentage = int(s.overall_score * 100)
    color = (
        "#28a745"
        if percentage >= 80
        else ("#ffc107" if percentage >= 60 else "#dc3545")
    )
    emoji = "🟢" if percentage >= 80 else ("🟡" if percentage >= 60 else "🔴")

    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px;
                    background-color: rgba(0,0,0,0.05); border-radius: 8px;">
            <div style="font-size: 2em; font-weight: bold; color: {color};">
                {emoji} {percentage}%
            </div>
            <div style="font-size: 0.8em; color: #666;">Design Score</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Compact metrics
    st.write("")
    st.markdown(f"**Status:** {s.design_status}")

    if s.key_issues:
        st.markdown(f"**Issues:** {len(s.key_issues)}")

    if dashboard.cost:
        st.markdown(f"**Savings:** {dashboard.cost.savings_percent:.1f}%")
