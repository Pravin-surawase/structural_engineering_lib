# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
LLM Tool Definitions for StructEng AI Assistant.

Defines the tools available to the LLM for structural engineering operations.
Compatible with OpenAI function calling API format.
"""

from __future__ import annotations

from typing import Any, Callable

# Tool definitions in OpenAI function calling format
STRUCTENG_TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "design_beam",
            "description": "Design a reinforced concrete beam per IS 456:2000. Calculates required steel area, checks safety, and provides complete design output.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "b_mm": {
                        "type": "number",
                        "description": "Beam width in mm (150-600)",
                    },
                    "D_mm": {
                        "type": "number",
                        "description": "Beam depth in mm (200-900)",
                    },
                    "fck": {
                        "type": "number",
                        "enum": [20, 25, 30, 35, 40],
                        "description": "Concrete grade (M20-M40)",
                    },
                    "fy": {
                        "type": "number",
                        "enum": [415, 500, 550],
                        "description": "Steel grade (Fe415, Fe500, Fe550)",
                    },
                    "mu_knm": {
                        "type": "number",
                        "description": "Design moment in kN·m",
                    },
                    "vu_kn": {
                        "type": "number",
                        "description": "Design shear force in kN",
                    },
                    "span_m": {
                        "type": "number",
                        "description": "Beam span in meters",
                    },
                },
                "required": ["mu_knm"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "optimize_cost",
            "description": "Optimize beam design for minimum cost. Finds the most economical section that satisfies all code requirements.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "mu_knm": {
                        "type": "number",
                        "description": "Design moment in kN·m",
                    },
                    "vu_kn": {
                        "type": "number",
                        "description": "Design shear force in kN",
                    },
                    "b_min_mm": {
                        "type": "number",
                        "description": "Minimum width constraint in mm",
                    },
                    "b_max_mm": {
                        "type": "number",
                        "description": "Maximum width constraint in mm",
                    },
                    "D_min_mm": {
                        "type": "number",
                        "description": "Minimum depth constraint in mm",
                    },
                    "D_max_mm": {
                        "type": "number",
                        "description": "Maximum depth constraint in mm",
                    },
                },
                "required": ["mu_knm"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_suggestions",
            "description": "Get improvement suggestions for an existing beam design. Returns ranked recommendations to improve safety, cost, or constructability.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "enum": ["cost", "safety", "constructability", "all"],
                        "description": "Focus area for suggestions",
                    },
                    "max_suggestions": {
                        "type": "integer",
                        "description": "Maximum number of suggestions to return (1-10)",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_design",
            "description": "Run comprehensive SmartDesigner analysis. Returns overall score, key issues, quick wins, and detailed metrics.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "include_cost": {
                        "type": "boolean",
                        "description": "Include cost analysis",
                    },
                    "include_constructability": {
                        "type": "boolean",
                        "description": "Include constructability assessment",
                    },
                    "include_sensitivity": {
                        "type": "boolean",
                        "description": "Include sensitivity analysis",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_options",
            "description": "Compare multiple beam design options. Useful for evaluating different section sizes or material grades.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "options": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "b_mm": {"type": "number"},
                                "D_mm": {"type": "number"},
                                "fck": {"type": "number"},
                            },
                            "required": ["name", "b_mm", "D_mm"],
                        },
                        "description": "List of design options to compare",
                    },
                },
                "required": ["options"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_code_clause",
            "description": "Explain an IS 456 code clause in simple terms. Helps engineers understand specific requirements.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "clause": {
                        "type": "string",
                        "description": "Clause number or topic (e.g., '26.5.1.1' or 'minimum steel')",
                    },
                },
                "required": ["clause"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_3d_view",
            "description": "Switch the workspace to show 3D visualization of the current beam design.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "show_reinforcement": {
                        "type": "boolean",
                        "description": "Show reinforcement bars in the visualization",
                    },
                    "show_dimensions": {
                        "type": "boolean",
                        "description": "Show dimension annotations",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
]


def get_tool_names() -> list[str]:
    """Get list of available tool names."""
    return [tool["function"]["name"] for tool in STRUCTENG_TOOLS]


def get_tool_by_name(name: str) -> dict[str, Any] | None:
    """Get tool definition by name."""
    for tool in STRUCTENG_TOOLS:
        if tool["function"]["name"] == name:
            return tool
    return None


def get_tool_description(name: str) -> str | None:
    """Get tool description by name."""
    tool = get_tool_by_name(name)
    if tool:
        return tool["function"].get("description")
    return None


# Tool handlers - map tool names to execution functions
def create_tool_handler(
    design_fn: Callable[..., Any],
    optimize_fn: Callable[..., Any],
    suggestions_fn: Callable[..., Any],
    analyze_fn: Callable[..., Any],
) -> dict[str, Callable[..., Any]]:
    """
    Create a tool handler mapping.

    Args:
        design_fn: Function to design a beam
        optimize_fn: Function to optimize cost
        suggestions_fn: Function to get suggestions
        analyze_fn: Function to analyze design

    Returns:
        Dict mapping tool names to handler functions
    """
    return {
        "design_beam": design_fn,
        "optimize_cost": optimize_fn,
        "get_suggestions": suggestions_fn,
        "analyze_design": analyze_fn,
        "compare_options": lambda **kwargs: {"message": "Compare coming soon"},
        "explain_code_clause": lambda **kwargs: {
            "message": f"Explanation for {kwargs.get('clause', 'clause')}"
        },
        "show_3d_view": lambda **kwargs: {"action": "switch_to_3d_tab"},
    }


# System prompt with tool context
SYSTEM_PROMPT_WITH_TOOLS = """You are StructEng AI, an expert structural engineering assistant specializing in
IS 456 reinforced concrete design. You have access to powerful tools for beam design and analysis.

## Available Tools:
1. **design_beam** - Design a beam for given moment/shear
2. **optimize_cost** - Find the most economical section
3. **get_suggestions** - Get improvement recommendations
4. **analyze_design** - Run comprehensive SmartDesigner analysis
5. **compare_options** - Compare multiple design alternatives
6. **explain_code_clause** - Explain IS 456 clauses
7. **show_3d_view** - Display 3D visualization

## Guidelines:
1. **Use tools proactively**: If someone asks for a design, use design_beam immediately.
2. **Combine tools**: For optimization, use design_beam then get_suggestions.
3. **Present results clearly**: Format tool outputs with markdown tables and metrics.
4. **Suggest follow-ups**: After each result, offer related actions.

## Response Flow:
1. Understand the user's intent
2. Call appropriate tool(s)
3. Format results clearly with key metrics
4. Suggest next steps

## Important:
- All calculations follow IS 456:2000
- Never fabricate structural data
- If uncertain, say so and recommend verification
- Always prioritize safety over economy
"""


def format_tool_result_for_display(
    tool_name: str,
    result: dict[str, Any],
) -> str:
    """
    Format tool result for display to user.

    Args:
        tool_name: Name of the tool that was called
        result: Result from tool execution

    Returns:
        Formatted markdown string
    """
    if tool_name == "design_beam":
        if result.get("success"):
            return f"""**Design Complete** ✅

| Metric | Value |
|--------|-------|
| Section | {result.get("section", "N/A")} |
| Steel Required | {result.get("ast_mm2", 0):.0f} mm² |
| Utilization | {result.get("utilization", 0):.1%} |
| Status | {"SAFE" if result.get("is_safe") else "UNSAFE"} |
"""
        else:
            return f"**Design Failed** ❌\n\n{result.get('error', 'Unknown error')}"

    elif tool_name == "analyze_design":
        if result.get("success"):
            dashboard = result.get("dashboard")
            if dashboard:
                s = dashboard.summary
                return f"""**SmartDesigner Analysis** 📊

**Overall Score: {s.overall_score:.1%}**

| Metric | Score |
|--------|-------|
| Safety | {s.safety_score:.1%} |
| Cost Efficiency | {s.cost_efficiency:.1%} |
| Constructability | {s.constructability:.1%} |

**Status:** {s.design_status}
"""
        return "Analysis not available."

    elif tool_name == "show_3d_view":
        return "Switched to 3D view. 👉 See the workspace panel."

    else:
        return f"Tool `{tool_name}` executed successfully."
