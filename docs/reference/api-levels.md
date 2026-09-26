---
owner: Main Agent
status: active
last_updated: 2026-09-27
doc_type: reference
complexity: intermediate
tags: [api, reference]
---

# Which API Should I Use?

Choose the surface by the work you need to do. All contracts remain pre-1.0;
pin the installed distribution for reproducible calculations.

| Task | Public entry point | Start here |
|---|---|---|
| Supported IS 456 element design/checks | `structural_lib.design.is456` | [Family cookbook](../cookbook/python/family-facades.md) |
| Physical beam reinforcement, analysis and project workflows | `structural_lib.beam` | [Beam library guide](../library/getting-started.md) |
| An individual expert calculation | `structural_lib.codes.is456` | [Code reference](../api-reference/index.md#is-456-code-modules) |
| JSON files and exports | `python -m structural_lib` | [CLI reference](../cookbook/cli-reference.md) |
| HTTP applications | FastAPI routes in `/docs` and `/openapi.json` | [Canonical beam contract](beam-facade.md) |
| An existing script using root/service functions | Retained `structural_lib`, `structural_lib.api`, `structural_lib.services.api` functions | [Compatibility reference](api.md) |

## Element workflow: construct, calculate, inspect

Use the family module for both operations and its request group types. For
example, `column.ColumnGeometryV1` describes geometry; `column.input(...)`
combines explicit groups and `column.check(request)` evaluates supplied steel.
The [typed workflow example](../../Python/examples/canonical_workflows.py)
executes a beam schedule, column check, slab check, JSON round-trip and rejected
input. It targets the current source/wheel; newly exposed group imports and slab
builders require that build rather than an older published wheel.

```python
from structural_lib.design.is456 import column

# payload is the explicit input mapping from the column cookbook.
request = column.load(payload)
result = column.check(request)
print(result.engineering_status.value)
print(result.calculation["governing_check"])
print(result.qualified_review_required)
serializable_result = result.to_dict()
```

For new typed code, construct the named groups and pass them to `input`.
For data received as JSON, decode with `json.loads` and pass the mapping to
`load`. Both use the same validation owner; neither guesses geometry, materials,
load basis, reinforcement or review evidence. Slab routes use
`input_one_way`, `input_continuous_one_way` or `input_two_way` and matching
`load_*`/`design_*` names.

Invalid intake raises `InputContractError`; inspect `error.issues` for the
field path, code and constraint. A valid request may calculate an engineering
`FAIL` or `HOLD` and return normally. `PASS` covers the documented checks;
`qualified_review_required` remains separate. Read `limitations`, `assumptions`
and `provenance` before consuming the result.

The beam facade additionally supports explicit design → detailing → BBS.
See its [reference](beam-facade.md) and the runnable typed example for matching
reinforcement geometry and effective-depth inputs.

## Physical beam and project workflows

`structural_lib.beam` exposes the newer explicit physical-bar, analysis,
serviceability, detailing, quantities and complete-member workflow. It has its
own request/result vocabulary, including execution, applicability, completeness
and freshness. Follow the [beam library guide](../library/getting-started.md);
do not mix its result states with the element facade envelope by name alone.

## Expert calculation and compatibility

Expert functions perform individual calculations. Their parameter names,
units and sign conventions belong to that function; do not infer them from a
service wrapper. These checks do not automatically form a complete member
workflow.

Existing root and `api` imports continue to delegate to their maintained
owners. They are supported compatibility routes, not a reason to duplicate
formulas or migrate working callers unnecessarily. The machine-readable
[API classification](api-classification.json) records retained surfaces.

## HTTP boundary

`POST /api/v2/design/beam` accepts the canonical nested beam request. Use
`request.model_dump(mode="json")` when calling it from Python and consult
`/openapi.json` for the exact transport schema. Retained V1 routes may have
separate field names and response wrappers. A successful HTTP request can
contain an engineering failure; inspect the result status, not just HTTP 200.
