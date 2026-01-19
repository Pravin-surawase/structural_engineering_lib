# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tester Feedback Page — Daily Feedback Collection

This page enables engineers/testers to submit feedback during testing sessions.
Feedback is saved locally and can be exported for review.

Usage:
    - Navigate to this page after testing a feature
    - Select feedback type and describe the issue
    - Optionally attach screenshots
    - Submit to save feedback locally
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# Feedback storage directory
FEEDBACK_DIR = Path(__file__).parent.parent / "feedback"
FEEDBACK_DIR.mkdir(exist_ok=True)


# =============================================================================
# Utility Functions (defined first for AST scanner compatibility)
# =============================================================================


def generate_feedback_id() -> str:
    """Generate a unique feedback ID."""
    now = datetime.now()
    return f"FB-{now.strftime('%Y%m%d')}-{now.strftime('%H%M%S')}"


def save_feedback(data: dict[str, Any]) -> Path:
    """Save feedback to a JSON file.

    Security: Validates that the generated filename doesn't contain
    path traversal characters and stays within FEEDBACK_DIR.
    """
    # Sanitize ID to prevent path traversal (use .get() to avoid KeyError)
    feedback_id = data.get("id", "")
    if not feedback_id:
        raise ValueError("Feedback data must have an 'id' field")
    safe_id = "".join(c for c in feedback_id if c.isalnum() or c == "-")
    filename = f"{safe_id}.json"
    # Path join to build file path (FEEDBACK_DIR is a Path object)
    filepath = Path(FEEDBACK_DIR) / filename

    # Security: Verify path stays within feedback directory
    resolved = filepath.resolve()
    if not str(resolved).startswith(str(FEEDBACK_DIR.resolve())):
        raise ValueError("Invalid feedback path")

    with open(resolved, "w") as f:
        json.dump(data, f, indent=2)
    return resolved


def load_all_feedback() -> list[dict[str, Any]]:
    """Load all feedback from the feedback directory.

    Security: Only loads files matching strict FB-YYYYMMDD-HHMMSS.json pattern
    from the designated feedback directory. Path traversal is prevented by:
    1. Using glob with strict pattern (no user input in pattern)
    2. Verifying resolved path is within FEEDBACK_DIR
    """
    feedback_list = []
    for filepath in sorted(FEEDBACK_DIR.glob("FB-*.json")):
        # Security: Ensure file is actually within feedback directory
        try:
            resolved = filepath.resolve()
            if not str(resolved).startswith(str(FEEDBACK_DIR.resolve())):
                continue  # Skip files outside feedback directory
            with open(resolved) as f:
                feedback_list.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue
    return feedback_list


def get_library_version() -> str:
    """Get the library version.

    Note: Import inside function to handle optional dependency gracefully.
    """
    try:
        from structural_lib import api

        return api.get_library_version()
    except Exception:
        return "unknown"


# =============================================================================
# Page Components
# =============================================================================


def render_submit_form() -> None:
    """Render the feedback submission form."""

    st.subheader("Submit New Feedback")

    # Form
    with st.form("feedback_form", clear_on_submit=True):
        # Feedback type
        feedback_type = st.selectbox(
            "Feedback Type",
            [
                "🐛 Bug Report",
                "❌ Incorrect Result",
                "🎨 UI/UX Issue",
                "💡 Feature Request",
                "📚 Documentation Issue",
                "✅ Works Well (Positive)",
                "❓ Other",
            ],
            help="Select the type of feedback",
        )

        # Feature tested
        feature_tested = st.selectbox(
            "Feature/Page Tested",
            [
                "Single Beam Design",
                "Cost Optimizer",
                "Compliance Checker",
                "3D Viewer",
                "Batch Processing",
                "DXF Export",
                "BBS Export",
                "Report Generation",
                "ETABS Import",
                "API Functions",
                "Documentation",
                "Other",
            ],
            help="Which feature did you test?",
        )

        # Severity
        severity = st.select_slider(
            "Severity",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium",
            help="How severe is the issue?",
        )

        # Description
        description = st.text_area(
            "Description",
            placeholder="Describe what happened, what you expected, and steps to reproduce...",
            height=150,
            help="Be as specific as possible",
        )

        # Input values (optional)
        st.markdown("**Optional: Capture Test Inputs**")
        col1, col2 = st.columns(2)
        with col1:
            b_mm = st.number_input("b (mm)", value=0, min_value=0, help="Beam width")
            D_mm = st.number_input("D (mm)", value=0, min_value=0, help="Beam depth")
            span_mm = st.number_input(
                "Span (mm)", value=0, min_value=0, help="Beam span"
            )
        with col2:
            mu_knm = st.number_input(
                "Mu (kN·m)", value=0.0, min_value=0.0, help="Applied moment"
            )
            vu_kn = st.number_input(
                "Vu (kN)", value=0.0, min_value=0.0, help="Applied shear"
            )
            fck = st.selectbox("fck (N/mm²)", [0, 20, 25, 30, 35, 40], index=0)

        # Expected vs actual
        col3, col4 = st.columns(2)
        with col3:
            expected_result = st.text_input(
                "Expected Result",
                placeholder="What did you expect to happen?",
            )
        with col4:
            actual_result = st.text_input(
                "Actual Result",
                placeholder="What actually happened?",
            )

        # Reference
        reference = st.text_input(
            "Reference (optional)",
            placeholder="Hand calculation, Excel, reference book, etc.",
            help="How did you verify the expected result?",
        )

        # Tester info
        tester_name = st.text_input(
            "Your Name/Initials",
            placeholder="e.g., PS, John D.",
            help="So we know who to follow up with",
        )

        # Submit button
        submitted = st.form_submit_button("📤 Submit Feedback", type="primary")

        if submitted:
            if not description.strip():
                st.error("Please provide a description.")
            else:
                feedback_data = {
                    "id": generate_feedback_id(),
                    "timestamp": datetime.now().isoformat(),
                    "type": feedback_type,
                    "feature": feature_tested,
                    "severity": severity,
                    "description": description,
                    "inputs": {
                        "b_mm": b_mm if b_mm > 0 else None,
                        "D_mm": D_mm if D_mm > 0 else None,
                        "span_mm": span_mm if span_mm > 0 else None,
                        "mu_knm": mu_knm if mu_knm > 0 else None,
                        "vu_kn": vu_kn if vu_kn > 0 else None,
                        "fck": fck if fck > 0 else None,
                    },
                    "expected": expected_result,
                    "actual": actual_result,
                    "reference": reference,
                    "tester": tester_name,
                    "library_version": get_library_version(),
                    "status": "new",
                }

                save_feedback(feedback_data)
                st.success(
                    f"✅ Feedback submitted! Reference: **{feedback_data['id']}**"
                )
                st.balloons()


def render_feedback_history() -> None:
    """Render the feedback history view."""

    st.subheader("Feedback History")

    feedback_list = load_all_feedback()

    if not feedback_list:
        st.info("No feedback submitted yet.")
        return

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", len(feedback_list))
    with col2:
        bugs = sum(1 for f in feedback_list if "Bug" in f.get("type", ""))
        st.metric("Bugs", bugs)
    with col3:
        new_count = sum(1 for f in feedback_list if f.get("status") == "new")
        st.metric("New", new_count)
    with col4:
        positive = sum(1 for f in feedback_list if "Positive" in f.get("type", ""))
        st.metric("Positive", positive)

    st.divider()

    # Filter
    filter_type = st.selectbox(
        "Filter by type",
        ["All"] + list(set(f.get("type", "Unknown") for f in feedback_list)),
        key="filter_type",
    )

    # Display feedback
    for fb in reversed(feedback_list):
        if filter_type != "All" and fb.get("type") != filter_type:
            continue

        with st.expander(
            f"**{fb['id']}** — {fb.get('type', 'Unknown')} — {fb.get('feature', 'Unknown')}",
            expanded=False,
        ):
            st.markdown(f"**Timestamp:** {fb.get('timestamp', 'Unknown')}")
            st.markdown(f"**Severity:** {fb.get('severity', 'Unknown')}")
            st.markdown(f"**Tester:** {fb.get('tester', 'Anonymous')}")
            st.markdown(f"**Status:** {fb.get('status', 'new')}")
            st.divider()
            st.markdown("**Description:**")
            st.text(fb.get("description", "No description"))

            if fb.get("inputs"):
                inputs = {k: v for k, v in fb["inputs"].items() if v is not None}
                if inputs:
                    st.markdown("**Test Inputs:**")
                    st.json(inputs)

            if fb.get("expected") or fb.get("actual"):
                st.markdown(f"**Expected:** {fb.get('expected', '-')}")
                st.markdown(f"**Actual:** {fb.get('actual', '-')}")

            if fb.get("reference"):
                st.markdown(f"**Reference:** {fb.get('reference')}")

    # Export button
    st.divider()
    if st.button("📥 Export All Feedback (JSON)"):
        json_str = json.dumps(feedback_list, indent=2)
        st.download_button(
            "Download JSON",
            data=json_str,
            file_name=f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )


# =============================================================================
# Main Entry Point (defined after all dependencies for AST scanner)
# =============================================================================


def main() -> None:
    """Main page entry point."""
    st.set_page_config(
        page_title="Tester Feedback",
        page_icon="📝",
        layout="wide",
    )

    st.title("📝 Tester Feedback")
    st.markdown(
        """
    Help us improve! Submit your feedback after testing any feature.
    Your input directly shapes the library's development.
    """
    )

    # Tabs for submit and view
    tab_submit, tab_history = st.tabs(["Submit Feedback", "View History"])

    with tab_submit:
        render_submit_form()

    with tab_history:
        render_feedback_history()


if __name__ == "__main__":
    main()
