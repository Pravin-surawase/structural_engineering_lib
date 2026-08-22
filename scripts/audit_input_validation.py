#!/usr/bin/env python3
"""Audit validation ownership across maintained IS 456 calculation inputs.

The inventory is discovered from the maintained API-classification registry,
the exported table/material helpers, and public ``IS456Code`` methods. The audit
reports evidence-bearing ownership states rather than a misleading percentage.
It does not claim that static analysis proves every runtime domain; adversarial
route tests remain the decisive safety evidence.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IS456_ROOT = REPO_ROOT / "Python" / "structural_lib" / "codes" / "is456"
LIB_ROOT = REPO_ROOT / "Python" / "structural_lib"
CLASSIFICATION_PATH = REPO_ROOT / "docs" / "reference" / "api-classification.json"

EXPLICIT_PUBLIC_FUNCTIONS = {
    "materials.py": {"get_ec", "get_fcr", "get_steel_stress", "get_xu_max_d"},
    "tables.py": {"get_tc_max_value", "get_tc_value"},
}
IS456_CODE_CLASS = "IS456Code"

PUBLIC_ROUTE_ALIASES = {
    "materials.py:get_ec": ("structural_lib.materials.get_ec",),
    "materials.py:get_fcr": ("structural_lib.materials.get_fcr",),
    "materials.py:get_steel_stress": ("structural_lib.materials.get_steel_stress",),
    "materials.py:get_xu_max_d": ("structural_lib.materials.get_xu_max_d",),
    "tables.py:get_tc_max_value": ("structural_lib.tables.get_tc_max_value",),
    "tables.py:get_tc_value": ("structural_lib.tables.get_tc_value",),
}

VALIDATOR_PREFIXES = (
    "check_positive",
    "check_range",
    "ensure_",
    "require_",
    "validate",
)
CALCULATION_DELEGATES = {
    "calculate_development_length",
    "get_ec",
    "get_fcr",
    "get_steel_stress",
    "get_tau_c",
    "get_tau_c_max",
    "get_tc_max_value",
    "get_tc_value",
    "get_xu_max_d",
}
NUMERIC_ANNOTATIONS = {"complex", "decimal", "float", "int", "real"}
CATEGORICAL_ANNOTATIONS = {"bool", "enum", "literal", "str"}
STRUCTURED_ANNOTATIONS = {"dict", "list", "mapping", "sequence", "set", "tuple"}
TYPED_MODEL_SUFFIXES = (
    "config",
    "geometry",
    "input",
    "materials",
    "model",
    "options",
    "profile",
    "request",
    "spec",
)
AUDITED_DISPOSITIONS = {"advanced", "canonical", "compatibility"}


class ValidationStatus(str, Enum):
    """Static ownership status for one maintained input parameter."""

    PROVEN = "PROVEN"
    DELEGATED = "DELEGATED"
    UNPROVEN = "UNPROVEN"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True)
class ParameterFinding:
    """Validation ownership evidence for one parameter."""

    name: str
    status: ValidationStatus
    owner: str
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class FunctionInfo:
    """Discovered maintained calculation function and its input findings."""

    name: str
    module: str
    file: str
    line: int
    inventory_basis: str
    routes: tuple[str, ...]
    parameters: tuple[ParameterFinding, ...] = field(default_factory=tuple)

    @property
    def qualified_name(self) -> str:
        return f"{self.module}:{self.name}"


def _decorator_name(decorator: ast.expr) -> str | None:
    candidate = decorator.func if isinstance(decorator, ast.Call) else decorator
    if isinstance(candidate, ast.Name):
        return candidate.id
    if isinstance(candidate, ast.Attribute):
        return candidate.attr
    return None


def _is_clause_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_decorator_name(item) == "clause" for item in node.decorator_list)


def _call_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _referenced_parameters(node: ast.AST, parameters: set[str]) -> set[str]:
    return {
        candidate.id
        for candidate in ast.walk(node)
        if isinstance(candidate, ast.Name) and candidate.id in parameters
    }


def _is_failure_return(candidate: ast.Return) -> bool:
    """Recognize fail-closed exits without treating normal branches as guards."""
    value = candidate.value
    if value is None:
        return True
    if isinstance(value, ast.Constant) and value.value is False:
        return True
    if isinstance(value, ast.Call):
        call_name = (_call_name(value) or "").lower()
        if "fail" in call_name or "error" in call_name:
            return True
        for keyword in value.keywords:
            if keyword.arg in {"errors", "is_ok", "is_safe", "valid"}:
                if keyword.arg == "errors":
                    return True
                if (
                    isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is False
                ):
                    return True
    return any(
        isinstance(item, ast.Name)
        and ("error" in item.id.lower() or "fail" in item.id.lower())
        for item in ast.walk(value)
    )


def _contains_guard_exit(statements: list[ast.stmt]) -> bool:
    for statement in statements:
        for candidate in ast.walk(statement):
            if isinstance(candidate, ast.Raise):
                return True
            if isinstance(candidate, ast.Return) and _is_failure_return(candidate):
                return True
    return False


def _contains_validator_call(statements: list[ast.stmt]) -> bool:
    for statement in statements:
        for candidate in ast.walk(statement):
            if not isinstance(candidate, ast.Call):
                continue
            name = (_call_name(candidate) or "").lstrip("_").lower()
            if name.startswith(VALIDATOR_PREFIXES):
                return True
    return False


class FunctionBodyAnalyzer(ast.NodeVisitor):
    """Analyze one function body without leaking state into nested functions."""

    def __init__(self, parameters: set[str]):
        self.parameters = parameters
        self.local_guards: dict[str, set[str]] = {name: set() for name in parameters}
        self.delegations: dict[str, set[str]] = {name: set() for name in parameters}

    def analyze(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for statement in node.body:
            self.visit(statement)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return None

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return None

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return None

    def visit_If(self, node: ast.If) -> None:
        if _contains_guard_exit(node.body):
            evidence = f"direct guard at line {node.lineno}"
            for parameter in _referenced_parameters(node.test, self.parameters):
                self.local_guards[parameter].add(evidence)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        if _contains_validator_call(node.body):
            evidence = f"looped validator at line {node.lineno}"
            for parameter in _referenced_parameters(node.iter, self.parameters):
                self.delegations[parameter].add(evidence)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node)
        if name is None:
            self.generic_visit(node)
            return

        normalized = name.lstrip("_").lower()
        is_validator = normalized.startswith(VALIDATOR_PREFIXES)
        is_calculation_delegate = normalized in CALCULATION_DELEGATES
        if is_validator or is_calculation_delegate:
            evidence = f"{name} at line {node.lineno}"
            referenced = set()
            for argument in node.args:
                referenced.update(_referenced_parameters(argument, self.parameters))
            for keyword in node.keywords:
                referenced.update(
                    _referenced_parameters(keyword.value, self.parameters)
                )
            for parameter in referenced:
                self.delegations[parameter].add(evidence)
        self.generic_visit(node)


def _all_parameters(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.arg]:
    parameters = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
    if node.args.vararg is not None:
        parameters.append(node.args.vararg)
    if node.args.kwarg is not None:
        parameters.append(node.args.kwarg)
    return [item for item in parameters if item.arg not in {"self", "cls"}]


def _annotation_tokens(argument: ast.arg) -> set[str]:
    if argument.annotation is None:
        return set()
    return {
        node.id.lower()
        for node in ast.walk(argument.annotation)
        if isinstance(node, ast.Name)
    }


def _typed_owner(argument: ast.arg) -> tuple[ValidationStatus, str, tuple[str, ...]]:
    tokens = _annotation_tokens(argument)
    annotation = ast.unparse(argument.annotation) if argument.annotation else "missing"
    if tokens & CATEGORICAL_ANNOTATIONS:
        return (
            ValidationStatus.NOT_APPLICABLE,
            "categorical/control contract",
            (f"annotation {annotation}",),
        )
    if tokens & STRUCTURED_ANNOTATIONS:
        return (
            ValidationStatus.UNPROVEN,
            "unassigned collection-content validation",
            (f"annotation {annotation}",),
        )
    if any(token.endswith(TYPED_MODEL_SUFFIXES) for token in tokens):
        return (
            ValidationStatus.DELEGATED,
            "typed domain-model contract",
            (f"annotation {annotation}",),
        )
    return (
        ValidationStatus.UNPROVEN,
        "unassigned",
        (f"annotation {annotation}",),
    )


def _analyze_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    relative_module: str,
    filepath: Path,
    inventory_basis: str,
    routes: tuple[str, ...],
) -> FunctionInfo:
    arguments = _all_parameters(node)
    parameter_names = {item.arg for item in arguments}
    analyzer = FunctionBodyAnalyzer(parameter_names)
    analyzer.analyze(node)

    findings: list[ParameterFinding] = []
    for argument in arguments:
        name = argument.arg
        local_evidence = tuple(sorted(analyzer.local_guards[name]))
        delegated_evidence = tuple(sorted(analyzer.delegations[name]))
        if local_evidence:
            finding = ParameterFinding(
                name,
                ValidationStatus.PROVEN,
                "local guard",
                local_evidence,
            )
        elif delegated_evidence:
            finding = ParameterFinding(
                name,
                ValidationStatus.DELEGATED,
                "called validator or guarded calculation",
                delegated_evidence,
            )
        else:
            status, owner, evidence = _typed_owner(argument)
            finding = ParameterFinding(name, status, owner, evidence)
        findings.append(finding)

    return FunctionInfo(
        name=node.name,
        module=relative_module,
        file=str(filepath),
        line=node.lineno,
        inventory_basis=inventory_basis,
        routes=routes,
        parameters=tuple(findings),
    )


def _module_tree(filepath: Path) -> ast.Module:
    try:
        return ast.parse(filepath.read_text(encoding="utf-8"), filename=str(filepath))
    except (OSError, SyntaxError) as exc:
        raise RuntimeError(f"cannot audit {filepath}: {exc}") from exc


def _find_top_level_function(
    filepath: Path, name: str
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in _module_tree(filepath).body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == name
        ):
            return node
    raise RuntimeError(f"classified function {name} not found in {filepath}")


def _classification_owners(directory: Path) -> dict[tuple[str, str], set[str]]:
    classification_path = directory / "docs" / "reference" / "api-classification.json"
    try:
        registry = json.loads(classification_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"cannot read {classification_path}: {exc}") from exc

    owners: dict[tuple[str, str], set[str]] = {}
    for surface in registry.get("surfaces", []):
        for symbol in surface.get("symbols", []):
            if (
                not symbol.get("declared_export")
                or symbol.get("kind") != "function"
                or symbol.get("claim_disposition") not in AUDITED_DISPOSITIONS
            ):
                continue
            owner = (symbol["defined_in"], symbol["name"])
            owners.setdefault(owner, set()).add(symbol["qualified_name"])
    return owners


def audit_directory(directory: Path, verbose: bool = False) -> list[FunctionInfo]:
    """Discover classified public owners plus explicit compatibility helpers."""
    library_root = directory / "Python" / "structural_lib"
    is456_root = library_root / "codes" / "is456"
    if not library_root.is_dir():
        raise RuntimeError(f"Directory not found: {library_root}")

    owners = _classification_owners(directory)
    functions: list[FunctionInfo] = []
    for (defined_in, name), routes in sorted(owners.items()):
        if not defined_in.startswith("structural_lib."):
            raise RuntimeError(
                f"classified owner is outside structural_lib: {defined_in}.{name}"
            )
        relative_module = (
            defined_in.removeprefix("structural_lib.").replace(".", "/") + ".py"
        )
        filepath = library_root / relative_module
        node = _find_top_level_function(filepath, name)
        functions.append(
            _analyze_function(
                node,
                relative_module=relative_module,
                filepath=filepath,
                inventory_basis="classified public owner",
                routes=tuple(sorted(routes)),
            )
        )

    for relative_module, names in sorted(EXPLICIT_PUBLIC_FUNCTIONS.items()):
        filepath = is456_root / relative_module
        for name in sorted(names):
            node = _find_top_level_function(filepath, name)
            canonical = (
                "structural_lib.codes.is456."
                + relative_module.removesuffix(".py").replace("/", ".")
                + f".{name}"
            )
            aliases = PUBLIC_ROUTE_ALIASES.get(f"{relative_module}:{name}", ())
            functions.append(
                _analyze_function(
                    node,
                    relative_module=f"codes/is456/{relative_module}",
                    filepath=filepath,
                    inventory_basis="explicit lower-level compatibility helper",
                    routes=(canonical, *aliases),
                )
            )

    class_path = is456_root / "__init__.py"
    for node in _module_tree(class_path).body:
        if not isinstance(node, ast.ClassDef) or node.name != IS456_CODE_CLASS:
            continue
        for method in node.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if method.name.startswith("_") or not _all_parameters(method):
                continue
            functions.append(
                _analyze_function(
                    method,
                    relative_module="codes/is456/__init__.py",
                    filepath=class_path,
                    inventory_basis="public IS456Code method",
                    routes=(f"structural_lib.codes.is456.IS456Code.{method.name}",),
                )
            )

    deduplicated = {
        (item.module, item.name, item.inventory_basis): item for item in functions
    }
    functions = list(deduplicated.values())
    if verbose:
        for function in sorted(functions, key=lambda item: (item.module, item.line)):
            print(f"  Scanning: {function.qualified_name} ({function.inventory_basis})")
    return functions


def generate_report(functions: list[FunctionInfo], verbose: bool = False) -> dict:
    """Build a deterministic status report without a synthetic percentage."""
    del verbose
    status_counts = {status.value: 0 for status in ValidationStatus}
    unresolved: list[dict[str, object]] = []
    serialized_functions = []
    for function in sorted(functions, key=lambda item: (item.module, item.line)):
        serialized_parameters = []
        for parameter in function.parameters:
            status_counts[parameter.status.value] += 1
            serialized = {
                "name": parameter.name,
                "status": parameter.status.value,
                "owner": parameter.owner,
                "evidence": list(parameter.evidence),
            }
            serialized_parameters.append(serialized)
            if parameter.status is ValidationStatus.UNPROVEN:
                unresolved.append(
                    {
                        "function": function.qualified_name,
                        "file": function.file,
                        "line": function.line,
                        **serialized,
                    }
                )
        serialized_functions.append(
            {
                **{
                    key: value
                    for key, value in asdict(function).items()
                    if key != "parameters"
                },
                "qualified_name": function.qualified_name,
                "routes": list(function.routes),
                "parameters": serialized_parameters,
            }
        )

    return {
        "schema_version": "input-validation-ownership/v1",
        "scope": {
            "root": "Python/structural_lib",
            "inventory": [
                "canonical, advanced, and compatibility owners from api-classification.json",
                "explicit lower-level table/material compatibility helpers",
                "public IS456Code methods with inputs",
            ],
            "compatibility_aliases": "reported on their canonical owner",
            "limitation": (
                "Static ownership evidence is not runtime safety proof; "
                "adversarial public-route tests remain decisive."
            ),
        },
        "summary": {
            "total_functions": len(functions),
            "total_parameters": sum(len(item.parameters) for item in functions),
            "status_counts": status_counts,
            "unproven_count": len(unresolved),
        },
        "unresolved_parameters": unresolved,
        "functions": serialized_functions,
    }


def print_report(report: dict, verbose: bool = False) -> None:
    """Print the ownership summary and every unresolved parameter."""
    summary = report["summary"]
    counts = summary["status_counts"]
    print()
    print("=" * 64)
    print("  INPUT VALIDATION OWNERSHIP AUDIT")
    print("=" * 64)
    print(f"  Maintained functions: {summary['total_functions']}")
    print(f"  Input parameters:     {summary['total_parameters']}")
    for status in ValidationStatus:
        print(f"  {status.value:18} {counts[status.value]}")
    print()

    unresolved = report["unresolved_parameters"]
    if unresolved:
        print("UNRESOLVED PARAMETERS")
        for item in unresolved:
            print(
                f"  - {item['function']}:{item['line']}::{item['name']} "
                f"({'; '.join(item['evidence'])})"
            )
    else:
        print("Result: no unassigned validation owners in the maintained inventory.")

    if verbose:
        print()
        print("Compatibility aliases are bound to the same canonical owner.")
        print(report["scope"]["limitation"])


def diagnostic_exit_code(report: dict) -> int:
    """Return nonzero while any maintained parameter is unassigned."""
    return 1 if report["summary"]["unproven_count"] else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", "-j", type=Path, help="Write the report as JSON")
    parser.add_argument("--directory", "-d", type=Path, default=Path("."))
    args = parser.parse_args()

    project_dir = args.directory.resolve()
    print(f"Auditing input-validation ownership in {project_dir}")
    functions = audit_directory(project_dir, verbose=args.verbose)
    if not functions:
        print("No maintained calculation functions found.", file=sys.stderr)
        return 1

    report = generate_report(functions)
    if args.json:
        args.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Report saved to {args.json}")
    else:
        print_report(report, verbose=args.verbose)
    return diagnostic_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
