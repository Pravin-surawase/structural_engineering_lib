"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.imports
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.imports."""

from __future__ import annotations

from structural_lib.services.imports import (  # noqa: F401, E402
    ImportWarnings,
    merge_geometry_forces,
    parse_dual_csv,
    validate_import,
)
