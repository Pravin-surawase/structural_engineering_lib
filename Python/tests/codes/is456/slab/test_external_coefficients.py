# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Exact P9 tests for external two-way slab coefficient recording."""

from __future__ import annotations

import ast
import inspect
import math

import pytest

from structural_lib.codes.is456.slab.external_coefficients import (
    AMENDMENT_6_SOURCE_ID,
    IS456_CONSOLIDATED_SOURCE_ID,
    ExternalCoefficientPolicyStatus,
    ExternalCoefficientReviewStatus,
    record_external_two_way_slab_coefficients,
)
from structural_lib.codes.is456.slab.models import (
    SlabContractError,
    SolidRectangularSlabGeometry,
)


def _record_kwargs(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "geometry": SolidRectangularSlabGeometry(3000, 6000, 150),
        "support_case_id": "caller-defined-support-case",
        "alpha_x": 0.08,
        "alpha_y": 0.06,
        "coefficient_source_reference": "caller-controlled-record:sheet-4,row-12",
        "coefficient_source_is_approved": True,
    }
    values.update(overrides)
    return values


def test_exact_ratio_two_is_accepted_and_recorded_for_qualified_review() -> None:
    record = record_external_two_way_slab_coefficients(**_record_kwargs())

    assert record.span_ratio_ly_lx == 2.0
    assert record.alpha_x == 0.08
    assert record.alpha_y == 0.06
    assert record.support_case_id == "caller-defined-support-case"
    assert record.coefficient_source_is_approved is True
    assert record.source_ids == (IS456_CONSOLIDATED_SOURCE_ID, AMENDMENT_6_SOURCE_ID)
    assert (
        record.policy_status is ExternalCoefficientPolicyStatus.EXTERNAL_SOURCE_REQUIRED
    )
    assert record.review_status is ExternalCoefficientReviewStatus.REVIEW_REQUIRED
    assert record.coefficient_correctness_is_verified is False
    assert any("P10" in limitation for limitation in record.limitations)


def test_ratio_below_two_is_accepted_with_exact_ratio_echoed() -> None:
    record = record_external_two_way_slab_coefficients(
        **_record_kwargs(geometry=SolidRectangularSlabGeometry(4000, 6000, 150))
    )

    assert record.span_ratio_ly_lx == 1.5


def test_ratio_above_two_is_rejected() -> None:
    with pytest.raises(SlabContractError, match="classified as two_way"):
        record_external_two_way_slab_coefficients(
            **_record_kwargs(geometry=SolidRectangularSlabGeometry(3000, 6001, 150))
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("coefficient_source_is_approved", False, "must be True"),
        ("coefficient_source_is_approved", 1, "must be True"),
        ("coefficient_source_reference", "", "non-blank"),
        ("coefficient_source_reference", "   ", "non-blank"),
        ("support_case_id", "", "non-blank"),
        ("support_case_id", "   ", "non-blank"),
    ],
)
def test_provenance_and_caller_defined_support_case_fail_closed(
    field_name: str, value: object, message: str
) -> None:
    with pytest.raises(SlabContractError, match=message):
        record_external_two_way_slab_coefficients(
            **_record_kwargs(**{field_name: value})
        )


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        ("alpha_x", 0.0, "interval"),
        ("alpha_y", -0.01, "interval"),
        ("alpha_x", 1.01, "interval"),
        ("alpha_y", math.inf, "finite"),
        ("alpha_x", math.nan, "finite"),
        ("alpha_y", True, "real dimensionless"),
    ],
)
def test_invalid_external_coefficients_fail_closed(
    field_name: str, value: object, message: str
) -> None:
    with pytest.raises(SlabContractError, match=message):
        record_external_two_way_slab_coefficients(
            **_record_kwargs(**{field_name: value})
        )


def test_record_is_frozen_and_does_not_embed_a_coefficient_dataset() -> None:
    record = record_external_two_way_slab_coefficients(**_record_kwargs())
    with pytest.raises(AttributeError):
        record.alpha_x = 0.07  # type: ignore[misc]

    module = inspect.getmodule(record_external_two_way_slab_coefficients)
    assert module is not None
    module_tree = ast.parse(inspect.getsource(module))
    dataset_assignments = [
        node
        for node in ast.walk(module_tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, (ast.Dict, ast.List, ast.Set, ast.Tuple))
        and any(
            isinstance(target, ast.Name)
            and ("alpha" in target.id or "coefficient" in target.id)
            for target in node.targets
        )
    ]
    assert dataset_assignments == []
