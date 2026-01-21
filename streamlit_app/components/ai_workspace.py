# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
AI Workspace Component - Dynamic State-Based Workspace

This module provides a unified workspace that transitions based on workflow state:
- WELCOME: Quick start cards for getting started
- IMPORT: Auto-mapped preview after file upload
- DESIGN: Interactive results table with beam selection
- BUILDING_3D: Full building 3D visualization with all beams
- VIEW_3D: Selected beam with rebar visualization
- REBAR_EDIT: Interactive reinforcement editor with real-time checks
- EDIT: Single beam editor with live preview
- DASHBOARD: SmartDesigner insights

Architecture:
    User Action → State Transition → Workspace Re-render

Usage:
    from components.ai_workspace import (
        WorkspaceState,
        init_workspace_state,
        render_dynamic_workspace,
    )

    init_workspace_state()
    render_dynamic_workspace()
"""

from __future__ import annotations

import io
import math
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Try to import visualization components
try:
    from components.visualizations_3d import create_beam_3d_figure

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Import adapter system (reusing proven infrastructure from multi-format import)
try:
    from structural_lib.adapters import (
        ETABSAdapter,
        SAFEAdapter,
        GenericCSVAdapter,
    )
    from structural_lib.models import (
        BeamGeometry,
        BeamForces,
        DesignDefaults,
    )

    ADAPTERS_AVAILABLE = True
    ADAPTERS = {
        "ETABS": ETABSAdapter(),
        "SAFE": SAFEAdapter(),
        "Generic": GenericCSVAdapter(),
    }
except ImportError:
    ADAPTERS_AVAILABLE = False
    ADAPTERS = {}

# Import cached design from api_wrapper (used by multi-format import)
try:
    from utils.api_wrapper import cached_design

    CACHED_DESIGN_AVAILABLE = True
except ImportError:
    CACHED_DESIGN_AVAILABLE = False


class WorkspaceState(Enum):
    """Workspace state machine states."""

    WELCOME = "welcome"
    IMPORT = "import"
    DESIGN = "design"
    BUILDING_3D = "building_3d"  # Full building view
    VIEW_3D = "view_3d"  # Single beam detail
    CROSS_SECTION = "cross_section"  # Beautiful cross-section view
    REBAR_EDIT = "rebar_edit"  # Interactive reinforcement editor
    EDIT = "edit"
    DASHBOARD = "dashboard"


# Bar options for rebar editor
BAR_OPTIONS = [
    (10, 78.5),
    (12, 113.1),
    (16, 201.1),
    (20, 314.2),
    (25, 490.9),
    (32, 804.2),
]

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


def set_workspace_state(new_state: WorkspaceState) -> None:
    """Change workspace state and trigger rerun."""
    st.session_state.ws_state = new_state


def get_workspace_state() -> WorkspaceState:
    """Get current workspace state."""
    init_workspace_state()  # Ensure state is initialized
    return st.session_state.ws_state


def auto_map_columns(df: pd.DataFrame) -> dict[str, str]:
    """Auto-detect column mapping from CSV headers."""
    mapping = {}
    df_cols_lower = {c.lower().strip(): c for c in df.columns}

    for target, patterns in COLUMN_PATTERNS.items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            for col_lower, col_orig in df_cols_lower.items():
                if pattern_lower in col_lower or col_lower in pattern_lower:
                    if target not in mapping:  # Only take first match
                        mapping[target] = col_orig
                    break

    return mapping


def standardize_dataframe(
    df: pd.DataFrame,
    mapping: dict[str, str],
    defaults: dict[str, float],
) -> pd.DataFrame:
    """Standardize DataFrame to common format."""
    result = pd.DataFrame()

    # Map columns
    result["beam_id"] = df[mapping.get("beam_id", df.columns[0])]

    # Geometry with defaults
    if "b_mm" in mapping:
        result["b_mm"] = pd.to_numeric(df[mapping["b_mm"]], errors="coerce").fillna(300)
    else:
        result["b_mm"] = 300

    if "D_mm" in mapping:
        result["D_mm"] = pd.to_numeric(df[mapping["D_mm"]], errors="coerce").fillna(500)
    else:
        result["D_mm"] = 500

    if "span_mm" in mapping:
        result["span_mm"] = pd.to_numeric(df[mapping["span_mm"]], errors="coerce").fillna(5000)
    else:
        result["span_mm"] = 5000

    # Forces
    if "mu_knm" in mapping:
        result["mu_knm"] = pd.to_numeric(df[mapping["mu_knm"]], errors="coerce").fillna(100)
    else:
        result["mu_knm"] = 100

    if "vu_kn" in mapping:
        result["vu_kn"] = pd.to_numeric(df[mapping["vu_kn"]], errors="coerce").fillna(50)
    else:
        result["vu_kn"] = 50

    # Story
    if "story" in mapping:
        result["story"] = df[mapping["story"]].fillna("Unknown")
    else:
        result["story"] = "Story1"

    # Coordinates for 3D building view (generate if not provided)
    coord_fields = ["x1", "y1", "z1", "x2", "y2", "z2"]
    has_coords = all(field in mapping for field in coord_fields)

    if has_coords:
        for field in coord_fields:
            result[field] = pd.to_numeric(df[mapping[field]], errors="coerce").fillna(0)
    else:
        # Generate grid layout based on story and index
        stories = result["story"].unique()
        story_heights = {s: i * 3.0 for i, s in enumerate(sorted(stories))}  # 3m per story

        x_pos = 0.0
        coords_data = {"x1": [], "y1": [], "z1": [], "x2": [], "y2": [], "z2": []}
        for idx, row in result.iterrows():
            span_m = row["span_mm"] / 1000 if row["span_mm"] > 0 else 5.0
            story = row["story"]
            z = story_heights.get(story, 0)

            # Alternate between X and Y directions
            if idx % 2 == 0:
                coords_data["x1"].append(x_pos)
                coords_data["y1"].append(0)
                coords_data["x2"].append(x_pos + span_m)
                coords_data["y2"].append(0)
            else:
                coords_data["x1"].append(0)
                coords_data["y1"].append(x_pos)
                coords_data["x2"].append(0)
                coords_data["y2"].append(x_pos + span_m)

            coords_data["z1"].append(z)
            coords_data["z2"].append(z)
            x_pos += span_m * 0.3  # Offset next beam

        for field in coord_fields:
            result[field] = coords_data[field]

    # Material defaults
    result["fck"] = defaults.get("fck", 25.0)
    result["fy"] = defaults.get("fy", 500.0)
    result["cover_mm"] = defaults.get("cover_mm", 40.0)

    return result


def load_sample_data() -> None:
    """Load built-in sample ETABS data."""
    df = pd.read_csv(io.StringIO(SAMPLE_ETABS_DATA))
    mapping = auto_map_columns(df)
    st.session_state.ws_beams_df = standardize_dataframe(
        df, mapping, st.session_state.ws_defaults
    )
    st.session_state.ws_state = WorkspaceState.IMPORT


def detect_format_from_content(content: str, filename: str) -> str:
    """Auto-detect file format from content and filename."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # Check for ETABS patterns
    etabs_patterns = ["story", "unique name", "m3", "v2", "output case", "xi", "xj"]
    if any(p in content_lower for p in etabs_patterns):
        return "ETABS"

    # Check for SAFE patterns
    safe_patterns = ["strip", "m22", "v23"]
    if any(p in content_lower for p in safe_patterns):
        return "SAFE"

    return "Generic"


def process_with_adapters(
    geometry_file,
    forces_file,
    defaults: dict[str, float],
) -> tuple[bool, str, list, list]:
    """Process files using the adapter system (reuses multi-format import infrastructure).

    Returns:
        (success, message, beams_list, forces_list)
    """
    if not ADAPTERS_AVAILABLE:
        return False, "Adapter system not available. Install structural_lib.", [], []

    # Create DesignDefaults from dict
    design_defaults = DesignDefaults(
        fck_mpa=defaults.get("fck", 25.0),
        fy_mpa=defaults.get("fy", 500.0),
        cover_mm=defaults.get("cover_mm", 40.0),
    )

    beams = []
    forces = []
    detected_format = "Generic"

    # Process geometry file
    if geometry_file is not None:
        content = geometry_file.getvalue().decode("utf-8")
        detected_format = detect_format_from_content(content, geometry_file.name)
        adapter = ADAPTERS.get(detected_format, ADAPTERS.get("Generic"))

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            if adapter and adapter.can_handle(temp_path):
                beams = adapter.load_geometry(temp_path, defaults=design_defaults)
        except Exception as e:
            return False, f"Error loading geometry: {e}", [], []
        finally:
            Path(temp_path).unlink(missing_ok=True)

    # Process forces file
    if forces_file is not None:
        content = forces_file.getvalue().decode("utf-8")
        if detected_format == "Generic":
            detected_format = detect_format_from_content(content, forces_file.name)
        adapter = ADAPTERS.get(detected_format, ADAPTERS.get("Generic"))

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_path = f.name

        try:
            if adapter:
                forces = adapter.load_forces(temp_path)
        except Exception as e:
            return False, f"Error loading forces: {e}", [], []
        finally:
            Path(temp_path).unlink(missing_ok=True)

    msg = f"✅ Loaded from {detected_format}:"
    if beams:
        msg += f"\n- {len(beams)} beams with geometry"
    if forces:
        msg += f"\n- {len(forces)} force records"

    return True, msg, beams, forces


def beams_to_dataframe(beams: list, forces: list, defaults: dict) -> pd.DataFrame:
    """Convert BeamGeometry and BeamForces lists to unified DataFrame.

    This replicates the logic from multi-format import page.
    """
    # Create lookup for forces by beam ID
    force_lookup = {}
    for force in forces:
        if force.id not in force_lookup:
            force_lookup[force.id] = []
        force_lookup[force.id].append(force)

    rows = []
    for idx, beam in enumerate(beams):
        # Get governing forces for this beam
        beam_forces = force_lookup.get(beam.id, [])
        if beam_forces:
            max_mu = max(f.mu_knm for f in beam_forces)
            max_vu = max(f.vu_kn for f in beam_forces)
        else:
            max_mu = defaults.get("mu_knm", 100.0)
            max_vu = defaults.get("vu_kn", 50.0)

        rows.append({
            "beam_id": beam.id,
            "story": beam.story,
            "b_mm": beam.section.width_mm,
            "D_mm": beam.section.depth_mm,
            "span_mm": beam.length_m * 1000,
            "mu_knm": max_mu,
            "vu_kn": max_vu,
            "fck": beam.section.fck_mpa,
            "fy": beam.section.fy_mpa,
            "cover_mm": beam.section.cover_mm,
            "x1": beam.point1.x if beam.point1 else 0,
            "y1": beam.point1.y if beam.point1 else 0,
            "z1": beam.point1.z if beam.point1 else 0,
            "x2": beam.point2.x if beam.point2 else beam.length_m,
            "y2": beam.point2.y if beam.point2 else 0,
            "z2": beam.point2.z if beam.point2 else 0,
        })

    return pd.DataFrame(rows)


def process_uploaded_file(file) -> tuple[bool, str]:
    """Process uploaded CSV with auto-mapping.

    Uses adapter system if available, falls back to simple mapping.
    """
    if ADAPTERS_AVAILABLE:
        # Use adapter system (same as multi-format import)
        success, msg, beams, forces = process_with_adapters(
            file, None, st.session_state.ws_defaults
        )
        if success and beams:
            st.session_state.ws_beams_df = beams_to_dataframe(
                beams, forces, st.session_state.ws_defaults
            )
            return True, msg
        # Fall through to simple mapping if adapter fails

    # Fallback: simple auto-mapping
    try:
        file.seek(0)  # Reset file position
        df = pd.read_csv(file)
        mapping = auto_map_columns(df)

        if not mapping:
            return False, "Could not auto-detect columns. Check CSV format."

        st.session_state.ws_beams_df = standardize_dataframe(
            df, mapping, st.session_state.ws_defaults
        )

        detected = ", ".join(f"{k}→{v}" for k, v in mapping.items())
        return True, f"✅ Auto-mapped: {detected}"

    except Exception as e:
        return False, f"Error reading file: {e}"


def process_multi_files(geometry_file, forces_file) -> tuple[bool, str]:
    """Process separate geometry and forces files.

    Uses adapter system if available (same as multi-format import page).
    """
    if ADAPTERS_AVAILABLE:
        success, msg, beams, forces = process_with_adapters(
            geometry_file, forces_file, st.session_state.ws_defaults
        )
        if success and (beams or forces):
            if beams:
                st.session_state.ws_beams_df = beams_to_dataframe(
                    beams, forces, st.session_state.ws_defaults
                )
            return True, msg

    # Fallback to simple merge
    try:
        geo_df = None
        forces_df = None

        # Read geometry file
        if geometry_file:
            if geometry_file.name.endswith('.xlsx'):
                geo_df = pd.read_excel(geometry_file)
            else:
                geo_df = pd.read_csv(geometry_file)

        # Read forces file
        if forces_file:
            if forces_file.name.endswith('.xlsx'):
                forces_df = pd.read_excel(forces_file)
            else:
                forces_df = pd.read_csv(forces_file)

        # If only one file, process as single
        if geo_df is not None and forces_df is None:
            mapping = auto_map_columns(geo_df)
            st.session_state.ws_beams_df = standardize_dataframe(
                geo_df, mapping, st.session_state.ws_defaults
            )
            return True, f"✅ Loaded geometry with {len(geo_df)} beams"

        if forces_df is not None and geo_df is None:
            mapping = auto_map_columns(forces_df)
            st.session_state.ws_beams_df = standardize_dataframe(
                forces_df, mapping, st.session_state.ws_defaults
            )
            return True, f"✅ Loaded forces with {len(forces_df)} entries"

        # Merge both files
        if geo_df is not None and forces_df is not None:
            # Auto-map columns for both
            geo_mapping = auto_map_columns(geo_df)
            forces_mapping = auto_map_columns(forces_df)

            # Find common key (beam_id / unique name)
            geo_id_col = geo_mapping.get("beam_id")
            forces_id_col = forces_mapping.get("beam_id")

            if geo_id_col and forces_id_col:
                # Merge on beam ID
                merged_df = geo_df.merge(
                    forces_df,
                    left_on=geo_id_col,
                    right_on=forces_id_col,
                    how="outer",
                    suffixes=("", "_forces")
                )

                # Combine mappings
                combined_mapping = {**geo_mapping}
                for key, col in forces_mapping.items():
                    if key not in combined_mapping:
                        combined_mapping[key] = col

                st.session_state.ws_beams_df = standardize_dataframe(
                    merged_df, combined_mapping, st.session_state.ws_defaults
                )
                return True, f"✅ Merged {len(geo_df)} geometry + {len(forces_df)} forces → {len(merged_df)} beams"
            else:
                # Fallback: just use geometry with defaults for forces
                mapping = auto_map_columns(geo_df)
                st.session_state.ws_beams_df = standardize_dataframe(
                    geo_df, mapping, st.session_state.ws_defaults
                )
                return True, f"⚠️ Could not match beam IDs. Using geometry with default forces."

        return False, "No files provided"

    except Exception as e:
        return False, f"Error processing files: {e}"


def calculate_rebar_layout(
    ast_mm2: float,
    b_mm: float,
    D_mm: float,
    span_mm: float,
    vu_kn: float = 50.0,
    cover_mm: float = 40.0,
    stirrup_dia: float = 8.0,
) -> dict[str, Any]:
    """Calculate rebar layout for visualization."""
    BAR_OPTIONS = [(12, 113.1), (16, 201.1), (20, 314.2), (25, 490.9), (32, 804.2)]

    best_config = None
    for dia, area in BAR_OPTIONS:
        num_bars = math.ceil(ast_mm2 / area) if ast_mm2 > 0 else 2
        if 2 <= num_bars <= 6:
            best_config = (dia, num_bars, num_bars * area)
            break

    if best_config is None:
        best_config = (16, 3, 3 * 201.1)

    bar_dia, num_bars, ast_provided = best_config

    edge_dist = cover_mm + stirrup_dia + bar_dia / 2
    z_bottom = edge_dist
    z_top = D_mm - edge_dist
    available_width = b_mm - 2 * edge_dist

    bottom_bars = []
    spacing = available_width / max(num_bars - 1, 1)
    for i in range(num_bars):
        y = -available_width / 2 + i * spacing
        bottom_bars.append((0, y, z_bottom))

    top_bars = [
        (0, -available_width / 2, z_top),
        (0, available_width / 2, z_top),
    ]

    d_mm = D_mm - cover_mm - stirrup_dia - bar_dia / 2
    sv_base = min(200, max(100, 0.75 * d_mm))
    tau_v = (vu_kn * 1000) / max(b_mm * d_mm, 1)
    if tau_v > 0.5:
        sv_base = min(sv_base, 150)

    stirrup_positions = []
    zone_2d = 2 * d_mm
    sv_support = sv_base * 0.75

    x = 50
    while x < min(zone_2d, span_mm - 50):
        stirrup_positions.append(x)
        x += sv_support
    while x < max(span_mm - zone_2d, zone_2d):
        stirrup_positions.append(x)
        x += sv_base
    while x < span_mm - 50:
        stirrup_positions.append(x)
        x += sv_support

    return {
        "bottom_bars": bottom_bars,
        "top_bars": top_bars,
        "stirrup_positions": stirrup_positions,
        "bar_diameter": bar_dia,
        "stirrup_diameter": stirrup_dia,
        "summary": f"{num_bars}T{bar_dia} ({ast_provided:.0f} mm²)",
        "spacing_summary": f"Stirrups: Ø{stirrup_dia}@{sv_support:.0f}mm (ends), @{sv_base:.0f}mm (mid)",
    }


def design_beam_row(row: pd.Series) -> dict[str, Any]:
    """Design a single beam and return results.

    Uses cached_design when available (same as multi-format import page).
    """
    try:
        b_mm = float(row["b_mm"])
        D_mm = float(row["D_mm"])
        d_mm = D_mm - float(row.get("cover_mm", 50)) - 8  # cover + stirrup radius
        fck = float(row["fck"])
        fy = float(row["fy"])
        mu_knm = float(row["mu_knm"])
        vu_kn = float(row["vu_kn"])

        # Validate dimensions before design
        if D_mm < 100 or b_mm < 100:
            return {
                "is_safe": False,
                "ast_req": 0,
                "utilization": float("inf"),
                "status": f"❌ Invalid dims: {b_mm}x{D_mm}",
            }

        # Use cached_design if available (consistent with multi-format import)
        if CACHED_DESIGN_AVAILABLE:
            result = cached_design(
                mu_knm=mu_knm,
                vu_kn=vu_kn,
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck,
                fy_nmm2=fy,
            )
            # cached_design returns dict, not object
            is_safe = result.get("is_safe", False)
            flexure = result.get("flexure", {})
            ast_req = flexure.get("ast_required", 0) if isinstance(flexure, dict) else 0
            utilization = result.get("governing_utilization", 0)
        else:
            # Fallback to direct API call
            from structural_lib import api as structural_api

            result = structural_api.design_beam_is456(
                units="IS456",
                b_mm=b_mm,
                D_mm=D_mm,
                d_mm=d_mm,
                fck_nmm2=fck,
                fy_nmm2=fy,
                mu_knm=mu_knm,
                vu_kn=vu_kn,
            )
            # API returns object with attributes
            is_safe = result.is_ok
            ast_req = result.flexure.ast_required
            utilization = result.governing_utilization

        return {
            "is_safe": is_safe,
            "ast_req": ast_req,
            "utilization": utilization,
            "status": "✅ OK" if is_safe else "❌ FAIL",
        }
    except Exception as e:
        return {
            "is_safe": False,
            "ast_req": 0,
            "utilization": 0,
            "status": f"❌ {str(e)[:30]}",
        }


def design_all_beams_ws() -> pd.DataFrame:
    """Design all beams in the workspace."""
    df = st.session_state.ws_beams_df
    if df is None or df.empty:
        return pd.DataFrame()

    results = []
    for idx, row in df.iterrows():
        design = design_beam_row(row)
        result_row = {
            "beam_id": row["beam_id"],
            "story": row["story"],
            "b_mm": row["b_mm"],
            "D_mm": row["D_mm"],
            "span_mm": row["span_mm"],
            "mu_knm": row["mu_knm"],
            "vu_kn": row["vu_kn"],
            "fck": row["fck"],
            "fy": row["fy"],
            "cover_mm": row["cover_mm"],
            "ast_req": design["ast_req"],
            "utilization": design["utilization"],
            "is_safe": design["is_safe"],
            "status": design["status"],
        }
        # Preserve coordinate columns for 3D view
        for coord in ["x1", "y1", "z1", "x2", "y2", "z2"]:
            if coord in row:
                result_row[coord] = row[coord]
        results.append(result_row)

    return pd.DataFrame(results)


# =============================================================================
# Workspace Renderers
# =============================================================================


def render_welcome_panel() -> None:
    """Render welcome state with quick start cards."""
    st.markdown("### 🏗️ Beam Design Workspace")

    # Compact intro
    st.caption("Import your ETABS/SAFE data or start with sample beams")

    col1, col2 = st.columns([1, 1])

    with col1:
        with st.container(border=True):
            st.markdown("#### 📂 Quick Demo")
            st.caption("10 beams · 3 stories · Ready to design")
            if st.button("▶ Load Sample Data", key="ws_sample", use_container_width=True, type="primary",
                        help="Load sample ETABS data with 3D coordinates"):
                with st.spinner("Loading sample data..."):
                    load_sample_data()
                st.rerun()

    with col2:
        with st.container(border=True):
            st.markdown("#### 📤 Import CSV Files")
            st.caption("Geometry + Forces (1 or 2 files)")

            # Single unified file uploader that accepts multiple files
            uploaded_files = st.file_uploader(
                "Upload CSV/Excel",
                type=["csv", "xlsx"],
                key="ws_multi_upload",
                label_visibility="collapsed",
                accept_multiple_files=True,
                help="Upload 1 file (combined) or 2 files (geometry + forces)"
            )

            if uploaded_files:
                if len(uploaded_files) == 1:
                    # Single file - process as combined
                    with st.spinner("Processing file..."):
                        success, message = process_uploaded_file(uploaded_files[0])
                    if success:
                        st.success(message)
                        st.session_state.ws_state = WorkspaceState.IMPORT
                        st.rerun()
                    else:
                        st.error(message)
                elif len(uploaded_files) == 2:
                    # Two files - merge geometry + forces
                    st.info(f"📁 {uploaded_files[0].name} + {uploaded_files[1].name}")
                    if st.button("🔄 Merge & Import", type="primary", use_container_width=True):
                        with st.spinner("Merging files..."):
                            success, message = process_multi_files(uploaded_files[0], uploaded_files[1])
                        if success:
                            st.success(message)
                            st.session_state.ws_state = WorkspaceState.IMPORT
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please upload 1 or 2 files only")

    # Compact workflow hint
    st.markdown("---")
    st.markdown("**Workflow:** `load sample` → `design all` → `building 3d` → Select beam → `edit rebar`")


def render_import_preview() -> None:
    """Render import preview with auto-mapped data."""
    df = st.session_state.ws_beams_df

    st.markdown("### 📥 Import Preview")

    if df is None or df.empty:
        st.warning("No data loaded. Go back to Welcome.")
        if st.button("← Back to Welcome"):
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Beams", len(df))
    col2.metric("Stories", df["story"].nunique())
    col3.metric("Avg Mu", f"{df['mu_knm'].mean():.1f} kN·m")
    col4.metric("Avg Vu", f"{df['vu_kn'].mean():.1f} kN")

    # Preview table
    st.dataframe(
        df[["beam_id", "story", "b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn"]],
        use_container_width=True,
        height=250,
    )

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Design All Beams", type="primary", use_container_width=True,
                    help="Run IS456 flexure & shear design on all beams"):
            with st.spinner("Designing beams..."):
                st.session_state.ws_design_results = design_all_beams_ws()
            st.session_state.ws_state = WorkspaceState.DESIGN
            st.rerun()
    with col2:
        if st.button("← Back to Welcome", use_container_width=True,
                    help="Clear data and return to start screen"):
            st.session_state.ws_beams_df = None
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()


def render_design_results() -> None:
    """Render design results with interactive table."""
    df = st.session_state.ws_design_results

    if df is None or df.empty:
        st.warning("No design results. Design beams first.")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary metrics in compact row
    total = len(df)
    passed = len(df[df["is_safe"] == True])
    failed = total - passed
    avg_util = df["utilization"].mean() * 100

    # Compact header with metrics
    c1, c2, c3, c4, c5 = st.columns([1.5, 1, 1, 1, 1.5])
    c1.markdown("### 📊 Results")
    c2.metric("Total", total)
    c3.metric("✅ Pass", passed)
    c4.metric("❌ Fail", failed)
    c5.metric("Util", f"{avg_util:.1f}%")

    # Filter row
    fc1, fc2, fc3 = st.columns([1, 1, 2])
    with fc1:
        story_filter = st.selectbox("📍 Story", ["All"] + sorted(df["story"].unique().tolist()), key="ws_story_filter")
    with fc2:
        status_filter = st.selectbox("🎯 Status", ["All", "Safe", "Failed"], key="ws_status_filter")

    # Apply filters
    filtered_df = df.copy()
    if story_filter != "All":
        filtered_df = filtered_df[filtered_df["story"] == story_filter]
    if status_filter == "Safe":
        filtered_df = filtered_df[filtered_df["is_safe"] == True]
    elif status_filter == "Failed":
        filtered_df = filtered_df[filtered_df["is_safe"] == False]

    # Results table with styled status
    display_df = filtered_df[["beam_id", "story", "b_mm", "D_mm", "mu_knm", "vu_kn", "ast_req", "utilization", "status"]].copy()
    display_df.columns = ["ID", "Story", "b", "D", "Mu", "Vu", "Ast", "Util", "Status"]
    display_df["Util"] = display_df["Util"].apply(lambda x: f"{x*100:.0f}%")

    st.dataframe(display_df, use_container_width=True, height=180, hide_index=True)

    # Beam selector with quick actions
    beam_options = filtered_df["beam_id"].tolist()
    if beam_options:
        selected = st.selectbox("🔍 Select beam for details:", beam_options, key="ws_beam_select2")
        st.session_state.ws_selected_beam = selected

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🎨 3D View", use_container_width=True, type="primary",
                        help="Interactive 3D visualization of the selected beam"):
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
        with col2:
            if st.button("📐 Section", use_container_width=True,
                        help="View cross-section with reinforcement layout"):
                set_workspace_state(WorkspaceState.CROSS_SECTION)
                st.rerun()
        with col3:
            if st.button("🔧 Rebar", use_container_width=True,
                        help="Edit reinforcement to fix failed designs"):
                set_workspace_state(WorkspaceState.REBAR_EDIT)
                st.rerun()
        with col4:
            if st.button("🏗️ Building", use_container_width=True,
                        help="See all beams in 3D building context"):
                set_workspace_state(WorkspaceState.BUILDING_3D)
                st.rerun()

    # Help tip for failed beams
    if failed > 0:
        st.warning(f"💡 **{failed} beams failed.** Select one and use **Edit Rebar** to increase reinforcement.")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📊 Dashboard", use_container_width=True,
                    help="See summary stats, cost breakdown, and export options"):
            set_workspace_state(WorkspaceState.DASHBOARD)
            st.rerun()
    with c2:
        if st.button("← Import", use_container_width=True,
                    help="Go back to review or modify imported data"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()


def create_building_3d_figure(df: pd.DataFrame) -> go.Figure:
    """Create impressive 3D building visualization with all beams.

    Features:
    - Real 3D beam volumes with proper orientation
    - Color by story or design status
    - Hover details for each beam
    - Professional lighting and camera
    """
    fig = go.Figure()

    if df is None or df.empty:
        return fig

    # Group by story for coloring
    stories = sorted(df["story"].unique())
    color_palette = [
        "#3498db",  # Blue
        "#2ecc71",  # Green
        "#e74c3c",  # Red
        "#9b59b6",  # Purple
        "#f39c12",  # Orange
        "#1abc9c",  # Teal
        "#e91e63",  # Pink
        "#00bcd4",  # Cyan
    ]
    story_colors = {s: color_palette[i % len(color_palette)] for i, s in enumerate(stories)}

    # Track extents for camera
    all_x, all_y, all_z = [], [], []

    for idx, row in df.iterrows():
        beam_id = row["beam_id"]
        story = row["story"]

        # Get coordinates
        x1 = float(row.get("x1", 0))
        y1 = float(row.get("y1", 0))
        z1 = float(row.get("z1", 0))
        x2 = float(row.get("x2", x1 + row["span_mm"] / 1000))
        y2 = float(row.get("y2", y1))
        z2 = float(row.get("z2", z1))

        all_x.extend([x1, x2])
        all_y.extend([y1, y2])
        all_z.extend([z1, z2])

        # Beam dimensions in meters
        b = row["b_mm"] / 1000
        d = row["D_mm"] / 1000

        # Calculate beam orientation
        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        if length < 0.01:
            continue

        # Normalize direction
        dir_x, dir_y, dir_z = dx / length, dy / length, dz / length

        # Perpendicular vectors
        if abs(dir_z) < 0.99:
            perp_x, perp_y = -dir_y, dir_x
            perp_len = math.sqrt(perp_x**2 + perp_y**2)
            if perp_len > 0.001:
                perp_x, perp_y = perp_x / perp_len, perp_y / perp_len
            else:
                perp_x, perp_y = 1, 0
            up_x, up_y, up_z = 0, 0, 1
        else:
            perp_x, perp_y = 1, 0
            up_x, up_y, up_z = 0, 1, 0

        hw, hd = b / 2, d / 2

        # Build 8 corners
        corners = []
        for (ex, ey, ez) in [(x1, y1, z1), (x2, y2, z2)]:
            for ws in [-1, 1]:
                for ds in [-1, 1]:
                    cx = ex + ws * hw * perp_x + ds * hd * up_x
                    cy = ey + ws * hw * perp_y + ds * hd * up_y
                    cz = ez + ds * hd * up_z
                    corners.append((cx, cy, cz))

        x_mesh = [c[0] for c in corners]
        y_mesh = [c[1] for c in corners]
        z_mesh = [c[2] for c in corners]

        # Triangular faces for mesh
        i_faces = [0, 0, 4, 4, 0, 1, 2, 3, 0, 2, 1, 3]
        j_faces = [1, 2, 5, 6, 4, 5, 6, 7, 1, 6, 5, 7]
        k_faces = [3, 3, 7, 7, 5, 4, 4, 5, 2, 4, 3, 6]

        # Color based on status or story
        status = row.get("status", "")
        if "SAFE" in str(status).upper():
            color = "rgba(46, 204, 113, 0.85)"
        elif "FAIL" in str(status).upper():
            color = "rgba(231, 76, 60, 0.85)"
        else:
            base = story_colors.get(story, "#3498db")
            r, g, b_col = int(base[1:3], 16), int(base[3:5], 16), int(base[5:7], 16)
            color = f"rgba({r}, {g}, {b_col}, 0.8)"

        # Concise hover info - just beam name, utilization, pass/fail
        util_pct = row.get("utilization", 0) * 100
        status_icon = "✅" if "SAFE" in str(status).upper() else "❌" if "FAIL" in str(status).upper() else "⏳"
        hover = f"<b>{beam_id}</b> {status_icon}<br>Util: {util_pct:.0f}%"

        fig.add_trace(go.Mesh3d(
            x=x_mesh, y=y_mesh, z=z_mesh,
            i=i_faces, j=j_faces, k=k_faces,
            color=color,
            opacity=0.9,
            flatshading=True,
            lighting=dict(ambient=0.6, diffuse=0.8, specular=0.4, roughness=0.3),
            lightposition=dict(x=100, y=200, z=300),
            hovertemplate=hover + "<extra></extra>",
            name=beam_id,
            showlegend=False,
        ))

    # Add story legend
    for story in stories:
        base = story_colors[story]
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode="markers",
            marker=dict(size=10, color=base, symbol="square"),
            name=f"📍 {story}",
        ))

    # Calculate scene range
    if all_x and all_y and all_z:
        x_range = [min(all_x) - 2, max(all_x) + 2]
        y_range = [min(all_y) - 2, max(all_y) + 2]
        z_range = [min(all_z) - 1, max(all_z) + 3]
    else:
        x_range = y_range = z_range = [0, 10]

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=x_range, title="X (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(range=y_range, title="Y (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            zaxis=dict(range=z_range, title="Z (m)", showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.0),
                up=dict(x=0, y=0, z=1),
            ),
            bgcolor="rgba(20, 20, 30, 1)",
        ),
        paper_bgcolor="rgba(20, 20, 30, 1)",
        plot_bgcolor="rgba(20, 20, 30, 1)",
        font=dict(color="white"),
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            yanchor="top", y=0.99, xanchor="left", x=0.01,
            bgcolor="rgba(30, 30, 40, 0.8)",
        ),
    )

    return fig


def render_building_3d() -> None:
    """Render impressive full building 3D view."""
    # Get design results for status, but use beams_df for coordinates
    results_df = st.session_state.ws_design_results
    beams_df = st.session_state.ws_beams_df

    if beams_df is None or beams_df.empty:
        st.warning("No beam data to visualize. Load data first.")
        if st.button("← Back"):
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
        return

    # Merge status from results into beams data if available
    df = beams_df.copy()
    if results_df is not None and not results_df.empty:
        # Add status and utilization from design results
        status_map = dict(zip(results_df["beam_id"], results_df["status"]))
        util_map = dict(zip(results_df["beam_id"], results_df["utilization"]))
        df["status"] = df["beam_id"].map(status_map).fillna("⏳ Pending")
        df["utilization"] = df["beam_id"].map(util_map).fillna(0)
    else:
        df["status"] = "⏳ Pending"
        df["utilization"] = 0

    # Compact header with stats inline
    total = len(df)
    stories = df["story"].nunique()
    safe_count = len(df[df["status"].str.contains("OK|SAFE", case=False, na=False)]) if "status" in df.columns else 0
    pass_rate = f"{safe_count/total*100:.0f}%" if total > 0 else "N/A"

    st.markdown(f"### 🏗️ Building 3D — {total} beams, {stories} stories, {pass_rate} pass")

    # Create 3D figure with larger height
    fig = create_building_3d_figure(df)
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True, key="ws_building_3d")

    # Compact controls in single row
    c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
    with c1:
        if st.button("← Back", key="bldg_back"):
            # Go back to design if results exist, else import
            if results_df is not None:
                set_workspace_state(WorkspaceState.DESIGN)
            else:
                set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
    with c2:
        beam_ids = df["beam_id"].tolist() if len(df) > 0 else []
        if beam_ids:
            selected = st.selectbox("Select beam:", ["—"] + beam_ids, key="bldg_beam_select", label_visibility="collapsed")
            if selected != "—":
                st.session_state.ws_selected_beam = selected
                set_workspace_state(WorkspaceState.VIEW_3D)
                st.rerun()
    with c3:
        if st.button("📊 Dashboard", key="bldg_dash"):
            set_workspace_state(WorkspaceState.DASHBOARD)
            st.rerun()
    with c4:
        st.caption("Drag to rotate")


def calculate_constructability_score(
    bottom_bars: list[tuple[int, int]],
    top_bars: list[tuple[int, int]],
    stirrup_spacing: int,
    b_mm: float,
) -> dict[str, Any]:
    """Calculate constructability score for rebar configuration.

    Factors considered:
    - Fewer bars = easier to place (score: +20 for <=3 bars)
    - Same diameter = easier cutting (score: +20 for uniform dia)
    - Wider stirrup spacing = easier (score: +20 for >=150mm)
    - Single layer = easier (score: +20 for no Layer 2)
    - Good width/bar ratio = easier (score: +20 for spacing >50mm)
    """
    score = 0
    notes = []

    # Count total bottom bars
    total_bottom = sum(count for _, count in bottom_bars)
    if total_bottom <= 3:
        score += 20
        notes.append("Few bars")
    elif total_bottom <= 5:
        score += 10
        notes.append("Moderate bars")
    else:
        notes.append("Many bars - harder placement")

    # Check if all same diameter
    diameters = set(dia for dia, count in bottom_bars if count > 0)
    top_dias = set(dia for dia, count in top_bars if count > 0)
    if len(diameters) == 1:
        score += 20
        notes.append("Uniform dia")
    elif len(diameters) <= 2:
        score += 10

    if top_dias and diameters.intersection(top_dias):
        score += 5
        notes.append("Same as top")

    # Stirrup spacing
    if stirrup_spacing >= 200:
        score += 20
        notes.append("Wide stirrups")
    elif stirrup_spacing >= 150:
        score += 15
        notes.append("OK stirrups")
    elif stirrup_spacing >= 100:
        score += 5
        notes.append("Tight stirrups")
    else:
        notes.append("Very tight stirrups")

    # Single layer bonus
    if len(bottom_bars) == 1 or (len(bottom_bars) == 2 and bottom_bars[1][1] == 0):
        score += 20
        notes.append("Single layer")
    else:
        notes.append("Multi-layer")

    # Width/bar ratio
    bar_spacing_approx = b_mm / max(total_bottom, 1)
    if bar_spacing_approx >= 80:
        score += 20
        notes.append("Good spacing")
    elif bar_spacing_approx >= 50:
        score += 10

    summary = " | ".join(notes[:3])  # First 3 notes
    return {"score": min(score, 100), "summary": summary, "notes": notes}


def suggest_optimal_rebar(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    cover_mm: float,
) -> dict | None:
    """Suggest optimal reinforcement for given loads.

    Tries to minimize steel while maintaining safety and constructability.
    """
    # Calculate required steel area
    d_eff = D_mm - cover_mm - 8 - 16/2  # Assume 8mm stirrup, 16mm bar
    ast_req = mu_knm * 1e6 / (0.87 * fy * 0.9 * d_eff) if d_eff > 0 and fy > 0 else 500

    # Add 10% safety margin
    ast_target = ast_req * 1.1

    # Try different bar configurations
    bar_options = [12, 16, 20, 25]
    best_config = None
    best_waste = float('inf')

    for dia in bar_options:
        area_per_bar = math.pi * (dia / 2) ** 2
        count = max(2, math.ceil(ast_target / area_per_bar))

        # Check if fits in width
        clear_cover = cover_mm + 8  # Assuming 8mm stirrup
        available = b_mm - 2 * clear_cover
        bar_width_needed = count * dia + (count - 1) * max(dia, 25)

        if bar_width_needed > available:
            # Need 2 layers
            layer1 = count // 2 + count % 2
            layer2 = count - layer1
            if layer1 <= 6 and layer2 <= 4:
                waste = count * area_per_bar - ast_target
                if 0 <= waste < best_waste:
                    best_waste = waste
                    best_config = {
                        "bottom_layer1_dia": dia,
                        "bottom_layer1_count": layer1,
                        "bottom_layer2_dia": dia,
                        "bottom_layer2_count": layer2,
                    }
        else:
            if count <= 6:
                waste = count * area_per_bar - ast_target
                if 0 <= waste < best_waste:
                    best_waste = waste
                    best_config = {
                        "bottom_layer1_dia": dia,
                        "bottom_layer1_count": count,
                        "bottom_layer2_dia": 0,
                        "bottom_layer2_count": 0,
                    }

    return best_config


def calculate_rebar_checks(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float,
    fy: float,
    cover_mm: float,
    bottom_bars: list[tuple[int, int]],  # [(dia, count), ...]
    top_bars: list[tuple[int, int]],
    stirrup_dia: int,
    stirrup_spacing: int,
) -> dict[str, Any]:
    """Calculate all design checks for given rebar configuration.

    Returns utilization ratios and pass/fail status for:
    - Flexure capacity
    - Shear capacity
    - Minimum reinforcement
    - Maximum reinforcement
    - Spacing requirements
    - Development length
    """
    # Calculate areas
    ast_bottom = sum(count * math.pi * (dia/2)**2 for dia, count in bottom_bars)
    ast_top = sum(count * math.pi * (dia/2)**2 for dia, count in top_bars) if top_bars else 0
    ast_total = ast_bottom + ast_top

    # Effective depth
    max_dia_bottom = max((dia for dia, _ in bottom_bars), default=16)
    d_eff = D_mm - cover_mm - stirrup_dia - max_dia_bottom / 2

    # IS 456 checks
    results = {
        "ast_provided": ast_bottom,
        "ast_top": ast_top,
        "d_eff": d_eff,
    }

    # 1. Flexure capacity (approximate)
    # Mu = 0.87 * fy * Ast * (d - 0.42 * xu)
    # Simplified: Mu ≈ 0.87 * fy * Ast * 0.9 * d / 1e6 (for under-reinforced)
    mu_capacity = 0.87 * fy * ast_bottom * 0.9 * d_eff / 1e6 if fy > 0 else 0
    flexure_util = mu_knm / mu_capacity if mu_capacity > 0 else 999
    results["mu_capacity_knm"] = mu_capacity
    results["flexure_util"] = flexure_util
    results["flexure_ok"] = flexure_util <= 1.0

    # 2. Minimum reinforcement (IS 456 Cl 26.5.1.1)
    ast_min = 0.85 * b_mm * d_eff / fy if fy > 0 else 0
    results["ast_min"] = ast_min
    results["min_reinf_ok"] = ast_bottom >= ast_min

    # 3. Maximum reinforcement (4% of gross area)
    ast_max = 0.04 * b_mm * D_mm
    results["ast_max"] = ast_max
    results["max_reinf_ok"] = ast_total <= ast_max

    # 4. Shear capacity
    # τc from IS 456 Table 19 (approximate)
    pt = 100 * ast_bottom / (b_mm * d_eff) if d_eff > 0 else 0
    tau_c = min(0.28 * (pt ** 0.5) * (fck ** 0.33), 0.62 * (fck ** 0.5))  # Simplified
    vc_concrete = tau_c * b_mm * d_eff / 1000  # kN

    # Stirrup contribution
    asv = 2 * math.pi * (stirrup_dia / 2) ** 2
    sv = max(stirrup_spacing, 50)  # Avoid division issues
    vs_stirrup = 0.87 * fy * asv * d_eff / sv / 1000  # kN

    vu_capacity = vc_concrete + vs_stirrup
    shear_util = vu_kn / vu_capacity if vu_capacity > 0 else 999
    results["vu_capacity_kn"] = vu_capacity
    results["shear_util"] = shear_util
    results["shear_ok"] = shear_util <= 1.0

    # 5. Spacing check (min clear spacing = max(bar_dia, 25mm))
    # For multi-layer reinforcement, calculate spacing per layer and take minimum
    clear_cover = cover_mm + stirrup_dia
    available_width = b_mm - 2 * clear_cover

    # Calculate spacing for each layer separately
    layer_spacings = []
    for dia, count in bottom_bars:
        if count > 1:
            total_bar_width_layer = count * dia
            layer_spacing = (available_width - total_bar_width_layer) / (count - 1)
            layer_spacings.append((layer_spacing, dia))
        elif count == 1:
            layer_spacings.append((available_width - dia, dia))  # Single bar, plenty of space

    # Minimum spacing across all layers (worst case)
    if layer_spacings:
        min_layer_spacing = min(sp for sp, _ in layer_spacings)
        # Min required is max(bar_dia, 25mm) for the layer with smallest spacing
        worst_layer = min(layer_spacings, key=lambda x: x[0])
        min_spacing = max(worst_layer[1], 25)
        spacing = min_layer_spacing
    else:
        spacing = available_width
        min_spacing = 25

    results["bar_spacing"] = spacing
    results["spacing_ok"] = spacing >= min_spacing

    # Overall status
    all_ok = all([
        results["flexure_ok"],
        results["min_reinf_ok"],
        results["max_reinf_ok"],
        results["shear_ok"],
        results["spacing_ok"],
    ])
    results["all_ok"] = all_ok
    results["status"] = "✅ SAFE" if all_ok else "❌ REVISE"

    return results


def render_rebar_editor() -> None:
    """Render interactive reinforcement editor with real-time checks."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_design_results
    if df is None:
        df = st.session_state.ws_beams_df

    st.markdown(f"### 🔧 Reinforcement Editor: {beam_id}")

    if not beam_id or df is None or df.empty:
        st.warning("No beam selected.")
        if st.button("← Back"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    row = df[df["beam_id"] == beam_id]
    if row.empty:
        st.error(f"Beam {beam_id} not found")
        return
    row = row.iloc[0]

    # Fixed beam properties
    b_mm = float(row["b_mm"])
    D_mm = float(row["D_mm"])
    span_mm = float(row["span_mm"])
    mu_knm = float(row.get("mu_knm", 100))
    vu_kn = float(row.get("vu_kn", 50))
    fck = float(row.get("fck", 25))
    fy = float(row.get("fy", 500))
    cover_mm = float(row.get("cover_mm", 40))

    # Show fixed properties
    st.markdown(f"**Section:** {b_mm:.0f}×{D_mm:.0f} mm | **Span:** {span_mm/1000:.1f} m | **Mu:** {mu_knm:.1f} kN·m | **Vu:** {vu_kn:.1f} kN")

    # Initialize rebar config from session state or defaults
    config = st.session_state.ws_rebar_config
    if config is None or config.get("beam_id") != beam_id:
        # Initialize with design suggestion
        ast_req = float(row.get("ast_req", 500))
        suggested = calculate_rebar_layout(ast_req, b_mm, D_mm, span_mm, vu_kn, cover_mm)
        config = {
            "beam_id": beam_id,
            "bottom_layer1_dia": suggested.get("bar_diameter", 16),
            "bottom_layer1_count": len(suggested.get("bottom_bars", [])),
            "bottom_layer2_dia": 0,
            "bottom_layer2_count": 0,
            "top_dia": 12,
            "top_count": 2,
            "stirrup_dia": 8,
            "stirrup_spacing": 150,
        }
        st.session_state.ws_rebar_config = config

    # Editable rebar configuration
    col1, col2 = st.columns([0.45, 0.55])

    with col1:
        st.markdown("##### Bottom Reinforcement")
        c1, c2 = st.columns(2)
        with c1:
            l1_dia = st.selectbox("Layer 1 Dia (mm)", [10, 12, 16, 20, 25, 32],
                                  index=[10, 12, 16, 20, 25, 32].index(config["bottom_layer1_dia"]),
                                  key="re_l1_dia")
            l2_dia = st.selectbox("Layer 2 Dia (mm)", [0, 10, 12, 16, 20, 25, 32],
                                  index=[0, 10, 12, 16, 20, 25, 32].index(config.get("bottom_layer2_dia", 0)),
                                  key="re_l2_dia")
        with c2:
            l1_count = st.number_input("Count", 2, 8, config["bottom_layer1_count"], key="re_l1_cnt")
            l2_count = st.number_input("Count", 0, 6, config.get("bottom_layer2_count", 0), key="re_l2_cnt")

        st.markdown("##### Top Reinforcement")
        c1, c2 = st.columns(2)
        with c1:
            top_dia = st.selectbox("Dia (mm)", [10, 12, 16, 20],
                                   index=[10, 12, 16, 20].index(config.get("top_dia", 12)),
                                   key="re_top_dia")
        with c2:
            top_count = st.number_input("Count", 2, 6, config.get("top_count", 2), key="re_top_cnt")

        st.markdown("##### Stirrups")
        c1, c2 = st.columns(2)
        with c1:
            stir_dia = st.selectbox("Dia (mm)", [6, 8, 10],
                                    index=[6, 8, 10].index(config.get("stirrup_dia", 8)),
                                    key="re_stir_dia")
        with c2:
            stir_spacing = st.number_input("Spacing (mm)", 75, 300, config.get("stirrup_spacing", 150),
                                           step=25, key="re_stir_sp")

    # Update config
    config.update({
        "bottom_layer1_dia": l1_dia,
        "bottom_layer1_count": l1_count,
        "bottom_layer2_dia": l2_dia,
        "bottom_layer2_count": l2_count,
        "top_dia": top_dia,
        "top_count": top_count,
        "stirrup_dia": stir_dia,
        "stirrup_spacing": stir_spacing,
    })
    st.session_state.ws_rebar_config = config

    # Build bar lists
    bottom_bars = [(l1_dia, l1_count)]
    if l2_dia > 0 and l2_count > 0:
        bottom_bars.append((l2_dia, l2_count))
    top_bars = [(top_dia, top_count)]

    # Calculate checks
    checks = calculate_rebar_checks(
        b_mm, D_mm, mu_knm, vu_kn, fck, fy, cover_mm,
        bottom_bars, top_bars, stir_dia, stir_spacing
    )

    with col2:
        st.markdown("##### Design Checks")

        # Flexure
        flex_color = "🟢" if checks["flexure_ok"] else "🔴"
        st.markdown(f"{flex_color} **Flexure:** {checks['flexure_util']*100:.1f}% (Mu = {checks['mu_capacity_knm']:.1f} kN·m)")

        # Shear
        shear_color = "🟢" if checks["shear_ok"] else "🔴"
        st.markdown(f"{shear_color} **Shear:** {checks['shear_util']*100:.1f}% (Vu = {checks['vu_capacity_kn']:.1f} kN)")

        # Min reinforcement
        min_color = "🟢" if checks["min_reinf_ok"] else "🔴"
        st.markdown(f"{min_color} **Min Ast:** {checks['ast_provided']:.0f} ≥ {checks['ast_min']:.0f} mm²")

        # Max reinforcement
        max_color = "🟢" if checks["max_reinf_ok"] else "🔴"
        st.markdown(f"{max_color} **Max Ast:** {checks['ast_provided']:.0f} ≤ {checks['ast_max']:.0f} mm²")

        # Spacing
        sp_color = "🟢" if checks["spacing_ok"] else "🔴"
        st.markdown(f"{sp_color} **Bar Spacing:** {checks['bar_spacing']:.0f} mm")

        st.divider()

        # Overall status with big indicator
        if checks["all_ok"]:
            st.success(f"### {checks['status']}")
            st.caption(f"Ast provided: {checks['ast_provided']:.0f} mm² | d_eff: {checks['d_eff']:.0f} mm")
        else:
            st.error(f"### {checks['status']}")
            st.caption("Adjust reinforcement to satisfy all checks")

        # Constructability rating
        st.divider()
        constructability = calculate_constructability_score(
            bottom_bars, top_bars, stir_spacing, b_mm
        )
        const_icon = "🟢" if constructability["score"] >= 80 else ("🟡" if constructability["score"] >= 60 else "🔴")
        st.markdown(f"##### {const_icon} Construction Ease: {constructability['score']}/100")
        st.caption(constructability["summary"])

        # Quick optimization button
        if st.button("⚡ Auto-Optimize", use_container_width=True, help="Optimize for cost while maintaining safety"):
            optimized = suggest_optimal_rebar(b_mm, D_mm, mu_knm, vu_kn, fck, fy, cover_mm)
            if optimized:
                config.update(optimized)
                st.session_state.ws_rebar_config = config
                st.rerun()

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back to 3D View"):
            set_workspace_state(WorkspaceState.VIEW_3D)
            st.rerun()
    with col2:
        if st.button("🏗️ Building View"):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with col3:
        if st.button("▶ Next Beam"):
            beam_list = df["beam_id"].tolist() if len(df) > 0 else []
            if len(beam_list) > 1:
                curr_idx = beam_list.index(beam_id) if beam_id in beam_list else 0
                next_idx = (curr_idx + 1) % len(beam_list)
                st.session_state.ws_selected_beam = beam_list[next_idx]
                st.session_state.ws_rebar_config = None  # Reset for new beam
                st.rerun()


def create_cross_section_figure(
    b: float,
    D: float,
    cover: float,
    bottom_bars: list[tuple[float, float, float]],
    top_bars: list[tuple[float, float, float]],
    stirrup_dia: float = 8,
    rebar_config: dict | None = None,
) -> go.Figure:
    """Create professional cross-section 2D view using Plotly.

    Args:
        b: Beam width in mm
        D: Beam depth in mm
        cover: Clear cover in mm
        bottom_bars: List of (x, y, dia) for bottom reinforcement
        top_bars: List of (x, y, dia) for top reinforcement
        stirrup_dia: Stirrup diameter in mm
        rebar_config: Optional config from rebar editor

    Returns:
        Plotly figure showing cross-section
    """
    fig = go.Figure()

    # Colors for professional look
    concrete_color = "#e8e4e0"
    stirrup_color = "#666666"
    main_bar_color = "#1a5276"
    top_bar_color = "#28b463"

    # Concrete outline (filled rectangle)
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=b, y1=D,
        line=dict(color="#333", width=2),
        fillcolor=concrete_color,
        layer="below",
    )

    # Stirrup (inner rectangle)
    stirrup_offset = cover + stirrup_dia / 2
    fig.add_shape(
        type="rect",
        x0=stirrup_offset,
        y0=stirrup_offset,
        x1=b - stirrup_offset,
        y1=D - stirrup_offset,
        line=dict(color=stirrup_color, width=3),
        fillcolor="rgba(0,0,0,0)",
    )

    # Draw bottom bars
    for bx, by, dia in bottom_bars:
        fig.add_trace(go.Scatter(
            x=[bx], y=[by],
            mode="markers",
            marker=dict(
                size=max(10, dia * 0.6),
                color=main_bar_color,
                line=dict(color="#000", width=1),
            ),
            name=f"Bottom Bar Φ{dia:.0f}",
            hovertemplate=f"Bottom Bar<br>Φ{dia:.0f}mm<br>x: {bx:.1f}, y: {by:.1f}<extra></extra>",
            showlegend=False,
        ))

    # Draw top bars
    for tx, ty, dia in top_bars:
        fig.add_trace(go.Scatter(
            x=[tx], y=[ty],
            mode="markers",
            marker=dict(
                size=max(10, dia * 0.6),
                color=top_bar_color,
                line=dict(color="#000", width=1),
            ),
            name=f"Top Bar Φ{dia:.0f}",
            hovertemplate=f"Top Bar<br>Φ{dia:.0f}mm<br>x: {tx:.1f}, y: {ty:.1f}<extra></extra>",
            showlegend=False,
        ))

    # Dimension lines and annotations
    # Width dimension
    fig.add_annotation(
        x=b/2, y=-30,
        text=f"b = {b:.0f} mm",
        showarrow=False,
        font=dict(size=12, color="#333"),
    )
    fig.add_shape(
        type="line", x0=0, y0=-15, x1=b, y1=-15,
        line=dict(color="#666", width=1),
    )
    fig.add_shape(type="line", x0=0, y0=-5, x1=0, y1=-25, line=dict(color="#666", width=1))
    fig.add_shape(type="line", x0=b, y0=-5, x1=b, y1=-25, line=dict(color="#666", width=1))

    # Depth dimension
    fig.add_annotation(
        x=b+40, y=D/2,
        text=f"D = {D:.0f} mm",
        showarrow=False,
        font=dict(size=12, color="#333"),
        textangle=-90,
    )
    fig.add_shape(
        type="line", x0=b+15, y0=0, x1=b+15, y1=D,
        line=dict(color="#666", width=1),
    )
    fig.add_shape(type="line", x0=b+5, y0=0, x1=b+25, y1=0, line=dict(color="#666", width=1))
    fig.add_shape(type="line", x0=b+5, y0=D, x1=b+25, y1=D, line=dict(color="#666", width=1))

    # Cover annotation
    fig.add_annotation(
        x=cover/2, y=cover/2,
        text=f"{cover:.0f}",
        showarrow=False,
        font=dict(size=9, color="#888"),
    )

    # Legend/key
    legend_items = [
        (b+60, D-30, main_bar_color, "Bottom Bars"),
        (b+60, D-60, top_bar_color, "Top Bars"),
        (b+60, D-90, stirrup_color, "Stirrups"),
    ]
    for lx, ly, color, text in legend_items:
        fig.add_trace(go.Scatter(
            x=[lx], y=[ly],
            mode="markers+text",
            marker=dict(size=10, color=color),
            text=[f"  {text}"],
            textposition="middle right",
            showlegend=False,
            hoverinfo="skip",
        ))

    # Layout
    fig.update_layout(
        title=dict(
            text="Beam Cross-Section",
            font=dict(size=16, color="#333"),
            x=0.5,
        ),
        xaxis=dict(
            scaleanchor="y",
            scaleratio=1,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-50, b + 120],
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            range=[-60, D + 30],
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
    )

    return fig


def render_cross_section() -> None:
    """Render beautiful 2D cross-section view for selected beam."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_design_results

    st.markdown(f"### 📐 Cross-Section: {beam_id}")

    if not beam_id or df is None:
        st.warning("No beam selected.")
        if st.button("← Back to Results"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    row = df[df["beam_id"] == beam_id]
    if row.empty:
        st.error(f"Beam {beam_id} not found")
        return

    row = row.iloc[0]
    b = row["b_mm"]
    D = row["D_mm"]
    cover = row.get("cover_mm", 40)

    # Get rebar layout
    rebar = calculate_rebar_layout(
        ast_mm2=row["ast_req"],
        b_mm=b,
        D_mm=D,
        span_mm=row["span_mm"],
        vu_kn=row["vu_kn"],
        cover_mm=cover,
    )

    # Check for custom config from rebar editor
    rebar_config = st.session_state.get("ws_rebar_config")

    # Calculate bar positions for cross-section
    bottom_bars = []
    top_bars = []

    if rebar_config:
        # Use custom rebar configuration
        bottom_dia_1 = rebar_config.get("bottom_dia_1", 16)
        bottom_count_1 = rebar_config.get("bottom_count_1", 3)
        bottom_dia_2 = rebar_config.get("bottom_dia_2", 0)
        bottom_count_2 = rebar_config.get("bottom_count_2", 0)
        top_dia = rebar_config.get("top_dia", 12)
        top_count = rebar_config.get("top_count", 2)
    else:
        # Use calculated values
        bottom_dia_1 = rebar.get("bar_diameter", 16)
        n_bars = len(rebar["bottom_bars"])
        bottom_count_1 = min(n_bars, 4)
        bottom_count_2 = max(0, n_bars - 4)
        bottom_dia_2 = bottom_dia_1 if bottom_count_2 > 0 else 0
        top_dia = 12
        top_count = len(rebar["top_bars"])

    # Calculate bottom layer 1 positions
    layer1_y = cover + 8 + bottom_dia_1 / 2  # stirrup + half bar dia
    available_width = b - 2 * cover - 2 * 8  # inside stirrups
    if bottom_count_1 > 1:
        spacing_1 = available_width / (bottom_count_1 - 1)
    else:
        spacing_1 = 0
    for i in range(bottom_count_1):
        bx = cover + 8 + bottom_dia_1/2 + i * spacing_1 if bottom_count_1 > 1 else b/2
        bottom_bars.append((bx, layer1_y, bottom_dia_1))

    # Calculate bottom layer 2 positions (if any)
    if bottom_count_2 > 0 and bottom_dia_2 > 0:
        layer2_y = layer1_y + bottom_dia_1/2 + 25 + bottom_dia_2/2  # vertical spacing
        if bottom_count_2 > 1:
            spacing_2 = available_width / (bottom_count_2 - 1)
        else:
            spacing_2 = 0
        for i in range(bottom_count_2):
            bx = cover + 8 + bottom_dia_2/2 + i * spacing_2 if bottom_count_2 > 1 else b/2
            bottom_bars.append((bx, layer2_y, bottom_dia_2))

    # Calculate top bar positions
    top_y = D - cover - 8 - top_dia / 2
    if top_count > 1:
        spacing_top = available_width / (top_count - 1)
    else:
        spacing_top = 0
    for i in range(top_count):
        tx = cover + 8 + top_dia/2 + i * spacing_top if top_count > 1 else b/2
        top_bars.append((tx, top_y, top_dia))

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Section", f"{b:.0f} × {D:.0f}")
    col2.metric("Cover", f"{cover:.0f} mm")

    # Calculate total Ast
    total_ast = sum(3.14159 * (d/2)**2 for _, _, d in bottom_bars)
    col3.metric("Ast Provided", f"{total_ast:.0f} mm²")

    utilization = (row["ast_req"] / total_ast * 100) if total_ast > 0 else 0
    col4.metric("Utilization", f"{utilization:.0f}%")

    # Create and display cross-section
    if VISUALIZATION_AVAILABLE:
        fig = create_cross_section_figure(
            b=b,
            D=D,
            cover=cover,
            bottom_bars=bottom_bars,
            top_bars=top_bars,
            stirrup_dia=8,
            rebar_config=rebar_config,
        )
        st.plotly_chart(fig, use_container_width=True, key="cross_section_fig")
    else:
        st.warning("Plotly not available for visualization")
        st.write(f"Section: {b}×{D} mm")
        st.write(f"Bottom bars: {len(bottom_bars)}")
        st.write(f"Top bars: {len(top_bars)}")

    # Rebar schedule table
    st.markdown("#### 📋 Rebar Schedule")
    schedule_data = {
        "Location": ["Bottom Layer 1", "Bottom Layer 2", "Top Bars"],
        "Bars": [
            f"{bottom_count_1}Φ{bottom_dia_1}",
            f"{bottom_count_2}Φ{bottom_dia_2}" if bottom_count_2 > 0 else "-",
            f"{top_count}Φ{top_dia}",
        ],
        "Ast (mm²)": [
            f"{bottom_count_1 * 3.14159 * (bottom_dia_1/2)**2:.0f}",
            f"{bottom_count_2 * 3.14159 * (bottom_dia_2/2)**2:.0f}" if bottom_count_2 > 0 else "-",
            f"{top_count * 3.14159 * (top_dia/2)**2:.0f}",
        ],
    }
    st.dataframe(schedule_data, hide_index=True, use_container_width=True)

    # Navigation
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("← Back to 3D"):
            set_workspace_state(WorkspaceState.VIEW_3D)
            st.rerun()
    with c2:
        if st.button("🔧 Edit Rebar"):
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            st.rerun()
    with c3:
        if st.button("🏗️ Building"):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with c4:
        if st.button("📊 Results"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()


def render_3d_view() -> None:
    """Render detailed 3D view for selected beam."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_design_results

    st.markdown(f"### 🎨 3D View: {beam_id}")

    if not beam_id or df is None:
        st.warning("No beam selected.")
        if st.button("← Back to Results"):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
        return

    row = df[df["beam_id"] == beam_id]
    if row.empty:
        st.error(f"Beam {beam_id} not found")
        return

    row = row.iloc[0]

    # Beam info metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Section", f"{row['b_mm']:.0f}×{row['D_mm']:.0f}")
    col2.metric("Span", f"{row['span_mm']/1000:.1f} m")
    col3.metric("Ast Required", f"{row['ast_req']:.0f} mm²")
    col4.metric("Status", row["status"])

    # Calculate rebar layout
    rebar = calculate_rebar_layout(
        ast_mm2=row["ast_req"],
        b_mm=row["b_mm"],
        D_mm=row["D_mm"],
        span_mm=row["span_mm"],
        vu_kn=row["vu_kn"],
        cover_mm=row.get("cover_mm", 40),
    )

    st.caption(f"**{rebar['summary']}** — {rebar['spacing_summary']}")

    # 3D Figure
    if VISUALIZATION_AVAILABLE:
        try:
            fig = create_beam_3d_figure(
                b=row["b_mm"],
                D=row["D_mm"],
                span=row["span_mm"],
                bottom_bars=rebar["bottom_bars"],
                top_bars=rebar["top_bars"],
                stirrup_positions=rebar["stirrup_positions"],
                bar_diameter=rebar.get("bar_diameter", 16),
                stirrup_diameter=rebar.get("stirrup_diameter", 8),
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="ws_3d_view")
        except Exception as e:
            st.error(f"3D rendering error: {e}")
    else:
        st.info("3D visualization not available")

    # Navigation - compact 5-button row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("← Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with col2:
        if st.button("📐 Section", use_container_width=True):
            set_workspace_state(WorkspaceState.CROSS_SECTION)
            st.rerun()
    with col3:
        if st.button("🔧 Edit Rebar", use_container_width=True, type="primary"):
            set_workspace_state(WorkspaceState.REBAR_EDIT)
            st.rerun()
    with col4:
        if st.button("🏗️ Building", use_container_width=True):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with col5:
        # Next beam button
        beam_list = df["beam_id"].tolist() if df is not None and len(df) > 0 else []
        if len(beam_list) > 1:
            curr_idx = beam_list.index(beam_id) if beam_id in beam_list else 0
            next_idx = (curr_idx + 1) % len(beam_list)
            if st.button("▶ Next", use_container_width=True):
                st.session_state.ws_selected_beam = beam_list[next_idx]
                st.rerun()
        else:
            st.button("▶ Next", use_container_width=True, disabled=True)


def render_beam_editor() -> None:
    """Render single beam editor with live preview."""
    beam_id = st.session_state.ws_selected_beam
    df = st.session_state.ws_beams_df

    st.markdown(f"### ✏️ Edit Beam: {beam_id or 'New'}")

    if df is None or df.empty:
        st.warning("No beam data.")
        if st.button("← Back to Welcome"):
            set_workspace_state(WorkspaceState.WELCOME)
            st.rerun()
        return

    # Get beam data
    if beam_id:
        row = df[df["beam_id"] == beam_id]
        if row.empty:
            row = df.iloc[[0]]
        row = row.iloc[0]
    else:
        row = df.iloc[0]

    # Safe float conversion helper
    def safe_float(val, default: float) -> float:
        try:
            return float(val) if val is not None and not pd.isna(val) else default
        except (ValueError, TypeError):
            return default

    col1, col2 = st.columns([0.4, 0.6])

    with col1:
        st.markdown("**Geometry**")
        b = st.number_input("Width b (mm)", value=safe_float(row.get("b_mm"), 300.0), step=25.0, key="edit_b")
        D = st.number_input("Depth D (mm)", value=safe_float(row.get("D_mm"), 500.0), step=25.0, key="edit_D")
        span = st.number_input("Span (mm)", value=safe_float(row.get("span_mm"), 5000.0), step=100.0, key="edit_span")

        st.markdown("**Loading**")
        mu = st.number_input("Moment Mu (kN·m)", value=safe_float(row.get("mu_knm"), 100.0), step=10.0, key="edit_mu")
        vu = st.number_input("Shear Vu (kN)", value=safe_float(row.get("vu_kn"), 50.0), step=5.0, key="edit_vu")

        st.markdown("**Materials**")
        fck = st.selectbox("Concrete", [20, 25, 30, 35, 40], index=1, key="edit_fck")
        fy = st.selectbox("Steel", [415, 500, 550], index=1, key="edit_fy")

        if st.button("💫 Redesign", type="primary", use_container_width=True):
            # Update dataframe
            idx = df[df["beam_id"] == row["beam_id"]].index
            if len(idx) > 0:
                df.loc[idx[0], ["b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn", "fck", "fy"]] = [b, D, span, mu, vu, fck, fy]
                st.session_state.ws_beams_df = df
                st.session_state.ws_design_results = design_all_beams_ws()
                st.success("✅ Redesigned!")
                st.rerun()

    with col2:
        # Live preview with current values
        updated_row = pd.Series({
            "b_mm": b, "D_mm": D, "span_mm": span,
            "mu_knm": mu, "vu_kn": vu, "fck": fck, "fy": fy,
            "cover_mm": row.get("cover_mm", 40),
        })
        design = design_beam_row(updated_row)

        st.metric("Status", design["status"])
        st.metric("Ast Required", f"{design['ast_req']:.0f} mm²")
        st.metric("Utilization", f"{design['utilization']*100:.1f}%")

        if VISUALIZATION_AVAILABLE and design["ast_req"] > 0:
            rebar = calculate_rebar_layout(
                ast_mm2=design["ast_req"],
                b_mm=b,
                D_mm=D,
                span_mm=span,
                vu_kn=vu,
            )
            try:
                fig = create_beam_3d_figure(
                    b=b, D=D, span=span,
                    bottom_bars=rebar["bottom_bars"],
                    top_bars=rebar["top_bars"],
                    stirrup_positions=rebar["stirrup_positions"],
                )
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True, key="edit_3d_preview")
            except Exception as e:
                st.error(f"Preview error: {e}")

    st.divider()
    if st.button("← Back to Results"):
        set_workspace_state(WorkspaceState.DESIGN)
        st.rerun()


def calculate_material_takeoff(df: pd.DataFrame) -> dict:
    """Calculate material takeoff from design results.

    Args:
        df: Design results DataFrame

    Returns:
        Dictionary with material quantities and costs
    """
    total_concrete = 0  # m³
    total_steel = 0  # kg

    for _, row in df.iterrows():
        # Concrete volume
        b = row["b_mm"] / 1000  # m
        D = row["D_mm"] / 1000  # m
        span = row["span_mm"] / 1000  # m
        concrete_vol = b * D * span
        total_concrete += concrete_vol

        # Steel weight (approximate from Ast)
        ast = row.get("ast_req", 0)
        # Bottom bars
        bottom_area = ast  # mm²
        # Top bars (approx 30% of bottom)
        top_area = ast * 0.3
        # Stirrups (approx 25% of main)
        stirrup_area = ast * 0.25

        total_area = bottom_area + top_area + stirrup_area
        # Weight = area × length × density
        # area in mm², length in mm, density = 7850 kg/m³
        steel_weight = total_area * (span * 1000) * 7850 / 1e9
        total_steel += steel_weight

    # Costs (₹ per unit)
    concrete_rate = 8000  # ₹/m³ for M25 RCC
    steel_rate = 85  # ₹/kg for Fe500

    concrete_cost = total_concrete * concrete_rate
    steel_cost = total_steel * steel_rate
    total_cost = concrete_cost + steel_cost

    return {
        "concrete_m3": total_concrete,
        "steel_kg": total_steel,
        "concrete_cost": concrete_cost,
        "steel_cost": steel_cost,
        "total_cost": total_cost,
        "concrete_rate": concrete_rate,
        "steel_rate": steel_rate,
    }


def render_dashboard() -> None:
    """Render SmartDesigner dashboard with material takeoff."""
    st.markdown("### 📊 Smart Dashboard")

    df = st.session_state.ws_design_results

    if df is None or df.empty:
        st.info("Design beams first to see dashboard")
        if st.button("← Back to Import"):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()
        return

    # Summary stats row
    total = len(df)
    passed = len(df[df["is_safe"] == True])
    avg_util = df["utilization"].mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Beams", total)
    c2.metric("Pass Rate", f"{100*passed/max(total,1):.0f}%")
    c3.metric("Avg Util", f"{avg_util:.0f}%")
    c4.metric("Failed", total - passed, delta=f"-{total-passed}" if total > passed else None, delta_color="inverse")

    st.divider()

    # Tabs for different insights
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Analysis", "📦 Material Takeoff", "💰 Cost Estimate", "📥 Export"])

    with tab1:
        # Utilization distribution
        st.markdown("##### Utilization Distribution")
        low = len(df[df["utilization"] < 0.6])
        optimal = len(df[(df["utilization"] >= 0.6) & (df["utilization"] <= 0.85)])
        high = len(df[df["utilization"] > 0.85])

        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Under-utilized", low, help="<60% - consider reducing section")
        col2.metric("🟡 Optimal", optimal, help="60-85% - good efficiency")
        col3.metric("🔴 Near Capacity", high, help=">85% - check carefully")

        # Quick wins
        st.markdown("##### 💡 Suggestions")
        if low > total * 0.3:
            st.success(f"💰 {low} beams under-utilized. Reduce sections to save {low*5:.0f}% material.")
        if high > 0:
            st.warning(f"⚠️ {high} beams near capacity. Verify under all load combinations.")
        if passed == total:
            st.success("✅ All beams pass design checks!")
        else:
            failed_beams = df[df["is_safe"] == False]["beam_id"].tolist()[:3]
            st.error(f"❌ Failed: {', '.join(failed_beams)}{'...' if len(failed_beams) > 3 else ''}")

    with tab2:
        # Material takeoff
        takeoff = calculate_material_takeoff(df)

        st.markdown("##### Material Quantities")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("🧱 Concrete", f"{takeoff['concrete_m3']:.1f} m³")
            st.caption("All beams combined")

        with col2:
            st.metric("🔩 Reinforcement", f"{takeoff['steel_kg']:.0f} kg")
            st.caption(f"≈ {takeoff['steel_kg']/1000:.2f} tonnes")

        # Steel ratio
        steel_ratio = takeoff['steel_kg'] / (takeoff['concrete_m3'] * 2400) * 100 if takeoff['concrete_m3'] > 0 else 0
        st.metric("Steel Ratio", f"{steel_ratio:.1f}%", help="kg steel per kg concrete")

        # Per-story breakdown if multiple stories
        if "story" in df.columns:
            st.markdown("##### Per-Story Breakdown")
            story_data = []
            for story in df["story"].unique():
                story_df = df[df["story"] == story]
                story_takeoff = calculate_material_takeoff(story_df)
                story_data.append({
                    "Story": story,
                    "Beams": len(story_df),
                    "Concrete (m³)": f"{story_takeoff['concrete_m3']:.1f}",
                    "Steel (kg)": f"{story_takeoff['steel_kg']:.0f}",
                })
            st.dataframe(story_data, hide_index=True, use_container_width=True)

    with tab3:
        # Cost estimate
        takeoff = calculate_material_takeoff(df)

        st.markdown("##### Cost Estimate (INR)")
        st.caption("Rates: Concrete ₹8000/m³ | Steel ₹85/kg")

        col1, col2, col3 = st.columns(3)
        col1.metric("Concrete", f"₹{takeoff['concrete_cost']:,.0f}")
        col2.metric("Steel", f"₹{takeoff['steel_cost']:,.0f}")
        col3.metric("**Total**", f"₹{takeoff['total_cost']:,.0f}")

        # Cost per meter
        total_length = df["span_mm"].sum() / 1000  # m
        cost_per_m = takeoff['total_cost'] / total_length if total_length > 0 else 0

        st.metric("Cost per Running Meter", f"₹{cost_per_m:,.0f}/m", help="Total cost / total beam length")

        # Visualization
        if VISUALIZATION_AVAILABLE:
            cost_data = {
                "Item": ["Concrete", "Steel"],
                "Cost (₹)": [takeoff['concrete_cost'], takeoff['steel_cost']],
            }
            fig = go.Figure(data=[go.Pie(
                labels=cost_data["Item"],
                values=cost_data["Cost (₹)"],
                hole=0.4,
                marker_colors=["#2ecc71", "#3498db"],
            )])
            fig.update_layout(
                height=250,
                margin=dict(l=0, r=0, t=30, b=0),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1),
            )
            st.plotly_chart(fig, use_container_width=True, key="cost_pie")

    with tab4:
        # Export options
        st.markdown("##### Download Design Results")
        st.caption("Export your beam designs for documentation or further analysis")

        # Prepare export data with key columns
        export_cols = ["beam_id", "b_mm", "D_mm", "span_mm", "mu_knm", "vu_kn",
                       "is_safe", "utilization", "ast_provided_mm2", "ast_required_mm2",
                       "main_bars", "stirrup_spacing_mm"]
        export_df = df[[c for c in export_cols if c in df.columns]].copy()

        # Add status column for clarity
        export_df.insert(0, "status", export_df["is_safe"].apply(lambda x: "PASS" if x else "FAIL"))

        # CSV download
        csv_data = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="beam_design_results.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download all beam design results as CSV file",
        )

        # Summary download
        takeoff = calculate_material_takeoff(df)
        summary_text = f"""BEAM DESIGN SUMMARY
====================
Generated by: structural_engineering_lib AI Assistant v2
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

DESIGN SUMMARY
--------------
Total Beams: {len(df)}
Passed: {len(df[df['is_safe']==True])}
Failed: {len(df[df['is_safe']==False])}
Average Utilization: {df['utilization'].mean()*100:.1f}%

MATERIAL TAKEOFF
----------------
Concrete: {takeoff['concrete_m3']:.2f} m³
Steel: {takeoff['steel_kg']:.0f} kg ({takeoff['steel_kg']/1000:.2f} tonnes)

COST ESTIMATE (INR)
-------------------
Concrete (@₹8000/m³): ₹{takeoff['concrete_cost']:,.0f}
Steel (@₹85/kg): ₹{takeoff['steel_cost']:,.0f}
TOTAL: ₹{takeoff['total_cost']:,.0f}
"""
        st.download_button(
            label="📄 Download Summary",
            data=summary_text,
            file_name="beam_design_summary.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download material takeoff and cost summary",
        )

        st.info("💡 **Tip:** Use CSV export to import results into Excel for detailed reporting.")

    # Navigation
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("← Results", use_container_width=True):
            set_workspace_state(WorkspaceState.DESIGN)
            st.rerun()
    with c2:
        if st.button("🏗️ Building 3D", use_container_width=True):
            set_workspace_state(WorkspaceState.BUILDING_3D)
            st.rerun()
    with c3:
        if st.button("📥 New Import", use_container_width=True):
            set_workspace_state(WorkspaceState.IMPORT)
            st.rerun()


def render_dynamic_workspace() -> None:
    """Main workspace renderer - routes to correct state panel."""
    state = st.session_state.ws_state

    # State indicator bar - show progress through workflow
    states_order = [
        WorkspaceState.WELCOME,
        WorkspaceState.IMPORT,
        WorkspaceState.DESIGN,
        WorkspaceState.BUILDING_3D,
        WorkspaceState.VIEW_3D,
    ]

    current_idx = states_order.index(state) if state in states_order else 0
    # Calculate progress (safe division - states_order always has 5 items)
    progress = (current_idx + 1) / max(len(states_order), 1)

    # Compact state badge instead of progress bar
    state_labels = {
        WorkspaceState.WELCOME: "🏠 Welcome",
        WorkspaceState.IMPORT: "📥 Import",
        WorkspaceState.DESIGN: "📊 Design",
        WorkspaceState.BUILDING_3D: "🏗️ Building 3D",
        WorkspaceState.VIEW_3D: "🎨 Beam 3D",
        WorkspaceState.CROSS_SECTION: "📐 Cross-Section",
        WorkspaceState.REBAR_EDIT: "🔧 Rebar Edit",
        WorkspaceState.EDIT: "✏️ Edit",
        WorkspaceState.DASHBOARD: "📈 Dashboard",
    }
    st.caption(f"**{state_labels.get(state, state.value.upper())}**")

    # Route to correct renderer
    if state == WorkspaceState.WELCOME:
        render_welcome_panel()
    elif state == WorkspaceState.IMPORT:
        render_import_preview()
    elif state == WorkspaceState.DESIGN:
        render_design_results()
    elif state == WorkspaceState.BUILDING_3D:
        render_building_3d()
    elif state == WorkspaceState.VIEW_3D:
        render_3d_view()
    elif state == WorkspaceState.CROSS_SECTION:
        render_cross_section()
    elif state == WorkspaceState.REBAR_EDIT:
        render_rebar_editor()
    elif state == WorkspaceState.EDIT:
        render_beam_editor()
    elif state == WorkspaceState.DASHBOARD:
        render_dashboard()
    else:
        st.error(f"Unknown state: {state}")
        render_welcome_panel()
