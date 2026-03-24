# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Workspace Package — Split from ai_workspace.py (TASK-508).

Modules:
    workspace_state  — WorkspaceState enum, session state init, constants
    import_handler   — CSV/Excel import, auto-mapping, adapter integration
    design_handler   — Rebar layout calculation, single/batch beam design
    rebar_handler    — Constructability scoring, optimal rebar, beam line optimization
    export_handler   — HTML/PDF/DXF reports, material takeoff
    ui_renderers     — All render_* functions + render_dynamic_workspace dispatcher
"""

from .workspace_state import (
    WorkspaceState,
    BAR_OPTIONS,
    STIRRUP_OPTIONS,
    COLUMN_PATTERNS,
    SAMPLE_ETABS_DATA,
    init_workspace_state,
    set_workspace_state,
    get_workspace_state,
)
from .import_handler import (
    auto_map_columns,
    standardize_dataframe,
    load_sample_data,
    detect_format_from_content,
    process_with_adapters,
    beams_to_dataframe,
    process_uploaded_file,
    process_multi_files,
    ADAPTERS,
    ADAPTERS_AVAILABLE,
)
from .design_handler import (
    calculate_rebar_layout,
    design_beam_row,
    design_all_beams_ws,
    CACHED_DESIGN_AVAILABLE,
)
from .rebar_handler import (
    calculate_constructability_score,
    suggest_optimal_rebar,
    optimize_beam_line,
    calculate_rebar_checks,
)
from .export_handler import (
    _generate_and_download_report,
    _generate_and_download_pdf_report,
    _generate_and_download_dxf,
    calculate_material_takeoff,
)
from .ui_renderers import (
    render_welcome_panel,
    render_import_preview,
    render_design_results,
    render_building_3d,
    render_rebar_editor,
    render_cross_section,
    render_3d_view,
    render_beam_editor,
    render_dashboard,
    render_unified_editor,
    render_dynamic_workspace,
    create_building_3d_figure,
    create_cross_section_figure,
)

__all__ = [
    # State
    "WorkspaceState",
    "init_workspace_state",
    "set_workspace_state",
    "get_workspace_state",
    # Constants
    "BAR_OPTIONS",
    "STIRRUP_OPTIONS",
    "COLUMN_PATTERNS",
    "SAMPLE_ETABS_DATA",
    # Import
    "auto_map_columns",
    "standardize_dataframe",
    "load_sample_data",
    "detect_format_from_content",
    "process_with_adapters",
    "beams_to_dataframe",
    "process_uploaded_file",
    "process_multi_files",
    "ADAPTERS",
    "ADAPTERS_AVAILABLE",
    # Design
    "calculate_rebar_layout",
    "design_beam_row",
    "design_all_beams_ws",
    "CACHED_DESIGN_AVAILABLE",
    # Rebar
    "calculate_constructability_score",
    "suggest_optimal_rebar",
    "optimize_beam_line",
    "calculate_rebar_checks",
    # Export
    "_generate_and_download_report",
    "_generate_and_download_pdf_report",
    "_generate_and_download_dxf",
    "calculate_material_takeoff",
    # UI Renderers
    "render_welcome_panel",
    "render_import_preview",
    "render_design_results",
    "render_building_3d",
    "render_rebar_editor",
    "render_cross_section",
    "render_3d_view",
    "render_beam_editor",
    "render_dashboard",
    "render_unified_editor",
    "render_dynamic_workspace",
    "create_building_3d_figure",
    "create_cross_section_figure",
]
