# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Assistant Page — ChatGPT-like structural engineering assistant.

Layout: 40% chat (left) + 60% workspace (right)
Features:
- Natural language beam design
- Cost optimization suggestions
- SmartDesigner insights
- Interactive 3D visualization
"""

from __future__ import annotations

import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="StructEng AI Assistant",
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

import pandas as pd

# Check for OpenAI availability
try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.visualizations_3d import create_beam_3d_figure

# Import structural_lib at module level
from structural_lib import api as structural_api
from structural_lib.insights import SmartDesigner


def get_openai_client() -> OpenAI | None:
    """Get OpenAI client if API key is available."""
    if not OPENAI_AVAILABLE:
        return None

    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if not api_key:
        return None

    return OpenAI(api_key=api_key)


def get_openai_config() -> dict[str, Any]:
    """Get OpenAI configuration from secrets.

    Returns config dict with model, temperature, max_tokens.
    Defaults to gpt-4o-mini if not specified.
    """
    config = {
        "model": "gpt-4o-mini",  # Default: fast, cost-efficient GPT-4o Mini
        "temperature": 0.7,
        "max_tokens": 2000,
    }

    # Read from secrets if available
    if "openai" in st.secrets:
        openai_config = st.secrets.get("openai", {})
        if "model" in openai_config:
            config["model"] = openai_config.get("model", config["model"])
        if "temperature" in openai_config:
            try:
                config["temperature"] = float(openai_config.get("temperature", config["temperature"]))
            except (ValueError, TypeError):
                pass  # Keep default
        if "max_tokens" in openai_config:
            try:
                config["max_tokens"] = int(openai_config.get("max_tokens", config["max_tokens"]))
            except (ValueError, TypeError):
                pass  # Keep default

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

## Guidelines:
1. **Be practical**: Engineers want actionable advice, not theory.
2. **Be specific**: Always include numbers (dimensions, costs, percentages).
3. **Show your work**: Explain the reasoning behind recommendations.
4. **Follow IS 456**: All designs must comply with IS 456:2000.

## Response Format:
- Start with a brief answer
- Present results clearly with key metrics
- Offer follow-up options

## Important:
- Never fabricate structural calculations
- If uncertain, say so and suggest verification
- Always prioritize safety over economy
- Be concise but thorough
"""


def init_session_state():
    """Initialize session state variables."""
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []

    if "current_design" not in st.session_state:
        st.session_state.current_design = None

    if "design_params" not in st.session_state:
        st.session_state.design_params = {
            "b_mm": 300.0,
            "D_mm": 500.0,
            "fck": 25,
            "fy": 500,
            "mu_knm": 100.0,
            "vu_kn": 50.0,
            "span_m": 5.0,
        }

    if "workspace_tab" not in st.session_state:
        st.session_state.workspace_tab = 0

    if "smart_dashboard" not in st.session_state:
        st.session_state.smart_dashboard = None

    if "imported_beams" not in st.session_state:
        st.session_state.imported_beams = None  # DataFrame of imported beams

    if "batch_results" not in st.session_state:
        st.session_state.batch_results = None  # List of design results


def run_design(params: dict[str, Any]) -> dict[str, Any]:
    """Run beam design with given parameters."""
    try:
        b_mm = params.get("b_mm", 300)
        D_mm = params.get("D_mm", 500)

        result = structural_api.design_beam_is456(
            units="IS456",
            b_mm=b_mm,
            D_mm=D_mm,
            d_mm=D_mm - 50,
            fck_nmm2=params.get("fck", 25),
            fy_nmm2=params.get("fy", 500),
            mu_knm=params.get("mu_knm", 100),
            vu_kn=params.get("vu_kn", 50),
        )

        return {
            "success": True,
            "is_safe": result.is_ok,
            "result": result,
            "section": f"{b_mm}×{D_mm}mm",
            "ast_mm2": result.flexure.ast_required,
            "utilization": result.governing_utilization,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_smart_analysis(design_result: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Run SmartDesigner analysis on a design.

    Note: SmartDesigner.analyze expects BeamDesignOutput (with .geometry, .materials).
    Since we use design_beam_is456 which returns ComplianceCaseResult, we need to
    create a wrapper object with the expected attributes.
    """
    try:
        # Create a wrapper object that mimics BeamDesignOutput structure
        # SmartDesigner needs: design.geometry.b_mm, design.geometry.D_mm,
        #                      design.geometry.d_mm, design.materials.fck_nmm2,
        #                      design.materials.fy_nmm2, design.flexure, design.shear
        from types import SimpleNamespace

        b_mm = params.get("b_mm", 300)
        D_mm = params.get("D_mm", 500)
        d_mm = D_mm - 50
        fck = params.get("fck", 25)
        fy = params.get("fy", 500)

        # Create geometry object
        geometry = SimpleNamespace(
            b_mm=b_mm,
            D_mm=D_mm,
            d_mm=d_mm,
            span_mm=params.get("span_m", 5.0) * 1000,
            cover_mm=50,
            d_dash_mm=50,
        )

        # Create materials object
        materials = SimpleNamespace(
            fck_nmm2=fck,
            fy_nmm2=fy,
        )

        # Create flexure wrapper that matches expected interface
        # design_result.flexure has ast_required, we need ast_required_mm2
        flexure_wrapper = SimpleNamespace(
            ast_required_mm2=design_result.flexure.ast_required,
            asc_required_mm2=getattr(design_result.flexure, 'asc', 0),
            xu_mm=getattr(design_result.flexure, 'xu', 0),
            xu_max_mm=getattr(design_result.flexure, 'xu_max', 0),
            mu_lim_knm=getattr(design_result.flexure, 'mu_lim', 0),
            xu_d_ratio=getattr(design_result.flexure, 'xu_d', 0),
            section_type=getattr(design_result.flexure, 'section_type', 'UNDER_REINFORCED'),
            is_safe=design_result.flexure.is_safe,
            utilization=getattr(design_result.flexure, 'utilization', 0),
        )

        # Create shear wrapper
        shear_wrapper = SimpleNamespace(
            tau_v_nmm2=getattr(design_result.shear, 'tv', 0),
            tau_c_nmm2=getattr(design_result.shear, 'tc', 0),
            tau_c_max_nmm2=getattr(design_result.shear, 'tc_max', 0),
            vus_kn=getattr(design_result.shear, 'vus', 0),
            sv_required_mm=getattr(design_result.shear, 'spacing', 0),
            is_safe=design_result.shear.is_safe if design_result.shear else True,
            utilization=getattr(design_result.shear, 'utilization', 0) if design_result.shear else 0,
        )

        # Create wrapper that mimics BeamDesignOutput
        design_wrapper = SimpleNamespace(
            geometry=geometry,
            materials=materials,
            flexure=flexure_wrapper,
            shear=shear_wrapper,
            is_ok=design_result.is_ok,
            governing_utilization=design_result.governing_utilization,
        )

        dashboard = SmartDesigner.analyze(
            design=design_wrapper,
            span_mm=params.get("span_m", 5.0) * 1000,
            mu_knm=params.get("mu_knm", 100),
            vu_kn=params.get("vu_kn", 50),
            include_cost=True,
            include_suggestions=True,
            include_sensitivity=False,  # Skip for speed
            include_constructability=True,
        )
        return {"success": True, "dashboard": dashboard}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _parse_design_request(msg_lower: str, params: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """
    Parse design request from user message and extract parameters.

    Returns updated params and a description of what was parsed.
    """
    updated_params = params.copy()
    parsed_items = []

    # Parse moment (e.g., "150 kN·m", "150 knm", "moment 150")
    moment_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:kn[·\-]?m|knm)", msg_lower)
    if moment_match:
        updated_params["mu_knm"] = float(moment_match.group(1))
        parsed_items.append(f"Moment: {moment_match.group(1)} kN·m")
    else:
        # Try "moment 150" pattern
        moment_match2 = re.search(r"moment\s+(\d+(?:\.\d+)?)", msg_lower)
        if moment_match2:
            updated_params["mu_knm"] = float(moment_match2.group(1))
            parsed_items.append(f"Moment: {moment_match2.group(1)} kN·m")

    # Parse shear (e.g., "80 kN", "shear 80")
    shear_match = re.search(r"(\d+(?:\.\d+)?)\s*kn(?!\s*[·\-]?m)", msg_lower)
    if shear_match:
        updated_params["vu_kn"] = float(shear_match.group(1))
        parsed_items.append(f"Shear: {shear_match.group(1)} kN")
    else:
        shear_match2 = re.search(r"shear\s+(\d+(?:\.\d+)?)", msg_lower)
        if shear_match2:
            updated_params["vu_kn"] = float(shear_match2.group(1))
            parsed_items.append(f"Shear: {shear_match2.group(1)} kN")

    # Parse dimensions (e.g., "300x500", "300×500mm")
    dim_match = re.search(r"(\d+)\s*[x×]\s*(\d+)\s*(?:mm)?", msg_lower)
    if dim_match:
        updated_params["b_mm"] = int(dim_match.group(1))
        updated_params["D_mm"] = int(dim_match.group(2))
        parsed_items.append(f"Section: {dim_match.group(1)}×{dim_match.group(2)}mm")

    # Parse span (e.g., "5m span", "span 5m")
    span_match = re.search(r"(?:span\s+)?(\d+(?:\.\d+)?)\s*m(?:\s+span)?", msg_lower)
    if span_match and "mm" not in msg_lower[max(0, span_match.start()-5):span_match.end()+5]:
        updated_params["span_m"] = float(span_match.group(1))
        parsed_items.append(f"Span: {span_match.group(1)}m")

    # Parse concrete grade (e.g., "M25", "M30 concrete")
    grade_match = re.search(r"m\s*(\d+)\s*(?:concrete)?", msg_lower)
    if grade_match and int(grade_match.group(1)) in [20, 25, 30, 35, 40]:
        updated_params["fck"] = int(grade_match.group(1))
        parsed_items.append(f"Concrete: M{grade_match.group(1)}")

    parsed_desc = ", ".join(parsed_items) if parsed_items else "Using current parameters"
    return updated_params, parsed_desc


def simulate_ai_response(user_message: str) -> str:
    """
    Simulate AI response when OpenAI is not available.
    Uses SmartDesigner for intelligent responses.
    """
    msg_lower = user_message.lower()

    # Check for design request
    if any(word in msg_lower for word in ["design", "beam", "moment", "shear"]):
        # Parse user input for parameters
        updated_params, parsed_desc = _parse_design_request(msg_lower, st.session_state.design_params)

        # Update session state with parsed parameters
        st.session_state.design_params = updated_params

        # Run design with updated parameters
        result = run_design(updated_params)

        if result.get("success", False):
            st.session_state.current_design = result.get("result")

            # Show what was parsed
            parsed_info = f"\n📝 *Parsed from your request: {parsed_desc}*\n" if parsed_desc != "Using current parameters" else ""

            response = f"""I've designed a beam for your requirements:
{parsed_info}
**Design Summary:**
- Section: **{result.get('section', 'N/A')}**
- Steel Area Required: **{result.get('ast_mm2', 0):.0f} mm²**
- Utilization: **{result.get('utilization', 0):.1%}**
- Status: {"✅ **SAFE**" if result.get('is_safe', False) else "❌ **UNSAFE**"}

The design uses M{updated_params.get('fck', 25)} concrete and Fe{updated_params.get('fy', 500)} steel.

Would you like me to:
1. 💰 Optimize for cost?
2. 📊 Show detailed analysis?
3. 🎨 View in 3D?
"""
            return response
        else:
            return f"Sorry, I encountered an error: {result.get('error', 'Unknown error')}"

    # Check for optimization request
    elif any(word in msg_lower for word in ["cost", "optimize", "cheaper", "save"]):
        if st.session_state.current_design:
            analysis = run_smart_analysis(
                st.session_state.current_design, st.session_state.design_params
            )

            if analysis["success"]:
                st.session_state.smart_dashboard = analysis["dashboard"]
                dashboard = analysis["dashboard"]

                response = f"""Here's my cost optimization analysis:

**Current Design:**
- Cost: ₹{dashboard.cost.current_cost:,.0f}/m
- Optimal: ₹{dashboard.cost.optimal_cost:,.0f}/m
- **Potential Savings: {dashboard.cost.savings_percent:.1f}%**

**Quick Wins:**
"""
                for win in dashboard.summary.quick_wins[:3]:
                    response += f"- {win}\n"

                if dashboard.suggestions:
                    response += f"\n**Top Recommendations:**\n"
                    for sug in dashboard.suggestions.top_3[:2]:
                        response += f"- [{sug.get('impact', 'MEDIUM')}] {sug.get('category', '')}: {sug.get('description', '')[:100]}...\n"

                return response
            else:
                return f"Analysis failed: {analysis.get('error', 'Unknown error')}. Try redesigning the beam first."
        else:
            return "Please design a beam first, then I can help optimize the cost."

    # Check for analysis request
    elif any(
        word in msg_lower for word in ["analyze", "analysis", "smart", "dashboard"]
    ):
        if st.session_state.current_design:
            analysis = run_smart_analysis(
                st.session_state.current_design, st.session_state.design_params
            )

            if analysis["success"]:
                st.session_state.smart_dashboard = analysis["dashboard"]
                dashboard = analysis["dashboard"]
                s = dashboard.summary

                response = f"""Here's the comprehensive SmartDesigner analysis:

**Overall Score: {s.overall_score:.1%}**

| Metric | Score |
|--------|-------|
| Safety | {s.safety_score:.1%} |
| Cost Efficiency | {s.cost_efficiency:.1%} |
| Constructability | {s.constructability:.1%} |
| Robustness | {s.robustness:.1%} |

**Status: {s.design_status}**
"""
                if s.key_issues:
                    response += "\n**⚠️ Issues:**\n"
                    for issue in s.key_issues:
                        response += f"- {issue}\n"

                if s.quick_wins:
                    response += "\n**💡 Quick Wins:**\n"
                    for win in s.quick_wins:
                        response += f"- {win}\n"

                return response
            else:
                return f"Analysis failed: {analysis.get('error', 'Unknown error')}. Try redesigning the beam first."
        else:
            return "Please design a beam first, then I can analyze it."

    # Check for 3D view request
    elif any(word in msg_lower for word in ["3d", "visual", "show", "view"]):
        if st.session_state.current_design:
            st.session_state.workspace_tab = 1  # Switch to 3D tab
            return "I've switched to the 3D view in the workspace panel. You can see the beam visualization there. 👉"
        return "Please design a beam first to see the 3D visualization."

    # Check for help request
    elif any(word in msg_lower for word in ["help", "what can", "how to"]):
        return """I'm your structural engineering AI assistant! Here's what I can do:

**Design:**
- "Design a beam for 150 kN·m moment"
- "Design a 300×500mm beam"

**Optimize:**
- "Optimize the cost"
- "How can I make this cheaper?"

**Analyze:**
- "Run smart analysis"
- "Show the dashboard"

**Visualize:**
- "Show 3D view"
- "Visualize the beam"

Try asking me to design a beam to get started!"""

    # Default response
    else:
        return """I'm not sure what you're asking. Try one of these:

- **"Design a beam for 120 kN·m"** - I'll design a beam
- **"Optimize cost"** - I'll find savings
- **"Analyze"** - I'll run SmartDesigner
- **"Show 3D"** - I'll display visualization
- **"Help"** - I'll show all options"""


def get_ai_response(user_message: str) -> str:
    """Get AI response - uses OpenAI if available, else simulation."""
    client = get_openai_client()

    if client:
        try:
            config = get_openai_config()

            # Build messages
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add history (last 10 messages)
            for msg in st.session_state.ai_messages[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": user_message})

            # Call OpenAI with configured model
            response = client.chat.completions.create(
                model=config["model"],
                messages=messages,
                max_tokens=config["max_tokens"],
                temperature=config["temperature"],
            )

            return response.choices[0].message.content

        except Exception as e:
            # Fallback to simulation on error with error info
            return f"⚠️ API Error: {str(e)[:100]}... Using local SmartDesigner.\n\n" + simulate_ai_response(user_message)
    else:
        # No API key - use simulation
        return simulate_ai_response(user_message)


def _handle_quick_action(message: str) -> None:
    """Handle quick action button clicks - helper to avoid code duplication."""
    st.session_state.ai_messages.append({"role": "user", "content": message})
    response = get_ai_response(message)
    st.session_state.ai_messages.append({"role": "assistant", "content": response})
    st.rerun()


def render_chat_panel():
    """Render the chat panel (left side)."""
    st.markdown("### 💬 Chat")

    # Welcome message if no history
    if len(st.session_state.ai_messages) == 0:
        st.info(
            "👋 **Welcome!** I'm your AI structural engineering assistant.\n\n"
            "Try asking: *\"Design a beam for 150 kN·m moment\"* or click a quick action below."
        )

    # Chat container with fixed height
    chat_container = st.container(height=450)

    with chat_container:
        # Display message history
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input - use traditional pattern for scanner compatibility
    prompt = st.chat_input("Ask about beam design, costs, IS 456 clauses...")
    if prompt:
        # Add user message
        st.session_state.ai_messages.append({"role": "user", "content": prompt})

        # Get AI response
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt)

        # Add assistant response
        st.session_state.ai_messages.append({"role": "assistant", "content": response})

        # Rerun to show new messages
        st.rerun()

    # Quick action buttons with Clear option
    st.markdown("**Quick Actions:**")
    cols = st.columns(5)
    with cols[0]:
        if st.button("🏗️ Design", use_container_width=True, help="Design a beam"):
            _handle_quick_action("Design a beam for current parameters")
    with cols[1]:
        if st.button("💰 Cost", use_container_width=True, help="Optimize cost"):
            _handle_quick_action("Optimize the cost")
    with cols[2]:
        if st.button("📊 Analyze", use_container_width=True, help="Smart analysis"):
            _handle_quick_action("Run smart analysis")
    with cols[3]:
        if st.button("🎨 3D", use_container_width=True, help="Show 3D view"):
            _handle_quick_action("Show 3D view")
    with cols[4]:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear chat"):
            st.session_state.ai_messages = []
            st.session_state.current_design = None
            st.session_state.smart_dashboard = None
            st.rerun()


def render_workspace_panel():
    """Render the workspace panel (right side)."""
    st.markdown("### 📊 Workspace")

    # Tabs for different views (compact)
    tabs = st.tabs(["📋 Results", "🎨 3D", "📥 Import", "💰 Cost", "📊 Dashboard"])

    # Tab 0: Design Results
    with tabs[0]:
        if st.session_state.current_design:
            design = st.session_state.current_design
            params = st.session_state.design_params

            # Get dimensions from params (not design.geometry which doesn't exist)
            b_mm = params.get("b_mm", 300)
            D_mm = params.get("D_mm", 500)

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Section", f"{b_mm}×{D_mm}mm")
                st.metric(
                    "Concrete",
                    f"M{params.get('fck', 25)}",
                    help=f"fck = {params.get('fck', 25)} N/mm²",
                )

            with col2:
                st.metric(
                    "Utilization",
                    f"{design.governing_utilization:.1%}",
                    delta="SAFE" if design.is_ok else "UNSAFE",
                    delta_color="normal" if design.is_ok else "inverse",
                )
                st.metric(
                    "Steel", f"Fe{params.get('fy', 500)}", help=f"fy = {params.get('fy', 500)} N/mm²"
                )

            st.divider()

            st.markdown("**Flexure Design:**")
            st.write(
                f"- Steel Required: **{design.flexure.ast_required:.0f} mm²**"
            )
            st.write(f"- Section Type: {design.flexure.section_type.value}")
            st.write(f"- Mu,lim: {design.flexure.mu_lim:.1f} kN·m")

            if design.shear:
                st.markdown("**Shear Design:**")
                st.write(f"- Status: **{'SAFE' if design.shear.is_safe else 'UNSAFE'}**")
                st.write(f"- τv = {design.shear.tv:.2f} N/mm²")
                st.write(f"- τc = {design.shear.tc:.2f} N/mm²")
                if design.shear.spacing > 0:
                    st.write(f"- Stirrup Spacing: {design.shear.spacing:.0f} mm")
        else:
            st.info(
                "No design yet. Ask the AI to design a beam or click 🏗️ Design button."
            )

        # Design parameters editor
        with st.expander("⚙️ Design Parameters", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.design_params["b_mm"] = st.number_input(
                    "Width (mm)", value=float(st.session_state.design_params["b_mm"]), step=25.0
                )
                st.session_state.design_params["D_mm"] = st.number_input(
                    "Depth (mm)", value=float(st.session_state.design_params["D_mm"]), step=25.0
                )
                st.session_state.design_params["span_m"] = st.number_input(
                    "Span (m)",
                    value=float(st.session_state.design_params["span_m"]),
                    step=0.5,
                )
            with col2:
                st.session_state.design_params["mu_knm"] = st.number_input(
                    "Moment (kN·m)",
                    value=float(st.session_state.design_params["mu_knm"]),
                    step=10.0,
                )
                st.session_state.design_params["vu_kn"] = st.number_input(
                    "Shear (kN)", value=float(st.session_state.design_params["vu_kn"]), step=5.0
                )
                st.session_state.design_params["fck"] = st.selectbox(
                    "Concrete Grade",
                    [20, 25, 30, 35, 40],
                    index=[20, 25, 30, 35, 40].index(
                        st.session_state.design_params["fck"]
                    ),
                )

    # Tab 1: 3D View
    with tabs[1]:
        if st.session_state.current_design:
            params = st.session_state.design_params

            # Get dimensions from params
            b = params.get("b_mm", 300)
            D = params.get("D_mm", 500)
            span = params.get("span_m", 5.0) * 1000

            try:
                fig = create_beam_3d_figure(
                    b=b,
                    D=D,
                    span=span,
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering 3D: {e}")
        else:
            st.info("Design a beam to see 3D visualization.")

    # Tab 2: Import CSV (Multiple Files Support)
    with tabs[2]:
        st.markdown("**Multi-File CSV Import**")
        st.caption("Upload beam data from ETABS, SAFE, or custom CSV files")

        # Two file uploaders for geometry and forces (like ETABS export)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📐 Geometry CSV** (optional)")
            geom_file = st.file_uploader(
                "Beam geometry",
                type=["csv"],
                help="Beam IDs, dimensions (b, D)",
                key="geom_csv",
                label_visibility="collapsed",
            )
        with col2:
            st.markdown("**📊 Forces CSV** (required)")
            forces_file = st.file_uploader(
                "Beam forces",
                type=["csv"],
                help="Beam IDs, Mu, Vu values",
                key="forces_csv",
                label_visibility="collapsed",
            )

        # Process uploaded files
        if forces_file is not None:
            try:
                forces_df = pd.read_csv(forces_file)
                geom_df = pd.read_csv(geom_file) if geom_file else None

                st.success(f"✅ Loaded {len(forces_df)} force records" +
                          (f" + {len(geom_df)} geometry records" if geom_df is not None else ""))

                # Show preview
                with st.expander("Preview data", expanded=False):
                    if geom_df is not None:
                        st.markdown("**Geometry:**")
                        st.dataframe(geom_df.head(5), use_container_width=True)
                    st.markdown("**Forces:**")
                    st.dataframe(forces_df.head(5), use_container_width=True)

                # Column mapping
                st.markdown("**Map Columns**")
                force_cols = list(forces_df.columns)
                geom_cols = list(geom_df.columns) if geom_df is not None else force_cols

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("*Geometry*")
                    id_col = st.selectbox("Beam ID", ["--"] + force_cols, key="id_col_ai")
                    b_col = st.selectbox("Width (b)", ["--"] + geom_cols, key="b_col_ai")
                    d_col = st.selectbox("Depth (D)", ["--"] + geom_cols, key="d_col_ai")
                with col2:
                    st.markdown("*Forces*")
                    mu_col = st.selectbox("Moment (Mu)", ["--"] + force_cols, key="mu_col_ai")
                    vu_col = st.selectbox("Shear (Vu)", ["--"] + force_cols, key="vu_col_ai")
                with col3:
                    st.markdown("*Defaults*")
                    default_b = st.number_input("Default b (mm)", value=300.0, step=25.0, key="def_b")
                    default_d = st.number_input("Default D (mm)", value=500.0, step=25.0, key="def_d")

                # Combine data
                if geom_df is not None and id_col != "--":
                    # Merge geometry and forces on beam ID
                    combined_df = forces_df.merge(geom_df, on=id_col, how="left", suffixes=("", "_geom"))
                else:
                    combined_df = forces_df

                st.session_state.imported_beams = combined_df

                # Design button
                if st.button("🏗️ Design All Beams", type="primary", key="batch_design_btn"):
                    if mu_col != "--":
                        total_beams = len(combined_df)
                        if total_beams == 0:
                            st.warning("No beams to design. Check your CSV file.")
                        else:
                            with st.spinner(f"Designing {total_beams} beams..."):
                                results = []
                                progress = st.progress(0)
                                for idx, row in combined_df.iterrows():
                                    # Get dimensions from columns or use defaults
                                    b_val = row.get(b_col, default_b) if b_col != "--" else default_b
                                    d_val = row.get(d_col, default_d) if d_col != "--" else default_d

                                    params = {
                                        "b_mm": float(b_val) if pd.notna(b_val) else default_b,
                                        "D_mm": float(d_val) if pd.notna(d_val) else default_d,
                                        "mu_knm": float(row.get(mu_col, 100)),
                                        "vu_kn": float(row.get(vu_col, 50)) if vu_col != "--" and pd.notna(row.get(vu_col)) else 50.0,
                                        "fck": 25,
                                        "fy": 500,
                                    }
                                    result = run_design(params)
                                    result["beam_id"] = row.get(id_col, f"B{idx+1}") if id_col != "--" else f"B{idx+1}"
                                    results.append(result)
                                    progress.progress((idx + 1) / total_beams)

                                st.session_state.batch_results = results
                                safe_count = sum(1 for r in results if r.get("is_safe", False))
                                st.success(f"✅ Designed {len(results)} beams: {safe_count} SAFE, {len(results)-safe_count} UNSAFE")

                                # Show results summary
                                results_data = []
                                for r in results:
                                    results_data.append({
                                        "ID": r.get("beam_id", "-"),
                                        "Section": r.get("section", "-"),
                                        "Ast (mm²)": round(r.get("ast_mm2", 0)),
                                        "Util": f"{r.get('utilization', 0):.0%}",
                                        "Status": "✅" if r.get("is_safe") else "❌",
                                    })
                                st.dataframe(pd.DataFrame(results_data), use_container_width=True)
                    else:
                        st.warning("Please map at least the Moment (Mu) column")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
        else:
            st.info("📁 Upload CSV files to batch design beams.")
            st.caption("**ETABS workflow:** Export 'Connectivity - Frame' and 'Element Forces - Beams'")
            st.caption("**Simple CSV:** Just needs columns for Mu (moment) values")

    # Tab 3: Cost Analysis
    with tabs[3]:
        if st.session_state.smart_dashboard and st.session_state.smart_dashboard.cost:
            cost = st.session_state.smart_dashboard.cost

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Cost", f"₹{cost.current_cost:,.0f}/m")
            with col2:
                st.metric("Optimal Cost", f"₹{cost.optimal_cost:,.0f}/m")
            with col3:
                st.metric(
                    "Savings",
                    f"{cost.savings_percent:.1f}%",
                    delta=f"-₹{cost.current_cost - cost.optimal_cost:,.0f}",
                )

            st.divider()

            if st.session_state.smart_dashboard.suggestions:
                st.markdown("**💡 Cost Reduction Suggestions:**")
                for sug in st.session_state.smart_dashboard.suggestions.suggestions[:5]:
                    impact = sug.get("impact", "medium").upper()
                    impact_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                        impact, "⚪"
                    )
                    st.markdown(
                        f"{impact_color} **[{impact}]** {sug.get('description', 'No description')}"
                    )
        else:
            st.info("Run cost optimization to see analysis. Ask 'Optimize cost'.")

    # Tab 4: Smart Dashboard
    with tabs[4]:
        if st.session_state.smart_dashboard:
            dashboard = st.session_state.smart_dashboard
            s = dashboard.summary

            # Overall score gauge
            st.markdown(f"### Overall Score: **{s.overall_score:.1%}**")

            # Score breakdown
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Safety", f"{s.safety_score:.0%}")
            with col2:
                st.metric("Cost", f"{s.cost_efficiency:.0%}")
            with col3:
                st.metric("Constructability", f"{s.constructability:.0%}")
            with col4:
                st.metric("Robustness", f"{s.robustness:.0%}")

            st.divider()

            # Status
            status_color = {"PASS": "✅", "WARNING": "⚠️", "FAIL": "❌"}.get(
                s.design_status, "❓"
            )
            st.markdown(f"**Status:** {status_color} {s.design_status}")

            # Key issues
            if s.key_issues:
                st.markdown("**⚠️ Key Issues:**")
                for issue in s.key_issues:
                    st.warning(issue)

            # Quick wins
            if s.quick_wins:
                st.markdown("**💡 Quick Wins:**")
                for win in s.quick_wins:
                    st.success(win)

            # Constructability
            if dashboard.constructability:
                with st.expander("🏗️ Constructability Details"):
                    cons = dashboard.constructability
                    st.write(f"- Score: **{cons.score:.1%}** ({cons.level})")
                    st.write(f"- Bar Complexity: {cons.bar_complexity}")
                    st.write(f"- Congestion Risk: {cons.congestion_risk}")
                    if cons.issues:
                        st.write("Issues:")
                        for issue in cons.issues:
                            st.write(f"  - {issue}")
        else:
            st.info("Run smart analysis to see dashboard. Ask 'Run smart analysis'.")


def main():
    """Main function."""
    init_session_state()

    # Compact header
    st.markdown("## 🤖 StructEng AI Assistant")

    # Subtle status in sidebar instead of main area
    with st.sidebar:
        st.markdown("### AI Status")
        client = get_openai_client()
        if client:
            config = get_openai_config()
            st.caption(f"✅ OpenAI {config['model']}")
        else:
            st.caption("💡 Local SmartDesigner mode")
            st.caption("Add OPENAI_API_KEY in secrets for GPT")

    # Main layout: 40% chat, 60% workspace
    chat_col, workspace_col = st.columns([0.4, 0.6])

    with chat_col:
        render_chat_panel()

    with workspace_col:
        render_workspace_panel()


if __name__ == "__main__":
    main()
