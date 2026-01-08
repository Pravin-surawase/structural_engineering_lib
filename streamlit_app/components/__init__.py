"""
Component Library
=================

Reusable UI components for the Streamlit dashboard.

This module provides:
- Input widgets (dimension_input, material_selector, load_input)
- Result displays (display_flexure, display_shear, display_summary)
- Layout helpers (sidebar_inputs, result_tabs)

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
    render_cost_summary
)

# This file will be populated in STREAMLIT-IMPL-002
