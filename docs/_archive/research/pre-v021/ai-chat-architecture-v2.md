# AI Chat Architecture V2 — Streamlit Implementation

**Type:** Research
**Audience:** All Agents
**Status:** Draft
**Importance:** Critical
**Created:** 2026-01-19
**Last Updated:** 2026-01-19
**Related Tasks:** TASK-AI-001, TASK-3D-VIZ

---

## Executive Summary

This document defines the architecture for an AI-powered structural engineering chat interface using Streamlit. The goal is to create a ChatGPT-like experience where engineers can ask questions naturally and receive design assistance, cost optimization advice, and visualizations.

**Key Decisions:**
- **Framework:** Streamlit (pure Python, already in use)
- **LLM Provider:** OpenAI GPT-4 (or compatible: Anthropic, local LLaMA)
- **Tool Calling:** OpenAI function calling API
- **UI Pattern:** 40% chat (left) + 60% workspace (right)

---

## 1. UI Layout Design

### ChatGPT-Inspired Split Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ StructEng AI Assistant                                     [Settings]│
├──────────────────────┬───────────────────────────────────────────────┤
│                      │                                               │
│  💬 CHAT (40%)       │  📊 WORKSPACE (60%)                          │
│                      │                                               │
│  ┌────────────────┐  │  ┌─────────────────────────────────────────┐ │
│  │ 🧑 User        │  │  │  📋 Design Summary                      │ │
│  │ Design a beam  │  │  │                                         │ │
│  │ for 150 kN·m   │  │  │  Beam: 300×500mm                        │ │
│  └────────────────┘  │  │  Steel: 4×20mm (1257 mm²)               │ │
│                      │  │  Utilization: 78%                       │ │
│  ┌────────────────┐  │  │  Status: ✅ SAFE                         │ │
│  │ 🤖 Assistant   │  │  └─────────────────────────────────────────┘ │
│  │ I've designed  │  │                                               │
│  │ an optimal beam│  │  ┌─────────────────────────────────────────┐ │
│  │ Here are 3     │  │  │  💰 Cost Analysis                       │ │
│  │ alternatives...│  │  │  Current: ₹4,200/m                       │ │
│  └────────────────┘  │  │  Optimal: ₹3,800/m                       │ │
│                      │  │  Savings: 9.5%                           │ │
│  ┌────────────────┐  │  └─────────────────────────────────────────┘ │
│  │ 🧑 User        │  │                                               │
│  │ Can we reduce  │  │  ┌─────────────────────────────────────────┐ │
│  │ cost more?     │  │  │  🎨 3D Preview                          │ │
│  └────────────────┘  │  │  [Interactive Plotly 3D visualization]  │ │
│                      │  │                                         │ │
│  ┌────────────────┐  │  │                                         │ │
│  │ 🤖 Assistant   │  │  │                                         │ │
│  │ Yes! Here are  │  │  │                                         │ │
│  │ 3 ways to save │  │  └─────────────────────────────────────────┘ │
│  │ money...       │  │                                               │
│  └────────────────┘  │                                               │
│                      │                                               │
│  [📝 Type message]   │  [📊 Results] [🎨 3D] [💰 Cost] [📋 Details] │
│                      │                                               │
└──────────────────────┴───────────────────────────────────────────────┘
```

### Workspace Tabs

The right panel dynamically shows content based on conversation:

| Tab | Content | Triggers |
|-----|---------|----------|
| **Results** | Design summary, utilization, status | Any design action |
| **3D** | Interactive 3D beam visualization | "show 3D", "visualize" |
| **Cost** | Cost breakdown, optimization options | "cost", "cheaper", "optimize" |
| **Details** | Full technical data, detailing | "details", "rebar", "stirrups" |
| **Compare** | Side-by-side design comparison | "compare", "alternatives" |

---

## 2. LLM Tool Functions

### Core Design Tools

These are the functions the LLM can call to interact with our library:

```python
STRUCTURAL_TOOLS = [
    {
        "type": "function",
        "name": "design_beam",
        "description": "Design a reinforced concrete beam for given moment and shear. Returns section size, reinforcement, and status.",
        "parameters": {
            "type": "object",
            "properties": {
                "moment_knm": {
                    "type": "number",
                    "description": "Design moment in kN·m"
                },
                "shear_kn": {
                    "type": "number",
                    "description": "Design shear in kN"
                },
                "span_m": {
                    "type": "number",
                    "description": "Beam span in meters (default: 5.0)"
                },
                "width_mm": {
                    "type": "number",
                    "description": "Beam width in mm (optional, will optimize if not provided)"
                },
                "depth_mm": {
                    "type": "number",
                    "description": "Beam depth in mm (optional, will optimize if not provided)"
                },
                "concrete_grade": {
                    "type": "string",
                    "enum": ["M20", "M25", "M30", "M35", "M40"],
                    "description": "Concrete grade (default: M25)"
                },
                "steel_grade": {
                    "type": "string",
                    "enum": ["Fe415", "Fe500", "Fe550"],
                    "description": "Steel grade (default: Fe500)"
                }
            },
            "required": ["moment_knm", "shear_kn"]
        }
    },
    {
        "type": "function",
        "name": "optimize_cost",
        "description": "Find the most cost-effective beam design for given loads. Returns optimal dimensions and cost savings.",
        "parameters": {
            "type": "object",
            "properties": {
                "moment_knm": {"type": "number"},
                "shear_kn": {"type": "number"},
                "span_m": {"type": "number"},
                "max_depth_mm": {"type": "number", "description": "Maximum allowed depth"},
                "min_width_mm": {"type": "number", "description": "Minimum width"}
            },
            "required": ["moment_knm", "shear_kn", "span_m"]
        }
    },
    {
        "type": "function",
        "name": "get_suggestions",
        "description": "Get design improvement suggestions for an existing beam. Returns prioritized recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "beam_id": {"type": "string", "description": "Reference to current beam design"},
                "focus": {
                    "type": "string",
                    "enum": ["cost", "safety", "constructability", "all"],
                    "description": "Focus area for suggestions"
                }
            },
            "required": []
        }
    },
    {
        "type": "function",
        "name": "analyze_design",
        "description": "Perform comprehensive smart analysis including cost, sensitivity, and constructability.",
        "parameters": {
            "type": "object",
            "properties": {
                "beam_id": {"type": "string"},
                "include_cost": {"type": "boolean", "default": True},
                "include_sensitivity": {"type": "boolean", "default": True}
            }
        }
    },
    {
        "type": "function",
        "name": "compare_options",
        "description": "Compare multiple beam design alternatives side by side.",
        "parameters": {
            "type": "object",
            "properties": {
                "alternatives": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "width_mm": {"type": "number"},
                            "depth_mm": {"type": "number"},
                            "concrete_grade": {"type": "string"}
                        }
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "name": "explain_code_clause",
        "description": "Explain a specific IS 456 code clause in simple terms.",
        "parameters": {
            "type": "object",
            "properties": {
                "clause_number": {"type": "string", "description": "e.g., '26.5.1.1'"},
                "topic": {"type": "string", "description": "e.g., 'minimum reinforcement'"}
            }
        }
    },
    {
        "type": "function",
        "name": "show_3d_view",
        "description": "Generate and display 3D visualization of the beam.",
        "parameters": {
            "type": "object",
            "properties": {
                "beam_id": {"type": "string"},
                "show_rebar": {"type": "boolean", "default": True},
                "show_stirrups": {"type": "boolean", "default": True}
            }
        }
    }
]
```

---

## 3. System Prompt

```markdown
You are StructEng AI, an expert structural engineering assistant specializing in
IS 456 reinforced concrete design. You help engineers design beams, optimize costs,
and understand code requirements.

## Your Capabilities:
- Design RC beams for moment and shear (IS 456:2000)
- Optimize designs for cost, safety, or constructability
- Explain code clauses in simple terms
- Generate 3D visualizations
- Compare design alternatives

## Guidelines:
1. **Be practical**: Engineers want actionable advice, not theory.
2. **Be specific**: Always include numbers (dimensions, costs, percentages).
3. **Use tools**: Call functions to get accurate calculations. Never guess.
4. **Show results**: After design, display results in the workspace panel.
5. **Explain trade-offs**: Cost vs safety, depth vs width, etc.
6. **Follow IS 456**: All designs must comply with IS 456:2000.

## Response Format:
- Start with a brief answer
- Call tools to perform calculations
- Present results clearly with key metrics
- Offer follow-up options ("Would you like me to optimize for cost?")

## Important:
- Never fabricate structural calculations
- If uncertain, say so and suggest verification
- Always prioritize safety over economy
- Be concise but thorough
```

---

## 4. Implementation Plan

### Phase 1: Basic Chat UI (This Session)

```python
# streamlit_app/pages/10_🤖_ai_assistant.py

import streamlit as st
from openai import OpenAI

st.set_page_config(layout="wide")

# Split layout: 40% chat, 60% workspace
chat_col, workspace_col = st.columns([0.4, 0.6])

with chat_col:
    st.header("💬 Chat")

    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask about beam design..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Process with LLM...

with workspace_col:
    st.header("📊 Workspace")

    # Tabs for different views
    tabs = st.tabs(["Results", "3D View", "Cost", "Details"])

    with tabs[0]:  # Results
        if "current_design" in st.session_state:
            display_design_summary(st.session_state.current_design)

    with tabs[1]:  # 3D
        if "current_design" in st.session_state:
            render_3d_view(st.session_state.current_design)
```

### Phase 2: Tool Calling Integration

```python
def process_with_tools(user_message: str, history: list) -> tuple[str, dict]:
    """Process user message with OpenAI tool calling."""

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Add system prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_message}
    ]

    # First call - may request tool use
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=STRUCTURAL_TOOLS,
        tool_choice="auto"
    )

    # Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            result = execute_tool(tool_call.function.name, tool_call.function.arguments)
            # Add result to context and get final response...

    return response.choices[0].message.content, workspace_updates
```

### Phase 3: Library Integration

Map LLM tool calls to actual library functions:

```python
def execute_tool(name: str, arguments: str) -> dict:
    """Execute structural engineering tool and return results."""

    import json
    from structural_lib import api

    args = json.loads(arguments)

    if name == "design_beam":
        result = api.design_beam_is456(
            units="IS456",
            b_mm=args.get("width_mm", 300),
            D_mm=args.get("depth_mm", 500),
            d_mm=args.get("depth_mm", 500) - 50,
            fck_nmm2=_grade_to_fck(args.get("concrete_grade", "M25")),
            fy_nmm2=_grade_to_fy(args.get("steel_grade", "Fe500")),
            mu_knm=args["moment_knm"],
            vu_kn=args["shear_kn"]
        )

        return {
            "status": "safe" if result.is_ok else "unsafe",
            "section": f"{result.geometry.b_mm}×{result.geometry.D_mm}mm",
            "steel_area_mm2": result.flexure.ast_required_mm2,
            "utilization": result.governing_utilization,
            "full_result": result  # For workspace display
        }

    elif name == "optimize_cost":
        result = api.optimize_beam_cost(
            span_mm=args["span_m"] * 1000,
            mu_knm=args["moment_knm"],
            vu_kn=args["shear_kn"]
        )
        return {
            "optimal_section": result.optimal_candidate,
            "savings_percent": result.savings_percent,
            "alternatives": result.candidates[:5]
        }

    elif name == "analyze_design":
        from structural_lib.insights import SmartDesigner
        dashboard = SmartDesigner.analyze(
            design=st.session_state.current_design,
            span_mm=args.get("span_mm", 5000),
            mu_knm=args.get("mu_knm", 100),
            vu_kn=args.get("vu_kn", 50)
        )
        return dashboard.to_dict()

    # ... other tools
```

---

## 5. Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **UI Framework** | Streamlit | Already using, Python-native, fast iteration |
| **Chat Elements** | `st.chat_message`, `st.chat_input` | Native Streamlit, good UX |
| **LLM Provider** | OpenAI GPT-4 | Best tool calling, reliable |
| **Fallback LLM** | Anthropic Claude | Better reasoning, alternative |
| **3D Rendering** | Plotly.js | Already integrated, works well |
| **Session State** | `st.session_state` | Built-in, handles chat history |

### Environment Variables

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
ANTHROPIC_API_KEY = "sk-ant-..."  # Optional fallback
```

---

## 6. Example Conversations

### Example 1: Basic Design

```
User: Design a beam for 150 kN·m moment and 80 kN shear