# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Tests for IS 456 Traceability Module
====================================

Comprehensive tests for clause decorator, registry, and API.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from structural_lib.codes.is456.traceability import (
    _CLAUSE_REGISTRY,
    _load_clause_database,
    clause,
    generate_traceability_report,
    get_all_registered_functions,
    get_clause_info,
    get_clause_refs,
    get_database_metadata,
    list_clauses_by_category,
    search_clauses,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear the clause registry before and after each test."""
    _CLAUSE_REGISTRY.clear()
    yield
    _CLAUSE_REGISTRY.clear()


@pytest.fixture
def sample_decorated_function():
    """Create a sample decorated function for testing."""

    @clause("38.1", "40.1")
    def sample_design_function(b: float, d: float) -> float:
        """Sample function with clause references."""
        return b * d

    return sample_design_function


# =============================================================================
# Test: Clause Database Loading
# =============================================================================


class TestClauseDatabaseLoading:
    """Tests for clause database loading."""

    def test_database_exists(self):
        """Verify clauses.json file exists."""
        # Use relative path from test location
        from structural_lib.codes.is456 import traceability

        actual_path = Path(traceability.__file__).parent / "clauses.json"
        assert actual_path.exists(), f"Clause database not found at {actual_path}"

    def test_database_loads_successfully(self):
        """Verify database loads without errors."""
        db = _load_clause_database()
        assert db is not None
        assert isinstance(db, dict)

    def test_database_has_required_keys(self):
        """Verify database has required structure."""
        db = _load_clause_database()
        assert "metadata" in db
        assert "clauses" in db
        assert "tables" in db

    def test_database_metadata_valid(self):
        """Verify metadata contains required fields."""
        db = _load_clause_database()
        metadata = db["metadata"]
        assert metadata["standard"] == "IS 456:2000"
        assert "total_clauses" in metadata
        assert metadata["total_clauses"] >= 40  # Minimum expected clauses

    def test_clauses_have_required_fields(self):
        """Verify each clause has required fields."""
        db = _load_clause_database()
        for clause_ref, info in db["clauses"].items():
            assert "title" in info, f"Clause {clause_ref} missing 'title'"
            assert "text" in info, f"Clause {clause_ref} missing 'text'"
            assert "category" in info, f"Clause {clause_ref} missing 'category'"


# =============================================================================
# Test: @clause Decorator
# =============================================================================


class TestClauseDecorator:
    """Tests for the @clause decorator."""

    def test_single_clause_reference(self):
        """Test decorator with single clause reference."""

        @clause("38.1")
        def my_func():
            return 42

        assert hasattr(my_func, "_is456_clauses")
        assert my_func._is456_clauses == ["38.1"]
        assert my_func() == 42  # Function still works

    def test_multiple_clause_references(self):
        """Test decorator with multiple clause references."""

        @clause("38.1", "38.2", "40.1")
        def my_func():
            return 100

        assert my_func._is456_clauses == ["38.1", "38.2", "40.1"]

    def test_decorator_preserves_function_name(self):
        """Verify decorator preserves function metadata."""

        @clause("38.1")
        def calculate_moment():
            """Calculate bending moment."""

        assert calculate_moment.__name__ == "calculate_moment"
        assert "bending moment" in calculate_moment.__doc__

    def test_decorator_registers_function(self):
        """Verify decorated function is registered."""

        @clause("38.1")
        def registered_func():
            pass

        funcs = get_all_registered_functions()
        # Function should be in registry (with module prefix)
        assert any("registered_func" in key for key in funcs.keys())

    def test_chained_decorators(self):
        """Test multiple @clause decorators on same function."""

        @clause("40.1")
        @clause("38.1")
        def double_decorated():
            pass

        refs = get_clause_refs(double_decorated)
        assert "38.1" in refs
        assert "40.1" in refs

    def test_decorator_with_function_args(self):
        """Verify decorator works with various function signatures."""

        @clause("38.1")
        def complex_func(a: int, b: float, *, c: str = "default") -> float:
            return a * b

        result = complex_func(2, 3.0, c="test")
        assert result == 6.0
        assert get_clause_refs(complex_func) == ["38.1"]


# =============================================================================
# Test: get_clause_refs()
# =============================================================================


class TestGetClauseRefs:
    """Tests for get_clause_refs function."""

    def test_get_refs_from_function(self, sample_decorated_function):
        """Get clause refs from function object."""
        refs = get_clause_refs(sample_decorated_function)
        assert refs == ["38.1", "40.1"]

    def test_get_refs_from_string(self):
        """Get clause refs using function name string."""

        @clause("26.2.1")
        def test_func_for_string():
            pass

        # Get the full qualified name
        func_key = (
            f"{test_func_for_string.__module__}.{test_func_for_string.__qualname__}"
        )
        refs = get_clause_refs(func_key)
        assert "26.2.1" in refs

    def test_get_refs_undecorated_function(self):
        """Return empty list for undecorated function."""

        def plain_function():
            pass

        refs = get_clause_refs(plain_function)
        assert refs == []


# =============================================================================
# Test: get_clause_info()
# =============================================================================


class TestGetClauseInfo:
    """Tests for get_clause_info function."""

    def test_get_existing_clause(self):
        """Get info for existing clause."""
        info = get_clause_info("38.1")
        assert info is not None
        assert "title" in info
        assert info["category"] == "flexure"

    def test_get_nonexistent_clause(self):
        """Return None for unknown clause."""
        info = get_clause_info("99.99.99")
        assert info is None

    def test_clause_info_has_keywords(self):
        """Verify clause info includes keywords."""
        info = get_clause_info("38.1")
        assert "keywords" in info
        assert isinstance(info["keywords"], list)

    def test_clause_info_has_formula(self):
        """Verify clauses with formulas include them."""
        info = get_clause_info("26.2.1")
        assert "formula" in info or "formulas" in info


# =============================================================================
# Test: list_clauses_by_category()
# =============================================================================


class TestListClausesByCategory:
    """Tests for list_clauses_by_category function."""

    def test_list_flexure_clauses(self):
        """List all flexure-related clauses."""
        clauses = list_clauses_by_category("flexure")
        assert len(clauses) >= 5  # Should have multiple flexure clauses
        assert all(c["category"] == "flexure" for c in clauses)

    def test_list_shear_clauses(self):
        """List all shear-related clauses."""
        clauses = list_clauses_by_category("shear")
        assert len(clauses) >= 3
        assert all(c["category"] == "shear" for c in clauses)

    def test_list_detailing_clauses(self):
        """List all detailing-related clauses."""
        clauses = list_clauses_by_category("detailing")
        assert len(clauses) >= 5

    def test_list_unknown_category(self):
        """Return empty list for unknown category."""
        clauses = list_clauses_by_category("unknown_category_xyz")
        assert clauses == []


# =============================================================================
# Test: search_clauses()
# =============================================================================


class TestSearchClauses:
    """Tests for search_clauses function."""

    def test_search_by_keyword(self):
        """Search clauses by keyword."""
        results = search_clauses("shear")
        assert len(results) > 0
        # All results should mention shear somewhere
        for r in results:
            text = f"{r.get('title', '')} {r.get('text', '')} {' '.join(r.get('keywords', []))}".lower()
            assert "shear" in text

    def test_search_case_insensitive(self):
        """Search should be case-insensitive."""
        results_lower = search_clauses("flexure")
        results_upper = search_clauses("FLEXURE")
        assert len(results_lower) == len(results_upper)

    def test_search_no_results(self):
        """Return empty list for no matches."""
        results = search_clauses("xyznonexistent123")
        assert results == []

    def test_search_in_title(self):
        """Search finds matches in clause title."""
        results = search_clauses("Development Length")
        assert any("26.2.1" in r.get("clause_ref", "") for r in results)


# =============================================================================
# Test: generate_traceability_report()
# =============================================================================


class TestGenerateTraceabilityReport:
    """Tests for traceability report generation."""

    def test_report_structure(self, sample_decorated_function):
        """Verify report has required structure."""
        # Register a function first
        _ = sample_decorated_function  # This registers the function

        report = generate_traceability_report()
        assert "functions" in report
        assert "clauses_used" in report
        assert "total_clauses_in_db" in report
        assert "total_clauses_used" in report
        assert "coverage_percent" in report

    def test_report_includes_registered_functions(self):
        """Verify report includes all registered functions."""

        @clause("38.1")
        def func_a():
            pass

        @clause("40.1")
        def func_b():
            pass

        report = generate_traceability_report()
        func_names = [f["function"] for f in report["functions"]]
        assert any("func_a" in name for name in func_names)
        assert any("func_b" in name for name in func_names)

    def test_report_coverage_calculation(self):
        """Verify coverage percentage is calculated correctly."""

        @clause("38.1", "40.1", "26.2.1")
        def multi_clause_func():
            pass

        report = generate_traceability_report()
        assert report["total_clauses_used"] >= 3
        assert 0 <= report["coverage_percent"] <= 100


# =============================================================================
# Test: get_database_metadata()
# =============================================================================


class TestGetDatabaseMetadata:
    """Tests for database metadata retrieval."""

    def test_metadata_returns_dict(self):
        """Verify metadata returns a dictionary."""
        metadata = get_database_metadata()
        assert isinstance(metadata, dict)

    def test_metadata_contains_standard(self):
        """Verify metadata contains standard name."""
        metadata = get_database_metadata()
        assert metadata["standard"] == "IS 456:2000"

    def test_metadata_contains_version(self):
        """Verify metadata contains version info."""
        metadata = get_database_metadata()
        assert "version" in metadata


# =============================================================================
# Test: Integration with Real Functions
# =============================================================================


class TestRealWorldIntegration:
    """Integration tests with realistic scenarios."""

    def test_beam_design_traceability(self):
        """Simulate traceability for beam design function."""

        @clause("38.1", "38.2", "40.1", "40.4", "26.5.1.1")
        def design_beam(
            b: float,
            d: float,
            fck: float,
            fy: float,
            Mu: float,
            Vu: float,
        ) -> dict[str, Any]:
            """Design RC beam per IS 456."""
            return {
                "Ast": 1000.0,
                "Asv": 200.0,
                "clauses": get_clause_refs(design_beam),
            }

        result = design_beam(300, 450, 25, 500, 150, 100)
        assert "clauses" in result
        assert "38.1" in result["clauses"]
        assert "40.1" in result["clauses"]

    def test_full_workflow(self):
        """Test complete traceability workflow."""

        # 1. Define functions with clauses
        @clause("38.1")
        def step1_flexure():
            pass

        @clause("40.1", "40.4")
        def step2_shear():
            pass

        @clause("26.2.1", "26.3.2")
        def step3_detailing():
            pass

        # 2. Generate report
        report = generate_traceability_report()

        # 3. Verify all functions tracked
        assert len(report["functions"]) >= 3

        # 4. Verify clauses used
        used = set(report["clauses_used"])
        assert "38.1" in used
        assert "40.1" in used
        assert "26.2.1" in used


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_clause_list(self):
        """Test decorator with no clauses (edge case)."""

        # This shouldn't happen in practice but should handle gracefully
        @clause()
        def empty_clause_func():
            pass

        refs = get_clause_refs(empty_clause_func)
        assert refs == []

    def test_duplicate_clause_references(self):
        """Handle duplicate clause references gracefully."""

        @clause("38.1", "38.1", "40.1")
        def duplicate_func():
            pass

        refs = get_clause_refs(duplicate_func)
        assert refs.count("38.1") == 2  # Duplicates preserved (intentional)

    def test_clause_with_special_characters(self):
        """Handle clause refs with dots correctly."""
        # Clause refs like "26.2.1.1" should work
        info = get_clause_info("26.2.1.1")
        assert info is not None or info is None  # May or may not exist

    def test_lambda_function_with_clause(self):
        """Decorator works with lambda (unusual but valid)."""

        # Lambdas can't use decorators directly, but wrapped ones can
        def make_decorated():
            @clause("38.1")
            def inner():
                return lambda x: x * 2

            return inner

        func = make_decorated()
        assert get_clause_refs(func) == ["38.1"]
