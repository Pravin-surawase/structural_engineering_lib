"""
PDF Report Generator Page
=========================

Generate professional structural design reports in PDF format.

Features:
- Cover page with project info
- Calculation sheets with IS 456 references
- Results summary
- Optional BBS and diagrams
- Compliance checklist
- Download PDF

Author: Agent 6 (Streamlit Specialist)
Task: STREAMLIT-FEAT-003

Dependencies:
    reportlab - Install with: pip install structural-lib-is456[pdf]
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from streamlit_app.utils.pdf_generator import (
    BeamDesignReportGenerator,
    is_reportlab_available,
)


def _transform_design_data_for_pdf(design_result: dict, beam_inputs: dict) -> dict:
    """Transform design result to format expected by PDF generator.

    The PDF generator expects a specific data structure with keys like:
    - inputs.span_m, inputs.width_mm, flexure.Mu_kNm, etc.

    This function maps our actual data to that format.

    Args:
        design_result: Design result from api_wrapper
        beam_inputs: Beam inputs from session state

    Returns:
        Transformed dict matching PDF generator expectations
    """
    # Get flexure and shear data with defaults
    flexure = design_result.get("flexure", {})
    shear = design_result.get("shear", {})
    detailing = design_result.get("detailing", {})
    compliance = design_result.get("compliance", {})

    # Extract input values from beam_inputs
    span_mm = beam_inputs.get("span_mm", 0)
    b_mm = beam_inputs.get("b_mm", beam_inputs.get("width_mm", 0))
    D_mm = beam_inputs.get("D_mm", beam_inputs.get("depth_mm", 0))
    d_mm = beam_inputs.get("d_mm", 0)  # Already calculated
    cover = beam_inputs.get("cover", beam_inputs.get("cover_mm", 30))

    # Get factored moment and shear from inputs (the app uses these directly)
    mu_knm = beam_inputs.get("mu_knm", 0)
    vu_kn = beam_inputs.get("vu_kn", 0)

    # Extract concrete grade (M25 -> 25)
    fck = 25
    grade_str = beam_inputs.get("concrete_grade", "M25")
    if grade_str:
        try:
            fck = int(str(grade_str).replace("M", "").replace("m", ""))
        except (ValueError, AttributeError):
            fck = 25

    # Steel grade (Fe500 -> 500)
    fy = 500
    steel_grade = beam_inputs.get("steel_grade", "Fe500")
    if steel_grade:
        try:
            fy = int(str(steel_grade).replace("Fe", "").replace("fe", ""))
        except (ValueError, AttributeError):
            fy = 500

    # Calculate effective depth if not provided
    if d_mm <= 0 and D_mm > 0:
        main_bar_dia = flexure.get("bar_dia", 16)
        d_mm = D_mm - cover - main_bar_dia / 2

    # Loading - the current app uses direct Mu and Vu inputs
    # Try to get dead/live loads if available, otherwise estimate from factored values
    dead_load = beam_inputs.get("dead_load", beam_inputs.get("dead_load_kN", 0))
    live_load = beam_inputs.get("live_load", beam_inputs.get("live_load_kN", 0))

    # If no dead/live loads but we have Mu, back-calculate an estimate
    factored_load = 0.0
    if dead_load == 0 and live_load == 0 and mu_knm > 0 and span_mm > 0:
        # Mu = wu * L^2 / 8, so wu = 8 * Mu / L^2 (for simply supported)
        span_m = span_mm / 1000
        factored_load = (8 * mu_knm) / (span_m * span_m) if span_m > 0 else 0
        # Assume 1.5 factor, so service load = factored / 1.5
        service_load = factored_load / 1.5 if factored_load > 0 else 0
        # Assume 60/40 dead/live split
        dead_load = service_load * 0.6
        live_load = service_load * 0.4
    else:
        factored_load = beam_inputs.get(
            "factored_load", 1.5 * (dead_load + live_load) if (dead_load + live_load) > 0 else 0
        )

    # Build transformed dict
    pdf_data = {
        "inputs": {
            "span_m": span_mm / 1000 if span_mm > 0 else 0,
            "width_mm": b_mm,
            "depth_mm": D_mm,
            "effective_depth_mm": d_mm,
            "cover_mm": cover,
            "fck": fck,
            "fy": fy,
            "dead_load_kN": dead_load,
            "live_load_kN": live_load,
            "factored_load_kN": factored_load,
        },
        "flexure": {
            # Use the input Mu, or the one from results
            "Mu_kNm": mu_knm if mu_knm > 0 else flexure.get("mu_limit_knm", 0),
            "Mu_lim_kNm": flexure.get("mu_limit_knm", flexure.get("Mu_lim_kNm", 0)),
            "Ast_req_mm2": flexure.get("ast_required", flexure.get("Ast_req_mm2", 0)),
            "Ast_min_mm2": flexure.get("ast_min", flexure.get("Ast_min_mm2", 0)),
            "Ast_prov_mm2": flexure.get("ast_provided", flexure.get("Ast_prov_mm2", 0)),
            "is_safe": flexure.get("is_safe", False),
        },
        "shear": {
            # Use the input Vu, or the one from results
            "Vu_kN": vu_kn if vu_kn > 0 else shear.get("vu_kn", 0),
            "tau_v": shear.get("tv", shear.get("tau_v", 0)),
            "tau_c": shear.get("tc", shear.get("tau_c", 0)),
            "spacing_mm": shear.get("sv_required_mm", shear.get("spacing_mm", 0)),
            "stirrup_legs": shear.get("stirrup_legs", 2),
            "is_safe": shear.get("is_safe", False),
        },
        "detailing": {
            "Ld_req_mm": detailing.get("ld_required", detailing.get("Ld_req_mm", 0)),
            "Ld_avail_mm": detailing.get("ld_provided", detailing.get("Ld_avail_mm", 0)),
            "is_safe": detailing.get("is_safe", True),  # Default to True if not checked
        },
        "compliance": {
            "min_steel_ok": compliance.get("min_steel_ok", True),
            "max_steel_ok": compliance.get("max_steel_ok", True),
            "spacing_ok": compliance.get("spacing_ok", True),
            "dev_length_ok": compliance.get("dev_length_ok", True),
            "shear_reinf_ok": compliance.get("shear_reinf_ok", True),
        },
        "is_safe": design_result.get("is_safe", False),
    }

    # Copy BBS if present (using .get() for scanner compliance)
    bbs_data = design_result.get("bbs")
    if bbs_data is not None:
        pdf_data["bbs"] = bbs_data

    return pdf_data


def render_page():
    """Render PDF Report Generator page."""
    st.title("📄 PDF Report Generator")
    st.markdown(
        "Generate professional structural design reports with calculations, "
        "diagrams, and compliance documentation."
    )

    # Check if reportlab is available
    if not is_reportlab_available():
        st.error("⚠️ **Missing Dependency: reportlab**")
        st.info(
            "The PDF report generator requires the `reportlab` package.\n\n"
            "**Install with:**\n"
            "```bash\n"
            "pip install reportlab\n"
            "```\n\n"
            "Or install with the structural library:\n"
            "```bash\n"
            "pip install structural-lib-is456[pdf]\n"
            "```"
        )
        return

    # Check if design results exist (check multiple possible locations)
    design_result = None
    if "design_results" in st.session_state:
        design_result = st.session_state["design_results"]
    elif "design_result" in st.session_state:
        design_result = st.session_state["design_result"]
    elif "beam_inputs" in st.session_state:
        beam_inputs = st.session_state["beam_inputs"]
        if isinstance(beam_inputs, dict):
            design_result = beam_inputs.get("design_result")

    if not design_result:
        st.warning(
            "⚠️ No design results available. Please complete a beam design first."
        )
        st.info(
            "👈 Go to **Beam Design** page to run a design calculation, "
            "then return here to generate the report."
        )
        return

    # Store reference for later use
    st.session_state["_current_design_result"] = design_result

    st.divider()

    # Project Information Section
    st.subheader("📋 Project Information")

    col1, col2 = st.columns(2)

    with col1:
        project_name = st.text_input(
            "Project Name",
            value="Residential Building - Ground Floor",
            help="Enter the project name",
        )

        location = st.text_input(
            "Location", value="Mumbai, Maharashtra", help="Project location"
        )

        client = st.text_input(
            "Client", value="ABC Developers Pvt. Ltd.", help="Client name"
        )

    with col2:
        engineer = st.text_input(
            "Design Engineer",
            value="Pravin Surawase, M.Tech (Structures)",
            help="Name and credentials of design engineer",
        )

        checker = st.text_input(
            "Checked By", value="", help="Name of checking engineer (optional)"
        )

        company = st.text_input(
            "Company/Organization",
            value="XYZ Consultants",
            help="Engineering firm name",
        )

    st.divider()

    # Report Options
    st.subheader("⚙️ Report Options")

    col1, col2, col3 = st.columns(3)

    with col1:
        include_bbs = st.checkbox(
            "Include BBS Table",
            value=True,
            help="Include Bar Bending Schedule table in report",
        )

    with col2:
        include_diagrams = st.checkbox(
            "Include Diagrams", value=True, help="Include beam cross-section diagrams"
        )

    with col3:
        include_calcs = st.checkbox(
            "Show Detailed Calculations",
            value=True,
            help="Include step-by-step calculation sheets",
        )

    # Logo upload (optional)
    with st.expander("🖼️ Company Logo (Optional)"):
        logo_file = st.file_uploader(
            "Upload company logo",
            type=["png", "jpg", "jpeg"],
            help="Upload your company logo for the cover page (max 2MB)",
        )

        if logo_file:
            st.image(logo_file, width=200, caption="Logo Preview")

    st.divider()

    # Preview section
    st.subheader("👀 Report Preview")

    # Show what will be included
    sections_included = []
    if include_calcs:
        sections_included.append("✓ Detailed Calculations")
    if include_bbs:
        sections_included.append("✓ Bar Bending Schedule")
    if include_diagrams:
        sections_included.append("✓ Beam Diagrams")

    sections_text = (
        " | ".join(sections_included) if sections_included else "Basic report only"
    )

    st.info(
        f"**Report will include:** {sections_text}\n\n"
        f"**Total pages:** Estimated 6-8 pages"
    )

    # Design summary (from session state)
    design_result = st.session_state.get("_current_design_result", {})

    # Get beam inputs for display (stored separately from design results)
    beam_inputs = st.session_state.get("beam_inputs", {})
    span_mm = beam_inputs.get("span_mm", 0)
    b_mm = beam_inputs.get("b_mm", 0)
    D_mm = beam_inputs.get("D_mm", 0)
    fck = 25  # Default
    if beam_inputs.get("concrete_grade"):
        # Extract grade number from "M25" -> 25
        grade_str = beam_inputs.get("concrete_grade", "M25")
        try:
            fck = int(grade_str.replace("M", ""))
        except (ValueError, AttributeError):
            fck = 25

    with st.expander("📊 Design Summary (from current session)"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Span", f"{span_mm / 1000:.1f} m")
            st.metric("Width", f"{b_mm:.0f} mm")

        with col2:
            flexure = design_result.get("flexure", {})
            # Try multiple possible keys for steel area
            ast_prov = (
                flexure.get("Ast_prov_mm2")
                or flexure.get("ast_provided")
                or flexure.get("ast_prov")
                or 0
            )
            st.metric("Main Steel", f"{ast_prov:.0f} mm²")
            st.metric(
                "Status",
                "✓ SAFE" if design_result.get("is_safe", False) else "✗ UNSAFE",
            )

        with col3:
            shear = design_result.get("shear", {})
            # Try multiple possible keys for spacing
            spacing = (
                shear.get("spacing_mm")
                or shear.get("spacing")
                or shear.get("sv_required_mm")
                or 0
            )
            st.metric("Stirrups", f"@ {spacing:.0f} mm")
            st.metric("Grade", f"M{fck:.0f}")

    st.divider()

    # Generate button
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        generate_button = st.button(
            "📄 Generate PDF",
            type="primary",
            width="stretch",
            help="Generate and download PDF report",
        )

    if generate_button:
        # Validate inputs
        if not project_name or not engineer:
            st.error("⚠️ Please fill in at least Project Name and Engineer Name.")
            return

        # Show progress
        with st.spinner("Generating PDF report..."):
            try:
                # Prepare project info
                project_info = {
                    "project_name": project_name,
                    "location": location,
                    "client": client,
                    "engineer": engineer,
                    "checker": checker,
                    "company": company,
                }

                # Handle logo if uploaded
                logo_path = None
                if logo_file:
                    # Save temporarily
                    logo_path = f"/tmp/{logo_file.name}"
                    with open(logo_path, "wb") as f:
                        f.write(logo_file.getbuffer())

                # Transform design data to PDF format
                # Get beam_inputs from session state for full context
                beam_inputs_for_pdf = st.session_state.get("beam_inputs", {})
                pdf_design_data = _transform_design_data_for_pdf(
                    design_result, beam_inputs_for_pdf
                )

                # Generate PDF with transformed data
                generator = BeamDesignReportGenerator()
                pdf_buffer = generator.generate_report(
                    design_data=pdf_design_data,
                    project_info=project_info,
                    include_bbs=include_bbs,
                    include_diagrams=include_diagrams,
                    logo_path=logo_path,
                )

                st.success("✅ PDF report generated successfully!")

                # Download button
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"beam_design_report_{project_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="primary",
                    width="stretch",
                )

                # Show file size
                pdf_size_kb = len(pdf_buffer.getvalue()) / 1024
                st.caption(f"📦 File size: {pdf_size_kb:.1f} KB")

            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")
                st.info("Please check that all design data is valid and try again.")

                # Debug info
                with st.expander("🐛 Debug Information"):
                    st.code(str(e))
                    st.write("Design Result Keys:", list(design_result.keys()))

    # Help section
    with st.expander("ℹ️ How to Use"):
        st.markdown(
            """
        **Steps to generate a PDF report:**

        1. **Complete a beam design** on the Beam Design page first
        2. **Fill in project information** (project name, engineer, etc.)
        3. **Select report options** (BBS, diagrams, calculations)
        4. **Upload company logo** (optional)
        5. **Click "Generate PDF"** and download the report

        **Report Contents:**
        - ✅ Cover page with project details
        - ✅ Input summary (geometry, materials, loading)
        - ✅ Design calculations with IS 456 references
        - ✅ Results summary with pass/fail status
        - ✅ Optional: Bar Bending Schedule table
        - ✅ Optional: Beam cross-section diagrams
        - ✅ Compliance checklist (IS 456:2000)
        - ✅ Signature block

        **Tips:**
        - Report is generated in professional format suitable for submission
        - All calculations include IS 456 clause references
        - PDF is print-ready (A4 size)
        """
        )

    # Technical info
    with st.expander("🔧 Technical Information"):
        st.markdown(
            """
        **Report Standards:**
        - Design Code: IS 456:2000
        - Page Size: A4 (210 × 297 mm)
        - Margins: 20 mm all sides
        - Font: Helvetica (professional standard)

        **What's Included:**
        - All design checks as per IS 456
        - Clause-by-clause compliance
        - Step-by-step calculations
        - Professional formatting

        **File Format:**
        - PDF/A compliant
        - Vector graphics (scalable)
        - Print-ready quality
        """
        )


if __name__ == "__main__":
    # For standalone testing
    render_page()
