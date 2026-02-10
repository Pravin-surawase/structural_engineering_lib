"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.report

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.report is deprecated. "
    "Use structural_lib.services.report instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.report import (  # noqa: F401, E402
    CriticalCase,
    ReportData,
    SanityCheck,
    ScorecardItem,
    UnitsAlert,
    export_critical_csv,
    export_critical_html,
    export_design_json,
    export_html,
    export_json,
    get_critical_set,
    get_input_sanity,
    get_stability_scorecard,
    get_units_sentinel,
    load_design_results,
    load_report_data,
    render_design_report_single,
    write_design_report_package,
)
