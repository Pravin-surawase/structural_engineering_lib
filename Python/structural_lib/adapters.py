"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.adapters
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.adapters."""

from __future__ import annotations

from structural_lib.services.adapters import (  # noqa: F401, E402
    ETABSAdapter,
    GenericCSVAdapter,
    InputAdapter,
    ManualInputAdapter,
    SAFEAdapter,
    STAADAdapter,
)
