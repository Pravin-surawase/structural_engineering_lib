"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.detailing

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import detailing` continue to work.

Migration date: 2026-01-10 (Session 5)
"""

from __future__ import annotations

# Re-export everything from the new location
from structural_lib.codes.is456.detailing import *  # noqa: F401, F403

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.detailing import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__
