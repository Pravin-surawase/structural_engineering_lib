# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Session state helper utilities for Streamlit pages.

Provides common functions for reading and managing session state,
especially for sharing data between pages (e.g., beam design results).

Created: 2026-01-24 (Session 70 - UI Duplication Fix)
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import streamlit as st


def get_beam_design_from_session() -> Optional[Dict[str, Any]]:
    """Get beam design inputs from beam_design page if available.

    Checks session state for computed beam design results that can
    be used by downstream pages (BBS generator, DXF export, etc.).

    Returns:
        Dict with 'inputs' and 'result' keys if design exists, else None

    Example:
        >>> data = get_beam_design_from_session()
        >>> if data:
        ...     inputs = data["inputs"]
        ...     result = data["result"]
    """
    if "beam_inputs" in st.session_state:
        beam = st.session_state.beam_inputs
        if beam.get("design_computed") and beam.get("design_result"):
            return {"inputs": beam, "result": beam["design_result"]}
    return None


def get_session_value(key: str, default: Any = None) -> Any:
    """Safely get a value from session state.

    Args:
        key: Session state key
        default: Default value if key not found

    Returns:
        Session value or default
    """
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any) -> None:
    """Set a value in session state.

    Args:
        key: Session state key
        value: Value to store
    """
    st.session_state[key] = value


def has_computed_design() -> bool:
    """Check if a beam design has been computed in the session.

    Returns:
        True if design results exist
    """
    return get_beam_design_from_session() is not None
