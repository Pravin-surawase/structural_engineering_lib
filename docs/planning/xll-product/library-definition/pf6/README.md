---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF6
---

# PF6 — Python/.NET parity and package strategy

PF6 is complete. [baseline.json](baseline.json) defines what “the same library”
means across Python and .NET, how each language remains idiomatic, and where
Windows application adapters differ.

## D12 and D13 decisions

Parity is an operation-level claim. Equivalent effective inputs, profile and
code-data revision must produce the same semantic states and independently
qualified expected values within PF7 tolerances. The languages need not share
source code, internal algorithms, object layout, spelling or exception text.

FO01-FO08, reusable AO operations and the calculation-record model are native
in both languages. Excel and live ETABS work are .NET Windows adapters because
they are product integration, not structural calculation. Their requests,
captured snapshots, transaction receipts and reusable results remain portable,
so Python can inspect and replay the same engineering work without a COM clone.

Reviewed semantic manifests own purpose, applicability and meaning. Reviewed
JSON Schemas own portable structure. Normalized code-data files and conformance
vectors own their respective data and examples. Python and C# domain algorithms
remain handwritten and independently reviewable. Transport DTOs, validators,
reference tables and fixture bindings may be generated, but generated code can
never become the only definition of an engineering rule.

The Python and .NET maps use the same dependency direction: contracts/core,
design-code rules, analysis/member/reinforcement/construction/search services,
report records and interchange. Compatibility and application adapters sit at
the outside. Pure packages load without FastAPI, React, Excel-DNA or CSI API.

## Exit review

- All 17 capabilities and FO01-FO08/AO01-AO26 have a parity mode.
- Ten drift controls cover catalogue, schema, fixtures, identity, calculations,
  code data, dependencies, compatibility, application replay and releases.
- Semantic, schema, data, code and generated-artifact authorities are explicit.
- Vendor dependencies exist only in the .NET Windows adapter assemblies.

PF7 supplies the independent engineering evidence and numerical comparison
rules that make the parity claims meaningful.
