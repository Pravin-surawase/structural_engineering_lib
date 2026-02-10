"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.job_runner

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.job_runner is deprecated. "
    "Use structural_lib.services.job_runner instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.job_runner import (  # noqa: F401, E402
    load_job_json,
    load_job_spec,
    run_job,
    run_job_is456,
)
