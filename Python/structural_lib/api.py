"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.api
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.api."""

from __future__ import annotations

# Re-export non-__all__ names used by tests/callers
from importlib.metadata import PackageNotFoundError, version  # noqa: F401, E402

from structural_lib.services.api import *  # noqa: F401, F403, E402
from structural_lib.services.api import __all__  # noqa: F401, E402
