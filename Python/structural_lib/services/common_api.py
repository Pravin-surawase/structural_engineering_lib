# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Pravin Surawase
"""
Module:       common_api
Description:  Shared validators, utilities and helper functions for the public API.

Split from services/api.py (ARCH-NEW-12) to support domain-based modules.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import platform as _platform
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from structural_lib.core.data_types import (
    CheckCodeReport,
    ValidationReport,
    VersionInfo,
)
from structural_lib.services import beam_pipeline, job_runner

# ============================================================================
# Unit & plausibility validators
# ============================================================================


def _require_is456_units(units: str) -> None:
    beam_pipeline.validate_units(units)


def _validate_plausibility(
    *,
    fck_nmm2: float | None = None,
    fy_nmm2: float | None = None,
    b_mm: float | None = None,
    d_mm: float | None = None,
    D_mm: float | None = None,
) -> None:
    """Catch common unit-confusion mistakes at the API boundary.

    Guards are deliberately generous (e.g. fck ≤ 120 allows UHPC).
    The goal is to catch Pa-vs-MPa and μm-vs-mm mistakes, not to
    enforce IS 456 material limits.
    """
    if fck_nmm2 is not None and fck_nmm2 <= 0:
        raise ValueError(
            f"fck_nmm2={fck_nmm2} must be positive. "
            "Concrete strength cannot be zero or negative."
        )
    if fck_nmm2 is not None and fck_nmm2 > 120:
        raise ValueError(
            f"fck_nmm2={fck_nmm2} seems too large. "
            "Expected N/mm² (e.g., 25), not Pa or kPa."
        )
    if fy_nmm2 is not None and fy_nmm2 <= 0:
        raise ValueError(
            f"fy_nmm2={fy_nmm2} must be positive. "
            "Steel strength cannot be zero or negative."
        )
    if fy_nmm2 is not None and fy_nmm2 > 700:
        raise ValueError(
            f"fy_nmm2={fy_nmm2} seems too large. "
            "Expected N/mm² (e.g., 415), not Pa or kPa."
        )
    if b_mm is not None and b_mm > 5000:
        raise ValueError(
            f"b_mm={b_mm} seems too large. " "Expected mm (e.g., 300), not μm or m."
        )
    if d_mm is not None and d_mm > 5000:
        raise ValueError(
            f"d_mm={d_mm} seems too large. " "Expected mm (e.g., 450), not μm or m."
        )
    if D_mm is not None and D_mm > 5000:
        raise ValueError(
            f"D_mm={D_mm} seems too large. " "Expected mm (e.g., 500), not μm or m."
        )
    if d_mm is not None and D_mm is not None and d_mm >= D_mm:
        raise ValueError(
            f"Effective depth d_mm ({d_mm}) must be less than overall depth "
            f"D_mm ({D_mm}). Per IS 456 Cl 26.4.1, "
            f"d = D − clear_cover − stirrup_dia − bar_dia/2. "
            f"Typical: d ≈ D − 40 to D − 60 mm."
        )


# ============================================================================
# Version & validation utilities
# ============================================================================


def get_library_version() -> str:
    """Return the installed package version.

    Returns:
        Package version string. Falls back to a default when package metadata
        is unavailable (e.g., running from a source checkout).
    """
    try:
        return version("structural-lib-is456")
    except PackageNotFoundError:
        pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.strip().startswith("version"):
                    return line.split("=", 1)[1].strip().strip('"')
        return "0.0.0-dev"


def validate_job_spec(path: str | Path) -> ValidationReport:
    """Validate a job.json specification file.

    Returns a ValidationReport with errors/warnings and summary details.
    """
    try:
        spec = job_runner.load_job_spec(path)
    except Exception as exc:
        return ValidationReport(ok=False, errors=[str(exc)])

    details = {
        "schema_version": spec.get("schema_version"),
        "job_id": spec.get("job_id"),
        "code": spec.get("code"),
        "units": spec.get("units"),
        "beam_keys": sorted(spec.get("beam", {}).keys()),
        "cases_count": len(spec.get("cases", [])),
    }
    return ValidationReport(ok=True, details=details)


def _beam_has_geometry(beam: dict[str, Any]) -> bool:
    geom = beam.get("geometry")
    if isinstance(geom, dict):
        if all(k in geom for k in ("b_mm", "D_mm", "d_mm")):
            return True
        if all(k in geom for k in ("b", "D", "d")):
            return True
    return all(k in beam for k in ("b", "D", "d"))


def _beam_has_materials(beam: dict[str, Any]) -> bool:
    mats = beam.get("materials")
    if isinstance(mats, dict):
        return any(k in mats for k in ("fck_nmm2", "fck")) and any(
            k in mats for k in ("fy_nmm2", "fy")
        )
    return any(k in beam for k in ("fck_nmm2", "fck")) and any(
        k in beam for k in ("fy_nmm2", "fy")
    )


def _beam_has_loads(beam: dict[str, Any]) -> bool:
    loads = beam.get("loads")
    if isinstance(loads, dict):
        return any(k in loads for k in ("mu_knm", "Mu")) and any(
            k in loads for k in ("vu_kn", "Vu")
        )
    return any(k in beam for k in ("mu_knm", "Mu")) and any(
        k in beam for k in ("vu_kn", "Vu")
    )


def validate_design_results(path: str | Path) -> ValidationReport:
    """Validate a design results JSON file (single or multi-beam)."""
    errors: list[str] = []
    warnings: list[str] = []

    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return ValidationReport(ok=False, errors=[str(exc)])

    if not isinstance(data, dict):
        return ValidationReport(
            ok=False, errors=["Results file must be a JSON object."]
        )

    schema_version = data.get("schema_version")
    if schema_version is None:
        errors.append("Missing required field 'schema_version'.")
    else:
        try:
            schema_version_int = int(schema_version)
            if schema_version_int != beam_pipeline.SCHEMA_VERSION:
                errors.append(
                    f"Unsupported schema_version: {schema_version_int} "
                    f"(expected {beam_pipeline.SCHEMA_VERSION})."
                )
        except (ValueError, TypeError):
            errors.append(f"Invalid schema_version: {schema_version!r}.")

    code = data.get("code")
    if not code:
        errors.append("Missing required field 'code'.")

    units = data.get("units")
    if not units:
        warnings.append("Missing 'units' field (recommended for stable outputs).")

    beams = data.get("beams")
    if not isinstance(beams, list) or not beams:
        errors.append("Missing or empty 'beams' list.")
        beams = []

    for idx, beam in enumerate(beams):
        if not isinstance(beam, dict):
            errors.append(f"Beam {idx}: expected object, got {type(beam).__name__}.")
            continue
        if not beam.get("beam_id"):
            errors.append(f"Beam {idx}: missing 'beam_id'.")
        if not beam.get("story"):
            errors.append(f"Beam {idx}: missing 'story'.")
        if not _beam_has_geometry(beam):
            errors.append(f"Beam {idx}: missing geometry fields.")
        if not _beam_has_materials(beam):
            errors.append(f"Beam {idx}: missing material fields.")
        if not _beam_has_loads(beam):
            errors.append(f"Beam {idx}: missing load fields.")

    details = {
        "schema_version": schema_version,
        "code": code,
        "units": units,
        "beams_count": len(beams),
    }

    return ValidationReport(
        ok=not errors, errors=errors, warnings=warnings, details=details
    )


# ============================================================================
# Code self-validation (check_code)
# ============================================================================

# Standard IS 456 symbols exempt from unit-suffix naming
_EXEMPT_PARAMS = frozenset(
    {
        "fck",
        "fy",
        "fsc",
        "Es",
        "Ec",
        # common non-dimensional / generic names
        "self",
        "cls",
        "args",
        "kwargs",
        "return",
        "n",
        "n_bars",
        "num_bars",
        "num_legs",
        "num_layers",
        "pt",
        "pc",
        "k",
        "beta",
        "alpha",
        "gamma",
        "ratio",
        "is_sway",
        "braced",
        "code_id",
        "standard",
        "section_type",
        "bar_dia",
        "stirrup_dia",
        "cover",
        "clear_cover",
        "exposure",
        "beam_type",
        "support_condition",
        "end_condition",
        "end_condition_top",
        "end_condition_bottom",
        "load_type",
        "span_type",
        "grade",
        "steel_grade",
        "verbose",
        "debug",
        "strict",
    }
)

# Known dimensional parameter stems that MUST have unit suffixes
_DIMENSIONAL_STEMS = frozenset(
    {
        "b",
        "d",
        "D",
        "L",
        "span",
        "width",
        "depth",
        "height",
        "area",
        "moment",
        "shear",
        "force",
        "stress",
        "load",
        "pressure",
        "weight",
        "length",
        "dia",
        "diameter",
        "spacing",
        "pitch",
        "cover",
    }
)


def _check_importable(code_id: str) -> tuple[bool, list[str]]:
    """Check that all expected sub-packages are importable."""
    issues: list[str] = []
    code_pkg = f"structural_lib.codes.{code_id.lower()}"
    subpackages = ("beam", "column", "footing", "common")
    for sub in subpackages:
        mod_path = f"{code_pkg}.{sub}"
        try:
            importlib.import_module(mod_path)
        except ImportError as exc:
            issues.append(f"ImportError for {mod_path}: {exc}")
    return (len(issues) == 0), issues


def _check_decorated(code_id: str) -> tuple[bool, list[str]]:
    """Check that public functions have @clause decorator."""
    issues: list[str] = []
    code_pkg = f"structural_lib.codes.{code_id.lower()}"

    # Get all registered (decorated) functions from traceability
    try:
        traceability = importlib.import_module(f"{code_pkg}.traceability")
        registered = traceability.get_all_registered_functions()
    except (ImportError, AttributeError) as exc:
        issues.append(f"Cannot access traceability: {exc}")
        return False, issues

    registered_qualnames = set(registered.keys())

    # Scan subpackages for public functions
    subpackages = ("beam", "column", "footing", "common")
    undecorated: list[str] = []

    for sub in subpackages:
        mod_path = f"{code_pkg}.{sub}"
        try:
            pkg = importlib.import_module(mod_path)
        except ImportError:
            continue

        # Check the package and its child modules
        modules_to_check = [pkg]
        if hasattr(pkg, "__path__"):
            import pkgutil

            for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):
                if modname.startswith("_"):
                    continue
                try:
                    child = importlib.import_module(f"{mod_path}.{modname}")
                    modules_to_check.append(child)
                except ImportError:
                    pass

        for mod in modules_to_check:
            for name, obj in inspect.getmembers(mod, inspect.isfunction):
                if name.startswith("_"):
                    continue
                if obj.__module__ != mod.__name__:
                    continue  # skip re-exports
                func_key = f"{obj.__module__}.{obj.__qualname__}"
                if func_key not in registered_qualnames:
                    undecorated.append(func_key)

    if undecorated:
        for fn in undecorated[:10]:  # cap to avoid noise
            issues.append(f"Missing @clause: {fn}")
        if len(undecorated) > 10:
            issues.append(f"... and {len(undecorated) - 10} more undecorated functions")

    return (len(undecorated) == 0), issues


def _check_frozen(code_id: str) -> tuple[bool, list[str]]:
    """Check that result dataclasses are frozen."""
    from structural_lib.core import data_types

    issues: list[str] = []
    result_classes: list[type] = []

    for name, obj in inspect.getmembers(data_types, inspect.isclass):
        if not name.endswith("Result"):
            continue
        if hasattr(obj, "__dataclass_params__"):
            result_classes.append(obj)

    not_frozen: list[str] = []
    for cls in result_classes:
        params = getattr(cls, "__dataclass_params__", None)
        if params is not None and not params.frozen:
            not_frozen.append(cls.__name__)

    if not_frozen:
        for cls_name in not_frozen:
            issues.append(f"Not frozen: {cls_name}")

    return (len(not_frozen) == 0), issues


def _check_results_valid(code_id: str) -> tuple[bool, list[str]]:
    """Check that result dataclasses have to_dict() method."""
    from structural_lib.core import data_types

    issues: list[str] = []
    missing_to_dict: list[str] = []

    for name, obj in inspect.getmembers(data_types, inspect.isclass):
        if not name.endswith("Result"):
            continue
        if not hasattr(obj, "__dataclass_params__"):
            continue
        if not hasattr(obj, "to_dict"):
            missing_to_dict.append(name)

    if missing_to_dict:
        for cls_name in missing_to_dict:
            issues.append(f"Missing to_dict(): {cls_name}")

    return (len(missing_to_dict) == 0), issues


def _check_params_named(code_id: str) -> tuple[bool, list[str]]:
    """Check that dimensional parameters have unit suffixes (heuristic)."""
    issues: list[str] = []
    code_pkg = f"structural_lib.codes.{code_id.lower()}"
    unit_suffixes = ("_mm", "_kn", "_knm", "_nmm2", "_m", "_mm2", "_kn_m")
    subpackages = ("beam", "column", "footing", "common")
    suspect_params: list[str] = []

    for sub in subpackages:
        mod_path = f"{code_pkg}.{sub}"
        try:
            pkg = importlib.import_module(mod_path)
        except ImportError:
            continue

        modules_to_check = [pkg]
        if hasattr(pkg, "__path__"):
            import pkgutil

            for _importer, modname, _ispkg in pkgutil.iter_modules(pkg.__path__):
                if modname.startswith("_"):
                    continue
                try:
                    child = importlib.import_module(f"{mod_path}.{modname}")
                    modules_to_check.append(child)
                except ImportError:
                    pass

        for mod in modules_to_check:
            for name, obj in inspect.getmembers(mod, inspect.isfunction):
                if name.startswith("_"):
                    continue
                if obj.__module__ != mod.__name__:
                    continue
                try:
                    sig = inspect.signature(obj)
                except (ValueError, TypeError):
                    continue
                for param_name in sig.parameters:
                    if param_name in _EXEMPT_PARAMS:
                        continue
                    if any(param_name.endswith(s) for s in unit_suffixes):
                        continue
                    # Check if it looks dimensional
                    param_lower = param_name.lower()
                    if any(
                        stem == param_lower or param_lower.startswith(stem + "_")
                        for stem in _DIMENSIONAL_STEMS
                    ):
                        suspect_params.append(
                            f"{obj.__module__}.{obj.__qualname__}({param_name})"
                        )

    if suspect_params:
        for sp in suspect_params[:10]:
            issues.append(f"Param without unit suffix: {sp}")
        if len(suspect_params) > 10:
            issues.append(
                f"... and {len(suspect_params) - 10} more params without unit suffix"
            )

    return (len(suspect_params) == 0), issues


def _check_boundary_violations(code_id: str) -> tuple[bool, list[str]]:
    """Check that codes.is456 modules don't import from services/ or fastapi_app/."""
    issues: list[str] = []
    code_pkg_name = f"codes.{code_id.lower()}"

    # Find the codes/is456 directory
    try:
        code_mod = importlib.import_module(f"structural_lib.{code_pkg_name}")
    except ImportError as exc:
        issues.append(f"Cannot import code package: {exc}")
        return False, issues

    if not hasattr(code_mod, "__path__"):
        return True, issues

    code_dir = Path(code_mod.__path__[0])
    forbidden_imports = (
        "structural_lib.services",
        "structural_lib.fastapi_app",
        "fastapi_app",
        "services",
    )

    for py_file in code_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError) as exc:
            issues.append(f"Parse error in {py_file.name}: {exc}")
            continue

        rel_path = py_file.relative_to(code_dir)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(f) for f in forbidden_imports):
                        issues.append(
                            f"Boundary violation in {rel_path}: " f"import {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module and any(
                    node.module.startswith(f) for f in forbidden_imports
                ):
                    issues.append(
                        f"Boundary violation in {rel_path}: "
                        f"from {node.module} import ..."
                    )

    return (len(issues) == 0), issues


def check_code(code_id: str) -> CheckCodeReport:
    """Validate that a design code implementation meets the API contract.

    Inspired by scikit-learn's ``check_estimator()``. Checks that a
    registered design code has proper clause decorators, frozen results,
    named parameters, and respects architecture boundaries.

    Args:
        code_id: Code identifier, e.g. ``"IS456"``.

    Returns:
        :class:`~structural_lib.core.data_types.CheckCodeReport` with
        pass/fail for each check category.

    Raises:
        KeyError: If *code_id* is not registered in
            :class:`~structural_lib.core.registry.CodeRegistry`.

    Example:
        >>> from structural_lib import check_code
        >>> report = check_code("IS456")
        >>> print(report.summary())
    """
    from structural_lib.core.registry import CodeRegistry

    if not CodeRegistry.is_registered(code_id):
        available = ", ".join(CodeRegistry.list_codes()) or "none"
        raise KeyError(
            f"Design code '{code_id}' not registered. Available: {available}"
        )

    all_issues: list[str] = []

    importable_ok, importable_issues = _check_importable(code_id)
    all_issues.extend(importable_issues)

    decorated_ok, decorated_issues = _check_decorated(code_id)
    all_issues.extend(decorated_issues)

    frozen_ok, frozen_issues = _check_frozen(code_id)
    all_issues.extend(frozen_issues)

    results_ok, results_issues = _check_results_valid(code_id)
    all_issues.extend(results_issues)

    params_ok, params_issues = _check_params_named(code_id)
    all_issues.extend(params_issues)

    boundary_ok, boundary_issues = _check_boundary_violations(code_id)
    all_issues.extend(boundary_issues)

    return CheckCodeReport(
        code_id=code_id,
        all_importable=importable_ok,
        all_decorated=decorated_ok,
        all_frozen=frozen_ok,
        all_results_valid=results_ok,
        all_params_named=params_ok,
        no_boundary_violations=boundary_ok,
        issues=tuple(all_issues),
    )


# ============================================================================
# Diagnostic version report (TASK-725)
# ============================================================================

# Packages to check — order matters for display.
_VERSION_DEPS: tuple[str, ...] = (
    "pydantic",
    "numpy",
    "pandas",
    "hypothesis",
    "ezdxf",
    "jinja2",
    "reportlab",
    "pytest",
    "httpx",
)


def show_versions(*, as_dict: bool = False) -> VersionInfo | None:
    """Print library and environment version information.

    Inspired by ``sklearn.show_versions()`` and ``pd.show_versions()``.
    Reports library version, Python version, platform, registered
    design codes, and optional dependency versions.

    Args:
        as_dict: If ``True``, return a
            :class:`~structural_lib.core.data_types.VersionInfo`
            dataclass instead of printing.  If ``False`` (default),
            print to stdout and return ``None``.

    Returns:
        :class:`~structural_lib.core.data_types.VersionInfo` when
        *as_dict* is ``True``, otherwise ``None``.

    Example:
        >>> show_versions()
        structural_lib: 0.21.6
        Python: 3.12.4
        Platform: macOS-14.5-arm64
        ...
    """
    from structural_lib.core.registry import CodeRegistry

    # -- dependency versions ------------------------------------------------
    deps: dict[str, str | None] = {}
    for pkg in _VERSION_DEPS:
        try:
            deps[pkg] = version(pkg)
        except PackageNotFoundError:
            deps[pkg] = None

    info = VersionInfo(
        library_version=get_library_version(),
        python_version=_platform.python_version(),
        platform=_platform.platform(),
        design_codes=tuple(CodeRegistry.list_codes()),
        dependencies=deps,
    )

    if as_dict:
        return info

    print(info.to_string())  # noqa: T201 – intentional diagnostic print
    return None
