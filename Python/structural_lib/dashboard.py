"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.dashboard
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.dashboard."""

from __future__ import annotations

from structural_lib.services.dashboard import (  # noqa: F401, E402
    CodeCheckResult,
    DashboardSummary,
    RebarSuggestion,
    RebarSuggestionsResult,
    code_checks_live,
    generate_dashboard,
    suggest_rebar_options,
)
