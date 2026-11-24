#!/usr/bin/env python3
"""Generate or check the 13-family public cookbook and reference."""

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

import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _lib.utils import REPO_ROOT

PYTHON_ROOT = REPO_ROOT / "Python"
COOKBOOK_ROOT = REPO_ROOT / "docs/cookbook/python"
REFERENCE_PATH = REPO_ROOT / "docs/reference/family-facade-contracts.md"
INDEX_PATH = COOKBOOK_ROOT / "family-facades.md"
PROJECT_VERSION = str(
    tomllib.loads((PYTHON_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]["version"]
)


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


_CONTINUOUS_SLAB_RERUN = """## Rerun affected 0.31.0 results

Rerun continuous one-way slab checks from 0.31.0 that used a strip width
other than 1,000 mm. Rerun any saved result whose submitted width you cannot
confirm. This applies to built-in and supplied coefficients through Python or
HTTP. Prioritize accepted results from narrower strips, where 0.31.0 could
understate steel demand and report a false `PASS`.

Use a build that includes the 0.31.1 correction. Resubmit the original loads,
geometry, strip width, reinforcement and reviewed inputs. Review the new
engineering verdict and the moment, required steel and shear values per metre.
Refresh reports or exports that used the old results. The line load along the
physical strip still scales with its width. Capacity-exceeded diagnostics give
moments for that physical strip in kN·m.

"""


def _continuous_slab_width_example() -> str:
    evidence = REPO_ROOT / "docs/verification/library-0311-s1-continuous-slab.json"
    frozen = json.loads(evidence.read_text(encoding="utf-8"))
    case = next(
        case
        for case in frozen["built_in"]["cases"]
        if case["id"] == "SLAB-01-DEFICIENT"
    )
    widths = tuple(case["widths_mm"])
    updates = []
    for group, fields in case["request_overrides"].items():
        arguments = "".join(
            f"    {name}={value!r},\n" for name, value in fields.items()
        )
        updates.append(f'challenge["{group}"].update(\n{arguments})')
    update_code = "\n".join(updates)
    expected = case["expected_at_each_width"]
    required = expected["positive_governing_steel_mm2_per_m"]
    provided = expected["positive_provided_steel_mm2_per_m"]
    status = expected["engineering_status"]
    output = "\n".join(
        f"{width} mm: {status}, {required:.3f} required, {provided:.3f} provided (mm²/m)"
        for width in widths
    )
    positive_moment = expected["positive_moment_knm_per_m"]
    negative_moment = expected["negative_moment_knm_per_m"]
    shear = expected["shear_kn_per_m"]
    return f"""## Corrected strip-width example

Run this block after the passing recipe above, using source that includes the
0.31.1 correction. The modified loads, section and positive bars produce a
steel shortfall.

```python
challenge = json.loads(request_json)
{update_code}

for width_mm in {widths}:
    challenge["geometry"]["strip_width_mm"] = width_mm
    request = slab.load_continuous_one_way_json(json.dumps(challenge))
    checked = slab.design_continuous_one_way(request)
    steel = checked.calculation.positive_reinforcement
    print(
        f"{{width_mm}} mm: {{checked.engineering_status.value}}, "
        f"{{steel.governing_required_mm2_per_m:.3f}} required, "
        f"{{steel.provided_mm2_per_m:.3f}} provided (mm²/m)"
    )
```

The corrected calculation prints the following output.

```text
{output}
```

At every width the positive moment is {positive_moment:g} kN·m/m, the negative moment
magnitude is {negative_moment:.2f} kN·m/m and the end shear is {shear:g} kN/m.
Use the 1,000 mm recipe above as the passing control. A completed `FAIL`
means the input was evaluated and a check failed. See the
[frozen slab cases](../../verification/library-0311-s1-continuous-slab.json).

"""


def _page(workflow: Any, recipe: Any) -> str:
    alias = workflow.module.rsplit(".", 1)[-1]
    payload = json.dumps(recipe.payload, indent=4, sort_keys=True, allow_nan=False)
    members = list(
        dict.fromkeys(workflow.constructor.split("/") + workflow.operation.split("/"))
    )
    related_workflow = ""
    if workflow.journey_id == "is456.column.supplied-steel-check/v1":
        members.extend(
            (
                "load_four_corner_member",
                "check_four_corner_member",
                "render_four_corner_member_html",
                "load_tied_rectangular_member",
                "check_tied_rectangular_member",
                "render_tied_rectangular_member_html",
                "load_positioned_rectangular_member",
                "check_positioned_rectangular_member",
                "render_positioned_rectangular_member_html",
                "load_slender_rectangular_member",
                "check_slender_rectangular_member",
                "render_slender_rectangular_member_html",
                "render_slender_rectangular_member_svg",
                "load_circular_member",
                "check_circular_member",
                "render_circular_member_html",
                "render_circular_member_svg",
                "load_column_catalogue",
                "select_column_from_catalogue",
                "render_column_catalogue_html",
                "render_column_catalogue_svg",
                "load_column_member_detailing",
                "check_column_member_detailing",
                "render_column_member_detailing_html",
                "render_column_member_detailing_svg",
                "render_column_member_bbs_csv",
            )
        )
        related_workflow = (
            "For four equal physical corner bars and actual closed ties, use the "
            "[four-corner member guide](column-four-corner-member-check.md).\n\n"
            "For eight equal bars or either orientation of a six-bar cage, use the "
            "[tied rectangular column guide](column-four-corner-member-check.md#six-and-eight-bar-tied-rectangles).\n\n"
            "For larger or asymmetric mixed-diameter cages with aligned links, see the "
            "[positioned rectangular column guide](column-four-corner-member-check.md#positioned-mixed-bar-rectangles).\n\n"
            "For axis-specific restraint and slenderness using those actual cages, see the "
            "[slender rectangular column guide](column-four-corner-member-check.md#slender-rectangular-columns-with-actual-bars).\n\n"
            "For short circular cages with closed rings or spirals, see the "
            "[circular column guide](circular-column-member-check.md).\n\n"
            "To select a short eight-bar rectangle from approved sizes, bars and ties, see the "
            "[column catalogue guide](column-catalogue-selection.md).\n\n"
            "For supplied column shear, tie zones, end development and schedules, see the "
            "[column member detailing guide](column-member-detailing.md).\n\n"
        )
    api_members = "\n".join(f"        - {name}" for name in members)
    engineering_failure = ""
    if workflow.journey_id == "is456.beam.design/v1":
        engineering_failure = """## Engineering `FAIL` example
```python
failed_payload = dict(payload)
failed_payload["actions"] = dict(payload["actions"], mu_knm=2000.0)
failed = beam.design(beam.load(failed_payload))
assert failed.engineering_status.value == "FAIL"
assert failed.to_dict()["envelope"]["overall_status"] == "FAIL"
```

This is valid intake and a completed calculation. It must not be represented as
an exception, HTTP failure, or professional acceptance.

"""
    last_updated = "2026-08-28"
    rerun_note = ""
    corrected_example = ""
    replay_guidance = (
        f"Replay this recipe with a local build of source package version `{PROJECT_VERSION}`.\n"
        "Use the [release guide](../../getting-started/release-status.md) for the public\n"
        "package. Results require qualified review."
    )
    if workflow.journey_id == "is456.slab.continuous-one-way/v1":
        last_updated = "2026-11-18"
        rerun_note = _CONTINUOUS_SLAB_RERUN
        corrected_example = _continuous_slab_width_example()
        replay_guidance = (
            "Use the [Current Release page](../../getting-started/release-status.md) to\n"
            "check public package availability. The strip-width example above was checked\n"
            "on source with the correction. Results require qualified review."
        )
    return f'''---
owner: Main Agent
status: active
last_updated: {last_updated}
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

{rerun_note}## Copy-paste recipe

```python
import json

from structural_lib.design.is456 import {alias}

request_json = r"""{payload}"""
request = {alias}.{recipe.loader}_json(request_json)
payload = request.model_dump(mode="json")
result = {alias}.{recipe.operation}(request)

print(result.intake_status)
print(result.calculation_status)
print(result.engineering_status)  # expected: {recipe.expected_engineering_status}
print(json.dumps(result.to_dict(), allow_nan=False, sort_keys=True))
```

`PASS`, `FAIL`, and `HOLD` are engineering/review outcomes for valid intake.
They are not interchangeable with `InputContractError`.

The JSON loader accepts text or UTF-8 bytes (including a byte-order mark),
rejects duplicate fields and non-finite numbers, and preserves field issue
paths. For a saved request, use
`{alias}.{recipe.loader}_json(Path("request.json").read_bytes())` after importing
`Path` from `pathlib`. Existing Python mappings use `{alias}.{recipe.loader}`.

{corrected_example}## Rejected-input example

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

{engineering_failure}{related_workflow}## Python API

Typed request groups are exported from `{workflow.module}` alongside the
operations below. Mapping inputs remain supported for JSON/HTTP callers.
This reference follows the current source; JSON loaders, newly added builders,
and group imports require its matching build rather than an older published wheel.

::: {workflow.module}
    options:
      docstring_style: numpy
      show_root_heading: false
      show_signature_annotations: true
      members:
{api_members}

## Compatibility and evidence

- Maintained calculation owner: `{workflow.compatibility_owner}`
- Result consumer: `{workflow.consumer_contract}`
- Evidence class: {workflow.evidence_class}
- Exact signatures, units, enums, field decisions, and status guidance:
  [family facade contracts](../../reference/family-facade-contracts.md)

{replay_guidance}
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

The source package version is `{PROJECT_VERSION}`. Use the
[release guide](../../getting-started/release-status.md) for the public package.
Results require qualified review.
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
            f"`{name}{inspect.signature(getattr(module, name))}`".replace("|", "\\|")
            for name in constructor_names
        )
        operation_signatures = "<br>".join(
            f"`{name}{inspect.signature(getattr(module, name))}`".replace("|", "\\|")
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

No calculation or review status is professional approval, engineering-use
approval, construction-use approval, or Windows application acceptance. The
`v{PROJECT_VERSION}` software-release status is tracked separately in the release ledger.
"""


def _beam_documentation_namespace() -> dict[str, Any]:
    return runpy.run_path(
        str(REPO_ROOT / "scripts/verify_lib_pro_012_r0_external_preview.py")
    )


def _beam_supplied_page(namespace: Mapping[str, Any]) -> str:
    payload = namespace["_beam_supplied_documentation_payload"]()
    serialized = json.dumps(payload, indent=4, sort_keys=True, allow_nan=False)
    return f'''---
owner: Main Agent
status: active
last_updated: 2026-09-27
doc_type: guide
complexity: advanced
tags: [beam, supplied-reinforcement, canonical-api, lib-pro-015-d1]
---

# Supplied Beam Reinforcement Check V2

Request: `beam-supplied-check/v2`<br>
Result: `beam-supplied-check-result/v2`<br>
Errors: `input-issue/v1`, `structural-problem/v1`, and
`beam-supplied-check-error/v2`

The check consumes exact longitudinal layers, stirrup diameter/legs/spacing,
effective depth, materials, factored actions, selection constraints, support
basis, source references, identity, tension face, and correlation identity.

Each longitudinal group must meet the calculated required area and stay within
`0.04 * b_mm * D_mm`. Inspect `longitudinal.checks.tension_area` and
`compression_area` for `required_mm2`, `provided_mm2`, `maximum_mm2`,
`is_within_maximum` and `is_adequate`. Extra bars can therefore cause `FAIL` even
when they exceed the required strength area.

Support acceptance uses unrounded development length. The M40-and-above bond
value is used by the shared anchorage helpers for M40 and higher grades. The
canonical V2 beam request still admits M20–M40 only; this correction does not
expand that domain. Zero shear is
accepted and still requires the same conservative support anchorage check.

The bend flags declare a standard bend; this route does not reconstruct its
shape or fit. Its support-width screen takes no M1/V enhancement. Serviceability
is separate: `beam.check`/`beam.design` accept `BeamServiceabilityChecksV1` with
the caller's service-analysis, section and reinforcement references. A supplied
reinforcement PASS does not include deflection or crack-width qualification.

See the [function review](../../planning/library-usability-improvement.md#function-review-lib-deep-review-002)
for source checks, numerical examples and the remaining physical-member scope.

## Valid `PASS`

```python
import json

from structural_lib.design.is456 import beam

payload = json.loads(
    r"""{serialized}"""
)
request = beam.load_supplied_check(payload)
result = beam.check_supplied(request)
assert result.status == "PASS"
assert result.effective_depth_resolution["d_mm"] == 442.0
```

## Rejected input

```python
import copy

from structural_lib.core.errors import InputContractError

invalid_payload = copy.deepcopy(payload)
del invalid_payload["section"]["effective_depth_basis"]

try:
    beam.load_supplied_check(invalid_payload)
except InputContractError as error:
    issue = error.issues[0]
    assert issue.code == "CROSS_FIELD_CONTRACT_INVALID"
    assert issue.path == "section"
```

## Engineering `FAIL`

```python
failed_payload = copy.deepcopy(payload)
failed_payload["actions"]["vu_kn"] = 200.0
failed_payload["reinforcement"]["stirrup_spacing_mm"] = 300.0
failed = beam.check_supplied(beam.load_supplied_check(failed_payload))
assert failed.status == "FAIL"
assert failed.shear.spacing_is_adequate is False
```

## Engineering `HOLD`

```python
held_payload = copy.deepcopy(payload)
held_payload["support"] = None
held = beam.check_supplied(beam.load_supplied_check(held_payload))
assert held.status == "HOLD"
assert held.result_envelope.overall_status.value == "HOLD"
```

`HOLD` is never an adequate Boolean. REST and WebSocket project the same result
dictionary and preserve `correlation_id`. See the
[V1 migration](../../migration/beam-supplied-check-v2.md) and
[beam facade reference](../../reference/beam-facade.md).

Replay these examples with a local build of source package version
`{PROJECT_VERSION}`. Results require qualified review.
'''


def _beam_reference() -> str:
    module = importlib.import_module("structural_lib.design.is456.beam")
    operations = (
        "input",
        "load",
        "design",
        "check",
        "detail",
        "design_and_detail",
        "bbs",
        "load_supplied_check",
        "check_supplied",
        "load_continuous",
        "check_continuous",
        "render_continuous_html",
        "load_cantilever",
        "check_cantilever",
        "render_cantilever_html",
        "load_section",
        "check_section",
        "render_section_html",
    )
    rows: list[str] = []
    sections: list[str] = []
    for name in operations:
        value = getattr(module, name)
        signature = inspect.signature(value)
        table_signature = str(signature).replace("|", "\\|")
        summary = (inspect.getdoc(value) or "").splitlines()[0]
        rows.append(
            f"| `{name}` | `structural_lib.design.is456.beam.{name}{table_signature}` | "
            f"{summary} |"
        )
        sections.append(
            f"### `{name}`\n\n"
            f"```python\n{name}{signature}\n```\n\n"
            f"{inspect.getdoc(value)}"
        )
    return f"""---
owner: Main Agent
status: active
last_updated: 2026-09-01
doc_type: reference
complexity: advanced
tags: [beam, canonical-api, exact-signatures, lib-pro-015-d1]
---

# Canonical IS 456 Beam Facade

Recommended import: `from structural_lib.design.is456 import beam`<br>
Classification: pre-1.0 canonical workflow facade<br>
Introduced contract family: `beam-design-input/v1`; supplied check added as
`beam-supplied-check/v2`<br>
Source package version: `{PROJECT_VERSION}`

## Operations

| Operation | Exact live signature | Purpose |
|---|---|---|
{chr(10).join(rows)}

## Request, result, and error contracts

| Journey | Request | Result | Intake/calculation errors |
|---|---|---|---|
| Required design/detailing | `BeamDesignInputV1` | `BeamDesignResultV1`, `BeamDetailingResultV1`, `BeamDesignAndDetailResultV1`, `BeamBBSResultV1` | `InputContractError` / `input-issue/v1`; calculation errors remain distinct |
| Two-span supplied actions | `BeamContinuousCheckRequestV1` | `BeamContinuousCheckResultV1` and a bound HTML report | `InputContractError` / `input-issue/v1` |
| Cantilever supplied actions | `BeamCantileverCheckRequestV1` | `BeamCantileverCheckResultV1` and a bound HTML report | `InputContractError` / `input-issue/v1` |
| Signed section and multilayer steel | `BeamSectionCheckRequestV1` | `BeamSectionCheckResultV1` and a bound HTML report | `InputContractError` / `input-issue/v1` |
| Supplied reinforcement | `BeamSuppliedCheckRequestV2` | `BeamSuppliedCheckResultV2` with `PASS`/`FAIL`/`HOLD` | Same Python issue boundary; REST 422 problem; WebSocket terminal `ERROR` |

The typed request schemas own field type, unit-suffixed name, domain,
optionality, defaults, identity/provenance, and cross-field validation. The
machine-readable schemas and per-field decisions are in
[`api-classification.json`](api-classification.json). Supplied-check HTTP fields
are also in `/openapi.json`; WebSocket uses the checked-in
[V2 exchange schema](beam-supplied-check-websocket-v2.schema.json).

## Examples and migration

- [Design valid, invalid, and engineering `FAIL`](../cookbook/python/beam-design.md)
- [Supplied check valid, invalid, `FAIL`, and `HOLD`](../cookbook/python/beam-supplied-check.md)
- [Two-span continuous beam, concurrent rows and review report](../cookbook/python/continuous-beam-check.md)
- [Flat V1 supplied-check migration](../migration/beam-supplied-check-v2.md)
- REST: `POST /api/v2/design/beam` and retained path
  `POST /api/v1/design/beam/check`

## Limitations and review boundary

The facade does not generate project loads, infer reinforcement/source facts,
expand supported topology, or provide professional acceptance. Result intake,
calculation, engineering, freshness, and qualified-review axes remain separate.
Calculation provenance remains with the maintained IS 456 owners named by each
result; facade functions contain no independent formula.

## Operation docstrings

{chr(10).join(sections)}
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
    beam_namespace = _beam_documentation_namespace()
    outputs[Path("docs/cookbook/python/beam-supplied-check.md")] = _beam_supplied_page(
        beam_namespace
    )
    outputs[Path("docs/reference/beam-facade.md")] = _beam_reference()
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
