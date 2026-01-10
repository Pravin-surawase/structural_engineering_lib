"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.flexure

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import flexure` continue to work.

Migration date: 2026-01-XX (Session X)
"""

from __future__ import annotations

# Re-export everything from the new location
from structural_lib.codes.is456.flexure import *  # noqa: F401, F403

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.flexure import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__
