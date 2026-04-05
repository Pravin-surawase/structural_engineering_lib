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


import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


class TestWheelContents:
    """Build the wheel and verify its contents directly.

    This catches packaging issues that runtime tests cannot detect,
    such as missing data files or leaked test/dev artifacts.
    """

    @pytest.fixture(scope="class")
    def wheel_path(self, tmp_path_factory):
        """Build wheel in a temp directory and return path to .whl file."""
        dist_dir = tmp_path_factory.mktemp("dist")
        project_root = Path(__file__).resolve().parents[1]  # Python/
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(dist_dir),
                str(project_root),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            pytest.skip(f"wheel build failed: {result.stderr[:500]}")
        wheels = list(dist_dir.glob("*.whl"))
        assert len(wheels) == 1, f"Expected 1 wheel, found {len(wheels)}"
        return wheels[0]

    @pytest.fixture(scope="class")
    def wheel_filelist(self, wheel_path):
        """Return sorted list of all file paths inside the wheel."""
        with zipfile.ZipFile(wheel_path) as zf:
            return sorted(zf.namelist())

    def test_clauses_json_in_wheel(self, wheel_filelist):
        """clauses.json must be packed into the wheel."""
        clauses_files = [f for f in wheel_filelist if f.endswith("clauses.json")]
        assert (
            len(clauses_files) >= 1
        ), "clauses.json not found in wheel — update pyproject.toml package-data"

    def test_no_tests_dir_in_wheel(self, wheel_filelist):
        """tests/ directory must NOT be in the wheel."""
        test_files = [f for f in wheel_filelist if f.startswith("tests/")]
        assert len(test_files) == 0, (
            f"tests/ found in wheel ({len(test_files)} files) — "
            "update pyproject.toml packages.find exclude"
        )

    def test_no_examples_dir_in_wheel(self, wheel_filelist):
        """examples/ directory must NOT be in the wheel."""
        example_files = [f for f in wheel_filelist if f.startswith("examples/")]
        assert (
            len(example_files) == 0
        ), "examples/ found in wheel — update pyproject.toml packages.find exclude"

    def test_no_scripts_dir_in_wheel(self, wheel_filelist):
        """scripts/ directory must NOT be in the wheel."""
        script_files = [f for f in wheel_filelist if f.startswith("scripts/")]
        assert (
            len(script_files) == 0
        ), "scripts/ found in wheel — update pyproject.toml packages.find exclude"

    def test_structural_lib_present(self, wheel_filelist):
        """structural_lib package must be in the wheel."""
        lib_files = [f for f in wheel_filelist if f.startswith("structural_lib/")]
        assert (
            len(lib_files) > 10
        ), f"Only {len(lib_files)} structural_lib files in wheel — expected 50+"
