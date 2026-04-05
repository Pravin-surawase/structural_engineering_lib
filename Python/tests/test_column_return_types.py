# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""Tests for UX-02: Column API return type unification.

Verifies that column API functions return typed dataclass objects
(not raw dicts) while maintaining backward compatibility via
DictCompatMixin (dict-style access: result['key'], 'key' in result, etc.).

References:
    UX-02 Phase 1: Column return type unification
    IS 456:2000, Cl. 39.3 (axial), Cl. 39.5 (uniaxial)
"""

from __future__ import annotations

import dataclasses

import pytest

from structural_lib import (
    design_column_axial_is456,
    design_short_column_uniaxial_is456,
)
from structural_lib.core.data_types import (
    ColumnAxialResult,
    ColumnUniaxialResult,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture()
def axial_result() -> ColumnAxialResult:
    """Standard axial capacity result for a 300x300 column."""
    return design_column_axial_is456(
        fck=25.0,
        fy=415.0,
        Ag_mm2=90_000.0,  # 300x300
        Asc_mm2=1_800.0,  # 2% steel
    )


@pytest.fixture()
def uniaxial_result() -> ColumnUniaxialResult:
    """Standard uniaxial result for a 300x450 column."""
    return design_short_column_uniaxial_is456(
        Pu_kN=1200.0,
        Mu_kNm=150.0,
        b_mm=300.0,
        D_mm=450.0,
        le_mm=3000.0,
        fck=25.0,
        fy=415.0,
        Asc_mm2=2700.0,
        d_prime_mm=50.0,
        l_unsupported_mm=3000.0,
    )


# ============================================================================
# 1. Dataclass attribute access
# ============================================================================


class TestColumnAxialDataclass:
    """UX-02: design_column_axial_is456 returns typed ColumnAxialResult."""

    def test_returns_dataclass_instance(self, axial_result: ColumnAxialResult) -> None:
        """Return type is ColumnAxialResult dataclass, not dict."""
        assert isinstance(axial_result, ColumnAxialResult)
        assert dataclasses.is_dataclass(axial_result)

    def test_attribute_access(self, axial_result: ColumnAxialResult) -> None:
        """Dataclass fields are accessible as attributes."""
        assert hasattr(axial_result, "Pu_kN")
        assert hasattr(axial_result, "fck")
        assert hasattr(axial_result, "fy")
        assert hasattr(axial_result, "Ag_mm2")
        assert hasattr(axial_result, "Asc_mm2")
        assert hasattr(axial_result, "Ac_mm2")
        assert hasattr(axial_result, "steel_ratio")
        assert hasattr(axial_result, "classification")
        assert hasattr(axial_result, "is_safe")
        assert hasattr(axial_result, "warnings")

    def test_pu_kn_is_positive(self, axial_result: ColumnAxialResult) -> None:
        """Axial capacity must be a positive float."""
        assert isinstance(axial_result.Pu_kN, float)
        assert axial_result.Pu_kN > 0

    def test_is_safe_is_bool(self, axial_result: ColumnAxialResult) -> None:
        """is_safe must be a boolean."""
        assert isinstance(axial_result.is_safe, bool)


class TestColumnUniaxialDataclass:
    """UX-02: design_short_column_uniaxial_is456 returns typed ColumnUniaxialResult."""

    def test_returns_dataclass_instance(
        self, uniaxial_result: ColumnUniaxialResult
    ) -> None:
        """Return type is ColumnUniaxialResult dataclass, not dict."""
        assert isinstance(uniaxial_result, ColumnUniaxialResult)
        assert dataclasses.is_dataclass(uniaxial_result)

    def test_attribute_access(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """Dataclass fields are accessible as attributes."""
        assert hasattr(uniaxial_result, "Pu_kN")
        assert hasattr(uniaxial_result, "Mu_kNm")
        assert hasattr(uniaxial_result, "Pu_cap_kN")
        assert hasattr(uniaxial_result, "Mu_cap_kNm")
        assert hasattr(uniaxial_result, "utilization_ratio")
        assert hasattr(uniaxial_result, "eccentricity_mm")
        assert hasattr(uniaxial_result, "is_safe")
        assert hasattr(uniaxial_result, "classification")
        assert hasattr(uniaxial_result, "governing_check")
        assert hasattr(uniaxial_result, "clause_ref")

    def test_utilization_is_numeric(
        self, uniaxial_result: ColumnUniaxialResult
    ) -> None:
        """utilization_ratio must be a positive float."""
        assert isinstance(uniaxial_result.utilization_ratio, float)
        assert uniaxial_result.utilization_ratio > 0

    def test_is_safe_is_bool(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """is_safe must be a boolean."""
        assert isinstance(uniaxial_result.is_safe, bool)


# ============================================================================
# 2. Dict-style backward compatibility (DictCompatMixin)
# ============================================================================


class TestAxialDictCompat:
    """UX-02: ColumnAxialResult supports dict-style access for backward compat."""

    def test_getitem(self, axial_result: ColumnAxialResult) -> None:
        """result['Pu_kN'] returns same value as result.Pu_kN."""
        assert axial_result["Pu_kN"] == axial_result.Pu_kN

    def test_contains(self, axial_result: ColumnAxialResult) -> None:
        """'Pu_kN' in result works."""
        assert "Pu_kN" in axial_result
        assert "is_safe" in axial_result
        assert "nonexistent_field" not in axial_result

    def test_get_with_default(self, axial_result: ColumnAxialResult) -> None:
        """result.get('key', default) works like dict.get()."""
        assert axial_result.get("Pu_kN") == axial_result.Pu_kN
        assert axial_result.get("nonexistent", 42) == 42

    def test_keys(self, axial_result: ColumnAxialResult) -> None:
        """result.keys() returns field names."""
        k = axial_result.keys()
        assert "Pu_kN" in k
        assert "is_safe" in k

    def test_values(self, axial_result: ColumnAxialResult) -> None:
        """result.values() returns field values."""
        v = axial_result.values()
        assert axial_result.Pu_kN in v

    def test_items(self, axial_result: ColumnAxialResult) -> None:
        """result.items() returns (key, value) pairs."""
        items = dict(axial_result.items())
        assert items["Pu_kN"] == axial_result.Pu_kN

    def test_iter(self, axial_result: ColumnAxialResult) -> None:
        """Iterating over result yields field names (like dict)."""
        field_names = list(axial_result)
        assert "Pu_kN" in field_names
        assert "is_safe" in field_names

    def test_getitem_missing_key_raises(self, axial_result: ColumnAxialResult) -> None:
        """result['bad_key'] raises KeyError, not AttributeError."""
        with pytest.raises(KeyError):
            _ = axial_result["nonexistent_field"]


class TestUniaxialDictCompat:
    """UX-02: ColumnUniaxialResult supports dict-style access."""

    def test_getitem(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """result['is_safe'] returns same value as result.is_safe."""
        assert uniaxial_result["is_safe"] == uniaxial_result.is_safe

    def test_contains(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """'utilization_ratio' in result works."""
        assert "utilization_ratio" in uniaxial_result
        assert "bogus" not in uniaxial_result

    def test_get_with_default(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """result.get('key', default) matches dict behaviour."""
        assert uniaxial_result.get("Mu_kNm") == uniaxial_result.Mu_kNm
        assert uniaxial_result.get("missing", -1) == -1

    def test_getitem_missing_key_raises(
        self, uniaxial_result: ColumnUniaxialResult
    ) -> None:
        """result['bad_key'] raises KeyError."""
        with pytest.raises(KeyError):
            _ = uniaxial_result["no_such_field"]


# ============================================================================
# 3. to_dict() — returns plain dict
# ============================================================================


class TestAxialToDict:
    """UX-02: ColumnAxialResult.to_dict() returns a plain dict."""

    def test_to_dict_returns_dict(self, axial_result: ColumnAxialResult) -> None:
        """to_dict() returns a plain dict, not a dataclass."""
        d = axial_result.to_dict()
        assert isinstance(d, dict)
        assert not dataclasses.is_dataclass(d)

    def test_to_dict_has_all_fields(self, axial_result: ColumnAxialResult) -> None:
        """to_dict() includes every dataclass field."""
        d = axial_result.to_dict()
        for f in dataclasses.fields(axial_result):
            assert f.name in d, f"Missing field: {f.name}"

    def test_to_dict_values_match(self, axial_result: ColumnAxialResult) -> None:
        """to_dict() values match attribute values."""
        d = axial_result.to_dict()
        assert d["Pu_kN"] == axial_result.Pu_kN
        assert d["fck"] == axial_result.fck
        assert d["steel_ratio"] == axial_result.steel_ratio


class TestUniaxialToDict:
    """UX-02: ColumnUniaxialResult.to_dict() returns a plain dict."""

    def test_to_dict_returns_dict(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """to_dict() returns a plain dict."""
        d = uniaxial_result.to_dict()
        assert isinstance(d, dict)
        assert not dataclasses.is_dataclass(d)

    def test_to_dict_has_all_fields(
        self, uniaxial_result: ColumnUniaxialResult
    ) -> None:
        """to_dict() includes every field."""
        d = uniaxial_result.to_dict()
        for f in dataclasses.fields(uniaxial_result):
            assert f.name in d, f"Missing field: {f.name}"

    def test_to_dict_values_match(self, uniaxial_result: ColumnUniaxialResult) -> None:
        """Values match attribute values."""
        d = uniaxial_result.to_dict()
        assert d["Pu_kN"] == uniaxial_result.Pu_kN
        assert d["is_safe"] == uniaxial_result.is_safe
        assert d["utilization_ratio"] == uniaxial_result.utilization_ratio


# ============================================================================
# 4. Frozen dataclass — immutability
# ============================================================================


class TestFrozenDataclass:
    """UX-02: Column result dataclasses are frozen (immutable)."""

    def test_axial_result_is_frozen(self, axial_result: ColumnAxialResult) -> None:
        """ColumnAxialResult cannot be mutated."""
        with pytest.raises(dataclasses.FrozenInstanceError):
            axial_result.Pu_kN = 999.0  # type: ignore[misc]

    def test_uniaxial_result_is_frozen(
        self, uniaxial_result: ColumnUniaxialResult
    ) -> None:
        """ColumnUniaxialResult cannot be mutated."""
        with pytest.raises(dataclasses.FrozenInstanceError):
            uniaxial_result.is_safe = False  # type: ignore[misc]
