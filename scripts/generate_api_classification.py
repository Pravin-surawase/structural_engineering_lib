#!/usr/bin/env python3
"""Generate or validate the pre-1.0 public API classification registry.

The registry covers all declared exports and every public-looking callable on
the supported root and service facades plus the retained compatibility module.
Names outside ``__all__`` are classified as internal so they cannot silently
become an undocumented public surface. The canonical family facade is also
inventoried so compatibility projections cannot be mistaken for the owner.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import inspect
import json
import os
import re
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import Any, get_args

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

DEFAULT_OUT = REPO_ROOT / "docs/reference/api-classification.json"
DEFAULT_COMPATIBILITY_OUT = REPO_ROOT / "docs/reference/api-compatibility-ledger.json"
SURFACE_POLICY = (
    ("structural_lib.design.is456.beam", "preview"),
    ("structural_lib.design.is456.torsion", "preview"),
    ("structural_lib.design.is456.column", "preview"),
    ("structural_lib.design.is456.slab", "preview"),
    ("structural_lib.design.is456.wall", "preview"),
    ("structural_lib.design.is456.staircase", "preview"),
    ("structural_lib.design.is456.deep_beam", "preview"),
    ("structural_lib.design.is456.flat_slab", "preview"),
    ("structural_lib.design.is456.isolated_footing", "preview"),
    ("structural_lib.design.is456.combined_footing", "preview"),
    ("structural_lib.design.is456.strap_footing", "preview"),
    ("structural_lib", "preview"),
    ("structural_lib.services.api", "preview"),
    ("structural_lib.api", "compatibility"),
)
_ADVANCED_MODULE_PREFIXES = (
    "structural_lib.services.audit",
    "structural_lib.services.calculation_report",
    "structural_lib.services.costing",
    "structural_lib.services.multi_objective_optimizer",
)
_HOLD_MODULE_PREFIXES = (
    "structural_lib.services.etabs_import",
    "structural_lib.visualization",
    "structural_lib.codes.is456.load_analysis",
)
_CANONICAL_TASK_EXPORTS = frozenset({"design_beam_is456"})
_CANONICAL_FACADE_MODULES = frozenset(
    module for module, _classification in SURFACE_POLICY if ".design.is456." in module
)
_CANONICAL_SUPPORT_EXPORTS = frozenset(
    {"EffectiveDepthBasisV1", "EffectiveDepthResolutionV1"}
)
_COMPATIBILITY_TAXONOMY = (
    "CANONICAL_OWNER",
    "INTENTIONAL_PUBLIC_FACADE",
    "DELEGATING_COMPATIBILITY_SHIM",
    "MAINTAINED_CALLER_MIGRATED",
    "HELD_COMPATIBILITY",
    "RETIREMENT_CANDIDATE_PENDING_APPROVAL",
    "OUT_OF_SCOPE_PRESERVED",
    "BLOCKED_AMBIGUOUS_OWNER",
)
_P5_HELD_COMPATIBILITY = frozenset(
    {
        "create_job_from_etabs",
        "create_jobs_from_etabs_csv",
        "load_etabs_csv",
        "normalize_etabs_forces",
    }
)
_LEDGER_RECORD_SECTIONS = (
    "canonical_owners",
    "facade_projections",
    "root_stub_modules",
    "root_stub_projections",
    "additional_module_records",
    "caller_records",
    "blocked_ambiguous_callers",
    "retirement_candidates",
)
_LEDGER_MISSING_VALUE = {"__p7_missing_value__": True}
_TEXT_SUFFIXES = frozenset(
    {
        ".json",
        ".md",
        ".mjs",
        ".py",
        ".sh",
        ".toml",
        ".ts",
        ".tsx",
        ".yaml",
        ".yml",
    }
)
_SKIP_PARTS = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "build",
        "dist",
        "htmlcov",
        "node_modules",
        "sdist",
        "site",
    }
)
_EXCLUDED_SCAN_PATHS = frozenset(
    {
        "docs/SESSION_LOG.md",
        "docs/reference/api-classification.json",
        "docs/reference/api-compatibility-ledger.json",
        "docs/reference/api-manifest.json",
    }
)
_INTENTIONAL_COMPATIBILITY_PATHS = frozenset(
    {
        "Python/scripts/pre_release_check.sh",
        "Python/README.md",
        "README.md",
        "docs/contributing/agent-coding-standards.md",
        "docs/getting-started/python-quickstart.md",
        "docs/guidelines/folder-structure-governance.md",
        "docs/guides/etabs-exported-snapshot-v1.md",
        "docs/reference/api-levels.md",
        "docs/reference/api-stability.md",
        "docs/reference/api.md",
        "docs/reference/deprecation-policy.md",
        "scripts/benchmark_api.py",
        "scripts/check_api.py",
        "scripts/discover_api_signatures.py",
        "scripts/external_cli_test.py",
        "scripts/generate_api_classification.py",
        "scripts/generate_api_manifest.py",
        "scripts/launch_stack.sh",
        "scripts/parity_dashboard.py",
        "scripts/release.py",
        "scripts/sync_numbers.py",
        "scripts/test_api_parity.py",
        "scripts/validate_api_contracts.py",
        "scripts/verify_canonical_transport_artifact.py",
    }
)
_INTENTIONAL_COMPATIBILITY_PREFIXES = (
    "Python/tests/",
    "fastapi_app/tests/",
    "docs/migration/",
    "docs/guidelines/migration-",
)
_OUT_OF_SCOPE_PREFIXES = (
    "docs/_archive/",
    "docs/_internal/",
    "docs/blog-drafts/",
    "docs/publications/",
    "docs/verification/",
)
_OUT_OF_SCOPE_PARTS = frozenset({"fixtures", "vendor", "vendors"})
_OPTIONAL_DEPENDENCY_STUB_SYMBOLS = frozenset(
    {
        "structural_lib.dxf_export.TextEntityAlignment",
        "structural_lib.dxf_export.ezdxf",
        "structural_lib.dxf_export.units",
    }
)
_CANONICAL_DOCSTRING_SECTIONS = (
    "parameters",
    "returns",
    "raises",
    "examples",
    "limitations",
    "provenance",
)
_DOCSTRING_SECTION_PATTERNS = {
    section: re.compile(rf"(?m)^\s*{section.title()}:?\s*$")
    for section in _CANONICAL_DOCSTRING_SECTIONS
}
_DOCUMENTED_BEAM_OPERATIONS = frozenset(
    {
        "bbs",
        "check",
        "check_supplied",
        "design",
        "design_and_detail",
        "detail",
        "input",
        "load",
        "load_supplied_check",
    }
)
_TEMPORARY_DOCUMENTATION_DEBT_BASELINE = frozenset(
    {
        "structural_lib.design.is456.column.check",
        "structural_lib.design.is456.column.design",
        "structural_lib.design.is456.column.input",
        "structural_lib.design.is456.column.load",
        "structural_lib.design.is456.combined_footing.design",
        "structural_lib.design.is456.combined_footing.input",
        "structural_lib.design.is456.combined_footing.load",
        "structural_lib.design.is456.deep_beam.design",
        "structural_lib.design.is456.deep_beam.input",
        "structural_lib.design.is456.deep_beam.load",
        "structural_lib.design.is456.flat_slab.design",
        "structural_lib.design.is456.flat_slab.input",
        "structural_lib.design.is456.flat_slab.load",
        "structural_lib.design.is456.isolated_footing.design",
        "structural_lib.design.is456.isolated_footing.input",
        "structural_lib.design.is456.isolated_footing.load",
        "structural_lib.design.is456.slab.design_continuous_one_way",
        "structural_lib.design.is456.slab.design_one_way",
        "structural_lib.design.is456.slab.design_two_way",
        "structural_lib.design.is456.slab.load_continuous_one_way",
        "structural_lib.design.is456.slab.load_one_way",
        "structural_lib.design.is456.slab.load_two_way",
        "structural_lib.design.is456.staircase.design",
        "structural_lib.design.is456.staircase.input",
        "structural_lib.design.is456.staircase.load",
        "structural_lib.design.is456.strap_footing.design",
        "structural_lib.design.is456.strap_footing.input",
        "structural_lib.design.is456.strap_footing.load",
        "structural_lib.design.is456.torsion.design",
        "structural_lib.design.is456.torsion.input",
        "structural_lib.design.is456.torsion.load",
        "structural_lib.design.is456.wall.design",
        "structural_lib.design.is456.wall.input",
        "structural_lib.design.is456.wall.load",
    }
)
_BEAM_EXAMPLE_INVENTORY = (
    *(
        {
            "example_id": f"is456.beam.facade.{operation}.docstring",
            "operation": operation,
            "kind": "DOCSTRING",
            "expected": "EXECUTES_FROM_EXACT_WHEEL",
            "path": "docs/reference/beam-facade.md",
        }
        for operation in sorted(_DOCUMENTED_BEAM_OPERATIONS)
    ),
    {
        "example_id": "is456.beam.design.valid",
        "operation": "design",
        "kind": "VALID",
        "expected": "PASS",
        "path": "docs/cookbook/python/beam-design.md",
    },
    {
        "example_id": "is456.beam.design.invalid",
        "operation": "load",
        "kind": "INVALID",
        "expected": "INPUT_OUT_OF_RANGE:actions.mu_knm",
        "path": "docs/cookbook/python/beam-design.md",
    },
    {
        "example_id": "is456.beam.design.engineering-fail",
        "operation": "design",
        "kind": "ENGINEERING_FAIL",
        "expected": "FAIL",
        "path": "docs/cookbook/python/beam-design.md",
    },
    {
        "example_id": "is456.beam.supplied.valid",
        "operation": "check_supplied",
        "kind": "VALID",
        "expected": "PASS",
        "path": "docs/cookbook/python/beam-supplied-check.md",
    },
    {
        "example_id": "is456.beam.supplied.invalid",
        "operation": "load_supplied_check",
        "kind": "INVALID",
        "expected": "CROSS_FIELD_CONTRACT_INVALID:section",
        "path": "docs/cookbook/python/beam-supplied-check.md",
    },
    {
        "example_id": "is456.beam.supplied.engineering-fail",
        "operation": "check_supplied",
        "kind": "ENGINEERING_FAIL",
        "expected": "FAIL",
        "path": "docs/cookbook/python/beam-supplied-check.md",
    },
    {
        "example_id": "is456.beam.supplied.engineering-hold",
        "operation": "check_supplied",
        "kind": "ENGINEERING_HOLD",
        "expected": "HOLD",
        "path": "docs/cookbook/python/beam-supplied-check.md",
    },
)


def _documentation_role(
    *, kind: str, declared_export: bool, claim_disposition: str
) -> str:
    """Classify one symbol's public documentation obligation."""

    if not declared_export:
        return "INTERNAL_NO_PUBLIC_DOCUMENTATION"
    if kind == "function" and claim_disposition == "canonical":
        return "CANONICAL_WORKFLOW_OPERATION"
    if kind == "function" and claim_disposition == "advanced":
        return "EXPERT_OPERATION"
    if kind == "function":
        return "COMPATIBILITY_OPERATION"
    if kind == "class" and claim_disposition == "canonical":
        return "CANONICAL_CONTRACT"
    if kind == "class":
        return "PUBLIC_CONTRACT"
    return "PUBLIC_VALUE"


def _documentation_record(
    *,
    value: object,
    qualified_name: str,
    kind: str,
    declared_export: bool,
    claim_disposition: str,
) -> dict[str, Any]:
    """Return measurable documentation obligations for one classified symbol."""

    role = _documentation_role(
        kind=kind,
        declared_export=declared_export,
        claim_disposition=claim_disposition,
    )
    docstring = inspect.getdoc(value) or ""
    present_sections = sorted(
        section
        for section, pattern in _DOCSTRING_SECTION_PATTERNS.items()
        if pattern.search(docstring)
    )
    required_sections = (
        list(_CANONICAL_DOCSTRING_SECTIONS)
        if role == "CANONICAL_WORKFLOW_OPERATION"
        else []
    )
    missing_sections = sorted(set(required_sections) - set(present_sections))
    example_ids = [
        item["example_id"]
        for item in _BEAM_EXAMPLE_INVENTORY
        if qualified_name == "structural_lib.design.is456.beam." + item["operation"]
    ]
    return {
        "role": role,
        "obligations": (
            [
                "EXACT_SIGNATURE",
                "COMPLETE_DOCSTRING",
                "GENERATED_REFERENCE",
                "REGISTERED_EXECUTABLE_EXAMPLE",
            ]
            if role == "CANONICAL_WORKFLOW_OPERATION"
            else ["CLASSIFIED_PUBLIC_ROLE"]
            if declared_export
            else []
        ),
        "signature": _signature(value) if kind == "function" else "",
        "docstring_sections": present_sections,
        "missing_docstring_sections": missing_sections,
        "example_ids": example_ids,
    }


def _kind(value: object) -> str:
    if inspect.isclass(value):
        return "class"
    if inspect.isfunction(value) or inspect.isbuiltin(value):
        return "function"
    if inspect.ismodule(value):
        return "module"
    return "value"


def _signature(value: object) -> str:
    if not (
        inspect.isclass(value) or inspect.isfunction(value) or inspect.isbuiltin(value)
    ):
        return ""
    if inspect.isclass(value) and issubclass(value, Enum):
        return "(value)"
    try:
        signature = inspect.signature(value)
    except (TypeError, ValueError):
        return "(...)"
    if inspect.isclass(value):
        parameters = list(signature.parameters.values())
        if parameters and parameters[0].name in {"self", "cls"}:
            signature = signature.replace(parameters=parameters[1:])
    return str(signature).replace("typing.Annotated[", "Annotated[")


def _canonical_owner(value: object, fallback: str) -> str:
    if inspect.ismodule(value):
        return str(getattr(value, "__name__", fallback))
    module = getattr(value, "__module__", None)
    name = getattr(value, "__qualname__", None) or getattr(value, "__name__", None)
    if module and name:
        # Parameterized typing aliases inherit their factory's metadata. Only
        # name that metadata as the owner when it resolves to this exact object.
        owner = importlib.import_module(module)
        for part in name.split("."):
            owner = getattr(owner, part, None)
        if owner is value:
            return f"{module}.{name}"
    return fallback


def _import_qualified_type(path: str) -> type[Any]:
    module_name, _, name = path.rpartition(".")
    value = getattr(importlib.import_module(module_name), name)
    if not inspect.isclass(value):
        raise RuntimeError(f"Family request type is not a class: {path}")
    return value


def _nested_model_types(root: type[Any]) -> tuple[type[Any], ...]:
    """Return one Pydantic request type and all nested request model types."""

    found: dict[str, type[Any]] = {}
    pending = [root]
    while pending:
        model = pending.pop()
        qualified = f"{model.__module__}.{model.__qualname__}"
        if qualified in found:
            continue
        found[qualified] = model
        for field in getattr(model, "model_fields", {}).values():
            candidates = [field.annotation]
            while candidates:
                candidate = candidates.pop()
                candidates.extend(get_args(candidate))
                if (
                    inspect.isclass(candidate)
                    and hasattr(candidate, "model_fields")
                    and candidate is not model
                ):
                    pending.append(candidate)
    return tuple(found[name] for name in sorted(found))


def _validator_inventory(root: type[Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for model in _nested_model_types(root):
        decorators = getattr(model, "__pydantic_decorators__", None)
        records.append(
            {
                "request_type": f"{model.__module__}.{model.__qualname__}",
                "field_validators": sorted(getattr(decorators, "field_validators", {})),
                "model_validators": sorted(getattr(decorators, "model_validators", {})),
            }
        )
    return records


def _family_workflow_record(workflow: Any) -> dict[str, Any]:
    from structural_lib.services.contracts.common import (
        ValidationDimension,
        schema_leaf_paths,
    )

    request_type = _import_qualified_type(workflow.request_type)
    schema = request_type.model_json_schema(mode="validation")
    field_contracts = tuple(request_type.field_contracts)
    contract_paths = {contract.path for contract in field_contracts}
    leaf_paths = schema_leaf_paths(request_type)
    unowned = sorted(set(leaf_paths) - contract_paths)
    if unowned:
        raise RuntimeError(
            f"{workflow.journey_id} has unowned advertised fields: {unowned}"
        )
    represented = {
        dimension.value
        for contract in field_contracts
        for dimension in contract.dimensions
    }
    all_dimensions = {dimension.value for dimension in ValidationDimension}
    validators = _validator_inventory(request_type)
    has_request_relation_validator = any(
        record["model_validators"] for record in validators
    )
    return {
        "journey_id": workflow.journey_id,
        "module": workflow.module,
        "request_contract": workflow.request_contract,
        "request_type": workflow.request_type,
        "request_schema": schema,
        "request_schema_sha256": hashlib.sha256(
            json.dumps(schema, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        "request_field_contracts": [
            contract.model_dump(mode="json") for contract in field_contracts
        ],
        "request_field_count": len(leaf_paths),
        "unowned_field_paths": unowned,
        "represented_validation_dimensions": sorted(represented),
        "not_applicable_validation_dimensions": sorted(all_dimensions - represented),
        "validator_inventory": validators,
        "cross_field_validation_owner": (
            "STRICT_REQUEST_MODEL"
            if has_request_relation_validator
            else f"DELEGATED_TO_MAINTAINED_OWNER:{workflow.compatibility_owner}"
        ),
        "result_contract": workflow.result_contract,
        "validation_contract": workflow.validation_contract,
        "error_contract": workflow.error_contract,
        "constructor": workflow.constructor,
        "operation": workflow.operation,
        "consumer_contract": workflow.consumer_contract,
        "compatibility_owner": workflow.compatibility_owner,
        "cookbook_path": workflow.cookbook_path,
        "evidence_class": workflow.evidence_class,
    }


def _identity_key(value: object, fallback: str) -> str:
    owner = _canonical_owner(value, fallback)
    payload = f"{owner}|{_kind(value)}|{_signature(value)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _stub_projection_identity(
    qualified_path: str, owner: str, value: object
) -> dict[str, str]:
    """Return stable identity metadata for one compatibility-stub symbol."""

    if qualified_path in _OPTIONAL_DEPENDENCY_STUB_SYMBOLS:
        payload = f"{qualified_path}|{owner}|OPTIONAL_DEPENDENCY_PROXY"
        return {
            "kind": "optional_dependency_proxy",
            "signature": "",
            "identity_key": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            "identity_behavior": "OPTIONAL_DEPENDENCY_SAME_OBJECT",
            "runtime_availability": "OPTIONAL_EZDXF",
        }
    return {
        "kind": _kind(value),
        "signature": _signature(value),
        "identity_key": _identity_key(value, qualified_path),
        "identity_behavior": "SAME_OBJECT",
    }


def _migration_metadata(value: object, replacement: str) -> dict[str, Any]:
    deprecated = getattr(value, "__deprecated__", None)
    compatibility = getattr(value, "__compatibility__", None)
    if isinstance(deprecated, dict):
        return {
            "status": "DEPRECATED",
            "since": deprecated.get("version"),
            "removal_version": deprecated.get("remove_version"),
            "replacement": deprecated.get("alternative") or replacement,
            "reason": deprecated.get("reason"),
            "compatibility": compatibility if isinstance(compatibility, dict) else None,
        }
    return {
        "status": "NOT_DEPRECATED_NO_REMOVAL_SCHEDULE",
        "since": None,
        "removal_version": None,
        "replacement": replacement,
        "reason": None,
        "compatibility": compatibility if isinstance(compatibility, dict) else None,
    }


def _stub_warning_metadata(tree: ast.Module) -> dict[str, Any] | None:
    for node in tree.body:
        if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.Call):
            continue
        call = node.value
        if not (
            isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "warnings"
            and call.func.attr == "warn"
            and call.args
        ):
            continue
        try:
            message = ast.literal_eval(call.args[0])
        except (ValueError, TypeError):
            message = None
        category = None
        if len(call.args) > 1 and isinstance(call.args[1], ast.Name):
            category = call.args[1].id
        stacklevel = None
        for keyword in call.keywords:
            if keyword.arg == "stacklevel":
                try:
                    stacklevel = ast.literal_eval(keyword.value)
                except (ValueError, TypeError):
                    stacklevel = None
        return {
            "category": category,
            "message": message,
            "stacklevel": stacklevel,
        }
    return None


def _attribute_chain(node: ast.AST) -> tuple[str, ...]:
    values: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        values.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        values.append(current.id)
    return tuple(reversed(values))


def _is_scannable_text_path(relative: Path) -> bool:
    """Return whether one repository-relative source path belongs in the scan."""

    return (
        not relative.is_absolute()
        and ".." not in relative.parts
        and not any(part in _SKIP_PARTS for part in relative.parts)
        and relative.suffix in _TEXT_SUFFIXES
        and relative.as_posix() not in _EXCLUDED_SCAN_PATHS
    )


def _git_tracked_paths() -> list[Path] | None:
    """Return Git's maintained source allowlist, or None outside a checkout."""

    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "-z"],
            cwd=REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return sorted(
        Path(os.fsdecode(raw_path))
        for raw_path in result.stdout.split(b"\0")
        if raw_path
    )


def _iter_text_files() -> list[Path]:
    tracked_paths = _git_tracked_paths()
    if tracked_paths is not None:
        return [
            REPO_ROOT / relative
            for relative in tracked_paths
            if _is_scannable_text_path(relative) and (REPO_ROOT / relative).is_file()
        ]

    # Source archives have no Git metadata. They contain the maintained tree,
    # so retain a deterministic fallback while excluding generated outputs.
    paths: list[Path] = []
    for current, directories, filenames in os.walk(REPO_ROOT):
        directories[:] = sorted(
            directory for directory in directories if directory not in _SKIP_PARTS
        )
        current_path = Path(current)
        for filename in sorted(filenames):
            path = current_path / filename
            relative = path.relative_to(REPO_ROOT)
            if not _is_scannable_text_path(relative):
                continue
            paths.append(path)
    return sorted(paths)


def _path_scope(relative: str, *, compatibility_module: bool) -> str:
    parts = set(Path(relative).parts)
    if (
        relative.startswith(_OUT_OF_SCOPE_PREFIXES)
        or "_archive" in parts
        or parts & _OUT_OF_SCOPE_PARTS
    ):
        return "OUT_OF_SCOPE_PRESERVED"
    if (
        relative in _INTENTIONAL_COMPATIBILITY_PATHS
        or relative.startswith(_INTENTIONAL_COMPATIBILITY_PREFIXES)
        or relative.startswith("tests/")
    ):
        return (
            "DELEGATING_COMPATIBILITY_SHIM"
            if compatibility_module
            else "INTENTIONAL_PUBLIC_FACADE"
        )
    if relative.startswith("Python/structural_lib/") and Path(relative).parent == Path(
        "Python/structural_lib"
    ):
        return (
            "DELEGATING_COMPATIBILITY_SHIM"
            if compatibility_module
            else "MAINTAINED_CALLER_MIGRATED"
        )
    return (
        "BLOCKED_AMBIGUOUS_OWNER"
        if compatibility_module
        else "MAINTAINED_CALLER_MIGRATED"
    )


def _discover_root_stubs() -> dict[str, dict[str, Any]]:
    stubs: dict[str, dict[str, Any]] = {}
    package_root = REPO_ROOT / "Python/structural_lib"
    for path in sorted(package_root.glob("*.py")):
        if path.name in {"__init__.py", "api.py"}:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docstring = ast.get_docstring(tree) or ""
        match = re.search(r"migrated to:\s*([^\s]+)", docstring)
        if not match:
            continue
        module_name = f"structural_lib.{path.stem}"
        imported: list[tuple[str, str, str]] = []
        for node in tree.body:
            if not isinstance(node, ast.ImportFrom) or not node.module:
                continue
            if not node.module.startswith("structural_lib"):
                continue
            for alias in node.names:
                if alias.name == "__all__":
                    continue
                imported.append((node.module, alias.name, alias.asname or alias.name))
        stubs[module_name] = {
            "path": path.relative_to(REPO_ROOT).as_posix(),
            "documented_replacement": match.group(1).rstrip("."),
            "imports": imported,
            "warning": _stub_warning_metadata(tree),
        }
    return stubs


def _known_symbols(
    registry: dict[str, Any], stubs: dict[str, dict[str, Any]]
) -> dict[str, set[str]]:
    known = {
        surface["module"]: {record["name"] for record in surface["symbols"]}
        for surface in registry["surfaces"]
    }
    for module_name, stub in stubs.items():
        names: set[str] = set()
        for owner_module, owner_name, exposed_name in stub["imports"]:
            if owner_name == "*":
                owner = importlib.import_module(owner_module)
                names.update(getattr(owner, "__all__", ()))
            else:
                names.add(exposed_name)
        known[module_name] = names
    api_hub = importlib.import_module("structural_lib.services.api_hub")
    known[api_hub.__name__] = set(getattr(api_hub, "__all__", ()))
    return known


def _stub_symbol_owner(stub: dict[str, Any], name: str) -> str:
    for owner_module, owner_name, exposed_name in stub["imports"]:
        if owner_name == "*":
            owner = importlib.import_module(owner_module)
            if name in getattr(owner, "__all__", ()):
                return f"{owner_module}.{name}"
        elif exposed_name == name:
            return f"{owner_module}.{owner_name}"
    raise KeyError(f"No imported owner found for {name}")


def _import_compatibility_module(module_name: str) -> ModuleType:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return importlib.import_module(module_name)


def _scan_callers(
    known: dict[str, set[str]], compatibility_modules: set[str]
) -> tuple[dict[tuple[str, str], set[str]], dict[str, set[str]], list[dict[str, Any]]]:
    symbol_paths: dict[tuple[str, str], set[str]] = {
        (module, name): set() for module, names in known.items() for name in names
    }
    module_paths: dict[str, set[str]] = {module: set() for module in known}
    caller_records: set[tuple[str, str, str, str]] = set()
    unknown_compatibility_callers: set[tuple[str, str, str]] = set()

    def record(
        relative: str, module: str, name: str, *, unknown_is_error: bool = False
    ) -> None:
        if module not in known:
            return
        if name not in known[module]:
            if unknown_is_error and module in compatibility_modules:
                unknown_compatibility_callers.add((relative, module, name))
            return
        symbol_paths[(module, name)].add(relative)
        module_paths[module].add(relative)
        disposition = _path_scope(
            relative, compatibility_module=module in compatibility_modules
        )
        caller_records.add((relative, module, name, disposition))

    def record_module(relative: str, module: str) -> None:
        if module not in known:
            return
        module_paths[module].add(relative)

    for path in _iter_text_files():
        relative = path.relative_to(REPO_ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.suffix == ".py":
            try:
                tree = ast.parse(text)
            except SyntaxError:
                tree = None
            if tree is not None:
                aliases: dict[str, str] = {}
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in known:
                                local = alias.asname or alias.name.split(".")[0]
                                aliases[local] = alias.name
                                record_module(relative, alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        if node.module in known:
                            record_module(relative, node.module)
                            for alias in node.names:
                                if alias.name == "*":
                                    for name in known[node.module]:
                                        record(relative, node.module, name)
                                else:
                                    record(
                                        relative,
                                        node.module,
                                        alias.name,
                                        unknown_is_error=True,
                                    )
                        for alias in node.names:
                            candidate = f"{node.module}.{alias.name}"
                            if candidate in known:
                                local = alias.asname or alias.name
                                aliases[local] = candidate
                                record_module(relative, candidate)
                    elif isinstance(node, ast.Attribute):
                        chain = _attribute_chain(node)
                        if len(chain) < 2:
                            continue
                        module = aliases.get(chain[0])
                        if module and len(chain) == 2:
                            record(
                                relative,
                                module,
                                chain[1],
                                unknown_is_error=True,
                            )
                        else:
                            for split in range(1, len(chain)):
                                candidate = ".".join(chain[:split])
                                if candidate in known and split < len(chain):
                                    record(relative, candidate, chain[split])
                continue

        text_aliases: dict[str, str] = {}
        for match in re.finditer(
            r"\bimport\s+(structural_lib(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
            r"(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?",
            text,
        ):
            module = match.group(1)
            if module in known:
                text_aliases[match.group(2) or module.split(".")[0]] = module
                record_module(relative, module)
        for match in re.finditer(
            r"\bfrom\s+(structural_lib(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
            r"\s+import\s+(\([^)]*\)|[^\n#]+)",
            text,
            re.DOTALL,
        ):
            module = match.group(1)
            clause = match.group(2)
            imported_names = re.findall(
                r"\b([A-Za-z_][A-Za-z0-9_]*)\b(?:\s+as\s+([A-Za-z_][A-Za-z0-9_]*))?",
                clause,
            )
            if module in known:
                record_module(relative, module)
                for name, _alias in imported_names:
                    record(relative, module, name, unknown_is_error=True)
            for name, local_alias in imported_names:
                candidate = f"{module}.{name}"
                if candidate in known:
                    text_aliases[local_alias or name] = candidate
                    record_module(relative, candidate)
        for match in re.finditer(
            r"\bstructural_lib(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b", text
        ):
            text_chain = match.group(0).split(".")
            for split in range(len(text_chain) - 1, 0, -1):
                module = ".".join(text_chain[:split])
                if module in known:
                    record(relative, module, text_chain[split])
                    break
        for local_name, module in text_aliases.items():
            for match in re.finditer(
                rf"\b{re.escape(local_name)}\.([A-Za-z_][A-Za-z0-9_]*)\b", text
            ):
                record(
                    relative,
                    module,
                    match.group(1),
                    unknown_is_error=True,
                )

    records = [
        {
            "path": path,
            "target": f"{module}.{name}",
            "module": module,
            "public_name": name,
            "disposition": disposition,
        }
        for path, module, name, disposition in sorted(caller_records)
    ]
    records.extend(
        {
            "path": path,
            "target": f"{module}.{name}",
            "module": module,
            "public_name": name,
            "disposition": _path_scope(path, compatibility_module=True),
            "reason": "Compatibility caller references a symbol not exported by the live module.",
        }
        for path, module, name in sorted(unknown_compatibility_callers)
    )
    records.sort(key=lambda item: (item["path"], item["module"], item["public_name"]))
    return symbol_paths, module_paths, records


def _claim_disposition(
    *,
    module_name: str,
    name: str,
    defined_in: str,
    declared_export: bool,
    canonical_task_exports: set[str],
    capability_bound_exports: set[str],
) -> str:
    if not declared_export:
        return "internal"
    if module_name in _CANONICAL_FACADE_MODULES:
        return "canonical"
    if module_name == "structural_lib.api":
        return "compatibility"
    if name in canonical_task_exports:
        return "compatibility"
    if name in _CANONICAL_SUPPORT_EXPORTS:
        return "canonical"
    if defined_in.startswith(_HOLD_MODULE_PREFIXES):
        return "hold"
    if defined_in.startswith(_ADVANCED_MODULE_PREFIXES):
        return "advanced"
    if name in capability_bound_exports:
        return "advanced"
    return "compatibility"


def _build_surface(
    module_name: str,
    export_class: str,
    canonical_task_exports: set[str],
    capability_bound_exports: set[str],
) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    declared = tuple(getattr(module, "__all__", ()))
    declared_set = set(declared)
    records: list[dict[str, Any]] = []

    missing = sorted(name for name in declared_set if not hasattr(module, name))
    if missing:
        raise RuntimeError(f"{module_name} declares missing exports: {missing}")

    for name in sorted(declared_set):
        value = getattr(module, name)
        defined_in = getattr(value, "__module__", module_name)
        kind = _kind(value)
        qualified_name = f"{module_name}.{name}"
        claim_disposition = _claim_disposition(
            module_name=module_name,
            name=name,
            defined_in=defined_in,
            declared_export=True,
            canonical_task_exports=canonical_task_exports,
            capability_bound_exports=capability_bound_exports,
        )
        records.append(
            {
                "name": name,
                "qualified_name": qualified_name,
                "kind": kind,
                "classification": export_class,
                "declared_export": True,
                "defined_in": defined_in,
                "claim_disposition": claim_disposition,
                "documentation": _documentation_record(
                    value=value,
                    qualified_name=qualified_name,
                    kind=kind,
                    declared_export=True,
                    claim_disposition=claim_disposition,
                ),
            }
        )

    for name, value in sorted(vars(module).items()):
        if name.startswith("_") or name in declared_set:
            continue
        if not (
            inspect.isclass(value)
            or inspect.isfunction(value)
            or inspect.isbuiltin(value)
        ):
            continue
        defined_in = getattr(value, "__module__", module_name)
        kind = _kind(value)
        qualified_name = f"{module_name}.{name}"
        records.append(
            {
                "name": name,
                "qualified_name": qualified_name,
                "kind": kind,
                "classification": "internal",
                "declared_export": False,
                "defined_in": defined_in,
                "claim_disposition": "internal",
                "documentation": _documentation_record(
                    value=value,
                    qualified_name=qualified_name,
                    kind=kind,
                    declared_export=False,
                    claim_disposition="internal",
                ),
            }
        )

    return {
        "module": module_name,
        "export_classification": export_class,
        "declared_export_count": len(declared_set),
        "classified_symbol_count": len(records),
        "symbols": sorted(records, key=lambda item: item["name"]),
    }


def _release_channel(version: str) -> str:
    """Return the repository's supported public distribution channel."""
    if re.fullmatch(r"\d+\.\d+\.\d+", version):
        return "normal"
    if re.fullmatch(r"\d+\.\d+\.\d+a\d+", version):
        return "alpha"
    raise RuntimeError(f"Unsupported package version for API registry: {version}")


def _documentation_contract(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the debt-frozen documentation contract from classified surfaces."""

    canonical_debt = [
        {
            "qualified_name": record["qualified_name"],
            "missing_docstring_sections": record["documentation"][
                "missing_docstring_sections"
            ],
        }
        for surface in surfaces
        for record in surface["symbols"]
        if record["documentation"]["role"] == "CANONICAL_WORKFLOW_OPERATION"
        and record["documentation"]["missing_docstring_sections"]
    ]
    current_names = {item["qualified_name"] for item in canonical_debt}
    return {
        "schema_version": "api-documentation-contract/v1",
        "required_canonical_docstring_sections": list(_CANONICAL_DOCSTRING_SECTIONS),
        "temporary_debt_baseline": sorted(_TEMPORARY_DOCUMENTATION_DEBT_BASELINE),
        "current_debt": canonical_debt,
        "unbaselined_debt": sorted(
            current_names - _TEMPORARY_DOCUMENTATION_DEBT_BASELINE
        ),
        "resolved_baseline_symbols": sorted(
            _TEMPORARY_DOCUMENTATION_DEBT_BASELINE - current_names
        ),
        "exact_wheel_beam_operations": sorted(_DOCUMENTED_BEAM_OPERATIONS),
        "example_inventory": list(_BEAM_EXAMPLE_INVENTORY),
    }


def build_registry() -> dict[str, Any]:
    sys.path.insert(0, str(REPO_ROOT / "Python"))
    from structural_lib import __version__
    from structural_lib.services.capabilities import get_supported_is456_capabilities
    from structural_lib.services.family_facade_registry import FAMILY_FACADE_WORKFLOWS

    capability_bound_exports = {
        workflow
        for capability in get_supported_is456_capabilities()
        for workflow in capability.public_workflows
    }
    canonical_task_exports = set(_CANONICAL_TASK_EXPORTS)
    missing_authority = canonical_task_exports - capability_bound_exports
    if missing_authority:
        raise RuntimeError(
            "Canonical task exports are absent from capability authority: "
            + ", ".join(sorted(missing_authority))
        )

    surfaces = [
        _build_surface(
            module_name,
            export_class,
            canonical_task_exports,
            capability_bound_exports,
        )
        for module_name, export_class in SURFACE_POLICY
    ]
    documentation_contract = _documentation_contract(surfaces)
    return {
        "schema_version": "2.0",
        "claim_surface_matrix_schema_version": "claim-surface-matrix/v1",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "package_version": __version__,
        "release_channel": _release_channel(__version__),
        "classifications": {
            "stable": "Reserved for a separately approved stable compatibility promise.",
            "preview": "Declared pre-1.0 export; callable but subject to documented change.",
            "compatibility": "Retained delegating facade; use the recommended root or service facade.",
            "internal": "Not declared in __all__; no public compatibility promise.",
        },
        "claim_dispositions": {
            "canonical": "Bounded task workflow listed by the capability authority.",
            "advanced": "Maintained specialist tool outside the small task API.",
            "compatibility": "Retained public surface without a canonical task claim.",
            "hold": "Callable preview surface that cannot support its broader advertised use until its named gate passes.",
            "internal": "Undeclared implementation detail.",
        },
        "canonical_task_exports": sorted(canonical_task_exports),
        "canonical_journey_ids": [
            workflow.journey_id for workflow in FAMILY_FACADE_WORKFLOWS
        ],
        "family_facade_workflows": [
            _family_workflow_record(workflow) for workflow in FAMILY_FACADE_WORKFLOWS
        ],
        "canonical_support_exports": sorted(_CANONICAL_SUPPORT_EXPORTS),
        "advanced_capability_exports": sorted(
            capability_bound_exports - canonical_task_exports
        ),
        "artifact_boundaries": {
            "wheel": ["structural_lib Python API", "structural_lib CLI"],
            "exact_head_application": ["FastAPI", "React"],
            "repository_clients": ["clients/python", "clients/typescript"],
            "not_in_wheel": ["fastapi_app", "react_app", "clients"],
        },
        "canonical_reference_journey": {
            "task_id": "is456.beam.design/v1",
            "input_contract": "beam-design-input/v1",
            "effective_depth_contract": "effective-depth-basis/v1",
            "result_contract": "beam-design-result/v1 + structural-result-envelope/v2",
            "problem_contract": "structural-problem/v1",
            "field_contract_dimensions": [
                "TYPE_AND_FINITE_VALUE",
                "RANGE_AND_ZERO_POLICY",
                "UNIT_AND_QUANTITY",
                "CODE_AND_MATERIAL_DOMAIN",
                "CROSS_FIELD_RELATION",
                "IDENTITY_AND_PROVENANCE",
                "ENUM_AND_TOPOLOGY",
                "COLLECTION_CARDINALITY_AND_UNIQUENESS",
                "DOWNSTREAM_CONSUMABILITY",
                "COMPATIBILITY_ALIAS_AND_MIGRATION_TARGET",
            ],
            "surfaces": [
                {
                    "surface": "python_facade",
                    "locator": "structural_lib.design.is456.beam",
                    "artifact": "wheel",
                    "disposition": "canonical",
                },
                {
                    "surface": "python_root_compatibility",
                    "locator": "structural_lib.design_beam_is456",
                    "artifact": "wheel",
                    "disposition": "compatibility",
                    "canonical_target": "structural_lib.design.is456.beam.design",
                },
                {
                    "surface": "python_service_compatibility",
                    "locator": "structural_lib.services.api.design_beam_is456",
                    "artifact": "wheel",
                    "disposition": "compatibility",
                    "canonical_target": "structural_lib.design.is456.beam.design",
                },
                {
                    "surface": "python_compatibility",
                    "locator": "structural_lib.api.design_beam_is456",
                    "artifact": "wheel",
                    "disposition": "compatibility",
                    "canonical_target": "structural_lib.design.is456.beam.design",
                },
                {
                    "surface": "cli",
                    "locator": "python -m structural_lib beam-v1",
                    "artifact": "wheel",
                    "disposition": "canonical",
                },
                {
                    "surface": "rest_v2",
                    "locator": "POST /api/v2/design/beam",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                },
                {
                    "surface": "rest_v1_compatibility",
                    "locator": "POST /api/v1/design/beam",
                    "artifact": "exact_head_application",
                    "disposition": "compatibility",
                    "canonical_target": "POST /api/v2/design/beam",
                },
                {
                    "surface": "generated_python_client",
                    "locator": "StructuralDesignClient.design_beam_v2",
                    "artifact": "repository_clients",
                    "disposition": "canonical",
                },
                {
                    "surface": "generated_typescript_client",
                    "locator": "StructuralDesignClient.designBeamV2",
                    "artifact": "repository_clients",
                    "disposition": "canonical",
                },
                {
                    "surface": "workflow",
                    "locator": "is456.beam.review@1.1.0",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                    "activation": "feature_gated",
                },
                {
                    "surface": "react_manual",
                    "locator": "/workbench/quick/manual",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                },
                {
                    "surface": "react_catalog",
                    "locator": "/workbench/quick",
                    "artifact": "exact_head_application",
                    "disposition": "canonical",
                    "activation": "feature_gated",
                },
            ],
            "compatibility_holds": [
                {
                    "surface": "websocket_design",
                    "locator": "/ws/design/{session_id}",
                    "condition": "missing structural-result-envelope/v2",
                    "outcome": "HOLD",
                }
            ],
        },
        "stable_exports": [],
        "internal_policy": "Every public-looking callable outside __all__ is tracked as internal.",
        "compatibility_ledger": {
            "schema_version": "api-compatibility-ledger/v1",
            "path": "docs/reference/api-compatibility-ledger.json",
            "taxonomy": list(_COMPATIBILITY_TAXONOMY),
            "projection_reconciliation": "Every classified facade symbol has exactly one projection record.",
        },
        "documentation_contract": documentation_contract,
        "surfaces": surfaces,
    }


def _replacement_for_projection(
    module_name: str, name: str, value: object, claim_disposition: str
) -> str:
    compatibility = getattr(value, "__compatibility__", None)
    if isinstance(compatibility, dict) and compatibility.get("canonical_target"):
        return str(compatibility["canonical_target"])
    if name in _P5_HELD_COMPATIBILITY:
        return "structural_lib.imports.build_etabs_canonical_snapshot_v1"
    if module_name == "structural_lib.api":
        return f"structural_lib.{name}"
    if module_name == "structural_lib.services.api":
        return _canonical_owner(value, f"{module_name}.{name}")
    if module_name == "structural_lib":
        return f"structural_lib.{name}"
    if claim_disposition == "hold":
        return _canonical_owner(value, f"{module_name}.{name}")
    return _canonical_owner(value, f"{module_name}.{name}")


def _projection_disposition(module_name: str, claim_disposition: str) -> str:
    if claim_disposition == "hold":
        return "HELD_COMPATIBILITY"
    if module_name == "structural_lib.api":
        return "DELEGATING_COMPATIBILITY_SHIM"
    return "INTENTIONAL_PUBLIC_FACADE"


def _projection_reason(module_name: str, name: str, claim_disposition: str) -> str:
    if module_name in _CANONICAL_FACADE_MODULES:
        return (
            "The family facade owns the strict request, typed result, and named "
            "composition journey while delegating calculations to maintained owners."
        )
    if name in _P5_HELD_COMPATIBILITY:
        return (
            "Historical ETABS return shape lacks complete project/export identity, "
            "row dispositions, ambiguities, and the canonical snapshot hash; it is "
            "not an accepted P5 snapshot path."
        )
    if claim_disposition == "hold":
        return (
            "The callable remains available inside its documented pre-1.0 boundary, "
            "but its broader claim is held and must not be promoted."
        )
    if module_name == "structural_lib.api":
        return (
            "The legacy facade imports the exact service object and therefore adds "
            "no wrapper, default, or second calculation path."
        )
    return (
        "The supported facade exposes the exact canonical object; object and "
        "signature identity prevent a second calculation path."
    )


def _active_and_preserved_callers(
    paths: set[str], *, compatibility_module: bool
) -> tuple[list[str], list[str]]:
    active: list[str] = []
    preserved: list[str] = []
    for path in sorted(paths):
        disposition = _path_scope(path, compatibility_module=compatibility_module)
        if disposition == "OUT_OF_SCOPE_PRESERVED":
            preserved.append(path)
        else:
            active.append(path)
    return active, preserved


def build_compatibility_ledger(
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the deterministic P7 compatibility and caller ledger."""

    registry = registry or build_registry()
    stubs = _discover_root_stubs()
    known = _known_symbols(registry, stubs)
    compatibility_modules = {
        "structural_lib.api",
        "structural_lib.services.api_hub",
        *stubs.keys(),
    }
    symbol_paths, module_paths, callers = _scan_callers(known, compatibility_modules)

    projections: list[dict[str, Any]] = []
    owner_groups: dict[str, dict[str, Any]] = {}
    surface_modules = {
        surface["module"]: importlib.import_module(surface["module"])
        for surface in registry["surfaces"]
    }
    for surface in registry["surfaces"]:
        module_name = surface["module"]
        module = surface_modules[module_name]
        for record in surface["symbols"]:
            name = record["name"]
            value = getattr(module, name)
            qualified_path = f"{module_name}.{name}"
            owner = _canonical_owner(value, qualified_path)
            identity_behavior = "SAME_OBJECT"
            if inspect.ismodule(value) and module_name == "structural_lib":
                if name == "api":
                    owner = "structural_lib.services.api"
                    identity_behavior = "MODULE_NAMESPACE_DELEGATE"
                elif qualified_path in stubs:
                    owner = stubs[qualified_path]["documented_replacement"]
                    identity_behavior = "MODULE_NAMESPACE_DELEGATE"
            replacement = _replacement_for_projection(
                module_name, name, value, record["claim_disposition"]
            )
            if inspect.ismodule(value):
                replacement = owner
            namespace_symbol_owners: dict[str, str] | None = None
            if identity_behavior == "MODULE_NAMESPACE_DELEGATE":
                if qualified_path == "structural_lib.api":
                    namespace_symbol_owners = {
                        public_name: f"structural_lib.services.api.{public_name}"
                        for public_name in sorted(known[qualified_path])
                    }
                else:
                    namespace_symbol_owners = {
                        public_name: _stub_symbol_owner(
                            stubs[qualified_path], public_name
                        )
                        for public_name in sorted(known[qualified_path])
                    }
            active, preserved = _active_and_preserved_callers(
                symbol_paths[(module_name, name)],
                compatibility_module=module_name in compatibility_modules,
            )
            same_object_facades = sorted(
                candidate_module
                for candidate_module, candidate in surface_modules.items()
                if hasattr(candidate, name) and getattr(candidate, name) is value
            )
            projection = {
                "public_name": name,
                "qualified_path": qualified_path,
                "facades_exposing_same_object": same_object_facades,
                "canonical_owner": owner,
                "replacement_path": replacement,
                "kind": record["kind"],
                "signature": _signature(value),
                "identity_key": _identity_key(value, qualified_path),
                "identity_behavior": identity_behavior,
                "namespace_symbol_owners": namespace_symbol_owners,
                "active_caller_count": len(active),
                "active_maintained_caller_paths": active,
                "out_of_scope_reference_paths": preserved,
                "migration_metadata": _migration_metadata(value, replacement),
                "safety_behavior_reason": (
                    "The compatibility module is a formula-free namespace adapter; "
                    "its exported symbols resolve to canonical owner objects."
                    if identity_behavior == "MODULE_NAMESPACE_DELEGATE"
                    else _projection_reason(
                        module_name, name, record["claim_disposition"]
                    )
                ),
                "proposed_disposition": _projection_disposition(
                    module_name, record["claim_disposition"]
                ),
                "classification": record["classification"],
                "claim_disposition": record["claim_disposition"],
                "tests": [
                    "Python/tests/test_compatibility_convergence.py::test_facade_projection_ledger_reconciles_live_classification",
                    "Python/tests/test_compatibility_convergence.py::test_all_facade_projections_preserve_object_and_signature_identity",
                ],
                "deletion_authorized": False,
            }
            projections.append(projection)
            group = owner_groups.setdefault(
                owner,
                {
                    "public_name": name,
                    "qualified_path": owner,
                    "facades_exposing_same_object": set(),
                    "canonical_owner": owner,
                    "replacement_path": replacement,
                    "kind": record["kind"],
                    "signature": _signature(value),
                    "identity_key": _identity_key(value, qualified_path),
                    "identity_behavior": (
                        "CANONICAL_MODULE_NAMESPACE"
                        if inspect.ismodule(value)
                        else "CANONICAL_OBJECT"
                    ),
                    "active_maintained_caller_paths": set(),
                    "out_of_scope_reference_paths": set(),
                    "migration_metadata": _migration_metadata(value, replacement),
                    "safety_behavior_reason": (
                        "This exact module/function/type owns the retained behavior; "
                        "facades contain no independent implementation."
                    ),
                    "proposed_disposition": "CANONICAL_OWNER",
                    "tests": [
                        "Python/tests/test_compatibility_convergence.py::test_all_facade_projections_preserve_object_and_signature_identity"
                    ],
                    "deletion_authorized": False,
                },
            )
            group["facades_exposing_same_object"].update(same_object_facades)
            group["active_maintained_caller_paths"].update(active)
            group["out_of_scope_reference_paths"].update(preserved)

    owners: list[dict[str, Any]] = []
    for owner in sorted(owner_groups):
        group = owner_groups[owner]
        group["facades_exposing_same_object"] = sorted(
            group["facades_exposing_same_object"]
        )
        group["active_maintained_caller_paths"] = sorted(
            group["active_maintained_caller_paths"]
        )
        group["out_of_scope_reference_paths"] = sorted(
            group["out_of_scope_reference_paths"]
        )
        group["active_caller_count"] = len(group["active_maintained_caller_paths"])
        owners.append(group)

    stub_modules: list[dict[str, Any]] = []
    stub_projections: list[dict[str, Any]] = []
    for module_name in sorted(stubs):
        stub = stubs[module_name]
        module = _import_compatibility_module(module_name)
        canonical_modules = sorted(
            {owner_module for owner_module, _, _ in stub["imports"]}
        )
        module_active, module_preserved = _active_and_preserved_callers(
            module_paths[module_name], compatibility_module=True
        )
        documented_matches_runtime = stub["documented_replacement"] in canonical_modules
        module_disposition = (
            "DELEGATING_COMPATIBILITY_SHIM"
            if documented_matches_runtime
            else "BLOCKED_AMBIGUOUS_OWNER"
        )
        warning_metadata = stub["warning"]
        migration_metadata = {
            "status": (
                "DEPRECATED_IMPORT_PATH"
                if warning_metadata is not None
                else "NOT_DEPRECATED_NO_REMOVAL_SCHEDULE"
            ),
            "since": None,
            "removal_version": None,
            "replacement": stub["documented_replacement"],
            "source": "module_docstring_and_runtime_warning",
        }
        if warning_metadata is not None:
            migration_metadata["warning"] = warning_metadata
        module_record = {
            "public_name": module_name.rsplit(".", 1)[-1],
            "qualified_path": module_name,
            "source_path": stub["path"],
            "facades_exposing_same_object": [module_name],
            "canonical_owner": canonical_modules,
            "replacement_path": stub["documented_replacement"],
            "object_signature_or_adapter_behavior": "PURE_IMPORT_REEXPORT_NO_LOCAL_FUNCTION_OR_CLASS",
            "active_caller_count": len(module_active),
            "active_maintained_caller_paths": module_active,
            "out_of_scope_reference_paths": module_preserved,
            "migration_metadata": migration_metadata,
            "safety_behavior_reason": (
                "The module defines no function or class and re-exports owner objects."
            ),
            "proposed_disposition": module_disposition,
            "tests": [
                "Python/tests/test_compatibility_convergence.py::test_root_stub_modules_are_pure_identity_delegates"
            ],
            "deletion_authorized": False,
        }
        stub_modules.append(module_record)

        for name in sorted(known[module_name]):
            if not hasattr(module, name):
                continue
            value = getattr(module, name)
            owner = _stub_symbol_owner(stub, name)
            qualified_path = f"{module_name}.{name}"
            identity = _stub_projection_identity(qualified_path, owner, value)
            active, preserved = _active_and_preserved_callers(
                symbol_paths[(module_name, name)], compatibility_module=True
            )
            disposition = (
                "HELD_COMPATIBILITY"
                if name in _P5_HELD_COMPATIBILITY
                else module_disposition
            )
            stub_projections.append(
                {
                    "public_name": name,
                    "qualified_path": qualified_path,
                    "facades_exposing_same_object": [module_name],
                    "canonical_owner": owner,
                    "replacement_path": (
                        "structural_lib.imports.build_etabs_canonical_snapshot_v1"
                        if name in _P5_HELD_COMPATIBILITY
                        else owner
                    ),
                    **identity,
                    "active_caller_count": len(active),
                    "active_maintained_caller_paths": active,
                    "out_of_scope_reference_paths": preserved,
                    "migration_metadata": _migration_metadata(value, owner),
                    "safety_behavior_reason": _projection_reason(
                        module_name,
                        name,
                        "hold" if name in _P5_HELD_COMPATIBILITY else "compatibility",
                    ),
                    "proposed_disposition": disposition,
                    "tests": [
                        "Python/tests/test_compatibility_convergence.py::test_root_stub_modules_are_pure_identity_delegates"
                    ],
                    "deletion_authorized": False,
                }
            )

    api_hub = importlib.import_module("structural_lib.services.api_hub")
    service_api = importlib.import_module("structural_lib.services.api")
    hub_active, hub_preserved = _active_and_preserved_callers(
        module_paths[api_hub.__name__], compatibility_module=True
    )
    hub_mismatches = sorted(
        name
        for name in api_hub.__all__
        if not hasattr(service_api, name)
        or getattr(api_hub, name) is not getattr(service_api, name)
    )
    api_hub_record = {
        "public_name": "api_hub",
        "qualified_path": api_hub.__name__,
        "source_path": "Python/structural_lib/services/api_hub.py",
        "facades_exposing_same_object": [api_hub.__name__],
        "canonical_owner": "structural_lib.services.api",
        "replacement_path": "structural_lib.services.api",
        "object_signature_or_adapter_behavior": "PURE_SUBSET_REEXPORT_NO_LOCAL_CALCULATION",
        "export_count": len(api_hub.__all__),
        "identity_mismatches": hub_mismatches,
        "active_caller_count": len(hub_active),
        "active_maintained_caller_paths": hub_active,
        "out_of_scope_reference_paths": hub_preserved,
        "migration_metadata": {
            "status": "NOT_DEPRECATED_NO_REMOVAL_SCHEDULE",
            "since": None,
            "removal_version": None,
            "replacement": "structural_lib.services.api",
        },
        "safety_behavior_reason": (
            "All retained names resolve to the exact service objects; the module "
            "does not own a calculation path."
        ),
        "proposed_disposition": (
            "DELEGATING_COMPATIBILITY_SHIM"
            if not hub_mismatches
            else "BLOCKED_AMBIGUOUS_OWNER"
        ),
        "tests": [
            "Python/tests/test_compatibility_convergence.py::test_api_hub_is_an_identity_only_subset"
        ],
        "deletion_authorized": False,
    }

    disposition_counts: dict[str, int] = {}
    for item in [
        *owners,
        *projections,
        *stub_modules,
        *stub_projections,
        api_hub_record,
        *callers,
    ]:
        disposition = str(item.get("proposed_disposition") or item.get("disposition"))
        disposition_counts[disposition] = disposition_counts.get(disposition, 0) + 1
    classification_projection_count = sum(
        surface["classified_symbol_count"] for surface in registry["surfaces"]
    )
    compatibility_claim_entries = sum(
        1
        for surface in registry["surfaces"]
        for record in surface["symbols"]
        if record["claim_disposition"] == "compatibility"
    )
    blocked_callers = [
        caller
        for caller in callers
        if caller["disposition"] == "BLOCKED_AMBIGUOUS_OWNER"
    ]
    return {
        "schema_version": "api-compatibility-ledger/v1",
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "package_version": registry["package_version"],
        "release_channel": registry["release_channel"],
        "taxonomy": list(_COMPATIBILITY_TAXONOMY),
        "scope": {
            "in_scope_facades": [surface["module"] for surface in registry["surfaces"]],
            "root_stub_modules": sorted(stubs),
            "additional_delegating_module": "structural_lib.services.api_hub",
            "out_of_scope_preserved": [
                "archives",
                "historical migration material",
                "vendor sources",
                "Streamlit reference material",
                "fixtures and golden evidence",
                "branches and worktrees",
            ],
        },
        "classification_reconciliation": {
            "surface_counts": [
                {
                    "module": surface["module"],
                    "declared_export_count": surface["declared_export_count"],
                    "classified_symbol_count": surface["classified_symbol_count"],
                }
                for surface in registry["surfaces"]
            ],
            "classification_projection_count": classification_projection_count,
            "ledger_projection_count": len(projections),
            "compatibility_claim_entries": compatibility_claim_entries,
            "exactly_reconciled": classification_projection_count == len(projections),
        },
        "summary": {
            "canonical_owner_count": len(owners),
            "facade_projection_count": len(projections),
            "root_stub_module_count": len(stub_modules),
            "root_stub_projection_count": len(stub_projections),
            "api_hub_export_count": len(api_hub.__all__),
            "caller_record_count": len(callers),
            "blocked_ambiguous_caller_count": len(blocked_callers),
            "disposition_counts": dict(sorted(disposition_counts.items())),
        },
        "canonical_owners": owners,
        "facade_projections": projections,
        "root_stub_modules": stub_modules,
        "root_stub_projections": stub_projections,
        "additional_module_records": [api_hub_record],
        "caller_records": callers,
        "blocked_ambiguous_callers": blocked_callers,
        "retirement_candidates": [],
        "authorization": {
            "deletion_authorized": False,
            "public_contract_break_authorized": False,
            "release_authorized": False,
            "professional_approval": False,
            "engineering_use_approval": False,
        },
    }


def _normalized(registry: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in registry.items() if key != "generated"}


def _intern_ledger_value(
    value: Any, value_indexes: dict[str, int], values: list[Any]
) -> int:
    value_key = json.dumps(value, sort_keys=True, separators=(",", ":"))
    if value_key not in value_indexes:
        value_indexes[value_key] = len(values)
        values.append(value)
    return value_indexes[value_key]


def _pack_record_table(
    records: list[dict[str, Any]],
    value_indexes: dict[str, int],
    values: list[Any],
) -> dict[str, Any]:
    """Factor record fields through a ledger-wide value dictionary."""

    fields = sorted({field for record in records for field in record})
    rows = [
        [
            _intern_ledger_value(
                record.get(field, _LEDGER_MISSING_VALUE), value_indexes, values
            )
            for field in fields
        ]
        for record in records
    ]
    return {"fields": fields, "rows": rows}


def _encode_ledger_value(
    value: Any, string_indexes: dict[str, int], strings: list[str]
) -> Any:
    """Replace every string, including mapping keys, with one table reference."""

    if isinstance(value, str):
        if value not in string_indexes:
            string_indexes[value] = len(strings)
            strings.append(value)
        return str(string_indexes[value])
    if isinstance(value, list):
        return [_encode_ledger_value(item, string_indexes, strings) for item in value]
    if isinstance(value, dict):
        return {
            _encode_ledger_value(key, string_indexes, strings): _encode_ledger_value(
                value[key], string_indexes, strings
            )
            for key in sorted(value)
        }
    return value


def _decode_ledger_value(value: Any, strings: list[str]) -> Any:
    if isinstance(value, str):
        return strings[int(value)]
    if isinstance(value, list):
        return [_decode_ledger_value(item, strings) for item in value]
    if isinstance(value, dict):
        return {
            strings[int(key)]: _decode_ledger_value(item, strings)
            for key, item in value.items()
        }
    return value


def _remap_ledger_string_references(value: Any, old_to_new: dict[int, int]) -> Any:
    if isinstance(value, str):
        return str(old_to_new[int(value)])
    if isinstance(value, list):
        return [_remap_ledger_string_references(item, old_to_new) for item in value]
    if isinstance(value, dict):
        return {
            str(old_to_new[int(key)]): _remap_ledger_string_references(item, old_to_new)
            for key, item in value.items()
        }
    return value


def _front_code_strings(strings: list[str]) -> list[Any]:
    encoded: list[Any] = []
    previous = ""
    for value in strings:
        common = 0
        while (
            common < len(previous)
            and common < len(value)
            and previous[common] == value[common]
        ):
            common += 1
        encoded.append([common, value[common:]] if common >= 4 else value)
        previous = value
    return encoded


def _expand_front_coded_strings(encoded: list[Any]) -> list[str]:
    strings: list[str] = []
    previous = ""
    for item in encoded:
        value = previous[: item[0]] + item[1] if isinstance(item, list) else item
        strings.append(value)
        previous = value
    return strings


def _pack_compatibility_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    """Return the lossless small-file representation used in Git."""

    raw_values: list[Any] = []
    value_indexes: dict[str, int] = {}
    record_tables = {
        section: _pack_record_table(ledger[section], value_indexes, raw_values)
        for section in _LEDGER_RECORD_SECTIONS
    }
    strings: list[str] = []
    string_indexes: dict[str, int] = {}
    encoded_values = [
        _encode_ledger_value(value, string_indexes, strings) for value in raw_values
    ]
    sorted_old_indexes = sorted(range(len(strings)), key=strings.__getitem__)
    old_to_new = {
        old_index: new_index for new_index, old_index in enumerate(sorted_old_indexes)
    }
    sorted_strings = [strings[old_index] for old_index in sorted_old_indexes]
    packed = {
        key: value
        for key, value in ledger.items()
        if key not in _LEDGER_RECORD_SECTIONS
    }
    packed["encoding"] = "column-dictionary-v1"
    packed["strings"] = _front_code_strings(sorted_strings)
    packed["values"] = [
        _remap_ledger_string_references(value, old_to_new) for value in encoded_values
    ]
    packed["record_tables"] = record_tables
    return packed


def _unpack_compatibility_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    """Expand the checked-in compact ledger to its complete record contract."""

    if ledger.get("encoding") != "column-dictionary-v1":
        return ledger
    unpacked = {
        key: value
        for key, value in ledger.items()
        if key not in {"encoding", "record_tables", "strings", "values"}
    }
    strings = _expand_front_coded_strings(ledger["strings"])
    decoded_values = [
        _decode_ledger_value(value, strings) for value in ledger["values"]
    ]
    for section in _LEDGER_RECORD_SECTIONS:
        table = ledger["record_tables"][section]
        fields = table["fields"]
        records: list[dict[str, Any]] = []
        for row in table["rows"]:
            record: dict[str, Any] = {}
            for column, field in enumerate(fields):
                value = decoded_values[row[column]]
                if value != _LEDGER_MISSING_VALUE:
                    record[field] = value
            records.append(record)
        unpacked[section] = records
    return unpacked


def _untracked_caller_paths() -> list[str]:
    """Do not silently generate an incomplete tracked-only caller inventory."""
    if not (REPO_ROOT / ".git").exists():
        return []  # Source archives retain their existing deterministic scan.
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0"},
    )
    if result.returncode:
        raise RuntimeError(
            "Cannot establish untracked caller inventory; no outputs written"
        )
    return sorted(
        os.fsdecode(path)
        for path in result.stdout.split(b"\0")
        if path and _is_scannable_text_path(Path(os.fsdecode(path)))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--compatibility-out", type=Path, default=DEFAULT_COMPATIBILITY_OUT
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        untracked = _untracked_caller_paths()
    except (OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if untracked:
        print(
            "ERROR: Untracked caller text would be omitted. Review and stage only intended paths before generating/checking:",
            file=sys.stderr,
        )
        for path in untracked:
            print(f"  {path}", file=sys.stderr)
        return 1

    expected = build_registry()
    unbaselined_debt = expected["documentation_contract"]["unbaselined_debt"]
    if unbaselined_debt:
        print(
            "ERROR: canonical documentation debt is not in the temporary baseline:",
            file=sys.stderr,
        )
        for qualified_name in unbaselined_debt:
            print(f"  {qualified_name}", file=sys.stderr)
        return 1
    expected_compatibility = build_compatibility_ledger(expected)
    if args.check:
        failed = False
        if not args.out.exists():
            print(f"ERROR: missing API classification registry: {args.out}")
            return 1
        actual = json.loads(args.out.read_text(encoding="utf-8"))
        if _normalized(actual) != _normalized(expected):
            print("ERROR: API classification registry is out of date.")
            print(
                "Run: ./scripts/python_runtime.sh scripts/generate_api_classification.py"
            )
            failed = True
        if not args.compatibility_out.exists():
            print(f"ERROR: missing API compatibility ledger: {args.compatibility_out}")
            failed = True
        else:
            actual_compatibility = _unpack_compatibility_ledger(
                json.loads(args.compatibility_out.read_text(encoding="utf-8"))
            )
            if _normalized(actual_compatibility) != _normalized(expected_compatibility):
                print("ERROR: API compatibility ledger is out of date.")
                print(
                    "Run: ./scripts/python_runtime.sh "
                    "scripts/generate_api_classification.py"
                )
                failed = True
        if expected_compatibility["blocked_ambiguous_callers"]:
            print("ERROR: maintained compatibility callers require migration:")
            for caller in expected_compatibility["blocked_ambiguous_callers"]:
                print(f"  - {caller['path']}: {caller['target']}")
            failed = True
        if failed:
            return 1
        print("API classification registry and compatibility ledger are current.")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    args.compatibility_out.parent.mkdir(parents=True, exist_ok=True)
    args.compatibility_out.write_text(
        json.dumps(
            _pack_compatibility_ledger(expected_compatibility),
            separators=(",", ":"),
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote API classification registry to {args.out}")
    print(f"Wrote API compatibility ledger to {args.compatibility_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
