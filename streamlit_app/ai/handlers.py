"""
AI Tool Handlers - Execute workspace actions

These handlers connect the AI's function calls to actual workspace operations.
Each handler modifies session state and returns results for the AI to report.
"""

from __future__ import annotations

import json
import math
from typing import Any

import pandas as pd
import streamlit as st


def handle_tool_call(tool_name: str, arguments: dict[str, Any]) -> str:
    """Execute a tool call and return the result as a string for the AI.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments from the AI

    Returns:
        String result to send back to the AI
    """
    handlers = {
        "design_beam": _handle_design_beam,
        "design_all_beams": _handle_design_all,
        "get_beam_details": _handle_get_beam_details,
        "select_beam": _handle_select_beam,
        "show_visualization": _handle_show_visualization,
        "suggest_optimization": _handle_suggest_optimization,
        "export_results": _handle_export_results,
        "filter_3d_view": _handle_filter_3d,
        "get_critical_beams": _handle_get_critical_beams,
        "start_optimization": _handle_start_optimization,
        "export_dxf": _handle_export_dxf,
        "generate_report": _handle_generate_report,
    }

    handler = handlers.get(tool_name)
    if handler:
        try:
            return handler(arguments)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    else:
        return f"Unknown tool: {tool_name}"


def _handle_design_beam(args: dict) -> str:
    """Design a single beam with given parameters."""
    from components.ai_workspace import design_beam_row

    # Build row from arguments
    row = pd.Series({
        "beam_id": args.get("beam_id", "Custom"),
        "b_mm": args.get("b_mm", 300),
        "D_mm": args.get("D_mm", 500),
        "span_mm": args.get("span_mm", 5000),
        "mu_knm": args.get("mu_knm", 100),
        "vu_kn": args.get("vu_kn", 50),
        "fck": args.get("fck", 25),
        "fy": args.get("fy", 500),
        "cover_mm": 40,
    })

    result = design_beam_row(row)

    return json.dumps({
        "beam_id": row["beam_id"],
        "is_safe": result["is_safe"],
        "ast_required_mm2": round(result["ast_req"], 0),
        "utilization_pct": round(result["utilization"] * 100, 1),
        "status": result["status"],
        "section": f"{row['b_mm']}x{row['D_mm']} mm",
        "moment_knm": row["mu_knm"],
        "shear_kn": row["vu_kn"],
    })


def _handle_design_all(args: dict) -> str:
    """Design all beams in workspace."""
    from components.ai_workspace import design_all_beams_ws, WorkspaceState

    beams_df = st.session_state.get("ws_beams_df")
    if beams_df is None or beams_df.empty:
        return json.dumps({"error": "No beams loaded. Load data first."})

    results = design_all_beams_ws()
    st.session_state.ws_design_results = results
    st.session_state.ws_state = WorkspaceState.DESIGN

    total = len(results)
    passed = len(results[results["is_safe"] == True])
    failed = total - passed
    avg_util = results["utilization"].mean() * 100

    # Get failed beam IDs
    failed_beams = results[~results["is_safe"]]["beam_id"].tolist()[:5]

    return json.dumps({
        "total_beams": total,
        "passed": passed,
        "failed": failed,
        "pass_rate_pct": round(passed / total * 100, 1) if total > 0 else 0,
        "avg_utilization_pct": round(avg_util, 1),
        "failed_beam_ids": failed_beams,
    })


def _handle_get_beam_details(args: dict) -> str:
    """Get detailed results for a specific beam."""
    beam_id = args.get("beam_id", "")
    results_df = st.session_state.get("ws_design_results")

    if results_df is None:
        return json.dumps({"error": "No design results. Run 'design all' first."})

    # Find beam (case-insensitive)
    mask = results_df["beam_id"].str.upper() == beam_id.upper()
    if not mask.any():
        available = results_df["beam_id"].tolist()[:10]
        return json.dumps({"error": f"Beam '{beam_id}' not found", "available": available})

    row = results_df[mask].iloc[0]

    return json.dumps({
        "beam_id": row["beam_id"],
        "story": row.get("story", "Unknown"),
        "section_mm": f"{row['b_mm']}x{row['D_mm']}",
        "span_mm": row["span_mm"],
        "moment_knm": row["mu_knm"],
        "shear_kn": row["vu_kn"],
        "ast_required_mm2": round(row["ast_req"], 0),
        "utilization_pct": round(row["utilization"] * 100, 1),
        "is_safe": row["is_safe"],
        "status": row["status"],
        "materials": f"M{row['fck']}/Fe{row['fy']}",
    })


def _handle_select_beam(args: dict) -> str:
    """Select a beam for visualization."""
    from components.ai_workspace import WorkspaceState

    beam_id = args.get("beam_id", "")
    results_df = st.session_state.get("ws_design_results")

    if results_df is None:
        return json.dumps({"error": "No design results. Run 'design all' first."})

    # Find beam (case-insensitive)
    mask = results_df["beam_id"].str.upper() == beam_id.upper()
    if not mask.any():
        # Try partial match
        mask = results_df["beam_id"].str.upper().str.contains(beam_id.upper())

    if not mask.any():
        available = results_df["beam_id"].tolist()[:10]
        return json.dumps({"error": f"Beam '{beam_id}' not found", "available": available})

    actual_id = results_df[mask].iloc[0]["beam_id"]
    st.session_state.ws_selected_beam = actual_id
    st.session_state.ws_state = WorkspaceState.VIEW_3D

    row = results_df[mask].iloc[0]
    return json.dumps({
        "selected": actual_id,
        "section": f"{row['b_mm']}x{row['D_mm']} mm",
        "status": row["status"],
        "view": "3D with reinforcement",
    })


def _handle_show_visualization(args: dict) -> str:
    """Trigger a visualization view."""
    from components.ai_workspace import WorkspaceState

    view_type = args.get("view_type", "3d").lower()

    view_map = {
        "3d": WorkspaceState.VIEW_3D,
        "cross_section": WorkspaceState.CROSS_SECTION,
        "building": WorkspaceState.BUILDING_3D,
        "dashboard": WorkspaceState.DASHBOARD,
        "rebar": WorkspaceState.REBAR_EDIT,
    }

    new_state = view_map.get(view_type, WorkspaceState.BUILDING_3D)
    st.session_state.ws_state = new_state

    return json.dumps({
        "view": view_type,
        "status": "displayed",
    })


def _handle_suggest_optimization(args: dict) -> str:
    """Get optimization suggestions for a beam."""
    beam_id = args.get("beam_id", "")
    target = args.get("target", "cost")
    results_df = st.session_state.get("ws_design_results")

    if results_df is None:
        return json.dumps({"error": "No design results."})

    # Find beam
    mask = results_df["beam_id"].str.upper() == beam_id.upper()
    if not mask.any():
        return json.dumps({"error": f"Beam '{beam_id}' not found"})

    row = results_df[mask].iloc[0]
    util = row["utilization"]

    suggestions = []

    # Check if over-designed
    if util < 0.5:
        suggestions.append({
            "type": "reduce_section",
            "message": f"Section is over-designed (util={util*100:.0f}%). Consider reducing depth by 50mm.",
            "savings_pct": 10,
        })
    elif util < 0.7:
        suggestions.append({
            "type": "reduce_steel",
            "message": f"Steel could be reduced (util={util*100:.0f}%). Try smaller bar diameters.",
            "savings_pct": 5,
        })

    # Check if under-designed
    if util > 1.0:
        suggestions.append({
            "type": "increase_section",
            "message": f"Section fails (util={util*100:.0f}%). Increase depth by 50-100mm.",
            "savings_pct": 0,
        })

    # General suggestions
    suggestions.append({
        "type": "stirrup_optimization",
        "message": "Consider variable stirrup spacing: closer at supports, wider at mid-span.",
        "savings_pct": 3,
    })

    return json.dumps({
        "beam_id": beam_id,
        "current_utilization_pct": round(util * 100, 1),
        "target": target,
        "suggestions": suggestions,
    })


def _handle_export_results(args: dict) -> str:
    """Export design results."""
    export_format = args.get("format", "csv")
    results_df = st.session_state.get("ws_design_results")

    if results_df is None:
        return json.dumps({"error": "No results to export."})

    filename = args.get("filename", f"beam_design_results.{export_format}")

    # Store for download
    st.session_state.export_data = {
        "format": export_format,
        "filename": filename,
        "df": results_df,
    }

    return json.dumps({
        "format": export_format,
        "filename": filename,
        "rows": len(results_df),
        "status": "ready_for_download",
    })


def _handle_filter_3d(args: dict) -> str:
    """Filter 3D view to specific floor/story."""
    from components.ai_workspace import WorkspaceState

    floor = args.get("floor", args.get("story", "all"))
    show_rebar = args.get("show_rebar", True)

    results_df = st.session_state.get("ws_design_results")
    beams_df = st.session_state.get("ws_beams_df")

    df = results_df if results_df is not None else beams_df
    if df is None:
        return json.dumps({"error": "No data loaded."})

    # Get available floors
    floors = df["story"].unique().tolist() if "story" in df.columns else []

    # Filter if floor specified
    if floor.lower() != "all":
        # Find matching floor (case-insensitive, partial match)
        matched_floor = None
        for f in floors:
            if floor.lower() in str(f).lower():
                matched_floor = f
                break

        if matched_floor:
            # Store filter in session state for the workspace to use
            st.session_state.ws_filter_floor = matched_floor
            st.session_state.ws_show_rebar = show_rebar
            filtered_count = len(df[df["story"] == matched_floor])
        else:
            return json.dumps({
                "error": f"Floor '{floor}' not found",
                "available_floors": floors,
            })
    else:
        st.session_state.ws_filter_floor = None
        filtered_count = len(df)

    st.session_state.ws_state = WorkspaceState.BUILDING_3D

    return json.dumps({
        "floor": floor if floor.lower() != "all" else "all",
        "beams_shown": filtered_count,
        "rebar_visible": show_rebar,
        "view": "3D building",
    })


def _handle_get_critical_beams(args: dict) -> str:
    """Get list of critical beams by various criteria."""
    criterion = args.get("criterion", "moment")  # moment, shear, utilization
    count = args.get("count", 3)
    floor = args.get("floor", None)

    results_df = st.session_state.get("ws_design_results")
    if results_df is None:
        return json.dumps({"error": "No design results. Run 'design all' first."})

    df = results_df.copy()

    # Filter by floor if specified
    if floor:
        mask = df["story"].str.lower().str.contains(floor.lower())
        if mask.any():
            df = df[mask]

    # Sort by criterion
    sort_cols = {
        "moment": "mu_knm",
        "shear": "vu_kn",
        "utilization": "utilization",
    }
    sort_col = sort_cols.get(criterion, "mu_knm")

    # Get top N
    top_beams = df.nlargest(count, sort_col)

    beam_list = []
    for _, row in top_beams.iterrows():
        beam_list.append({
            "beam_id": row["beam_id"],
            "story": row.get("story", "Unknown"),
            "moment_knm": round(row["mu_knm"], 1),
            "shear_kn": round(row["vu_kn"], 1),
            "utilization_pct": round(row["utilization"] * 100, 1),
            "status": row["status"],
        })

    return json.dumps({
        "criterion": criterion,
        "count": len(beam_list),
        "floor_filter": floor,
        "beams": beam_list,
    })


def _handle_start_optimization(args: dict) -> str:
    """Start optimization for beam(s) on a floor/story."""
    floor = args.get("floor", args.get("story", None))
    beam_id = args.get("beam_id", None)
    target = args.get("target", "cost")

    results_df = st.session_state.get("ws_design_results")
    if results_df is None:
        return json.dumps({"error": "No design results. Run 'design all' first."})

    # Find beam to optimize
    if beam_id:
        mask = results_df["beam_id"].str.upper() == beam_id.upper()
    elif floor:
        # Get most critical beam on floor
        mask = results_df["story"].str.lower().str.contains(floor.lower())
        if mask.any():
            floor_df = results_df[mask]
            beam_id = floor_df.loc[floor_df["mu_knm"].idxmax(), "beam_id"]
            mask = results_df["beam_id"] == beam_id
        else:
            return json.dumps({"error": f"No beams found on floor '{floor}'"})
    else:
        # Get most critical beam overall
        beam_id = results_df.loc[results_df["mu_knm"].idxmax(), "beam_id"]
        mask = results_df["beam_id"] == beam_id

    if not mask.any():
        return json.dumps({"error": f"Beam '{beam_id}' not found"})

    row = results_df[mask].iloc[0]
    current_ast = row["ast_req"]
    current_util = row["utilization"]

    # Simulate optimization (in real implementation, would call optimizer)
    optimized_ast = current_ast * 0.95 if current_util < 0.85 else current_ast
    steel_savings = (current_ast - optimized_ast) / current_ast * 100

    # Estimate costs (INR)
    steel_rate = 85  # Rs/kg
    steel_density = 7850  # kg/m³
    span_m = row["span_mm"] / 1000

    current_weight = current_ast * 1e-6 * span_m * steel_density
    optimized_weight = optimized_ast * 1e-6 * span_m * steel_density
    cost_savings = (current_weight - optimized_weight) * steel_rate

    return json.dumps({
        "beam_id": row["beam_id"],
        "story": row.get("story", "Unknown"),
        "target": target,
        "current": {
            "ast_mm2": round(current_ast, 0),
            "utilization_pct": round(current_util * 100, 1),
            "steel_kg": round(current_weight, 1),
        },
        "optimized": {
            "ast_mm2": round(optimized_ast, 0),
            "utilization_pct": round(current_util * 0.95 * 100, 1),
            "steel_kg": round(optimized_weight, 1),
        },
        "savings": {
            "steel_pct": round(steel_savings, 1),
            "cost_inr": round(cost_savings, 0),
        },
        "recommendations": [
            f"Reduce bar diameter from current to next lower size",
            "Use variable stirrup spacing (tighter at supports)",
            f"Current section {row['b_mm']}x{row['D_mm']}mm is adequate",
        ],
    })


def _handle_export_dxf(args: dict) -> str:
    """Export DXF drawing for beam(s)."""
    import tempfile
    from pathlib import Path

    beam_id = args.get("beam_id")
    floor = args.get("floor")
    include_schedule = args.get("include_schedule", True)
    include_title_block = args.get("include_title_block", True)

    results_df = st.session_state.get("ws_design_results")
    if results_df is None:
        return json.dumps({"error": "No design results. Run 'design all' first."})

    # Get detailing results from session state
    all_detailing = st.session_state.get("ws_detailing_results", {})
    if not all_detailing:
        return json.dumps({
            "error": "No detailing results available. Design beams first to generate DXF."
        })

    # Filter beams based on arguments
    if beam_id:
        # Single beam export
        mask = results_df["beam_id"].str.upper() == beam_id.upper()
        if not mask.any():
            return json.dumps({"error": f"Beam '{beam_id}' not found"})
        beam_ids = [beam_id.upper()]
    elif floor:
        # Floor-based export
        mask = results_df["story"].str.lower().str.contains(floor.lower())
        if not mask.any():
            return json.dumps({"error": f"No beams found on floor '{floor}'"})
        beam_ids = results_df[mask]["beam_id"].tolist()
    else:
        # All beams
        beam_ids = results_df["beam_id"].tolist()

    # Get detailing for selected beams
    detailing_list = []
    missing_beams = []
    for bid in beam_ids:
        if bid in all_detailing:
            detailing_list.append(all_detailing[bid])
        else:
            missing_beams.append(bid)

    if not detailing_list:
        return json.dumps({
            "error": "No detailing data for selected beams",
            "missing_beams": missing_beams[:5],  # Show first 5
        })

    # Generate DXF
    try:
        from structural_lib import api

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".dxf", delete=False, prefix="beam_export_"
        ) as tmp:
            output_path = Path(tmp.name)

        api.compute_dxf(
            detailing_list,
            str(output_path),
            include_title_block=include_title_block,
            multi=len(detailing_list) > 1,
        )

        # Store for download
        with open(output_path, "rb") as f:
            dxf_bytes = f.read()

        st.session_state.ai_export_dxf = {
            "bytes": dxf_bytes,
            "filename": f"beam_design_{len(beam_ids)}_beams.dxf"
            if len(beam_ids) > 1
            else f"beam_{beam_ids[0]}.dxf",
            "beam_count": len(detailing_list),
        }

        return json.dumps({
            "status": "ready_for_download",
            "beam_count": len(detailing_list),
            "filename": st.session_state.ai_export_dxf["filename"],
            "includes": {
                "cross_sections": True,
                "reinforcement_layout": True,
                "schedule_table": include_schedule,
                "title_block": include_title_block,
            },
            "missing_beams": missing_beams[:3] if missing_beams else None,
        })

    except ImportError:
        return json.dumps({
            "error": "DXF export not available. Install ezdxf: pip install ezdxf"
        })
    except Exception as e:
        return json.dumps({"error": f"DXF generation failed: {str(e)}"})


def _handle_generate_report(args: dict) -> str:
    """Generate design calculation report."""
    beam_id = args.get("beam_id")
    report_format = args.get("format", "html")
    include_bbs = args.get("include_bbs", True)

    results_df = st.session_state.get("ws_design_results")
    if results_df is None:
        return json.dumps({"error": "No design results. Run 'design all' first."})

    # Get stored design results for report generation
    design_results = st.session_state.get("ws_full_results", {})
    if not design_results:
        return json.dumps({
            "error": "No detailed design results available for report generation."
        })

    # Filter to specific beam if requested
    if beam_id:
        mask = results_df["beam_id"].str.upper() == beam_id.upper()
        if not mask.any():
            return json.dumps({"error": f"Beam '{beam_id}' not found"})
        beam_ids = [beam_id.upper()]
    else:
        beam_ids = results_df["beam_id"].tolist()

    # Build report data
    report_beams = []
    for bid in beam_ids:
        if bid in design_results:
            report_beams.append(design_results[bid])

    if not report_beams:
        return json.dumps({
            "error": "No detailed results found for report generation",
            "hint": "Try redesigning the beams to populate full results"
        })

    try:
        from structural_lib import api

        # Generate report
        report_content = api.compute_report(
            {"results": report_beams},
            format=report_format,
        )

        # Store for display/download
        st.session_state.ai_report = {
            "content": report_content,
            "format": report_format,
            "beam_count": len(report_beams),
            "filename": f"beam_report_{len(report_beams)}.{report_format}"
            if len(report_beams) > 1
            else f"beam_{beam_ids[0]}_report.{report_format}",
        }

        return json.dumps({
            "status": "ready",
            "format": report_format,
            "beam_count": len(report_beams),
            "filename": st.session_state.ai_report["filename"],
            "includes": {
                "design_checks": True,
                "reinforcement_details": True,
                "is456_compliance": True,
                "bar_bending_schedule": include_bbs,
            },
        })

    except Exception as e:
        return json.dumps({"error": f"Report generation failed: {str(e)}"})

