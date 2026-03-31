"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is13920.beam

IS 13920:2016 is the Indian Standard for ductile detailing of reinforced
concrete structures subjected to seismic forces. It was separated from
IS 456 code modules in Phase 0 restructure.

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import ductile` continue to work.

Migration date: 2026-03-31 (TASK-709)
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "structural_lib.ductile has moved to "
    "structural_lib.codes.is13920.beam. "
    "Update imports to suppress this warning.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the new location
from structural_lib.codes.is13920.beam import *  # noqa: F401, F403, E402

# Re-export __all__ if defined
try:
    from structural_lib.codes.is13920.beam import __all__  # noqa: F401, E402
except ImportError:
    pass  # Module may not define __all__
