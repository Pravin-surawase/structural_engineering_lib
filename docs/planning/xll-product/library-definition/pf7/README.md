---
owner: Main Agent
last_updated: 2026-09-03
doc_type: spec
phase_id: PF7
---

# PF7 — engineering assurance and examples

PF7 is complete. [baseline.json](baseline.json) assigns assurance to AO01-AO26,
defines the example/conformance corpus, fixes numerical comparison rules and
sets conservative whole-member aggregation.

## D14 and D15 decisions

Every engineering operation has a source category, minimum evidence level,
test method and independent oracle. Cross-language agreement is E3 correlation;
it accompanies portable operations but never proves that either calculation is
correct. Excel/ETABS claims require E5 evidence from identified installed hosts.

The 180 sourcebook records remain candidate evidence. Each selected numerical
case is promoted only after source/revision, units, applicability, canonical
input, code-data revision, expected precision and an independent reconstruction
are reviewed. Promotion applies to that case and operation only; it does not
cover missing lookup nodes, interpolation interiors, limits or invalid paths.

Comparison uses exact equality for states, IDs, choices and decisions, and
quantity-specific absolute/relative tolerances for unrounded numerical values.
Published rounding is checked separately. Raw values decide code and
construction limits, so a tolerance cannot turn a failing boundary into a pass.
Money uses decimal arithmetic and a named currency rounding stage.

Whole-member evaluation freezes the expected leaf set before calculation and
retains every leaf afterward. Every required leaf must be completed, applicable,
passing, complete and current. A required `not_applicable`, `not_evaluated`,
stale or missing result makes the member partial and unqualified. Candidate
ranking may use only fully qualified candidates and cannot claim an optimum
from an incomplete search.

## Existing foundation reconciliation

The current C# ranker already excludes required `NotEvaluated` and
`NotApplicable` outcomes. Its remaining semantic gap is loss of the distinct
reason/state and reliance on a caller-supplied required-check list. The later
implementation must supply the profile-derived expected leaf set and retain
reason-coded exclusions before the ranker is promoted beyond E2.

## Exit review

- All 26 AO operations have source references, evidence levels and oracle types.
- Eleven example classes include nodes, interiors, boundaries and non-success.
- Six tolerance classes cover exact, numeric, source, boundary and money rules.
- Ten aggregation rules protect completeness, freshness and construction state.

PF8 applies these states and evidence rules to immutable ETABS snapshots, Excel
functions/commands and coupled candidate reanalysis.
