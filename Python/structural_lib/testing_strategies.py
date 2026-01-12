# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       testing_strategies
Description:  Engineering testing utilities for structural calculations (TASK-279)

Provides:
- Property-based testing patterns (using stdlib random - no hypothesis required)
- Boundary value testing for engineering calculations
- Regression testing helpers for comparing across versions
- Numerical tolerance testing utilities
- Engineering invariant validation

Example:
    >>> from structural_lib.testing_strategies import EngineeringTestCase
    >>> from structural_lib.testing_strategies import BoundaryValueGenerator
    >>>
    >>> # Generate boundary test cases
    >>> gen = BoundaryValueGenerator(min_val=100, max_val=1000)
    >>> for val in gen.generate():
    ...     result = my_function(val)
    ...     assert result > 0
"""

from __future__ import annotations

import hashlib
import json
import logging
import random
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

_logger = logging.getLogger(__name__)

T = TypeVar("T")


# -----------------------------------------------------------------------------
# Tolerance Testing
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ToleranceSpec:
    """Specification for numerical tolerance comparison.

    Attributes:
        relative: Relative tolerance (e.g., 0.001 = 0.1%)
        absolute: Absolute tolerance (e.g., 0.1 mm)
        description: Human-readable description

    Engineering guidance:
    - Areas: relative=0.001 (0.1%), absolute=1.0 mm²
    - Lengths: relative=0.001 (0.1%), absolute=0.1 mm
    - Forces: relative=0.001 (0.1%), absolute=0.01 kN
    - Stresses: relative=0.01 (1%), absolute=0.1 N/mm²
    """

    relative: float = 0.001  # 0.1% relative tolerance
    absolute: float = 0.1  # 0.1 absolute tolerance
    description: str = ""

    def is_close(self, actual: float, expected: float) -> bool:
        """Check if actual value is within tolerance of expected.

        Uses combined relative+absolute tolerance (like math.isclose).
        """
        diff = abs(actual - expected)
        threshold = self.absolute + self.relative * abs(expected)
        return diff <= threshold

    def assert_close(
        self,
        actual: float,
        expected: float,
        message: str = "",
    ) -> None:
        """Assert that actual is close to expected, with descriptive error."""
        if not self.is_close(actual, expected):
            diff = abs(actual - expected)
            rel_diff = diff / abs(expected) if expected != 0 else float("inf")
            raise AssertionError(
                f"{message}\n"
                f"  Expected: {expected:.6f}\n"
                f"  Actual:   {actual:.6f}\n"
                f"  Diff:     {diff:.6f} ({rel_diff*100:.3f}%)\n"
                f"  Tolerance: rel={self.relative}, abs={self.absolute}"
            )


# Common tolerance specs for structural engineering
AREA_TOLERANCE = ToleranceSpec(relative=0.001, absolute=1.0, description="mm²")
LENGTH_TOLERANCE = ToleranceSpec(relative=0.001, absolute=0.1, description="mm")
FORCE_TOLERANCE = ToleranceSpec(relative=0.001, absolute=0.01, description="kN")
STRESS_TOLERANCE = ToleranceSpec(relative=0.01, absolute=0.1, description="N/mm²")
RATIO_TOLERANCE = ToleranceSpec(relative=0.001, absolute=0.0001, description="ratio")


# -----------------------------------------------------------------------------
# Boundary Value Testing
# -----------------------------------------------------------------------------


@dataclass
class BoundaryValueGenerator:
    """Generate boundary values for testing.

    Produces: min, min+1, typical, max-1, max for integer-like values.
    For float ranges, produces min, min+epsilon, mid, max-epsilon, max.

    Attributes:
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        typical_val: Typical/common value (defaults to midpoint)
        epsilon: Small increment for near-boundary values
        include_invalid: Whether to include just-outside-boundary values

    Example:
        >>> gen = BoundaryValueGenerator(min_val=20, max_val=80)
        >>> list(gen.generate())
        [20, 20.1, 50.0, 79.9, 80]
    """

    min_val: float
    max_val: float
    typical_val: float | None = None
    epsilon: float | None = None
    include_invalid: bool = False

    def __post_init__(self) -> None:
        if self.typical_val is None:
            self.typical_val = (self.min_val + self.max_val) / 2
        if self.epsilon is None:
            self.epsilon = (self.max_val - self.min_val) * 0.001

    def generate(self) -> list[float]:
        """Generate boundary values."""
        # After __post_init__, these are guaranteed to be set
        eps = self.epsilon if self.epsilon is not None else 0.0
        typical = self.typical_val if self.typical_val is not None else self.min_val
        values: list[float] = [
            self.min_val,  # Minimum
            self.min_val + eps,  # Just above minimum
            typical,  # Typical value
            self.max_val - eps,  # Just below maximum
            self.max_val,  # Maximum
        ]
        if self.include_invalid:
            values.insert(0, self.min_val - eps)  # Below minimum
            values.append(self.max_val + eps)  # Above maximum
        return values


@dataclass
class BeamParameterRanges:
    """Standard parameter ranges for IS 456 beam design.

    Based on IS 456:2000 requirements and common practice.
    """

    # Geometry (mm)
    b_min: float = 200.0  # Minimum beam width
    b_max: float = 600.0  # Maximum beam width for typical beams
    D_min: float = 300.0  # Minimum overall depth
    D_max: float = 1000.0  # Maximum practical depth
    d_min: float = 250.0  # Minimum effective depth
    d_max: float = 950.0  # Maximum effective depth
    span_min: float = 2000.0  # Minimum span
    span_max: float = 10000.0  # Maximum span for simply supported
    cover_min: float = 25.0  # Minimum cover (mild exposure)
    cover_max: float = 75.0  # Maximum cover (severe exposure)

    # Materials (N/mm²)
    fck_min: float = 20.0  # M20 minimum
    fck_max: float = 50.0  # M50 maximum for normal design
    fy_min: float = 415.0  # Fe415 minimum
    fy_max: float = 550.0  # Fe550 maximum

    # Loads
    mu_min: float = 10.0  # kN·m minimum moment
    mu_max: float = 500.0  # kN·m practical maximum
    vu_min: float = 5.0  # kN minimum shear
    vu_max: float = 300.0  # kN practical maximum

    def get_boundary_generator(self, param: str) -> BoundaryValueGenerator:
        """Get boundary value generator for a parameter.

        Args:
            param: Parameter name (e.g., 'b', 'D', 'fck')

        Returns:
            BoundaryValueGenerator for that parameter
        """
        ranges = {
            "b": (self.b_min, self.b_max, 300.0),
            "D": (self.D_min, self.D_max, 500.0),
            "d": (self.d_min, self.d_max, 460.0),
            "span": (self.span_min, self.span_max, 6000.0),
            "cover": (self.cover_min, self.cover_max, 40.0),
            "fck": (self.fck_min, self.fck_max, 25.0),
            "fy": (self.fy_min, self.fy_max, 500.0),
            "mu": (self.mu_min, self.mu_max, 150.0),
            "vu": (self.vu_min, self.vu_max, 100.0),
        }
        if param not in ranges:
            raise ValueError(f"Unknown parameter: {param}")
        min_val, max_val, typical = ranges[param]
        return BoundaryValueGenerator(
            min_val=min_val, max_val=max_val, typical_val=typical
        )


# -----------------------------------------------------------------------------
# Property-Based Testing (stdlib implementation)
# -----------------------------------------------------------------------------


@dataclass
class RandomTestCase:
    """Container for randomly generated test case.

    Attributes:
        seed: Random seed used
        inputs: Input values generated
        expected_properties: Properties that should hold
    """

    seed: int
    inputs: dict[str, Any]
    expected_properties: list[str] = field(default_factory=list)


class PropertyBasedTester:
    """Property-based testing using stdlib random.

    Generates random test cases and validates that properties hold.

    Example:
        >>> tester = PropertyBasedTester(seed=42)
        >>> cases = tester.generate_beam_cases(n=100)
        >>> for case in cases:
        ...     result = design_beam(**case.inputs)
        ...     assert result.ast_provided >= result.ast_required
    """

    def __init__(self, seed: int | None = None):
        """Initialize with optional seed for reproducibility."""
        self.seed = seed if seed is not None else random.randint(0, 2**32)  # nosec B311
        self._rng = random.Random(self.seed)  # nosec B311

    def reset(self, seed: int | None = None) -> None:
        """Reset random state with new seed."""
        self.seed = seed if seed is not None else random.randint(0, 2**32)  # nosec B311
        self._rng = random.Random(self.seed)  # nosec B311

    def generate_beam_cases(
        self,
        n: int = 100,
        ranges: BeamParameterRanges | None = None,
    ) -> list[RandomTestCase]:
        """Generate random beam design test cases.

        Args:
            n: Number of cases to generate
            ranges: Parameter ranges (uses defaults if not provided)

        Returns:
            List of RandomTestCase objects
        """
        if ranges is None:
            ranges = BeamParameterRanges()

        cases = []
        for _ in range(n):
            case_seed = self._rng.randint(0, 2**32)
            case_rng = random.Random(case_seed)  # nosec B311

            # Generate consistent geometry
            b = case_rng.uniform(ranges.b_min, ranges.b_max)
            D = case_rng.uniform(max(ranges.D_min, b * 1.5), ranges.D_max)
            cover = case_rng.uniform(ranges.cover_min, ranges.cover_max)
            d = D - cover - 20  # Approximate effective depth

            # Ensure d is valid
            d = max(d, ranges.d_min)
            d = min(d, D - cover - 10)

            inputs = {
                "b_mm": round(b, 0),
                "D_mm": round(D, 0),
                "d_mm": round(d, 0),
                "cover_mm": round(cover, 0),
                "fck_nmm2": case_rng.choice([20, 25, 30, 35, 40, 45, 50]),
                "fy_nmm2": case_rng.choice([415, 500, 550]),
                "mu_knm": round(case_rng.uniform(ranges.mu_min, ranges.mu_max), 1),
                "vu_kn": round(case_rng.uniform(ranges.vu_min, ranges.vu_max), 1),
            }

            cases.append(
                RandomTestCase(
                    seed=case_seed,
                    inputs=inputs,
                    expected_properties=[
                        "ast_provided >= ast_required",
                        "ast_provided >= ast_min",
                        "is_ok is boolean",
                    ],
                )
            )

        return cases


# -----------------------------------------------------------------------------
# Engineering Invariants
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class InvariantCheck:
    """Engineering invariant that must always hold.

    Attributes:
        name: Short name for the invariant
        description: Detailed description
        check_fn: Function that returns True if invariant holds
        severity: How severe a violation is ('critical', 'warning')
    """

    name: str
    description: str
    check_fn: Callable[[Any], bool]
    severity: str = "critical"

    def check(self, result: Any) -> tuple[bool, str]:
        """Check if invariant holds.

        Returns:
            Tuple of (passed, message)
        """
        try:
            passed = self.check_fn(result)
            if passed:
                return True, f"✓ {self.name}"
            return False, f"✗ {self.name}: {self.description}"
        except Exception as e:
            return False, f"✗ {self.name}: Error - {e}"


class BeamDesignInvariants:
    """Standard invariants for beam design results.

    These invariants should always hold for valid IS 456 designs.
    """

    @staticmethod
    def get_all() -> list[InvariantCheck]:
        """Get all beam design invariants."""
        return [
            # Flexure invariants
            InvariantCheck(
                name="ast_provided >= ast_required",
                description="Provided steel must meet or exceed required",
                check_fn=lambda r: (
                    r.flexure.ast_provided >= r.flexure.ast_required
                    if hasattr(r, "flexure")
                    else True
                ),
            ),
            InvariantCheck(
                name="ast_provided >= ast_min",
                description="Provided steel must meet minimum reinforcement",
                check_fn=lambda r: (
                    r.flexure.ast_provided >= r.flexure.ast_min
                    if hasattr(r, "flexure") and hasattr(r.flexure, "ast_min")
                    else True
                ),
            ),
            InvariantCheck(
                name="ast_provided <= ast_max",
                description="Provided steel must not exceed maximum (4%)",
                check_fn=lambda r: (
                    r.flexure.ast_provided <= r.flexure.ast_max
                    if hasattr(r, "flexure") and hasattr(r.flexure, "ast_max")
                    else True
                ),
            ),
            # Shear invariants
            InvariantCheck(
                name="vn_kn >= vu_kn when is_ok",
                description="Nominal capacity must exceed demand if OK",
                check_fn=lambda r: (
                    not r.shear.is_ok or r.shear.vn_kn >= r.shear.vu_kn
                    if hasattr(r, "shear")
                    and hasattr(r.shear, "vn_kn")
                    and hasattr(r.shear, "vu_kn")
                    else True
                ),
            ),
            # Detailing invariants
            InvariantCheck(
                name="main_bars_dia >= 10mm",
                description="Main bar diameter must be at least 10mm",
                check_fn=lambda r: (
                    r.detailing.main_bar_dia >= 10
                    if hasattr(r, "detailing") and hasattr(r.detailing, "main_bar_dia")
                    else True
                ),
            ),
            InvariantCheck(
                name="stirrup_dia <= main_bar_dia",
                description="Stirrup diameter should not exceed main bar",
                check_fn=lambda r: (
                    r.detailing.stirrup_dia <= r.detailing.main_bar_dia
                    if hasattr(r, "detailing")
                    and hasattr(r.detailing, "stirrup_dia")
                    and hasattr(r.detailing, "main_bar_dia")
                    else True
                ),
            ),
        ]

    @staticmethod
    def check_all(result: Any) -> list[tuple[bool, str]]:
        """Check all invariants and return results."""
        invariants = BeamDesignInvariants.get_all()
        return [inv.check(result) for inv in invariants]


# -----------------------------------------------------------------------------
# Regression Testing
# -----------------------------------------------------------------------------


@dataclass
class RegressionBaseline:
    """Baseline data for regression testing.

    Attributes:
        version: Library version that produced baseline
        inputs: Input parameters
        outputs: Expected output values
        tolerances: Tolerance specs for each output
        hash: SHA-256 hash of baseline data
    """

    version: str
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    tolerances: dict[str, ToleranceSpec] = field(default_factory=dict)
    hash: str = ""

    def __post_init__(self) -> None:
        if not self.hash:
            data = json.dumps(
                {
                    "version": self.version,
                    "inputs": self.inputs,
                    "outputs": self.outputs,
                },
                sort_keys=True,
            )
            self.hash = hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "version": self.version,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "tolerances": {
                k: {"relative": v.relative, "absolute": v.absolute}
                for k, v in self.tolerances.items()
            },
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegressionBaseline:
        """Create from dictionary."""
        tolerances = {
            k: ToleranceSpec(relative=v["relative"], absolute=v["absolute"])
            for k, v in data.get("tolerances", {}).items()
        }
        return cls(
            version=data["version"],
            inputs=data["inputs"],
            outputs=data["outputs"],
            tolerances=tolerances,
            hash=data.get("hash", ""),
        )


class RegressionTestSuite:
    """Manage regression test baselines.

    Stores baselines in JSON format and compares against current results.

    Example:
        >>> suite = RegressionTestSuite("tests/baselines/")
        >>> suite.add_baseline("case1", inputs, outputs, version="0.16.0")
        >>> suite.save()
        >>> # Later:
        >>> results = suite.compare("case1", current_outputs)
    """

    def __init__(self, baseline_dir: str | Path):
        """Initialize with baseline directory."""
        self.baseline_dir = Path(baseline_dir)
        self.baselines: dict[str, RegressionBaseline] = {}
        self._load_baselines()

    def _load_baselines(self) -> None:
        """Load baselines from directory."""
        if not self.baseline_dir.exists():
            return

        for path in self.baseline_dir.glob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                name = path.stem
                self.baselines[name] = RegressionBaseline.from_dict(data)
            except Exception as e:
                _logger.warning(f"Failed to load baseline {path}: {e}")

    def add_baseline(
        self,
        name: str,
        inputs: dict[str, Any],
        outputs: dict[str, Any],
        version: str = "",
        tolerances: dict[str, ToleranceSpec] | None = None,
    ) -> RegressionBaseline:
        """Add a new baseline.

        Args:
            name: Baseline name
            inputs: Input parameters
            outputs: Expected outputs
            version: Library version
            tolerances: Tolerance specs for outputs

        Returns:
            Created RegressionBaseline
        """
        baseline = RegressionBaseline(
            version=version,
            inputs=inputs,
            outputs=outputs,
            tolerances=tolerances or {},
        )
        self.baselines[name] = baseline
        return baseline

    def save(self) -> None:
        """Save all baselines to directory."""
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        for name, baseline in self.baselines.items():
            path = self.baseline_dir / f"{name}.json"
            with open(path, "w") as f:
                json.dump(baseline.to_dict(), f, indent=2)

    def compare(
        self,
        name: str,
        actual_outputs: dict[str, Any],
    ) -> list[tuple[str, bool, str]]:
        """Compare actual outputs against baseline.

        Args:
            name: Baseline name
            actual_outputs: Current output values

        Returns:
            List of (output_name, passed, message) tuples
        """
        if name not in self.baselines:
            raise ValueError(f"Baseline '{name}' not found")

        baseline = self.baselines[name]
        results = []

        for key, expected in baseline.outputs.items():
            if key not in actual_outputs:
                results.append((key, False, f"Missing output: {key}"))
                continue

            actual = actual_outputs[key]

            # Get tolerance for this output
            tol = baseline.tolerances.get(
                key, ToleranceSpec(relative=0.001, absolute=0.1)
            )

            if isinstance(expected, int | float) and isinstance(actual, int | float):
                passed = tol.is_close(actual, expected)
                if passed:
                    results.append((key, True, f"{key}: {actual:.4f} ≈ {expected:.4f}"))
                else:
                    diff = abs(actual - expected)
                    results.append(
                        (
                            key,
                            False,
                            f"{key}: {actual:.4f} ≠ {expected:.4f} (Δ={diff:.4f})",
                        )
                    )
            else:
                passed = actual == expected
                results.append(
                    (
                        key,
                        passed,
                        f"{key}: {actual} {'==' if passed else '!='} {expected}",
                    )
                )

        return results


# -----------------------------------------------------------------------------
# Test Utilities
# -----------------------------------------------------------------------------


def assert_beam_design_valid(result: Any) -> None:
    """Assert that a beam design result satisfies all invariants.

    Raises AssertionError with detailed message if any invariant fails.
    """
    check_results = BeamDesignInvariants.check_all(result)
    failures = [(msg) for passed, msg in check_results if not passed]
    if failures:
        raise AssertionError(
            "Beam design invariant violations:\n" + "\n".join(failures)
        )


def create_test_case_id(inputs: dict[str, Any]) -> str:
    """Create a deterministic test case ID from inputs.

    Args:
        inputs: Input parameters

    Returns:
        Short hash-based ID like "TC-a1b2c3d4"
    """
    data = json.dumps(inputs, sort_keys=True)
    hash_val = hashlib.sha256(data.encode()).hexdigest()[:8]
    return f"TC-{hash_val}"
