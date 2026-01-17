"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.tables

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import tables` continue to work.

Migration date: 2026-01-10 (Session 5)
"""

from __future__ import annotations

# Re-export utilities for backward compatibility (used by some tests)
from structural_lib import utilities  # noqa: F401

# Re-export private functions that tests depend on
# (star import doesn't include names starting with _)
# Re-export everything from the new location
from structural_lib.codes.is456.tables import *  # noqa: F401, F403
from structural_lib.codes.is456.tables import (  # noqa: F401
    _PT_ROWS,
    _TC_COLUMNS,
    _get_tc_for_grade,
)

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.tables import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__
