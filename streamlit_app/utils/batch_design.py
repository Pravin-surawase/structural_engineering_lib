"""Shared batch design utilities for designing multiple beams.

This module consolidates duplicate implementations from:
- components/ai_workspace.py:678 (design_beam_row) + :751 (design_all_beams_ws)
- pages/06_multi_format_import.py:606 (design_all_beams)
- pages/_hidden/_06_etabs_import.py:240 (design_beam)

All had similar logic for calling the library's design function and formatting results.
This is the canonical version that:
- Uses cached_design from api_wrapper.py for performance
- Returns consistent output format
- Handles errors gracefully

Created: Session 63 (Jan 23, 2026)
Related: TASK-351
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from .api_wrapper import cached_design

if TYPE_CHECKING:
    from collections.abc import Callable


def design_single_beam(
    b_mm: float,
    D_mm: float,
    mu_knm: float,
    vu_kn: float,
    fck: float = 25.0,
    fy: float = 500.0,
    cover_mm: float = 40.0,
) -> dict[str, Any]:
    """Design a single beam and return standardized results.

    This wraps the library's design function and returns a dict suitable for
    DataFrame storage and UI display.

    Args:
        b_mm: Beam width in mm
        D_mm: Beam total depth in mm
        mu_knm: Ultimate moment in kN·m
        vu_kn: Ultimate shear in kN
        fck: Concrete strength in N/mm²
        fy: Steel yield strength in N/mm²
        cover_mm: Clear cover in mm

    Returns:
        dict with:
            - ast_req: Required steel area (mm²)
            - ast_prov: Provided steel area (mm²) or None if failed
            - utilization: Utilization ratio (0-100+)
            - is_safe: Boolean pass/fail
            - status: Status emoji + text
            - flexure: Full flexure result dict
            - shear: Full shear result dict
            - error: Error message if design failed
    """
    try:
        d_mm = D_mm - cover_mm - 8 - 8  # Effective depth (stirrup + half bar)

        result = cached_design(
            mu_knm=mu_knm,
            vu_kn=vu_kn,
            b_mm=b_mm,
            D_mm=D_mm,
            d_mm=d_mm,
            fck_nmm2=fck,
            fy_nmm2=fy,
        )

        flexure = result.get("flexure", {})
        shear = result.get("shear", {})
        is_safe = result.get("is_safe", False)

        ast_req = flexure.get("ast_required", 0)
        mu_capacity = flexure.get("mu_capacity_knm", 0)

        # Calculate utilization
        utilization = 0.0
        if mu_capacity > 0:
            utilization = (mu_knm / mu_capacity) * 100

        # Status with emoji
        if is_safe:
            status = f"✅ Pass ({utilization:.0f}%)"
        else:
            shortfall = ast_req - flexure.get("ast_provided", ast_req)
            status = f"❌ Fail ({shortfall:.0f} mm² short)"

        return {
            "ast_req": ast_req,
            "ast_prov": flexure.get("ast_provided"),
            "utilization": utilization,
            "is_safe": is_safe,
            "status": status,
            "flexure": flexure,
            "shear": shear,
            "error": None,
        }

    except Exception as e:
        return {
            "ast_req": 0,
            "ast_prov": None,
            "utilization": 0,
            "is_safe": False,
            "status": f"⚠️ Error",
            "flexure": {},
            "shear": {},
            "error": str(e),
        }


def design_beam_row(row: pd.Series) -> dict[str, Any]:
    """Design a single beam from a DataFrame row.

    This is a convenience wrapper for DataFrame.apply() operations.

    Args:
        row: DataFrame row with columns:
            - b_mm, D_mm: Geometry
            - mu_knm, vu_kn: Forces
            - fck, fy: Materials (optional, defaults to M25/Fe500)
            - cover_mm: Cover (optional, defaults to 40)

    Returns:
        dict suitable for creating result row in DataFrame
    """
    try:
        b_mm = float(row.get("b_mm", row.get("width_mm", 300)))
        D_mm = float(row.get("D_mm", row.get("depth_mm", 450)))
        mu_knm = float(row.get("mu_knm", row.get("Mu_kNm", 0)))
        vu_kn = float(row.get("vu_kn", row.get("Vu_kN", 0)))
        fck = float(row.get("fck", row.get("fck_mpa", 25)))
        fy = float(row.get("fy", row.get("fy_mpa", 500)))
        cover_mm = float(row.get("cover_mm", 40))

        return design_single_beam(
            b_mm=b_mm,
            D_mm=D_mm,
            mu_knm=mu_knm,
            vu_kn=vu_kn,
            fck=fck,
            fy=fy,
            cover_mm=cover_mm,
        )
    except Exception as e:
        return {
            "ast_req": 0,
            "ast_prov": None,
            "utilization": 0,
            "is_safe": False,
            "status": "⚠️ Error",
            "flexure": {},
            "shear": {},
            "error": str(e),
        }


def design_all_beams_df(
    df: pd.DataFrame,
    progress_callback: Callable[[float, str], None] | None = None,
) -> pd.DataFrame:
    """Design all beams in a DataFrame and return results.

    This is the main batch design function that should be used by all pages.

    Args:
        df: DataFrame with beam data. Required columns:
            - beam_id (or ID): Unique identifier
            - b_mm (or width_mm): Width in mm
            - D_mm (or depth_mm): Depth in mm
            - mu_knm (or Mu_kNm): Moment in kN·m
            - vu_kn (or Vu_kN): Shear in kN
            Optional columns:
            - fck, fy: Material properties
            - cover_mm: Clear cover
            - story: Story level
            - span_mm: Span length

        progress_callback: Optional function(progress: float, message: str)
            to report progress. Progress is 0.0-1.0.

    Returns:
        DataFrame with design results added:
            - ast_req, ast_prov, utilization, is_safe, status
    """
    if df is None or df.empty:
        return pd.DataFrame()

    results = []
    total = len(df)

    for idx, (_, row) in enumerate(df.iterrows()):
        # Report progress
        if progress_callback and total > 0:
            progress = (idx + 1) / total
            beam_id = row.get("beam_id", row.get("ID", f"Beam {idx + 1}"))
            progress_callback(progress, f"Designing {beam_id}... ({idx + 1}/{total})")

        # Design this beam
        design = design_beam_row(row)

        # Build result row with original data + design results
        result_row = row.to_dict()
        result_row.update(
            {
                "ast_req": design["ast_req"],
                "utilization": design["utilization"],
                "is_safe": design["is_safe"],
                "status": design["status"],
            }
        )
        results.append(result_row)

    return pd.DataFrame(results)


def design_beams_with_streamlit_progress(
    df: pd.DataFrame,
    progress_bar: st.delta_generator.DeltaGenerator,
    status_text: st.delta_generator.DeltaGenerator,
) -> pd.DataFrame:
    """Design beams with Streamlit progress bar and status text.

    Convenience wrapper for use in Streamlit pages.

    Args:
        df: DataFrame with beam data
        progress_bar: Streamlit progress bar widget
        status_text: Streamlit text widget for status messages

    Returns:
        DataFrame with design results
    """

    def callback(progress: float, message: str) -> None:
        progress_bar.progress(progress)
        status_text.text(message)

    return design_all_beams_df(df, progress_callback=callback)
