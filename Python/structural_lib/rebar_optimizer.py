"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.rebar_optimizer
All functionality is re-exported here for backward compatibility.
Prefer importing directly from structural_lib.services.rebar_optimizer."""

from __future__ import annotations

from structural_lib.services.rebar_optimizer import (  # noqa: F401, E402
    Objective,
    RebarOptimizerResult,
    optimize_bar_arrangement,
)
