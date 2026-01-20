"""
AI Context Generation

This module generates dynamic context about the current workspace state
for injection into AI prompts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st


def load_system_prompt() -> str:
    """Load the static system prompt from file."""
    prompt_path = Path(__file__).parent / "prompts" / "system.md"
    if prompt_path.exists():
        return prompt_path.read_text()
    return _fallback_system_prompt()


def _fallback_system_prompt() -> str:
    """Fallback system prompt if file not found."""
    return """You are StructEng AI, an expert structural engineering assistant
specializing in RC beam design per IS 456:2000. Help engineers design,
analyze, and optimize reinforced concrete beams with professional calculations.

Always cite IS 456 clauses, include units, and explain your reasoning."""


def generate_workspace_context() -> str:
    """Generate current workspace context for AI prompts."""
    ctx_parts = ["<workspace>"]

    # Beams loaded
    beams_df = st.session_state.get("ws_beams_df")
    if beams_df is not None and len(beams_df) > 0:
        ctx_parts.append(f"  <beams_loaded>{len(beams_df)}</beams_loaded>")
        beam_ids = beams_df["beam_id"].tolist() if "beam_id" in beams_df.columns else []
        if len(beam_ids) <= 10:
            ctx_parts.append(f"  <beam_ids>{beam_ids}</beam_ids>")
        else:
            ctx_parts.append(f"  <beam_ids>{beam_ids[:10]} (and {len(beam_ids) - 10} more)</beam_ids>")
    else:
        ctx_parts.append("  <beams_loaded>0</beams_loaded>")

    # Current state
    state = st.session_state.get("ws_state", "WELCOME")
    if hasattr(state, "value"):
        state = state.value
    ctx_parts.append(f"  <state>{state}</state>")

    # Selected beam
    selected = st.session_state.get("ws_selected_beam")
    if selected:
        ctx_parts.append(f"  <selected_beam>{selected}</selected_beam>")
        _add_selected_beam_details(ctx_parts, selected)

    # Design summary
    results_df = st.session_state.get("ws_design_results")
    if results_df is not None and len(results_df) > 0:
        _add_design_summary(ctx_parts, results_df)

    ctx_parts.append("</workspace>")
    return "\n".join(ctx_parts)


def _add_selected_beam_details(ctx_parts: list[str], beam_id: str) -> None:
    """Add details for the selected beam."""
    results_df = st.session_state.get("ws_design_results")
    if results_df is None or results_df.empty:
        return

    beam_row = results_df[results_df.get("beam_id", results_df.index) == beam_id]
    if beam_row.empty:
        return

    row = beam_row.iloc[0]
    ctx_parts.append("  <selected_beam_details>")

    # Safety status
    is_safe = row.get("is_safe", False)
    ctx_parts.append(f"    <is_safe>{is_safe}</is_safe>")

    # Flexure results
    ast_required = row.get("ast_required", 0)
    if ast_required:
        ctx_parts.append(f"    <ast_required>{ast_required:.0f}</ast_required>")

    ast_provided = row.get("ast_provided", 0)
    if ast_provided:
        ctx_parts.append(f"    <ast_provided>{ast_provided:.0f}</ast_provided>")

    # Moment capacity
    mu_knm = row.get("mu_knm", 0)
    mu_capacity = row.get("mu_capacity_knm", row.get("mu_capacity", 0))
    if mu_knm and mu_capacity:
        utilization = (mu_knm / mu_capacity * 100) if mu_capacity > 0 else 0
        ctx_parts.append(f"    <moment_utilization>{utilization:.1f}%</moment_utilization>")

    # Shear results
    sv_required = row.get("sv_required", 0)
    if sv_required:
        ctx_parts.append(f"    <sv_required>{sv_required:.0f}</sv_required>")

    ctx_parts.append("  </selected_beam_details>")


def _add_design_summary(ctx_parts: list[str], results_df) -> None:
    """Add overall design summary."""
    ctx_parts.append("  <design_summary>")
    ctx_parts.append(f"    <total>{len(results_df)}</total>")

    # Count pass/fail
    if "is_safe" in results_df.columns:
        passed = results_df["is_safe"].sum()
        failed = len(results_df) - passed
        ctx_parts.append(f"    <passed>{passed}</passed>")
        ctx_parts.append(f"    <failed>{failed}</failed>")

        # List failed beams if any
        if failed > 0:
            failed_beams = results_df[~results_df["is_safe"]]
            if "beam_id" in failed_beams.columns:
                failed_ids = failed_beams["beam_id"].tolist()[:5]
                ctx_parts.append(f"    <failed_beams>{failed_ids}</failed_beams>")

    ctx_parts.append("  </design_summary>")


def build_messages(
    user_message: str,
    history: list[dict] | None = None,
    include_workspace: bool = True
) -> list[dict]:
    """
    Build the complete message list for API call.

    Args:
        user_message: The current user message
        history: Previous conversation messages
        include_workspace: Whether to include workspace context

    Returns:
        List of messages for the API call
    """
    messages = []

    # System prompt with static content
    system_content = load_system_prompt()

    # Add dynamic workspace context
    if include_workspace:
        workspace_context = generate_workspace_context()
        system_content += f"\n\n## Current Workspace State\n\n{workspace_context}"

    messages.append({
        "role": "system",
        "content": system_content
    })

    # Add conversation history
    if history:
        for msg in history:
            if msg.get("role") in ("user", "assistant"):
                messages.append({
                    "role": msg["role"],
                    "content": msg.get("content", "")
                })

    # Add current user message
    messages.append({
        "role": "user",
        "content": user_message
    })

    return messages
