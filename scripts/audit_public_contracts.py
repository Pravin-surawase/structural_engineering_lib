#!/usr/bin/env python3
"""Reconcile S3 contract owners and schema semantics without granting qualification.

The existing classification, compatibility ledger and OpenAPI remain the source
catalogues. This receipt records exhaustive ownership/reachability, field policy
counts and the maintained instance-test locations for their frozen candidate.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

OUTPUT = REPO_ROOT / "docs/verification/library-s3-contract-matrix.json"
METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def references(value: Any) -> set[str]:
    if isinstance(value, dict):
        refs = (
            {value["$ref"].rsplit("/", 1)[-1]}
            if "$ref" in value and value["$ref"].startswith("#/components/schemas/")
            else set()
        )
        return refs | set().union(*(references(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(references(v) for v in value))
    return set()


def _test_calls() -> list[tuple[str, str, str]]:
    found = []
    for path in sorted((REPO_ROOT / "fastapi_app/tests").glob("test_*.py")):
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                not isinstance(node, ast.Call)
                or not isinstance(node.func, ast.Attribute)
                or node.func.attr not in METHODS
                or not node.args
            ):
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                found.append(
                    (node.func.attr, arg.value, str(path.relative_to(REPO_ROOT)))
                )
    return found


def build_matrix() -> dict[str, Any]:
    from fastapi import routing
    from fastapi_app.main import app
    from scripts.generate_api_classification import build_registry

    registry = build_registry()
    spec = app.openapi()
    schemas = spec["components"]["schemas"]
    test_calls = _test_calls()
    # New FastAPI releases retain included routers as lazy contexts. Their
    # public iterator exposes the effective IDs/prefixes used by OpenAPI;
    # older releases already expose those effective routes directly.
    contexts = getattr(routing, "iter_route_contexts", None)
    routes = contexts(app.routes) if contexts is not None else app.routes
    route_by_id = {
        (r.operation_id or r.unique_id): r for r in routes if hasattr(r, "unique_id")
    }
    operations = []
    roles: dict[str, dict[str, set[int]]] = {
        name: {"request": set(), "response": set()} for name in schemas
    }

    def closure(roots: set[str]) -> set[str]:
        seen: set[str] = set()
        pending = list(roots)
        while pending:
            name = pending.pop()
            if name in seen:
                continue
            if name not in schemas:
                raise RuntimeError(f"Unresolved component schema: {name}")
            seen.add(name)
            pending.extend(references(schemas[name]) - seen)
        return seen

    for path, item in sorted(spec["paths"].items()):
        for method, operation in sorted(item.items()):
            if method not in METHODS:
                continue
            route = route_by_id[operation["operationId"]]
            owner = inspect.getmodule(route.endpoint).__name__
            pattern = re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", path) + "$")
            tests = sorted(
                {p for m, url, p in test_calls if m == method and pattern.match(url)}
            )
            index = len(operations)
            roots = {
                "request": references(operation.get("requestBody", {}))
                | references(operation.get("parameters", [])),
                "response": references(operation["responses"]),
            }
            for role, names in roots.items():
                for name in closure(names):
                    roles[name][role].add(index)
            operations.append(
                {
                    "id": operation["operationId"],
                    "method": method.upper(),
                    "path": path,
                    "owner": owner,
                    "schema_roots": {k: sorted(v) for k, v in roots.items()},
                    "instance_tests": tests,
                    "evidence_boundary": (
                        "MAINTAINED_INSTANCE_TESTS"
                        if tests
                        else "SCHEMA_AND_SHARED_ENVELOPE_ONLY"
                    ),
                    "support": (
                        "SEPARATE_NATIVE_ACCEPTANCE_GATE"
                        if "etabs" in path or "excel" in path
                        else "DECLARED_BOUNDED_OPERATION"
                    ),
                    "admission": "OWNING_PYDANTIC_MODEL_AND_ROUTE_VALIDATORS",
                }
            )

    components = []
    for name, schema in sorted(schemas.items()):
        Draft202012Validator.check_schema(schema)
        role = roles[name]
        if not (role["request"] or role["response"]):
            raise RuntimeError(f"Orphan component schema: {name}")
        properties = schema.get("properties", {})

        def nullable(p: dict[str, Any]) -> bool:
            return p.get("type") == "null" or any(
                v.get("type") == "null" for v in p.get("anyOf", [])
            )

        counts = [
            len(properties),
            len(schema.get("required", [])),
            sum("default" in p for p in properties.values()),
            sum(nullable(p) for p in properties.values()),
            sum("enum" in p for p in properties.values()),
        ]
        components.append(
            {
                "name": name,
                "role": (
                    "shared"
                    if all(role.values())
                    else "request_only" if role["request"] else "response_only"
                ),
                "operations": sorted(role["request"] | role["response"]),
                "field_counts": counts,
                "sha256": digest(schema),
            }
        )

    families = [
        {
            "journey": w["journey_id"],
            "request_type": w["request_type"],
            "fields": w["request_field_count"],
            "schema_sha256": w["request_schema_sha256"],
            "cookbook": w["cookbook_path"],
            "admission": "STRICT_FINITE_NO_COERCION_EXTRA_FORBIDDEN_VALIDATE_DEFAULTS",
            "schema_default": w["request_contract"],
            "instance_test": "Python/tests/integration/test_family_facade_convergence.py::test_every_family_admission_defaults_schema_and_json_policy",
        }
        for w in registry["family_facade_workflows"]
    ]
    return {
        "schema_version": "library-s3-contract-matrix/v1",
        "evidence_boundary": "SOURCE_AND_SOFTWARE_CONTRACT_AUDIT_NOT_ENGINEERING_OR_NATIVE_ACCEPTANCE",
        "component_policy_pointer": "fastapi_app/openapi_baseline.json#/components/schemas/<name>",
        "field_count_columns": [
            "properties",
            "required",
            "default",
            "nullable",
            "enum",
        ],
        "schema_policy": {
            "omission": "Follow each owning schema required/default declaration; defaults validated by owning model",
            "null": "Only a declared null branch admits null; never substitute zero for unavailable results",
            "bounds_enums_units_basis": "Owning model validators and family field contracts remain authoritative",
            "evolution": "Review schema and caller meaning before updating snapshot; additive compatibility fields and unsafe-input corrections documented in api-stability.md",
            "wall_compatibility": "Retain legacy numeric-string coercion; strict family facade remains non-coercing",
            "instances": "Indexed tests are evidence owners, not a claim every possible payload or native workflow was executed",
        },
        "counts": {
            "surfaces": len(registry["surfaces"]),
            "projections": sum(
                s["classified_symbol_count"] for s in registry["surfaces"]
            ),
            "operations": len(operations),
            "paths": len(spec["paths"]),
            "components": len(components),
            "family_fields": sum(f["fields"] for f in families),
        },
        "openapi_sha256": digest(spec),
        "signature_policy": registry["signature_policy"],
        "families": families,
        "operations": operations,
        "components": components,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    value = build_matrix()
    if args.write:
        OUTPUT.write_text(json.dumps(value, separators=(",", ":")) + "\n")
    elif not OUTPUT.exists() or json.loads(OUTPUT.read_text()) != value:
        print("FAIL: S3 contract matrix is stale; review semantics before --write")
        return 1
    print(json.dumps(value["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
