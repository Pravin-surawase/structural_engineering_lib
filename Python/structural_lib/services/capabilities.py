# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Discoverable supported-case registry for the IS 456 public library."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["IS456Capability", "get_supported_is456_capabilities"]


@dataclass(frozen=True)
class IS456Capability:
    """One intentionally supported public workflow and its held boundary."""

    element: str
    public_workflows: tuple[str, ...]
    supported_case: str
    held_cases: tuple[str, ...]
    qualified_review_required: bool


_CAPABILITIES = (
    IS456Capability(
        element="beam",
        public_workflows=("design_beam_is456", "check_beam_is456", "detail_beam_is456"),
        supported_case="Route-specific rectangular/flanged flexure, shear and detailing; torsion is a separate explicit workflow.",
        held_cases=("The primary combined beam route does not include torsion.",),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="column",
        public_workflows=("design_column_is456", "design_long_column_is456"),
        supported_case="Rectangular columns with the declared symmetric/two-face reinforcement assumptions.",
        held_cases=(
            "Circular, asymmetric and arbitrary multilayer layouts are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="isolated_footing",
        public_workflows=(
            "size_footing",
            "footing_flexure",
            "footing_one_way_shear",
            "footing_punching_shear",
            "check_isolated_footing_load_transfer",
        ),
        supported_case="Square/rectangular isolated footing checks and bounded concentric dowel transfer.",
        held_cases=(
            "Combined, strap, raft, pile-cap, settlement and lateral stability design are excluded.",
        ),
        qualified_review_required=True,
    ),
    IS456Capability(
        element="solid_slab",
        public_workflows=("design_one_way_slab_is456", "design_two_way_slab_is456"),
        supported_case="Simply supported one-way strip; one interior rectangular two-way flexure case using accepted external coefficients.",
        held_cases=(
            "Two-way coefficient lookup is not built in.",
            "Flat/drop/ribbed slabs, openings, irregular panels and FEM are excluded.",
        ),
        qualified_review_required=True,
    ),
)


def get_supported_is456_capabilities() -> tuple[IS456Capability, ...]:
    """Return the immutable supported-case registry for this library version."""
    return _CAPABILITIES
