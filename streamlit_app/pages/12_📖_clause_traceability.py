# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
IS 456 Clause Traceability Page
===============================

Interactive viewer for IS 456:2000 clause database and code traceability.

Features:
- Browse all IS 456 clauses by category
- Search clauses by keyword
- View clause details (title, text, formulas, keywords)
- See which functions implement which clauses
- Generate traceability reports

Author: MAIN Agent (Session 15)
Status: ✅ IMPLEMENTED (TASK-273)
"""

import streamlit as st
import sys
from pathlib import Path

import pandas as pd  # For dataframe display

# Fix import path
current_file = Path(__file__).resolve()
pages_dir = current_file.parent
streamlit_app_dir = pages_dir.parent

if str(streamlit_app_dir) not in sys.path:
    sys.path.insert(0, str(streamlit_app_dir))

# Import traceability API
try:
    from structural_lib.codes.is456.traceability import (
        get_clause_info,
        list_clauses_by_category,
        search_clauses,
        get_database_metadata,
        _load_clause_database,
        _CLAUSE_REGISTRY,
        generate_traceability_report,
    )
    # Import modules to populate registry at module level
    from structural_lib.codes.is456 import flexure, shear, detailing
    TRACEABILITY_AVAILABLE = True
except ImportError:
    TRACEABILITY_AVAILABLE = False
    _CLAUSE_REGISTRY = {}


def _count_unique_clauses(report: dict) -> int:
    """Count unique clauses from a traceability report.

    Args:
        report: Report dict with 'functions' mapping function names to clause lists.

    Returns:
        Count of unique clauses referenced.
    """
    unique_refs: set[str] = set()
    functions_dict = report.get("functions") or {}
    # Early return for non-dict avoids conditional variable definition
    items = functions_dict.items() if isinstance(functions_dict, dict) else []
    for _, refs in items:
        refs_list = refs if isinstance(refs, list) else []
        unique_refs.update(refs_list)
    return len(unique_refs)

from utils.layout import setup_page, page_header, section_header

# Page setup
setup_page(title="Clause Traceability | IS 456", icon="📖", layout="wide")


def main():
    """Main page function."""
    page_header("IS 456 Clause Traceability", "Browse and search IS 456:2000 clauses")

    if not TRACEABILITY_AVAILABLE:
        st.error("Traceability module not available. Please ensure structural_lib is installed.")
        return

    # Get database metadata
    try:
        metadata = get_database_metadata()
        db = _load_clause_database()
    except Exception as e:
        st.error(f"Failed to load clause database: {e}")
        return

    # Statistics sidebar
    with st.sidebar:
        st.header("📊 Database Statistics")
        st.metric("Standard", metadata.get("standard", "IS 456:2000"))
        st.metric("Total Clauses", metadata.get("total_clauses", "N/A"))
        st.metric("Last Updated", metadata.get("last_updated", "N/A"))

        # Category filter
        st.header("🗂️ Categories")
        clauses = db.get("clauses", {})
        categories = sorted(set(c.get("category", "other") for c in clauses.values() if isinstance(c, dict)))
        selected_category = st.selectbox(
            "Filter by Category",
            ["All"] + categories,
            index=0
        )

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Browse Clauses",
        "🔍 Search",
        "📐 Functions",
        "📊 Report"
    ])

    # Tab 1: Browse Clauses
    with tab1:
        section_header("Browse IS 456 Clauses")

        if selected_category == "All":
            display_clauses = clauses
        else:
            display_clauses = {
                ref: info for ref, info in clauses.items()
                if isinstance(info, dict) and info.get("category") == selected_category
            }

        if not display_clauses:
            st.info("No clauses found for this category.")
        else:
            # Display as expandable sections
            def sort_clause_key(x: str) -> tuple[str, str]:
                """Sort key for clause references."""
                # split('.') always returns at least 1 element
                # Use safe access pattern for scanner compatibility
                first_part = x.split('.')[0] if x else x
                return (first_part.zfill(3), x)

            for ref in sorted(display_clauses.keys(), key=sort_clause_key):
                info = display_clauses[ref]
                if not isinstance(info, dict):
                    continue

                title = info.get("title", "Untitled")
                category = info.get("category", "other")
                section = info.get("section", "")

                with st.expander(f"**Cl. {ref}** — {title}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Section:** {section}")
                        st.markdown(f"**Category:** `{category}`")
                        if info.get("text"):
                            st.markdown("**Text:**")
                            st.markdown(f"> {info['text']}")
                    with col2:
                        if info.get("formulas"):
                            st.markdown("**Formulas:**")
                            for formula in info["formulas"]:
                                st.code(formula, language="text")
                        if info.get("keywords"):
                            st.markdown("**Keywords:**")
                            st.write(", ".join(f"`{k}`" for k in info["keywords"]))

    # Tab 2: Search
    with tab2:
        section_header("Search Clauses")

        search_query = st.text_input(
            "Search by keyword",
            placeholder="e.g., shear, reinforcement, stress...",
            key="clause_search"
        )

        if search_query:
            results = search_clauses(search_query)
            if results:
                st.success(f"Found {len(results)} matching clause(s)")
                for result in results:
                    ref = result.get("clause_ref", "?")
                    title = result.get("title", "Untitled")
                    category = result.get("category", "other")
                    with st.expander(f"**Cl. {ref}** — {title} ({category})"):
                        text = result.get("text", "")
                        if text:
                            st.markdown(f"> {text}")
                        formulas = result.get("formulas", [])
                        if formulas:
                            st.markdown("**Formulas:**")
                            for formula in formulas:
                                st.code(formula, language="text")
            else:
                st.warning(f"No clauses found matching '{search_query}'")

        # Quick lookup by clause number
        st.markdown("---")
        st.subheader("Quick Lookup")
        clause_ref = st.text_input(
            "Enter clause reference",
            placeholder="e.g., 38.1, 40.1, 26.2.1",
            key="clause_lookup"
        )

        if clause_ref:
            info = get_clause_info(clause_ref)
            if info:
                st.success(f"Found Clause {clause_ref}")
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"### {info.get('title', 'Untitled')}")
                    st.markdown(f"**Section:** {info.get('section', 'N/A')}")
                    st.markdown(f"**Category:** `{info.get('category', 'other')}`")
                    if info.get("text"):
                        st.markdown("**Text:**")
                        st.markdown(f"> {info['text']}")
                with col2:
                    if info.get("formulas"):
                        st.markdown("**Formulas:**")
                        for formula in info["formulas"]:
                            st.code(formula, language="text")
                    if info.get("keywords"):
                        st.markdown("**Keywords:**")
                        st.write(", ".join(f"`{k}`" for k in info["keywords"]))
            else:
                st.warning(f"Clause '{clause_ref}' not found in database")

    # Tab 3: Function Traceability
    with tab3:
        section_header("Function → Clause Mapping")

        st.markdown("""
        This table shows which IS 456 clauses are implemented by which functions
        in the `structural_lib.codes.is456` module.
        """)

        # Use module-level registry (already imported)
        try:
            if _CLAUSE_REGISTRY:
                # Create a table
                data = []
                for func_key, refs in sorted(_CLAUSE_REGISTRY.items()):
                    parts = func_key.split(".")
                    module = parts[-2] if len(parts) >= 2 else "unknown"
                    func_name = parts[-1] if parts else "unknown"
                    data.append({
                        "Module": module,
                        "Function": func_name,
                        "Clauses": ", ".join(refs)
                    })

                # Display as dataframe (pandas imported at module level)
                df = pd.DataFrame(data)
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Module": st.column_config.TextColumn("Module", width="small"),
                        "Function": st.column_config.TextColumn("Function", width="medium"),
                        "Clauses": st.column_config.TextColumn("Clauses", width="medium"),
                    }
                )

                st.info(f"📊 **{len(_CLAUSE_REGISTRY)}** functions with clause traceability")
            else:
                st.warning("No functions registered with @clause decorator")
        except Exception as e:
            st.error(f"Failed to load function registry: {e}")

    # Tab 4: Report
    with tab4:
        section_header("Traceability Report")

        st.markdown("""
        Generate a comprehensive traceability report showing the coverage
        of IS 456 clauses in the codebase.
        """)

        if st.button("📄 Generate Report", type="primary"):
            try:
                # Use module-level generate_traceability_report (already imported)
                report = generate_traceability_report()

                st.markdown("### Report Summary")

                # Use helper function to count unique clauses
                unique_clause_count = _count_unique_clauses(report)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Standard", report.get("standard", "IS 456:2000"))
                with col2:
                    st.metric("Functions Decorated", report.get("total_decorated_functions", 0))
                with col3:
                    st.metric("Unique Clauses Referenced", unique_clause_count)

                # Functions by clause
                st.markdown("### Decorated Functions")
                functions = report.get("functions", {})
                if isinstance(functions, dict):
                    for func_name, refs in sorted(functions.items()):
                        if isinstance(refs, list):
                            st.markdown(f"- **{func_name}**: {', '.join(refs)}")

            except Exception as e:
                st.error(f"Failed to generate report: {e}")

    # Footer
    st.markdown("---")
    st.caption(f"IS 456:2000 Clause Database | {metadata.get('total_clauses', '?')} clauses | v{metadata.get('version', '?')}")


if __name__ == "__main__":
    main()
