"""
Utilities Module
================

Helper functions for the Streamlit dashboard.

Modules:
- api_wrapper: Cached API calls to structural_lib
- validation: Input validation functions
- formatters: Data formatting utilities
- state: Session state management
- input_bridge: Bridge between UI inputs and library inputs (TASK-276-279)

Author: STREAMLIT UI SPECIALIST (Agent 6)
"""

# Input bridge for TASK-276-279 integration
from .input_bridge import (
    InputBridge,
    get_beam_input_from_session,
    log_design_to_audit,
)
