---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: INDIA-2-DEEP-C
---

# INDIA-2-DEEP-C Public Python Workflow Evidence

## Published composition

`design_simply_supported_deep_beam_is456` is the single typed Python workflow
for the G0-approved case. It is exported identically from
`structural_lib.services.api` and the package root. Its input names every mm,
kN m, and N/mm2 value plus support/topology assertions and the four caller
evidence references; no unit or topology is inferred.

The service constructs the integrated DEEP-A geometry/action contracts and the
DEEP-B provided-reinforcement contract, then returns their composed status and
intermediates without a second engineering calculation path. The frozen
supported case and all held systems are machine-visible in every result.

## Public clause, source, and approval truth

`SimplySupportedDeepBeamDesignProvenance` exposes IS 456:2000 Clauses 29,
29.1, 29.2, 29.3, 29.3.1, 29.3.4, 26.2.1, 26.2.1.1, and 32.5-32.5.2; the
Amendment No. 3 correction; the public-distribution decision; NPTEL scope
cross-check; benchmark identity; and all caller geometry, bearing/nodal,
action, and reinforcement references.

It states that the positive factored moment was caller supplied and not
generated, and that bearing/compression-nodal verification is an external
confirmed prerequisite rather than a library calculation. Qualified review is
always required and complete engineering approval is always false.

## Executable benchmark and gates

The public workflow reproduces effective span `3000 mm`, lever arm `1400 mm`,
required/provided tie `1477.832512 / 1520.530844 mm2`, required embedment
`797.5 mm`, and provided vertical/horizontal side-face steel
`523.598776 / 628.318531 mm2/m`. Its complete result serializes through
`dataclasses.asdict` and JSON. Valid under-reinforcement and short anchorage
return composed `FAIL`; blank/unsupported topology and missing external
verification fail closed.

The direct-plus-public selection passes 47 tests; the combined deep-beam,
public-workflow, clause, traceability, Indian-manifest, and API-manifest
selection passes 141 tests. Black, Ruff, mypy, and
Bandit pass; architecture reports 0 violations across 175 files and imports
report 0 broken imports across 604 scanned files. Public API documentation,
manifest generation, and all three maintained API checks pass. All 1,176
internal links are valid, touched indexes are current, and quick gate passes
10/10. Required hosted checks must pass on the unchanged reviewed head. Generated
Indian capability truth remains held until DEEP-D adds transport and the
canonical capability/semantic contract.

The broad Python suite and 30-check repository gate remain deferred to the one
whole-INDIA-2 closeout. The next and final packet for today is
`INDIA-2-DEEP-D`; family acceptance remains for the next work session.
