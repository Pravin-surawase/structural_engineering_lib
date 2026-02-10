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
- **Function calling** for AI to execute workspace actions
- **Action-oriented AI** that just does things (no clarifying questions)

States: WELCOME → IMPORT → DESIGN → VIEW_3D → EDIT → DASHBOARD

Author: Session 52-58 Agents
"""

from __future__ import annotations

import json
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
from pathlib import Path
from typing import Any

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.ai_workspace import (
    WorkspaceState,
    init_workspace_state,
    render_dynamic_workspace,
    render_unified_editor,
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

# Import AI module for context and tools
try:
    from ai.context import (
        load_system_prompt,
        generate_workspace_context,
        build_messages,
    )
    from ai.tools import get_tools
    from ai.handlers import handle_tool_call

    AI_MODULE_AVAILABLE = True
except ImportError:
    AI_MODULE_AVAILABLE = False

# Import structural_lib
try:
    from structural_lib import api as structural_api
    from structural_lib.insights import SmartDesigner

    STRUCTURAL_LIB_AVAILABLE = True
except ImportError:
    STRUCTURAL_LIB_AVAILABLE = False


def get_openai_client() -> OpenAI | None:
    """Get OpenAI client if API key is available.

    Supports both OpenAI and OpenRouter API keys:
    - OpenAI: sk-...
    - OpenRouter: sk-or-v1-...
    """
    if not OPENAI_AVAILABLE:
        return None

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        return None

    # OpenRouter uses different base URL
    if api_key.startswith("sk-or-"):
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    return OpenAI(api_key=api_key)


def get_openai_config() -> dict[str, Any]:
    """Get OpenAI configuration from secrets."""
    # Default model - gpt-4o-mini is fast, cost-efficient
    model = "gpt-4o-mini"
    temperature = 0.7
    max_tokens = 2000

    if "openai" in st.secrets:
        # st.secrets returns AttrDict, access directly with get() or bracket
        openai_config = st.secrets["openai"]
        if hasattr(openai_config, "get") or isinstance(openai_config, dict):
            # Try to read model - supports both dict and AttrDict
            try:
                model = openai_config.get("model", model)
            except (AttributeError, TypeError):
                if hasattr(openai_config, "model"):
                    model = openai_config.model
            try:
                temperature = float(openai_config.get("temperature", temperature))
            except (ValueError, TypeError, AttributeError):
                if hasattr(openai_config, "temperature"):
                    temperature = float(openai_config.temperature)
            try:
                max_tokens = int(openai_config.get("max_tokens", max_tokens))
            except (ValueError, TypeError, AttributeError):
                if hasattr(openai_config, "max_tokens"):
                    max_tokens = int(openai_config.max_tokens)

    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def init_chat_state():
    """Initialize chat session state."""
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []


def get_ai_response(user_message: str) -> str:
    """Get AI response for user message.

    Uses function calling when AI module is available, falls back to
    hardcoded commands and local responses otherwise.
    """
    msg_lower = user_message.lower()

    # Check for workspace commands first (fast path)
    if "load sample" in msg_lower or "sample data" in msg_lower:
        load_sample_data()
        return "✅ **Loaded sample data** — 10 beams across 3 stories.\n\nSay **'design all'** to run IS 456 design."

    if "design all" in msg_lower or "design beams" in msg_lower:
        if st.session_state.get("ws_beams_df") is not None:
            st.session_state.ws_design_results = design_all_beams_ws()
            set_workspace_state(WorkspaceState.DESIGN)
            df = st.session_state.ws_design_results
            passed = len(df[df["is_safe"]])
            failed = len(df) - passed
            avg_util = df["utilization"].mean() * 100
            return f"✅ **Designed {len(df)} beams** — {passed} passed, {failed} failed, avg util {avg_util:.0f}%\n\nSay **'building 3d'** to see the structure or click a beam for details."
        else:
            return (
                "📂 No beam data loaded. Say **'load sample'** or upload a CSV first."
            )

    if (
        "building 3d" in msg_lower
        or "building view" in msg_lower
        or "full 3d" in msg_lower
    ):
        set_workspace_state(WorkspaceState.BUILDING_3D)
        return "🏗️ **Showing full building 3D view.** Click any beam to see details."

    if "edit rebar" in msg_lower or "rebar editor" in msg_lower:
        selected_beam = st.session_state.get("ws_selected_beam")
        if selected_beam:
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            return f"🔧 **Opening rebar editor for {selected_beam}.** Adjust bars and stirrups."
        else:
            return "Select a beam first from design results."

    if "show 3d" in msg_lower or "3d view" in msg_lower or "beam 3d" in msg_lower:
        selected_beam = st.session_state.get("ws_selected_beam")
        if selected_beam:
            set_workspace_state(WorkspaceState.VIEW_3D)
            return f"🎨 **Showing 3D view for {selected_beam}** with reinforcement."
        else:
            return "Select a beam first from the design results."

    if (
        "cross section" in msg_lower
        or "section view" in msg_lower
        or "2d section" in msg_lower
    ):
        selected_beam = st.session_state.get("ws_selected_beam")
        if selected_beam:
            set_workspace_state(WorkspaceState.CROSS_SECTION)
            return f"📐 **Showing cross-section for {selected_beam}** with bar layout."
        else:
            return "Select a beam first from design results."

    if "dashboard" in msg_lower or "insights" in msg_lower:
        set_workspace_state(WorkspaceState.DASHBOARD)
        return "📊 **Showing smart insights dashboard.**"

    # Beam selection commands
    beam_match = re.search(r"select\s+(beam\s+)?([a-zA-Z0-9_-]+)", msg_lower)
    if beam_match:
        beam_id = beam_match.group(2).upper()
        df = st.session_state.get("ws_design_results")
        if df is not None and beam_id in df["beam_id"].str.upper().values:
            match_row = df[df["beam_id"].str.upper() == beam_id]
            if not match_row.empty:
                actual_id = match_row.iloc[0]["beam_id"]
                st.session_state.ws_selected_beam = actual_id
                set_workspace_state(WorkspaceState.VIEW_3D)
                return (
                    f"✅ **Selected {actual_id}** — showing 3D view with reinforcement."
                )
        return f"Beam '{beam_id}' not found. Available: {', '.join(df['beam_id'].tolist()[:5])}..."

    # Use AI with function calling if available
    client = get_openai_client()
    if client:
        try:
            return _get_ai_response_with_tools(client, user_message)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "quota" in error_str.lower():
                return "⚠️ Rate limit hit. Try again shortly.\n\n" + _local_response(
                    user_message
                )
            elif "401" in error_str or "auth" in error_str.lower():
                return "🔑 API key invalid. Using local mode.\n\n" + _local_response(
                    user_message
                )
            elif "timeout" in error_str.lower() or "connect" in error_str.lower():
                return "⏱️ Connection timeout. Using local mode.\n\n" + _local_response(
                    user_message
                )
            else:
                # Log error for debugging but still provide fallback
                import logging

                logging.warning(f"AI API error: {error_str}")
                return f"⚠️ AI error: {error_str[:100]}\n\n" + _local_response(
                    user_message
                )

    # Local SmartDesigner fallback
    return _local_response(user_message)


def _get_ai_response_with_tools(client: OpenAI, user_message: str) -> str:
    """Get AI response using function calling for workspace actions."""
    config = get_openai_config()

    # Build messages with context
    if AI_MODULE_AVAILABLE:
        system_prompt = load_system_prompt()
        workspace_context = generate_workspace_context()
        system_content = (
            f"{system_prompt}\n\n## Current Workspace State\n\n{workspace_context}"
        )
    else:
        system_content = SYSTEM_PROMPT

    messages = [{"role": "system", "content": system_content}]

    # Add conversation history (last 10 messages)
    for msg in st.session_state.ai_messages[-10:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    # Get tools if available
    tools = get_tools() if AI_MODULE_AVAILABLE else None

    # First API call
    response = client.chat.completions.create(
        model=config.get("model", "gpt-4o-mini"),
        messages=messages,
        tools=tools,
        tool_choice="auto" if tools else None,
        temperature=config.get("temperature", 0.7),
        max_tokens=config.get("max_tokens", 2000),
    )

    assistant_message = response.choices[0].message

    # Check if AI wants to use tools
    if assistant_message.tool_calls:
        # Execute tool calls
        tool_results = []
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                tool_args = {}

            # Execute the tool
            result = handle_tool_call(tool_name, tool_args)
            tool_results.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": result,
                }
            )

        # Add assistant message and tool results
        messages.append(assistant_message)
        messages.extend(tool_results)

        # Second API call to get final response
        final_response = client.chat.completions.create(
            model=config.get("model", "gpt-4o-mini"),
            messages=messages,
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 2000),
        )

        return final_response.choices[0].message.content

    # No tool calls, return direct response
    return assistant_message.content


# Fallback system prompt (used when AI module not available)
SYSTEM_PROMPT = """You are StructEng AI, an expert structural engineering assistant.

⚡ CRITICAL: ACTION-ORIENTED BEHAVIOR
- DO NOT ASK CLARIFYING QUESTIONS. JUST DO IT.
- Use sensible defaults when information is missing
- Show results first, then ask if they want changes

Available commands:
- "load sample" - Load sample ETABS data
- "design all" - Design all imported beams
- "building 3d" - Show full building 3D view
- "show 3d" - Show selected beam 3D view
- "dashboard" - Show smart insights
- "select B1" - Select beam by ID

When asked to filter floors, list critical beams, or optimize:
Execute immediately using defaults. Don't ask for confirmation."""


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


def _render_ai_export_downloads() -> None:
    """Render download buttons for AI-generated exports (DXF, reports)."""
    # DXF export download
    dxf_data = st.session_state.get("ai_export_dxf")
    if dxf_data:
        st.markdown("---")
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.caption(f"📐 DXF Ready: {dxf_data.get('beam_count', 1)} beam(s)")
        with col2:
            if st.download_button(
                label="📥 DXF",
                data=dxf_data.get("bytes", b""),
                file_name=dxf_data.get("filename", "beam_export.dxf"),
                mime="application/dxf",
                use_container_width=True,
                help="Download CAD drawing",
                key="ai_dxf_download",
            ):
                # Clear after download
                st.session_state.pop("ai_export_dxf", None)

    # Report download
    report_data = st.session_state.get("ai_report")
    if report_data:
        if not dxf_data:  # Only show divider if DXF wasn't shown
            st.markdown("---")
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.caption(f"📄 Report Ready: {report_data.get('beam_count', 1)} beam(s)")
        with col2:
            content = report_data.get("content", "")
            if isinstance(content, str):
                content = content.encode("utf-8")
            fmt = report_data.get("format", "html")
            mime = "text/html" if fmt == "html" else "application/json"

            if st.download_button(
                label="📄 Report",
                data=content,
                file_name=report_data.get("filename", f"beam_report.{fmt}"),
                mime=mime,
                use_container_width=True,
                help="Download design report",
                key="ai_report_download",
            ):
                # Clear after download
                st.session_state.pop("ai_report", None)


def render_chat_panel():
    """Render the chat panel (left side)."""
    # Chat container with maximum height
    chat_container = st.container(height=500)

    with chat_container:
        # Welcome message if no messages
        if not st.session_state.ai_messages:
            st.markdown("""
👋 **Welcome to StructEng AI v2!**

**Quick Start (try these commands):**
1. `load sample` — Load demo building data
2. `design all` — Run IS 456 design on all beams
3. `building 3d` — See interactive 3D visualization
4. `edit rebar` — Customize reinforcement

**Or upload your CSV** in the workspace →

💡 *Tip: Click the buttons below for quick actions*
            """)

        # Display messages
        for message in st.session_state.ai_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Render download buttons for AI-generated exports
        _render_ai_export_downloads()

    # Chat input (always visible)
    prompt = st.chat_input("Ask about beam design, or say 'help'...")

    if prompt:
        st.session_state.ai_messages.append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt)
        st.session_state.ai_messages.append({"role": "assistant", "content": response})
        st.rerun()

    # Quick actions row (compact)
    cols = st.columns(5)
    if len(cols) > 0:
        with cols[0]:
            if st.button("📂", use_container_width=True, help="Load sample data"):
                _handle_quick_action("load sample")
    if len(cols) > 1:
        with cols[1]:
            if st.button("🚀", use_container_width=True, help="Design all beams"):
                _handle_quick_action("design all beams")
    if len(cols) > 2:
        with cols[2]:
            if st.button("🏗️", use_container_width=True, help="Building 3D"):
                _handle_quick_action("building 3d")
    if len(cols) > 3:
        with cols[3]:
            if st.button("📊", use_container_width=True, help="Show insights"):
                _handle_quick_action("show dashboard")
    if len(cols) > 4:
        with cols[4]:
            if st.button("🗑️", use_container_width=True, help="Clear chat"):
                st.session_state.ai_messages = []
                st.rerun()


def main():
    """Main function."""
    init_chat_state()
    init_workspace_state()

    # Custom CSS for compact layout - reduce top padding
    st.markdown(
        """
    <style>
        /* Reduce top padding of main content */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }
        /* Compact header styling */
        .compact-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
            margin-bottom: 0.5rem;
        }
        /* Hide default Streamlit header spacing */
        header[data-testid="stHeader"] {
            height: 2.5rem;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Check if unified editor mode (full-width, no chat column)
    workspace_state = st.session_state.get("ws_state", WorkspaceState.WELCOME)

    if workspace_state == WorkspaceState.UNIFIED_EDITOR:
        # Full-width editor mode - no header, no chat, maximize space
        render_unified_editor()
    else:
        # Inline compact header - single row
        col1, col2, col3 = st.columns([0.45, 0.35, 0.2])
        with col1:
            st.markdown("**⚡ StructEng AI**")
        with col2:
            # Compact status
            client = get_openai_client()
            if client:
                config = get_openai_config()
                model_name = config.get("model", "gpt-4o-mini")
                # Shorten model name for display
                if "/" in model_name:
                    model_name = model_name.split("/")[-1]
                st.caption(f"✅ {model_name}")
            else:
                st.caption("💡 Local mode")
        with col3:
            # Quick access links
            st.caption(f"📍 {workspace_state.value.title()}")

        # Session 32: Make chat collapsible - maximize workspace by default
        # User can expand chat when needed with toggle
        show_chat = st.session_state.get("show_chat_panel", False)

        # Toggle in header
        chat_toggle_col, spacer_col = st.columns([0.15, 0.85])
        with chat_toggle_col:
            if st.button(
                "💬" if not show_chat else "✕ Hide Chat",
                key="toggle_chat",
                type="secondary" if not show_chat else "primary",
            ):
                st.session_state.show_chat_panel = not show_chat
                st.rerun()

        if show_chat:
            # Layout: 30% chat, 70% workspace when chat visible
            chat_col, workspace_col = st.columns([0.30, 0.70])
            with chat_col:
                render_chat_panel()
            with workspace_col:
                render_dynamic_workspace()
        else:
            # Full-width workspace when chat hidden
            render_dynamic_workspace()


if __name__ == "__main__":
    main()
