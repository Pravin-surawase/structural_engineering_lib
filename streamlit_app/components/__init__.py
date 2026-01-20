"""
Component Library
=================

Reusable UI components for the Streamlit dashboard.

This module provides:
- Input widgets (dimension_input, material_selector, load_input)
- Result displays (display_flexure, display_shear, display_summary)
- Layout helpers (sidebar_inputs, result_tabs)
- AI workspace (dynamic workspace for AI assistant v2)

All components follow:
- IS 456 theme (navy #003366, orange #FF6600)
- WCAG 2.1 Level AA accessibility
- Consistent styling and validation
- Reusable across pages

Author: STREAMLIT UI SPECIALIST (Agent 6)
Phase: Implementation (STREAMLIT-IMPL-002)
"""

# Preview component (Phase 3 UI Layout)
from .preview import (
    render_real_time_preview,
    create_beam_preview_diagram,
    calculate_quick_checks,
    render_status_dashboard,
    calculate_rough_cost,
    render_cost_summary,
)

# Report export component (TASK-276-279 Integration)
from .report_export import (
    show_export_options,
    show_audit_trail_summary,
)

# AI Workspace component (Session 52 - AI v2)
from .ai_workspace import (
    WorkspaceState,
    init_workspace_state,
    set_workspace_state,
    get_workspace_state,
    load_sample_data,
    design_all_beams_ws,
    render_dynamic_workspace,
)

# This file will be populated in STREAMLIT-IMPL-002
