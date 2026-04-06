# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Pytest configuration and Hypothesis profiles for the test suite.

Hypothesis Profiles:
- default: Standard testing (100 examples)
- dev: Fast iteration (25 examples)
- ci: Thorough CI testing (200 examples)
- exhaustive: Deep testing for critical code (1000 examples)

Usage:
    pytest --hypothesis-profile=ci  # Use in CI
    pytest --hypothesis-profile=dev  # Fast local testing
"""

from hypothesis import Verbosity, settings

# =============================================================================
# HYPOTHESIS PROFILES
# =============================================================================

# Default profile for local development
settings.register_profile(
    "default",
    max_examples=100,
    verbosity=Verbosity.normal,
    deadline=None,  # No deadline for structural calculations
)

# Fast profile for quick iteration
settings.register_profile(
    "dev",
    max_examples=25,
    verbosity=Verbosity.quiet,
    deadline=None,
)

# CI profile for thorough testing
settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.normal,
    deadline=None,
    derandomize=True,  # Reproducible failures in CI
)

# Exhaustive profile for critical functions
settings.register_profile(
    "exhaustive",
    max_examples=1000,
    verbosity=Verbosity.verbose,
    deadline=None,
)

# Load default profile
settings.load_profile("default")


# =============================================================================
# COMMON MATERIAL FIXTURES
# =============================================================================

import json  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

# =============================================================================
# GOLDEN VECTORS FIXTURE
# =============================================================================


@pytest.fixture(scope="session")
def golden_vectors():
    """Load SP:16 golden vector test data."""
    data_file = Path(__file__).parent / "data" / "golden_vectors_is456.json"
    with open(data_file, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture()
def m25_fe415() -> dict:
    """Standard M25 concrete + Fe415 steel combination.

    Most common grade in Indian construction practice.
    """
    return {"fck": 25.0, "fy": 415.0}


@pytest.fixture()
def m30_fe500() -> dict:
    """M30 concrete + Fe500 steel combination.

    Common for higher-grade construction.
    """
    return {"fck": 30.0, "fy": 500.0}


@pytest.fixture()
def m20_fe415() -> dict:
    """M20 concrete + Fe415 steel — minimum grade for RCC (IS 456 Cl. 6.1.2)."""
    return {"fck": 20.0, "fy": 415.0}


@pytest.fixture()
def standard_beam_230x500(m25_fe415: dict) -> dict:
    """Standard 230x500mm beam with M25/Fe415 — common residential beam.

    Returns dict with b_mm, D_mm, d_mm, fck, fy, cover_mm.
    """
    return {
        "b_mm": 230.0,
        "D_mm": 500.0,
        "d_mm": 450.0,
        "cover_mm": 25.0,
        **m25_fe415,
    }


@pytest.fixture()
def standard_beam_300x600(m30_fe500: dict) -> dict:
    """Standard 300x600mm beam with M30/Fe500 — common commercial beam."""
    return {
        "b_mm": 300.0,
        "D_mm": 600.0,
        "d_mm": 550.0,
        "cover_mm": 25.0,
        **m30_fe500,
    }
