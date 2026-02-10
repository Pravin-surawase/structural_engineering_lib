"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.report_svg

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.report_svg is deprecated. "
    "Use structural_lib.services.report_svg instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.report_svg import (  # noqa: F401, E402
    render_section_svg,
    render_section_svg_from_beam,
)
