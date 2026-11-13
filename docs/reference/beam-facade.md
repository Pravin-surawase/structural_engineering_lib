---
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
Source package version: `0.29.0`

## Operations

| Operation | Exact live signature | Purpose |
|---|---|---|
| `input` | `structural_lib.design.is456.beam.input(*, member_id: 'str', story: 'str', case_id: 'str', span_mm: 'float', b_mm: 'float', D_mm: 'float', fck_nmm2: 'float', fy_nmm2: 'float', fy_transverse_nmm2: 'float \| None' = None, mu_knm: 'float', vu_kn: 'float', d_dash_mm: 'float', asv_mm2: 'float', d_mm: 'float \| None' = None, effective_depth_basis: 'EffectiveDepthBasisRequestV1 \| CentroidCoverDepthRequestV1 \| None' = None, tu_knm: 'float' = 0.0, primary_tension_face: "Literal['TOP', 'BOTTOM'] \| None" = None, pt_percent: 'float \| None' = None, ast_mm2_for_shear: 'float \| None' = None, detailing: 'BeamDetailingOptionsV1 \| None' = None, serviceability: 'BeamServiceabilityV1 \| BeamServiceabilityChecksV1 \| None' = None, source_provenance: 'str \| None' = None) -> 'BeamDesignInputV1'` | Build one strict rectangular-beam design request. |
| `load` | `structural_lib.design.is456.beam.load(value: 'Mapping[str, object] \| BeamDesignInputV1') -> 'BeamDesignInputV1'` | Parse nested Python or decoded JSON into a canonical beam request. |
| `design` | `structural_lib.design.is456.beam.design(request: 'BeamDesignInputV1') -> 'BeamDesignResultV1'` | Run the canonical rectangular-beam design journey. |
| `check` | `structural_lib.design.is456.beam.check(request: 'BeamDesignInputV1') -> 'BeamDesignResultV1'` | Evaluate a canonical request without converting failure into an exception. |
| `detail` | `structural_lib.design.is456.beam.detail(design_result: 'BeamDesignResultV1', *, detailing_standard: 'DetailingStandard \| None' = None) -> 'BeamDetailingResultV1'` | Create explicit detailing from a completed canonical design result. |
| `design_and_detail` | `structural_lib.design.is456.beam.design_and_detail(request: 'BeamDesignInputV1', *, detailing_standard: 'DetailingStandard \| None' = None) -> 'BeamDesignAndDetailResultV1'` | Compose canonical design and detailing without hidden choices. |
| `bbs` | `structural_lib.design.is456.beam.bbs(result: 'BeamDesignAndDetailResultV1 \| BeamDetailingResultV1 \| list[BeamDetailingResultV1]') -> 'BeamBBSResultV1'` | Generate a canonical BBS from exact accepted detailing results. |
| `load_supplied_check` | `structural_lib.design.is456.beam.load_supplied_check(value: 'Mapping[str, object] \| BeamSuppliedCheckRequestV2') -> 'BeamSuppliedCheckRequestV2'` | Parse the exact supplied-reinforcement V2 request. |
| `check_supplied` | `structural_lib.design.is456.beam.check_supplied(request: 'BeamSuppliedCheckRequestV2') -> 'BeamSuppliedCheckResultV2'` | Evaluate exact supplied longitudinal bars and stirrups for one case. |
| `load_continuous` | `structural_lib.design.is456.beam.load_continuous(value: 'Mapping[str, object] \| str \| bytes \| BeamContinuousCheckRequestV1') -> 'BeamContinuousCheckRequestV1'` | Parse a strict supplied two-span beam request. |
| `check_continuous` | `structural_lib.design.is456.beam.check_continuous(request: 'BeamContinuousCheckRequestV1') -> 'BeamContinuousCheckResultV1'` | Check signed flexure, shear and straight anchorage on a two-span beam. |
| `render_continuous_html` | `structural_lib.design.is456.beam.render_continuous_html(result: 'BeamContinuousCheckResultV1') -> 'str'` | Render the checked rows, governing cases and limits in a review report. |
| `load_cantilever` | `structural_lib.design.is456.beam.load_cantilever(value: 'Mapping[str, object] \| str \| bytes \| BeamCantileverCheckRequestV1') -> 'BeamCantileverCheckRequestV1'` | Parse a strict supplied-action cantilever request. |
| `check_cantilever` | `structural_lib.design.is456.beam.check_cantilever(request: 'BeamCantileverCheckRequestV1') -> 'BeamCantileverCheckResultV1'` | Check signed flexure, shear and straight fixed-face anchorage. |
| `render_cantilever_html` | `structural_lib.design.is456.beam.render_cantilever_html(result: 'BeamCantileverCheckResultV1') -> 'str'` | Render the checked cantilever result and its input identity. |

## Request, result, and error contracts

| Journey | Request | Result | Intake/calculation errors |
|---|---|---|---|
| Required design/detailing | `BeamDesignInputV1` | `BeamDesignResultV1`, `BeamDetailingResultV1`, `BeamDesignAndDetailResultV1`, `BeamBBSResultV1` | `InputContractError` / `input-issue/v1`; calculation errors remain distinct |
| Two-span supplied actions | `BeamContinuousCheckRequestV1` | `BeamContinuousCheckResultV1` and a bound HTML report | `InputContractError` / `input-issue/v1` |
| Cantilever supplied actions | `BeamCantileverCheckRequestV1` | `BeamCantileverCheckResultV1` and a bound HTML report | `InputContractError` / `input-issue/v1` |
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

### `input`

```python
input(*, member_id: 'str', story: 'str', case_id: 'str', span_mm: 'float', b_mm: 'float', D_mm: 'float', fck_nmm2: 'float', fy_nmm2: 'float', fy_transverse_nmm2: 'float | None' = None, mu_knm: 'float', vu_kn: 'float', d_dash_mm: 'float', asv_mm2: 'float', d_mm: 'float | None' = None, effective_depth_basis: 'EffectiveDepthBasisRequestV1 | CentroidCoverDepthRequestV1 | None' = None, tu_knm: 'float' = 0.0, primary_tension_face: "Literal['TOP', 'BOTTOM'] | None" = None, pt_percent: 'float | None' = None, ast_mm2_for_shear: 'float | None' = None, detailing: 'BeamDetailingOptionsV1 | None' = None, serviceability: 'BeamServiceabilityV1 | BeamServiceabilityChecksV1 | None' = None, source_provenance: 'str | None' = None) -> 'BeamDesignInputV1'
```

Build one strict rectangular-beam design request.

Parameters
----------
member_id, story, case_id : str
    Caller-owned member and action-case identity.
span_mm, b_mm, D_mm : float
    Span, section width, and overall depth in millimetres.
fck_nmm2, fy_nmm2, fy_transverse_nmm2 : float
    Concrete, longitudinal-steel, and optional transverse-steel strengths.
mu_knm, vu_kn, tu_knm : float
    Caller-supplied factored bending, shear, and torsion actions.
d_dash_mm, asv_mm2 : float
    Compression-steel depth and transverse-reinforcement area basis.
d_mm : float, optional
    Explicit effective depth; mutually exclusive with ``effective_depth_basis``.
effective_depth_basis : EffectiveDepthBasisRequestV1 or CentroidCoverDepthRequestV1, optional
    Complete typed basis used by the shared effective-depth owner.
primary_tension_face : {"TOP", "BOTTOM"}, optional
    Physical tension face required for signed/torsional workflows.
pt_percent, ast_mm2_for_shear : float, optional
    Longitudinal steel for the concrete shear-strength lookup: supply its
    percentage or area in mm². With neither, use flexure-required steel.
    If both are supplied, they must agree with ``pt = 100 * Ast / (b * d)``
    (relative tolerance 1e-9, absolute area tolerance 1e-6 mm²). Generated
    detailing must supply at least this area; these inputs do not select bars.
detailing : BeamDetailingOptionsV1, optional
    Complete caller-selected detailing choices.
serviceability : BeamServiceabilityV1 or BeamServiceabilityChecksV1, optional
    Versioned bounded serviceability evidence.
source_provenance : str, optional
    Caller-owned source reference for the request.

Returns
-------
BeamDesignInputV1
    Immutable, strictly validated canonical request.

Raises
------
InputContractError
    If a field or cross-field relationship violates the public contract.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> request = beam.input(
...     member_id="B1", story="L1", case_id="ULS-1", span_mm=5000,
...     b_mm=300, D_mm=500, d_mm=442, fck_nmm2=25, fy_nmm2=500,
...     mu_knm=100, vu_kn=60, d_dash_mm=58, asv_mm2=100.53,
...     source_provenance="reviewed schedule B1",
... )
>>> request.schema_version
'beam-design-input/v1'

Limitations
-----------
This builder does not generate loads, infer project criteria, or approve a
section. Complex evidence remains in the named typed groups.

Provenance
----------
Field validation is owned by ``BeamDesignInputV1`` and is shared with the
canonical CLI and REST V2 journey.
### `load`

```python
load(value: 'Mapping[str, object] | BeamDesignInputV1') -> 'BeamDesignInputV1'
```

Parse nested Python or decoded JSON into a canonical beam request.

Parameters
----------
value : Mapping[str, object] or BeamDesignInputV1
    Mapping-like decoded data for ``beam-design-input/v1``.

Returns
-------
BeamDesignInputV1
    Strict typed request with no coercion of numeric strings or booleans.

Raises
------
InputContractError
    If input type, fields, values, identity, or cross-field basis is invalid.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> request = beam.load({
...     "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS"},
...     "section": {"span_mm": 5000, "b_mm": 300, "D_mm": 500, "d_mm": 442},
...     "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
...     "actions": {"mu_knm": 100, "vu_kn": 60, "tu_knm": 0},
...     "calculation_basis": {"d_dash_mm": 58, "asv_mm2": 100.53},
... })
>>> request.identity.member_id
'B1'

Limitations
-----------
Parsing validates caller data only; it does not create actions, geometry,
reinforcement choices, or qualified-review evidence.

Provenance
----------
Validation errors are translated by the shared library-owned
``model_validate_or_error`` boundary.
### `design`

```python
design(request: 'BeamDesignInputV1') -> 'BeamDesignResultV1'
```

Run the canonical rectangular-beam design journey.

Parameters
----------
request : BeamDesignInputV1
    Strict caller-owned identity, section, materials, actions, and basis.

Returns
-------
BeamDesignResultV1
    Typed calculation and orthogonal result envelope. Engineering
    inadequacy is returned as ``FAIL`` rather than raised as intake error.

Raises
------
InputContractError
    If ``request`` is not a ``BeamDesignInputV1``.
CalculationError
    If the maintained calculation owner cannot complete the calculation.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> request = beam.load({
...     "identity": {"member_id": "B1", "story": "L1", "case_id": "ULS"},
...     "section": {"span_mm": 5000, "b_mm": 300, "D_mm": 500, "d_mm": 442},
...     "materials": {"fck_nmm2": 25, "fy_nmm2": 500},
...     "actions": {"mu_knm": 100, "vu_kn": 60, "tu_knm": 0},
...     "calculation_basis": {"d_dash_mm": 58, "asv_mm2": 100.53},
... })
>>> beam.design(request).engineering_status.value
'PASS'

Limitations
-----------
The request supplies factored actions. This operation does not generate
loads or professional acceptance and supports only its declared rectangular
strength and bounded serviceability scope.

Provenance
----------
Delegates to the maintained IS 456 beam calculation owner and returns its
clause/source basis in the canonical result.
### `check`

```python
check(request: 'BeamDesignInputV1') -> 'BeamDesignResultV1'
```

Evaluate a canonical request without converting failure into an exception.

Parameters
----------
request : BeamDesignInputV1
    Strict canonical beam request.

Returns
-------
BeamDesignResultV1
    The same typed result as ``design`` with explicit engineering status.

Raises
------
InputContractError
    If the request type is not the canonical input contract.
CalculationError
    If the maintained calculation cannot complete.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> inspectable = beam.check
>>> inspectable is beam.design
False

Limitations
-----------
This is a semantic alias for required-design evaluation, not the supplied-
reinforcement V2 check. Use ``check_supplied`` for exact installed bars.

Provenance
----------
Delegates directly to ``design`` and therefore has identical calculation
and result ownership.
### `detail`

```python
detail(design_result: 'BeamDesignResultV1', *, detailing_standard: 'DetailingStandard | None' = None) -> 'BeamDetailingResultV1'
```

Create explicit detailing from a completed canonical design result.

Parameters
----------
design_result : BeamDesignResultV1
    Completed canonical design whose request includes detailing options.
detailing_standard : DetailingStandard, optional
    Use the standard already selected in ``request.detailing`` when omitted.
    An explicit argument is an assertion and must match that choice.

Returns
-------
BeamDetailingResultV1
    Typed detailing and result envelope bound to the source request.

Raises
------
InputContractError
    If the source type/status/options are unacceptable or the standard,
    serviceability, torsion, spacing, side-face or generated-depth basis is
    incomplete or inconsistent.
ValueError
    If the maintained detailing owner rejects an unsupported value outside
    the translated public issue cases.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> callable(beam.detail)
True

Limitations
-----------
This operation consumes explicit options. It does not choose project bar
stock, revise service analysis, or approve detailing for construction.

Provenance
----------
Delegates to ``detail_beam_is456`` and retains the canonical request and
calculation envelope in the returned result.
### `design_and_detail`

```python
design_and_detail(request: 'BeamDesignInputV1', *, detailing_standard: 'DetailingStandard | None' = None) -> 'BeamDesignAndDetailResultV1'
```

Compose canonical design and detailing without hidden choices.

Parameters
----------
request : BeamDesignInputV1
    Strict request containing complete detailing options.
detailing_standard : DetailingStandard, optional
    Use ``request.detailing.standard`` when omitted. An explicit argument
    must match it; the request always carries the caller's standard choice.

Returns
-------
BeamDesignAndDetailResultV1
    Design and detailing results with one fail-closed aggregate envelope.

Raises
------
InputContractError
    If design/detailing intake, scope, or standard reconciliation fails.
CalculationError
    If the maintained strength calculation cannot complete.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> callable(beam.design_and_detail)
True

Limitations
-----------
Composition does not turn a ``FAIL`` into ``PASS`` and does not create
project load, stock, review, or construction-approval evidence.

Provenance
----------
Calls the exact canonical ``design`` and ``detail`` owners sequentially and
aggregates their existing result identities.
### `bbs`

```python
bbs(result: 'BeamDesignAndDetailResultV1 | BeamDetailingResultV1 | list[BeamDetailingResultV1]') -> 'BeamBBSResultV1'
```

Generate a canonical BBS from exact accepted detailing results.

Parameters
----------
result : BeamDesignAndDetailResultV1, BeamDetailingResultV1, or list
    One accepted result, or a non-empty list of accepted detailing results.

Returns
-------
BeamBBSResultV1
    All-or-nothing finite bar-bending schedule with source result identities.

Raises
------
InputContractError
    If the input type, collection, or engineering/detailing status is unaccepted.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> callable(beam.bbs)
True

Limitations
-----------
BBS generation consumes accepted canonical detailing; it does not revise
bars, invent a span, or convert a failed/held result into an artifact.

Provenance
----------
The facade delegates to ``generate_bbs`` and preserves the source result
schema versions in the returned schedule.
### `load_supplied_check`

```python
load_supplied_check(value: 'Mapping[str, object] | BeamSuppliedCheckRequestV2') -> 'BeamSuppliedCheckRequestV2'
```

Parse the exact supplied-reinforcement V2 request.

Parameters
----------
value : Mapping[str, object] or BeamSuppliedCheckRequestV2
    Nested decoded data conforming to ``beam-supplied-check/v2``.

Returns
-------
BeamSuppliedCheckRequestV2
    Strict request that preserves identity, depth, bars, stirrups, and sources.

Raises
------
InputContractError
    If the request is partial, flat/legacy, coercive, non-finite, or inconsistent.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> schema = beam.BeamSuppliedCheckRequestV2.model_json_schema()
>>> schema["additionalProperties"]
False

Limitations
-----------
The former flat area-only payload is rejected because it cannot reconstruct
exact layers, transverse reinforcement, or source evidence.

Provenance
----------
``BeamSuppliedCheckRequestV2`` is the shared Python, REST, and WebSocket
intake owner; the full executable request is in the supplied-check cookbook.
### `check_supplied`

```python
check_supplied(request: 'BeamSuppliedCheckRequestV2') -> 'BeamSuppliedCheckResultV2'
```

Evaluate exact supplied longitudinal bars and stirrups for one case.

Parameters
----------
request : BeamSuppliedCheckRequestV2
    Fully validated section, action, reinforcement, selection, and source basis.

Returns
-------
BeamSuppliedCheckResultV2
    Correlated ``PASS``, ``FAIL``, or ``HOLD`` result and orthogonal envelope.

Raises
------
InputContractError
    If a non-V2 request reaches the facade boundary.
CalculationError
    If the maintained calculation owner cannot complete the declared check.

Examples
--------
>>> from structural_lib.design.is456 import beam
>>> callable(beam.check_supplied)
True

Limitations
-----------
This rectangular-beam slice does not infer support widths or professional
acceptance. Missing support evidence returns ``HOLD``.

Provenance
----------
Delegates without formula duplication to ``check_supplied_beam_v2``; the
complete valid, invalid, ``FAIL``, and ``HOLD`` vectors are executable in
the supplied-check cookbook.
### `load_continuous`

```python
load_continuous(value: 'Mapping[str, object] | str | bytes | BeamContinuousCheckRequestV1') -> 'BeamContinuousCheckRequestV1'
```

Parse a strict supplied two-span beam request.

Parameters
----------
value : Mapping, JSON str or bytes, or BeamContinuousCheckRequestV1
    Physical supports, bar positions and revision-bound station actions.

Returns
-------
BeamContinuousCheckRequestV1
    The immutable request to pass to :func:`check_continuous`.

Raises
------
InputContractError
    Duplicate rows, inconsistent topology or other invalid intake.

Examples
--------
>>> callable(load_continuous)
True

Limitations
-----------
Accepts already normalized mm, kN and kN·m. The worked example shows
the complete request and how to run PASS, FAIL and HOLD cases.

Provenance
----------
Uses the strict IS 456 continuous-beam request model and canonical issues.
### `check_continuous`

```python
check_continuous(request: 'BeamContinuousCheckRequestV1') -> 'BeamContinuousCheckResultV1'
```

Check signed flexure, shear and straight anchorage on a two-span beam.

Parameters
----------
request : BeamContinuousCheckRequestV1
    Two spans of a prismatic rectangular beam, both physical bar faces,
    three supports and concurrent actions at the declared stations.

Returns
-------
BeamContinuousCheckResultV1
    Supplied ultimate disposition, exact source rows, governing checks
    and separately held service evidence.

Raises
------
TypeError
    The input is not a validated continuous-beam request.

Examples
--------
>>> callable(check_continuous)
True

Limitations
-----------
The check consumes already supplied actions. It holds stale, incomplete
or unsupported evidence. Fabrication, lateral stability and service
deflection or cracking require separate checks.

Provenance
----------
Composes the maintained IS 456 physical flexure, shear, geometry and
anchorage checks. The result records their identities and the input hash.
### `render_continuous_html`

```python
render_continuous_html(result: 'BeamContinuousCheckResultV1') -> 'str'
```

Render the checked rows, governing cases and limits in a review report.

Parameters
----------
result : BeamContinuousCheckResultV1
    A result from :func:`check_continuous`.

Returns
-------
str
    Self-contained UTF-8 HTML.

Raises
------
TypeError
    The input is not a continuous-beam result.

Examples
--------
>>> callable(render_continuous_html)
True

Limitations
-----------
The report preserves the bounded disposition and qualified-review status.

Provenance
----------
Reads the exact result and input identity without recalculating any row.
### `load_cantilever`

```python
load_cantilever(value: 'Mapping[str, object] | str | bytes | BeamCantileverCheckRequestV1') -> 'BeamCantileverCheckRequestV1'
```

Parse a strict supplied-action cantilever request.

Parameters
----------
value : Mapping, JSON str or bytes, or BeamCantileverCheckRequestV1
    Physical section, fixed-support geometry and revision-bound actions.

Returns
-------
BeamCantileverCheckRequestV1
    A validated request for :func:`check_cantilever`.

Raises
------
InputContractError
    The payload violates the request contract.

Examples
--------
>>> callable(load_cantilever)
True

Limitations
-----------
Coordinates are in mm from the fixed face toward the free end. Supply
actions in kN and kN·m, including both sides of each discontinuity.

Provenance
----------
Uses the strict IS 456 cantilever request model and canonical input issues.
### `check_cantilever`

```python
check_cantilever(request: 'BeamCantileverCheckRequestV1') -> 'BeamCantileverCheckResultV1'
```

Check signed flexure, shear and straight fixed-face anchorage.

Parameters
----------
request : BeamCantileverCheckRequestV1
    Validated section, bars and supplied station actions.

Returns
-------
BeamCantileverCheckResultV1
    Checked rows, governing row IDs and revision-bound dispositions.

Raises
------
TypeError
    The request is not a validated cantilever request.

Examples
--------
>>> callable(check_cantilever)
True

Limitations
-----------
Ordinary prismatic rectangular section, one bar layer per face and a
zero-action free end. Serviceability and fabrication need separate checks.

Provenance
----------
Composes the maintained IS 456 section, shear and direct anchorage checks.
### `render_cantilever_html`

```python
render_cantilever_html(result: 'BeamCantileverCheckResultV1') -> 'str'
```

Render the checked cantilever result and its input identity.

Parameters
----------
result : BeamCantileverCheckResultV1
    A result from :func:`check_cantilever`.

Returns
-------
str
    Standalone HTML retaining station sides and result dispositions.

Raises
------
TypeError
    The result is not a cantilever check result.

Examples
--------
>>> callable(render_cantilever_html)
True

Limitations
-----------
Renders the supplied result without rechecking or creating a schedule.

Provenance
----------
Uses the same result and analysis revision as the JSON projection.
