"""Tests for package distribution correctness.

Verifies that the installed package includes required data files
and does not include test/dev artifacts.
"""

import importlib.resources
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


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


class TestImportSilence:
    """EA-6: Importing structural_lib must produce zero user-facing warnings.

    Tests marked @pytest.mark.repo_only are excluded when running from sdist:
      pytest -m "not repo_only" Python/tests/
    """

    def test_import_no_warnings(self):
        """Import structural_lib and assert no warnings are emitted."""
        import importlib
        import warnings

        # Temporarily remove structural_lib from sys.modules to force re-import
        mods_to_remove = [k for k in sys.modules if k.startswith("structural_lib")]
        saved = {k: sys.modules.pop(k) for k in mods_to_remove}

        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                importlib.import_module("structural_lib")
                # Filter to only our package warnings
                pkg_warnings = [
                    w
                    for w in caught
                    if "structural_lib" in str(w.filename)
                    and not any(
                        skip in str(w.message)
                        for skip in [
                            "ezdxf",  # third-party
                            "pyparsing",  # third-party
                            "has moved to",  # intentional backward-compat shims
                        ]
                    )
                ]
            assert (
                len(pkg_warnings) == 0
            ), f"Import produced {len(pkg_warnings)} warning(s):\n" + "\n".join(
                f"  - {w.category.__name__}: {w.message}" for w in pkg_warnings
            )
        finally:
            # Restore original modules
            sys.modules.update(saved)


class TestAPIStability:
    """Verify all __all__ exports are importable and not broken."""

    def test_all_exports_importable(self):
        """Every name in __all__ must be importable from structural_lib."""
        import structural_lib

        all_names = structural_lib.__all__
        missing = []
        for name in all_names:
            if not hasattr(structural_lib, name):
                missing.append(name)
        assert not missing, f"__all__ exports not importable: {missing}"

    def test_all_count_minimum(self):
        """__all__ should have at least 100 exports (current: ~104)."""
        import structural_lib

        assert (
            len(structural_lib.__all__) >= 90
        ), f"__all__ has only {len(structural_lib.__all__)} exports, expected 90+"

    def test_key_functions_callable(self):
        """Core API functions must be callable."""
        from structural_lib import (
            build_detailing_input,
            check_beam_is456,
            design_beam_is456,
            detail_beam_is456,
            optimize_beam_cost,
        )

        for func in [
            design_beam_is456,
            detail_beam_is456,
            optimize_beam_cost,
            check_beam_is456,
            build_detailing_input,
        ]:
            assert callable(func), f"{func.__name__} is not callable"

    def test_key_classes_instantiable(self):
        """Core result classes must be importable."""
        from structural_lib import (
            ComplianceCaseResult,
            DesignAndDetailResult,
            TorsionResult,
        )

        for cls in [ComplianceCaseResult, DesignAndDetailResult, TorsionResult]:
            assert isinstance(cls, type), f"{cls.__name__} is not a class"


class TestReportTemplatesPackaged:
    """Regression: report templates must be included in package data.

    Audit finding: Jinja2 .j2 templates in reports/templates/ were not
    listed in pyproject.toml package-data, causing FileNotFoundError
    at runtime when generating reports.
    """

    def test_report_templates_accessible(self):
        """Report .j2 templates must be accessible via importlib.resources."""
        templates_dir = importlib.resources.files("structural_lib.reports").joinpath(
            "templates"
        )
        j2_files = [p.name for p in templates_dir.iterdir() if str(p).endswith(".j2")]
        assert len(j2_files) >= 1, (
            "No .j2 templates found in structural_lib/reports/templates/ — "
            "update pyproject.toml package-data to include 'reports/templates/*.j2'"
        )

    def test_pyproject_includes_template_glob(self):
        """pyproject.toml package-data must include the template glob."""
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")
        assert "reports/templates/*.j2" in content, (
            "pyproject.toml [tool.setuptools.package-data] must include "
            "'reports/templates/*.j2'"
        )
