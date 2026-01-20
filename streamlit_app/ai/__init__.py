"""
AI Assistant Module

Provides context-aware AI assistant capabilities for the StructEng app.
"""

from streamlit_app.ai.context import (
    build_messages,
    generate_workspace_context,
    load_system_prompt,
)
from streamlit_app.ai.tools import TOOLS, get_tool_names, get_tools

__all__ = [
    "TOOLS",
    "build_messages",
    "generate_workspace_context",
    "get_tool_names",
    "get_tools",
    "load_system_prompt",
]
