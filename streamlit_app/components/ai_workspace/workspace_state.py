# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Workspace state management and constants.

Extracted from ai_workspace.py (TASK-508).
Contains the WorkspaceState enum, session state initialization,
constants (BAR_OPTIONS, STIRRUP_OPTIONS, COLUMN_PATTERNS, SAMPLE_ETABS_DATA).
"""

from __future__ import annotations

from enum import Enum

import streamlit as st

# Import shared utilities (Session 63 consolidation)
try:
    from utils.rebar_layout import BAR_OPTIONS

    SHARED_REBAR_AVAILABLE = True
except ImportError:
    SHARED_REBAR_AVAILABLE = False
    # Fallback BAR_OPTIONS if import fails
    BAR_OPTIONS = [
        (10, 78.5),
        (12, 113.1),
        (16, 201.1),
        (20, 314.2),
        (25, 490.9),
        (32, 804.2),
    ]


class WorkspaceState(Enum):
    """Workspace state machine states."""

    WELCOME = "welcome"
    IMPORT = "import"
    DESIGN = "design"
    BUILDING_3D = "building_3d"  # Full building view
    VIEW_3D = "view_3d"  # Single beam detail
    CROSS_SECTION = "cross_section"  # Beautiful cross-section view
    REBAR_EDIT = "rebar_edit"  # Interactive reinforcement editor
    UNIFIED_EDITOR = "unified_editor"  # Full-width unified editor mode
    EDIT = "edit"
    DASHBOARD = "dashboard"


# Stirrup options
STIRRUP_OPTIONS = [(6, 28.3), (8, 50.3), (10, 78.5)]


# Sample ETABS-like data for quick start - with proper 3D building coordinates
SAMPLE_ETABS_DATA = """Unique Name,Width,Depth,Length,M3,V2,Story,X1,Y1,Z1,X2,Y2,Z2
B1-G1,300,500,6000,120.5,45.2,Story1,0,0,3,6,0,3
B2-G1,300,500,6000,135.3,48.1,Story1,6,0,3,12,0,3
B3-G1,300,500,5000,110.7,42.3,Story1,0,6,3,5,6,3
B4-G1,350,600,5000,145.2,55.4,Story1,5,6,3,10,6,3
B1-G2,300,500,6000,155.6,58.9,Story2,0,0,6,6,0,6
B2-G2,300,500,6000,165.3,62.1,Story2,6,0,6,12,0,6
B3-G2,300,550,5000,140.8,52.7,Story2,0,6,6,5,6,6
B4-G2,350,600,5000,175.2,65.4,Story2,5,6,6,10,6,6
B1-G3,350,650,6000,195.6,72.2,Story3,0,0,9,6,0,9
B2-G3,350,650,6000,210.3,78.1,Story3,6,0,9,12,0,9
"""

# Column name patterns for auto-mapping
COLUMN_PATTERNS = {
    "beam_id": ["unique name", "beam", "element", "name", "id", "label"],
    "b_mm": ["width", "b", "b_mm", "breadth", "b (mm)"],
    "D_mm": ["depth", "d", "D_mm", "D", "height", "h", "d (mm)"],
    "span_mm": ["length", "span", "L", "l_mm", "span_mm"],
    "mu_knm": ["moment", "m3", "mu", "m_max", "bending", "mu_knm"],
    "vu_kn": ["shear", "v2", "vu", "v_max", "vu_kn"],
    "story": ["story", "floor", "level"],
    "fck": ["fck", "concrete", "fc", "grade"],
    "fy": ["fy", "steel", "rebar"],
    "x1": ["x1", "start_x", "xi"],
    "y1": ["y1", "start_y", "yi"],
    "z1": ["z1", "start_z", "zi", "elev1"],
    "x2": ["x2", "end_x", "xj"],
    "y2": ["y2", "end_y", "yj"],
    "z2": ["z2", "end_z", "zj", "elev2"],
}


def init_workspace_state() -> None:
    """Initialize workspace session state."""
    if "ws_state" not in st.session_state:
        st.session_state.ws_state = WorkspaceState.WELCOME

    if "ws_beams_df" not in st.session_state:
        st.session_state.ws_beams_df = None

    if "ws_design_results" not in st.session_state:
        st.session_state.ws_design_results = None

    if "ws_selected_beam" not in st.session_state:
        st.session_state.ws_selected_beam = None

    # Rebar editor state
    if "ws_rebar_config" not in st.session_state:
        st.session_state.ws_rebar_config = None

    if "ws_defaults" not in st.session_state:
        st.session_state.ws_defaults = {
            "fck": 25.0,
            "fy": 500.0,
            "cover_mm": 40.0,
        }

    # Unified editor mode state
    if "ws_editor_mode" not in st.session_state:
        st.session_state.ws_editor_mode = {
            "active": False,
            "current_beam_idx": 0,
            "beam_queue": [],
            "filter_mode": "all",  # "all", "failed", "story", "beam_line"
            "undo_stack": [],
            "redo_stack": [],
        }


def set_workspace_state(new_state: WorkspaceState) -> None:
    """Change workspace state and trigger rerun."""
    st.session_state.ws_state = new_state


def get_workspace_state() -> WorkspaceState:
    """Get current workspace state."""
    init_workspace_state()  # Ensure state is initialized
    return st.session_state.ws_state
