---
owner: Main Agent
status: active
last_updated: 2026-11-15
doc_type: guide
complexity: intermediate
tags: [slab, supplied-actions, canonical-api, library-030]
---

# Slab Supplied Actions

- Journey `is456.slab.supplied-action-set/v1`
- Request `slab-action-set-input/v1`
- Result `family-design-result/v1`

This workflow checks an explicit set of factored slab actions. It does not
generate loads, infer a support arrangement, or perform direct deflection
acceptance. The reviewed service check is limited to the supplied span/depth
evidence. This is the preview Python profile for supplied-action references;
its request and result remain intentionally bounded to that scope.

## Runnable frozen reference

From any directory, run the example by absolute path and name the immutable
reference fixture:

```bash
/absolute/path/to/scripts/python_runtime.sh /absolute/path/to/Python/examples/slab_supplied_action_references.py \
  --reference /absolute/path/to/docs/verification/library-030-sl06-actions.json \
  --specimen B02 --route builtin --scenario baseline
```

`B02` is a continuous one-way strip and `B04` is a two-way panel. Choose
`external` when the caller supplies qualified coefficient evidence; choose
`builtin` when the applicable built-in coefficient route is selected. The
example emits the public `result.to_dict()` JSON for valid intake.

The continuous one-way scope is a 1000 mm strip. It does not represent a
whole-floor load-takeoff or infer an effective strip width.

The scenario is `baseline` or an exact control key in the selected fixture,
such as `reordered`, `exact_tie`, `missing_B`,
`missing_shared_service_basis`, or `duplicate_id`. The duplicate-ID control is
expected to emit structured `InputContractError` issues rather than a result.

## Request shape

Use `slab.load_action_set(mapping)` followed by
`slab.check_action_set(request)`. The mapping identifies its `kind`, immutable
geometry/reinforcement revisions, shared geometry/material/reinforcement, the
reviewed service evidence (or `null`), required row IDs, and action rows.
Continuous one-way sets additionally acknowledge substantially uniform loading
and state that redistribution was not applied.

Each row has a stable `row_id`, a supplied
`factored_area_load_kn_per_m2`, and a `coefficient_basis`. External bases carry
the qualified coefficient inputs; built-in bases carry the selected route
inputs. The continuous built-in route derives its fixed action from the row
load, so do not duplicate a load argument inside `coefficient_basis`.

Positive bending moments are positive and support moments are negative. Support
shear is reported as a magnitude. These signs and units should be preserved
when comparing a result to an upstream analysis model.

## Reading the result

`result.calculation` records `coverage`, `uls`, `reviewed_service`,
`missing_required_row_ids`, per-ID `rows`, `governing_ids`, and
`governing_rows`. `result.calculation.governing_rows` references the actual
retained row objects selected by those governor IDs. Consequently a governing
ID remains traceable to its exact row, including under reordered input or
lexical tie-breaking.

Incomplete required-row coverage yields a whole-set `HOLD`; it is not a
per-row substitute for an omitted combination. A conclusive ULS failure still
takes precedence over that HOLD: the result retains evaluated failures and is
`FAIL` when any conclusive strength failure exists. Missing reviewed service
evidence yields a reviewed-service `HOLD`; it does not erase the available ULS
outcome.

## Python API

::: structural_lib.design.is456.slab
    options:
      docstring_style: numpy
      show_root_heading: false
      show_signature_annotations: true
      members:
        - load_action_set
        - check_action_set
