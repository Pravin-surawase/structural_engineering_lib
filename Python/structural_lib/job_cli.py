"""Backward compatibility stub.

This module has been migrated to: structural_lib.services.job_cli

All functionality is re-exported here for backward compatibility.
Prefer importing directly from the new location."""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing from structural_lib.job_cli is deprecated. "
    "Use structural_lib.services.job_cli instead.",
    DeprecationWarning,
    stacklevel=2,
)

from structural_lib.services.job_cli import (  # noqa: F401, E402
    _build_parser,
    job_runner,
    main,
)

if __name__ == "__main__":
    raise SystemExit(main())
