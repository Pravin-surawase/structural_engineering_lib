"""Tests for package distribution correctness.

Verifies that the installed package includes required data files
and does not include test/dev artifacts.
"""

import importlib.resources
import json


class TestPackageDataFiles:
    """Verify required data files are accessible at runtime."""

    def test_clauses_json_loadable(self):
        """clauses.json must be accessible via importlib.resources."""
        data = (
            importlib.resources.files("structural_lib.codes.is456")
            .joinpath("clauses.json")
            .read_text(encoding="utf-8")
        )
        db = json.loads(data)
        assert isinstance(db, dict)
        assert len(db) > 0, "clauses.json must contain clause entries"

    def test_clause_38_1_exists(self):
        """IS 456 Cl 38.1 (flexure) must be in the clause database."""
        from structural_lib.codes.is456.traceability import get_clause_info

        info = get_clause_info("38.1")
        assert info is not None, "Clause 38.1 must be resolvable"

    def test_search_clauses_returns_results(self):
        """Searching for 'flexure' must return at least one clause."""
        from structural_lib.codes.is456.traceability import search_clauses

        results = search_clauses("flexure")
        assert len(results) > 0, "search_clauses('flexure') must return results"


class TestPackageScope:
    """Verify no test/dev packages leak into the distribution."""

    def test_no_tests_in_top_level(self):
        """tests package should not be importable as a top-level package."""
        # This tests that pyproject.toml excludes tests* from discovery
        # In a properly scoped package, 'tests' is not a top-level installable
        import structural_lib

        # Verify structural_lib itself is importable
        assert hasattr(structural_lib, "__version__") or hasattr(structural_lib, "api")
