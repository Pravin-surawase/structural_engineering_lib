# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       result_base
Description:  Base classes for result objects

This module defines the foundational base class for all result objects in the library.
All result dataclasses should inherit from BaseResult to ensure consistent behavior.

Related:
- docs/guidelines/result-object-standard.md
- TASK-214: Create result object base classes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class BaseResult(ABC):
    """
    Abstract base class for all result objects in structural_engineering_lib.

    All result dataclasses MUST:
    - Be frozen (immutable)
    - Implement summary() for human-readable output
    - Support to_dict() for serialization (provided by this base class)

    Example:
        >>> @dataclass(frozen=True)
        ... class MyResult(BaseResult):
        ...     value: float
        ...     unit: str
        ...
        ...     def summary(self) -> str:
        ...         return f"Result: {self.value} {self.unit}"
        ...
        >>> result = MyResult(123.45, "mm")
        >>> print(result.summary())
        Result: 123.45 mm
        >>> print(result.to_dict())
        {'value': 123.45, 'unit': 'mm'}
    """

    @abstractmethod
    def summary(self) -> str:
        """
        Return human-readable summary of the result.

        This method MUST be implemented by all subclasses.

        Returns:
            Formatted string suitable for console display or reports

        Example:
            >>> result.summary()
            'Flexure Design Summary:\\n  Required Ast: 1250 mm²\\n  Capacity: 165.5 kN-m'
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        Convert result to dictionary for serialization.

        Uses dataclasses.asdict() to recursively convert nested dataclasses.

        Returns:
            Dictionary with all fields expanded. Nested dataclasses are
            recursively converted to dicts.

        Example:
            >>> result.to_dict()
            {'moment_capacity_knm': 165.5, 'reinforcement': {'area_mm2': 1250, ...}}
        """
        return asdict(self)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate the result object.

        Override this method to add custom validation logic.
        Default implementation always returns valid.

        Returns:
            Tuple of (is_valid, error_messages)
            - is_valid: True if result is valid
            - error_messages: List of validation error messages (empty if valid)

        Example:
            >>> is_valid, errors = result.validate()
            >>> if not is_valid:
            ...     for error in errors:
            ...         print(f"Validation error: {error}")
        """
        return (True, [])


class CalculationResult(BaseResult):
    """
    Base class for calculation results that include metadata.

    NOTE: This is a mixin class, not a dataclass. Subclasses should be dataclasses
    that include the metadata fields they need.

    Common metadata fields to include in subclasses:
    - design_method: Method used for calculation
    - assumptions: List of assumptions made
    - code_references: IS 456 clause references

    Example:
        >>> @dataclass(frozen=True)
        ... class FlexureResult(CalculationResult):
        ...     moment_capacity_knm: float
        ...     ast_required_mm2: float
        ...     design_method: str = ""
        ...     assumptions: tuple[str, ...] = ()
        ...
        ...     def summary(self) -> str:
        ...         return f"Capacity: {self.moment_capacity_knm:.1f} kN-m"
    """


@dataclass(frozen=True)
class ComplianceResult(BaseResult):
    """
    Base class for compliance check results.

    Provides common functionality for tracking pass/fail checks.

    Attributes:
        checks_passed: Dict mapping check name to boolean result
        failed_checks: List of failed check names (computed property)

    Example:
        >>> @dataclass(frozen=True)
        ... class MyComplianceResult(ComplianceResult):
        ...     checks_passed: dict[str, bool]
        ...
        ...     def summary(self) -> str:
        ...         status = "PASS" if self.is_valid() else "FAIL"
        ...         return f"Compliance: {status}"
        ...
        ...     def _get_checks(self) -> dict[str, bool]:
        ...         return self.checks_passed
    """

    @abstractmethod
    def _get_checks(self) -> dict[str, bool]:
        """
        Return dictionary of check names to pass/fail status.

        Subclasses must implement this to expose their checks.

        Returns:
            Dict mapping check name (str) to pass status (bool)
        """
        ...

    def is_valid(self) -> bool:
        """
        Return True if all compliance checks passed.

        Returns:
            True if all checks in _get_checks() returned True
        """
        checks = self._get_checks()
        return all(checks.values())

    @property
    def failed_checks(self) -> list[str]:
        """
        Return list of failed check names.

        Returns:
            List of check names that returned False
        """
        checks = self._get_checks()
        return [name for name, passed in checks.items() if not passed]

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate compliance result.

        Returns:
            Tuple of (is_valid, failed_check_names)
        """
        return (self.is_valid(), self.failed_checks)
