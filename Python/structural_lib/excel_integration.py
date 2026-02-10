"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.excel_integration

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.excel_integration is deprecated. "
    "Use structural_lib.services.excel_integration instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.excel_integration import (  # noqa: F401, E402
    BeamDesignData,
    ProcessingResult,
    batch_generate_dxf,
    export_beam_data_to_json,
    export_schedule_to_csv,
    generate_detailing_schedule,
    generate_summary_report,
    load_beam_data_from_csv,
    load_beam_data_from_json,
    main,
    process_single_beam,
)
