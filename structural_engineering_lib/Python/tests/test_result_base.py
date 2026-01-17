# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for result_base module."""

from dataclasses import dataclass

import pytest

from structural_lib.result_base import BaseResult, CalculationResult, ComplianceResult


# Test concrete implementations
@dataclass(frozen=True)
class SimpleResult(BaseResult):
    """Simple test result."""

    value: float
    unit: str

    def summary(self) -> str:
        return f"Value: {self.value} {self.unit}"


@dataclass(frozen=True)
class CalculationTestResult(CalculationResult):
    """Test calculation result with metadata."""

    output: float
    design_method: str = ""
    assumptions: tuple[str, ...] = ()
    code_references: tuple[str, ...] = ()

    def summary(self) -> str:
        return f"Output: {self.output}"


@dataclass(frozen=True)
class ComplianceTestResult(ComplianceResult):
    """Test compliance result."""

    check_a: bool
    check_b: bool
    check_c: bool

    def _get_checks(self) -> dict[str, bool]:
        return {
            "check_a": self.check_a,
            "check_b": self.check_b,
            "check_c": self.check_c,
        }

    def summary(self) -> str:
        status = "PASS" if self.is_valid() else "FAIL"
        return f"Compliance: {status}"


class TestBaseResult:
    """Tests for BaseResult base class."""

    def test_summary_required(self):
        """Test that summary() must be implemented."""
        result = SimpleResult(123.45, "mm")
        assert result.summary() == "Value: 123.45 mm"

    def test_to_dict(self):
        """Test to_dict() serialization."""
        result = SimpleResult(123.45, "mm")
        data = result.to_dict()
        assert data == {"value": 123.45, "unit": "mm"}

    def test_validate_default(self):
        """Test default validate() returns valid."""
        result = SimpleResult(100.0, "N")
        is_valid, errors = result.validate()
        assert is_valid is True
        assert errors == []

    def test_immutability(self):
        """Test that results are frozen/immutable."""
        result = SimpleResult(50.0, "kN")
        with pytest.raises(AttributeError):  # FrozenInstanceError is a subclass
            result.value = 100.0  # type: ignore


class TestCalculationResult:
    """Tests for CalculationResult base class."""

    def test_with_metadata(self):
        """Test calculation result with metadata."""
        result = CalculationTestResult(
            output=250.0,
            design_method="limit_state",
            assumptions=("rectangular stress block", "tension only"),
            code_references=("IS 456 Cl. 38.1",),
        )
        assert result.output == 250.0
        assert result.design_method == "limit_state"
        # Can be list or tuple - both work
        assert list(result.assumptions) == ["rectangular stress block", "tension only"]
        assert list(result.code_references) == ["IS 456 Cl. 38.1"]

    def test_empty_metadata(self):
        """Test calculation result with no metadata."""
        result = CalculationTestResult(output=100.0)
        assert result.output == 100.0
        assert result.design_method == ""
        assert result.assumptions == ()
        assert result.code_references == ()

    def test_to_dict_with_metadata(self):
        """Test serialization includes metadata."""
        result = CalculationTestResult(
            output=300.0,
            design_method="test_method",
            assumptions=("assumption1",),
            code_references=("clause1",),
        )
        data = result.to_dict()
        assert data["output"] == 300.0
        assert data["design_method"] == "test_method"
        # Serialized as lists or tuples - both valid
        assert list(data["assumptions"]) == ["assumption1"]
        assert list(data["code_references"]) == ["clause1"]


class TestComplianceResult:
    """Tests for ComplianceResult base class."""

    def test_all_checks_passed(self):
        """Test is_valid() when all checks pass."""
        result = ComplianceTestResult(check_a=True, check_b=True, check_c=True)
        assert result.is_valid() is True
        assert result.failed_checks == []

    def test_some_checks_failed(self):
        """Test is_valid() when some checks fail."""
        result = ComplianceTestResult(check_a=True, check_b=False, check_c=True)
        assert result.is_valid() is False
        assert result.failed_checks == ["check_b"]

    def test_multiple_checks_failed(self):
        """Test failed_checks with multiple failures."""
        result = ComplianceTestResult(check_a=False, check_b=False, check_c=True)
        assert result.is_valid() is False
        assert set(result.failed_checks) == {"check_a", "check_b"}

    def test_validate_method(self):
        """Test validate() returns correct tuple."""
        # All pass
        result_pass = ComplianceTestResult(check_a=True, check_b=True, check_c=True)
        is_valid, failures = result_pass.validate()
        assert is_valid is True
        assert failures == []

        # Some fail
        result_fail = ComplianceTestResult(check_a=True, check_b=False, check_c=False)
        is_valid, failures = result_fail.validate()
        assert is_valid is False
        assert set(failures) == {"check_b", "check_c"}

    def test_summary(self):
        """Test summary() shows compliance status."""
        result_pass = ComplianceTestResult(check_a=True, check_b=True, check_c=True)
        assert "PASS" in result_pass.summary()

        result_fail = ComplianceTestResult(check_a=False, check_b=True, check_c=True)
        assert "FAIL" in result_fail.summary()


class TestNestedResults:
    """Tests for nested result objects."""

    @dataclass(frozen=True)
    class InnerResult(BaseResult):
        """Inner nested result."""

        inner_value: float

        def summary(self) -> str:
            return f"Inner: {self.inner_value}"

    @dataclass(frozen=True)
    class OuterResult(BaseResult):
        """Outer result containing inner result."""

        outer_value: float
        inner: "TestNestedResults.InnerResult"

        def summary(self) -> str:
            return f"Outer: {self.outer_value}\\n{self.inner.summary()}"

    def test_nested_to_dict(self):
        """Test to_dict() recursively converts nested results."""
        inner = self.InnerResult(inner_value=100.0)
        outer = self.OuterResult(outer_value=200.0, inner=inner)

        data = outer.to_dict()
        assert data["outer_value"] == 200.0
        assert data["inner"]["inner_value"] == 100.0

    def test_nested_summary(self):
        """Test summary() works with nested results."""
        inner = self.InnerResult(inner_value=50.0)
        outer = self.OuterResult(outer_value=150.0, inner=inner)

        summary = outer.summary()
        assert "Outer: 150.0" in summary
        assert "Inner: 50.0" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
