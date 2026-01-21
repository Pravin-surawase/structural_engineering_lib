# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Input Bridge - Converts between Streamlit and Library Input Types
=================================================================

Bridges the gap between:
- streamlit_app.utils.session_manager.BeamInputs (UI layer)
- structural_lib.inputs.BeamInput (Professional library)

This allows Streamlit UI to leverage professional features like:
- Calculation reports (TASK-277)
- Audit trails (TASK-278)
- Testing strategies (TASK-279)

Usage:
    >>> from utils.input_bridge import InputBridge
    >>> from utils.session_manager import BeamInputs
    >>>
    >>> ui_inputs = BeamInputs(b_mm=300, D_mm=500, ...)
    >>> lib_input = InputBridge.to_library(ui_inputs)
    >>> # Now use with professional features
"""

from __future__ import annotations

import logging

import streamlit as st

from structural_lib.audit import AuditTrail
from utils.session_manager import BeamInputs, DesignResult

logger = logging.getLogger(__name__)


class InputBridge:
    """Bridge between Streamlit UI inputs and structural_lib professional inputs."""

    @staticmethod
    def to_library_input(ui_inputs: BeamInputs) -> dict:
        """Convert Streamlit BeamInputs to library-compatible dict.

        This dict can be used with:
        - structural_lib.inputs.BeamInput.from_dict()
        - structural_lib.api.design_beam_is456()
        - structural_lib.calculation_report.generate_calculation_report()

        Args:
            ui_inputs: Streamlit UI input dataclass

        Returns:
            Dictionary compatible with structural_lib functions
        """
        return {
            "beam_id": f"B-{ui_inputs.timestamp[:10] if ui_inputs.timestamp else 'UNNAMED'}",
            "story": "GF",
            "geometry": {
                "b_mm": ui_inputs.b_mm,
                "D_mm": ui_inputs.D_mm,
                "d_mm": ui_inputs.d_mm,
                "span_mm": ui_inputs.span_mm,
                "cover_mm": ui_inputs.cover_mm,
            },
            "materials": {
                "fck_nmm2": ui_inputs.fck_mpa,
                "fy_nmm2": ui_inputs.fy_mpa,
            },
            "loads": {
                "mu_knm": ui_inputs.mu_knm,
                "vu_kn": ui_inputs.vu_kn,
            },
        }

    @staticmethod
    def to_api_kwargs(ui_inputs: BeamInputs) -> dict:
        """Convert Streamlit BeamInputs to API function kwargs.

        Use with: api.design_beam_is456(**kwargs)

        Args:
            ui_inputs: Streamlit UI input dataclass

        Returns:
            Keyword arguments for design_beam_is456
        """
        return {
            "units": "IS456",
            "case_id": "STREAMLIT-DESIGN",
            "b_mm": ui_inputs.b_mm,
            "D_mm": ui_inputs.D_mm,
            "d_mm": ui_inputs.d_mm,
            "fck_nmm2": ui_inputs.fck_mpa,
            "fy_nmm2": ui_inputs.fy_mpa,
            "mu_knm": ui_inputs.mu_knm,
            "vu_kn": ui_inputs.vu_kn,
        }

    @staticmethod
    def to_audit_log_inputs(ui_inputs: BeamInputs) -> dict:
        """Convert to format suitable for audit trail logging.

        Use with: audit_trail.log_design(inputs=this_dict, ...)

        Args:
            ui_inputs: Streamlit UI input dataclass

        Returns:
            Dictionary for audit logging
        """
        return {
            "source": "streamlit_ui",
            "timestamp": ui_inputs.timestamp,
            "b_mm": ui_inputs.b_mm,
            "D_mm": ui_inputs.D_mm,
            "d_mm": ui_inputs.d_mm,
            "span_mm": ui_inputs.span_mm,
            "cover_mm": ui_inputs.cover_mm,
            "fck_nmm2": ui_inputs.fck_mpa,
            "fy_nmm2": ui_inputs.fy_mpa,
            "mu_knm": ui_inputs.mu_knm,
            "vu_kn": ui_inputs.vu_kn,
        }

    @staticmethod
    def to_report_project_info(
        project_name: str = "Streamlit Design Session",
        engineer: str = "",
        client: str = "",
    ) -> dict:
        """Create project info dict for calculation reports.

        Use with: generate_calculation_report(project_info=this_dict, ...)

        Args:
            project_name: Project name for report header
            engineer: Engineer name (optional)
            client: Client name (optional)

        Returns:
            Project info dictionary
        """
        return {
            "project_name": project_name,
            "project_number": "",
            "client_name": client,
            "engineer_name": engineer,
            "checker_name": "",
            "revision": "A",
        }

    @staticmethod
    def result_to_audit_outputs(result: DesignResult) -> dict:
        """Convert Streamlit DesignResult to audit-compatible outputs dict.

        Args:
            result: Streamlit design result

        Returns:
            Dictionary for audit output logging
        """
        return {
            "ast_mm2": result.ast_mm2,
            "ast_provided_mm2": result.ast_provided_mm2,
            "num_bars": result.num_bars,
            "bar_diameter_mm": result.bar_diameter_mm,
            "stirrup_spacing_mm": result.stirrup_spacing_mm,
            "utilization_pct": result.utilization_pct,
            "status": result.status,
            "is_ok": result.status == "PASS",
        }


def get_beam_input_from_session() -> dict | None:
    """Get current beam input from Streamlit session state as library-compatible dict.

    Returns:
        Library-compatible input dict, or None if no inputs in session
    """
    try:
        inputs = st.session_state.get("current_inputs", None)
        if inputs is None:
            return None

        if isinstance(inputs, dict):
            inputs = BeamInputs.from_dict(inputs)

        return InputBridge.to_library_input(inputs)
    except Exception as e:
        logger.error(f"Failed to get beam input from session: {e}")
        return None


def log_design_to_audit(
    ui_inputs: BeamInputs,
    result: DesignResult,
    beam_id: str = "B1",
    story: str = "GF",
) -> str | None:
    """Log a design calculation to the audit trail.

    Creates an audit log entry with SHA-256 hashed inputs/outputs.

    Args:
        ui_inputs: Streamlit UI inputs
        result: Design result
        beam_id: Beam identifier
        story: Story/floor

    Returns:
        Audit entry ID if successful, None otherwise
    """
    try:
        # Get or create audit trail from session
        if "audit_trail" not in st.session_state:
            session_id = st.session_state.get("session_id", "DEFAULT")
            st.session_state["audit_trail"] = AuditTrail(
                project_id=f"STREAMLIT-{session_id}"
            )

        trail: AuditTrail = st.session_state["audit_trail"]

        inputs_dict = InputBridge.to_audit_log_inputs(ui_inputs)
        outputs_dict = InputBridge.result_to_audit_outputs(result)

        entry = trail.log_design(
            beam_id=beam_id,
            story=story,
            inputs=inputs_dict,
            outputs=outputs_dict,
        )

        return entry.entry_id

    except Exception as e:
        logger.error(f"Failed to log design to audit: {e}")
        return None
