"""
AI Assistant Tools & Function Calling

This module defines the tool schemas and handlers for the AI assistant
to interact with the structural engineering workspace.
"""


# Tool definitions for OpenAI/OpenRouter function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "design_beam",
            "description": "Design a single RC beam per IS 456:2000. Returns required steel area, shear reinforcement, and pass/fail status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beam_id": {
                        "type": "string",
                        "description": "Beam identifier (e.g., 'B1_Ground')",
                    },
                    "b_mm": {"type": "number", "description": "Beam width in mm"},
                    "D_mm": {"type": "number", "description": "Overall depth in mm"},
                    "span_mm": {"type": "number", "description": "Clear span in mm"},
                    "mu_knm": {
                        "type": "number",
                        "description": "Factored moment in kN·m",
                    },
                    "vu_kn": {"type": "number", "description": "Factored shear in kN"},
                    "fck": {
                        "type": "number",
                        "description": "Concrete grade in N/mm² (default: 25)",
                    },
                    "fy": {
                        "type": "number",
                        "description": "Steel grade in N/mm² (default: 500)",
                    },
                },
                "required": ["b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "design_all_beams",
            "description": "Design all beams currently loaded in the workspace. Returns summary of pass/fail results.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_beam_details",
            "description": "Get detailed design results for a specific beam including flexure, shear, and detailing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beam_id": {
                        "type": "string",
                        "description": "Beam identifier to query",
                    }
                },
                "required": ["beam_id"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "select_beam",
            "description": "Select a beam for detailed viewing in the 3D visualizer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beam_id": {
                        "type": "string",
                        "description": "Beam identifier to select",
                    }
                },
                "required": ["beam_id"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_visualization",
            "description": "Trigger a visualization in the workspace: 3D view, cross-section, building view, or dashboard.",
            "parameters": {
                "type": "object",
                "properties": {
                    "view_type": {
                        "type": "string",
                        "enum": ["3d", "cross_section", "building", "dashboard"],
                        "description": "Type of visualization to display",
                    }
                },
                "required": ["view_type"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_3d_view",
            "description": "Filter the 3D building view to show only a specific floor/story. Use this when user asks to 'show floor 2' or 'filter to story 1'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "floor": {
                        "type": "string",
                        "description": "Floor/story name to filter (e.g., 'Floor 2', 'Story1', 'Level 0'). Use 'all' to show entire building.",
                    },
                    "show_rebar": {
                        "type": "boolean",
                        "description": "Whether to show reinforcement (default: true)",
                    },
                },
                "required": ["floor"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_critical_beams",
            "description": "Get list of most critical beams by moment, shear, or utilization. Use this for 'list top 3 critical beams' requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "criterion": {
                        "type": "string",
                        "enum": ["moment", "shear", "utilization"],
                        "description": "Criterion for ranking beams (default: moment)",
                    },
                    "count": {
                        "type": "number",
                        "description": "Number of beams to return (default: 3)",
                    },
                    "floor": {
                        "type": "string",
                        "description": "Optional floor/story filter",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_optimization",
            "description": "Start cost/weight optimization for beams. Automatically finds the most critical beam if not specified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "floor": {
                        "type": "string",
                        "description": "Floor/story to optimize beams on (e.g., 'Level 0', 'Story1')",
                    },
                    "beam_id": {
                        "type": "string",
                        "description": "Specific beam ID to optimize",
                    },
                    "target": {
                        "type": "string",
                        "enum": ["cost", "weight", "constructability"],
                        "description": "Optimization target (default: cost)",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_optimization",
            "description": "Get optimization suggestions for a beam design to reduce cost, weight, or improve constructability.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beam_id": {
                        "type": "string",
                        "description": "Beam identifier to optimize",
                    },
                    "target": {
                        "type": "string",
                        "enum": ["cost", "weight", "constructability"],
                        "description": "Optimization target (default: cost)",
                    },
                },
                "required": ["beam_id"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_results",
            "description": "Export design results to a file format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["csv", "json", "excel"],
                        "description": "Export file format",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Custom filename (auto-generated if not specified)",
                    },
                },
                "required": ["format"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "export_dxf",
            "description": "Generate CAD DXF drawing for beam(s) with cross-section, reinforcement layout, and schedule table. Can export single beam or batch of beams.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beam_id": {
                        "type": "string",
                        "description": "Single beam ID to export (e.g., 'B1', 'B101'). If not specified, exports all designed beams.",
                    },
                    "floor": {
                        "type": "string",
                        "description": "Export all beams on a specific floor/story (e.g., 'Level 0', 'Story1')",
                    },
                    "include_schedule": {
                        "type": "boolean",
                        "description": "Include beam schedule table in DXF (default: true)",
                    },
                    "include_title_block": {
                        "type": "boolean",
                        "description": "Include standard title block (default: true)",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "Generate design calculation report for beam(s). Creates HTML report with design checks, reinforcement details, and IS 456 code compliance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "beam_id": {
                        "type": "string",
                        "description": "Single beam ID for report (e.g., 'B1'). If not specified, generates summary report for all beams.",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["html", "json"],
                        "description": "Report format (default: html)",
                    },
                    "include_bbs": {
                        "type": "boolean",
                        "description": "Include Bar Bending Schedule in report (default: true)",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]


def get_tools() -> list[dict]:
    """Return the list of available tools for function calling."""
    return TOOLS


def get_tool_names() -> list[str]:
    """Return list of tool names."""
    return [t["function"]["name"] for t in TOOLS]
