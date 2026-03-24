# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Export and report generation handler.

Extracted from ai_workspace.py (TASK-508).
Contains HTML report, PDF report, DXF export,
and material takeoff calculation.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

# Import PDF generator (professional reportlab-based reports)
try:
    from utils.pdf_generator import BeamDesignReportGenerator, is_reportlab_available

    PDF_AVAILABLE = is_reportlab_available()
except ImportError:
    PDF_AVAILABLE = False


def _generate_and_download_report(results_df: pd.DataFrame) -> None:
    """Generate and offer download for design report.

    Builds report format from DataFrame and uses structural_lib API.
    """
    if results_df is None or results_df.empty:
        st.error("No results to export")
        return

    try:
        from structural_lib import api

        # Build report-compatible format
        beams_for_report = []
        for _, row in results_df.iterrows():
            beam_data = {
                "beam_id": str(row["beam_id"]),
                "story": str(row.get("story", "")),
                "is_ok": bool(row.get("is_safe", False)),
                "governing_utilization": float(row.get("utilization", 0)),
                "geometry": {
                    "b_mm": float(row["b_mm"]),
                    "D_mm": float(row["D_mm"]),
                    "d_mm": float(row["D_mm"]) - float(row.get("cover_mm", 40)) - 8,
                    "span_mm": float(row["span_mm"]),
                },
                "materials": {
                    "fck": float(row["fck"]),
                    "fy": float(row["fy"]),
                },
                "loads": {
                    "case_id": "DESIGN",
                    "mu_knm": float(row["mu_knm"]),
                    "vu_kn": float(row["vu_kn"]),
                },
                "flexure": {
                    "ast_required_mm2": float(row.get("ast_req", 0)),
                    "utilization": float(row.get("utilization", 0)),
                    "section_type": "under-reinforced",
                },
                "shear": {
                    "is_safe": bool(row.get("is_safe", False)),
                    "utilization": 0.5,
                },
            }
            beams_for_report.append(beam_data)

        report_input = {
            "code": "IS 456:2000",
            "units": "SI",
            "beams": beams_for_report,
            "summary": {
                "total_beams": len(beams_for_report),
                "passed": sum(1 for b in beams_for_report if b["is_ok"]),
                "failed": sum(1 for b in beams_for_report if not b["is_ok"]),
            },
        }

        # High threshold forces single-report mode for in-memory generation
        report_html = api.compute_report(
            report_input, format="html", batch_threshold=10000
        )

        st.download_button(
            label="⬇️ Download Report",
            data=report_html,
            file_name=f"beam_report_{len(beams_for_report)}.html",
            mime="text/html",
            key="ws_report_download",
        )

    except Exception as e:
        st.error(f"Report generation failed: {str(e)}")


def _generate_and_download_pdf_report(results_df: pd.DataFrame) -> None:
    """Generate and offer download for professional PDF report.

    Uses BeamDesignReportGenerator with reportlab for CAD-quality output.
    Generates a combined batch report for all beams with TOC and summary.

    The PDF generator expects specific data keys. This function transforms
    the DataFrame columns to match the expected structure:
    - inputs: span_m, width_mm, depth_mm, effective_depth_mm, cover_mm, fck, fy
    - flexure: Mu_kNm, Mu_lim_kNm, Ast_req_mm2, Ast_min_mm2, Ast_prov_mm2
    - shear: Vu_kN, tau_v, tau_c
    """
    if results_df is None or results_df.empty:
        st.error("No results to export")
        return

    if not PDF_AVAILABLE:
        st.error("PDF export requires reportlab. Install with: pip install reportlab")
        return

    try:
        generator = BeamDesignReportGenerator()

        # Convert DataFrame rows to design data format expected by PDF generator
        design_data_list = []
        for _, row in results_df.iterrows():
            b_mm = float(row["b_mm"])
            D_mm = float(row["D_mm"])
            span_mm = float(row["span_mm"])
            cover_mm = float(row.get("cover_mm", 40))
            fck = float(row["fck"])
            fy = float(row["fy"])
            mu_knm = float(row["mu_knm"])
            vu_kn = float(row["vu_kn"])
            ast_req = float(row.get("ast_req", 0))
            ast_prov = float(row.get("ast_prov", ast_req * 1.1))
            d_eff = D_mm - cover_mm - 8 - 8  # Assume 8mm stirrup + 8mm half bar dia

            # Calculate limiting moment and other values for PDF
            mu_lim = 0.138 * fck * b_mm * d_eff**2 / 1e6  # kN·m
            ast_min = 0.85 * b_mm * d_eff / fy

            design_data = {
                "beam_id": str(row["beam_id"]),
                "story": str(row.get("story", "")),
                "is_safe": bool(row.get("is_safe", False)),
                "inputs": {
                    "span_m": span_mm / 1000,
                    "width_mm": b_mm,
                    "depth_mm": D_mm,
                    "effective_depth_mm": d_eff,
                    "cover_mm": cover_mm,
                    "fck": fck,
                    "fy": fy,
                    "dead_load_kN": 0,
                    "live_load_kN": 0,
                    "factored_load_kN": 0,
                },
                "flexure": {
                    "Mu_kNm": mu_knm,
                    "Mu_lim_kNm": mu_lim,
                    "Ast_req_mm2": ast_req,
                    "Ast_min_mm2": ast_min,
                    "Ast_prov_mm2": ast_prov,
                    "utilization": float(row.get("utilization", 0)),
                    "section_type": "under-reinforced" if mu_knm < mu_lim else "doubly",
                },
                "shear": {
                    "Vu_kN": vu_kn,
                    "tau_v": vu_kn * 1000 / (b_mm * d_eff) if d_eff > 0 else 0,
                    "tau_c": 0.36,  # Approximate for M25, 0.5% steel
                    "is_safe": bool(row.get("is_safe", False)),
                },
            }
            design_data_list.append(design_data)

        # Project info for the batch report
        project_info = {
            "project_name": st.session_state.get("project_name", "Beam Design Project"),
            "location": st.session_state.get("project_location", "N/A"),
            "client": st.session_state.get("project_client", "N/A"),
            "engineer": st.session_state.get("engineer_name", "Structural Engineer"),
        }

        # Generate batch report if multiple beams, single report otherwise
        if len(design_data_list) > 1:
            pdf_buffer = generator.generate_batch_report(
                design_data_list,
                project_info,
                include_bbs=False,
                include_diagrams=False,
            )
            file_name = f"beam_design_report_{len(design_data_list)}_beams.pdf"
            label = f"⬇️ Download Report ({len(design_data_list)} beams)"
        else:
            pdf_buffer = generator.generate_report(
                design_data_list[0],
                project_info,
                include_bbs=False,
                include_diagrams=False,
            )
            beam_id = design_data_list[0]["beam_id"]
            file_name = f"beam_{beam_id}_report.pdf"
            label = f"⬇️ Download Report ({beam_id})"

        st.download_button(
            label=label,
            data=pdf_buffer.getvalue(),
            file_name=file_name,
            mime="application/pdf",
            key="pdf_batch_report",
            use_container_width=True,
        )

        st.success(
            f"✅ Professional PDF report ready ({len(design_data_list)} beam(s))"
        )

    except Exception as e:
        st.error(f"PDF generation failed: {str(e)}")


def _generate_and_download_dxf(results_df: pd.DataFrame) -> None:
    """Generate and offer download for DXF drawings.

    Builds detailing on-the-fly and uses structural_lib API.
    """
    if results_df is None or results_df.empty:
        st.error("No results to export")
        return

    try:
        from structural_lib import api, detailing

        detailing_list = []
        for _, row in results_df.iterrows():
            det_result = detailing.create_beam_detailing(
                beam_id=str(row["beam_id"]),
                story=str(row.get("story", "")),
                b=float(row["b_mm"]),
                D=float(row["D_mm"]),
                span=float(row["span_mm"]),
                cover=float(row.get("cover_mm", 40)),
                fck=float(row["fck"]),
                fy=float(row["fy"]),
                ast_start=float(row.get("ast_req", 0)),
                ast_mid=float(row.get("ast_req", 0)),
                ast_end=float(row.get("ast_req", 0)),
                asc_start=0,
                asc_mid=0,
                asc_end=0,
                stirrup_dia=8.0,
                stirrup_spacing_start=150.0,
                stirrup_spacing_mid=200.0,
                stirrup_spacing_end=150.0,
                is_seismic=False,
            )
            detailing_list.append(det_result)

        if not detailing_list:
            st.error("Could not generate detailing")
            return

        # Generate DXF to temp file
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tmp:
            output_path = tmp.name

        api.compute_dxf(
            detailing_list,
            output_path,
            include_title_block=True,
            multi=len(detailing_list) > 1,
        )

        with open(output_path, "rb") as f:
            dxf_bytes = f.read()

        st.download_button(
            label="⬇️ Download DXF",
            data=dxf_bytes,
            file_name=f"beam_design_{len(detailing_list)}.dxf",
            mime="application/dxf",
            key="ws_dxf_download",
        )

    except ImportError:
        st.error("DXF export requires ezdxf: pip install ezdxf")
    except Exception as e:
        st.error(f"DXF generation failed: {str(e)}")


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
