"""Code-independent PF4 freshness state shared by operations and services."""

from enum import StrEnum


class FreshnessState(StrEnum):
    """Whether a result is bound to its current effective input basis."""

    CURRENT = "current"
    STALE = "stale"
    UNBOUND = "unbound"


__all__ = ["FreshnessState"]
