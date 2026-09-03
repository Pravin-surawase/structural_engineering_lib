---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF4
---

# PF4 — engineering semantic model

PF4 is complete. [baseline.json](baseline.json) is the common semantic contract
for Python, .NET, Excel and ETABS adapters. It defines quantities, boundary
units, signed actions, axes, station identity, optional-value resolution,
provenance identities and independent result states.

## D06 through D09 decisions

Public operations use explicit quantity meanings and units. A bare `span`,
`cover`, `steel area`, `bar length` or `cost` is not a professional input or
output. Compatibility wrappers may accept an old term only when they translate
it to one named meaning and return the translation.

Actions retain all six signed local-axis components from one source row. An
adapter records its unit and axis transform. A component envelope cannot be
used as if it were concurrent in flexure, shear and torsion interaction.
Physical reinforcement faces come from section geometry and the axis transform,
not an unexplained moment-sign convention.

Absent, explicit null, Excel blank and numerical zero are different states.
Defaults must come from a named profile; derived values identify their rule and
dependencies. Results return the effective inputs and their origin so equivalent
Python and .NET calls can be replayed and compared.

Raw artifacts, acquisition events, model revisions, analysis revisions,
normalized inputs, calculations, details and reports have separate identities.
The normalized-input identity uses a versioned unit-normalized canonical JSON
contract rather than a runtime serializer or acquisition timestamp.

Execution, applicability, engineering outcome, completeness, freshness and
human approval are independent. Invalid input or software failure does not
become an engineering failure, and software never grants professional approval.

## Exit review

- Thirty-seven common quantities have explicit dimensions, units and meanings.
- Unit, sign, axis, concurrency and station rules apply to every adapter.
- Four field obligations and eight value states prevent hidden defaults.
- Ten identities bind the source-to-report chain without conflating events.
- Six result-state dimensions preserve failure, inapplicability and approval.

PF5 projects these meanings into the public operation catalogue and idiomatic
Python and C# signatures.
