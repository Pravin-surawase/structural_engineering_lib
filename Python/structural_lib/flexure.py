"""Backward compatibility stub.

This module has been migrated to: structural_lib.codes.is456.beam.flexure

All functionality is re-exported here for backward compatibility.
Existing imports like `from structural_lib import flexure` continue to work.

Migration date: 2026-01-10 (Session 5)
Phase 1.5 update: points to beam/ subpackage.
"""

from __future__ import annotations

# Re-export materials for backward compatibility (used by some tests)
from structural_lib import materials  # noqa: F401

# Re-export everything from the canonical location
from structural_lib.codes.is456.beam.flexure import *  # noqa: F401, F403

# Re-export __all__ if defined
try:
    from structural_lib.codes.is456.beam.flexure import __all__  # noqa: F401
except ImportError:
    pass  # Module may not define __all__
