# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Controlled IS 456 source and route-specific amendment identities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from structural_lib.core.source_identity import (
    AMENDMENT_6_SOURCE_ID,
    IS456_CONSOLIDATED_SOURCE_ID,
)

__all__ = [
    "AMENDMENT_6_SOURCE_ID",
    "BEAM_STRENGTH_SOURCE_BASIS",
    "IS456_CONSOLIDATED_SOURCE_ID",
    "AmendmentApplicability",
    "ControlledSourceBasisV1",
]


class AmendmentApplicability(StrEnum):
    """Whether the controlled amendment has been resolved for one route."""

    REVIEWED_NO_CALCULATION_CHANGE = "REVIEWED_NO_CALCULATION_CHANGE"
    APPLICABLE = "APPLICABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ControlledSourceBasisV1:
    """Exact source identities plus a route-specific applicability decision."""

    route_id: str
    source_ids: tuple[str, ...]
    amendment_identity: str
    amendment_applicability: AmendmentApplicability
    applicability_review_id: str | None

    @property
    def is_resolved(self) -> bool:
        return (
            self.amendment_applicability is not AmendmentApplicability.UNKNOWN
            and bool(self.applicability_review_id)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "route_id": self.route_id,
            "source_ids": list(self.source_ids),
            "amendment_identity": self.amendment_identity,
            "amendment_applicability": self.amendment_applicability.value,
            "applicability_review_id": self.applicability_review_id,
            "resolved": self.is_resolved,
        }


BEAM_STRENGTH_SOURCE_BASIS = ControlledSourceBasisV1(
    route_id="design_beam_is456",
    source_ids=(IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID),
    amendment_identity=AMENDMENT_6_SOURCE_ID,
    amendment_applicability=AmendmentApplicability.REVIEWED_NO_CALCULATION_CHANGE,
    applicability_review_id="LIB-PRO-002-E-BEAM-AMENDMENT-REVIEW",
)
