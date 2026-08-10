# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Fail-closed external coefficient carriers for supported slab methods."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from numbers import Real
from typing import Protocol

from structural_lib.codes.is456.slab.models import SlabContractError
from structural_lib.codes.is456.slab.topology import SlabSupportTopologyKind

__all__ = [
    "CoefficientMethod",
    "OneWayContinuousCoefficientSet",
    "TwoWayPanelCoefficientSet",
]


class CoefficientMethod(StrEnum):
    EXTERNAL_EXACT = "external_exact"
    BUILT_IN_EXACT = "built_in_exact"
    BUILT_IN_INTERPOLATED = "built_in_interpolated"


class _CoefficientCarrier(Protocol):
    @property
    def source_reference(self) -> str: ...

    @property
    def source_is_approved(self) -> bool: ...

    @property
    def qualified_acceptance_reference(self) -> str: ...

    @property
    def qualified_acceptance_acknowledged(self) -> bool: ...

    @property
    def method(self) -> CoefficientMethod: ...


def _coefficient(value: float, field_name: str, *, allow_zero: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise SlabContractError(f"{field_name} must be a real dimensionless value")
    normalized = float(value)
    lower_ok = normalized >= 0.0 if allow_zero else normalized > 0.0
    if not math.isfinite(normalized) or not lower_ok or normalized > 1.0:
        bound = "non-negative" if allow_zero else "positive"
        raise SlabContractError(
            f"{field_name} must be finite, {bound}, and no greater than 1.0"
        )
    return normalized


def _nonblank(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SlabContractError(f"{field_name} must be a non-blank string")
    return value.strip()


def _require_external_acceptance(instance: _CoefficientCarrier) -> None:
    for name in ("source_reference", "qualified_acceptance_reference"):
        object.__setattr__(instance, name, _nonblank(getattr(instance, name), name))
    if instance.source_is_approved is not True:
        raise SlabContractError("source_is_approved must be explicitly True")
    if instance.qualified_acceptance_acknowledged is not True:
        raise SlabContractError(
            "qualified_acceptance_acknowledged must be explicitly True"
        )
    method = instance.method
    if not isinstance(method, CoefficientMethod):
        try:
            method = CoefficientMethod(method)
            object.__setattr__(instance, "method", method)
        except (TypeError, ValueError) as exc:
            raise SlabContractError("unsupported coefficient method") from exc
    if method is CoefficientMethod.EXTERNAL_EXACT:
        return
    if not instance.source_reference.startswith("IS456_TABLE_"):
        raise SlabContractError(
            "built-in coefficient records require the canonical IS456_TABLE source reference"
        )
    if instance.qualified_acceptance_reference != (
        "OWNER_DECISION_2026-08-10_BUILT_IN_SLAB_COEFFICIENTS"
    ):
        raise SlabContractError(
            "built-in coefficient records require the frozen owner-decision reference"
        )


@dataclass(frozen=True)
class OneWayContinuousCoefficientSet:
    """Reviewed external action coefficients for one continuous strip case."""

    positive_midspan: float
    negative_support: float
    shear_support: float
    source_reference: str
    source_is_approved: bool
    qualified_acceptance_reference: str
    qualified_acceptance_acknowledged: bool
    method: CoefficientMethod = CoefficientMethod.EXTERNAL_EXACT
    table_id: str | None = None
    case_id: str | None = None
    interpolation_bounds: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        for name in ("positive_midspan", "negative_support", "shear_support"):
            object.__setattr__(self, name, _coefficient(getattr(self, name), name))
        _require_external_acceptance(self)

    @property
    def verified_by_library(self) -> bool:
        return self.method is not CoefficientMethod.EXTERNAL_EXACT


@dataclass(frozen=True)
class TwoWayPanelCoefficientSet:
    """Four reviewed coefficients tied to one explicit physical topology."""

    support_topology_kind: SlabSupportTopologyKind
    alpha_x_negative: float
    alpha_x_positive: float
    alpha_y_negative: float
    alpha_y_positive: float
    source_reference: str
    source_is_approved: bool
    qualified_acceptance_reference: str
    qualified_acceptance_acknowledged: bool
    method: CoefficientMethod = CoefficientMethod.EXTERNAL_EXACT
    table_id: str | None = None
    case_id: str | None = None
    aspect_ratio_ly_lx: float | None = None
    interpolation_bounds: tuple[float, float] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.support_topology_kind, SlabSupportTopologyKind):
            try:
                object.__setattr__(
                    self,
                    "support_topology_kind",
                    SlabSupportTopologyKind(self.support_topology_kind),
                )
            except (TypeError, ValueError) as exc:
                raise SlabContractError(
                    "support_topology_kind must be a supported explicit topology"
                ) from exc
        for name in ("alpha_x_negative", "alpha_y_negative"):
            object.__setattr__(
                self, name, _coefficient(getattr(self, name), name, allow_zero=True)
            )
        for name in ("alpha_x_positive", "alpha_y_positive"):
            object.__setattr__(self, name, _coefficient(getattr(self, name), name))
        _require_external_acceptance(self)

    @property
    def verified_by_library(self) -> bool:
        return self.method is not CoefficientMethod.EXTERNAL_EXACT
