# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Import and data processing handler.

Extracted from ai_workspace.py (TASK-508).
Contains CSV/Excel import, auto-mapping, adapter integration,
and DataFrame standardization functions.
"""

from __future__ import annotations

import io
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from .workspace_state import (
    COLUMN_PATTERNS,
    SAMPLE_ETABS_DATA,
    WorkspaceState,
)

# Import adapter system (reusing proven infrastructure from multi-format import)
try:
    from structural_lib.services.adapters import (
        ETABSAdapter,
        SAFEAdapter,
        GenericCSVAdapter,
    )
    from structural_lib.core.models import (
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
        result["span_mm"] = pd.to_numeric(
            df[mapping["span_mm"]], errors="coerce"
        ).fillna(5000)
    else:
        result["span_mm"] = 5000

    # Forces
    if "mu_knm" in mapping:
        result["mu_knm"] = pd.to_numeric(df[mapping["mu_knm"]], errors="coerce").fillna(
            100
        )
    else:
        result["mu_knm"] = 100

    if "vu_kn" in mapping:
        result["vu_kn"] = pd.to_numeric(df[mapping["vu_kn"]], errors="coerce").fillna(
            50
        )
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
        story_heights = {
            s: i * 3.0 for i, s in enumerate(sorted(stories))
        }  # 3m per story

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
    geometry_file: Any,
    forces_file: Any,
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

        rows.append(
            {
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
            }
        )

    return pd.DataFrame(rows)


def process_uploaded_file(file: Any) -> tuple[bool, str]:
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


def process_multi_files(geometry_file: Any, forces_file: Any) -> tuple[bool, str]:
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
            if geometry_file.name.endswith(".xlsx"):
                geo_df = pd.read_excel(geometry_file)
            else:
                geo_df = pd.read_csv(geometry_file)

        # Read forces file
        if forces_file:
            if forces_file.name.endswith(".xlsx"):
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
                    suffixes=("", "_forces"),
                )

                # Combine mappings
                combined_mapping = {**geo_mapping}
                for key, col in forces_mapping.items():
                    if key not in combined_mapping:
                        combined_mapping[key] = col

                st.session_state.ws_beams_df = standardize_dataframe(
                    merged_df, combined_mapping, st.session_state.ws_defaults
                )
                return (
                    True,
                    f"✅ Merged {len(geo_df)} geometry + {len(forces_df)} forces → {len(merged_df)} beams",
                )
            else:
                # Fallback: just use geometry with defaults for forces
                mapping = auto_map_columns(geo_df)
                st.session_state.ws_beams_df = standardize_dataframe(
                    geo_df, mapping, st.session_state.ws_defaults
                )
                return (
                    True,
                    "⚠️ Could not match beam IDs. Using geometry with default forces.",
                )

        return False, "No files provided"

    except Exception as e:
        return False, f"Error processing files: {e}"
