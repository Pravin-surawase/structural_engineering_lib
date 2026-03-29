# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       logging_config
Description:  Centralized logging configuration for structural_lib.

Provides a consistent logger factory so all modules use the same format
and respect the STRUCTURAL_LIB_LOG_LEVEL environment variable.

Usage:
    from structural_lib.core.logging_config import get_logger
    logger = get_logger(__name__)
    logger.debug("xu_max = %s for fck=%s, fy=%s", xu_max, fck, fy)

Environment Variables:
    STRUCTURAL_LIB_LOG_LEVEL: Set log level (DEBUG, INFO, WARNING, ERROR).
                              Default: WARNING
"""

from __future__ import annotations

import logging
import os

_LOG_FORMAT = "[%(levelname)s] %(name)s: %(message)s"
_DEFAULT_LEVEL = "WARNING"

_configured = False


def _configure_root_logger() -> None:
    """Configure the structural_lib root logger once."""
    global _configured
    if _configured:
        return

    level_name = os.environ.get("STRUCTURAL_LIB_LOG_LEVEL", _DEFAULT_LEVEL).upper()
    level = getattr(logging, level_name, logging.WARNING)

    root_logger = logging.getLogger("structural_lib")
    root_logger.setLevel(level)

    # Only add handler if none exist (avoid duplicate handlers on re-import)
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        root_logger.addHandler(handler)

    # Prevent propagation to root logger (application can add its own handlers)
    root_logger.propagate = False
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for the given module.

    Args:
        name: Module name, typically ``__name__``.

    Returns:
        A :class:`logging.Logger` scoped under ``structural_lib``.
    """
    _configure_root_logger()
    return logging.getLogger(name)
