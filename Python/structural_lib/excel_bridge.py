"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.excel_bridge

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.excel_bridge is deprecated. "
    "Use structural_lib.services.excel_bridge instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.excel_bridge import (  # noqa: F401, E402
    IS456_AstRequired,
    IS456_BarCallout,
    IS456_Ld,
    IS456_MuLim,
    IS456_ShearSpacing,
    IS456_StirrupCallout,
    create_design_sheet,
)
