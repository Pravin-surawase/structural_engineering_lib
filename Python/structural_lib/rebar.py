"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.rebar
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.rebar."""

from __future__ import annotations

from structural_lib.services.rebar import (  # noqa: F401, E402
    apply_rebar_config,
    validate_rebar_config,
)
