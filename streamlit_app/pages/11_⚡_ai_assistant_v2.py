# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Assistant v2 — Professional Redesign with Dynamic Workspace

Layout: Full page with 35% chat (left) + 65% dynamic workspace (right)

Key Improvements over v1:
- Uses 97% of screen (no wasted header space)
- Single dynamic workspace (not 5 tabs)
- Auto-mapping for CSV import (no manual column selection)
- Built-in sample data for quick start
- Beam-by-beam editing with live 3D preview
- State machine for workflow transitions

States: WELCOME → IMPORT → DESIGN → VIEW_3D → EDIT → DASHBOARD

Author: Session 52 Agent
"""

from __future__ import annotations

import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="StructEng AI v2",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Imports after page config
import re
import sys
import time
from pathlib import Path
from typing import Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.ai_workspace import (
    WorkspaceState,
    init_workspace_state,
    render_dynamic_workspace,
    set_workspace_state,
    load_sample_data,
    design_all_beams_ws,
)

# Check for OpenAI availability
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import structural_lib
try:
    from structural_lib import api as structural_api
    from structural_lib.insights import SmartDesigner

    STRUCTURAL_LIB_AVAILABLE = True
except ImportError:
    STRUCTURAL_LIB_AVAILABLE = False


def get_openai_client() -> OpenAI | None:
    """Get OpenAI client if API key is available."""
    if not OPENAI_AVAILABLE:
        return None

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def get_openai_config() -> dict[str, Any]:
    """Get OpenAI configuration from secrets."""
    config = {
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    if "openai" in st.secrets:
        openai_config = st.secrets.get("openai", {})
        if "model" in openai_config:
            config["model"] = openai_config.get("model", config["model"])
        if "temperature" in openai_config:
            try:
                config["temperature"] = float(openai_config.get("temperature", config["temperature"]))
            except (ValueError, TypeError):
                pass
        if "max_tokens" in openai_config:
            try:
                config["max_tokens"] = int(openai_config.get("max_tokens", config["max_tokens"]))
            except (ValueError, TypeError):
                pass

    return config


# System prompt for structural engineering assistant
SYSTEM_PROMPT = """You are StructEng AI, an expert structural engineering assistant specializing in
IS 456 reinforced concrete design. You help engineers design beams, optimize costs,
and understand code requirements.

## Your Capabilities:
- Design RC beams for moment and shear (IS 456:2000)
- Optimize designs for cost, safety, or constructability
- Explain code clauses in simple terms
- Provide practical engineering advice
- Import data from ETABS, SAFE, and other formats
- Show 3D visualizations with actual reinforcement

## Guidelines:
1. Be practical: Engineers want actionable advice, not theory.
2. Be specific: Always include numbers (dimensions, costs, percentages).
3. Show your work: Explain the reasoning behind recommendations.
4. Follow IS 456: All designs must comply with IS 456:2000.

## Available Commands:
- "load sample" - Load sample ETABS data
- "design all" - Design all imported beams
- "show 3d" - Show 3D view for selected beam
- "dashboard" - Show smart insights dashboard

## Response Format:
- Start with a brief answer
- Present results clearly with key metrics
- Offer follow-up options
"""


def init_chat_state():
    """Initialize chat session state."""
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []


def get_ai_response(user_message: str) -> str:
    """Get AI response for user message."""
    msg_lower = user_message.lower()

    # Check for workspace commands first
    if "load sample" in msg_lower or "sample data" in msg_lower:
        load_sample_data()
        return "✅ Loaded sample data with 10 beams (3 stories). Click **Design All** in the workspace or say **'design all'**."

    if "design all" in msg_lower or "design beams" in msg_lower:
        if st.session_state.get("ws_beams_df") is not None:
            st.session_state.ws_design_results = design_all_beams_ws()
            set_workspace_state(WorkspaceState.DESIGN)
            df = st.session_state.ws_design_results
            passed = len(df[df["is_safe"] == True])
            return f"✅ Designed **{len(df)} beams** — **{passed}** passed, **{len(df)-passed}** need review.\n\nSay **'building 3d'** to see the full structure or select a beam for details."
        else:
            return "📂 No beam data loaded. Say **'load sample'** or upload a CSV first."

    if "building 3d" in msg_lower or "building view" in msg_lower or "full 3d" in msg_lower:
        set_workspace_state(WorkspaceState.BUILDING_3D)
        return "🏗️ Showing full building 3D visualization. Click any beam to see details."

    if "edit rebar" in msg_lower or "rebar editor" in msg_lower:
        selected_beam = st.session_state.get("ws_selected_beam")
        if selected_beam:
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            return f"🔧 Opening rebar editor for **{selected_beam}**. Adjust bars and stirrups to see real-time checks."
        else:
            return "Select a beam first from design results."

    if "show 3d" in msg_lower or "3d view" in msg_lower or "beam 3d" in msg_lower:
        selected_beam = st.session_state.get("ws_selected_beam")
        if selected_beam:
            set_workspace_state(WorkspaceState.VIEW_3D)
            return f"🎨 Showing 3D view for **{selected_beam}** with actual reinforcement."
        else:
            return "Select a beam first from the design results."

    if "cross section" in msg_lower or "section view" in msg_lower or "2d section" in msg_lower:
        selected_beam = st.session_state.get("ws_selected_beam")
        if selected_beam:
            set_workspace_state(WorkspaceState.CROSS_SECTION)
            return f"📐 Showing professional cross-section for **{selected_beam}** with bar layout and dimensions."
        else:
            return "Select a beam first from design results."

    if "dashboard" in msg_lower or "insights" in msg_lower:
        set_workspace_state(WorkspaceState.DASHBOARD)
        return "📊 Showing smart insights dashboard."

    # Beam selection commands
    beam_match = re.search(r'select\s+(beam\s+)?([a-zA-Z0-9_-]+)', msg_lower)
    if beam_match:
        beam_id = beam_match.group(2).upper()
        df = st.session_state.get("ws_design_results")
        if df is not None and beam_id in df["beam_id"].str.upper().values:
            # Find exact match
            match_row = df[df["beam_id"].str.upper() == beam_id]
            if not match_row.empty:
                actual_id = match_row.iloc[0]["beam_id"]
                st.session_state.ws_selected_beam = actual_id
                set_workspace_state(WorkspaceState.VIEW_3D)
                return f"Selected **{actual_id}** — showing 3D view with reinforcement details."
        return f"Beam '{beam_id}' not found. Available: {', '.join(df['beam_id'].tolist()[:5])}..."

    # OpenAI API if available
    client = get_openai_client()
    if client:
        try:
            config = get_openai_config()
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add conversation history (last 10 messages)
            for msg in st.session_state.ai_messages[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=config["model"],
                messages=messages,
                temperature=config["temperature"],
                max_tokens=config["max_tokens"],
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"OpenAI error: {str(e)[:100]}. Using local mode."

    # Local SmartDesigner fallback
    return _local_response(user_message)


def _local_response(msg: str) -> str:
    """Generate local response without OpenAI."""
    msg_lower = msg.lower()

    if "hello" in msg_lower or "hi" in msg_lower:
        return """👋 Hello! I'm StructEng AI, your structural engineering assistant.

**Quick Start:**
- Say **"load sample"** to try with sample data
- Or **upload a CSV** in the workspace

**I can help with:**
- IS 456 beam design & optimization
- Building 3D visualization
- Interactive rebar editor with live checks
- Batch design from ETABS/SAFE exports"""

    if "help" in msg_lower or "command" in msg_lower:
        return """**Available Commands:**

📂 **Data**
- **load sample** — Load 10 sample beams (3 stories)
- **design all** — Run IS 456 design on all beams

🎨 **Visualization**
- **building 3d** — Full building 3D view
- **show 3d** — Selected beam 3D view
- **select B1** — Select beam by ID

🔧 **Design**
- **edit rebar** — Interactive reinforcement editor
- **dashboard** — Insights & analytics

**Workflow:**
1. Import → Design All → Building 3D
2. Select Beam → 3D View → Edit Rebar"""

    if any(w in msg_lower for w in ["design", "beam", "moment", "shear"]):
        return """To design beams:
1. Say **"load sample"** or upload CSV
2. Say **"design all"** to run IS 456 design
3. Say **"building 3d"** to see full structure
4. Click any beam → **"edit rebar"** to customize"""

    return """I can help you with structural beam design. Try:

🚀 **"load sample"** — Quick start with demo data
📐 **"design all"** — Run batch design
🏗️ **"building 3d"** — See full structure
❓ **"help"** — All commands

For full AI capabilities, add your OpenAI API key to secrets.toml."""


def _handle_quick_action(prompt: str) -> None:
    """Handle quick action button click."""
    st.session_state.ai_messages.append({"role": "user", "content": prompt})
    response = get_ai_response(prompt)
    st.session_state.ai_messages.append({"role": "assistant", "content": response})
    st.rerun()


def render_chat_panel():
    """Render the chat panel (left side)."""
    # Chat container with maximum height
    chat_container = st.container(height=500)

    with chat_container:
        # Welcome message if no messages
        if not st.session_state.ai_messages:
            st.markdown("""
            👋 **Welcome to StructEng AI v2!**

            Quick start:
            - Say **"load sample"** to try sample data
            - Or upload a CSV in the workspace →

            Type a message below to begin.
            """)

        # Display messages
        for message in st.session_state.ai_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input (always visible)
    prompt = st.chat_input("Ask about beam design, or say 'help'...")

    if prompt:
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt)
        st.session_state.ai_messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Quick actions row (compact)
    cols = st.columns(4)
    with cols[0]:
        if st.button("📂 Sample", use_container_width=True, help="Load sample data"):
            _handle_quick_action("load sample")
    with cols[1]:
        if st.button("🚀 Design", use_container_width=True, help="Design all beams"):
            _handle_quick_action("design all beams")
    with cols[2]:
        if st.button("📊 Insights", use_container_width=True, help="Show dashboard"):
            _handle_quick_action("show dashboard")
    with cols[3]:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear chat"):
            st.session_state.ai_messages = []
            st.rerun()


def main():
    """Main function."""
    init_chat_state()
    init_workspace_state()

    # Minimal header (uses only ~3% of screen)
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("## ⚡ StructEng AI")
    with col2:
        # Compact status indicator
        client = get_openai_client()
        if client:
            config = get_openai_config()
            st.caption(f"✅ {config['model']}")
        else:
            st.caption("💡 Local mode")

    # Main layout: 35% chat, 65% workspace (maximized)
    chat_col, workspace_col = st.columns([0.35, 0.65])

    with chat_col:
        render_chat_panel()

    with workspace_col:
        render_dynamic_workspace()


if __name__ == "__main__":
    main()
