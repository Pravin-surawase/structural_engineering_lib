"""
AI Assistant Tools & Function Calling

This module defines the tool schemas and handlers for the AI assistant
to interact with the structural engineering workspace.
"""

from typing import Any

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
                        "description": "Beam identifier (e.g., 'B1_Ground')"
                    },
                    "b_mm": {
                        "type": "number",
                        "description": "Beam width in mm"
                    },
                    "D_mm": {
                        "type": "number",
                        "description": "Overall depth in mm"
                    },
                    "d_mm": {
                        "type": "number",
                        "description": "Effective depth in mm (default: D - 50)"
                    },
                    "span_mm": {
                        "type": "number",
                        "description": "Clear span in mm"
                    },
                    "mu_knm": {
                        "type": "number",
                        "description": "Factored moment in kN·m"
                    },
                    "vu_kn": {
                        "type": "number",
                        "description": "Factored shear in kN"
                    },
                    "fck": {
                        "type": "number",
                        "description": "Concrete grade in N/mm² (default: 25)"
                    },
                    "fy": {
                        "type": "number",
                        "description": "Steel grade in N/mm² (default: 500)"
                    }
                },
                "required": ["b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn"],
                "additionalProperties": False
            },
            "strict": True
        }
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
                "additionalProperties": False
            },
            "strict": True
        }
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
                        "description": "Beam identifier to query"
                    }
                },
                "required": ["beam_id"],
                "additionalProperties": False
            },
            "strict": True
        }
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
                        "description": "Beam identifier to select"
                    }
                },
                "required": ["beam_id"],
                "additionalProperties": False
            },
            "strict": True
        }
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
                        "description": "Type of visualization to display"
                    }
                },
                "required": ["view_type"],
                "additionalProperties": False
            },
            "strict": True
        }
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
                        "description": "Beam identifier to optimize"
                    },
                    "target": {
                        "type": "string",
                        "enum": ["cost", "weight", "constructability"],
                        "description": "Optimization target (default: cost)"
                    }
                },
                "required": ["beam_id"],
                "additionalProperties": False
            },
            "strict": True
        }
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
                        "description": "Export file format"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Custom filename (auto-generated if not specified)"
                    }
                },
                "required": ["format"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]


def get_tools() -> list[dict]:
    """Return the list of available tools for function calling."""
    return TOOLS


def get_tool_names() -> list[str]:
    """Return list of tool names."""
    return [t["function"]["name"] for t in TOOLS]
