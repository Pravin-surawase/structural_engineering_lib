#!/usr/bin/env python3
"""Generate or check the 13-family external-preview cookbook and reference."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import runpy
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

PYTHON_ROOT = REPO_ROOT / "Python"
COOKBOOK_ROOT = REPO_ROOT / "docs/cookbook/python"
REFERENCE_PATH = REPO_ROOT / "docs/reference/family-facade-contracts.md"
INDEX_PATH = COOKBOOK_ROOT / "family-facades.md"


def _recipe_specs() -> tuple[Any, ...]:
    namespace = runpy.run_path(
        str(REPO_ROOT / "scripts/verify_lib_pro_013_f0_family_artifact.py")
    )
    return namespace["recipe_specs"]()


def _request_type(path: str) -> type[Any]:
    module_name, _, name = path.rpartition(".")
    return getattr(importlib.import_module(module_name), name)


def _schema_hash(schema: Mapping[str, Any]) -> str:
    payload = json.dumps(schema, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _title(journey_id: str) -> str:
    words = (
        journey_id.removeprefix("is456.")
        .removesuffix("/v1")
        .replace(".", " ")
        .replace("-", " ")
        .split()
    )
    return " ".join(word.upper() if word == "is456" else word.title() for word in words)


def _python_assignment(path: tuple[str, ...], value: Any) -> str:
    target = "invalid_payload" + "".join(f"[{part!r}]" for part in path)
    return f"{target} = {value!r}"


def _page(workflow: Any, recipe: Any) -> str:
    alias = workflow.module.rsplit(".", 1)[-1]
    payload = json.dumps(recipe.payload, indent=4, sort_keys=True, allow_nan=False)
    return f'''---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# {_title(workflow.journey_id)}

Journey: `{workflow.journey_id}`
Request: `{workflow.request_contract}`
Result: `{workflow.result_contract}`
Errors: `{workflow.error_contract}`

This recipe constructs caller-supplied data and delegates to the maintained
calculation owner. It does not infer loads, geometry, topology, soil data,
evidence, review inputs, or professional acceptance.

## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import {alias}

payload = json.loads(
    r"""{payload}"""
)
request = {alias}.{recipe.loader}(payload)
result = {alias}.{recipe.operation}(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: {recipe.expected_engineering_status}
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

## Rejected-input example

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
{_python_assignment(recipe.invalid_path, recipe.invalid_value)}

try:
    {alias}.{recipe.loader}(invalid_payload)
except InputContractError as error:
    print([issue.to_dict() for issue in error.issues])
```

## Compatibility and evidence

- Maintained calculation owner: `{workflow.compatibility_owner}`
- Result consumer: `{workflow.consumer_contract}`
- Evidence class: {workflow.evidence_class}
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

This Alpha recipe is not professional approval, engineering-use approval,
Windows application acceptance, a release authorization, or publication.
'''


def _index(workflows: tuple[Any, ...], recipes: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| `{workflow.journey_id}` | [{_title(workflow.journey_id)}]({Path(workflow.cookbook_path).name}) | "
        f"`{recipes[workflow.journey_id].expected_engineering_status}` |"
        for workflow in workflows
    )
    return f"""---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: guide
complexity: intermediate
tags: [canonical-api, family-facades, lib-pro-012-r0]
---

# Canonical IS 456 Family Facades

These 13 copy-paste journeys are generated from the frozen facade registry and
the exact-wheel recipe owner. Every page uses strict grouped intake, the common
structured error boundary, the maintained calculation owner, and finite JSON
result consumption.

| Journey | Recipe | Valid recipe outcome |
|---|---|---|
{rows}

The two non-PASS recipes are intentional valid-input evidence. An engineering
`FAIL` or review `HOLD` is not invalid intake.

See [family facade contracts](../../reference/family-facade-contracts.md) for
generated signatures, schema identities, units, enums, structured issues, and
status guidance. Replay all pages against an exact wheel with:

```bash
./scripts/python_runtime.sh scripts/verify_lib_pro_012_r0_external_preview.py --wheel dist/structural_lib_is456-*.whl
```

This external-preview candidate remains subject to qualified review. It is not
professional approval, Windows application acceptance, release authorization,
or publication.
"""


def _resolve(node: Mapping[str, Any], root: Mapping[str, Any]) -> Mapping[str, Any]:
    current = node
    if "$ref" in current:
        value: Any = root
        for part in str(current["$ref"])[2:].split("/"):
            value = value[part]
        if isinstance(value, Mapping):
            return _resolve(value, root)
    alternatives = current.get("anyOf")
    if isinstance(alternatives, list):
        non_null = [
            item
            for item in alternatives
            if isinstance(item, Mapping) and item.get("type") != "null"
        ]
        if len(non_null) == 1:
            return _resolve(non_null[0], root)
    return current


def _enum_rows(
    node: Mapping[str, Any], root: Mapping[str, Any], prefix: str = ""
) -> list[tuple[str, str]]:
    current = _resolve(node, root)
    properties = current.get("properties")
    if isinstance(properties, Mapping) and properties:
        rows: list[tuple[str, str]] = []
        for name, child in properties.items():
            if isinstance(child, Mapping):
                path = f"{prefix}.{name}" if prefix else str(name)
                rows.extend(_enum_rows(child, root, path))
        return rows
    values = current.get("enum")
    if values is None and "const" in current:
        values = [current["const"]]
    if values is None and current.get("type") == "boolean":
        values = [False, True]
    if values is None:
        return []
    return [(prefix, ", ".join(f"`{value}`" for value in values))]


def _reference(workflows: tuple[Any, ...]) -> str:
    from structural_lib.services.contracts.common import (
        INPUT_ISSUE_CODES_V1,
        ValidationDimension,
        schema_leaf_paths,
    )

    signature_rows: list[str] = []
    enum_sections: list[str] = []
    unit_counts: Counter[str] = Counter()
    total_fields = 0
    for workflow in workflows:
        module = importlib.import_module(workflow.module)
        request_type = _request_type(workflow.request_type)
        schema = request_type.model_json_schema(mode="validation")
        leaf_paths = schema_leaf_paths(request_type)
        total_fields += len(leaf_paths)
        for contract in request_type.field_contracts:
            if contract.unit is not None:
                unit_counts[contract.unit] += 1
        constructor_names = workflow.constructor.split("/")
        operation_names = workflow.operation.split("/")
        constructor_signatures = "<br>".join(
            f"`{name}{inspect.signature(getattr(module, name))}`"
            for name in constructor_names
        )
        operation_signatures = "<br>".join(
            f"`{name}{inspect.signature(getattr(module, name))}`"
            for name in operation_names
        )
        signature_rows.append(
            f"| `{workflow.journey_id}` | {constructor_signatures} | "
            f"{operation_signatures} | `{len(leaf_paths)}` | `{_schema_hash(schema)}` |"
        )
        enums = _enum_rows(schema, schema)
        if enums:
            enum_sections.append(
                f"### `{workflow.journey_id}`\n\n"
                + "\n".join(f"- `{path}`: {values}" for path, values in enums)
            )

    units = "\n".join(
        f"| `{unit}` | {count} |" for unit, count in sorted(unit_counts.items())
    )
    dimensions = "\n".join(
        f"- `{dimension.value}`" for dimension in ValidationDimension
    )
    issues = "\n".join(f"- `{code}`" for code in INPUT_ISSUE_CODES_V1)
    return f"""---
owner: Main Agent
status: active
last_updated: 2026-08-28
doc_type: reference
complexity: advanced
tags: [canonical-api, field-contracts, lib-pro-012-r0]
---

# Family Facade Contracts

This file is generated from the live 13-journey registry and strict request
models. It covers {total_fields} advertised request-field leaves. The full JSON
schemas and per-field decisions are in `api-classification.json`.

## Exact signatures and schema identities

| Journey | Constructor | Operation | Fields | Schema SHA-256 |
|---|---|---|---:|---|
{chr(10).join(signature_rows)}

## Validation dimensions

Every advertised field has a decision in the generated classification. A
dimension absent from a route is recorded there as `not_applicable`, never
`UNPROVEN`. The classification also distinguishes a strict request-model
cross-field validator from an explicit delegation to the maintained owner;
generated metadata is not promoted into independent arithmetic evidence.

{dimensions}

## Units

Units are read from field contracts; `dimensionless` is an explicit quantity
decision rather than a hidden conversion.

| Unit | Field contracts |
|---|---:|
{units}

## Enum and topology values

{chr(10).join(enum_sections)}

## Structured input issues

Invalid intake raises `InputContractError`. Each issue uses `input-issue/v1`;
transport projection uses `structural-problem/v1`.

{issues}

## Result and review status

- `intake_status`: `VALID` only after strict construction.
- `calculation_status`: `COMPLETED` only after the maintained owner returns.
- `engineering_status`: `PASS`, `FAIL`, or `HOLD`; this is not intake validity.
- `review_status`: remains `QUALIFIED_REVIEW_REQUIRED` for every recipe.
- Result consumption is finite JSON through `to_dict()` and
  `structural-result-envelope/v2`.

No status is professional approval, engineering-use approval, Windows
application acceptance, release authorization, or publication.
"""


def build_outputs() -> dict[Path, str]:
    sys.path.insert(0, str(PYTHON_ROOT))
    from structural_lib.services.family_facade_registry import (
        FAMILY_FACADE_WORKFLOWS,
    )

    workflows = tuple(FAMILY_FACADE_WORKFLOWS)
    recipes = {recipe.journey_id: recipe for recipe in _recipe_specs()}
    journey_ids = {workflow.journey_id for workflow in workflows}
    if set(recipes) != journey_ids:
        raise RuntimeError(
            "Facade registry and exact-wheel recipes have different journey ids."
        )
    outputs = {
        Path(workflow.cookbook_path): _page(workflow, recipes[workflow.journey_id])
        for workflow in workflows
    }
    outputs[INDEX_PATH.relative_to(REPO_ROOT)] = _index(workflows, recipes)
    outputs[REFERENCE_PATH.relative_to(REPO_ROOT)] = _reference(workflows)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    outputs = build_outputs()
    stale: list[str] = []
    for relative, content in outputs.items():
        path = REPO_ROOT / relative
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(relative.as_posix())
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    if stale:
        print("Stale family facade documentation:")
        for path in stale:
            print(f"- {path}")
        return 1
    if args.check:
        print(f"Family facade documentation is current ({len(outputs)} files).")
    else:
        print(f"Generated family facade documentation ({len(outputs)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
