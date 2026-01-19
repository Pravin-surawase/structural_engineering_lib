# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Assistant Page — ChatGPT-like structural engineering assistant.

Layout: Compact professional design with chat + workspace
Features:
- Natural language beam design with OpenAI GPT
- Real-time design feedback
- SmartDesigner cost & constructability insights
- Interactive 3D visualization
- ETABS import integration

UI/UX: Compact, professional, responsive design with cards
"""

from __future__ import annotations

import streamlit as st

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="AI Assistant | StructEng",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Imports after page config
import re
import sys
from pathlib import Path
from typing import Any

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

# Import layout utilities
try:
    from utils.layout import inject_modern_css
    from utils.theme_manager import apply_dark_mode_theme, initialize_theme

    HAS_LAYOUT = True
except ImportError:
    HAS_LAYOUT = False


# Default model configuration
DEFAULT_MODEL = "gpt-4o-mini"  # Fast and cost-effective for engineering tasks
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 1500


def get_openai_config() -> dict[str, Any]:
    """Get OpenAI configuration from secrets.

    Reads from secrets.toml:
        OPENAI_API_KEY = "sk-..."
        [openai]
        model = "gpt-4o-mini"  # or gpt-4, gpt-4o, etc.
        temperature = 0.7
        max_tokens = 1500

    Returns dict with api_key, model, temperature, max_tokens.
    """
    config = {
        "api_key": None,
        "model": DEFAULT_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
    }

    # Get API key (top-level secret)
    config["api_key"] = st.secrets.get("OPENAI_API_KEY", None)

    # Get optional model settings from [openai] section
    if "openai" in st.secrets:
        openai_config = st.secrets["openai"]
        config["model"] = openai_config.get("model", DEFAULT_MODEL)
        config["temperature"] = openai_config.get("temperature", DEFAULT_TEMPERATURE)
        config["max_tokens"] = int(openai_config.get("max_tokens", DEFAULT_MAX_TOKENS))

    return config


def get_openai_client() -> OpenAI | None:
    """Get OpenAI client if API key is available."""
    if not OPENAI_AVAILABLE:
        return None

    config = get_openai_config()
    if not config["api_key"]:
        return None

    return OpenAI(api_key=config["api_key"])


def inject_ai_page_css() -> None:
    """Inject custom CSS for AI Assistant page - compact professional styling."""
    st.markdown(
        """
        <style>
        /* Compact header styling */
        .ai-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 1rem 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            color: white;
        }
        .ai-header h1 {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 600;
        }
        .ai-header p {
            margin: 0.25rem 0 0 0;
            opacity: 0.8;
            font-size: 0.85rem;
        }

        /* Status badge */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .status-connected {
            background: rgba(34, 197, 94, 0.15);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }
        .status-local {
            background: rgba(234, 179, 8, 0.15);
            color: #eab308;
            border: 1px solid rgba(234, 179, 8, 0.3);
        }

        /* Chat container styling */
        .chat-section {
            background: #fafafa;
            border-radius: 12px;
            border: 1px solid #e5e5e5;
            height: 100%;
        }

        /* Message styling */
        [data-testid="stChatMessage"] {
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
        }

        /* Quick action buttons - compact grid */
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 0.5rem;
        }

        /* Metric cards - compact */
        .metric-row {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
        }
        .mini-metric {
            flex: 1;
            background: white;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        .mini-metric .value {
            font-size: 1.25rem;
            font-weight: 600;
            color: #1a1a2e;
        }
        .mini-metric .label {
            font-size: 0.7rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Results card */
        .results-card {
            background: white;
            border: 1px solid #e5e5e5;
            border-radius: 12px;
            padding: 1rem;
        }

        /* Hide default streamlit padding for tighter layout */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Tab styling - compact */
        [data-testid="stTabs"] button {
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


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
            "b_mm": 300,
            "D_mm": 500,
            "fck": 25,
            "fy": 500,
            "mu_knm": 100,
            "vu_kn": 50,
            "span_m": 5.0,
        }

    if "workspace_tab" not in st.session_state:
        st.session_state.workspace_tab = 0

    if "smart_dashboard" not in st.session_state:
        st.session_state.smart_dashboard = None


def run_design(params: dict[str, Any]) -> dict[str, Any]:
    """Run beam design with given parameters.

    Returns a dict with success status and design results.
    Uses params for section dimensions since ComplianceCaseResult
    doesn't store geometry (it's an input, not output).
    """
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

        # ComplianceCaseResult structure:
        # - flexure.ast_required (not ast_required_mm2)
        # - governing_utilization
        # - is_ok
        return {
            "success": True,
            "is_safe": result.is_ok,
            "result": result,
            "section": f"{b_mm}×{D_mm}mm",
            "ast_mm2": result.flexure.ast_required,
            "utilization": result.governing_utilization,
            "b_mm": b_mm,
            "D_mm": D_mm,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_smart_analysis(design_result: Any, params: dict[str, Any]) -> dict[str, Any]:
    """Run SmartDesigner analysis on a design."""
    try:
        dashboard = SmartDesigner.analyze(
            design=design_result,
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


def simulate_ai_response(user_message: str) -> str:
    """
    Simulate AI response when OpenAI is not available.
    Uses SmartDesigner for intelligent responses.
    """
    msg_lower = user_message.lower()

    # Check for design request
    if any(word in msg_lower for word in ["design", "beam", "moment", "shear"]):
        # Extract numbers if present (re imported at module level)
        numbers = re.findall(r"(\d+(?:\.\d+)?)\s*(?:kn|knm|kn·m|mm|m)", msg_lower)

        # Run design with current parameters
        result = run_design(st.session_state.design_params)

        if result.get("success", False):
            st.session_state.current_design = result.get("result")

            response = f"""I've designed a beam for your requirements:

**Design Summary:**
- Section: **{result.get('section', 'N/A')}**
- Steel Area Required: **{result.get('ast_mm2', 0):.0f} mm²**
- Utilization: **{result.get('utilization', 0):.1%}**
- Status: {"✅ **SAFE**" if result.get('is_safe', False) else "❌ **UNSAFE**"}

The design uses M{st.session_state.design_params.get('fck', 25)} concrete and Fe{st.session_state.design_params.get('fy', 500)} steel.

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
                return "I need a design first. Please ask me to design a beam."
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
            # Fallback to simulation on error
            return f"⚠️ API Error: {str(e)[:100]}... Using local SmartDesigner.\n\n" + simulate_ai_response(user_message)
    else:
        # No API key - use simulation
        return simulate_ai_response(user_message)


def render_chat_panel():
    """Render the chat panel - compact design with welcome message."""
    # Welcome message if no history
    if len(st.session_state.ai_messages) == 0:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                border: 1px solid #bae6fd;
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 0.5rem;
            ">
                <div style="font-weight: 600; color: #0369a1; margin-bottom: 0.5rem;">
                    👋 Welcome! I'm your AI structural engineering assistant.
                </div>
                <div style="font-size: 0.85rem; color: #0c4a6e;">
                    Try: <b>"Design a beam for 150 kN·m"</b> or click a quick action below.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Chat container with fixed height - taller for better UX
    chat_container = st.container(height=420)

    with chat_container:
        # Display message history
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Quick action buttons ABOVE chat input for better flow
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🏗️ Design", use_container_width=True, help="Design a beam"):
            _handle_quick_action("Design a beam for current parameters")
    with c2:
        if st.button("💰 Cost", use_container_width=True, help="Optimize cost"):
            _handle_quick_action("Optimize the cost")
    with c3:
        if st.button("📊 Analyze", use_container_width=True, help="Smart analysis"):
            _handle_quick_action("Run smart analysis")
    with c4:
        if st.button("🔄 Clear", use_container_width=True, help="Clear chat"):
            st.session_state.ai_messages = []
            st.session_state.current_design = None
            st.session_state.smart_dashboard = None
            st.rerun()

    # Chat input
    prompt = st.chat_input("Ask about beam design, costs, or IS 456...")
    if prompt:
        # Add user message
        st.session_state.ai_messages.append({"role": "user", "content": prompt})

        # Get AI response
        with st.spinner("Thinking..."):
            response = get_ai_response(prompt)

        # Add assistant response
        st.session_state.ai_messages.append({"role": "assistant", "content": response})
        st.rerun()


def _handle_quick_action(message: str) -> None:
    """Handle quick action button clicks."""
    st.session_state.ai_messages.append({"role": "user", "content": message})
    response = get_ai_response(message)
    st.session_state.ai_messages.append({"role": "assistant", "content": response})
    st.rerun()


def render_workspace_panel():
    """Render the workspace panel (right side)."""
    # Tabs for different views - added Import tab
    tabs = st.tabs(["📋 Results", "🎨 3D View", "💰 Cost", "📊 Dashboard", "📥 Import"])

    # Tab 0: Design Results
    with tabs[0]:
        if st.session_state.current_design:
            design = st.session_state.current_design
            params = st.session_state.design_params

            # Extract dimensions from params (not from result)
            b_mm = params.get("b_mm", 300)
            D_mm = params.get("D_mm", 500)

            # Compact metric cards
            st.markdown(
                f"""
                <div class="metric-row">
                    <div class="mini-metric">
                        <div class="value">{b_mm}×{D_mm}</div>
                        <div class="label">Section (mm)</div>
                    </div>
                    <div class="mini-metric">
                        <div class="value">{design.governing_utilization:.0%}</div>
                        <div class="label">Utilization</div>
                    </div>
                    <div class="mini-metric">
                        <div class="value">{design.flexure.ast_required:.0f}</div>
                        <div class="label">Ast (mm²)</div>
                    </div>
                    <div class="mini-metric">
                        <div class="value">{"✅" if design.is_ok else "❌"}</div>
                        <div class="label">Status</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Detailed results in expanders
            with st.expander("📐 Flexure Details", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Steel Required:** {design.flexure.ast_required:.0f} mm²")
                    st.write(f"**Section Type:** {design.flexure.section_type.name}")
                with col2:
                    st.write(f"**Mu_lim:** {design.flexure.mu_lim:.1f} kN·m")
                    st.write(f"**Materials:** M{params.get('fck', 25)} / Fe{params.get('fy', 500)}")

            if design.shear:
                with st.expander("⚔️ Shear Details"):
                    status = "✅ SAFE" if design.shear.is_safe else "❌ Unsafe"
                    st.write(f"**Status:** {status}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**τv:** {design.shear.tv:.2f} N/mm²")
                    with col2:
                        st.write(f"**τc:** {design.shear.tc:.2f} N/mm²")
        else:
            st.info("💡 Ask the AI to design a beam or click the 🏗️ Design button.")

        # Design parameters editor
        with st.expander("⚙️ Design Parameters", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.design_params["b_mm"] = st.number_input(
                    "Width (mm)", value=st.session_state.design_params["b_mm"], step=25
                )
                st.session_state.design_params["D_mm"] = st.number_input(
                    "Depth (mm)", value=st.session_state.design_params["D_mm"], step=25
                )
                st.session_state.design_params["span_m"] = st.number_input(
                    "Span (m)",
                    value=st.session_state.design_params["span_m"],
                    step=0.5,
                )
            with col2:
                st.session_state.design_params["mu_knm"] = st.number_input(
                    "Moment (kN·m)",
                    value=st.session_state.design_params["mu_knm"],
                    step=10,
                )
                st.session_state.design_params["vu_kn"] = st.number_input(
                    "Shear (kN)", value=st.session_state.design_params["vu_kn"], step=5
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

            try:
                fig = create_beam_3d_figure(
                    b_mm=params.get("b_mm", 300),
                    D_mm=params.get("D_mm", 500),
                    span_mm=params.get("span_m", 5.0) * 1000,
                    title="Beam 3D Preview",
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering 3D: {e}")
        else:
            st.info("Design a beam to see 3D visualization.")

    # Tab 2: Cost Analysis
    with tabs[2]:
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

    # Tab 3: Smart Dashboard
    with tabs[3]:
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

    # Tab 4: Import from ETABS/Multi-Format
    with tabs[4]:
        st.markdown("**📥 Import ETABS / Analysis Results**")

        # Check if there's data from Multi-Format Import page
        has_import_data = (
            st.session_state.get("mf_beams") or
            st.session_state.get("mf_forces") or
            st.session_state.get("mf_design_results")
        )

        if has_import_data:
            st.success("✅ Import data found from Multi-Format Import page!")

            # Show summary of imported data
            beams = st.session_state.get("mf_beams", [])
            forces = st.session_state.get("mf_forces", [])
            results = st.session_state.get("mf_design_results")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Beams", len(beams))
            with col2:
                st.metric("Load Cases", len(forces))
            with col3:
                st.metric("Results", "Yes" if results else "No")

            st.divider()

            # Allow selecting a beam to analyze
            if beams:
                beam_labels = [f"{b.beam_id} ({b.width_mm}×{b.depth_mm}mm)" for b in beams]
                selected = st.selectbox("Select beam to analyze:", beam_labels)

                if st.button("📊 Load into AI Chat", use_container_width=True):
                    # Get selected beam index
                    idx = beam_labels.index(selected)
                    beam = beams[idx]

                    # Update design params from imported beam
                    st.session_state.design_params["b_mm"] = beam.width_mm
                    st.session_state.design_params["D_mm"] = beam.depth_mm

                    # Find forces for this beam if available
                    if forces:
                        beam_forces = [f for f in forces if f.beam_id == beam.beam_id]
                        if beam_forces:
                            max_mu = max(abs(f.mu_knm) for f in beam_forces)
                            max_vu = max(abs(f.vu_kn) for f in beam_forces)
                            st.session_state.design_params["mu_knm"] = max_mu
                            st.session_state.design_params["vu_kn"] = max_vu

                    # Add message to chat
                    msg = f"I've loaded beam **{beam.beam_id}** ({beam.width_mm}×{beam.depth_mm}mm) from your ETABS import. Please design this beam."
                    st.session_state.ai_messages.append({"role": "user", "content": msg})
                    response = get_ai_response("Design a beam for current parameters")
                    st.session_state.ai_messages.append({"role": "assistant", "content": response})
                    st.rerun()

            # Chat about all results
            if results:
                if st.button("💬 Analyze All Results", use_container_width=True):
                    msg = f"I have {len(beams)} beams imported from ETABS. Can you give me a summary of the design results and highlight any issues?"
                    st.session_state.ai_messages.append({"role": "user", "content": msg})
                    # For now, use simulation since we can't pass structured data to OpenAI easily
                    response = f"""Based on your imported data:

**Summary:**
- **Total Beams:** {len(beams)}
- **Analyzed:** {len(results.cases) if hasattr(results, 'cases') else 'N/A'} load cases

**Recommendations:**
1. Review beams with utilization > 90%
2. Check shear capacity for heavily loaded spans
3. Consider optimization for under-utilized sections

Would you like me to analyze a specific beam in detail?"""
                    st.session_state.ai_messages.append({"role": "assistant", "content": response})
                    st.rerun()
        else:
            st.info(
                """No import data found.

**To import ETABS/Analysis results:**
1. Go to **📥 Multi-Format Import** page (page 7)
2. Upload your ETABS geometry and forces CSV files
3. Return here to chat about the results

Or use the quick parameters above to design a beam manually."""
            )

            if st.button("➡️ Go to Multi-Format Import", use_container_width=True):
                st.switch_page("pages/07_📥_multi_format_import.py")


def render_compact_header() -> None:
    """Render a compact professional header with status indicator."""
    client = get_openai_client()

    # Build status badge HTML
    if client:
        config = get_openai_config()
        model_name = config["model"]
        status_html = f"""
        <span class="status-badge status-connected">
            🟢 {model_name}
        </span>
        """
    else:
        status_html = """
        <span class="status-badge status-local">
            🟡 Local SmartDesigner
        </span>
        """

    # Compact header with gradient background
    st.markdown(
        f"""
        <div class="ai-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>🤖 StructEng AI Assistant</h1>
                    <p>Your intelligent structural engineering companion • IS 456 Beam Design</p>
                </div>
                <div>
                    {status_html}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_params_bar() -> None:
    """Render a compact parameters bar at the top."""
    params = st.session_state.design_params

    with st.expander("⚙️ Quick Parameters", expanded=False):
        cols = st.columns(7)
        with cols[0]:
            st.session_state.design_params["b_mm"] = st.number_input(
                "Width", value=params.get("b_mm", 300), step=25, key="qp_b"
            )
        with cols[1]:
            st.session_state.design_params["D_mm"] = st.number_input(
                "Depth", value=params.get("D_mm", 500), step=25, key="qp_D"
            )
        with cols[2]:
            st.session_state.design_params["span_m"] = st.number_input(
                "Span (m)", value=params.get("span_m", 5.0), step=0.5, key="qp_span"
            )
        with cols[3]:
            st.session_state.design_params["mu_knm"] = st.number_input(
                "Mu (kN·m)", value=params.get("mu_knm", 100), step=10, key="qp_mu"
            )
        with cols[4]:
            st.session_state.design_params["vu_kn"] = st.number_input(
                "Vu (kN)", value=params.get("vu_kn", 50), step=5, key="qp_vu"
            )
        with cols[5]:
            st.session_state.design_params["fck"] = st.selectbox(
                "Concrete",
                [20, 25, 30, 35, 40],
                index=[20, 25, 30, 35, 40].index(params.get("fck", 25)),
                key="qp_fck",
            )
        with cols[6]:
            st.session_state.design_params["fy"] = st.selectbox(
                "Steel",
                [415, 500, 550],
                index=[415, 500, 550].index(params.get("fy", 500)),
                key="qp_fy",
            )


def main():
    """Main function - compact professional layout."""
    # Initialize
    init_session_state()

    # Apply theme and styling
    if HAS_LAYOUT:
        initialize_theme()
        apply_dark_mode_theme()
    inject_ai_page_css()

    # Compact header with status
    render_compact_header()

    # Quick parameters bar (collapsed by default)
    render_quick_params_bar()

    # Main layout: 45% chat, 55% workspace (slightly more balanced)
    chat_col, workspace_col = st.columns([0.45, 0.55], gap="medium")

    with chat_col:
        render_chat_panel()

    with workspace_col:
        render_workspace_panel()


if __name__ == "__main__":
    main()
