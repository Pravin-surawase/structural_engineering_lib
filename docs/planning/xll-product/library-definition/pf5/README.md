---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF5
---

# PF5 — public operations and professional signatures

PF5 is complete. [baseline.json](baseline.json) replaces implementation-shaped
planning names with normative semantic operations, then projects those
operations into idiomatic Python and C# APIs. It covers eight small value or
capacity functions and AO01-AO26.

## D10 and D11 decisions

The library has seven public levels: value, capacity, check, design,
member/service, application command and human approval record. A value does not
claim capacity, capacity does not claim that a demand passed, a check does not
select reinforcement, and a design does not create professional approval.

Every public operation states its purpose, applicability/profile, request and
result meaning, quantities and units, signs, conditional inputs, optional-value
resolution, effective inputs, outputs, state, diagnostics, provenance,
identity, valid example, non-success example and compatibility behavior.

Python uses snake_case functions and immutable typed records. C# uses PascalCase
methods and immutable records, with async reserved for I/O or cooperative long
work. Both projections publish the same semantic identifier and exchange
schema. Convenience overloads and Excel functions may simplify data entry but
cannot change defaults, meanings or outcomes.

Expected invalid, unsupported, inapplicable, stale, incomplete and engineering
failure states return structured results. Exceptions are reserved for programmer
misuse or unexpected infrastructure failure and are translated by adapters.

## Corrections to the old C# foundation

`ForceNormalizer.Normalize(EtabsForceBatch)` becomes a compatibility projection
over vendor-neutral action normalization; ETABS acquisition remains an adapter.
`CandidateRanker.Rank` must treat a required `not_applicable` or `not_evaluated`
check as incomplete for the selected profile. It may rank only fully evaluated,
feasible candidates bound to one analysis revision.

## Exit review

- FO01-FO08 and AO01-AO26 each have a valid and non-success example.
- Request, result, check, design and command envelope fields are fixed.
- Twenty-one stable diagnostic codes replace free-text control flow.
- Every PF1 workflow traces to the operations it uses.
- Compatibility preserves recoverable callers through visible translation.

PF6 now decides which semantic operations are native in both languages, which
are shared through schemas, and which remain Windows application adapters.
