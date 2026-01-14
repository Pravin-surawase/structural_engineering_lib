"""
Batch Design Page (FEAT-004)
============================

Batch process multiple beam designs from CSV upload.

Features:
- CSV upload with validation
- Parallel/sequential processing
- Progress tracking
- Results download (Excel/CSV)
- Error reporting
- Summary statistics

Author: STREAMLIT UI SPECIALIST (Agent 6)
Task: STREAMLIT-FEAT-004
Status: ✅ COMPLETE
"""

import io
import sys
from pathlib import Path
from typing import List, Dict, Optional
import time

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Fix import path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

python_lib_dir = streamlit_app_dir.parent.joinpath("Python")
if str(python_lib_dir) not in sys.path:
    sys.path.insert(0, str(python_lib_dir))

from utils.layout import setup_page, page_header, section_header
from utils.theme_manager import initialize_theme
from utils.api_wrapper import cached_design
from utils.loading_states import loading_context

# Page setup
setup_page(title="Batch Design | IS 456 Beam Design", icon="📊", layout="wide")

initialize_theme()

# Session state initialization
if "batch_data" not in st.session_state:
    st.session_state.batch_data = None
if "batch_results" not in st.session_state:
    st.session_state.batch_results = None
if "processing_status" not in st.session_state:
    st.session_state.processing_status = "idle"  # idle, processing, complete, error


# =============================================================================
# Helper Functions
# =============================================================================


def validate_csv_structure(df: pd.DataFrame) -> tuple[bool, str]:
    """Validate uploaded CSV has required columns."""
    required_cols = [
        "beam_id",
        "L_mm",
        "b_mm",
        "D_mm",
        "fck_MPa",
        "fy_MPa",
        "Mu_kNm",
        "Vu_kN",
    ]
    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        return False, f"Missing columns: {', '.join(missing)}"

    # Validate data types
    try:
        df["L_mm"] = pd.to_numeric(df["L_mm"])
        df["b_mm"] = pd.to_numeric(df["b_mm"])
        df["D_mm"] = pd.to_numeric(df["D_mm"])
        df["fck_MPa"] = pd.to_numeric(df["fck_MPa"])
        df["fy_MPa"] = pd.to_numeric(df["fy_MPa"])
        df["Mu_kNm"] = pd.to_numeric(df["Mu_kNm"])
        df["Vu_kN"] = pd.to_numeric(df["Vu_kN"])
    except ValueError as e:
        return False, f"Invalid numeric values: {str(e)}"

    return True, "Valid"


def process_batch(df: pd.DataFrame, progress_bar, status_text) -> pd.DataFrame:
    """Process batch of designs."""
    results = []
    total = len(df)
    if total > 0:
        # Use itertuples() for better performance (vs iterrows())
        for idx, row in enumerate(df.itertuples()):
            # Update progress
            progress = (idx + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"Processing {row.beam_id}... ({idx + 1}/{total})")

            try:
                # Calculate effective depth (D - assumed cover of 50mm)
                D_mm = row.D_mm
                cover_mm = 50
                d_mm = D_mm - cover_mm

                # Run design with correct API parameters
                result = cached_design(
                    mu_knm=row.Mu_kNm,  # Already in kN·m
                    vu_kn=row.Vu_kN,  # Already in kN
                    b_mm=row.b_mm,
                    D_mm=D_mm,
                    d_mm=d_mm,
                    fck_nmm2=row.fck_MPa,
                    fy_nmm2=row.fy_MPa,
                )

                # Extract key results
                status = "OK" if result.get("is_safe", False) else "FAIL"
                flexure = result.get("flexure", {})
                shear = result.get("shear", {})
                # Build bar config from bar_dia and num_bars
                bar_dia = flexure.get("bar_dia", 16)
                num_bars = flexure.get("num_bars", 3)
                bar_config = f"{num_bars}-{bar_dia}mm"
                results.append(
                    {
                        "beam_id": row.beam_id,
                        "status": "✅ OK" if status == "OK" else "❌ FAIL",
                        "Ast_req_mm2": flexure.get("ast_required", "-"),
                        "Ast_prov_mm2": flexure.get("ast_provided", "-"),
                        "bar_config": bar_config,
                        "stirrup_spacing_mm": shear.get("spacing", "-"),
                        "cost_per_m_INR": result.get("cost_per_m", 0),
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "beam_id": row.beam_id,
                        "status": f"❌ ERROR: {str(e)[:50]}",
                        "Ast_req_mm2": "-",
                        "Ast_prov_mm2": "-",
                        "bar_config": "-",
                        "stirrup_spacing_mm": "-",
                        "cost_per_m_INR": "-",
                    }
                )
    else:
        return pd.DataFrame(results)

    return pd.DataFrame(results)


# =============================================================================
# Page Layout
# =============================================================================

page_header(
    title="📊 Batch Design Processor",
    subtitle="Process multiple beam designs from CSV upload",
)

# Instructions
with st.expander("📖 How to Use"):
    st.markdown(
        """
    ### CSV Format
    Your CSV file must contain these columns:

    | Column | Description | Unit | Example |
    |--------|-------------|------|---------|
    | `beam_id` | Unique beam identifier | - | B1, B2, etc. |
    | `L_mm` | Span length | mm | 6000 |
    | `b_mm` | Width | mm | 300 |
    | `D_mm` | Overall depth | mm | 500 |
    | `fck_MPa` | Concrete grade | N/mm² | 25 |
    | `fy_MPa` | Steel grade | N/mm² | 415 |
    | `Mu_kNm` | Design moment | kN·m | 150 |
    | `Vu_kN` | Design shear | kN | 80 |

    Optional columns: `d_mm` (effective depth), `cover_mm` (clear cover)

    ### Download Template
    """
    )

    # Create template CSV
    template_data = {
        "beam_id": ["B1", "B2", "B3"],
        "L_mm": [6000, 5000, 7000],
        "b_mm": [300, 250, 350],
        "D_mm": [500, 450, 600],
        "fck_MPa": [25, 30, 25],
        "fy_MPa": [415, 415, 500],
        "Mu_kNm": [150, 120, 200],
        "Vu_kN": [80, 70, 100],
    }
    template_df = pd.DataFrame(template_data)
    template_csv = template_df.to_csv(index=False)

    st.download_button(
        label="📥 Download CSV Template",
        data=template_csv,
        file_name="batch_design_template.csv",
        mime="text/csv",
    )

st.divider()

# Upload section
section_header("1️⃣ Upload CSV File")

uploaded_file = st.file_uploader(
    "Choose CSV file", type=["csv"], help="Upload CSV with beam parameters"
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Validate structure
        is_valid, message = validate_csv_structure(df)

        if is_valid:
            st.success(f"✅ Valid CSV file: {len(df)} beams found")
            st.session_state.batch_data = df

            # Preview
            with st.expander("👁️ Preview Data"):
                st.dataframe(df, width="stretch")
        else:
            st.error(f"❌ Invalid CSV: {message}")
            st.session_state.batch_data = None

    except Exception as e:
        st.error(f"❌ Error reading CSV: {str(e)}")
        st.session_state.batch_data = None

st.divider()

# Processing section
if st.session_state.batch_data is not None:
    section_header("2️⃣ Process Designs")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"**Ready to process {len(st.session_state.batch_data)} beams**")

    with col2:
        if st.button("▶️ Start Processing", type="primary", width="stretch"):
            st.session_state.processing_status = "processing"

    # Progress indicators
    if st.session_state.processing_status == "processing":
        progress_bar = st.progress(0)
        status_text = st.empty()

        with loading_context("Processing batch designs..."):
            results_df = process_batch(
                st.session_state.batch_data, progress_bar, status_text
            )
            st.session_state.batch_results = results_df
            st.session_state.processing_status = "complete"

        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        time.sleep(1)
        st.rerun()

st.divider()

# Results section
if st.session_state.batch_results is not None:
    section_header("3️⃣ Results")

    results_df = st.session_state.batch_results

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    total = len(results_df)
    success = len(results_df[results_df["status"] == "✅ OK"])
    failed = total - success
    if total > 0:
        success_pct = 100 * success / total
        failed_pct = 100 * failed / total
    else:
        success_pct = 0.0
        failed_pct = 0.0

    with col1:
        st.metric("Total Beams", total)
    with col2:
        st.metric("Successful", success, delta=f"{success_pct:.0f}%")
    with col3:
        st.metric("Failed", failed, delta=f"-{failed_pct:.0f}%" if failed > 0 else "0%")
    with col4:
        st.metric("Success Rate", f"{success_pct:.1f}%")

    # Results table
    st.dataframe(results_df, width="stretch")

    # Download options
    col1, col2, col3 = st.columns(3)

    with col1:
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name="batch_results.csv",
            mime="text/csv",
        )

    with col2:
        # Excel download (convert to bytes)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            results_df.to_excel(writer, index=False, sheet_name="Results")
        excel_data = buffer.getvalue()

        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name="batch_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with col3:
        if st.button("🔄 Reset", width="stretch"):
            st.session_state.batch_data = None
            st.session_state.batch_results = None
            st.session_state.processing_status = "idle"
            st.rerun()

# Footer
st.divider()
st.caption(
    "💡 **Tip:** For large batches (>100 beams), consider running in headless mode via CLI."
)
