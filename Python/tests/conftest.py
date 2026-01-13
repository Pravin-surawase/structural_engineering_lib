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
